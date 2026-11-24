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
    "academic": "#80B5A4",
    "financial": "#B5A083",
    "relationships": "#8FB8C9",
    "family": "#D2A679",
    "lifestyle": "#C3B7A6",
    "health": "#7DCAA5",
    "legacy": "#A9B7C9",
    "friendship": "#8FB8C9",
    "coursework": "#80B5A4",
    "recovery": "#C3B7A6",
}
_FALLBACK = ("#E9EDF2", "#80B5A4", "#B5A083", "#8FB8C9", "#D2A679")

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
  html, body {{ margin: 0; height: 100%; background: #11161F; }}
  #universe {{
    position: relative;
    width: 100%;
    height: 100%;
    background: #11161F;
    overflow: hidden;
    color: #E9EDF2;
    font-family: Inter, system-ui, sans-serif;
  }}
  #sky {{ width: 100%; height: 100%; display: block; }}
  #pause, #close {{
    position: absolute;
    top: 8px;
    right: 8px;
    background: transparent;
    color: #8D98A8;
    border: 1px solid rgba(255,255,255,.07);
    font-family: Inter, system-ui, sans-serif;
    font-weight: 400;
    font-size: 12px;
    padding: 0.15rem 0.45rem;
    cursor: pointer;
  }}
  #detail {{
    position: absolute;
    left: 12px;
    right: 12px;
    bottom: 12px;
    background: #151C27;
    color: #E9EDF2;
    border: 1px solid rgba(255,255,255,.07);
    padding: 0.6rem 0.75rem;
  }}
  #detail h3 {{
    margin: 0 0 0.3rem;
    font-family: Inter, system-ui, sans-serif;
    font-weight: 500;
    font-size: 14px;
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
  const nextW = Math.max(280, Math.floor(rect.width));
  const nextH = Math.max(280, Math.floor(rect.height));
  if (canvas.width === nextW && canvas.height === nextH) return;
  canvas.width = nextW;
  canvas.height = nextH;
  if (paused) draw(0);
}}

let hoverKey = null;
const homes = {{
  academic: [-0.72, -0.58],
  career: [-0.95, 0.02],
  financial: [0.92, -0.08],
  relationships: [0.12, 0.72],
  family: [-0.42, 0.48],
  health: [0.78, 0.58],
  lifestyle: [0.7, -0.62],
  legacy: [-0.78, 0.48],
  recovery: [0.28, -0.28]
}};

