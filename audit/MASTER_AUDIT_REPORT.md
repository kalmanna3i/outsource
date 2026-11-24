---
cursor:
  subagentId: "bc-a8420708-ef01-52b9-9382-dfd4f0aa4511"
---

# OUTSOURCE master audit

Independent read-only audit of `/Users/kalmannai/Desktop/AI/outsource`. Date: 23 Nov 2026, America/New_York. Auditor process did not commit, push, or call a model API. Existing source, tests, deliverables, and env files were not edited. The local SQLite file was touched by a page render and then put back to the same row counts; see section 8.

## 1. Executive summary

Full text: `audit/01_EXECUTIVE_SUMMARY.md`. The ten points are repeated in section 14 so a reader of this file does not need to open the other one.

## 2. Repository inventory

Full text: `audit/02_REPOSITORY_INVENTORY.md`.

HEAD `cd54e49965690c3befb820ba4881063ca9a2d050` on `main`, pull already up to date. One dirty tracked file: `deliverables/report.pdf`. No repo `.env`. Parent `~/Desktop/AI/.env` holds the key names listed in section 8, with `APP_MODE=demo` and `OPENAI_MODEL=gpt-6-luna`. 7,771 Python lines. 66 tracked Python files.

## 3. Feature matrix

Full table: `audit/03_FEATURE_MATRIX.csv` (44 rows).

Counts from that file:

| Classification | Rows |
| --- | --- |
| WORKING | 23 |
| SIMULATED | 7 |
| PARTIALLY_IMPLEMENTED | 2 |
| NOT_IMPLEMENTED | 8 |
| NOT_TESTED | 4 |
| UI_ONLY | 0 |
| BROKEN | 0 |

UI_ONLY is unused because every named screen either calls real code or is recorded as NOT_IMPLEMENTED (a banner or a planned table). Pages that only display an empty session are still WORKING as views; AppTest rendered all 15.

## 4. Agent inventory

Full text: `audit/04_AGENT_INVENTORY.md`.

24 classes with `run()`. 24 use demo fixtures and skip HTTP. 24 have a live `chat.completions.create` path when their engine reaches them. This audit invoked all 24 on fixtures and made 0 live calls.

## 5. Test results

Command: `APP_MODE=demo .venv/bin/pytest -q tests/` from the repo root, using `.venv`.

Saved stdout and stderr: `audit/05_TEST_RESULTS.txt`.

**55 passed, 283 warnings, 5.35s.** Exit code 0. An earlier run the same evening was 55 passed, 283 warnings, 5.42s. The warnings are `datetime.utcnow()` deprecations in Pydantic defaults, `core/models.py`, `services/insurer.py`, and `services/radar.py`.

## 6. End-to-end test

Full text: `audit/06_END_TO_END_TEST.md`.

22 of 22 fixture steps PASS. 0 BLOCKED. Temp directory only. Final status COMPLETED. Call order A01, A02, B01, F02, F03, F05, F04, F06. Tokens and cost null. ICS public. REVIEW_ALL stopped before F03.

## 7. Architecture

Full text: `audit/07_ARCHITECTURE.md`.

Streamlit UI, three orchestrators, one LLM wrapper, SQLite, deterministic scheduler and money math beside fixture or model JSON. Agents have no tool schema. Search is configured and unused.

## 8. Safety and privacy

Full text: `audit/08_SAFETY_AND_PRIVACY.md`.

No secrets printed. Repo scan found only the alphabet canary in `tests/test_safety.py`. Database pattern scan was clean before the page render.

Incident: AppTest opened Strategic Radar, which auto-runs discovery and inserted 7 fixture rows. Those rows were deleted and the database vacuumed. Row counts match the pre-audit snapshot. File size went from 73,728 to 61,440 bytes. Workflow `updated_at` stayed `2026-11-23T23:28:50.858081Z`.

The briefing warning does not swap the scrubbed string into `run_priority0`.

## 9. Tokenomics

Full text: `audit/09_TOKENOMICS.md`.

Demo cost is unknown by construction. Report HTML claims 4,283 input, 0 cached, 5,387 output, $0.003122 on `gpt-6-luna`. Token sums check out. The price formula in `core/llm.py` yields $0.0031218. Row costs in the HTML sum to $0.003123. The live call was not repeated. No usage log is in the tree.

## 10. Academic readiness

Full text: `audit/10_ACADEMIC_READINESS.md`.

The course page was fetched. Report headings 1–8 and a 10-section reveal.js deck exist. Parent env loading is implemented and unit-tested with a dummy. Fresh install, printed page count, slide arrow keys, and collaborator `zlisto` were not checked. No demo video in the repo.

