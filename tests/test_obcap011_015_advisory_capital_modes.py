from dataclasses import replace
from datetime import datetime, timedelta, timezone
from hashlib import sha256

import pytest

from web.ob_capital_truth import build_capital_observation, build_capital_snapshot
from web.ob_capital_waterfall import (
    ATM_ACCOUNT, ATM_SCOPES, SleeveIntent, build_atm_waterfall_plan,
    build_atm_waterfall_projection,
)
from web.ob_capital_modes import (
    MODES, SCHEMA_VERSION, CapitalModeThresholds, SleeveModeIntent,
    build_mode_review_policy, build_capital_mode_review,
    verify_mode_review_policy, verify_capital_mode_review,
    capital_mode_review_reference, capital_mode_review_contract,
)

NOW = datetime(2026, 9, 26, 21, 0, tzinfo=timezone.utc)
SRC = sha256(b"indicative capital-source fixture").hexdigest()
POLICY_HASH = sha256(b"existing owner-plan metadata only").hexdigest()
AMOUNTS = {
    "total_account_value": "30000.00",
    "settled_cash": "25000.00",
    "protected_base": "5000.00",
    "protected_reserve": "2000.00",
    "committed_capital": "4000.00",
    "pending_distribution": "1000.00",
    "realized_pnl": "3000.00",
    "surplus_capital": "5000.00",
}


def plan():
    return build_atm_waterfall_plan(
        intents=tuple(SleeveIntent(scope, floor, target, 2800000, floor)
                      for scope, floor, target in zip(ATM_SCOPES,
                          (300000, 500000, 400000, 600000),
                          (1000000, 1400000, 1500000, 1900000))),
        policy_source_ref="owner-existing-atm-capital-plan:r1",
        policy_source_hash=POLICY_HASH, policy_revision="r1",
        owner_confirmed_intent=True,
    )


def mode_policy(p, *, modes=None, thresholds=None, revision="r1"):
    return build_mode_review_policy(
        plan=p,
        thresholds=thresholds or CapitalModeThresholds(
            drawdown_watch_bps=500, drawdown_protect_bps=1200,
            recovery_exit_bps=100, minimum_hypothetical_harvest_minor=200000,
            minimum_indicative_surplus_growth_minor=500000,
            consecutive_reviews_required=2,
        ),
        sleeve_intents=tuple(SleeveModeIntent(scope, mode, "owner-review:" + scope)
                             for scope, mode in zip(ATM_SCOPES, modes or ("ACCUMULATE",)*4)),
        owner_policy_source_ref="owner-capital-mode-intent:" + revision,
        owner_policy_source_hash=POLICY_HASH,
        revision=revision, owner_confirmed_intent=True,
    )


def snaps(*, as_of=NOW, amounts=None, revision="r1"):
    amount_map = AMOUNTS if amounts is None else amounts
    return tuple(build_capital_snapshot(
        account_key=ATM_ACCOUNT, capital_scope_ref=scope, as_of=as_of,
        observations=tuple(build_capital_observation(
            account_key=ATM_ACCOUNT, capital_scope_ref=scope,
            metric=metric, value=value, source_role="owner_operating_profile",
            source_ref=scope + ":" + metric, source_revision=revision,
            source_payload_hash=SRC,
            observed_at=NOW - timedelta(minutes=30),
            received_at=NOW - timedelta(minutes=29),
            expires_at=NOW + timedelta(hours=1),
        ) for metric, value in amount_map.items())
    ) for scope in ATM_SCOPES)


def build(*, p=None, policy=None, snapshots=None, previous=None):
    p = p or plan()
    policy = policy or mode_policy(p)
    snapshots = snapshots or snaps()
    w = build_atm_waterfall_projection(plan=p, snapshots=snapshots)
    review = build_capital_mode_review(policy=policy, plan=p, waterfall=w,
                                       snapshots=snapshots, previous=previous)
    return p, policy, snapshots, w, review


