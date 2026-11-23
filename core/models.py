"""Pydantic schemas for OUTSOURCE."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field


def new_id(prefix: str = "id") -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class EvidenceType(str, Enum):
    VERIFIED_SOURCE = "VERIFIED_SOURCE"
    USER_PROVIDED = "USER_PROVIDED"
    MODELED_ASSUMPTION = "MODELED_ASSUMPTION"
    UNVERIFIED = "UNVERIFIED"
    SIMULATED_FIXTURE = "SIMULATED_FIXTURE"


class TaskStatus(str, Enum):
    INTAKE = "INTAKE"
    ANALYZING = "ANALYZING"
    PLANNED = "PLANNED"
    EXECUTING = "EXECUTING"
    BLOCKED_HUMAN = "BLOCKED_HUMAN"
    WAITING_RESULT = "WAITING_RESULT"
    RESUMING = "RESUMING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class PermissionMode(str, Enum):
    REVIEW_ALL = "REVIEW_ALL"
    MANAGED_AUTONOMY = "MANAGED_AUTONOMY"
    CUSTOM_AUTONOMY = "CUSTOM_AUTONOMY"


class EvidenceRecord(BaseModel):
    evidence_id: str = Field(default_factory=lambda: new_id("ev"))
    evidence_type: EvidenceType
    source: str
    summary: str
    retrieved_at: datetime = Field(default_factory=datetime.utcnow)
    confidence: float = 0.5
    agent_id: str | None = None
    raw_ref: str | None = None
    labeled_demo: bool = False


class Goal(BaseModel):
    goal_id: str = Field(default_factory=lambda: new_id("goal"))
    title: str
    domain: str  # career, academic, financial, relationships, health, legacy
    target_date: str | None = None
    importance: int = Field(ge=1, le=10, default=5)
    progress: float = Field(ge=0, le=1, default=0.0)
    resources: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    flexibility: str = "medium"
    success_criteria: str = ""


class LifeBlueprint(BaseModel):
    user_name: str = "Kay Al Mannai"
    personal_summary: str = ""
    career: str = ""
    academic: str = ""
    financial: str = ""
    relationships: str = ""
    family: str = ""
    lifestyle: str = ""
    health: str = ""
    legacy: str = ""
    goals: list[Goal] = Field(default_factory=list)


class OpportunityCostItem(BaseModel):
    option_id: str = Field(default_factory=lambda: new_id("opt"))
    label: str
    time_hours: float
    monetary_usd: float | None = None
    qualitative_value: str
    goal_alignment: list[str] = Field(default_factory=list)
    risk_notes: str = ""
    recommended: bool = False


class DecisionPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: new_id("plan"))
    situation: str
    constraints: list[str]
    options: list[OpportunityCostItem]
    recommended_sequence: list[str]
    tradeoffs: list[str]
    assumptions: list[str]
    uncertainty_notes: str
    evidence: list[EvidenceRecord] = Field(default_factory=list)


class WorkPackage(BaseModel):
    package_id: str = Field(default_factory=lambda: new_id("wp"))
    title: str
    assignee: Literal["AI", "HUMAN", "DELEGATED"]
    rationale: str
    status: TaskStatus = TaskStatus.PLANNED
    deliverable_summary: str | None = None
    blocker: str | None = None
    depends_on: list[str] = Field(default_factory=list)


class CalendarSlot(BaseModel):
    slot_id: str = Field(default_factory=lambda: new_id("slot"))
    title: str
    start: datetime
    end: datetime
    location: str | None = None
    public_description: str = ""
    private_brief_ref: str | None = None
    busy: bool = True


class HumanIntervention(BaseModel):
    intervention_id: str = Field(default_factory=lambda: new_id("hi"))
    title: str
    why_human_required: str
    prepared_brief: str
    talking_points: list[str]
    documents_ready: list[str]
    suggested_slot: CalendarSlot | None = None
    ics_path: str | None = None
    status: Literal["PREPARED", "SCHEDULED", "WAITING_RESULT", "RESOLVED"] = "PREPARED"
    user_result: str | None = None
    sensitive: bool = True


class AgentCallRecord(BaseModel):
    call_id: str = Field(default_factory=lambda: new_id("call"))
    agent_id: str
    role: str
    started_at: datetime = Field(default_factory=datetime.utcnow)
    finished_at: datetime | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    cached_input_tokens: int | None = None
    cache_write_tokens: int | None = None
    cost_usd: float | None = None
    cost_known: bool = False
    mode: Literal["demo", "live"] = "demo"
    summary: str = ""
    success: bool = True
    error: str | None = None


class WorkflowState(BaseModel):
    workflow_id: str = Field(default_factory=lambda: new_id("wf"))
    user_request: str
    status: TaskStatus = TaskStatus.INTAKE
    blueprint_snapshot: LifeBlueprint | None = None
    decision_plan: DecisionPlan | None = None
    work_packages: list[WorkPackage] = Field(default_factory=list)
    interventions: list[HumanIntervention] = Field(default_factory=list)
    calendar_slots: list[CalendarSlot] = Field(default_factory=list)
    evidence: list[EvidenceRecord] = Field(default_factory=list)
    agent_calls: list[AgentCallRecord] = Field(default_factory=list)
    transitions: list[dict[str, Any]] = Field(default_factory=list)
    digital_deliverables: list[str] = Field(default_factory=list)
    follow_ups: list[str] = Field(default_factory=list)
    mode: Literal["demo", "live"] = "demo"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def transition(self, new_status: TaskStatus, note: str = "") -> None:
        self.transitions.append(
            {
                "from": self.status.value,
                "to": new_status.value,
                "at": datetime.utcnow().isoformat() + "Z",
                "note": note,
            }
        )
        self.status = new_status
        self.updated_at = datetime.utcnow()


class PersonProfile(BaseModel):
    person_id: str = Field(default_factory=lambda: new_id("person"))
    name: str
    relationship: str
    notes: str = ""
    birthday: str | None = None
    milestones: list[str] = Field(default_factory=list)
