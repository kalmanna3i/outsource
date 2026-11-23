"""Permission modes that gate autonomous AI execution."""

from __future__ import annotations

from core.models import PermissionMode


def normalize_permission(raw: str | None) -> PermissionMode:
    try:
        return PermissionMode((raw or "MANAGED_AUTONOMY").strip().upper())
    except ValueError:
        return PermissionMode.MANAGED_AUTONOMY


def may_auto_execute(mode: PermissionMode) -> bool:
    """REVIEW_ALL requires explicit human approval before F03 runs."""
    return mode != PermissionMode.REVIEW_ALL
