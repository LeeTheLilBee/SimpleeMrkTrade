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



from web.ob_owner_review_evidence import (
    SCHEMA_VERSION, OwnerReviewDecision, ReviewIssue,
    build_owner_review, verify_owner_review, owner_review_contract,
)


def decision(disposition="DEFER", **changes):
    fields = dict(
        decision_id="OWNER-DECISION-1", disposition=disposition,
        recorded_at_utc="2026-09-24T15:00:00+00:00",
        owner_context_ref="claimed-owner-session-r1",
        owner_assertion_hash=SOURCE_HASH,
        explicit_owner_acknowledgement=True,
        note="Owner review disposition only; no broker execution",
    )
    return OwnerReviewDecision(**{**fields, **changes})


def issue(code="NEGATIVE_DIVE", **changes):
    fields = dict(
        issue_id="OWNER-ISSUE-1", issue_code=code,
        source_ref="review-source-issue-r1",
        source_payload_hash=SOURCE_HASH,
        source_revision="r1",
        note="Source-asserted adverse review pending verification",
    )
    return ReviewIssue(**{**fields, **changes})


def chain(*, with_intent=False, tmp_path=None, alert=None):
    inputs = fixture()
    if alert is None:
        alert = signals()
    intent = canonical_intent(tmp_path, inputs["mode_state"]) if with_intent else None
    safety = build_safety_review(**inputs, signals=alert, intent=intent)
    args = arguments(inputs, safety, alert=alert, intent=intent)
    recommendation = build_recommendation_review(**args)
    return recommendation, args


def test_obrev001_no_owner_decision_is_explicit_source_hold():
    rec, args = chain()
    result = build_owner_review(rec, **args)
    assert result.authority == SCHEMA_VERSION
    assert result.state == "EVIDENCE_HOLD"
    assert result.decision is None
    assert result.recommendation_id == rec.recommendation_id
    assert result.inherited_safety_reasons == rec.reason_codes
    assert result.owner_context_tower_authenticated is False
    assert result.actual_fill_recorded is False
    assert verify_owner_review(result, rec, **args)


def test_obrev002_explicit_owner_defer_and_decline_do_not_execute(tmp_path):
    rec, args = chain(with_intent=True, tmp_path=tmp_path)
    assert rec.state == "OWNER_REVIEW_READY"
    deferred = build_owner_review(rec, **args, decision=decision())
    declined = build_owner_review(rec, **args, decision=decision("DECLINE"))
    interested = build_owner_review(rec, **args, decision=decision("INTERESTED_FOR_REVIEW"))
    assert deferred.state == "OWNER_DEFERRED"
    assert declined.state == "OWNER_DECLINED"
    assert interested.state == "OWNER_INTEREST_RECORDED"
    for item in (deferred, declined, interested):
        assert not item.execution_authorized and not item.broker_submission
        assert not item.actual_fill_recorded and not item.realized_pnl_asserted
        assert not item.owner_context_tower_authenticated
        assert verify_owner_review(
            item, rec, **args, decision=item.decision,
        )


def test_obrev002_interest_for_review_cannot_override_block_or_hold():
    rec, args = chain()
    with pytest.raises(ValueError, match="cannot override safety"):
        build_owner_review(rec, **args, decision=decision("INTERESTED_FOR_REVIEW"))
    alert = signals(overreach=True)
    blocked, blocked_args = chain(alert=alert)
    assert blocked.state == "BLOCKED"
    with pytest.raises(ValueError, match="cannot override safety"):
        build_owner_review(blocked, **blocked_args, decision=decision("INTERESTED_FOR_REVIEW"))
    stored = build_owner_review(blocked, **blocked_args, decision=decision("DECLINE"))
    assert stored.state == "SOURCE_BLOCKED"


@pytest.mark.parametrize("code", ("NEGATIVE_DIVE", "OVERTIME", "OVERREACH", "SOURCE_GAP"))
def test_obrev003_adverse_source_issues_are_review_hold_not_realized_outcome(code, tmp_path):
    rec, args = chain(with_intent=True, tmp_path=tmp_path)
    item = issue(code)
    value = build_owner_review(rec, **args, issues=(item,))
    assert value.state == "ADVERSE_REVIEW_PENDING"
    assert value.issues[0].issue_code == code
    assert value.source_issue_authenticity_verified is False
    assert not value.realized_pnl_asserted and not value.actual_fill_recorded
    assert verify_owner_review(value, rec, **args, issues=(item,))


def test_obrev004_duplicate_unknown_invalid_source_and_owner_time_fail_closed(tmp_path):
    rec, args = chain(with_intent=True, tmp_path=tmp_path)
    with pytest.raises(ValueError, match="duplicate"):
        build_owner_review(rec, **args, issues=(issue(), issue()))
    with pytest.raises(ValueError, match="canonical issue code"):
        build_owner_review(rec, **args, issues=(issue("INVENTED_PROFIT"),))
    with pytest.raises(ValueError, match="SHA-256"):
        build_owner_review(rec, **args, issues=(issue(source_payload_hash="not-hash"),))
    with pytest.raises(ValueError, match="acknowledgement"):
        build_owner_review(
            rec, **args, decision=decision(explicit_owner_acknowledgement=False),
        )
    with pytest.raises(ValueError, match="precede"):
        build_owner_review(
            rec, **args, decision=decision(recorded_at_utc="2026-09-24T13:00:00+00:00"),
        )


def test_obrev005_verified_source_replay_not_mutable_owner_grant(tmp_path):
    rec, args = chain(with_intent=True, tmp_path=tmp_path)
    owner = decision("REQUEST_MORE_EVIDENCE")
    result = build_owner_review(rec, **args, decision=owner)
    assert result == build_owner_review(rec, **args, decision=owner)
    assert not verify_owner_review(
        replace(result, execution_authorized=True), rec, **args, decision=owner,
    )
    with pytest.raises(ValueError, match="verified OBREC"):
        build_owner_review(
            replace(rec, integrity_hash="0"*64), **args, decision=owner,
        )
    contract = owner_review_contract()
    assert contract["owner_decision_is_claim_not_tower_authentication"]
    assert contract["actual_broker_fills_tracked"] is False
    assert contract["direct_buybox_access"] is False
    for flag in ("execution_authority", "broker_submission", "capital_movement",
                 "mode_changed", "manual_live_unlock", "hybrid_unlock", "automated_unlock"):
        assert contract[flag] is False
