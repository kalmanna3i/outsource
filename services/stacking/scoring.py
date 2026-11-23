"""Stacking scores without double-counting overlapping or speculative board guarantees."""

from __future__ import annotations

from core.models import (
    BenefitKind,
    ContributionLevel,
    DimensionContribution,
    LifeDimension,
    StackedOpportunity,
    StackingScore,
    _LEVEL_WEIGHT,
)

_BOARD_KEYWORDS = (
    "board seat",
    "board member",
    "nonprofit board",
    "infrastructure nonprofit board",
)


def _level_weight(level: ContributionLevel) -> float:
    return _LEVEL_WEIGHT[level]


def _is_board_career_overclaim(opp: StackedOpportunity, contrib: DimensionContribution) -> bool:
    label_lower = opp.label.lower()
    if not any(k in label_lower for k in _BOARD_KEYWORDS):
        return False
    if contrib.benefit_kind not in (BenefitKind.VERIFIED, BenefitKind.DIRECT):
        return False
    return contrib.dimension in (LifeDimension.COLLEAGUE, LifeDimension.MENTEE)


def compute_stacking_score(opp: StackedOpportunity) -> StackingScore:
    """Per-dimension effective weights; exclude OVERLAPPING from composite; warn on board hype."""
    per_dim: dict[str, float] = {}
    overlapping_excluded: list[str] = []
    speculative_warnings: list[str] = []

    for contrib in opp.dimensions:
        dim_key = contrib.dimension.value

        if contrib.benefit_kind == BenefitKind.OVERLAPPING:
            overlapping_excluded.append(
                f"{dim_key}: overlapping benefit — not added to composite (counts elsewhere)"
            )
            continue

        weight = _level_weight(contrib.level)

        if _is_board_career_overclaim(opp, contrib):
            speculative_warnings.append(
                f"{opp.label}: board-related role does not guarantee career advancement; "
                f"downgraded {dim_key} from {contrib.benefit_kind.value} to speculative."
            )
            weight *= 0.35

        if contrib.benefit_kind == BenefitKind.SPECULATIVE:
            weight *= 0.5
            speculative_warnings.append(f"{dim_key}: speculative benefit — discounted in composite")

        per_dim[dim_key] = max(per_dim.get(dim_key, 0.0), weight)

    composite = round(sum(per_dim.values()), 4)

    return StackingScore(
        opportunity_id=opp.opportunity_id,
        per_dimension=per_dim,
        composite=composite,
        overlapping_excluded=overlapping_excluded,
        speculative_warnings=speculative_warnings,
        labeled_illustrative=opp.labeled_illustrative,
    )


def count_unique_benefit_dimensions(contributions: list[DimensionContribution]) -> int:
    """Overlapping pairs should not inflate unique dimension count."""
    scored = set()
    for c in contributions:
        if c.benefit_kind == BenefitKind.OVERLAPPING:
            continue
        scored.add(c.dimension)
    return len(scored)