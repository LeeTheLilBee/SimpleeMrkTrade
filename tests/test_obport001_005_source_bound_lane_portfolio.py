from dataclasses import replace
from datetime import datetime, timezone

import pytest

from web.ob_multi_simulation_harness import (
    SimulationLane as Lane, SimulationAction as Action,
    create_multi_simulation_harness, build_simulation_instrument,
    build_market_frame, broadcast_market_frame, apply_simulation_decision,
)
from web.ob_position_truth import build_simulated_position_snapshot
from web.ob_portfolio_view import (
    SCHEMA_VERSION, build_portfolio_comparison,
    verify_portfolio_comparison, portfolio_reference, portfolio_contract,
)

OPTION = build_simulation_instrument(
    symbol="AAPL", instrument_kind="OPTION", contract_id="AAPL-20261218-C-250",
)
STOCK = build_simulation_instrument(symbol="MSFT", instrument_kind="STOCK")


def fresh():
    return create_multi_simulation_harness(
        harness_id="OBPORT001-005", account_key="trust", starting_capital=10000.,
        control_ref="CONTROL-FROZEN", integrated_ref="INTEGRATED-ACCEPTED",
        experimental_ref="EXPERIMENTAL-DEVELOPMENT",
    )


def frame(key, minute, instrument, mark):
    return build_market_frame(
        frame_id=key,
        observed_at=datetime(2026, 9, 26, 16, minute, tzinfo=timezone.utc).isoformat(),
        instrument=instrument, mark_price=mark, source_reference="EXPLICIT-" + key,
    )


def with_two_distinct_positions():
    h = fresh()
    first = frame("F1", 0, STOCK, 100.0)
    h = broadcast_market_frame(h, first)
    h = apply_simulation_decision(
        h, lane=Lane.CONTROL, frame=first, decision_id="CONTROL-STOCK-OPEN",
        action=Action.OPEN, strategy="TEST-STOCK", reason="explicit simulation choice",
        quantity=2,
    )
    second = frame("F2", 5, OPTION, 5.0)
    h = broadcast_market_frame(h, second)
    h = apply_simulation_decision(
        h, lane=Lane.INTEGRATED, frame=second, decision_id="INTEGRATED-OPTION-OPEN",
        action=Action.OPEN, strategy="TEST-OPTION", reason="explicit simulation choice",
        quantity=1,
    )
    return h, second


def sources(h):
    return tuple(build_simulated_position_snapshot(h, lane=lane) for lane in Lane)


def test_obport001_three_lanes_are_independent_and_not_spendable():
    h = fresh()
    s = sources(h)
    out = build_portfolio_comparison(h, sources=s)
    assert verify_portfolio_comparison(out, harness=h, sources=s)
    assert out.authority == SCHEMA_VERSION
    assert len(out.lanes) == 3
    assert all(row.position_count == 0 for row in out.lanes)
    assert all(row.simulated_cash == 10000.0 for row in out.lanes)
    assert all(not row.deployable_for_acquisition for row in out.lanes)
    assert out.winner_selected is False
    assert out.automatic_promotion is False
    assert out.broker_authenticated is False


def test_obport002_stock_and_option_exposures_use_obpos_inputs_not_new_fill_math():
    h, _ = with_two_distinct_positions()
    ss = sources(h)
    result = build_portfolio_comparison(h, sources=ss)
    control, integrated, experimental = result.lanes
    assert control.stock_position_count == 1 and control.option_position_count == 0
    assert control.stock_market_exposure == 200.0
    assert integrated.option_position_count == 1 and integrated.stock_position_count == 0
    assert integrated.option_market_exposure == 500.0
    assert experimental.position_count == 0
    assert experimental.gross_market_exposure == 0.0
    assert control.simulated_equity == round(control.simulated_cash + control.gross_market_exposure, 4)
    assert integrated.simulated_equity == round(integrated.simulated_cash + integrated.gross_market_exposure, 4)
    assert result.common_market_frame_ids == ("F1", "F2")
    assert all(row.source_truth == "OBSIM_ONLY_INDICATIVE_NOT_BROKER" for row in result.lanes)


def test_obport003_source_mark_revaluation_is_per_instrument_and_lane():
    h, _ = with_two_distinct_positions()
    mark = frame("F3", 10, OPTION, 0.01)
    marked = broadcast_market_frame(h, mark)
    out = build_portfolio_comparison(marked)
    control, integrated, experimental = out.lanes
    assert control.stock_market_exposure == 200.0
    assert integrated.option_market_exposure == 1.0
    assert integrated.simulated_unrealized_pnl < 0
    assert experimental.position_count == 0
    assert out.ranking_generated is False


def test_obport004_tampered_source_account_or_position_hash_fails_closed():
    h, _ = with_two_distinct_positions()
    ss = sources(h)
    wrong = (replace(ss[0], account_key="personal"), *ss[1:])
    with pytest.raises(ValueError, match="OBPOS verification"):
        build_portfolio_comparison(h, sources=wrong)
    mismatched = (ss[1], ss[0], ss[2])
    with pytest.raises(ValueError, match="lane order"):
        build_portfolio_comparison(h, sources=mismatched)
    out = build_portfolio_comparison(h, sources=ss)
    assert not verify_portfolio_comparison(replace(out, winner_selected=True), harness=h, sources=ss)
    assert not verify_portfolio_comparison(replace(out, lanes=(replace(out.lanes[0], deployable_for_acquisition=True),
                                                         *out.lanes[1:])), harness=h, sources=ss)


def test_obport005_reference_only_no_money_values_or_mode_unlock():
    h, _ = with_two_distinct_positions()
    ss = sources(h)
    out = build_portfolio_comparison(h, sources=ss)
    ref = portfolio_reference(out, harness=h, sources=ss)
    assert ref["amounts_exposed"] is False
    assert ref["broker_authenticated"] is False
    assert ref["teller_readiness_required"] is True
    assert "simulated_cash" not in ref and "gross_market_exposure" not in ref
    c = portfolio_contract()
    assert c["new_position_ledger"] is False
    assert c["automatic_winner_selection"] is False
    for key in ("broker_authenticated", "execution_authority", "capital_movement",
                "direct_buybox_access", "manual_live_unlock", "hybrid_unlock", "automated_unlock"):
        assert c[key] is False
