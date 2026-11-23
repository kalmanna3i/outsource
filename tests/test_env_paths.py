"""Verify .env loading from parent directory (course grading layout)."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path


def test_parent_env_is_loaded(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "outsource"
    repo.mkdir()
    parent_env = tmp_path / ".env"
    parent_env.write_text("PORTKEY_API_KEY=dummy-parent-key\nAPP_MODE=demo\n", encoding="utf-8")
    monkeypatch.chdir(repo)
    monkeypatch.delenv("PORTKEY_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    # Point module at temp repo by patching APP_ROOT before reload
    import core.config as cfg

    monkeypatch.setattr(cfg, "APP_ROOT", repo)
    cfg._load_env()
    assert __import__("os").getenv("PORTKEY_API_KEY") == "dummy-parent-key"