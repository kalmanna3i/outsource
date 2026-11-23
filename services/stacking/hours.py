"""Deterministic hours math for separate vs bundled commitments."""

from __future__ import annotations

from core.models import HoursComparison

EIGHT_HOUR_WORKDAY = 8.0


def compare_hours(
    separate_commitment_hours: list[float],
    bundled_hours: float,
) -> HoursComparison:
    """Monthly and annual time recovered when bundling comparable commitments."""
    separate_total = sum(separate_commitment_hours)
    monthly_saved = max(0.0, separate_total - bundled_hours)
    annual_recovered = monthly_saved * 12.0
    return HoursComparison(
        separate_commitment_hours=list(separate_commitment_hours),
        bundled_hours=bundled_hours,
        monthly_hours_saved=monthly_saved,
        annual_hours_recovered=annual_recovered,
    )


def eight_hour_days_equivalent(annual_hours: float) -> float:
    return annual_hours / EIGHT_HOUR_WORKDAY


def canonical_efficiency_example() -> HoursComparison:
    """Spec example: 5+4+5+4 = 18 hrs/mo separate vs 6 combined → 144 hrs/year."""
    return compare_hours([5.0, 4.0, 5.0, 4.0], bundled_hours=6.0)