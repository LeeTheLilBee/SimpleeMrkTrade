"""OBSIM016–020: owner-started free cadence, report archive, stop/recovery."""
from dataclasses import replace
from datetime import date, datetime, timedelta, timezone
import json
from zoneinfo import ZoneInfo

import pytest

from web.ob_market_time_authority import build_canonical_market_time, build_market_schedule
from web.ob_multi_simulation_harness import (
    SimulationAction as Action, SimulationLane as Lane,
    build_market_frame, build_simulation_instrument,
    create_multi_simulation_harness, stable_hash,
)
from web.ob_multi_simulation_replay import ReplayDecision, ReplayStep
from web.ob_on_demand_simulation_session import (
    INTERVAL_SECONDS, LocalSimulationReportStore, SessionStatus, SourceKind,
    pause_session, resume_session, session_contract, start_session, stop_session,
    tick_session,
)

UTC = timezone.utc
NY = ZoneInfo("America/New_York")
DAY = date(2026, 9, 24)
BASE = datetime(2026, 9, 26, 12, tzinfo=UTC)


def harness():
    return create_multi_simulation_harness(
        harness_id="OBSIM016-020", account_key="PROOF-DEMO", starting_capital=10000.0,
        control_ref="CONTROL-FROZEN", integrated_ref="INTEGRATED-ACCEPTED",
        experimental_ref="EXPERIMENTAL-ISOLATED",
    )


def step(key, minute=0, choices=None):
    schedule = build_market_schedule(
        market="US_EQUITIES", exchange_timezone="America/New_York",
        trading_date=DAY, day_status="OPEN", calendar_authority="BETA_TEST_FIXTURE",
        calendar_reference=DAY.isoformat(),
        calendar_payload={"date": DAY.isoformat(), "status": "OPEN"},
        premarket_open=datetime(2026, 9, 24, 4, tzinfo=NY),
        regular_open=datetime(2026, 9, 24, 9, 30, tzinfo=NY),
        regular_close=datetime(2026, 9, 24, 16, tzinfo=NY),
        after_hours_close=datetime(2026, 9, 24, 20, tzinfo=NY),
    )
    observed = datetime(2026, 9, 24, 10, minute, tzinfo=NY)
    inst = build_simulation_instrument(
        symbol="AAPL", instrument_kind="OPTION", contract_id="AAPL-20261218-C-250",
    )
    frame = build_market_frame(
        frame_id=key, observed_at=observed.isoformat(), instrument=inst,
        mark_price=2.0 + minute, underlying_price=250.0,
        source_reference="HISTORICAL-TEST-" + key,
    )
    decisions = choices or tuple(
        ReplayDecision(
            lane=lane, decision_id=f"{key}-{lane.value}",
            action=Action.HOLD, strategy="BETA_REPLAY", reason="explicit test decision",
        ) for lane in Lane
    )
    return ReplayStep(
        frame=frame, market_time=build_canonical_market_time(
            schedule=schedule, observed_at=observed,
        ), decisions=decisions,
    )


def start():
    return start_session(
        session_id="BETA-001", initial_harness=harness(),
        source_kind=SourceKind.HISTORICAL, now=BASE,
    )


def test_30_second_cadence_three_lanes_and_local_reports(tmp_path):
    store = LocalSimulationReportStore(tmp_path)
    session = start()
    with pytest.raises(ValueError, match="not due"):
        tick_session(session, step("F1"), now=BASE + timedelta(seconds=29), store=store)
    assert not session.reports
    result = tick_session(session, step("F1"), now=BASE + timedelta(seconds=30), store=store)
    assert not session.steps  # immutable input
    assert len(result.steps) == len(result.reports) == 1
    report = result.reports[0]
    assert report["sequence"] == 1
    assert report["interval_seconds"] == INTERVAL_SECONDS == 30
    assert set(report["lanes"]) == {lane.value for lane in Lane}
    assert set(report["deltas"]) == {lane.value for lane in Lane}
    assert report["receipt_chains_valid"] is True
    assert report["source_kind"] == "HISTORICAL"
    assert report["source_claim_verified"] is False
    assert report["source_freshness"] == "HISTORICAL"
    assert report["simulation_only"] and not report["broker_submission"]
    assert not report["capital_movement"] and not report["manual_live_unlock"]
    assert len(store.load_ticks("BETA-001")) == 1
    assert store.load_ticks("BETA-001")[0] == report

    second = tick_session(
        result, step("F2", minute=1), now=BASE + timedelta(seconds=60), store=store,
    )
    assert len(second.reports) == 2
    assert second.reports[1]["frame_id"] == "F2"
    assert second.reports[1]["replay_report_hash"] != report["replay_report_hash"]
    assert len(store.load_ticks("BETA-001")) == 2


