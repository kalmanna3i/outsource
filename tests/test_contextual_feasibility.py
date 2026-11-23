"""Geographic / layover feasibility tests."""

from __future__ import annotations

from datetime import datetime, time, timedelta

from core.contextual_models import ContextualOpportunity, TravelContext
from core.models import EvidenceType
from services.contextual.feasibility import CandidateGeo, assess_feasibility
from services.contextual import fixtures as fx


def _opp(**kw) -> ContextualOpportunity:
    base = dict(
        title="Test",
        who="x",
        what="x",
        when="x",
        where="x",
        why="x",
        how="x",
        prep_time_minutes=15,
        incremental_time_minutes=90,
        incremental_cost_usd=40.0,
        verification_status=EvidenceType.SIMULATED_FIXTURE,
    )
    base.update(kw)
    return ContextualOpportunity(**base)


def test_ord_msi_feasible() -> None:
    ctx = fx.ord_layover_context()
    opp = _opp(title="MSI visit")
    geo = fx.ORD_GEO["msi"]
    out = assess_feasibility(ctx, opp, geo)
    assert out.feasibility_status == "feasible"
    assert out.infeasible_reason is None
    assert out.recommended is True


def test_ord_suburb_infeasible_time() -> None:
    ctx = fx.ord_layover_context()
    opp = _opp(title="Suburban plant", incremental_time_minutes=120, prep_time_minutes=20)
    geo = fx.ORD_GEO["suburb"]
    out = assess_feasibility(ctx, opp, geo)
    assert out.feasibility_status == "infeasible"
    assert out.infeasible_reason
    assert out.infeasible_reason
    assert any(
        s in out.infeasible_reason
        for s in ("Time budget", "Distance exceeds", "boarding", "security")
    ) or "Distance" in out.infeasible_reason
    assert out.recommended is False


def test_low_energy_rejects_high_min_energy() -> None:
    ctx = fx.ord_layover_context().model_copy(update={"energy_level": "low"})
    opp = _opp()
    geo = CandidateGeo(
        distance_km=10,
        base_travel_minutes_one_way=20,
        venue_open=time(9, 0),
        venue_close=time(17, 0),
        min_energy="high",
    )
    out = assess_feasibility(ctx, opp, geo)
    assert out.feasibility_status == "infeasible"
    assert "Energy" in (out.infeasible_reason or "")


def test_short_layover_rejects_distant() -> None:
    ctx = TravelContext(
        kind="layover",
        label="tight",
        location="ORD",
        window_start=datetime(2026, 6, 1, 12, 0),
        window_end=datetime(2026, 6, 1, 13, 30),
        next_departure=datetime(2026, 6, 1, 13, 30),
        energy_level="medium",
        location_permission_granted=False,
    )
    opp = _opp(prep_time_minutes=10, incremental_time_minutes=30)
    geo = CandidateGeo(
        distance_km=20,
        base_travel_minutes_one_way=45,
        venue_open=time(8, 0),
        venue_close=time(22, 0),
    )
    out = assess_feasibility(ctx, opp, geo)
    assert out.feasibility_status == "infeasible"


def test_venue_hours_rejection() -> None:
    ctx = fx.ord_layover_context()
    opp = _opp()
    geo = CandidateGeo(
        distance_km=5,
        base_travel_minutes_one_way=15,
        venue_open=time(8, 0),
        venue_close=time(9, 0),
    )
    out = assess_feasibility(ctx, opp, geo)
    assert out.feasibility_status == "infeasible"
    assert "Venue hours" in (out.infeasible_reason or "")