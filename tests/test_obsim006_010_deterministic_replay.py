from dataclasses import replace
from datetime import date, datetime
from zoneinfo import ZoneInfo
import pytest

from web.ob_multi_simulation_replay import (
    ReplayDecision, ReplayStep, replay_three_lanes, replay_contract,
)
from web.ob_multi_simulation_harness import (
    SimulationLane as Lane, SimulationAction as Action, build_market_frame,
    build_simulation_instrument, create_multi_simulation_harness, lane_state,
    verify_lane_receipt_chain, stable_hash,
)
from web.ob_market_time_authority import build_market_schedule, build_canonical_market_time
from web.ob_owner_operating_profile import draft_operating_profile, activate_operating_profile
from web.ob_effective_policy import (
    owner_profile_policy_layer, product_phase_policy_layer, resolve_effective_policy,
)

NY = ZoneInfo("America/New_York")
DAY = date(2026, 9, 24)
INST = build_simulation_instrument(
    symbol="AAPL", instrument_kind="OPTION", contract_id="AAPL-20261218-C-250"
)


def harness():
    return create_multi_simulation_harness(
        harness_id="OBSIM006-010", account_key="trust", starting_capital=10000.0,
        control_ref="CONTROL-FROZEN", integrated_ref="ACCEPTED-BUILD",
        experimental_ref="NEW-EXPERIMENT",
    )


def step(frame_id, hour, minute, price, decisions):
    schedule = build_market_schedule(
        market="US_EQUITIES", exchange_timezone="America/New_York",
        trading_date=DAY, day_status="OPEN", calendar_authority="REPLAY_TEST_CALENDAR",
        calendar_reference=DAY.isoformat(),
        calendar_payload={"date": DAY.isoformat(), "status": "OPEN"},
        premarket_open=datetime(2026, 9, 24, 4, tzinfo=NY),
        regular_open=datetime(2026, 9, 24, 9, 30, tzinfo=NY),
        regular_close=datetime(2026, 9, 24, 16, tzinfo=NY),
        after_hours_close=datetime(2026, 9, 24, 20, tzinfo=NY),
    )
    observed = datetime(2026, 9, 24, hour, minute, tzinfo=NY)
    time = build_canonical_market_time(schedule=schedule, observed_at=observed)
    frame = build_market_frame(
        frame_id=frame_id, observed_at=observed.isoformat(), instrument=INST,
        mark_price=price, underlying_price=250.0, source_reference="REPLAY-" + frame_id,
    )
    return ReplayStep(frame=frame, market_time=time, decisions=tuple(decisions))


def decision(lane, action, key, quantity=0, **kwargs):
    return ReplayDecision(
        lane=lane, decision_id=key, action=action, strategy="REPLAY_TEST",
        reason="pre-authored historical comparison", quantity=quantity, **kwargs,
    )


def holds(prefix):
    return tuple(decision(lane, Action.HOLD, prefix + "-" + lane.value) for lane in Lane)


def policy(tmp_path):
    profile = activate_operating_profile(
        "replay-owner", draft_operating_profile("trust", "GROWTH", "MODERATE"),
        owner_confirmed=True, path=tmp_path / "replay_profile.sqlite3",
    )["profile"]
    return resolve_effective_policy(account_key="trust", layers=[
        owner_profile_policy_layer(profile), product_phase_policy_layer("trust")
    ])


def test_three_lanes_share_frames_but_not_positions_or_cash():
    initial = harness()
    first = list(holds("FIRST"))
    first[0] = decision(Lane.CONTROL, Action.OPEN, "CONTROL-OPEN", 1)
    second = list(holds("SECOND"))
    second[0] = decision(Lane.CONTROL, Action.CLOSE, "CONTROL-CLOSE", 1)
    result = replay_three_lanes(initial, [
        step("F1", 10, 0, 5.0, first),
        step("F2", 10, 30, 6.0, second),
    ])
    assert initial.market_frames == ()
    assert len(result.harness.market_frames) == 2
    assert len(lane_state(result.harness, Lane.CONTROL).trades) == 2
    assert not lane_state(result.harness, Lane.INTEGRATED).trades
    assert not lane_state(result.harness, Lane.EXPERIMENTAL).trades
    assert all(verify_lane_receipt_chain(x) for x in result.harness.lanes)
    assert result.report["broker_submission"] is False
    assert result.report["report_hash"] == stable_hash({
        key: value for key, value in result.report.items() if key != "report_hash"
    })


