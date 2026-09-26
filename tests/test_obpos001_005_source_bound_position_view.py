from dataclasses import replace
from hashlib import sha256
from datetime import datetime, timezone

import pytest

from web.ob_multi_simulation_harness import (
    SimulationAction as Action, SimulationLane as Lane,
    build_simulation_instrument, build_market_frame,
    create_multi_simulation_harness, broadcast_market_frame,
    apply_simulation_decision, lane_state,
)
from web.ob_position_truth import (
    SCHEMA_VERSION, build_simulated_position_snapshot,
    verify_simulated_position_snapshot, repository_position_source_summary,
    position_truth_contract,
)

AT = datetime(2026, 9, 26, 16, 0, tzinfo=timezone.utc)
INST = build_simulation_instrument(
    symbol="AAPL", instrument_kind="OPTION", contract_id="AAPL-20261218-C-250",
)


def harness():
    return create_multi_simulation_harness(
        harness_id="OBPOS001-005", account_key="trust",
        starting_capital=10000.0, control_ref="FROZEN",
        integrated_ref="ACCEPTED", experimental_ref="DEVELOPMENT",
    )


def frame(frame_id="F1", mark=5.0, minute=0, instrument=INST):
    return build_market_frame(
        frame_id=frame_id,
        observed_at=datetime(2026, 9, 26, 16, minute, tzinfo=timezone.utc).isoformat(),
        instrument=instrument, mark_price=mark, source_reference="TEST-"+frame_id,
    )


def opened():
    starting = harness()
    first = frame()
    one = broadcast_market_frame(starting, first)
    two = apply_simulation_decision(
        one, lane=Lane.CONTROL, frame=first, decision_id="CTRL-OPEN",
        action=Action.OPEN, strategy="CONTROL_TEST", reason="owner-authored simulation",
        quantity=1,
    )
    return starting, two, first


def source_summary(values, *, account="trust"):
    return repository_position_source_summary(
        account_key=account, explicit_source_values=values,
        source_ref="repository-input:explicit", source_revision="r1",
        source_payload_hash=sha256(b"caller-supplied repository evidence").hexdigest(),
    )


def test_obpos001_pristine_harness_is_simulation_empty_not_live_broker_zero():
    h = harness()
    for lane in Lane:
        snapshot = build_simulated_position_snapshot(h, lane=lane)
        assert snapshot.open_positions == ()
        assert snapshot.simulation_only is True
        assert snapshot.broker_authenticated is False
        assert snapshot.account_key == "trust"
        assert snapshot.as_of_utc is None
        assert verify_simulated_position_snapshot(snapshot, h)


def test_obpos002_open_position_uses_exact_existing_canonical_fill_and_mark():
    original, h, f = opened()
    position = lane_state(h, Lane.CONTROL).positions[0]
    s = build_simulated_position_snapshot(h, lane=Lane.CONTROL)
    assert s.authority == SCHEMA_VERSION
    assert len(s.open_positions) == 1
    p = s.open_positions[0]
    assert p.position_id == position.position_id
    assert p.entry_fill_price == position.entry_price
    assert p.entry_commission == position.entry_commission
    assert p.latest_mark_price == f.mark_price
    assert p.contract_id == INST.contract_id and p.multiplier == 100
    assert p.source_truth == "OBSIM_ONLY_NOT_BROKER"
    assert s.source_cash == lane_state(h, Lane.CONTROL).cash
    assert original.market_frames == ()
    for untouched in (Lane.INTEGRATED, Lane.EXPERIMENTAL):
        assert not build_simulated_position_snapshot(h, lane=untouched).open_positions


def test_obpos002_revalue_and_closed_position_reconcile_existing_trades():
    _, h, _ = opened()
    shock = frame("SHOCK", mark=0.01, minute=5)
    marked = broadcast_market_frame(h, shock)
    snap = build_simulated_position_snapshot(marked, lane=Lane.CONTROL)
    assert snap.open_positions[0].latest_mark_price == 0.01
    assert snap.source_unrealized_pnl < 0
    closed = apply_simulation_decision(
        marked, lane=Lane.CONTROL, frame=shock, decision_id="CTRL-CLOSE",
        action=Action.CLOSE, strategy="CONTROL_TEST", reason="simulated exit", quantity=1,
    )
    final = build_simulated_position_snapshot(closed, lane=Lane.CONTROL)
    assert not final.open_positions
    assert final.source_unrealized_pnl == 0
    assert final.source_realized_pnl < 0
    assert len(final.source_trade_ids) == 2
    assert verify_simulated_position_snapshot(final, closed)


