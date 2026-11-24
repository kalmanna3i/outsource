"""Editable Life Mandate. The user approves revisions. The office does not rewrite the mission."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field

from core.models import new_id


class MandateStatus(str, Enum):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"


class LifeMandate(BaseModel):
    """Persistent personal constitution. Success is the user's sentence, not a score."""

    mandate_id: str = Field(default_factory=lambda: new_id("mandate"))
    revision: int = 1
    status: MandateStatus = MandateStatus.DRAFT
    display_name: str = "OUTSOURCE"
    philosophy: str = "The art of building an intentional life."
    promise: str = "Every dimension of you. One intentional life."
    mission: str = ""
    vision: str = ""
    values: list[str] = Field(default_factory=list)
    principles: list[str] = Field(default_factory=list)
    success_definition: str = ""
    legacy: str = ""
    long_objectives: list[str] = Field(default_factory=list)
    short_objectives: list[str] = Field(default_factory=list)
    nonnegotiables: list[str] = Field(default_factory=list)
    priorities: list[str] = Field(default_factory=list)
    risk_posture: str = ""
    lifestyle: str = ""
    time_budget_hours_week: float = 20.0
    money_budget_usd_month: float = 400.0
    energy_note: str = ""
    recovery_note: str = ""
    approved_at: datetime | None = None
    approved_by: str = ""
    change_note: str = ""


def _lines(items: list[str]) -> list[str]:
    return [item.strip() for item in items if item and item.strip()]


def default_life_mandate() -> LifeMandate:
    return LifeMandate(
        mission=(
            "Build an intentional life: protect the people and the work that matter, "
            "and do not treat busyness as success."
        ),
        vision="A week with room for coursework, friendship, and recovery.",
        values=["humanity beside achievement", "honesty about what is unfinished"],
        principles=[
            "Do not fill every hour",
            "Do not invent a definition of success for the user",
        ],
        success_definition=(
            "I decide what a good week is. A full calendar is not the definition."
        ),
        legacy="Useful work and a life that still has unscheduled time.",
        long_objectives=["Stay present for people while finishing the MBA"],
        short_objectives=["Finish the MGT 409 submission without dropping a fixed personal commitment"],
        nonnegotiables=["No travel during the coursework deadline week"],
        priorities=["friendship", "coursework", "recovery"],
        risk_posture="Name conflicts. Do not auto-block or rewrite the mission.",
        lifestyle="Leave unscheduled time on purpose.",
        energy_note="Energy is finite. More completed tasks are not a better life.",
        recovery_note="Recovery time is user-stated. The office does not infer a diagnosis.",
        status=MandateStatus.DRAFT,
    )


def fictional_executive_mandate() -> LifeMandate:
    """Fictional MBA executive. Not a real person and not a pilot user."""
    return LifeMandate(
        display_name="OUTSOURCE",
        philosophy="The art of building an intentional life.",
        promise="Every dimension of you. One intentional life.",
        mission=(
            "Keep the infrastructure company honest, finish the MBA, and stay a good friend "
            "to people and to my dog — without pretending every hour must be optimized."
        ),
        vision=(
            "An intentional week: coursework, one philanthropic contribution, friendships, "
            "home, health, and the dog. Travel waits."
        ),
        values=[
            "achievement and humanity together",
            "reciprocal giving",
            "finite time, money, energy, and attention",
        ],
        principles=[
            "Friendships are not instruments",
            "Do not spend energy I have not got",
            "Success is defined by me, not by the software",
        ],
        success_definition=(
            "I decide what a good week is. This week: submit coursework, walk the dog, "
            "and see one friend. A full calendar is not the goal."
        ),
        legacy="Useful infrastructure and a life that still has dinner at home.",
        long_objectives=[
            "Grow as an infrastructure operator without treating colleagues as a network to harvest",
            "Give time to one community organization",
        ],
        short_objectives=[
            "Protect the coursework deadline week",
            "One stacked philanthropic conversation, not five committees",
            "Keep a home dinner on the calendar",
        ],
        nonnegotiables=[
            "No travel during the coursework deadline week",
            "Dog care and a recovery evening are mandatory",
            "Do not send email or spend money without me",
        ],
        priorities=["philanthropy", "infrastructure", "friendship"],
        risk_posture="Name conflicts with nonnegotiables. Do not rewrite the mission to remove them.",
        lifestyle="Infrastructure job by day. Evenings are not a second shift unless I say so.",
        time_budget_hours_week=20,
        money_budget_usd_month=400,
        energy_note="Attention is the scarce resource. Do not fill it.",
        recovery_note=(
            "I want an early night twice this week. That is my statement, not a medical finding."
        ),
        status=MandateStatus.DRAFT,
        change_note="Fictional executive scenario draft. Not approved until the user clicks Approve.",
    )


def approved_citations(mandate: LifeMandate) -> list[str]:
    """Quotes the user already approved. Empty when the revision is still a draft."""
    if mandate.status != MandateStatus.APPROVED:
        return []
    cited = [f"mission: {mandate.mission}"]
    for index, priority in enumerate(_lines(mandate.priorities)):
        cited.append(f"priority[{index}]: {priority}")
    for rule in _lines(mandate.nonnegotiables):
        cited.append(f"nonnegotiable: {rule}")
    if mandate.success_definition.strip():
        cited.append(f"success (user-authored): {mandate.success_definition.strip()}")
    return cited


def name_conflicts(text: str, conflict_keywords: list[str], mandate: LifeMandate) -> list[str]:
    """Name clashes with nonnegotiables. Does not edit the mission or hide the option."""
    blob = " ".join(mandate.nonnegotiables).lower()
    notes: list[str] = []
    for keyword in conflict_keywords:
        if keyword.lower() in blob:
            notes.append(
                f"{text} conflicts with a nonnegotiable that mentions '{keyword}'. "
                "The conflict is named. The mission was not rewritten and the option was not deleted."
            )
    return notes


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
