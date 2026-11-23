"""Run all six Life Dimension strategists (demo or live)."""

from __future__ import annotations

from agents.life_strategists import LIFE_STRATEGIST_AGENTS
from agents.registry import demo_fixture_for
from core.llm import LLMClient
from core.models import AgentCallRecord


def run_life_strategists(
    llm: LLMClient | None = None,
    opportunity_summary: str = "Illustrative stacking comparison matrix",
) -> tuple[list[dict], list[AgentCallRecord]]:
    client = llm or LLMClient()
    outputs: list[dict] = []
    records: list[AgentCallRecord] = []
    payload = (
        f"Opportunity stacking review (all rows labeled illustrative): {opportunity_summary}"
    )
    for agent_cls in LIFE_STRATEGIST_AGENTS:
        agent = agent_cls(client)
        out, rec = agent.run(payload, demo_fixture_for(agent_cls.agent_id))
        outputs.append({"agent_id": agent_cls.agent_id, "role": agent_cls.role, "output": out})
        records.append(rec)
    return outputs, records