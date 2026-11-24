"""Write live-call logs without ever storing a secret."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any

from core.models import AgentCallRecord

SECRET_RE = re.compile(r"sk-[A-Za-z0-9_\-]{10,}|bearer\s+\S+|api[_-]?key\s*[:=]\s*\S+", re.I)

COLUMNS = [
    "agent_id",
    "agent_name",
    "run_id",
    "model",
    "input_tokens",
    "cached_input_tokens",
    "cache_write_tokens",
    "output_tokens",
    "duration_ms",
    "tool_calls",
    "handoff_to",
    "error",
    "cost_usd",
    "price_source",
    "mode",
    "success",
]


def assert_no_secrets(text: str) -> None:
    if SECRET_RE.search(text):
        raise RuntimeError("Refusing to write a log that looks like it contains a secret.")


def row_from_record(record: AgentCallRecord, *, run_id: str | None = None) -> dict[str, Any]:
    error = record.error or ""
    assert_no_secrets(error)
    assert_no_secrets(record.summary or "")
    return {
        "agent_id": record.agent_id,
        "agent_name": record.role,
        "run_id": run_id or record.run_id or "",
        "model": record.model or "",
        "input_tokens": record.input_tokens if record.input_tokens is not None else "",
        "cached_input_tokens": record.cached_input_tokens if record.cached_input_tokens is not None else "",
        "cache_write_tokens": record.cache_write_tokens if record.cache_write_tokens is not None else "",
        "output_tokens": record.output_tokens if record.output_tokens is not None else "",
        "duration_ms": record.duration_ms if record.duration_ms is not None else "",
        "tool_calls": record.tool_calls,
        "handoff_to": record.handoff_to or "",
        "error": error,
        "cost_usd": record.cost_usd if record.cost_usd is not None else "",
        "price_source": record.price_source or "",
        "mode": record.mode,
        "success": record.success,
    }


def write_usage_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in COLUMNS})
    assert_no_secrets(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2, default=str)
    assert_no_secrets(text)
    path.write_text(text, encoding="utf-8")
