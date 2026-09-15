from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Iterable

from web.ob_candidate_admission_receipt_binding import (
    ReceiptBoundCandidateEvidenceSet,
    verify_receipt_bound_candidate_set,
)
from web.ob_candidate_evidence_sufficiency import (
    CandidateEvidenceSufficiencyAssessment,
    EvidenceRequirement,
    SufficiencyState,
    assess_candidate_evidence_sufficiency,
    build_candidate_evidence_support,
    build_evidence_requirement,
)
from web.ob_evidence_independence import (
    CorroborationIntegrityState,
    CorroborationWeightAssessment,
    EvidenceOriginIdentity,
    assess_corroboration_weight_integrity,
)


@dataclass(frozen=True)
class BoundEvidenceOrigin:
    observation_id: str
    observation_version: int
    lineage_hash: str
    source_id: str
    source_family_id: str
    origin_family_id: str
    independence_family_id: str
    dependency_ids: tuple[str, ...]
    dependency_known: bool
    category: str


@dataclass(frozen=True)
class CandidateIndependenceReceipt:
    receipt_id: str
    candidate_set_receipt_id: str
    candidate_set_integrity_hash: str
    assessment: CorroborationWeightAssessment
    origin_hash: str
    integrity_hash: str


@dataclass(frozen=True)
class PolicyEvidenceRequirementSet:
    requirement_set_id: str
    effective_policy_id: str
    effective_policy_hash: str
    requirements: tuple[EvidenceRequirement, ...]
    integrity_hash: str


@dataclass(frozen=True)
class CandidateSufficiencyReceipt:
    receipt_id: str
    candidate_set_receipt_id: str
    candidate_set_integrity_hash: str
    independence_receipt_id: str
    requirement_set_id: str
    effective_policy_id: str
    effective_policy_hash: str
    assessment: CandidateEvidenceSufficiencyAssessment
    integrity_hash: str


def _nonblank(value: object, *, name: str) -> str:
    text = str(value).strip()
    if not text:
        raise ValueError(f"{name} cannot be blank")
    return text


def _hash(payload: dict[str, object]) -> str:
    return hashlib.sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
    ).hexdigest()


def bind_evidence_origins(
    *,
    candidate_set: ReceiptBoundCandidateEvidenceSet,
    origins: Iterable[BoundEvidenceOrigin],
) -> tuple[BoundEvidenceOrigin, ...]:
    if not verify_receipt_bound_candidate_set(candidate_set):
        raise ValueError("candidate evidence set failed integrity verification")

    origin_items = tuple(origins)

    expected = {
        (
            item.observation_id,
            item.observation_version,
            item.lineage_hash,
        )
        for item in candidate_set.evidence_set.items
    }

    actual = {
        (
            item.observation_id,
            item.observation_version,
            item.lineage_hash,
        )
        for item in origin_items
    }

    if expected != actual:
        raise ValueError(
            "origin identities must exactly cover the admitted candidate evidence set"
        )

    if len(actual) != len(origin_items):
        raise ValueError("duplicate bound origin identity")

    return origin_items


def build_candidate_independence_receipt(
    *,
    candidate_set: ReceiptBoundCandidateEvidenceSet,
    origins: Iterable[BoundEvidenceOrigin],
) -> CandidateIndependenceReceipt:
    bound = bind_evidence_origins(
        candidate_set=candidate_set,
        origins=origins,
    )

    identities = tuple(
        EvidenceOriginIdentity(
            observation_id=item.observation_id,
            observation_version=item.observation_version,
            lineage_hash=item.lineage_hash,
            source_id=_nonblank(item.source_id, name="source_id"),
            source_family_id=_nonblank(
                item.source_family_id,
                name="source_family_id",
            ),
            origin_family_id=_nonblank(
                item.origin_family_id,
                name="origin_family_id",
            ),
            independence_family_id=_nonblank(
                item.independence_family_id,
                name="independence_family_id",
            ),
            dependency_ids=tuple(
                sorted(
                    {
                        _nonblank(value, name="dependency_id")
                        for value in item.dependency_ids
                    }
                )
            ),
            dependency_known=bool(item.dependency_known),
        )
        for item in bound
    )

    assessment = assess_corroboration_weight_integrity(identities)

    origin_payload = [
        {
            "observation_id": item.observation_id,
            "observation_version": item.observation_version,
            "lineage_hash": item.lineage_hash,
            "source_id": item.source_id,
            "source_family_id": item.source_family_id,
            "origin_family_id": item.origin_family_id,
            "independence_family_id": item.independence_family_id,
            "dependency_ids": list(item.dependency_ids),
            "dependency_known": item.dependency_known,
            "category": item.category.upper(),
        }
        for item in sorted(
            bound,
            key=lambda value: (
                value.observation_id,
                value.observation_version,
                value.lineage_hash,
            ),
        )
    ]

    origin_hash = _hash({"origins": origin_payload})

    payload = {
        "candidate_set_receipt_id": candidate_set.set_receipt_id,
        "candidate_set_integrity_hash": candidate_set.set_integrity_hash,
        "origin_hash": origin_hash,
        "state": assessment.state.value,
        "independent_confirmation_count": assessment.independent_confirmation_count,
        "dependent_observation_count": assessment.dependent_observation_count,
        "unresolved_dependency_count": assessment.unresolved_dependency_count,
    }

    digest = _hash(payload)

    return CandidateIndependenceReceipt(
        receipt_id=f"OBIND-{digest[:24]}",
        candidate_set_receipt_id=candidate_set.set_receipt_id,
        candidate_set_integrity_hash=candidate_set.set_integrity_hash,
        assessment=assessment,
        origin_hash=origin_hash,
        integrity_hash=digest,
    )


