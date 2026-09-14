from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class InvalidationState(str, Enum):
    VALID = "VALID"
    REVOKED = "REVOKED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    UNKNOWN = "UNKNOWN"


class RevocationReason(str, Enum):
    SOURCE_COMPROMISED = "SOURCE_COMPROMISED"
    DATA_CORRUPTION = "DATA_CORRUPTION"
    PROVENANCE_FAILURE = "PROVENANCE_FAILURE"
    MATERIAL_ERROR = "MATERIAL_ERROR"
    IMPOSSIBLE_OBSERVATION = "IMPOSSIBLE_OBSERVATION"
    OWNER_REVIEW = "OWNER_REVIEW"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"


class RevokedReasoningUse(str, Enum):
    CURRENT_TRUTH_ALLOWED = "CURRENT_TRUTH_ALLOWED"
    HISTORICAL_WITH_WARNING_ONLY = "HISTORICAL_WITH_WARNING_ONLY"
    BLOCKED = "BLOCKED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ObservationRevocationAssessment:
    observation_id: str
    version: int
    invalidation: InvalidationState
    reason: RevocationReason | None
    reasoning_use: RevokedReasoningUse
    original_effective_state: str
    lineage_hash: str
    notes: tuple[str, ...]


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


def valid_observation(
    *,
    observation_id: str,
    version: int,
    effective_state: Any,
    lineage_hash: str,
) -> ObservationRevocationAssessment:
    observation_id = observation_id.strip()
    lineage_hash = lineage_hash.strip()

    if not observation_id:
        raise ValueError(
            "observation_id cannot be blank"
        )

    if version < 1:
        raise ValueError(
            "version must be >= 1"
        )

    if not lineage_hash:
        raise ValueError(
            "lineage_hash cannot be blank"
        )

    effective = _norm(
        effective_state
    )

    if effective == "UNKNOWN":
        return ObservationRevocationAssessment(
            observation_id=observation_id,
            version=version,
            invalidation=InvalidationState.UNKNOWN,
            reason=None,
            reasoning_use=RevokedReasoningUse.UNKNOWN,
            original_effective_state=effective,
            lineage_hash=lineage_hash,
            notes=(
                "Observation validity cannot be established from an unknown effective state.",
            ),
        )

    return ObservationRevocationAssessment(
        observation_id=observation_id,
        version=version,
        invalidation=InvalidationState.VALID,
        reason=None,
        reasoning_use=RevokedReasoningUse.CURRENT_TRUTH_ALLOWED,
        original_effective_state=effective,
        lineage_hash=lineage_hash,
        notes=(
            "Observation has not been revoked.",
        ),
    )


def revoke_observation(
    *,
    observation_id: str,
    version: int,
    effective_state: Any,
    lineage_hash: str,
    reason: RevocationReason,
    note: str,
) -> ObservationRevocationAssessment:
    observation_id = observation_id.strip()
    lineage_hash = lineage_hash.strip()
    note = note.strip()

    if not observation_id:
        raise ValueError(
            "observation_id cannot be blank"
        )

    if version < 1:
        raise ValueError(
            "version must be >= 1"
        )

    if not lineage_hash:
        raise ValueError(
            "lineage_hash cannot be blank"
        )

    if reason is RevocationReason.UNKNOWN:
        raise ValueError(
            "explicit revocation cannot use UNKNOWN reason"
        )

    if not note:
        raise ValueError(
            "revocation note cannot be blank"
        )

    return ObservationRevocationAssessment(
        observation_id=observation_id,
        version=version,
        invalidation=InvalidationState.REVOKED,
        reason=reason,
        reasoning_use=RevokedReasoningUse.HISTORICAL_WITH_WARNING_ONLY,
        original_effective_state=_norm(
            effective_state
        ),
        lineage_hash=lineage_hash,
        notes=(
            note,
            "Revoked observation remains retained as historical evidence.",
            "Revoked observation must not be used as current observation truth.",
        ),
    )


def request_revocation_review(
    *,
    observation_id: str,
    version: int,
    effective_state: Any,
    lineage_hash: str,
    note: str,
) -> ObservationRevocationAssessment:
    observation_id = observation_id.strip()
    lineage_hash = lineage_hash.strip()
    note = note.strip()

    if not observation_id:
        raise ValueError(
            "observation_id cannot be blank"
        )

    if version < 1:
        raise ValueError(
            "version must be >= 1"
        )

    if not lineage_hash:
        raise ValueError(
            "lineage_hash cannot be blank"
        )

    if not note:
        raise ValueError(
            "review note cannot be blank"
        )

    return ObservationRevocationAssessment(
        observation_id=observation_id,
        version=version,
        invalidation=InvalidationState.REVIEW_REQUIRED,
        reason=None,
        reasoning_use=RevokedReasoningUse.BLOCKED,
        original_effective_state=_norm(
            effective_state
        ),
        lineage_hash=lineage_hash,
        notes=(
            note,
            "Observation use is blocked while revocation review remains unresolved.",
        ),
    )


def may_be_used_as_current_truth(
    assessment: ObservationRevocationAssessment,
) -> bool:
    return (
        assessment.invalidation
        is InvalidationState.VALID
        and assessment.reasoning_use
        is RevokedReasoningUse.CURRENT_TRUTH_ALLOWED
    )


def must_show_revocation_warning(
    assessment: ObservationRevocationAssessment,
) -> bool:
    return (
        assessment.invalidation
        is InvalidationState.REVOKED
    )


def blocked_from_current_reasoning(
    assessment: ObservationRevocationAssessment,
) -> bool:
    return assessment.invalidation in {
        InvalidationState.REVOKED,
        InvalidationState.REVIEW_REQUIRED,
        InvalidationState.UNKNOWN,
    }


def revocation_snapshot(
    assessment: ObservationRevocationAssessment,
) -> dict[str, object]:
    return {
        "observation_id": assessment.observation_id,
        "version": assessment.version,
        "invalidation": assessment.invalidation.value,
        "reason": (
            assessment.reason.value
            if assessment.reason is not None
            else None
        ),
        "reasoning_use": assessment.reasoning_use.value,
        "original_effective_state": assessment.original_effective_state,
        "lineage_hash": assessment.lineage_hash,
        "notes": list(
            assessment.notes
        ),
    }
