# OUTSOURCE — BUILD STATUS (submission)

**Public repo:** https://github.com/kalmanna3i/outsource  
**Kay Al Mannai · MGT 409 · Nov 23, 2026**

**Tests:** `APP_MODE=demo LLM_MODE=demo pytest -q tests/` → **68 passed**  
**Live tokens:** **Measured** Nov 23, 2026, 7:28 PM ET. `gpt-6-luna` on the OpenAI API. `LLM_MODE=live`, `INTEGRATION_MODE=simulated`. 13 calls · 5,487 input / 0 cached / 1,058 cache-write / 8,712 output · **$0.004931** summed from `audit/LIVE_TOKEN_USAGE.csv` · 83.8 s. Not a provider invoice. See Report §5.  
**Model vs score:** deterministic rank chose `infra-nonprofit`. The model chose `home-dinner`. Both are recorded. The mission was not rewritten.

| Area | Status |
|------|--------|
| Priority 0 workflow (demo) | **Operational** |
| Life Mandate (edit, approve, revisions, priority change) | **Operational** |
| Deterministic scores, portfolio, dinner periods, make-or-buy | **Operational** |
| Personal discovery S01 and quality auditor Q01 | **Operational** (live path measured; user can reject the note) |
| Discovery dataset for the fictional executive | **Simulated** (labeled records; model chooses an id; not live web) |
| Email, purchases, insurer submission | **Simulated** (stay off when the model is live) |
| Opportunity Stacking module | **Simulated** (fixtures + deterministic optimizer) |
| Life Dimension agents L01–L06 | **Simulated** (demo fixtures; live one-call each if API key) |
| Live multi-agent calls | **Operational** (measured Nov 23, 7:28 PM ET; 13 calls) |
| Insurer portal | **Simulated** |
| People CRM | **Simulated** |
| Finance projection | **Simulated** (deterministic) |
| Contextual Opportunity Engine | **Simulated** (SIMULATED_FIXTURE scenarios; deterministic feasibility + bundling) |
| Contextual feasibility / bundling | **Operational** (deterministic, unit-tested) |
| Contextual execution drafts (ICS, meeting, registration) | **Operational** (requires authorization; nothing sent/booked) |
| Strategic Radar (discovery feed, mission audit, network graph) | **Simulated** (illustrative `SIMULATED_FIXTURE`; no live search/LinkedIn wired) |
| Strategic Radar (research-to-action: draft, ICS, brief, follow-up) | **Operational** (demo; outreach never sent) |
| Strategic Radar background monitoring | **Planned** (schedule prefs saved; no running scheduler) |
| My Network graph | **Simulated** (illustrative graph; 1 VERIFIED public fact) |
| My Career | **Planned** |
| Side Quest Engine / Focus Guardian / Opportunity Portfolio Optimizer | **Planned** (integration panel only) |
| CUSTOM_AUTONOMY allowlist | **Planned** |
| Parent-folder `.env` + `gpt-6-luna` Portkey default | **Operational** (dry-run verified) |

**Contextual demo scenarios**
1. **5h ORD layover** — MSI-style downtown visit **feasible**; distant suburban plant tour **rejected** (distance / time).
2. **Boston conference** — original 3-night vs +1 day (lecture + meeting); incremental cost **$210** computed in code.

**Canvas upload:** `deliverables/report.html` + `deliverables/slides.html` only (self-contained). Repo code on GitHub.