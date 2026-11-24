"""Saved self-assessments, aspiration targets, and one cited population fact.

Personal history, aspiration, and the population figure stay separate.
Nothing here builds a percentile.
"""

from __future__ import annotations

from typing import Any

# BLS American Time Use Survey, 2024 results, released June 26, 2025.
# "people in the United States age 15 and over spent 3.1 hours per day working."
POPULATION_HOURS = 3.1
POPULATION_YEAR = 2024
POPULATION_GEOGRAPHY = "United States"
POPULATION_URL = "https://www.bls.gov/news.release/archives/atus_06262025.htm"
POPULATION_SOURCE = "U.S. Bureau of Labor Statistics, American Time Use Survey — 2024 Results"


def population_benchmark() -> dict[str, Any]:
    """A published average. Not a percentile and not a mix with a saved score."""
    return {
        "label": "Population",
        "available": True,
        "value_hours_per_day": POPULATION_HOURS,
        "year": POPULATION_YEAR,
        "geography": POPULATION_GEOGRAPHY,
        "source": POPULATION_SOURCE,
        "url": POPULATION_URL,
        "method": (
            "ATUS annual average for the civilian noninstitutional population age 15 and over. "
            "The 3.1 hour figure is an average day across all people and all days of the week, "
            "including people who did not work that day. It is not a percentile of this user "
            "and it is not combined with a 0–10 self-assessment."
        ),
        "statement": (
            "In 2024, people in the United States age 15 and over spent 3.1 hours per day working."
        ),
    }


def dimension_snapshot(
    key: str,
    assessments: dict[str, int],
    aspirations: dict[str, int],
    history: list[dict[str, Any]],
) -> dict[str, Any]:
    """Current score, saved aspiration, gap, and only the dates that were actually saved."""
    current = assessments.get(key)
    aspiration = aspirations.get(key)
    gap = None
    if current is not None and aspiration is not None:
        gap = int(aspiration) - int(current)
    points = []
    for row in history:
        scores = row.get("scores") or {}
        if key not in scores or not row.get("recorded_at"):
            continue
        points.append({"recorded_at": str(row["recorded_at"]), "score": int(scores[key])})
    return {
        "current": None if current is None else int(current),
        "aspiration": None if aspiration is None else int(aspiration),
        "gap": gap,
        "last_saved": points[-1]["recorded_at"] if points else None,
        "history": points,
    }


def saved_radar_scores(
    dimensions: list[dict[str, Any]], assessments: dict[str, int]
) -> list[tuple[str, int]]:
    """Active dimensions that have a saved self-assessment. Unsaved ones are omitted."""
    scored = []
    for dimension in dimensions:
        if dimension["key"] in assessments:
            scored.append((dimension["name"], int(assessments[dimension["key"]])))
    return scored
