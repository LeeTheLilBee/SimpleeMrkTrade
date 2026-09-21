from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from web.ob_multi_simulation_harness import (
    SimulationAction,
    SimulationLane,
    apply_simulation_decision,
    broadcast_market_frame,
    build_market_frame,
    build_simulation_instrument,
    compare_simulation_lanes,
    create_multi_simulation_harness,
    harness_snapshot,
    lane_state,
    record_simulation_review,
    simulation_contract,
    verify_lane_receipt_chain,
)


CERTIFIED_FOUNDATION = (
    "a280f88a5d2348f09487e8321e5e9bfda1df1bea"
)


def base_harness():
    return create_multi_simulation_harness(
        harness_id="HARNESS-001",
        account_key="PROOF-DEMO",
        starting_capital=10000.0,
        control_ref=CERTIFIED_FOUNDATION,
        integrated_ref=CERTIFIED_FOUNDATION,
        experimental_ref="OBTIME-PENDING",
    )


def option_frame(
    frame_id="FRAME-001",
    mark=2.00,
):
    instrument = build_simulation_instrument(
        symbol="AAPL",
        instrument_kind="OPTION",
        contract_id="AAPL-20261218-C-250",
    )

    return build_market_frame(
        frame_id=frame_id,
        observed_at="2026-09-21T14:00:00Z",
        instrument=instrument,
        mark_price=mark,
        underlying_price=250.0,
        source_reference=f"SOURCE-{frame_id}",
    )


def stock_frame(
    frame_id="FRAME-STOCK-001",
    mark=100.0,
):
    instrument = build_simulation_instrument(
        symbol="MSFT",
        instrument_kind="STOCK",
    )

    return build_market_frame(
        frame_id=frame_id,
        observed_at="2026-09-21T14:00:00Z",
        instrument=instrument,
        mark_price=mark,
        underlying_price=mark,
        source_reference=f"SOURCE-{frame_id}",
    )


def test_obsim001_exact_three_independent_lanes():
    harness = base_harness()

    assert tuple(
        lane.lane
        for lane
        in harness.lanes
    ) == (
        SimulationLane.CONTROL,
        SimulationLane.INTEGRATED,
        SimulationLane.EXPERIMENTAL,
    )

    assert all(
        lane.starting_capital == 10000.0
        for lane
        in harness.lanes
    )

    assert all(
        lane.cash == 10000.0
        for lane
        in harness.lanes
    )

    assert all(
        lane.positions == ()
        for lane
        in harness.lanes
    )


def test_obsim002_common_market_frame_broadcasts_to_all_lanes():
    harness = base_harness()
    frame = option_frame()

    updated = broadcast_market_frame(
        harness,
        frame,
    )

    assert len(
        updated.market_frames
    ) == 1

    for lane in updated.lanes:
        assert len(
            lane.receipts
        ) == 1

        assert (
            lane.receipts[0].event_type
            == "MARKET_FRAME"
        )

        assert verify_lane_receipt_chain(
            lane
        )


def test_obsim003_experimental_trade_does_not_mutate_other_lanes():
    harness = base_harness()
    frame = option_frame()

    harness = broadcast_market_frame(
        harness,
        frame,
    )

    harness = apply_simulation_decision(
        harness,
        lane=SimulationLane.EXPERIMENTAL,
        frame=frame,
        decision_id="EXP-OPEN-001",
        action=SimulationAction.OPEN,
        strategy="LONG_CALL",
        reason="Experimental lane opens candidate trade.",
        quantity=1,
        evidence_refs=("CTX-001",),
    )

    control = lane_state(
        harness,
        SimulationLane.CONTROL,
    )

    integrated = lane_state(
        harness,
        SimulationLane.INTEGRATED,
    )

    experimental = lane_state(
        harness,
        SimulationLane.EXPERIMENTAL,
    )

    assert control.positions == ()
    assert integrated.positions == ()

    assert len(
        experimental.positions
    ) == 1

    assert len(
        experimental.trades
    ) == 1

    assert (
        experimental.positions[0].multiplier
        == 100
    )

    assert (
        experimental.trades[0].fill_price
        > frame.mark_price
    )

    assert (
        experimental.cash
        < experimental.starting_capital
    )


def test_obsim003_stock_fallback_uses_stock_multiplier_only():
    harness = base_harness()
    frame = stock_frame()

    harness = broadcast_market_frame(
        harness,
        frame,
    )

    harness = apply_simulation_decision(
        harness,
        lane=SimulationLane.INTEGRATED,
        frame=frame,
        decision_id="INT-STOCK-001",
        action=SimulationAction.OPEN,
        strategy="LONG_STOCK",
        reason="Stock fallback simulation.",
        quantity=2,
    )

    state = lane_state(
        harness,
        SimulationLane.INTEGRATED,
    )

    assert len(
        state.positions
    ) == 1

    assert (
        state.positions[0].multiplier
        == 1
    )

    assert (
        state.positions[0].instrument_kind
        == "STOCK"
    )


