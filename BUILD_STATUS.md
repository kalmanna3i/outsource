# OUTSOURCE — BUILD STATUS (QA-verified)

**Founder:** Kay Al Mannai · **Course:** Yale MGT 409  
**QA pass:** 2026-11-23 (America/New_York) · agent `bc-8509c433-0599-57fa-aeb0-26d5f7ddefda`  
**Tests:** `APP_MODE=demo pytest -q tests/` → **14 passed**  
**Live AI run:** **Not executed** — no `OPENAI_API_KEY` / `PORTKEY_API_KEY` in environment or `.env`.

Legend: **Operational** = verified working in this repo · **Simulated** = labeled fixture / local-only · **Planned** = not implemented · **Incomplete** = partially wired.

---

## Answers to the 15 review criteria

| # | Criterion | Finding |
|---|---|---|
| 1 | Genuinely operational | Priority 0 pipeline in demo: intake → A01–F05/F04 → ICS → resume → F06; Blueprint CRUD; Decisions/Work/Attention/Calendar views; scheduler; safety scrub; spend/call caps; REVIEW_ALL gate; Streamlit UI |
| 2 | Simulated | Insurer portal (`SIMULATED_FIXTURE`); CRM people seed (no email/SMS); demo agent fixtures; finance projection (tax/retirement omitted) |
| 3 | Incomplete | `CUSTOM_AUTONOMY` has no per-tool allowlist (behaves like MANAGED); live tokenomics unverified here; GitHub repo not pushed from this VM |
| 4 | Independent model calls | **Live path coded** in `core/llm.py` (one `chat.completions.create` per agent). **Demo path:** labeled fixtures, not model calls. Live not run this QA (no keys). |
| 5 | Prompts / placeholders only | Priority 0 agents A01,A02,B01,F02–F06 are real classes with prompts + `run()`. Network/Career nav pages are Planned stubs. No fake commercial A–G registry pretending to be operational. |
| 6 | Structured outputs → downstream | **Yes.** Orchestrator passes prior JSON into next prompts and builds `DecisionPlan` / `WorkPackage` / intervention from returned dicts (`services/workflow.py`). Demo fixtures are coherent by construction; live would use API JSON. |
| 7 | Financial calculations deterministic | **Yes.** `services/finance.py` `project_cashflow` is pure arithmetic; covered by `tests/test_finance.py`. |
| 8 | Scheduling vs deadlines/conflicts | **Yes.** `find_slot` respects busy blocks + buffer + business hours + deadline; `detect_impossible` tested. Wedding busy block avoided in E2E. |
| 9 | Human intervention required fields | **Yes.** title, why_human_required, prepared_brief, talking_points, documents_ready, status, sensitive, suggested_slot, ics_path — asserted in `tests/test_intervention_fields.py`. |
| 10 | Resume after human intervention | **Yes.** `resume_with_result` → F06 → COMPLETED; tested. |
| 11 | Research citations genuine | **No live research.** Evidence types observed in demo: `USER_PROVIDED`, `SIMULATED_FIXTURE` only. No `VERIFIED_SOURCE` citations produced. Do not claim web research. |
| 12 | Token usage / costs recorded | **Demo:** tokens/cost = `None` / UNKNOWN (correct). **Live:** records usage from API when present; USD estimate only if model is in a small price table — else UNKNOWN. Not measured this QA. |
| 13 | Permissions & safety | **Safety Operational** (injection heuristic + secret redaction + tests). **Permissions:** REVIEW_ALL now blocks F03 unless approved; MANAGED allows; CUSTOM = Planned (same as MANAGED). Caps: `MAX_AGENT_CALLS`, `MAX_WORKFLOW_COST_USD`. |
| 14 | UI polish / usable | Usable executive theme; mode pill; module status labels; ICS download; intervention brief. Not a design-system showcase; sufficient for staff walkthrough. |
| 15 | Setup reproducible | README + `.env.example` + parent `.env` load + `requirements.txt` + pytest. Verified: venv install, 14 tests, demo workflow, Streamlit HTTP 200 earlier this session. |

---

## Priority 0 checklist

| Capability | Status | Evidence |
|---|---|---|
| App launch | Operational | Streamlit 200 on :8501 (earlier run) |
| Life Blueprint | Operational | SQLite load/save |
| Task intake | Operational | Daily Briefing |
| A01–F06 agents (demo) | Operational (fixtures) | E2E test + manual demo |
| A01–F06 agents (live) | Incomplete / unverified | Code path exists; no keys this QA |
| Opportunity-cost plan | Operational | DecisionPlan from B01 output |
| AI vs human decomposition | Operational | F02 → WorkPackage |
| AI execution (digital only) | Operational | F03; no fake sends |
| Insurer identity barrier | Simulated | `services/insurer.py` |
| Human brief + ICS | Operational | Fields + ICS tests |
| Resume + follow-ups | Operational | F06 |
| Agent Activity display | Operational | Shows UNKNOWN in demo |
| Safety guards | Operational | `tests/test_safety.py` |
| Permission REVIEW_ALL | Operational | `tests/test_permissions_budget.py` |
| CUSTOM_AUTONOMY allowlist | Planned | — |

## Modules

| Module | Status |
|---|---|
| Daily Briefing | Operational |
| My Life Blueprint | Operational |
| My Decisions | Operational |
| My Work | Operational |
| My Attention | Operational |
| My Calendar | Operational |
| My People | Simulated |
| My Network | Planned |
| My Career | Planned |
| My Financial Future | Simulated (deterministic; simplifications labeled) |
| Agent Activity | Operational |
| Settings | Operational (mode + permissions + safety check) |

## Mandatory demo (demo mode) — verified this QA

Request: MBA final + wedding + work + insurance.  
Result: `WAITING_RESULT` → resume → `COMPLETED`. Agents: A01,A02,B01,F02,F03,F05,F04 (+F06). ICS written. Evidence types: USER_PROVIDED, SIMULATED_FIXTURE.

## Remaining submission risks

1. **No GitHub remote from this VM** — Canvas needs a repo URL; `gh` not authenticated.  
2. **No live tokenomics screenshot** — without keys, report cannot show measured tokens.  
3. **No real screenshots embedded** in HTML (text stand-ins only).  
4. **CUSTOM_AUTONOMY** unfinished.  
5. **No VERIFIED_SOURCE research** — do not imply web citations.  
6. Teaching staff must follow README with `.env` one folder up for live mode.
