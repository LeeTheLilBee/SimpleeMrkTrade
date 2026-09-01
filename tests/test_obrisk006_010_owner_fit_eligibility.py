from __future__ import annotations

from copy import deepcopy

import pytest

from web.ob_engine_account_authority import (
    build_authority_registry,
)
from web.ob_owner_fit_eligibility import (
    SCHEMA_VERSION as OWNER_FIT_SCHEMA_VERSION,
    evaluate_owner_fit,
    owner_fit_eligibility_contract,
)
from web.ob_owner_operating_profile import (
    activate_operating_profile,
    draft_operating_profile,
)
from web.ob_trade_intent import (
    apply_owner_fit_eligibility,
    bind_owner_operating_profile,
    create_trade_intent,
    get_trade_intent,
    manual_live_handoff_payload,
    trade_intent_contract,
    transition_trade_intent,
)


def _profile(
    tmp_path,
    *,
    growth="AGGRESSIVE_GROWTH",
    risk="MODERATE",
    account="trust",
):
    profile_db = tmp_path / "profiles.sqlite3"

    draft = draft_operating_profile(
        account,
        growth,
        risk,
    )

    return activate_operating_profile(
        "owner-solice",
        draft,
        owner_confirmed=True,
        path=profile_db,
    )["profile"]


def _contract(
    *,
    symbol="MU",
    spread_pct=0.05,
    volume=100,
    open_interest=500,
    iv=0.55,
    executable=True,
):
    row = {
        "symbol": symbol,
        "contract_symbol": f"{symbol}_RESEARCH_001",
        "option_type": "CALL",
        "strike": 100.0,
        "expiration": "2099-12-19",
        "bid": 4.75,
        "ask": 5.00,
        "spread_pct": spread_pct,
        "volume": volume,
        "open_interest": open_interest,
        "implied_volatility": iv,
        "source_backed": True,
        "current_market_truth": True,
        "is_executable": executable,
        "automatic_contract_selection": False,
        "brokerage_execution": False,
        "automatic_execution": False,
    }

    return row


def _intent(
    tmp_path,
    *,
    candidate_overrides=None,
    contracts=None,
    instrument_type="option",
    growth="AGGRESSIVE_GROWTH",
    risk="MODERATE",
):
    trade_db = tmp_path / "trade_intents.sqlite3"

    candidate = {
        "candidate_id": "cand-mu-001",
        "symbol": "MU",
        "source": "canonical_engine_feed",
        "verified": True,
        "current_eligible": True,
        "display_eligible": True,
        "projection_status": "fresh",
        "actionable_state": "ready",
        "instrument_type": instrument_type,
        "strategy": "source_backed_setup",
        "direction": "bullish",
        "score": 88.0,
        "rank": 1,
        "expected_hold_minutes": 120,
    }

    candidate.update(
        candidate_overrides
        or {}
    )

    if contracts is None:
        contracts = [_contract()]

    research = {
        "schema_version": "OB_OPTIONS_RESEARCH_V1",
        "authority": "ENGINE_RESEARCH_PROJECTION",
        "research_only": True,
        "ranked_contracts": contracts,
        "research_contracts": [],
        "options_by_symbol": {},
        "automatic_contract_selection": False,
        "brokerage_execution": False,
        "automatic_execution": False,
    }

    created = create_trade_intent(
        {
            "candidate": candidate,
            "options_research": research,
        },
        path=trade_db,
    )

    intent_id = created["intent"]["intent_id"]

    profile = _profile(
        tmp_path,
        growth=growth,
        risk=risk,
    )

    bound = bind_owner_operating_profile(
        intent_id,
        profile,
        path=trade_db,
    )

    return {
        "path": trade_db,
        "intent_id": intent_id,
        "intent": bound["intent"],
        "profile": profile,
    }


