from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Any


class InstrumentKind(str, Enum):
    EQUITY = "EQUITY"
    ETF = "ETF"
    OPTION = "OPTION"
    INDEX = "INDEX"
    FUTURE = "FUTURE"
    FOREX = "FOREX"
    CRYPTO = "CRYPTO"
    UNKNOWN = "UNKNOWN"


class OptionRight(str, Enum):
    CALL = "CALL"
    PUT = "PUT"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    UNKNOWN = "UNKNOWN"


class ScopeBindingState(str, Enum):
    MATCH = "MATCH"
    SYMBOL_MISMATCH = "SYMBOL_MISMATCH"
    UNDERLYING_MISMATCH = "UNDERLYING_MISMATCH"
    INSTRUMENT_KIND_MISMATCH = "INSTRUMENT_KIND_MISMATCH"
    OPTION_RIGHT_MISMATCH = "OPTION_RIGHT_MISMATCH"
    STRIKE_MISMATCH = "STRIKE_MISMATCH"
    EXPIRATION_MISMATCH = "EXPIRATION_MISMATCH"
    CONTRACT_MISMATCH = "CONTRACT_MISMATCH"
    UNKNOWN = "UNKNOWN"


class ScopeReasoningEligibility(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    INELIGIBLE = "INELIGIBLE"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class InstrumentIdentity:
    symbol: str
    instrument_kind: InstrumentKind
    underlying_symbol: str
    option_right: OptionRight
    strike: float | None
    expiration: date | None
    contract_id: str | None


@dataclass(frozen=True)
class InstrumentBindingAssessment:
    state: ScopeBindingState
    reasoning_eligibility: ScopeReasoningEligibility
    observation: InstrumentIdentity
    target: InstrumentIdentity
    reasons: tuple[str, ...]


def _norm_symbol(value: Any) -> str:
    if value is None:
        return ""

    return str(value).strip().upper()


def _kind(value: Any) -> InstrumentKind:
    if isinstance(value, InstrumentKind):
        return value

    if value is None:
        return InstrumentKind.UNKNOWN

    raw = getattr(
        value,
        "value",
        value,
    )

    text = str(raw).strip().upper()

    try:
        return InstrumentKind(text)
    except ValueError:
        return InstrumentKind.UNKNOWN


def _right(value: Any) -> OptionRight:
    if isinstance(value, OptionRight):
        return value

    if value is None:
        return OptionRight.UNKNOWN

    raw = getattr(
        value,
        "value",
        value,
    )

    text = str(raw).strip().upper()

    try:
        return OptionRight(text)
    except ValueError:
        return OptionRight.UNKNOWN


def build_instrument_identity(
    *,
    symbol: str,
    instrument_kind: Any,
    underlying_symbol: str | None = None,
    option_right: Any = OptionRight.NOT_APPLICABLE,
    strike: float | None = None,
    expiration: date | None = None,
    contract_id: str | None = None,
) -> InstrumentIdentity:
    normalized_symbol = _norm_symbol(
        symbol
    )

    if not normalized_symbol:
        raise ValueError(
            "symbol cannot be blank"
        )

    resolved_kind = _kind(
        instrument_kind
    )

    if resolved_kind is InstrumentKind.UNKNOWN:
        raise ValueError(
            "instrument_kind must be known"
        )

    normalized_underlying = _norm_symbol(
        underlying_symbol
    )

    normalized_contract_id = (
        str(contract_id).strip()
        if contract_id is not None
        else None
    )

    if normalized_contract_id == "":
        normalized_contract_id = None

    if resolved_kind is InstrumentKind.OPTION:
        if not normalized_underlying:
            raise ValueError(
                "option identity requires underlying_symbol"
            )

        resolved_right = _right(
            option_right
        )

        if resolved_right not in {
            OptionRight.CALL,
            OptionRight.PUT,
        }:
            raise ValueError(
                "option identity requires CALL or PUT"
            )

        if strike is None:
            raise ValueError(
                "option identity requires strike"
            )

        if float(strike) <= 0:
            raise ValueError(
                "option strike must be > 0"
            )

        if expiration is None:
            raise ValueError(
                "option identity requires expiration"
            )

        if not normalized_contract_id:
            raise ValueError(
                "option identity requires contract_id"
            )

        return InstrumentIdentity(
            symbol=normalized_symbol,
            instrument_kind=resolved_kind,
            underlying_symbol=normalized_underlying,
            option_right=resolved_right,
            strike=float(strike),
            expiration=expiration,
            contract_id=normalized_contract_id,
        )

    if (
        strike is not None
        or expiration is not None
        or normalized_contract_id is not None
    ):
        raise ValueError(
            "non-option identity cannot carry option contract fields"
        )

    resolved_right = _right(
        option_right
    )

    if resolved_right not in {
        OptionRight.NOT_APPLICABLE,
        OptionRight.UNKNOWN,
    }:
        raise ValueError(
            "non-option identity cannot carry CALL or PUT right"
        )

    return InstrumentIdentity(
        symbol=normalized_symbol,
        instrument_kind=resolved_kind,
        underlying_symbol=normalized_underlying or normalized_symbol,
        option_right=OptionRight.NOT_APPLICABLE,
        strike=None,
        expiration=None,
        contract_id=None,
    )


def assess_instrument_binding(
    *,
    observation: InstrumentIdentity,
    target: InstrumentIdentity,
) -> InstrumentBindingAssessment:
    if observation.instrument_kind is not target.instrument_kind:
        return InstrumentBindingAssessment(
            state=ScopeBindingState.INSTRUMENT_KIND_MISMATCH,
            reasoning_eligibility=ScopeReasoningEligibility.INELIGIBLE,
            observation=observation,
            target=target,
            reasons=(
                "Observation and target have different instrument kinds.",
            ),
        )

    if observation.symbol != target.symbol:
        return InstrumentBindingAssessment(
            state=ScopeBindingState.SYMBOL_MISMATCH,
            reasoning_eligibility=ScopeReasoningEligibility.INELIGIBLE,
            observation=observation,
            target=target,
            reasons=(
                "Observation symbol does not match target symbol.",
            ),
        )

    if observation.underlying_symbol != target.underlying_symbol:
        return InstrumentBindingAssessment(
            state=ScopeBindingState.UNDERLYING_MISMATCH,
            reasoning_eligibility=ScopeReasoningEligibility.INELIGIBLE,
            observation=observation,
            target=target,
            reasons=(
                "Observation underlying does not match target underlying.",
            ),
        )

    if observation.instrument_kind is InstrumentKind.OPTION:
        if observation.option_right is not target.option_right:
            return InstrumentBindingAssessment(
                state=ScopeBindingState.OPTION_RIGHT_MISMATCH,
                reasoning_eligibility=ScopeReasoningEligibility.INELIGIBLE,
                observation=observation,
                target=target,
                reasons=(
                    "Observation option right does not match target contract.",
                ),
            )

        if observation.strike != target.strike:
            return InstrumentBindingAssessment(
                state=ScopeBindingState.STRIKE_MISMATCH,
                reasoning_eligibility=ScopeReasoningEligibility.INELIGIBLE,
                observation=observation,
                target=target,
                reasons=(
                    "Observation strike does not match target contract.",
                ),
            )

        if observation.expiration != target.expiration:
            return InstrumentBindingAssessment(
                state=ScopeBindingState.EXPIRATION_MISMATCH,
                reasoning_eligibility=ScopeReasoningEligibility.INELIGIBLE,
                observation=observation,
                target=target,
                reasons=(
                    "Observation expiration does not match target contract.",
                ),
            )

        if observation.contract_id != target.contract_id:
            return InstrumentBindingAssessment(
                state=ScopeBindingState.CONTRACT_MISMATCH,
                reasoning_eligibility=ScopeReasoningEligibility.INELIGIBLE,
                observation=observation,
                target=target,
                reasons=(
                    "Observation contract identity does not match target contract.",
                ),
            )

    return InstrumentBindingAssessment(
        state=ScopeBindingState.MATCH,
        reasoning_eligibility=ScopeReasoningEligibility.ELIGIBLE,
        observation=observation,
        target=target,
        reasons=(
            "Observation identity exactly matches current reasoning target.",
        ),
    )


def eligible_for_current_instrument_reasoning(
    assessment: InstrumentBindingAssessment,
) -> bool:
    return (
        assessment.state
        is ScopeBindingState.MATCH
        and assessment.reasoning_eligibility
        is ScopeReasoningEligibility.ELIGIBLE
    )


def blocked_by_instrument_scope(
    assessment: InstrumentBindingAssessment,
) -> bool:
    return assessment.state is not ScopeBindingState.MATCH


def instrument_identity_snapshot(
    identity: InstrumentIdentity,
) -> dict[str, object]:
    return {
        "symbol": identity.symbol,
        "instrument_kind": identity.instrument_kind.value,
        "underlying_symbol": identity.underlying_symbol,
        "option_right": identity.option_right.value,
        "strike": identity.strike,
        "expiration": (
            identity.expiration.isoformat()
            if identity.expiration is not None
            else None
        ),
        "contract_id": identity.contract_id,
    }


def binding_snapshot(
    assessment: InstrumentBindingAssessment,
) -> dict[str, object]:
    return {
        "state": assessment.state.value,
        "reasoning_eligibility": assessment.reasoning_eligibility.value,
        "observation": instrument_identity_snapshot(
            assessment.observation
        ),
        "target": instrument_identity_snapshot(
            assessment.target
        ),
        "reasons": list(
            assessment.reasons
        ),
    }