function arrange(time) {{
  const byKey = Object.fromEntries(nodes.map((node) => [node.key, node]));
  const children = {{}};
  const parents = [];
  nodes.forEach((node) => {{
    if (node.parent && byKey[node.parent]) {{
      (children[node.parent] ||= []).push(node);
    }} else {{
      parents.push(node);
    }}
  }});
  const cx = canvas.width / 2;
  const cy = canvas.height / 2;
  const reach = Math.min(canvas.width, canvas.height) * 0.34;
  const drift = paused ? 0 : Math.sin(time * 0.0004) * 1.2;
  const pad = 72;
  const inside = (x, y) => x > pad && x < canvas.width - pad && y > pad + 8 && y < canvas.height - pad;
  const placed = parents.map((node, i) => {{
    const home = homes[node.key] || [Math.cos(i * 1.7) * 0.7, Math.sin(i * 1.7) * 0.7];
    const x = Math.min(canvas.width - pad, Math.max(pad, cx + home[0] * reach + drift));
    const y = Math.min(canvas.height - pad, Math.max(pad, cy + home[1] * reach));
    const kids = (children[node.key] || []).map((child, k) => {{
      const base = Math.atan2(y - cy, x - cx);
      let angle = base + 0.85 + k * 0.5;
      let kx = x + Math.cos(angle) * 46;
      let ky = y + Math.sin(angle) * 46;
      if (!inside(kx, ky)) {{
        angle = base + Math.PI - 0.4;
        kx = x + Math.cos(angle) * 46;
        ky = y + Math.sin(angle) * 46;
      }}
      kx = Math.min(canvas.width - pad, Math.max(pad, kx));
      ky = Math.min(canvas.height - pad, Math.max(pad, ky));
      return {{ ...child, x: kx, y: ky, angle, primary: false }};
    }});
    return {{ ...node, x, y, angle: Math.atan2(y - cy, x - cx), lines: [node.name], kids, primary: true }};
  }});
  function kidsCount(key) {{ return (children[key] || []).length; }}
  const flat = [];
  placed.forEach((node) => {{
    flat.push(node);
    if (node.cluster) {{
      const child = node.kids[0];
      const away = child ? Math.atan2(node.y - child.y, node.x - child.x) : node.angle + Math.PI;
      flat.push({{
        key: node.key + "-cluster",
        name: node.cluster,
        detail: "",
        color: node.color,
        x: node.x + Math.cos(away) * 34,
        y: node.y + Math.sin(away) * 26,
        angle: away,
        lines: [node.cluster],
        labelOnly: true
      }});
    }}
    node.kids.forEach((child) => flat.push({{ ...child, lines: [child.name] }}));
  }});
  flat.forEach((node) => {{
    const lines = node.lines;
    ctx.font = "400 11px Inter, system-ui, sans-serif";
    const width = Math.max(...lines.map((line) => ctx.measureText(line).width));
    const height = lines.length * 14;
    const outward = node.angle === undefined ? 0 : node.angle;
    const dist = 12 + width / 2 * Math.abs(Math.cos(outward)) + height / 2 * Math.abs(Math.sin(outward));
    node.lx = node.x + Math.cos(outward) * dist;
    node.ly = node.y + Math.sin(outward) * dist;
    if (Math.hypot(node.lx - cx, node.ly - (cy + 8)) < 52) {{
      const away = Math.atan2(node.y - cy, node.x - cx);
      node.lx = node.x + Math.cos(away) * (dist + 18);
      node.ly = node.y + Math.sin(away) * (dist + 18);
    }}
    node.lw = width;
    node.lh = height;
    node.lines = lines;
  }});
  for (let pass = 0; pass < 40; pass += 1) {{
    let moved = false;
    for (let i = 0; i < flat.length; i += 1) {{
      for (let j = i + 1; j < flat.length; j += 1) {{
        const a = flat[i];
        const b = flat[j];
        const gapX = (a.lw + b.lw) / 2 + 14 - Math.abs(a.lx - b.lx);
        const gapY = (a.lh + b.lh) / 2 + 10 - Math.abs(a.ly - b.ly);
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

function draw(time) {{
  const {{ placed, flat }} = arrange(time);
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "#11161F";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  const cx = canvas.width / 2;
  const cy = canvas.height / 2;
  placed.forEach((node) => {{
    node.kids.forEach((child) => {{
      const hot = hoverKey === node.key || hoverKey === child.key;
      ctx.strokeStyle = hot ? "#80B5A4" : "rgba(141,152,168,0.45)";
      ctx.lineWidth = hot ? 1 : 0.7;
      ctx.beginPath();
      ctx.moveTo(node.x, node.y);
      ctx.lineTo(child.x, child.y);
      ctx.stroke();
    }});
  }});
  ctx.fillStyle = "#8D98A8";
  ctx.beginPath();
  ctx.arc(cx, cy, 3.5, 0, Math.PI * 2);
  ctx.fill();
  ctx.font = "400 11px Inter, system-ui, sans-serif";
  ctx.textAlign = "center";
  ctx.fillText("Mission", cx, cy + 16);
  flat.forEach((node) => {{
    if (!node.labelOnly) {{
      const hot = hoverKey === node.key;
      ctx.fillStyle = node.color;
      ctx.beginPath();
      ctx.arc(node.x, node.y, hot ? (node.primary ? 6 : 3) : (node.primary ? 4.5 : 2.2), 0, Math.PI * 2);
      ctx.fill();
    }}
    ctx.fillStyle = node.labelOnly ? "#8D98A8" : "#E9EDF2";
    ctx.font = "400 11px Inter, system-ui, sans-serif";
    ctx.textAlign = "center";
    node.lines.forEach((line, index) => {{
      const y = node.ly - node.lh / 2 + 11 + index * 14;
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

canvas.addEventListener("mousemove", (event) => {{
  const rect = canvas.getBoundingClientRect();
  const x = (event.clientX - rect.left) * (canvas.width / rect.width);
  const y = (event.clientY - rect.top) * (canvas.height / rect.height);
  const hit = (canvas._placed || []).find((node) => {{
    if (node.labelOnly) return false;
    const dx = node.x - x;
    const dy = node.y - y;
    return dx * dx + dy * dy < 12 * 12;
  }});
  const next = hit ? hit.key : null;
  if (next !== hoverKey) {{
    hoverKey = next;
    if (paused) draw(0);
  }}
}});

canvas.addEventListener("click", (event) => {{
  const rect = canvas.getBoundingClientRect();
  const x = (event.clientX - rect.left) * (canvas.width / rect.width);
  const y = (event.clientY - rect.top) * (canvas.height / rect.height);
  const hit = (canvas._placed || []).find((node) => {{
    if (node.labelOnly) return false;
    const dx = node.x - x;
    const dy = node.y - y;
    return dx * dx + dy * dy < 14 * 14;
  }});
  if (!hit || !hit.detail) return;
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
    components.html(universe_html(nodes), height=360, scrolling=False)
