"""Homepage visuals: mission, universe, one decision question, saved check-in, charts."""

from __future__ import annotations

import html
from datetime import datetime, timezone

import streamlit as st

from core.config import get_settings
from core.llm import LLMClient
from database.db import (
    load_aspirations,
    load_assessments,
    load_daily_checkin,
    save_assessments,
    save_daily_checkin,
)
from services.radar_graph import figure as network_figure
from services.universe import (
    active_dimensions,
    ask_decision,
    assessed_scores,
    capability_gaps,
    daily_plan_text,
)
from ui.living_universe import render_living_universe
from ui.strategic_charts import (
    capability_gap_chart,
    life_radar,
    opportunity_bubbles,
    opportunity_heatmap,
    spending_comparison,
)


def _today() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def render_today(mandate, blueprint, workflow) -> None:
    st.markdown('<p class="life-headline">Your life, in motion</p>', unsafe_allow_html=True)
    _question(mandate, workflow)
    mission = (mandate.mission or "").strip() or "No mission is saved yet."
    st.markdown(f'<p class="life-mission">{html.escape(mission)}</p>', unsafe_allow_html=True)
    assessments = load_assessments()
    _stored_cards(mandate, blueprint, assessments)
    render_living_universe(mandate, blueprint, assessments)
    _checkin()
    _assessments(mandate, blueprint, assessments)
    _charts(mandate, blueprint, assessments)


def _stored_cards(mandate, blueprint, assessments: dict[str, int]) -> None:
    """Compact cards for stored records only. No sparklines and no filled-in series."""
    names = {item["key"]: item["name"] for item in active_dimensions(mandate, blueprint)}
    cards = [
        ("Saved mandate", f"{mandate.time_budget_hours_week:g} h/wk", "Time budget"),
        ("Saved mandate", f"${mandate.money_budget_usd_month:g}/mo", "Money budget"),
    ]
    checkin = load_daily_checkin(_today())
    if checkin:
        cards.append(("Today's check-in", f"{int(checkin['energy'])}/5", "Energy"))
    for key, score in assessments.items():
        cards.append(("Saved assessment", f"{int(score)}/10", names.get(key, key)))
    for key, score in load_aspirations().items():
        cards.append(("Aspiration", f"{int(score)}/10", names.get(key, key)))
    bits = []
    for source, value, label in cards:
        bits.append(
            "<div class='metric-card'>"
            f"<div class='k'>{html.escape(source)}</div>"
            f"<div class='v'>{html.escape(value)}</div>"
            f"<div class='s'>{html.escape(label)}</div>"
            "</div>"
        )
    st.markdown(f"<div class='metric-row'>{''.join(bits)}</div>", unsafe_allow_html=True)


def _question(mandate, workflow) -> None:
    question = st.text_input("What would you like to explore today?", key="universe_question")
    asked = st.session_state.setdefault("universe_answers", {})
    if st.button("Ask the office"):
        text = question.strip()
        if not text:
            st.warning("Write a question first.")
        elif text not in asked:
            sequence = None
            if workflow is not None and workflow.decision_plan is not None:
                sequence = list(workflow.decision_plan.recommended_sequence)
            result, record = ask_decision(
                text,
                mandate,
                client=LLMClient(get_settings()),
                workflow_sequence=sequence,
            )
            asked[text] = {"result": result, "call_id": record.call_id, "mode": record.mode}
        st.session_state["universe_shown"] = question.strip()
    shown = st.session_state.get("universe_shown")
    if shown and shown in asked:
        packet = asked[shown]
        answer = packet["result"].get("answer") or packet["result"].get("summary") or ""
        st.write(answer)


def _checkin() -> None:
    st.markdown("#### Today's check-in")
    saved = load_daily_checkin(_today())
    feeling = st.text_input("How are you feeling?", value=(saved or {}).get("feeling", ""))
    energy = st.number_input(
        "Energy (1–5)",
        min_value=1,
        max_value=5,
        value=int((saved or {}).get("energy", 3)),
        step=1,
    )
    must_do = st.text_input("Must-do today", value=(saved or {}).get("must_do", ""))
    responsibilities = st.text_input(
        "Responsibilities", value=(saved or {}).get("responsibilities", "")
    )
    surprises = st.text_area("Surprises", value=(saved or {}).get("surprises", ""), height=68)
    discretionary = st.number_input(
        "Discretionary hours",
        min_value=0.0,
        max_value=24.0,
        value=float((saved or {}).get("discretionary_hours", 0.0)),
        step=0.5,
    )
    if st.button("Save today's check-in"):
        payload = {
            "feeling": feeling.strip(),
            "energy": int(energy),
            "must_do": must_do.strip(),
            "responsibilities": responsibilities.strip(),
            "surprises": surprises.strip(),
            "discretionary_hours": float(discretionary),
        }
        save_daily_checkin(_today(), payload)
        saved = payload
        st.success("Check-in saved.")
    st.markdown(daily_plan_text(saved if saved else load_daily_checkin(_today())))


def _assessments(mandate, blueprint, assessments: dict[str, int]) -> None:
    st.markdown("#### Dimension assessments")
    st.caption("0–10, saved by you. The radar and the gaps read only what is saved.")
    dimensions = active_dimensions(mandate, blueprint)
    draft: dict[str, int] = {}
    for dimension in dimensions:
        current = assessments.get(dimension["key"], 0)
        draft[dimension["key"]] = int(
            st.slider(
                dimension["name"],
                min_value=0,
                max_value=10,
                value=int(current),
                key=f"assess_{dimension['key']}",
            )
        )
    if st.button("Save assessments"):
        save_assessments(draft)
        st.success("Assessments saved.")
        st.rerun()


def _charts(mandate, blueprint, assessments: dict[str, int]) -> None:
    dimensions = active_dimensions(mandate, blueprint)
    if len(assessed_scores(dimensions, assessments)) >= 3:
        st.markdown("#### Life radar")
        st.plotly_chart(life_radar(dimensions, assessments), use_container_width=True)
    gaps = capability_gaps(dimensions, assessments)
    if gaps:
        st.markdown("#### Capability gaps")
        st.plotly_chart(capability_gap_chart(dimensions, assessments), use_container_width=True)
        st.caption("Gap = stored goal importance minus your saved assessment. Unsaved dimensions are omitted.")

    st.markdown("#### Opportunity heatmap")
    heat, heat_note = opportunity_heatmap(mandate)
    st.plotly_chart(heat, use_container_width=True)
    st.caption(heat_note)

    st.markdown("#### Strategic value, cost, and time")
    bubbles, bubble_note = opportunity_bubbles(mandate)
    st.plotly_chart(bubbles, use_container_width=True)
    st.caption(bubble_note)

    st.markdown("#### Intersection graph")
    st.caption(
        "Reused from Strategic Radar. Solid edges are verified citations. "
        "Dashed edges are hypothetical and are not relationships."
    )
    st.plotly_chart(network_figure(), use_container_width=True)

    st.markdown("#### Spending comparison")
    st.caption(
        "These fields recalculate the labeled catalog. They do not change the saved mandate "
        "and they do not spend money."
    )
    hours = st.number_input(
        "Comparison time budget (hours / week)",
        min_value=0.0,
        value=float(mandate.time_budget_hours_week),
        step=1.0,
        key="compare_hours",
    )
    money = st.number_input(
        "Comparison money budget (USD / month)",
        min_value=0.0,
        value=float(mandate.money_budget_usd_month),
        step=50.0,
        key="compare_money",
    )
    spent, note = spending_comparison(mandate, hours, money)
    st.plotly_chart(spent, use_container_width=True)
    st.caption(note)
