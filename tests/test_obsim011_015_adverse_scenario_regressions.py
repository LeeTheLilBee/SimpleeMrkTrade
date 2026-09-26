"""OBSIM011–015: replay adverse scenarios against the accepted immutable harness."""
from dataclasses import replace
from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest

from web.ob_market_time_authority import build_canonical_market_time, build_market_schedule
from web.ob_multi_simulation_harness import (
    SimulationAction as Action, SimulationLane as Lane, build_market_frame,
    build_simulation_instrument, create_multi_simulation_harness,
    lane_state, verify_lane_receipt_chain, stable_hash,
)
from web.ob_multi_simulation_replay import ReplayDecision, ReplayStep, replay_three_lanes

NY = ZoneInfo("America/New_York")
DAY = date(2026, 9, 24)
INST = build_simulation_instrument(
    symbol="AAPL", instrument_kind="OPTION", contract_id="AAPL-20261218-C-250",
)


def harness():
    return create_multi_simulation_harness(
        harness_id="OBSIM011-015", account_key="trust",
        starting_capital=10000.0, control_ref="CONTROL-FROZEN",
        integrated_ref="INTEGRATED-ACCEPTED", experimental_ref="EXPERIMENTAL-CANDIDATE",
    )


def decision(lane, action, key, quantity=0, **options):
    return ReplayDecision(
        lane=lane, action=action, decision_id=key,
        strategy="PREAUTHORED_ADVERSE_REPLAY", reason="explicit historical-only choice",
        quantity=quantity, **options,
    )


def holds(key):
    return tuple(decision(lane, Action.HOLD, f"{key}-{lane.value}") for lane in Lane)


def frame(key, hour, minute, mark, choices):
    observed = datetime(2026, 9, 24, hour, minute, tzinfo=NY)
    schedule = build_market_schedule(
        market="US_EQUITIES", exchange_timezone="America/New_York",
        trading_date=DAY, day_status="OPEN",
        calendar_authority="OBSIM011_TEST_CALENDAR",
        calendar_reference=DAY.isoformat(),
        calendar_payload={"date": DAY.isoformat(), "status": "OPEN"},
        premarket_open=datetime(2026, 9, 24, 4, tzinfo=NY),
        regular_open=datetime(2026, 9, 24, 9, 30, tzinfo=NY),
        regular_close=datetime(2026, 9, 24, 16, tzinfo=NY),
        after_hours_close=datetime(2026, 9, 24, 20, tzinfo=NY),
    )
    receipt = build_canonical_market_time(schedule=schedule, observed_at=observed)
    return ReplayStep(
        frame=build_market_frame(
            frame_id=key, observed_at=observed.isoformat(), instrument=INST,
            mark_price=mark, underlying_price=250.0,
            source_reference="HISTORICAL-ADVERSE-" + key,
        ),
        market_time=receipt, decisions=tuple(choices),
    )


def test_price_collapse_only_changes_each_lane_through_its_own_fills():
    baseline = harness()
    initial = list(holds("OPEN"))
    initial[0] = decision(Lane.CONTROL, Action.OPEN, "CONTROL-OPEN", 1)
    initial[1] = decision(Lane.INTEGRATED, Action.OPEN, "INTEGRATED-OPEN", 1)
    shock = frame("MARK-SHOCK", 10, 30, 0.01, holds("AFTER-SHOCK"))
    out = replay_three_lanes(baseline, [
        frame("MARK-ENTRY", 10, 0, 5.0, initial), shock,
    ])
    control = lane_state(out.harness, Lane.CONTROL)
    integrated = lane_state(out.harness, Lane.INTEGRATED)
    experimental = lane_state(out.harness, Lane.EXPERIMENTAL)
    assert control.positions[0].current_price == 0.01
    assert integrated.positions[0].current_price == 0.01
    assert control.equity < control.starting_capital
    assert integrated.equity < integrated.starting_capital
    assert experimental.positions == () and experimental.trades == ()
    assert experimental.cash == experimental.starting_capital
    assert all(verify_lane_receipt_chain(x) for x in out.harness.lanes)
    assert baseline.market_frames == () and all(not lane.positions for lane in baseline.lanes)
    assert out.report["promotion_or_winner_selected"] is False
    assert out.report["report_hash"] == stable_hash({
        k: v for k, v in out.report.items() if k != "report_hash"
    })


