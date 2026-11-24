"""Strategic network graph (Plotly). VERIFIED edges and HYPOTHETICAL paths are styled apart.

Labels are wrapped, pushed apart, and kept inside the plot so long names are not
stacked or clipped.
"""

from __future__ import annotations

import html
import math

import plotly.graph_objects as go

from core.radar_models import NetworkEdge, NetworkGraph, NetworkNode
from services.radar_fixtures import network_fixture

EDGE_STYLE = {
    "VERIFIED": {"color": "#83B7A1", "width": 1.35, "dash": "solid",
                 "label": "Verified · cited source"},
    "USER_PROVIDED": {"color": "#E9EDF2", "width": 1.0, "dash": "solid",
                      "label": "Your records"},
    "HYPOTHETICAL": {"color": "#B5A083", "width": 1.15, "dash": "dash",
                     "label": "Hypothetical · not a relationship"},
    "MISSION_LINK": {"color": "#9AABBB", "width": 0.8, "dash": "dot",
                     "label": "Mission link · analysis only"},
}

NODE_COLOR = {
    "user": "#E9EDF2", "person": "#83B7A1", "company": "#9AABBB", "university": "#B5A083",
    "industry": "#C4A484", "publication": "#C4B0D4", "event": "#D2B48C",
    "association": "#8FB8C9", "goal": "#E9EDF2",
}

_RING = {"user": 0, "university": 1, "association": 2, "person": 2, "event": 2,
         "company": 2, "industry": 3, "publication": 3, "goal": 3}

# Coordinates are sized like the chart people actually see, and label boxes
# are wider than the glyphs, so a slightly smaller render still does not collide.
CANVAS_W = 760
CANVAS_H = 560
_MARGIN = 16
_FONT = 11
_CHAR = 0.86
_LINE = _FONT + 3


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


def _wrap(label: str, limit: int = 16) -> list[str]:
    words = label.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = word if not current else f"{current} {word}"
        if current and len(trial) > limit:
            lines.append(current)
            current = word
        else:
            current = trial
    if current:
        lines.append(current)
    return lines or [label]


def _size(lines: list[str]) -> tuple[float, float]:
    width = max(len(line) for line in lines) * _FONT * _CHAR
    height = len(lines) * _LINE
    return width, height


def layout(graph: NetworkGraph) -> dict[str, tuple[float, float]]:
    """Node centers in plot coordinates (y increases upward)."""
    rings: dict[int, list[NetworkNode]] = {}
    for n in graph.nodes:
        rings.setdefault(_RING.get(n.node_type, 3), []).append(n)
    cx, cy = CANVAS_W / 2, CANVAS_H / 2 - 8
    radii = {0: 0.0, 1: 72.0, 2: 148.0, 3: 214.0}
    start = {1: 0.35, 2: 0.35 + math.pi / 8, 3: 0.35 + math.pi / 12}
    pos: dict[str, tuple[float, float]] = {}
    for ring, members in rings.items():
        radius = radii.get(ring, 520.0)
        offset = start.get(ring, 0.2)
        for i, n in enumerate(members):
            angle = offset + 2 * math.pi * i / max(len(members), 1)
            pos[n.node_id] = (cx + radius * math.cos(angle), cy + radius * math.sin(angle))
    return pos


def _overlaps(a: dict, b: dict, gap: float) -> bool:
    return (
        abs(a["cx"] - b["cx"]) < (a["w"] + b["w"]) / 2 + gap
        and abs(a["cy"] - b["cy"]) < (a["h"] + b["h"]) / 2 + gap
    )


