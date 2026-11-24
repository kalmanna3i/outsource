"""Plotly charts for the homepage. Transparent paper, ink on ivory, fixtures labeled."""

from __future__ import annotations

from typing import Any

import plotly.graph_objects as go

from core.mandate import LifeMandate
from services.universe import (
    assessed_scores,
    bubble_rows,
    capability_gaps,
    heatmap_matrix,
    spending_snapshot,
)

NAVY = "#142438"
IVORY = "#F8F7F3"
SAGE = "#496E65"
CHAMPAGNE = "#B5A083"
INK = "#1A2430"


def _layout(fig: go.Figure, height: int = 380) -> go.Figure:
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=INK, family="Source Sans 3, sans-serif"),
        margin=dict(l=24, r=16, t=36, b=24),
        height=height,
        legend=dict(orientation="h", y=-0.2),
    )
    return fig


def _empty(message: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        showarrow=False,
        font=dict(color=INK, size=14),
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return _layout(fig, height=220)


def life_radar(dimensions: list[dict[str, Any]], assessments: dict[str, int]) -> go.Figure:
    scored = assessed_scores(dimensions, assessments)
    if len(scored) < 3:
        return _empty("Save at least three 0–10 assessments to draw the life radar.")
    names = [name for name, _score in scored]
    values = [score for _name, score in scored]
    fig = go.Figure(
        go.Scatterpolar(
            r=values + [values[0]],
            theta=names + [names[0]],
            fill="toself",
            name="Saved assessment",
            line=dict(color=SAGE, width=2),
            fillcolor="rgba(73,110,101,0.35)",
        )
    )
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(range=[0, 10], color=NAVY, gridcolor="#D9D2C5", dtick=2),
            angularaxis=dict(color=NAVY),
        ),
        showlegend=False,
    )
    return _layout(fig)


def capability_gap_chart(dimensions: list[dict[str, Any]], assessments: dict[str, int]) -> go.Figure:
    rows = capability_gaps(dimensions, assessments)
    if not rows:
        return _empty(
            "No capability gap yet. A gap needs both a saved 0–10 assessment and a stored goal importance."
        )
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name="Saved assessment",
            x=[row["name"] for row in rows],
            y=[row["assessment"] for row in rows],
            marker_color=SAGE,
        )
    )
    fig.add_trace(
        go.Bar(
            name="Stored goal importance",
            x=[row["name"] for row in rows],
            y=[row["importance"] for row in rows],
            marker_color=CHAMPAGNE,
        )
    )
    fig.update_layout(barmode="group", yaxis=dict(range=[0, 10], title="0–10", gridcolor="#E6E0D6"))
    return _layout(fig)


def opportunity_heatmap(mandate: LifeMandate) -> tuple[go.Figure, str]:
    matrix = heatmap_matrix(mandate)
    fig = go.Figure(
        go.Heatmap(
            z=matrix["z"],
            x=matrix["themes"],
            y=matrix["labels"],
            colorscale=[[0, IVORY], [0.45, SAGE], [1, NAVY]],
            colorbar=dict(title="score"),
            hovertemplate="%{y}<br>%{x}: %{z}<extra></extra>",
        )
    )
    fig.update_yaxes(autorange="reversed")
    return _layout(fig, height=460), matrix["label"]


def opportunity_bubbles(mandate: LifeMandate) -> tuple[go.Figure, str]:
    rows = bubble_rows(mandate)
    fig = go.Figure()
    for selected, name, color in (
        (True, "In the current portfolio", SAGE),
        (False, "Not selected", CHAMPAGNE),
    ):
        group = [row for row in rows if row["selected"] is selected]
        fig.add_trace(
            go.Scatter(
                x=[row["cash_usd"] for row in group],
                y=[row["strategic_value"] for row in group],
                mode="markers",
                name=name,
                text=[row["label"] for row in group],
                hovertemplate=(
                    "%{text}<br>cash $%{x}<br>strategic value %{y}"
                    "<br>hours %{customdata[0]}<br>objectives %{customdata[1]}<extra></extra>"
                ),
                customdata=[[row["hours"], row["objectives"]] for row in group],
                marker=dict(
                    color=color,
                    size=[12 + row["hours"] * 4 for row in group],
                    line=dict(color=NAVY, width=1),
                    sizemode="diameter",
                ),
            )
        )
    fig.update_xaxes(title="Weekly cash on the labeled catalog ($)", gridcolor="#E6E0D6")
    fig.update_yaxes(title="Strategic value", gridcolor="#E6E0D6")
    return _layout(fig, height=420), "Labeled catalog fixtures. Marker size is hours. Not a market quote."


def spending_comparison(mandate: LifeMandate, hours: float, money: float) -> tuple[go.Figure, str]:
    snap = spending_snapshot(mandate, hours, money)
    fig = go.Figure(
        go.Bar(
            x=[item["label"] for item in snap["selected"]],
            y=[item["cash_usd"] for item in snap["selected"]],
            marker_color=[NAVY if item["mandatory"] else SAGE for item in snap["selected"]],
            name="Weekly cash",
        )
    )
    fig.update_yaxes(title="Weekly cash ($)", gridcolor="#E6E0D6")
    note = (
        f"{snap['label']} Weekly envelope ${snap['weekly_cash_envelope']} "
        f"leaves ${snap['weekly_cash_left']}. Unscheduled hours: {snap['hours_left_unscheduled']}. "
        f"Make-or-buy constraint: {snap['scarce_constraint']} "
        f"(make {snap['make_hours']}h, buy ${snap['buy_cash']} plus {snap['buy_hours']}h). "
        "Changing the budget fields above recalculates this. It does not spend money."
    )
    return _layout(fig, height=380), note