def test_contract_is_owner_review_eligibility_only():
    contract = owner_fit_eligibility_contract()

    assert contract["schema_version"] == OWNER_FIT_SCHEMA_VERSION
    assert contract["buckets"] == ["NOW", "WATCH", "NOT_YET"]
    assert contract["market_truth_mutation"] is False
    assert contract["market_score_recalculation"] is False
    assert contract["candidate_rank_recalculation"] is False
    assert contract["contract_selection"] is False
    assert contract["selection_authority"] == "OWNER"
    assert contract["execution_authority"] is False
    assert contract["broker_submission"] is False
    assert contract["capital_movement"] is False
    assert contract["automatic_execution"] is False
    assert contract["live_auto_locked"] is True
    assert contract["now_is_execution_permission"] is False


def test_evaluation_requires_explicit_bound_account(tmp_path):
    trade_db = tmp_path / "unbound.sqlite3"

    created = create_trade_intent(
        {
            "candidate": {
                "candidate_id": "unbound",
                "symbol": "MU",
                "source": "canonical_engine_feed",
            },
            "options_research": {
                "schema_version": "OB_OPTIONS_RESEARCH_V1",
                "ranked_contracts": [_contract()],
                "automatic_contract_selection": False,
                "brokerage_execution": False,
                "automatic_execution": False,
            },
        },
        path=trade_db,
    )

    with pytest.raises(ValueError, match="BOUND"):
        evaluate_owner_fit(
            created["intent"]
        )


def test_aggressive_growth_moderate_risk_is_preserved(tmp_path):
    bundle = _intent(
        tmp_path,
        growth="AGGRESSIVE_GROWTH",
        risk="MODERATE",
    )

    result = evaluate_owner_fit(
        bundle["intent"]
    )

    fit = result["owner_fit"]

    assert fit["growth_objective_ref"]["growth_key"] == "AGGRESSIVE_GROWTH"
    assert fit["risk_envelope_ref"]["risk_key"] == "MODERATE"
    assert fit["growth_context"]["risk_envelope_overridden"] is False
    assert fit["growth_context"]["expected_return_target"] is None
    assert fit["growth_context"]["market_score_recalculated"] is False


def test_passing_candidate_becomes_now_and_advances_owner_review(tmp_path):
    bundle = _intent(tmp_path)

    result = apply_owner_fit_eligibility(
        bundle["intent_id"],
        path=bundle["path"],
    )

    assert result["bucket"] == "NOW"
    assert result["eligible"] is True
    assert result["advanced_to_owner_review"] is True

    intent = result["intent"]

    assert intent["lifecycle_state"] == "OWNER_REVIEW_READY"
    assert intent["owner_fit"]["status"] == "NOW"
    assert intent["owner_fit"]["execution_authorized"] is False
    assert intent["mode_authority"]["status"] == "PENDING_OBMODE"
    assert intent["manual_live_bridge"]["ready"] is False


def test_spread_ratio_is_normalized_to_percentage_points(tmp_path):
    bundle = _intent(
        tmp_path,
        contracts=[
            _contract(
                spread_pct=0.05,
            )
        ],
    )

    result = evaluate_owner_fit(
        bundle["intent"]
    )

    contract = (
        result["owner_fit"]
        ["option_research_gate"]
        ["contracts"][0]
    )

    spread = contract["evidence"]["spread_pct"]

    assert spread["value"] == pytest.approx(5.0)
    assert spread["normalization"] == "ratio_to_percentage_points"
    assert contract["bucket"] == "NOW"


def test_wide_spread_is_not_yet_and_stays_visible_pending(tmp_path):
    bundle = _intent(
        tmp_path,
        contracts=[
            _contract(
                spread_pct=0.20,
            )
        ],
    )

    result = apply_owner_fit_eligibility(
        bundle["intent_id"],
        path=bundle["path"],
    )

    assert result["bucket"] == "NOT_YET"
    assert result["eligible"] is False
    assert result["advanced_to_owner_review"] is False
    assert result["intent"]["lifecycle_state"] == "OWNER_FIT_PENDING"
    assert (
        "NO_OPTION_RESEARCH_CONTRACT_FITS_RISK_ENVELOPE"
        in result["intent"]["owner_fit"]["hard_failure_reasons"]
    )


