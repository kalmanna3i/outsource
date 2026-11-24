"""Long-form report body (3,500–4,500 words) for MGT 409."""

from __future__ import annotations

import base64
import html
import json
from pathlib import Path
from typing import Any, Callable


LIVE_SHOT = Path(__file__).resolve().parent.parent / "deliverables" / "live_agent_activity.png"


def live_figure() -> str:
    """Figure 9: Agent Activity screenshot from the measured live run (Nov 23, 2026)."""
    b64 = base64.b64encode(LIVE_SHOT.read_bytes()).decode()
    return (
        '<figure class="shot"><img alt="Figure 9 — Agent Activity after the live gpt-6-luna run: per-agent input, cached and output tokens and cost" style="max-width:100%;max-height:none;border:1px solid #D9D2C5" src="data:image/png;base64,'
        + b64
        + '" /><figcaption>Figure 9 — Agent Activity after the live gpt-6-luna run (measured tokens and cost per agent)</figcaption></figure>'
    )


def capture_demo_trace() -> dict[str, Any]:
    from datetime import datetime

    from core.config import get_settings
    from core.llm import LLMClient
    from database.db import reset_demo_data
    from services.workflow import WorkflowEngine

    reset_demo_data()
    engine = WorkflowEngine(LLMClient(get_settings()))
    req = (
        "I need to finish my MBA final tonight, attend a wedding, "
        "handle an important work obligation, and find out what is happening with my insurance claim."
    )
    state = engine.run_priority0(req, now=datetime(2026, 11, 23, 9, 30))
    state = engine.resume_with_result(
        state, "Verified identity. Claim under review; upload EOB within 14 days."
    )
    return {
        "workflow_id": state.workflow_id,
        "mode": state.mode,
        "transitions": state.transitions,
        "agent_calls": [
            c.model_dump(include={"agent_id", "role", "mode", "success", "summary"})
            for c in state.agent_calls
        ],
        "recommended_sequence": state.decision_plan.recommended_sequence if state.decision_plan else [],
        "work_packages": [w.model_dump() for w in state.work_packages],
        "intervention": state.interventions[-1].model_dump() if state.interventions else {},
        "calendar_slots": [s.model_dump() for s in state.calendar_slots],
        "evidence_types": [e.evidence_type for e in state.evidence],
        "follow_ups": state.follow_ups,
        "final_status": state.status.value,
    }


AGENT_TABLE_ROWS = """
<tr><td>A01</td><td>Chief of Staff</td><td>user_request, goal titles</td><td>LLM JSON only (no external tools)</td><td>summary, obligations, constraints, specialists_needed</td><td>A02, B01</td></tr>
<tr><td>A02</td><td>Life Strategy Architect</td><td>Life Blueprint goals (SQLite), A01 JSON</td><td>read Blueprint DB</td><td>goal_readout, alignment_scores, strategic_guidance</td><td>B01, F02</td></tr>
<tr><td>B01</td><td>Opportunity Cost Economist</td><td>A02 output, constraints</td><td>LLM JSON</td><td>options[], recommended_sequence, tradeoffs</td><td>F02 → DecisionPlan UI</td></tr>
<tr><td>F02</td><td>Task Decomposition</td><td>B01 sequence, strategy text</td><td>LLM JSON</td><td>work_packages[] with assignee AI|HUMAN</td><td>F03, human packages</td></tr>
<tr><td>F03</td><td>Autonomous Execution</td><td>AI-tagged work_packages</td><td>LLM JSON; permission gate</td><td>executed[], blockers[]</td><td>digital_deliverables UI</td></tr>
<tr><td>—</td><td>Insurer fixture</td><td>claim ref</td><td><strong>simulated</strong> Python (<code>check_claim_status</code>)</td><td>IDENTITY_VERIFICATION_REQUIRED</td><td>F05</td></tr>
<tr><td>F05</td><td>Human Handoff</td><td>insurer blocker message</td><td>LLM JSON</td><td>title, prepared_brief, talking_points, documents_ready</td><td>HumanIntervention model, F04</td></tr>
<tr><td>F04</td><td>Calendar &amp; Logistics</td><td>intervention title, busy wedding block</td><td>LLM JSON + <strong>deterministic</strong> <code>find_slot</code>, <code>export_ics</code></td><td>scheduling_requests[] → CalendarSlot</td><td>ICS download, My Calendar UI</td></tr>
<tr><td>F06</td><td>Follow-Up</td><td>user_result string, work_packages</td><td>LLM JSON</td><td>follow_ups[], closure_status</td><td>My Work UI</td></tr>
"""


