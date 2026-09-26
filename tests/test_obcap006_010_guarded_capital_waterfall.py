from dataclasses import replace
from datetime import datetime, timedelta, timezone
from hashlib import sha256

import pytest

from web.ob_capital_truth import build_capital_observation, build_capital_snapshot
from web.ob_capital_waterfall import (
    ATM_ACCOUNT, ATM_SCOPES, SCHEMA_VERSION, SleeveIntent,
    build_atm_waterfall_plan, build_atm_waterfall_projection,
    verify_waterfall_plan, verify_atm_waterfall_projection,
    waterfall_contract, waterfall_reference,
)

NOW = datetime(2026, 9, 26, 19, 0, tzinfo=timezone.utc)
SRC = sha256(b"indicative receipt").hexdigest()
PLAN_HASH = sha256(b"owner-declared existing policy revision").hexdigest()
VALUES = {
    "total_account_value": "30000.00",
    "settled_cash": "25000.00",
    "protected_base": "5000.00",
    "protected_reserve": "2000.00",
    "committed_capital": "4000.00",
    "pending_distribution": "1000.00",
    "realized_pnl": "3000.00",
    "surplus_capital": "5000.00",
}


def intent(scope, floor, target, hwm=2800000, ratchet=None):
    return SleeveIntent(
        scope=scope, existing_protected_floor_minor=floor,
        minimum_target_minor=target, prior_high_water_minor=hwm,
        requested_floor_ratchet_minor=floor if ratchet is None else ratchet,
    )


def plan():
    return build_atm_waterfall_plan(
        intents=(
            intent(ATM_SCOPES[0], 300000, 1000000),
            intent(ATM_SCOPES[1], 500000, 1400000),
            intent(ATM_SCOPES[2], 400000, 1500000),
            intent(ATM_SCOPES[3], 600000, 1900000),
        ),
        policy_source_ref="owner-existing-capital-plan:revision-1",
        policy_source_hash=PLAN_HASH, policy_revision="1",
        owner_confirmed_intent=True,
    )


def snapshot(scope, *, amounts=None, expiry=None, role="owner_operating_profile"):
    if amounts is None:
        amounts = VALUES
    obs = tuple(build_capital_observation(
        account_key=ATM_ACCOUNT, capital_scope_ref=scope,
        metric=metric, value=amount, source_role=role,
        source_ref=scope + ":" + metric, source_revision="1",
        source_payload_hash=SRC,
        observed_at=NOW - timedelta(minutes=30),
        received_at=NOW - timedelta(minutes=29),
        expires_at=expiry or NOW + timedelta(hours=1),
    ) for metric, amount in amounts.items())
    return build_capital_snapshot(
        account_key=ATM_ACCOUNT, capital_scope_ref=scope,
        observations=obs, as_of=NOW,
    )


def four(**changes):
    return tuple(snapshot(s, **changes) for s in ATM_SCOPES)


def test_obcap006_four_sleeves_and_set2_higher_target_required():
    p = plan()
    assert verify_waterfall_plan(p)
    assert tuple(s.scope for s in p.intents) == ATM_SCOPES
    assert p.intents[2].minimum_target_minor > p.intents[0].minimum_target_minor
    assert p.intents[3].minimum_target_minor > p.intents[1].minimum_target_minor
    assert p.external_policy_authenticity_verified is False
    with pytest.raises(ValueError, match="owner confirmation"):
        build_atm_waterfall_plan(
            intents=p.intents, policy_source_ref="x", policy_source_hash=PLAN_HASH,
            policy_revision="1", owner_confirmed_intent=False,
        )
    assert not verify_waterfall_plan(replace(p, external_policy_authenticity_verified=True))
    bad = list(p.intents)
    bad[2] = replace(bad[2], minimum_target_minor=bad[0].minimum_target_minor)
    with pytest.raises(ValueError, match="Set 1/Set 2"):
        build_atm_waterfall_plan(
            intents=tuple(bad), policy_source_ref="x",
            policy_source_hash=PLAN_HASH, policy_revision="1",
            owner_confirmed_intent=True,
        )


def test_obcap007_conservative_ordering_protects_floor_committed_pending_and_no_cross_pool():
    p = plan()
    projection = build_atm_waterfall_projection(plan=p, snapshots=four())
    assert verify_atm_waterfall_projection(projection, plan=p, snapshots=four())
    assert projection.authority == SCHEMA_VERSION
    assert len(projection.sleeves) == 4
    first = projection.sleeves[0]
    assert first.state == "REVIEW_INDICATIVE"
    assert first.indicative_unallocated_minor == 1300000
    assert first.indicative_target_gap_minor == 0
    assert first.existing_protected_floor_minor == p.intents[0].existing_protected_floor_minor
    assert first.acquisition_readiness == "NOT_ASSESSED_BY_OB"
    assert first.spend_authorized is False
    assert projection.external_capital_verified is False
    assert projection.capital_movement is False


