"""Stacking score tests — no double-count, board not guaranteed advancement."""

from core.models import (
    BenefitKind,
    ContributionLevel,
    DimensionContribution,
    LifeDimension,
    StackedOpportunity,
)
from services.stacking.fixtures import ILLUSTRATIVE_OPPORTUNITIES
from services.stacking.scoring import compute_stacking_score, count_unique_benefit_dimensions


def test_overlapping_friend_not_inflates_composite() -> None:
    mentor_opp = next(
        o for o in ILLUSTRATIVE_OPPORTUNITIES if "mentor program" in o.label.lower()
    )
    score = compute_stacking_score(mentor_opp)
    assert score.overlapping_excluded
    without_friend = [
        c for c in mentor_opp.dimensions if c.dimension != LifeDimension.FRIEND
    ]
    assert count_unique_benefit_dimensions(mentor_opp.dimensions) == count_unique_benefit_dimensions(
        without_friend
    )
    assert LifeDimension.FRIEND.value not in score.per_dimension or score.per_dimension.get(
        LifeDimension.FRIEND.value, 0
    ) == 0


def test_board_seat_warns_not_guaranteed_career() -> None:
    board = next(o for o in ILLUSTRATIVE_OPPORTUNITIES if "nonprofit board" in o.label.lower())
    score = compute_stacking_score(board)
    assert any("does not guarantee" in w for w in score.speculative_warnings)
    colleague_weight = score.per_dimension.get(LifeDimension.COLLEAGUE.value, 1.0)
    assert colleague_weight < 0.6


def test_double_direct_same_dimension_keeps_max_not_sum() -> None:
    opp = StackedOpportunity(
        label="Illustrative — test double",
        monthly_hours=1,
        dimensions=[
            DimensionContribution(
                dimension=LifeDimension.MENTOR,
                level=ContributionLevel.STRONG,
                benefit_kind=BenefitKind.DIRECT,
            ),
            DimensionContribution(
                dimension=LifeDimension.MENTOR,
                level=ContributionLevel.LIMITED,
                benefit_kind=BenefitKind.INDIRECT,
            ),
        ],
    )
    score = compute_stacking_score(opp)
    assert score.per_dimension[LifeDimension.MENTOR.value] == 1.0
    assert score.composite == 1.0