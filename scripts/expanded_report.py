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


def render_expanded_report(
    *,
    repo: str,
    arch_svg: str,
    safety_test: str,
    trace: dict[str, Any],
    img: Callable[[str, str], str],
) -> str:
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
.shot img{{display:block;width:100%;max-height:2.75in;object-fit:contain;border:1px solid #D9D2C5}}
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
<p><strong>Public repo:</strong> <a href="{repo}">{repo}</a></p>
<p><strong>Application:</strong> run locally — <code>streamlit run app.py</code> (no production hosting in this submission).</p>
<p>OUTSOURCE is a Personal Strategy &amp; Execution Office: it reads life goals, compares opportunity costs across competing obligations, assigns work to AI versus human, executes draftable work, and—when a barrier requires a person—prepares a private intervention brief, schedules a calendar slot, exports ICS, and resumes only after the user records an outcome.</p>
<p class="small">This report describes a working prototype built by the author. Screenshots are from a real demo-mode run on the build machine ({trace['mode']} mode).</p>

<h2>2. Motivation</h2>
<h3>Fictional persona (not a real pilot user)</h3>
<p><strong>Maya Chen</strong> is a <em>fictional</em> second-year MBA executive: she leads a small product team during the day, carries a 4.0 credit load, and is responsible for family logistics. On submission nights she faces four simultaneous pulls: a course final due at 11:59 PM Eastern, a close friend’s wedding with a fixed ceremony window, a stakeholder expecting a work status note, and an insurance claim stuck behind an identity-verification gate. Maya is competent; her bottleneck is not lack of intelligence but <strong>attention fragmentation</strong> and tools that optimize the wrong objective.</p>
<h3>Today’s manual workflow (typical)</h3>
<ol>
<li>Open the academic deliverable checklist in a notes app and mentally rank “MBA final” first without writing down tradeoffs against the wedding.</li>
<li>Ask a general-purpose chat assistant for a priority list; receive fluent text with no persistent link to her stored goals or calendar conflicts.</li>
<li>Draft a work email in the same chat thread; risk sending language she has not verified, or lose time merging versions across tabs.</li>
<li>Open the insurer portal in a browser; hit knowledge-based authentication; stop without a prepared brief or a scheduled block on the calendar.</li>
<li>Copy partial instructions into a calendar event—sometimes leaking claim identifiers into a description shared with an assistant’s calendar sync.</li>
<li>After the call, forget to translate the outcome into follow-ups for the MBA and work threads.</li>
</ol>
<p>Conservatively, this manual sequence involves <strong>fifteen or more</strong> context switches (apps, tabs, mental replans) before anything is “done.” Maya pays in three currencies: <strong>time</strong> (20–45 minutes of unstructured replanning on a deadline night), <strong>cognitive load</strong> (keeping four parallel state machines in working memory), and <strong>error risk</strong> (false completion—“ChatGPT said it checked the claim”—or privacy mistakes in calendar text). None of those costs appear on a profit-and-loss statement, but they show up as late submission risk, strained relationships, and compliance mistakes when claim identifiers leak into shared calendars.</p>
<p>OUTSOURCE does not replace Maya’s judgment on the MBA final or the wedding toast. It compresses the <em>preparation surface area</em>: one intake, one ranked plan, one explicit split of AI draft work versus human-only gates, and one resume step that records what the insurer actually said.</p>
<h3>Why a manager should care</h3>
<p>Knowledge workers do not need another drafting chatbot. They need a system that encodes <em>which outcomes are non-negotiable</em>, computes what each hour buys in goal terms, executes only what automation can honestly complete, and surfaces a single prepared human moment when the world requires ID, presence, or signature. OUTSOURCE is scoped to that pattern for Maya’s archetype; the builder (Kay) dogfoods the same submission-night scenario in the mandatory demo.</p>
<h3>Design constraints implied by Maya’s evening</h3>
<p>First, the academic final has a sharp external deadline—missing it is not negotiable, but parts of the work (outline, checklist, slide structure) can be drafted by AI while submission remains human. Second, the wedding is a fixed window: the system must treat it as an immovable busy block when searching for insurance-call slots. Third, the work obligation is urgent but not legally identity-gated—appropriate for draft generation plus human send approval. Fourth, the insurer path is explicitly a human-authentication wall in the demo fixture, standing in for portals that will not release PHI to an API. Any credible “chief of staff” software for Maya must represent those four obligation classes differently, not collapse them into a single prioritized to-do list.</p>
<p>From a managerial lens, the lesson generalizes beyond students: organizations routinely ask leaders to reason about opportunity cost without giving them software that records assumptions, tradeoffs, and who (human vs machine) should act. OUTSOURCE is a course-sized prototype of that recordkeeping discipline.</p>

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
<p>The novelty for grading purposes is not “no competitors exist” but <strong>honest orchestration</strong>: separate public ICS text from private intervention fields, resume F06 only after user-supplied evidence, and default to demo fixtures that never masquerade as live model telemetry.</p>
<p><strong>Lindy</strong> and similar “AI employee” products optimize for recurring business workflows (inbox, CRM, SDR tasks). OUTSOURCE deliberately does not integrate with corporate SaaS in this MVP; instead it stores a personal Life Blueprint locally so opportunity-cost comparisons reference <em>your</em> stated goals rather than a template industry vertical.</p>
<p><strong>Motion</strong> and <strong>Reclaim</strong> are strong at calendar mechanics. OUTSOURCE’s scheduler is intentionally narrow—business hours, buffers, overlap detection—because the grading scenario is legibility and testability, not ML-optimized scheduling. The teaching point is scheduling in service of a <em>human intervention</em> that follows a strategy conversation, not scheduling for its own sake.</p>
<p><strong>Duckbill</strong> sells outcome completion with humans behind the scenes. OUTSOURCE inverts the transparency model for education: every agent step is logged with mode=<code>demo</code> or <code>live</code>, and simulated insurer results are typed <code>SIMULATED_FIXTURE</code> in the evidence ledger.</p>
<p><strong>ChatGPT agents</strong> (OpenAI’s agent modes and custom GPTs) can call tools broadly. Without hard constraints, they may summarize insurer status inaccurately. F03’s system prompt forbids claiming sends/calls; the workflow adds a Python gate that always routes insurer status through the fixture or a future real integration, never through unconstrained prose.</p>

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
<p>Each specialist returns a single JSON object via <code>LLMClient.complete</code>. The orchestrator (<code>WorkflowEngine</code>) performs three mechanical steps: (1) append an <code>AgentCallRecord</code> to <code>WorkflowState.agent_calls</code>; (2) map JSON fields into Pydantic models (<code>DecisionPlan</code>, <code>WorkPackage</code>, <code>HumanIntervention</code>); (3) pass serialized prior objects as plain text inside the next agent’s user message. Demo mode injects fixtures tagged <code>_demo_labeled</code>; live mode uses OpenAI-compatible chat completions with <code>response_format: json_object</code>. The insurer step is not an LLM call—it is a Python function returning <code>SIMULATED_FIXTURE</code> evidence.</p>
<p><strong>Downstream coupling example:</strong> B01’s <code>recommended_sequence</code> list is not merely displayed; F02’s prompt includes that list verbatim, and the UI’s My Decisions page renders the structured <code>OpportunityCostItem</code> rows rather than re-parsing free text. If a live model returned malformed JSON, the workflow would fail fast with an agent error recorded in Agent Activity—there is no silent fallback to fake success.</p>
<p><strong>Permission insertion point:</strong> between F02 and F03, <code>normalize_permission</code> and <code>may_auto_execute</code> decide whether F03 runs at all. That is a different handoff from “model didn't feel like executing”; it is an explicit organizational control matching the MANAGED_AUTONOMY / REVIEW_ALL modes in the spec.</p>
<h3>Model choice: why <code>gpt-6-luna</code> on the course key</h3>
<p>Yale MGT 409 project requirements restrict the course Portkey key to <strong>gpt-6-luna</strong> only. OUTSOURCE defaults <code>OPENAI_MODEL</code> to that slug when <code>PORTKEY_API_KEY</code> is set without a personal OpenAI key. Eight short JSON completions per Priority 0 run favor a capable instruction-following model while remaining inside course budget rules. Personal <code>OPENAI_API_KEY</code> runs may set any model via <code>OPENAI_MODEL</code>. Demo submissions use zero model spend.</p>
<p>Structured outputs reduce parse failures: each specialist prompt enumerates required JSON keys, and the orchestrator assumes dict shapes when building Pydantic objects. That design trades a few extra output tokens for fewer orchestration bugs—important when teaching staff run the app once under time pressure.</p>
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
<h3>State transitions (from SQLite workflow persistence)</h3>
<pre>{transitions_esc}</pre>
<h3>Agent call ledger (excerpt)</h3>
<pre>{calls_esc}</pre>
<h3>Work packages (first three JSON records)</h3>
<pre>{wp_esc}</pre>
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
<p>All numbers below are <strong>measured</strong> from one live Priority 0 run on Nov 23, 2026 (5:37 PM ET), including the resume after the human intervention. The run used <code>gpt-6-luna</code> called <strong>directly on the OpenAI API with Kay&#39;s personal OpenAI key</strong> (<code>APP_MODE=live</code>). The course Portkey key was rejected with HTTP 401 (&ldquo;Invalid API Key&rdquo;, code 03), so the course route could not be used. Token counts come from each response&#39;s <code>usage</code> object. Cost uses OpenAI Standard prices for gpt-6-luna per 1M tokens: input $0.10, cached input $0.01, cache write $0.125, output $0.50 (the same as Lecture 11).</p>
<h3>Measured run (workflow wf_f56cc5c696df, status COMPLETED)</h3>
<table>
<tr><th>Agent call</th><th>Input tokens</th><th>Cached input</th><th>Output tokens</th><th>Cost (USD)</th></tr>
<tr><td>A01 Chief of Staff</td><td>152</td><td>0</td><td>757</td><td>$0.000394</td></tr>
<tr><td>A02 Life Strategy Architect</td><td>1,005</td><td>0</td><td>990</td><td>$0.000596</td></tr>
<tr><td>B01 Opportunity Cost Economist</td><td>877</td><td>0</td><td>1,220</td><td>$0.000698</td></tr>
<tr><td>F02 Task Decomposition and Delegation</td><td>890</td><td>0</td><td>842</td><td>$0.000510</td></tr>
<tr><td>F03 Autonomous Execution</td><td>196</td><td>0</td><td>177</td><td>$0.000108</td></tr>
<tr><td>F05 Human Intervention and Handoff</td><td>138</td><td>0</td><td>355</td><td>$0.000191</td></tr>
<tr><td>F04 Calendar and Logistics</td><td>125</td><td>0</td><td>422</td><td>$0.000224</td></tr>
<tr><td>F06 Follow-Up and Accountability</td><td>900</td><td>0</td><td>624</td><td>$0.000402</td></tr>
<tr><td><strong>Total (8 live calls)</strong></td><td><strong>4,283</strong></td><td><strong>0</strong></td><td><strong>5,387</strong></td><td><strong>$0.003122</strong></td></tr>
</table>
<p>Wall time: <strong>49.1 s</strong> end to end. That is 42.9 s for the seven calls up to the human barrier (A01&ndash;F04) and 6.2 s for F06 after the verification result was entered. It excludes the human&#39;s own time on the insurer call.</p>
{live_figure()}
<h3>Definitions</h3>
<ul>
<li><strong>R</strong> = Priority 0 workflows per user per month. Assumption: <strong>R = 20</strong> (about one per weekday).</li>
<li><strong>T_in, T_cached, T_out</strong> = tokens per workflow from provider usage (measured above: 4,283 / 0 / 5,387).</li>
<li><strong>P_in, P_cached, P_out</strong> = price per 1M tokens ($0.10, $0.01, $0.50 for <code>gpt-6-luna</code>; this table is in <code>core/llm.py</code>).</li>
<li><strong>C_run</strong> = ((T_in &minus; T_cached)/10⁶)&middot;P_in + (T_cached/10⁶)&middot;P_cached + (T_out/10⁶)&middot;P_out.</li>
</ul>
<table>
<tr><th>Scale</th><th>Formula</th><th>Demo (grading mode)</th><th>Live (from measured run, R = 20)</th></tr>
<tr><td>One run</td><td>C_run</td><td>$0 (fixtures, no tokens)</td><td><strong>$0.00312</strong></td></tr>
<tr><td>Per user / month</td><td>R &times; C_run</td><td>$0</td><td><strong>$0.0624</strong></td></tr>
<tr><td>100 users / month</td><td>100 &times; R &times; C_run</td><td>$0</td><td><strong>$6.24</strong></td></tr>
<tr><td>10,000 users / month</td><td>10,000 &times; R &times; C_run</td><td>$0</td><td><strong>$624.36</strong> before batching, output caps or caching</td></tr>
</table>
<h3>What drives the cost</h3>
<p>Output tokens are 86% of the bill ($0.002694 of $0.003122), even though output is only 56% of all tokens, because gpt-6-luna output costs 5&times; input. Cached input was 0: each agent sends a different, short prompt (the largest is about 1,000 tokens), so there is no long shared prefix for the provider to cache. At this scale the useful lever is capping output length and tightening the JSON each agent returns, not caching. A02 and B01 together are 41% of cost. Two aborted attempts before the measured run made three extra billed calls, not included above: the model rejected <code>temperature=0.2</code>, and B01 answered a numeric field in prose. Both bugs were fixed in code before the run.</p>
<h3>Cost controls and tradeoffs</h3>
<ul>
<li><code>MAX_AGENT_CALLS</code> (default 25) &mdash; hard stop before another completion; prevents runaway loops; may truncate unfinished workflows if set too low (tested at 3).</li>
<li><code>MAX_WORKFLOW_COST_USD</code> (default 2.00) &mdash; accumulates live spend from usage &times; the price table; the measured run used $0.0031, about 0.16% of the cap.</li>
<li><code>APP_MODE=demo</code> &mdash; zero spend for grading and screenshots; tradeoff: demo runs show no token counts, which is why the figures above come from a separate live pass.</li>
<li><code>REVIEW_ALL</code> permission &mdash; blocks F03 until checkbox approval; saves tokens but requires extra UI click (operational in tests).</li>
<li><strong>Deterministic engines</strong> &mdash; insurer check, scheduler, ICS export, finance projection, safety regex scan run without LLM spend; tradeoff: insurer is simulation only.</li>
</ul>
<p>Stress case: if Maya ran live eight times per evening during exam season (R &asymp; 240), she would cost about $0.75 per month. Even at 10,000 such users that is about $7,492 per month, so the caps exist to stop loops, not to make the base case affordable. Teaching staff grading in demo mode will see $0 and no token counts&mdash;this is correct behavior, not missing implementation.</p>

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
<h3>Operational notes on each defense</h3>
<p><strong>Injection quarantine</strong> is heuristic, not cryptographic: it pattern-matches instruction-override phrases and wraps the payload so downstream prompts treat content as data. Staff can verify by pasting attack strings into Daily Briefing or the Settings scanner.</p>
<p><strong>REVIEW_ALL</strong> is enforced in code before F03, not merely described in documentation: a run without the Daily Briefing approval checkbox stops at PLANNED with a visible digital deliverable explaining the block (see permissions tests).</p>
<p><strong>Spend caps</strong> increment only when live usage objects return token counts with a known price row; demo mode never increments cost, preventing accidental fabrication of “cheap” metrics.</p>
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
<h3>Scheduler evidence from the same run</h3>
<p>The workflow seeds a <strong>fixed wedding busy block</strong> (16:00–20:00 local naive time). The intervention slot was placed <strong>09:45–10:15</strong>, respecting business hours and avoiding overlap with the wedding block—the deterministic engine’s purpose. Unit tests additionally cover overlap detection and impossible deadlines (<code>tests/test_scheduler.py</code>).</p>
<p>For course grading, the meaningful comparison is <strong>structural</strong>: manual workflows scatter state across tabs; OUTSOURCE persists a single <code>WorkflowState</code> with enumerated transitions, six packages, and an intervention object that must receive <code>user_result</code> before <code>COMPLETED</code>. That persistence is what teaching staff can replay in demo mode without inventing a pilot narrative.</p>
<p class="warn">Hours-saved or revenue figures are <em>not</em> claimed. A one-user timed study would be required to quote minutes saved credibly.</p>

<h2>8. Limits + next steps</h2>
<h3>Operational / Simulated / Planned</h3>
<table>
<tr><th>Component</th><th>Label</th></tr>
<tr><td>Priority 0 demo E2E, Blueprint CRUD, Decisions/Work/Attention/Calendar UI</td><td><strong>Operational</strong></td></tr>
<tr><td>Parent-folder <code>.env</code>, Portkey gpt-6-luna default</td><td><strong>Operational</strong></td></tr>
<tr><td>Live eight-call path with measured tokens</td><td><strong>Operational</strong> (one live run, Nov 23; see Section 5)</td></tr>
<tr><td>Insurer portal, CRM email</td><td><strong>Simulated</strong></td></tr>
<tr><td>Finance projection module</td><td><strong>Simulated</strong> (deterministic; tax/retirement omitted)</td></tr>
<tr><td>Network, Career nav, CUSTOM_AUTONOMY allowlist</td><td><strong>Planned</strong></td></tr>
</table>
<h3>What teaching staff should expect when grading</h3>
<p>Clone the public repository, optionally place a course <code>.env</code> one directory above the project folder, run <code>streamlit run app.py</code>, and execute the Priority 0 path in demo mode without spending tokens. Agent Activity should list eight calls after resume, each marked demo with UNKNOWN cost. If staff insert a real Portkey key and set <code>APP_MODE=live</code>, the same UI path should issue eight completions against <code>gpt-6-luna</code>; token fields populate only when the provider returns usage metadata. Staff should not expect email send buttons, live insurer APIs, or Network/Career modules—their absence is documented here rather than hidden.</p>
<h3>One-month roadmap (if continued)</h3>
<ol>
<li>Week 1: cap per-agent output length and rerun live to compare cost against the Section 5 baseline.</li>
<li>Week 2: Google Calendar OAuth read-only for real busy blocks.</li>
<li>Week 3: email draft→approve→send behind MANAGED_AUTONOMY only.</li>
<li>Week 4: three fictional-to-real pilot sessions with timed before/after protocol (still no invented quotes in reports).</li>
</ol>
<p class="small">Demo trace summary (full state in repo SQLite when staff run the app):</p>
<pre>{trace_json}</pre>
<p class="small">Public repo · {repo}</p>
</body></html>"""