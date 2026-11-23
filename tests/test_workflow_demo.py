"""Priority 0 end-to-end workflow in APP_MODE=demo."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

os.environ["APP_MODE"] = "demo"

from core.config import Settings
from core.llm import LLMClient
from core.models import TaskStatus
from database.db import reset_demo_data
from services.workflow import WorkflowEngine


def test_priority0_demo_e2e(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("APP_MODE", "demo")

    def fake_settings() -> Settings:
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

    import core.config as cfg
    import database.db as dbmod
    from services import workflow as wfmod

    monkeypatch.setattr(cfg, "get_settings", fake_settings)
    monkeypatch.setattr(dbmod, "get_settings", fake_settings)
    monkeypatch.setattr(wfmod, "get_settings", fake_settings)

    reset_demo_data()
    engine = WorkflowEngine(LLMClient(fake_settings()))
    request = (
        "I need to finish my MBA final tonight, attend a wedding, "
        "handle an important work obligation, and find out what is happening with my insurance claim."
    )
    state = engine.run_priority0(
        request,
        now=datetime(2026, 11, 23, 9, 30, 0),
    )

    assert state.mode == "demo"
    assert state.status == TaskStatus.WAITING_RESULT
    assert len(state.agent_calls) >= 6
    agent_ids = {c.agent_id for c in state.agent_calls}
    assert {"A01", "A02", "B01", "F02", "F03", "F05", "F04"}.issubset(agent_ids)
    assert state.decision_plan is not None
    assert any(o.recommended for o in state.decision_plan.options)
    assert any(w.assignee == "AI" for w in state.work_packages)
    assert any(w.assignee == "HUMAN" for w in state.work_packages)
    assert state.interventions
    hi = state.interventions[-1]
    assert hi.ics_path and Path(hi.ics_path).exists()
    ics = Path(hi.ics_path).read_text(encoding="utf-8")
    assert "BEGIN:VCALENDAR" in ics
    assert "Photo ID" not in ics

    state2 = engine.resume_with_result(
        state, "Verified identity. Claim under review; upload EOB within 14 days."
    )
    assert state2.status == TaskStatus.COMPLETED
    assert state2.follow_ups
    assert any(c.agent_id == "F06" for c in state2.agent_calls)
    assert all(c.mode == "demo" for c in state2.agent_calls)
