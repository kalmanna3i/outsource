#!/usr/bin/env python3
"""Build self-contained report.html and slides.html with embedded screenshots."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "deliverables" / "screenshots" / "manifest.b64.json"
REPO = "https://github.com/kalmanna3i/outsource"

import sys

SAFETY_TEST = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/test_safety.py", "tests/test_permissions_budget.py", "-q"],
    cwd=ROOT,
    capture_output=True,
    text=True,
    env={**__import__("os").environ, "APP_MODE": "demo"},
).stdout

ARCH_SVG = """<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 820 420' role='img' aria-label='OUTSOURCE agent flow'>
<defs><linearGradient id='g' x1='0' y1='0' x2='1' y2='1'><stop offset='0%' stop-color='#0B1F33'/><stop offset='100%' stop-color='#3F6F7A'/></linearGradient></defs>
<rect width='820' height='420' fill='#F7F3EC'/>
<rect x='20' y='20' width='180' height='50' rx='4' fill='url(#g)'/><text x='35' y='50' fill='#F7F3EC' font-family='sans-serif' font-size='14'>User request</text>
<rect x='220' y='20' width='160' height='50' fill='#14304A'/><text x='235' y='42' fill='#fff' font-size='12'>A01 Chief of Staff</text>
<rect x='400' y='20' width='160' height='50' fill='#14304A'/><text x='415' y='42' fill='#fff' font-size='12'>A02 Strategy</text>
<rect x='580' y='20' width='180' height='50' fill='#14304A'/><text x='595' y='42' fill='#fff' font-size='12'>B01 Opportunity Cost</text>
<rect x='120' y='110' width='160' height='50' fill='#3F6F7A'/><text x='135' y='140' fill='#fff' font-size='12'>F02 Decompose</text>
<rect x='320' y='110' width='160' height='50' fill='#3F6F7A'/><text x='335' y='140' fill='#fff' font-size='12'>F03 Execute</text>
<rect x='520' y='110' width='180' height='50' fill='#8A5A2B'/><text x='530' y='132' fill='#fff' font-size='11'>Simulated insurer wall</text>
<rect x='200' y='200' width='160' height='50' fill='#3F6F7A'/><text x='215' y='230' fill='#fff' font-size='12'>F05 Handoff brief</text>
<rect x='400' y='200' width='160' height='50' fill='#3F6F7A'/><text x='415' y='230' fill='#fff' font-size='12'>F04 Calendar/ICS</text>
<rect x='600' y='200' width='160' height='50' fill='#3F6F7A'/><text x='615' y='222' fill='#fff' font-size='12'>User result</text>
<rect x='320' y='300' width='200' height='50' fill='#0B1F33'/><text x='360' y='330' fill='#fff' font-size='12'>F06 Follow-up</text>
<line x1='200' y1='45' x2='220' y2='45' stroke='#3F6F7A' stroke-width='2'/>
<line x1='380' y1='45' x2='400' y2='45' stroke='#3F6F7A' stroke-width='2'/>
<line x1='560' y1='45' x2='580' y2='45' stroke='#3F6F7A' stroke-width='2'/>
<line x1='670' y1='70' x2='200' y2='110' stroke='#3F6F7A' stroke-width='2'/>
<line x1='280' y1='135' x2='320' y2='135' stroke='#3F6F7A' stroke-width='2'/>
<line x1='480' y1='135' x2='520' y2='135' stroke='#3F6F7A' stroke-width='2'/>
<line x1='610' y1='160' x2='280' y2='200' stroke='#3F6F7A' stroke-width='2'/>
<line x1='360' y1='225' x2='400' y2='225' stroke='#3F6F7A' stroke-width='2'/>
<line x1='560' y1='225' x2='600' y2='225' stroke='#3F6F7A' stroke-width='2'/>
<line x1='680' y1='250' x2='420' y2='300' stroke='#3F6F7A' stroke-width='2'/>
</svg>"""

IMG = json.loads(MANIFEST.read_text(encoding="utf-8"))


def img_tag(key: str, alt: str, max_width: str = "100%") -> str:
    return (
        f'<figure class="shot"><img alt="{alt}" style="max-width:{max_width};border:1px solid #D9D2C5" '
        f'src="data:image/png;base64,{IMG[key]}" /><figcaption>{alt}</figcaption></figure>'
    )


def build_report() -> str:
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/>
<title>OUTSOURCE — MGT 409 Report — Kay Al Mannai</title>
<style>
@page{{size:letter;margin:0.75in}}
body{{font-family:"Source Sans 3",Segoe UI,sans-serif;color:#1A2430;background:#F7F3EC;line-height:1.5;max-width:7.2in;margin:0 auto;padding:0.75in}}
h1,h2,h3{{font-family:Georgia,serif;color:#0B1F33}}
h2{{border-bottom:2px solid #3F6F7A;padding-bottom:.2rem;margin-top:1.6rem;page-break-after:avoid}}
table{{width:100%;border-collapse:collapse;font-size:.9rem;margin:.6rem 0}}
th,td{{border:1px solid #D9D2C5;padding:.35rem .45rem;text-align:left}}
th{{background:#E8EEF0}}
.shot{{margin:.7rem 0;page-break-inside:avoid}}
.shot img{{display:block;width:100%;height:auto}}
pre{{background:#0B1F33;color:#F7F3EC;padding:.6rem;font-size:.75rem;overflow:auto}}
.callout{{background:#EAF1F2;border-left:4px solid #3F6F7A;padding:.6rem .8rem;margin:.7rem 0}}
.warn{{background:#F3E8DA;border-left:4px solid #8A5A2B;padding:.6rem .8rem}}
.pagebreak{{page-break-before:always}}
.small{{font-size:.85rem;color:#5C6B7A}}
</style></head><body>

<h1>OUTSOURCE</h1>
<p><strong>Personal Strategy &amp; Execution Office</strong> · Kay Al Mannai · Yale MGT 409 · November 23, 2026</p>
<p><strong>Public repo:</strong> <a href="{REPO}">{REPO}</a><br/>
App: run locally with <code>streamlit run app.py</code> (no hosted link).<br/>
One sentence: OUTSOURCE decides what deserves your attention, executes AI-eligible work, and prepares the exact human moment when automation cannot continue.</p>

<h2>2. Motivation</h2>
<p>Kay Al Mannai (MBA candidate) faces evenings where an academic hard deadline, a fixed wedding, a work stakeholder update, and an insurance portal compete for the same hours. Today: calendar apps ignore goal weights; generic chatbots draft text but hallucinate completed calls; task lists do not produce a private brief plus a public ICS when identity verification blocks automation.</p>
<p>Cost: misallocated attention (polishing low-leverage email while a non-movable obligation approaches), rework after “the AI said it called the insurer,” and sensitive claim details pasted into calendar invites.</p>

<h2>3. What is new here</h2>
<table><tr><th>Existing</th><th>What they do</th><th>Gap OUTSOURCE addresses</th></tr>
<tr><td><strong>Lindy</strong></td><td>AI assistants for workflow automation</td><td>Not grounded in personal life-goal tradeoffs or human-only insurer gates with ICS handoff</td></tr>
<tr><td><strong>Motion</strong> / <strong>Reclaim</strong></td><td>Calendar autopilot for focus time</td><td>Optimize free/busy, not opportunity cost across relationship vs academic vs financial goals</td></tr>
<tr><td><strong>Duckbill</strong></td><td>Human+AI concierge for tasks</td><td>Humans-in-the-loop as a service; not a transparent multi-agent plan you can audit locally</td></tr>
<tr><td><strong>ChatGPT agents</strong></td><td>General agents + tools</td><td>Risk inventing completed external actions; no dedicated REVIEW_ALL gate or labeled demo insurer fixture</td></tr></table>
<p>OUTSOURCE’s twist: a <strong>strategy-aware execution office</strong> with honest simulation boundaries, separate private intervention briefs from public calendar text, and resume-after-result orchestration.</p>

<h2>4. The agents</h2>
<div class="shot">{ARCH_SVG}</div>
<table><tr><th>Agent</th><th>Role</th><th>Tools / outputs</th><th>Model</th></tr>
<tr><td>A01</td><td>Chief of Staff</td><td>Structured intake JSON</td><td>gpt-6-luna (Portkey) or OPENAI_MODEL when live</td></tr>
<tr><td>A02</td><td>Life Strategy</td><td>Reads SQLite Life Blueprint goals</td><td>same</td></tr>
<tr><td>B01</td><td>Opportunity Cost</td><td>Options, tradeoffs, sequence</td><td>same</td></tr>
<tr><td>F02</td><td>Decomposition</td><td>AI / HUMAN / DELEGATED packages</td><td>same</td></tr>
<tr><td>F03</td><td>Execution</td><td>Digital drafts only (no fake sends)</td><td>same</td></tr>
<tr><td>—</td><td>Insurer check</td><td><strong>Simulated</strong> Python fixture</td><td>n/a</td></tr>
<tr><td>F05</td><td>Human handoff</td><td>Brief, talking points, documents</td><td>same</td></tr>
<tr><td>F04</td><td>Calendar</td><td>Deterministic scheduler + ICS export</td><td>same</td></tr>
<tr><td>F06</td><td>Follow-up</td><td>Resume after user result</td><td>same</td></tr></table>
<p><strong>Organization:</strong> explicit Python orchestrator passes each agent’s JSON to the next prompt. Demo mode uses labeled fixtures (not live calls). Live mode: one chat completion per agent when keys present.</p>

<h3>One real run (demo mode, captured {len(IMG)} screens)</h3>
<ol>
<li>Daily Briefing intake with four-obligation request.</li>
<li>Run Priority 0 → goals, opportunity cost, AI vs human split.</li>
<li>Simulated insurer identity wall → intervention brief + ICS download.</li>
<li>User pastes verification result → COMPLETED + follow-ups.</li>
</ol>
{img_tag("daily_briefing_start","Step 1 — Daily Briefing (before run)")}
{img_tag("daily_briefing_after","Step 2 — After multi-agent run (intervention visible)")}
<div class="pagebreak"></div>
{img_tag("decisions","Step 3 — My Decisions (opportunity-cost plan)")}
{img_tag("work","Step 4 — My Work (AI vs human packages)")}
{img_tag("intervention","Step 5 — Intervention brief + ICS on Daily Briefing")}
{img_tag("resume","Step 6 — After submit result & resume (COMPLETED)")}
{img_tag("agent_activity","Step 7 — Agent Activity (demo: tokens/cost UNKNOWN)")}

<h2>5. Tokenomics</h2>
<table>
<tr><th>Metric</th><th>Demo run (measured)</th><th>Live run</th></tr>
<tr><td>Input tokens</td><td><strong>Not measured</strong> (fixtures; $0)</td><td class="warn"><strong>PLACEHOLDER — paste measured values after one live run:</strong> input: ____ · cached: ____ · output: ____</td></tr>
<tr><td>Cost per Priority 0 run</td><td>$0</td><td>Unknown until measured; app records usage when API returns it</td></tr>
<tr><td>20 runs / user / month</td><td>$0</td><td>20 × measured run cost</td></tr>
<tr><td>100 users / month</td><td>$0</td><td>100 × (monthly per user)</td></tr>
<tr><td>10,000 users / month</td><td>$0</td><td>10,000 × (monthly per user); caching + shorter prompts needed</td></tr>
</table>
<p><strong>Cost controls built:</strong> <code>MAX_AGENT_CALLS</code>, <code>MAX_WORKFLOW_COST_USD</code>, <code>APP_MODE=demo</code> default, REVIEW_ALL skips F03 unless approved. Tradeoff: demo cannot evidence token savings without live keys.</p>

<h2>6. Safety</h2>
<ul>
<li>Prompt-injection heuristics + quarantine banner on untrusted input</li>
<li>Secret scrubbing in UI/logs</li>
<li>Agents cannot claim emails/insurer calls completed</li>
<li>REVIEW_ALL permission gate before autonomous execution</li>
<li>ICS excludes private brief contents</li>
</ul>
{img_tag("safety","Settings — permission mode + safety self-check")}
<h3>Automated test output (defense evidence)</h3>
<pre>{SAFETY_TEST}</pre>

<h2>7. Impact</h2>
<p><strong>Evidence from this build (not a multi-user pilot):</strong></p>
<ul>
<li>End-to-end demo path completes in under one minute on local hardware (builder test).</li>
<li>Workflow cannot reach COMPLETED on insurance without a user-supplied verification result (WAITING_RESULT gate).</li>
<li>pytest: 14+ tests including E2E, scheduler conflict tests, safety, permissions.</li>
</ul>
<p class="warn">No invented user quotes or hours-saved claims. A real pilot would be the next evidence step.</p>

<h2>8. Limits + next steps</h2>
<ul>
<li>Insurer, email, SMS, purchases: simulated or not built.</li>
<li>Live tokenomics: Kay can run with course <code>PORTKEY_API_KEY</code> + <code>gpt-6-luna</code> and paste measured numbers into the placeholder above.</li>
<li>CUSTOM_AUTONOMY tool allowlist, Network/Career modules: planned.</li>
<li>Next month: calendar OAuth, live token screenshot, 3–5 user pilot.</li>
</ul>
<p class="small">Public repo · {REPO}</p>
</body></html>"""


