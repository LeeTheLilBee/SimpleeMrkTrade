
"""Owner-only release candidate and exact decision lifecycle projection / TWR108."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from tower.hosted_owner_release_review import (
    APPROVE_RELEASE,
    HOLD_RELEASE,
    REJECT_RELEASE,
    SAFETY_FALSE_FIELDS,
    owner_release_session_context,
    read_owner_release_decision_receipts,
    validate_owner_release_context,
    verify_owner_release_decision_receipt,
)
from tower.hosted_release_packet_provider import load_canonical_release_packet


OWNER_VERIFICATION_REQUIRED = "OWNER_VERIFICATION_REQUIRED"
NO_CANDIDATE = "NO_CANDIDATE"
STALE_CANDIDATE = "STALE_CANDIDATE"
CANDIDATE_CHANGED = "CANDIDATE_CHANGED"
CANDIDATE_INVALID = "CANDIDATE_INVALID"
DECISION_STATE_UNAVAILABLE = "DECISION_STATE_UNAVAILABLE"
READY_FOR_OWNER_REVIEW = "READY_FOR_OWNER_REVIEW"
OWNER_APPROVED = "OWNER_APPROVED"
OWNER_HELD = "OWNER_HELD"
OWNER_REJECTED = "OWNER_REJECTED"

DECISION_STATES = {
    APPROVE_RELEASE: OWNER_APPROVED,
    HOLD_RELEASE: OWNER_HELD,
    REJECT_RELEASE: OWNER_REJECTED,
}


def _projection(state: str, *, reason: str = "", **extra: Any) -> dict[str, Any]:
    return {
        "status": "tower_owner_release_candidate_state_ready",
        "candidate_state": state,
        "reason": reason,
        "owner_review_required": True,
        "owner_decision_recorded": state in DECISION_STATES.values(),
        "separate_release_execution_gate_required": True,
        **{field: False for field in SAFETY_FALSE_FIELDS},
        **extra,
    }


def project_owner_release_candidate_state(
    *,
    owner_context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    context = owner_context if owner_context is not None else owner_release_session_context()
    validation = validate_owner_release_context(context)
    if not validation.get("valid"):
        return _projection(
            OWNER_VERIFICATION_REQUIRED,
            reason="fresh_owner_session_and_step_up_required",
        )

    candidate = load_canonical_release_packet()
    if not candidate.get("reviewable"):
        reason = str(candidate.get("reason") or "packet_source_missing")
        if reason == "packet_stale_or_future_dated":
            state = STALE_CANDIDATE
        elif reason == "packet_candidate_revision_mismatch":
            state = CANDIDATE_CHANGED
        elif reason in {"packet_source_missing", "expected_candidate_revision_unavailable"}:
            state = NO_CANDIDATE
        else:
            state = CANDIDATE_INVALID
        return _projection(state, reason=reason)

    packet = candidate["packet"]
    receipts = read_owner_release_decision_receipts(owner_context=context)
    if receipts.get("status") != "tower_owner_release_receipts_ready" or receipts.get("chain_valid") is not True:
        return _projection(
            DECISION_STATE_UNAVAILABLE,
            reason="owner_decision_ledger_unavailable_or_invalid",
        )

    for receipt in reversed(receipts.get("receipts", [])):
        if (
            receipt.get("packet_integrity_hash") != packet.get("packet_integrity_hash")
            or receipt.get("expected_revision") != packet.get("expected_revision")
        ):
            continue
        verification = verify_owner_release_decision_receipt(receipt)
        if not verification.get("valid"):
            return _projection(DECISION_STATE_UNAVAILABLE, reason="owner_decision_receipt_integrity_invalid")
        state = DECISION_STATES.get(receipt.get("decision"))
        if not state:
            return _projection(DECISION_STATE_UNAVAILABLE, reason="owner_decision_receipt_decision_invalid")
        return _projection(
            state,
            expected_revision=packet["expected_revision"],
            packet_integrity_hash=packet["packet_integrity_hash"],
            owner_decision=receipt["decision"],
            receipt_id=receipt["receipt_id"],
            decided_at_utc=receipt["decided_at_utc"],
            receipt_integrity_verified=True,
        )

    return _projection(
        READY_FOR_OWNER_REVIEW,
        expected_revision=packet["expected_revision"],
        packet_integrity_hash=packet["packet_integrity_hash"],
        packet_age_seconds=candidate.get("packet_age_seconds", 0),
        owner_decision=None,
        receipt_integrity_verified=False,
    )


def owner_release_dashboard_snapshot() -> dict[str, str]:
    projection = project_owner_release_candidate_state()
    state = projection["candidate_state"]
    labels = {
        OWNER_VERIFICATION_REQUIRED: ("Owner verification needed", "Verify your Tower owner session to inspect release status."),
        NO_CANDIDATE: ("No candidate published", "Run a genuine hosted parity check to prepare owner review."),
        STALE_CANDIDATE: ("Candidate needs refresh", "The published candidate expired; run a fresh hosted parity check."),
        CANDIDATE_CHANGED: ("Candidate revision changed", "The hosted revision changed; verify the exact current candidate."),
        CANDIDATE_INVALID: ("Candidate unavailable", "The candidate could not be verified and remains unavailable."),
        DECISION_STATE_UNAVAILABLE: ("Decision state unavailable", "The owner receipt ledger could not be verified."),
        READY_FOR_OWNER_REVIEW: ("Ready for your review", "A sealed, current hosted candidate is waiting for your decision."),
        OWNER_APPROVED: ("Approved · execution locked", "Your approval is recorded. Deployment and trading remain locked."),
        OWNER_HELD: ("Held for owner review", "Your hold decision is recorded; no execution is authorized."),
        OWNER_REJECTED: ("Rejected · execution locked", "Your rejection is recorded; no execution is authorized."),
    }
    label, detail = labels.get(state, ("Release status unavailable", "Tower could not verify release status."))
    return {"state": state, "label": label, "detail": detail}
