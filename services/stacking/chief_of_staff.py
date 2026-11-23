"""Chief of Staff stacking recommendation vs a Life Mandate (deterministic demo logic)."""

from __future__ import annotations

from core.models import LifeMandateSample, StackedOpportunity, StackingRecommendation
from services.stacking.scoring import compute_stacking_score


def recommend_bundle(
    opportunities: list[StackedOpportunity],
    mandate: LifeMandateSample,
    separate_activity_labels: list[str] | None = None,
) -> StackingRecommendation:
    """Pick highest composite score among feasible (hours cap) opportunities."""
    separate = separate_activity_labels or [
        "Separate giving committee (illustrative)",
        "Separate mentor night (illustrative)",
        "Separate civic board prep (illustrative)",
        "Separate learning salon (illustrative)",
    ]
    feasible = [o for o in opportunities if o.monthly_hours <= mandate.max_monthly_hours]
    if not feasible:
        return StackingRecommendation(
            chosen_bundle_label="None feasible under mandate hours cap",
            rationale=["All illustrative opportunities exceed max_monthly_hours."],
            separate_activities_rejected=separate,
            mandate_fit_notes="Adjust mandate cap or reduce hours in fixtures.",
        )

    ranked = sorted(
        feasible,
        key=lambda o: (compute_stacking_score(o).composite, -o.monthly_hours),
        reverse=True,
    )
    best = ranked[0]
    score = compute_stacking_score(best)

    rationale = [
        f"Highest stacking composite ({score.composite}) among feasible bundles.",
        f"Fits {mandate.max_monthly_hours} hr/mo cap at {best.monthly_hours} hr/mo.",
        "Principles: strategic synergy, economies of scope, reciprocal value — "
        "friendships and colleagues are not instruments.",
    ]
    if score.speculative_warnings:
        rationale.append(
            "Caution: " + score.speculative_warnings[0]
        )

    return StackingRecommendation(
        chosen_bundle_label=best.label,
        rationale=rationale,
        separate_activities_rejected=separate,
        mandate_fit_notes="; ".join(mandate.priorities[:2]),
    )