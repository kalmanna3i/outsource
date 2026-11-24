"""Living universe canvas. Animation stays in the browser. No model call per frame.

Friendship sits with relationships, and coursework sits with intellectual,
as a visual cluster only. Saved dimensions stay in the payload.
"""

from __future__ import annotations

import json
from typing import Any

import streamlit.components.v1 as components

from services.universe import active_dimensions, node_detail

# Visible on the dark canvas. Keys that are not listed keep a light fallback.
_DISPLAY_COLOR = {
    "career": "#E9EDF2",
    "academic": "#83B7A1",
    "financial": "#B5A083",
    "relationships": "#8FB8C9",
    "family": "#D2A679",
    "lifestyle": "#C3B7A6",
    "health": "#7DCAA5",
    "legacy": "#A9B7C9",
    "friendship": "#8FB8C9",
    "coursework": "#83B7A1",
    "recovery": "#C3B7A6",
}
_FALLBACK = ("#E9EDF2", "#83B7A1", "#B5A083", "#8FB8C9", "#D2A679")

# Visual grouping only. The stored dimension is not removed or renamed.
_CLUSTER_PARENT = {"friendship": "relationships", "coursework": "academic"}
_CLUSTER_TITLE = {"academic": "Intellectual"}


def _display_color(key: str) -> str:
    if key in _DISPLAY_COLOR:
        return _DISPLAY_COLOR[key]
    return _FALLBACK[sum(ord(ch) for ch in key) % len(_FALLBACK)]


def universe_nodes(mandate, blueprint, assessments: dict[str, int]) -> list[dict[str, Any]]:
    nodes = []
    for dimension in active_dimensions(mandate, blueprint):
        shown = node_detail(dimension, assessments.get(dimension["key"]))
        nodes.append(
            {
                "key": dimension["key"],
                "name": dimension["name"],
                "description": dimension["description"],
                "detail": shown["detail"],
                "ring": shown["ring"],
                "color": _display_color(dimension["key"]),
                "parent": _CLUSTER_PARENT.get(dimension["key"]),
                "cluster": _CLUSTER_TITLE.get(dimension["key"]),
            }
        )
    return nodes


