from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from typing import Iterable, Mapping

from web.ob_reasoning_context_composition import GateVerdict

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
from web.ob_candidate_evidence_sufficiency import (
    CandidateEvidenceSufficiencyAssessment,
    EvidenceRequirement,
    SufficiencyState,
    assess_candidate_evidence_sufficiency,
    build_candidate_evidence_support,
)
from web.ob_canonical_reasoning_context_spine import (
    CanonicalReasoningContextReceipt,
    canonical_context_eligible,
    verify_canonical_reasoning_context_receipt,
)
from web.ob_evidence_independence import (
    CorroborationWeightAssessment,
    EvidenceOriginIdentity,
    assess_corroboration_weight_integrity,
)


def _hash(payload: object) -> str:
    return hashlib.sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            default=str,
        ).encode("utf-8")
    ).hexdigest()


def _nonblank(value: object, *, name: str) -> str:
    text = str(value).strip()
    if not text:
        raise ValueError(f"{name} cannot be blank")
    return text



ALLOWED_NATIVE_AUTHORITY_MODULES = (
    "web.ob_source_provenance",
    "web.ob_observation_freshness",
    "web.ob_cross_source_corroboration",
    "web.ob_observation_quality",
    "web.ob_effective_observation",
    "web.ob_observation_conflict",
    "web.ob_evidence_lineage",
    "web.ob_observation_versioning",
    "web.ob_observation_lifecycle",
    "web.ob_observation_revocation",
    "web.ob_observation_rehabilitation",
    "web.ob_observation_temporal_validity",
    "web.ob_observation_instrument_binding",
)


def _instrument_payload(instrument) -> dict[str, object]:
    return {
        "symbol": instrument.symbol,
        "instrument_kind": instrument.instrument_kind,
        "contract_id": instrument.contract_id,
        "underlying_symbol": instrument.underlying_symbol,
        "option_right": instrument.option_right,
        "strike": instrument.strike,
        "expiration": instrument.expiration,
    }


# ==============================================================================================================
# OBFIXINT001 — VERIFIED AUTHORITY SOURCE BOUNDARY
# ==============================================================================================================

@dataclass(frozen=True)
class VerifiedAuthorityArtifact:
    gate: str
    observation_id: str
    observation_version: int
    reasoning_target_id: str
    symbol: str
    instrument_kind: str
    verdict: str
    reason: str
    native_authority_type: str
    native_authority_identity: str
    native_authority_hash: str
    native_payload_hash: str
    integrity_hash: str



def _native_enum_value(value: object) -> str:
    raw = getattr(value, "value", value)
    return str(raw).strip().upper()


def _native_reason(native_authority: object) -> str:
    for attr in ("reason", "reasons", "limitations"):
        if not hasattr(native_authority, attr):
            continue

        value = getattr(native_authority, attr)

        if isinstance(value, str) and value.strip():
            return value.strip()

        if isinstance(value, (tuple, list)) and value:
            joined = " ".join(
                str(item).strip()
                for item in value
                if str(item).strip()
            )

            if joined:
                return joined

    return (
        f"Native authority "
        f"{native_authority.__class__.__qualname__} "
        f"derived the certified gate state."
    )


