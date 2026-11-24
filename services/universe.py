"""Stored life dimensions, check-ins, and the office scores the homepage charts read.

Nothing here invents a headline percentage, an hour count, or a dollar figure.
Missing assessments stay missing.
"""

from __future__ import annotations

from typing import Any

from core.config import get_settings
from core.llm import LLMClient
from core.mandate import LifeMandate
from core.models import LifeBlueprint
from services.office import (
    CATALOG,
    make_or_buy,
    optimize_portfolio,
    recommend,
    strategic_value,
)

DOMAIN_FIELDS: tuple[tuple[str, str], ...] = (
    ("career", "Career"),
    ("academic", "Academic"),
    ("financial", "Financial"),
    ("relationships", "Relationships"),
    ("family", "Family"),
    ("lifestyle", "Lifestyle"),
    ("health", "Health"),
    ("legacy", "Legacy"),
)

# Same key always gets the same color on the canvas and the charts.
DIMENSION_COLORS = {
    "career": "#142438",
    "academic": "#496E65",
    "financial": "#B5A083",
    "relationships": "#3F6F7A",
    "family": "#8A5A2B",
    "lifestyle": "#14304A",
    "health": "#1F5C45",
    "legacy": "#5C6B7A",
}
_EXTRA_COLORS = ("#142438", "#496E65", "#B5A083", "#3F6F7A")


def color_for(key: str) -> str:
    if key in DIMENSION_COLORS:
        return DIMENSION_COLORS[key]
    return _EXTRA_COLORS[sum(ord(ch) for ch in key) % len(_EXTRA_COLORS)]


def active_dimensions(mandate: LifeMandate, blueprint: LifeBlueprint) -> list[dict[str, Any]]:
    """Dimensions that already have blueprint text, goals, or a mandate priority."""
    found: list[dict[str, Any]] = []
    for key, label in DOMAIN_FIELDS:
        text = str(getattr(blueprint, key, "") or "").strip()
        goals = [goal for goal in blueprint.goals if goal.domain.lower() == key]
        if not text and not goals:
            continue
        importance = max((goal.importance for goal in goals), default=None)
        progress = (sum(goal.progress for goal in goals) / len(goals)) if goals else None
        description = text
        if goals:
            titles = "; ".join(goal.title for goal in goals)
            description = f"{text} Goals: {titles}".strip()
        found.append(
            {
                "key": key,
                "name": label,
                "description": description or label,
                "goal_progress": progress,
                "importance": importance,
            }
        )
    seen = {item["key"] for item in found} | {item["name"].lower() for item in found}
    for priority in mandate.priorities:
        name = priority.strip()
        if not name or name.lower() in seen:
            continue
        slug = name.lower().replace(" ", "-")
        if slug in seen:
            continue
        seen.add(slug)
        seen.add(name.lower())
        found.append(
            {
                "key": slug,
                "name": name,
                "description": "Named on the Life Mandate priorities. No blueprint goals are stored for it.",
                "goal_progress": None,
                "importance": None,
            }
        )
    return found


def node_detail(dimension: dict[str, Any], assessment: int | None) -> dict[str, Any]:
    """What the canvas shows when a node is clicked. Unassessed stays unassessed."""
    if assessment is not None:
        return {
            "ring": assessment / 10,
            "detail": (
                f"Saved assessment {assessment} of 10. {dimension['description']}"
            ),
        }
    progress = dimension.get("goal_progress")
    if progress is not None:
        percent = round(float(progress) * 100)
        return {
            "ring": float(progress),
            "detail": (
                f"Blueprint goal progress is {percent}% on the stored Life Blueprint. "
                "That number is not a 0–10 assessment. "
                f"{dimension['description']}"
            ),
        }
    return {
        "ring": None,
        "detail": f"No assessment saved. {dimension['description']}",
    }


def daily_plan_text(checkin: dict[str, Any] | None) -> str:
    if not checkin:
        return "No check-in is saved for today. The plan stays empty until you save one."
    energy = int(checkin["energy"])
    if energy <= 2:
        pace = "Keep the must-do short and leave recovery time."
    else:
        pace = "Start with the must-do while energy is available."
    surprises = str(checkin.get("surprises") or "").strip() or "none recorded"
    return (
        f"Feeling: {checkin['feeling']}. Energy {energy}/5. {pace} "
        f"Must-do: {checkin['must_do']}. Responsibilities: {checkin['responsibilities']}. "
        f"Discretionary time: {checkin['discretionary_hours']}h. Surprises: {surprises}."
    )


def assessed_scores(
    dimensions: list[dict[str, Any]], assessments: dict[str, int]
) -> list[tuple[str, int]]:
    """Only dimensions the user has saved. Order follows the dimension list."""
    scored = []
    for dimension in dimensions:
        if dimension["key"] in assessments:
            scored.append((dimension["name"], int(assessments[dimension["key"]])))
    return scored


