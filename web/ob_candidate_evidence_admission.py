from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class AdmissionState(str, Enum):
    ADMITTED = "ADMITTED"
    BLOCKED = "BLOCKED"
    UNKNOWN = "UNKNOWN"


class AdmissionReason(str, Enum):
    CLEAN_ADMISSION = "CLEAN_ADMISSION"
    UPSTREAM_NOT_ELIGIBLE = "UPSTREAM_NOT_ELIGIBLE"
    TARGET_ID_MISMATCH = "TARGET_ID_MISMATCH"
    SYMBOL_MISMATCH = "SYMBOL_MISMATCH"
    INSTRUMENT_KIND_MISMATCH = "INSTRUMENT_KIND_MISMATCH"
    EXACT_DUPLICATE = "EXACT_DUPLICATE"
    OBSERVATION_VERSION_CONFLICT = "OBSERVATION_VERSION_CONFLICT"
    LINEAGE_DUPLICATE = "LINEAGE_DUPLICATE"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class CandidateIdentity:
    candidate_id: str
    reasoning_target_id: str
    target_symbol: str
    target_instrument_kind: str
    purpose: str


@dataclass(frozen=True)
class CandidateEvidenceItem:
    observation_id: str
    observation_version: int
    lineage_hash: str
    reasoning_target_id: str
    target_symbol: str
    target_instrument_kind: str
    upstream_composition_state: str


@dataclass(frozen=True)
class EvidenceAdmissionAssessment:
    candidate_id: str
    observation_id: str
    observation_version: int
    state: AdmissionState
    reason: AdmissionReason
    details: tuple[str, ...]


@dataclass(frozen=True)
class CandidateEvidenceSet:
    candidate: CandidateIdentity
    items: tuple[CandidateEvidenceItem, ...]


def _nonblank(value: object, *, name: str) -> str:
    text = str(value).strip()

    if not text:
        raise ValueError(
            f"{name} cannot be blank"
        )

    return text


def build_candidate_identity(
    *,
    candidate_id: str,
    reasoning_target_id: str,
    target_symbol: str,
    target_instrument_kind: str,
    purpose: str,
) -> CandidateIdentity:
    return CandidateIdentity(
        candidate_id=_nonblank(
            candidate_id,
            name="candidate_id",
        ),
        reasoning_target_id=_nonblank(
            reasoning_target_id,
            name="reasoning_target_id",
        ),
        target_symbol=_nonblank(
            target_symbol,
            name="target_symbol",
        ).upper(),
        target_instrument_kind=_nonblank(
            target_instrument_kind,
            name="target_instrument_kind",
        ).upper(),
        purpose=_nonblank(
            purpose,
            name="purpose",
        ),
    )


def build_candidate_evidence_item(
    *,
    observation_id: str,
    observation_version: int,
    lineage_hash: str,
    reasoning_target_id: str,
    target_symbol: str,
    target_instrument_kind: str,
    upstream_composition_state: str,
) -> CandidateEvidenceItem:
    if observation_version < 1:
        raise ValueError(
            "observation_version must be >= 1"
        )

    return CandidateEvidenceItem(
        observation_id=_nonblank(
            observation_id,
            name="observation_id",
        ),
        observation_version=observation_version,
        lineage_hash=_nonblank(
            lineage_hash,
            name="lineage_hash",
        ),
        reasoning_target_id=_nonblank(
            reasoning_target_id,
            name="reasoning_target_id",
        ),
        target_symbol=_nonblank(
            target_symbol,
            name="target_symbol",
        ).upper(),
        target_instrument_kind=_nonblank(
            target_instrument_kind,
            name="target_instrument_kind",
        ).upper(),
        upstream_composition_state=_nonblank(
            upstream_composition_state,
            name="upstream_composition_state",
        ).upper(),
    )


def empty_candidate_evidence_set(
    candidate: CandidateIdentity,
) -> CandidateEvidenceSet:
    return CandidateEvidenceSet(
        candidate=candidate,
        items=(),
    )


