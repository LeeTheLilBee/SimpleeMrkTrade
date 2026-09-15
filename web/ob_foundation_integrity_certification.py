from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

from web.ob_analytical_conclusion_binding import (
    AnalyticalConclusionReceipt,
    verify_analytical_conclusion_receipt,
)
from web.ob_candidate_admission_receipt_binding import (
    ReceiptBoundCandidateEvidenceSet,
    verify_receipt_bound_candidate_set,
)
from web.ob_canonical_reasoning_context_spine import (
    CanonicalReasoningContextReceipt,
    verify_canonical_reasoning_context_receipt,
)
from web.ob_independence_sufficiency_binding import (
    CandidateIndependenceReceipt,
    CandidateSufficiencyReceipt,
    PolicyEvidenceRequirementSet,
    verify_candidate_independence_receipt,
    verify_candidate_sufficiency_receipt,
    verify_policy_requirement_set,
)


@dataclass(frozen=True)
class FoundationIntegrityCertificate:
    certificate_id: str
    context_receipt_id: str
    candidate_set_receipt_id: str
    independence_receipt_id: str
    requirement_set_id: str
    sufficiency_receipt_id: str
    conclusion_receipt_id: str
    observation_id: str
    observation_version: int
    lineage_hash: str
    reasoning_target_id: str
    symbol: str
    instrument_kind: str
    contract_id: str | None
    operating_mode: str
    effective_policy_id: str
    effective_policy_hash: str
    conclusion_state: str
    chain_valid: bool
    integrity_hash: str


def _hash(payload: dict[str, object]) -> str:
    return hashlib.sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
    ).hexdigest()


def certify_foundation_integrity(
    *,
    context_receipt: CanonicalReasoningContextReceipt,
    candidate_set: ReceiptBoundCandidateEvidenceSet,
    independence_receipt: CandidateIndependenceReceipt,
    requirement_set: PolicyEvidenceRequirementSet,
    sufficiency_receipt: CandidateSufficiencyReceipt,
    conclusion_receipt: AnalyticalConclusionReceipt,
) -> FoundationIntegrityCertificate:
    if not verify_canonical_reasoning_context_receipt(context_receipt):
        raise ValueError("context receipt integrity failure")

    if not verify_receipt_bound_candidate_set(candidate_set):
        raise ValueError("candidate set integrity failure")

    if not verify_candidate_independence_receipt(independence_receipt):
        raise ValueError("independence receipt integrity failure")

    if not verify_policy_requirement_set(requirement_set):
        raise ValueError("requirement set integrity failure")

    if not verify_candidate_sufficiency_receipt(sufficiency_receipt):
        raise ValueError("sufficiency receipt integrity failure")

    if not verify_analytical_conclusion_receipt(conclusion_receipt):
        raise ValueError("conclusion receipt integrity failure")

    context = context_receipt.context
    identity = candidate_set.identity

    if identity.context_receipt_id != context_receipt.receipt_id:
        raise ValueError("context/candidate receipt discontinuity")

    if identity.context_integrity_hash != context_receipt.integrity_hash:
        raise ValueError("context/candidate integrity discontinuity")

    if identity.candidate.reasoning_target_id != context.reasoning_target_id:
        raise ValueError("reasoning target discontinuity")

    if identity.candidate.target_symbol != context.instrument.symbol:
        raise ValueError("symbol discontinuity")

    if identity.candidate.target_instrument_kind != context.instrument.instrument_kind:
        raise ValueError("instrument kind discontinuity")

    if identity.contract_id != context.instrument.contract_id:
        raise ValueError("exact contract discontinuity")

    if (
        independence_receipt.candidate_set_receipt_id
        != candidate_set.set_receipt_id
        or independence_receipt.candidate_set_integrity_hash
        != candidate_set.set_integrity_hash
    ):
        raise ValueError("candidate/independence discontinuity")

    if (
        requirement_set.effective_policy_id
        != identity.effective_policy_id
        or requirement_set.effective_policy_hash
        != identity.effective_policy_hash
    ):
        raise ValueError("candidate/requirement policy discontinuity")

    if (
        sufficiency_receipt.candidate_set_receipt_id
        != candidate_set.set_receipt_id
        or sufficiency_receipt.candidate_set_integrity_hash
        != candidate_set.set_integrity_hash
        or sufficiency_receipt.independence_receipt_id
        != independence_receipt.receipt_id
        or sufficiency_receipt.requirement_set_id
        != requirement_set.requirement_set_id
    ):
        raise ValueError("sufficiency chain discontinuity")

    if (
        sufficiency_receipt.effective_policy_id
        != context.effective_policy_id
        or sufficiency_receipt.effective_policy_hash
        != context.effective_policy_hash
    ):
        raise ValueError("sufficiency policy discontinuity")

    if (
        conclusion_receipt.candidate_set_receipt_id
        != candidate_set.set_receipt_id
        or conclusion_receipt.candidate_set_integrity_hash
        != candidate_set.set_integrity_hash
        or conclusion_receipt.sufficiency_receipt_id
        != sufficiency_receipt.receipt_id
        or conclusion_receipt.sufficiency_integrity_hash
        != sufficiency_receipt.integrity_hash
    ):
        raise ValueError("conclusion chain discontinuity")

    if (
        conclusion_receipt.effective_policy_id
        != context.effective_policy_id
        or conclusion_receipt.effective_policy_hash
        != context.effective_policy_hash
    ):
        raise ValueError("conclusion policy discontinuity")

    if conclusion_receipt.contract_id != context.instrument.contract_id:
        raise ValueError("conclusion exact-contract discontinuity")

    payload = {
        "context_receipt_id": context_receipt.receipt_id,
        "candidate_set_receipt_id": candidate_set.set_receipt_id,
        "independence_receipt_id": independence_receipt.receipt_id,
        "requirement_set_id": requirement_set.requirement_set_id,
        "sufficiency_receipt_id": sufficiency_receipt.receipt_id,
        "conclusion_receipt_id": conclusion_receipt.receipt_id,
        "observation_id": context.observation_id,
        "observation_version": context.observation_version,
        "lineage_hash": context.lineage_hash,
        "reasoning_target_id": context.reasoning_target_id,
        "symbol": context.instrument.symbol,
        "instrument_kind": context.instrument.instrument_kind,
        "contract_id": context.instrument.contract_id,
        "operating_mode": context.operating_mode,
        "effective_policy_id": context.effective_policy_id,
        "effective_policy_hash": context.effective_policy_hash,
        "conclusion_state": conclusion_receipt.assessment.state.value,
        "chain_valid": True,
    }

    digest = _hash(payload)

    return FoundationIntegrityCertificate(
        certificate_id=f"OBFOUND-{digest[:24]}",
        context_receipt_id=context_receipt.receipt_id,
        candidate_set_receipt_id=candidate_set.set_receipt_id,
        independence_receipt_id=independence_receipt.receipt_id,
        requirement_set_id=requirement_set.requirement_set_id,
        sufficiency_receipt_id=sufficiency_receipt.receipt_id,
        conclusion_receipt_id=conclusion_receipt.receipt_id,
        observation_id=context.observation_id,
        observation_version=context.observation_version,
        lineage_hash=context.lineage_hash,
        reasoning_target_id=context.reasoning_target_id,
        symbol=context.instrument.symbol,
        instrument_kind=context.instrument.instrument_kind,
        contract_id=context.instrument.contract_id,
        operating_mode=context.operating_mode,
        effective_policy_id=context.effective_policy_id,
        effective_policy_hash=context.effective_policy_hash,
        conclusion_state=conclusion_receipt.assessment.state.value,
        chain_valid=True,
        integrity_hash=digest,
    )


