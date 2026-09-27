"""OBSIM036–040: explicit historical/synthetic input never becomes broker or Tower proof."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import math
from zoneinfo import ZoneInfo

import pytest

from test_obsim016_020_on_demand_session import BASE, harness
from web.ob_market_time_authority import verify_canonical_market_time_receipt
from web.ob_multi_simulation_harness import SimulationLane
from web.ob_on_demand_simulation_session import (
    LocalSimulationReportStore, SourceKind, start_session,
)
from web.ob_explicit_owner_rehearsal_input import (
    SCHEMA_VERSION, LocalOwnerRehearsalDesk,
    build_explicit_owner_rehearsal_step, explicit_owner_rehearsal_contract,
)

NY = ZoneInfo("America/New_York")


def payload(frame_id="LOCAL-F1", minute=0, *, source_kind="HISTORICAL"):
    observed = datetime(2026, 9, 24, 10, minute, tzinfo=NY)
    return {
        "schema_version": SCHEMA_VERSION, "source_kind": source_kind,
        "account_key": "PROOF-DEMO",
        "frame": {
            "frame_id": frame_id, "observed_at": observed.isoformat(),
            "symbol": "AAPL", "instrument_kind": "OPTION",
            "contract_id": "AAPL-20261218-C-250",
            "mark_price": 2.0 + minute, "underlying_price": 250.0,
            "source_reference": "OWNER-HISTORICAL-INPUT-" + frame_id,
        },
        "calendar": {
            "market": "US_EQUITIES", "exchange_timezone": "America/New_York",
            "trading_date": "2026-09-24", "day_status": "OPEN",
            "calendar_authority": "OWNER_DECLARED_HISTORICAL_FIXTURE",
            "calendar_reference": "OWNER-DECLARED-CALENDAR-2026-09-24",
            "calendar_payload": {"date": "2026-09-24", "status": "OPEN", "verified_externally": False},
            "premarket_open": datetime(2026, 9, 24, 4, tzinfo=NY).isoformat(),
            "regular_open": datetime(2026, 9, 24, 9, 30, tzinfo=NY).isoformat(),
            "regular_close": datetime(2026, 9, 24, 16, tzinfo=NY).isoformat(),
            "after_hours_close": datetime(2026, 9, 24, 20, tzinfo=NY).isoformat(),
        },
        "decisions": {
            lane.value: {
                "decision_id": frame_id + "-" + lane.value,
                "action": "HOLD", "strategy": "OWNER_DECLARED_PRACTICE",
                "reason": "Explicit owner practice decision", "quantity": 0,
                "evidence_refs": ["LOCAL-ONLY-OWNER-REHEARSAL"],
            } for lane in SimulationLane
        },
    }


def desk(tmp_path):
    session = start_session(
        session_id="LOCAL-OWNER-001", initial_harness=harness(),
        source_kind=SourceKind.HISTORICAL, now=BASE,
    )
    return LocalOwnerRehearsalDesk(session, LocalSimulationReportStore(tmp_path / "private"))


def test_obsim036_explicit_input_reuses_canonical_time_and_replay_types():
    step = build_explicit_owner_rehearsal_step(
        payload(), source_kind=SourceKind.HISTORICAL, account_key="PROOF-DEMO",
    )
    assert verify_canonical_market_time_receipt(step.market_time)
    assert step.market_time.calendar_authority == "OWNER_DECLARED_HISTORICAL_FIXTURE"
    assert step.frame.source_reference.startswith("OWNER-HISTORICAL")
    assert {d.lane for d in step.decisions} == set(SimulationLane)
    assert not any(d.action.value == "OPEN" for d in step.decisions)


def test_obsim037_owner_desk_due_explicit_input_and_report_only_stop(tmp_path):
    owner = desk(tmp_path)
    assert owner.view(now=BASE + timedelta(seconds=29))["due"]["state"] == "WAIT_INTERVAL"
    with pytest.raises(ValueError, match="not due"):
        owner.submit_explicit_input(payload(), now=BASE + timedelta(seconds=29))
    assert owner.session.reports == ()
    first = owner.submit_explicit_input(payload(), now=BASE + timedelta(seconds=30))
    assert first["accepted_ticks"] == 1 and first["last_report_hash"]
    assert first["declared_source_kind"] == "HISTORICAL"
    assert not first["source_provider_authenticated"] and not first["owner_authenticated_here"]
    owner.pause()
    assert owner.view(now=BASE + timedelta(seconds=40))["state"] == "PAUSED"
    with pytest.raises(ValueError, match="not due"):
        owner.submit_explicit_input(
            payload("LOCAL-F2", 1), now=BASE + timedelta(seconds=60),
        )
    owner.resume(now=BASE + timedelta(seconds=100))
    second = owner.submit_explicit_input(
        payload("LOCAL-F2", 1), now=BASE + timedelta(seconds=130),
    )
    assert second["accepted_ticks"] == 2
    final = owner.stop(now=BASE + timedelta(seconds=131))
    assert final["status"] == "FINALIZED_REPORT_ONLY"
    assert final["tick_count"] == 2 and not final["in_memory_session_restored"]
    assert not owner.view(now=BASE + timedelta(seconds=131))["broker_submission"]
    assert not owner.view(now=BASE + timedelta(seconds=131))["manual_live_unlock"]


def test_obsim038_no_malformed_or_cross_account_input_can_advance_or_write(tmp_path):
    owner = desk(tmp_path)
    good = payload()
    failures = [
        {**good, "account_key": "trust"},
        {**good, "source_kind": "LIVE_OBSERVED"},
        {**good, "verified_tower_owner": True},
        {**good, "frame": {**good["frame"], "source_provider_authenticated": True}},
        {**good, "calendar": {**good["calendar"], "calendar_authority": "NASDAQ"}},
        {**good, "decisions": {**good["decisions"], "BROKER": good["decisions"]["CONTROL"]}},
    ]
    for rejected in failures:
        with pytest.raises(ValueError):
            owner.submit_explicit_input(rejected, now=BASE + timedelta(seconds=30))
        assert not owner.session.reports
    assert not (tmp_path / "private" / "LOCAL-OWNER-001" / "0001.json").exists()
    assert owner.submit_explicit_input(good, now=BASE + timedelta(seconds=30))["accepted_ticks"] == 1


def test_obsim039_reject_fake_price_future_naive_time_and_experimental_policy_bypass():
    raw = payload()
    mistakes = []
    for value in (float("nan"), float("inf"), True, -1.0):
        altered = deepcopy(raw)
        altered["frame"]["mark_price"] = value
        mistakes.append(altered)
    altered = deepcopy(raw)
    altered["frame"]["observed_at"] = "2026-09-24T10:00:00"
    mistakes.append(altered)
    altered = deepcopy(raw)
    altered["calendar"]["regular_close"] = "2026-09-24T08:00:00-04:00"
    mistakes.append(altered)
    altered = deepcopy(raw)
    altered["decisions"]["EXPERIMENTAL"]["action"] = "OPEN"
    altered["decisions"]["EXPERIMENTAL"]["quantity"] = 1
    mistakes.append(altered)
    altered = deepcopy(raw)
    altered["frame"]["instrument_kind"] = "STOCK"
    mistakes.append(altered)
    for rejected in mistakes:
        with pytest.raises(ValueError):
            build_explicit_owner_rehearsal_step(
                rejected, source_kind=SourceKind.HISTORICAL, account_key="PROOF-DEMO",
            )


def test_obsim040_complete_contract_is_rehearsal_only():
    contract = explicit_owner_rehearsal_contract()
    assert contract["explicit_owner_authored_three_lane_input"] is True
    assert contract["source_kinds"] == ["SYNTHETIC", "HISTORICAL"]
    for field in (
        "external_calendar_or_market_provenance_authenticated",
        "live_observed_user_payload_admitted",
        "experimental_open_without_capsim", "automated_decision_or_price",
        "automatic_tick_scheduled", "hosted_route_or_tower_session_created",
        "broker_submission", "capital_movement", "manual_live_unlock",
        "hybrid_unlock", "automated_unlock",
    ):
        assert contract[field] is False