def test_obcap011_six_modes_and_explicit_owner_hysteresis_thresholds():
    p = plan()
    policy = mode_policy(p)
    assert verify_mode_review_policy(policy, plan=p)
    assert set(MODES) == {"ACCUMULATE", "BALANCED_GROWTH", "PROTECT",
                          "SURPLUS_GROWTH", "HARVEST", "RECOVERY"}
    assert policy.external_policy_authenticity_verified is False
    assert not verify_mode_review_policy(replace(policy, policy_mutation=True), plan=p)
    with pytest.raises(ValueError, match="owner confirmation"):
        build_mode_review_policy(
            plan=p, thresholds=policy.thresholds, sleeve_intents=policy.sleeve_intents,
            owner_policy_source_ref="x", owner_policy_source_hash=POLICY_HASH,
            revision="r1", owner_confirmed_intent=False,
        )
    reversed_thresholds = replace(policy.thresholds, drawdown_watch_bps=1500)
    with pytest.raises(ValueError, match="thresholds"):
        mode_policy(p, thresholds=reversed_thresholds)
    one_review_threshold = replace(policy.thresholds, consecutive_reviews_required=1)
    with pytest.raises(ValueError, match="thresholds"):
        mode_policy(p, thresholds=one_review_threshold)


def test_obcap012_four_independent_modes_preserve_funding_before_harvest():
    p, policy, snapshots, waterfall, review = build()
    assert verify_capital_mode_review(review, policy=policy, plan=p,
                                      waterfall=waterfall, snapshots=snapshots)
    assert review.authority == SCHEMA_VERSION
    assert tuple(s.scope for s in review.sleeves) == ATM_SCOPES
    assert review.sleeves[0].candidate_mode == "HARVEST"
    assert tuple(s.candidate_mode for s in review.sleeves[1:]) == (
        "ACCUMULATE", "ACCUMULATE", "ACCUMULATE")
    assert all(s.review_state == "OBSERVING_HYSTERESIS" for s in review.sleeves)
    assert all(not s.activation_authorized for s in review.sleeves)
    assert review.trading_mode_changed is False
    assert review.acquisition_readiness == "NOT_ASSESSED_BY_OB"


def test_obcap013_hysteresis_requires_new_evidence_and_strictly_later_receipts():
    p, policy, snapshots, waterfall, first = build()
    later = snaps(as_of=NOW + timedelta(minutes=5))
    p, policy, later, waterfall2, repeated = build(
        p=p, policy=policy, snapshots=later, previous=first)
    assert repeated.sleeves[0].consistent_observation_streak == 1
    assert repeated.sleeves[0].review_state == "AWAITING_FRESH_SOURCE_EVIDENCE"
    assert repeated.sleeves[0].source_evidence_fingerprint == first.sleeves[0].source_evidence_fingerprint
    fresh = snaps(as_of=NOW + timedelta(minutes=10), revision="r2")
    p, policy, fresh, waterfall3, second = build(
        p=p, policy=policy, snapshots=fresh, previous=repeated)
    assert second.sleeves[0].consistent_observation_streak == 2
    assert second.sleeves[0].review_state == "CONSECUTIVE_REVIEW_CRITERION_MET"
    assert second.sleeves[0].source_evidence_fingerprint != repeated.sleeves[0].source_evidence_fingerprint
    assert all(not s.activation_authorized for s in second.sleeves)
    assert second.prior_review_id == repeated.review_id
    with pytest.raises(ValueError, match="duplicate waterfall"):
        build_capital_mode_review(policy=policy, plan=p, waterfall=waterfall,
                                  snapshots=snapshots, previous=first)
    earlier = snaps(as_of=NOW + timedelta(minutes=3))
    earlier_waterfall = build_atm_waterfall_projection(plan=p, snapshots=earlier)
    with pytest.raises(ValueError, match="chronology"):
        build_capital_mode_review(policy=policy, plan=p, waterfall=earlier_waterfall,
                                  snapshots=earlier, previous=second)


def test_obcap013_previous_receipt_and_policy_tampering_cannot_reuse_hysteresis():
    p, policy, snapshots, waterfall, first = build()
    later = snaps(as_of=NOW + timedelta(minutes=5))
    later_waterfall = build_atm_waterfall_projection(plan=p, snapshots=later)
    with pytest.raises(ValueError, match="same-policy"):
        build_capital_mode_review(policy=policy, plan=p, waterfall=later_waterfall,
                                  snapshots=later, previous=replace(first, integrity_hash="0"*64))
    other_policy = mode_policy(p, revision="r2")
    with pytest.raises(ValueError, match="same-policy"):
        build_capital_mode_review(policy=other_policy, plan=p, waterfall=later_waterfall,
                                  snapshots=later, previous=first)
    restarted = build_capital_mode_review(
        policy=other_policy, plan=p, waterfall=later_waterfall, snapshots=later)
    assert restarted.sleeves[0].consistent_observation_streak == 1


