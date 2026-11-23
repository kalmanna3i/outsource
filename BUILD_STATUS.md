# OUTSOURCE — BUILD STATUS (submission)

**Public repo:** https://github.com/kalmanna3i/outsource  
**Kay Al Mannai · MGT 409 · Nov 23, 2026**

**Tests:** `APP_MODE=demo pytest -q tests/` → **17 passed** (includes parent `.env` load test and gpt-6-luna pricing)  
**Demo:** Priority 0 E2E verified (demo fixtures + UI screenshots embedded in `deliverables/report.html` / `slides.html`)  
**Live tokens:** **Not measured.** On Nov 23 both the course Portkey key and Kay’s personal OpenAI key returned 401, so Report §5 and the Cost slide show labeled estimates (gpt-6-luna course prices), not measurements.

| Area | Status |
|------|--------|
| Priority 0 workflow (demo) | **Operational** |
| Live multi-agent calls | **Incomplete** until keys + one live run |
| Insurer portal | **Simulated** |
| People CRM | **Simulated** |
| Finance projection | **Simulated** (deterministic) |
| Network / Career | **Planned** |
| CUSTOM_AUTONOMY allowlist | **Planned** |
| Parent-folder `.env` + `gpt-6-luna` Portkey default | **Operational** (dry-run verified) |

**Canvas upload:** `deliverables/report.html` + `deliverables/slides.html` only (self-contained). Repo code on GitHub.