def _derive_native_gate_verdict(
    *,
    gate: str,
    native_authority: object,
) -> tuple[GateVerdict, str]:

    module = native_authority.__class__.__module__

    if module not in ALLOWED_NATIVE_AUTHORITY_MODULES:
        raise ValueError(
            "native authority type is not an approved OBDATA authority"
        )

    reason = _native_reason(native_authority)

    if gate == "source_provenance":
        status = _native_enum_value(
            getattr(native_authority, "status", "UNKNOWN")
        )

        if status == "COMPLETE":
            return GateVerdict.ALLOW, reason

        if status == "INCOMPLETE":
            return GateVerdict.BLOCK, reason

        return GateVerdict.UNKNOWN, reason

    if gate == "freshness":
        status = _native_enum_value(
            getattr(native_authority, "status", "UNKNOWN")
        )

        if status == "FRESH":
            return GateVerdict.ALLOW, reason

        if status == "AGING":
            return GateVerdict.REVIEW, reason

        if status in {"STALE", "EXPIRED"}:
            return GateVerdict.BLOCK, reason

        return GateVerdict.UNKNOWN, reason

    if gate == "corroboration":
        status = _native_enum_value(
            getattr(native_authority, "status", "UNKNOWN")
        )

        if status in {"SINGLE_SOURCE", "CORROBORATED"}:
            return GateVerdict.ALLOW, reason

        if status == "MINOR_DISAGREEMENT":
            return GateVerdict.REVIEW, reason

        if status in {
            "MATERIAL_DISAGREEMENT",
            "CONFLICTED",
        }:
            return GateVerdict.BLOCK, reason

        return GateVerdict.UNKNOWN, reason

    if gate == "quality":
        disposition = _native_enum_value(
            getattr(native_authority, "disposition", "UNKNOWN")
        )

        if disposition == "ACCEPT":
            return GateVerdict.ALLOW, reason

        if disposition == "REVIEW":
            return GateVerdict.REVIEW, reason

        if disposition in {"QUARANTINE", "REJECT"}:
            return GateVerdict.BLOCK, reason

        return GateVerdict.UNKNOWN, reason

    if gate == "effective_observation":
        state = _native_enum_value(
            getattr(native_authority, "state", "UNKNOWN")
        )

        if state in {"TRUSTED", "USABLE"}:
            return GateVerdict.ALLOW, reason

        if state == "CAUTION":
            return GateVerdict.REVIEW, reason

        if state in {"QUARANTINED", "UNUSABLE"}:
            return GateVerdict.BLOCK, reason

        return GateVerdict.UNKNOWN, reason

    if gate == "conflict":
        escalation = _native_enum_value(
            getattr(native_authority, "escalation", "UNKNOWN")
        )

        if escalation == "NONE":
            return GateVerdict.ALLOW, reason

        if escalation in {"REVIEW", "OWNER_REVIEW"}:
            return GateVerdict.REVIEW, reason

        if escalation == "HARD_BLOCK":
            return GateVerdict.BLOCK, reason

        return GateVerdict.UNKNOWN, reason

    for attr in (
        "state",
        "status",
        "disposition",
        "validity",
        "lifecycle",
        "binding",
        "result",
    ):
        if hasattr(native_authority, attr):
            native_state = _native_enum_value(
                getattr(native_authority, attr)
            )
            break
    else:
        native_state = "UNKNOWN"

    allow_states = {
        "ALLOW",
        "ALLOWED",
        "VALID",
        "CURRENT",
        "ACTIVE",
        "COMPLETE",
        "VERIFIED",
        "BOUND",
        "MATCHED",
        "MATCH",
        "CONSISTENT",
        "INTACT",
        "AVAILABLE",
        "ELIGIBLE",
        "REHABILITATED",
        "NOT_REVOKED",
    }

    review_states = {
        "REVIEW",
        "REVIEW_REQUIRED",
        "CAUTION",
        "AGING",
        "DEGRADED",
        "PARTIAL",
        "RECONCILABLE",
    }

    block_states = {
        "BLOCK",
        "BLOCKED",
        "INVALID",
        "STALE",
        "EXPIRED",
        "REVOKED",
        "SUPERSEDED",
        "INACTIVE",
        "QUARANTINED",
        "UNUSABLE",
        "REJECT",
        "MISMATCH",
        "CONFLICTED",
        "HARD_BLOCK",
        "INELIGIBLE",
    }

    if native_state in allow_states:
        return GateVerdict.ALLOW, reason

    if native_state in review_states:
        return GateVerdict.REVIEW, reason

    if native_state in block_states:
        return GateVerdict.BLOCK, reason

    return GateVerdict.UNKNOWN, reason


