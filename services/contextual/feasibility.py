"""Deterministic geographic and time-window feasibility for contextual opportunities."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta

from core.contextual_models import ContextualOpportunity, EnergyLevel, TravelContext

# Layover buffers (minutes) — conservative for ORD-style hubs.
SECURITY_REENTRY_MINUTES = 25
BOARDING_BUFFER_MINUTES = 40
UNCERTAINTY_BUFFER_FACTOR = 1.35  # inflate travel-time estimates
RECOVERY_AFTER_OUTING: dict[EnergyLevel, int] = {"low": 45, "medium": 25, "high": 15}


@dataclass(frozen=True)
class CandidateGeo:
    """Known travel estimate from context anchor to opportunity venue."""

    distance_km: float
    base_travel_minutes_one_way: int
    venue_open: time
    venue_close: time
    event_start: datetime | None = None
    event_end: datetime | None = None
    min_energy: EnergyLevel = "medium"


def _effective_travel(one_way: int) -> int:
    return int(one_way * UNCERTAINTY_BUFFER_FACTOR) + 1


def _available_minutes(ctx: TravelContext) -> int:
    end = ctx.window_end
    if ctx.next_departure and ctx.next_departure < end:
        end = ctx.next_departure
    return max(0, int((end - ctx.window_start).total_seconds() // 60))


def _layover_required_buffer(ctx: TravelContext) -> int:
    if ctx.kind != "layover":
        return 0
    return SECURITY_REENTRY_MINUTES + BOARDING_BUFFER_MINUTES


def assess_feasibility(
    ctx: TravelContext,
    opp: ContextualOpportunity,
    geo: CandidateGeo,
) -> ContextualOpportunity:
    """Return opp with feasibility_status and infeasible_reason set."""
    opp = opp.model_copy(
        update={
            "distance_km": geo.distance_km,
            "travel_time_minutes": _effective_travel(geo.base_travel_minutes_one_way),
        }
    )

    if ctx.kind == "layover" and not ctx.location_permission_granted:
        # Layover excursions do not use private GPS; still allow airport-adjacent public venues.
        if geo.distance_km > 15:
            return opp.model_copy(
                update={
                    "feasibility_status": "infeasible",
                    "infeasible_reason": (
                        "Distance exceeds safe layover radius without user-authorized location; "
                        "recommend in-terminal or airside options only."
                    ),
                    "recommended": False,
                }
            )

    energy_order = {"low": 0, "medium": 1, "high": 2}
    if energy_order[ctx.energy_level] < energy_order[geo.min_energy]:
        return opp.model_copy(
            update={
                "feasibility_status": "infeasible",
                "infeasible_reason": (
                    f"Energy level '{ctx.energy_level}' is insufficient for this outing "
                    f"(requires '{geo.min_energy}')."
                ),
                "recommended": False,
            }
        )

    one_way = _effective_travel(geo.base_travel_minutes_one_way)
    round_trip = one_way * 2
    buffers = _layover_required_buffer(ctx)
    recovery = RECOVERY_AFTER_OUTING[ctx.energy_level]
    onsite = opp.incremental_time_minutes
    prep = opp.prep_time_minutes
    total_need = round_trip + buffers + recovery + onsite + prep

    available = _available_minutes(ctx)
    if total_need > available:
        return opp.model_copy(
            update={
                "feasibility_status": "infeasible",
                "infeasible_reason": (
                    f"Time budget exceeded: need ~{total_need} min "
                    f"(travel {round_trip}, buffers {buffers}, prep {prep}, "
                    f"activity {onsite}, recovery {recovery}) but only {available} min available."
                ),
                "recommended": False,
            }
        )

    if ctx.kind == "layover" and ctx.next_departure:
        latest_return = ctx.next_departure - timedelta(minutes=buffers + recovery)
        depart_after = ctx.window_start + timedelta(minutes=prep + one_way)
        if depart_after > latest_return - timedelta(minutes=onsite):
            return opp.model_copy(
                update={
                    "feasibility_status": "infeasible",
                    "infeasible_reason": (
                        "Cannot complete outing and return through security with boarding buffer "
                        f"before departure at {ctx.next_departure.strftime('%H:%M')}."
                    ),
                    "recommended": False,
                }
            )

    # Business hours: outing must fit inside venue hours on window day (local naive).
    if ctx.kind != "delay":
        open_dt = datetime.combine(ctx.window_start.date(), geo.venue_open)
        close_dt = datetime.combine(ctx.window_start.date(), geo.venue_close)
        outing_start = ctx.window_start + timedelta(minutes=prep + one_way)
        outing_end = outing_start + timedelta(minutes=onsite)
        if outing_start < open_dt or outing_end > close_dt:
            return opp.model_copy(
                update={
                    "feasibility_status": "infeasible",
                    "infeasible_reason": (
                        f"Venue hours {geo.venue_open.strftime('%H:%M')}–"
                        f"{geo.venue_close.strftime('%H:%M')} do not fit the travel window."
                    ),
                    "recommended": False,
                }
            )

    if geo.event_start and geo.event_end:
        outing_start = ctx.window_start + timedelta(minutes=prep + one_way)
        outing_end = outing_start + timedelta(minutes=onsite)
        if outing_start > geo.event_start or outing_end < geo.event_end:
            return opp.model_copy(
                update={
                    "feasibility_status": "infeasible",
                    "infeasible_reason": "Event schedule does not align with available layover window.",
                    "recommended": False,
                }
            )

    return opp.model_copy(
        update={
            "feasibility_status": "feasible",
            "infeasible_reason": None,
            "recommended": True,
        }
    )