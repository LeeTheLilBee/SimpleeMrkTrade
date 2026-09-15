from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class SufficiencyState(str, Enum):
    SUFFICIENT = "SUFFICIENT"
    INSUFFICIENT = "INSUFFICIENT"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"
    UNKNOWN = "UNKNOWN"


class SufficiencyReason(str, Enum):
    REQUIREMENTS_SATISFIED = "REQUIREMENTS_SATISFIED"
    REQUIRED_CATEGORY_MISSING = "REQUIRED_CATEGORY_MISSING"
    INDEPENDENT_SUPPORT_MISSING = "INDEPENDENT_SUPPORT_MISSING"
    INDEPENDENCE_INTEGRITY_BLOCKED = "INDEPENDENCE_INTEGRITY_BLOCKED"
    INDEPENDENCE_REVIEW_REQUIRED = "INDEPENDENCE_REVIEW_REQUIRED"
    UNRESOLVED_EVIDENCE = "UNRESOLVED_EVIDENCE"
    UNKNOWN_REQUIREMENT = "UNKNOWN_REQUIREMENT"
    EMPTY_REQUIREMENTS = "EMPTY_REQUIREMENTS"
    EMPTY_EVIDENCE = "EMPTY_EVIDENCE"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class EvidenceRequirement:
    category: str
    minimum_observations: int
    minimum_independent_confirmations: int
    required: bool


@dataclass(frozen=True)
class CandidateEvidenceSupport:
    observation_id: str
    observation_version: int
    category: str
    independence_family_id: str
    dependency_known: bool


@dataclass(frozen=True)
class CategorySufficiencyAssessment:
    category: str
    required: bool
    observation_count: int
    independent_confirmation_count: int
    unresolved_dependency_count: int
    minimum_observations: int
    minimum_independent_confirmations: int
    satisfied: bool
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class CandidateEvidenceSufficiencyAssessment:
    state: SufficiencyState
    reason: SufficiencyReason
    category_assessments: tuple[CategorySufficiencyAssessment, ...]
    missing_required_categories: tuple[str, ...]
    insufficient_independent_categories: tuple[str, ...]
    unresolved_categories: tuple[str, ...]
    reasons: tuple[str, ...]


def _nonblank(value: object, *, name: str) -> str:
    text = str(value).strip()

    if not text:
        raise ValueError(
            f"{name} cannot be blank"
        )

    return text


def _category(value: object) -> str:
    return _nonblank(
        value,
        name="category",
    ).upper()


def build_evidence_requirement(
    *,
    category: str,
    minimum_observations: int,
    minimum_independent_confirmations: int,
    required: bool = True,
) -> EvidenceRequirement:
    normalized_category = _category(
        category
    )

    if minimum_observations < 1:
        raise ValueError(
            "minimum_observations must be >= 1"
        )

    if minimum_independent_confirmations < 1:
        raise ValueError(
            "minimum_independent_confirmations must be >= 1"
        )

    if (
        minimum_independent_confirmations
        > minimum_observations
    ):
        raise ValueError(
            "minimum_independent_confirmations cannot exceed minimum_observations"
        )

    return EvidenceRequirement(
        category=normalized_category,
        minimum_observations=minimum_observations,
        minimum_independent_confirmations=minimum_independent_confirmations,
        required=bool(
            required
        ),
    )


def build_candidate_evidence_support(
    *,
    observation_id: str,
    observation_version: int,
    category: str,
    independence_family_id: str,
    dependency_known: bool = True,
) -> CandidateEvidenceSupport:
    if observation_version < 1:
        raise ValueError(
            "observation_version must be >= 1"
        )

    return CandidateEvidenceSupport(
        observation_id=_nonblank(
            observation_id,
            name="observation_id",
        ),
        observation_version=observation_version,
        category=_category(
            category
        ),
        independence_family_id=_nonblank(
            independence_family_id,
            name="independence_family_id",
        ),
        dependency_known=bool(
            dependency_known
        ),
    )


def assess_category_sufficiency(
    *,
    requirement: EvidenceRequirement,
    evidence: Iterable[CandidateEvidenceSupport],
) -> CategorySufficiencyAssessment:
    matching = tuple(
        item
        for item in evidence
        if item.category == requirement.category
    )

    known = tuple(
        item
        for item in matching
        if item.dependency_known
    )

    unresolved = tuple(
        item
        for item in matching
        if not item.dependency_known
    )

    independent_families = {
        item.independence_family_id
        for item in known
    }

    observation_count = len(
        matching
    )

    independent_count = len(
        independent_families
    )

    reasons = []

    if (
        observation_count
        < requirement.minimum_observations
    ):
        reasons.append(
            (
                f"{requirement.category} has {observation_count} observation(s); "
                f"{requirement.minimum_observations} required."
            )
        )

    if (
        independent_count
        < requirement.minimum_independent_confirmations
    ):
        reasons.append(
            (
                f"{requirement.category} has {independent_count} independently "
                f"supported family/families; "
                f"{requirement.minimum_independent_confirmations} required."
            )
        )

    if unresolved:
        reasons.append(
            (
                f"{len(unresolved)} {requirement.category} observation(s) have "
                "unresolved dependency provenance and receive no independent-support credit."
            )
        )

    satisfied = (
        observation_count
        >= requirement.minimum_observations
        and independent_count
        >= requirement.minimum_independent_confirmations
        and not unresolved
    )

    if satisfied:
        reasons.append(
            (
                f"{requirement.category} satisfies observation-count and "
                "independent-support requirements."
            )
        )

    return CategorySufficiencyAssessment(
        category=requirement.category,
        required=requirement.required,
        observation_count=observation_count,
        independent_confirmation_count=independent_count,
        unresolved_dependency_count=len(
            unresolved
        ),
        minimum_observations=requirement.minimum_observations,
        minimum_independent_confirmations=(
            requirement.minimum_independent_confirmations
        ),
        satisfied=satisfied,
        reasons=tuple(
            reasons
        ),
    )


