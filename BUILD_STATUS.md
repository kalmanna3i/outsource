# OUTSOURCE — BUILD STATUS (submission)

**Public repo:** https://github.com/kalmanna3i/outsource  
**Kay Al Mannai · MGT 409 · Nov 23, 2026**

**Tests:** `APP_MODE=demo pytest -q tests/` → **44 passed** (Priority 0 + Contextual Opportunity Engine + Strategic Radar)  
**Demo:** Priority 0 E2E verified (demo fixtures + UI screenshots embedded in `deliverables/report.html` / `slides.html`)  
**Live tokens:** **Measured** Nov 23 (5:37 PM ET): one live run + resume on gpt-6-luna via OpenAI directly (course Portkey key returned 401 on that path). 8 calls · 4,283 input / 0 cached / 5,387 output tokens · $0.003122 · 49.1 s. See Report §5 and the Cost slide.

| Area | Status |
|------|--------|
| Priority 0 workflow (demo) | **Operational** |
| Live multi-agent calls | **Operational** (one measured live run, Nov 23) |
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