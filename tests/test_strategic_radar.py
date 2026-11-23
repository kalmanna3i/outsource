"""Strategic Radar: schema, dedup, mission audit, graph honesty, research-to-action."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

import pytest

os.environ["APP_MODE"] = "demo"

from core.config import Settings
from core.llm import LLMClient
from core.models import EvidenceType
from core.radar_models import SIX_QUESTIONS, SPEC_REQUIRED_FIELDS, NetworkEdge, OpportunityRecord
from services import radar_fixtures as fx


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        app_mode="demo",
        openai_api_key=None,
        portkey_api_key=None,
        openai_base_url=None,
        openai_model=None,
        search_api_key=None,
        search_provider=None,
        max_agent_calls=25,
        max_workflow_cost_usd=2.0,
        data_dir=tmp_path,
    )


@pytest.fixture()
def engine(tmp_path, monkeypatch):
    import core.config as cfg
    import database.db as dbmod

    monkeypatch.setattr(cfg, "get_settings", lambda: _settings(tmp_path))
    monkeypatch.setattr(dbmod, "get_settings", lambda: _settings(tmp_path))
    dbmod.reset_demo_data()
    from services.radar import RadarEngine

    s = _settings(tmp_path)
    return RadarEngine(LLMClient(s), s)


@pytest.fixture()
def blueprint(engine):
    from database.db import load_blueprint

    return load_blueprint()


def test_opportunity_schema_has_every_spec_field():
    fields = OpportunityRecord.model_fields
    missing = [f for f in SPEC_REQUIRED_FIELDS + SIX_QUESTIONS if f not in fields]
    assert not missing


def test_verified_opportunity_requires_source():
    with pytest.raises(ValueError):
        OpportunityRecord(
            title="x", opportunity_type="event", description="x",
            verification_status=EvidenceType.VERIFIED_SOURCE,
        )
    ok = OpportunityRecord(
        title="x", opportunity_type="event", description="x",
        verification_status=EvidenceType.VERIFIED_SOURCE,
        source_urls=[fx.YALE_SOM_ABOUT], source_retrieved_at=fx.VERIFIED_RETRIEVED,
    )
    ev = ok.evidence()
    assert ev[0].evidence_type == EvidenceType.VERIFIED_SOURCE and ev[0].source == fx.YALE_SOM_ABOUT


def test_discovery_records_are_complete_and_labeled(engine, blueprint):
    run = engine.discover(blueprint)
    assert run.opportunities
    assert {c.agent_id for c in run.agent_calls} == {f"R0{i}" for i in range(1, 9)}
    for opp in run.opportunities:
        assert opp.verification_status == EvidenceType.SIMULATED_FIXTURE
        assert opp.illustrative
        for q in SIX_QUESTIONS:
            assert getattr(opp, q), f"{opp.title} missing {q}"
    assert len(run.evidence) >= len(run.opportunities)
    assert all(e.labeled_demo for e in run.evidence)


def test_dedup_merges_duplicates_and_keeps_provenance(engine, blueprint):
    from services.radar import deduplicate, _coerce

    raw = [
        _coerce(fx.EXEC_EVENT, "R01", "demo"),
        _coerce(fx.EXEC_EVENT_DUP, "R02", "demo"),
        _coerce(fx.EXEC_EVENT, "R03", "demo"),
        _coerce(fx.ACADEMIC_COLLAB, "R06", "demo"),
    ]
    unique, merged = deduplicate(raw)
    assert merged == 2 and len(unique) == 2
    event = next(o for o in unique if o.opportunity_type == "event")
    assert event.discovered_by == ["R01", "R02", "R03"]

    run = engine.discover(blueprint)
    titles = [o.title.lower() for o in run.opportunities]
    assert sum("roundtable" in t for t in titles) == 1
    assert run.duplicates_merged >= 2


def test_rediscovery_marks_nothing_new(engine, blueprint):
    first = engine.discover(blueprint)
    assert first.new_opportunity_ids
    second = engine.discover(blueprint)
    assert second.new_opportunity_ids == []


def test_auditor_flags_distractions_and_conflicts(engine, blueprint):
    run = engine.discover(blueprint)
    by_title = {o.title: o for o in run.opportunities}
    prestige = by_title[fx.DISTRACTION_PRESTIGE["title"]]
    tonight = by_title[fx.DISTRACTION_TONIGHT["title"]]
    assert prestige.classification == "DISTRACTION"
    assert any("prestige" in c.lower() for c in prestige.potential_conflicts)
    assert any("financial" in c.lower() for c in prestige.potential_conflicts)
    assert tonight.classification == "DISTRACTION"
    assert any("MGT 409" in c for c in tonight.potential_conflicts)
    genuine = {o.category for o in run.genuine}
    assert {
        "Potential capital partner", "Academic collaboration", "Executive networking event",
        "Professional speaking opportunity", "Friend's upcoming milestone",
    } <= genuine
    for o in run.opportunities:
        assert o.opportunity_cost


def test_money_does_not_change_alignment_score(blueprint):
    from services.radar import audit_opportunity, _coerce

    cheap = _coerce(fx.EXEC_EVENT, "R03", "demo")
    pricey = cheap.model_copy(update={"estimated_financial_cost": 900.0})
    assert audit_opportunity(cheap, blueprint)["alignment_score"] == (
        audit_opportunity(pricey, blueprint)["alignment_score"]
    )


def test_live_leads_are_never_verified(blueprint):
    from services.radar import _coerce

    raw = {**fx.CAPITAL_PARTNER, "verification_status": "VERIFIED_SOURCE",
           "source_urls": ["https://example.com"], "source_retrieved_at": "2026-11-23"}
    opp = _coerce(raw, "R05", "live")
    assert opp.verification_status == EvidenceType.UNVERIFIED


def test_graph_never_marks_hypothetical_as_verified():
    from services.radar_graph import EDGE_STYLE, build_graph, figure

    graph = build_graph()
    verified = [e for e in graph.edges if e.status == "VERIFIED"]
    hypothetical = [e for e in graph.edges if e.status == "HYPOTHETICAL"]
    assert verified and hypothetical
    assert all(e.source_url and e.retrieved_at for e in verified)
    illustrative = {n.node_id for n in graph.nodes if n.illustrative}
    for e in verified:
        assert e.source not in illustrative and e.target not in illustrative
    with pytest.raises(ValueError):
        NetworkEdge(source="a", target="b", relation="knows", status="VERIFIED")

    fig = figure(graph)
    styles = {t.name: t.line.dash for t in fig.data if t.mode == "lines"}
    assert styles[EDGE_STYLE["VERIFIED"]["label"]] == "solid"
    assert styles[EDGE_STYLE["HYPOTHETICAL"]["label"]] == "dash"


def test_research_to_action_produces_ics_draft_followup_and_sends_nothing(engine, blueprint):
    run = engine.discover(blueprint)
    opp = next(o for o in run.genuine if o.category == "Academic collaboration")
    pkg = engine.execute(opp, now=datetime(2026, 11, 23, 18, 0))
    assert pkg.outreach_draft.status == "DRAFT_NOT_SENT"
    assert pkg.outreach_sent is False
    assert pkg.outreach_draft.body
    assert pkg.calendar_slot is not None
    assert pkg.ics_path and Path(pkg.ics_path).exists()
    ics = Path(pkg.ics_path).read_text(encoding="utf-8")
    assert "BEGIN:VCALENDAR" in ics
    assert pkg.calendar_slot.start < datetime(2026, 12, 4)
    assert pkg.intervention is not None and pkg.intervention.talking_points
    assert pkg.follow_up_plan
    assert pkg.conversation_topics and pkg.preparation_requirements
    assert {c.agent_id for c in pkg.agent_calls} >= {"F03", "F04", "F05", "F06"}
    from core.radar_models import ExecutionPackage

    with pytest.raises(ValueError):
        ExecutionPackage.model_validate({**pkg.model_dump(), "outreach_sent": True})
    with pytest.raises(ValueError):
        ExecutionPackage.model_validate(
            {**pkg.model_dump(), "outreach_draft": {**pkg.outreach_draft.model_dump(), "status": "SENT"}}
        )


def test_schedule_background_monitoring_is_planned():
    from core.radar_models import RadarSchedule

    assert RadarSchedule().background_monitoring_status == "Planned"
    with pytest.raises(ValueError):
        RadarSchedule(background_monitoring_status="Operational")


def test_registry_lists_all_radar_agents():
    from agents.registry import AGENT_REGISTRY

    ids = {e.agent_id for e in AGENT_REGISTRY}
    assert {f"R0{i}" for i in range(1, 9)} <= ids
    assert {"A01", "F03", "F04", "F05", "F06"} <= ids
