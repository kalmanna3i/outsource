"""Life Mandate editor and the fictional executive scenario."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import streamlit as st

from core.config import get_settings
from core.llm import LLMClient
from core.mandate import LifeMandate, fictional_executive_mandate
from database.db import (
    approve_mandate,
    list_mandate_revisions,
    load_approved_mandate,
    load_mandate,
    save_draft,
    update_priorities,
)
from services.office import recommend, reject_discovery, resume_office, run_office


def _lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def _fill(mandate: LifeMandate) -> LifeMandate:
    mandate.mission = st.text_area("Mission", mandate.mission, height=80, key="mandate_mission")
    mandate.vision = st.text_area("Vision", mandate.vision, height=68, key="mandate_vision")
    mandate.values = _lines(st.text_area("Values (one per line)", "\n".join(mandate.values), key="mandate_values"))
    mandate.principles = _lines(
        st.text_area("Principles (one per line)", "\n".join(mandate.principles), key="mandate_principles")
    )
    mandate.success_definition = st.text_area(
        "Success — your sentence, not the software's",
        mandate.success_definition,
        key="mandate_success",
    )
    mandate.legacy = st.text_area("Legacy", mandate.legacy, key="mandate_legacy")
    mandate.long_objectives = _lines(
        st.text_area("Long objectives (one per line)", "\n".join(mandate.long_objectives), key="mandate_long")
    )
    mandate.short_objectives = _lines(
        st.text_area("Short objectives (one per line)", "\n".join(mandate.short_objectives), key="mandate_short")
    )
    mandate.nonnegotiables = _lines(
        st.text_area("Nonnegotiables (one per line)", "\n".join(mandate.nonnegotiables), key="mandate_nonnegotiables")
    )
    mandate.priorities = _lines(
        st.text_area(
            "Priorities, highest first (one per line)",
            "\n".join(mandate.priorities),
            key="mandate_priorities",
        )
    )
    mandate.risk_posture = st.text_input("Risk posture", mandate.risk_posture, key="mandate_risk")
    mandate.lifestyle = st.text_area("Lifestyle", mandate.lifestyle, key="mandate_lifestyle")
    cols = st.columns(2)
    mandate.time_budget_hours_week = cols[0].number_input(
        "Time budget (hours / week)",
        min_value=0.0,
        value=float(mandate.time_budget_hours_week),
        key="mandate_time",
    )
    mandate.money_budget_usd_month = cols[1].number_input(
        "Money budget (USD / month)",
        min_value=0.0,
        value=float(mandate.money_budget_usd_month),
        key="mandate_money",
    )
    mandate.energy_note = st.text_area("Energy", mandate.energy_note, key="mandate_energy")
    mandate.recovery_note = st.text_area("Recovery", mandate.recovery_note, key="mandate_recovery")
    mandate.philosophy = st.text_input("Philosophy", mandate.philosophy, key="mandate_philosophy")
    mandate.promise = st.text_input("Promise", mandate.promise, key="mandate_promise")
    return mandate


def _show_recommendation(title: str, mandate: LifeMandate | None) -> None:
    st.markdown(f"#### {title}")
    if mandate is None:
        st.caption("No approved mandate yet. Recommendations will not cite a draft as if you had approved it.")
        return
    rec = recommend(mandate)
    st.write(f"**Discretionary pick:** {rec.chosen_label} ({rec.chosen_id})")
    st.write(f"Strategic value {rec.strategic_value}. Approved: {rec.used_approved}.")
    if rec.citations:
        st.write("Cites approved items:")
        for line in rec.citations:
            st.write(f"- {line}")
    else:
        st.caption("No approved citations on this revision.")
    for conflict in rec.conflicts:
        st.warning(conflict)
    st.caption(f"Mission left unchanged: {mandate.mission}")


def render_mandate() -> None:
    st.subheader("Life Mandate")
    st.caption(
        "The art of building an intentional life. Every dimension of you. One intentional life. "
        "Success stays in your words. Priorities change the discretionary pick. "
        "Nothing here sends email or spends money."
    )
    current = load_mandate()
    edited = _fill(current.model_copy(deep=True))

    preview = edited.model_copy(deep=True)
    preview.status = current.status
    _show_recommendation("Preview from the form (not saved until you click)", preview)

    c1, c2, c3 = st.columns(3)
    if c1.button("Save draft"):
        saved = save_draft(edited)
        st.success(f"Draft revision {saved.revision} saved. The approved mandate, if any, was not replaced.")
    if c2.button("Approve mandate"):
        approved = approve_mandate(edited, "user")
        st.success(f"Approved revision {approved.revision}. Recommendations can cite it.")
    if c3.button("Update priorities"):
        try:
            updated = update_priorities(edited.priorities, "user")
            st.success(
                "Priorities updated on a new approved revision. "
                f"Pick: {recommend(updated).chosen_label}."
            )
        except ValueError as exc:
            st.error(str(exc))

    if st.button("Load fictional executive draft"):
        save_draft(fictional_executive_mandate())
        st.success("Loaded the fictional executive as a draft. Approve it before treating it as the mandate.")
        st.rerun()

    approved = load_approved_mandate()
    _show_recommendation("Recommendation from the latest approved revision", approved)

    with st.expander("Revisions"):
        for revision in list_mandate_revisions():
            st.write(
                f"r{revision.revision} · {revision.status.value} · priorities: "
                + ", ".join(revision.priorities)
            )

    st.markdown("### Executive scenario")
    st.caption(
        "Fictional MBA executive at an infrastructure company. Discovery uses a labeled dataset. "
        "Scores are deterministic. S01, D01, and Q01 are the only model calls."
    )
    if st.button("Run discovery and recommendation"):
        settings = get_settings()
        base = approved or edited
        with st.spinner("Running S01, D01, and Q01…"):
            package = run_office(
                LLMClient(settings),
                base,
                now=datetime.now(),
                ics_dir=settings.data_dir / "ics",
            )
        st.session_state.office_run = package
        st.success(f"{package['run_id']} → {package['status']} · agents {', '.join(package['agents_invoked'])}")

    package = st.session_state.get("office_run")
    if not package:
        return
    st.write(
        f"Dataset **{package['label_dataset']}** · scores **{package['label_scores']}** · "
        f"model path **{package['label_model']}** · status `{package['status']}`"
    )
    st.write(package["persona"])
    if package.get("discovery_accepted"):
        st.write("Discovery note is still accepted.")
    else:
        st.warning("You rejected the discovery note. It is not treated as accepted.")
    if st.button("Reject discovery note"):
        st.session_state.office_run = reject_discovery(package)
        st.rerun()

    strength = package.get("strength_gap") or {}
    st.markdown("#### Strength and gap")
    for key in ("strengths", "gaps", "opportunities", "threats"):
        for row in strength.get(key) or []:
            if isinstance(row, dict):
                st.write(f"- {key[:-1]}: {row.get('note')} (evidence {row.get('evidence_id')})")
    det = package["deterministic_recommendation"]
    st.write(f"Deterministic pick: **{det['chosen_label']}**. Model id: `{package['model_choice']['chosen_id']}`.")
    st.markdown("#### Scores")
    st.dataframe(package["scores"], use_container_width=True, hide_index=True)
    st.markdown("#### Stacked philanthropy and matrix")
    st.write(package["philanthropy"]["opportunity"])
    st.dataframe(package["matrix"], use_container_width=True, hide_index=True)
    st.markdown("#### Dinner spend across periods")
    st.caption(package["dinner"]["assumption"])
    st.dataframe(package["dinner"]["periods"], use_container_width=True, hide_index=True)
    st.markdown("#### Portfolio")
    st.write("Selected:", ", ".join(package["portfolio"]["selected_ids"]))
    st.write("Left unscheduled (hours):", package["portfolio"]["hours_left_unscheduled"])
    st.markdown("#### Make or buy")
    mob = package["make_or_buy"]
    st.write(mob["task"])
    st.write(f"Make: ${mob['make']['cash_usd']} cash, {mob['make']['hours']} h. {mob['make']['opportunity_cost']}")
    st.write(f"Buy: ${mob['buy']['cash_usd']} cash, {mob['buy']['hours']} h. {mob['buy']['opportunity_cost']}")
    st.caption(mob["suggestion"])
    st.markdown("#### Itinerary")
    for row in package["itinerary"]:
        st.write(f"- {row['when']}: {row['title']}")
    st.markdown("#### Outreach draft")
    st.write(f"`{package['outreach']['status']}` · sent={package['outreach_sent']}")
    st.text(package["outreach"]["body"])
    st.markdown("#### Human brief")
    st.write(package["human_brief"])
    if package.get("ics_path") and Path(package["ics_path"]).exists():
        st.download_button(
            "Download coursework ICS",
            data=Path(package["ics_path"]).read_text(encoding="utf-8"),
            file_name=Path(package["ics_path"]).name,
            mime="text/calendar",
        )
    if package["status"] == "WAITING_RESULT":
        result = st.text_area("Your result (required to resume)", key="office_result")
        if st.button("Submit office result"):
            if not result.strip():
                st.error("Enter a result first. The scenario does not complete itself.")
            else:
                st.session_state.office_run = resume_office(package, result)
                st.rerun()
    elif package.get("user_result"):
        st.success(f"Recorded your result. No email sent. No purchase. Status {package['status']}.")
    st.markdown("#### Quality")
    st.write(package.get("quality_agent"))
    for finding in package.get("quality_checks") or []:
        st.write(f"- {finding['severity']}: {finding['note']}")
