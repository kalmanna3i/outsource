#!/usr/bin/env python3
"""Measure live model calls. Does not print or store API keys.

LLM_MODE=live is set in this process only. INTEGRATION_MODE stays simulated.
Parent ~/Desktop/AI/.env remains the only key file. A 401 stops the run.
"""

from __future__ import annotations

import os
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ["LLM_MODE"] = "live"
os.environ["INTEGRATION_MODE"] = "simulated"
os.environ["OUTSOURCE_DATA_DIR"] = str(ROOT / "audit" / "_live_work")
sys.path.insert(0, str(ROOT))

from core.config import get_settings  # noqa: E402
from core.llm import LLMClient, PRICE_SOURCE  # noqa: E402
from core.mandate import fictional_executive_mandate, MandateStatus  # noqa: E402
from core.models import AgentCallRecord  # noqa: E402
from core.safety import scrub_secrets  # noqa: E402
from core.usage_log import row_from_record, write_json, write_usage_csv  # noqa: E402
from services.office import run_office  # noqa: E402
from services.workflow import WorkflowEngine  # noqa: E402

AUDIT = ROOT / "audit"
PRIORITY_HANDOFF = {
    "A01": "A02",
    "A02": "B01",
    "B01": "F02",
    "F02": "F03",
    "F03": "F05",
    "F05": "F04",
    "F04": "F06",
    "F06": "",
}


def _auth_failure(exc: BaseException) -> bool:
    status = getattr(exc, "status_code", None)
    text = scrub_secrets(str(exc)).lower()
    return status == 401 or "401" in text or "invalid_api_key" in text or "invalid api key" in text


def _scrub_record(record: AgentCallRecord) -> AgentCallRecord:
    record.error = scrub_secrets(record.error or "") or None
    record.summary = scrub_secrets(record.summary or "")
    return record


def _fail_401(rows: list[dict], note: str) -> None:
    payload = {
        "stopped": True,
        "reason": "HTTP 401 from the model provider. Feature work stops. No usage was invented.",
        "note": scrub_secrets(note)[:500],
        "calls_recorded": len(rows),
    }
    write_json(AUDIT / "LIVE_AGENT_EXECUTION.json", payload)
    write_usage_csv(AUDIT / "LIVE_TOKEN_USAGE.csv", rows)
    (AUDIT / "LIVE_WORKFLOW_RESULTS.md").write_text(
        "# Live workflow results\n\n"
        "Stopped. The model provider returned 401. No token totals were invented.\n\n"
        f"Calls recorded before the failure: {len(rows)}.\n",
        encoding="utf-8",
    )
    print("LIVE_AUTH_FAILED 401")
    raise SystemExit(2)


def _one(client: LLMClient, **kwargs):
    try:
        payload, record = client.complete(**kwargs)
        return payload, _scrub_record(record), None
    except Exception as exc:  # noqa: BLE001
        if client.records:
            _scrub_record(client.records[-1])
        if _auth_failure(exc):
            return None, client.records[-1] if client.records else None, "401"
        return None, client.records[-1] if client.records else None, scrub_secrets(str(exc))[:400]


