#!/usr/bin/env python3
"""Capture Streamlit UI screenshots for report/slides (demo mode)."""

from __future__ import annotations

import base64
import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent.parent / "deliverables" / "screenshots"
BASE = "http://127.0.0.1:8501"

SHOTS = [
    ("01_daily_briefing_start", "daily_briefing_start"),
    ("02_daily_briefing_after_run", "daily_briefing_after"),
    ("03_decisions", "decisions"),
    ("04_work_split", "work"),
    ("05_intervention_ics", "intervention"),
    ("06_resume_completed", "resume"),
    ("07_agent_activity", "agent_activity"),
    ("08_safety_permissions", "safety"),
]


def capture() -> dict[str, str]:
    OUT.mkdir(parents=True, exist_ok=True)
    paths: dict[str, str] = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto(BASE, wait_until="domcontentloaded", timeout=120_000)
        time.sleep(3)
        p0 = OUT / "01_daily_briefing_start.png"
        page.screenshot(path=str(p0), full_page=True)
        paths["daily_briefing_start"] = str(p0)

        page.get_by_role("button", name="Run Priority 0 workflow").click()
        time.sleep(12)
        p1 = OUT / "02_daily_briefing_after_run.png"
        page.screenshot(path=str(p1), full_page=True)
        paths["daily_briefing_after"] = str(p1)

        for nav, key, fname in [
            ("My Decisions", "decisions", "03_decisions.png"),
            ("My Work", "work", "04_work_split.png"),
            ("Agent Activity", "agent_activity", "07_agent_activity.png"),
            ("Settings", "safety", "08_safety_permissions.png"),
        ]:
            page.get_by_text(nav, exact=True).first.click()
            time.sleep(2)
            fp = OUT / fname
            page.screenshot(path=str(fp), full_page=True)
            paths[key] = str(fp)

        page.get_by_text("Daily Briefing", exact=True).first.click()
        time.sleep(1)
        fp5 = OUT / "05_intervention_ics.png"
        page.screenshot(path=str(fp5), full_page=True)
        paths["intervention"] = str(fp5)

        ta = page.locator("textarea").filter(has=page.locator("xpath=..")).nth(-1)
        if ta.count() == 0:
            ta = page.locator("textarea").last
        ta.fill("Verified identity. Claim under review; upload EOB within 14 days.")
        page.get_by_role("button", name="Submit result & resume").click()
        time.sleep(4)
        fp6 = OUT / "06_resume_completed.png"
        page.screenshot(path=str(fp6), full_page=True)
        paths["resume"] = str(fp6)

        browser.close()
    return paths


def to_b64(paths: dict[str, str]) -> dict[str, str]:
    out = {}
    for k, p in paths.items():
        out[k] = base64.b64encode(Path(p).read_bytes()).decode("ascii")
    return out


if __name__ == "__main__":
    paths = capture()
    b64 = to_b64(paths)
    manifest = OUT / "manifest.b64.json"
    manifest.write_text(json.dumps(b64), encoding="utf-8")
    print("captured", len(paths), "->", manifest)