def assess_candidate_evidence_sufficiency(
    *,
    requirements: Iterable[EvidenceRequirement],
    evidence: Iterable[CandidateEvidenceSupport],
    independence_integrity_state: str,
) -> CandidateEvidenceSufficiencyAssessment:
    requirement_items = tuple(
        requirements
    )

    evidence_items = tuple(
        evidence
    )

    integrity_state = _nonblank(
        independence_integrity_state,
        name="independence_integrity_state",
    ).upper()

    if integrity_state == "BLOCKED":
        return CandidateEvidenceSufficiencyAssessment(
            state=SufficiencyState.BLOCKED,
            reason=SufficiencyReason.INDEPENDENCE_INTEGRITY_BLOCKED,
            category_assessments=(),
            missing_required_categories=(),
            insufficient_independent_categories=(),
            unresolved_categories=(),
            reasons=(
                "Evidence independence / corroboration-weight integrity is BLOCKED.",
                "Blocked independence integrity cannot support candidate sufficiency.",
            ),
        )

    if integrity_state == "UNKNOWN":
        return CandidateEvidenceSufficiencyAssessment(
            state=SufficiencyState.UNKNOWN,
            reason=SufficiencyReason.UNKNOWN_REQUIREMENT,
            category_assessments=(),
            missing_required_categories=(),
            insufficient_independent_categories=(),
            unresolved_categories=(),
            reasons=(
                "Evidence independence integrity is UNKNOWN.",
                "Candidate sufficiency fails closed.",
            ),
        )

    if integrity_state not in {
        "VALID",
        "REVIEW_REQUIRED",
    }:
        return CandidateEvidenceSufficiencyAssessment(
            state=SufficiencyState.UNKNOWN,
            reason=SufficiencyReason.UNKNOWN_REQUIREMENT,
            category_assessments=(),
            missing_required_categories=(),
            insufficient_independent_categories=(),
            unresolved_categories=(),
            reasons=(
                (
                    "Unrecognized evidence independence integrity state: "
                    f"{integrity_state}"
                ),
            ),
        )

    if not requirement_items:
        return CandidateEvidenceSufficiencyAssessment(
            state=SufficiencyState.BLOCKED,
            reason=SufficiencyReason.EMPTY_REQUIREMENTS,
            category_assessments=(),
            missing_required_categories=(),
            insufficient_independent_categories=(),
            unresolved_categories=(),
            reasons=(
                "No evidence requirements were supplied.",
                "Candidate sufficiency cannot be established without explicit requirements.",
            ),
        )

    categories = [
        requirement.category
        for requirement in requirement_items
    ]

    if len(categories) != len(set(categories)):
        return CandidateEvidenceSufficiencyAssessment(
            state=SufficiencyState.BLOCKED,
            reason=SufficiencyReason.UNKNOWN_REQUIREMENT,
            category_assessments=(),
            missing_required_categories=(),
            insufficient_independent_categories=(),
            unresolved_categories=(),
            reasons=(
                "Duplicate evidence requirement categories detected.",
            ),
        )

    if not evidence_items:
        required_categories = tuple(
            sorted(
                requirement.category
                for requirement in requirement_items
                if requirement.required
            )
        )

        return CandidateEvidenceSufficiencyAssessment(
            state=SufficiencyState.INSUFFICIENT,
            reason=SufficiencyReason.EMPTY_EVIDENCE,
            category_assessments=tuple(
                assess_category_sufficiency(
                    requirement=requirement,
                    evidence=(),
                )
                for requirement in requirement_items
            ),
            missing_required_categories=required_categories,
            insufficient_independent_categories=required_categories,
            unresolved_categories=(),
            reasons=(
                "No candidate evidence was supplied.",
            ),
        )

    assessments = tuple(
        assess_category_sufficiency(
            requirement=requirement,
            evidence=evidence_items,
        )
        for requirement in requirement_items
    )

    missing_required = tuple(
        sorted(
            assessment.category
            for assessment in assessments
            if (
                assessment.required
                and assessment.observation_count == 0
            )
        )
    )

    insufficient_independent = tuple(
        sorted(
            assessment.category
            for assessment in assessments
            if (
                assessment.required
                and (
                    assessment.independent_confirmation_count
                    < assessment.minimum_independent_confirmations
                )
            )
        )
    )

    unresolved_categories = tuple(
        sorted(
            assessment.category
            for assessment in assessments
            if (
                assessment.required
                and assessment.unresolved_dependency_count > 0
            )
        )
    )

    unsatisfied_required = tuple(
        assessment
        for assessment in assessments
        if (
            assessment.required
            and not assessment.satisfied
        )
    )

    if missing_required:
        return CandidateEvidenceSufficiencyAssessment(
            state=SufficiencyState.INSUFFICIENT,
            reason=SufficiencyReason.REQUIRED_CATEGORY_MISSING,
            category_assessments=assessments,
            missing_required_categories=missing_required,
            insufficient_independent_categories=insufficient_independent,
            unresolved_categories=unresolved_categories,
            reasons=(
                "One or more required evidence categories are absent.",
            ),
        )

    if insufficient_independent:
        return CandidateEvidenceSufficiencyAssessment(
            state=SufficiencyState.INSUFFICIENT,
            reason=SufficiencyReason.INDEPENDENT_SUPPORT_MISSING,
            category_assessments=assessments,
            missing_required_categories=missing_required,
            insufficient_independent_categories=insufficient_independent,
            unresolved_categories=unresolved_categories,
            reasons=(
                "One or more required evidence categories lack required independent support.",
            ),
        )

    if unresolved_categories:
        return CandidateEvidenceSufficiencyAssessment(
            state=SufficiencyState.REVIEW_REQUIRED,
            reason=SufficiencyReason.UNRESOLVED_EVIDENCE,
            category_assessments=assessments,
            missing_required_categories=missing_required,
            insufficient_independent_categories=insufficient_independent,
            unresolved_categories=unresolved_categories,
            reasons=(
                "Required evidence contains unresolved dependency provenance.",
                "Unresolved evidence cannot establish final sufficiency.",
            ),
        )

    if integrity_state == "REVIEW_REQUIRED":
        return CandidateEvidenceSufficiencyAssessment(
            state=SufficiencyState.REVIEW_REQUIRED,
            reason=SufficiencyReason.INDEPENDENCE_REVIEW_REQUIRED,
            category_assessments=assessments,
            missing_required_categories=missing_required,
            insufficient_independent_categories=insufficient_independent,
            unresolved_categories=unresolved_categories,
            reasons=(
                "Evidence requirements are otherwise met, but upstream independence integrity requires review.",
            ),
        )

    if unsatisfied_required:
        return CandidateEvidenceSufficiencyAssessment(
            state=SufficiencyState.INSUFFICIENT,
            reason=SufficiencyReason.UNKNOWN,
            category_assessments=assessments,
            missing_required_categories=missing_required,
            insufficient_independent_categories=insufficient_independent,
            unresolved_categories=unresolved_categories,
            reasons=(
                "One or more required evidence categories remain unsatisfied.",
            ),
        )

    return CandidateEvidenceSufficiencyAssessment(
        state=SufficiencyState.SUFFICIENT,
        reason=SufficiencyReason.REQUIREMENTS_SATISFIED,
        category_assessments=assessments,
        missing_required_categories=(),
        insufficient_independent_categories=(),
        unresolved_categories=(),
        reasons=(
            "All required evidence categories satisfy explicit observation and independent-support requirements.",
            "SUFFICIENT means sufficient for analytical reasoning only.",
        ),
    )


