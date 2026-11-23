#!/usr/bin/env python3
"""Build self-contained report.html and slides.html with embedded screenshots."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "deliverables" / "screenshots" / "manifest.b64.json"
REPO = "https://github.com/kalmanna3i/outsource"

import sys

SAFETY_TEST = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/test_safety.py", "tests/test_permissions_budget.py", "-q"],
    cwd=ROOT,
    capture_output=True,
    text=True,
    env={**__import__("os").environ, "APP_MODE": "demo"},
).stdout

ARCH_SVG = """<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 820 420' role='img' aria-label='OUTSOURCE agent flow'>
<defs><linearGradient id='g' x1='0' y1='0' x2='1' y2='1'><stop offset='0%' stop-color='#0B1F33'/><stop offset='100%' stop-color='#3F6F7A'/></linearGradient></defs>
<rect width='820' height='420' fill='#F7F3EC'/>
<rect x='20' y='20' width='180' height='50' rx='4' fill='url(#g)'/><text x='35' y='50' fill='#F7F3EC' font-family='sans-serif' font-size='14'>User request</text>
<rect x='220' y='20' width='160' height='50' fill='#14304A'/><text x='235' y='42' fill='#fff' font-size='12'>A01 Chief of Staff</text>
<rect x='400' y='20' width='160' height='50' fill='#14304A'/><text x='415' y='42' fill='#fff' font-size='12'>A02 Strategy</text>
<rect x='580' y='20' width='180' height='50' fill='#14304A'/><text x='595' y='42' fill='#fff' font-size='12'>B01 Opportunity Cost</text>
<rect x='120' y='110' width='160' height='50' fill='#3F6F7A'/><text x='135' y='140' fill='#fff' font-size='12'>F02 Decompose</text>
<rect x='320' y='110' width='160' height='50' fill='#3F6F7A'/><text x='335' y='140' fill='#fff' font-size='12'>F03 Execute</text>
<rect x='520' y='110' width='180' height='50' fill='#8A5A2B'/><text x='530' y='132' fill='#fff' font-size='11'>Simulated insurer wall</text>
<rect x='200' y='200' width='160' height='50' fill='#3F6F7A'/><text x='215' y='230' fill='#fff' font-size='12'>F05 Handoff brief</text>
<rect x='400' y='200' width='160' height='50' fill='#3F6F7A'/><text x='415' y='230' fill='#fff' font-size='12'>F04 Calendar/ICS</text>
<rect x='600' y='200' width='160' height='50' fill='#3F6F7A'/><text x='615' y='222' fill='#fff' font-size='12'>User result</text>
<rect x='320' y='300' width='200' height='50' fill='#0B1F33'/><text x='360' y='330' fill='#fff' font-size='12'>F06 Follow-up</text>
<line x1='200' y1='45' x2='220' y2='45' stroke='#3F6F7A' stroke-width='2'/>
<line x1='380' y1='45' x2='400' y2='45' stroke='#3F6F7A' stroke-width='2'/>
<line x1='560' y1='45' x2='580' y2='45' stroke='#3F6F7A' stroke-width='2'/>
<line x1='670' y1='70' x2='200' y2='110' stroke='#3F6F7A' stroke-width='2'/>
<line x1='280' y1='135' x2='320' y2='135' stroke='#3F6F7A' stroke-width='2'/>
<line x1='480' y1='135' x2='520' y2='135' stroke='#3F6F7A' stroke-width='2'/>
<line x1='610' y1='160' x2='280' y2='200' stroke='#3F6F7A' stroke-width='2'/>
<line x1='360' y1='225' x2='400' y2='225' stroke='#3F6F7A' stroke-width='2'/>
<line x1='560' y1='225' x2='600' y2='225' stroke='#3F6F7A' stroke-width='2'/>
<line x1='680' y1='250' x2='420' y2='300' stroke='#3F6F7A' stroke-width='2'/>
</svg>"""

IMG = json.loads(MANIFEST.read_text(encoding="utf-8"))


def img_tag(key: str, alt: str, max_width: str = "100%") -> str:
    return (
        f'<figure class="shot"><img alt="{alt}" style="max-width:{max_width};border:1px solid #D9D2C5" '
        f'src="data:image/png;base64,{IMG[key]}" /><figcaption>{alt}</figcaption></figure>'
    )


def build_report() -> str:
    import importlib.util
    import sys

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    spec = importlib.util.spec_from_file_location(
        "expanded_report", ROOT / "scripts" / "expanded_report.py"
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    trace = mod.capture_demo_trace()
    return mod.render_expanded_report(
        repo=REPO,
        arch_svg=ARCH_SVG,
        safety_test=SAFETY_TEST,
        trace=trace,
        img=lambda k, alt: img_tag(k, alt),
    )


def build_slides() -> str:
    keys = [
        ("daily_briefing_after", "Demo: after Priority 0 run"),
        ("decisions", "Opportunity-cost decisions"),
        ("intervention", "Human brief + ICS"),
        ("agent_activity", "Agent Activity (demo)"),
        ("safety", "Safety + permissions"),
    ]
    imgs = "\n".join(
        f'<img alt="{alt}" style="max-height:320px;width:auto;border:1px solid #3F6F7A" src="data:image/png;base64,{IMG[k]}"/>'
        for k, alt in keys
    )
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"/><title>OUTSOURCE Slides</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.css"/>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/theme/black.css"/>
<style>
.reveal h1,.reveal h2{{font-family:Georgia,serif;color:#F7F3EC}}
.reveal section{{background:linear-gradient(160deg,#0B1F33,#10263A 55%,#3F6F7A);}}
.reveal p,li{{color:#E7EEF2;font-size:.88em}}
.reveal a{{color:#9FCBD3}}
</style></head><body>
<div class="reveal"><div class="slides">

<section>
<h1>OUTSOURCE</h1>
<p>Kay Al Mannai · MGT 409</p>
<p><a href="{REPO}">{REPO}</a></p>
<p class="fragment">Know what matters. Do what only you can. Delegate the rest.</p>
</section>

<section><h2>Problem</h2><p>One evening: MBA deadline · wedding · work · insurance identity wall.</p></section>

<section><h2>What’s new vs Lindy, Motion, Reclaim, Duckbill, ChatGPT agents</h2><p>Goal-aware opportunity cost + honest human handoff (brief/ICS/resume), not generic automation.</p></section>

<section><h2>Agents</h2>{ARCH_SVG}<p>8 specialist calls (live) or labeled fixtures (demo).</p></section>

<section><h2>Demo screenshots</h2>{imgs}</section>

<section><h2>Cost</h2><p>Estimate, not measured (gpt-6-luna course prices; assumed 12k in / 2.5k out per run): ≈ $0.00245 per run · $0.049 per user per month (20 runs) · $4.90 for 100 users · $490 for 10,000 users.</p><p>Both the course Portkey key and the personal OpenAI key returned 401 on Nov 23, so no live run was possible before the deadline. Demo: $0.</p></section>

<section><h2>Safety</h2><p>Injection quarantine · REVIEW_ALL gate · no fake insurer calls</p></section>

<section><h2>Impact (honest)</h2><p>Verified E2E locally; no pilot users.</p></section>

<section><h2>Limits &amp; next</h2><p>Public repo on GitHub · push live tokenomics · pilot users</p></section>

<section><h2>Run it</h2><p><code>streamlit run app.py</code></p><p><a href="{REPO}">{REPO}</a></p></section>

</div></div>
<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.js"></script>
<script>Reveal.initialize({{hash:true,slideNumber:true}});</script>
</body></html>"""


