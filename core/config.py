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
    """Course layout: parent `submissions/.env`, then repo `.env` overrides."""
    local = APP_ROOT / ".env"
    parent = APP_ROOT.parent / ".env"
    if parent.exists():
        load_dotenv(parent)
    if local.exists():
        load_dotenv(local, override=True)
    if not parent.exists() and not local.exists():
        load_dotenv()


_load_env()


AppMode = Literal["demo", "live"]
LlmMode = Literal["demo", "live"]
IntegrationMode = Literal["simulated", "live"]


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
    llm_mode: LlmMode = "demo"
    integration_mode: IntegrationMode = "simulated"

    @property
    def has_live_credentials(self) -> bool:
        return bool(self.openai_api_key or self.portkey_api_key)

    @property
    def effective_mode(self) -> AppMode:
        """Model path. Independent of email, purchases, and insurers."""
        if self.llm_mode == "live" and not self.has_live_credentials:
            return "demo"
        return self.llm_mode

    @property
    def external_actions_allowed(self) -> bool:
        """Email, purchases, and insurer submissions stay off.

        INTEGRATION_MODE is stored so it can differ from LLM_MODE. Only the
        simulated integration path is implemented. A live flag does not enable
        sending or spending.
        """
        return False

    @property
    def api_key(self) -> str | None:
        return self.openai_api_key or self.portkey_api_key

    @property
    def model(self) -> str:
        # Never invent a course-key model. Prefer explicit OPENAI_MODEL.
        if self.openai_model:
            return self.openai_model
        if self.portkey_api_key and not self.openai_api_key:
            # Course key: gpt-6-luna only (MGT 409 project requirements).
            return os.getenv("OPENAI_MODEL") or "gpt-6-luna"
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
    llm_raw = os.getenv("LLM_MODE")
    if llm_raw is None or not str(llm_raw).strip():
        llm_mode: LlmMode = mode
    else:
        llm_mode = "live" if str(llm_raw).strip().lower() == "live" else "demo"
    integration_raw = (os.getenv("INTEGRATION_MODE") or "simulated").strip().lower()
    integration_mode: IntegrationMode = "live" if integration_raw == "live" else "simulated"
    data_env = os.getenv("OUTSOURCE_DATA_DIR")
    data_dir = Path(data_env) if data_env else (APP_ROOT / "data")
    data_dir.mkdir(parents=True, exist_ok=True)
    return Settings(
        app_mode=mode,
        llm_mode=llm_mode,
        integration_mode=integration_mode,
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
