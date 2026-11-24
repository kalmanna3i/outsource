"""Life Mandate, deterministic scores, and the fictional executive scenario."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest

from core.config import Settings
from core.llm import LLMClient
from core.mandate import MandateStatus, fictional_executive_mandate
from core.models import AgentCallRecord
from core.usage_log import write_usage_csv
from database.db import approve_mandate, load_approved_mandate, load_mandate, update_priorities
from services.office import (
    CATALOG,
    dinner_spend,
    make_or_buy,
    optimize_portfolio,
    philanthropic_stack,
    recommend,
    reject_discovery,
    resume_office,
    run_office,
)


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
        llm_mode="demo",
        integration_mode="simulated",
    )


def _bind(monkeypatch, settings: Settings) -> None:
    import core.config as cfg
    import database.db as dbmod

    monkeypatch.setattr(cfg, "get_settings", lambda: settings)
    monkeypatch.setattr(dbmod, "get_settings", lambda: settings)


def test_priority_change_changes_the_pick() -> None:
    friendship = fictional_executive_mandate()
    friendship.status = MandateStatus.APPROVED
    friendship.priorities = ["friendship"]
    infra = friendship.model_copy(deep=True)
    infra.priorities = ["infrastructure"]
    left = recommend(friendship)
    right = recommend(infra)
    assert left.chosen_id == "home-dinner"
    assert right.chosen_id == "site-seminar"
    assert left.mission == right.mission == friendship.mission
    assert left.citations
    assert any(line.startswith("priority[0]: friendship") for line in left.citations)
    assert any(line.startswith("priority[0]: infrastructure") for line in right.citations)


def test_draft_is_not_cited_as_approved() -> None:
    draft = fictional_executive_mandate()
    assert draft.status == MandateStatus.DRAFT
    rec = recommend(draft)
    assert rec.citations == []
    assert rec.used_approved is False
    assert rec.mission == draft.mission


def test_conflict_is_named_and_mission_is_not_rewritten() -> None:
    mandate = fictional_executive_mandate()
    mandate.status = MandateStatus.APPROVED
    mandate.priorities = ["travel"]
    before = mandate.mission
    rec = recommend(mandate)
    assert rec.chosen_id == "conference-travel"
    assert rec.conflicts
    assert "not rewritten" in rec.conflicts[0]
    assert mandate.mission == before == rec.mission


def test_portfolio_protects_mandatory_commitments() -> None:
    mandate = fictional_executive_mandate()
    mandate.status = MandateStatus.APPROVED
    plan = optimize_portfolio(mandate)
    selected = set(plan["selected_ids"])
    assert {"mba-coursework", "dog-care", "recovery-block", "home-upkeep"} <= selected
    assert "conference-travel" not in selected
    assert "infra-nonprofit" in selected
    assert plan["hours_left_unscheduled"] >= 1

    squeezed = mandate.model_copy(deep=True)
    squeezed.time_budget_hours_week = 2
    tight = optimize_portfolio(squeezed)
    assert set(tight["mandatory_ids"]) <= set(tight["selected_ids"])
    assert "infra-nonprofit" not in tight["selected_ids"]


def test_scores_keep_confidence_separate_and_do_not_double_count() -> None:
    mandate = fictional_executive_mandate()
    mandate.status = MandateStatus.APPROVED
    plan = optimize_portfolio(mandate)
    from services.office import score_cards

    cards = {row["item_id"]: row for row in score_cards(mandate, set(plan["selected_ids"]))}
    dinner = cards["home-dinner"]
    assert dinner["confidence"] == 0.45
    assert dinner["strategic_value"] != dinner["confidence"]
    assert dinner["stacking_factor"] == 0.75
    stack = philanthropic_stack()
    per = stack["stacking_score"]["per_dimension"]
    assert "colleague" not in per
    assert stack["colleague_excluded"] is True
    assert stack["matrix"]


def test_dinner_periods_and_make_or_buy_keep_cash_separate() -> None:
    spend = dinner_spend()
    year = next(row for row in spend["periods"] if row["period"] == "year")
    assert year["evenings_assumed"] == 24
    assert year["cash_difference_usd"] == 2040
    assert year["home_hours"] == 72
    assert "not money already saved" in spend["assumption"]
    mandate = fictional_executive_mandate()
    mandate.status = MandateStatus.APPROVED
    choice = make_or_buy(mandate)
    assert choice["make"]["cash_usd"] == 0
    assert choice["buy"]["cash_usd"] == 180
    assert choice["purchase_made"] is False
    assert choice["cash_separate_from_opportunity_cost"] is True
    assert "dollar wage" in choice["make"]["opportunity_cost"]


def test_mandate_revisions_persist_and_priority_update_keeps_mission(tmp_path: Path, monkeypatch) -> None:
    settings = _settings(tmp_path)
    _bind(monkeypatch, settings)
    original = load_mandate()
    original.mission = "A mission written by the user."
    original.priorities = ["friendship"]
    approve_mandate(original, "user")
    approved = load_approved_mandate()
    assert approved is not None
    assert approved.mission == "A mission written by the user."
    assert recommend(approved).chosen_id == "home-dinner"
    updated = update_priorities(["infrastructure"], "user")
    assert updated.mission == "A mission written by the user."
    assert updated.revision > approved.revision
    assert recommend(updated).chosen_id == "site-seminar"
    assert load_approved_mandate().mission == "A mission written by the user."


def test_executive_office_demo_and_safety(tmp_path: Path, monkeypatch) -> None:
    settings = _settings(tmp_path)
    _bind(monkeypatch, settings)
    mandate = fictional_executive_mandate()
    mandate.status = MandateStatus.APPROVED
    package = run_office(
        LLMClient(settings),
        mandate,
        now=datetime(2026, 11, 23, 9, 30),
        ics_dir=tmp_path / "ics",
    )
    assert package["agents_invoked"] == ["S01", "D01", "Q01"]
    assert package["status"] == "WAITING_RESULT"
    assert package["outreach"]["status"] == "DRAFT_NOT_SENT"
    assert package["outreach_sent"] is False
    assert package["email_sent"] is False
    assert package["purchase_made"] is False
    assert package["mission_unchanged"] is True
    assert package["model_choice"]["valid"] is True
    assert package["model_choice"]["chosen_id"] in {item.item_id for item in CATALOG}
    assert "ds-course" in str(package["strength_gap"])
    assert "ds-pet" in str(package["strength_gap"])
    assert package["philanthropy"]["colleague_excluded"] is True
    assert package["dinner"]["periods"]
    assert package["make_or_buy"]["purchase_made"] is False
    assert any(row["item_id"] == "dog-care" for row in package["itinerary"])
    assert any(row["item_id"] == "open" for row in package["itinerary"])
    assert package["ics_path"]
    ics = Path(package["ics_path"]).read_text(encoding="utf-8")
    assert "BEGIN:VCALENDAR" in ics
    assert "PRIVATE-ONLY" not in ics
    assert "PRIVATE-ONLY" in package["human_brief"]
    assert package["quality_checks"] == []
    assert all(call["input_tokens"] is None for call in package["agent_calls"])
    with pytest.raises(ValueError):
        resume_office(package, "  ")
    resumed = resume_office(package, "I will take the committee call myself next week.")
    assert resumed["status"] == "RESOLVED_WITH_USER"
    assert resumed["external_actions_completed"] is False
    assert resumed["email_sent"] is False
    rejected = reject_discovery(package)
    assert rejected["discovery_accepted"] is False
    assert rejected["strength_gap"]["rejected_by_user"] is True


def test_usage_csv_columns_and_secret_guard(tmp_path: Path) -> None:
    record = AgentCallRecord(
        agent_id="S01",
        role="Personal discovery",
        mode="live",
        model="gpt-6-luna",
        input_tokens=10,
        output_tokens=5,
        cached_input_tokens=0,
        cost_usd=0.00001,
        cost_known=True,
        duration_ms=12.5,
        tool_calls=0,
        handoff_to="D01",
        price_source="unit-test price source",
        success=True,
    )
    path = tmp_path / "usage.csv"
    from core.usage_log import row_from_record

    write_usage_csv(path, [row_from_record(record, run_id="run_test")])
    text = path.read_text(encoding="utf-8")
    assert "agent_name" in text.splitlines()[0]
    assert "S01" in text
    assert "sk-" not in text
    poisoned = record.model_copy(deep=True)
    poisoned.error = "api_key=sk-abcdefghijklmnopqrstuvwxyz"
    with pytest.raises(RuntimeError):
        row_from_record(poisoned, run_id="run_test")
