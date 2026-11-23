"""Chief of Staff stacking recommendation tests."""

from services.stacking.chief_of_staff import recommend_bundle
from services.stacking.fixtures import ILLUSTRATIVE_OPPORTUNITIES, SAMPLE_LIFE_MANDATE


def test_recommends_feasible_bundle_under_mandate() -> None:
    rec = recommend_bundle(ILLUSTRATIVE_OPPORTUNITIES, SAMPLE_LIFE_MANDATE)
    chosen = next(
        o for o in ILLUSTRATIVE_OPPORTUNITIES if o.label == rec.chosen_bundle_label
    )
    assert chosen.monthly_hours <= SAMPLE_LIFE_MANDATE.max_monthly_hours
    assert rec.separate_activities_rejected
    assert "not instruments" in " ".join(rec.rationale).lower()