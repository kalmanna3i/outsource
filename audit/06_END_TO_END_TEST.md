---
cursor:
  subagentId: "bc-a8420708-ef01-52b9-9382-dfd4f0aa4511"
---

# 22-step end-to-end test

The repo has no document titled “22-step scenario.” The steps below are the Priority 0 path in `services/workflow.py`, driven by `sample_data/demo_request.txt`, which is the same sentence as the Daily Briefing default and `tests/test_workflow_demo.py`.

Method: a child process with `APP_MODE=demo` and blank `OPENAI_API_KEY`, `PORTKEY_API_KEY`, and `SEARCH_API_KEY`. `get_settings` was pointed at a temporary directory so `data/outsource.db` was not the target of this run. Clock frozen at `2026-11-23 09:30`. No network.

Result: **22 PASS, 0 FAIL, 0 BLOCKED.**

| Step | Result | Check | Evidence |
| --- | --- | --- | --- |
| 1 | PASS | Read the fixture request | 149 characters from `sample_data/demo_request.txt`; contains “MBA final” and “insurance claim” |
| 2 | PASS | Load blueprint goals | Four titles: Submit MGT 409 final; Attend close friend's wedding; Clear critical work obligation; Resolve insurance claim status |
| 3 | PASS | A01 intake call | `mode=demo`, `input_tokens` is None |
| 4 | PASS | A02 reads goals | Snapshot has 4 goals |
| 5 | PASS | Constraints captured | 4 constraints on the decision plan |
| 6 | PASS | Alternatives | 4 opportunity-cost options |
| 7 | PASS | Recommended flags | All 4 options have `recommended=True` because that is what `_demo_fixtures` contains |
| 8 | PASS | Recommended sequence | 6 steps |
| 9 | PASS | Decomposition | 6 work packages including AI and HUMAN |
| 10 | PASS | Managed autonomy allows F03 | F03 is in the call list |
| 11 | PASS | Digital deliverables | 4 strings appended |
| 12 | PASS | Simulated insurer barrier | Evidence source `simulated://insurer-portal/identity-gate`, type `SIMULATED_FIXTURE` |
| 13 | PASS | Intervention brief | Status `WAITING_RESULT`, `sensitive=True`, brief, talking points, and documents present |
| 14 | PASS | Slot does not overlap the wedding | Admin `2026-11-23T09:45:00`–`10:15:00`; wedding `16:00:00`–`20:00:00` |
| 15 | PASS | ICS written | 366 bytes, `BEGIN:VCALENDAR` and `END:VEVENT` |
| 16 | PASS | ICS stays public | File text has neither `Photo ID` nor `CLAIM-SIM-409`; it does contain “private brief” |
| 17 | PASS | Waiting for the user | Status `WAITING_RESULT` before resume |
| 18 | PASS | Accept a result | Pasted “Verified identity. Claim under review; upload EOB within 14 days.” Intervention status `RESOLVED` |
| 19 | PASS | Resume | Status `COMPLETED` |
| 20 | PASS | Follow-ups | F06 present and 3 follow-up strings |
| 21 | PASS | Eight demo calls | Order `A01,A02,B01,F02,F03,F05,F04,F06`; every call `success`, `mode=demo`, `cost_usd` None |
| 22 | PASS | Transition log | `ANALYZING > PLANNED > EXECUTING > BLOCKED_HUMAN > WAITING_RESULT > RESUMING > COMPLETED` |

## Adjacent checks in the same process (not part of the 22)

| Check | Result |
| --- | --- |
| REVIEW_ALL | Status `PLANNED`. Calls `A01,A02,B01,F02`. F03 absent. |
| Radar discover | 8 calls `R01`–`R08`, 7 opportunities, mode demo, evidence only `SIMULATED_FIXTURE` |
| Radar execute | Calls `F03,F04,F05,F06`, ICS written, `outreach_sent` false, draft `DRAFT_NOT_SENT` |
| ORD layover | Feasible museum-style option and infeasible suburban option. Calls `C01,C02` |
| Boston bundle | Incremental cost 210.0 and time 35 minutes. Calls `C01,C02`. Scout payload is not what builds the opportunity (see feature FEAT-35). |
| Six strategists | `L01`–`L06`, all demo, tokens None |
| Stacking bundle | Chosen label `Illustrative — Infrastructure nonprofit board` |
| Hours example | 12.0 hours/month saved, 144.0 hours/year |
| Safety canary | Cleaned text had no `sk-` prefix. Finding kinds: prompt injection heuristic and secret-like content |

## Not run

- Live `APP_MODE=live` against either key.
- Browser clicks on “Run Priority 0 workflow” or “Submit result & resume.” The engine was called in-process instead. AppTest only proved the pages render.
- A fresh virtualenv install.
