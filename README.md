# OUTSOURCE — Personal Strategy & Execution Office

**Public repo:** https://github.com/kalmanna3i/outsource  
**Kay Al Mannai · Yale SOM · MGT 409**

> The art of building an intentional life. Every dimension of you. One intentional life.

OUTSOURCE is a multi-agent Streamlit app: read goals → opportunity-cost decisions → AI vs human allocation → execute drafts → hit a simulated insurer identity wall → human brief + ICS → resume after your result.

## Quick start (under 10 minutes)

Requirements: **Python 3.11+** (3.12 OK), `git`, internet for `pip install`.

```bash
git clone https://github.com/kalmanna3i/outsource.git
cd outsource
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Open the URL shown (usually http://localhost:8501). Default **`APP_MODE=demo`** — no API key required.

Optional: set `LLM_MODE=live` in the environment. `INTEGRATION_MODE` stays `simulated`, so email, purchases, and insurers do not go live with the model. Keys stay in the parent `.env` (see below). Do not commit a key.

## API keys (course grading layout)

The app loads environment variables from:

1. **Parent folder** `.env` (teaching-staff batch layout)  
2. **Repo folder** `.env` (overrides parent)

```
submissions/
├── .env                 ← staff keys here
└── outsource/           ← this repo (clone)
```

**Exact variable names:** `PORTKEY_API_KEY` and/or `OPENAI_API_KEY` (spelled exactly).

- **Course key:** `PORTKEY_API_KEY` + `OPENAI_MODEL=gpt-6-luna` (Portkey) — only this model on the course key.  
- **Personal key:** `OPENAI_API_KEY` (+ optional `OPENAI_MODEL`).

See `.env.example`. Never commit a real `.env`.

If `LLM_MODE=live` (or `APP_MODE=live` when `LLM_MODE` is unset) but no key is present, the UI **falls back to demo** and labels it. Sending email or spending money stays off.

## Priority 0 demo

**Daily Briefing** → use the default request → **Run Priority 0 workflow** → download **ICS** → paste a human result → **Submit result & resume** → check **Agent Activity**.

**Life Mandate** → edit the mission → **Save draft** → **Approve mandate** → change the priority order → **Update priorities**. The discretionary pick changes with the approved order. **Run discovery and recommendation** uses a labeled dataset for a fictional executive, not a live web search. The outreach draft is not sent.

## Tests

```bash
APP_MODE=demo pytest -q tests/
```

## Canvas submission

Upload **only** `deliverables/report.html` and `deliverables/slides.html` to Canvas (repo URL is inside both files). Full code stays in this GitHub repo.

## Honest status

See `BUILD_STATUS.md`. The insurer, purchases, and email are simulated. Live search and background monitoring are not built. The measured token log is `audit/LIVE_TOKEN_USAGE.csv`.