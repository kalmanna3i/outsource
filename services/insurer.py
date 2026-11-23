"""Simulated insurance identity-verification barrier.

This is intentionally a fixture integration. It never contacts a real insurer
and never invents claim outcomes beyond the labeled simulation.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from core.models import EvidenceRecord, EvidenceType


@dataclass
class InsurerCheckResult:
    claim_ref: str
    status: str
    identity_verification_required: bool
    message: str
    next_human_action: str
    evidence: EvidenceRecord


def check_claim_status(claim_ref: str = "CLAIM-SIM-409") -> InsurerCheckResult:
    """Simulate portal check that hits an identity-verification wall."""
    evidence = EvidenceRecord(
        evidence_type=EvidenceType.SIMULATED_FIXTURE,
        source="simulated://insurer-portal/identity-gate",
        summary=(
            "Simulated insurer portal requires identity verification before claim "
            "details can be disclosed. No live insurer API was called."
        ),
        confidence=1.0,
        agent_id="F03",
        labeled_demo=True,
        retrieved_at=datetime.utcnow(),
    )
    return InsurerCheckResult(
        claim_ref=claim_ref,
        status="IDENTITY_VERIFICATION_REQUIRED",
        identity_verification_required=True,
        message=(
            f"[SIMULATED] Claim {claim_ref}: the portal will not release status "
            "until a human completes identity verification (knowledge-based or ID upload)."
        ),
        next_human_action=(
            "Complete insurer identity verification with phone/ID ready; "
            "then enter the verification result so OUTSOURCE can resume."
        ),
        evidence=evidence,
    )
