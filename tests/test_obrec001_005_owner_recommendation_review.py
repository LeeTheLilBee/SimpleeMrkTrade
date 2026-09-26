from dataclasses import replace
from datetime import date, datetime
from hashlib import sha256
from zoneinfo import ZoneInfo

import pytest

from web.ob_market_time_authority import build_canonical_market_time, build_market_schedule
from web.ob_multi_simulation_harness import (
    SimulationLane as Lane, create_multi_simulation_harness,
    build_simulation_instrument, build_market_frame, broadcast_market_frame,
)
from web.ob_operating_mode import build_initial_mode_state
from web.ob_owner_operating_profile import activate_operating_profile, draft_operating_profile
from web.ob_trade_intent import (
    create_trade_intent, bind_owner_operating_profile, bind_operating_mode,
)
from web.ob_position_truth import build_simulated_position_snapshot
from web.ob_portfolio_view import build_portfolio_comparison
from web.ob_strategy_review import StrategyCandidate, build_strategy_review
from web.ob_safety_review import (
    SCHEMA_VERSION, SafetySignals, build_safety_review,
    verify_safety_review, safety_review_reference, safety_review_contract,
)

NY = ZoneInfo("America/New_York")
DAY = date(2026, 9, 24)
CONTRACT = "MU_RESEARCH_001"
SOURCE_HASH = sha256(b"owner/source asserted danger signals").hexdigest()


def fixture():
    instrument = build_simulation_instrument(
        symbol="MU", instrument_kind="OPTION", contract_id=CONTRACT,
    )
    observed = datetime(2026, 9, 24, 10, 0, tzinfo=NY)
    schedule = build_market_schedule(
        market="US_EQUITIES", exchange_timezone="America/New_York",
        trading_date=DAY, day_status="OPEN", calendar_authority="OBSAFE_TEST_CALENDAR",
        calendar_reference=DAY.isoformat(),
        calendar_payload={"date": DAY.isoformat(), "status": "OPEN"},
        premarket_open=datetime(2026, 9, 24, 4, tzinfo=NY),
        regular_open=datetime(2026, 9, 24, 9, 30, tzinfo=NY),
        regular_close=datetime(2026, 9, 24, 16, tzinfo=NY),
        after_hours_close=datetime(2026, 9, 24, 20, tzinfo=NY),
    )
    time = build_canonical_market_time(schedule=schedule, observed_at=observed)
    h = create_multi_simulation_harness(
        harness_id="OBSAFE001-005", account_key="trust", starting_capital=10000.,
        control_ref="CONTROL", integrated_ref="ACCEPTED",
        experimental_ref="DEVELOPMENT",
    )
    frame = build_market_frame(
        frame_id="F1", observed_at=observed.isoformat(), instrument=instrument,
        mark_price=5.0, underlying_price=100.0, source_reference="OBSAFE-HISTORICAL-F1",
    )
    h = broadcast_market_frame(h, frame)
    sources = tuple(build_simulated_position_snapshot(h, lane=lane) for lane in Lane)
    portfolio = build_portfolio_comparison(h, sources=sources)
    candidate = StrategyCandidate(
        candidate_id="C1", lane="EXPERIMENTAL", market_frame_id="F1",
        symbol="MU", instrument_kind="OPTION", contract_id=CONTRACT,
        strategy_label="OWNER_EXPLICIT_RESEARCH", source_evidence_refs=("F1",),
    )
    candidates = (candidate,)
    strategy = build_strategy_review(
        portfolio, harness=h, sources=sources, candidates=candidates,
        owner_selected_candidate_id="C1", owner_confirmed_selection_for_review=True,
    )
    mode = build_initial_mode_state(
        account_key="trust", mode="PAPER", owner_authorized=True,
        reason="obsafe-owner-explicit-paper-review",
    )
    return dict(strategy=strategy, portfolio=portfolio, harness=h, sources=sources,
                candidates=candidates, market_time=time, mode_state=mode)