def test_experimental_open_requires_capsim_and_does_not_modify_input():
    initial = harness()
    orders = list(holds("NO-POLICY"))
    orders[2] = decision(Lane.EXPERIMENTAL, Action.OPEN, "EXP-OPEN", 1)
    with pytest.raises(ValueError, match="CAPSIM effective policy"):
        replay_three_lanes(initial, [step("F1", 10, 0, 5.0, orders)])
    assert initial.market_frames == ()
    assert all(not state.trades for state in initial.lanes)


def test_experimental_open_admitted_with_canonical_policy_and_time(tmp_path):
    orders = list(holds("ADMISSION"))
    orders[2] = decision(
        Lane.EXPERIMENTAL, Action.OPEN, "EXP-OPEN", 1,
        declared_max_loss_amount=50.0, risk_reference="RISK-50",
    )
    result = replay_three_lanes(
        harness(), [step("F1", 10, 0, 5.0, orders)], effective_policy=policy(tmp_path),
    )
    assert result.events[2].status == "ADMITTED"
    assert result.events[2].capital_assessment_id
    assert len(lane_state(result.harness, Lane.EXPERIMENTAL).trades) == 1
    assert not lane_state(result.harness, Lane.CONTROL).trades
    assert not lane_state(result.harness, Lane.INTEGRATED).trades


def test_capsim_block_is_reported_without_experimental_open(tmp_path):
    orders = list(holds("BLOCK"))
    orders[2] = decision(
        Lane.EXPERIMENTAL, Action.OPEN, "EXP-BLOCK", 1,
        declared_max_loss_amount=500000.0, risk_reference="RISK-BLOCK",
    )
    result = replay_three_lanes(
        harness(), [step("F1", 10, 0, 5.0, orders)], effective_policy=policy(tmp_path),
    )
    assert result.events[2].status.startswith("REJECTED_")
    assert not lane_state(result.harness, Lane.EXPERIMENTAL).trades
    assert not lane_state(result.harness, Lane.EXPERIMENTAL).positions


def test_unverified_time_is_rejected_before_mutation():
    initial = harness()
    valid = step("F1", 10, 0, 5.0, holds("BAD-TIME"))
    tampered = replace(valid, market_time=replace(valid.market_time, integrity_hash="0"*64))
    with pytest.raises(ValueError, match="verified OBTIME"):
        replay_three_lanes(initial, [tampered])
    assert initial.market_frames == ()


def test_duplicate_or_out_of_order_frames_fail_closed():
    a = step("F1", 10, 0, 5.0, holds("FIRST"))
    b = step("F2", 9, 45, 5.0, holds("SECOND"))
    with pytest.raises(ValueError, match="strictly in time"):
        replay_three_lanes(harness(), [a, b])
    with pytest.raises(ValueError, match="unique"):
        replay_three_lanes(harness(), [a, replace(a, decisions=holds("OTHER"))])


def test_missing_lane_cannot_silently_participate():
    a = step("F1", 10, 0, 5.0, holds("MISSING")[:2])
    with pytest.raises(ValueError, match="one explicit decision per lane"):
        replay_three_lanes(harness(), [a])


def test_simulation_authority_only():
    c = replay_contract()
    assert c["experimental_open_requires_existing_capsim_admission"]
    for name in ("broker_submission", "capital_movement", "automatic_contract_selection",
                 "manual_live_unlock", "hybrid_unlock", "automated_unlock"):
        assert c[name] is False
