"""Homepage visuals read stored assessments and office scores. They do not invent headlines."""

from __future__ import annotations

from pathlib import Path

from core.config import get_settings
from core.llm import LLMClient
from core.mandate import default_life_mandate
from database.db import (
    load_assessments,
    load_blueprint,
    load_daily_checkin,
    save_assessments,
    save_daily_checkin,
)
from services.universe import (
    active_dimensions,
    ask_decision,
    assessed_scores,
    capability_gaps,
    daily_plan_text,
    heatmap_matrix,
    spending_snapshot,
)
from ui.living_universe import universe_html, universe_nodes


def _demo(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("APP_MODE", "demo")
    monkeypatch.setenv("LLM_MODE", "demo")
    monkeypatch.setenv("INTEGRATION_MODE", "simulated")
    monkeypatch.setenv("OUTSOURCE_DATA_DIR", str(tmp_path))
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("PORTKEY_API_KEY", raising=False)


def test_empty_plan_and_radar_do_not_invent_headlines(tmp_path: Path, monkeypatch) -> None:
    _demo(monkeypatch, tmp_path)
    assert "86%" not in daily_plan_text(None)
    assert "6.5" not in daily_plan_text(None)
    assert "$185" not in daily_plan_text(None)
    blueprint = load_blueprint()
    mandate = default_life_mandate()
    assert assessed_scores(active_dimensions(mandate, blueprint), {}) == []
    assert capability_gaps(active_dimensions(mandate, blueprint), {}) == []


def test_saved_checkin_changes_the_plan_and_survives_reload(tmp_path: Path, monkeypatch) -> None:
    _demo(monkeypatch, tmp_path)
    save_daily_checkin(
        "2026-11-23",
        {
            "feeling": "tired",
            "energy": 2,
            "must_do": "submit the final",
            "responsibilities": "wedding logistics",
            "surprises": "train delay",
            "discretionary_hours": 1.5,
        },
    )
    low = daily_plan_text(load_daily_checkin("2026-11-23"))
    assert "recovery" in low
    assert "1.5h" in low
    save_daily_checkin(
        "2026-11-23",
        {
            "feeling": "clear",
            "energy": 5,
            "must_do": "submit the final",
            "responsibilities": "wedding logistics",
            "surprises": "",
            "discretionary_hours": 4,
        },
    )
    high = daily_plan_text(load_daily_checkin("2026-11-23"))
    assert "Start with the must-do" in high
    assert "recovery" not in high
    assert high != low


def test_saved_assessment_changes_gap(tmp_path: Path, monkeypatch) -> None:
    _demo(monkeypatch, tmp_path)
    blueprint = load_blueprint()
    mandate = default_life_mandate()
    dimensions = active_dimensions(mandate, blueprint)
    save_assessments({"academic": 3, "career": 8, "relationships": 6})
    stored = load_assessments()
    first = capability_gaps(dimensions, stored)
    academic = next(row for row in first if row["name"] == "Academic")
    assert academic["gap"] == academic["importance"] - 3
    save_assessments({"academic": 9, "career": 8, "relationships": 6})
    second = capability_gaps(dimensions, load_assessments())
    academic_next = next(row for row in second if row["name"] == "Academic")
    assert academic_next["gap"] < academic["gap"]
    assert [name for name, _score in assessed_scores(dimensions, load_assessments())] == [
        "Career",
        "Academic",
        "Relationships",
    ]


def test_priorities_and_budget_change_the_scores(tmp_path: Path, monkeypatch) -> None:
    _demo(monkeypatch, tmp_path)
    mandate = default_life_mandate()
    base = heatmap_matrix(mandate)
    shifted = mandate.model_copy(deep=True)
    shifted.priorities = ["infrastructure"]
    assert heatmap_matrix(shifted)["z"] != base["z"]
    tight = spending_snapshot(mandate, hours=15, money=80)
    wide = spending_snapshot(mandate, hours=40, money=4000)
    assert len(wide["selected"]) > len(tight["selected"])
    assert tight["weekly_cash_envelope"] != wide["weekly_cash_envelope"]


def test_question_uses_one_call_and_the_office_pick(tmp_path: Path, monkeypatch) -> None:
    _demo(monkeypatch, tmp_path)
    client = LLMClient(get_settings())
    result, record = ask_decision("What should I do with the free hour?", default_life_mandate(), client)
    assert client.call_count == 1
    assert record.agent_id == "Q01"
    assert result["chosen_label"]
    assert "free hour" in result["answer"]
    assert result["_demo_labeled"] is True


def test_universe_respects_reduced_motion_and_saved_score(tmp_path: Path, monkeypatch) -> None:
    _demo(monkeypatch, tmp_path)
    nodes = universe_nodes(default_life_mandate(), load_blueprint(), {"academic": 4})
    html = universe_html(nodes)
    assert "prefers-reduced-motion" in html
    assert "Pause" in html
    assert "Saved assessment 4 of 10" in html
    assert "86%" not in html
    keys = {node["key"] for node in nodes}
    assert {"friendship", "coursework", "relationships", "academic"} <= keys
    assert "Intellectual" in html
    assert "Georgia" not in html