def main() -> None:
    started = time.perf_counter()
    settings = get_settings()
    if settings.effective_mode != "live":
        print("LIVE_NOT_CONFIGURED", settings.effective_mode, settings.llm_mode)
        raise SystemExit(2)
    print(
        "model", settings.model,
        "portkey_base", bool(settings.base_url and "portkey" in settings.base_url),
        "integrations_simulated", settings.integration_mode == "simulated" or not settings.external_actions_allowed,
    )
    rows: list[dict] = []
    sections: list[dict] = []

    smoke_client = LLMClient(settings)
    smoke_payload, smoke_rec, smoke_err = _one(
        smoke_client,
        agent_id="SMOKE",
        role="Smoke test",
        system='Return JSON {"ok": true}.',
        user="Ping.",
        run_id="smoke",
    )
    if smoke_err == "401":
        if smoke_rec:
            rows.append(row_from_record(smoke_rec, run_id="smoke"))
        _fail_401(rows, "smoke")
    if smoke_err or smoke_rec is None or not (isinstance(smoke_payload, dict) and smoke_payload.get("ok") is True):
        print("SMOKE_FAILED", smoke_err)
        raise SystemExit(1)
    rows.append(row_from_record(smoke_rec, run_id="smoke"))
    sections.append({"name": "smoke", "run_id": "smoke", "ok": True, "calls": 1})

    struct_client = LLMClient(settings)
    struct_payload, struct_rec, struct_err = _one(
        struct_client,
        agent_id="STRUCT",
        role="Structured output",
        system=(
            "Return JSON with keys agent, run_kind, and note. "
            "note must say the integrations are simulated."
        ),
        user="Structured ping for the executive office.",
        run_id="structured",
    )
    if struct_err == "401":
        if struct_rec:
            rows.append(row_from_record(struct_rec, run_id="structured"))
        _fail_401(rows, "structured")
    struct_ok = (
        struct_err is None
        and isinstance(struct_payload, dict)
        and {"agent", "run_kind", "note"} <= set(struct_payload)
    )
    if struct_rec:
        rows.append(row_from_record(struct_rec, run_id="structured"))
    if not struct_ok:
        print("STRUCTURED_FAILED", struct_err)
        raise SystemExit(1)
    sections.append({"name": "structured", "run_id": "structured", "ok": True, "calls": 1})

    wf_client = LLMClient(settings)
    engine = WorkflowEngine(wf_client)
    request = (
        "I need to finish my MBA final tonight, attend a wedding, "
        "handle an important work obligation, and find out what is happening with my insurance claim."
    )
    workflow_error = None
    state = None
    try:
        state = engine.run_priority0(request, now=datetime(2026, 11, 23, 9, 30))
        state = engine.resume_with_result(
            state,
            "Verified identity. Claim under review; upload EOB within 14 days.",
        )
    except Exception as exc:  # noqa: BLE001
        for rec in wf_client.records:
            _scrub_record(rec)
        if _auth_failure(exc):
            for rec in wf_client.records:
                rows.append(row_from_record(rec, run_id="priority0"))
            _fail_401(rows, "priority0")
        workflow_error = scrub_secrets(str(exc))[:400]
        print("WORKFLOW_FAILED", workflow_error)
    for rec in wf_client.records:
        _scrub_record(rec)
        if not rec.handoff_to:
            rec.handoff_to = PRIORITY_HANDOFF.get(rec.agent_id) or None
        rows.append(row_from_record(rec, run_id=state.workflow_id if state else "priority0"))
    if workflow_error or state is None or state.status.value != "COMPLETED":
        print("WORKFLOW_INCOMPLETE", workflow_error, None if state is None else state.status.value)
        raise SystemExit(1)
    sections.append(
        {
            "name": "priority0",
            "run_id": state.workflow_id,
            "status": state.status.value,
            "calls": [c.agent_id for c in state.agent_calls],
            "insurer": "SIMULATED",
            "email_sent": False,
            "purchase_made": False,
        }
    )

    mandate = fictional_executive_mandate()
    mandate.status = MandateStatus.APPROVED
    mandate.approved_by = "user"
    office_client = LLMClient(settings)
    office_error = None
    package = None
    try:
        package = run_office(
            office_client,
            mandate,
            now=datetime(2026, 11, 23, 18, 0),
            ics_dir=settings.data_dir / "ics",
            run_id="discovery",
        )
    except Exception as exc:  # noqa: BLE001
        for rec in office_client.records:
            _scrub_record(rec)
        if _auth_failure(exc):
            for rec in office_client.records:
                rows.append(row_from_record(rec, run_id="discovery"))
            _fail_401(rows, "discovery")
        office_error = scrub_secrets(str(exc))[:400]
        print("DISCOVERY_FAILED", office_error)
    for rec in office_client.records:
        _scrub_record(rec)
        rows.append(row_from_record(rec, run_id="discovery"))
    if office_error or package is None:
        raise SystemExit(1)

    elapsed = round(time.perf_counter() - started, 1)
    def _num(key: str) -> int:
        total = 0
        for row in rows:
            raw = row.get(key)
            if raw == "" or raw is None:
                continue
            total += int(raw)
        return total

    input_tokens = _num("input_tokens")
    cached_tokens = _num("cached_input_tokens")
    output_tokens = _num("output_tokens")
    cost = 0.0
    for row in rows:
        raw = row.get("cost_usd")
        if raw not in ("", None):
            cost += float(raw)
    execution = {
        "measured_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "timezone": "America/New_York",
        "model": settings.model,
        "llm_mode": settings.llm_mode,
        "integration_mode": settings.integration_mode,
        "external_actions_allowed": settings.external_actions_allowed,
        "price_source": PRICE_SOURCE,
        "wall_clock_seconds": elapsed,
        "call_count": len(rows),
        "input_tokens": input_tokens,
        "cached_input_tokens": cached_tokens,
        "output_tokens": output_tokens,
        "cost_usd": round(cost, 6),
        "tool_calls": sum(int(row["tool_calls"] or 0) for row in rows),
        "sections": sections,
        "discovery": {
            "run_id": package["run_id"],
            "status": package["status"],
            "agents": package["agents_invoked"],
            "deterministic_choice": package["deterministic_recommendation"]["chosen_id"],
            "model_choice": package["model_choice"]["chosen_id"],
            "model_choice_valid": package["model_choice"]["valid"],
            "model_rationale": scrub_secrets(str(package["model_choice"]["payload"].get("rationale", "")))[:800],
            "outreach_sent": package["outreach_sent"],
            "email_sent": package["email_sent"],
            "purchase_made": package["purchase_made"],
            "mission_unchanged": package["mission_unchanged"],
            "dataset": "LABELED_DATASET fictional executive scenario, not a live web fetch",
        },
        "calls": rows,
    }
    write_json(AUDIT / "LIVE_AGENT_EXECUTION.json", execution)
    write_usage_csv(AUDIT / "LIVE_TOKEN_USAGE.csv", rows)
    lines = [
        "# Live workflow results",
        "",
        f"Measured {execution['measured_at']} (America/New_York).",
        f"Model `{settings.model}`. LLM_MODE=live. INTEGRATION_MODE=simulated. Email, purchases, and the insurer were not live.",
        f"Calls: {len(rows)}. Input tokens: {input_tokens}. Cached input: {cached_tokens}. Output tokens: {output_tokens}.",
        f"Estimated cost: ${cost:.6f}. Wall clock: {elapsed} s.",
        "",
        "Price source:",
        "",
        PRICE_SOURCE,
        "",
        "Tool calls on the model: 0. The insurer check is a simulated Python function, not a model tool.",
        "",
        "## Runs",
        "",
        f"- Smoke JSON ok=true. Run id smoke.",
        "- Structured output required keys agent, run_kind, note.",
        f"- Priority 0 workflow `{state.workflow_id}` status {state.status.value}. Agents: "
        + ", ".join(c.agent_id for c in state.agent_calls)
        + ". Handoffs follow A01→A02→B01→F02→F03→F05→F04, then F06 after the human result.",
        f"- Discovery run `{package['run_id']}` agents S01→D01→Q01. "
        f"Deterministic pick `{package['deterministic_recommendation']['chosen_id']}`. "
        f"Model pick `{package['model_choice']['chosen_id']}` (valid={package['model_choice']['valid']}).",
        f"- Outreach sent: {package['outreach_sent']}. Purchase: {package['purchase_made']}. Mission unchanged: {package['mission_unchanged']}.",
        "",
        "No token number in this file was typed in by hand. Totals are the sum of LIVE_TOKEN_USAGE.csv.",
        "",
    ]
    (AUDIT / "LIVE_WORKFLOW_RESULTS.md").write_text("\n".join(lines), encoding="utf-8")
    print(
        "LIVE_OK",
        "calls", len(rows),
        "in", input_tokens,
        "cached", cached_tokens,
        "out", output_tokens,
        "cost", round(cost, 6),
        "seconds", elapsed,
    )


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        traceback.print_exc()
        raise SystemExit(1)
