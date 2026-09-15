from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Iterable

from web.ob_analytical_conclusion_integrity import (
    AnalyticalClaim,
    AnalyticalConclusionAssessment,
    ClaimKind,
    ConclusionState,
    SupportState,
    UncertaintyState,
    assess_analytical_conclusion,
    build_analytical_claim,
)
from web.ob_candidate_admission_receipt_binding import (
    ReceiptBoundCandidateEvidenceSet,
    verify_receipt_bound_candidate_set,
)
from web.ob_candidate_evidence_sufficiency import SufficiencyState
from web.ob_independence_sufficiency_binding import (
    CandidateSufficiencyReceipt,
    verify_candidate_sufficiency_receipt,
)


@dataclass(frozen=True)
class GovernedClaimBasis:
    claim_id: str
    statement: str
    claim_kind: ClaimKind
    evidence_refs: tuple[str, ...]
    inference_basis: tuple[str, ...]
    conflict_refs: tuple[str, ...]
    partial_support: bool = False
    material_uncertainty: bool = False


@dataclass(frozen=True)
class BoundAnalyticalClaim:
    claim: AnalyticalClaim
    candidate_set_receipt_id: str
    sufficiency_receipt_id: str
    basis_hash: str


@dataclass(frozen=True)
class AnalyticalConclusionReceipt:
    receipt_id: str
    candidate_id: str
    candidate_set_receipt_id: str
    candidate_set_integrity_hash: str
    sufficiency_receipt_id: str
    sufficiency_integrity_hash: str
    effective_policy_id: str
    effective_policy_hash: str
    contract_id: str | None
    assessment: AnalyticalConclusionAssessment
    claim_hashes: tuple[str, ...]
    integrity_hash: str


def _nonblank(value: object, *, name: str) -> str:
    text = str(value).strip()
    if not text:
        raise ValueError(f"{name} cannot be blank")
    return text


def _refs(values: Iterable[str], *, name: str) -> tuple[str, ...]:
    result = tuple(_nonblank(x, name=name) for x in values)

    if len(result) != len(set(result)):
        raise ValueError(f"{name} contains duplicates")

    return result


def _hash(payload: dict[str, object]) -> str:
    return hashlib.sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
    ).hexdigest()


def _candidate_evidence_refs(
    candidate_set: ReceiptBoundCandidateEvidenceSet,
) -> set[str]:
    refs = set()

    for item in candidate_set.evidence_set.items:
        refs.add(
            f"{item.observation_id}:{item.observation_version}:{item.lineage_hash}"
        )

    return refs


def build_governed_claim_basis(
    *,
    claim_id: str,
    statement: str,
    claim_kind: ClaimKind,
    evidence_refs: Iterable[str],
    inference_basis: Iterable[str] = (),
    conflict_refs: Iterable[str] = (),
    partial_support: bool = False,
    material_uncertainty: bool = False,
) -> GovernedClaimBasis:
    if not isinstance(claim_kind, ClaimKind):
        raise ValueError("claim_kind must be canonical ClaimKind")

    if claim_kind is ClaimKind.UNKNOWN:
        raise ValueError("UNKNOWN claim kind cannot enter canonical conclusion path")

    return GovernedClaimBasis(
        claim_id=_nonblank(claim_id, name="claim_id"),
        statement=_nonblank(statement, name="statement"),
        claim_kind=claim_kind,
        evidence_refs=_refs(evidence_refs, name="evidence_ref"),
        inference_basis=_refs(inference_basis, name="inference_basis"),
        conflict_refs=_refs(conflict_refs, name="conflict_ref"),
        partial_support=bool(partial_support),
        material_uncertainty=bool(material_uncertainty),
    )


