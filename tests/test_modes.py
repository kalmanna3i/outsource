"""LLM_MODE is independent of INTEGRATION_MODE. Sending stays off."""

from __future__ import annotations

from core.config import get_settings


def test_llm_mode_falls_back_without_a_key(monkeypatch) -> None:
    monkeypatch.setenv("LLM_MODE", "live")
    monkeypatch.setenv("APP_MODE", "demo")
    monkeypatch.setenv("INTEGRATION_MODE", "simulated")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("PORTKEY_API_KEY", raising=False)
    settings = get_settings()
    assert settings.llm_mode == "live"
    assert settings.app_mode == "demo"
    assert settings.effective_mode == "demo"
    assert settings.integration_mode == "simulated"
    assert settings.external_actions_allowed is False


def test_model_can_be_demo_while_app_mode_says_live(monkeypatch) -> None:
    monkeypatch.setenv("APP_MODE", "live")
    monkeypatch.setenv("LLM_MODE", "demo")
    monkeypatch.setenv("INTEGRATION_MODE", "live")
    settings = get_settings()
    assert settings.app_mode == "live"
    assert settings.llm_mode == "demo"
    assert settings.effective_mode == "demo"
    assert settings.integration_mode == "live"
    assert settings.external_actions_allowed is False


def test_unset_llm_mode_follows_app_mode(monkeypatch) -> None:
    monkeypatch.delenv("LLM_MODE", raising=False)
    monkeypatch.setenv("APP_MODE", "demo")
    settings = get_settings()
    assert settings.llm_mode == "demo"
    assert settings.effective_mode == "demo"
