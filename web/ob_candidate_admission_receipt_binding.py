from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

from web.ob_candidate_evidence_admission import (
    AdmissionState,
    CandidateEvidenceItem,
    CandidateEvidenceSet,
    CandidateIdentity,
    admit_candidate_evidence,
    assess_candidate_evidence_admission,
    build_candidate_evidence_item,
    candidate_evidence_set_integrity,
    empty_candidate_evidence_set,
)
from web.ob_canonical_reasoning_context_spine import (
    CanonicalReasoningContextReceipt,
    canonical_context_eligible,
    verify_canonical_reasoning_context_receipt,
)


@dataclass(frozen=True)
class BoundCandidateIdentity:
    candidate: CandidateIdentity
    context_receipt_id: str
    context_integrity_hash: str
    effective_policy_id: str
    effective_policy_hash: str
    contract_id: str | None


@dataclass(frozen=True)
class ReceiptBoundEvidenceItem:
    candidate_id: str
    context_receipt_id: str
    context_integrity_hash: str
    item: CandidateEvidenceItem


@dataclass(frozen=True)
class CandidateAdmissionReceipt:
    receipt_id: str
    candidate_id: str
    context_receipt_id: str
    context_integrity_hash: str
    observation_id: str
    observation_version: int
    lineage_hash: str
    state: str
    reason: str
    integrity_hash: str


@dataclass(frozen=True)
class ReceiptBoundCandidateEvidenceSet:
    identity: BoundCandidateIdentity
    evidence_set: CandidateEvidenceSet
    admission_receipts: tuple[CandidateAdmissionReceipt, ...]
    set_receipt_id: str
    set_integrity_hash: str


def _nonblank(value: object, *, name: str) -> str:
    text = str(value).strip()
    if not text:
        raise ValueError(f"{name} cannot be blank")
    return text


def _hash(payload: dict[str, object]) -> str:
    raw = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def bind_candidate_identity(
    *,
    candidate_id: str,
    purpose: str,
    context_receipt: CanonicalReasoningContextReceipt,
) -> BoundCandidateIdentity:
    if not verify_canonical_reasoning_context_receipt(context_receipt):
        raise ValueError("canonical reasoning-context receipt failed integrity verification")

    if not canonical_context_eligible(context_receipt):
        raise ValueError("canonical reasoning context is not eligible")

    context = context_receipt.context

    candidate = CandidateIdentity(
        candidate_id=_nonblank(candidate_id, name="candidate_id"),
        reasoning_target_id=context.reasoning_target_id,
        target_symbol=context.instrument.symbol,
        target_instrument_kind=context.instrument.instrument_kind,
        purpose=_nonblank(purpose, name="purpose"),
    )

    return BoundCandidateIdentity(
        candidate=candidate,
        context_receipt_id=context_receipt.receipt_id,
        context_integrity_hash=context_receipt.integrity_hash,
        effective_policy_id=context.effective_policy_id,
        effective_policy_hash=context.effective_policy_hash,
        contract_id=context.instrument.contract_id,
    )


def evidence_item_from_context_receipt(
    *,
    identity: BoundCandidateIdentity,
    context_receipt: CanonicalReasoningContextReceipt,
) -> ReceiptBoundEvidenceItem:
    if not verify_canonical_reasoning_context_receipt(context_receipt):
        raise ValueError("canonical reasoning-context receipt failed integrity verification")

    if not canonical_context_eligible(context_receipt):
        raise ValueError("canonical reasoning context is not eligible")

    if identity.context_receipt_id != context_receipt.receipt_id:
        raise ValueError("candidate/context receipt mismatch")

    if identity.context_integrity_hash != context_receipt.integrity_hash:
        raise ValueError("candidate/context integrity mismatch")

    context = context_receipt.context
    candidate = identity.candidate

    if context.reasoning_target_id != candidate.reasoning_target_id:
        raise ValueError("reasoning target mismatch")

    if context.instrument.symbol != candidate.target_symbol:
        raise ValueError("symbol mismatch")

    if context.instrument.instrument_kind != candidate.target_instrument_kind:
        raise ValueError("instrument kind mismatch")

    item = build_candidate_evidence_item(
        observation_id=context.observation_id,
        observation_version=context.observation_version,
        lineage_hash=context.lineage_hash,
        reasoning_target_id=context.reasoning_target_id,
        target_symbol=context.instrument.symbol,
        target_instrument_kind=context.instrument.instrument_kind,
        upstream_composition_state=context_receipt.state.value,
    )

    return ReceiptBoundEvidenceItem(
        candidate_id=candidate.candidate_id,
        context_receipt_id=context_receipt.receipt_id,
        context_integrity_hash=context_receipt.integrity_hash,
        item=item,
    )


