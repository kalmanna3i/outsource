"""Strategic Radar Streamlit views."""

from __future__ import annotations

from datetime import datetime
from html import escape
from pathlib import Path

import streamlit as st

from agents.registry import AGENT_REGISTRY
from core.models import EvidenceType, WorkflowState
from core.radar_models import DiscoveryRun, ExecutionPackage, OpportunityRecord, RadarSchedule
from database.db import get_setting_json, load_blueprint, set_setting_json
from services.radar import RadarEngine
from services.radar_graph import EDGE_STYLE, build_graph, figure

_CLASS_BADGE = {
    "GENUINE_OPPORTUNITY": ("badge-genuine", "Genuine opportunity", ""),
    "DISTRACTION": ("badge-distraction", "Distraction", "distraction"),
    "NEEDS_REVIEW": ("badge-review", "Needs review", "review"),
    "UNSCORED": ("badge-review", "Unscored", "review"),
}


def _verification_badge(opp: OpportunityRecord) -> str:
    if opp.verification_status == EvidenceType.VERIFIED_SOURCE:
        return '<span class="badge badge-ver">VERIFIED_SOURCE</span>'
    if opp.verification_status == EvidenceType.SIMULATED_FIXTURE:
        return '<span class="badge badge-sim">SIMULATED_FIXTURE · Illustrative</span>'
    return f'<span class="badge badge-unv">{escape(opp.verification_status.value)}</span>'


def _card(opp: OpportunityRecord) -> str:
    badge_cls, badge_label, card_cls = _CLASS_BADGE[opp.classification]
    rows = "".join(
        f"<b>{q.upper()}</b><span>{escape(getattr(opp, q) or '—')}</span>"
        for q in ("who", "what", "when", "where", "why", "how", "cost")
    )
    score = f"{opp.alignment_score:g}/10" if opp.alignment_score is not None else "—"
    money = (
        f"${opp.estimated_financial_cost:,.0f}" if opp.estimated_financial_cost is not None else "unknown"
    )
    conflicts = (
        "<div class='muted' style='margin-top:.35rem'>Conflicts: "
        + escape("; ".join(opp.potential_conflicts)) + "</div>"
        if opp.potential_conflicts else ""
    )
    return f"""
    <div class="opp-card {card_cls}">
      <div class="opp-cat">{escape(opp.category or opp.opportunity_type)} · {escape(opp.mission_area or '—')}</div>
      <div class="opp-title">{escape(opp.title)}</div>
      <div>{_verification_badge(opp)}<span class="badge {badge_cls}">{badge_label}</span>
        <span class="muted">Mission fit {score} · Money (separate): {money} · Found by {escape(', '.join(opp.discovered_by))}</span></div>
      <div style="margin-top:.4rem">{escape(opp.description)}</div>
      <div class="opp-grid">{rows}</div>
      <div class="muted" style="margin-top:.35rem">{escape(opp.mission_alignment_reason)}</div>
      {conflicts}
      <div class="next-action">Recommended next action: {escape(opp.recommended_next_action or '—')}</div>
    </div>
    """


def _run_discovery() -> DiscoveryRun:
    progress: list[str] = []
    run = RadarEngine().discover(load_blueprint(), progress=progress.append)
    st.session_state.radar_run = run
    st.session_state.radar_log = progress
    st.session_state.radar_exec = None
    return run