def derive_bound_analytical_claim(
    *,
    candidate_set: ReceiptBoundCandidateEvidenceSet,
    sufficiency_receipt: CandidateSufficiencyReceipt,
    basis: GovernedClaimBasis,
) -> BoundAnalyticalClaim:
    if not verify_receipt_bound_candidate_set(candidate_set):
        raise ValueError("candidate evidence set failed integrity verification")

    if not verify_candidate_sufficiency_receipt(sufficiency_receipt):
        raise ValueError("sufficiency receipt failed integrity verification")

    if (
        sufficiency_receipt.candidate_set_receipt_id
        != candidate_set.set_receipt_id
    ):
        raise ValueError("sufficiency/candidate receipt mismatch")

    if (
        sufficiency_receipt.candidate_set_integrity_hash
        != candidate_set.set_integrity_hash
    ):
        raise ValueError("sufficiency/candidate integrity mismatch")

    admitted_refs = _candidate_evidence_refs(candidate_set)

    if not basis.evidence_refs:
        raise ValueError("canonical analytical claim requires evidence")

    if not set(basis.evidence_refs).issubset(admitted_refs):
        raise ValueError(
            "claim evidence must be a subset of the admitted candidate evidence set"
        )

    if basis.claim_kind is ClaimKind.DIRECT and basis.inference_basis:
        raise ValueError("DIRECT claim cannot carry inference basis")

    if basis.claim_kind is ClaimKind.INFERENCE and not basis.inference_basis:
        raise ValueError("INFERENCE claim requires inference basis")

    # Support is DERIVED here, not caller supplied.
    #
    # Evidence support and unresolved conflict are separate dimensions.
    # A claim may have direct admitted support while still carrying an
    # unresolved conflict that requires review. The sealed OBDATA096–100
    # primitive requires a DIRECT claim to remain SUPPORTED before its
    # unresolved_conflicts field can correctly drive REVIEW_REQUIRED.
    if basis.partial_support:
        support = SupportState.PARTIAL
    else:
        support = SupportState.SUPPORTED

    # Uncertainty is DERIVED here, not caller supplied.
    # Unresolved conflict is preserved independently and makes uncertainty
    # material without falsely converting direct support into unsupported
    # or non-direct evidence.
    uncertainty = (
        UncertaintyState.MATERIAL
        if basis.material_uncertainty or basis.conflict_refs
        else UncertaintyState.RESOLVED
    )

    claim = build_analytical_claim(
        claim_id=basis.claim_id,
        statement=basis.statement,
        claim_kind=basis.claim_kind,
        support_state=support,
        uncertainty_state=uncertainty,
        evidence_refs=basis.evidence_refs,
        inference_basis=basis.inference_basis,
        unresolved_conflicts=basis.conflict_refs,
    )

    payload = {
        "claim_id": basis.claim_id,
        "statement": basis.statement,
        "claim_kind": basis.claim_kind.value,
        "evidence_refs": list(basis.evidence_refs),
        "inference_basis": list(basis.inference_basis),
        "conflict_refs": list(basis.conflict_refs),
        "partial_support": basis.partial_support,
        "material_uncertainty": basis.material_uncertainty,
        "derived_support_state": support.value,
        "derived_uncertainty_state": uncertainty.value,
        "candidate_set_receipt_id": candidate_set.set_receipt_id,
        "sufficiency_receipt_id": sufficiency_receipt.receipt_id,
    }

    basis_hash = _hash(payload)

    return BoundAnalyticalClaim(
        claim=claim,
        candidate_set_receipt_id=candidate_set.set_receipt_id,
        sufficiency_receipt_id=sufficiency_receipt.receipt_id,
        basis_hash=basis_hash,
    )