def _admission_payload(
    *,
    candidate_id: str,
    bound_item: ReceiptBoundEvidenceItem,
    state: str,
    reason: str,
) -> dict[str, object]:
    item = bound_item.item

    return {
        "candidate_id": candidate_id,
        "context_receipt_id": bound_item.context_receipt_id,
        "context_integrity_hash": bound_item.context_integrity_hash,
        "observation_id": item.observation_id,
        "observation_version": item.observation_version,
        "lineage_hash": item.lineage_hash,
        "state": state,
        "reason": reason,
    }


def assess_receipt_bound_admission(
    *,
    bound_set: ReceiptBoundCandidateEvidenceSet,
    bound_item: ReceiptBoundEvidenceItem,
) -> CandidateAdmissionReceipt:
    if bound_item.candidate_id != bound_set.identity.candidate.candidate_id:
        state = AdmissionState.BLOCKED.value
        reason = "CANDIDATE_ID_MISMATCH"
    elif bound_item.context_receipt_id != bound_set.identity.context_receipt_id:
        state = AdmissionState.BLOCKED.value
        reason = "CONTEXT_RECEIPT_MISMATCH"
    elif bound_item.context_integrity_hash != bound_set.identity.context_integrity_hash:
        state = AdmissionState.BLOCKED.value
        reason = "CONTEXT_INTEGRITY_MISMATCH"
    else:
        assessment = assess_candidate_evidence_admission(
            evidence_set=bound_set.evidence_set,
            item=bound_item.item,
        )
        state = assessment.state.value
        reason = assessment.reason.value

    payload = _admission_payload(
        candidate_id=bound_set.identity.candidate.candidate_id,
        bound_item=bound_item,
        state=state,
        reason=reason,
    )

    digest = _hash(payload)

    return CandidateAdmissionReceipt(
        receipt_id=f"OBADM-{digest[:24]}",
        candidate_id=bound_set.identity.candidate.candidate_id,
        context_receipt_id=bound_item.context_receipt_id,
        context_integrity_hash=bound_item.context_integrity_hash,
        observation_id=bound_item.item.observation_id,
        observation_version=bound_item.item.observation_version,
        lineage_hash=bound_item.item.lineage_hash,
        state=state,
        reason=reason,
        integrity_hash=digest,
    )


def verify_candidate_admission_receipt(
    receipt: CandidateAdmissionReceipt,
) -> bool:
    payload = {
        "candidate_id": receipt.candidate_id,
        "context_receipt_id": receipt.context_receipt_id,
        "context_integrity_hash": receipt.context_integrity_hash,
        "observation_id": receipt.observation_id,
        "observation_version": receipt.observation_version,
        "lineage_hash": receipt.lineage_hash,
        "state": receipt.state,
        "reason": receipt.reason,
    }

    digest = _hash(payload)

    return (
        receipt.integrity_hash == digest
        and receipt.receipt_id == f"OBADM-{digest[:24]}"
    )


def _set_hash(
    identity: BoundCandidateIdentity,
    evidence_set: CandidateEvidenceSet,
    receipts: tuple[CandidateAdmissionReceipt, ...],
) -> str:
    payload = {
        "candidate_id": identity.candidate.candidate_id,
        "context_receipt_id": identity.context_receipt_id,
        "context_integrity_hash": identity.context_integrity_hash,
        "effective_policy_id": identity.effective_policy_id,
        "effective_policy_hash": identity.effective_policy_hash,
        "contract_id": identity.contract_id,
        "items": [
            {
                "observation_id": item.observation_id,
                "observation_version": item.observation_version,
                "lineage_hash": item.lineage_hash,
            }
            for item in evidence_set.items
        ],
        "admission_receipts": [
            receipt.receipt_id
            for receipt in receipts
        ],
    }
    return _hash(payload)


