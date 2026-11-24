"""Living universe canvas. Animation stays in the browser. No model call per frame."""

from __future__ import annotations

import json
from typing import Any

import streamlit.components.v1 as components

from services.universe import active_dimensions, color_for, node_detail


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
                "color": color_for(dimension["key"]),
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
  #universe {{
    position: relative;
    height: 420px;
    background: #142438;
    border-radius: 8px;
    overflow: hidden;
    color: #F8F7F3;
    font-family: "Source Sans 3", sans-serif;
  }}
  #sky {{ width: 100%; height: 100%; display: block; }}
  #pause, #close {{
    position: absolute;
    top: 12px;
    right: 12px;
    background: transparent;
    color: #F8F7F3;
    border: 1px solid #B5A083;
    padding: 0.3rem 0.7rem;
    cursor: pointer;
  }}
  #detail {{
    position: absolute;
    left: 16px;
    right: 16px;
    bottom: 16px;
    background: #142438;
    color: #F8F7F3;
    border: 1px solid #B5A083;
    padding: 0.8rem 1rem 0.9rem;
  }}
  #detail h3 {{ margin: 0 0 0.35rem; font-family: Georgia, serif; color: #F8F7F3; }}
  #detail p {{ margin: 0; line-height: 1.45; color: #F8F7F3; }}
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
let frame = 0;
if (reduced) pauseBtn.textContent = "Motion off";

function resize() {{
  const rect = canvas.parentElement.getBoundingClientRect();
  canvas.width = Math.max(320, rect.width);
  canvas.height = 420;
}}
resize();
window.addEventListener("resize", resize);

const particles = Array.from({{length: 36}}, (_, i) => ({{
  edge: i % Math.max(nodes.length, 1),
  t: (i * 0.17) % 1,
  speed: 0.0015 + (i % 5) * 0.0004
}}));

function layout(time) {{
  const cx = canvas.width / 2;
  const cy = canvas.height / 2;
  const rx = Math.min(canvas.width, 880) * 0.34;
  const ry = 130;
  return nodes.map((node, i) => {{
    const drift = paused ? 0 : time * 0.00015;
    const angle = drift + (Math.PI * 2 * i) / Math.max(nodes.length, 1);
    return {{
      ...node,
      x: cx + Math.cos(angle) * rx,
      y: cy + Math.sin(angle) * ry
    }};
  }});
}}

function ring(x, y, portion, color) {{
  ctx.beginPath();
  ctx.strokeStyle = "rgba(181,160,131,0.45)";
  ctx.lineWidth = 4;
  ctx.arc(x, y, 28, 0, Math.PI * 2);
  ctx.stroke();
  if (portion === null || portion === undefined) return;
  ctx.beginPath();
  ctx.strokeStyle = color;
  ctx.lineWidth = 4;
  ctx.arc(x, y, 28, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * Math.max(0, Math.min(1, portion)));
  ctx.stroke();
}}

function draw(time) {{
  const placed = layout(time);
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "#142438";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  const cx = canvas.width / 2;
  const cy = canvas.height / 2;
  placed.forEach((a, i) => {{
    const b = placed[(i + 1) % placed.length];
    if (!b || placed.length < 2) return;
    ctx.strokeStyle = "rgba(73,110,101,0.85)";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(a.x, a.y);
    ctx.lineTo(b.x, b.y);
    ctx.stroke();
  }});
  if (!paused && placed.length) {{
    particles.forEach((p) => {{
      p.t = (p.t + p.speed) % 1;
      const a = placed[p.edge % placed.length];
      const b = placed[(p.edge + 1) % placed.length];
      const x = a.x + (b.x - a.x) * p.t;
      const y = a.y + (b.y - a.y) * p.t;
      ctx.fillStyle = "#B5A083";
      ctx.beginPath();
      ctx.arc(x, y, 2.2, 0, Math.PI * 2);
      ctx.fill();
    }});
  }}
  ctx.fillStyle = "#F8F7F3";
  ctx.font = "600 18px Georgia, serif";
  ctx.textAlign = "center";
  ctx.fillText("One life", cx, cy + 6);
  placed.forEach((node) => {{
    ring(node.x, node.y, node.ring, node.color);
    ctx.fillStyle = node.color;
    ctx.beginPath();
    ctx.arc(node.x, node.y, 8, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = "#F8F7F3";
    ctx.font = "600 14px Source Sans 3, sans-serif";
    ctx.fillText(node.name, node.x, node.y + 48);
  }});
  canvas._placed = placed;
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
    return dx * dx + dy * dy < 34 * 34;
  }});
  if (!hit) return;
  document.getElementById("detail-name").textContent = hit.name;
  document.getElementById("detail-body").textContent = hit.detail;
  detail.hidden = false;
}});
document.getElementById("close").addEventListener("click", () => {{ detail.hidden = true; }});
requestAnimationFrame(draw);
</script>
"""


def render_living_universe(mandate, blueprint, assessments: dict[str, int]) -> None:
    nodes = universe_nodes(mandate, blueprint, assessments)
    if not nodes:
        components.html(
            "<p style='color:#1A2430;font-family:sans-serif'>No active life dimensions are stored yet.</p>",
            height=80,
        )
        return
    components.html(universe_html(nodes), height=440, scrolling=False)
