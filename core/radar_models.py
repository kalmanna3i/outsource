"""Strategic Radar schemas: opportunity records, network graph, execution packages."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from core.models import (
    AgentCallRecord,
    CalendarSlot,
    EvidenceRecord,
    EvidenceType,
    HumanIntervention,
    new_id,
)

OpportunityClass = Literal["GENUINE_OPPORTUNITY", "DISTRACTION", "NEEDS_REVIEW", "UNSCORED"]

# Spec §6 required fields, in spec order.
SPEC_REQUIRED_FIELDS: tuple[str, ...] = (
    "opportunity_id",
    "opportunity_type",
    "relevant_people",
    "relevant_organizations",
    "description",
    "date_discovered",
    "event_date_or_deadline",
    "location",
    "source_urls",
    "verification_status",
    "relevant_strategic_objectives",
    "relevant_guiding_principles",
    "mission_alignment_reason",
    "potential_conflicts",
    "estimated_financial_cost",
    "estimated_time_commitment",
    "nonfinancial_considerations",
    "opportunity_cost",
    "recommended_next_action",
    "contact_or_registration_info",
    "conversation_topics",
    "preparation_requirements",
    "follow_up_plan",
)

SIX_QUESTIONS: tuple[str, ...] = ("who", "what", "when", "where", "why", "how", "cost")


class OpportunityRecord(BaseModel):
    opportunity_id: str = Field(default_factory=lambda: new_id("opp"))
    title: str
    opportunity_type: str
    category: str = ""
    mission_area: str = ""
    relevant_people: list[str] = Field(default_factory=list)
    relevant_organizations: list[str] = Field(default_factory=list)
    description: str
    date_discovered: datetime = Field(default_factory=datetime.utcnow)
    event_date_or_deadline: str | None = None
    location: str | None = None
    source_urls: list[str] = Field(default_factory=list)
    source_retrieved_at: str | None = None
    verification_status: EvidenceType = EvidenceType.SIMULATED_FIXTURE
    illustrative: bool = True
    relevant_strategic_objectives: list[str] = Field(default_factory=list)
    relevant_guiding_principles: list[str] = Field(default_factory=list)
    mission_alignment_reason: str = ""
    potential_conflicts: list[str] = Field(default_factory=list)
    # Money is kept apart from the qualitative alignment score.
    estimated_financial_cost: float | None = None
    estimated_time_commitment: str = ""
    estimated_time_hours: float | None = None
    nonfinancial_considerations: list[str] = Field(default_factory=list)
    opportunity_cost: str = ""
    recommended_next_action: str = ""
    contact_or_registration_info: str = ""
    conversation_topics: list[str] = Field(default_factory=list)
    preparation_requirements: list[str] = Field(default_factory=list)
    follow_up_plan: list[str] = Field(default_factory=list)

    who: str = ""
    what: str = ""
    when: str = ""
    where: str = ""
    why: str = ""
    how: str = ""
    cost: str = ""

    risk_flags: list[str] = Field(default_factory=list)
    discovered_by: list[str] = Field(default_factory=list)
    alignment_score: float | None = Field(default=None, ge=0, le=10)
    classification: OpportunityClass = "UNSCORED"

    @model_validator(mode="after")
    def _verified_needs_source(self) -> "OpportunityRecord":
        if self.verification_status == EvidenceType.VERIFIED_SOURCE and not (
            self.source_urls and self.source_retrieved_at
        ):
            raise ValueError("VERIFIED_SOURCE opportunities need source_urls and source_retrieved_at")
        return self

    def evidence(self) -> list[EvidenceRecord]:
        """Evidence-ledger entries for this opportunity's sources."""
        demo = self.verification_status == EvidenceType.SIMULATED_FIXTURE
        if not self.source_urls:
            return [
                EvidenceRecord(
                    evidence_type=self.verification_status,
                    source=f"radar:{','.join(self.discovered_by) or 'unknown'}",
                    summary=f"{self.title} — no external source URL",
                    agent_id=(self.discovered_by or [None])[0],
                    confidence=0.3 if demo else 0.4,
                    raw_ref=self.opportunity_id,
                    labeled_demo=demo,
                )
            ]
        return [
            EvidenceRecord(
                evidence_type=self.verification_status,
                source=url,
                summary=f"{self.title} (retrieved {self.source_retrieved_at or 'n/a'})",
                agent_id=(self.discovered_by or [None])[0],
                confidence=0.9 if self.verification_status == EvidenceType.VERIFIED_SOURCE else 0.4,
                raw_ref=self.opportunity_id,
                labeled_demo=demo,
            )
            for url in self.source_urls
        ]