def build_verified_authority_artifact(
    *,
    gate: str,
    observation_id: str,
    observation_version: int,
    reasoning_target_id: str,
    symbol: str,
    instrument_kind: str,
    native_authority: object,
) -> VerifiedAuthorityArtifact:
    """
    Compatibility-safe closure boundary.

    The canonical closure path no longer accepts a bare caller assertion
    consisting only of verdict/reason/hash strings.

    A concrete native authority object must be supplied and its complete
    dataclass/dict/object state is serialized into the artifact.

    This does NOT claim every legacy OBDATA primitive has already been
    redesigned as a receipt. It prevents the closure path from treating
    arbitrary authority_identity/authority_hash strings as native proof.
    """

    if native_authority is None:
        raise ValueError("native authority object is required")

    native_module = native_authority.__class__.__module__

    if native_module not in ALLOWED_NATIVE_AUTHORITY_MODULES:
        raise ValueError(
            "native authority type is not an approved OBDATA authority"
        )

    if not hasattr(native_authority, "__dataclass_fields__"):
        raise ValueError(
            "approved native authority must be a dataclass authority object"
        )

    native_payload = asdict(native_authority)

    native_type = (
        f"{native_authority.__class__.__module__}."
        f"{native_authority.__class__.__qualname__}"
    )

    native_payload_hash = _hash(native_payload)

    flattened = json.dumps(
        native_payload,
        sort_keys=True,
        default=str,
    ).upper()

    derived_verdict, derived_reason = _derive_native_gate_verdict(
        gate=gate,
        native_authority=native_authority,
    )

    native_identity = (
        f"{native_type}:"
        f"{observation_id}:{observation_version}:{gate}"
    )

    native_hash = _hash({
        "type": native_type,
        "payload": native_payload,
    })

    payload = {
        "gate": _nonblank(gate, name="gate"),
        "observation_id": _nonblank(
            observation_id,
            name="observation_id",
        ),
        "observation_version": int(observation_version),
        "reasoning_target_id": _nonblank(
            reasoning_target_id,
            name="reasoning_target_id",
        ),
        "symbol": _nonblank(symbol, name="symbol").upper(),
        "instrument_kind": _nonblank(
            instrument_kind,
            name="instrument_kind",
        ).upper(),
        "verdict": derived_verdict.value,
        "reason": derived_reason,
        "native_authority_type": native_type,
        "native_authority_identity": native_identity,
        "native_authority_hash": native_hash,
        "native_payload_hash": native_payload_hash,
    }

    digest = _hash(payload)

    return VerifiedAuthorityArtifact(
        **payload,
        integrity_hash=digest,
    )


def verify_verified_authority_artifact(
    artifact: VerifiedAuthorityArtifact,
) -> bool:
    payload = {
        "gate": artifact.gate,
        "observation_id": artifact.observation_id,
        "observation_version": artifact.observation_version,
        "reasoning_target_id": artifact.reasoning_target_id,
        "symbol": artifact.symbol,
        "instrument_kind": artifact.instrument_kind,
        "verdict": artifact.verdict,
        "reason": artifact.reason,
        "native_authority_type": artifact.native_authority_type,
        "native_authority_identity": artifact.native_authority_identity,
        "native_authority_hash": artifact.native_authority_hash,
        "native_payload_hash": artifact.native_payload_hash,
    }

    return _hash(payload) == artifact.integrity_hash


# ==============================================================================================================
# OBFIXINT002 — MULTI-CONTEXT CANDIDATE AGGREGATION
# ==============================================================================================================

@dataclass(frozen=True)
class ClosureCandidateIdentity:
    candidate_id: str
    reasoning_target_id: str
    instrument_payload: dict[str, object]
    operating_mode: str
    effective_policy_id: str
    effective_policy_hash: str
    purpose: str


@dataclass(frozen=True)
class ClosureEvidenceItem:
    candidate_id: str
    context_receipt_id: str
    context_integrity_hash: str
    observation_id: str
    observation_version: int
    lineage_hash: str
    provenance_identity: str
    item: CandidateEvidenceItem


