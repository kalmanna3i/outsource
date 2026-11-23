#!/usr/bin/env python3
"""Build self-contained report.html and slides.html with embedded screenshots."""

from __future__ import annotations

import base64
import html
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = "https://github.com/kalmanna3i/outsource"

def main_short_sha() -> str:
    import os
    import subprocess

    override = os.environ.get("CANVAS_MAIN_SHA", "").strip()
    if override:
        return override
    return subprocess.check_output(
        ["git", "rev-parse", "--short=7", "HEAD"],
        cwd=ROOT,
        text=True,
    ).strip()
MEDIA = Path(
    "/Users/kalmannai/Library/Application Support/Cursor/AgentStores/"
    "cursor_agent_stores/bc-07aa36f8-4fc8-464b-9258-096c7fa8bd7d/files/media"
)
MANIFEST = ROOT / "deliverables" / "screenshots" / "manifest.b64.json"
PRIORITY_KEY_FRAGMENTS = [
    ("daily_briefing_start", "Figure 1"),
    ("daily_briefing_after", "Figure 2"),
    ("decisions", "Figure 3"),
    ("work", "Figure 4"),
    ("intervention", "Figure 5"),
    ("resume", "Figure 6"),
    ("agent_activity", "Figure 7"),
    ("safety", "Figure 8"),
]

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

MODULE_FILES = {
    "radar_feed": "radar-feed.png",
    "radar_network_graph": "radar-network-graph.png",
    "contextual_ord_layover": "contextual-ord-layover.png",
    "contextual_boston_bundle": "contextual-boston-bundle.png",
    "stacking_matrix": "stacking-matrix.png",
}


def _extract_priority_manifest_from_report() -> dict[str, str]:
    report_path = ROOT / "deliverables" / "report.html"
    if not report_path.exists():
        return {}
    text = report_path.read_text(encoding="utf-8")
    pat = re.compile(
        r'<img[^>]+src="data:image/png;base64,([^"]+)"[^>]*>\s*<figcaption>([^<]+)</figcaption>',
        re.I,
    )
    found: dict[str, str] = {}
    for m in pat.finditer(text):
        b64, cap = m.group(1), m.group(2)
        for key, frag in PRIORITY_KEY_FRAGMENTS:
            if frag in cap and key not in found:
                found[key] = b64
                break
    return found


def load_priority_images() -> dict[str, str]:
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    extracted = _extract_priority_manifest_from_report()
    if extracted:
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(json.dumps(extracted), encoding="utf-8")
    return extracted


def load_module_images() -> dict[str, str]:
    out: dict[str, str] = {}
    for key, fname in MODULE_FILES.items():
        path = MEDIA / fname
        if not path.exists():
            raise FileNotFoundError(f"Missing module screenshot: {path}")
        out[key] = base64.b64encode(path.read_bytes()).decode()
    return out


LIVE_B64 = base64.b64encode((ROOT / "deliverables" / "live_agent_activity.png").read_bytes()).decode()


def img_tag(img: dict[str, str], key: str, alt: str, max_width: str = "100%") -> str:
    if key not in img:
        return f'<p class="warn">Missing screenshot key: {html.escape(key)}</p>'
    return (
        f'<figure class="shot"><img alt="{alt}" style="max-width:{max_width};border:1px solid #D9D2C5" '
        f'src="data:image/png;base64,{img[key]}" /><figcaption>{alt}</figcaption></figure>'
    )


