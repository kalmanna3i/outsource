# Academic submission checklist

Course page: MGT 409 project requirements. Due Monday Nov 23, 2026, 11:59 PM ET.

| Requirement | Where | Status |
| --- | --- | --- |
| Public repo | https://github.com/kalmanna3i/outsource branch `main` | In the report and slides |
| `report.html`, sections 1–8 | `deliverables/report.html` | 8 headings. 12 printed pages |
| `slides.html`, reveal.js, at most 10 | `deliverables/slides.html` | 10 `<section>` elements. CDN reveal.js 5.1.0 |
| Parent-folder `.env` | `core/config.py` loads the parent file, then a repo `.env` if one exists | Clean install saw the parent key names set. No repo `.env` |
| Key names `PORTKEY_API_KEY` and `OPENAI_API_KEY` | `.env.example` and `get_settings` | Exact names |
| Demo mode without a key | `LLM_MODE` / `APP_MODE` fall back to labeled fixtures | Tested |
| Live measurement with a usage log | `audit/LIVE_TOKEN_USAGE.csv` | 13 calls, $0.004931, Nov 23, 7:28 PM ET |
| No key in the repo | Secret scan of the staged diff | Only the known unit-test placeholder strings, no live key |
| Insurer, email, purchases | Simulated. Nothing is sent | `external_actions_allowed` is false |
| Tests | `pytest -q tests/` | 68 passed in the project venv and in a fresh venv |

Canvas upload is `deliverables/report.html` and `deliverables/slides.html`. The rest stays in the GitHub repo.