@dataclass(frozen=True)
class ClosureCandidateSet:
    identity: ClosureCandidateIdentity
    evidence_set: CandidateEvidenceSet
    evidence_items: tuple[ClosureEvidenceItem, ...]
    set_receipt_id: str
    integrity_hash: str


def build_closure_candidate_identity(
    *,
    candidate_id: str,
    purpose: str,
    context_receipt: CanonicalReasoningContextReceipt,
) -> ClosureCandidateIdentity:
    if not verify_canonical_reasoning_context_receipt(context_receipt):
        raise ValueError("context receipt integrity failure")

    if not canonical_context_eligible(context_receipt):
        raise ValueError("context is not eligible")

    context = context_receipt.context

    return ClosureCandidateIdentity(
        candidate_id=_nonblank(candidate_id, name="candidate_id"),
        reasoning_target_id=context.reasoning_target_id,
        instrument_payload=_instrument_payload(context.instrument),
        operating_mode=context.operating_mode,
        effective_policy_id=context.effective_policy_id,
        effective_policy_hash=context.effective_policy_hash,
        purpose=_nonblank(purpose, name="purpose"),
    )


def _legacy_candidate(identity: ClosureCandidateIdentity) -> CandidateIdentity:
    return CandidateIdentity(
        candidate_id=identity.candidate_id,
        reasoning_target_id=identity.reasoning_target_id,
        target_symbol=str(identity.instrument_payload["symbol"]),
        target_instrument_kind=str(
            identity.instrument_payload["instrument_kind"]
        ),
        purpose=identity.purpose,
    )


def _candidate_set_hash(
    identity: ClosureCandidateIdentity,
    items: tuple[ClosureEvidenceItem, ...],
) -> str:
    return _hash({
        "identity": {
            "candidate_id": identity.candidate_id,
            "reasoning_target_id": identity.reasoning_target_id,
            "instrument": identity.instrument_payload,
            "operating_mode": identity.operating_mode,
            "effective_policy_id": identity.effective_policy_id,
            "effective_policy_hash": identity.effective_policy_hash,
            "purpose": identity.purpose,
        },
        "evidence": [
            {
                "context_receipt_id": item.context_receipt_id,
                "context_integrity_hash": item.context_integrity_hash,
                "observation_id": item.observation_id,
                "observation_version": item.observation_version,
                "lineage_hash": item.lineage_hash,
                "provenance_identity": item.provenance_identity,
            }
            for item in items
        ],
    })


def empty_closure_candidate_set(
    identity: ClosureCandidateIdentity,
) -> ClosureCandidateSet:
    legacy = empty_candidate_evidence_set(_legacy_candidate(identity))
    digest = _candidate_set_hash(identity, ())

    return ClosureCandidateSet(
        identity=identity,
        evidence_set=legacy,
        evidence_items=(),
        set_receipt_id=f"OBFIXSET-{digest[:24]}",
        integrity_hash=digest,
    )


def evidence_from_compatible_context(
    *,
    identity: ClosureCandidateIdentity,
    context_receipt: CanonicalReasoningContextReceipt,
) -> ClosureEvidenceItem:
    if not verify_canonical_reasoning_context_receipt(context_receipt):
        raise ValueError("context receipt integrity failure")

    if not canonical_context_eligible(context_receipt):
        raise ValueError("context is not eligible")

    context = context_receipt.context

    if context.reasoning_target_id != identity.reasoning_target_id:
        raise ValueError("reasoning target mismatch")

    if _instrument_payload(context.instrument) != identity.instrument_payload:
        raise ValueError("exact instrument identity mismatch")

    if context.operating_mode != identity.operating_mode:
        raise ValueError("operating mode mismatch")

    if context.effective_policy_id != identity.effective_policy_id:
        raise ValueError("effective policy id mismatch")

    if context.effective_policy_hash != identity.effective_policy_hash:
        raise ValueError("effective policy hash mismatch")

    item = build_candidate_evidence_item(
        observation_id=context.observation_id,
        observation_version=context.observation_version,
        lineage_hash=context.lineage_hash,
        reasoning_target_id=context.reasoning_target_id,
        target_symbol=context.instrument.symbol,
        target_instrument_kind=context.instrument.instrument_kind,
        upstream_composition_state=context_receipt.state.value,
    )

    return ClosureEvidenceItem(
        candidate_id=identity.candidate_id,
        context_receipt_id=context_receipt.receipt_id,
        context_integrity_hash=context_receipt.integrity_hash,
        observation_id=context.observation_id,
        observation_version=context.observation_version,
        lineage_hash=context.lineage_hash,
        provenance_identity=context.provenance_identity,
        item=item,
    )


