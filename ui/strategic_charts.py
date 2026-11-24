"""Plotly charts for the dark homepage. Fixtures stay labeled. Missing scores stay missing."""

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

NAVY = "#8D98A8"
IVORY = "#11161F"
SAGE = "#80B5A4"
CHAMPAGNE = "#B5A083"
INK = "#E9EDF2"
GRID = "rgba(255,255,255,0.07)"


def _layout(fig: go.Figure, height: int = 300) -> go.Figure:
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=INK, family="Inter, system-ui, sans-serif", size=11),
        margin=dict(l=16, r=10, t=20, b=16),
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


def dimension_levels(current: int | None, aspiration: int | None) -> go.Figure:
    """Current self-assessment and saved aspiration. No bar is drawn for a missing score."""
    if current is None and aspiration is None:
        return _empty("Nothing is saved for this dimension yet.")
    names: list[str] = []
    values: list[int] = []
    colors: list[str] = []
    if current is not None:
        names.append("Personal history")
        values.append(current)
        colors.append(SAGE)
    if aspiration is not None:
        names.append("Aspiration")
        values.append(aspiration)
        colors.append(CHAMPAGNE)
    fig = go.Figure(go.Bar(x=names, y=values, marker_color=colors, name="Saved"))
    fig.update_yaxes(range=[0, 10], title="0–10", gridcolor=GRID)
    return _layout(fig, height=320)


def history_line(points: list[dict[str, Any]]) -> go.Figure:
    """One point per save. Dates that were never saved are not added."""
    if not points:
        return _empty("No saved history for this dimension.")
    fig = go.Figure(
        go.Scatter(
            x=[point["recorded_at"] for point in points],
            y=[point["score"] for point in points],
            mode="lines+markers" if len(points) > 1 else "markers",
            name="Personal history",
            line=dict(color=SAGE, width=1),
            marker=dict(color=NAVY, size=4),
        )
    )
    fig.update_yaxes(range=[0, 10], title="Saved score", gridcolor=GRID)
    fig.update_xaxes(type="category", title="Saved at")
    return _layout(fig, height=320)


def portfolio_radar(
    dimensions: list[dict[str, Any]],
    assessments: dict[str, int],
    aspirations: dict[str, int],
) -> go.Figure:
    """Saved self-assessments, plus aspiration only where the user stored a target."""
    from services.benchmark import saved_radar_scores

    current = saved_radar_scores(dimensions, assessments)
    if len(current) < 3:
        return _empty("Save at least three self-assessments to draw the portfolio radar.")
    names = [name for name, _score in current]
    values = [score for _name, score in current]
    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=values + [values[0]],
            theta=names + [names[0]],
            fill="toself",
            name="Personal history",
            line=dict(color=SAGE, width=1),
            fillcolor="rgba(131,183,161,0.28)",
        )
    )
    by_name = {dimension["name"]: dimension["key"] for dimension in dimensions}
    aspiration_values = []
    for name in names:
        key = by_name.get(name)
        if key is None or key not in aspirations:
            aspiration_values = []
            break
        aspiration_values.append(int(aspirations[key]))
    if aspiration_values:
        fig.add_trace(
            go.Scatterpolar(
                r=aspiration_values + [aspiration_values[0]],
                theta=names + [names[0]],
                name="Aspiration",
                line=dict(color=CHAMPAGNE, width=1),
            )
        )
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(range=[0, 10], color=NAVY, gridcolor=GRID, dtick=2),
            angularaxis=dict(color=NAVY),
        ),
    )
    return _layout(fig)


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
            line=dict(color=SAGE, width=1),
            fillcolor="rgba(131,183,161,0.28)",
        )
    )
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(range=[0, 10], color=NAVY, gridcolor=GRID, dtick=2),
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
    fig.update_layout(barmode="group", yaxis=dict(range=[0, 10], title="0–10", gridcolor=GRID))
    return _layout(fig)


def opportunity_heatmap(mandate: LifeMandate) -> tuple[go.Figure, str]:
    matrix = heatmap_matrix(mandate)
    fig = go.Figure(
        go.Heatmap(
            z=matrix["z"],
            x=matrix["themes"],
            y=matrix["labels"],
            colorscale=[[0, "#101923"], [0.5, SAGE], [1, "#E9EDF2"]],
            colorbar=dict(title="score"),
            hovertemplate="%{y}<br>%{x}: %{z}<extra></extra>",
        )
    )
    fig.update_yaxes(autorange="reversed")
    return _layout(fig, height=340), matrix["label"]


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
    fig.update_xaxes(title="Weekly cash on the labeled catalog ($)", gridcolor=GRID)
    fig.update_yaxes(title="Strategic value", gridcolor=GRID)
    return _layout(fig, height=300), "Labeled catalog fixtures. Marker size is hours. Not a market quote."


def spending_comparison(mandate: LifeMandate, hours: float, money: float) -> tuple[go.Figure, str]:
    snap = spending_snapshot(mandate, hours, money)
    fig = go.Figure(
        go.Bar(
            x=[item["label"] for item in snap["selected"]],
            y=[item["cash_usd"] for item in snap["selected"]],
            marker_color=[CHAMPAGNE if item["mandatory"] else SAGE for item in snap["selected"]],
            name="Weekly cash",
        )
    )
    fig.update_yaxes(title="Weekly cash ($)", gridcolor=GRID)
    note = (
        f"{snap['label']} Weekly envelope ${snap['weekly_cash_envelope']} "
        f"leaves ${snap['weekly_cash_left']}. Unscheduled hours: {snap['hours_left_unscheduled']}. "
        f"Make-or-buy constraint: {snap['scarce_constraint']} "
        f"(make {snap['make_hours']}h, buy ${snap['buy_cash']} plus {snap['buy_hours']}h). "
        "Changing the budget fields above recalculates this. It does not spend money."
    )
    return _layout(fig, height=280), note
