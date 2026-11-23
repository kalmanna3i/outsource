"""Contextual Opportunity Engine orchestration."""

from __future__ import annotations

from typing import Any, Callable

from agents.contextual_agents import ContextualBundlingAnalyst, ContextualScout
from core.config import get_settings
from core.contextual_models import (
    ContextualOpportunity,
    ContextualRun,
    ItineraryLine,
    TravelContext,
)
from core.llm import LLMClient
from core.models import LifeBlueprint
from database.db import load_blueprint
from services.contextual.alignment import score_alignment
from services.contextual.bundling import compare_bundles
from services.contextual.execution import prepare_execution
from services.contextual.feasibility import assess_feasibility
from services.contextual import fixtures as fx

ProgressCb = Callable[[str], None]


def _noop(_: str) -> None:
    pass


def _lines_from_dicts(rows: list[dict[str, Any]]) -> list[ItineraryLine]:
    return [
        ItineraryLine(
            label=r["label"],
            cost_usd=float(r["cost_usd"]),
            duration_minutes=int(r["duration_minutes"]),
            notes=r.get("notes", ""),
        )
        for r in rows
    ]


class ContextualEngine:
    def __init__(self, llm: LLMClient | None = None) -> None:
        settings = get_settings()
        self.llm = llm or LLMClient(settings)
        self.mode = settings.effective_mode

    def run_layover_scenario(self, progress: ProgressCb = _noop) -> ContextualRun:
        ctx = fx.ord_layover_context()
        bp = load_blueprint()
        progress("Contextual Scout (C01) scanning ORD layover window…")
        scout = ContextualScout(self.llm)
        payload, call1 = scout.run(
            f"Context: {ctx.model_dump_json()}",
            demo_payload=scout.demo_ord(),
        )
        opportunities = self._coerce_list(
            payload, bp, ctx, fx.ORD_GEO, scenario_key="ord_layover"
        )
        progress("Itinerary/Bundling Analyst (C02) narrating layover tradeoffs…")
        analyst = ContextualBundlingAnalyst(self.llm)
        _, call2 = analyst.run(
            f"Opportunities: {[o.title for o in opportunities]}",
            demo_payload=analyst.demo_layover_narrative(),
        )
        return ContextualRun(
            context=ctx,
            mode=self.mode,  # type: ignore[arg-type]
            opportunities=opportunities,
            comparison=None,
            agent_calls=[call1, call2],
            scenario_key="ord_layover",
        )

    def run_conference_scenario(self, progress: ProgressCb = _noop) -> ContextualRun:
        ctx = fx.boston_conference_context()
        bp = load_blueprint()
        progress("Contextual Scout (C01) scanning conference extension…")
        scout = ContextualScout(self.llm)
        template = fx.boston_opportunity_template()
        geo = fx.BOSTON_GEO
        opp = ContextualOpportunity(**{k: v for k, v in template.items() if k != "geo_key"})
        opp = assess_feasibility(ctx, opp, geo)
        opp = score_alignment(opp, bp, scenario_key="boston_conference")
        opp.discovered_by = ["C01"]
        progress("Bundling: comparing original vs +1 day (deterministic math)…")
        orig_rows, ext_rows = fx.boston_bundle_lines()
        comparison = compare_bundles(
            context_label=ctx.label,
            original_lines=_lines_from_dicts(orig_rows),
            alternative_lines=_lines_from_dicts(ext_rows),
            original_label="Original 3-night itinerary",
            alternative_label="Extend 1 day: lecture + meeting",
            alt_benefits=[
                "Public lecture visibility",
                "Founder conversation for post-MBA pipeline",
            ],
            alt_risks=[
                "Extra $195 hotel + meals (deterministic)",
                "One day delay returning to New Haven rhythm",
            ],
            orig_benefits=["Minimal time away from campus"],
            orig_risks=["Misses public lecture and local meeting"],
        )
        analyst = ContextualBundlingAnalyst(self.llm)
        _, call2 = analyst.run(
            comparison.net_benefit_summary,
            demo_payload=analyst.demo_conference_narrative(comparison.incremental_cost_usd),
        )
        _, call1 = scout.run(ctx.label, demo_payload=scout.demo_boston())
        return ContextualRun(
            context=ctx,
            mode=self.mode,  # type: ignore[arg-type]
            opportunities=[opp],
            comparison=comparison,
            agent_calls=[call1, call2],
            scenario_key="boston_conference",
        )

    def execute(self, opp: ContextualOpportunity, ctx: TravelContext) -> Any:
        return prepare_execution(opp, ctx)

    def _coerce_list(
        self,
        payload: dict[str, Any],
        bp: LifeBlueprint,
        ctx: TravelContext,
        geo_map: dict[str, Any],
        scenario_key: str = "ord_layover",
    ) -> list[ContextualOpportunity]:
        raw_list = payload.get("opportunities") or fx.ord_opportunity_templates()
        out: list[ContextualOpportunity] = []
        for raw in raw_list:
            row = dict(raw)
            gk = row.pop("geo_key", "msi")
            geo = geo_map.get(gk) or fx.ORD_GEO["msi"]
            opp = ContextualOpportunity(**row)
            opp = assess_feasibility(ctx, opp, geo)
            opp = score_alignment(opp, bp, scenario_key=scenario_key)
            opp.discovered_by = ["C01"]
            out.append(opp)
        return out