def signals(**overrides):
    base = dict(
        source_ref="risk-signal:owner-source-r1",
        source_payload_hash=SOURCE_HASH, source_revision="r1",
        source_conflict=False, source_stale=False, overreach=False,
        negative_dive=False, overtime=False, kill_switch_engaged=False,
    )
    return SafetySignals(**{**base, **overrides})


def canonical_intent(tmp_path, mode):
    trade_db = tmp_path / "trade.sqlite3"
    profile_db = tmp_path / "profile.sqlite3"
    contract = {
        "symbol": "MU", "contract_symbol": CONTRACT, "option_type": "CALL",
        "strike": 100.0, "expiration": "2099-12-19", "bid": 4.75, "ask": 5.0,
        "spread_pct": 0.05, "volume": 100, "open_interest": 500,
        "implied_volatility": 0.55, "source_backed": True,
        "current_market_truth": True, "is_executable": True,
        "automatic_contract_selection": False, "brokerage_execution": False,
        "automatic_execution": False,
    }
    candidate = {
        "candidate_id": "cand-mu-001", "symbol": "MU", "source": "canonical_engine_feed",
        "verified": True, "current_eligible": True, "display_eligible": True,
        "projection_status": "fresh", "actionable_state": "ready",
        "instrument_type": "option", "strategy": "source_backed_setup",
        "direction": "bullish", "score": 88.0, "rank": 1,
        "expected_hold_minutes": 120,
    }
    created = create_trade_intent(
        {"candidate": candidate, "options_research": {
            "schema_version": "OB_OPTIONS_RESEARCH_V1",
            "authority": "ENGINE_RESEARCH_PROJECTION", "research_only": True,
            "ranked_contracts": [contract], "research_contracts": [],
            "options_by_symbol": {}, "automatic_contract_selection": False,
            "brokerage_execution": False, "automatic_execution": False,
        }}, path=trade_db,
    )
    intent_id = created["intent"]["intent_id"]
    profile = activate_operating_profile(
        "obsafe-owner", draft_operating_profile(
            "trust", "AGGRESSIVE_GROWTH", "MODERATE",
        ), owner_confirmed=True, path=profile_db,
    )["profile"]
    bind_owner_operating_profile(intent_id, profile, path=trade_db)
    return bind_operating_mode(intent_id, mode, path=trade_db)["intent"]



from web.ob_strategy_review import build_strategy_review
from web.ob_recommendation_review import (
    SCHEMA_VERSION, build_recommendation_review,
    verify_recommendation_review, recommendation_reference,
    recommendation_contract,
)


def arguments(inputs, safety, *, alert=None, intent=None, context=None):
    return {
        **inputs, "safety": safety,
        "signals": alert, "intent": intent, "context": context,
    }


def test_obrec001_missing_safety_source_keeps_owner_recommendation_pending():
    inputs = fixture()
    alert = signals()
    safety = build_safety_review(**inputs, signals=alert)
    packet = build_recommendation_review(**arguments(inputs, safety, alert=alert))
    assert packet.authority == SCHEMA_VERSION
    assert packet.state == "EVIDENCE_PENDING"
    assert packet.explanation_code == "CANONICAL_SAFETY_OR_EVIDENCE_HOLD"
    assert "OWNER_FIT_SOURCE_NOT_PROVIDED" in packet.reason_codes
    assert packet.owner_review_ready is False
    assert packet.selected_candidate_id == "C1"
    assert packet.candidate_cards[0].is_explicit_owner_review_selection
    assert packet.candidate_cards[0].contract_id == CONTRACT
    assert packet.candidate_cards[0].source_truth == "HISTORICAL_SIMULATION_SOURCE_NOT_BROKER"
    assert packet.broker_submission is False


