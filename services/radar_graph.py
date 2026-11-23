"""Strategic network graph (Plotly). VERIFIED edges and HYPOTHETICAL paths are styled apart."""

from __future__ import annotations

import math

import plotly.graph_objects as go

from core.radar_models import NetworkEdge, NetworkGraph, NetworkNode
from services.radar_fixtures import network_fixture

EDGE_STYLE = {
    "VERIFIED": {"color": "#1F5C45", "width": 3.5, "dash": "solid",
                 "label": "VERIFIED relationship (cited public source)"},
    "USER_PROVIDED": {"color": "#0B1F33", "width": 2.0, "dash": "solid",
                      "label": "User-provided (your own records)"},
    "HYPOTHETICAL": {"color": "#C07A2C", "width": 2.0, "dash": "dash",
                     "label": "HYPOTHETICAL introduction path (unverified)"},
    "MISSION_LINK": {"color": "#9AA7B2", "width": 1.2, "dash": "dot",
                     "label": "Mission link (analysis, not a relationship)"},
}

NODE_COLOR = {
    "user": "#0B1F33", "person": "#3F6F7A", "company": "#5C6B7A", "university": "#14304A",
    "industry": "#8A5A2B", "publication": "#6B4E71", "event": "#C07A2C",
    "association": "#7A8B6F", "goal": "#D7E4E7",
}

_RING = {"user": 0, "university": 1, "association": 2, "person": 2, "event": 2,
         "company": 2, "industry": 3, "publication": 3, "goal": 3}


def build_graph(raw: dict | None = None) -> NetworkGraph:
    """Validate the graph. A VERIFIED edge without a citation fails validation."""
    raw = raw or network_fixture()
    nodes = [NetworkNode.model_validate(n) for n in raw["nodes"]]
    ids = {n.node_id for n in nodes}
    edges = []
    for e in raw["edges"]:
        edge = NetworkEdge.model_validate(e)
        if edge.source in ids and edge.target in ids:
            edges.append(edge)
    return NetworkGraph(nodes=nodes, edges=edges)


def layout(graph: NetworkGraph) -> dict[str, tuple[float, float]]:
    rings: dict[int, list[NetworkNode]] = {}
    for n in graph.nodes:
        rings.setdefault(_RING.get(n.node_type, 3), []).append(n)
    pos: dict[str, tuple[float, float]] = {}
    for ring, members in rings.items():
        radius = ring * 1.15
        offset = ring * 0.45
        for i, n in enumerate(members):
            angle = offset + 2 * math.pi * i / max(len(members), 1)
            pos[n.node_id] = (radius * math.cos(angle), radius * math.sin(angle))
    return pos


def figure(graph: NetworkGraph | None = None) -> go.Figure:
    graph = graph or build_graph()
    pos = layout(graph)
    fig = go.Figure()
    for status, style in EDGE_STYLE.items():
        xs: list[float | None] = []
        ys: list[float | None] = []
        for e in graph.edges:
            if e.status != status:
                continue
            (x0, y0), (x1, y1) = pos[e.source], pos[e.target]
            xs += [x0, x1, None]
            ys += [y0, y1, None]
        fig.add_trace(go.Scatter(
            x=xs or [None], y=ys or [None], mode="lines", name=style["label"],
            line=dict(color=style["color"], width=style["width"], dash=style["dash"]),
            hoverinfo="skip", legendgroup=status,
        ))
    mids_x, mids_y, mids_text = [], [], []
    for e in graph.edges:
        (x0, y0), (x1, y1) = pos[e.source], pos[e.target]
        mids_x.append((x0 + x1) / 2)
        mids_y.append((y0 + y1) / 2)
        cite = f"<br>Source: {e.source_url} (retrieved {e.retrieved_at})" if e.source_url else ""
        mids_text.append(f"{e.relation} — {e.status}{cite}{('<br>' + e.note) if e.note else ''}")
    fig.add_trace(go.Scatter(
        x=mids_x, y=mids_y, mode="markers", marker=dict(size=6, opacity=0),
        hovertext=mids_text, hoverinfo="text", showlegend=False,
    ))
    fig.add_trace(go.Scatter(
        x=[pos[n.node_id][0] for n in graph.nodes],
        y=[pos[n.node_id][1] for n in graph.nodes],
        mode="markers+text",
        text=[n.label for n in graph.nodes],
        textposition="top center",
        textfont=dict(size=11, color="#1A2430"),
        marker=dict(
            size=[26 if n.node_type == "user" else 16 for n in graph.nodes],
            color=[NODE_COLOR.get(n.node_type, "#5C6B7A") for n in graph.nodes],
            line=dict(color="#0B1F33", width=1),
            symbol=["diamond" if n.node_type == "goal" else "circle" for n in graph.nodes],
        ),
        hovertext=[f"{n.label} ({n.node_type}){' — illustrative' if n.illustrative else ''}"
                   for n in graph.nodes],
        hoverinfo="text", showlegend=False,
    ))
    fig.update_layout(
        paper_bgcolor="#F7F3EC", plot_bgcolor="#F7F3EC", font=dict(color="#1A2430"),
        margin=dict(l=10, r=10, t=30, b=10), height=620,
        xaxis=dict(visible=False), yaxis=dict(visible=False, scaleanchor="x"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.12, x=0, bgcolor="rgba(0,0,0,0)"),
    )
    return fig
