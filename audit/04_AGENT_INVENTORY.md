---
cursor:
  subagentId: "bc-a8420708-ef01-52b9-9382-dfd4f0aa4511"
---

# Agent inventory

Count rule used here: a named agent counts only if a Python class subclasses `BaseAgent` and some engine calls `run()`. Registry status strings were not used as the count.

## Totals

| Count | What it means | Result |
| --- | --- | --- |
| 24 | Classes with a real `run()` path | A01 A02 B01 F02 F03 F04 F05 F06 C01 C02 R01 R02 R03 R04 R05 R06 R07 R08 L01 L02 L03 L04 L05 L06 |
| 24 | Of those, demo mode uses a fixture and does not build an API client | `LLMClient.complete` returns at the `mode == "demo"` branch (`core/llm.py`) |
| 24 | Of those, live mode calls the model when that agent’s `run()` is reached and `effective_mode == "live"` | `client.chat.completions.create` in the same method |
| 24 | Invoked on fixtures during this audit | Priority 0 resume, radar discover, radar execute (reuses F03–F06), both contextual scenarios, `run_life_strategists` |
| 0 | Live HTTP model calls made by this audit | Keys were blanked in the fixture process. `APP_MODE` stayed `demo`. |

`agents/registry.py` `ALL_REGISTERED_AGENTS` is only the 8 Priority 0 classes plus the 6 life strategists. Radar and contextual classes are in `AGENT_REGISTRY` and are still called. That tuple is a narrower list than the engines use.

No class in a G department exists. `agents/` has `base.py`, `specialists.py`, `radar.py`, `contextual_agents.py`, `life_strategists.py`, and `registry.py`.

Agents do not receive tool definitions. The orchestrators call Python functions (scheduler, insurer fixture, finance, scoring, feasibility) around the JSON the model or the fixture returns.

## Priority 0 — each `run()` is one `complete()`

| ID | Class | Called from | Demo this audit | Live code path |
| --- | --- | --- | --- | --- |
| A01 | ChiefOfStaff | `WorkflowEngine.run_priority0` | Fixture, tokens None | `chat.completions.create` |
| A02 | LifeStrategyArchitect | same | Fixture | same |
| B01 | OpportunityCostEconomist | same | Fixture | same |
| F02 | TaskDecomposition | same | Fixture | same |
| F03 | AutonomousExecution | workflow if not blocked; also `RadarEngine.execute` | Fixture both times | same |
| F04 | CalendarLogistics | workflow and radar execute | Fixture | same |
| F05 | HumanHandoff | workflow and radar execute | Fixture | same |
| F06 | FollowUp | `resume_with_result` and radar execute | Fixture | same |

REVIEW_ALL skips F03 and everything after it. Confirmed: calls were only A01 A02 B01 F02.

## Contextual

| ID | Class | Called from | Note |
| --- | --- | --- | --- |
| C01 | ContextualScout | layover and conference engines | Layover uses the fixture payload. Conference builds the opportunity from `boston_opportunity_template()` and discards the scout return value. |
| C02 | ContextualBundlingAnalyst | both scenarios | Narrates numbers already computed by `compare_bundles` / `assess_feasibility`. |

## Strategic Radar

| ID | Class | Called from |
| --- | --- | --- |
| R01 | PeopleIntelligence | `RadarEngine.discover` loop over `INTELLIGENCE_AGENTS` |
| R02 | ProfessionalResearch | same |
| R03 | EventIntelligence | same |
| R04 | CareerIntelligence | same |
| R05 | BusinessInvestmentIntelligence | same |
| R06 | AcademicResearch | same |
| R07 | RelationshipIntelligence | same |
| R08 | MissionAlignmentAuditor | after the loop; deterministic `audit_opportunity` also runs |

Demo discover in the temp directory: 8 calls, 7 opportunities, every `verification_status` was `SIMULATED_FIXTURE`. `_coerce` sets live leads to `UNVERIFIED` even if the payload says verified. That branch was unit-tested, not called against a model.

## Life strategists

| ID | Class | Called from |
| --- | --- | --- |
| L01 | FriendshipStrategist | `services/stacking/strategists.py` `run_life_strategists` |
| L02 | ProfessionalRelationshipStrategist | same |
| L03 | PhilanthropicStrategist | same |
| L04 | CivicEngagementStrategist | same |
| L05 | MentorshipStrategist | same |
| L06 | PersonalDevelopmentStrategist | same |

The stacking page runs the matrix and `recommend_bundle` without these six calls. The six run when the button is pressed, or when `run_life_strategists` is called directly, which this audit did. All six demo records had null tokens.

## Registry labels vs this audit

`AGENT_REGISTRY.status` marks A01–F06, C02, and R08 as Operational and the others as Simulated. Those strings are the authors’ labels. This audit’s classifications are in `audit/03_FEATURE_MATRIX.csv`. C02 and R08 still take a demo fixture in demo mode; their deterministic helpers are what ran without a model.
