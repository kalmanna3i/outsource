"""Homepage visuals: mission, universe, one decision question, saved check-in, charts."""

from __future__ import annotations

import html
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import streamlit as st

from core.config import get_settings
from core.llm import LLMClient
from database.db import (
    load_aspirations,
    load_assessment_history,
    load_assessments,
    load_daily_checkin,
    save_assessments,
    save_daily_checkin,
)
from services.universe import (
    active_dimensions,
    ask_decision,
    capability_gaps,
    daily_plan_text,
)
from ui.living_universe import render_living_universe
from ui.strategic_charts import (
    capability_gap_chart,
    dimension_levels,
    history_line,
    opportunity_heatmap,
    spending_comparison,
)


def _today() -> str:
    """Same UTC day the check-in was saved under. The header date stays local."""
    return datetime.now(timezone.utc).date().isoformat()


def _mode_line() -> str:
    settings = get_settings()
    if settings.effective_mode == "live" and settings.integration_mode != "live":
        return "Live AI · Simulated integrations"
    if settings.effective_mode == "live":
        return "Live AI · Live integrations"
    return "Demonstration mode"


def _spark(values: list[int]) -> str:
    """A line only when two or more saved points exist. One point stays a number."""
    if len(values) < 2:
        return ""
    low, high = min(values), max(values)
    span = high - low or 1
    width, height = 120, 28
    coords = []
    for index, value in enumerate(values):
        x = 2 + (width - 4) * index / (len(values) - 1)
        y = height - 4 - (height - 8) * (value - low) / span
        coords.append(f"{x:.1f},{y:.1f}")
    return (
        f"<svg class='spark' viewBox='0 0 {width} {height}' aria-hidden='true'>"
        f"<polyline points='{' '.join(coords)}'/></svg>"
    )


def render_today(mandate, blueprint, workflow) -> None:
    assessments = load_assessments()
    _identity(blueprint)
    mission = (mandate.mission or "").strip() or "No mission is saved yet."
    st.markdown(f'<p class="life-mission">{html.escape(mission)}</p>', unsafe_allow_html=True)
    _question(mandate, workflow)
    _stored_cards(mandate, blueprint, assessments)
    graph, side = st.columns([1.35, 1], gap="medium")
    with graph:
        st.markdown("<p class='section-label'>Network</p>", unsafe_allow_html=True)
        render_living_universe(mandate, blueprint, assessments)
    with side:
        _today_side(mandate)
    _charts(mandate, blueprint, assessments)
    _checkin()
    _assessments(mandate, blueprint, assessments)


def _identity(blueprint) -> None:
    name = getattr(blueprint, "user_name", "") or "Local"
    when = datetime.now(ZoneInfo("America/New_York")).strftime("%b %-d")
    st.markdown(
        "<p class='life-headline'>Personal overview</p>"
        f"<p class='life-meta'>{html.escape(name)} · {html.escape(when)} · {html.escape(_mode_line())}</p>",
        unsafe_allow_html=True,
    )


def _stored_cards(mandate, blueprint, assessments: dict[str, int]) -> None:
    """Up to four stored records. A sparkline is drawn only from saved history."""
    names = {item["key"]: item["name"] for item in active_dimensions(mandate, blueprint)}
    history = load_assessment_history()
    cards: list[tuple[str, str, str, list[int]]] = [
        ("Time budget", f"{mandate.time_budget_hours_week:g} h/wk", "Saved mandate", []),
        ("Money budget", f"${mandate.money_budget_usd_month:g}/mo", "Saved mandate", []),
    ]
    checkin = load_daily_checkin(_today())
    if checkin:
        cards.append(("Energy", f"{int(checkin['energy'])}/5", "Today's check-in", []))
    for key, score in assessments.items():
        series = [int(row["scores"][key]) for row in history if key in row["scores"]]
        cards.append((names.get(key, key), f"{int(score)}/10", "Saved assessment", series))
        if len(cards) >= 4:
            break
    bits = []
    for label, value, source, series in cards[:4]:
        bits.append(
            "<div class='metric-card'>"
            f"<div class='k'>{html.escape(source)}</div>"
            f"<div class='v'>{html.escape(value)}</div>"
            f"<div class='s'>{html.escape(label)}</div>"
            f"{_spark(series)}"
            "</div>"
        )
    st.markdown(f"<div class='metric-row'>{''.join(bits)}</div>", unsafe_allow_html=True)


def _today_side(mandate) -> None:
    st.markdown("<p class='section-label'>Today</p>", unsafe_allow_html=True)
    checkin = load_daily_checkin(_today())
    st.markdown(daily_plan_text(checkin))
    if mandate.priorities:
        joined = ", ".join(str(item) for item in mandate.priorities)
        st.caption(f"Saved priorities: {joined}")


def _question(mandate, workflow) -> None:
    question = st.text_input(
        "Explore a decision or opportunity...",
        key="universe_question",
        placeholder="Explore a decision or opportunity...",
    )
    asked = st.session_state.setdefault("universe_answers", {})
    if st.button("Ask the office"):
        text = question.strip()
        if not text:
            st.warning("Write a question first.")
        elif text not in asked:
            sequence = None
            if workflow is not None and workflow.decision_plan is not None:
                sequence = list(workflow.decision_plan.recommended_sequence)
            result, record = ask_decision(
                text,
                mandate,
                client=LLMClient(get_settings()),
                workflow_sequence=sequence,
            )
            asked[text] = {"result": result, "call_id": record.call_id, "mode": record.mode}
        st.session_state["universe_shown"] = question.strip()
    shown = st.session_state.get("universe_shown")
    if shown and shown in asked:
        packet = asked[shown]
        answer = packet["result"].get("answer") or packet["result"].get("summary") or ""
        st.write(answer)


