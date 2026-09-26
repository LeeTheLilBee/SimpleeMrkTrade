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



from web.ob_adverse_guard_review import (
    SCHEMA_VERSION, GuardEvidence, build_guard_review,
    verify_guard_review, guard_reference, guard_contract,
)


def guard_entry(rec, args, *, owner=None, issues=()):
    review = build_owner_review(rec, **args, decision=owner, issues=issues)
    learning = build_review_learning(
        **learning_args(rec, args, review, owner=owner, issues=issues),
    )
    return GuardEvidence(
        **{**learning_args(rec, args, review, owner=owner, issues=issues),
           "learning": learning}
    )


def test_obguard001_single_missing_source_does_not_certify_safety():
    rec, args = chain()
    evidence = (guard_entry(rec, args),)
    result = build_guard_review(evidence)
    assert result.authority == SCHEMA_VERSION
    assert result.state == "SOURCE_EVIDENCE_HOLD"
    assert not result.source_assertion_patterns
    assert result.actual_outcome_verified is False
    assert result.automatic_kill_switch_activated is False
    assert verify_guard_review(result, evidence)


def test_obguard002_two_distinct_source_payloads_emit_owner_attention_not_actuator(tmp_path):
    rec, args = chain(with_intent=True, tmp_path=tmp_path)
    i1 = issue("NEGATIVE_DIVE")
    i2 = issue("NEGATIVE_DIVE", issue_id="OWNER-ISSUE-2",
               source_ref="review-source-issue-r2",
               source_payload_hash=sha256(b"independent source incident r2").hexdigest(),
               source_revision="r2")
    d1 = decision("DEFER")
    d2 = decision("REQUEST_MORE_EVIDENCE", decision_id="OWNER-DECISION-2",
                  recorded_at_utc="2026-09-24T15:05:00+00:00")
    evidence = (
        guard_entry(rec, args, owner=d1, issues=(i1,)),
        guard_entry(rec, args, owner=d2, issues=(i2,)),
    )
    result = build_guard_review(evidence)
    assert result.state == "REPEATED_ADVERSE_SOURCE_REVIEW"
    assert len(result.source_assertion_patterns) == 1
    p = result.source_assertion_patterns[0]
    assert p.issue_code == "NEGATIVE_DIVE"
    assert p.distinct_source_payload_count == 2
    assert p.repeated_source_assertion is True
    assert p.authenticated_market_pattern is False
    assert "OWNER_REVIEW_REPEATED_DISTINCT_SOURCE_ASSERTIONS" in result.owner_attention_tasks
    assert result.policy_mutated is False and result.mode_changed is False
    assert result.broker_submission is False and result.capital_movement is False


def test_obguard003_same_payload_replayed_is_not_distinct_event(tmp_path):
    rec, args = chain(with_intent=True, tmp_path=tmp_path)
    i1 = issue("OVERTIME")
    i2 = issue("OVERTIME", issue_id="OWNER-ISSUE-2",
               source_ref="owner-copied-alert",
               source_revision="r2",
               source_payload_hash=i1.source_payload_hash)
    first = guard_entry(rec, args, owner=decision("DEFER"), issues=(i1,))
    second = guard_entry(
        rec, args, owner=decision("DECLINE", decision_id="OWNER-DECISION-2",
                                 recorded_at_utc="2026-09-24T15:05:00+00:00"),
        issues=(i2,),
    )
    result = build_guard_review((first, second))
    assert result.state == "ADVERSE_SOURCE_REVIEW"
    assert result.source_assertion_patterns[0].distinct_source_payload_count == 1
    assert not result.source_assertion_patterns[0].repeated_source_assertion


def test_obguard004_duplicate_receipt_and_owner_chronology_fail_closed(tmp_path):
    rec, args = chain(with_intent=True, tmp_path=tmp_path)
    first = guard_entry(rec, args, owner=decision("DEFER"))
    with pytest.raises(ValueError, match="duplicate owner review"):
        build_guard_review((first, first))
    second = guard_entry(rec, args, owner=decision("DECLINE", decision_id="OWNER-DECISION-2"))
    with pytest.raises(ValueError, match="strictly"):
        build_guard_review((first, second))
    with pytest.raises(ValueError, match="strictly"):
        build_guard_review((
            guard_entry(rec, args, owner=decision("DEFER",
                        recorded_at_utc="2026-09-24T15:10:00+00:00")),
            guard_entry(rec, args, owner=decision("DECLINE", decision_id="OWNER-DECISION-2",
                        recorded_at_utc="2026-09-24T15:05:00+00:00")),
        ))


def test_obguard005_tampered_learning_and_grant_flags_fail_closed(tmp_path):
    rec, args = chain(with_intent=True, tmp_path=tmp_path)
    entry = guard_entry(rec, args, owner=decision("DEFER"))
    baseline = build_guard_review((entry,))
    assert baseline == build_guard_review((entry,))
    assert not verify_guard_review(replace(baseline, automatic_kill_switch_activated=True), (entry,))
    assert not verify_guard_review(replace(baseline, state="ALL_SAFE"), (entry,))
    bad = replace(entry, learning=replace(entry.learning, integrity_hash="0"*64))
    with pytest.raises(ValueError, match="verified source-bound OBLEARN"):
        build_guard_review((bad,))
    with pytest.raises(ValueError, match="fully verified source lineage"):
        guard_reference(replace(baseline, broker_submission=True), (entry,))
    ref = guard_reference(baseline, (entry,))
    assert ref["amounts_exposed"] is False
    assert ref["automatic_kill_switch_activated"] is False
    contract = guard_contract()
    assert contract["source_assertions_not_authenticated_market_events"]
    assert contract["identical_source_replay_is_not_new_alert"]
    assert contract["no_adverse_source_is_not_proof_of_safety"]
    assert contract["direct_buybox_access"] is False
    for flag in ("automatic_kill_switch", "risk_limit_widening", "policy_mutation",
                 "mode_change", "broker_submission", "capital_movement",
                 "manual_live_unlock", "hybrid_unlock", "automated_unlock"):
        assert contract[flag] is False