def verify_foundation_integrity_certificate(
    certificate: FoundationIntegrityCertificate,
) -> bool:
    payload = {
        "context_receipt_id": certificate.context_receipt_id,
        "candidate_set_receipt_id": certificate.candidate_set_receipt_id,
        "independence_receipt_id": certificate.independence_receipt_id,
        "requirement_set_id": certificate.requirement_set_id,
        "sufficiency_receipt_id": certificate.sufficiency_receipt_id,
        "conclusion_receipt_id": certificate.conclusion_receipt_id,
        "observation_id": certificate.observation_id,
        "observation_version": certificate.observation_version,
        "lineage_hash": certificate.lineage_hash,
        "reasoning_target_id": certificate.reasoning_target_id,
        "symbol": certificate.symbol,
        "instrument_kind": certificate.instrument_kind,
        "contract_id": certificate.contract_id,
        "operating_mode": certificate.operating_mode,
        "effective_policy_id": certificate.effective_policy_id,
        "effective_policy_hash": certificate.effective_policy_hash,
        "conclusion_state": certificate.conclusion_state,
        "chain_valid": certificate.chain_valid,
    }

    digest = _hash(payload)

    return (
        certificate.chain_valid is True
        and digest == certificate.integrity_hash
        and certificate.certificate_id == f"OBFOUND-{digest[:24]}"
    )


def foundation_integrity_snapshot(
    certificate: FoundationIntegrityCertificate,
) -> dict[str, object]:
    return {
        "certificate_id": certificate.certificate_id,
        "chain_valid": certificate.chain_valid,
        "observation_id": certificate.observation_id,
        "observation_version": certificate.observation_version,
        "lineage_hash": certificate.lineage_hash,
        "reasoning_target_id": certificate.reasoning_target_id,
        "symbol": certificate.symbol,
        "instrument_kind": certificate.instrument_kind,
        "contract_id": certificate.contract_id,
        "operating_mode": certificate.operating_mode,
        "effective_policy_id": certificate.effective_policy_id,
        "effective_policy_hash": certificate.effective_policy_hash,
        "conclusion_state": certificate.conclusion_state,
        "integrity_hash": certificate.integrity_hash,
        "authority_boundary": {
            "foundation_integrity_certification_only": True,
            "natural_language_truth_proof": False,
            "logical_inference_proof": False,
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