def build_slides() -> str:
    keys = [
        ("daily_briefing_after", "Demo: after Priority 0 run"),
        ("decisions", "Opportunity-cost decisions"),
        ("intervention", "Human brief + ICS"),
        ("agent_activity", "Agent Activity (demo)"),
        ("safety", "Safety + permissions"),
    ]
    imgs = "\n".join(
        f'<img alt="{alt}" style="max-height:320px;width:auto;border:1px solid #3F6F7A" src="data:image/png;base64,{IMG[k]}"/>'
        for k, alt in keys
    )
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"/><title>OUTSOURCE Slides</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.css"/>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/theme/black.css"/>
<style>
.reveal h1,.reveal h2{{font-family:Georgia,serif;color:#F7F3EC}}
.reveal section{{background:linear-gradient(160deg,#0B1F33,#10263A 55%,#3F6F7A);}}
.reveal p,li{{color:#E7EEF2;font-size:.88em}}
.reveal a{{color:#9FCBD3}}
</style></head><body>
<div class="reveal"><div class="slides">

<section>
<h1>OUTSOURCE</h1>
<p>Kay Al Mannai · MGT 409</p>
<p><a href="{REPO}">{REPO}</a></p>
<p class="fragment">Know what matters. Do what only you can. Delegate the rest.</p>
</section>

<section><h2>Problem</h2><p>One evening: MBA deadline · wedding · work · insurance identity wall.</p></section>

<section><h2>What’s new vs Lindy, Motion, Reclaim, Duckbill, ChatGPT agents</h2><p>Goal-aware opportunity cost + honest human handoff (brief/ICS/resume), not generic automation.</p></section>

<section><h2>Agents</h2>{ARCH_SVG}<p>8 specialist calls (live) or labeled fixtures (demo).</p></section>

<section><h2>Demo screenshots</h2>{imgs}</section>

<section><h2>Cost</h2><p>Demo: $0, tokens not measured.</p><p>Live: fill measured tokens in report placeholder.</p></section>

<section><h2>Safety</h2><p>Injection quarantine · REVIEW_ALL gate · no fake insurer calls</p></section>

<section><h2>Impact (honest)</h2><p>Verified E2E locally; no pilot users.</p></section>

<section><h2>Limits &amp; next</h2><p>Public repo on GitHub · push live tokenomics · pilot users</p></section>

<section><h2>Run it</h2><p><code>streamlit run app.py</code></p><p><a href="{REPO}">{REPO}</a></p></section>

</div></div>
<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.js"></script>
<script>Reveal.initialize({{hash:true,slideNumber:true}});</script>
</body></html>"""


if __name__ == "__main__":
    (ROOT / "deliverables" / "report.html").write_text(build_report(), encoding="utf-8")
    (ROOT / "deliverables" / "slides.html").write_text(build_slides(), encoding="utf-8")
  # slide count
    slide_count = build_slides().count("<section>")
    print("wrote report + slides, sections=", slide_count)