"""Strategic Radar: discovery pipeline, dedup, mission audit and research-to-action."""

from __future__ import annotations

import re
from datetime import date, datetime, timedelta
from difflib import SequenceMatcher
from typing import Any, Callable

from agents.radar import INTELLIGENCE_AGENTS, MissionAlignmentAuditor
from agents.specialists import AutonomousExecution, CalendarLogistics, FollowUp, HumanHandoff
from core.config import Settings, get_settings
from core.llm import LLMClient
from core.models import CalendarSlot, EvidenceType, HumanIntervention, LifeBlueprint
from core.radar_models import (
    DiscoveryRun,
    ExecutionPackage,
    OpportunityRecord,
    OutreachDraft,
)
from database.db import save_opportunity, seen_opportunity_keys
from services.radar_fixtures import intelligence_fixtures
from services.scheduler import export_ics, find_slot
from services.workflow import _to_number

ProgressCb = Callable[[str], None]

GENUINE_MIN_SCORE = 6.0
DISTRACTION_MAX_SCORE = 5.0
LARGE_COMMITMENT_USD = 2500.0
HUMAN_TYPES = {"introduction", "collaboration", "speaking", "milestone", "event", "meeting"}

_STOP = {
    "about", "their", "there", "which", "would", "could", "should", "within", "years",
    "with", "from", "that", "this", "your", "into", "stay", "build", "close",
}


def _noop(_: str) -> None:
    pass


def _tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z]+", text.lower()) if len(t) > 4 and t not in _STOP}


def _norm_title(title: str) -> str:
    t = title.lower().replace("[illustrative]", "").replace("&", "and")
    return " ".join(re.sub(r"[^a-z0-9 ]+", " ", t).split())


def dedup_key(opp: OpportunityRecord) -> str:
    words = " ".join(sorted(set(re.findall(r"[a-z0-9]+", _norm_title(opp.title)))))
    return f"{opp.opportunity_type.lower()}|{opp.event_date_or_deadline or ''}|{words}"


def _is_duplicate(a: OpportunityRecord, b: OpportunityRecord) -> bool:
    if dedup_key(a) == dedup_key(b):
        return True
    if a.opportunity_type.lower() != b.opportunity_type.lower():
        return False
    ratio = SequenceMatcher(None, _norm_title(a.title), _norm_title(b.title)).ratio()
    same_date = (a.event_date_or_deadline or "") == (b.event_date_or_deadline or "")
    return ratio >= 0.85 or (same_date and ratio >= 0.7)


def deduplicate(candidates: list[OpportunityRecord]) -> tuple[list[OpportunityRecord], int]:
    """Merge duplicate candidates, keeping sources and discovering agents from both."""
    kept: list[OpportunityRecord] = []
    merged = 0
    for cand in candidates:
        match = next((k for k in kept if _is_duplicate(k, cand)), None)
        if match is None:
            kept.append(cand.model_copy(deep=True))
            continue
        merged += 1
        for agent in cand.discovered_by:
            if agent not in match.discovered_by:
                match.discovered_by.append(agent)
        for url in cand.source_urls:
            if url not in match.source_urls:
                match.source_urls.append(url)
    return kept, merged


def _objectives(bp: LifeBlueprint) -> list[tuple[str, str]]:
    out = []
    for obj in bp.strategic_objectives:
        area, _, detail = obj.partition(":")
        out.append((area.strip().lower(), obj))
    return out


def _parse_date(raw: str | None) -> date | None:
    if not raw:
        return None
    try:
        return date.fromisoformat(raw[:10])
    except ValueError:
        return None


