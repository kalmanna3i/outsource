# OUTSOURCE — Personal Strategy & Execution Office

**Kay Al Mannai · Yale SOM · MGT 409 AI Foundations for Managers**

> Know what matters. Do what only you can. Delegate the rest.

OUTSOURCE is a multi-agent Streamlit app that reads your life goals, runs opportunity-cost decisions across competing obligations, allocates work to AI vs human, executes what AI can do, and — when it hits a real barrier (demo: insurer identity verification) — prepares a human intervention brief, schedules a calendar slot, exports ICS, then resumes after you enter the result.

## Quick start (≤10 minutes)

```bash
cd outsource
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # optional; demo mode works with no keys
streamlit run app.py
```

Default mode is **demo** (`APP_MODE=demo`): labeled fixtures, no API spend. Open the URL Streamlit prints (usually http://localhost:8501).

### Course grading `.env` layout

The app loads `.env` from the project folder first, then **one level up** (teaching-staff layout):

```
submissions/
├── .env                 ← PORTKEY_API_KEY / OPENAI_API_KEY
└── outsource/           ← this repo
```

### Live mode (optional)

```bash
export APP_MODE=live
export OPENAI_API_KEY=...          # or PORTKEY_API_KEY for the course key
# optional: OPENAI_BASE_URL=...  OPENAI_MODEL=...
streamlit run app.py
```

- Course key: use `PORTKEY_API_KEY` with the course-allowed model only.
- Personal key: use `OPENAI_API_KEY` and pay yourself.
- If live is requested but no key is found, the UI falls back to **demo** and says so.

Never commit a real `.env`.

## Priority 0 demo path

On **Daily Briefing**, keep (or paste) this request and click **Run Priority 0 workflow**:

> I need to finish my MBA final tonight, attend a wedding, handle an important work obligation, and find out what is happening with my insurance claim.

You should see: goals read → opportunity-cost plan → AI vs human packages → AI drafts → simulated insurer identity wall → private intervention brief → calendar slot + **Download ICS** → paste a human result → resume + follow-ups. Inspect **Agent Activity** for per-agent calls and costs (UNKNOWN in demo).

Full narration: [`deliverables/demo_script.md`](deliverables/demo_script.md).

## Tests

```bash
APP_MODE=demo pytest -q tests/
```

## Honest status

See [`BUILD_STATUS.md`](BUILD_STATUS.md). Email/calls/purchases and live insurer APIs are **not** implemented. Networking and career modules are **planned**.

## Deliverables

| File | Purpose |
|---|---|
| `deliverables/report.html` | Course report (self-contained) |
| `deliverables/slides.html` | reveal.js deck ≤10 slides |
| `deliverables/demo_script.md` | Demo narration |
| `BUILD_STATUS.md` | Operational vs simulated vs planned |

## Stack

Python 3.11+, Streamlit, Pydantic, SQLite, OpenAI-compatible client, Plotly, pytest.