def test_pause_resume_requires_fresh_interval_and_stop_creates_summary(tmp_path):
    store = LocalSimulationReportStore(tmp_path)
    running = tick_session(
        start(), step("F1"), now=BASE + timedelta(seconds=30), store=store,
    )
    paused = pause_session(running)
    with pytest.raises(ValueError, match="not running"):
        tick_session(paused, step("F2", 1), now=BASE + timedelta(seconds=60), store=store)
    resumed = resume_session(paused, now=BASE + timedelta(minutes=10))
    with pytest.raises(ValueError, match="not due"):
        tick_session(resumed, step("F2", 1), now=BASE + timedelta(minutes=10, seconds=29), store=store)
    active = tick_session(
        resumed, step("F2", 1), now=BASE + timedelta(minutes=10, seconds=30), store=store,
    )
    done = stop_session(
        active, now=BASE + timedelta(minutes=11), store=store,
    )
    assert done.status is SessionStatus.STOPPED
    final = json.loads((tmp_path / "BETA-001" / "_final.json").read_text())
    hashed = {k: v for k, v in final.items() if k != "report_hash"}
    assert final["report_hash"] == stable_hash(hashed)
    assert final["total_ticks"] == 2
    assert final["last_report_hash"] == active.reports[-1]["report_hash"]
    with pytest.raises(ValueError, match="not running"):
        tick_session(done, step("F3", 2), now=BASE + timedelta(minutes=12), store=store)
    with pytest.raises(ValueError, match="already stopped"):
        stop_session(done, now=BASE + timedelta(minutes=12), store=store)


def test_bad_later_frame_fails_closed_without_damaging_saved_history(tmp_path):
    store = LocalSimulationReportStore(tmp_path)
    first = tick_session(
        start(), step("F1"), now=BASE + timedelta(seconds=30), store=store,
    )
    with pytest.raises(ValueError, match="unique"):
        tick_session(
            first, step("F1", minute=1),
            now=BASE + timedelta(seconds=60), store=store,
        )
    assert len(first.steps) == 1 and len(first.reports) == 1
    assert len(store.load_ticks("BETA-001")) == 1
    assert not (tmp_path / "BETA-001" / "0002.json").exists()


def test_store_rejects_duplicate_and_tamper(tmp_path):
    store = LocalSimulationReportStore(tmp_path)
    first = tick_session(
        start(), step("F1"), now=BASE + timedelta(seconds=30), store=store,
    )
    with pytest.raises(FileExistsError, match="already exists"):
        tick_session(
            start(), step("F1"), now=BASE + timedelta(seconds=30), store=store,
        )
    location = tmp_path / "BETA-001" / "0001.json"
    saved = json.loads(location.read_text())
    saved["lanes"]["CONTROL"]["equity"] = 999999.0
    location.write_text(json.dumps(saved))
    with pytest.raises(ValueError, match="integrity"):
        store.load_ticks(first.session_id)


def test_invalid_source_and_status_boundaries(tmp_path):
    with pytest.raises(ValueError, match="source kind"):
        start_session(
            session_id="BETA-001", initial_harness=harness(),
            source_kind="LIVE_OBSERVED", now=BASE,
        )
    with pytest.raises(ValueError, match="timezone-aware"):
        start_session(
            session_id="BETA-001", initial_harness=harness(),
            source_kind=SourceKind.HISTORICAL, now=datetime(2026, 9, 26),
        )
    with pytest.raises(ValueError, match="fresh"):
        from web.ob_multi_simulation_harness import broadcast_market_frame
        polluted = broadcast_market_frame(harness(), step("F1").frame)
        start_session(
            session_id="BETA-001", initial_harness=polluted,
            source_kind=SourceKind.HISTORICAL, now=BASE,
        )
    assert session_contract()["no_unattended_timer_or_hosting"] is True
    assert session_contract()["no_price_feed_or_trade_generator"] is True
    assert session_contract()["broker_submission"] is False
    assert session_contract()["capital_movement"] is False
