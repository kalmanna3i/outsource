---
cursor:
  subagentId: "bc-a8420708-ef01-52b9-9382-dfd4f0aa4511"
---

# Repository inventory

| Item | Observed |
| --- | --- |
| Path | `/Users/kalmannai/Desktop/AI/outsource` |
| Remote | `https://github.com/kalmanna3i/outsource.git` |
| Branch | `main` tracking `origin/main` |
| HEAD | `cd54e49965690c3befb820ba4881063ca9a2d050` |
| Subject | `Canvas deliverables: reference branch main, not commit SHA` |
| Pull | `git pull --ff-only origin main` → Already up to date |
| Dirty tracked file | `deliverables/report.pdf` (binary size 1139083 in the index, 2300418 on disk) |
| Python | `.venv/bin/python` 3.14.7 |
| Pytest file | `pytest.ini` sets `pythonpath = .` and `testpaths = tests` |
| Dependencies | `requirements.txt`: streamlit, pydantic, python-dotenv, openai, plotly, pytest, httpx |
| `.env` in repo | Absent |
| `.env.example` keys | `PORTKEY_API_KEY`, `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL`, `SEARCH_API_KEY`, `SEARCH_PROVIDER`, `APP_MODE`, `MAX_AGENT_CALLS`, `MAX_WORKFLOW_COST_USD` |
| Parent env | `~/Desktop/AI/.env` exists. Set names: `PORTKEY_API_KEY`, `PORTKEY_PROVIDER`, `OPENAI_API_KEY`, `APP_MODE=demo`, `OPENAI_MODEL=gpt-6-luna`. `~/Desktop/AI/submissions/.env` does not exist. |
| Python LOC | 7,771 lines across the `.py` files outside `.venv` (including blanks) |
| Tracked `.py` files | 66 |

`.gitignore` ignores `.env`, `.venv/`, `__pycache__/`, `.pytest_cache/`, `data/*.db`, `*.ics`, and `deliverables/screenshots/*`.

## Tree (source and deliverables)

Application entry: `app.py` (571 lines).

| Directory | Role | Largest files (lines) |
| --- | --- | --- |
| `agents/` | Agent classes and registry | `registry.py` 176, `radar.py` 127, `specialists.py` 95 |
| `core/` | Config, LLM client, schemas, safety, permissions | `models.py` 329, `radar_models.py` 226, `llm.py` 196, `contextual_models.py` 151 |
| `services/` | Orchestrators and deterministic engines | `workflow.py` 593, `radar.py` 477, `contextual/engine.py` 142, `scheduler.py` 136 |
| `services/stacking/` | Scoring, hours, chief recommendation, fixtures | `fixtures.py` 247, `scoring.py` 84 |
| `services/contextual/` | Feasibility, bundling, alignment, execution, fixtures | `fixtures.py` 174, `feasibility.py` 159 |
| `database/` | SQLite schema and fictional seed | `db.py` 310 |
| `ui/` | Streamlit pages and CSS | `radar_page.py` 262, `contextual_page.py` 171, `theme.py` 147 |
| `tests/` | 18 test modules, 55 test functions | `test_strategic_radar.py` 214, `test_permissions_budget.py` 115 |
| `scripts/` | Report builders and a screenshot helper | `expanded_report.py` 318, `build_deliverables.py` 240 |
| `sample_data/` | `demo_request.txt` (149 characters) | the Priority 0 sentence |
| `deliverables/` | `report.html` (3,331,761 bytes), `slides.html` (1,716,163), `report.pdf`, `demo_script.md`, `live_agent_activity.png` | HTML embeds images |

`data/outsource.db` is gitignored (local SQLite). Before this audit: blueprint 1, workflows 1, people 3, settings 1 (`permission_mode`), radar 0, agent_activity 0. `data/ics/` holds previously generated `.ics` files; none were newer than 18:40 ET during this audit. Both the database and the ICS files are excluded from the review zip.

`httpx` is listed in `requirements.txt`. A search of `*.py` found no `httpx` or `requests` usage and no second use of `SEARCH_API_KEY` outside `core/config.py`.

## What was not used as evidence

`README.md` and `BUILD_STATUS.md` were read so their claims could be compared with code. They were not treated as proof of a live run, of test counts, or of module status. The pytest count and the fixture run above are the checks this audit executed.
