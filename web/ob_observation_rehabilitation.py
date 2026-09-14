from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class RehabilitationState(str, Enum):
    NOT_APPLICABLE = "NOT_APPLICABLE"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    APPROVED_FOR_NEW_VERSION = "APPROVED_FOR_NEW_VERSION"
    REJECTED = "REJECTED"
    UNKNOWN = "UNKNOWN"


class RehabilitationReason(str, Enum):
    SOURCE_RESTORED = "SOURCE_RESTORED"
    CORRECTED_DATA = "CORRECTED_DATA"
    PROVENANCE_REESTABLISHED = "PROVENANCE_REESTABLISHED"
    ERROR_CORRECTED = "ERROR_CORRECTED"
    NEW_INDEPENDENT_EVIDENCE = "NEW_INDEPENDENT_EVIDENCE"
    OWNER_REVIEW = "OWNER_REVIEW"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class RehabilitationReview:
    observation_id: str
    revoked_version: int
    revoked_lineage_hash: str
    state: RehabilitationState
    reason: RehabilitationReason | None
    review_note: str
    new_lineage_hash: str | None


@dataclass(frozen=True)
class RehabilitatedObservationVersion:
    observation_id: str
    version: int
    rehabilitates_revoked_version: int
    revoked_lineage_hash: str
    new_lineage_hash: str
    effective_state: str
    confidence: str
    rehabilitation_reason: RehabilitationReason
    review_note: str


def _norm(value: Any) -> str:
    if value is None:
        return "UNKNOWN"

    raw = getattr(
        value,
        "value",
        value,
    )

    text = str(raw).strip().upper()

    return text if text else "UNKNOWN"


def request_rehabilitation_review(
    *,
    observation_id: str,
    revoked_version: int,
    revoked_lineage_hash: str,
    review_note: str,
) -> RehabilitationReview:
    observation_id = observation_id.strip()
    revoked_lineage_hash = revoked_lineage_hash.strip()
    review_note = review_note.strip()

    if not observation_id:
        raise ValueError(
            "observation_id cannot be blank"
        )

    if revoked_version < 1:
        raise ValueError(
            "revoked_version must be >= 1"
        )

    if not revoked_lineage_hash:
        raise ValueError(
            "revoked_lineage_hash cannot be blank"
        )

    if not review_note:
        raise ValueError(
            "review_note cannot be blank"
        )

    return RehabilitationReview(
        observation_id=observation_id,
        revoked_version=revoked_version,
        revoked_lineage_hash=revoked_lineage_hash,
        state=RehabilitationState.REVIEW_REQUIRED,
        reason=None,
        review_note=review_note,
        new_lineage_hash=None,
    )


def approve_rehabilitation(
    review: RehabilitationReview,
    *,
    reason: RehabilitationReason,
    new_lineage_hash: str,
    approval_note: str,
) -> RehabilitationReview:
    new_lineage_hash = new_lineage_hash.strip()
    approval_note = approval_note.strip()

    if review.state is not RehabilitationState.REVIEW_REQUIRED:
        raise ValueError(
            "rehabilitation approval requires REVIEW_REQUIRED state"
        )

    if reason is RehabilitationReason.UNKNOWN:
        raise ValueError(
            "rehabilitation approval requires explicit known reason"
        )

    if not new_lineage_hash:
        raise ValueError(
            "new_lineage_hash cannot be blank"
        )

    if new_lineage_hash == review.revoked_lineage_hash:
        raise ValueError(
            "rehabilitation requires new evidence lineage"
        )

    if not approval_note:
        raise ValueError(
            "approval_note cannot be blank"
        )

    return RehabilitationReview(
        observation_id=review.observation_id,
        revoked_version=review.revoked_version,
        revoked_lineage_hash=review.revoked_lineage_hash,
        state=RehabilitationState.APPROVED_FOR_NEW_VERSION,
        reason=reason,
        review_note=approval_note,
        new_lineage_hash=new_lineage_hash,
    )


