from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable


class ConflictState(str, Enum):
    NONE = "NONE"
    RECONCILABLE = "RECONCILABLE"
    AMBIGUOUS = "AMBIGUOUS"
    MATERIAL = "MATERIAL"
    UNRESOLVED = "UNRESOLVED"
    UNKNOWN = "UNKNOWN"


class ResolutionState(str, Enum):
    NO_ACTION = "NO_ACTION"
    PRESERVE_ALL = "PRESERVE_ALL"
    ANALYTICALLY_RECONCILED = "ANALYTICALLY_RECONCILED"
    ESCALATE = "ESCALATE"
    BLOCK = "BLOCK"
    UNKNOWN = "UNKNOWN"


class EscalationLevel(str, Enum):
    NONE = "NONE"
    REVIEW = "REVIEW"
    OWNER_REVIEW = "OWNER_REVIEW"
    HARD_BLOCK = "HARD_BLOCK"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ConflictObservation:
    source_id: str
    value: Any
    effective_state: str
    confidence: str

    def __post_init__(self) -> None:
        if not self.source_id.strip():
            raise ValueError("source_id cannot be blank")


@dataclass(frozen=True)
class ConflictAssessment:
    conflict: ConflictState
    resolution: ResolutionState
    escalation: EscalationLevel
    observations: tuple[ConflictObservation, ...]
    reasons: tuple[str, ...]
    preserved_source_ids: tuple[str, ...]
    selected_source_id: str | None


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


