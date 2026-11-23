"""Priority 0 end-to-end workflow orchestration."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable

from agents.specialists import (
    AutonomousExecution,
    CalendarLogistics,
    ChiefOfStaff,
    FollowUp,
    HumanHandoff,
    LifeStrategyArchitect,
    OpportunityCostEconomist,
    TaskDecomposition,
)
from core.config import get_settings
from core.llm import LLMClient
from core.models import (
    CalendarSlot,
    DecisionPlan,
    EvidenceRecord,
    EvidenceType,
    HumanIntervention,
    OpportunityCostItem,
    PermissionMode,
    TaskStatus,
    WorkPackage,
    WorkflowState,
)
from core.permissions import may_auto_execute, normalize_permission
from database.db import get_permission_mode, load_blueprint, save_workflow
from services.insurer import check_claim_status
from services.scheduler import export_ics, find_slot


def _normalize_assignee(raw: object) -> str:
    val = str(raw or "AI").strip().upper()
    if val in ("AI", "HUMAN", "DELEGATED"):
        return val
    if "human" in val.lower():
        return "HUMAN"
    if "deleg" in val.lower():
        return "DELEGATED"
    return "AI"


ProgressCb = Callable[[str], None]


def _noop(_: str) -> None:
    pass


def _demo_fixtures(user_request: str, goals: list[str]) -> dict:
    return {
        "A01": {
            "summary": "Four competing obligations tonight: MBA final, wedding, work, insurance.",
            "obligations": [
                "Finish MBA final (MGT 409)",
                "Attend wedding",
                "Handle work obligation",
                "Insurance claim status",
            ],
            "goal_links": goals,
            "constraints": [
                "Hard academic deadline 11:59 PM ET",
                "Wedding is time-fixed (presence required)",
                "Insurance portal likely needs human identity verification",
                "Work stakeholder expects a response today",
            ],
            "specialists_needed": ["A02", "B01", "F02", "F03", "F04", "F05", "F06"],
            "intake_notes": user_request,
        },
        "A02": {
            "goal_readout": goals,
            "alignment_scores": {
                "MBA final": 10,
                "Wedding": 9,
                "Work obligation": 8,
                "Insurance claim": 7,
            },
            "strategic_guidance": (
                "Protect the non-movable wedding window and the academic hard stop. "
                "AI should prep work and insurance materials; human time is for presence "
                "and identity verification only."
            ),
        },
        "B01": {
            "options": [
                {
                    "label": "Deep-work MBA final first (AI-assisted drafting)",
                    "time_hours": 3.0,
                    "monetary_usd": None,
                    "qualitative_value": "Protects graduation-critical deliverable",
                    "goal_alignment": ["academic"],
                    "risk_notes": "Crowds wedding prep if started too late",
                    "recommended": True,
                },
                {
                    "label": "Attend wedding (presence; logistics pre-handled)",
                    "time_hours": 4.0,
                    "monetary_usd": None,
                    "qualitative_value": "Irreplaceable relationship capital",
                    "goal_alignment": ["relationships"],
                    "risk_notes": "Cannot reschedule",
                    "recommended": True,
                },
                {
                    "label": "Ship concise work update (AI draft, human send)",
                    "time_hours": 0.75,
                    "monetary_usd": None,
                    "qualitative_value": "Maintains stakeholder trust",
                    "goal_alignment": ["career"],
                    "risk_notes": "Delay damages credibility",
                    "recommended": True,
                },
                {
                    "label": "Insurance: AI prep + human identity verification",
                    "time_hours": 0.5,
                    "monetary_usd": None,
                    "qualitative_value": "Unblocks claim without wasting AI cycles on the portal wall",
                    "goal_alignment": ["financial"],
                    "risk_notes": "Portal will block automated access",
                    "recommended": True,
                },
            ],
            "recommended_sequence": [
                "AI: outline + draft MBA artifacts",
                "AI: draft work stakeholder update",
                "AI: attempt insurance status → hit verification barrier",
                "HUMAN: identity verification call (scheduled)",
                "HUMAN: attend wedding",
                "HUMAN: final MBA submit polish",
            ],
            "tradeoffs": [
                "Skipping wedding saves time but violates a high-importance relationship goal",
                "Fully automating insurance fails at identity gate — prepare the human moment instead",
            ],
            "assumptions": [
                "Wedding start is fixed",
                "Insurer requires human identity verification (simulated fixture)",
                "Work update can be AI-drafted then human-approved",
            ],
            "uncertainty_notes": "Exact wedding travel buffer unknown; used 30-minute logistics buffer.",
        },
        "F02": {
            "work_packages": [
                {
                    "title": "MBA final structure + draft checklist",
                    "assignee": "AI",
                    "rationale": "High leverage drafting; human does final judgment/submit",
                    "depends_on": [],
                },
                {
                    "title": "Work stakeholder update draft",
                    "assignee": "AI",
                    "rationale": "AI can draft; human must approve/send",
                    "depends_on": [],
                },
                {
                    "title": "Insurance claim status check",
                    "assignee": "AI",
                    "rationale": "Attempt digital check; escalate on identity barrier",
                    "depends_on": [],
                },
                {
                    "title": "Insurer identity verification",
                    "assignee": "HUMAN",
                    "rationale": "Cannot be automated; prepare brief + calendar slot",
                    "depends_on": ["Insurance claim status check"],
                },
                {
                    "title": "Attend wedding",
                    "assignee": "HUMAN",
                    "rationale": "Presence is the product",
                    "depends_on": [],
                },
                {
                    "title": "Final MBA submit",
                    "assignee": "HUMAN",
                    "rationale": "Academic integrity + Canvas submit requires human",
                    "depends_on": ["MBA final structure + draft checklist"],
                },
            ]
        },
        "F03": {
            "executed": [
                {
                    "title": "MBA final structure + draft checklist",
                    "deliverable_summary": (
                        "Draft checklist: README run steps, BUILD_STATUS honesty labels, "
                        "report sections 1–8 mapped to evidence, slides outline (≤10), "
                        "demo script for Priority 0 path."
                    ),
                    "status": "COMPLETED",
                },
                {
                    "title": "Work stakeholder update draft",
                    "deliverable_summary": (
                        "Draft note for Jordan Lee: status, blockers, ETA, ask. "
                        "Not sent — awaiting human approval."
                    ),
                    "status": "COMPLETED",
                },
                {
                    "title": "Insurance claim status check",
                    "deliverable_summary": "Simulated portal check initiated.",
                    "status": "BLOCKED_HUMAN",
                },
            ],
            "blockers": ["Insurer identity verification required (simulated)."],
        },
        "F04": {
            "scheduling_requests": [
                {
                    "title": "Insurer identity verification",
                    "duration_minutes": 30,
                    "public_description": "Personal admin call — details in OUTSOURCE private brief",
                }
            ]
        },
        "F05": {
            "title": "Complete insurer identity verification",
            "why_human_required": (
                "The simulated insurer portal blocks claim details until a human "
                "passes identity verification. AI cannot complete KBA/ID upload."
            ),
            "prepared_brief": (
                "Call or use the portal with photo ID ready. Confirm claim reference "
                "CLAIM-SIM-409. After verification, record the status result in OUTSOURCE "
                "so the workflow can resume follow-ups."
            ),
            "talking_points": [
                "State claim reference CLAIM-SIM-409",
                "Complete identity challenges exactly as prompted",
                "Ask for current claim status + next required document",
                "Do not share passwords with OUTSOURCE — only the outcome summary",
            ],
            "documents_ready": [
                "Photo ID",
                "Claim reference CLAIM-SIM-409",
                "Policy number on file (user-held; not stored here)",
            ],
        },
        "F06": {
            "follow_ups": [
                "Log insurer status after verification",
                "Send approved work update to Jordan Lee",
                "Final MBA Canvas submit before 11:59 PM ET",
            ],
            "closure_status": "PARTIAL — waiting on human verification result",
            "notes": "Workflow resumes when user pastes verification outcome.",
        },
    }


class WorkflowEngine:
    def __init__(self, llm: LLMClient | None = None) -> None:
        self.settings = get_settings()
        self.llm = llm or LLMClient(self.settings)

    def run_priority0(
        self,
        user_request: str,
        progress: ProgressCb = _noop,
        now: datetime | None = None,
        permission_mode: PermissionMode | None = None,
        approve_ai_execution: bool = False,
    ) -> WorkflowState:
        now = now or datetime.now()
        mode = self.settings.effective_mode
        perm = permission_mode or normalize_permission(get_permission_mode())
        bp = load_blueprint()
        state = WorkflowState(user_request=user_request, mode=mode, blueprint_snapshot=bp)
        state.transition(TaskStatus.ANALYZING, "Intake started")
        progress("Loading Life Blueprint goals…")
        progress(f"Permission mode: {perm.value}")

        goals = [g.title for g in bp.goals]
        fixtures = _demo_fixtures(user_request, goals)

        # Seed busy calendar: wedding block (fixed)
        wedding_start = now.replace(hour=16, minute=0, second=0, microsecond=0)
        if wedding_start < now:
            wedding_start = now + timedelta(hours=2)
        wedding_end = wedding_start + timedelta(hours=4)
        busy = [
            CalendarSlot(
                title="Wedding (fixed)",
                start=wedding_start,
                end=wedding_end,
                public_description="Attend wedding",
            )
        ]
        state.calendar_slots.extend(busy)

        # A01 Chief of Staff
        progress("A01 Chief of Staff — intake…")
        a01 = ChiefOfStaff(self.llm)
        cos, rec = a01.run(
            f"User request: {user_request}\nGoals: {goals}",
            fixtures["A01"],
        )
        state.agent_calls.append(rec)
        state.evidence.append(
            EvidenceRecord(
                evidence_type=EvidenceType.USER_PROVIDED,
                source="user_request",
                summary=user_request,
                agent_id="A01",
                confidence=1.0,
            )
        )

        # A02 Life Strategy
        progress("A02 Life Strategy Architect — reading goals…")
        a02 = LifeStrategyArchitect(self.llm)
        strat, rec = a02.run(
            f"Blueprint goals: {[g.model_dump() for g in bp.goals]}\nCoS: {cos}",
            fixtures["A02"],
        )
        state.agent_calls.append(rec)

        # B01 Opportunity cost
        progress("B01 Opportunity Cost Economist — deciding…")
        state.transition(TaskStatus.PLANNED, "Building opportunity-cost plan")
        b01 = OpportunityCostEconomist(self.llm)
        econ, rec = b01.run(
            f"Request: {user_request}\nStrategy: {strat}\nConstraints: {cos.get('constraints')}",
            fixtures["B01"],
        )
        state.agent_calls.append(rec)

        options = [
            OpportunityCostItem(
                label=o["label"],
                time_hours=float(o.get("time_hours") or 0),
                monetary_usd=o.get("monetary_usd"),
                qualitative_value=o.get("qualitative_value") or "",
                goal_alignment=list(o.get("goal_alignment") or []),
                risk_notes=o.get("risk_notes") or "",
                recommended=bool(o.get("recommended")),
            )
            for o in econ.get("options", [])
        ]
        state.decision_plan = DecisionPlan(
            situation=user_request,
            constraints=list(cos.get("constraints") or []),
            options=options,
            recommended_sequence=list(econ.get("recommended_sequence") or []),
            tradeoffs=list(econ.get("tradeoffs") or []),
            assumptions=list(econ.get("assumptions") or []),
            uncertainty_notes=str(econ.get("uncertainty_notes") or ""),
            evidence=[
                EvidenceRecord(
                    evidence_type=EvidenceType.MODELED_ASSUMPTION
                    if mode == "live"
                    else EvidenceType.SIMULATED_FIXTURE,
                    source="B01 Opportunity Cost Economist",
                    summary="Opportunity-cost comparison across obligations",
                    agent_id="B01",
                    labeled_demo=(mode == "demo"),
                    confidence=0.7,
                )
            ],
        )

        # F02 Decomposition
        progress("F02 Task Decomposition — AI vs human…")
        f02 = TaskDecomposition(self.llm)
        decomp, rec = f02.run(
            f"Plan sequence: {econ.get('recommended_sequence')}\nStrategy: {strat}",
            fixtures["F02"],
        )
        state.agent_calls.append(rec)
        for wp in decomp.get("work_packages", []):
            state.work_packages.append(
                WorkPackage(
                    title=str(wp.get("title") or "Untitled package"),
                    assignee=_normalize_assignee(wp.get("assignee")),  # type: ignore[arg-type]
                    rationale=wp.get("rationale") or "",
                    depends_on=list(wp.get("depends_on") or []),
                )
            )

        # F03 Execution (gated by permissions)
        auto_ok = may_auto_execute(perm) or approve_ai_execution
        if not auto_ok:
            progress("REVIEW_ALL: skipping autonomous execution until approved.")
            state.transition(
                TaskStatus.PLANNED,
                "REVIEW_ALL — AI packages await explicit approval",
            )
            state.digital_deliverables.append(
                "Autonomous execution blocked by REVIEW_ALL. Approve AI execution to continue."
            )
            self._persist(state)
            return state

        progress("F03 Autonomous Execution — doing AI work…")
        state.transition(TaskStatus.EXECUTING, "Executing AI packages")
        f03 = AutonomousExecution(self.llm)
        exec_out, rec = f03.run(
            f"AI packages: {[w.model_dump() for w in state.work_packages if w.assignee == 'AI']}",
            fixtures["F03"],
        )
        state.agent_calls.append(rec)

        ai_packages = [w for w in state.work_packages if w.assignee == "AI"]
        for item in exec_out.get("executed", []):
            title = item.get("title")
            matched = False
            for wp in state.work_packages:
                if wp.title == title:
                    matched = True
                    wp.deliverable_summary = item.get("deliverable_summary")
                    if item.get("status") == "BLOCKED_HUMAN":
                        wp.status = TaskStatus.BLOCKED_HUMAN
                        wp.blocker = "Identity verification required"
                    else:
                        wp.status = TaskStatus.COMPLETED
                    if wp.deliverable_summary:
                        state.digital_deliverables.append(wp.deliverable_summary)
            # Live models may paraphrase titles — attach leftover deliverables in order
            if not matched and ai_packages:
                wp = ai_packages.pop(0)
                wp.deliverable_summary = item.get("deliverable_summary")
                if item.get("status") == "BLOCKED_HUMAN":
                    wp.status = TaskStatus.BLOCKED_HUMAN
                    wp.blocker = "Identity verification required"
                else:
                    wp.status = TaskStatus.COMPLETED
                if wp.deliverable_summary:
                    state.digital_deliverables.append(wp.deliverable_summary)

        # Simulated insurer barrier
        progress("Simulated insurer portal check…")
        insurer = check_claim_status("CLAIM-SIM-409")
        state.evidence.append(insurer.evidence)
        state.digital_deliverables.append(insurer.message)

        # F05 Handoff brief
        progress("F05 Human Intervention — preparing brief…")
        state.transition(TaskStatus.BLOCKED_HUMAN, "Identity verification barrier")
        f05 = HumanHandoff(self.llm)
        handoff, rec = f05.run(
            f"Blocker: {insurer.message}\nNext action: {insurer.next_human_action}",
            fixtures["F05"],
        )
        state.agent_calls.append(rec)

        intervention = HumanIntervention(
            title=handoff.get("title") or "Insurer identity verification",
            why_human_required=handoff.get("why_human_required") or insurer.next_human_action,
            prepared_brief=handoff.get("prepared_brief") or "",
            talking_points=list(handoff.get("talking_points") or []),
            documents_ready=list(handoff.get("documents_ready") or []),
            status="PREPARED",
            sensitive=True,
        )

        # F04 Calendar + ICS
        progress("F04 Calendar — scheduling human slot + ICS…")
        f04 = CalendarLogistics(self.llm)
        cal, rec = f04.run(
            f"Intervention: {intervention.title}\nBusy: wedding {wedding_start}–{wedding_end}",
            fixtures["F04"],
        )
        state.agent_calls.append(rec)

        req = (cal.get("scheduling_requests") or [{}])[0]
        # Prefer a slot before the wedding if possible
        slot = find_slot(
            title=req.get("title") or intervention.title,
            duration_minutes=int(req.get("duration_minutes") or 30),
            busy=busy,
            search_start=now + timedelta(minutes=15),
            deadline=wedding_start,
            public_description=req.get("public_description")
            or "Personal admin call — details in OUTSOURCE private brief",
            private_brief_ref=intervention.intervention_id,
        )
        if slot is None:
            # After wedding as fallback
            slot = find_slot(
                title=req.get("title") or intervention.title,
                duration_minutes=int(req.get("duration_minutes") or 30),
                busy=busy,
                search_start=wedding_end + timedelta(minutes=30),
                public_description=req.get("public_description")
                or "Personal admin call — details in OUTSOURCE private brief",
                private_brief_ref=intervention.intervention_id,
            )

        if slot:
            ics_dir = get_settings().data_dir / "ics"
            ics_path = export_ics(slot, ics_dir / f"{slot.slot_id}.ics")
            intervention.suggested_slot = slot
            intervention.ics_path = str(ics_path)
            intervention.status = "WAITING_RESULT"
            state.calendar_slots.append(slot)
        else:
            intervention.status = "PREPARED"
            state.digital_deliverables.append(
                "No calendar slot found before/after constraints; brief prepared without ICS."
            )

        state.interventions.append(intervention)
        state.transition(TaskStatus.WAITING_RESULT, "ICS prepared; awaiting user result")
        progress("Waiting for human verification result…")

        self._persist(state)
        return state

    def resume_with_result(
        self,
        state: WorkflowState,
        user_result: str,
        progress: ProgressCb = _noop,
    ) -> WorkflowState:
        progress("Recording human result and resuming…")
        state.transition(TaskStatus.RESUMING, "User provided verification result")
        if state.interventions:
            hi = state.interventions[-1]
            hi.user_result = user_result
            hi.status = "RESOLVED"

        for wp in state.work_packages:
            if wp.status == TaskStatus.BLOCKED_HUMAN:
                wp.status = TaskStatus.COMPLETED
                wp.blocker = None
                wp.deliverable_summary = (
                    (wp.deliverable_summary or "")
                    + f" | Human result: {user_result}"
                )

        fixtures = _demo_fixtures(state.user_request, [])
        f06 = FollowUp(self.llm)
        follow, rec = f06.run(
            f"User verification result: {user_result}\nWork packages: "
            f"{[w.model_dump() for w in state.work_packages]}",
            {
                **fixtures["F06"],
                "closure_status": "RESUMED",
                "follow_ups": [
                    "Confirm claim next step from insurer result",
                    "Send approved work update",
                    "Submit MBA final before deadline",
                ],
                "notes": f"Resumed after user result: {user_result}",
            },
        )
        state.agent_calls.append(rec)
        state.follow_ups = list(follow.get("follow_ups") or [])
        state.digital_deliverables.append(
            f"Follow-up plan: {follow.get('closure_status')} — {follow.get('notes')}"
        )
        state.evidence.append(
            EvidenceRecord(
                evidence_type=EvidenceType.USER_PROVIDED,
                source="human_intervention_result",
                summary=user_result,
                agent_id="F06",
                confidence=1.0,
            )
        )
        state.transition(TaskStatus.COMPLETED, "Workflow completed after human resume")
        progress("Workflow complete.")
        self._persist(state)
        return state

    def _persist(self, state: WorkflowState) -> None:
        save_workflow(
            state.model_dump_json(),
            state.workflow_id,
            state.updated_at.isoformat() + "Z",
        )
