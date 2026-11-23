"""Life strategist agent registry and demo runs."""

import os

from agents.life_strategists import LIFE_STRATEGIST_AGENTS
from agents.registry import ALL_REGISTERED_AGENTS, agent_catalog, demo_fixture_for
from services.stacking.strategists import run_life_strategists


def test_six_life_strategists_registered() -> None:
    assert len(LIFE_STRATEGIST_AGENTS) == 6
    ids = {a.agent_id for a in LIFE_STRATEGIST_AGENTS}
    assert ids == {"L01", "L02", "L03", "L04", "L05", "L06"}


def test_catalog_includes_priority0_and_life() -> None:
    assert len(ALL_REGISTERED_AGENTS) == 8 + 6
    catalog = agent_catalog()
    assert any(c["agent_id"] == "L03" for c in catalog)


def test_demo_fixtures_labeled() -> None:
    for agent_id in ("L01", "L02", "L03", "L04", "L05", "L06"):
        fix = demo_fixture_for(agent_id)
        assert fix.get("labeled_illustrative") is True
        assert fix.get("evidence") == "SIMULATED_FIXTURE"


def test_run_strategists_demo_mode() -> None:
    os.environ["APP_MODE"] = "demo"
    outputs, records = run_life_strategists()
    assert len(outputs) == 6
    assert len(records) == 6
    assert all(r.mode == "demo" for r in records)