def audit_opportunity(opp: OpportunityRecord, bp: LifeBlueprint) -> dict[str, Any]:
    """Deterministic Mission Alignment audit. Money never enters the score."""
    objectives = _objectives(bp)
    text_tokens = _tokens(f"{opp.description} {opp.why} {opp.what}")
    matched: list[str] = []
    score = 0.0
    area = opp.mission_area.strip().lower()
    for obj_area, obj_text in objectives:
        if area and area == obj_area:
            matched.append(obj_text)
            score = max(score, 6.0)
    overlap = 0
    for _, obj_text in objectives:
        overlap += len(text_tokens & _tokens(obj_text))
    score += min(overlap * 0.5, 3.0)

    principles_supported: list[str] = []
    principles_violated: list[str] = []
    conflicts: list[str] = []
    for p in bp.guiding_principles:
        pl = p.lower()
        if "milestone" in pl and opp.opportunity_type == "milestone":
            principles_supported.append(p)
            score += 1.0
        if "financial" in pl and (opp.estimated_financial_cost or 0) >= LARGE_COMMITMENT_USD:
            principles_violated.append(p)
            conflicts.append(f"${opp.estimated_financial_cost:,.0f} commitment conflicts with '{p}'")
        if "prestige" in pl and "prestige_only" in opp.risk_flags:
            principles_violated.append(p)
            conflicts.append(f"Prestige-only offer conflicts with '{p}'")

    when = _parse_date(opp.event_date_or_deadline)
    for g in bp.goals:
        gd = _parse_date(g.target_date)
        if when and gd and when == gd and g.importance >= 9:
            conflicts.append(f"Same day as '{g.title}' (importance {g.importance}/10)")
            focus = next((p for p in bp.guiding_principles if "focus" in p.lower()), None)
            if focus and g.importance >= 10 and focus not in principles_violated:
                principles_violated.append(focus)

    score = round(min(score, 10.0), 1)
    if score < DISTRACTION_MAX_SCORE or principles_violated:
        classification = "DISTRACTION"
    elif conflicts:
        classification = "NEEDS_REVIEW"
    elif score >= GENUINE_MIN_SCORE:
        classification = "GENUINE_OPPORTUNITY"
    else:
        classification = "NEEDS_REVIEW"

    if matched:
        reason = f"Supports objective(s): {'; '.join(matched)}."
    else:
        reason = "No stated strategic objective is advanced by this opportunity."
    if principles_supported:
        reason += f" Honors principle(s): {'; '.join(principles_supported)}."

    top_goal = max(bp.goals, key=lambda g: g.importance).title if bp.goals else "current commitments"
    money = (
        f"${opp.estimated_financial_cost:,.0f}" if opp.estimated_financial_cost is not None else "money unknown"
    )
    hours = f"{opp.estimated_time_hours:g} h" if opp.estimated_time_hours is not None else "time unknown"
    return {
        "opportunity_id": opp.opportunity_id,
        "alignment_score": score,
        "classification": classification,
        "mission_alignment_reason": reason,
        "relevant_strategic_objectives": matched,
        "relevant_guiding_principles": principles_supported + principles_violated,
        "potential_conflicts": conflicts,
        "opportunity_cost": f"{hours} and {money} not spent on '{top_goal}' or other objectives",
    }


def _apply_audit(opp: OpportunityRecord, a: dict[str, Any]) -> None:
    opp.alignment_score = a["alignment_score"]
    opp.classification = a["classification"]
    opp.mission_alignment_reason = a["mission_alignment_reason"]
    opp.relevant_strategic_objectives = a["relevant_strategic_objectives"]
    opp.relevant_guiding_principles = a["relevant_guiding_principles"]
    opp.potential_conflicts = a["potential_conflicts"]
    opp.opportunity_cost = a["opportunity_cost"]


def _as_list(raw: Any) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(x) for x in raw]
    return [str(raw)]


