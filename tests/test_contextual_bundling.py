"""Deterministic bundling math tests."""

from __future__ import annotations

from core.contextual_models import ItineraryLine
from services.contextual.bundling import compare_bundles
from services.contextual import fixtures as fx


def test_boston_incremental_cost_deterministic() -> None:
    orig, ext = fx.boston_bundle_lines()
    from services.contextual.engine import _lines_from_dicts

    cmp = compare_bundles(
        context_label="Boston",
        original_lines=_lines_from_dicts(orig),
        alternative_lines=_lines_from_dicts(ext),
        original_label="Original",
        alternative_label="Extended",
        alt_benefits=["lecture"],
        alt_risks=["time"],
    )
    assert cmp.original.total_cost_usd == 1070.0
    assert cmp.alternative.total_cost_usd == 1280.0
    assert cmp.incremental_cost_usd == 210.0


def test_bundle_sums_lines() -> None:
    lines = [
        ItineraryLine(label="a", cost_usd=10.5, duration_minutes=30),
        ItineraryLine(label="b", cost_usd=20.0, duration_minutes=60),
    ]
    cmp = compare_bundles(
        context_label="x",
        original_lines=lines,
        alternative_lines=lines,
        original_label="o",
        alternative_label="a",
        alt_benefits=[],
        alt_risks=[],
    )
    assert cmp.incremental_cost_usd == 0.0
    assert cmp.incremental_time_minutes == 0