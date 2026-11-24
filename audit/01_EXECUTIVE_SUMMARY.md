---
cursor:
  subagentId: "bc-a8420708-ef01-52b9-9382-dfd4f0aa4511"
---

# OUTSOURCE audit — executive summary

Read-only audit of `/Users/kalmannai/Desktop/AI/outsource` on 23 Nov 2026 (America/New_York). Evidence is from the git checkout, source, pytest, a temp-directory fixture run, and a short Streamlit start. README and BUILD_STATUS claims are not treated as proof. No API call was made. No commit.

## Ten points

1. **Checkout.** Branch `main` at `cd54e49965690c3befb820ba4881063ca9a2d050`. `git pull --ff-only origin main` was already up to date. The only local modification of an existing file is `deliverables/report.pdf` (binary, 1,139,083 bytes in git to 2,300,418 bytes on disk). This audit did not commit or push.

2. **Tests.** `APP_MODE=demo .venv/bin/pytest -q tests/` passed **55** tests with **283** warnings. The saved run in `audit/05_TEST_RESULTS.txt` finished in **5.35s**. An earlier run in the same session was 55 passed, 283 warnings, 5.42s. Warnings are `datetime.utcnow()` deprecations on Python 3.14.7.

3. **Process start.** `APP_MODE=demo streamlit run app.py` on `127.0.0.1:18711` printed “You can now view your Streamlit app”, `/_stcore/health` returned 200, and the process was stopped. A Streamlit AppTest then rendered all 15 sidebar pages with no exception. Opening Strategic Radar auto-runs discovery (`ui/radar_page.py` lines 88–90) and inserted 7 fixture rows into `data/outsource.db`. Those rows were deleted and the file was vacuumed so `radar_opportunities` is empty again. Blueprint, workflow, people, settings, and agent_activity counts match the pre-audit snapshot (1, 1, 3, 1, 0). The database file size changed (73,728 → 86,016 → 61,440 bytes) because SQLite rewrote it. Workflow action buttons were not clicked.

4. **22-step fixture path.** All 22 steps passed in a temporary data directory using `sample_data/demo_request.txt`. Final status `COMPLETED`. Agent order `A01, A02, B01, F02, F03, F05, F04, F06`. Every call was `mode=demo` with `input_tokens=None` and `cost_usd=None`. The ICS file contained `BEGIN:VCALENDAR` and did not contain `Photo ID` or `CLAIM-SIM-409`.

5. **Agents.** 24 classes have a real `BaseAgent.run()` path: A01, A02, B01, F02, F03, F04, F05, F06, C01, C02, R01–R08, L01–L06. In demo mode, `LLMClient.complete` returns the fixture and does not construct an API client. In live mode the same 24 call `chat.completions.create` when their engine reaches `run()` and a key is present. This audit invoked all 24 on fixtures and made **0** live model calls. There is no G-department validator class.

6. **Executed behavior.** The temp run showed a real state machine (`ANALYZING` through `COMPLETED`), a REVIEW_ALL stop after F02 (no F03), a 09:45–10:15 slot that does not overlap the 16:00–20:00 wedding, an ICS file, a simulated identity wall, secret redaction, stacking math of 12 hours/month and 144 hours/year, a Boston bundle of +$210 and +35 minutes, an ORD layover with one feasible and one infeasible option, and a radar execution package whose draft status is `DRAFT_NOT_SENT` and `outreach_sent` is false.

7. **Simulated or absent.** Insurer, people CRM, radar lead text, contextual scenarios, and L01–L06 narratives are labeled fixtures. `SEARCH_API_KEY` is loaded in `core/config.py` and never read again. No email, SMS, purchase, LinkedIn, or live insurer client exists. My Career is a planned banner. Side Quest Engine, Focus Guardian, and Opportunity Portfolio Optimizer are a planned markdown table in `ui/contextual_page.py`. `RadarSchedule.background_monitoring_status` can only be `"Planned"`. `CUSTOM_AUTONOMY` uses the same gate as `MANAGED_AUTONOMY`. Goal rows on My Life Blueprint are displayed, not edited.

8. **Secrets and privacy.** The repo has no `.env`. `~/Desktop/AI/.env` exists; names set there are `PORTKEY_API_KEY`, `PORTKEY_PROVIDER`, `OPENAI_API_KEY`, `APP_MODE` (value `demo`), and `OPENAI_MODEL` (value `gpt-6-luna`). The audit process also had `PORTKEY_API_KEY` set. Values were not printed. A pattern scan of `data/outsource.db` found no `sk-` strings of length 16+, no `api_key=` assignments, no `password=` assignments, and no bearer tokens. The only `sk-` string in source is the unit-test canary `sk-abcdefghijklmnopqrstuvwxyz` in `tests/test_safety.py`.

9. **Tokenomics.** Demo calls record unknown tokens and unknown cost, which the Agent Activity page is written to display as UNKNOWN. `deliverables/report.html` section 5 claims one live Priority 0 run on 23 Nov 2026 at 5:37 PM ET: 4,283 input, 0 cached, 5,387 output, about $0.00312, model `gpt-6-luna`. Those token sums match the per-agent figures in that HTML, and the dollars match `core/llm.py` prices ($0.10 / $0.01 / $0.125 / $0.50 per 1M). This audit did not repeat the live call. The repo contains no raw usage log. Per-row costs in the HTML sum to $0.003123; the aggregate formula is $0.003122. Radar, contextual, and stacking are outside that claimed measurement.

10. **Course package.** The official requirements page `https://zlisto.github.io/mgt_409_fa26/project_requirements.html` was fetched. Due Monday 23 Nov 2026, 11:59 PM. It asks for a repo, `report.html` (sections 1–8), and `slides.html` (reveal.js, at most 10 slides), plus parent-folder `.env` loading and the key names `PORTKEY_API_KEY` and `OPENAI_API_KEY`. Those files and that loader exist (`core/config.py`, `tests/test_env_paths.py`). `slides.html` has 10 `<section>` elements and loads reveal.js from `cdn.jsdelivr.net`. A fresh clone plus `pip install` was not run. Printed page count was not measured. No demo video file is in this repo.
