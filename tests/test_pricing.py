"""Cost estimate tests for course model pricing."""

import pytest

from core.llm import LLMClient


def test_gpt_6_luna_cost_with_cached_tokens() -> None:
    client = LLMClient()
    cost, known = client._estimate_cost("gpt-6-luna", 1_000_000, 1_000_000, 400_000)
    assert known
    # 600k uncached * $0.10 + 400k cached * $0.01 + 1M output * $0.50
    assert cost == pytest.approx(0.06 + 0.004 + 0.50)


def test_unknown_model_cost_stays_unknown() -> None:
    cost, known = LLMClient()._estimate_cost("not-a-model", 10, 10)
    assert cost is None and not known


def test_gpt_6_luna_cache_write_billed_at_write_rate() -> None:
    cost, known = LLMClient()._estimate_cost("gpt-6-luna", 1_000_000, 0, 0, 1_000_000)
    assert known
    assert cost == pytest.approx(0.125)