def assess_observation_conflict(
    observations: Iterable[ConflictObservation],
    *,
    corroboration_state: Any,
) -> ConflictAssessment:
    """
    Assess conflict without silently choosing a source winner.

    This function may classify whether evidence is reconcilable,
    ambiguous, materially conflicted, or unresolved.

    It never grants trading or capital authority.
    """

    supplied = tuple(
        observations
    )

    if not supplied:
        return ConflictAssessment(
            conflict=ConflictState.UNKNOWN,
            resolution=ResolutionState.UNKNOWN,
            escalation=EscalationLevel.UNKNOWN,
            observations=(),
            reasons=(
                "No observations supplied.",
            ),
            preserved_source_ids=(),
            selected_source_id=None,
        )

    seen = set()

    for item in supplied:
        if item.source_id in seen:
            raise ValueError(
                f"duplicate source_id: {item.source_id}"
            )

        seen.add(
            item.source_id
        )

    preserved = tuple(
        item.source_id
        for item in supplied
    )

    effective_states = tuple(
        _norm(item.effective_state)
        for item in supplied
    )

    confidences = tuple(
        _norm(item.confidence)
        for item in supplied
    )

    corroboration = _norm(
        corroboration_state
    )

    # ----------------------------------------------------------------------------------------------------------
    # HARD INVALID / BLOCK CONDITIONS
    # ----------------------------------------------------------------------------------------------------------

    if any(
        state in {
            "UNUSABLE",
            "QUARANTINED",
        }
        for state in effective_states
    ):
        return ConflictAssessment(
            conflict=ConflictState.MATERIAL,
            resolution=ResolutionState.BLOCK,
            escalation=EscalationLevel.HARD_BLOCK,
            observations=supplied,
            reasons=(
                "At least one observation is unusable or quarantined.",
                "Conflict cannot be resolved by selecting another source silently.",
            ),
            preserved_source_ids=preserved,
            selected_source_id=None,
        )

    # ----------------------------------------------------------------------------------------------------------
    # UNKNOWN AUTHORITY
    # ----------------------------------------------------------------------------------------------------------

    if any(
        state == "UNKNOWN"
        for state in effective_states
    ) or any(
        confidence == "UNKNOWN"
        for confidence in confidences
    ):
        return ConflictAssessment(
            conflict=ConflictState.UNRESOLVED,
            resolution=ResolutionState.ESCALATE,
            escalation=EscalationLevel.OWNER_REVIEW,
            observations=supplied,
            reasons=(
                "One or more observations lack sufficient authority evidence.",
            ),
            preserved_source_ids=preserved,
            selected_source_id=None,
        )

    # ----------------------------------------------------------------------------------------------------------
    # NO CONFLICT
    # ----------------------------------------------------------------------------------------------------------

    if corroboration == "CORROBORATED":
        return ConflictAssessment(
            conflict=ConflictState.NONE,
            resolution=ResolutionState.NO_ACTION,
            escalation=EscalationLevel.NONE,
            observations=supplied,
            reasons=(
                "Independent observations are corroborated.",
            ),
            preserved_source_ids=preserved,
            selected_source_id=None,
        )

    # ----------------------------------------------------------------------------------------------------------
    # RECONCILABLE / MINOR DIFFERENCE
    # ----------------------------------------------------------------------------------------------------------

    if corroboration == "MINOR_DISAGREEMENT":

        if all(
            state in {
                "TRUSTED",
                "USABLE",
                "CAUTION",
            }
            for state in effective_states
        ):
            return ConflictAssessment(
                conflict=ConflictState.RECONCILABLE,
                resolution=ResolutionState.ANALYTICALLY_RECONCILED,
                escalation=EscalationLevel.REVIEW,
                observations=supplied,
                reasons=(
                    "Sources show minor disagreement.",
                    "All observations remain analytically usable.",
                    "Reconciliation preserves every source rather than selecting a winner.",
                ),
                preserved_source_ids=preserved,
                selected_source_id=None,
            )

    # ----------------------------------------------------------------------------------------------------------
    # MATERIAL DISAGREEMENT
    # ----------------------------------------------------------------------------------------------------------

    if corroboration == "MATERIAL_DISAGREEMENT":
        return ConflictAssessment(
            conflict=ConflictState.AMBIGUOUS,
            resolution=ResolutionState.PRESERVE_ALL,
            escalation=EscalationLevel.OWNER_REVIEW,
            observations=supplied,
            reasons=(
                "Material disagreement must remain visible.",
                "Multiple viable observations are preserved for owner review.",
            ),
            preserved_source_ids=preserved,
            selected_source_id=None,
        )

    # ----------------------------------------------------------------------------------------------------------
    # CONFLICTED
    # ----------------------------------------------------------------------------------------------------------

    if corroboration == "CONFLICTED":
        return ConflictAssessment(
            conflict=ConflictState.MATERIAL,
            resolution=ResolutionState.ESCALATE,
            escalation=EscalationLevel.OWNER_REVIEW,
            observations=supplied,
            reasons=(
                "Cross-source evidence is materially conflicted.",
                "OB cannot safely reconcile the conflict automatically.",
            ),
            preserved_source_ids=preserved,
            selected_source_id=None,
        )

    # ----------------------------------------------------------------------------------------------------------
    # SINGLE SOURCE
    # ----------------------------------------------------------------------------------------------------------

    if corroboration == "SINGLE_SOURCE":
        return ConflictAssessment(
            conflict=ConflictState.NONE,
            resolution=ResolutionState.NO_ACTION,
            escalation=EscalationLevel.NONE,
            observations=supplied,
            reasons=(
                "Only one independent usable source is present; there is no cross-source conflict to resolve.",
            ),
            preserved_source_ids=preserved,
            selected_source_id=None,
        )

    # ----------------------------------------------------------------------------------------------------------
    # FALLBACK UNKNOWN
    # ----------------------------------------------------------------------------------------------------------

    return ConflictAssessment(
        conflict=ConflictState.UNKNOWN,
        resolution=ResolutionState.ESCALATE,
        escalation=EscalationLevel.OWNER_REVIEW,
        observations=supplied,
        reasons=(
            "Conflict state could not be established safely.",
        ),
        preserved_source_ids=preserved,
        selected_source_id=None,
    )


def may_continue_normal_reasoning(
    assessment: ConflictAssessment,
) -> bool:
    return assessment.resolution in {
        ResolutionState.NO_ACTION,
        ResolutionState.ANALYTICALLY_RECONCILED,
    }


def requires_owner_review(
    assessment: ConflictAssessment,
) -> bool:
    return assessment.escalation is EscalationLevel.OWNER_REVIEW


def must_block_observation_truth(
    assessment: ConflictAssessment,
) -> bool:
    return assessment.escalation is EscalationLevel.HARD_BLOCK


def preserves_ambiguity(
    assessment: ConflictAssessment,
) -> bool:
    return assessment.resolution in {
        ResolutionState.PRESERVE_ALL,
        ResolutionState.ESCALATE,
        ResolutionState.BLOCK,
    }


def conflict_snapshot(
    assessment: ConflictAssessment,
) -> dict[str, object]:
    return {
        "conflict": assessment.conflict.value,
        "resolution": assessment.resolution.value,
        "escalation": assessment.escalation.value,
        "selected_source_id": assessment.selected_source_id,
        "preserved_source_ids": list(
            assessment.preserved_source_ids
        ),
        "observations": [
            {
                "source_id": item.source_id,
                "value": item.value,
                "effective_state": item.effective_state,
                "confidence": item.confidence,
            }
            for item in assessment.observations
        ],
        "reasons": list(
            assessment.reasons
        ),
    }
