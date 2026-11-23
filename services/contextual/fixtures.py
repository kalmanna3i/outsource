"""SIMULATED_FIXTURE scenarios for Contextual Opportunity Engine demo."""

from __future__ import annotations

from datetime import datetime, time
from typing import Any

from core.contextual_models import TravelContext
from core.models import EvidenceType
from services.contextual.feasibility import CandidateGeo

ILLUSTRATIVE = "[Illustrative]"
SIM = EvidenceType.SIMULATED_FIXTURE

VERIFIED_URL = "https://www.msichicago.org/visit/"
VERIFIED_DATE = "2026-11-23"


def ord_layover_context() -> TravelContext:
    return TravelContext(
        kind="layover",
        label="5h ORD layover (SIMULATED_FIXTURE)",
        location="Chicago O'Hare International Airport (ORD)",
        window_start=datetime(2026, 12, 5, 11, 30),
        window_end=datetime(2026, 12, 5, 16, 30),
        next_departure=datetime(2026, 12, 5, 16, 30),
        energy_level="medium",
        location_permission_granted=False,
        airport_code="ORD",
        notes="Illustrative itinerary — not live flight data.",
    )


def ord_opportunity_templates() -> list[dict[str, Any]]:
    return [
        {
            "title": f"{ILLUSTRATIVE} MSI exhibit + coffee debrief (near downtown)",
            "who": f"{ILLUSTRATIVE} Yale alumni host at Museum of Science and Industry",
            "what": "90-minute museum visit plus informal networking",
            "when": "Dec 5, 13:00–14:30 CT (public hours)",
            "where": "Museum of Science and Industry, Chicago (public venue)",
            "why": "Supports relationship + intellectual development goals during business travel",
            "how": "CTA Blue Line from ORD to downtown, then short rideshare",
            "access_requirements": "General admission ticket; no private credentials",
            "source_urls": [VERIFIED_URL],
            "source_retrieved_at": VERIFIED_DATE,
            "verification_status": EvidenceType.VERIFIED_SOURCE,
            "illustrative": True,
            "transport_requirements": "CTA Blue Line + 15 min rideshare each way (illustrative times)",
            "prep_time_minutes": 15,
            "incremental_time_minutes": 90,
            "incremental_cost_usd": 42.0,
            "opportunity_cost": "Misses quiet work block in terminal; low email catch-up time",
            "strategic_benefits": [
                "Maintains alumni tie before graduation",
                "Inspiration for OUTSOURCE demo storytelling",
            ],
            "geo_key": "msi",
        },
        {
            "title": f"{ILLUSTRATIVE} Suburban manufacturing plant tour",
            "who": f"{ILLUSTRATIVE} Operator acquaintance",
            "what": "2-hour facility walkthrough",
            "when": "Dec 5, 12:00–14:00 CT",
            "where": f"{ILLUSTRATIVE} West suburban Illinois (55 km from ORD)",
            "why": "Acquisition-learning objective",
            "how": "Rideshare round trip",
            "access_requirements": "Pre-registered visitor badge (not yet requested)",
            "source_urls": [],
            "verification_status": SIM,
            "transport_requirements": "Rideshare ~55 km each way",
            "prep_time_minutes": 20,
            "incremental_time_minutes": 120,
            "incremental_cost_usd": 95.0,
            "opportunity_cost": "High stress before international connection",
            "strategic_benefits": ["Operator pattern recognition"],
            "geo_key": "suburb",
        },
    ]


ORD_GEO: dict[str, CandidateGeo] = {
    "msi": CandidateGeo(
        distance_km=14.0,
        base_travel_minutes_one_way=32,
        venue_open=time(9, 30),
        venue_close=time(16, 0),
        min_energy="medium",
    ),
    "suburb": CandidateGeo(
        distance_km=55.0,
        base_travel_minutes_one_way=52,
        venue_open=time(8, 0),
        venue_close=time(17, 0),
        min_energy="high",
    ),
}


def boston_conference_context() -> TravelContext:
    return TravelContext(
        kind="conference",
        label="Boston conference trip (SIMULATED_FIXTURE)",
        location="Boston, MA",
        window_start=datetime(2026, 1, 14, 8, 0),
        window_end=datetime(2026, 1, 17, 18, 0),
        energy_level="high",
        location_permission_granted=True,
        notes="Illustrative SOM-style conference week.",
    )


def boston_bundle_lines() -> tuple[list[dict], list[dict]]:
    """Original vs extend-one-day lines (costs are illustrative, math is deterministic)."""
    original = [
        {"label": "Round-trip airfare (economy)", "cost_usd": 420.0, "duration_minutes": 0, "notes": "Fixed"},
        {"label": "Conference hotel (3 nights)", "cost_usd": 585.0, "duration_minutes": 0},
        {"label": "Conference registration", "cost_usd": 0.0, "duration_minutes": 0, "notes": "Employer-paid"},
        {
            "label": "Evening blocks (travel prep)",
            "cost_usd": 65.0,
            "duration_minutes": 160,
            "notes": "Replaced on extension day by public activities in alternative",
        },
    ]
    extended = [
        {"label": "Round-trip airfare (economy)", "cost_usd": 420.0, "duration_minutes": 0},
        {"label": "Conference hotel (4 nights)", "cost_usd": 780.0, "duration_minutes": 0},
        {"label": "Conference registration", "cost_usd": 0.0, "duration_minutes": 0},
        {
            "label": f"{ILLUSTRATIVE} Public lecture at MIT Sloan",
            "cost_usd": 0.0,
            "duration_minutes": 90,
            "notes": "Public event",
        },
        {
            "label": f"{ILLUSTRATIVE} Coffee meeting — local founder",
            "cost_usd": 18.0,
            "duration_minutes": 60,
        },
        {"label": "Meals + local transit (extra day)", "cost_usd": 62.0, "duration_minutes": 45},
    ]
    return original, extended


def boston_opportunity_template() -> dict[str, Any]:
    return {
        "title": f"{ILLUSTRATIVE} MIT public lecture + founder coffee",
        "who": f"{ILLUSTRATIVE} MIT Sloan speaker; founder 'Chris M.'",
        "what": "Attend public AI-in-operations lecture; 60-min coffee nearby",
        "when": "Jan 17, 10:00–12:30 ET",
        "where": "Cambridge, MA (public venues)",
        "why": "Aligns with entrepreneurship + reputation objectives",
        "how": "Extend trip one day; register for free public ticket",
        "access_requirements": "Free registration; coffee is walk-in public café",
        "source_urls": ["https://mitsloan.mit.edu/"],
        "source_retrieved_at": VERIFIED_DATE,
        "verification_status": EvidenceType.VERIFIED_SOURCE,
        "transport_requirements": "Red Line + walking",
        "prep_time_minutes": 30,
        "incremental_time_minutes": 150,
        "incremental_cost_usd": 275.0,
        "opportunity_cost": "One day away from New Haven job-search rhythm",
        "strategic_benefits": ["Visible thought leadership", "Pipeline conversation for post-MBA"],
        "geo_key": "boston",
    }


BOSTON_GEO = CandidateGeo(
    distance_km=4.5,
    base_travel_minutes_one_way=22,
    venue_open=time(8, 0),
    venue_close=time(21, 0),
    min_energy="medium",
)