def build_analytical_conclusion_receipt(
    *,
    candidate_set: ReceiptBoundCandidateEvidenceSet,
    sufficiency_receipt: CandidateSufficiencyReceipt,
    claims: Iterable[BoundAnalyticalClaim],
) -> AnalyticalConclusionReceipt:
    if not verify_receipt_bound_candidate_set(candidate_set):
        raise ValueError("candidate evidence set failed integrity verification")

    if not verify_candidate_sufficiency_receipt(sufficiency_receipt):
        raise ValueError("sufficiency receipt failed integrity verification")

    if (
        sufficiency_receipt.candidate_set_receipt_id
        != candidate_set.set_receipt_id
        or sufficiency_receipt.candidate_set_integrity_hash
        != candidate_set.set_integrity_hash
    ):
        raise ValueError("sufficiency receipt is not bound to candidate set")

    if (
        sufficiency_receipt.effective_policy_id
        != candidate_set.identity.effective_policy_id
        or sufficiency_receipt.effective_policy_hash
        != candidate_set.identity.effective_policy_hash
    ):
        raise ValueError("policy continuity mismatch")

    bound_claims = tuple(claims)

    if not bound_claims:
        raise ValueError("canonical conclusion requires at least one bound claim")

    for item in bound_claims:
        if item.candidate_set_receipt_id != candidate_set.set_receipt_id:
            raise ValueError("claim/candidate set mismatch")

        if item.sufficiency_receipt_id != sufficiency_receipt.receipt_id:
            raise ValueError("claim/sufficiency receipt mismatch")

    # The sealed OBDATA096–100 compatibility primitive still accepts a
    # sufficiency string. Canonical integration derives it ONLY from the
    # verified CandidateSufficiencyReceipt.
    assessment = assess_analytical_conclusion(
        sufficiency_state=sufficiency_receipt.assessment.state.value,
        claims=tuple(item.claim for item in bound_claims),
    )

    payload = {
        "candidate_id": candidate_set.identity.candidate.candidate_id,
        "candidate_set_receipt_id": candidate_set.set_receipt_id,
        "candidate_set_integrity_hash": candidate_set.set_integrity_hash,
        "sufficiency_receipt_id": sufficiency_receipt.receipt_id,
        "sufficiency_integrity_hash": sufficiency_receipt.integrity_hash,
        "effective_policy_id": candidate_set.identity.effective_policy_id,
        "effective_policy_hash": candidate_set.identity.effective_policy_hash,
        "contract_id": candidate_set.identity.contract_id,
        "conclusion_state": assessment.state.value,
        "conclusion_reason": assessment.reason.value,
        "claim_hashes": [item.basis_hash for item in bound_claims],
    }

    digest = _hash(payload)

    return AnalyticalConclusionReceipt(
        receipt_id=f"OBCONC-{digest[:24]}",
        candidate_id=candidate_set.identity.candidate.candidate_id,
        candidate_set_receipt_id=candidate_set.set_receipt_id,
        candidate_set_integrity_hash=candidate_set.set_integrity_hash,
        sufficiency_receipt_id=sufficiency_receipt.receipt_id,
        sufficiency_integrity_hash=sufficiency_receipt.integrity_hash,
        effective_policy_id=candidate_set.identity.effective_policy_id,
        effective_policy_hash=candidate_set.identity.effective_policy_hash,
        contract_id=candidate_set.identity.contract_id,
        assessment=assessment,
        claim_hashes=tuple(item.basis_hash for item in bound_claims),
        integrity_hash=digest,
    )


def verify_analytical_conclusion_receipt(
    receipt: AnalyticalConclusionReceipt,
) -> bool:
    payload = {
        "candidate_id": receipt.candidate_id,
        "candidate_set_receipt_id": receipt.candidate_set_receipt_id,
        "candidate_set_integrity_hash": receipt.candidate_set_integrity_hash,
        "sufficiency_receipt_id": receipt.sufficiency_receipt_id,
        "sufficiency_integrity_hash": receipt.sufficiency_integrity_hash,
        "effective_policy_id": receipt.effective_policy_id,
        "effective_policy_hash": receipt.effective_policy_hash,
        "contract_id": receipt.contract_id,
        "conclusion_state": receipt.assessment.state.value,
        "conclusion_reason": receipt.assessment.reason.value,
        "claim_hashes": list(receipt.claim_hashes),
    }

    digest = _hash(payload)

    return (
        digest == receipt.integrity_hash
        and receipt.receipt_id == f"OBCONC-{digest[:24]}"
    )


def analytical_conclusion_eligible(
    receipt: AnalyticalConclusionReceipt,
) -> bool:
    return (
        verify_analytical_conclusion_receipt(receipt)
        and receipt.assessment.state is ConclusionState.ELIGIBLE
    )


def analytical_conclusion_binding_snapshot(
    receipt: AnalyticalConclusionReceipt,
) -> dict[str, object]:
    return {
        "receipt_id": receipt.receipt_id,
        "candidate_id": receipt.candidate_id,
        "candidate_set_receipt_id": receipt.candidate_set_receipt_id,
        "sufficiency_receipt_id": receipt.sufficiency_receipt_id,
        "state": receipt.assessment.state.value,
        "reason": receipt.assessment.reason.value,
        "effective_policy_id": receipt.effective_policy_id,
        "effective_policy_hash": receipt.effective_policy_hash,
        "contract_id": receipt.contract_id,
        "integrity_hash": receipt.integrity_hash,
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
