from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from enum import Enum
from typing import Any


class TemporalValidityState(str, Enum):
    VALID_NOW = "VALID_NOW"
    NOT_YET_VALID = "NOT_YET_VALID"
    OUT_OF_WINDOW = "OUT_OF_WINDOW"
    SESSION_MISMATCH = "SESSION_MISMATCH"
    TRADING_DATE_MISMATCH = "TRADING_DATE_MISMATCH"
    UNKNOWN = "UNKNOWN"


class TemporalReasoningEligibility(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    INELIGIBLE = "INELIGIBLE"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    UNKNOWN = "UNKNOWN"


class MarketSession(str, Enum):
    PREMARKET = "PREMARKET"
    REGULAR = "REGULAR"
    AFTER_HOURS = "AFTER_HOURS"
    CLOSED = "CLOSED"
    ANY = "ANY"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class TemporalValidityWindow:
    valid_from: datetime
    valid_until: datetime
    trading_date: date
    session: MarketSession


@dataclass(frozen=True)
class TemporalValidityAssessment:
    state: TemporalValidityState
    reasoning_eligibility: TemporalReasoningEligibility
    evaluated_at: datetime
    observation_trading_date: date
    current_trading_date: date
    observation_session: MarketSession
    current_session: MarketSession
    valid_from: datetime
    valid_until: datetime
    reasons: tuple[str, ...]


def _require_aware(value: datetime, *, name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(
            f"{name} must be timezone-aware"
        )


def _session(value: Any) -> MarketSession:
    if isinstance(value, MarketSession):
        return value

    if value is None:
        return MarketSession.UNKNOWN

    raw = getattr(
        value,
        "value",
        value,
    )

    text = str(raw).strip().upper()

    try:
        return MarketSession(text)
    except ValueError:
        return MarketSession.UNKNOWN


def build_temporal_validity_window(
    *,
    valid_from: datetime,
    valid_until: datetime,
    trading_date: date,
    session: Any,
) -> TemporalValidityWindow:
    _require_aware(
        valid_from,
        name="valid_from",
    )

    _require_aware(
        valid_until,
        name="valid_until",
    )

    if valid_until <= valid_from:
        raise ValueError(
            "valid_until must be later than valid_from"
        )

    resolved_session = _session(
        session
    )

    if resolved_session is MarketSession.UNKNOWN:
        raise ValueError(
            "temporal validity window requires known session"
        )

    return TemporalValidityWindow(
        valid_from=valid_from.astimezone(
            timezone.utc
        ),
        valid_until=valid_until.astimezone(
            timezone.utc
        ),
        trading_date=trading_date,
        session=resolved_session,
    )


def assess_temporal_validity(
    *,
    window: TemporalValidityWindow,
    evaluated_at: datetime,
    current_trading_date: date,
    current_session: Any,
) -> TemporalValidityAssessment:
    _require_aware(
        evaluated_at,
        name="evaluated_at",
    )

    evaluated_utc = evaluated_at.astimezone(
        timezone.utc
    )

    resolved_session = _session(
        current_session
    )

    if resolved_session is MarketSession.UNKNOWN:
        return TemporalValidityAssessment(
            state=TemporalValidityState.UNKNOWN,
            reasoning_eligibility=TemporalReasoningEligibility.UNKNOWN,
            evaluated_at=evaluated_utc,
            observation_trading_date=window.trading_date,
            current_trading_date=current_trading_date,
            observation_session=window.session,
            current_session=resolved_session,
            valid_from=window.valid_from,
            valid_until=window.valid_until,
            reasons=(
                "Current market session is unknown.",
            ),
        )

    if current_trading_date != window.trading_date:
        return TemporalValidityAssessment(
            state=TemporalValidityState.TRADING_DATE_MISMATCH,
            reasoning_eligibility=TemporalReasoningEligibility.INELIGIBLE,
            evaluated_at=evaluated_utc,
            observation_trading_date=window.trading_date,
            current_trading_date=current_trading_date,
            observation_session=window.session,
            current_session=resolved_session,
            valid_from=window.valid_from,
            valid_until=window.valid_until,
            reasons=(
                "Observation belongs to a different trading date.",
            ),
        )

    if (
        window.session is not MarketSession.ANY
        and resolved_session is not window.session
    ):
        return TemporalValidityAssessment(
            state=TemporalValidityState.SESSION_MISMATCH,
            reasoning_eligibility=TemporalReasoningEligibility.INELIGIBLE,
            evaluated_at=evaluated_utc,
            observation_trading_date=window.trading_date,
            current_trading_date=current_trading_date,
            observation_session=window.session,
            current_session=resolved_session,
            valid_from=window.valid_from,
            valid_until=window.valid_until,
            reasons=(
                "Observation is bound to a different market session.",
            ),
        )

    if evaluated_utc < window.valid_from:
        return TemporalValidityAssessment(
            state=TemporalValidityState.NOT_YET_VALID,
            reasoning_eligibility=TemporalReasoningEligibility.INELIGIBLE,
            evaluated_at=evaluated_utc,
            observation_trading_date=window.trading_date,
            current_trading_date=current_trading_date,
            observation_session=window.session,
            current_session=resolved_session,
            valid_from=window.valid_from,
            valid_until=window.valid_until,
            reasons=(
                "Observation validity window has not started.",
            ),
        )

    if evaluated_utc > window.valid_until:
        return TemporalValidityAssessment(
            state=TemporalValidityState.OUT_OF_WINDOW,
            reasoning_eligibility=TemporalReasoningEligibility.INELIGIBLE,
            evaluated_at=evaluated_utc,
            observation_trading_date=window.trading_date,
            current_trading_date=current_trading_date,
            observation_session=window.session,
            current_session=resolved_session,
            valid_from=window.valid_from,
            valid_until=window.valid_until,
            reasons=(
                "Observation validity window has expired.",
            ),
        )

    return TemporalValidityAssessment(
        state=TemporalValidityState.VALID_NOW,
        reasoning_eligibility=TemporalReasoningEligibility.ELIGIBLE,
        evaluated_at=evaluated_utc,
        observation_trading_date=window.trading_date,
        current_trading_date=current_trading_date,
        observation_session=window.session,
        current_session=resolved_session,
        valid_from=window.valid_from,
        valid_until=window.valid_until,
        reasons=(
            "Observation is within its explicit temporal validity window.",
        ),
    )


def eligible_for_current_temporal_reasoning(
    assessment: TemporalValidityAssessment,
) -> bool:
    return (
        assessment.state
        is TemporalValidityState.VALID_NOW
        and assessment.reasoning_eligibility
        is TemporalReasoningEligibility.ELIGIBLE
    )


def blocked_by_temporal_authority(
    assessment: TemporalValidityAssessment,
) -> bool:
    return assessment.state in {
        TemporalValidityState.NOT_YET_VALID,
        TemporalValidityState.OUT_OF_WINDOW,
        TemporalValidityState.SESSION_MISMATCH,
        TemporalValidityState.TRADING_DATE_MISMATCH,
        TemporalValidityState.UNKNOWN,
    }


def temporal_validity_snapshot(
    assessment: TemporalValidityAssessment,
) -> dict[str, object]:
    return {
        "state": assessment.state.value,
        "reasoning_eligibility": assessment.reasoning_eligibility.value,
        "evaluated_at": assessment.evaluated_at.isoformat(),
        "observation_trading_date": assessment.observation_trading_date.isoformat(),
        "current_trading_date": assessment.current_trading_date.isoformat(),
        "observation_session": assessment.observation_session.value,
        "current_session": assessment.current_session.value,
        "valid_from": assessment.valid_from.isoformat(),
        "valid_until": assessment.valid_until.isoformat(),
        "reasons": list(
            assessment.reasons
        ),
    }
