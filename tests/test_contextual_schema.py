"""Schema, safety, and engine integration tests."""

from __future__ import annotations

import pytest

from core.contextual_models import CONTEXTUAL_REQUIRED_FIELDS, ContextualOpportunity
from core.models import EvidenceType
from services.contextual.engine import ContextualEngine
from services.contextual.execution import prepare_execution
from services.contextual import fixtures as fx


def test_required_fields_on_model() -> None:
    fields = set(ContextualOpportunity.model_fields)
    for name in CONTEXTUAL_REQUIRED_FIELDS:
        assert name in fields, f"missing {name}"


def test_verified_source_requires_url_and_date() -> None:
    with pytest.raises(ValueError):
        ContextualOpportunity(
            title="t",
            who="w",
            what="w",
            when="w",
            where="w",
            why="w",
            how="h",
            verification_status=EvidenceType.VERIFIED_SOURCE,
            source_urls=[],
        )


def test_no_private_whereabouts_fields() -> None:
    forbidden = {"private_location", "inferred_whereabouts", "gps_trace", "home_address_inferred"}
    assert forbidden.isdisjoint(ContextualOpportunity.model_fields)


def test_ord_layover_alignment_excludes_wedding_and_work_obligation() -> None:
    run = ContextualEngine().run_layover_scenario()
    feasible = next(o for o in run.opportunities if o.feasibility_status == "feasible")
    reason = feasible.mission_alignment_reason.lower()
    assert "wedding" not in reason
    assert "work obligation" not in reason
    assert "insurance" not in reason


def test_engine_layover_has_feasible_and_infeasible() -> None:
    run = ContextualEngine().run_layover_scenario()
    statuses = {o.feasibility_status for o in run.opportunities}
    assert "feasible" in statuses
    assert "infeasible" in statuses
    for o in run.opportunities:
        assert o.booking_status == "requires_authorization"
        assert o.outreach_status == "requires_authorization"
        assert "private" not in o.model_dump_json().lower() or "private credentials" in o.access_requirements.lower()


def test_execution_not_sent_or_booked() -> None:
    run = ContextualEngine().run_layover_scenario()
    feasible = next(o for o in run.opportunities if o.feasibility_status == "feasible")
    pkg = prepare_execution(feasible, run.context)
    assert pkg.outreach_status == "requires_authorization"
    assert pkg.booking_status == "requires_authorization"
    assert "not been sent" in pkg.meeting_request_draft.lower() or "draft" in pkg.meeting_request_draft.lower()