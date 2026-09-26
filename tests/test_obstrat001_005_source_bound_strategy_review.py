from dataclasses import replace
from datetime import datetime, timezone

import pytest

from web.ob_multi_simulation_harness import (
    SimulationLane as Lane, create_multi_simulation_harness,
    build_simulation_instrument, build_market_frame, broadcast_market_frame,
)
from web.ob_position_truth import build_simulated_position_snapshot
from web.ob_portfolio_view import build_portfolio_comparison
from web.ob_strategy_review import (
    SCHEMA_VERSION, StrategyCandidate, build_strategy_review,
    verify_strategy_review, strategy_review_contract,
)

OPTION = build_simulation_instrument(
    symbol="AAPL", instrument_kind="OPTION", contract_id="AAPL-20261218-C-250",
)
STOCK = build_simulation_instrument(symbol="MSFT", instrument_kind="STOCK")


def setup():
    h = create_multi_simulation_harness(
        harness_id="OBSTRAT001-005", account_key="trust", starting_capital=10000.,
        control_ref="CONTROL-FROZEN", integrated_ref="INTEGRATED-ACCEPTED",
        experimental_ref="EXPERIMENTAL-CANDIDATE",
    )
    for idx, inst in enumerate((OPTION, STOCK)):
        f = build_market_frame(
            frame_id="FRAME-"+str(idx),
            observed_at=datetime(2026, 9, 26, 16, idx*5, tzinfo=timezone.utc).isoformat(),
            instrument=inst, mark_price=5.0 if idx == 0 else 100.0,
            source_reference="HISTORICAL-REVIEW-"+str(idx),
        )
        h = broadcast_market_frame(h, f)
    sources = tuple(build_simulated_position_snapshot(h, lane=lane) for lane in Lane)
    portfolio = build_portfolio_comparison(h, sources=sources)
    return h, sources, portfolio


def option(**kwargs):
    base = dict(
        candidate_id="OPTION-C1", lane="EXPERIMENTAL", market_frame_id="FRAME-0",
        symbol="AAPL", instrument_kind="OPTION", contract_id=OPTION.contract_id,
        strategy_label="OWNER_OPTIONS_RESEARCH",
        source_evidence_refs=("MARKET_FRAME:FRAME-0", "OPTION_RESEARCH_EXPLICIT"),
    )
    return StrategyCandidate(**{**base, **kwargs})


def stock(**kwargs):
    base = dict(
        candidate_id="STOCK-FALLBACK", lane="INTEGRATED", market_frame_id="FRAME-1",
        symbol="MSFT", instrument_kind="STOCK", contract_id=None,
        strategy_label="STOCK_FALLBACK_OWNER_REVIEW",
        source_evidence_refs=("MARKET_FRAME:FRAME-1",),
        owner_declared_stock_fallback_reason="owner specifically requested stock review",
    )
    return StrategyCandidate(**{**base, **kwargs})


def test_obstrat001_explicit_candidates_and_no_automatic_winner():
    h, sources, portfolio = setup()
    inputs = (option(), stock())
    review = build_strategy_review(
        portfolio, harness=h, sources=sources, candidates=inputs,
    )
    assert review.authority == SCHEMA_VERSION
    assert len(review.candidates) == 2
    assert review.owner_selected_candidate_id is None
    assert review.ranking_generated is False
    assert review.winner_selected_by_system is False
    assert review.trade_intent_created is False
    assert verify_strategy_review(
        review, portfolio=portfolio, harness=h, sources=sources, candidates=inputs,
    )


def test_obstrat002_owner_review_selection_is_not_trade_intent():
    h, sources, portfolio = setup()
    inputs = (option(), stock())
    with pytest.raises(ValueError, match="explicit matching confirmation"):
        build_strategy_review(
            portfolio, harness=h, sources=sources, candidates=inputs,
            owner_selected_candidate_id="OPTION-C1",
        )
    result = build_strategy_review(
        portfolio, harness=h, sources=sources, candidates=inputs,
        owner_selected_candidate_id="OPTION-C1",
        owner_confirmed_selection_for_review=True,
    )
    assert result.owner_selected_candidate_id == "OPTION-C1"
    assert not result.trade_intent_created and not result.capital_admission_granted
    assert not result.broker_submission and not result.mode_unlock
    assert not verify_strategy_review(
        replace(result, trade_intent_created=True), portfolio=portfolio,
        harness=h, sources=sources, candidates=inputs,
        owner_selected_candidate_id="OPTION-C1",
        owner_confirmed_selection_for_review=True,
    )


def test_obstrat003_option_contract_and_stock_fallback_source_required():
    h, sources, portfolio = setup()
    for bad in (option(contract_id=None), option(contract_id="WRONG-CONTRACT")):
        with pytest.raises(ValueError):
            build_strategy_review(
                portfolio, harness=h, sources=sources, candidates=(bad,),
            )
    with pytest.raises(ValueError, match="STOCK fallback"):
        build_strategy_review(
            portfolio, harness=h, sources=sources,
            candidates=(stock(owner_declared_stock_fallback_reason=None),),
        )
    with pytest.raises(ValueError, match="source"):
        build_strategy_review(
            portfolio, harness=h, sources=sources,
            candidates=(option(source_evidence_refs=()),),
        )


def test_obstrat004_missing_market_frame_cross_lane_and_duplicate_fail_closed():
    h, sources, portfolio = setup()
    for bad in (option(market_frame_id="NOT-EXISTING"), option(lane="NONEXISTENT")):
        with pytest.raises(ValueError):
            build_strategy_review(
                portfolio, harness=h, sources=sources, candidates=(bad,),
            )
    with pytest.raises(ValueError, match="unique"):
        build_strategy_review(
            portfolio, harness=h, sources=sources, candidates=(option(), option()),
        )
    with pytest.raises(ValueError, match="not in explicit"):
        build_strategy_review(
            portfolio, harness=h, sources=sources, candidates=(option(),),
            owner_selected_candidate_id="SOME-OTHER-ID",
            owner_confirmed_selection_for_review=True,
        )


def test_obstrat005_portfolio_lineage_and_nonexecuting_contract():
    h, sources, portfolio = setup()
    tampered = replace(portfolio, integrity_hash="0"*64)
    with pytest.raises(ValueError, match="OBPORT"):
        build_strategy_review(
            tampered, harness=h, sources=sources, candidates=(option(),),
        )
    c = strategy_review_contract()
    assert c["explicit_owner_choice_for_review_only"]
    assert c["option_contract_must_be_explicit"]
    assert c["stock_fallback_requires_owner_declared_reason"]
    assert c["direct_buybox_access"] is False
    for flag in ("ranking_generated", "automatic_selection", "trade_intent_created",
                 "capital_admission_granted", "broker_submission", "capital_movement",
                 "manual_live_unlock", "hybrid_unlock", "automated_unlock"):
        assert c[flag] is False
