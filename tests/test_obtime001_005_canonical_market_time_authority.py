from __future__ import annotations

from dataclasses import replace
from datetime import date, datetime, timedelta, timezone
import inspect
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from web.ob_market_time_authority import (
    MarketTimeState,
    TradingDayStatus,
    assess_temporal_validity_from_market_time,
    build_canonical_market_time,
    build_market_schedule,
    market_time_contract,
    market_time_reference,
    market_time_snapshot,
    verify_canonical_market_time_receipt,
    verify_market_schedule,
)
from web.ob_observation_temporal_validity import (
    MarketSession,
    TemporalValidityState,
    build_temporal_validity_window,
)


ROOT = Path(__file__).resolve().parents[1]

NY = ZoneInfo(
    "America/New_York"
)

DAY = date(
    2026,
    9,
    21,
)


def open_schedule():
    payload = {
        "market": "US_EQUITIES",
        "date": "2026-09-21",
        "status": "OPEN",
        "premarket_open": "04:00",
        "regular_open": "09:30",
        "regular_close": "16:00",
        "after_hours_close": "20:00",
    }

    return build_market_schedule(
        market="US_EQUITIES",
        exchange_timezone="America/New_York",
        trading_date=DAY,
        day_status=TradingDayStatus.OPEN,
        calendar_authority="TEST_CALENDAR_AUTHORITY",
        calendar_reference="CAL-2026-09-21",
        calendar_payload=payload,
        premarket_open=datetime(
            2026,
            9,
            21,
            4,
            0,
            tzinfo=NY,
        ),
        regular_open=datetime(
            2026,
            9,
            21,
            9,
            30,
            tzinfo=NY,
        ),
        regular_close=datetime(
            2026,
            9,
            21,
            16,
            0,
            tzinfo=NY,
        ),
        after_hours_close=datetime(
            2026,
            9,
            21,
            20,
            0,
            tzinfo=NY,
        ),
    )


def closed_schedule():
    payload = {
        "market": "US_EQUITIES",
        "date": "2026-09-21",
        "status": "CLOSED",
    }

    return build_market_schedule(
        market="US_EQUITIES",
        exchange_timezone="America/New_York",
        trading_date=DAY,
        day_status=TradingDayStatus.CLOSED,
        calendar_authority="TEST_CALENDAR_AUTHORITY",
        calendar_reference="CAL-CLOSED-2026-09-21",
        calendar_payload=payload,
    )


def regular_time(
    hour=10,
    minute=0,
):
    return datetime(
        2026,
        9,
        21,
        hour,
        minute,
        tzinfo=NY,
    )


def test_obtime001_schedule_identity_is_hash_bound():
    schedule = open_schedule()

    assert verify_market_schedule(
        schedule
    )

    assert schedule.schedule_id.startswith(
        "OBTIMESCH-"
    )

    forged = replace(
        schedule,
        calendar_reference="FORGED",
    )

    assert not verify_market_schedule(
        forged
    )


def test_obtime001_schedule_requires_timezone_aware_boundaries():
    with pytest.raises(
        ValueError,
        match="timezone-aware",
    ):
        build_market_schedule(
            market="US_EQUITIES",
            exchange_timezone="America/New_York",
            trading_date=DAY,
            day_status="OPEN",
            calendar_authority="TEST",
            calendar_reference="TEST",
            calendar_payload={"status": "OPEN"},
            premarket_open=datetime(
                2026,
                9,
                21,
                4,
                0,
            ),
            regular_open=datetime(
                2026,
                9,
                21,
                9,
                30,
                tzinfo=NY,
            ),
            regular_close=datetime(
                2026,
                9,
                21,
                16,
                0,
                tzinfo=NY,
            ),
            after_hours_close=datetime(
                2026,
                9,
                21,
                20,
                0,
                tzinfo=NY,
            ),
        )


