from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from enum import Enum
from hashlib import sha256
import json
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from web.ob_observation_temporal_validity import (
    MarketSession,
    TemporalValidityAssessment,
    TemporalValidityWindow,
    assess_temporal_validity,
)


SCHEMA_VERSION = "OB_MARKET_TIME_V1"
SERVICE_VERSION = "OBTIME001_015_CANONICAL_MARKET_TIME"

DEFAULT_EXCHANGE_TIMEZONE = "America/New_York"


class TradingDayStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class MarketTimeState(str, Enum):
    RESOLVED = "RESOLVED"
    CLOSED_DAY = "CLOSED_DAY"
    SCHEDULE_DATE_MISMATCH = "SCHEDULE_DATE_MISMATCH"


@dataclass(frozen=True)
class CanonicalMarketSchedule:
    schedule_id: str
    market: str
    exchange_timezone: str
    trading_date: date
    day_status: TradingDayStatus
    calendar_authority: str
    calendar_reference: str
    calendar_payload_hash: str
    premarket_open: datetime | None
    regular_open: datetime | None
    regular_close: datetime | None
    after_hours_close: datetime | None
    schedule_hash: str


@dataclass(frozen=True)
class CanonicalMarketTimeReceipt:
    receipt_id: str
    authority: str
    market: str
    exchange_timezone: str
    state: MarketTimeState
    market_session: MarketSession
    observed_at_utc: datetime
    observed_at_local: datetime
    trading_date: date
    schedule_id: str
    schedule_hash: str
    calendar_authority: str
    calendar_reference: str
    calendar_payload_hash: str
    integrity_hash: str


def _nonblank(
    value: object,
    *,
    name: str,
) -> str:
    text = str(
        value
    ).strip()

    if not text:
        raise ValueError(
            f"{name} cannot be blank"
        )

    return text


def _require_aware(
    value: datetime,
    *,
    name: str,
) -> None:
    if (
        not isinstance(
            value,
            datetime,
        )
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise ValueError(
            f"{name} must be timezone-aware"
        )


def _canonical_json(
    value: object,
) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
        ensure_ascii=True,
        default=str,
    )


def stable_hash(
    value: object,
) -> str:
    return sha256(
        _canonical_json(
            value
        ).encode(
            "utf-8"
        )
    ).hexdigest()


def _timezone(
    name: str,
) -> ZoneInfo:
    clean = _nonblank(
        name,
        name="exchange_timezone",
    )

    try:
        return ZoneInfo(
            clean
        )

    except ZoneInfoNotFoundError as exc:
        raise ValueError(
            "unknown exchange timezone"
        ) from exc


def _iso(
    value: datetime | None,
) -> str | None:
    return (
        None
        if value is None
        else value.isoformat()
    )


def _schedule_material(
    schedule: CanonicalMarketSchedule,
) -> dict[str, object]:
    return {
        "market":
            schedule.market,

        "exchange_timezone":
            schedule.exchange_timezone,

        "trading_date":
            schedule.trading_date.isoformat(),

        "day_status":
            schedule.day_status.value,

        "calendar_authority":
            schedule.calendar_authority,

        "calendar_reference":
            schedule.calendar_reference,

        "calendar_payload_hash":
            schedule.calendar_payload_hash,

        "premarket_open":
            _iso(
                schedule.premarket_open
            ),

        "regular_open":
            _iso(
                schedule.regular_open
            ),

        "regular_close":
            _iso(
                schedule.regular_close
            ),

        "after_hours_close":
            _iso(
                schedule.after_hours_close
            ),
    }


def verify_market_schedule(
    schedule: CanonicalMarketSchedule,
) -> bool:
    if not isinstance(
        schedule,
        CanonicalMarketSchedule,
    ):
        return False

    expected = stable_hash(
        _schedule_material(
            schedule
        )
    )

    if (
        schedule.schedule_hash
        != expected
    ):
        return False

    if (
        schedule.schedule_id
        != "OBTIMESCH-"
        + expected[:24]
    ):
        return False

    return True


