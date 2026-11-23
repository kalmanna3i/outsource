"""Stacking hours math tests."""

from services.stacking.hours import canonical_efficiency_example, compare_hours, eight_hour_days_equivalent


def test_canonical_18_vs_6_recovers_144_hours_per_year() -> None:
    ex = canonical_efficiency_example()
    assert sum(ex.separate_commitment_hours) == 18.0
    assert ex.bundled_hours == 6.0
    assert ex.monthly_hours_saved == 12.0
    assert ex.annual_hours_recovered == 144.0
    assert eight_hour_days_equivalent(144.0) == 18.0


def test_hours_never_negative() -> None:
    cmp = compare_hours([2.0, 2.0], bundled_hours=10.0)
    assert cmp.monthly_hours_saved == 0.0
    assert cmp.annual_hours_recovered == 0.0


def test_assumption_present() -> None:
    ex = canonical_efficiency_example()
    assert "comparable benefits" in ex.comparable_benefits_assumption.lower()