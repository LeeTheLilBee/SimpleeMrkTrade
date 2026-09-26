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



from web.ob_review_learning import (
    SCHEMA_VERSION, build_review_learning, verify_review_learning,
    learning_review_contract,
)


def learning_args(recommendation, args, review, *, owner=None, issues=()):
    return {
        **args, "review": review, "recommendation": recommendation,
        "decision": owner, "issues": issues,
    }


def test_oblearn001_no_real_outcome_remains_evidence_review_not_reward():
    rec, args = chain()
    review = build_owner_review(rec, **args)
    packet = build_review_learning(**learning_args(rec, args, review))
    assert packet.authority == SCHEMA_VERSION
    assert packet.state == "REVIEW_FEEDBACK_ONLY"
    assert "RESOLVE_CANONICAL_SAFETY_EVIDENCE" in packet.owner_review_tasks
    assert packet.actual_broker_outcome_verified is False
    assert packet.numeric_return_estimated is False
    assert packet.training_feedback_applied is False
    assert verify_review_learning(packet, **learning_args(rec, args, review))


@pytest.mark.parametrize("code,task", (
    ("NEGATIVE_DIVE", "REVIEW_NEGATIVE_DIVE"),
    ("OVERTIME", "REVIEW_OVERTIME"),
    ("OVERREACH", "REVIEW_OVERREACH"),
    ("SOURCE_GAP", "REQUEST_MISSING_SOURCE_EVIDENCE"),
))
def test_oblearn002_adverse_source_flags_create_tasks_not_policy_or_pnl(code, task, tmp_path):
    rec, args = chain(with_intent=True, tmp_path=tmp_path)
    x = issue(code)
    review = build_owner_review(rec, **args, issues=(x,))
    learning = build_review_learning(**learning_args(rec, args, review, issues=(x,)))
    assert learning.state == "ADVERSE_SOURCE_REVIEW_REQUIRED"
    assert learning.source_issue_codes == (code,)
    assert task in learning.owner_review_tasks
    assert learning.actual_broker_outcome_verified is False
    assert learning.risk_limits_widened is False
    assert learning.guardrails_relaxed is False


def test_oblearn003_explicit_owner_interest_cannot_become_positive_reward(tmp_path):
    rec, args = chain(with_intent=True, tmp_path=tmp_path)
    owner = decision("INTERESTED_FOR_REVIEW")
    review = build_owner_review(rec, **args, decision=owner)
    learning = build_review_learning(**learning_args(rec, args, review, owner=owner))
    assert learning.state == "REVIEW_FEEDBACK_ONLY"
    assert "AWAIT_AUTHENTICATED_OUTCOME_BEFORE_LEARNING" in learning.owner_review_tasks
    assert learning.training_feedback_applied is False
    assert learning.numeric_return_estimated is False
    assert learning.simulation_promoted_to_live is False
    assert verify_review_learning(
        learning, **learning_args(rec, args, review, owner=owner),
    )


def test_oblearn004_rejects_tampered_or_misbound_review_sources(tmp_path):
    rec, args = chain(with_intent=True, tmp_path=tmp_path)
    owner = decision("DEFER")
    review = build_owner_review(rec, **args, decision=owner)
    all_args = learning_args(rec, args, review, owner=owner)
    baseline = build_review_learning(**all_args)
    assert not verify_review_learning(
        replace(baseline, effective_policy_mutated=True), **all_args,
    )
    assert not verify_review_learning(
        replace(baseline, state="ACTUAL_RETURN_CERTIFIED"), **all_args,
    )
    with pytest.raises(ValueError, match="verified OBREV"):
        build_review_learning(**{**all_args, "review": replace(review, integrity_hash="0"*64)})
    assert baseline == build_review_learning(**all_args)


def test_oblearn005_review_contract_preserves_policy_and_teller_boundaries():
    c = learning_review_contract()
    assert c["review_tasks_only"] is True
    assert c["actual_broker_outcome_available"] is False
    assert c["review_notes_are_not_reward_labels"] is True
    assert c["direct_buybox_access"] is False
    assert c["teller_owns_acquisition_readiness"] is True
    for key in ("numeric_return_estimated", "new_prediction_engine", "autonomous_training",
                "effective_policy_mutation", "risk_limit_widening", "guardrail_relaxation",
                "simulation_promotion_to_live", "broker_submission", "capital_movement",
                "manual_live_unlock", "hybrid_unlock", "automated_unlock"):
        assert c[key] is False
