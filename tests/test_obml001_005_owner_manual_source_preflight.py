from dataclasses import replace

import pytest

from test_obres001_005_fail_closed_source_recovery import bundle, observation
from test_obguard001_005_distinct_source_adverse_review import signals
from web.ob_recovery_review import build_recovery_review
from web.ob_manual_live_owner_preflight import (
    SCHEMA_VERSION, ManualLiveSourceBundle, OwnerReviewPlan,
    build_owner_manual_live_preflight, verify_owner_manual_live_preflight,
    manual_live_preflight_reference, manual_live_preflight_contract,
)


def make_sources(*, alert=None, owner_fit=False, tmp_path=None, observations=()):
    original = bundle(alert=alert, with_intent=owner_fit, tmp_path=tmp_path)
    recovery = build_recovery_review(**original, observations=observations)
    return recovery, ManualLiveSourceBundle(**original, observations=observations)


def plan(recovery, bundle, **overrides):
    data = dict(
        account_key=recovery.account_key,
        candidate_id=bundle.recommendation.selected_candidate_id,
        owner_declared_purpose="MANUAL_LIVE_1_HUMAN_BROKER_REVIEW",
        owner_acknowledges_review_not_execution=True,
        owner_note="Review only; any later order is manually placed at the broker.",
    )
    return OwnerReviewPlan(**{**data, **overrides})


def test_obml001_missing_canonical_fit_and_recovery_holds_not_live():
    recovery, evidence = make_sources()
    result = build_owner_manual_live_preflight(recovery, evidence)
    assert result.authority == SCHEMA_VERSION
    assert result.status == "HOLD_UPSTREAM_OWNER_REVIEW"
    assert "TOWER_OBML_SERVER_VERIFIED_HANDOFF_NOT_IMPLEMENTED" in result.reason_codes
    assert "BROKER_ACCOUNT_AND_OPTIONS_PERMISSIONS_NOT_EXTERNALLY_VERIFIED" in result.reason_codes
    assert result.tower_server_authorization_verified is False
    assert not result.actual_owner_live_mode_enabled
    assert not result.broker_api_order_placed and not result.capital_movement
    assert verify_owner_manual_live_preflight(result, recovery, evidence)


def test_obml002_review_ready_still_requires_current_sources_and_real_tower(tmp_path):
    recovery, evidence = make_sources(owner_fit=True, tmp_path=tmp_path)
    result = build_owner_manual_live_preflight(
        recovery, evidence, owner_plan=plan(recovery, evidence),
    )
    assert evidence.recommendation.state == "OWNER_REVIEW_READY"
    assert result.status == "HOLD_SOURCE_RECONCILIATION"
    assert "RECOVERY_SOURCES_NOT_RECONCILED" in result.reason_codes
    assert result.canonical_mode == "PAPER"
    assert result.source_only_rehearsal is True
    assert not result.real_account_spendability_verified
    assert verify_owner_manual_live_preflight(
        result, recovery, evidence, owner_plan=plan(recovery, evidence),
    )


def test_obml002_two_distinct_source_restorations_still_no_trading_grant(tmp_path):
    history = (
        observation("RESTORED_ASSERTED", "r1", "2026-09-24T14:01:00+00:00"),
        observation("RESTORED_ASSERTED", "r2", "2026-09-24T14:02:00+00:00"),
    )
    recovery, evidence = make_sources(
        owner_fit=True, tmp_path=tmp_path, observations=history,
    )
    result = build_owner_manual_live_preflight(
        recovery, evidence, owner_plan=plan(recovery, evidence),
    )
    assert recovery.state == "FRESH_CANONICAL_REVALIDATION_REQUIRED"
    assert result.status == "HOLD_FRESH_REVALIDATION_TOWER_AND_BROKER"
    assert "DISTINCT_RESTORATION_CLAIMS_REQUIRE_FRESH_CANONICAL_REVALIDATION" in result.reason_codes
    assert not result.actual_broker_order_or_fill_verified


