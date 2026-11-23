"""Deterministic mission alignment for contextual opportunities (Life Blueprint)."""

from __future__ import annotations

from core.contextual_models import ContextualOpportunity
from core.models import LifeBlueprint

# Per-scenario bindings — layover cards must not cite wedding / day-job obligations.
SCENARIO_RULES: dict[str, dict[str, object]] = {
    "ord_layover": {
        "domains": frozenset({"academic", "career"}),
        "blocked_goal_phrases": (
            "wedding",
            "insurance claim",
            "work obligation",
        ),
        "domain_keywords": {
            "academic": ("mba", "mgt", "409", "yale", "academic", "museum", "intellectual", "outsource", "demo"),
            "career": ("alumni", "network", "founder", "operator", "acquisition", "professional"),
        },
    },
    "boston_conference": {
        "domains": frozenset({"academic", "career"}),
        "blocked_goal_phrases": ("wedding", "insurance claim"),
        "domain_keywords": {
            "academic": ("mba", "lecture", "mit", "sloan", "academic", "research"),
            "career": ("founder", "entrepreneur", "network", "reputation", "post-mba", "pipeline"),
        },
    },
}


def score_alignment(
    opp: ContextualOpportunity,
    bp: LifeBlueprint,
    *,
    scenario_key: str | None = None,
) -> ContextualOpportunity:
    """Rule-based alignment scoped to the active demo scenario."""
    text = " ".join(
        [
            opp.why,
            opp.what,
            opp.who,
            " ".join(opp.strategic_benefits),
            opp.title,
        ]
    ).lower()
    rules = SCENARIO_RULES.get(scenario_key or "", {})
    allowed_domains: frozenset[str] = rules.get("domains", frozenset())  # type: ignore[assignment]
    blocked: tuple[str, ...] = rules.get("blocked_goal_phrases", ())  # type: ignore[assignment]
    domain_keywords: dict[str, tuple[str, ...]] = rules.get("domain_keywords", {})  # type: ignore[assignment]

    matched: list[str] = []
    score = 4.0
    for goal in bp.goals:
        gtitle = goal.title.lower()
        dom = goal.domain.lower()
        if blocked and any(p in gtitle for p in blocked):
            continue
        if allowed_domains and dom not in allowed_domains:
            continue
        keys = domain_keywords.get(dom, ())
        title_hit = any(w in text for w in gtitle.split() if len(w) > 4)
        keyword_hit = any(k in text for k in keys)
        if title_hit or keyword_hit:
            matched.append(goal.title)
            score += goal.importance * 0.35
    if opp.verification_status.value == "VERIFIED_SOURCE":
        score += 0.5
    if opp.feasibility_status == "feasible":
        score += 1.0
    elif opp.feasibility_status == "infeasible":
        score -= 2.0
    score = max(0.0, min(10.0, round(score, 1)))
    scope = f"scenario={scenario_key}" if scenario_key else "scenario=unspecified"
    reason = (
        f"Supports goals: {', '.join(matched) if matched else 'no goals matched for this scenario'}. "
        f"{scope}; feasibility={opp.feasibility_status}."
    )
    return opp.model_copy(update={"alignment_score": score, "mission_alignment_reason": reason})