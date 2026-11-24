# Live workflow results

Measured 2026-11-23T19:28:11-05:00 (America/New_York).
Model `gpt-6-luna`. LLM_MODE=live. INTEGRATION_MODE=simulated. Email, purchases, and the insurer were not live.
Calls: 13. Input tokens: 5487. Cached input: 0. Cache-write tokens: 1058 (A02 only; already inside the input count, priced at $0.125 per 1M). Output tokens: 8712.
Estimated cost: $0.004931, the sum of the CSV row costs. A plain input-plus-output product is $0.004905. Wall clock: 83.8 s.

Price source:

Estimate from core/llm.py _EST_PRICE_PER_1M, not a provider invoice. gpt-6-luna uses OpenAI Standard short-context prices from MGT 409 Lecture 11: input $0.10, cached input $0.01, cache write $0.125, output $0.50 per 1M tokens. Other named models use the input/output rates in the same table.

Tool calls on the model: 0. The insurer check is a simulated Python function, not a model tool.

## Runs

- Smoke JSON ok=true. Run id smoke.
- Structured output required keys agent, run_kind, note.
- Priority 0 workflow `wf_1fb3c7f55ef2` status COMPLETED. Agents: A01, A02, B01, F02, F03, F05, F04, F06. Handoffs follow A01→A02→B01→F02→F03→F05→F04, then F06 after the human result.
- Discovery run `discovery` agents S01→D01→Q01. Deterministic pick `infra-nonprofit`. Model pick `home-dinner` (valid=True).
- Outreach sent: False. Purchase: False. Mission unchanged: True.

No token number in this file was typed in by hand. Totals are the sum of LIVE_TOKEN_USAGE.csv.