def build_market_schedule(
    *,
    market: str,
    exchange_timezone: str,
    trading_date: date,
    day_status: TradingDayStatus | str,
    calendar_authority: str,
    calendar_reference: str,
    calendar_payload: object,
    premarket_open: datetime | None = None,
    regular_open: datetime | None = None,
    regular_close: datetime | None = None,
    after_hours_close: datetime | None = None,
) -> CanonicalMarketSchedule:
    clean_market = _nonblank(
        market,
        name="market",
    ).upper()

    zone_name = _nonblank(
        exchange_timezone,
        name="exchange_timezone",
    )

    zone = _timezone(
        zone_name
    )

    if not isinstance(
        trading_date,
        date,
    ):
        raise ValueError(
            "trading_date must be a date"
        )

    status = (
        day_status
        if isinstance(
            day_status,
            TradingDayStatus,
        )
        else TradingDayStatus(
            str(
                day_status
            ).strip().upper()
        )
    )

    authority = _nonblank(
        calendar_authority,
        name="calendar_authority",
    )

    reference = _nonblank(
        calendar_reference,
        name="calendar_reference",
    )

    calendar_payload_hash = stable_hash(
        calendar_payload
    )

    boundaries = (
        premarket_open,
        regular_open,
        regular_close,
        after_hours_close,
    )

    if status is TradingDayStatus.CLOSED:
        if any(
            item is not None
            for item in boundaries
        ):
            raise ValueError(
                "closed trading day cannot contain open-session boundaries"
            )

    else:
        if any(
            item is None
            for item in boundaries
        ):
            raise ValueError(
                "open trading day requires all session boundaries"
            )

        resolved = []

        for index, item in enumerate(
            boundaries
        ):
            assert item is not None

            _require_aware(
                item,
                name=(
                    "session_boundary_"
                    + str(index)
                ),
            )

            local = item.astimezone(
                zone
            )

            if (
                local.date()
                != trading_date
            ):
                raise ValueError(
                    "session boundary must belong to schedule trading_date"
                )

            resolved.append(
                local
            )

        if not (
            resolved[0]
            < resolved[1]
            < resolved[2]
            < resolved[3]
        ):
            raise ValueError(
                "session boundaries must be strictly increasing"
            )

        premarket_open = resolved[0]
        regular_open = resolved[1]
        regular_close = resolved[2]
        after_hours_close = resolved[3]

    provisional = CanonicalMarketSchedule(
        schedule_id="PENDING",
        market=clean_market,
        exchange_timezone=zone_name,
        trading_date=trading_date,
        day_status=status,
        calendar_authority=authority,
        calendar_reference=reference,
        calendar_payload_hash=calendar_payload_hash,
        premarket_open=premarket_open,
        regular_open=regular_open,
        regular_close=regular_close,
        after_hours_close=after_hours_close,
        schedule_hash="PENDING",
    )

    schedule_hash = stable_hash(
        _schedule_material(
            provisional
        )
    )

    schedule = CanonicalMarketSchedule(
        schedule_id=(
            "OBTIMESCH-"
            + schedule_hash[:24]
        ),
        market=provisional.market,
        exchange_timezone=provisional.exchange_timezone,
        trading_date=provisional.trading_date,
        day_status=provisional.day_status,
        calendar_authority=provisional.calendar_authority,
        calendar_reference=provisional.calendar_reference,
        calendar_payload_hash=provisional.calendar_payload_hash,
        premarket_open=provisional.premarket_open,
        regular_open=provisional.regular_open,
        regular_close=provisional.regular_close,
        after_hours_close=provisional.after_hours_close,
        schedule_hash=schedule_hash,
    )

    if not verify_market_schedule(
        schedule
    ):
        raise ValueError(
            "constructed market schedule failed integrity verification"
        )

    return schedule


def _classify_open_day_session(
    schedule: CanonicalMarketSchedule,
    observed_local: datetime,
) -> MarketSession:
    if schedule.day_status is not TradingDayStatus.OPEN:
        return MarketSession.CLOSED

    pre = schedule.premarket_open
    regular_open = schedule.regular_open
    regular_close = schedule.regular_close
    after_close = schedule.after_hours_close

    if (
        pre is None
        or regular_open is None
        or regular_close is None
        or after_close is None
    ):
        raise ValueError(
            "open schedule is missing session boundaries"
        )

    if (
        pre
        <= observed_local
        < regular_open
    ):
        return MarketSession.PREMARKET

    if (
        regular_open
        <= observed_local
        < regular_close
    ):
        return MarketSession.REGULAR

    if (
        regular_close
        <= observed_local
        < after_close
    ):
        return MarketSession.AFTER_HOURS

    return MarketSession.CLOSED


