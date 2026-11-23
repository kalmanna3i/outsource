"""Deterministic itinerary bundling — incremental cost/time computed in code."""

from __future__ import annotations

from core.contextual_models import BundleComparison, ItineraryBundle, ItineraryLine


def _sum_bundle(lines: list[ItineraryLine]) -> tuple[float, int]:
    cost = sum(l.cost_usd for l in lines)
    minutes = sum(l.duration_minutes for l in lines)
    return cost, minutes


def build_bundle(
    *,
    label: str,
    lines: list[ItineraryLine],
    benefits: list[str] | None = None,
    risks: list[str] | None = None,
    is_original: bool = False,
) -> ItineraryBundle:
    cost, minutes = _sum_bundle(lines)
    return ItineraryBundle(
        label=label,
        lines=lines,
        total_cost_usd=round(cost, 2),
        total_time_minutes=minutes,
        benefits=benefits or [],
        risks=risks or [],
        is_original=is_original,
    )


def compare_bundles(
    *,
    context_label: str,
    original_lines: list[ItineraryLine],
    alternative_lines: list[ItineraryLine],
    original_label: str,
    alternative_label: str,
    alt_benefits: list[str],
    alt_risks: list[str],
    orig_benefits: list[str] | None = None,
    orig_risks: list[str] | None = None,
) -> BundleComparison:
    original = build_bundle(
        label=original_label,
        lines=original_lines,
        benefits=orig_benefits or [],
        risks=orig_risks or [],
        is_original=True,
    )
    alternative = build_bundle(
        label=alternative_label,
        lines=alternative_lines,
        benefits=alt_benefits,
        risks=alt_risks,
    )
    d_cost = round(alternative.total_cost_usd - original.total_cost_usd, 2)
    d_time = alternative.total_time_minutes - original.total_time_minutes
    summary = (
        f"Alternative adds ${d_cost:,.2f} and {d_time} minutes vs original "
        f"(${original.total_cost_usd:,.2f} → ${alternative.total_cost_usd:,.2f})."
    )
    return BundleComparison(
        context_label=context_label,
        original=original,
        alternative=alternative,
        incremental_cost_usd=d_cost,
        incremental_time_minutes=d_time,
        net_benefit_summary=summary,
    )