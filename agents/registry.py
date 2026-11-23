"""Agent registry for Priority 0, Contextual Opportunity Engine, Strategic Radar, and Stacking."""

from __future__ import annotations

from dataclasses import dataclass

from agents import radar, specialists
from agents.base import BaseAgent
from agents.contextual_agents import ContextualBundlingAnalyst, ContextualScout
from agents.life_strategists import LIFE_STRATEGIST_AGENTS


@dataclass(frozen=True)
class AgentEntry:
    agent_cls: type[BaseAgent]
    module: str
    status: str
    note: str = ""

    @property
    def agent_id(self) -> str:
        return self.agent_cls.agent_id

    @property
    def role(self) -> str:
        return self.agent_cls.role


_CONTEXTUAL_NOTE = (
    "Demo: SIMULATED_FIXTURE scenarios. Feasibility and bundling math are deterministic. "
    "Execution drafts require authorization."
)

_RADAR_LIVE_NOTE = (
    "Live: own model call, leads returned UNVERIFIED (no web/LinkedIn/search integration wired). "
    "Demo: labeled SIMULATED_FIXTURE."
)

_STACKING_NOTE = (
    "Demo: SIMULATED_FIXTURE illustrative opportunities. Stacking scores and hours are deterministic. "
    "Friendships and colleagues are not instruments."
)

AGENT_REGISTRY: tuple[AgentEntry, ...] = (
    AgentEntry(specialists.ChiefOfStaff, "Priority 0", "Operational"),
    AgentEntry(specialists.LifeStrategyArchitect, "Priority 0", "Operational"),
    AgentEntry(specialists.OpportunityCostEconomist, "Priority 0", "Operational"),
    AgentEntry(specialists.TaskDecomposition, "Priority 0", "Operational"),
    AgentEntry(specialists.AutonomousExecution, "Priority 0 + Radar execution", "Operational"),
    AgentEntry(specialists.CalendarLogistics, "Priority 0 + Radar execution", "Operational"),
    AgentEntry(specialists.HumanHandoff, "Priority 0 + Radar execution", "Operational"),
    AgentEntry(specialists.FollowUp, "Priority 0 + Radar execution", "Operational"),
    AgentEntry(ContextualScout, "Contextual Opportunity Engine", "Simulated", _CONTEXTUAL_NOTE),
    AgentEntry(
        ContextualBundlingAnalyst,
        "Contextual Opportunity Engine",
        "Operational",
        "Deterministic bundling + model narrative in live mode.",
    ),
    AgentEntry(radar.PeopleIntelligence, "Strategic Radar", "Simulated", _RADAR_LIVE_NOTE),
    AgentEntry(
        radar.ProfessionalResearch,
        "Strategic Radar",
        "Simulated",
        "No LinkedIn integration; public/permitted info only, never scraped. " + _RADAR_LIVE_NOTE,
    ),
    AgentEntry(radar.EventIntelligence, "Strategic Radar", "Simulated", _RADAR_LIVE_NOTE),
    AgentEntry(radar.CareerIntelligence, "Strategic Radar", "Simulated", _RADAR_LIVE_NOTE),
    AgentEntry(radar.BusinessInvestmentIntelligence, "Strategic Radar", "Simulated", _RADAR_LIVE_NOTE),
    AgentEntry(radar.AcademicResearch, "Strategic Radar", "Simulated", _RADAR_LIVE_NOTE),
    AgentEntry(
        radar.RelationshipIntelligence,
        "Strategic Radar",
        "Simulated",
        "Reads only the local People CRM seed (simulated contacts). " + _RADAR_LIVE_NOTE,
    ),
    AgentEntry(
        radar.MissionAlignmentAuditor,
        "Strategic Radar",
        "Operational",
        "Deterministic rule-based scoring runs in both modes; live mode adds a model review.",
    ),
    *(
        AgentEntry(cls, "Opportunity Stacking", "Simulated", _STACKING_NOTE)
        for cls in LIFE_STRATEGIST_AGENTS
    ),
)


PRIORITY0_AGENTS: tuple[type[BaseAgent], ...] = (
    specialists.ChiefOfStaff,
    specialists.LifeStrategyArchitect,
    specialists.OpportunityCostEconomist,
    specialists.TaskDecomposition,
    specialists.AutonomousExecution,
    specialists.CalendarLogistics,
    specialists.HumanHandoff,
    specialists.FollowUp,
)

ALL_REGISTERED_AGENTS: tuple[type[BaseAgent], ...] = PRIORITY0_AGENTS + LIFE_STRATEGIST_AGENTS


def get_agent(agent_id: str) -> AgentEntry:
    for entry in AGENT_REGISTRY:
        if entry.agent_id == agent_id:
            return entry
    raise KeyError(agent_id)


def agent_catalog() -> list[dict[str, str]]:
    return [{"agent_id": e.agent_id, "role": e.role, "module": e.module} for e in AGENT_REGISTRY]


def demo_fixture_for(agent_id: str) -> dict:
    """SIMULATED_FIXTURE payloads per Life Dimension strategist."""
    common = {
        "labeled_illustrative": True,
        "evidence": "SIMULATED_FIXTURE",
        "_demo_labeled": True,
    }
    fixtures: dict[str, dict] = {
        "L01": {
            **common,
            "friendship_principles": (
                "Celebrate milestones; shared experiences over transactional networking."
            ),
            "dimension_scores": [
                {
                    "opportunity": "Illustrative — Entrepreneurship nonprofit mentor program",
                    "level": "limited",
                    "benefit_kind": "overlapping",
                    "rationale": "Social overlap with mentor cohort — not primary friendship strategy.",
                }
            ],
        },
        "L02": {
            **common,
            "collaboration_notes": "Workplace credibility may rise; promotion not guaranteed.",
            "dimension_scores": [],
        },
        "L03": {
            **common,
            "research_summary": "Illustrative philanthropic due diligence scaffold.",
            "philanthropic_fields": [
                "mission",
                "impact",
                "governance",
                "time",
                "money",
                "skills given/gained",
                "application path",
                "conflicts",
            ],
        },
        "L04": {
            **common,
            "civic_impact_notes": "Community institutions benefit from operator expertise.",
            "dimension_scores": [],
        },
        "L05": {
            **common,
            "mentorship_ethics": "Mentor for their growth, not your résumé.",
            "dimension_scores": [],
        },
        "L06": {
            **common,
            "learning_notes": "Seek advisors; board seats are not guaranteed accelerators.",
            "dimension_scores": [],
        },
    }
    if agent_id in fixtures:
        return fixtures[agent_id]
    return {
        **common,
        "summary": f"[DEMO] Agent {agent_id} acknowledged opportunity stacking intake.",
    }