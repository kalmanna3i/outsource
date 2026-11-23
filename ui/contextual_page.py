"""Contextual Opportunities Streamlit page."""

from __future__ import annotations

from html import escape
from pathlib import Path

import streamlit as st

from agents.registry import AGENT_REGISTRY
from core.contextual_models import ContextualExecution, ContextualOpportunity, ContextualRun
from core.models import EvidenceType
from services.contextual.engine import ContextualEngine


def _badge(opp: ContextualOpportunity) -> str:
    if opp.verification_status == EvidenceType.VERIFIED_SOURCE:
        ver = '<span class="status-op">VERIFIED_SOURCE</span>'
    else:
        ver = '<span class="status-sim">SIMULATED_FIXTURE · Illustrative</span>'
    feas = opp.feasibility_status
    feas_cls = "status-op" if feas == "feasible" else "status-sim" if feas == "infeasible" else "status-plan"
    return f"{ver} · <span class='{feas_cls}'>{feas.upper()}</span>"


def _card(opp: ContextualOpportunity) -> str:
    fields = (
        "who",
        "what",
        "when",
        "where",
        "why",
        "how",
    )
    grid = "".join(
        f"<b>{f.upper()}</b><span>{escape(getattr(opp, f) or '—')}</span>" for f in fields
    )
    reason = ""
    if opp.infeasible_reason:
        reason = f"<div class='status-sim' style='margin-top:.4rem'>{escape(opp.infeasible_reason)}</div>"
    return f"""
    <div class="panel">
      <div class="opp-title" style="font-size:1.2rem;font-weight:600">{escape(opp.title)}</div>
      <div style="font-size:.9rem">{_badge(opp)} · Alignment {opp.alignment_score or '—'}/10</div>
      <div class="opp-grid" style="display:grid;grid-template-columns:80px 1fr;gap:.25rem .75rem;margin-top:.6rem">{grid}</div>
      <div class="muted" style="margin-top:.5rem">{escape(opp.mission_alignment_reason)}</div>
      <div class="muted">Incremental: ${opp.incremental_cost_usd:.2f} · {opp.incremental_time_minutes} min ·
        Prep {opp.prep_time_minutes} min</div>
      {reason}
    </div>
    """


def render_contextual() -> None:
    st.subheader("Contextual Opportunities")
    st.caption("Mission-aligned discovery for travel, layovers, and conferences.")
    st.markdown(
        '<p class="status-sim">Simulated scenarios use SIMULATED_FIXTURE data. '
        "Feasibility rejections and bundling math are deterministic. "
        "Nothing is sent, booked, or registered without your authorization.</p>",
        unsafe_allow_html=True,
    )

    if "ctx_run" not in st.session_state:
        st.session_state.ctx_run = None
    if "ctx_exec" not in st.session_state:
        st.session_state.ctx_exec = None

    scenario = st.radio(
        "Demo scenario",
        ["5h ORD layover", "Boston conference (+1 day)"],
        horizontal=True,
    )
    engine = ContextualEngine()

    if st.button("Run contextual analysis", type="primary"):
        with st.spinner("Contextual Scout + Bundling Analyst…"):
            if scenario.startswith("5h"):
                st.session_state.ctx_run = engine.run_layover_scenario()
            else:
                st.session_state.ctx_run = engine.run_conference_scenario()
            st.session_state.ctx_exec = None

    run: ContextualRun | None = st.session_state.ctx_run
    if run is None:
        st.session_state.ctx_run = engine.run_layover_scenario()
        run = st.session_state.ctx_run

    st.markdown(f"**Context:** {run.context.label}")
    st.markdown(
        f"Window: {run.context.window_start:%Y-%m-%d %H:%M} → "
        f"{run.context.window_end:%H:%M} · Energy: {run.context.energy_level} · "
        f"Location permission: {'yes' if run.context.location_permission_granted else 'no'}"
    )

    st.markdown("### Opportunities")
    for opp in run.opportunities:
        st.markdown(_card(opp), unsafe_allow_html=True)
        if opp.feasibility_status == "feasible" and st.button(
            f"Prepare execution draft — {opp.title[:40]}…",
            key=f"exec_{opp.opportunity_id}",
        ):
            st.session_state.ctx_exec = engine.execute(opp, run.context)

    if run.comparison:
        st.markdown("### Itinerary bundling (deterministic)")
        c = run.comparison
        st.write(c.net_benefit_summary)
        rows = []
        for bundle, tag in ((c.original, "Original"), (c.alternative, "Alternative")):
            for line in bundle.lines:
                rows.append(
                    {
                        "Itinerary": tag,
                        "Line": line.label,
                        "Cost USD": line.cost_usd,
                        "Minutes": line.duration_minutes,
                    }
                )
        st.dataframe(rows, use_container_width=True)
        st.markdown(
            f"**Incremental cost:** ${c.incremental_cost_usd:,.2f} · "
            f"**Incremental time:** {c.incremental_time_minutes} min"
        )
        st.write("**Alternative benefits:**", ", ".join(c.alternative.benefits))
        st.write("**Risks:**", ", ".join(c.alternative.risks))

    exec_pkg: ContextualExecution | None = st.session_state.ctx_exec
    if exec_pkg:
        st.markdown("### Execution (requires your authorization)")
        st.warning(exec_pkg.authorization_note)
        st.markdown(exec_pkg.itinerary_markdown)
        st.markdown("**Meeting request (draft — not sent)**")
        st.code(exec_pkg.meeting_request_draft)
        for opt in exec_pkg.registration_options:
            st.write(f"- {opt}")
        st.caption(
            f"Outreach: {exec_pkg.outreach_status} · Registration: {exec_pkg.registration_status} · "
            f"Booking: {exec_pkg.booking_status}"
        )
        if exec_pkg.ics_paths:
            p = Path(exec_pkg.ics_paths[0])
            if p.exists():
                st.download_button(
                    "Download ICS (draft calendar block)",
                    data=p.read_text(encoding="utf-8"),
                    file_name=p.name,
                    mime="text/calendar",
                )

    with st.expander("Privacy & permissions"):
        st.write(
            "Location: used only when you grant permission; layover mode avoids private GPS "
            "and limits distance without authorization."
        )
        st.write("No private-whereabouts fields are stored or inferred.")
        st.checkbox("Simulate location permission granted", value=run.context.location_permission_granted, disabled=True)

    with st.expander("Integrations"):
        st.markdown(
            "| Data source / consumer | Status |\n|---|---|\n"
            "| Life Mandate (Life Blueprint) | **Operational** |\n"
            "| Strategic Radar | **Operational** (module on `strategic-radar` branch) |\n"
            "| Side Quest Engine | **Planned** |\n"
            "| Focus Guardian | **Planned** |\n"
            "| Opportunity Portfolio Optimizer | **Planned** |"
        )

    with st.expander("Agent registry (Contextual)"):
        for entry in AGENT_REGISTRY:
            if "Contextual" in entry.module:
                st.write(f"**{entry.agent_id}** {entry.role} — {entry.status}. {entry.note}")