def test_full_close_after_shock_uses_existing_fill_math_not_mark_as_realized():
    opening = list(holds("OPEN"))
    opening[0] = decision(Lane.CONTROL, Action.OPEN, "CTRL-ENTRY", 1)
    opening[1] = decision(Lane.INTEGRATED, Action.OPEN, "INT-ENTRY", 1)
    closing = list(holds("CLOSE"))
    closing[0] = decision(Lane.CONTROL, Action.CLOSE, "CTRL-CLOSE", 1)
    closing[1] = decision(Lane.INTEGRATED, Action.CLOSE, "INT-CLOSE", 1)
    result = replay_three_lanes(harness(), [
        frame("ENTRY", 10, 0, 5.0, opening),
        frame("SHOCK", 10, 30, 0.01, holds("HOLD")),
        frame("CLOSE", 11, 0, 0.01, closing),
    ])
    for selected in (Lane.CONTROL, Lane.INTEGRATED):
        state = lane_state(result.harness, selected)
        assert not state.positions and len(state.trades) == 2
        assert state.realized_pnl < 0 and state.unrealized_pnl == 0
        assert verify_lane_receipt_chain(state)
    untouched = lane_state(result.harness, Lane.EXPERIMENTAL)
    assert not untouched.trades and not untouched.positions
    assert untouched.realized_pnl == 0


def test_late_tampered_time_fails_before_any_caller_mutation():
    initial = harness()
    opening = list(holds("FIRST"))
    opening[0] = decision(Lane.CONTROL, Action.OPEN, "CONTROL-OPEN", 1)
    first = frame("FRAME-1", 10, 0, 5.0, opening)
    second = frame("FRAME-2", 10, 30, 0.01, holds("SECOND"))
    bad = replace(second, market_time=replace(second.market_time, integrity_hash="0"*64))
    with pytest.raises(ValueError, match="verified OBTIME"):
        replay_three_lanes(initial, (first, bad))
    assert initial.market_frames == ()
    assert all(not lane.receipts and not lane.trades for lane in initial.lanes)


def test_duplicate_canonical_frame_and_missing_lane_block_adverse_replay():
    first = frame("FRAME-1", 10, 0, 5.0, holds("FIRST"))
    duplicate = frame("FRAME-1", 10, 30, 0.01, holds("SECOND"))
    with pytest.raises(ValueError, match="unique"):
        replay_three_lanes(harness(), (first, duplicate))
    incomplete = frame("FRAME-2", 10, 30, 0.01, holds("TWO")[:2])
    with pytest.raises(ValueError, match="one explicit decision per lane"):
        replay_three_lanes(harness(), (first, incomplete))


def test_extreme_declared_risk_rejected_without_impact_on_two_other_lanes(tmp_path):
    from web.ob_owner_operating_profile import draft_operating_profile, activate_operating_profile
    from web.ob_effective_policy import (
        owner_profile_policy_layer, product_phase_policy_layer, resolve_effective_policy,
    )
    owner = activate_operating_profile(
        "obsim-adverse-owner",
        draft_operating_profile("trust", "GROWTH", "MODERATE"),
        owner_confirmed=True, path=tmp_path / "owner.sqlite3",
    )["profile"]
    policy = resolve_effective_policy(account_key="trust", layers=[
        owner_profile_policy_layer(owner), product_phase_policy_layer("trust"),
    ])
    choices = list(holds("RISK"))
    choices[2] = decision(
        Lane.EXPERIMENTAL, Action.OPEN, "EXP-OVERREACH", 1,
        declared_max_loss_amount=1000000.0, risk_reference="RISK-OVERREACH",
    )
    result = replay_three_lanes(
        harness(), (frame("RISK-ENTRY", 10, 0, 5.0, choices),),
        effective_policy=policy,
    )
    assert result.events[2].status.startswith("REJECTED_")
    assert result.events[2].capital_assessment_id
    assert not lane_state(result.harness, Lane.EXPERIMENTAL).trades
    assert not lane_state(result.harness, Lane.CONTROL).trades
    assert not lane_state(result.harness, Lane.INTEGRATED).trades
    assert result.report["broker_submission"] is False
    assert result.report["manual_live_unlock"] is False