def _coerce(raw: dict[str, Any], agent_id: str, mode: str) -> OpportunityRecord | None:
    title = str(raw.get("title") or "").strip()
    if not title:
        return None
    fields = dict(raw)
    fields.pop("_demo_labeled", None)
    if mode == "live":
        # Model output with no search integration is never treated as verified.
        fields["verification_status"] = EvidenceType.UNVERIFIED
        fields["illustrative"] = False
        fields.pop("source_retrieved_at", None)
    for key in (
        "relevant_people", "relevant_organizations", "source_urls", "conversation_topics",
        "preparation_requirements", "nonfinancial_considerations", "risk_flags",
    ):
        fields[key] = _as_list(fields.get(key))
    cost = fields.get("estimated_financial_cost")
    fields["estimated_financial_cost"] = None if cost in (None, "") else _to_number(cost, 0.0)
    hours = fields.get("estimated_time_hours")
    fields["estimated_time_hours"] = None if hours in (None, "") else _to_number(hours, 0.0)
    for key in ("who", "what", "when", "where", "why", "how", "cost", "description",
                "opportunity_type", "category", "mission_area", "location",
                "event_date_or_deadline", "recommended_next_action",
                "contact_or_registration_info", "estimated_time_commitment"):
        if key in fields and fields[key] is not None and not isinstance(fields[key], str):
            fields[key] = str(fields[key])
    fields.setdefault("opportunity_type", "other")
    fields.setdefault("description", title)
    fields["discovered_by"] = [agent_id]
    try:
        return OpportunityRecord.model_validate(fields)
    except Exception:  # noqa: BLE001 — a malformed lead is dropped, not fatal
        return None


def _blueprint_brief(bp: LifeBlueprint) -> str:
    return (
        f"Mission: {bp.mission}\nGuiding principles: {bp.guiding_principles}\n"
        f"Strategic objectives: {bp.strategic_objectives}\n"
        f"Current goals: {[(g.title, g.target_date, g.importance) for g in bp.goals]}"
    )