def capability_gaps(
    dimensions: list[dict[str, Any]], assessments: dict[str, int]
) -> list[dict[str, int | str]]:
    """Gap is stored goal importance minus the saved assessment. No invented target of 10."""
    rows = []
    for dimension in dimensions:
        key = dimension["key"]
        importance = dimension.get("importance")
        if key not in assessments or importance is None:
            continue
        score = int(assessments[key])
        rows.append(
            {
                "name": dimension["name"],
                "assessment": score,
                "importance": int(importance),
                "gap": int(importance) - score,
            }
        )
    return rows


def _with_budget(mandate: LifeMandate, hours: float, money: float) -> LifeMandate:
    trial = mandate.model_copy(deep=True)
    trial.time_budget_hours_week = float(hours)
    trial.money_budget_usd_month = float(money)
    return trial


def portfolio_for(mandate: LifeMandate, hours: float, money: float) -> dict[str, Any]:
    return optimize_portfolio(_with_budget(mandate, hours, money))


def heatmap_matrix(mandate: LifeMandate) -> dict[str, Any]:
    """Deterministic scores on the labeled catalog. Not a live search."""
    themes = sorted({theme for item in CATALOG for theme in item.tags})
    labels = [item.label for item in CATALOG]
    matrix = []
    for item in CATALOG:
        value = strategic_value(item, mandate)
        matrix.append([round(item.tags.get(theme, 0.0) * value, 2) for theme in themes])
    return {
        "labels": labels,
        "themes": themes,
        "z": matrix,
        "label": "Labeled catalog fixtures. Scores follow the saved mandate priorities.",
    }


def bubble_rows(mandate: LifeMandate) -> list[dict[str, Any]]:
    portfolio = optimize_portfolio(mandate)
    selected = set(portfolio["selected_ids"])
    rows = []
    for item in CATALOG:
        rows.append(
            {
                "label": item.label,
                "cash_usd": item.cash_usd,
                "hours": item.hours_week,
                "strategic_value": strategic_value(item, mandate),
                "objectives": len(item.stacking_themes),
                "selected": item.item_id in selected,
                "mandatory": item.mandatory,
            }
        )
    return rows


def spending_snapshot(mandate: LifeMandate, hours: float, money: float) -> dict[str, Any]:
    trial = _with_budget(mandate, hours, money)
    portfolio = optimize_portfolio(trial)
    choice = make_or_buy(trial)
    by_id = {item.item_id: item for item in CATALOG}
    selected = []
    for item_id in portfolio["selected_ids"]:
        item = by_id[item_id]
        selected.append(
            {
                "label": item.label,
                "cash_usd": item.cash_usd,
                "hours": item.hours_week,
                "mandatory": item.mandatory,
            }
        )
    return {
        "selected": selected,
        "weekly_cash_left": portfolio["weekly_cash_left"],
        "weekly_cash_envelope": portfolio["weekly_cash_envelope"],
        "hours_left_unscheduled": portfolio["hours_left_unscheduled"],
        "notes": portfolio["notes"],
        "scarce_constraint": choice["scarce_constraint"],
        "make_hours": choice["make"]["hours"],
        "buy_cash": choice["buy"]["cash_usd"],
        "buy_hours": choice["buy"]["hours"],
        "label": "OPERATIONAL scores on the labeled catalog. Not money already spent.",
    }


def build_decision_fixture(
    question: str,
    mandate: LifeMandate,
    workflow_sequence: list[str] | None = None,
) -> dict[str, Any]:
    """One structured answer from the existing office recommendation. No second invented pick."""
    rec = recommend(mandate)
    portfolio = optimize_portfolio(mandate)
    sequence = ""
    if workflow_sequence:
        sequence = " Priority 0 sequence already on this session: " + "; ".join(workflow_sequence) + "."
    answer = (
        f"You asked: {question.strip()} "
        f"The office discretionary pick is {rec.chosen_label} "
        f"(strategic value {rec.strategic_value}). "
        f"Approved mandate cited: {rec.used_approved}. "
        f"Portfolio keeps {len(portfolio['selected_ids'])} items and leaves "
        f"{portfolio['hours_left_unscheduled']}h unscheduled and "
        f"${portfolio['weekly_cash_left']} of the weekly cash envelope."
        f"{sequence}"
    )
    if rec.conflicts:
        answer += " Conflicts named: " + " ".join(rec.conflicts)
    return {
        "answer": answer,
        "chosen_id": rec.chosen_id,
        "chosen_label": rec.chosen_label,
        "strategic_value": rec.strategic_value,
        "selected_ids": list(portfolio["selected_ids"]),
        "used_approved": rec.used_approved,
        "source": "office.recommend + optimize_portfolio",
    }


def ask_decision(
    question: str,
    mandate: LifeMandate,
    client: LLMClient | None = None,
    workflow_sequence: list[str] | None = None,
) -> tuple[dict[str, Any], Any]:
    """Exactly one model call. Demo mode returns the office fixture and does not hit the network."""
    llm = client or LLMClient(get_settings())
    fixture = build_decision_fixture(question, mandate, workflow_sequence)
    return llm.complete(
        agent_id="Q01",
        role="Decision guide",
        system=(
            "Answer the user's question using only the office recommendation in the JSON. "
            "Do not invent a different winner. One JSON object."
        ),
        user=question.strip(),
        demo_payload=fixture,
    )