def render_radar() -> None:
    st.subheader("Strategic Radar")
    st.caption("The art of building an intentional life — discover what should be on your list.")
    st.markdown(
        '<p class="status-sim">Simulated discovery: demo mode uses labeled SIMULATED_FIXTURE '
        "opportunities (illustrative, not live research). No web search, LinkedIn or calendar "
        "integration is wired; live mode returns model-generated leads marked UNVERIFIED. "
        "Research-to-action (draft, schedule, ICS, brief, follow-up) is Operational. "
        "Nothing is ever sent.</p>",
        unsafe_allow_html=True,
    )
    if st.button("Run discovery now", type="primary"):
        with st.spinner("Strategic Intelligence Department scanning…"):
            _run_discovery()
    run: DiscoveryRun | None = st.session_state.get("radar_run")
    if run is None:
        _run_discovery()
        run = st.session_state.radar_run

    c1, c2, c3, c4 = st.columns(4)
    for col, label, val in (
        (c1, "Candidates found", run.candidates_raw),
        (c2, "Duplicates merged", run.duplicates_merged),
        (c3, "Genuine opportunities", len(run.genuine)),
        (c4, "Distractions filtered", len(run.distractions)),
    ):
        col.markdown(
            f'<div class="panel"><div class="muted">{label}</div><div class="kpi">{val}</div></div>',
            unsafe_allow_html=True,
        )
    st.caption(f"Mode: {run.mode.upper()} · {len(run.agent_calls)} agent calls · " + " ".join(run.notes))

    feed, graph_tab, action, agents_tab = st.tabs(
        ["Radar feed", "Strategic network", "Research → action", "Intelligence agents"]
    )
    with feed:
        st.markdown("#### Genuine opportunities")
        for opp in run.opportunities:
            if opp.classification == "GENUINE_OPPORTUNITY":
                st.markdown(_card(opp), unsafe_allow_html=True)
        review = [o for o in run.opportunities if o.classification == "NEEDS_REVIEW"]
        if review:
            st.markdown("#### Needs your review")
            for opp in review:
                st.markdown(_card(opp), unsafe_allow_html=True)
        with st.expander(f"Distractions filtered by the Mission Alignment Auditor ({len(run.distractions)})"):
            for opp in run.distractions:
                st.markdown(_card(opp), unsafe_allow_html=True)
    with graph_tab:
        render_network_graph()
    with action:
        _render_action(run)
    with agents_tab:
        st.dataframe(
            [
                {"Agent": e.agent_id, "Role": e.role, "Module": e.module, "Status": e.status, "Note": e.note}
                for e in AGENT_REGISTRY
            ],
            use_container_width=True,
            hide_index=True,
        )
        for line in st.session_state.get("radar_log", []):
            st.text(line)


def render_network_graph() -> None:
    graph = build_graph()
    st.markdown(
        "Solid green edges are **VERIFIED** (cited public source with retrieval date). "
        "Dashed amber edges are **HYPOTHETICAL** introduction paths: unverified and never "
        "presented as real relationships. Illustrative personas are labeled."
    )
    st.plotly_chart(figure(graph), use_container_width=True)
    st.markdown("**Legend**")
    for status, style in EDGE_STYLE.items():
        n = sum(1 for e in graph.edges if e.status == status)
        dash = {"solid": "━━━", "dash": "╍╍╍", "dot": "┈┈┈"}[style["dash"]]
        st.markdown(
            f"<span style='color:{style['color']};font-weight:700'>{dash}</span> "
            f"{style['label']} — {n} edge(s)",
            unsafe_allow_html=True,
        )
    for e in graph.edges:
        if e.status == "VERIFIED":
            st.caption(f"Verified: {e.source} → {e.target} ({e.relation}). Source: {e.source_url}, retrieved {e.retrieved_at}.")


def _busy_slots():
    wf: WorkflowState | None = st.session_state.get("workflow")
    return list(wf.calendar_slots) if wf else []