## 11. Prioritized gaps

Full text: `audit/11_PRIORITIZED_GAP_ANALYSIS.md`.

Highest: radar auto-persist, quarantine not applied to the workflow string, live usage not stored as data, no external tools, CUSTOM_AUTONOMY alias, goals not editable, Boston scout payload dropped, cost cap blind to unknown models.

## 12. Review package

`PROJECT_REVIEW_PACKAGE.zip` is built from the repo root after these audit files exist. Exclusions: `.git`, `.venv`, `__pycache__`, `.pytest_cache`, `.mypy_cache`, `.env`, `data/*.db`, `data/ics`, `*.ics`, `.DS_Store`, and the zip itself. The zip listing is grepped for `sk-`, `api_key`, `password`, and `token`. A content scan is recorded in the same step. The alphabet canary in `tests/test_safety.py` is a test fixture, not a credential, and stays in the zip so the safety test still matches the repo.

## 13. Limits

- Browser buttons for Run workflow, Submit result, Run discovery, and Run strategists were not clicked. Engines were called in-process, and AppTest only changed the sidebar radio.
- Live mode was not run.
- `som.yale.edu` was not fetched, so the graph’s VERIFIED citation was not re-checked.
- `deliverables/report.html` sections other than the tokenomics extract and the eight headings were not audited sentence by sentence.
- The database file bytes are not identical to the pre-audit file because of the vacuum in section 8. Logical counts of the six tables match.
- README and BUILD_STATUS were read and not used as measurements.

## 14. Ten-point summary

1. **Checkout.** `main` at `cd54e49965690c3befb820ba4881063ca9a2d050`. Fast-forward pull already up to date. Dirty file: `deliverables/report.pdf` (1,139,083 bytes in git, 2,300,418 on disk). No commit.

2. **Tests.** `APP_MODE=demo pytest -q tests/` → **55 passed, 283 warnings, 5.35s** in `audit/05_TEST_RESULTS.txt`. Warnings are `datetime.utcnow()` on Python 3.14.7.

3. **App start.** Streamlit on `127.0.0.1:18711` reached “You can now view,” health HTTP 200, then stopped. AppTest rendered all 15 sidebar pages with no exception. Opening Strategic Radar inserted 7 fixture rows; they were deleted and the DB vacuumed. Other table counts are unchanged. Workflow buttons were not clicked.

4. **22-step fixture path.** 22/22 PASS in a temp directory. Status `COMPLETED`. Calls `A01, A02, B01, F02, F03, F05, F04, F06`, all demo, tokens and cost null. ICS omitted `Photo ID` and `CLAIM-SIM-409`.

5. **Agents.** 24 classes with a real `run()` path. Demo: 0 model calls. Live code: those 24 call `chat.completions.create` when reached with a key. This audit made 0 live calls. No G-department class.

6. **What ran.** State machine, REVIEW_ALL stop after F02, a non-overlapping 09:45 slot, ICS, simulated identity wall, secret redaction, stacking 144 hours/year, Boston +$210 and +35 minutes, ORD feasible plus infeasible, radar draft `DRAFT_NOT_SENT`.

7. **Simulated or missing.** Insurer, CRM, radar copy, contextual scenarios, and L01–L06 text are fixtures. No search, LinkedIn, email, SMS, purchase, or live insurer client. Career and three “planned” engines are labels. Background monitoring cannot be Operational. CUSTOM_AUTONOMY matches MANAGED_AUTONOMY. Goals are not editable.

8. **Secrets.** No repo `.env`. Parent `~/Desktop/AI/.env` has `PORTKEY_API_KEY`, `PORTKEY_PROVIDER`, `OPENAI_API_KEY`, `APP_MODE=demo`, `OPENAI_MODEL=gpt-6-luna` set. The process also had `PORTKEY_API_KEY` set. Values were not printed. DB had no secret-like patterns. The only long `sk-` source string is the safety-test canary.

9. **Tokenomics.** Demo cost is UNKNOWN in code. The report claims 4,283 / 0 / 5,387 tokens and about $0.00312. Arithmetic matches `core/llm.py`. The live call was not repeated and no usage log is in the repo. Radar, contextual, and stacking are outside that claim.

10. **Course package.** Requirements page fetched (due 23 Nov 2026, 11:59 PM ET). `report.html` has sections 1–8. `slides.html` has 10 sections and loads reveal.js from a CDN. Parent `.env` loading is implemented. Fresh `pip install`, printed page count, and a demo video in this repo were not verified.
