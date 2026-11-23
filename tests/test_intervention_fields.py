"""Human intervention brief field completeness + resume."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from core.config import Settings
from core.llm import LLMClient
from core.models import TaskStatus
from database.db import reset_demo_data
from services.workflow import WorkflowEngine


REQUIRED_HI_FIELDS = (
    "title",
    "why_human_required",
    "prepared_brief",
    "talking_points",
    "documents_ready",
    "status",
    "sensitive",
)


def test_intervention_has_required_fields_and_resumes(tmp_path: Path, monkeypatch) -> None:
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
        "MBA final, wedding, work, insurance claim",
        now=datetime(2026, 11, 23, 9, 30),
    )
    assert state.interventions
    hi = state.interventions[-1]
    data = hi.model_dump()
    for field in REQUIRED_HI_FIELDS:
        assert field in data
        assert data[field] not in (None, "", [])
    assert hi.suggested_slot is not None
    assert hi.ics_path
    assert hi.status == "WAITING_RESULT"
    # Sensitive details not in public ICS
    ics = Path(hi.ics_path).read_text(encoding="utf-8")
    for secretish in hi.talking_points + hi.documents_ready:
        if len(secretish) > 8:
            assert secretish not in ics

    resumed = engine.resume_with_result(state, "Verified; claim under review.")
    assert resumed.status == TaskStatus.COMPLETED
    assert resumed.interventions[-1].status == "RESOLVED"
    assert resumed.interventions[-1].user_result
    assert resumed.follow_ups