def test_obtime001_open_schedule_requires_strict_boundary_order():
    with pytest.raises(
        ValueError,
        match="strictly increasing",
    ):
        build_market_schedule(
            market="US_EQUITIES",
            exchange_timezone="America/New_York",
            trading_date=DAY,
            day_status="OPEN",
            calendar_authority="TEST",
            calendar_reference="TEST",
            calendar_payload={"status": "OPEN"},
            premarket_open=datetime(
                2026,
                9,
                21,
                4,
                0,
                tzinfo=NY,
            ),
            regular_open=datetime(
                2026,
                9,
                21,
                9,
                30,
                tzinfo=NY,
            ),
            regular_close=datetime(
                2026,
                9,
                21,
                9,
                0,
                tzinfo=NY,
            ),
            after_hours_close=datetime(
                2026,
                9,
                21,
                20,
                0,
                tzinfo=NY,
            ),
        )


def test_obtime002_receipt_normalizes_local_and_utc_time():
    receipt = build_canonical_market_time(
        schedule=open_schedule(),
        observed_at=regular_time(
            10,
            0,
        ),
    )

    assert receipt.state is MarketTimeState.RESOLVED
    assert receipt.market_session is MarketSession.REGULAR

    assert receipt.observed_at_local.hour == 10

    assert (
        receipt.observed_at_utc
        == datetime(
            2026,
            9,
            21,
            14,
            0,
            tzinfo=timezone.utc,
        )
    )

    assert verify_canonical_market_time_receipt(
        receipt
    )


def test_obtime003_classifies_exact_session_boundaries():
    schedule = open_schedule()

    cases = (
        (
            datetime(
                2026,
                9,
                21,
                3,
                59,
                tzinfo=NY,
            ),
            MarketSession.CLOSED,
        ),
        (
            datetime(
                2026,
                9,
                21,
                4,
                0,
                tzinfo=NY,
            ),
            MarketSession.PREMARKET,
        ),
        (
            datetime(
                2026,
                9,
                21,
                9,
                30,
                tzinfo=NY,
            ),
            MarketSession.REGULAR,
        ),
        (
            datetime(
                2026,
                9,
                21,
                16,
                0,
                tzinfo=NY,
            ),
            MarketSession.AFTER_HOURS,
        ),
        (
            datetime(
                2026,
                9,
                21,
                20,
                0,
                tzinfo=NY,
            ),
            MarketSession.CLOSED,
        ),
    )

    for observed_at, expected in cases:
        receipt = build_canonical_market_time(
            schedule=schedule,
            observed_at=observed_at,
        )

        assert (
            receipt.market_session
            is expected
        )


def test_obtime003_closed_day_never_fabricates_open_session():
    receipt = build_canonical_market_time(
        schedule=closed_schedule(),
        observed_at=regular_time(
            10,
            0,
        ),
    )

    assert (
        receipt.state
        is MarketTimeState.CLOSED_DAY
    )

    assert (
        receipt.market_session
        is MarketSession.CLOSED
    )


def test_obtime003_schedule_date_mismatch_fails_closed():
    receipt = build_canonical_market_time(
        schedule=open_schedule(),
        observed_at=datetime(
            2026,
            9,
            22,
            10,
            0,
            tzinfo=NY,
        ),
    )

    assert (
        receipt.state
        is MarketTimeState.SCHEDULE_DATE_MISMATCH
    )

    assert (
        receipt.market_session
        is MarketSession.CLOSED
    )

    assert (
        receipt.trading_date
        == date(
            2026,
            9,
            22,
        )
    )


def test_obtime004_temporal_validity_consumes_canonical_time():
    schedule = open_schedule()

    receipt = build_canonical_market_time(
        schedule=schedule,
        observed_at=regular_time(
            10,
            0,
        ),
    )

    window = build_temporal_validity_window(
        valid_from=datetime(
            2026,
            9,
            21,
            9,
            45,
            tzinfo=NY,
        ),
        valid_until=datetime(
            2026,
            9,
            21,
            10,
            15,
            tzinfo=NY,
        ),
        trading_date=DAY,
        session=MarketSession.REGULAR,
    )

    result = (
        assess_temporal_validity_from_market_time(
            window=window,
            market_time=receipt,
        )
    )

    assert (
        result.state
        is TemporalValidityState.VALID_NOW
    )

    assert (
        result.current_session
        is MarketSession.REGULAR
    )

    assert (
        result.current_trading_date
        == DAY
    )


