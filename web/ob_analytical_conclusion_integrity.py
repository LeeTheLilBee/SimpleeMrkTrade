from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class ClaimKind(str, Enum):
    DIRECT = "DIRECT"
    INFERENCE = "INFERENCE"
    UNKNOWN = "UNKNOWN"


class SupportState(str, Enum):
    SUPPORTED = "SUPPORTED"
    PARTIAL = "PARTIAL"
    UNSUPPORTED = "UNSUPPORTED"
    CONFLICTED = "CONFLICTED"
    UNKNOWN = "UNKNOWN"


class UncertaintyState(str, Enum):
    RESOLVED = "RESOLVED"
    MATERIAL = "MATERIAL"
    UNKNOWN = "UNKNOWN"


class ConclusionState(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"
    UNKNOWN = "UNKNOWN"


class ConclusionReason(str, Enum):
    INTEGRITY_SATISFIED = "INTEGRITY_SATISFIED"
    EVIDENCE_NOT_SUFFICIENT = "EVIDENCE_NOT_SUFFICIENT"
    UNSUPPORTED_CLAIM = "UNSUPPORTED_CLAIM"
    DIRECT_CLAIM_NOT_DIRECTLY_SUPPORTED = "DIRECT_CLAIM_NOT_DIRECTLY_SUPPORTED"
    MATERIAL_UNCERTAINTY = "MATERIAL_UNCERTAINTY"
    UNRESOLVED_CONFLICT = "UNRESOLVED_CONFLICT"
    UNKNOWN_SUPPORT = "UNKNOWN_SUPPORT"
    UNKNOWN_CLAIM_KIND = "UNKNOWN_CLAIM_KIND"
    EMPTY_CLAIMS = "EMPTY_CLAIMS"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class AnalyticalClaim:
    claim_id: str
    statement: str
    claim_kind: ClaimKind
    support_state: SupportState
    uncertainty_state: UncertaintyState
    evidence_refs: tuple[str, ...]
    inference_basis: tuple[str, ...]
    unresolved_conflicts: tuple[str, ...]


@dataclass(frozen=True)
class ClaimIntegrityAssessment:
    claim_id: str
    state: ConclusionState
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class AnalyticalConclusionAssessment:
    state: ConclusionState
    reason: ConclusionReason
    claim_assessments: tuple[ClaimIntegrityAssessment, ...]
    unsupported_claim_ids: tuple[str, ...]
    conflicted_claim_ids: tuple[str, ...]
    uncertain_claim_ids: tuple[str, ...]
    reasons: tuple[str, ...]


def _nonblank(value: object, *, name: str) -> str:
    text = str(value).strip()

    if not text:
        raise ValueError(f"{name} cannot be blank")

    return text


def _clean_refs(
    values: Iterable[str],
    *,
    name: str,
) -> tuple[str, ...]:
    result = tuple(
        _nonblank(value, name=name)
        for value in values
    )

    if len(result) != len(set(result)):
        raise ValueError(
            f"{name} cannot contain duplicates"
        )

    return result


def build_analytical_claim(
    *,
    claim_id: str,
    statement: str,
    claim_kind: ClaimKind | str,
    support_state: SupportState | str,
    uncertainty_state: UncertaintyState | str,
    evidence_refs: Iterable[str] = (),
    inference_basis: Iterable[str] = (),
    unresolved_conflicts: Iterable[str] = (),
) -> AnalyticalClaim:
    try:
        kind = (
            claim_kind
            if isinstance(claim_kind, ClaimKind)
            else ClaimKind(str(claim_kind).strip().upper())
        )
    except ValueError:
        kind = ClaimKind.UNKNOWN

    try:
        support = (
            support_state
            if isinstance(support_state, SupportState)
            else SupportState(str(support_state).strip().upper())
        )
    except ValueError:
        support = SupportState.UNKNOWN

    try:
        uncertainty = (
            uncertainty_state
            if isinstance(uncertainty_state, UncertaintyState)
            else UncertaintyState(
                str(uncertainty_state).strip().upper()
            )
        )
    except ValueError:
        uncertainty = UncertaintyState.UNKNOWN

    return AnalyticalClaim(
        claim_id=_nonblank(
            claim_id,
            name="claim_id",
        ),
        statement=_nonblank(
            statement,
            name="statement",
        ),
        claim_kind=kind,
        support_state=support,
        uncertainty_state=uncertainty,
        evidence_refs=_clean_refs(
            evidence_refs,
            name="evidence_ref",
        ),
        inference_basis=_clean_refs(
            inference_basis,
            name="inference_basis",
        ),
        unresolved_conflicts=_clean_refs(
            unresolved_conflicts,
            name="unresolved_conflict",
        ),
    )


def assess_claim_integrity(
    claim: AnalyticalClaim,
) -> ClaimIntegrityAssessment:
    reasons = []

    if claim.claim_kind is ClaimKind.UNKNOWN:
        return ClaimIntegrityAssessment(
            claim_id=claim.claim_id,
            state=ConclusionState.UNKNOWN,
            reasons=(
                "Claim kind is UNKNOWN.",
            ),
        )

    if claim.support_state is SupportState.UNKNOWN:
        return ClaimIntegrityAssessment(
            claim_id=claim.claim_id,
            state=ConclusionState.UNKNOWN,
            reasons=(
                "Claim support state is UNKNOWN.",
            ),
        )

    if claim.support_state is SupportState.UNSUPPORTED:
        return ClaimIntegrityAssessment(
            claim_id=claim.claim_id,
            state=ConclusionState.BLOCKED,
            reasons=(
                "Claim is unsupported by admitted analytical evidence.",
            ),
        )

    if claim.claim_kind is ClaimKind.DIRECT:
        if not claim.evidence_refs:
            return ClaimIntegrityAssessment(
                claim_id=claim.claim_id,
                state=ConclusionState.BLOCKED,
                reasons=(
                    "DIRECT claim has no evidence references.",
                ),
            )

        if claim.inference_basis:
            return ClaimIntegrityAssessment(
                claim_id=claim.claim_id,
                state=ConclusionState.BLOCKED,
                reasons=(
                    "DIRECT claim cannot carry inference basis.",
                ),
            )

        if claim.support_state is not SupportState.SUPPORTED:
            return ClaimIntegrityAssessment(
                claim_id=claim.claim_id,
                state=ConclusionState.BLOCKED,
                reasons=(
                    "DIRECT claim is not directly SUPPORTED.",
                ),
            )

    if claim.claim_kind is ClaimKind.INFERENCE:
        if not claim.inference_basis:
            return ClaimIntegrityAssessment(
                claim_id=claim.claim_id,
                state=ConclusionState.BLOCKED,
                reasons=(
                    "INFERENCE claim must identify its inference basis.",
                ),
            )

        if not claim.evidence_refs:
            return ClaimIntegrityAssessment(
                claim_id=claim.claim_id,
                state=ConclusionState.BLOCKED,
                reasons=(
                    "INFERENCE claim must identify supporting evidence.",
                ),
            )

    if (
        claim.support_state is SupportState.CONFLICTED
        or claim.unresolved_conflicts
    ):
        return ClaimIntegrityAssessment(
            claim_id=claim.claim_id,
            state=ConclusionState.REVIEW_REQUIRED,
            reasons=(
                "Claim contains unresolved evidentiary conflict.",
            ),
        )

    if claim.support_state is SupportState.PARTIAL:
        reasons.append(
            "Claim is only partially supported."
        )

    if claim.uncertainty_state is UncertaintyState.UNKNOWN:
        return ClaimIntegrityAssessment(
            claim_id=claim.claim_id,
            state=ConclusionState.UNKNOWN,
            reasons=(
                "Claim uncertainty state is UNKNOWN.",
            ),
        )

    if claim.uncertainty_state is UncertaintyState.MATERIAL:
        reasons.append(
            "Claim contains material uncertainty."
        )

    if reasons:
        return ClaimIntegrityAssessment(
            claim_id=claim.claim_id,
            state=ConclusionState.REVIEW_REQUIRED,
            reasons=tuple(reasons),
        )

    return ClaimIntegrityAssessment(
        claim_id=claim.claim_id,
        state=ConclusionState.ELIGIBLE,
        reasons=(
            "Claim preserves support type, uncertainty and evidence basis.",
        ),
    )


def assess_analytical_conclusion(
    *,
    sufficiency_state: str,
    claims: Iterable[AnalyticalClaim],
) -> AnalyticalConclusionAssessment:
    normalized_sufficiency = _nonblank(
        sufficiency_state,
        name="sufficiency_state",
    ).upper()

    claim_items = tuple(claims)

    if normalized_sufficiency != "SUFFICIENT":
        state = (
            ConclusionState.UNKNOWN
            if normalized_sufficiency == "UNKNOWN"
            else ConclusionState.BLOCKED
        )

        return AnalyticalConclusionAssessment(
            state=state,
            reason=ConclusionReason.EVIDENCE_NOT_SUFFICIENT,
            claim_assessments=(),
            unsupported_claim_ids=(),
            conflicted_claim_ids=(),
            uncertain_claim_ids=(),
            reasons=(
                (
                    "Candidate evidence sufficiency is "
                    f"{normalized_sufficiency}, not SUFFICIENT."
                ),
                "Analytical conclusion eligibility fails closed.",
            ),
        )

    if not claim_items:
        return AnalyticalConclusionAssessment(
            state=ConclusionState.BLOCKED,
            reason=ConclusionReason.EMPTY_CLAIMS,
            claim_assessments=(),
            unsupported_claim_ids=(),
            conflicted_claim_ids=(),
            uncertain_claim_ids=(),
            reasons=(
                "No analytical claims were supplied.",
            ),
        )

    ids = tuple(
        claim.claim_id
        for claim in claim_items
    )

    if len(ids) != len(set(ids)):
        return AnalyticalConclusionAssessment(
            state=ConclusionState.BLOCKED,
            reason=ConclusionReason.UNKNOWN,
            claim_assessments=(),
            unsupported_claim_ids=(),
            conflicted_claim_ids=(),
            uncertain_claim_ids=(),
            reasons=(
                "Duplicate analytical claim IDs detected.",
            ),
        )

    assessments = tuple(
        assess_claim_integrity(claim)
        for claim in claim_items
    )

    unsupported = tuple(
        sorted(
            claim.claim_id
            for claim in claim_items
            if claim.support_state is SupportState.UNSUPPORTED
        )
    )

    conflicted = tuple(
        sorted(
            claim.claim_id
            for claim in claim_items
            if (
                claim.support_state is SupportState.CONFLICTED
                or bool(claim.unresolved_conflicts)
            )
        )
    )

    uncertain = tuple(
        sorted(
            claim.claim_id
            for claim in claim_items
            if claim.uncertainty_state is not UncertaintyState.RESOLVED
        )
    )

    blocked = tuple(
        assessment
        for assessment in assessments
        if assessment.state is ConclusionState.BLOCKED
    )

    unknown = tuple(
        assessment
        for assessment in assessments
        if assessment.state is ConclusionState.UNKNOWN
    )

    review = tuple(
        assessment
        for assessment in assessments
        if assessment.state is ConclusionState.REVIEW_REQUIRED
    )

    if unsupported:
        return AnalyticalConclusionAssessment(
            state=ConclusionState.BLOCKED,
            reason=ConclusionReason.UNSUPPORTED_CLAIM,
            claim_assessments=assessments,
            unsupported_claim_ids=unsupported,
            conflicted_claim_ids=conflicted,
            uncertain_claim_ids=uncertain,
            reasons=(
                "One or more analytical claims are unsupported.",
            ),
        )

    if blocked:
        direct_failures = tuple(
            claim.claim_id
            for claim, assessment in zip(
                claim_items,
                assessments,
            )
            if (
                assessment.state is ConclusionState.BLOCKED
                and claim.claim_kind is ClaimKind.DIRECT
            )
        )

        reason = (
            ConclusionReason.DIRECT_CLAIM_NOT_DIRECTLY_SUPPORTED
            if direct_failures
            else ConclusionReason.UNKNOWN
        )

        return AnalyticalConclusionAssessment(
            state=ConclusionState.BLOCKED,
            reason=reason,
            claim_assessments=assessments,
            unsupported_claim_ids=unsupported,
            conflicted_claim_ids=conflicted,
            uncertain_claim_ids=uncertain,
            reasons=(
                "One or more analytical claims fail integrity requirements.",
            ),
        )

    if unknown:
        unknown_kind = any(
            claim.claim_kind is ClaimKind.UNKNOWN
            for claim in claim_items
        )

        return AnalyticalConclusionAssessment(
            state=ConclusionState.UNKNOWN,
            reason=(
                ConclusionReason.UNKNOWN_CLAIM_KIND
                if unknown_kind
                else ConclusionReason.UNKNOWN_SUPPORT
            ),
            claim_assessments=assessments,
            unsupported_claim_ids=unsupported,
            conflicted_claim_ids=conflicted,
            uncertain_claim_ids=uncertain,
            reasons=(
                "One or more analytical claims have unknown integrity state.",
            ),
        )

    if conflicted:
        return AnalyticalConclusionAssessment(
            state=ConclusionState.REVIEW_REQUIRED,
            reason=ConclusionReason.UNRESOLVED_CONFLICT,
            claim_assessments=assessments,
            unsupported_claim_ids=unsupported,
            conflicted_claim_ids=conflicted,
            uncertain_claim_ids=uncertain,
            reasons=(
                "Unresolved evidentiary conflict is preserved.",
            ),
        )

    if review or uncertain:
        return AnalyticalConclusionAssessment(
            state=ConclusionState.REVIEW_REQUIRED,
            reason=ConclusionReason.MATERIAL_UNCERTAINTY,
            claim_assessments=assessments,
            unsupported_claim_ids=unsupported,
            conflicted_claim_ids=conflicted,
            uncertain_claim_ids=uncertain,
            reasons=(
                "Material uncertainty or partial support remains.",
            ),
        )

    return AnalyticalConclusionAssessment(
        state=ConclusionState.ELIGIBLE,
        reason=ConclusionReason.INTEGRITY_SATISFIED,
        claim_assessments=assessments,
        unsupported_claim_ids=(),
        conflicted_claim_ids=(),
        uncertain_claim_ids=(),
        reasons=(
            "All analytical claims preserve evidence basis, support type and uncertainty integrity.",
            "ELIGIBLE means eligible as an analytical conclusion only.",
        ),
    )


def eligible_analytical_conclusion(
    assessment: AnalyticalConclusionAssessment,
) -> bool:
    return assessment.state is ConclusionState.ELIGIBLE


def analytical_conclusion_snapshot(
    assessment: AnalyticalConclusionAssessment,
) -> dict[str, object]:
    return {
        "state": assessment.state.value,
        "reason": assessment.reason.value,
        "unsupported_claim_ids": list(
            assessment.unsupported_claim_ids
        ),
        "conflicted_claim_ids": list(
            assessment.conflicted_claim_ids
        ),
        "uncertain_claim_ids": list(
            assessment.uncertain_claim_ids
        ),
        "reasons": list(assessment.reasons),
        "claim_assessments": [
            {
                "claim_id": item.claim_id,
                "state": item.state.value,
                "reasons": list(item.reasons),
            }
            for item in assessment.claim_assessments
        ],
        "authority_boundary": {
            "analytical_conclusion_integrity_only": True,
            "trade_recommendation": False,
            "trade_ranking": False,
            "contract_auto_selection": False,
            "broker_submission": False,
            "capital_movement": False,
            "manual_live_unlock": False,
            "hybrid_execution": False,
            "automated_execution": False,
        },
    }