def test_missing_option_liquidity_evidence_is_watch_not_fake_pass(tmp_path):
    row = _contract()
    row.pop("volume")

    bundle = _intent(
        tmp_path,
        contracts=[row],
    )

    result = apply_owner_fit_eligibility(
        bundle["intent_id"],
        path=bundle["path"],
    )

    assert result["bucket"] == "WATCH"
    assert result["eligible"] is None
    assert result["intent"]["lifecycle_state"] == "OWNER_FIT_PENDING"
    assert result["intent"]["owner_fit"]["execution_authorized"] is False


def test_hold_window_cannot_exceed_selected_envelope(tmp_path):
    bundle = _intent(
        tmp_path,
        candidate_overrides={
            "expected_hold_minutes": 1000,
        },
    )

    result = apply_owner_fit_eligibility(
        bundle["intent_id"],
        path=bundle["path"],
    )

    assert result["bucket"] == "NOT_YET"
    failures = (
        result["intent"]["owner_fit"]
        ["risk_checks"]["hard_failures"]
    )
    assert "max_hold_minutes" in failures


def test_overnight_requirement_respects_owner_permission(tmp_path):
    bundle = _intent(
        tmp_path,
        candidate_overrides={
            "expected_hold_minutes": 600,
            "overnight_required": True,
        },
    )

    result = apply_owner_fit_eligibility(
        bundle["intent_id"],
        path=bundle["path"],
    )

    assert result["bucket"] == "NOT_YET"
    failures = (
        result["intent"]["owner_fit"]
        ["risk_checks"]["hard_failures"]
    )
    assert "overnight_allowed" in failures


def test_one_fitting_research_contract_is_enough_for_candidate_review_without_selection(tmp_path):
    bundle = _intent(
        tmp_path,
        contracts=[
            _contract(
                spread_pct=0.25,
            ),
            {
                **_contract(
                    spread_pct=0.05,
                ),
                "contract_symbol": "MU_RESEARCH_002",
            },
        ],
    )

    result = evaluate_owner_fit(
        bundle["intent"]
    )

    gate = result["owner_fit"]["option_research_gate"]

    assert result["bucket"] == "NOW"
    assert gate["passing_contract_count"] >= 1
    assert gate["failing_contract_count"] >= 1
    assert gate["contract_selected"] is False
    assert all(
        contract["selected"] is False
        for contract in gate["contracts"]
    )
    assert all(
        contract["selection_authority"] == "OWNER"
        for contract in gate["contracts"]
    )


def test_stock_fallback_does_not_require_option_contracts(tmp_path):
    bundle = _intent(
        tmp_path,
        contracts=[],
        instrument_type="stock",
    )

    result = evaluate_owner_fit(
        bundle["intent"]
    )

    gate = result["owner_fit"]["option_research_gate"]

    assert gate["status"] == "NOT_APPLICABLE_STOCK_FALLBACK"
    assert gate["contract_selected"] is False
    assert result["bucket"] == "NOW"


def test_quarantined_source_never_becomes_now(tmp_path):
    bundle = _intent(
        tmp_path,
        candidate_overrides={
            "source": "demo_sample_fallback",
        },
    )

    result = apply_owner_fit_eligibility(
        bundle["intent_id"],
        path=bundle["path"],
    )

    assert result["bucket"] == "NOT_YET"
    assert result["eligible"] is False
    assert any(
        reason.startswith("QUARANTINED_SOURCE_TOKEN:")
        for reason in (
            result["intent"]["owner_fit"]
            ["hard_failure_reasons"]
        )
    )


def test_owner_fit_does_not_mutate_candidate_or_market_score(tmp_path):
    bundle = _intent(tmp_path)

    before = deepcopy(
        bundle["intent"]["candidate"]
    )

    result = evaluate_owner_fit(
        bundle["intent"]
    )

    after = bundle["intent"]["candidate"]

    assert after == before
    assert result["market_truth_unchanged"] is True
    assert result["owner_fit"]["market_truth_mutated"] is False
    assert result["owner_fit"]["market_score_recalculated"] is False
    assert result["owner_fit"]["candidate_rank_recalculated"] is False
    assert (
        result["owner_fit"]["growth_context"]["canonical_candidate_score"]
        == 88.0
    )
    assert (
        result["owner_fit"]["growth_context"]["canonical_candidate_rank"]
        == 1
    )


