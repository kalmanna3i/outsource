"""Contextual Opportunity Engine schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from core.models import (
    AgentCallRecord,
    CalendarSlot,
    EvidenceType,
    HumanIntervention,
    new_id,
)

ContextKind = Literal["layover", "trip", "hotel", "conference", "delay"]
EnergyLevel = Literal["low", "medium", "high"]
FeasibilityStatus = Literal["feasible", "infeasible", "untested"]

CONTEXTUAL_REQUIRED_FIELDS: tuple[str, ...] = (
    "opportunity_id",
    "who",
    "what",
    "when",
    "where",
    "why",
    "how",
    "access_requirements",
    "source_urls",
    "source_retrieved_at",
    "transport_requirements",
    "prep_time_minutes",
    "incremental_cost_usd",
    "incremental_time_minutes",
    "opportunity_cost",
    "strategic_benefits",
    "verification_status",
    "feasibility_status",
)


class TravelContext(BaseModel):
    context_id: str = Field(default_factory=lambda: new_id("ctx"))
    kind: ContextKind
    label: str
    location: str
    window_start: datetime
    window_end: datetime
    energy_level: EnergyLevel = "medium"
    location_permission_granted: bool = False
    airport_code: str | None = None
    next_departure: datetime | None = None
    notes: str = ""


class ContextualOpportunity(BaseModel):
    opportunity_id: str = Field(default_factory=lambda: new_id("ctxopp"))
    title: str
    who: str
    what: str
    when: str
    where: str
    why: str
    how: str
    access_requirements: str = ""
    source_urls: list[str] = Field(default_factory=list)
    source_retrieved_at: str | None = None
    transport_requirements: str = ""
    prep_time_minutes: int = 0
    incremental_cost_usd: float = 0.0
    incremental_time_minutes: int = 0
    opportunity_cost: str = ""
    strategic_benefits: list[str] = Field(default_factory=list)
    verification_status: EvidenceType = EvidenceType.SIMULATED_FIXTURE
    illustrative: bool = True
    feasibility_status: FeasibilityStatus = "untested"
    infeasible_reason: str | None = None
    distance_km: float | None = None
    travel_time_minutes: int | None = None
    mission_alignment_reason: str = ""
    alignment_score: float | None = Field(default=None, ge=0, le=10)
    recommended: bool = False
    discovered_by: list[str] = Field(default_factory=list)
    # Execution artifacts — always drafts / requires authorization
    outreach_status: Literal["draft", "requires_authorization"] = "requires_authorization"
    registration_status: Literal["draft", "requires_authorization"] = "requires_authorization"
    booking_status: Literal["not_booked", "requires_authorization"] = "requires_authorization"

    @model_validator(mode="after")
    def _verified_needs_source(self) -> "ContextualOpportunity":
        if self.verification_status == EvidenceType.VERIFIED_SOURCE and not (
            self.source_urls and self.source_retrieved_at
        ):
            raise ValueError("VERIFIED_SOURCE requires source_urls and source_retrieved_at")
        return self


class ItineraryLine(BaseModel):
    label: str
    cost_usd: float
    duration_minutes: int
    notes: str = ""


class ItineraryBundle(BaseModel):
    bundle_id: str = Field(default_factory=lambda: new_id("bundle"))
    label: str
    lines: list[ItineraryLine]
    total_cost_usd: float
    total_time_minutes: int
    benefits: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    is_original: bool = False


class BundleComparison(BaseModel):
    comparison_id: str = Field(default_factory=lambda: new_id("cmp"))
    context_label: str
    original: ItineraryBundle
    alternative: ItineraryBundle
    incremental_cost_usd: float
    incremental_time_minutes: int
    net_benefit_summary: str


class ContextualRun(BaseModel):
    run_id: str = Field(default_factory=lambda: new_id("ctxrun"))
    context: TravelContext
    mode: Literal["demo", "live"] = "demo"
    opportunities: list[ContextualOpportunity] = Field(default_factory=list)
    comparison: BundleComparison | None = None
    agent_calls: list[AgentCallRecord] = Field(default_factory=list)
    scenario_key: str = ""


class ContextualExecution(BaseModel):
    package_id: str = Field(default_factory=lambda: new_id("ctxexec"))
    opportunity_id: str
    itinerary_markdown: str
    calendar_slots: list[CalendarSlot] = Field(default_factory=list)
    ics_paths: list[str] = Field(default_factory=list)
    meeting_request_draft: str
    registration_options: list[str] = Field(default_factory=list)
    authorization_note: str = (
        "All items below are drafts. Nothing is sent, booked, or registered without your authorization."
    )
    outreach_status: Literal["draft", "requires_authorization"] = "requires_authorization"
    registration_status: Literal["requires_authorization"] = "requires_authorization"
    booking_status: Literal["requires_authorization"] = "requires_authorization"
    human_intervention: HumanIntervention | None = None