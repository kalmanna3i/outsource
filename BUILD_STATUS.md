# OUTSOURCE — BUILD STATUS (contextual-engine branch)

**Public repo:** https://github.com/kalmanna3i/outsource  
**Kay Al Mannai · MGT 409 · Nov 23, 2026**

**Tests:** `APP_MODE=demo pytest -q tests/` → **31 passed** (19 baseline + 12 Contextual Opportunity Engine)

| Area | Status |
|------|--------|
| Priority 0 workflow (demo) | **Operational** |
| Live multi-agent calls | **Operational** (baseline on `main`) |
| Contextual Opportunity Engine | **Simulated** (SIMULATED_FIXTURE scenarios; deterministic feasibility + bundling) |
| Contextual feasibility / bundling | **Operational** (deterministic, unit-tested) |
| Contextual execution drafts (ICS, meeting, registration) | **Operational** (requires authorization; nothing sent/booked) |
| Strategic Radar | **On `strategic-radar` branch** (parallel worktree — not merged here) |
| Side Quest Engine / Focus Guardian / Opportunity Portfolio Optimizer | **Planned** (integration panel only) |

**Contextual demo scenarios**
1. **5h ORD layover** — MSI-style downtown visit **feasible**; distant suburban plant tour **rejected** (distance / time).
2. **Boston conference** — original 3-night vs +1 day (lecture + meeting); incremental cost **$210** computed in code.

**Merge note (shared files touched):** `app.py`, `ui/theme.py` only (additive nav + module status). All other contextual code in new files under `core/contextual_models.py`, `services/contextual/`, `agents/contextual_agents.py`, `agents/registry.py`, `ui/contextual_page.py`, `tests/test_contextual_*.py`.