"""Click the real Streamlit widgets. Demo mode, temporary database."""

from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app.py"


def _side(at: AppTest, label: str) -> None:
    for button in at.sidebar.button:
        if button.label == label:
            button.click()
            return
    raise AssertionError(
        f"No sidebar button {label!r}. Saw {[b.label for b in at.sidebar.button]}"
    )


def _click(at: AppTest, label: str) -> None:
    for button in at.button:
        if button.label == label:
            button.click()
            return
    raise AssertionError(f"No button {label!r}. Saw {[b.label for b in at.button]}")


def _area(at: AppTest, prefix: str):
    for widget in at.text_area:
        if widget.label.startswith(prefix):
            return widget
    raise AssertionError(f"No text area {prefix!r}. Saw {[w.label for w in at.text_area]}")


def _blob(at: AppTest) -> str:
    parts = [m.value for m in at.markdown]
    parts += [m.value for m in at.success]
    parts += [m.value for m in at.info]
    parts += [m.value for m in at.error]
    parts += [m.value for m in at.warning]
    return "\n".join(parts)


def test_ui_clicks_workflow_discovery_and_mandate(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("APP_MODE", "demo")
    monkeypatch.setenv("LLM_MODE", "demo")
    monkeypatch.setenv("INTEGRATION_MODE", "simulated")
    monkeypatch.setenv("OUTSOURCE_DATA_DIR", str(tmp_path))
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("PORTKEY_API_KEY", raising=False)

    at = AppTest.from_file(str(APP), default_timeout=90)
    at.run()
    assert not at.exception, at.exception

    _click(at, "Run Priority 0 workflow")
    at.run()
    assert not at.exception, at.exception
    assert "WAITING_RESULT" in _blob(at)

    _area(at, "Enter verification").set_value(
        "Verified identity. Claim under review; upload EOB within 14 days."
    )
    _click(at, "Submit result & resume")
    at.run()
    assert not at.exception, at.exception
    assert "COMPLETED" in _blob(at)

    assert not at.sidebar.radio
    _side(at, "Opportunity radar")
    at.run()
    assert not at.exception, at.exception
    assert "does not write the database" in _blob(at)
    _click(at, "Run discovery now")
    at.run()
    assert not at.exception, at.exception
    assert "Candidates found" in _blob(at) or "Mode:" in _blob(at)

    _side(at, "Mission and values")
    at.run()
    assert not at.exception, at.exception
    _area(at, "Mission").set_value("A mission the user saved from the form.")
    _click(at, "Save draft")
    at.run()
    assert not at.exception, at.exception
    assert "Draft revision" in _blob(at)

    again = AppTest.from_file(str(APP), default_timeout=90)
    again.run()
    _side(again, "Mission and values")
    again.run()
    assert _area(again, "Mission").value == "A mission the user saved from the form."

    _click(again, "Approve mandate")
    again.run()
    assert "Approved revision" in _blob(again)
    _area(again, "Priorities").set_value("infrastructure")
    _click(again, "Update priorities")
    again.run()
    assert not again.exception, again.exception
    assert "Infrastructure site seminar" in _blob(again)