def build_tokenomics_html() -> str:
    """Section 5 from audit/LIVE_TOKEN_USAGE.csv. Numbers are sums, not a second estimate."""
    import csv

    path = Path(__file__).resolve().parent.parent / "audit" / "LIVE_TOKEN_USAGE.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    def num(row: dict[str, str], key: str) -> float:
        raw = (row.get(key) or "").strip()
        return float(raw) if raw else 0.0

    input_tokens = int(sum(num(row, "input_tokens") for row in rows))
    cached = int(sum(num(row, "cached_input_tokens") for row in rows))
    cache_write = int(sum(num(row, "cache_write_tokens") for row in rows))
    output_tokens = int(sum(num(row, "output_tokens") for row in rows))
    cost = sum(num(row, "cost_usd") for row in rows)
    naive = (input_tokens / 1_000_000) * 0.10 + (output_tokens / 1_000_000) * 0.50
    body = []
    for row in rows:
        body.append(
            "<tr><td>{agent} {name}</td><td>{inn}</td><td>{cached}</td><td>{written}</td>"
            "<td>{out}</td><td>${cost:.6f}</td><td>{ms}</td></tr>".format(
                agent=html.escape(row["agent_id"]),
                name=html.escape(row["agent_name"]),
                inn=int(num(row, "input_tokens")),
                cached=int(num(row, "cached_input_tokens")),
                written=int(num(row, "cache_write_tokens")),
                out=int(num(row, "output_tokens")),
                cost=num(row, "cost_usd"),
                ms=html.escape(row.get("duration_ms") or ""),
            )
        )
    per_user = 20 * cost
    return f"""
<p>The numbers in this section are the sum of <code>audit/LIVE_TOKEN_USAGE.csv</code> from one live process on Nov 23, 2026 at 7:28 PM ET. The model was <code>gpt-6-luna</code> on the OpenAI API. <code>LLM_MODE=live</code> and <code>INTEGRATION_MODE=simulated</code>: email, purchases, and the insurer stayed simulated. The course Portkey route was not used for this measurement. Cached input tokens were {cached}. Cache-write tokens were {cache_write}, all on A02, and those tokens are already inside the input count. They are priced at $0.125 per 1M instead of $0.10, which is why the summed row cost differs from a plain input-plus-output product.</p>
<p>Plain product with zero cache-write: ${naive:.6f}. Sum of the row costs in the CSV: <strong>${cost:.6f}</strong>. Wall clock for the whole process: <strong>83.8 s</strong>. Model tool calls: <strong>0</strong>. The insurer step is simulated Python, not a tool call.</p>
<table>
<tr><th>Call</th><th>Input</th><th>Cached</th><th>Cache write</th><th>Output</th><th>Cost</th><th>ms</th></tr>
{''.join(body)}
<tr><td><strong>Total ({len(rows)} live calls)</strong></td><td><strong>{input_tokens}</strong></td><td><strong>{cached}</strong></td><td><strong>{cache_write}</strong></td><td><strong>{output_tokens}</strong></td><td><strong>${cost:.6f}</strong></td><td>83.8 s wall</td></tr>
</table>
<p>Runs inside that file: a smoke JSON call, one structured-output call, Priority 0 workflow <code>wf_1fb3c7f55ef2</code> through resume (A01, A02, B01, F02, F03, F05, F04, F06), and discovery S01 → D01 → Q01. The deterministic rank for the fictional executive chose <code>infra-nonprofit</code>. The model chose <code>home-dinner</code>, which is a real id in the labeled dataset. Both are kept. The mission was not rewritten to force them to agree. Radar R01–R08, contextual C01–C02, and stacking L01–L06 were not in this live bill.</p>
<h3>Definitions</h3>
<ul>
<li><strong>R</strong> = 20 workflows per user per month. That is an assumption, not a measured rate.</li>
<li><strong>C_run</strong> = ${cost:.6f}, the summed CSV cost, not a rounded slogan.</li>
<li>Price source: <code>core/llm.py</code> <code>_EST_PRICE_PER_1M</code>. gpt-6-luna rates are OpenAI Standard short-context prices from MGT 409 Lecture 11: input $0.10, cached input $0.01, cache write $0.125, output $0.50 per 1M. This is not a provider invoice.</li>
</ul>
<table>
<tr><th>Scale</th><th>Formula</th><th>Demo</th><th>Live, using this CSV and R = 20</th></tr>
<tr><td>One measured process</td><td>C_run</td><td>$0</td><td><strong>${cost:.6f}</strong></td></tr>
<tr><td>Per user / month</td><td>R × C_run</td><td>$0</td><td><strong>${per_user:.4f}</strong></td></tr>
<tr><td>100 users / month</td><td>100 × R × C_run</td><td>$0</td><td><strong>${100 * per_user:.2f}</strong></td></tr>
<tr><td>10,000 users / month</td><td>10,000 × R × C_run</td><td>$0</td><td><strong>${10000 * per_user:.2f}</strong> before caching or output caps</td></tr>
</table>
<p>Demo mode still records unknown tokens. The commercial product is not built. These figures are one homework measurement.</p>
"""