def _checkin() -> None:
    st.markdown("#### Today's check-in")
    saved = load_daily_checkin(_today())
    feeling = st.text_input("How are you feeling?", value=(saved or {}).get("feeling", ""))
    energy = st.number_input(
        "Energy (1–5)",
        min_value=1,
        max_value=5,
        value=int((saved or {}).get("energy", 3)),
        step=1,
    )
    must_do = st.text_input("Must-do today", value=(saved or {}).get("must_do", ""))
    responsibilities = st.text_input(
        "Responsibilities", value=(saved or {}).get("responsibilities", "")
    )
    surprises = st.text_area("Surprises", value=(saved or {}).get("surprises", ""), height=68)
    discretionary = st.number_input(
        "Discretionary hours",
        min_value=0.0,
        max_value=24.0,
        value=float((saved or {}).get("discretionary_hours", 0.0)),
        step=0.5,
    )
    if st.button("Save today's check-in"):
        payload = {
            "feeling": feeling.strip(),
            "energy": int(energy),
            "must_do": must_do.strip(),
            "responsibilities": responsibilities.strip(),
            "surprises": surprises.strip(),
            "discretionary_hours": float(discretionary),
        }
        save_daily_checkin(_today(), payload)
        saved = payload
        st.success("Check-in saved.")
    st.markdown(daily_plan_text(saved if saved else load_daily_checkin(_today())))


def _assessments(mandate, blueprint, assessments: dict[str, int]) -> None:
    st.markdown("#### Dimension assessments")
    st.caption("0–10, saved by you. The radar and the gaps read only what is saved.")
    dimensions = active_dimensions(mandate, blueprint)
    draft: dict[str, int] = {}
    for dimension in dimensions:
        current = assessments.get(dimension["key"], 0)
        draft[dimension["key"]] = int(
            st.slider(
                dimension["name"],
                min_value=0,
                max_value=10,
                value=int(current),
                key=f"assess_{dimension['key']}",
            )
        )
    if st.button("Save assessments"):
        save_assessments(draft)
        st.success("Assessments saved.")
        st.rerun()


def _charts(mandate, blueprint, assessments: dict[str, int]) -> None:
    dimensions = active_dimensions(mandate, blueprint)
    names = {item["key"]: item["name"] for item in dimensions}
    history = load_assessment_history()
    series_key = None
    best: list[dict] = []
    for key in names:
        points = [
            {"recorded_at": row["recorded_at"], "score": row["scores"][key]}
            for row in history
            if key in row["scores"]
        ]
        if len(points) > len(best):
            best = points
            series_key = key
    aspirations = load_aspirations()
    left, right = st.columns(2, gap="medium")
    with left:
        st.markdown("<p class='section-label'>Development trajectory</p>", unsafe_allow_html=True)
        if series_key and best:
            st.caption(names[series_key])
            st.plotly_chart(history_line(best), use_container_width=True)
        else:
            st.caption("No saved history yet.")
    with right:
        st.markdown("<p class='section-label'>Current and desired</p>", unsafe_allow_html=True)
        shown = False
        for key, name in names.items():
            current = assessments.get(key)
            desired = aspirations.get(key)
            if current is None and desired is None:
                continue
            st.caption(name)
            st.plotly_chart(dimension_levels(current, desired), use_container_width=True)
            shown = True
            break
        if not shown:
            gaps = capability_gaps(dimensions, assessments)
            if gaps:
                st.plotly_chart(capability_gap_chart(dimensions, assessments), use_container_width=True)
                st.caption(
                    "Gap = stored goal importance minus your saved assessment. "
                    "Unsaved dimensions are omitted."
                )
            else:
                st.caption("Nothing is saved for current or desired yet.")

    heat_col, spend_col = st.columns(2, gap="medium")
    with heat_col:
        st.markdown("<p class='section-label'>Opportunity stacking</p>", unsafe_allow_html=True)
        heat, heat_note = opportunity_heatmap(mandate)
        st.plotly_chart(heat, use_container_width=True)
        st.caption(heat_note)
    with spend_col:
        st.markdown("<p class='section-label'>Strategic spending</p>", unsafe_allow_html=True)
        st.caption(
            "These fields recalculate the labeled catalog. They do not change the saved mandate "
            "and they do not spend money."
        )
        hours = st.number_input(
            "Comparison time budget (hours / week)",
            min_value=0.0,
            value=float(mandate.time_budget_hours_week),
            step=1.0,
            key="compare_hours",
        )
        money = st.number_input(
            "Comparison money budget (USD / month)",
            min_value=0.0,
            value=float(mandate.money_budget_usd_month),
            step=50.0,
            key="compare_money",
        )
        spent, note = spending_comparison(mandate, hours, money)
        st.plotly_chart(spent, use_container_width=True)
        st.caption(note)
