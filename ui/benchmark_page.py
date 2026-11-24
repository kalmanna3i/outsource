"""One life-dimension screen. Scores appear only after they are saved."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st

from core.config import get_settings
from core.llm import LLMClient
from core.mandate import approved_citations
from database.db import (
    load_aspirations,
    load_assessment_history,
    load_assessments,
    load_blueprint,
    load_mandate,
    save_aspirations,
    save_assessments,
)
from services.benchmark import dimension_snapshot, population_benchmark
from services.universe import active_dimensions, ask_decision
from ui.strategic_charts import dimension_levels, history_line, portfolio_radar


def _saved_label(raw: str | None) -> str:
    if not raw:
        return "not stored"
    stamp = datetime.fromisoformat(raw)
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=ZoneInfo("UTC"))
    local = stamp.astimezone(ZoneInfo("America/New_York"))
    hour = local.strftime("%I").lstrip("0")
    return local.strftime(f"%b %-d, %Y, {hour}:%M %p ET")


def render_benchmark() -> None:
    mandate = load_mandate()
    dimensions = active_dimensions(mandate, load_blueprint())
    assessments = load_assessments()
    aspirations = load_aspirations()
    history = load_assessment_history()
    st.subheader("Life dimension")
    if not dimensions:
        st.info("No active life dimensions are stored yet.")
        return

    names = [item["name"] for item in dimensions]
    picked = st.selectbox("Dimension", names, key="benchmark_dimension")
    dimension = next(item for item in dimensions if item["name"] == picked)
    snap = dimension_snapshot(dimension["key"], assessments, aspirations, history)

    st.markdown("#### Personal history")
    st.plotly_chart(
        dimension_levels(snap["current"], snap["aspiration"]),
        use_container_width=True,
    )
    if snap["current"] is None and snap["aspiration"] is None:
        st.caption("Nothing is saved for this dimension yet.")
    else:
        gap = "not saved" if snap["gap"] is None else str(snap["gap"])
        saved_on = _saved_label(snap["last_saved"])
        st.caption(
            f"Current {snap['current'] if snap['current'] is not None else 'not saved'}. "
            f"Aspiration {snap['aspiration'] if snap['aspiration'] is not None else 'not saved'}. "
            f"Gap (aspiration minus current) {gap}. Last saved {saved_on}."
        )
    st.plotly_chart(history_line(snap["history"]), use_container_width=True)
    st.caption("The line uses saved assessments only. Days between saves are not filled in.")

    _save_controls(dimension["key"], assessments, aspirations, snap)

    st.markdown("#### Population")
    fact = population_benchmark()
    st.write(fact["statement"])
    st.caption(
        f"{fact['source']}, {fact['year']}, {fact['geography']}. {fact['method']} {fact['url']}"
    )

    st.markdown("#### Life portfolio")
    st.plotly_chart(portfolio_radar(dimensions, assessments, aspirations), use_container_width=True)
    st.caption("Personal history is the saved 0–10 score. Aspiration is shown only where you saved a target.")

    _recommend(mandate, dimension["name"], snap)


def _save_controls(key: str, assessments: dict[str, int], aspirations: dict[str, int], snap: dict) -> None:
    current_default = int(snap["current"]) if snap["current"] is not None else 5
    current = st.number_input(
        "Current self-assessment (0–10)",
        min_value=0,
        max_value=10,
        value=current_default,
        step=1,
        key=f"bench_current_{key}",
    )
    if st.button("Save current assessment"):
        updated = dict(assessments)
        updated[key] = int(current)
        save_assessments(updated)
        st.success("Current assessment saved.")
        st.rerun()

    target_default = int(snap["aspiration"]) if snap["aspiration"] is not None else 5
    target = st.number_input(
        "Aspiration target (0–10)",
        min_value=0,
        max_value=10,
        value=target_default,
        step=1,
        key=f"bench_target_{key}",
    )
    if st.button("Save aspiration"):
        updated = dict(aspirations)
        updated[key] = int(target)
        save_aspirations(updated)
        st.success("Aspiration saved. It is not a population percentile.")
        st.rerun()


def _recommend(mandate, dimension_name: str, snap: dict) -> None:
    st.markdown("#### Recommendation")
    st.caption("One call when you click. Demo mode returns a labeled fixture and cites the saved mandate.")
    citations = approved_citations(mandate)
    cite_text = (
        "; ".join(citations)
        if citations
        else f"Draft mission, not approved: {mandate.mission}"
    )
    question = (
        f"For {dimension_name}, current is "
        f"{'unsaved' if snap['current'] is None else snap['current']} and aspiration is "
        f"{'unsaved' if snap['aspiration'] is None else snap['aspiration']}. "
        f"What should I protect? Cite only this mandate: {cite_text}"
    )
    asked = st.session_state.setdefault("benchmark_answers", {})
    if st.button("Recommend from the saved mandate"):
        if question not in asked:
            result, record = ask_decision(question, mandate, client=LLMClient(get_settings()))
            asked[question] = {"result": result, "mode": record.mode, "call_id": record.call_id}
        st.session_state["benchmark_shown"] = question
    shown = st.session_state.get("benchmark_shown")
    if shown and shown in asked:
        packet = asked[shown]
        st.write(packet["result"].get("answer") or "")
        if packet["mode"] == "demo":
            st.caption(
                f"Demo fixture, not a live model call. Call {packet['call_id']}. "
                "Personal history, aspiration, and the population figure stay separate."
            )