def test_evaluation_fingerprint_is_deterministic(tmp_path):
    bundle = _intent(tmp_path)

    first = evaluate_owner_fit(
        bundle["intent"]
    )
    second = evaluate_owner_fit(
        bundle["intent"]
    )

    assert (
        first["evaluation_fingerprint"]
        == second["evaluation_fingerprint"]
    )


def test_not_yet_cannot_be_forced_to_owner_review(tmp_path):
    bundle = _intent(
        tmp_path,
        contracts=[
            _contract(
                spread_pct=0.30,
            )
        ],
    )

    applied = apply_owner_fit_eligibility(
        bundle["intent_id"],
        path=bundle["path"],
    )

    assert applied["bucket"] == "NOT_YET"

    with pytest.raises(ValueError, match="eligible"):
        transition_trade_intent(
            bundle["intent_id"],
            "OWNER_REVIEW_READY",
            reason="attempt_to_bypass_owner_fit",
            path=bundle["path"],
        )


def test_manual_live_bridge_rejects_non_now_owner_fit(tmp_path):
    bundle = _intent(
        tmp_path,
        contracts=[
            _contract(
                spread_pct=0.30,
            )
        ],
    )

    applied = apply_owner_fit_eligibility(
        bundle["intent_id"],
        path=bundle["path"],
    )

    with pytest.raises(ValueError, match="owner_fit_not_eligible_now"):
        manual_live_handoff_payload(
            applied["intent"],
            owner_id="owner-solice",
        )


def test_trade_intent_contract_points_to_real_owner_fit_authority():
    contract = trade_intent_contract()

    assert (
        contract["owner_fit_authority"]
        == "PENDING_OBRISK"
    )
    assert (
        contract["owner_fit_eligibility_authority"]
        == OWNER_FIT_SCHEMA_VERSION
    )
    assert contract["mode_authority"] == "PENDING_OBMODE"
    assert contract["hybrid_downstream"] == "LOCKED_PENDING_OBHYB"
    assert contract["automated_downstream"] == "LOCKED_PENDING_OBAUTO"


def test_authority_registry_registers_owner_fit_without_execution():
    registry = build_authority_registry(
        {
            "canonical_engine_adapter": "This is NOT another engine",
            "options_research_contract": "OB_OPTIONS_RESEARCH_V1",
            "owner_fit_eligibility": "OB_OWNER_FIT_ELIGIBILITY_V1",
        }
    )

    owner_fit = registry["owner_fit_eligibility"]

    assert owner_fit["authority"] == OWNER_FIT_SCHEMA_VERSION
    assert owner_fit["service_present"] is True
    assert owner_fit["market_truth_mutation"] is False
    assert owner_fit["market_score_recalculation"] is False
    assert owner_fit["automatic_contract_selection"] is False
    assert owner_fit["broker_submission"] is False
    assert owner_fit["capital_movement"] is False
    assert owner_fit["automatic_execution"] is False
    assert owner_fit["live_auto_locked"] is True


def test_execution_context_is_deferred_not_fabricated(tmp_path):
    bundle = _intent(tmp_path)

    result = evaluate_owner_fit(
        bundle["intent"]
    )

    risk_checks = result["owner_fit"]["risk_checks"]

    assert "max_loss_per_trade_pct" in (
        risk_checks["deferred_execution_context_checks"]
    )
    assert "max_position_allocation_pct" in (
        risk_checks["deferred_execution_context_checks"]
    )
    assert risk_checks["execution_authorized"] is False


def test_context_can_hard_fail_position_loss_without_changing_market_truth(tmp_path):
    bundle = _intent(tmp_path)

    result = evaluate_owner_fit(
        bundle["intent"],
        context={
            "estimated_loss_pct": 1.5,
        },
    )

    assert result["bucket"] == "NOT_YET"
    assert "max_loss_per_trade_pct" in (
        result["owner_fit"]["risk_checks"]["hard_failures"]
    )
    assert result["owner_fit"]["market_truth_mutated"] is False