def test_obrec002_overreach_denial_cannot_be_relabelled_as_recommendation():
    inputs = fixture()
    alert = signals(overreach=True)
    safety = build_safety_review(**inputs, signals=alert)
    packet = build_recommendation_review(**arguments(inputs, safety, alert=alert))
    assert packet.state == "BLOCKED"
    assert packet.explanation_code == "CANONICAL_SAFETY_DENIAL"
    assert "DANGER:OVERREACH" in packet.reason_codes
    assert not packet.owner_review_ready
    assert packet.trade_execution_permission is False
    with pytest.raises(ValueError, match="fully verified canonical OBSAFE"):
        build_recommendation_review(**arguments(inputs, safety, alert=signals()))


def test_obrec003_complete_canonical_sources_are_owner_review_only(tmp_path):
    inputs = fixture()
    intent = canonical_intent(tmp_path, inputs["mode_state"])
    alert = signals()
    safety = build_safety_review(**inputs, intent=intent, signals=alert)
    assert safety.state == "REVIEW_ONLY"
    args = arguments(inputs, safety, alert=alert, intent=intent)
    packet = build_recommendation_review(**args)
    assert packet.state == "OWNER_REVIEW_READY"
    assert packet.owner_review_ready is True
    assert packet.explanation_code == "EXPLICIT_OWNER_REVIEW_NO_EXECUTION"
    assert packet.auto_selected_contract is False
    assert packet.executable_trade_intent is False
    assert packet.trade_execution_permission is False
    assert packet.capital_movement is False
    assert verify_recommendation_review(packet, **args)
    ref = recommendation_reference(packet, **args)
    assert ref["amounts_exposed"] is False
    assert ref["trade_execution_permission"] is False


def test_obrec004_no_selection_does_not_create_one_automatically():
    inputs = fixture()
    strategy = build_strategy_review(
        inputs["portfolio"], harness=inputs["harness"], sources=inputs["sources"],
        candidates=inputs["candidates"],
    )
    inputs = {**inputs, "strategy": strategy}
    safety = build_safety_review(**inputs, signals=signals())
    packet = build_recommendation_review(**arguments(inputs, safety, alert=signals()))
    assert packet.state == "EVIDENCE_PENDING"
    assert packet.selected_candidate_id is None
    assert not packet.candidate_cards[0].is_explicit_owner_review_selection
    assert packet.ranked_by_system is False


def test_obrec004_tampered_strategy_safety_and_money_permission_rejected(tmp_path):
    inputs = fixture()
    intent = canonical_intent(tmp_path, inputs["mode_state"])
    alert = signals()
    safety = build_safety_review(**inputs, signals=alert, intent=intent)
    args = arguments(inputs, safety, alert=alert, intent=intent)
    packet = build_recommendation_review(**args)
    assert not verify_recommendation_review(
        replace(packet, trade_execution_permission=True), **args)
    assert not verify_recommendation_review(
        replace(packet, state="BLOCKED"), **args)
    with pytest.raises(ValueError, match="fully verified canonical OBSAFE"):
        build_recommendation_review(**{**args, "safety": replace(safety, integrity_hash="0"*64)})
    with pytest.raises(ValueError, match="full verified source lineage"):
        recommendation_reference(
            replace(packet, broker_submission=True), **args)


def test_obrec005_reproducible_receipt_and_no_capability_escalation(tmp_path):
    inputs = fixture()
    intent = canonical_intent(tmp_path, inputs["mode_state"])
    alert = signals()
    safety = build_safety_review(**inputs, intent=intent, signals=alert)
    args = arguments(inputs, safety, alert=alert, intent=intent)
    first = build_recommendation_review(**args)
    second = build_recommendation_review(**args)
    assert first == second and first.recommendation_id == second.recommendation_id
    c = recommendation_contract()
    assert c["source_lineage_reverified"]
    assert c["status_not_execution_grant"]
    assert c["direct_buybox_access"] is False
    assert c["teller_owns_acquisition_readiness"] is True
    for flag in ("automatic_candidate_ranking", "automatic_contract_selection",
                 "manual_live_unlock", "hybrid_unlock", "automated_unlock",
                 "broker_submission", "capital_movement", "mode_change"):
        assert c[flag] is False