def test_obtime004_wrong_session_blocks_through_time_authority():
    schedule = open_schedule()

    premarket_receipt = build_canonical_market_time(
        schedule=schedule,
        observed_at=datetime(
            2026,
            9,
            21,
            8,
            0,
            tzinfo=NY,
        ),
    )

    regular_window = build_temporal_validity_window(
        valid_from=datetime(
            2026,
            9,
            21,
            7,
            0,
            tzinfo=NY,
        ),
        valid_until=datetime(
            2026,
            9,
            21,
            10,
            0,
            tzinfo=NY,
        ),
        trading_date=DAY,
        session=MarketSession.REGULAR,
    )

    result = (
        assess_temporal_validity_from_market_time(
            window=regular_window,
            market_time=premarket_receipt,
        )
    )

    assert (
        result.state
        is TemporalValidityState.SESSION_MISMATCH
    )


def test_obtime004_temporal_adapter_rejects_tampered_receipt():
    receipt = build_canonical_market_time(
        schedule=open_schedule(),
        observed_at=regular_time(),
    )

    forged = replace(
        receipt,
        integrity_hash="0" * 64,
    )

    window = build_temporal_validity_window(
        valid_from=regular_time()
        - timedelta(
            minutes=5
        ),
        valid_until=regular_time()
        + timedelta(
            minutes=5
        ),
        trading_date=DAY,
        session=MarketSession.REGULAR,
    )

    with pytest.raises(
        ValueError,
        match="verified canonical market time",
    ):
        assess_temporal_validity_from_market_time(
            window=window,
            market_time=forged,
        )


def test_obtime005_temporal_adapter_has_no_caller_session_or_date_arguments():
    signature = inspect.signature(
        assess_temporal_validity_from_market_time
    )

    assert (
        "current_session"
        not in signature.parameters
    )

    assert (
        "current_trading_date"
        not in signature.parameters
    )


def test_obtime005_reference_and_snapshot_preserve_calendar_binding():
    receipt = build_canonical_market_time(
        schedule=open_schedule(),
        observed_at=regular_time(),
    )

    reference = market_time_reference(
        receipt
    )

    snapshot = market_time_snapshot(
        receipt
    )

    assert (
        reference["receipt_id"]
        == receipt.receipt_id
    )

    assert (
        reference["schedule_hash"]
        == receipt.schedule_hash
    )

    assert (
        reference["calendar_payload_hash"]
        == receipt.calendar_payload_hash
    )

    assert (
        snapshot["observed_at_utc"]
        == receipt.observed_at_utc.isoformat()
    )


def test_obtime005_contract_is_provider_neutral_and_non_executing():
    contract = market_time_contract()

    assert (
        contract["schedule_bound"]
        is True
    )

    assert (
        contract["calendar_payload_hash_bound"]
        is True
    )

    assert (
        contract["caller_supplied_current_session"]
        is False
    )

    assert (
        contract["caller_supplied_current_trading_date"]
        is False
    )

    assert (
        contract["hardcoded_weekday_is_market_calendar"]
        is False
    )

    assert (
        contract["hardcoded_holiday_table"]
        is False
    )

    for key in (
        "execution_authority",
        "broker_submission",
        "capital_movement",
        "automatic_contract_selection",
        "manual_live_unlock",
        "hybrid_unlock",
        "automated_unlock",
    ):
        assert contract[
            key
        ] is False


def test_obtime005_module_has_no_execution_or_broker_path():
    import web.ob_market_time_authority as module

    source = Path(
        module.__file__
    ).read_text(
        encoding="utf-8"
    )

    forbidden = (
        "from engine.paper_broker",
        "from engine.execution_handoff",
        "from engine.execution_loop",
        "place_order(",
        "submitOrder(",
        "executeTrade(",
        "broker.submit(",
        "moveCapital(",
        "unlockManualLive(",
        "unlockHybrid(",
        "unlockAutomated(",
    )

    for token in forbidden:
        assert token not in source


def test_obtime005_evidence_and_handoff_exist():
    assert (
        ROOT
        / "ob_evidence/time/"
        "obtime001_005_canonical_market_time_authority.json"
    ).is_file()

    assert (
        ROOT
        / "ob_evidence/time/"
        "obtime001_005_canonical_market_time_authority_handoff.md"
    ).is_file()
