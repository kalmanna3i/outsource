"""Shared agent base."""

from __future__ import annotations

from typing import Any

from core.llm import LLMClient
from core.models import AgentCallRecord


class BaseAgent:
    agent_id: str = "BASE"
    role: str = "Base Agent"
    system_prompt: str = "You are a careful specialist agent for OUTSOURCE."

    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def run(
        self, user_payload: str, demo_payload: dict[str, Any]
    ) -> tuple[dict[str, Any], AgentCallRecord]:
        return self.llm.complete(
            agent_id=self.agent_id,
            role=self.role,
            system=self.system_prompt,
            user=user_payload,
            demo_payload=demo_payload,
        )
