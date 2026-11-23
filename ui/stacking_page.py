"""Opportunity Stacking UI page."""

from __future__ import annotations

import streamlit as st

from agents.registry import agent_catalog
from core.config import get_settings
from core.llm import LLMClient
from core.models import MatrixColumn
from services.stacking.chief_of_staff import recommend_bundle
from services.stacking.fixtures import ILLUSTRATIVE_OPPORTUNITIES, SAMPLE_LIFE_MANDATE
from services.stacking.hours import canonical_efficiency_example, eight_hour_days_equivalent
from services.stacking.scoring import compute_stacking_score
from services.stacking.strategists import run_life_strategists

_COLUMN_LABELS = {
    MatrixColumn.GIVING_BACK: "Giving back",
    MatrixColumn.CAREER: "Career",
    MatrixColumn.LEARNING: "Learning",
    MatrixColumn.BUSINESS: "Business",
    MatrixColumn.NETWORK: "Network",
}


def page_opportunity_stacking() -> None:
    st.subheader("Opportunity Stacking")
    st.markdown(
        '<p class="status-sim">Simulated integration — comparison matrix uses '
        "SIMULATED_FIXTURE / Illustrative rows only; no researched organizations.</p>",
        unsafe_allow_html=True,
    )
    st.caption(
        "Brand line: Don't live fourteen separate lives. Build one life in which "
        "all fourteen dimensions can reinforce one another."
    )

    st.markdown("### Comparison matrix (illustrative)")
    rows = []
    for opp in ILLUSTRATIVE_OPPORTUNITIES:
        row: dict[str, str] = {"Opportunity (Illustrative)": opp.label, "Hrs/mo": opp.monthly_hours}
        for cell in opp.matrix:
            row[_COLUMN_LABELS[cell.column]] = (
                f"{cell.level.value} ({cell.benefit_kind.value})"
            )
        score = compute_stacking_score(opp)
        row["Stacking composite"] = score.composite
        rows.append(row)
    st.dataframe(rows, use_container_width=True)

    st.markdown("### Efficiency — separate vs bundled (deterministic)")
    example = canonical_efficiency_example()
    days = eight_hour_days_equivalent(example.annual_hours_recovered)
    st.markdown(
        f"""
        <div class="panel">
          <div class="muted">Spec example (comparable benefits assumed)</div>
          <div class="kpi">{example.monthly_hours_saved:.0f} hrs/mo recovered ·
            {example.annual_hours_recovered:.0f} hrs/yr · ~{days:.0f} eight-hour days</div>
          <p class="muted">Separate: {' + '.join(str(int(h)) for h in example.separate_commitment_hours)}
            = {sum(example.separate_commitment_hours):.0f} hrs/mo · Bundled: {example.bundled_hours:.0f} hrs/mo</p>
          <p><strong>Assumption:</strong> {example.comparable_benefits_assumption}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Reciprocal value (what you give the organization)")
    for opp in ILLUSTRATIVE_OPPORTUNITIES:
        if opp.reciprocal_value:
            st.write(f"**{opp.label}** — {opp.reciprocal_value}")

    phi = next(
        (o.philanthropy for o in ILLUSTRATIVE_OPPORTUNITIES if o.philanthropy),
        None,
    )
    if phi:
        st.markdown("### Philanthropic research fields (fixture)")
        st.json(
            {
                "mission": phi.mission,
                "community_impact": phi.community_impact,
                "governance": phi.governance,
                "time": phi.time_commitment_hours_month,
                "money": phi.financial_contribution,
                "skills_given": phi.skills_given,
                "skills_gained": phi.skills_gained,
                "application_path": phi.application_path,
                "conflicts": phi.conflicts_of_interest,
                "reciprocal_value_note": phi.reciprocal_value_note,
                "evidence": "SIMULATED_FIXTURE",
            }
        )

    st.markdown("### Chief of Staff recommendation")
    rec = recommend_bundle(ILLUSTRATIVE_OPPORTUNITIES, SAMPLE_LIFE_MANDATE)
    st.markdown(f"**Feasible bundle:** {rec.chosen_bundle_label}")
    for line in rec.rationale:
        st.write(f"- {line}")
    st.caption(f"Mandate fit: {rec.mandate_fit_notes}")
    st.caption("Compared against separate activities: " + "; ".join(rec.separate_activities_rejected))

    st.markdown("### Life Dimension strategists")
    life_agents = [a for a in agent_catalog() if a["agent_id"].startswith("L")]
    st.dataframe(life_agents, use_container_width=True, hide_index=True)

    settings = get_settings()
    if st.button("Run six strategists (demo fixtures)"):
        with st.spinner("Running L01–L06…"):
            _, records = run_life_strategists(LLMClient(settings))
        st.success(f"{len(records)} agent calls — mode={settings.effective_mode}")
        for r in records:
            st.caption(f"{r.agent_id} {r.role}: {r.summary}")
    elif settings.effective_mode == "live":
        st.info(
            "Live mode: each strategist would use one model call (same wiring as Priority 0). "
            "Use the button above to run in current effective mode."
        )