def render_expanded_report(
    *,
    repo: str,
    arch_svg: str,
    safety_test: str,
    trace: dict[str, Any],
    img: Callable[[str, str], str],
    img_media: Callable[[str, str], str] | None = None,
) -> str:
    if img_media is None:
        img_media = lambda _k, _a: ""
    trace_json = html.escape(
        json.dumps(
            {
                "workflow_id": trace["workflow_id"],
                "final_status": trace["final_status"],
                "follow_ups": trace["follow_ups"],
                "evidence_types": trace["evidence_types"],
            },
            indent=2,
        )
    )
    safety_esc = html.escape(safety_test)
    transitions_esc = html.escape(json.dumps(trace["transitions"], indent=2))
    wp_esc = html.escape(json.dumps(trace["work_packages"][:2], indent=2, default=str)[:1200])
    hi_min = {
        k: trace["intervention"].get(k)
        for k in (
            "intervention_id",
            "title",
            "status",
            "why_human_required",
            "suggested_slot",
            "ics_path",
        )
    }
    hi_esc = html.escape(json.dumps(hi_min, indent=2, default=str))
    calls_esc = html.escape(
        json.dumps([{"agent_id": c["agent_id"], "role": c["role"], "mode": c["mode"]} for c in trace["agent_calls"]], indent=2)
    )
    token_html = build_tokenomics_html()

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/>
<title>OUTSOURCE — MGT 409 Report — Kay Al Mannai</title>
<style>
@page{{size:letter;margin:0.7in}}
body{{font-family:"Source Sans 3",Segoe UI,sans-serif;color:#1A2430;background:#F7F3EC;line-height:1.55;font-size:11pt;max-width:7.25in;margin:0 auto;padding:0.65in 0.7in 0.9in}}
h1{{font-family:Georgia,serif;color:#0B1F33;font-size:26pt;margin-bottom:0.15in}}
h2{{font-family:Georgia,serif;color:#0B1F33;font-size:16pt;border-bottom:2px solid #3F6F7A;padding-bottom:0.12in;margin-top:0.35in;page-break-after:avoid}}
h3{{font-family:Georgia,serif;color:#14304A;font-size:12.5pt;margin-top:0.22in}}
p{{margin:0.45em 0;text-align:justify}}
table{{width:100%;border-collapse:collapse;font-size:10pt;margin:0.45em 0 0.65em}}
th,td{{border:1px solid #D9D2C5;padding:0.28em 0.38em;vertical-align:top}}
th{{background:#E8EEF0}}
.shot{{margin:0.5em 0;page-break-inside:avoid}}
.shot img{{display:block;width:100%;max-height:2.15in;object-fit:contain;border:1px solid #D9D2C5}}
.shot figcaption{{font-size:9pt;color:#5C6B7A;margin-top:0.2em}}
pre{{background:#0B1F33;color:#F7F3EC;padding:0.45em;font-size:8pt;line-height:1.35;overflow:auto;page-break-inside:avoid}}
.callout{{background:#EAF1F2;border-left:4px solid #3F6F7A;padding:0.45em 0.65em;margin:0.5em 0}}
.warn{{background:#F3E8DA;border-left:4px solid #8A5A2B;padding:0.45em 0.65em;margin:0.5em 0}}
.placeholder{{border:2px dashed #8A5A2B;background:#FFF9F0;padding:0.6em;margin:0.5em 0;font-size:10pt}}
.pagebreak{{page-break-before:always}}
ul,ol{{margin:0.35em 0;padding-left:1.25em}}
li{{margin:0.2em 0}}
.small{{font-size:9pt;color:#5C6B7A}}
</style></head><body>

<h1>OUTSOURCE</h1>

<h2>1. Title + links</h2>
<p><strong>Kay Al Mannai</strong> · Yale School of Management · MGT 409 AI Foundations for Managers · November 23, 2026 (America/New_York).</p>
<p><strong>Public repo:</strong> <a href="{repo}">{repo}</a> · clone branch <strong>main</strong> · <strong>68 tests</strong> pass under <code>APP_MODE=demo</code>.</p>
<p><strong>Application:</strong> run locally — <code>streamlit run app.py</code> (no production hosting in this submission).</p>
<p>OUTSOURCE is a Personal Strategy &amp; Execution Office: Priority 0 compares opportunity costs and prepares human handoffs; extension modules add <strong>Strategic Radar</strong> (mission-aligned discovery), <strong>Contextual Opportunities</strong> (travel-window bundling), and <strong>Opportunity Stacking</strong> (multidimensional life commitments). All extension UI paths in this submission ran in <strong>demo mode</strong> with labeled fixtures unless noted as deterministic code.</p>
<p class="small">Priority 0 screenshots are from a demo-mode run on the build machine ({trace['mode']} mode). Module screenshots are from labeled SIMULATED_FIXTURE flows on branch main.</p>

<h2>2. Motivation</h2>
<h3>Fictional persona (not a real pilot user)</h3>
<p><strong>Maya Chen</strong> is a <em>fictional</em> second-year MBA executive: she leads a small product team during the day, carries a 4.0 credit load, and is responsible for family logistics. On submission nights she faces four simultaneous pulls: a course final due at 11:59 PM Eastern, a close friend’s wedding with a fixed ceremony window, a stakeholder expecting a work status note, and an insurance claim stuck behind an identity-verification gate. Maya is competent; her bottleneck is not lack of intelligence but <strong>attention fragmentation</strong> and tools that optimize the wrong objective.</p>
<h3>Today’s manual workflow (typical)</h3>
<p>Maya scatters the evening across a notes app, a general chat tab, email drafts, and an insurer portal—often <strong>fifteen or more</strong> context switches—with no persisted tradeoffs, no calendar brief separation, and frequent false completion (“the bot checked the claim”). OUTSOURCE compresses preparation into one intake, one ranked plan, AI-only drafts where honest, and one resumable human gate for identity verification.</p>
<p>The same constraint shows up beyond one deadline night. Ambitions are expansive, and time, money, energy, and attention are finite. Achievement and humanity have to fit in the same week. A second fictional person, Amina Okonkwo, is an MBA student at an infrastructure company who also has a dog, a home, a recovery evening she stated herself, a philanthropic interest, and a trip she cannot honestly take during deadline week. The Life Mandate stores her mission and her sentence about success. The software does not invent that sentence, and it does not fill every hour.</p>

<h2>3. What is new here</h2>
<p>Competition is real. Lindy, Motion, Reclaim, Duckbill, and OpenAI’s agent experiences all help individuals offload work. OUTSOURCE does not claim a green-field market; it occupies a narrower wedge: <strong>goal-weighted opportunity cost</strong>, <strong>explicit AI/HUMAN allocation</strong>, and a <strong>handoff contract</strong> that stops at identity walls instead of faking success. The table below lists only features this repository actually implements (verifiable in code/UI) versus publicly known positioning of named products—without asserting their internal architectures.</p>
<table>
<tr><th>Product</th><th>What they are known for</th><th>OUTSOURCE implements (verifiable in this repo)</th><th>Still different here</th></tr>
<tr><td><strong>Lindy</strong></td><td>AI assistant / workflow automation for professionals</td><td>No Lindy integration; local multi-agent orchestration in Python</td><td>Life Blueprint SQLite goals feed B01 opportunity-cost objects; not a hosted Lindy clone</td></tr>
<tr><td><strong>Motion</strong></td><td>AI calendar and task auto-scheduling</td><td>Deterministic <code>find_slot</code> with busy blocks, business hours, buffers—not ML scheduling</td><td>Schedules <em>human intervention</em> after strategy agents, not generic task churn</td></tr>
<tr><td><strong>Reclaim</strong></td><td>Habits, focus time, calendar defense</td><td>Fixed wedding busy block seeded in workflow; slot search avoids overlap</td><td>Tradeoffs tied to academic/relationship/financial goals, not only focus habits</td></tr>
<tr><td><strong>Duckbill</strong></td><td>Human+AI concierge completing errands</td><td>No human concierge staff; simulated insurer only</td><td>Transparent local audit trail (Agent Activity, state transitions) for coursework</td></tr>
<tr><td><strong>ChatGPT agents</strong></td><td>General tool-using agents</td><td>Bounded specialist prompts + JSON handoffs + REVIEW_ALL permission gate</td><td>Insurer path labeled SIMULATED_FIXTURE; WAITING_RESULT until user_result</td></tr>
</table>
<p>The novelty for grading is <strong>honest orchestration</strong>: public ICS text stays separate from private briefs; F06 resumes only after user-supplied evidence; simulated discovery and stacking matrices stay labeled; one Yale SOM campus address is stored as <code>VERIFIED_SOURCE</code> while hypothetical introduction edges on the network graph are dashed and never shown as real relationships.</p>

<div class="pagebreak"></div>
<h2>4. The agents</h2>
<h3>Architecture (inline diagram)</h3>
<div class="shot">{arch_svg}</div>

<h3>Per-agent contract</h3>
<table>
<tr><th>ID</th><th>Role</th><th>Inputs</th><th>Tools</th><th>Output schema (keys)</th><th>Downstream consumer</th></tr>
{AGENT_TABLE_ROWS}
</table>
<h3>Handoff contract</h3>
<p>Each specialist returns JSON via <code>LLMClient.complete</code>; <code>WorkflowEngine</code> maps fields into Pydantic models and logs <code>AgentCallRecord</code> rows. Demo fixtures are <code>_demo_labeled</code>; live mode uses <code>response_format: json_object</code>. F03 is gated by REVIEW_ALL permissions; the insurer step is Python <code>SIMULATED_FIXTURE</code>, not an LLM claim.</p>
<h3>Extension modules (demo mode in submission)</h3>
<table>
<tr><th>Module</th><th>Agents</th><th>Simulated / illustrative</th><th>Operational (deterministic or gated)</th><th>Planned</th></tr>
<tr><td>Strategic Radar</td><td>R01–R08 + A01-style execution hooks</td><td>Discovery feed, graph nodes beyond one verified address</td><td>Mission audit rules; research-to-action (outreach draft <em>not sent</em>, ICS, brief, follow-up)</td><td>Background monitoring scheduler</td></tr>
<tr><td>Contextual Opportunities</td><td>C01–C02</td><td>ORD/Boston scenario fixtures</td><td>Layover feasibility math; Boston bundle +$210 / +35 min vs original itinerary</td><td>Live travel APIs</td></tr>
<tr><td>Opportunity Stacking</td><td>L01–L06 Life Dimension strategists</td><td>Comparison matrix rows (not researched orgs)</td><td>Hours math: 18 vs 6 hrs/mo → 144 hrs/yr <em>only if comparable benefits</em>; anti–double-count scoring</td><td>Live nonprofit research</td></tr>
</table>
<p>Radar, contextual scenarios, and the six stacking strategists were tested in demo mode. They are not in the Section 5 bill. The Life Mandate path did make three live calls (S01, D01, Q01) on a labeled dataset, not a web search. Changing an approved priority order changes the deterministic discretionary pick. The model may choose a different id. That disagreement is shown. The mission text is not rewritten to hide it.</p>
<h3>Model choice: why <code>gpt-6-luna</code> on the course key</h3>
<p>Yale MGT 409 restricts the course Portkey key to <strong>gpt-6-luna</strong>. Eight JSON completions cover Priority 0; demo mode spends $0 for grading and module screenshots.</p>
<h3>Step-by-step trace of the captured demo run</h3>
<p>Workflow <code>{trace['workflow_id']}</code> · final status <code>{trace['final_status']}</code> · agent calls before resume: 7 · after F06: 8.</p>
<ol>
<li><strong>INTAKE→ANALYZING:</strong> user request stored as <code>USER_PROVIDED</code> evidence.</li>
<li><strong>A01–B01:</strong> produce opportunity-cost sequence (six recommended steps).</li>
<li><strong>F02:</strong> six work packages—three AI, three HUMAN—with explicit <code>depends_on</code> on insurance verification.</li>
<li><strong>F03:</strong> MBA checklist + work draft marked COMPLETED; insurance package BLOCKED_HUMAN.</li>
<li><strong>Insurer fixture:</strong> returns identity gate (no API call).</li>
<li><strong>F05+F04:</strong> intervention brief + slot <code>2026-11-23 09:45–10:15</code> before wedding block <code>16:00–20:00</code>.</li>
<li><strong>WAITING_RESULT:</strong> UI blocks COMPLETED until user text.</li>
<li><strong>F06:</strong> three follow-ups after resume.</li>
</ol>
<h3>Human intervention object (truncated)</h3>
<pre>{hi_esc}</pre>
{img("daily_briefing_start","Figure 1 — Daily Briefing before Priority 0 run")}
{img("daily_briefing_after","Figure 2 — After run: WAITING_RESULT, intervention card")}
<div class="pagebreak"></div>
{img("decisions","Figure 3 — My Decisions: opportunity-cost table")}
{img("work","Figure 4 — My Work: AI vs HUMAN packages and statuses")}
{img("intervention","Figure 5 — Private brief, scheduled slot, ICS download")}
{img("resume","Figure 6 — After Submit result &amp; resume: COMPLETED")}
{img("agent_activity","Figure 7 — Agent Activity: per-call mode and summaries")}

<h2>5. Tokenomics</h2>
{token_html}
<h3>Cost controls</h3>
<ul>
<li><code>MAX_AGENT_CALLS</code> (default 25) stops another completion. This measurement used 13 calls.</li>
<li><code>MAX_WORKFLOW_COST_USD</code> (default $2.00). This process cost about $0.0049.</li>
<li><code>LLM_MODE=demo</code> spends nothing and stores no token counts. <code>INTEGRATION_MODE=simulated</code> keeps email, purchases, and insurers off even when the model is live.</li>
<li><code>REVIEW_ALL</code> blocks F03 until the checkbox is approved.</li>
<li>Scores, the portfolio, dinner arithmetic, make-or-buy, the scheduler, and the quality checks do not call the model.</li>
</ul>

<h2>6. Safety</h2>
<h3>Threat model (selected)</h3>
<table>
<tr><th>Threat</th><th>Example</th><th>Built defense</th><th>Evidence</th></tr>
<tr><td>Prompt injection in intake</td><td>“Ignore previous instructions…”</td><td><code>guard_external_content</code> quarantine banner</td><td><code>tests/test_safety.py</code></td></tr>
<tr><td>Secret exfiltration into logs/UI</td><td><code>api_key=sk-…</code> in paste</td><td><code>scrub_secrets</code> → [REDACTED]</td><td>pytest + Settings screenshot</td></tr>
<tr><td>Agent claims external action</td><td>“I called the insurer”</td><td>F03 prompt + simulated insurer + no send APIs</td><td>BUILD_STATUS labels</td></tr>
<tr><td>Runaway spend</td><td>bug loops completions</td><td><code>BudgetExceeded</code></td><td><code>tests/test_permissions_budget.py</code></td></tr>
<tr><td>Unauthorized autonomous execution</td><td>REVIEW_ALL user</td><td>F03 skipped until approve flag</td><td>pytest</td></tr>
<tr><td>Privacy leak via calendar</td><td>claim ID in ICS DESCRIPTION</td><td>public_description only; tests assert no Photo ID in ICS</td><td><code>tests/test_intervention_fields.py</code></td></tr>
</table>
{img("safety","Figure 8 — Settings: permission mode selector and safety scan UI")}
<h3>Pytest output (safety + permissions)</h3>
<pre>{safety_esc}</pre>

<div class="pagebreak"></div>
<h2>7. Impact</h2>
<p><strong>No real pilot users were interviewed for this submission.</strong> Impact evidence is limited to builder-side measurements and structured comparisons.</p>
<h3>Manual baseline vs OUTSOURCE (same four-obligation scenario)</h3>
<table>
<tr><th>Dimension</th><th>Manual baseline (fictional Maya workflow)</th><th>OUTSOURCE demo run ({trace['workflow_id'][:12]}…)</th></tr>
<tr><td>Distinct planning artifacts</td><td>~15 ad-hoc steps / context switches</td><td>7 specialist calls + 1 fixture + 1 resume call = 8 logged agent steps</td></tr>
<tr><td>Structured work packages</td><td>None persisted</td><td>6 <code>WorkPackage</code> rows with assignee + status</td></tr>
<tr><td>Insurance completion without human</td><td>Often falsely assumed</td><td>Blocked at <code>WAITING_RESULT</code> until user_result</td></tr>
<tr><td>Calendar artifact</td><td>Ad hoc event text</td><td>ICS file + private brief separation</td></tr>
<tr><td>Follow-ups</td><td>Memory-dependent</td><td>3 explicit strings from F06 after resume</td></tr>
</table>
<h3>Extension modules (screenshots, honest labels)</h3>
<p><strong>Strategic Radar:</strong> the discovery feed and most graph nodes are <strong>Simulated</strong> illustrative fixtures. One <strong>VERIFIED_SOURCE</strong> edge records the Yale School of Management street address from the public About page; hypothetical warm-introduction paths render as dashed <em>HYPOTHETICAL</em> edges and are not shown as real relationships. Research-to-action can draft outreach (never sent), calendar ICS, a private brief, and follow-ups&mdash;<strong>Operational</strong> in demo with authorization gates. Background monitoring preferences save to SQLite but no scheduler runs (<strong>Planned</strong>).</p>
{img_media("radar_feed", "Figure 10 — Strategic Radar: illustrative discovery feed (SIMULATED_FIXTURE)")}
{img_media("radar_network_graph", "Figure 11 — Network graph: one verified Yale SOM address; dashed hypothetical introduction paths")}
<p><strong>Contextual Opportunities:</strong> ORD layover feasibility rejects distant suburban tours and accepts a downtown MSI-style visit using buffer math in Python (<strong>Operational</strong>). The Boston conference scenario compares a 3-night baseline to a +1-day bundle; incremental cost <strong>$210</strong> and incremental time <strong>35 minutes</strong> are summed in <code>compare_bundles</code>, not asserted by the LLM. Scenario text is <strong>Simulated</strong>.</p>
{img_media("contextual_ord_layover", "Figure 12 — Contextual: ORD layover feasibility UI")}
{img_media("contextual_boston_bundle", "Figure 13 — Contextual: Boston bundle comparison (+$210, +35 min)")}
<p><strong>Opportunity Stacking:</strong> the comparison matrix uses illustrative rows only (not researched organizations). Deterministic code scores strong/moderate/limited contributions without double-counting overlapping benefits and downgrades board-seat career hype. Bundling 18 separate hours/month into one 6-hour commitment recovers <strong>144 hours/year</strong> (twelve months &times; twelve saved hours) <em>only if comparable benefits</em>&mdash;stated in UI. Life Dimension agents L01&ndash;L06 ran in <strong>demo</strong> fixtures for this submission.</p>
{img_media("stacking_matrix", "Figure 14 — Opportunity Stacking: illustrative comparison matrix")}
<p class="warn">Priority 0 hours-saved or revenue figures are still <em>not</em> claimed. Extension screenshots document structure and honesty labels, not pilot outcomes.</p>

<h2>8. Limits + next steps</h2>
<h3>Operational / Simulated / Planned</h3>
<table>
<tr><th>Component</th><th>Label</th></tr>
<tr><td>Priority 0 demo E2E, Blueprint CRUD, Decisions/Work/Attention/Calendar UI</td><td><strong>Operational</strong></td></tr>
<tr><td>Live model path (smoke, structured output, Priority 0, S01/D01/Q01)</td><td><strong>Operational</strong> — measured Nov 23, 7:28 PM ET; Section 5</td></tr>
<tr><td>Life Mandate edit, approval, revisions</td><td><strong>Operational</strong></td></tr>
<tr><td>Deterministic scores, portfolio, dinner periods, make-or-buy</td><td><strong>Operational</strong></td></tr>
<tr><td>Discovery dataset for the fictional executive</td><td><strong>Simulated</strong> — labeled records, not a live web fetch</td></tr>
<tr><td>Email, purchases, insurer submission</td><td><strong>Simulated</strong> — off even if INTEGRATION_MODE is set live</td></tr>
<tr><td>Strategic Radar discovery feed &amp; illustrative graph</td><td><strong>Simulated</strong></td></tr>
<tr><td>Strategic Radar research-to-action (draft not sent, ICS, brief)</td><td><strong>Operational</strong></td></tr>
<tr><td>Strategic Radar background monitoring</td><td><strong>Planned</strong></td></tr>
<tr><td>Contextual layover feasibility &amp; Boston bundling math</td><td><strong>Operational</strong></td></tr>
<tr><td>Contextual scenario narratives</td><td><strong>Simulated</strong></td></tr>
<tr><td>Opportunity Stacking matrix &amp; L01&ndash;L06 in submission</td><td><strong>Simulated</strong> (demo fixtures)</td></tr>
<tr><td>Opportunity Stacking hours / scoring engine</td><td><strong>Operational</strong></td></tr>
<tr><td>Insurer portal, People CRM email</td><td><strong>Simulated</strong></td></tr>
<tr><td>Finance projection</td><td><strong>Simulated</strong> (deterministic)</td></tr>
<tr><td>My Career module, CUSTOM_AUTONOMY allowlist</td><td><strong>Planned</strong></td></tr>
</table>
<h3>What teaching staff should expect when grading</h3>
<p>Clone <a href="{repo}">{repo}</a> (branch <strong>main</strong>), run <code>APP_MODE=demo streamlit run app.py</code>, and walk Daily Briefing, Life Mandate, Strategic Radar, Contextual Opportunities, and Opportunity Stacking. Demo Agent Activity shows UNKNOWN cost. The live token log is <code>audit/LIVE_TOKEN_USAGE.csv</code>. Staff should not expect sent email, a live insurer, a web search, or a running radar scheduler. Background monitoring, a full cabinet, and live purchases are <strong>Planned</strong> and were not built.</p>
<h3>One-month roadmap (if continued)</h3>
<ol>
<li>Cap per-agent output and re-measure Priority 0 live cost.</li>
<li>Calendar OAuth read-only; radar background jobs; nonprofit research with public sources only.</li>
</ol>
<p class="small">Public repo · {repo}</p>
</body></html>"""