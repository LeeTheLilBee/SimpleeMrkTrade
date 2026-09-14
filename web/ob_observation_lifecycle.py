from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ObservationLifecycleState(str, Enum):
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    HISTORICAL = "HISTORICAL"
    ARCHIVED = "ARCHIVED"
    RETAINED_EVIDENCE = "RETAINED_EVIDENCE"
    UNKNOWN = "UNKNOWN"


class CurrentReasoningEligibility(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    REVIEW_ONLY = "REVIEW_ONLY"
    INELIGIBLE = "INELIGIBLE"
    UNKNOWN = "UNKNOWN"


class RetentionState(str, Enum):
    HOT = "HOT"
    WARM = "WARM"
    ARCHIVE = "ARCHIVE"
    PERMANENT_EVIDENCE = "PERMANENT_EVIDENCE"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ObservationLifecycleAssessment:
    version_status: str
    effective_state: str
    lifecycle: ObservationLifecycleState
    reasoning_eligibility: CurrentReasoningEligibility
    retention: RetentionState
    reasons: tuple[str, ...]


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


def assess_observation_lifecycle(
    *,
    version_status: Any,
    effective_state: Any,
    retain_as_evidence: bool = True,
    archive_requested: bool = False,
) -> ObservationLifecycleAssessment:
    """
    Classify observation lifecycle separately from historical retention.

    Historical retention does not mean current analytical eligibility.
    """

    version = _norm(
        version_status
    )

    effective = _norm(
        effective_state
    )

    if version == "UNKNOWN" or effective == "UNKNOWN":
        return ObservationLifecycleAssessment(
            version_status=version,
            effective_state=effective,
            lifecycle=ObservationLifecycleState.UNKNOWN,
            reasoning_eligibility=CurrentReasoningEligibility.UNKNOWN,
            retention=RetentionState.UNKNOWN,
            reasons=(
                "Lifecycle cannot be established from unknown version or effective state.",
            ),
        )

    if version == "CURRENT":
        if effective in {
            "TRUSTED",
            "USABLE",
        }:
            return ObservationLifecycleAssessment(
                version_status=version,
                effective_state=effective,
                lifecycle=ObservationLifecycleState.ACTIVE,
                reasoning_eligibility=CurrentReasoningEligibility.ELIGIBLE,
                retention=RetentionState.HOT,
                reasons=(
                    "Current version remains eligible for normal analytical reasoning.",
                ),
            )

        if effective == "CAUTION":
            return ObservationLifecycleAssessment(
                version_status=version,
                effective_state=effective,
                lifecycle=ObservationLifecycleState.ACTIVE,
                reasoning_eligibility=CurrentReasoningEligibility.REVIEW_ONLY,
                retention=RetentionState.HOT,
                reasons=(
                    "Current version remains active but requires visible analytical caution.",
                ),
            )

        if effective in {
            "QUARANTINED",
            "UNUSABLE",
        }:
            return ObservationLifecycleAssessment(
                version_status=version,
                effective_state=effective,
                lifecycle=ObservationLifecycleState.RETAINED_EVIDENCE,
                reasoning_eligibility=CurrentReasoningEligibility.INELIGIBLE,
                retention=RetentionState.PERMANENT_EVIDENCE,
                reasons=(
                    "Current record is retained as evidence but cannot serve as current observation truth.",
                ),
            )

    if version == "SUPERSEDED":
        if archive_requested:
            return ObservationLifecycleAssessment(
                version_status=version,
                effective_state=effective,
                lifecycle=ObservationLifecycleState.ARCHIVED,
                reasoning_eligibility=CurrentReasoningEligibility.INELIGIBLE,
                retention=RetentionState.ARCHIVE,
                reasons=(
                    "Superseded version is archived and excluded from current reasoning.",
                ),
            )

        return ObservationLifecycleAssessment(
            version_status=version,
            effective_state=effective,
            lifecycle=ObservationLifecycleState.SUPERSEDED,
            reasoning_eligibility=CurrentReasoningEligibility.INELIGIBLE,
            retention=(
                RetentionState.PERMANENT_EVIDENCE
                if retain_as_evidence
                else RetentionState.WARM
            ),
            reasons=(
                "Superseded version remains historical evidence and is excluded from current reasoning.",
            ),
        )

    if version == "HISTORICAL":
        if archive_requested:
            return ObservationLifecycleAssessment(
                version_status=version,
                effective_state=effective,
                lifecycle=ObservationLifecycleState.ARCHIVED,
                reasoning_eligibility=CurrentReasoningEligibility.INELIGIBLE,
                retention=RetentionState.ARCHIVE,
                reasons=(
                    "Historical observation moved to archive retention.",
                ),
            )

        return ObservationLifecycleAssessment(
            version_status=version,
            effective_state=effective,
            lifecycle=ObservationLifecycleState.HISTORICAL,
            reasoning_eligibility=CurrentReasoningEligibility.INELIGIBLE,
            retention=(
                RetentionState.PERMANENT_EVIDENCE
                if retain_as_evidence
                else RetentionState.WARM
            ),
            reasons=(
                "Historical observation remains retained but is not current analytical truth.",
            ),
        )

    return ObservationLifecycleAssessment(
        version_status=version,
        effective_state=effective,
        lifecycle=ObservationLifecycleState.UNKNOWN,
        reasoning_eligibility=CurrentReasoningEligibility.UNKNOWN,
        retention=RetentionState.UNKNOWN,
        reasons=(
            "Lifecycle state could not be resolved safely.",
        ),
    )


def eligible_for_current_reasoning(
    assessment: ObservationLifecycleAssessment,
) -> bool:
    return (
        assessment.reasoning_eligibility
        is CurrentReasoningEligibility.ELIGIBLE
    )


def requires_current_reasoning_review(
    assessment: ObservationLifecycleAssessment,
) -> bool:
    return (
        assessment.reasoning_eligibility
        is CurrentReasoningEligibility.REVIEW_ONLY
    )


def excluded_from_current_reasoning(
    assessment: ObservationLifecycleAssessment,
) -> bool:
    return (
        assessment.reasoning_eligibility
        is CurrentReasoningEligibility.INELIGIBLE
    )


def retained_for_history(
    assessment: ObservationLifecycleAssessment,
) -> bool:
    return assessment.retention in {
        RetentionState.WARM,
        RetentionState.ARCHIVE,
        RetentionState.PERMANENT_EVIDENCE,
    }


def lifecycle_snapshot(
    assessment: ObservationLifecycleAssessment,
) -> dict[str, object]:
    return {
        "version_status": assessment.version_status,
        "effective_state": assessment.effective_state,
        "lifecycle": assessment.lifecycle.value,
        "reasoning_eligibility": assessment.reasoning_eligibility.value,
        "retention": assessment.retention.value,
        "reasons": list(
            assessment.reasons
        ),
    }
