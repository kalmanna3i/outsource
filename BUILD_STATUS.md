# OUTSOURCE — BUILD STATUS (submission)

**Public repo:** https://github.com/kalmanna3i/outsource  
**Kay Al Mannai · MGT 409 · Nov 23, 2026**

**Tests:** `APP_MODE=demo pytest -q tests/` → **19 passed** (includes parent `.env` load test, gpt-6-luna pricing and live-output number parsing)  
**Demo:** Priority 0 E2E verified (demo fixtures + UI screenshots embedded in `deliverables/report.html` / `slides.html`)  
**Live tokens:** **Measured** Nov 23 (5:37 PM ET): one live run + resume on gpt-6-luna via OpenAI directly (Kay’s personal key; course Portkey key returned 401). 8 calls · 4,283 input / 0 cached / 5,387 output tokens · $0.003122 · 49.1 s. See Report §5 and the Cost slide.  

| Area | Status |
|------|--------|
| Priority 0 workflow (demo) | **Operational** |
| Live multi-agent calls | **Operational** (one measured live run, Nov 23) |
| Insurer portal | **Simulated** |
| People CRM | **Simulated** |
| Finance projection | **Simulated** (deterministic) |
| Network / Career | **Planned** |
| CUSTOM_AUTONOMY allowlist | **Planned** |
| Parent-folder `.env` + `gpt-6-luna` Portkey default | **Operational** (dry-run verified) |

**Canvas upload:** `deliverables/report.html` + `deliverables/slides.html` only (self-contained). Repo code on GitHub.