def test_obsim003_full_close_realizes_lane_local_pnl():
    harness = base_harness()

    first = option_frame(
        "FRAME-OPEN",
        2.00,
    )

    harness = broadcast_market_frame(
        harness,
        first,
    )

    harness = apply_simulation_decision(
        harness,
        lane="EXPERIMENTAL",
        frame=first,
        decision_id="OPEN-001",
        action="OPEN",
        strategy="LONG_CALL",
        reason="Open.",
        quantity=1,
    )

    second = option_frame(
        "FRAME-CLOSE",
        3.00,
    )

    harness = broadcast_market_frame(
        harness,
        second,
    )

    harness = apply_simulation_decision(
        harness,
        lane="EXPERIMENTAL",
        frame=second,
        decision_id="CLOSE-001",
        action="CLOSE",
        strategy="LONG_CALL",
        reason="Close.",
        quantity=1,
    )

    experimental = lane_state(
        harness,
        "EXPERIMENTAL",
    )

    control = lane_state(
        harness,
        "CONTROL",
    )

    assert experimental.positions == ()

    assert (
        experimental.realized_pnl
        > 0
    )

    assert (
        experimental.cash
        > experimental.starting_capital
    )

    assert control.trades == ()
    assert control.realized_pnl == 0.0


def test_obsim004_market_revaluation_and_drawdown_are_lane_local():
    harness = base_harness()

    first = option_frame(
        "FRAME-DD-OPEN",
        2.00,
    )

    harness = broadcast_market_frame(
        harness,
        first,
    )

    harness = apply_simulation_decision(
        harness,
        lane="EXPERIMENTAL",
        frame=first,
        decision_id="DD-OPEN",
        action="OPEN",
        strategy="LONG_CALL",
        reason="Open for drawdown test.",
        quantity=1,
    )

    lower = option_frame(
        "FRAME-DD-LOWER",
        1.00,
    )

    harness = broadcast_market_frame(
        harness,
        lower,
    )

    experimental = lane_state(
        harness,
        "EXPERIMENTAL",
    )

    control = lane_state(
        harness,
        "CONTROL",
    )

    assert (
        experimental.unrealized_pnl
        < 0
    )

    assert (
        experimental.max_drawdown_pct
        > 0
    )

    assert control.unrealized_pnl == 0.0
    assert control.max_drawdown_pct == 0.0


def test_obsim004_hold_and_review_are_recorded_without_trade():
    harness = base_harness()
    frame = option_frame()

    harness = broadcast_market_frame(
        harness,
        frame,
    )

    harness = apply_simulation_decision(
        harness,
        lane="CONTROL",
        frame=frame,
        decision_id="CONTROL-HOLD",
        action="HOLD",
        strategy="LONG_CALL",
        reason="Control stays flat.",
    )

    harness = record_simulation_review(
        harness,
        lane="CONTROL",
        review_id="REVIEW-001",
        subject_id="CONTROL-HOLD",
        note="Control retained baseline behavior.",
    )

    control = lane_state(
        harness,
        "CONTROL",
    )

    assert len(
        control.decisions
    ) == 1

    assert control.trades == ()

    assert len(
        control.review_history
    ) == 1

    assert verify_lane_receipt_chain(
        control
    )


def test_obsim004_receipt_chain_fails_on_tamper():
    harness = base_harness()
    frame = option_frame()

    harness = broadcast_market_frame(
        harness,
        frame,
    )

    experimental = lane_state(
        harness,
        "EXPERIMENTAL",
    )

    assert verify_lane_receipt_chain(
        experimental
    )

    forged_receipt = replace(
        experimental.receipts[0],
        integrity_hash="0" * 64,
    )

    forged = replace(
        experimental,
        receipts=(
            forged_receipt,
        ),
    )

    assert not verify_lane_receipt_chain(
        forged
    )


def test_obsim005_comparison_reports_metrics_without_selecting_winner():
    harness = base_harness()

    comparison = compare_simulation_lanes(
        harness
    )

    assert (
        comparison["same_starting_capital"]
        is True
    )

    assert (
        comparison["ranking_generated"]
        is False
    )

    assert (
        comparison["winner_selected"]
        is False
    )

    assert set(
        comparison["lanes"]
    ) == {
        "CONTROL",
        "INTEGRATED",
        "EXPERIMENTAL",
    }


def test_obsim005_simulation_cannot_grant_live_authority():
    contract = simulation_contract()

    assert contract[
        "simulation_only"
    ] is True

    assert contract[
        "simulation_performance_grants_live_authority"
    ] is False

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

    snapshot = harness_snapshot(
        base_harness()
    )

    assert (
        snapshot[
            "authority_boundary"
        ][
            "broker_submission"
        ]
        is False
    )


def test_obsim005_harness_is_not_a_second_execution_engine():
    import web.ob_multi_simulation_harness as module

    source = Path(
        module.__file__
    ).read_text(
        encoding="utf-8"
    )

    for forbidden in (
        "from engine.paper_broker",
        "from engine.execution_handoff",
        "from engine.execution_loop",
        "place_order(",
        "submitOrder(",
        "executeTrade(",
        "broker.submit(",
    ):
        assert forbidden not in source