def admit_closure_evidence(
    *,
    candidate_set: ClosureCandidateSet,
    evidence: ClosureEvidenceItem,
) -> ClosureCandidateSet:
    if evidence.candidate_id != candidate_set.identity.candidate_id:
        raise ValueError("candidate id mismatch")

    assessment = assess_candidate_evidence_admission(
        evidence_set=candidate_set.evidence_set,
        item=evidence.item,
    )

    if assessment.state is not AdmissionState.ADMITTED:
        raise ValueError(
            f"evidence admission blocked: {assessment.reason.value}"
        )

    legacy = admit_candidate_evidence(
        evidence_set=candidate_set.evidence_set,
        item=evidence.item,
    )

    items = (*candidate_set.evidence_items, evidence)
    digest = _candidate_set_hash(candidate_set.identity, items)

    return ClosureCandidateSet(
        identity=candidate_set.identity,
        evidence_set=legacy,
        evidence_items=items,
        set_receipt_id=f"OBFIXSET-{digest[:24]}",
        integrity_hash=digest,
    )


def verify_closure_candidate_set(
    candidate_set: ClosureCandidateSet,
) -> bool:
    if not candidate_evidence_set_integrity(candidate_set.evidence_set):
        return False

    if candidate_set.evidence_set.candidate != _legacy_candidate(
        candidate_set.identity
    ):
        return False

    if len(candidate_set.evidence_set.items) != len(
        candidate_set.evidence_items
    ):
        return False

    for legacy, bound in zip(
        candidate_set.evidence_set.items,
        candidate_set.evidence_items,
    ):
        if (
            legacy.observation_id != bound.observation_id
            or legacy.observation_version != bound.observation_version
            or legacy.lineage_hash != bound.lineage_hash
        ):
            return False

    digest = _candidate_set_hash(
        candidate_set.identity,
        candidate_set.evidence_items,
    )

    return (
        digest == candidate_set.integrity_hash
        and candidate_set.set_receipt_id
        == f"OBFIXSET-{digest[:24]}"
    )


# ==============================================================================================================
# OBFIXINT003 — ORIGIN CONTINUITY
# ==============================================================================================================

@dataclass(frozen=True)
class ClosureEvidenceOrigin:
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
class ClosureIndependenceReceipt:
    receipt_id: str
    candidate_set_receipt_id: str
    candidate_set_integrity_hash: str
    origins: tuple[ClosureEvidenceOrigin, ...]
    origin_hash: str
    assessment: CorroborationWeightAssessment
    assessment_hash: str
    integrity_hash: str


def _origin_payload(origins):
    return [
        {
            "observation_id": x.observation_id,
            "observation_version": x.observation_version,
            "lineage_hash": x.lineage_hash,
            "source_id": x.source_id,
            "source_family_id": x.source_family_id,
            "origin_family_id": x.origin_family_id,
            "independence_family_id": x.independence_family_id,
            "dependency_ids": list(x.dependency_ids),
            "dependency_known": x.dependency_known,
            "category": x.category.upper(),
        }
        for x in sorted(
            origins,
            key=lambda x: (
                x.observation_id,
                x.observation_version,
                x.lineage_hash,
            ),
        )
    ]