def universe_html(nodes: list[dict[str, Any]]) -> str:
    payload = json.dumps(nodes).replace("<", "\\u003c")
    return f"""
<div id="universe">
  <canvas id="sky"></canvas>
  <button id="pause" type="button">Pause</button>
  <div id="detail" hidden>
    <button id="close" type="button">Close</button>
    <h3 id="detail-name"></h3>
    <p id="detail-body"></p>
  </div>
</div>
<script id="universe-data" type="application/json">{payload}</script>
<style>
  html, body {{ margin: 0; height: 100%; background: #101923; }}
  #universe {{
    position: relative;
    width: 100%;
    height: 100%;
    min-height: 640px;
    background: #101923;
    border-radius: 8px;
    overflow: hidden;
    color: #E9EDF2;
    font-family: "Source Sans 3", sans-serif;
  }}
  #sky {{ width: 100%; height: 100%; display: block; }}
  #pause, #close {{
    position: absolute;
    top: 12px;
    right: 12px;
    background: transparent;
    color: #E9EDF2;
    border: 1px solid #B5A083;
    font-family: "Source Sans 3", sans-serif;
    font-weight: 400;
    padding: 0.3rem 0.7rem;
    cursor: pointer;
  }}
  #detail {{
    position: absolute;
    left: 16px;
    right: 16px;
    bottom: 16px;
    background: #101923;
    color: #E9EDF2;
    border: 1px solid #B5A083;
    padding: 0.8rem 1rem 0.9rem;
  }}
  #detail h3 {{
    margin: 0 0 0.35rem;
    font-family: "Source Sans 3", sans-serif;
    font-weight: 500;
    color: #E9EDF2;
  }}
  #detail p {{ margin: 0; line-height: 1.45; color: #E9EDF2; }}
  #close {{ position: absolute; top: 8px; right: 8px; }}
</style>
<script>
const nodes = JSON.parse(document.getElementById("universe-data").textContent);
const canvas = document.getElementById("sky");
const ctx = canvas.getContext("2d");
const detail = document.getElementById("detail");
const pauseBtn = document.getElementById("pause");
const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
let paused = reduced;
if (reduced) pauseBtn.textContent = "Motion off";

function resize() {{
  const rect = canvas.parentElement.getBoundingClientRect();
  const nextW = Math.max(320, Math.floor(rect.width));
  const nextH = Math.max(640, Math.floor(rect.height));
  if (canvas.width === nextW && canvas.height === nextH) return;
  canvas.width = nextW;
  canvas.height = nextH;
  if (paused) draw(0);
}}

const particles = Array.from({{length: 42}}, (_, i) => ({{
  edge: i % Math.max(nodes.length, 1),
  t: (i * 0.17) % 1,
  speed: 0.0012 + (i % 5) * 0.0003
}}));

function arrange(time) {{
  const byKey = Object.fromEntries(nodes.map((node) => [node.key, node]));
  const children = {{}};
  const ring = [];
  nodes.forEach((node) => {{
    if (node.parent && byKey[node.parent]) {{
      (children[node.parent] ||= []).push(node);
    }} else {{
      ring.push(node);
    }}
  }});
  const cx = canvas.width / 2;
  const cy = canvas.height / 2;
  const drift = paused ? 0 : time * 0.00008;
  const rx = Math.max(180, canvas.width / 2 - 120);
  const ry = Math.max(170, canvas.height / 2 - 150);
  const placed = ring.map((node, i) => {{
    const angle = drift + (Math.PI * 2 * i) / Math.max(ring.length, 1) - Math.PI / 2;
    const x = cx + Math.cos(angle) * rx;
    const y = cy + Math.sin(angle) * ry;
    const kids = (children[node.key] || []).map((child, k) => {{
      const dist = 58 + k * 46;
      return {{
        ...child,
        x: x + Math.cos(angle) * dist,
        y: y + Math.sin(angle) * dist,
        angle
      }};
    }});
    const lines = node.cluster ? [node.cluster, node.name] : [node.name];
    return {{ ...node, x, y, angle, lines, kids }};
  }});
  const flat = [];
  placed.forEach((node) => {{
    flat.push(node);
    node.kids.forEach((child) => flat.push({{ ...child, lines: [child.name] }}));
  }});
  flat.forEach((node) => {{
    const lines = node.lines;
    ctx.font = "400 13px Source Sans 3, sans-serif";
    const width = Math.max(...lines.map((line) => ctx.measureText(line).width));
    const height = lines.length * 16;
    const outward = node.angle === undefined ? 0 : node.angle;
    const dist = 16 + width / 2 * Math.abs(Math.cos(outward)) + height / 2 * Math.abs(Math.sin(outward));
    node.lx = node.x + Math.cos(outward) * dist;
    node.ly = node.y + Math.sin(outward) * dist;
    node.lw = width;
    node.lh = height;
    node.lines = lines;
  }});
  for (let pass = 0; pass < 24; pass += 1) {{
    let moved = false;
    for (let i = 0; i < flat.length; i += 1) {{
      for (let j = i + 1; j < flat.length; j += 1) {{
        const a = flat[i];
        const b = flat[j];
        const gapX = (a.lw + b.lw) / 2 + 8 - Math.abs(a.lx - b.lx);
        const gapY = (a.lh + b.lh) / 2 + 6 - Math.abs(a.ly - b.ly);
        if (gapX <= 0 || gapY <= 0) continue;
        const dx = b.lx - a.lx || 1;
        const dy = b.ly - a.ly || 0.01;
        const dist = Math.hypot(dx, dy) || 1;
        const push = Math.min(gapX, gapY) / 2 + 1;
        a.lx -= dx / dist * push;
        a.ly -= dy / dist * push;
        b.lx += dx / dist * push;
        b.ly += dy / dist * push;
        moved = true;
      }}
    }}
    flat.forEach((node) => {{
      node.lx = Math.min(canvas.width - 18 - node.lw / 2, Math.max(18 + node.lw / 2, node.lx));
      node.ly = Math.min(canvas.height - 18 - node.lh / 2, Math.max(18 + node.lh / 2, node.ly));
    }});
    if (!moved) break;
  }}
  return {{ placed, flat }};
}}

function ring(x, y, portion, color) {{
  ctx.beginPath();
  ctx.strokeStyle = "rgba(181,160,131,0.35)";
  ctx.lineWidth = 0.8;
  ctx.arc(x, y, 8, 0, Math.PI * 2);
  ctx.stroke();
  if (portion === null || portion === undefined) return;
  ctx.beginPath();
  ctx.strokeStyle = color;
  ctx.lineWidth = 1;
  ctx.arc(x, y, 8, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * Math.max(0, Math.min(1, portion)));
  ctx.stroke();
}}

function draw(time) {{
  const {{ placed, flat }} = arrange(time);
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "#101923";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  const cx = canvas.width / 2;
  const cy = canvas.height / 2;
  for (let i = 0; i < 72; i += 1) {{
    const angle = (i * 2.399) % (Math.PI * 2);
    const span = Math.min(canvas.width, canvas.height);
    const reach = span * (0.08 + (i % 11) * 0.03);
    ctx.fillStyle = "rgba(233,237,242,0.22)";
    ctx.beginPath();
    ctx.arc(cx + Math.cos(angle) * reach, cy + Math.sin(angle) * reach * 0.58, 0.7, 0, Math.PI * 2);
    ctx.fill();
  }}
  placed.forEach((node, i) => {{
    const next = placed[(i + 1) % placed.length];
    const across = placed[(i + 3) % placed.length];
    if (!next || placed.length < 2) return;
    ctx.strokeStyle = "rgba(131,183,161,0.4)";
    ctx.lineWidth = 0.45;
    ctx.beginPath();
    ctx.moveTo(node.x, node.y);
    ctx.lineTo(next.x, next.y);
    ctx.stroke();
    if (across && across !== next && across !== node) {{
      ctx.strokeStyle = "rgba(154,171,187,0.16)";
      ctx.lineWidth = 0.35;
      ctx.beginPath();
      ctx.moveTo(node.x, node.y);
      ctx.lineTo(across.x, across.y);
      ctx.stroke();
    }}
    node.kids.forEach((child) => {{
      ctx.strokeStyle = "rgba(154,171,187,0.55)";
      ctx.lineWidth = 0.4;
      ctx.beginPath();
      ctx.moveTo(node.x, node.y);
      ctx.lineTo(child.x, child.y);
      ctx.stroke();
    }});
  }});
  if (!paused && placed.length) {{
    particles.forEach((particle) => {{
      particle.t = (particle.t + particle.speed) % 1;
      const a = placed[particle.edge % placed.length];
      const b = placed[(particle.edge + 1) % placed.length];
      ctx.fillStyle = "#B5A083";
      ctx.beginPath();
      ctx.arc(a.x + (b.x - a.x) * particle.t, a.y + (b.y - a.y) * particle.t, 1.4, 0, Math.PI * 2);
      ctx.fill();
    }});
  }}
  const crowded = flat.some((node) => Math.hypot(node.x - cx, node.y - cy) < 36);
  if (!crowded) {{
    ctx.fillStyle = "#E9EDF2";
    ctx.font = "500 15px Source Sans 3, sans-serif";
    ctx.textAlign = "center";
    ctx.fillText("One life", cx, cy + 5);
  }}
  flat.forEach((node) => {{
    ring(node.x, node.y, node.ring, node.color);
    ctx.fillStyle = node.color;
    ctx.beginPath();
    ctx.arc(node.x, node.y, node.kids ? 3.1 : 2.2, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = "#E9EDF2";
    ctx.font = "400 13px Source Sans 3, sans-serif";
    ctx.textAlign = "center";
    node.lines.forEach((line, index) => {{
      const y = node.ly - node.lh / 2 + 13 + index * 16;
      ctx.fillText(line, node.lx, y);
    }});
  }});
  canvas._placed = flat;
  if (!paused) requestAnimationFrame(draw);
}}

pauseBtn.addEventListener("click", () => {{
  if (reduced) return;
  paused = !paused;
  pauseBtn.textContent = paused ? "Play" : "Pause";
  if (!paused) requestAnimationFrame(draw);
  else draw(performance.now());
}});

canvas.addEventListener("click", (event) => {{
  const rect = canvas.getBoundingClientRect();
  const x = (event.clientX - rect.left) * (canvas.width / rect.width);
  const y = (event.clientY - rect.top) * (canvas.height / rect.height);
  const hit = (canvas._placed || []).find((node) => {{
    const dx = node.x - x;
    const dy = node.y - y;
    return dx * dx + dy * dy < 18 * 18;
  }});
  if (!hit) return;
  document.getElementById("detail-name").textContent = hit.name;
  document.getElementById("detail-body").textContent = hit.detail;
  detail.hidden = false;
}});
document.getElementById("close").addEventListener("click", () => {{ detail.hidden = true; }});
resize();
window.addEventListener("resize", resize);
if (window.ResizeObserver) new ResizeObserver(resize).observe(canvas.parentElement);
requestAnimationFrame(draw);
</script>
"""


def render_living_universe(mandate, blueprint, assessments: dict[str, int]) -> None:
    nodes = universe_nodes(mandate, blueprint, assessments)
    if not nodes:
        components.html(
            "<p style='color:#E9EDF2;font-family:sans-serif'>No active life dimensions are stored yet.</p>",
            height=80,
        )
        return
    components.html(universe_html(nodes), height=640, scrolling=False)
