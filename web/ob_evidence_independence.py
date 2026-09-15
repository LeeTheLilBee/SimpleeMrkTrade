from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class DependencyState(str, Enum):
    INDEPENDENT = "INDEPENDENT"
    DEPENDENT = "DEPENDENT"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    UNKNOWN = "UNKNOWN"


class DependencyReason(str, Enum):
    DISTINCT_INDEPENDENCE_FAMILY = "DISTINCT_INDEPENDENCE_FAMILY"
    SAME_SOURCE = "SAME_SOURCE"
    SAME_SOURCE_FAMILY = "SAME_SOURCE_FAMILY"
    SAME_ORIGIN_FAMILY = "SAME_ORIGIN_FAMILY"
    EXPLICIT_DEPENDENCY = "EXPLICIT_DEPENDENCY"
    UNKNOWN_DEPENDENCY = "UNKNOWN_DEPENDENCY"


class CorroborationIntegrityState(str, Enum):
    VALID = "VALID"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class EvidenceOriginIdentity:
    observation_id: str
    observation_version: int
    lineage_hash: str
    source_id: str
    source_family_id: str
    origin_family_id: str
    independence_family_id: str
    dependency_ids: tuple[str, ...]
    dependency_known: bool


@dataclass(frozen=True)
class PairwiseIndependenceAssessment:
    left_observation_id: str
    right_observation_id: str
    state: DependencyState
    reason: DependencyReason
    details: tuple[str, ...]


@dataclass(frozen=True)
class EvidenceIndependenceGroup:
    independence_family_id: str
    observation_keys: tuple[tuple[str, int], ...]


@dataclass(frozen=True)
class CorroborationWeightAssessment:
    total_observations: int
    independent_confirmation_count: int
    dependent_observation_count: int
    unresolved_dependency_count: int
    state: CorroborationIntegrityState
    groups: tuple[EvidenceIndependenceGroup, ...]
    reasons: tuple[str, ...]


def _nonblank(value: object, *, name: str) -> str:
    text = str(value).strip()

    if not text:
        raise ValueError(
            f"{name} cannot be blank"
        )

    return text


def _normalized_ids(values: Iterable[str]) -> tuple[str, ...]:
    normalized = tuple(
        sorted(
            {
                _nonblank(
                    value,
                    name="dependency_id",
                )
                for value in values
            }
        )
    )

    return normalized


def build_evidence_origin_identity(
    *,
    observation_id: str,
    observation_version: int,
    lineage_hash: str,
    source_id: str,
    source_family_id: str,
    origin_family_id: str,
    independence_family_id: str,
    dependency_ids: Iterable[str] = (),
    dependency_known: bool = True,
) -> EvidenceOriginIdentity:
    if observation_version < 1:
        raise ValueError(
            "observation_version must be >= 1"
        )

    return EvidenceOriginIdentity(
        observation_id=_nonblank(
            observation_id,
            name="observation_id",
        ),
        observation_version=observation_version,
        lineage_hash=_nonblank(
            lineage_hash,
            name="lineage_hash",
        ),
        source_id=_nonblank(
            source_id,
            name="source_id",
        ),
        source_family_id=_nonblank(
            source_family_id,
            name="source_family_id",
        ),
        origin_family_id=_nonblank(
            origin_family_id,
            name="origin_family_id",
        ),
        independence_family_id=_nonblank(
            independence_family_id,
            name="independence_family_id",
        ),
        dependency_ids=_normalized_ids(
            dependency_ids
        ),
        dependency_known=bool(
            dependency_known
        ),
    )