def assess_candidate_evidence_admission(
    *,
    evidence_set: CandidateEvidenceSet,
    item: CandidateEvidenceItem,
) -> EvidenceAdmissionAssessment:
    candidate = evidence_set.candidate

    if item.upstream_composition_state != "ELIGIBLE":
        return EvidenceAdmissionAssessment(
            candidate_id=candidate.candidate_id,
            observation_id=item.observation_id,
            observation_version=item.observation_version,
            state=AdmissionState.BLOCKED,
            reason=AdmissionReason.UPSTREAM_NOT_ELIGIBLE,
            details=(
                "Upstream reasoning-context composition did not explicitly yield ELIGIBLE.",
            ),
        )

    if item.reasoning_target_id != candidate.reasoning_target_id:
        return EvidenceAdmissionAssessment(
            candidate_id=candidate.candidate_id,
            observation_id=item.observation_id,
            observation_version=item.observation_version,
            state=AdmissionState.BLOCKED,
            reason=AdmissionReason.TARGET_ID_MISMATCH,
            details=(
                "Evidence belongs to a different reasoning target.",
            ),
        )

    if item.target_symbol != candidate.target_symbol:
        return EvidenceAdmissionAssessment(
            candidate_id=candidate.candidate_id,
            observation_id=item.observation_id,
            observation_version=item.observation_version,
            state=AdmissionState.BLOCKED,
            reason=AdmissionReason.SYMBOL_MISMATCH,
            details=(
                "Evidence symbol does not match candidate symbol.",
            ),
        )

    if item.target_instrument_kind != candidate.target_instrument_kind:
        return EvidenceAdmissionAssessment(
            candidate_id=candidate.candidate_id,
            observation_id=item.observation_id,
            observation_version=item.observation_version,
            state=AdmissionState.BLOCKED,
            reason=AdmissionReason.INSTRUMENT_KIND_MISMATCH,
            details=(
                "Evidence instrument kind does not match candidate instrument kind.",
            ),
        )

    for existing in evidence_set.items:
        if (
            existing.observation_id == item.observation_id
            and existing.observation_version == item.observation_version
            and existing.lineage_hash == item.lineage_hash
        ):
            return EvidenceAdmissionAssessment(
                candidate_id=candidate.candidate_id,
                observation_id=item.observation_id,
                observation_version=item.observation_version,
                state=AdmissionState.BLOCKED,
                reason=AdmissionReason.EXACT_DUPLICATE,
                details=(
                    "Exact evidence item is already admitted.",
                ),
            )

        if (
            existing.observation_id == item.observation_id
            and existing.observation_version != item.observation_version
        ):
            return EvidenceAdmissionAssessment(
                candidate_id=candidate.candidate_id,
                observation_id=item.observation_id,
                observation_version=item.observation_version,
                state=AdmissionState.BLOCKED,
                reason=AdmissionReason.OBSERVATION_VERSION_CONFLICT,
                details=(
                    "Another version of the same observation is already active in this candidate evidence set.",
                ),
            )

        if existing.lineage_hash == item.lineage_hash:
            return EvidenceAdmissionAssessment(
                candidate_id=candidate.candidate_id,
                observation_id=item.observation_id,
                observation_version=item.observation_version,
                state=AdmissionState.BLOCKED,
                reason=AdmissionReason.LINEAGE_DUPLICATE,
                details=(
                    "Evidence lineage already exists in this candidate set and cannot masquerade as independent evidence.",
                ),
            )

    return EvidenceAdmissionAssessment(
        candidate_id=candidate.candidate_id,
        observation_id=item.observation_id,
        observation_version=item.observation_version,
        state=AdmissionState.ADMITTED,
        reason=AdmissionReason.CLEAN_ADMISSION,
        details=(
            "Evidence passed upstream eligibility and candidate-set integrity checks.",
        ),
    )


def admit_candidate_evidence(
    *,
    evidence_set: CandidateEvidenceSet,
    item: CandidateEvidenceItem,
) -> CandidateEvidenceSet:
    assessment = assess_candidate_evidence_admission(
        evidence_set=evidence_set,
        item=item,
    )

    if assessment.state is not AdmissionState.ADMITTED:
        raise ValueError(
            f"evidence admission blocked: {assessment.reason.value}"
        )

    return CandidateEvidenceSet(
        candidate=evidence_set.candidate,
        items=(
            *evidence_set.items,
            item,
        ),
    )


def candidate_evidence_set_integrity(
    evidence_set: CandidateEvidenceSet,
) -> bool:
    candidate = evidence_set.candidate

    observation_ids = {}
    lineages = set()
    exact_keys = set()

    for item in evidence_set.items:
        if item.upstream_composition_state != "ELIGIBLE":
            return False

        if item.reasoning_target_id != candidate.reasoning_target_id:
            return False

        if item.target_symbol != candidate.target_symbol:
            return False

        if item.target_instrument_kind != candidate.target_instrument_kind:
            return False

        exact_key = (
            item.observation_id,
            item.observation_version,
            item.lineage_hash,
        )

        if exact_key in exact_keys:
            return False

        exact_keys.add(
            exact_key
        )

        previous_version = observation_ids.get(
            item.observation_id
        )

        if (
            previous_version is not None
            and previous_version != item.observation_version
        ):
            return False

        observation_ids[
            item.observation_id
        ] = item.observation_version

        if item.lineage_hash in lineages:
            return False

        lineages.add(
            item.lineage_hash
        )

    return True


def candidate_evidence_snapshot(
    evidence_set: CandidateEvidenceSet,
) -> dict[str, object]:
    return {
        "candidate": {
            "candidate_id": evidence_set.candidate.candidate_id,
            "reasoning_target_id": evidence_set.candidate.reasoning_target_id,
            "target_symbol": evidence_set.candidate.target_symbol,
            "target_instrument_kind": evidence_set.candidate.target_instrument_kind,
            "purpose": evidence_set.candidate.purpose,
        },
        "integrity": candidate_evidence_set_integrity(
            evidence_set
        ),
        "items": [
            {
                "observation_id": item.observation_id,
                "observation_version": item.observation_version,
                "lineage_hash": item.lineage_hash,
                "reasoning_target_id": item.reasoning_target_id,
                "target_symbol": item.target_symbol,
                "target_instrument_kind": item.target_instrument_kind,
                "upstream_composition_state": item.upstream_composition_state,
            }
            for item in evidence_set.items
        ],
    }