def test_obpos003_mutated_position_and_trade_fail_reconciliation_without_touching_input():
    _, h, _ = opened()
    state = lane_state(h, Lane.CONTROL)
    tampered_position = replace(state.positions[0], multiplier=1)
    altered = replace(h, lanes=(replace(state, positions=(tampered_position,)), *h.lanes[1:]))
    with pytest.raises(ValueError, match="position ID or quantity"):
        build_simulated_position_snapshot(altered, lane=Lane.CONTROL)
    mutated_trade = replace(state.trades[0], cash_effect=-1.0)
    altered_trade = replace(h, lanes=(replace(state, trades=(mutated_trade,)), *h.lanes[1:]))
    with pytest.raises(ValueError, match="OPEN fill"):
        build_simulated_position_snapshot(altered_trade, lane=Lane.CONTROL)
    assert verify_simulated_position_snapshot(
        build_simulated_position_snapshot(h, lane=Lane.CONTROL), h,
    )


def test_obpos003_receipt_corruption_fails_closed():
    _, h, _ = opened()
    state = lane_state(h, Lane.CONTROL)
    damaged = replace(state.receipts[-1], integrity_hash="0"*64)
    bad = replace(h, lanes=(replace(state, receipts=(*state.receipts[:-1], damaged)), *h.lanes[1:]))
    with pytest.raises(ValueError, match="receipt chain"):
        build_simulated_position_snapshot(bad, lane=Lane.CONTROL)


def test_obpos004_repository_explicit_store_only_not_history_synthesis():
    none = source_summary({})
    assert none["open_source_state"] == "unresolved"
    assert none["open_count"] is None
    assert none["empty_or_unreadable_means_zero"] is False
    empty = source_summary({"open_positions": [], "closed_positions": []})
    assert empty["open_source_state"] == "explicit_store" and empty["open_count"] == 0
    assert empty["position_rows_reconstructed"] is False
    only_historical = source_summary({
        "canonical_reporting_snapshot": {"ledger": [{"trade_id": "CLOSED-1"}]},
    })
    assert only_historical["open_source_state"] == "unresolved"
    assert only_historical["open_count"] is None
    assert only_historical["historical_reporting_not_open_truth"] is True
    assert only_historical["repository_not_broker_authenticated"] is True


def test_obpos004_account_identity_and_source_provenance_fail_closed():
    with pytest.raises(ValueError, match="account identity"):
        source_summary({}, account="UNKNOWN_ACCOUNT")
    with pytest.raises(ValueError, match="integrity reference"):
        repository_position_source_summary(
            account_key="trust", explicit_source_values={},
            source_ref="repo", source_revision="r1", source_payload_hash="not-a-hash",
        )


def test_obpos005_bound_snapshot_cannot_be_forged_into_execution_or_broker_truth():
    _, h, _ = opened()
    source = build_simulated_position_snapshot(h, lane=Lane.CONTROL)
    assert not verify_simulated_position_snapshot(replace(source, broker_authenticated=True), h)
    assert not verify_simulated_position_snapshot(replace(source, trading_authority=True), h)
    assert not verify_simulated_position_snapshot(replace(source, source_cash=10000000.0), h)
    assert source.snapshot_id == build_simulated_position_snapshot(h, lane=Lane.CONTROL).snapshot_id
    c = position_truth_contract()
    assert c["new_fill_engine"] is False and c["new_position_ledger"] is False
    assert c["broker_authenticated"] is False
    assert c["direct_buybox_access"] is False
    for key in ("execution_authority", "broker_submission", "capital_movement",
                "manual_live_unlock", "hybrid_unlock", "automated_unlock"):
        assert c[key] is False