def assess_pairwise_independence(
    *,
    left: EvidenceOriginIdentity,
    right: EvidenceOriginIdentity,
) -> PairwiseIndependenceAssessment:
    if (
        not left.dependency_known
        or not right.dependency_known
    ):
        return PairwiseIndependenceAssessment(
            left_observation_id=left.observation_id,
            right_observation_id=right.observation_id,
            state=DependencyState.UNKNOWN,
            reason=DependencyReason.UNKNOWN_DEPENDENCY,
            details=(
                "At least one evidence item has unresolved dependency provenance.",
                "Unknown dependency cannot receive independent-confirmation credit.",
            ),
        )

    if left.source_id == right.source_id:
        return PairwiseIndependenceAssessment(
            left_observation_id=left.observation_id,
            right_observation_id=right.observation_id,
            state=DependencyState.DEPENDENT,
            reason=DependencyReason.SAME_SOURCE,
            details=(
                "Evidence items originate from the same canonical source.",
            ),
        )

    if left.source_family_id == right.source_family_id:
        return PairwiseIndependenceAssessment(
            left_observation_id=left.observation_id,
            right_observation_id=right.observation_id,
            state=DependencyState.DEPENDENT,
            reason=DependencyReason.SAME_SOURCE_FAMILY,
            details=(
                "Evidence items belong to the same source family.",
            ),
        )

    if left.origin_family_id == right.origin_family_id:
        return PairwiseIndependenceAssessment(
            left_observation_id=left.observation_id,
            right_observation_id=right.observation_id,
            state=DependencyState.DEPENDENT,
            reason=DependencyReason.SAME_ORIGIN_FAMILY,
            details=(
                "Different source surfaces resolve to the same upstream origin family.",
            ),
        )

    left_dependencies = set(
        left.dependency_ids
    )
    right_dependencies = set(
        right.dependency_ids
    )

    if (
        left.source_id in right_dependencies
        or right.source_id in left_dependencies
        or bool(
            left_dependencies
            & right_dependencies
        )
    ):
        return PairwiseIndependenceAssessment(
            left_observation_id=left.observation_id,
            right_observation_id=right.observation_id,
            state=DependencyState.DEPENDENT,
            reason=DependencyReason.EXPLICIT_DEPENDENCY,
            details=(
                "Evidence items share or directly reference an explicit dependency.",
            ),
        )

    if (
        left.independence_family_id
        == right.independence_family_id
    ):
        return PairwiseIndependenceAssessment(
            left_observation_id=left.observation_id,
            right_observation_id=right.observation_id,
            state=DependencyState.REVIEW_REQUIRED,
            reason=DependencyReason.EXPLICIT_DEPENDENCY,
            details=(
                "Evidence items were assigned to the same independence family.",
                "They cannot be counted as separate independent confirmations.",
            ),
        )

    return PairwiseIndependenceAssessment(
        left_observation_id=left.observation_id,
        right_observation_id=right.observation_id,
        state=DependencyState.INDEPENDENT,
        reason=DependencyReason.DISTINCT_INDEPENDENCE_FAMILY,
        details=(
            "No declared source, family, origin-family, or explicit dependency overlap was found.",
            "This receipt grants corroboration-counting independence only; it grants no trade authority.",
        ),
    )


def compose_independence_groups(
    identities: Iterable[EvidenceOriginIdentity],
) -> tuple[EvidenceIndependenceGroup, ...]:
    grouped: dict[
        str,
        list[tuple[str, int]],
    ] = {}

    for identity in identities:
        grouped.setdefault(
            identity.independence_family_id,
            [],
        ).append(
            (
                identity.observation_id,
                identity.observation_version,
            )
        )

    return tuple(
        EvidenceIndependenceGroup(
            independence_family_id=family_id,
            observation_keys=tuple(
                sorted(
                    observation_keys
                )
            ),
        )
        for family_id, observation_keys
        in sorted(
            grouped.items()
        )
    )


