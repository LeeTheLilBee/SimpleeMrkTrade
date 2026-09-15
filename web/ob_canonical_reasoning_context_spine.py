from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from typing import Mapping

from web.ob_reasoning_context_composition import (
    CompositionState,
    GateAssessment,
    GateVerdict,
    REQUIRED_GATES,
    ReasoningContextAssessment,
    ReasoningTarget,
    compose_reasoning_context,
)


class SpineState(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"
    UNKNOWN = "UNKNOWN"


class SpineReason(str, Enum):
    CONTEXT_INTEGRITY_SATISFIED = "CONTEXT_INTEGRITY_SATISFIED"
    MISSING_AUTHORITY = "MISSING_AUTHORITY"
    AUTHORITY_GATE_MISMATCH = "AUTHORITY_GATE_MISMATCH"
    IDENTITY_MISMATCH = "IDENTITY_MISMATCH"
    POLICY_MISMATCH = "POLICY_MISMATCH"
    UNKNOWN_AUTHORITY_STATE = "UNKNOWN_AUTHORITY_STATE"
    UPSTREAM_BLOCKED = "UPSTREAM_BLOCKED"
    UPSTREAM_REVIEW_REQUIRED = "UPSTREAM_REVIEW_REQUIRED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class CanonicalInstrumentIdentity:
    symbol: str
    instrument_kind: str
    contract_id: str | None = None
    underlying_symbol: str | None = None
    option_right: str | None = None
    strike: str | None = None
    expiration: str | None = None


@dataclass(frozen=True)
class CanonicalContextIdentity:
    context_id: str
    observation_id: str
    observation_version: int
    lineage_hash: str
    provenance_identity: str
    reasoning_target_id: str
    instrument: CanonicalInstrumentIdentity
    operating_mode: str
    effective_policy_id: str
    effective_policy_hash: str
    purpose: str


@dataclass(frozen=True)
class CanonicalAuthorityResult:
    gate: str
    observation_id: str
    observation_version: int
    reasoning_target_id: str
    symbol: str
    instrument_kind: str
    verdict: GateVerdict
    reason: str
    authority_identity: str
    authority_hash: str


@dataclass(frozen=True)
class CanonicalReasoningContextReceipt:
    receipt_id: str
    context: CanonicalContextIdentity
    state: SpineState
    composition: ReasoningContextAssessment
    authority_results: tuple[CanonicalAuthorityResult, ...]
    blocking_gates: tuple[str, ...]
    review_gates: tuple[str, ...]
    unknown_gates: tuple[str, ...]
    reason: SpineReason
    integrity_hash: str


def _nonblank(value: str, *, name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise ValueError(f"{name} cannot be blank")
    return normalized


def _upper(value: str, *, name: str) -> str:
    return _nonblank(value, name=name).upper()


def build_canonical_instrument_identity(
    *,
    symbol: str,
    instrument_kind: str,
    contract_id: str | None = None,
    underlying_symbol: str | None = None,
    option_right: str | None = None,
    strike: str | None = None,
    expiration: str | None = None,
) -> CanonicalInstrumentIdentity:
    symbol = _upper(symbol, name="symbol")
    kind = _upper(instrument_kind, name="instrument_kind")

    if kind == "OPTION":
        required = {
            "contract_id": contract_id,
            "underlying_symbol": underlying_symbol,
            "option_right": option_right,
            "strike": strike,
            "expiration": expiration,
        }
        missing = [
            name for name, value in required.items()
            if value is None or not str(value).strip()
        ]
        if missing:
            raise ValueError(
                "OPTION identity requires exact contract fields: "
                + ", ".join(sorted(missing))
            )

    return CanonicalInstrumentIdentity(
        symbol=symbol,
        instrument_kind=kind,
        contract_id=None if contract_id is None else str(contract_id).strip(),
        underlying_symbol=(
            None if underlying_symbol is None
            else str(underlying_symbol).strip().upper()
        ),
        option_right=(
            None if option_right is None
            else str(option_right).strip().upper()
        ),
        strike=None if strike is None else str(strike).strip(),
        expiration=None if expiration is None else str(expiration).strip(),
    )


def build_canonical_context_identity(
    *,
    context_id: str,
    observation_id: str,
    observation_version: int,
    lineage_hash: str,
    provenance_identity: str,
    reasoning_target_id: str,
    instrument: CanonicalInstrumentIdentity,
    operating_mode: str,
    effective_policy_id: str,
    effective_policy_hash: str,
    purpose: str,
) -> CanonicalContextIdentity:
    if observation_version < 1:
        raise ValueError("observation_version must be >= 1")

    return CanonicalContextIdentity(
        context_id=_nonblank(context_id, name="context_id"),
        observation_id=_nonblank(observation_id, name="observation_id"),
        observation_version=observation_version,
        lineage_hash=_nonblank(lineage_hash, name="lineage_hash"),
        provenance_identity=_nonblank(
            provenance_identity,
            name="provenance_identity",
        ),
        reasoning_target_id=_nonblank(
            reasoning_target_id,
            name="reasoning_target_id",
        ),
        instrument=instrument,
        operating_mode=_upper(operating_mode, name="operating_mode"),
        effective_policy_id=_nonblank(
            effective_policy_id,
            name="effective_policy_id",
        ),
        effective_policy_hash=_nonblank(
            effective_policy_hash,
            name="effective_policy_hash",
        ),
        purpose=_nonblank(purpose, name="purpose"),
    )


def authority_result(
    *,
    gate: str,
    observation_id: str,
    observation_version: int,
    reasoning_target_id: str,
    symbol: str,
    instrument_kind: str,
    verdict: GateVerdict,
    reason: str,
    authority_identity: str,
    authority_hash: str,
) -> CanonicalAuthorityResult:
    if gate not in REQUIRED_GATES:
        raise ValueError(f"unknown authority gate: {gate}")

    if observation_version < 1:
        raise ValueError("observation_version must be >= 1")

    if not isinstance(verdict, GateVerdict):
        raise ValueError("verdict must be GateVerdict")

    return CanonicalAuthorityResult(
        gate=gate,
        observation_id=_nonblank(observation_id, name="observation_id"),
        observation_version=observation_version,
        reasoning_target_id=_nonblank(
            reasoning_target_id,
            name="reasoning_target_id",
        ),
        symbol=_upper(symbol, name="symbol"),
        instrument_kind=_upper(
            instrument_kind,
            name="instrument_kind",
        ),
        verdict=verdict,
        reason=_nonblank(reason, name="reason"),
        authority_identity=_nonblank(
            authority_identity,
            name="authority_identity",
        ),
        authority_hash=_nonblank(
            authority_hash,
            name="authority_hash",
        ),
    )


def _canonical_payload(
    *,
    context: CanonicalContextIdentity,
    state: SpineState,
    authority_results: tuple[CanonicalAuthorityResult, ...],
    reason: SpineReason,
) -> dict[str, object]:
    return {
        "context": {
            "context_id": context.context_id,
            "observation_id": context.observation_id,
            "observation_version": context.observation_version,
            "lineage_hash": context.lineage_hash,
            "provenance_identity": context.provenance_identity,
            "reasoning_target_id": context.reasoning_target_id,
            "instrument": {
                "symbol": context.instrument.symbol,
                "instrument_kind": context.instrument.instrument_kind,
                "contract_id": context.instrument.contract_id,
                "underlying_symbol": context.instrument.underlying_symbol,
                "option_right": context.instrument.option_right,
                "strike": context.instrument.strike,
                "expiration": context.instrument.expiration,
            },
            "operating_mode": context.operating_mode,
            "effective_policy_id": context.effective_policy_id,
            "effective_policy_hash": context.effective_policy_hash,
            "purpose": context.purpose,
        },
        "state": state.value,
        "reason": reason.value,
        "authorities": [
            {
                "gate": item.gate,
                "observation_id": item.observation_id,
                "observation_version": item.observation_version,
                "reasoning_target_id": item.reasoning_target_id,
                "symbol": item.symbol,
                "instrument_kind": item.instrument_kind,
                "verdict": item.verdict.value,
                "reason": item.reason,
                "authority_identity": item.authority_identity,
                "authority_hash": item.authority_hash,
            }
            for item in authority_results
        ],
    }


def _integrity_hash(payload: Mapping[str, object]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _unknown_receipt(
    *,
    context: CanonicalContextIdentity,
    results: tuple[CanonicalAuthorityResult, ...],
    reason: SpineReason,
) -> CanonicalReasoningContextReceipt:
    target = ReasoningTarget(
        target_id=context.reasoning_target_id,
        observation_id=context.observation_id,
        observation_version=context.observation_version,
        target_symbol=context.instrument.symbol,
        target_instrument_kind=context.instrument.instrument_kind,
        purpose=context.purpose,
    )

    composition = compose_reasoning_context(
        target=target,
        gates={
            item.gate: GateAssessment(
                gate=item.gate,
                verdict=item.verdict,
                reason=item.reason,
            )
            for item in results
        },
    )

    payload = _canonical_payload(
        context=context,
        state=SpineState.UNKNOWN,
        authority_results=results,
        reason=reason,
    )
    digest = _integrity_hash(payload)

    return CanonicalReasoningContextReceipt(
        receipt_id=f"OBCTX-{digest[:24]}",
        context=context,
        state=SpineState.UNKNOWN,
        composition=composition,
        authority_results=results,
        blocking_gates=composition.blocking_gates,
        review_gates=composition.review_gates,
        unknown_gates=composition.unknown_gates,
        reason=reason,
        integrity_hash=digest,
    )


def build_canonical_reasoning_context_receipt(
    *,
    context: CanonicalContextIdentity,
    authorities: Mapping[str, CanonicalAuthorityResult],
) -> CanonicalReasoningContextReceipt:
    supplied = set(authorities)
    required = set(REQUIRED_GATES)

    if supplied - required:
        raise ValueError(
            "unexpected authority gates: "
            + ", ".join(sorted(supplied - required))
        )

    ordered = tuple(
        authorities[name]
        for name in REQUIRED_GATES
        if name in authorities
    )

    if required - supplied:
        return _unknown_receipt(
            context=context,
            results=ordered,
            reason=SpineReason.MISSING_AUTHORITY,
        )

    for name, result in zip(REQUIRED_GATES, ordered):
        if result.gate != name:
            return _unknown_receipt(
                context=context,
                results=ordered,
                reason=SpineReason.AUTHORITY_GATE_MISMATCH,
            )

        identity_matches = (
            result.observation_id == context.observation_id
            and result.observation_version == context.observation_version
            and result.reasoning_target_id == context.reasoning_target_id
            and result.symbol == context.instrument.symbol
            and result.instrument_kind == context.instrument.instrument_kind
        )

        if not identity_matches:
            return _unknown_receipt(
                context=context,
                results=ordered,
                reason=SpineReason.IDENTITY_MISMATCH,
            )

    target = ReasoningTarget(
        target_id=context.reasoning_target_id,
        observation_id=context.observation_id,
        observation_version=context.observation_version,
        target_symbol=context.instrument.symbol,
        target_instrument_kind=context.instrument.instrument_kind,
        purpose=context.purpose,
    )

    gates = {
        item.gate: GateAssessment(
            gate=item.gate,
            verdict=item.verdict,
            reason=item.reason,
        )
        for item in ordered
    }

    composition = compose_reasoning_context(
        target=target,
        gates=gates,
    )

    state_map = {
        CompositionState.ELIGIBLE: SpineState.ELIGIBLE,
        CompositionState.REVIEW_REQUIRED: SpineState.REVIEW_REQUIRED,
        CompositionState.BLOCKED: SpineState.BLOCKED,
        CompositionState.UNKNOWN: SpineState.UNKNOWN,
    }

    state = state_map[composition.state]

    if state is SpineState.ELIGIBLE:
        reason = SpineReason.CONTEXT_INTEGRITY_SATISFIED
    elif state is SpineState.BLOCKED:
        reason = SpineReason.UPSTREAM_BLOCKED
    elif state is SpineState.REVIEW_REQUIRED:
        reason = SpineReason.UPSTREAM_REVIEW_REQUIRED
    else:
        reason = SpineReason.UNKNOWN_AUTHORITY_STATE

    payload = _canonical_payload(
        context=context,
        state=state,
        authority_results=ordered,
        reason=reason,
    )
    digest = _integrity_hash(payload)

    return CanonicalReasoningContextReceipt(
        receipt_id=f"OBCTX-{digest[:24]}",
        context=context,
        state=state,
        composition=composition,
        authority_results=ordered,
        blocking_gates=composition.blocking_gates,
        review_gates=composition.review_gates,
        unknown_gates=composition.unknown_gates,
        reason=reason,
        integrity_hash=digest,
    )


def verify_canonical_reasoning_context_receipt(
    receipt: CanonicalReasoningContextReceipt,
) -> bool:
    payload = _canonical_payload(
        context=receipt.context,
        state=receipt.state,
        authority_results=receipt.authority_results,
        reason=receipt.reason,
    )

    digest = _integrity_hash(payload)

    if digest != receipt.integrity_hash:
        return False

    if receipt.receipt_id != f"OBCTX-{digest[:24]}":
        return False

    if receipt.state is SpineState.ELIGIBLE:
        if receipt.composition.state is not CompositionState.ELIGIBLE:
            return False

        if len(receipt.authority_results) != len(REQUIRED_GATES):
            return False

        if not all(
            item.verdict is GateVerdict.ALLOW
            for item in receipt.authority_results
        ):
            return False

    return True


def canonical_context_eligible(
    receipt: CanonicalReasoningContextReceipt,
) -> bool:
    return (
        receipt.state is SpineState.ELIGIBLE
        and verify_canonical_reasoning_context_receipt(receipt)
    )


def canonical_context_snapshot(
    receipt: CanonicalReasoningContextReceipt,
) -> dict[str, object]:
    return {
        "receipt_id": receipt.receipt_id,
        "state": receipt.state.value,
        "reason": receipt.reason.value,
        "context_id": receipt.context.context_id,
        "observation_id": receipt.context.observation_id,
        "observation_version": receipt.context.observation_version,
        "lineage_hash": receipt.context.lineage_hash,
        "provenance_identity": receipt.context.provenance_identity,
        "reasoning_target_id": receipt.context.reasoning_target_id,
        "symbol": receipt.context.instrument.symbol,
        "instrument_kind": receipt.context.instrument.instrument_kind,
        "contract_id": receipt.context.instrument.contract_id,
        "operating_mode": receipt.context.operating_mode,
        "effective_policy_id": receipt.context.effective_policy_id,
        "effective_policy_hash": receipt.context.effective_policy_hash,
        "blocking_gates": list(receipt.blocking_gates),
        "review_gates": list(receipt.review_gates),
        "unknown_gates": list(receipt.unknown_gates),
        "integrity_hash": receipt.integrity_hash,
        "authority_boundary": {
            "analytical_context_integrity_only": True,
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