def test_obcap014_protection_escalation_is_immediate_even_without_streak():
    low = dict(AMOUNTS, total_account_value="23000.00")
    _, _, _, _, review = build(snapshots=snaps(amounts=low))
    assert all(s.candidate_mode == "PROTECT" for s in review.sleeves)
    assert all(s.review_state == "PROTECT_PRIORITY_OWNER_REVIEW" for s in review.sleeves)
    assert all("PROTECT_DRAWDOWN_THRESHOLD" in s.reasons for s in review.sleeves)
    assert not review.owner_mode_changed and not review.trading_mode_changed


def test_obcap014_watch_then_recovery_without_owner_mode_switch():
    watch = dict(AMOUNTS, total_account_value="26000.00")
    _, _, _, _, watched = build(snapshots=snaps(amounts=watch))
    assert watched.sleeves[0].candidate_mode == "PROTECT"
    assert "WATCH_DRAWDOWN_THRESHOLD" in watched.sleeves[0].reasons
    p = plan()
    policy = mode_policy(p, modes=("PROTECT",)*4)
    recovering = dict(AMOUNTS, total_account_value="27000.00")
    _, _, _, _, r = build(p=p, policy=policy, snapshots=snaps(amounts=recovering))
    assert all(s.candidate_mode == "RECOVERY" for s in r.sleeves)
    assert all(s.review_state == "OBSERVING_HYSTERESIS" for s in r.sleeves)
    assert r.owner_mode_changed is False


def test_obcap014_surplus_and_balanced_are_nonexecuting_scenarios():
    no_harvest = dict(AMOUNTS, realized_pnl="0.00", surplus_capital="0.00")
    p = plan()
    _, _, _, _, r = build(p=p, snapshots=snaps(amounts=no_harvest))
    assert r.sleeves[0].candidate_mode == "SURPLUS_GROWTH"
    high_surplus_threshold = CapitalModeThresholds(
        drawdown_watch_bps=500, drawdown_protect_bps=1200, recovery_exit_bps=100,
        minimum_hypothetical_harvest_minor=200000,
        minimum_indicative_surplus_growth_minor=2000000,
        consecutive_reviews_required=2)
    _, _, _, _, balanced = build(
        p=p, policy=mode_policy(p, thresholds=high_surplus_threshold),
        snapshots=snaps(amounts=no_harvest))
    assert balanced.sleeves[0].candidate_mode == "BALANCED_GROWTH"
    assert balanced.capital_movement is False


def test_obcap014_missing_source_does_not_forge_protect_or_funded_status():
    missing_cash = {k: v for k, v in AMOUNTS.items() if k != "settled_cash"}
    _, _, _, _, review = build(snapshots=snaps(amounts=missing_cash))
    assert all(s.candidate_mode is None for s in review.sleeves)
    assert all(s.review_state == "INSUFFICIENT_EVIDENCE" for s in review.sleeves)
    assert all(s.consistent_observation_streak == 0 for s in review.sleeves)
    assert review.acquisition_readiness == "NOT_ASSESSED_BY_OB"


def test_obcap015_immutable_bound_receipt_and_amount_free_teller_reference():
    p, policy, ss, w, review = build()
    assert not verify_capital_mode_review(
        replace(review, trading_mode_changed=True), policy=policy,
        plan=p, waterfall=w, snapshots=ss)
    assert not verify_capital_mode_review(
        replace(review, sleeves=(replace(review.sleeves[0], activation_authorized=True),
                                *review.sleeves[1:])), policy=policy,
        plan=p, waterfall=w, snapshots=ss)
    ref = capital_mode_review_reference(
        review, policy=policy, plan=p, waterfall=w, snapshots=ss)
    assert ref["amounts_exposed"] is False
    assert ref["activation_authorized"] is False
    assert "drawdown_bps" not in ref
    assert "hypothetical_harvest_minor" not in ref
    assert ref["tower_authorization_required"] is True
    c = capital_mode_review_contract()
    assert c["direct_buybox_access"] is False
    assert c["teller_owns_readiness"] is True
    assert all(c[k] is False for k in (
        "owner_mode_changed", "trading_mode_changed", "capital_movement",
        "broker_submission", "manual_live_unlock", "hybrid_unlock", "automated_unlock"))
