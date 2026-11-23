"""Scheduler and ICS tests."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from core.models import CalendarSlot
from services.scheduler import (
    detect_impossible,
    export_ics,
    find_slot,
    overlaps,
    within_business_hours,
)


def test_overlaps() -> None:
    a0 = datetime(2026, 11, 23, 10, 0)
    a1 = datetime(2026, 11, 23, 11, 0)
    b0 = datetime(2026, 11, 23, 10, 30)
    b1 = datetime(2026, 11, 23, 11, 30)
    assert overlaps(a0, a1, b0, b1)
    assert not overlaps(a0, a1, datetime(2026, 11, 23, 11, 0), datetime(2026, 11, 23, 12, 0))


def test_business_hours() -> None:
    start = datetime(2026, 11, 23, 9, 0)  # Monday
    end = datetime(2026, 11, 23, 10, 0)
    assert within_business_hours(start, end)
    assert not within_business_hours(datetime(2026, 11, 22, 10, 0), datetime(2026, 11, 22, 11, 0))  # Sunday


def test_find_slot_avoids_busy(tmp_path: Path) -> None:
    busy = [
        CalendarSlot(
            title="Wedding",
            start=datetime(2026, 11, 23, 16, 0),
            end=datetime(2026, 11, 23, 20, 0),
        )
    ]
    slot = find_slot(
        title="Verify identity",
        duration_minutes=30,
        busy=busy,
        search_start=datetime(2026, 11, 23, 9, 0),
        deadline=datetime(2026, 11, 23, 16, 0),
        public_description="Personal admin call",
    )
    assert slot is not None
    assert slot.end <= datetime(2026, 11, 23, 16, 0)
    assert not overlaps(slot.start, slot.end, busy[0].start, busy[0].end)

    ics = export_ics(slot, tmp_path / "test.ics")
    text = ics.read_text(encoding="utf-8")
    assert "BEGIN:VEVENT" in text
    assert "Personal admin call" in text
    assert "password" not in text.lower()


def test_impossible_deadline() -> None:
    busy = [
        CalendarSlot(
            title="All day block",
            start=datetime(2026, 11, 23, 9, 0),
            end=datetime(2026, 11, 23, 17, 0),
        )
    ]
    assert detect_impossible(
        60,
        busy,
        datetime(2026, 11, 23, 9, 0),
        datetime(2026, 11, 23, 17, 0),
    )