def assess_corroboration_weight_integrity(
    identities: Iterable[EvidenceOriginIdentity],
) -> CorroborationWeightAssessment:
    items = tuple(
        identities
    )

    if not items:
        return CorroborationWeightAssessment(
            total_observations=0,
            independent_confirmation_count=0,
            dependent_observation_count=0,
            unresolved_dependency_count=0,
            state=CorroborationIntegrityState.BLOCKED,
            groups=(),
            reasons=(
                "No evidence observations were supplied.",
            ),
        )

    exact_keys = [
        (
            item.observation_id,
            item.observation_version,
            item.lineage_hash,
        )
        for item in items
    ]

    if len(exact_keys) != len(set(exact_keys)):
        return CorroborationWeightAssessment(
            total_observations=len(items),
            independent_confirmation_count=0,
            dependent_observation_count=len(items),
            unresolved_dependency_count=0,
            state=CorroborationIntegrityState.BLOCKED,
            groups=compose_independence_groups(
                items
            ),
            reasons=(
                "Exact duplicate evidence identity detected.",
                "Duplicate evidence cannot receive corroboration weight.",
            ),
        )

    unresolved = tuple(
        item
        for item in items
        if not item.dependency_known
    )

    known = tuple(
        item
        for item in items
        if item.dependency_known
    )

    # A family is the unit of independent-confirmation credit.
    #
    # Multiple observations inside one family remain visible evidence,
    # but they contribute at most ONE independent confirmation.
    groups = compose_independence_groups(
        known
    )

    independent_count = len(
        groups
    )

    dependent_count = max(
        0,
        len(known) - independent_count,
    )

    reasons = []

    if dependent_count:
        reasons.append(
            f"{dependent_count} observation(s) share independence families and do not increase independent-confirmation count."
        )

    # Pairwise dependency checks may reveal cross-family dependency that
    # a caller incorrectly labeled as separate independence families.
    cross_family_dependency = False

    for left_index, left in enumerate(known):
        for right in known[left_index + 1:]:
            assessment = assess_pairwise_independence(
                left=left,
                right=right,
            )

            if (
                left.independence_family_id
                != right.independence_family_id
                and assessment.state
                in {
                    DependencyState.DEPENDENT,
                    DependencyState.REVIEW_REQUIRED,
                }
            ):
                cross_family_dependency = True

                reasons.append(
                    "Declared independence families conflict with detected source/dependency relationships."
                )

                break

        if cross_family_dependency:
            break

    if cross_family_dependency:
        return CorroborationWeightAssessment(
            total_observations=len(items),
            independent_confirmation_count=0,
            dependent_observation_count=len(known),
            unresolved_dependency_count=len(unresolved),
            state=CorroborationIntegrityState.BLOCKED,
            groups=groups,
            reasons=tuple(
                reasons
            ),
        )

    if unresolved:
        reasons.append(
            f"{len(unresolved)} observation(s) have unresolved dependency provenance and receive no independent-confirmation credit."
        )

        return CorroborationWeightAssessment(
            total_observations=len(items),
            independent_confirmation_count=independent_count,
            dependent_observation_count=dependent_count,
            unresolved_dependency_count=len(unresolved),
            state=CorroborationIntegrityState.REVIEW_REQUIRED,
            groups=groups,
            reasons=tuple(
                reasons
            ),
        )

    if not reasons:
        reasons.append(
            "All supplied evidence observations belong to distinct declared independence families with no detected dependency conflict."
        )

    return CorroborationWeightAssessment(
        total_observations=len(items),
        independent_confirmation_count=independent_count,
        dependent_observation_count=dependent_count,
        unresolved_dependency_count=0,
        state=CorroborationIntegrityState.VALID,
        groups=groups,
        reasons=tuple(
            reasons
        ),
    )


def independent_confirmation_count(
    identities: Iterable[EvidenceOriginIdentity],
) -> int:
    assessment = assess_corroboration_weight_integrity(
        identities
    )

    if assessment.state not in {
        CorroborationIntegrityState.VALID,
        CorroborationIntegrityState.REVIEW_REQUIRED,
    }:
        return 0

    return assessment.independent_confirmation_count


def corroboration_weight_snapshot(
    assessment: CorroborationWeightAssessment,
) -> dict[str, object]:
    return {
        "total_observations": assessment.total_observations,
        "independent_confirmation_count": assessment.independent_confirmation_count,
        "dependent_observation_count": assessment.dependent_observation_count,
        "unresolved_dependency_count": assessment.unresolved_dependency_count,
        "state": assessment.state.value,
        "groups": [
            {
                "independence_family_id": group.independence_family_id,
                "observation_keys": [
                    {
                        "observation_id": observation_id,
                        "observation_version": observation_version,
                    }
                    for observation_id, observation_version
                    in group.observation_keys
                ],
            }
            for group in assessment.groups
        ],
        "reasons": list(
            assessment.reasons
        ),
        "authority_boundary": {
            "corroboration_counting_only": True,
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