def test_obcap007_more_protective_owner_floor_ratchet_never_widens_unallocated():
    p = plan()
    higher = tuple(
        replace(s, requested_floor_ratchet_minor=s.existing_protected_floor_minor + 1000000)
        for s in p.intents
    )
    guarded = build_atm_waterfall_plan(
        intents=higher, policy_source_ref=p.policy_source_ref,
        policy_source_hash=p.policy_source_hash, policy_revision="2",
        owner_confirmed_intent=True,
    )
    before = build_atm_waterfall_projection(plan=p, snapshots=four())
    after = build_atm_waterfall_projection(plan=guarded, snapshots=four())
    assert after.sleeves[0].proposed_protected_floor_minor == 1300000
    assert after.sleeves[0].indicative_unallocated_minor < before.sleeves[0].indicative_unallocated_minor
    assert after.owner_policy_changed is False
    assert not verify_waterfall_plan(replace(p, intents=(
        replace(p.intents[0], requested_floor_ratchet_minor=299999), *p.intents[1:]
    )))


def test_obcap008_high_water_and_drawdown_are_proposals_not_adopted():
    p = plan()
    projected = build_atm_waterfall_projection(plan=p, snapshots=four())
    assert projected.sleeves[0].proposed_high_water_minor == 3000000
    assert projected.sleeves[0].indicative_drawdown_minor == 0
    down = dict(VALUES, total_account_value="23000.00")
    lowered = build_atm_waterfall_projection(plan=p, snapshots=four(amounts=down))
    assert lowered.sleeves[0].proposed_high_water_minor == 2800000
    assert lowered.sleeves[0].indicative_drawdown_minor == 500000
    assert lowered.owner_policy_changed is False


def test_obcap009_harvest_is_hypothetical_and_requires_realized_and_surplus_claims():
    p = plan()
    projected = build_atm_waterfall_projection(plan=p, snapshots=four())
    assert projected.sleeves[0].hypothetical_harvest_minor == 300000
    assert not projected.sleeves[0].spend_authorized
    no_profit = {k: v for k, v in VALUES.items() if k != "realized_pnl"}
    missing = build_atm_waterfall_projection(plan=p, snapshots=four(amounts=no_profit))
    assert missing.sleeves[0].hypothetical_harvest_minor is None
    losses = dict(VALUES, realized_pnl="-3000.00")
    negative = build_atm_waterfall_projection(plan=p, snapshots=four(amounts=losses))
    assert negative.sleeves[0].hypothetical_harvest_minor == 0
    assert negative.acquisition_readiness == "NOT_ASSESSED_BY_OB"


@pytest.mark.parametrize("field,state", [
    ("settled_cash", "UNKNOWN"),
    ("protected_base", "UNKNOWN"),
    ("committed_capital", "UNKNOWN"),
    ("pending_distribution", "UNKNOWN"),
])
def test_obcap009_missing_inputs_do_not_become_zero_or_releasable(field, state):
    amounts = {k: v for k, v in VALUES.items() if k != field}
    projection = build_atm_waterfall_projection(plan=plan(), snapshots=four(amounts=amounts))
    assert all(s.state == state and s.indicative_unallocated_minor is None
               and s.hypothetical_harvest_minor is None for s in projection.sleeves)
    assert projection.acquisition_readiness == "NOT_ASSESSED_BY_OB"


def test_obcap009_stale_conflict_and_cross_scope_fail_closed():
    p = plan()
    expired = build_atm_waterfall_projection(
        plan=p, snapshots=four(expiry=NOW - timedelta(minutes=1)))
    assert all(s.state == "STALE" and s.indicative_unallocated_minor is None
               for s in expired.sleeves)
    snaps = list(four())
    snaps[1] = snaps[0]
    with pytest.raises(ValueError, match="order/scope"):
        build_atm_waterfall_projection(plan=p, snapshots=tuple(snaps))
    tampered = list(four())
    tampered[0] = replace(tampered[0], integrity_hash="0" * 64)
    with pytest.raises(ValueError, match="integrity"):
        build_atm_waterfall_projection(plan=p, snapshots=tuple(tampered))


def test_obcap010_deterministic_hash_and_no_amount_leak_in_reference():
    p = plan()
    inputs = four()
    first = build_atm_waterfall_projection(plan=p, snapshots=inputs)
    second = build_atm_waterfall_projection(plan=p, snapshots=inputs)
    assert first == second
    assert not verify_atm_waterfall_projection(
        replace(first, acquisition_readiness="READY"), plan=p, snapshots=inputs)
    assert not verify_atm_waterfall_projection(
        replace(first, sleeves=(replace(first.sleeves[0], spend_authorized=True), *first.sleeves[1:])),
        plan=p, snapshots=inputs)
    receipt = waterfall_reference(first, plan=p, snapshots=inputs)
    assert receipt["amounts_exposed"] is False
    assert receipt["teller_readiness_required"] is True
    assert "indicative_unallocated_minor" not in receipt
    assert "hypothetical_harvest_minor" not in receipt
    contract = waterfall_contract()
    assert contract["direct_buybox_access"] is False
    assert contract["capital_movement"] is False
    assert contract["owner_policy_mutation"] is False
    assert all(contract[x] is False for x in (
        "broker_submission", "manual_live_unlock", "hybrid_unlock", "automated_unlock"))