class RadarEngine:
    def __init__(self, llm: LLMClient | None = None, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.llm = llm or LLMClient(self.settings)

    def discover(self, bp: LifeBlueprint, progress: ProgressCb = _noop) -> DiscoveryRun:
        mode = self.settings.effective_mode
        run = DiscoveryRun(mode=mode)
        fixtures = intelligence_fixtures()
        brief = _blueprint_brief(bp)

        candidates: list[OpportunityRecord] = []
        for cls in INTELLIGENCE_AGENTS:
            agent = cls(self.llm)
            progress(f"{agent.agent_id} {agent.role} — scanning…")
            try:
                payload, rec = agent.run(brief, fixtures.get(agent.agent_id, {"opportunities": []}))
            except Exception as exc:  # noqa: BLE001
                run.notes.append(f"{agent.agent_id} failed: {exc}")
                if self.llm.records:
                    run.agent_calls.append(self.llm.records[-1])
                continue
            run.agent_calls.append(rec)
            for raw in payload.get("opportunities") or []:
                if isinstance(raw, dict):
                    opp = _coerce(raw, agent.agent_id, mode)
                    if opp:
                        candidates.append(opp)

        run.candidates_raw = len(candidates)
        progress("Deduplicating candidates…")
        unique, merged = deduplicate(candidates)
        run.duplicates_merged = merged

        progress("R08 Mission Alignment Auditor — scoring against mission and principles…")
        audits = {o.opportunity_id: audit_opportunity(o, bp) for o in unique}
        auditor = MissionAlignmentAuditor(self.llm)
        listing = [
            {"opportunity_id": o.opportunity_id, "title": o.title, "description": o.description,
             "when": o.event_date_or_deadline, "cost_usd": o.estimated_financial_cost,
             "mission_area": o.mission_area}
            for o in unique
        ]
        try:
            review, rec = auditor.run(
                f"{brief}\nOpportunities: {listing}",
                {"assessments": list(audits.values())},
            )
            run.agent_calls.append(rec)
        except Exception as exc:  # noqa: BLE001
            review = {}
            run.notes.append(f"R08 model review failed; deterministic audit used: {exc}")

        model_notes = {
            str(a.get("opportunity_id")): a
            for a in (review.get("assessments") or [])
            if isinstance(a, dict)
        }
        for opp in unique:
            _apply_audit(opp, audits[opp.opportunity_id])
            note = model_notes.get(opp.opportunity_id)
            if mode == "live" and note and note.get("mission_alignment_reason"):
                opp.mission_alignment_reason += f" Model review: {note['mission_alignment_reason']}"

        order = {"GENUINE_OPPORTUNITY": 0, "NEEDS_REVIEW": 1, "DISTRACTION": 2, "UNSCORED": 3}
        unique.sort(key=lambda o: (order[o.classification], -(o.alignment_score or 0)))
        run.opportunities = unique

        seen = seen_opportunity_keys()
        now_iso = datetime.utcnow().isoformat() + "Z"
        for opp in unique:
            key = dedup_key(opp)
            if key not in seen:
                run.new_opportunity_ids.append(opp.opportunity_id)
            save_opportunity(key, opp.model_dump_json(), now_iso)
            run.evidence.extend(opp.evidence())
        meaningful = [o for o in unique if o.opportunity_id in run.new_opportunity_ids
                      and o.classification == "GENUINE_OPPORTUNITY"]
        run.notes.append(
            f"{len(meaningful)} meaningful new opportunities (new + genuine) would trigger a notification."
        )
        progress("Discovery complete.")
        return run

    def execute(
        self,
        opp: OpportunityRecord,
        now: datetime | None = None,
        busy: list[CalendarSlot] | None = None,
        progress: ProgressCb = _noop,
    ) -> ExecutionPackage:
        """Research-to-action: draft (never send), prep, schedule + ICS, brief, follow-up."""
        now = now or datetime.now()
        busy = list(busy or [])
        mode = self.settings.effective_mode
        contact = opp.relevant_people[0] if opp.relevant_people else (
            opp.relevant_organizations[0] if opp.relevant_organizations else "organizer"
        )
        prep_minutes = int(min(max((opp.estimated_time_hours or 1.0) * 60 * 0.4, 30), 120))
        travel = (
            "No travel (remote)" if (opp.location or "").lower() in ("online", "video call")
            else f"Travel to {opp.location}: estimate before confirming" if opp.location else "Unknown"
        )

        progress("F03 Autonomous Execution — drafting outreach (not sent)…")
        f03 = AutonomousExecution(self.llm)
        draft_fixture = {
            "executed": [{
                "title": "Outreach draft",
                "deliverable_summary": "Draft prepared; not sent — awaiting human approval.",
                "status": "COMPLETED",
                "subject": f"Introduction — {opp.category or opp.title}",
                "body": (
                    "Hello,\n\nI'm Kay Al Mannai, an MBA candidate at Yale SOM. "
                    f"I'm reaching out about: {opp.what or opp.description}.\n\n"
                    f"Why it matters to me: {opp.why or opp.mission_alignment_reason}.\n\n"
                    "Would you be open to a brief conversation? Topics I'd value your view on: "
                    f"{'; '.join(opp.conversation_topics[:2]) or 'your current work'}.\n\n"
                    "Thank you for considering it,\nKay"
                ),
            }],
            "blockers": [],
        }
        out, rec = f03.run(
            f"Draft (do not send) a short outreach message for this opportunity: {opp.model_dump_json()}. "
            "Return the draft in executed[0] with keys subject and body.",
            draft_fixture,
        )
        calls = [rec]
        item = (out.get("executed") or [{}])[0] if isinstance(out.get("executed"), list) else {}
        item = item if isinstance(item, dict) else {}
        draft = OutreachDraft(
            to=contact,
            channel="email" if opp.opportunity_type != "event" else "registration form",
            subject=str(item.get("subject") or draft_fixture["executed"][0]["subject"]),
            body=str(item.get("body") or draft_fixture["executed"][0]["body"]),
        )

        progress("F04 Calendar — finding a slot with the existing scheduler…")
        f04 = CalendarLogistics(self.llm)
        cal, rec = f04.run(
            f"Opportunity: {opp.title}. Prep minutes: {prep_minutes}. Busy: "
            f"{[(b.title, b.start.isoformat(), b.end.isoformat()) for b in busy]}",
            {"scheduling_requests": [{
                "title": f"Prep + outreach: {opp.category or 'opportunity'}",
                "duration_minutes": prep_minutes,
                "public_description": "Strategic Radar prep block — details in OUTSOURCE",
            }]},
        )
        calls.append(rec)
        req = (cal.get("scheduling_requests") or [{}])[0]
        req = req if isinstance(req, dict) else {}
        deadline_d = _parse_date(opp.event_date_or_deadline)
        deadline = datetime.combine(deadline_d, datetime.min.time()) if deadline_d else None
        if deadline and deadline <= now:
            deadline = None
        slot = find_slot(
            title=str(req.get("title") or f"Prep + outreach: {opp.category or 'opportunity'}"),
            duration_minutes=int(_to_number(req.get("duration_minutes"), prep_minutes)),
            busy=busy,
            search_start=now + timedelta(days=1),
            deadline=deadline,
            public_description=str(req.get("public_description")
                                   or "Strategic Radar prep block — details in OUTSOURCE"),
        )
        ics_path = None
        if slot:
            ics_path = str(export_ics(slot, self.settings.data_dir / "ics" / f"radar_{slot.slot_id}.ics"))

        intervention = None
        if opp.opportunity_type in HUMAN_TYPES:
            progress("F05 Human Intervention — preparing brief…")
            f05 = HumanHandoff(self.llm)
            hb, rec = f05.run(
                f"Prepare a human brief for pursuing: {opp.model_dump_json()}",
                {
                    "title": f"Your move: {opp.category or opp.title}",
                    "why_human_required": (
                        "Relationship-building and any commitment must come from you; "
                        "OUTSOURCE drafts but never sends outreach or accepts on your behalf."
                    ),
                    "prepared_brief": f"{opp.description} Next action: {opp.recommended_next_action}.",
                    "talking_points": opp.conversation_topics,
                    "documents_ready": opp.preparation_requirements,
                },
            )
            calls.append(rec)
            intervention = HumanIntervention(
                title=str(hb.get("title") or f"Your move: {opp.title}"),
                why_human_required=str(hb.get("why_human_required") or "Human relationship step"),
                prepared_brief=str(hb.get("prepared_brief") or opp.description),
                talking_points=_as_list(hb.get("talking_points")),
                documents_ready=_as_list(hb.get("documents_ready")),
                suggested_slot=slot,
                ics_path=ics_path,
                status="SCHEDULED" if slot else "PREPARED",
                sensitive=False,
            )
            if slot:
                slot.private_brief_ref = intervention.intervention_id

        progress("F06 Follow-Up — building follow-up plan…")
        f06 = FollowUp(self.llm)
        fu, rec = f06.run(
            f"Opportunity: {opp.title}. Outreach is a draft awaiting the user's approval. "
            "List follow-ups and closure criteria.",
            {
                "follow_ups": [
                    "Review and personally send (or discard) the outreach draft",
                    "If no reply in 7 days, one polite follow-up (draft on request)",
                    "After the conversation, log outcome and next step in OUTSOURCE",
                    "Re-audit mission fit after first contact",
                ],
                "closure_status": "OPEN — awaiting user decision on outreach",
                "notes": "Nothing has been sent.",
            },
        )
        calls.append(rec)
        follow_ups = [
            str(f.get("item") or f) if isinstance(f, dict) else str(f)
            for f in (fu.get("follow_ups") or [])
        ]

        return ExecutionPackage(
            opportunity_id=opp.opportunity_id,
            opportunity_title=opp.title,
            outreach_draft=draft,
            contact_info=opp.contact_or_registration_info,
            conversation_topics=opp.conversation_topics,
            preparation_requirements=opp.preparation_requirements,
            prep_minutes=prep_minutes,
            travel_estimate=travel,
            calendar_slot=slot,
            ics_path=ics_path,
            intervention=intervention,
            follow_up_plan=follow_ups,
            agent_calls=calls,
            evidence=opp.evidence(),
            mode=mode,
        )
