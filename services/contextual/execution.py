"""Draft execution package: itinerary, calendar, ICS, meeting request — authorization required."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from core.contextual_models import ContextualExecution, ContextualOpportunity, TravelContext
from core.models import CalendarSlot, HumanIntervention, new_id
from services.scheduler import export_ics, find_slot


def prepare_execution(
    opp: ContextualOpportunity,
    ctx: TravelContext,
    *,
    data_dir: Path | None = None,
) -> ContextualExecution:
    base = data_dir or Path("data/contextual_ics")
    base.mkdir(parents=True, exist_ok=True)

    start = ctx.window_start + timedelta(minutes=opp.prep_time_minutes + 30)
    duration = max(30, opp.incremental_time_minutes)
    slot = find_slot(
        title=opp.title[:80],
        duration_minutes=duration,
        busy=[],
        search_start=start,
        deadline=ctx.window_end - timedelta(minutes=60),
        public_description=f"Contextual opportunity (draft): {opp.what[:120]}",
    )
    slots: list[CalendarSlot] = []
    ics_paths: list[str] = []
    if slot:
        slots.append(slot)
        path = export_ics(slot, base / f"{opp.opportunity_id}.ics")
        ics_paths.append(str(path))

    itinerary = (
        f"## Draft itinerary — {opp.title}\n\n"
        f"- **Context:** {ctx.label}\n"
        f"- **When:** {opp.when}\n"
        f"- **Where:** {opp.where}\n"
        f"- **Transport:** {opp.transport_requirements}\n"
        f"- **Prep:** {opp.prep_time_minutes} min\n"
        f"- **Access:** {opp.access_requirements}\n\n"
        f"**Status:** requires your authorization before any booking or send.\n"
    )
    meeting = (
        f"Subject: {ILL_PREFIX}Meeting request — {opp.what[:60]}\n\n"
        f"Hello,\n\n"
        f"I'll be in the area during {ctx.label} and would value 30–45 minutes to discuss "
        f"{opp.what.lower()}. This message is a **draft only** and has not been sent.\n\n"
        f"Best,\nKay Al Mannai\n"
    )
    reg_opts = [
        f"Option A: Register via public link (draft) — {opp.access_requirements}",
        "Option B: Add to calendar block only (no registration)",
        "Option C: Decline and keep original itinerary",
    ]
    hi = HumanIntervention(
        intervention_id=new_id("hi"),
        title=f"Authorize contextual opportunity: {opp.title[:60]}",
        why_human_required="Purchases, reservations, and outreach require explicit authorization.",
        prepared_brief=(
            f"Review feasibility ({opp.feasibility_status}), alignment score "
            f"{opp.alignment_score}, and incremental cost ${opp.incremental_cost_usd:.2f}. "
            "Then approve send/register/book."
        ),
        talking_points=[opp.why, opp.how, *opp.strategic_benefits[:2]],
        documents_ready=["Draft meeting request", "ICS calendar block", "Registration options"],
        suggested_slot=slot,
        ics_path=ics_paths[0] if ics_paths else None,
        status="PREPARED",
    )
    return ContextualExecution(
        opportunity_id=opp.opportunity_id,
        itinerary_markdown=itinerary,
        calendar_slots=slots,
        ics_paths=ics_paths,
        meeting_request_draft=meeting,
        registration_options=reg_opts,
        human_intervention=hi,
    )


ILL_PREFIX = "[Illustrative draft] "