def sufficient_for_analytical_reasoning(
    assessment: CandidateEvidenceSufficiencyAssessment,
) -> bool:
    return (
        assessment.state
        is SufficiencyState.SUFFICIENT
    )


def candidate_evidence_sufficiency_snapshot(
    assessment: CandidateEvidenceSufficiencyAssessment,
) -> dict[str, object]:
    return {
        "state": assessment.state.value,
        "reason": assessment.reason.value,
        "missing_required_categories": list(
            assessment.missing_required_categories
        ),
        "insufficient_independent_categories": list(
            assessment.insufficient_independent_categories
        ),
        "unresolved_categories": list(
            assessment.unresolved_categories
        ),
        "reasons": list(
            assessment.reasons
        ),
        "category_assessments": [
            {
                "category": category.category,
                "required": category.required,
                "observation_count": category.observation_count,
                "independent_confirmation_count": (
                    category.independent_confirmation_count
                ),
                "unresolved_dependency_count": (
                    category.unresolved_dependency_count
                ),
                "minimum_observations": (
                    category.minimum_observations
                ),
                "minimum_independent_confirmations": (
                    category.minimum_independent_confirmations
                ),
                "satisfied": category.satisfied,
                "reasons": list(
                    category.reasons
                ),
            }
            for category in assessment.category_assessments
        ],
        "authority_boundary": {
            "analytical_reasoning_sufficiency_only": True,
            "analytical_conclusion": False,
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
