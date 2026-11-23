"""Contextual Opportunity Engine agents — C01 Scout, C02 Bundling Analyst."""

from __future__ import annotations

from typing import Any

from agents.base import BaseAgent


class ContextualScout(BaseAgent):
    agent_id = "C01"
    role = "Contextual Scout"
    system_prompt = (
        "You are C01 Contextual Scout. Given travel context and authorized location signals, "
        "propose mission-aligned public opportunities (conferences, lectures, venues, meetings). "
        "Never infer private whereabouts. Return JSON with key opportunities: list of objects with "
        "title, who, what, when, where, why, how, access_requirements, source_urls, "
        "source_retrieved_at, transport_requirements, prep_time_minutes, incremental_time_minutes, "
        "incremental_cost_usd, opportunity_cost, strategic_benefits, verification_status, geo_key."
    )

    def demo_ord(self) -> dict[str, Any]:
        from services.contextual import fixtures as fx

        return {
            "opportunities": fx.ord_opportunity_templates(),
            "labeled": "SIMULATED_FIXTURE",
            "_demo_labeled": True,
        }

    def demo_boston(self) -> dict[str, Any]:
        from services.contextual import fixtures as fx

        return {
            "opportunities": [fx.boston_opportunity_template()],
            "labeled": "SIMULATED_FIXTURE",
            "_demo_labeled": True,
        }


class ContextualBundlingAnalyst(BaseAgent):
    agent_id = "C02"
    role = "Itinerary and Bundling Analyst"
    system_prompt = (
        "You are C02 Itinerary and Bundling Analyst. Narrate tradeoffs given deterministic "
        "incremental cost and time (already computed). Do not recompute money. "
        "Return JSON with keys: narrative, highlights, risks."
    )

    def demo_layover_narrative(self) -> dict[str, Any]:
        return {
            "narrative": (
                "[SIMULATED_FIXTURE] One downtown museum visit fits the 5h ORD window with buffers; "
                "a distant plant tour fails the time budget — recommend only the feasible option."
            ),
            "highlights": ["Feasible option advances alumni + intellectual goals"],
            "risks": ["Infeasible option would risk missing boarding buffer"],
            "_demo_labeled": True,
        }

    def demo_conference_narrative(self, incremental_cost: float) -> dict[str, Any]:
        return {
            "narrative": (
                f"[SIMULATED_FIXTURE] Extending one day adds ${incremental_cost:,.2f} (computed in code) "
                "but unlocks a public lecture and founder coffee aligned with entrepreneurship goals."
            ),
            "highlights": ["Deterministic hotel delta", "Public lecture registration (draft)"],
            "risks": ["Extra day away from campus job-search rhythm"],
            "_demo_labeled": True,
        }