def word_count(html: str) -> int:
    import re

    text = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.S | re.I)
    text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return len(text.split())


def pdf_page_count(html_path: Path) -> int | None:
    try:
        from pypdf import PdfReader
        from playwright.sync_api import sync_playwright

        pdf_path = html_path.with_suffix(".pdf")
        url = html_path.resolve().as_uri()
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle", timeout=120_000)
            page.pdf(
                path=str(pdf_path),
                format="Letter",
                margin={"top": "0.7in", "bottom": "0.7in", "left": "0.7in", "right": "0.7in"},
                print_background=True,
            )
            browser.close()
        return len(PdfReader(str(pdf_path)).pages)
    except Exception as exc:  # noqa: BLE001
        print("pdf_page_count failed:", exc)
        return None


if __name__ == "__main__":
    report_html = build_report()
    report_path = ROOT / "deliverables" / "report.html"
    report_path.write_text(report_html, encoding="utf-8")
    (ROOT / "deliverables" / "slides.html").write_text(build_slides(), encoding="utf-8")
    wc = word_count(report_html)
    pages = pdf_page_count(report_path)
    slide_count = build_slides().count("<section>")
    print("wrote report + slides")
    print("word_count=", wc)
    print("pdf_pages=", pages)
    print("slide_sections=", slide_count)