def build_closure_independence_receipt(
    *,
    candidate_set: ClosureCandidateSet,
    origins: Iterable[ClosureEvidenceOrigin],
) -> ClosureIndependenceReceipt:
    if not verify_closure_candidate_set(candidate_set):
        raise ValueError("candidate set integrity failure")

    origins = tuple(origins)

    expected = {
        (
            x.observation_id,
            x.observation_version,
            x.lineage_hash,
        )
        for x in candidate_set.evidence_items
    }

    actual = {
        (
            x.observation_id,
            x.observation_version,
            x.lineage_hash,
        )
        for x in origins
    }

    if expected != actual or len(actual) != len(origins):
        raise ValueError("origins must exactly cover candidate evidence")

    identities = tuple(
        EvidenceOriginIdentity(
            observation_id=x.observation_id,
            observation_version=x.observation_version,
            lineage_hash=x.lineage_hash,
            source_id=x.source_id,
            source_family_id=x.source_family_id,
            origin_family_id=x.origin_family_id,
            independence_family_id=x.independence_family_id,
            dependency_ids=x.dependency_ids,
            dependency_known=x.dependency_known,
        )
        for x in origins
    )

    assessment = assess_corroboration_weight_integrity(identities)

    origin_hash = _hash({"origins": _origin_payload(origins)})
    assessment_payload = asdict(assessment)
    assessment_hash = _hash(assessment_payload)

    payload = {
        "candidate_set_receipt_id": candidate_set.set_receipt_id,
        "candidate_set_integrity_hash": candidate_set.integrity_hash,
        "origin_hash": origin_hash,
        "assessment": assessment_payload,
        "assessment_hash": assessment_hash,
    }

    digest = _hash(payload)

    return ClosureIndependenceReceipt(
        receipt_id=f"OBFIXIND-{digest[:24]}",
        candidate_set_receipt_id=candidate_set.set_receipt_id,
        candidate_set_integrity_hash=candidate_set.integrity_hash,
        origins=origins,
        origin_hash=origin_hash,
        assessment=assessment,
        assessment_hash=assessment_hash,
        integrity_hash=digest,
    )


def verify_closure_independence_receipt(
    receipt: ClosureIndependenceReceipt,
) -> bool:
    origin_hash = _hash({
        "origins": _origin_payload(receipt.origins)
    })

    assessment_payload = asdict(receipt.assessment)
    assessment_hash = _hash(assessment_payload)

    payload = {
        "candidate_set_receipt_id": receipt.candidate_set_receipt_id,
        "candidate_set_integrity_hash": receipt.candidate_set_integrity_hash,
        "origin_hash": origin_hash,
        "assessment": assessment_payload,
        "assessment_hash": assessment_hash,
    }

    digest = _hash(payload)

    return (
        origin_hash == receipt.origin_hash
        and assessment_hash == receipt.assessment_hash
        and digest == receipt.integrity_hash
        and receipt.receipt_id == f"OBFIXIND-{digest[:24]}"
    )


# ==============================================================================================================
# OBFIXINT004 — POLICY REQUIREMENT AUTHORSHIP
# ==============================================================================================================

@dataclass(frozen=True)
class PolicyRequirementAuthority:
    authority_id: str
    effective_policy_id: str
    effective_policy_hash: str
    requirements: tuple[EvidenceRequirement, ...]
    requirements_hash: str
    integrity_hash: str


def build_policy_requirement_authority(
    *,
    authority_id: str,
    effective_policy_id: str,
    effective_policy_hash: str,
    requirements: Iterable[EvidenceRequirement],
) -> PolicyRequirementAuthority:
    """
    Closure authority boundary.

    Downstream sufficiency may no longer receive arbitrary raw requirements.
    Requirements must first be sealed into an explicit policy-requirement
    authority whose policy identity and complete contents are hashed.

    Native MODE_POLICY projection can later be the sole producer of this
    authority without changing the downstream contract.
    """

    items = tuple(requirements)

    if not items:
        raise ValueError("requirements cannot be empty")

    categories = [x.category for x in items]

    if len(categories) != len(set(categories)):
        raise ValueError("duplicate requirement category")

    requirements_payload = [asdict(x) for x in items]
    requirements_hash = _hash(requirements_payload)

    payload = {
        "authority_id": _nonblank(
            authority_id,
            name="authority_id",
        ),
        "effective_policy_id": _nonblank(
            effective_policy_id,
            name="effective_policy_id",
        ),
        "effective_policy_hash": _nonblank(
            effective_policy_hash,
            name="effective_policy_hash",
        ),
        "requirements_hash": requirements_hash,
        "requirements": requirements_payload,
    }

    digest = _hash(payload)

    return PolicyRequirementAuthority(
        authority_id=payload["authority_id"],
        effective_policy_id=payload["effective_policy_id"],
        effective_policy_hash=payload["effective_policy_hash"],
        requirements=items,
        requirements_hash=requirements_hash,
        integrity_hash=digest,
    )


