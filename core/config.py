"""Configuration and environment loading.

Looks for .env in the app directory, then one level up (course grading layout).
Never hardcodes secrets or invents credentials.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv

APP_ROOT = Path(__file__).resolve().parent.parent


def _load_env() -> None:
    local = APP_ROOT / ".env"
    parent = APP_ROOT.parent / ".env"
    if local.exists():
        load_dotenv(local)
    elif parent.exists():
        load_dotenv(parent)
    else:
        load_dotenv()  # process env / cwd only


_load_env()


AppMode = Literal["demo", "live"]


@dataclass(frozen=True)
class Settings:
    app_mode: AppMode
    openai_api_key: str | None
    portkey_api_key: str | None
    openai_base_url: str | None
    openai_model: str | None
    search_api_key: str | None
    search_provider: str | None
    max_agent_calls: int
    max_workflow_cost_usd: float
    data_dir: Path

    @property
    def has_live_credentials(self) -> bool:
        return bool(self.openai_api_key or self.portkey_api_key)

    @property
    def effective_mode(self) -> AppMode:
        if self.app_mode == "live" and not self.has_live_credentials:
            return "demo"
        return self.app_mode

    @property
    def api_key(self) -> str | None:
        return self.openai_api_key or self.portkey_api_key

    @property
    def model(self) -> str:
        if self.openai_model:
            return self.openai_model
        if self.portkey_api_key and not self.openai_api_key:
            return "gpt-5.1-codex"
        return "gpt-4o-mini"

    @property
    def base_url(self) -> str | None:
        if self.openai_base_url:
            return self.openai_base_url
        if self.portkey_api_key and not self.openai_api_key:
            return "https://api.portkey.ai/v1"
        return None


def get_settings() -> Settings:
    mode_raw = (os.getenv("APP_MODE") or "demo").strip().lower()
    mode: AppMode = "live" if mode_raw == "live" else "demo"
    data_dir = APP_ROOT / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return Settings(
        app_mode=mode,
        openai_api_key=os.getenv("OPENAI_API_KEY") or None,
        portkey_api_key=os.getenv("PORTKEY_API_KEY") or None,
        openai_base_url=os.getenv("OPENAI_BASE_URL") or None,
        openai_model=os.getenv("OPENAI_MODEL") or None,
        search_api_key=os.getenv("SEARCH_API_KEY") or None,
        search_provider=os.getenv("SEARCH_PROVIDER") or None,
        max_agent_calls=int(os.getenv("MAX_AGENT_CALLS") or "25"),
        max_workflow_cost_usd=float(os.getenv("MAX_WORKFLOW_COST_USD") or "2.00"),
        data_dir=data_dir,
    )