def _receipt_payload(
    *,
    market: str,
    exchange_timezone: str,
    state: MarketTimeState,
    market_session: MarketSession,
    observed_at_utc: datetime,
    observed_at_local: datetime,
    trading_date: date,
    schedule_id: str,
    schedule_hash: str,
    calendar_authority: str,
    calendar_reference: str,
    calendar_payload_hash: str,
) -> dict[str, object]:
    return {
        "authority":
            SCHEMA_VERSION,

        "market":
            market,

        "exchange_timezone":
            exchange_timezone,

        "state":
            state.value,

        "market_session":
            market_session.value,

        "observed_at_utc":
            observed_at_utc.isoformat(),

        "observed_at_local":
            observed_at_local.isoformat(),

        "trading_date":
            trading_date.isoformat(),

        "schedule_id":
            schedule_id,

        "schedule_hash":
            schedule_hash,

        "calendar_authority":
            calendar_authority,

        "calendar_reference":
            calendar_reference,

        "calendar_payload_hash":
            calendar_payload_hash,
    }


def build_canonical_market_time(
    *,
    schedule: CanonicalMarketSchedule,
    observed_at: datetime,
) -> CanonicalMarketTimeReceipt:
    if not verify_market_schedule(
        schedule
    ):
        raise ValueError(
            "market schedule integrity verification failed"
        )

    _require_aware(
        observed_at,
        name="observed_at",
    )

    zone = _timezone(
        schedule.exchange_timezone
    )

    observed_local = observed_at.astimezone(
        zone
    )

    observed_utc = observed_at.astimezone(
        timezone.utc
    )

    local_date = observed_local.date()

    if (
        local_date
        != schedule.trading_date
    ):
        state = (
            MarketTimeState.SCHEDULE_DATE_MISMATCH
        )

        session = (
            MarketSession.CLOSED
        )

    elif (
        schedule.day_status
        is TradingDayStatus.CLOSED
    ):
        state = (
            MarketTimeState.CLOSED_DAY
        )

        session = (
            MarketSession.CLOSED
        )

    else:
        state = (
            MarketTimeState.RESOLVED
        )

        session = (
            _classify_open_day_session(
                schedule,
                observed_local,
            )
        )

    payload = _receipt_payload(
        market=schedule.market,
        exchange_timezone=schedule.exchange_timezone,
        state=state,
        market_session=session,
        observed_at_utc=observed_utc,
        observed_at_local=observed_local,
        trading_date=local_date,
        schedule_id=schedule.schedule_id,
        schedule_hash=schedule.schedule_hash,
        calendar_authority=schedule.calendar_authority,
        calendar_reference=schedule.calendar_reference,
        calendar_payload_hash=schedule.calendar_payload_hash,
    )

    integrity = stable_hash(
        payload
    )

    return CanonicalMarketTimeReceipt(
        receipt_id=(
            "OBTIME-"
            + integrity[:24]
        ),
        authority=SCHEMA_VERSION,
        market=schedule.market,
        exchange_timezone=schedule.exchange_timezone,
        state=state,
        market_session=session,
        observed_at_utc=observed_utc,
        observed_at_local=observed_local,
        trading_date=local_date,
        schedule_id=schedule.schedule_id,
        schedule_hash=schedule.schedule_hash,
        calendar_authority=schedule.calendar_authority,
        calendar_reference=schedule.calendar_reference,
        calendar_payload_hash=schedule.calendar_payload_hash,
        integrity_hash=integrity,
    )