def empty_receipt_bound_candidate_set(
    identity: BoundCandidateIdentity,
) -> ReceiptBoundCandidateEvidenceSet:
    evidence_set = empty_candidate_evidence_set(identity.candidate)
    digest = _set_hash(identity, evidence_set, ())

    return ReceiptBoundCandidateEvidenceSet(
        identity=identity,
        evidence_set=evidence_set,
        admission_receipts=(),
        set_receipt_id=f"OBSET-{digest[:24]}",
        set_integrity_hash=digest,
    )


def admit_receipt_bound_evidence(
    *,
    bound_set: ReceiptBoundCandidateEvidenceSet,
    bound_item: ReceiptBoundEvidenceItem,
) -> ReceiptBoundCandidateEvidenceSet:
    if not verify_receipt_bound_candidate_set(bound_set):
        raise ValueError("candidate evidence set failed integrity verification")

    receipt = assess_receipt_bound_admission(
        bound_set=bound_set,
        bound_item=bound_item,
    )

    if receipt.state != AdmissionState.ADMITTED.value:
        raise ValueError(f"evidence admission blocked: {receipt.reason}")

    new_set = admit_candidate_evidence(
        evidence_set=bound_set.evidence_set,
        item=bound_item.item,
    )

    receipts = (*bound_set.admission_receipts, receipt)
    digest = _set_hash(bound_set.identity, new_set, receipts)

    return ReceiptBoundCandidateEvidenceSet(
        identity=bound_set.identity,
        evidence_set=new_set,
        admission_receipts=receipts,
        set_receipt_id=f"OBSET-{digest[:24]}",
        set_integrity_hash=digest,
    )


def verify_receipt_bound_candidate_set(
    bound_set: ReceiptBoundCandidateEvidenceSet,
) -> bool:
    if not candidate_evidence_set_integrity(bound_set.evidence_set):
        return False

    if bound_set.evidence_set.candidate != bound_set.identity.candidate:
        return False

    if len(bound_set.evidence_set.items) != len(bound_set.admission_receipts):
        return False

    for item, receipt in zip(
        bound_set.evidence_set.items,
        bound_set.admission_receipts,
    ):
        if not verify_candidate_admission_receipt(receipt):
            return False

        if receipt.state != AdmissionState.ADMITTED.value:
            return False

        if receipt.candidate_id != bound_set.identity.candidate.candidate_id:
            return False

        if receipt.context_receipt_id != bound_set.identity.context_receipt_id:
            return False

        if receipt.context_integrity_hash != bound_set.identity.context_integrity_hash:
            return False

        if (
            receipt.observation_id != item.observation_id
            or receipt.observation_version != item.observation_version
            or receipt.lineage_hash != item.lineage_hash
        ):
            return False

    digest = _set_hash(
        bound_set.identity,
        bound_set.evidence_set,
        bound_set.admission_receipts,
    )

    return (
        digest == bound_set.set_integrity_hash
        and bound_set.set_receipt_id == f"OBSET-{digest[:24]}"
    )


def receipt_bound_candidate_snapshot(
    bound_set: ReceiptBoundCandidateEvidenceSet,
) -> dict[str, object]:
    return {
        "candidate_id": bound_set.identity.candidate.candidate_id,
        "context_receipt_id": bound_set.identity.context_receipt_id,
        "set_receipt_id": bound_set.set_receipt_id,
        "set_integrity_hash": bound_set.set_integrity_hash,
        "evidence_count": len(bound_set.evidence_set.items),
        "integrity": verify_receipt_bound_candidate_set(bound_set),
        "effective_policy_id": bound_set.identity.effective_policy_id,
        "effective_policy_hash": bound_set.identity.effective_policy_hash,
        "contract_id": bound_set.identity.contract_id,
        "authority_boundary": {
            "candidate_evidence_admission_only": True,
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
