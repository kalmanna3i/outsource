"""Agent registry for Priority 0 + Contextual Opportunity Engine."""

from __future__ import annotations

from dataclasses import dataclass

from agents import specialists
from agents.base import BaseAgent
from agents.contextual_agents import ContextualBundlingAnalyst, ContextualScout


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

AGENT_REGISTRY: tuple[AgentEntry, ...] = (
    AgentEntry(specialists.ChiefOfStaff, "Priority 0", "Operational"),
    AgentEntry(specialists.LifeStrategyArchitect, "Priority 0", "Operational"),
    AgentEntry(specialists.OpportunityCostEconomist, "Priority 0", "Operational"),
    AgentEntry(specialists.TaskDecomposition, "Priority 0", "Operational"),
    AgentEntry(specialists.AutonomousExecution, "Priority 0", "Operational"),
    AgentEntry(specialists.CalendarLogistics, "Priority 0", "Operational"),
    AgentEntry(specialists.HumanHandoff, "Priority 0", "Operational"),
    AgentEntry(specialists.FollowUp, "Priority 0", "Operational"),
    AgentEntry(ContextualScout, "Contextual Opportunity Engine", "Simulated", _CONTEXTUAL_NOTE),
    AgentEntry(
        ContextualBundlingAnalyst,
        "Contextual Opportunity Engine",
        "Operational",
        "Deterministic bundling + model narrative in live mode.",
    ),
)


def get_agent(agent_id: str) -> AgentEntry:
    for entry in AGENT_REGISTRY:
        if entry.agent_id == agent_id:
            return entry
    raise KeyError(agent_id)