def _render_action(run: DiscoveryRun) -> None:
    options = run.genuine + [o for o in run.opportunities if o.classification == "NEEDS_REVIEW"]
    if not options:
        st.info("No genuine opportunities to act on.")
        return
    labels = {o.title: o for o in options}
    default = next((i for i, o in enumerate(options) if o.category == "Academic collaboration"), 0)
    choice = st.selectbox("Select an opportunity to pursue", list(labels), index=default)
    if st.button("Prepare research-to-action package"):
        with st.spinner("F03 → F04 → F05 → F06…"):
            st.session_state.radar_exec = RadarEngine().execute(
                labels[choice], now=datetime.now(), busy=_busy_slots()
            )
    pkg: ExecutionPackage | None = st.session_state.get("radar_exec")
    if not pkg:
        st.caption("Uses the existing scheduler, ICS export, human handoff and follow-up agents.")
        return
    st.markdown(f"### {escape(pkg.opportunity_title)}")
    st.markdown(
        '<span class="badge badge-distraction">DRAFT — NOT SENT</span>'
        '<span class="muted">OUTSOURCE never sends outreach. You review and send it yourself.</span>',
        unsafe_allow_html=True,
    )
    d = pkg.outreach_draft
    st.text_input("To", d.to, disabled=True)
    st.text_input("Channel", d.channel, disabled=True)
    st.text_input("Subject", d.subject, disabled=True)
    st.text_area("Body (draft)", d.body, height=200)
    st.caption(f"Contact / registration: {pkg.contact_info or '—'}")
    a, b = st.columns(2)
    with a:
        st.markdown("**Conversation topics**")
        for t in pkg.conversation_topics:
            st.write(f"- {t}")
        st.markdown("**Preparation**")
        for p in pkg.preparation_requirements:
            st.write(f"- {p}")
        st.caption(f"Estimated prep: {pkg.prep_minutes} min · {pkg.travel_estimate}")
    with b:
        st.markdown("**Calendar (existing scheduler)**")
        if pkg.calendar_slot:
            s = pkg.calendar_slot
            st.write(f"{s.title}: **{s.start:%a %b %d %H:%M} → {s.end:%H:%M}**")
            st.caption(f"Public calendar text: {s.public_description}")
            if pkg.ics_path and Path(pkg.ics_path).exists():
                st.download_button(
                    "Download ICS", Path(pkg.ics_path).read_text(encoding="utf-8"),
                    file_name=Path(pkg.ics_path).name, mime="text/calendar",
                )
        else:
            st.warning("No free business-hours slot before the deadline.")
        st.markdown("**Follow-up plan**")
        for f in pkg.follow_up_plan:
            st.write(f"- {f}")
    if pkg.intervention:
        hi = pkg.intervention
        with st.expander(f"Human intervention brief — {hi.title}", expanded=True):
            st.write(hi.why_human_required)
            st.write(hi.prepared_brief)
            for t in hi.talking_points:
                st.write(f"- {t}")
    st.caption(
        f"{len(pkg.agent_calls)} agent calls ({pkg.mode}) · evidence: "
        + ", ".join(e.evidence_type.value for e in pkg.evidence)
    )


def load_schedule() -> RadarSchedule:
    raw = get_setting_json("radar_schedule")
    return RadarSchedule.model_validate_json(raw) if raw else RadarSchedule()


def render_radar_settings() -> None:
    st.markdown("#### Strategic Radar — continuous discovery")
    st.markdown(
        '<p class="status-plan">Background monitoring: Planned. No scheduler process runs; '
        "these preferences are saved for when it is built. Use “Run discovery now” on the "
        "Strategic Radar page.</p>",
        unsafe_allow_html=True,
    )
    sch = load_schedule()
    c1, c2, c3 = st.columns(3)
    daily = c1.checkbox("Daily briefing", sch.daily_briefing)
    daily_time = c1.text_input("Daily time", sch.daily_time)
    weekly = c2.checkbox("Weekly networking review", sch.weekly_networking_review)
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekly_day = c2.selectbox("Weekly day", days, index=days.index(sch.weekly_day))
    monthly = c3.checkbox("Monthly career / mission review", sch.monthly_mission_review)
    monthly_day = c3.number_input("Day of month", 1, 28, sch.monthly_day)
    event = st.checkbox("Event-triggered research", sch.event_triggered_research)
    if st.button("Save discovery schedule"):
        new = RadarSchedule(
            daily_briefing=daily, daily_time=daily_time, weekly_networking_review=weekly,
            weekly_day=weekly_day, monthly_mission_review=monthly, monthly_day=int(monthly_day),
            event_triggered_research=event,
        )
        set_setting_json("radar_schedule", new.model_dump_json())
        st.success("Saved schedule preferences (monitoring remains Planned).")
