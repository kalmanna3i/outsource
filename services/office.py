"""Executive-office scores, portfolio, dinner spend, and a short agent handoff.

Deterministic scores do not use the model. The model may narrate or choose among
a labeled dataset. It does not set the winner by a constant in source, and it
does not rewrite the mission.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from agents.office_agents import DiscoveryChooserAgent, QualityAuditorAgent, StrengthGapAgent
from core.llm import LLMClient
from core.mandate import LifeMandate, MandateStatus, approved_citations, name_conflicts
from core.models import (
    BenefitKind,
    CalendarSlot,
    ContributionLevel,
    DimensionContribution,
    EvidenceType,
    LifeDimension,
    MatrixCell,
    MatrixColumn,
    StackedOpportunity,
    new_id,
)
from services.scheduler import export_ics
from services.stacking.scoring import compute_stacking_score

# Keyword map for free-text priorities. First matching themes receive that rank's weight.
_THEMES: dict[str, tuple[str, ...]] = {
    "coursework": ("course", "mba", "academic", "homework", "class"),
    "philanthropy": ("philanthrop", "giving", "nonprofit", "community", "foundation"),
    "friendship": ("friend", "relationship"),
    "health": ("health", "sleep"),
    "recovery": ("recovery", "rest", "energy"),
    "pet": ("pet", "dog"),
    "infrastructure": ("infrastructure", "operator", "company"),
    "investment": ("invest", "capital", "fund"),
    "travel": ("travel", "conference", "trip"),
    "home": ("home", "house", "apartment"),
    "prestige": ("prestige", "gala", "status"),
}

_FLAVORS = ("exceptional", "amazing", "world-class", "outstanding", "incredible", "genius")
_DIAGNOSIS = ("diagnosed with", "you have depression", "clinical diagnosis", "anxiety disorder")


@dataclass(frozen=True)
class CatalogItem:
    item_id: str
    label: str
    summary: str
    tags: dict[str, float]
    hours_week: float
    cash_usd: float
    mandatory: bool
    stacking_themes: tuple[str, ...]
    overlapping_themes: tuple[str, ...]
    evidence_id: str
    conflict_keywords: tuple[str, ...] = ()
    philanthropic: bool = False
    matrix: dict[str, str] = field(default_factory=dict)

    @property
    def evidence_type(self) -> str:
        return "LABELED_DATASET"

    @property
    def source_label(self) -> str:
        return (
            "LABELED DATASET — authored scenario record for fictional executive "
            "Amina Okonkwo. Not a live web fetch, not a testimonial, not a verified public source."
        )


def _item(**kwargs: Any) -> CatalogItem:
    tags = dict(kwargs.pop("tags"))
    matrix = dict(kwargs.pop("matrix", {}))
    return CatalogItem(tags=tags, matrix=matrix, **kwargs)


# Discretionary winners are ranked from priorities. No item is marked recommended=True here.
CATALOG: tuple[CatalogItem, ...] = (
    _item(
        item_id="mba-coursework",
        label="MBA coursework block",
        summary="Protected time for the deadline-week assignment. User-stated, not graded by the model.",
        tags={"coursework": 1.0},
        hours_week=5,
        cash_usd=0,
        mandatory=True,
        stacking_themes=("coursework",),
        overlapping_themes=(),
        evidence_id="ds-course",
    ),
    _item(
        item_id="dog-care",
        label="Dog care",
        summary="Walks and feeding for the household dog. A commitment, not a productivity hack.",
        tags={"pet": 1.0, "friendship": 0.2, "recovery": 0.2},
        hours_week=3.5,
        cash_usd=25,
        mandatory=True,
        stacking_themes=("pet",),
        overlapping_themes=(),
        evidence_id="ds-pet",
    ),
    _item(
        item_id="recovery-block",
        label="Recovery evenings",
        summary="User-stated early nights. Not a diagnosis and not optional this week.",
        tags={"health": 1.0, "recovery": 1.0},
        hours_week=5,
        cash_usd=0,
        mandatory=True,
        stacking_themes=("recovery",),
        overlapping_themes=(),
        evidence_id="ds-health",
    ),
    _item(
        item_id="home-upkeep",
        label="Home upkeep",
        summary="Apartment filter and the dog's water. Household, not a project plan.",
        tags={"home": 1.0, "pet": 0.3},
        hours_week=0.5,
        cash_usd=0,
        mandatory=True,
        stacking_themes=("home",),
        overlapping_themes=("pet",),
        evidence_id="ds-home",
    ),
    _item(
        item_id="home-dinner",
        label="Home dinner with friends and a community-foundation introduction",
        summary=(
            "One evening at home. Friendship is the point. A community-foundation introduction "
            "can share the table. Hours are counted once."
        ),
        tags={"friendship": 1.0, "philanthropy": 0.6, "home": 0.4},
        hours_week=3,
        cash_usd=55,
        mandatory=False,
        stacking_themes=("friendship", "philanthropy", "home"),
        overlapping_themes=(),
        evidence_id="ds-dinner",
        matrix={"giving_back": "moderate", "network": "moderate", "learning": "limited"},
    ),
    _item(
        item_id="infra-nonprofit",
        label="Infrastructure nonprofit committee (stacked)",
        summary=(
            "One committee that uses infrastructure judgment for a community organization. "
            "Colleague overlap with the day job is overlapping and is not a second benefit."
        ),
        tags={"philanthropy": 1.0, "infrastructure": 0.8, "learning": 0.5},
        hours_week=4,
        cash_usd=0,
        mandatory=False,
        stacking_themes=("philanthropy", "infrastructure", "learning"),
        overlapping_themes=("colleague",),
        evidence_id="ds-philanthropy",
        philanthropic=True,
        matrix={
            "giving_back": "strong",
            "career": "limited",
            "learning": "moderate",
            "business": "moderate",
            "network": "limited",
        },
    ),
    _item(
        item_id="site-seminar",
        label="Infrastructure site seminar",
        summary="A two-hour local seminar. Useful for the company and slightly for class.",
        tags={"infrastructure": 1.0, "coursework": 0.3},
        hours_week=2,
        cash_usd=0,
        mandatory=False,
        stacking_themes=("infrastructure", "coursework"),
        overlapping_themes=(),
        evidence_id="ds-seminar",
    ),
    _item(
        item_id="fund-memo",
        label="Read one infrastructure-fund memo",
        summary="A labeled reading. Not investment advice and not a recommendation to buy a security.",
        tags={"investment": 1.0, "infrastructure": 0.4},
        hours_week=1,
        cash_usd=0,
        mandatory=False,
        stacking_themes=("investment",),
        overlapping_themes=("infrastructure",),
        evidence_id="ds-invest",
    ),
    _item(
        item_id="conference-travel",
        label="Out-of-town infrastructure conference",
        summary="Travel during deadline week. Conflicts with the no-travel nonnegotiable when that rule is approved.",
        tags={"travel": 1.0, "infrastructure": 0.4},
        hours_week=16,
        cash_usd=900,
        mandatory=False,
        stacking_themes=("travel",),
        overlapping_themes=(),
        evidence_id="ds-travel",
        conflict_keywords=("travel", "deadline"),
    ),
    _item(
        item_id="prestige-gala",
        label="Prestige gala",
        summary="A high-cash evening with no tie to the approved priorities unless the user adds prestige.",
        tags={"prestige": 1.0},
        hours_week=4,
        cash_usd=350,
        mandatory=False,
        stacking_themes=(),
        overlapping_themes=(),
        evidence_id="ds-gala",
    ),
)


def themes_in(text: str) -> list[str]:
    lowered = text.lower()
    found = []
    for theme, words in _THEMES.items():
        if any(word in lowered for word in words):
            found.append(theme)
    return found


def priority_weights(priorities: list[str]) -> dict[str, float]:
    weights: dict[str, float] = {}
    usable = [p for p in priorities if p and p.strip()]
    count = len(usable)
    if count == 0:
        return weights
    for index, text in enumerate(usable):
        weight = (count - index) / count
        for theme in themes_in(text):
            weights[theme] = max(weights.get(theme, 0.0), weight)
    return weights


def strategic_value(item: CatalogItem, mandate: LifeMandate) -> float:
    """0–100 alignment with ordered priorities. Confidence is not a factor."""
    weights = priority_weights(mandate.priorities)
    if not weights:
        return 0.0
    numerator = sum(item.tags.get(theme, 0.0) * weight for theme, weight in weights.items())
    return round(100.0 * numerator / sum(weights.values()), 2)


def stacking_factor(item: CatalogItem) -> float:
    """Unique non-overlapping themes, capped at 4. Overlap does not add."""
    unique = [theme for theme in item.stacking_themes if theme not in item.overlapping_themes]
    return round(min(len(unique) / 4.0, 1.0), 2)


def confidence_for(item: CatalogItem) -> float:
    """Separate from value. A labeled dataset is not a verified source."""
    if item.evidence_type == "USER_PROVIDED":
        return 0.9
    if item.evidence_type == "LABELED_DATASET":
        return 0.45
    return 0.3


def item_conflicts(item: CatalogItem, mandate: LifeMandate) -> list[str]:
    return name_conflicts(item.label, list(item.conflict_keywords), mandate)


def rank_discretionary(mandate: LifeMandate, items: tuple[CatalogItem, ...] = CATALOG) -> list[CatalogItem]:
    discretionary = [item for item in items if not item.mandatory]
    return sorted(
        discretionary,
        key=lambda item: (strategic_value(item, mandate), -item.hours_week),
        reverse=True,
    )


@dataclass
class Recommendation:
    chosen_id: str
    chosen_label: str
    strategic_value: float
    citations: list[str]
    conflicts: list[str]
    mission: str
    used_approved: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def recommend(mandate: LifeMandate, items: tuple[CatalogItem, ...] = CATALOG) -> Recommendation:
    ranked = rank_discretionary(mandate, items)
    top = ranked[0]
    return Recommendation(
        chosen_id=top.item_id,
        chosen_label=top.label,
        strategic_value=strategic_value(top, mandate),
        citations=approved_citations(mandate),
        conflicts=item_conflicts(top, mandate),
        mission=mandate.mission,
        used_approved=mandate.status == MandateStatus.APPROVED,
    )


def score_cards(mandate: LifeMandate, selected_ids: set[str]) -> list[dict[str, Any]]:
    cards = []
    for item in CATALOG:
        value = strategic_value(item, mandate)
        selected = item.item_id in selected_ids or item.mandatory
        missed = 0.0 if selected else value
        cards.append(
            {
                "item_id": item.item_id,
                "label": item.label,
                "strategic_value": value,
                "missed_opportunity": missed,
                "stacking_factor": stacking_factor(item),
                "confidence": confidence_for(item),
                "mandatory": item.mandatory,
                "conflicts": item_conflicts(item, mandate),
                "evidence_id": item.evidence_id,
                "evidence_type": item.evidence_type,
                "source_label": item.source_label,
            }
        )
    return cards


UNSCHEDULED_RESERVE_HOURS = 1.0


def optimize_portfolio(mandate: LifeMandate) -> dict[str, Any]:
    """Constraints first. Mandatory commitments are kept even when a higher score wants their hours."""
    weekly_cash = round(mandate.money_budget_usd_month / 4.0, 2)
    mandatory = [item for item in CATALOG if item.mandatory]
    mandatory_hours = round(sum(item.hours_week for item in mandatory), 2)
    mandatory_cash = round(sum(item.cash_usd for item in mandatory), 2)
    room_hours = round(
        mandate.time_budget_hours_week - mandatory_hours - UNSCHEDULED_RESERVE_HOURS,
        2,
    )
    room_cash = round(weekly_cash - mandatory_cash, 2)
    notes = [
        "Mandatory commitments are reserved first and are not dropped to raise a score.",
        f"{UNSCHEDULED_RESERVE_HOURS:g} hour(s) stay unscheduled on purpose.",
        "Weekly cash envelope is money_budget_usd_month / 4. That division is a MODELED_ASSUMPTION.",
    ]
    if room_hours < 0 or room_cash < 0:
        notes.append(
            "Mandatory commitments already exceed the stated budget. "
            "They stay on the plan. No discretionary item is added."
        )
        room_hours = min(room_hours, 0)
        room_cash = min(room_cash, 0)
    selected: list[str] = [item.item_id for item in mandatory]
    held: list[dict[str, str]] = []
    hours_left = max(room_hours, 0)
    cash_left = max(room_cash, 0)
    for item in rank_discretionary(mandate):
        value = strategic_value(item, mandate)
        conflicts = item_conflicts(item, mandate)
        if value <= 0:
            continue
        if conflicts:
            held.append(
                {
                    "item_id": item.item_id,
                    "reason": conflicts[0],
                    "scheduled": "no",
                }
            )
            continue
        if item.hours_week > hours_left + 1e-9 or item.cash_usd > cash_left + 1e-9:
            held.append(
                {
                    "item_id": item.item_id,
                    "reason": (
                        f"Does not fit remaining hours ({hours_left:g}) or weekly cash (${cash_left:g}) "
                        "after mandatory commitments and the unscheduled reserve."
                    ),
                    "scheduled": "no",
                }
            )
            continue
        selected.append(item.item_id)
        hours_left = round(hours_left - item.hours_week, 2)
        cash_left = round(cash_left - item.cash_usd, 2)
    return {
        "mandatory_ids": [item.item_id for item in mandatory],
        "selected_ids": selected,
        "not_scheduled": held,
        "hours_left_unscheduled": round(hours_left + UNSCHEDULED_RESERVE_HOURS, 2),
        "weekly_cash_left": cash_left,
        "weekly_cash_envelope": weekly_cash,
        "notes": notes,
        "label": "OPERATIONAL",
    }


def philanthropic_stack() -> dict[str, Any]:
    """One stacked philanthropic opportunity. Overlapping colleague credit is excluded."""
    item = next(entry for entry in CATALOG if entry.item_id == "infra-nonprofit")
    opportunity = StackedOpportunity(
        label=item.label,
        labeled_illustrative=True,
        monthly_hours=item.hours_week * 4,
        dimensions=[
            DimensionContribution(
                dimension=LifeDimension.PHILANTHROPIST,
                level=ContributionLevel.STRONG,
                benefit_kind=BenefitKind.DIRECT,
                rationale="Time and infrastructure judgment given to the organization.",
            ),
            DimensionContribution(
                dimension=LifeDimension.COMMUNITY_MEMBER,
                level=ContributionLevel.MODERATE,
                benefit_kind=BenefitKind.COMPLEMENTARY,
                rationale="Community benefit is related but not the same hour counted twice.",
            ),
            DimensionContribution(
                dimension=LifeDimension.COLLEAGUE,
                level=ContributionLevel.LIMITED,
                benefit_kind=BenefitKind.OVERLAPPING,
                rationale="Day-job overlap. Not an extra career benefit.",
            ),
            DimensionContribution(
                dimension=LifeDimension.MENTOR,
                level=ContributionLevel.LIMITED,
                benefit_kind=BenefitKind.SPECULATIVE,
                rationale="Mentoring might happen. It is not promised.",
            ),
        ],
        matrix=[
            MatrixCell(column=MatrixColumn.GIVING_BACK, level=ContributionLevel.STRONG, benefit_kind=BenefitKind.DIRECT),
            MatrixCell(column=MatrixColumn.CAREER, level=ContributionLevel.LIMITED, benefit_kind=BenefitKind.SPECULATIVE),
            MatrixCell(column=MatrixColumn.LEARNING, level=ContributionLevel.MODERATE, benefit_kind=BenefitKind.DIRECT),
            MatrixCell(column=MatrixColumn.BUSINESS, level=ContributionLevel.MODERATE, benefit_kind=BenefitKind.INDIRECT),
            MatrixCell(column=MatrixColumn.NETWORK, level=ContributionLevel.LIMITED, benefit_kind=BenefitKind.OVERLAPPING),
        ],
        reciprocal_value="The organization receives operator time. The user does not extract a board seat as a prize.",
    )
    score = compute_stacking_score(opportunity)
    return {
        "label": "SIMULATED",
        "opportunity": item.label,
        "evidence_id": item.evidence_id,
        "source_label": item.source_label,
        "matrix": [
            {"column": cell.column.value, "level": cell.level.value, "benefit_kind": cell.benefit_kind.value}
            for cell in opportunity.matrix
        ],
        "stacking_score": score.model_dump(),
        "colleague_excluded": any("colleague" in line for line in score.overlapping_excluded),
    }


def dinner_spend() -> dict[str, Any]:
    """Cash and hours across periods. The difference is an assumption, not savings achieved."""
    restaurant = {"id": "restaurant", "label": "Restaurant dinner for two friends", "cash_usd": 140.0, "hours": 2.5, "themes": ["friendship"]}
    home = {
        "id": "home-dinner",
        "label": "Home dinner with friends and a community-foundation introduction",
        "cash_usd": 55.0,
        "hours": 3.0,
        "themes": ["friendship", "philanthropy", "home"],
    }
    cadence = {"once": 1, "month": 2, "quarter": 6, "year": 24}
    rows = []
    for period, times in cadence.items():
        rows.append(
            {
                "period": period,
                "evenings_assumed": times,
                "restaurant_cash_usd": round(restaurant["cash_usd"] * times, 2),
                "restaurant_hours": round(restaurant["hours"] * times, 2),
                "home_cash_usd": round(home["cash_usd"] * times, 2),
                "home_hours": round(home["hours"] * times, 2),
                "cash_difference_usd": round((restaurant["cash_usd"] - home["cash_usd"]) * times, 2),
                "evidence_type": EvidenceType.MODELED_ASSUMPTION.value,
            }
        )
    return {
        "label": "SIMULATED",
        "assumption": (
            "Cadence is a model: once, then 2 evenings a month, 6 a quarter, 24 a year. "
            "Home hours are counted once even though the evening touches friendship, philanthropy, and home. "
            "The cash difference is arithmetic under that assumption, not money already saved."
        ),
        "options": [restaurant, home],
        "periods": rows,
    }


def make_or_buy(mandate: LifeMandate) -> dict[str, Any]:
    """Cash stays in dollars. Opportunity cost stays in hours and in the named constraint."""
    citations = approved_citations(mandate)
    make_hours = 3.0
    buy_cash = 180.0
    buy_hours = 0.5
    discretionary_room = max(
        mandate.time_budget_hours_week - 14.0 - UNSCHEDULED_RESERVE_HOURS,
        0,
    )
    scarce = "time" if make_hours > discretionary_room else "neither binding in this sketch"
    if mandate.money_budget_usd_month < buy_cash:
        scarce = "money"
    return {
        "label": "OPERATIONAL",
        "task": "Two-page infrastructure briefing for class",
        "make": {
            "cash_usd": 0.0,
            "hours": make_hours,
            "opportunity_cost": (
                f"{make_hours:g} hours from the weekly discretionary pool. "
                "Not taken from dog care or the recovery block. Not converted into a dollar wage."
            ),
        },
        "buy": {
            "cash_usd": buy_cash,
            "hours": buy_hours,
            "opportunity_cost": (
                f"${buy_cash:.0f} cash from the monthly money budget, plus {buy_hours:g} hours to review. "
                "The dollars are not added to the hours and are not called savings."
            ),
        },
        "cash_separate_from_opportunity_cost": True,
        "scarce_constraint": scarce,
        "suggestion": (
            "The user chooses. OUTSOURCE does not purchase the briefing and does not hire anyone. "
            f"The binding constraint in this sketch is {scarce}."
        ),
        "cited_mandate": citations,
        "purchase_made": False,
    }


def _itinerary(selected_ids: set[str], now: datetime) -> list[dict[str, str]]:
    """A sparse week. Open blocks are intentional."""
    blocks = [
        ("Mon 18:00–19:30", "recovery-block", "Recovery evening (user-stated)"),
        ("Tue 19:00–21:00", "mba-coursework", "Coursework block"),
        ("Wed 07:00–07:30", "dog-care", "Dog walk"),
        ("Wed 20:00–20:30", "home-upkeep", "Home upkeep"),
        ("Thu evening", "infra-nonprofit", "Nonprofit committee, only if selected"),
        ("Fri evening", "home-dinner", "Home dinner, only if selected"),
        ("Sat", "site-seminar", "Site seminar, only if selected"),
        ("Sun afternoon", "", "Unscheduled on purpose"),
    ]
    rows = []
    for when, item_id, title in blocks:
        if item_id and item_id not in selected_ids:
            continue
        rows.append({"when": when, "item_id": item_id or "open", "title": title, "anchor": now.date().isoformat()})
    return rows


def _outreach() -> dict[str, Any]:
    return {
        "status": "DRAFT_NOT_SENT",
        "outreach_sent": False,
        "email_sent": False,
        "to": "committee coordinator (fictional, not a real inbox)",
        "subject": "Question about the infrastructure committee — not sent",
        "body": (
            "Hello — I am an MBA student working in infrastructure. I am considering one committee "
            "conversation this month, after my coursework deadline. I have not committed. "
            "This draft was not sent."
        ),
    }


def _brief(mission: str) -> str:
    return (
        "PRIVATE-ONLY brief. You decide whether to have the committee conversation. "
        "The outreach draft was not sent. No money was spent. "
        f"Mission left as you wrote it: {mission}"
    )


_STRENGTH_FIXTURE = {
    "strengths": [
        {
            "note": "The mandate already names dog care and a recovery block as commitments.",
            "evidence_id": "ds-pet",
            "confidence": 0.45,
        }
    ],
    "gaps": [
        {
            "note": "Deadline-week coursework and the out-of-town conference cannot both fit.",
            "evidence_id": "ds-course",
            "confidence": 0.45,
        }
    ],
    "opportunities": [
        {
            "note": "One nonprofit committee can carry philanthropy and infrastructure together.",
            "evidence_id": "ds-philanthropy",
            "confidence": 0.45,
        }
    ],
    "threats": [
        {
            "note": "The conference asks for travel and cash the week the nonnegotiable forbids travel.",
            "evidence_id": "ds-travel",
            "confidence": 0.45,
        }
    ],
    "tows": [
        {"pair": "SO", "note": "Infrastructure judgment and one committee share an evening (ds-philanthropy)."},
        {"pair": "WO", "note": "Scarce hours make the conference the item to leave (ds-travel, ds-course)."},
        {"pair": "ST", "note": "A home dinner can include one foundation introduction without a second night (ds-dinner)."},
        {"pair": "WT", "note": "The money budget does not cover both the gala and the conference (ds-gala, ds-travel)."},
    ],
    "no_diagnosis": True,
    "flattery_avoided": True,
}


def _discovery_fixture(mandate: LifeMandate) -> dict[str, Any]:
    ranked = rank_discretionary(mandate)
    best = ranked[0]
    second = ranked[1] if len(ranked) > 1 else None
    return {
        "chosen_id": best.item_id,
        "rationale": (
            "Demo path echoes the deterministic rank from the approved priority order. "
            "The winner is not a constant in source."
        ),
        "cited_mandate_items": approved_citations(mandate),
        "conflicts": item_conflicts(best, mandate),
        "alternative_id": second.item_id if second else None,
    }


def _quality_fixture() -> dict[str, Any]:
    return {
        "verdict": "PASS",
        "findings": [],
        "mission_unchanged": True,
        "unsupported_claims": [],
        "email_sent": False,
        "purchase_made": False,
    }


def discovery_prompt(mandate: LifeMandate) -> str:
    lines = []
    for item in CATALOG:
        if item.mandatory:
            continue
        lines.append(
            f"- id={item.item_id}: {item.label}. {item.summary} "
            f"hours_week={item.hours_week} cash_usd={item.cash_usd} evidence={item.evidence_id}"
        )
    return (
        "Choose exactly one discretionary id from the list. Do not invent an id. "
        "Quote approved mandate lines you rely on. Name conflicts with nonnegotiables. "
        "Do not rewrite the mission. Do not flatter. Do not diagnose. "
        "Return JSON keys: chosen_id, rationale, cited_mandate_items, conflicts, alternative_id.\n"
        f"Approved mission (do not change it): {mandate.mission}\n"
        f"Priorities in order: {mandate.priorities}\n"
        f"Nonnegotiables: {mandate.nonnegotiables}\n"
        f"Success is the user's sentence: {mandate.success_definition}\n"
        + "\n".join(lines)
    )


def run_office(
    llm: LLMClient,
    mandate: LifeMandate,
    *,
    now: datetime | None = None,
    ics_dir: Path | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    """Three model calls, then deterministic scheduling. Not every specialist."""
    now = now or datetime.now()
    run_id = run_id or new_id("office")
    mission_before = mandate.mission
    portfolio = optimize_portfolio(mandate)
    selected = set(portfolio["selected_ids"])
    preference = recommend(mandate)
    stack = philanthropic_stack()
    spend = dinner_spend()
    buy = make_or_buy(mandate)
    known_ids = {item.item_id for item in CATALOG}

    strength_agent = StrengthGapAgent(llm)
    strength, rec_s = strength_agent.run(
        "Write a SWOT/TOWS note that cites evidence ids from the labeled dataset only. "
        f"Mission, which you must not rewrite: {mandate.mission}",
        _STRENGTH_FIXTURE,
        handoff_to="D01",
        run_id=run_id,
    )
    chooser = DiscoveryChooserAgent(llm)
    choice, rec_d = chooser.run(
        discovery_prompt(mandate),
        _discovery_fixture(mandate),
        handoff_to="Q01",
        run_id=run_id,
    )
    model_choice = str(choice.get("chosen_id") or "")
    model_choice_valid = model_choice in known_ids

    outreach = _outreach()
    brief = _brief(mission_before)
    start = (now + timedelta(hours=2)).replace(minute=0, second=0, microsecond=0)
    slot = CalendarSlot(
        title="Coursework block",
        start=start,
        end=start + timedelta(minutes=90),
        public_description="Personal coursework block — details in OUTSOURCE private brief",
        private_brief_ref=run_id,
    )
    ics_path = None
    if ics_dir is not None:
        ics_path = str(export_ics(slot, ics_dir / f"{slot.slot_id}.ics"))

    package_for_audit = {
        "mission": mission_before,
        "deterministic_choice": preference.chosen_id,
        "model_choice": model_choice,
        "model_choice_valid": model_choice_valid,
        "selected_ids": portfolio["selected_ids"],
        "outreach_sent": False,
        "email_sent": False,
        "purchase_made": False,
        "strength_evidence": _evidence_ids(strength),
    }
    auditor = QualityAuditorAgent(llm)
    audit, rec_q = auditor.run(
        "Review this package. Do not rewrite the mission. Flag unlabeled facts, flattery, "
        f"diagnosis, sent email, or a purchase. Package: {package_for_audit}",
        _quality_fixture(),
        handoff_to=None,
        run_id=run_id,
    )
    checks = deterministic_quality_checks(
        mission_before=mission_before,
        mission_after=mandate.mission,
        outreach=outreach,
        brief=brief,
        ics_path=ics_path,
        strength=strength,
        status="WAITING_RESULT",
        user_result=None,
        citations=preference.citations,
        mandate_approved=mandate.status == MandateStatus.APPROVED,
    )
    return {
        "run_id": run_id,
        "status": "WAITING_RESULT",
        "label_model": "OPERATIONAL" if rec_s.mode == "live" else "SIMULATED",
        "label_dataset": "SIMULATED",
        "label_scores": "OPERATIONAL",
        "persona": "Fictional MBA executive Amina Okonkwo. Infrastructure company, not a real user.",
        "mission": mission_before,
        "mission_unchanged": mandate.mission == mission_before,
        "mandate_status": mandate.status.value,
        "citations": preference.citations,
        "deterministic_recommendation": preference.to_dict(),
        "model_choice": {
            "chosen_id": model_choice,
            "valid": model_choice_valid,
            "payload": choice,
            "note": (
                "Invalid model id was not written into the mission and was not scheduled by force."
                if not model_choice_valid
                else "Model choice recorded beside the constraint-first portfolio."
            ),
        },
        "scores": score_cards(mandate, selected),
        "portfolio": portfolio,
        "philanthropy": stack,
        "matrix": stack["matrix"],
        "dinner": spend,
        "make_or_buy": buy,
        "itinerary": _itinerary(selected, now),
        "outreach": outreach,
        "human_brief": brief,
        "ics_path": ics_path,
        "strength_gap": strength,
        "discovery_accepted": True,
        "quality_agent": audit,
        "quality_checks": checks,
        "agent_calls": [rec_s.model_dump(mode="json"), rec_d.model_dump(mode="json"), rec_q.model_dump(mode="json")],
        "agents_invoked": ["S01", "D01", "Q01"],
        "email_sent": False,
        "purchase_made": False,
        "outreach_sent": False,
        "user_result": None,
        "external_actions_completed": False,
    }


def resume_office(package: dict[str, Any], user_result: str) -> dict[str, Any]:
    if not user_result or not user_result.strip():
        raise ValueError("A human result is required. The office does not mark the work finished.")
    updated = dict(package)
    updated["user_result"] = user_result.strip()
    updated["status"] = "RESOLVED_WITH_USER"
    updated["external_actions_completed"] = False
    updated["email_sent"] = False
    updated["purchase_made"] = False
    updated["outreach_sent"] = False
    updated["quality_checks"] = deterministic_quality_checks(
        mission_before=package["mission"],
        mission_after=package["mission"],
        outreach=package["outreach"],
        brief=package["human_brief"],
        ics_path=package.get("ics_path"),
        strength=package["strength_gap"],
        status=updated["status"],
        user_result=updated["user_result"],
        citations=package["citations"],
        mandate_approved=package["mandate_status"] == "APPROVED",
    )
    return updated


def reject_discovery(package: dict[str, Any]) -> dict[str, Any]:
    updated = dict(package)
    updated["discovery_accepted"] = False
    note = dict(updated.get("strength_gap") or {})
    note["rejected_by_user"] = True
    updated["strength_gap"] = note
    return updated


def _evidence_ids(strength: dict[str, Any]) -> list[str]:
    found = []
    for key in ("strengths", "gaps", "opportunities", "threats"):
        for row in strength.get(key) or []:
            if isinstance(row, dict) and row.get("evidence_id"):
                found.append(str(row["evidence_id"]))
    return found


def deterministic_quality_checks(
    *,
    mission_before: str,
    mission_after: str,
    outreach: dict[str, Any],
    brief: str,
    ics_path: str | None,
    strength: dict[str, Any],
    status: str,
    user_result: str | None,
    citations: list[str],
    mandate_approved: bool,
) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if outreach.get("outreach_sent") or outreach.get("email_sent"):
        findings.append({"severity": "error", "note": "Outreach or email is marked sent."})
    if outreach.get("status") != "DRAFT_NOT_SENT":
        findings.append({"severity": "error", "note": "Outreach status is not DRAFT_NOT_SENT."})
    if mission_after != mission_before:
        findings.append({"severity": "error", "note": "Mission text changed."})
    if status == "COMPLETED" or (status == "RESOLVED_WITH_USER" and not user_result):
        findings.append({"severity": "error", "note": "Completion without a user result."})
    if status == "WAITING_RESULT" and user_result:
        findings.append({"severity": "error", "note": "User result stored while still waiting."})
    blob = " ".join(
        str(row.get("note", ""))
        for key in ("strengths", "gaps", "opportunities", "threats")
        for row in (strength.get(key) or [])
        if isinstance(row, dict)
    ).lower()
    for word in _FLAVORS:
        if word in blob:
            findings.append({"severity": "warn", "note": f"Flattery word present: {word}"})
    for phrase in _DIAGNOSIS:
        if phrase in blob:
            findings.append({"severity": "error", "note": f"Diagnosis language present: {phrase}"})
    known = {item.evidence_id for item in CATALOG}
    for evidence_id in _evidence_ids(strength):
        if evidence_id not in known:
            findings.append({"severity": "error", "note": f"Evidence id {evidence_id} is not in the labeled dataset."})
    if mandate_approved and not citations:
        findings.append({"severity": "error", "note": "Approved mandate produced no citations."})
    if ics_path and Path(ics_path).exists():
        ics_text = Path(ics_path).read_text(encoding="utf-8")
        if "PRIVATE-ONLY" in ics_text or "BEGIN:VCALENDAR" not in ics_text:
            findings.append({"severity": "error", "note": "ICS contains the private brief or is not a calendar file."})
    if "PRIVATE-ONLY" not in brief:
        findings.append({"severity": "warn", "note": "Human brief is missing its private marker."})
    return findings
