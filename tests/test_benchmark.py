"""Benchmarks use saved scores only. Population stays a cited average, not a percentile."""

from __future__ import annotations

from pathlib import Path

from database.db import load_assessment_history, save_aspirations, save_assessments
from services.benchmark import dimension_snapshot, population_benchmark
from ui.strategic_charts import history_line


def _demo(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("APP_MODE", "demo")
    monkeypatch.setenv("LLM_MODE", "demo")
    monkeypatch.setenv("INTEGRATION_MODE", "simulated")
    monkeypatch.setenv("OUTSOURCE_DATA_DIR", str(tmp_path))
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("PORTKEY_API_KEY", raising=False)


def test_nothing_saved_has_no_gap_or_history(tmp_path: Path, monkeypatch) -> None:
    _demo(monkeypatch, tmp_path)
    snap = dimension_snapshot("academic", {}, {}, [])
    assert snap["current"] is None
    assert snap["aspiration"] is None
    assert snap["gap"] is None
    assert snap["history"] == []
    assert snap["last_saved"] is None


def test_history_is_only_the_saves(tmp_path: Path, monkeypatch) -> None:
    _demo(monkeypatch, tmp_path)
    save_assessments({"academic": 3, "career": 8})
    save_assessments({"academic": 6, "career": 8})
    history = load_assessment_history()
    assert len(history) == 2
    assert [row["scores"]["academic"] for row in history] == [3, 6]
    snap = dimension_snapshot("academic", {"academic": 6}, {"academic": 9}, history)
    assert snap["gap"] == 3
    assert len(snap["history"]) == 2
    assert snap["last_saved"] == history[-1]["recorded_at"]
    fig = history_line(snap["history"])
    assert list(fig.data[0].x) == [row["recorded_at"] for row in history]
    assert "percentile" not in str(fig.data[0].name).lower()


def test_gap_waits_for_a_saved_aspiration(tmp_path: Path, monkeypatch) -> None:
    _demo(monkeypatch, tmp_path)
    save_assessments({"academic": 4})
    history = load_assessment_history()
    missing = dimension_snapshot("academic", {"academic": 4}, {}, history)
    assert missing["gap"] is None
    save_aspirations({"academic": 7})
    both = dimension_snapshot("academic", {"academic": 4}, {"academic": 7}, history)
    assert both["gap"] == 3


def test_population_figure_is_cited_and_not_a_percentile() -> None:
    fact = population_benchmark()
    blob = " ".join(str(fact[key]) for key in fact)
    assert fact["value_hours_per_day"] == 3.1
    assert fact["year"] == 2024
    assert fact["geography"] == "United States"
    assert fact["url"].startswith("https://www.bls.gov/")
    assert "th percentile" not in blob
    assert "not a percentile" in fact["method"]
    assert fact["label"] == "Population"
