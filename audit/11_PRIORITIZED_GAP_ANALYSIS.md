---
cursor:
  subagentId: "bc-a8420708-ef01-52b9-9382-dfd4f0aa4511"
---

# Prioritized gap analysis

Order is by what changes a grader’s or a user’s next session. Each item was seen in code or in a command from this audit.

## P0 — behavior that already surprised this audit

1. **Strategic Radar writes the database on first view.** `ui/radar_page.py` calls `_run_discovery()` whenever `radar_run` is missing, and `discover` inserts rows. AppTest raised `radar_opportunities` from 0 to 7 without a button click. The button is not the only trigger. Restored by deleting those rows.

2. **Briefing quarantine does not replace the workflow input.** `guard_external_content` runs for the warning. `run_priority0` is still called with the raw text area. A pasted “ignore previous instructions” string is flagged and also handed to the agents.

3. **Live token evidence is not in the repo as data.** The HTML and `BUILD_STATUS.md` agree on 4,283 / 5,387 / $0.003122. No usage file and no matching workflow id are in the checkout. A grader who cannot see the embedded screenshot has only the prose.

## P1 — product holes that the UI already labels, or almost labels

4. **No external tool.** Search key is unused. No mail, SMS, LinkedIn, purchase, or insurer client. Career, Side Quest, Focus Guardian, and Portfolio Optimizer are labels only. Background monitoring cannot be marked Operational.

5. **CUSTOM_AUTONOMY is not a third policy.** It passes `may_auto_execute`. The Settings caption says this. The registry of permissions still offers it as a choice.

6. **Goals cannot be edited.** The blueprint page saves summary, mission, principles, and objectives. Goal importance, dates, and progress stay on the seed.

7. **Boston C01 output is discarded.** `run_conference_scenario` constructs the opportunity from the fixture template and ignores the scout payload. The call still counts as an agent call.

8. **Dollar budget misses unknown models.** If `OPENAI_MODEL` is not in `_EST_PRICE_PER_1M`, live cost stays unknown and `MAX_WORKFLOW_COST_USD` does not move. The call cap still applies.

## P2 — correctness and packaging

9. **ICS clock.** `export_ics` writes `DTSTART`/`DTEND` as naive local strings and `DTSTAMP` with a `Z` suffix from `datetime.now()`. The temp file was not checked in a calendar app. The privacy split (public description only) did hold.

10. **`datetime.utcnow()` on Python 3.14.** 283 deprecation warnings, tests still pass. Removal of `utcnow` in a future Python would break record timestamps.

11. **`use_container_width` deprecation** printed while AppTest rendered dataframes and charts. Streamlit said it will be removed after 2025-12-31.

12. **Slides need the CDN** for reveal.js behavior. Images are embedded. A double-click offline will not get the slide runtime.

13. **Fresh install not proven.** Staff following the README on a machine without this `.venv` was not timed.

14. **Uncommitted `deliverables/report.pdf`.** Binary differs from HEAD. Easy to ship the wrong artifact if someone packages the working tree without looking.

15. **`ALL_REGISTERED_AGENTS` drops radar and contextual classes** even though those classes run. Anything that iterates that tuple under-counts the office.

## Not a gap

Demo mode does not pretend the eight Priority 0 calls have token counts. The insurer function does not invent a paid claim outcome. Radar drafts are rejected by the schema if marked sent. Those three were checked, not assumed from the README.
