# OUTSOURCE — BUILD STATUS

**Founder:** Kay Al Mannai · **Course:** Yale MGT 409 · **Updated:** 2026-11-23

Legend: **Operational** = works end-to-end in this repo · **Simulated** = labeled fixture / local-only · **Planned** = not implemented (not faked).

## Priority 0 (mandatory)

| Capability | Status | Notes |
|---|---|---|
| App launch (`streamlit run app.py`) | Operational | |
| Life Blueprint load/edit/save | Operational | SQLite |
| Universal task intake | Operational | Daily Briefing |
| A01 Chief of Staff | Operational | Own call in live; labeled fixture in demo |
| A02 Life Strategy Architect | Operational | Reads goals |
| B01 Opportunity Cost Economist | Operational | Options + tradeoffs |
| F02 Decomposition (AI vs human) | Operational | |
| F03 Autonomous Execution | Operational | Digital drafts only; no fake sends |
| Simulated insurer identity barrier | Simulated | `services/insurer.py` — clearly labeled |
| F05 Human intervention brief | Operational | Private brief separate from calendar |
| F04 Calendar + ICS export | Operational | Deterministic scheduler |
| Resume after user result + F06 | Operational | |
| Agent Activity + token/cost display | Operational | Live: measured/estimated; Demo: UNKNOWN |
| Safety guards + tests | Operational | Injection heuristic + secret scrub |
| Integration test (demo E2E) | Operational | `tests/test_workflow_demo.py` |

## Modules (nav)

| Module | Status |
|---|---|
| Daily Briefing | Operational |
| My Life Blueprint | Operational |
| My Decisions | Operational |
| My Work | Operational |
| My Attention | Operational |
| My Calendar | Operational |
| My People | Simulated (local CRM seed; no email) |
| My Network | Planned |
| My Career | Planned |
| My Financial Future | Simulated (deterministic projection; tax/retirement omitted) |
| Agent Activity | Operational |
| Settings | Operational |

## Modes

- `APP_MODE=demo` (default): labeled fixtures; **not** real model calls.
- `APP_MODE=live`: real OpenAI-compatible calls when `OPENAI_API_KEY` or `PORTKEY_API_KEY` is present; otherwise falls back to demo with a clear banner.

## What is intentionally not claimed

- No real insurer API, email send, phone call, or purchase.
- No invented token costs in demo mode.
- Career fork / live networking research not built.
