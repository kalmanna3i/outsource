---
cursor:
  subagentId: "bc-a8420708-ef01-52b9-9382-dfd4f0aa4511"
---

# Academic readiness

Source for the rubric: fetched `https://zlisto.github.io/mgt_409_fa26/project_requirements.html` on 23 Nov 2026. Deadline on that page: Monday, November 23, 2026, 11:59 PM. Solo project. Canvas wants the repo URL, `report.html`, and `slides.html`. Demo video is optional.

## Checklist against that page

| Requirement | Observed in this repo | This audit |
| --- | --- | --- |
| README with run steps | `README.md` has venv, pip, `streamlit run app.py` | Read. Not followed on a fresh clone. |
| `.env.example` with empty keys | Present. Names include `PORTKEY_API_KEY` and `OPENAI_API_KEY` | Read. No real values in the example. |
| Do not commit `.env` | `.gitignore` lists `.env`. No `.env` in `git ls-files` | Confirmed. |
| Load `.env` from the repo and from the parent folder | `core/config.py` `_load_env` loads parent then local with override | `tests/test_env_paths.py` passed using a dummy key in a temp parent. |
| Course key uses gpt-6-luna only | Fallback when a Portkey key is set and `OPENAI_MODEL` is empty is `gpt-6-luna`. A personal `OPENAI_API_KEY` with no model falls through to `gpt-4o-mini` | Code read. Not called. |
| `report.html` sections 1–8 in order | `deliverables/report.html` has `<h2>` 1 through 8 matching the rubric titles | Headings read via a tag strip. Body of section 5 extracted. Other sections not graded for truth. |
| Self-contained images | The HTML file is 3,331,761 bytes and the extractor replaced `<img>` tags | Images are inside the file. Not opened in a browser. |
| 10–15 printed pages | Not measured | NOT_TESTED. |
| `slides.html` reveal.js, at most 10 slides | 10 `<section>` tags. CSS and JS from `cdn.jsdelivr.net` reveal.js 5.1.0 | Counted. Arrow-key walkthrough not done. Offline, the CDN assets would not load; images in the file are data URIs. |
| Staff can run it in about 10 minutes | Existing `.venv` ran pytest in 5.35s and Streamlit booted in about a second | Fresh install time NOT_TESTED. |
| App does real work | Orchestration, scheduler, ICS, permission gate, and the deterministic math ran. Model outputs in demo are fixtures. No external tool is wired | See the feature matrix. |
| Tokenomics evidence from a real run | Report states one live run. This audit did not repeat it and found no usage log | Half-evidence at best if a grader requires a reproducible log. The screenshot is embedded and was not OCR’d. |
| Safety defense with a test | `tests/test_safety.py` and the in-process canary passed | The briefing does not feed the scrubbed string into the workflow. |
| Real user for impact | No interview file, quote file, or pilot log in the tree that was listed | Not found. Report section 7 was not treated as proof. |
| Public repo or collaborator `zlisto` | Remote is `https://github.com/kalmanna3i/outsource.git` | Visibility and collaborator list were not queried. |

## Local submission nits

- `deliverables/report.pdf` is modified and uncommitted. Canvas, per the README, wants the HTML, not the PDF. The PDF was not opened.
- `deliverables/demo_script.md` matches the fixture sentence and tells the presenter to expect a DEMO pill and a simulated insurer. That script was not performed in a browser.
- No `*.mp4` in the repo. A video in the project store was not part of this checkout and was not reviewed.

## Fit to the rubric, from what ran

The demo path is a real program: state, calendar math, a file the user can download, a permission gate, and tests. The “agents” in demo mode are scripted JSON. Live multi-agent behavior is implemented and untested here. External actions the rubric’s “real tools, real data” line might expect (search, mail, a portal) are absent and the UI says so on Career, People, and Radar.

That is a readiness description, not a predicted grade.
