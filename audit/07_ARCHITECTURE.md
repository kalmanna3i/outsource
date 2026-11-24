---
cursor:
  subagentId: "bc-a8420708-ef01-52b9-9382-dfd4f0aa4511"
---

# Architecture

What the code does, from the files read. Not the README diagram.

## Shape

Streamlit `app.py` is the only UI process. It calls three orchestrators:

- `services/workflow.py` `WorkflowEngine` for the evening scenario.
- `services/radar.py` `RadarEngine` for discovery and research-to-action.
- `services/contextual/engine.py` `ContextualEngine` for the layover and the Boston extension.

Opportunity Stacking does not have one engine class. `ui/stacking_page.py` calls `compute_stacking_score`, `canonical_efficiency_example`, `recommend_bundle`, and, on a button, `run_life_strategists`.

Every agent class inherits `BaseAgent.run`, which only calls `LLMClient.complete`. There is no tool schema on that call. Tools are ordinary Python around the JSON.

## Mode switch

`core/config.py` loads a parent `.env`, then a repo `.env` with override. `APP_MODE=live` without `OPENAI_API_KEY` or `PORTKEY_API_KEY` becomes effective demo. Demo `complete()` sleeps 0.05s, stamps `_demo_labeled`, leaves tokens and cost null, and does not import the OpenAI client. Live `complete()` calls `chat.completions.create` with `response_format=json_object`. Temperature 0.2 is omitted when the model name starts with `gpt-6` or `gpt-5`.

Model name: `OPENAI_MODEL` if set; else if only a Portkey key is set, `gpt-6-luna`; else `gpt-4o-mini`. Those two fallbacks are hardcoded in `get_settings`.

## Priority 0 path

1. Load the blueprint from SQLite.
2. Plant a busy wedding block.
3. A01, A02, B01. Build `DecisionPlan`. Evidence type is `SIMULATED_FIXTURE` in demo and `MODELED_ASSUMPTION` in live.
4. F02 writes `WorkPackage` rows. Assignee strings are normalized to AI, HUMAN, or DELEGATED.
5. If the permission mode is REVIEW_ALL and the approval flag is false, persist and return.
6. F03 fills deliverable summaries. Title mismatches fall through to leftover AI packages in order.
7. `check_claim_status` always hits the identity wall.
8. F05 builds `HumanIntervention`. F04 asks for a slot. `find_slot` searches business hours (weekdays 09:00–17:00) with a 15-minute buffer, first before the wedding, then after.
9. `export_ics` writes the public description only.
10. Status `WAITING_RESULT` until `resume_with_result` runs F06 and sets `COMPLETED`.

`WorkflowState.transition` appends from/to/at/note. The temp run recorded seven transitions.

## Radar path

`discover` loops R01–R07, coerces JSON into `OpportunityRecord`, dedupes, runs `audit_opportunity` for every survivor, then R08. Demo fixtures stay `SIMULATED_FIXTURE`. Live coercion forces `UNVERIFIED`. Each survivor is `save_opportunity` into `radar_opportunities`. The Streamlit page calls this on first paint, not only on the button (`ui/radar_page.py` 88–90).

`execute` drafts with F03, schedules with F04 and `find_slot`, writes an ICS file, builds an F05 brief for human opportunity types, and lists F06 follow-ups. `OutreachDraft.status` is fixed to `DRAFT_NOT_SENT`.

## Contextual path

Feasibility (`services/contextual/feasibility.py`) and bundling (`services/contextual/bundling.py`) are pure functions. The agents add a labeled narrative. The Boston function does not use the scout’s JSON for the opportunity object.

## Data

SQLite file `data/outsource.db`, created by `database/db.py`. Tables: `blueprint`, `workflows`, `people`, `settings_kv`, `radar_opportunities`, `agent_activity`. Seed people and goals are fictional names plus the student name on the blueprint. ICS files go to `data/ics/`. Workflow JSON includes the private brief and any pasted human result.

## UI map

`NAV` in `app.py` has 15 entries. `ui/theme.py` `MODULE_STATUS` paints Operational, Simulated, or Planned in the sidebar. Those paints are labels. The feature matrix is the classification from execution.

## Gaps that are structural

- No background worker. Radar schedule fields are stored and the status literal cannot be Operational.
- `SEARCH_API_KEY` never leaves `Settings`.
- `httpx` is a dependency with no import in the application code.
- `ALL_REGISTERED_AGENTS` omits radar and contextual classes even though the engines call them.