def verify_policy_requirement_authority(
    authority: PolicyRequirementAuthority,
) -> bool:
    requirements_payload = [
        asdict(x)
        for x in authority.requirements
    ]

    requirements_hash = _hash(requirements_payload)

    payload = {
        "authority_id": authority.authority_id,
        "effective_policy_id": authority.effective_policy_id,
        "effective_policy_hash": authority.effective_policy_hash,
        "requirements_hash": requirements_hash,
        "requirements": requirements_payload,
    }

    return (
        requirements_hash == authority.requirements_hash
        and _hash(payload) == authority.integrity_hash
    )


# ==============================================================================================================
# OBFIXINT005 — COMPLETE SUFFICIENCY RECEIPT
# ==============================================================================================================

@dataclass(frozen=True)
class ClosureSufficiencyReceipt:
    receipt_id: str
    candidate_set_receipt_id: str
    candidate_set_integrity_hash: str
    independence_receipt_id: str
    independence_integrity_hash: str
    origin_hash: str
    policy_requirement_authority_id: str
    policy_requirement_integrity_hash: str
    effective_policy_id: str
    effective_policy_hash: str
    assessment: CandidateEvidenceSufficiencyAssessment
    assessment_hash: str
    integrity_hash: str


def build_closure_sufficiency_receipt(
    *,
    candidate_set: ClosureCandidateSet,
    independence_receipt: ClosureIndependenceReceipt,
    policy_requirement_authority: PolicyRequirementAuthority,
) -> ClosureSufficiencyReceipt:
    if not verify_closure_candidate_set(candidate_set):
        raise ValueError("candidate set integrity failure")

    if not verify_closure_independence_receipt(independence_receipt):
        raise ValueError("independence receipt integrity failure")

    if not verify_policy_requirement_authority(
        policy_requirement_authority
    ):
        raise ValueError("policy requirement authority integrity failure")

    if (
        independence_receipt.candidate_set_receipt_id
        != candidate_set.set_receipt_id
        or independence_receipt.candidate_set_integrity_hash
        != candidate_set.integrity_hash
    ):
        raise ValueError("independence/candidate discontinuity")

    identity = candidate_set.identity

    if (
        policy_requirement_authority.effective_policy_id
        != identity.effective_policy_id
        or policy_requirement_authority.effective_policy_hash
        != identity.effective_policy_hash
    ):
        raise ValueError("policy authority discontinuity")

    # CRITICAL:
    # sufficiency consumes the origins INSIDE the verified independence
    # receipt. There is no second origins= argument and therefore no
    # origin-substitution boundary.
    origins = independence_receipt.origins

    support = tuple(
        build_candidate_evidence_support(
            observation_id=x.observation_id,
            observation_version=x.observation_version,
            category=x.category,
            independence_family_id=x.independence_family_id,
            dependency_known=x.dependency_known,
        )
        for x in origins
    )

    assessment = assess_candidate_evidence_sufficiency(
        requirements=policy_requirement_authority.requirements,
        evidence=support,
        independence_integrity_state=(
            independence_receipt.assessment.state.value
        ),
    )

    assessment_payload = asdict(assessment)
    assessment_hash = _hash(assessment_payload)

    payload = {
        "candidate_set_receipt_id": candidate_set.set_receipt_id,
        "candidate_set_integrity_hash": candidate_set.integrity_hash,
        "independence_receipt_id": independence_receipt.receipt_id,
        "independence_integrity_hash": (
            independence_receipt.integrity_hash
        ),
        "origin_hash": independence_receipt.origin_hash,
        "policy_requirement_authority_id": (
            policy_requirement_authority.authority_id
        ),
        "policy_requirement_integrity_hash": (
            policy_requirement_authority.integrity_hash
        ),
        "effective_policy_id": identity.effective_policy_id,
        "effective_policy_hash": identity.effective_policy_hash,
        "assessment": assessment_payload,
        "assessment_hash": assessment_hash,
    }

    digest = _hash(payload)

    return ClosureSufficiencyReceipt(
        receipt_id=f"OBFIXSUFF-{digest[:24]}",
        candidate_set_receipt_id=candidate_set.set_receipt_id,
        candidate_set_integrity_hash=candidate_set.integrity_hash,
        independence_receipt_id=independence_receipt.receipt_id,
        independence_integrity_hash=(
            independence_receipt.integrity_hash
        ),
        origin_hash=independence_receipt.origin_hash,
        policy_requirement_authority_id=(
            policy_requirement_authority.authority_id
        ),
        policy_requirement_integrity_hash=(
            policy_requirement_authority.integrity_hash
        ),
        effective_policy_id=identity.effective_policy_id,
        effective_policy_hash=identity.effective_policy_hash,
        assessment=assessment,
        assessment_hash=assessment_hash,
        integrity_hash=digest,
    )