def label_layout(graph: NetworkGraph) -> list[dict]:
    """One box per node label, inside the canvas and clear of the other labels."""
    pos = layout(graph)
    cx, cy = CANVAS_W / 2, CANVAS_H / 2
    boxes: list[dict] = []
    for node in graph.nodes:
        nx, ny = pos[node.node_id]
        lines = _wrap(node.label)
        width, height = _size(lines)
        angle = math.atan2(ny - cy, nx - cx)
        if math.hypot(nx - cx, ny - cy) < 1:
            lx, ly = nx, ny - 36 - height / 2
        else:
            dist = 16 + (width / 2) * abs(math.cos(angle)) + (height / 2) * abs(math.sin(angle))
            lx = nx + math.cos(angle) * dist
            ly = ny + math.sin(angle) * dist
        boxes.append({
            "node_id": node.node_id,
            "text": "<br>".join(html.escape(line) for line in lines),
            "plain": node.label,
            "cx": lx,
            "cy": ly,
            "w": width,
            "h": height,
            "nx": nx,
            "ny": ny,
        })
    def _clamp(box: dict) -> None:
        half_w, half_h = box["w"] / 2, box["h"] / 2
        box["cx"] = min(max(box["cx"], _MARGIN + half_w), CANVAS_W - _MARGIN - half_w)
        box["cy"] = min(max(box["cy"], _MARGIN + half_h), CANVAS_H - _MARGIN - half_h)

    for _ in range(100):
        moved = False
        for i, box in enumerate(boxes):
            for other in boxes[i + 1:]:
                if not _overlaps(box, other, 8):
                    continue
                dx = other["cx"] - box["cx"]
                dy = other["cy"] - box["cy"]
                dist = math.hypot(dx, dy) or 1.0
                need_x = (box["w"] + other["w"]) / 2 + 8 - abs(dx)
                need_y = (box["h"] + other["h"]) / 2 + 8 - abs(dy)
                push = min(need_x, need_y) / 2 + 1
                box["cx"] -= (dx / dist) * push
                box["cy"] -= (dy / dist) * push
                other["cx"] += (dx / dist) * push
                other["cy"] += (dy / dist) * push
                moved = True
        for box in boxes:
            _clamp(box)
            ndx = box["cx"] - box["nx"]
            ndy = box["cy"] - box["ny"]
            nd = math.hypot(ndx, ndy) or 1.0
            if nd < 24:
                box["cx"] = box["nx"] + (ndx / nd) * 24
                box["cy"] = box["ny"] + (ndy / nd) * 24
                _clamp(box)
                moved = True
        if not moved:
            break
    for box in boxes:
        half_w, half_h = box["w"] / 2, box["h"] / 2
        box["cx"] = min(max(box["cx"], _MARGIN + half_w), CANVAS_W - _MARGIN - half_w)
        box["cy"] = min(max(box["cy"], _MARGIN + half_h), CANVAS_H - _MARGIN - half_h)
        box["x"] = box["cx"] - half_w
        box["y"] = box["cy"] - half_h
    return boxes


def figure(graph: NetworkGraph | None = None) -> go.Figure:
    graph = graph or build_graph()
    pos = layout(graph)
    boxes = label_layout(graph)
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
        mode="markers",
        marker=dict(
            size=[9 if n.node_type == "user" else 5 for n in graph.nodes],
            color=[NODE_COLOR.get(n.node_type, "#9AABBB") for n in graph.nodes],
            line=dict(color="#090F18", width=1),
            symbol=["diamond" if n.node_type == "goal" else "circle" for n in graph.nodes],
        ),
        hovertext=[f"{n.label} ({n.node_type}){' — illustrative' if n.illustrative else ''}"
                   for n in graph.nodes],
        hoverinfo="text", showlegend=False,
        cliponaxis=False,
    ))
    for box in boxes:
        fig.add_annotation(
            x=box["cx"],
            y=box["cy"],
            text=box["text"],
            showarrow=False,
            xanchor="center",
            yanchor="middle",
            align="center",
            font=dict(size=_FONT, color="#E9EDF2", family="Source Sans 3, sans-serif"),
        )
    fig.update_layout(
        paper_bgcolor="#090F18",
        plot_bgcolor="#101923",
        font=dict(color="#E9EDF2", family="Source Sans 3, sans-serif"),
        margin=dict(l=8, r=8, t=8, b=36),
        height=620,
        xaxis=dict(visible=False, range=[0, CANVAS_W], constrain="domain"),
        yaxis=dict(visible=False, range=[0, CANVAS_H], scaleanchor="x"),
        showlegend=False,
    )
    return fig
