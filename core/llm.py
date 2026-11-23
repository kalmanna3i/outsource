"""OpenAI-compatible LLM client with demo fixtures and spend guards."""

from __future__ import annotations

import json
import time
from typing import Any

from core.config import Settings, get_settings
from core.models import AgentCallRecord, new_id


# Approximate public list prices for reporting when provider returns usage.
# Labeled as estimates; never invented for demo runs as "measured."
_EST_PRICE_PER_1M = {
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-5.1-codex": {"input": 1.25, "output": 10.00},
    # OpenAI Standard short-context pricing (matches MGT 409 Lecture 11).
    "gpt-6-luna": {
        "input": 0.10,
        "cached_input": 0.01,
        "cache_write": 0.125,
        "output": 0.50,
    },
}

# These models reject any temperature other than the default (400 Unsupported value).
_DEFAULT_TEMPERATURE_ONLY = ("gpt-6", "gpt-5")


class BudgetExceeded(RuntimeError):
    pass


class LLMClient:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.call_count = 0
        self.total_cost_usd = 0.0
        self.records: list[AgentCallRecord] = []
        self._client = None

    def _ensure_client(self):
        if self._client is not None:
            return self._client
        if not self.settings.has_live_credentials:
            return None
        from openai import OpenAI

        kwargs: dict[str, Any] = {"api_key": self.settings.api_key}
        if self.settings.base_url:
            kwargs["base_url"] = self.settings.base_url
        # Portkey often wants x-portkey-config / virtual key headers; course keys vary.
        if self.settings.portkey_api_key and not self.settings.openai_api_key:
            kwargs["default_headers"] = {"x-portkey-api-key": self.settings.portkey_api_key}
        self._client = OpenAI(**kwargs)
        return self._client

    def _check_budget(self) -> None:
        if self.call_count >= self.settings.max_agent_calls:
            raise BudgetExceeded(
                f"MAX_AGENT_CALLS ({self.settings.max_agent_calls}) reached."
            )
        if self.total_cost_usd >= self.settings.max_workflow_cost_usd:
            raise BudgetExceeded(
                f"MAX_WORKFLOW_COST_USD (${self.settings.max_workflow_cost_usd}) reached."
            )

    def _estimate_cost(
        self,
        model: str,
        input_tokens: int | None,
        output_tokens: int | None,
        cached_input_tokens: int | None = None,
        cache_write_tokens: int | None = None,
    ) -> tuple[float | None, bool]:
        if input_tokens is None or output_tokens is None:
            return None, False
        prices = _EST_PRICE_PER_1M.get(model)
        if not prices:
            return None, False
        # prompt_tokens includes cached-read and cache-write tokens; bill each at its own rate.
        cached = min(cached_input_tokens or 0, input_tokens)
        written = min(cache_write_tokens or 0, input_tokens - cached)
        cached_rate = prices.get("cached_input", prices["input"])
        write_rate = prices.get("cache_write", prices["input"])
        cost = (
            ((input_tokens - cached - written) / 1_000_000) * prices["input"]
            + (cached / 1_000_000) * cached_rate
            + (written / 1_000_000) * write_rate
            + (output_tokens / 1_000_000) * prices["output"]
        )
        return cost, True

    def complete(
        self,
        *,
        agent_id: str,
        role: str,
        system: str,
        user: str,
        demo_payload: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any], AgentCallRecord]:
        """Return structured JSON from the model or a labeled demo fixture."""
        self._check_budget()
        mode = self.settings.effective_mode
        record = AgentCallRecord(
            call_id=new_id("call"),
            agent_id=agent_id,
            role=role,
            mode=mode,
        )

        if mode == "demo":
            time.sleep(0.05)  # small pause so activity log feels sequential
            payload = demo_payload or {"summary": f"[DEMO] {role} completed."}
            # Ensure fixture is labeled
            if isinstance(payload, dict):
                payload = {**payload, "_demo_labeled": True}
            record.finished_at = record.started_at
            record.input_tokens = None
            record.output_tokens = None
            record.cost_usd = None
            record.cost_known = False
            record.summary = f"[DEMO FIXTURE] {role}: structured output (not a live model call)."
            record.success = True
            self.call_count += 1
            self.records.append(record)
            return payload, record

        # LIVE mode — real API call
        client = self._ensure_client()
        if client is None:
            # Should not happen if effective_mode is live
            raise RuntimeError("Live mode requested but no API credentials found.")

        try:
            response = client.chat.completions.create(
                model=self.settings.model,
                messages=[
                    {"role": "system", "content": system},
                    {
                        "role": "user",
                        "content": user
                        + "\n\nRespond with a single JSON object only. No markdown.",
                    },
                ],
                response_format={"type": "json_object"},
                **(
                    {}
                    if self.settings.model.startswith(_DEFAULT_TEMPERATURE_ONLY)
                    else {"temperature": 0.2}
                ),
            )
            content = response.choices[0].message.content or "{}"
            payload = json.loads(content)
            usage = getattr(response, "usage", None)
            in_tok = getattr(usage, "prompt_tokens", None) if usage else None
            out_tok = getattr(usage, "completion_tokens", None) if usage else None
            cached = None
            written = None
            if usage and hasattr(usage, "prompt_tokens_details"):
                details = usage.prompt_tokens_details
                cached = getattr(details, "cached_tokens", None) if details else None
                written = getattr(details, "cache_write_tokens", None) if details else None
            cost, known = self._estimate_cost(
                self.settings.model, in_tok, out_tok, cached, written
            )
            record.input_tokens = in_tok
            record.output_tokens = out_tok
            record.cached_input_tokens = cached
            record.cache_write_tokens = written
            record.cost_usd = cost
            record.cost_known = known
            if cost:
                self.total_cost_usd += cost
            record.summary = f"[LIVE] {role} model call succeeded."
            record.success = True
            from datetime import datetime

            record.finished_at = datetime.utcnow()
        except Exception as exc:  # noqa: BLE001 — surface as agent failure
            record.success = False
            record.error = str(exc)
            record.summary = f"[LIVE] {role} failed: {exc}"
            from datetime import datetime

            record.finished_at = datetime.utcnow()
            self.call_count += 1
            self.records.append(record)
            raise

        self.call_count += 1
        self.records.append(record)
        return payload, record