EdgeStatus = Literal["VERIFIED", "USER_PROVIDED", "HYPOTHETICAL", "MISSION_LINK"]
NodeType = Literal[
    "user", "person", "company", "university", "industry", "publication",
    "event", "association", "goal",
]


class NetworkNode(BaseModel):
    node_id: str
    label: str
    node_type: NodeType
    illustrative: bool = False


class NetworkEdge(BaseModel):
    source: str
    target: str
    relation: str
    status: EdgeStatus
    source_url: str | None = None
    retrieved_at: str | None = None
    note: str = ""

    @model_validator(mode="after")
    def _verified_needs_citation(self) -> "NetworkEdge":
        if self.status == "VERIFIED" and not (self.source_url and self.retrieved_at):
            raise ValueError("VERIFIED edges require source_url and retrieved_at")
        return self


class NetworkGraph(BaseModel):
    nodes: list[NetworkNode] = Field(default_factory=list)
    edges: list[NetworkEdge] = Field(default_factory=list)


class OutreachDraft(BaseModel):
    to: str
    channel: str
    subject: str
    body: str
    status: Literal["DRAFT_NOT_SENT"] = "DRAFT_NOT_SENT"


class RadarSchedule(BaseModel):
    daily_briefing: bool = True
    daily_time: str = "07:30"
    weekly_networking_review: bool = True
    weekly_day: str = "Sunday"
    monthly_mission_review: bool = True
    monthly_day: int = Field(default=1, ge=1, le=28)
    event_triggered_research: bool = False
    # No background scheduler runs; discovery happens only on "Run discovery now".
    background_monitoring_status: Literal["Planned"] = "Planned"


class DiscoveryRun(BaseModel):
    run_id: str = Field(default_factory=lambda: new_id("radar"))
    mode: Literal["demo", "live"] = "demo"
    candidates_raw: int = 0
    duplicates_merged: int = 0
    opportunities: list[OpportunityRecord] = Field(default_factory=list)
    new_opportunity_ids: list[str] = Field(default_factory=list)
    agent_calls: list[AgentCallRecord] = Field(default_factory=list)
    evidence: list[EvidenceRecord] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def genuine(self) -> list[OpportunityRecord]:
        return [o for o in self.opportunities if o.classification == "GENUINE_OPPORTUNITY"]

    @property
    def distractions(self) -> list[OpportunityRecord]:
        return [o for o in self.opportunities if o.classification == "DISTRACTION"]


class ExecutionPackage(BaseModel):
    package_id: str = Field(default_factory=lambda: new_id("rx"))
    opportunity_id: str
    opportunity_title: str
    outreach_draft: OutreachDraft
    contact_info: str = ""
    conversation_topics: list[str] = Field(default_factory=list)
    preparation_requirements: list[str] = Field(default_factory=list)
    prep_minutes: int = 0
    travel_estimate: str = ""
    calendar_slot: CalendarSlot | None = None
    ics_path: str | None = None
    intervention: HumanIntervention | None = None
    follow_up_plan: list[str] = Field(default_factory=list)
    agent_calls: list[AgentCallRecord] = Field(default_factory=list)
    evidence: list[EvidenceRecord] = Field(default_factory=list)
    outreach_sent: Literal[False] = False
    mode: Literal["demo", "live"] = "demo"
