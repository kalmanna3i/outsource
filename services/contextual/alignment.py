"""Deterministic mission alignment for contextual opportunities (Life Blueprint)."""

from __future__ import annotations

from core.contextual_models import ContextualOpportunity
from core.models import LifeBlueprint


def score_alignment(opp: ContextualOpportunity, bp: LifeBlueprint) -> ContextualOpportunity:
    """Rule-based alignment — no radar dependency."""
    text = " ".join(
        [
            opp.why,
            opp.what,
            " ".join(opp.strategic_benefits),
            opp.title,
        ]
    ).lower()
    domains: dict[str, list[str]] = {
        "academic": ["mba", "yale", "academic", "research", "lecture", "som"],
        "career": ["career", "founder", "operator", "acquisition", "professional", "network"],
        "relationships": ["alumni", "friend", "wedding", "relationship"],
        "financial": ["insurance", "cash", "cost", "acquisition"],
        "entrepreneurship": ["entrepreneur", "startup", "outsource", "ai-enabled"],
    }
    matched: list[str] = []
    score = 4.0
    for goal in bp.goals:
        gtitle = goal.title.lower()
        dom = goal.domain.lower()
        keys = domains.get(dom, [])
        if any(k in text for k in keys) or dom in text:
            matched.append(goal.title)
            score += goal.importance * 0.35
    if opp.verification_status.value == "VERIFIED_SOURCE":
        score += 0.5
    if opp.feasibility_status == "feasible":
        score += 1.0
    elif opp.feasibility_status == "infeasible":
        score -= 2.0
    score = max(0.0, min(10.0, round(score, 1)))
    reason = (
        f"Supports goals: {', '.join(matched) if matched else 'general mission fit (weak keyword match)'}. "
        f"Feasibility={opp.feasibility_status}."
    )
    return opp.model_copy(update={"alignment_score": score, "mission_alignment_reason": reason})