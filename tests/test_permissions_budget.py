"""Permission gating and spend-cap tests."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest

from core.config import Settings
from core.llm import BudgetExceeded, LLMClient
from core.models import PermissionMode, TaskStatus
from core.permissions import may_auto_execute, normalize_permission
from database.db import reset_demo_data
from services.workflow import WorkflowEngine


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        app_mode="demo",
        openai_api_key=None,
        portkey_api_key=None,
        openai_base_url=None,
        openai_model=None,
        search_api_key=None,
        search_provider=None,
        max_agent_calls=3,
        max_workflow_cost_usd=2.0,
        data_dir=tmp_path,
    )


def test_review_all_blocks_execution(tmp_path: Path, monkeypatch) -> None:
    # Need headroom for A01–F02 before the REVIEW_ALL gate (F03 never runs).
    s = Settings(
        app_mode="demo",
        openai_api_key=None,
        portkey_api_key=None,
        openai_base_url=None,
        openai_model=None,
        search_api_key=None,
        search_provider=None,
        max_agent_calls=10,
        max_workflow_cost_usd=2.0,
        data_dir=tmp_path,
    )

    import core.config as cfg
    import database.db as dbmod
    from services import workflow as wfmod

    monkeypatch.setattr(cfg, "get_settings", lambda: s)
    monkeypatch.setattr(dbmod, "get_settings", lambda: s)
    monkeypatch.setattr(wfmod, "get_settings", lambda: s)

    reset_demo_data()
    engine = WorkflowEngine(LLMClient(s))
    state = engine.run_priority0(
        "MBA final, wedding, work, insurance",
        now=datetime(2026, 11, 23, 9, 30),
        permission_mode=PermissionMode.REVIEW_ALL,
        approve_ai_execution=False,
    )
    assert state.status == TaskStatus.PLANNED
    assert not any(c.agent_id == "F03" for c in state.agent_calls)
    assert any("REVIEW_ALL" in d for d in state.digital_deliverables)


def test_review_all_with_approval_continues(tmp_path: Path, monkeypatch) -> None:
    s = Settings(
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

    monkeypatch.setattr(cfg, "get_settings", lambda: s)
    monkeypatch.setattr(dbmod, "get_settings", lambda: s)
    monkeypatch.setattr(wfmod, "get_settings", lambda: s)
    reset_demo_data()
    engine = WorkflowEngine(LLMClient(s))
    state = engine.run_priority0(
        "MBA final, wedding, work, insurance",
        now=datetime(2026, 11, 23, 9, 30),
        permission_mode=PermissionMode.REVIEW_ALL,
        approve_ai_execution=True,
    )
    assert state.status == TaskStatus.WAITING_RESULT
    assert any(c.agent_id == "F03" for c in state.agent_calls)


def test_budget_exceeded_on_call_cap(tmp_path: Path) -> None:
    s = _settings(tmp_path)
    client = LLMClient(s)
    client.complete(agent_id="A", role="a", system="s", user="u", demo_payload={"ok": 1})
    client.complete(agent_id="B", role="b", system="s", user="u", demo_payload={"ok": 1})
    client.complete(agent_id="C", role="c", system="s", user="u", demo_payload={"ok": 1})
    with pytest.raises(BudgetExceeded):
        client.complete(agent_id="D", role="d", system="s", user="u", demo_payload={"ok": 1})


def test_permission_helpers() -> None:
    assert normalize_permission("review_all") == PermissionMode.REVIEW_ALL
    assert may_auto_execute(PermissionMode.MANAGED_AUTONOMY) is True
    assert may_auto_execute(PermissionMode.REVIEW_ALL) is False
