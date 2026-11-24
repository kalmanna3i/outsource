#!/usr/bin/env python3
"""Headless screenshots of the demo UI. No API key is read or written."""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MEDIA = Path(
    "/Users/kalmannai/Library/Application Support/Cursor/AgentStores/"
    "cursor_agent_stores/bc-07aa36f8-4fc8-464b-9258-096c7fa8bd7d/files/media"
)
PORT = "8771"
DATA = Path("/tmp/outsource-postfix-data")


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    MEDIA.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["APP_MODE"] = "demo"
    env["LLM_MODE"] = "demo"
    env["INTEGRATION_MODE"] = "simulated"
    env["OUTSOURCE_DATA_DIR"] = str(DATA)
    env.pop("OPENAI_API_KEY", None)
    env.pop("PORTKEY_API_KEY", None)
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "app.py",
            "--server.headless",
            "true",
            "--server.address",
            "127.0.0.1",
            "--server.port",
            PORT,
            "--browser.gatherUsageStats",
            "false",
        ],
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        deadline = time.time() + 40
        while time.time() < deadline:
            if proc.poll() is not None:
                raise RuntimeError("streamlit exited")
            time.sleep(0.4)
            try:
                import urllib.request

                with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/_stcore/health", timeout=2) as resp:
                    if resp.status == 200:
                        break
            except Exception:
                continue
        else:
            raise RuntimeError("streamlit health check timed out")

        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1440, "height": 1000})
            page.goto(f"http://127.0.0.1:{PORT}", wait_until="networkidle", timeout=60000)
            page.screenshot(path=str(MEDIA / "postfix-briefing.png"), full_page=True)
            page.get_by_role("button", name="Run Priority 0 workflow").click()
            page.get_by_text("WAITING_RESULT").first.wait_for(timeout=60000)
            page.screenshot(path=str(MEDIA / "postfix-workflow.png"), full_page=True)
            page.locator('[data-testid="stSidebar"]').get_by_text("Life Mandate", exact=True).click()
            page.get_by_text("Save draft").wait_for(timeout=30000)
            page.screenshot(path=str(MEDIA / "postfix-mandate.png"), full_page=True)
            page.locator('[data-testid="stSidebar"]').get_by_text("Strategic Radar", exact=True).click()
            page.get_by_role("button", name="Run discovery now").click()
            page.get_by_text("Candidates found").first.wait_for(timeout=60000)
            page.screenshot(path=str(MEDIA / "postfix-discovery.png"), full_page=True)
            browser.close()
        print("SHOTS_OK")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


if __name__ == "__main__":
    main()
