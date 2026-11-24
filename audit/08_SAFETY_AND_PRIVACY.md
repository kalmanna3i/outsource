---
cursor:
  subagentId: "bc-a8420708-ef01-52b9-9382-dfd4f0aa4511"
---

# Safety and privacy

## Credentials

| Location | What was checked | Result |
| --- | --- | --- |
| `/Users/kalmannai/Desktop/AI/outsource/.env` | File exists? | No |
| `~/Desktop/AI/.env` | Key names and set/unset only | `PORTKEY_API_KEY` SET, `PORTKEY_PROVIDER` SET, `OPENAI_API_KEY` SET, `APP_MODE` SET to `demo`, `OPENAI_MODEL` SET to `gpt-6-luna` |
| `~/Desktop/AI/submissions/.env` | Course layout path from the README | File absent |
| Process environment at audit start | Names only | `PORTKEY_API_KEY` SET. `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL`, `SEARCH_API_KEY` absent |
| Git tracked names | `git ls-files` filtered for env/secret/key | Only `.env.example` and `tests/test_env_paths.py` |
| Source scan | `sk-` of 20+ characters, outside `.venv` and `data/` | Only `tests/test_safety.py` lines that use `sk-abcdefghijklmnopqrstuvwxyz` as a redaction canary |
| `data/outsource.db` text | Patterns `sk-` (16+), `api_key=`, `password=`, `bearer` | 0 hits across 6 scanned blobs before the radar-page incident |

No value from any of those files was printed. No completion request was sent.

`tests/test_env_paths.py` writes `PORTKEY_API_KEY=dummy-parent-key` inside a pytest temp directory and asserts the loader reads it. That string is a test dummy.

## Controls that ran

`core/safety.py` has three secret regexes (api key / secret / password / token assignments, `sk-` plus 10 alphanumerics, bearer tokens) and five injection regexes (ignore previous instructions, system prompt, exfiltrate, do not follow safety rules, reveal prompt). `guard_external_content` scrubs then prefixes a quarantine line when any pattern hits.

This audit passed one combined string through that function. The cleaned text did not contain `sk-`. Findings were `prompt_injection_heuristic` and `secret_like_content`. `tests/test_safety.py` passed in the 55-test run. The Daily Briefing page calls the same function on the text area before a run. It does not refuse to run; it shows a warning. The workflow still receives the original `user_request` argument from the text area (`app.py` `page_briefing`), so the quarantine string is not what the agents see. The warning is real. The substitution into the model payload is not.

`may_auto_execute` blocks F03 under REVIEW_ALL. The temp run confirmed the early return. `MAX_AGENT_CALLS` is enforced inside `complete()` even in demo; the cap test passed.

The insurer function cannot return a live claim status. Radar outreach models reject `outreach_sent=True` and draft status `SENT` (`tests/test_strategic_radar.py`). The temp package had `outreach_sent` false and status `DRAFT_NOT_SENT`.

ICS from the temp run omitted the photo-ID line and the claim reference that sit in the private brief.

## Privacy notes from this session

Opening Strategic Radar is not a read. `render_radar` calls `_run_discovery()` when `radar_run` is missing, and `discover` writes every opportunity into `radar_opportunities`. AppTest did that against the real `data/outsource.db` and the count went from 0 to 7. The rows were deleted and `VACUUM` was run so the table is empty again. Counts after that: blueprint 1, workflows 1, people 3, settings 1, radar 0, agent_activity 0. The workflow row’s `updated_at` was still `2026-11-23T23:28:50.858081Z` (6:28 PM ET). The file is smaller than before (61,440 bytes versus 73,728) because vacuum compacted free pages. No new file appeared under `data/ics/` after 6:40 PM ET.

Pasted human results are stored inside workflow JSON. The seed and the fixture request use fictional claim id `CLAIM-SIM-409` and fictional people. The blueprint display name is Kay Al Mannai, which is also hardcoded in `default_blueprint`.

## What is not a control

- Regex injection detection, not a model policy.
- No per-tool allowlist. CUSTOM_AUTONOMY does not change `may_auto_execute`.
- No rate limit beyond the two budget numbers, and the cost budget only accumulates on live calls that return a known price.
- Unknown model names produce `cost_known=False`, so a live model missing from `_EST_PRICE_PER_1M` would not trip `MAX_WORKFLOW_COST_USD`.
- `scrub_secrets` is applied to activity-log errors in the UI, not to the SQLite workflow blob.