def verify_canonical_market_time_receipt(
    receipt: CanonicalMarketTimeReceipt,
) -> bool:
    if not isinstance(
        receipt,
        CanonicalMarketTimeReceipt,
    ):
        return False

    if (
        receipt.authority
        != SCHEMA_VERSION
    ):
        return False

    payload = _receipt_payload(
        market=receipt.market,
        exchange_timezone=receipt.exchange_timezone,
        state=receipt.state,
        market_session=receipt.market_session,
        observed_at_utc=receipt.observed_at_utc,
        observed_at_local=receipt.observed_at_local,
        trading_date=receipt.trading_date,
        schedule_id=receipt.schedule_id,
        schedule_hash=receipt.schedule_hash,
        calendar_authority=receipt.calendar_authority,
        calendar_reference=receipt.calendar_reference,
        calendar_payload_hash=receipt.calendar_payload_hash,
    )

    expected = stable_hash(
        payload
    )

    if (
        receipt.integrity_hash
        != expected
    ):
        return False

    if (
        receipt.receipt_id
        != "OBTIME-"
        + expected[:24]
    ):
        return False

    return True


def market_time_reference(
    receipt: CanonicalMarketTimeReceipt,
) -> dict[str, object]:
    if not verify_canonical_market_time_receipt(
        receipt
    ):
        raise ValueError(
            "canonical market-time receipt failed verification"
        )

    return {
        "authority":
            receipt.authority,

        "receipt_id":
            receipt.receipt_id,

        "integrity_hash":
            receipt.integrity_hash,

        "market":
            receipt.market,

        "exchange_timezone":
            receipt.exchange_timezone,

        "trading_date":
            receipt.trading_date.isoformat(),

        "market_session":
            receipt.market_session.value,

        "state":
            receipt.state.value,

        "schedule_id":
            receipt.schedule_id,

        "schedule_hash":
            receipt.schedule_hash,

        "calendar_authority":
            receipt.calendar_authority,

        "calendar_reference":
            receipt.calendar_reference,

        "calendar_payload_hash":
            receipt.calendar_payload_hash,
    }


def assess_temporal_validity_from_market_time(
    *,
    window: TemporalValidityWindow,
    market_time: CanonicalMarketTimeReceipt,
) -> TemporalValidityAssessment:
    if not verify_canonical_market_time_receipt(
        market_time
    ):
        raise ValueError(
            "temporal validity requires verified canonical market time"
        )

    return assess_temporal_validity(
        window=window,
        evaluated_at=market_time.observed_at_utc,
        current_trading_date=market_time.trading_date,
        current_session=market_time.market_session,
    )


def evaluate_freshness_from_market_time(
    *,
    provenance: Any,
    observation_class: Any,
    market_time: CanonicalMarketTimeReceipt,
    policy: Any = None,
):
    from web.ob_observation_freshness import (
        evaluate_freshness,
    )

    if not verify_canonical_market_time_receipt(
        market_time
    ):
        raise ValueError(
            "freshness evaluation requires verified canonical market time"
        )

    if (
        market_time.state
        is MarketTimeState.SCHEDULE_DATE_MISMATCH
    ):
        raise ValueError(
            "freshness evaluation cannot use schedule-date-mismatched market time"
        )

    return evaluate_freshness(
        provenance,
        observation_class,
        now=market_time.observed_at_utc,
        policy=policy,
    )


def market_time_contract() -> dict[str, object]:
    return {
        "schema_version":
            SCHEMA_VERSION,

        "service_version":
            SERVICE_VERSION,

        "authority":
            SCHEMA_VERSION,

        "timezone_aware_required":
            True,

        "schedule_bound":
            True,

        "calendar_payload_hash_bound":
            True,

        "caller_supplied_current_session":
            False,

        "caller_supplied_current_trading_date":
            False,

        "hardcoded_weekday_is_market_calendar":
            False,

        "hardcoded_holiday_table":
            False,

        "provider_neutral_calendar_boundary":
            True,

        "temporal_validity_adapter":
            True,

        "freshness_clock_adapter":
            True,

        "caller_supplied_freshness_now":
            False,

        "execution_authority":
            False,

        "broker_submission":
            False,

        "capital_movement":
            False,

        "automatic_contract_selection":
            False,

        "manual_live_unlock":
            False,

        "hybrid_unlock":
            False,

        "automated_unlock":
            False,
    }


def market_time_snapshot(
    receipt: CanonicalMarketTimeReceipt,
) -> dict[str, object]:
    reference = market_time_reference(
        receipt
    )

    return {
        **reference,

        "observed_at_utc":
            receipt.observed_at_utc.isoformat(),

        "observed_at_local":
            receipt.observed_at_local.isoformat(),

        "authority_boundary":
            market_time_contract(),
    }
