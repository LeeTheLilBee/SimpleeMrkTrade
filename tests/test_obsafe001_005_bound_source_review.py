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


def test_obsafe001_missing_intent_or_signal_is_hold_not_fake_green():
    inputs = fixture()
    value = build_safety_review(**inputs, signals=signals())
    assert value.state == "HOLD" and "OWNER_FIT_SOURCE_NOT_PROVIDED" in value.reasons
    assert value.order_authorized is False and value.execution_authorized is False
    without_signals = build_safety_review(**inputs)
    assert without_signals.state == "HOLD"
    assert "SAFETY_SOURCE_SIGNALS_MISSING" in without_signals.reasons
    assert verify_safety_review(value, **inputs, signals=signals())


def test_obsafe002_recompute_existing_owner_fit_and_effective_policy(tmp_path):
    inputs = fixture()
    intent = canonical_intent(tmp_path, inputs["mode_state"])
    value = build_safety_review(**inputs, intent=intent, signals=signals())
    assert value.authority == SCHEMA_VERSION
    assert value.owner_fit_fingerprint and value.effective_policy_fingerprint
    assert value.state == "REVIEW_ONLY" and value.owner_review_allowed is True
    assert value.order_authorized is False
    assert verify_safety_review(value, **inputs, intent=intent, signals=signals())
    ref = safety_review_reference(value, **inputs, intent=intent, signals=signals())
    assert ref["amounts_exposed"] is False and ref["execution_authorized"] is False


@pytest.mark.parametrize("field", (
    "overreach", "negative_dive", "overtime",
    "kill_switch_engaged", "source_conflict",
))
def test_obsafe003_adverse_source_signals_block_owner_review(field, tmp_path):
    inputs = fixture()
    intent = canonical_intent(tmp_path, inputs["mode_state"])
    alert = signals(**{field: True})
    value = build_safety_review(**inputs, intent=intent, signals=alert)
    assert value.state == "BLOCK"
    assert value.owner_review_allowed is False
    assert "DANGER:" + field.upper() in value.reasons
    assert not value.broker_submission and not value.capital_movement


def test_obsafe003_unknown_or_stale_signal_holds_without_grant(tmp_path):
    inputs = fixture()
    intent = canonical_intent(tmp_path, inputs["mode_state"])
    unknown = build_safety_review(
        **inputs, intent=intent, signals=signals(overreach=None),
    )
    assert unknown.state == "HOLD"
    assert "SAFETY_SOURCE_SIGNAL_UNKNOWN" in unknown.reasons
    stale = build_safety_review(
        **inputs, intent=intent, signals=signals(source_stale=True),
    )
    assert stale.state == "HOLD"
    assert "SAFETY_SOURCE_STALE" in stale.reasons
    with pytest.raises(ValueError, match="true/false/unknown"):
        build_safety_review(**inputs, intent=intent, signals=signals(overreach="false"))


def test_obsafe004_canonical_owner_fit_hard_stop_is_never_relabelled(tmp_path):
    inputs = fixture()
    intent = canonical_intent(tmp_path, inputs["mode_state"])
    value = build_safety_review(
        **inputs, intent=intent, signals=signals(),
        context={"estimated_loss_pct": 500.0},
    )
    assert value.state == "BLOCK"
    assert "CANONICAL_OWNER_FIT_NOT_YET" in value.reasons
    assert any(x.startswith("OWNER_FIT:") for x in value.reasons)
    assert not value.owner_review_allowed


def test_obsafe004_tampered_mode_time_strategy_and_wrong_contract_fail_closed(tmp_path):
    inputs = fixture()
    intent = canonical_intent(tmp_path, inputs["mode_state"])
    bad_mode = {**inputs, "mode_state": {**inputs["mode_state"], "mode": "MANUAL_LIVE"}}
    with pytest.raises(ValueError, match="Operating Mode|operating mode|fingerprint|locked"):
        build_safety_review(**bad_mode, signals=signals(), intent=intent)
    bad_time = {**inputs, "market_time": replace(inputs["market_time"], integrity_hash="0"*64)}
    with pytest.raises(ValueError, match="verified OBTIME"):
        build_safety_review(**bad_time, signals=signals(), intent=intent)
    bad_strategy = {**inputs, "strategy": replace(inputs["strategy"], integrity_hash="0"*64)}
    with pytest.raises(ValueError, match="OBSTRAT"):
        build_safety_review(**bad_strategy, signals=signals(), intent=intent)
    altered_intent = {**intent, "options_research": {**intent["options_research"], "ranked_contracts": []}}
    with pytest.raises(ValueError, match="selected option contract absent"):
        build_safety_review(**inputs, signals=signals(), intent=altered_intent)


def test_obsafe005_safety_receipt_is_lineage_bound_and_no_mode_unlock(tmp_path):
    inputs = fixture()
    intent = canonical_intent(tmp_path, inputs["mode_state"])
    receipt = build_safety_review(**inputs, signals=signals(), intent=intent)
    assert not verify_safety_review(
        replace(receipt, execution_authorized=True), **inputs,
        signals=signals(), intent=intent,
    )
    with pytest.raises(ValueError, match="verified full source lineage"):
        safety_review_reference(
            replace(receipt, state="BLOCK"), **inputs,
            signals=signals(), intent=intent,
        )
    c = safety_review_contract()
    assert c["no_second_policy_or_fill_engine"]
    assert c["source_hash_proves_external_authenticity"] is False
    assert c["direct_buybox_access"] is False
    for flag in ("order_authorized", "execution_authorized", "broker_submission",
                 "capital_movement", "mode_changed", "manual_live_unlock",
                 "hybrid_unlock", "automated_unlock"):
        assert c[flag] is False
