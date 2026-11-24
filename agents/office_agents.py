"""Three office agents. They are not invoked on every Priority 0 request."""

from __future__ import annotations

from typing import Any

from agents.base import BaseAgent
from core.llm import LLMClient
from core.models import AgentCallRecord


class _OfficeAgent(BaseAgent):
    def run(
        self,
        user_payload: str,
        demo_payload: dict[str, Any],
        handoff_to: str | None = None,
        run_id: str | None = None,
    ) -> tuple[dict[str, Any], AgentCallRecord]:
        return self.llm.complete(
            agent_id=self.agent_id,
            role=self.role,
            system=self.system_prompt,
            user=user_payload,
            demo_payload=demo_payload,
            handoff_to=handoff_to,
            run_id=run_id,
        )


class StrengthGapAgent(_OfficeAgent):
    agent_id = "S01"
    role = "Personal discovery"
    system_prompt = (
        "You write a short SWOT and TOWS note for one person. Cite only evidence ids "
        "you were given. Separate confidence from importance. Do not diagnose. Do not flatter. "
        "Do not rewrite the mission. The user may reject the note. "
        "Return JSON keys: strengths, gaps, opportunities, threats, tows, no_diagnosis, flattery_avoided. "
        "Each list item has note, evidence_id, and confidence."
    )


class DiscoveryChooserAgent(_OfficeAgent):
    agent_id = "D01"
    role = "Discovery chooser"
    system_prompt = (
        "You choose one discretionary id from the labeled dataset in the user message. "
        "You do not invent options or sources. You quote the mandate. You name conflicts. "
        "You do not rewrite the mission. "
        "Return JSON keys: chosen_id, rationale, cited_mandate_items, conflicts, alternative_id."
    )


class QualityAuditorAgent(_OfficeAgent):
    agent_id = "Q01"
    role = "Independent quality auditor"
    system_prompt = (
        "You are an independent reviewer, not the planner. Check that the mission is unchanged, "
        "that email was not sent, that no purchase was made, that evidence ids exist, and that "
        "confidence is not disguised as strategic value. Do not rewrite the mission. Do not add praise. "
        "Return JSON keys: verdict, findings, mission_unchanged, unsupported_claims, email_sent, purchase_made."
    )
