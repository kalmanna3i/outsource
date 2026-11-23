"""Live models sometimes return numeric fields as prose."""

from services.workflow import _to_number


def test_to_number_accepts_numbers_and_prose() -> None:
    assert _to_number(2.5, 0.0) == 2.5
    assert _to_number("about 3 hours", 0.0) == 3.0
    assert _to_number("Unknown; reserve a focused block", 0.0) == 0.0
    assert _to_number(None, 30) == 30