@pytest.mark.parametrize("flag", ("overreach", "negative_dive", "overtime", "kill_switch_engaged", "source_conflict"))
def test_obml003_canonical_source_danger_remains_blocked(flag):
    recovery, evidence = make_sources(alert=signals(**{flag: True}))
    result = build_owner_manual_live_preflight(
        recovery, evidence, owner_plan=plan(recovery, evidence),
    )
    assert result.status == "BLOCKED_CANONICAL_SAFETY"
    assert not result.kill_switch_cleared and not result.safety_override
    assert any("CANONICAL_SAFETY_DENIAL" in code for code in result.reason_codes)


def test_obml004_owner_claim_account_or_candidate_cannot_cross_source(tmp_path):
    recovery, evidence = make_sources(owner_fit=True, tmp_path=tmp_path)
    with pytest.raises(ValueError, match="same account"):
        build_owner_manual_live_preflight(
            recovery, evidence, owner_plan=plan(recovery, evidence, account_key="personal"),
        )
    with pytest.raises(ValueError, match="exact selection"):
        build_owner_manual_live_preflight(
            recovery, evidence, owner_plan=plan(recovery, evidence, candidate_id="unknown"),
        )
    with pytest.raises(ValueError, match="acknowledgement"):
        build_owner_manual_live_preflight(
            recovery, evidence,
            owner_plan=plan(recovery, evidence, owner_acknowledges_review_not_execution=False),
        )
    with pytest.raises(ValueError, match="review-only"):
        build_owner_manual_live_preflight(
            recovery, evidence,
            owner_plan=plan(recovery, evidence, owner_declared_purpose="LIVE_AUTO"),
        )


def test_obml004_tampered_recovery_or_mode_fails_before_source_preflight():
    recovery, evidence = make_sources()
    with pytest.raises(ValueError, match="full independent OBRES"):
        build_owner_manual_live_preflight(
            replace(recovery, integrity_hash="0"*64), evidence,
        )
    changed = replace(evidence, mode_state={**evidence.mode_state, "account_key": "personal"})
    with pytest.raises(ValueError, match="OBRES"):
        build_owner_manual_live_preflight(recovery, changed)


def test_obml005_zero_grants_and_full_lineage_reference(tmp_path):
    recovery, evidence = make_sources(owner_fit=True, tmp_path=tmp_path)
    p = plan(recovery, evidence)
    receipt = build_owner_manual_live_preflight(recovery, evidence, owner_plan=p)
    assert receipt == build_owner_manual_live_preflight(recovery, evidence, owner_plan=p)
    ref = manual_live_preflight_reference(receipt, recovery, evidence, owner_plan=p)
    assert ref["amounts_exposed"] is False and ref["tower_authorization_required"] is True
    assert ref["real_manual_live_enabled"] is False
    for field in (
        "tower_server_authorization_verified", "tower_owner_session_authenticated",
        "tower_purpose_bound_step_up_verified", "actual_broker_account_authenticated",
        "actual_broker_options_permission_verified", "actual_broker_order_or_fill_verified",
        "real_account_spendability_verified", "actual_owner_live_mode_enabled",
        "legacy_dry_run_is_production_permission", "manual_placement_recorded_as_provider_fill",
        "trade_intent_created", "broker_api_order_placed", "unattended_execution",
        "hybrid_or_automated_mode_enabled", "capital_movement", "protected_floors_released",
        "kill_switch_cleared", "safety_override", "tower_permission_mutated", "direct_buybox_access",
    ):
        assert getattr(receipt, field) is False
    assert not verify_owner_manual_live_preflight(
        replace(receipt, tower_server_authorization_verified=True), recovery, evidence, owner_plan=p,
    )
    with pytest.raises(ValueError, match="complete canonical source"):
        manual_live_preflight_reference(
            replace(receipt, status="LIVE_APPROVED"), recovery, evidence, owner_plan=p,
        )
    c = manual_live_preflight_contract()
    assert c["full_source_lineage_recomputed"] is True
    assert c["dry_run_is_not_production_permission"] is True
    assert c["owner_places_any_eventual_order_outside_ob"] is True
    for field in ("manual_live_unlock", "hybrid_unlock", "automated_unlock",
                  "broker_submission", "capital_movement", "direct_buybox_access"):
        assert c[field] is False