def build_report() -> str:
    import importlib.util

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    spec = importlib.util.spec_from_file_location(
        "expanded_report", ROOT / "scripts" / "expanded_report.py"
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    trace = mod.capture_demo_trace()
    priority = load_priority_images()
    modules = load_module_images()
    return mod.render_expanded_report(
        repo=REPO,
        main_sha=main_short_sha(),
        arch_svg=ARCH_SVG,
        safety_test=SAFETY_TEST,
        trace=trace,
        img=lambda k, alt: img_tag(priority, k, alt),
        img_media=lambda k, alt: img_tag(modules, k, alt),
    )


def build_slides() -> str:
    modules = load_module_images()
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"/><title>OUTSOURCE Slides</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.css"/>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/theme/black.css"/>
<style>
.reveal h1,.reveal h2{{font-family:Georgia,serif;color:#F7F3EC}}
.reveal section{{background:linear-gradient(160deg,#0B1F33,#10263A 55%,#3F6F7A);}}
.reveal p,li{{color:#E7EEF2;font-size:.82em}}
.reveal a{{color:#9FCBD3}}
</style></head><body>
<div class="reveal"><div class="slides">

<section>
<h1>OUTSOURCE</h1>
<p>Kay Al Mannai · MGT 409 · main {main_short_sha()}</p>
<p><a href="{REPO}">{REPO}</a></p>
<p class="fragment">Priority 0 + Strategic Radar + Contextual + Stacking · 55 tests (demo)</p>
</section>

<section><h2>Problem</h2><p>One evening: MBA deadline · wedding · work · insurance identity wall — goal-aware opportunity cost, not generic automation.</p></section>

<section><h2>Priority 0 agents</h2>{ARCH_SVG}<p>8 specialist live calls (measured) or labeled demo fixtures.</p></section>

<section><h2>Cost (measured, live only)</h2><p style="font-size:.58em">One Priority 0 live run, Nov 23 · 5:37 PM ET · gpt-6-luna (OpenAI direct; course Portkey 401) · 8 calls · 4,283 input / 0 cached / 5,387 output · <strong>$0.00312</strong> · 49.1 s. Radar / Contextual / Stacking: <strong>demo only</strong> (no new token counts).</p><img alt="Agent Activity after live run" style="max-height:220px;width:auto;border:1px solid #3F6F7A" src="data:image/png;base64,{LIVE_B64}"/></section>

<section><h2>Strategic Radar</h2><ul><li>Discovery feed: <strong>Simulated</strong> illustrative fixtures</li><li>Research-to-action (draft not sent, ICS, follow-up): <strong>Operational</strong></li><li>Background monitoring: <strong>Planned</strong></li><li>One <strong>VERIFIED</strong> Yale SOM address; dashed edges = hypothetical introductions (not real relationships)</li></ul><img alt="Radar feed" style="max-height:200px;border:1px solid #3F6F7A" src="data:image/png;base64,{modules['radar_feed']}"/></section>

<section><h2>Contextual Opportunities</h2><ul><li>ORD layover feasibility: <strong>Operational</strong> (deterministic)</li><li>Boston bundle: +$210 and +35 minutes for extended trip (computed in code)</li><li>Scenarios: <strong>Simulated</strong> SIMULATED_FIXTURE</li></ul>
<img alt="ORD layover" style="max-height:150px;margin:4px;border:1px solid #3F6F7A" src="data:image/png;base64,{modules['contextual_ord_layover']}"/>
<img alt="Boston bundle" style="max-height:150px;margin:4px;border:1px solid #3F6F7A" src="data:image/png;base64,{modules['contextual_boston_bundle']}"/></section>

<section><h2>Opportunity Stacking</h2><ul><li>Comparison matrix: <strong>Simulated</strong> / Illustrative rows</li><li>18 vs 6 hrs/mo bundled → 144 hrs/yr recovered <em>only if benefits are comparable</em></li><li>L01–L06 strategists: demo fixtures in submission</li></ul><img alt="Stacking matrix" style="max-height:220px;border:1px solid #3F6F7A" src="data:image/png;base64,{modules['stacking_matrix']}"/></section>

<section><h2>Safety</h2><p>Injection quarantine · REVIEW_ALL gate · no fake insurer calls · hypothetical graph edges labeled</p></section>

<section><h2>Limits</h2><p>No pilot users · live tokens measured once (Priority 0) · insurer CRM Network Career planned · public repo</p></section>

<section><h2>Run it</h2><p><code>streamlit run app.py</code> · <code>APP_MODE=demo</code></p><p><a href="{REPO}">{REPO}</a></p></section>

</div></div>
<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.js"></script>
<script>Reveal.initialize({{hash:true,slideNumber:true}});</script>
</body></html>"""


def word_count(html: str) -> int:
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
    slides_html = build_slides()
    (ROOT / "deliverables" / "slides.html").write_text(slides_html, encoding="utf-8")
    wc = word_count(report_html)
    pages = pdf_page_count(report_path)
    slide_count = slides_html.count("<section>")
    print("wrote report + slides")
    print("word_count=", wc)
    print("pdf_pages=", pages)
    print("slide_sections=", slide_count)