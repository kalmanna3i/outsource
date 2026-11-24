# Post-fix audit

Corrective pass on `main` after the read-only audit. Working Priority 0, radar, contextual, and stacking code was kept. This file records what was re-checked and what changed.

## Live model

One process on Nov 23, 2026 at 7:28 PM ET (America/New_York). Model `gpt-6-luna` on the OpenAI API. `LLM_MODE=live`. `INTEGRATION_MODE=simulated`. The call did not return 401.

| Item | Result |
| --- | --- |
| Calls | 13 |
| Input / cached / cache-write / output | 5487 / 0 / 1058 / 8712 |
| Sum of row costs | $0.004931 |
| Wall clock | 83.8 s |
| Model tool calls | 0 |
| Email sent / purchase | false / false |

The log is `audit/LIVE_TOKEN_USAGE.csv` and `audit/LIVE_AGENT_EXECUTION.json`. Price source is `core/llm.py` `_EST_PRICE_PER_1M` (Lecture 11 short-context rates), not a provider invoice. Cache-write tokens on A02 are inside the input count and billed at $0.125 per 1M, which is why the row sum is $0.004931 rather than the plain product $0.004905.

Runs in that process: smoke JSON, one structured-output call, Priority 0 `wf_1fb3c7f55ef2` through resume, and discovery S01 → D01 → Q01. The deterministic rank chose `infra-nonprofit`. The model chose `home-dinner`. Both ids are in the labeled dataset. The mission text was not rewritten.

## What changed

- `LLM_MODE` is separate from `INTEGRATION_MODE`. Email, purchases, and the insurer stay simulated. `external_actions_allowed` is false.
- Life Mandate is stored, edited, approved, and revised. Recommendations cite the approved revision. A later draft does not replace it until the user approves. Priority changes are an explicit approval and they change the discretionary pick.
- Strategic Radar no longer writes the database when the page is opened. Discovery runs from the button.
- The fictional executive path (infrastructure work, coursework, philanthropy, friendship, dog, home, a user-stated recovery block, travel that does not fit) uses three agents only: S01, D01, Q01. Scores, the portfolio, dinner periods, and make-or-buy are deterministic. Overlapping colleague credit is excluded from the philanthropic stack. Outreach is `DRAFT_NOT_SENT`. The ICS does not contain the private brief. An empty human result does not complete the run.
- AppTest clicks Run Priority 0, Submit result & resume, Run discovery now, Save draft, Approve mandate, and Update priorities. The saved mission is still there in a second session. Updating priorities to `infrastructure` shows the site seminar.

## Checks

- `APP_MODE=demo LLM_MODE=demo pytest -q tests/` → 68 passed.
- A fresh virtualenv from `requirements.txt` ran the same 68 tests.
- That clean interpreter loaded the parent `.env` (`OPENAI_API_KEY` and `PORTKEY_API_KEY` set, values not printed) and still reported sending as off.
- Screenshots: `media/postfix-briefing.png`, `postfix-workflow.png`, `postfix-mandate.png`, `postfix-discovery.png`.
- Report: 8 sections, 12 printed pages. Slides: 10 reveal.js sections.

## Not built

P2 live public search, network centrality, and a compounding ledger were not built. P3 (full cabinet, background monitor, live email, live purchases, mobile) was not built. The commercial product is not described as built.
