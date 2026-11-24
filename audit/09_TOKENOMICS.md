---
cursor:
  subagentId: "bc-a8420708-ef01-52b9-9382-dfd4f0aa4511"
---

# Tokenomics

## What this audit measured

The fixture Priority 0 run, including resume, made 8 `complete()` calls. Each record had `input_tokens=None`, `output_tokens=None`, `cost_usd=None`, `cost_known=False`, `mode=demo`. Radar (8), radar execute (4), contextual (2+2), and strategists (6) were the same. `LLMClient` does not add cost in the demo branch. Agent Activity is written to show UNKNOWN in that case (`app.py` `page_activity`).

No live usage was collected. A live call would have spent a key that is present on this Mac. That was out of scope.

## Price table in code

`core/llm.py` `_EST_PRICE_PER_1M` for `gpt-6-luna`: input 0.10, cached input 0.01, cache write 0.125, output 0.50, per 1M tokens. `gpt-4o-mini`, `gpt-4o`, and `gpt-5.1-codex` have input/output rates only. Any other model returns cost `None` and `cost_known=False` (`tests/test_pricing.py` passed).

Demo mode never uses this table. The comment above the table says prices are estimates and must not be invented as measured demo costs.

## What the report claims, and what was checked without calling the API

`deliverables/report.html` section 5, text extracted with tags and images stripped, says one live Priority 0 run on 23 Nov 2026 at 5:37 PM ET used `gpt-6-luna` on the OpenAI API, workflow id `wf_f56cc5c696df`, 8 calls:

| Agent | Input | Cached | Output | Cost in the HTML |
| --- | --- | --- | --- | --- |
| A01 | 152 | 0 | 757 | 0.000394 |
| A02 | 1005 | 0 | 990 | 0.000596 |
| B01 | 877 | 0 | 1220 | 0.000698 |
| F02 | 890 | 0 | 842 | 0.000510 |
| F03 | 196 | 0 | 177 | 0.000108 |
| F05 | 138 | 0 | 355 | 0.000191 |
| F04 | 125 | 0 | 422 | 0.000224 |
| F06 | 900 | 0 | 624 | 0.000402 |
| Total stated | 4283 | 0 | 5387 | 0.003122 |

Input figures sum to 4283. Output figures sum to 5387. Those two sums match the HTML total.

Aggregate formula with the code prices and zero cached tokens:

`(4283/1e6)*0.10 + (5387/1e6)*0.50 = 0.0031218`, which rounds to **$0.003122**.

The eight printed row costs sum to **$0.003123**. That is rounding of the row display, not a second measurement.

Scale lines in the same section use R = 20, an assumption stated as such. `20 * 0.0031218 * 10000 = 624.36`, which is the “10,000 users” cell. The “one run” cell is shown as $0.00312. The HTML says radar, contextual, and stacking were not part of this live measurement.

`BUILD_STATUS.md` repeats the same 4,283 / 0 / 5,387 / $0.003122 / 49.1s sentence. There is no JSON usage log, no saved API response, and no workflow row with that id in the local database (the stored workflow id observed after the incident was `wf_251bbe49978e`). An embedded screenshot is inside `report.html` and `slides.html`. This audit did not OCR it. The arithmetic is consistent with the price table. The provider usage itself was not reproduced.

## Caps

Defaults in `.env.example` and `get_settings`: `MAX_AGENT_CALLS=25`, `MAX_WORKFLOW_COST_USD=2.00`. The call cap increments on demo calls too. The dollar cap only moves when a live call returns a known cost. A model absent from the price dict would not increase `total_cost_usd`.

## Cost of the extensions if they were live

Not measured. Code path count if someone ran all three engines once in live mode: 8 (Priority 0 with resume) + 8 (radar discover) + 4 (one radar execute) + 4 (two contextual scenarios) + 6 (strategists) = 30 `complete()` calls, which is above the default cap of 25, so a single combined live pass would raise `BudgetExceeded` partway through unless the cap were raised. That is a reading of the cap plus the call sites, not a timed experiment.