def verify_candidate_independence_receipt(
    receipt: CandidateIndependenceReceipt,
) -> bool:
    payload = {
        "candidate_set_receipt_id": receipt.candidate_set_receipt_id,
        "candidate_set_integrity_hash": receipt.candidate_set_integrity_hash,
        "origin_hash": receipt.origin_hash,
        "state": receipt.assessment.state.value,
        "independent_confirmation_count": (
            receipt.assessment.independent_confirmation_count
        ),
        "dependent_observation_count": (
            receipt.assessment.dependent_observation_count
        ),
        "unresolved_dependency_count": (
            receipt.assessment.unresolved_dependency_count
        ),
    }

    digest = _hash(payload)

    return (
        digest == receipt.integrity_hash
        and receipt.receipt_id == f"OBIND-{digest[:24]}"
    )


def build_policy_requirement_set(
    *,
    candidate_set: ReceiptBoundCandidateEvidenceSet,
    requirements: Iterable[EvidenceRequirement],
) -> PolicyEvidenceRequirementSet:
    if not verify_receipt_bound_candidate_set(candidate_set):
        raise ValueError("candidate evidence set failed integrity verification")

    items = tuple(requirements)

    if not items:
        raise ValueError("requirement set cannot be empty")

    categories = [item.category for item in items]

    if len(categories) != len(set(categories)):
        raise ValueError("duplicate requirement categories")

    payload = {
        "effective_policy_id": candidate_set.identity.effective_policy_id,
        "effective_policy_hash": candidate_set.identity.effective_policy_hash,
        "requirements": [
            {
                "category": item.category,
                "minimum_observations": item.minimum_observations,
                "minimum_independent_confirmations": (
                    item.minimum_independent_confirmations
                ),
                "required": item.required,
            }
            for item in items
        ],
    }

    digest = _hash(payload)

    return PolicyEvidenceRequirementSet(
        requirement_set_id=f"OBREQ-{digest[:24]}",
        effective_policy_id=candidate_set.identity.effective_policy_id,
        effective_policy_hash=candidate_set.identity.effective_policy_hash,
        requirements=items,
        integrity_hash=digest,
    )


def verify_policy_requirement_set(
    requirement_set: PolicyEvidenceRequirementSet,
) -> bool:
    payload = {
        "effective_policy_id": requirement_set.effective_policy_id,
        "effective_policy_hash": requirement_set.effective_policy_hash,
        "requirements": [
            {
                "category": item.category,
                "minimum_observations": item.minimum_observations,
                "minimum_independent_confirmations": (
                    item.minimum_independent_confirmations
                ),
                "required": item.required,
            }
            for item in requirement_set.requirements
        ],
    }

    digest = _hash(payload)

    return (
        digest == requirement_set.integrity_hash
        and requirement_set.requirement_set_id == f"OBREQ-{digest[:24]}"
    )