def reject_rehabilitation(
    review: RehabilitationReview,
    *,
    reason: RehabilitationReason,
    rejection_note: str,
) -> RehabilitationReview:
    rejection_note = rejection_note.strip()

    if review.state is not RehabilitationState.REVIEW_REQUIRED:
        raise ValueError(
            "rehabilitation rejection requires REVIEW_REQUIRED state"
        )

    if reason is RehabilitationReason.UNKNOWN:
        raise ValueError(
            "rehabilitation rejection requires explicit known reason"
        )

    if not rejection_note:
        raise ValueError(
            "rejection_note cannot be blank"
        )

    return RehabilitationReview(
        observation_id=review.observation_id,
        revoked_version=review.revoked_version,
        revoked_lineage_hash=review.revoked_lineage_hash,
        state=RehabilitationState.REJECTED,
        reason=reason,
        review_note=rejection_note,
        new_lineage_hash=None,
    )


def create_rehabilitated_version(
    review: RehabilitationReview,
    *,
    new_version: int,
    effective_state: Any,
    confidence: Any,
) -> RehabilitatedObservationVersion:
    if review.state is not RehabilitationState.APPROVED_FOR_NEW_VERSION:
        raise ValueError(
            "rehabilitated version requires explicit approval"
        )

    if review.reason is None:
        raise ValueError(
            "approved rehabilitation must preserve reason"
        )

    if review.new_lineage_hash is None:
        raise ValueError(
            "approved rehabilitation must preserve new lineage hash"
        )

    if new_version <= review.revoked_version:
        raise ValueError(
            "rehabilitated version must be newer than revoked predecessor"
        )

    effective = _norm(
        effective_state
    )

    confidence_norm = _norm(
        confidence
    )

    if effective == "UNKNOWN":
        raise ValueError(
            "rehabilitated version requires known effective state"
        )

    if confidence_norm == "UNKNOWN":
        raise ValueError(
            "rehabilitated version requires known confidence"
        )

    return RehabilitatedObservationVersion(
        observation_id=review.observation_id,
        version=new_version,
        rehabilitates_revoked_version=review.revoked_version,
        revoked_lineage_hash=review.revoked_lineage_hash,
        new_lineage_hash=review.new_lineage_hash,
        effective_state=effective,
        confidence=confidence_norm,
        rehabilitation_reason=review.reason,
        review_note=review.review_note,
    )


def rehabilitation_approved(
    review: RehabilitationReview,
) -> bool:
    return (
        review.state
        is RehabilitationState.APPROVED_FOR_NEW_VERSION
    )


def revoked_predecessor_remains_revoked(
    version: RehabilitatedObservationVersion,
) -> bool:
    return (
        version.rehabilitates_revoked_version
        < version.version
        and version.revoked_lineage_hash
        != version.new_lineage_hash
    )


def rehabilitation_snapshot(
    review: RehabilitationReview,
) -> dict[str, object]:
    return {
        "observation_id": review.observation_id,
        "revoked_version": review.revoked_version,
        "revoked_lineage_hash": review.revoked_lineage_hash,
        "state": review.state.value,
        "reason": (
            review.reason.value
            if review.reason is not None
            else None
        ),
        "review_note": review.review_note,
        "new_lineage_hash": review.new_lineage_hash,
    }


def rehabilitated_version_snapshot(
    version: RehabilitatedObservationVersion,
) -> dict[str, object]:
    return {
        "observation_id": version.observation_id,
        "version": version.version,
        "rehabilitates_revoked_version": version.rehabilitates_revoked_version,
        "revoked_lineage_hash": version.revoked_lineage_hash,
        "new_lineage_hash": version.new_lineage_hash,
        "effective_state": version.effective_state,
        "confidence": version.confidence,
        "rehabilitation_reason": version.rehabilitation_reason.value,
        "review_note": version.review_note,
    }
