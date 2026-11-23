"""Deterministic calendar scheduler and ICS export."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from core.models import CalendarSlot, new_id


def overlaps(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
    return a_start < b_end and b_start < a_end


def within_business_hours(start: datetime, end: datetime) -> bool:
    """Weekday 09:00–17:00 local naive times."""
    if start.weekday() >= 5:
        return False
    if start.hour < 9 or end.hour > 17 or (end.hour == 17 and end.minute > 0):
        return False
    if end <= start:
        return False
    return True


def find_slot(
    *,
    title: str,
    duration_minutes: int,
    busy: list[CalendarSlot],
    search_start: datetime,
    deadline: datetime | None = None,
    buffer_minutes: int = 15,
    public_description: str = "",
    private_brief_ref: str | None = None,
) -> CalendarSlot | None:
    """Find the earliest non-overlapping business-hours slot."""
    cursor = search_start
    # Snap to next business open if needed
    if cursor.hour < 9:
        cursor = cursor.replace(hour=9, minute=0, second=0, microsecond=0)
    if cursor.hour >= 17 or cursor.weekday() >= 5:
        cursor = _next_business_open(cursor)

    duration = timedelta(minutes=duration_minutes)
    buffer = timedelta(minutes=buffer_minutes)
    limit = deadline or (search_start + timedelta(days=14))

    for _ in range(500):
        if cursor > limit:
            return None
        end = cursor + duration
        if not within_business_hours(cursor, end):
            cursor = _next_business_open(cursor)
            continue
        conflict = False
        for b in busy:
            # include buffer around busy blocks
            if overlaps(cursor - buffer, end + buffer, b.start, b.end):
                conflict = True
                cursor = b.end + buffer
                break
        if conflict:
            continue
        return CalendarSlot(
            slot_id=new_id("slot"),
            title=title,
            start=cursor,
            end=end,
            public_description=public_description,
            private_brief_ref=private_brief_ref,
            busy=True,
        )
    return None


def _next_business_open(dt: datetime) -> datetime:
    d = dt
    if d.hour >= 17:
        d = (d + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
    while d.weekday() >= 5:
        d = (d + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
    if d.hour < 9:
        d = d.replace(hour=9, minute=0, second=0, microsecond=0)
    return d


def detect_impossible(
    duration_minutes: int,
    busy: list[CalendarSlot],
    search_start: datetime,
    deadline: datetime,
) -> bool:
    """True if no slot fits before deadline."""
    return (
        find_slot(
            title="probe",
            duration_minutes=duration_minutes,
            busy=busy,
            search_start=search_start,
            deadline=deadline,
        )
        is None
    )


def export_ics(slot: CalendarSlot, path: Path) -> Path:
    """Write a minimal RFC5545 .ics file. Public description only (no private brief)."""
    path.parent.mkdir(parents=True, exist_ok=True)

    def fmt(dt: datetime) -> str:
        return dt.strftime("%Y%m%dT%H%M%S")

    uid = f"{slot.slot_id}@outsource.local"
    # Escape commas/semicolons lightly
    desc = (slot.public_description or "").replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;")
    summary = slot.title.replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;")
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//OUTSOURCE//Personal Strategy Office//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{fmt(datetime.utcnow())}Z",
        f"DTSTART:{fmt(slot.start)}",
        f"DTEND:{fmt(slot.end)}",
        f"SUMMARY:{summary}",
        f"DESCRIPTION:{desc}",
        "END:VEVENT",
        "END:VCALENDAR",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