def build_candidate_sufficiency_receipt(
    *,
    candidate_set: ReceiptBoundCandidateEvidenceSet,
    origins: Iterable[BoundEvidenceOrigin],
    independence_receipt: CandidateIndependenceReceipt,
    requirement_set: PolicyEvidenceRequirementSet,
) -> CandidateSufficiencyReceipt:
    if not verify_receipt_bound_candidate_set(candidate_set):
        raise ValueError("candidate evidence set failed integrity verification")

    if not verify_candidate_independence_receipt(independence_receipt):
        raise ValueError("independence receipt failed integrity verification")

    if not verify_policy_requirement_set(requirement_set):
        raise ValueError("requirement set failed integrity verification")

    if independence_receipt.candidate_set_receipt_id != candidate_set.set_receipt_id:
        raise ValueError("independence/candidate set receipt mismatch")

    if (
        independence_receipt.candidate_set_integrity_hash
        != candidate_set.set_integrity_hash
    ):
        raise ValueError("independence/candidate integrity mismatch")

    if requirement_set.effective_policy_id != candidate_set.identity.effective_policy_id:
        raise ValueError("requirement policy id mismatch")

    if (
        requirement_set.effective_policy_hash
        != candidate_set.identity.effective_policy_hash
    ):
        raise ValueError("requirement policy hash mismatch")

    bound = bind_evidence_origins(
        candidate_set=candidate_set,
        origins=origins,
    )

    support = tuple(
        build_candidate_evidence_support(
            observation_id=item.observation_id,
            observation_version=item.observation_version,
            category=item.category,
            independence_family_id=item.independence_family_id,
            dependency_known=item.dependency_known,
        )
        for item in bound
    )

    # IMPORTANT:
    # The sealed OBDATA091–095 primitive still accepts a string.
    # The canonical integration path derives that string ONLY from the
    # verified OBDATA086–090 assessment held by this bound receipt.
    assessment = assess_candidate_evidence_sufficiency(
        requirements=requirement_set.requirements,
        evidence=support,
        independence_integrity_state=(
            independence_receipt.assessment.state.value
        ),
    )

    payload = {
        "candidate_set_receipt_id": candidate_set.set_receipt_id,
        "candidate_set_integrity_hash": candidate_set.set_integrity_hash,
        "independence_receipt_id": independence_receipt.receipt_id,
        "requirement_set_id": requirement_set.requirement_set_id,
        "effective_policy_id": requirement_set.effective_policy_id,
        "effective_policy_hash": requirement_set.effective_policy_hash,
        "state": assessment.state.value,
        "reason": assessment.reason.value,
    }

    digest = _hash(payload)

    return CandidateSufficiencyReceipt(
        receipt_id=f"OBSUFF-{digest[:24]}",
        candidate_set_receipt_id=candidate_set.set_receipt_id,
        candidate_set_integrity_hash=candidate_set.set_integrity_hash,
        independence_receipt_id=independence_receipt.receipt_id,
        requirement_set_id=requirement_set.requirement_set_id,
        effective_policy_id=requirement_set.effective_policy_id,
        effective_policy_hash=requirement_set.effective_policy_hash,
        assessment=assessment,
        integrity_hash=digest,
    )


def verify_candidate_sufficiency_receipt(
    receipt: CandidateSufficiencyReceipt,
) -> bool:
    payload = {
        "candidate_set_receipt_id": receipt.candidate_set_receipt_id,
        "candidate_set_integrity_hash": receipt.candidate_set_integrity_hash,
        "independence_receipt_id": receipt.independence_receipt_id,
        "requirement_set_id": receipt.requirement_set_id,
        "effective_policy_id": receipt.effective_policy_id,
        "effective_policy_hash": receipt.effective_policy_hash,
        "state": receipt.assessment.state.value,
        "reason": receipt.assessment.reason.value,
    }

    digest = _hash(payload)

    return (
        digest == receipt.integrity_hash
        and receipt.receipt_id == f"OBSUFF-{digest[:24]}"
    )


def candidate_sufficiency_eligible(
    receipt: CandidateSufficiencyReceipt,
) -> bool:
    return (
        verify_candidate_sufficiency_receipt(receipt)
        and receipt.assessment.state is SufficiencyState.SUFFICIENT
    )


def independence_sufficiency_snapshot(
    *,
    independence_receipt: CandidateIndependenceReceipt,
    sufficiency_receipt: CandidateSufficiencyReceipt,
) -> dict[str, object]:
    return {
        "independence_receipt_id": independence_receipt.receipt_id,
        "independence_state": independence_receipt.assessment.state.value,
        "sufficiency_receipt_id": sufficiency_receipt.receipt_id,
        "sufficiency_state": sufficiency_receipt.assessment.state.value,
        "effective_policy_id": sufficiency_receipt.effective_policy_id,
        "effective_policy_hash": sufficiency_receipt.effective_policy_hash,
        "authority_boundary": {
            "evidence_independence_and_sufficiency_only": True,
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