def verify_closure_sufficiency_receipt(
    receipt: ClosureSufficiencyReceipt,
) -> bool:
    assessment_payload = asdict(receipt.assessment)
    assessment_hash = _hash(assessment_payload)

    payload = {
        "candidate_set_receipt_id": receipt.candidate_set_receipt_id,
        "candidate_set_integrity_hash": (
            receipt.candidate_set_integrity_hash
        ),
        "independence_receipt_id": receipt.independence_receipt_id,
        "independence_integrity_hash": (
            receipt.independence_integrity_hash
        ),
        "origin_hash": receipt.origin_hash,
        "policy_requirement_authority_id": (
            receipt.policy_requirement_authority_id
        ),
        "policy_requirement_integrity_hash": (
            receipt.policy_requirement_integrity_hash
        ),
        "effective_policy_id": receipt.effective_policy_id,
        "effective_policy_hash": receipt.effective_policy_hash,
        "assessment": assessment_payload,
        "assessment_hash": assessment_hash,
    }

    digest = _hash(payload)

    return (
        assessment_hash == receipt.assessment_hash
        and digest == receipt.integrity_hash
        and receipt.receipt_id == f"OBFIXSUFF-{digest[:24]}"
    )


def foundation_closure_snapshot(
    *,
    candidate_set: ClosureCandidateSet,
    independence_receipt: ClosureIndependenceReceipt,
    policy_requirement_authority: PolicyRequirementAuthority,
    sufficiency_receipt: ClosureSufficiencyReceipt,
) -> dict[str, object]:
    return {
        "candidate_set_receipt_id": candidate_set.set_receipt_id,
        "evidence_count": len(candidate_set.evidence_items),
        "independence_receipt_id": independence_receipt.receipt_id,
        "origin_hash": independence_receipt.origin_hash,
        "policy_requirement_authority_id": (
            policy_requirement_authority.authority_id
        ),
        "sufficiency_receipt_id": sufficiency_receipt.receipt_id,
        "sufficiency_state": sufficiency_receipt.assessment.state.value,
        "authority_boundary": {
            "foundation_integration_closure_only": True,
            "trade_recommendation": False,
            "trade_ranking": False,
            "automatic_contract_selection": False,
            "broker_submission": False,
            "capital_movement": False,
            "manual_live_unlock": False,
            "hybrid_execution": False,
            "automated_execution": False,
        },
    }
