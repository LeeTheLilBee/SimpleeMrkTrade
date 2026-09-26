from dataclasses import replace
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import importlib

import pytest

from web.ob_capital_truth import (
    CAPITAL_FIELDS, SCHEMA_VERSION,
    build_capital_observation, build_capital_snapshot,
    capital_truth_contract, capital_truth_reference,
    verify_capital_observation, verify_capital_snapshot,
)

AT = datetime(2026, 9, 26, 14, 0, tzinfo=timezone.utc)
OBSERVED = AT - timedelta(hours=1)
RECEIVED = AT - timedelta(minutes=55)
EXPIRY = AT + timedelta(hours=1)
SOURCE_HASH = sha256(b"source evidence bytes").hexdigest()


def claim(metric="settled_cash", value="1000.00", *, account="trust",
          scope="ACCOUNT_WIDE", role="account_operational_state",
          ref="repository:state:1", revision="1", observed=OBSERVED,
          received=RECEIVED, expiry=EXPIRY, conflict=False):
    return build_capital_observation(
        account_key=account, capital_scope_ref=scope, metric=metric,
        value=value, source_role=role, source_ref=ref,
        source_revision=revision, source_payload_hash=SOURCE_HASH,
        observed_at=observed, received_at=received, expires_at=expiry,
        explicit_conflict=conflict,
    )


def snapshot(*items, account="trust", scope="ACCOUNT_WIDE", at=AT):
    return build_capital_snapshot(
        account_key=account, capital_scope_ref=scope,
        observations=items, as_of=at,
    )


def field(state, metric):
    return next(f for f in state.fields if f.metric == metric)


def test_obcap001_registers_new_observation_authority_without_new_account_registry():
    contract = capital_truth_contract()
    assert contract["schema_version"] == SCHEMA_VERSION
    assert contract["account_authority"] == "OB_ACCOUNT_IDENTITY_TRUTH_V1"
    assert contract["money_unit"] == "INTEGER_CENTS"
    assert contract["canonical_fields"] == list(CAPITAL_FIELDS)
    assert contract["authenticated_broker_adapter_present"] is False
    assert contract["broker_verified_values_available"] is False


def test_obcap002_exact_cents_zero_distinct_from_missing_and_signed_pnl():
    zero = claim(value="0.00")
    pnl = claim("realized_pnl", "-18.47")
    unknown = claim("protected_reserve", None)
    state = snapshot(zero, pnl, unknown)
    assert verify_capital_snapshot(state)
    assert field(state, "settled_cash").value_minor_units == 0
    assert field(state, "settled_cash").state == "CURRENT"
    assert field(state, "realized_pnl").value_minor_units == -1847
    assert field(state, "protected_reserve").state == "UNKNOWN"
    assert field(state, "protected_reserve").value_minor_units is None
    assert field(state, "available_trading_capital").state == "UNKNOWN"
    assert field(state, "available_trading_capital").value_minor_units is None
    for invalid in ("1.001", "NaN", "Infinity"):
        with pytest.raises(ValueError):
            claim(value=invalid)
    for invalid in (1.2, True, "-1.00"):
        with pytest.raises(ValueError):
            claim(value=invalid)


def test_obcap003_repository_owner_projection_and_history_remain_indicative_only():
    roles = (
        "account_operational_state", "account_snapshot_projection",
        "performance_reporting", "owner_operating_profile",
    )
    for i, role in enumerate(roles):
        observation = claim(
            value="400.00", role=role,
            ref="source:" + str(i),
        )
        assert verify_capital_observation(observation)
        assert observation.external_authenticity_verified is False
        state = snapshot(observation)
        assert field(state, "settled_cash").state == "CURRENT"
        assert state.deployment_verified is False
        assert state.acquisition_readiness == "NOT_ASSESSED"
        assert capital_truth_reference(state)["amounts_exposed"] is False


def test_obcap003_fake_broker_verification_or_simulated_mission_money_rejected():
    with pytest.raises(ValueError, match="source role"):
        claim(role="BROKER_VERIFIED")
    with pytest.raises(ValueError, match="simulated"):
        claim(role="proof_demo_account")
    with pytest.raises(ValueError, match="correct explicit account"):
        claim(account="proof_demo", role="owner_operating_profile")
    demo = claim(account="proof_demo", role="proof_demo_account")
    state = snapshot(demo, account="proof_demo")
    assert field(state, "settled_cash").state == "CURRENT"
    assert state.deployment_verified is False


def test_obcap003_unknown_cross_account_and_cross_scope_fail_closed():
    with pytest.raises(ValueError, match="identity"):
        claim(account="made_up_account")
    with pytest.raises(ValueError, match="account"):
        snapshot(claim(account="trust"), account="personal")
    with pytest.raises(ValueError, match="mission scopes"):
        snapshot(claim(scope="ATM_SET_1_ACQUISITION"), scope="ATM_SET_2_OPERATIONS")
    with pytest.raises(ValueError, match="mission scopes"):
        snapshot(claim(scope="ATM_SET_1_ACQUISITION"), scope="ACCOUNT_WIDE")


def test_obcap004_conflict_stale_and_unknown_never_synthesize_spendability():
    a = claim(value="1500.00", ref="source-a")
    b = claim(value="1700.00", ref="source-b")
    state = snapshot(a, b)
    assert field(state, "settled_cash").state == "CONFLICT"
    assert field(state, "settled_cash").value_minor_units is None
    explicit = snapshot(claim(conflict=True))
    assert field(explicit, "settled_cash").state == "CONFLICT"
    stale = snapshot(claim(expiry=AT - timedelta(minutes=1)))
    assert field(stale, "settled_cash").state == "STALE"
    assert field(stale, "settled_cash").value_minor_units is None
    unknown = snapshot(claim(value=None))
    assert field(unknown, "settled_cash").state == "UNKNOWN"
    assert field(unknown, "settled_cash").value_minor_units is None
    assert all(not item.deployment_verified for item in (state, explicit, stale, unknown))


def test_obcap004_missing_all_claims_is_unknown_not_cash_zero():
    state = snapshot()
    assert len(state.fields) == len(CAPITAL_FIELDS)
    assert all(f.state == "UNKNOWN" and f.value_minor_units is None for f in state.fields)
    assert state.acquisition_readiness == "NOT_ASSESSED"


def test_obcap004_no_future_receipts_or_naive_or_retroactive_expiry():
    with pytest.raises(ValueError, match="timezone-aware"):
        claim(observed=datetime(2026, 9, 26, 12, 0))
    with pytest.raises(ValueError, match="sequence"):
        claim(expiry=OBSERVED - timedelta(seconds=1))
    with pytest.raises(ValueError, match="after requested"):
        snapshot(claim(received=AT + timedelta(seconds=1)))


def test_obcap005_deterministic_order_and_hash_bound_tamper_rejection():
    one = claim("settled_cash", "1000.00", ref="s1")
    two = claim("protected_base", "700.00", ref="s2")
    first = snapshot(one, two)
    second = snapshot(two, one)
    assert first == second
    assert first.snapshot_id == second.snapshot_id
    assert verify_capital_snapshot(first)
    assert not verify_capital_observation(replace(one, value_minor_units=999999))
    assert not verify_capital_observation(replace(one, external_authenticity_verified=True))
    assert not verify_capital_snapshot(replace(first, deployment_verified=True))
    assert not verify_capital_snapshot(replace(first, acquisition_readiness="READY"))
    assert not verify_capital_snapshot(replace(first, fields=tuple(reversed(first.fields))))


def test_obcap005_reference_contains_no_amounts_or_buybox_readiness():
    source = snapshot(claim())
    ref = capital_truth_reference(source)
    assert set(ref["metric_states"]) == set(CAPITAL_FIELDS)
    assert "value_minor_units" not in repr(ref)
    assert ref["external_authenticity_verified"] is False
    assert ref["acquisition_readiness"] == "NOT_ASSESSED"
    contract = capital_truth_contract()
    assert contract["buybox_may_consume_directly"] is False
    assert contract["ob_to_buybox_connection"] is False
    assert contract["teller_owns_financial_administration_and_readiness"] is True
    assert contract["requires_fresh_teller_readiness_on_material_deal_change"] is True
    for key in (
        "execution_authority", "broker_submission", "capital_movement",
        "policy_mutation", "manual_live_unlock", "hybrid_unlock",
        "automated_unlock",
    ):
        assert contract[key] is False


def test_obcap005_registry_is_non_circular_and_policies_unchanged():
    from web.ob_authority_registry import (
        build_canonical_authority_registry, resolve_authority_reference,
    )
    from web.ob_effective_policy import policy_source_registry
    registry = build_canonical_authority_registry()
    assert registry["validation"]["valid"]
    assert registry["validation"]["dependency_cycle_free"]
    record = registry["authority_records"]["capital_truth"]
    assert record["authority_id"] == SCHEMA_VERSION
    assert record["inputs"] == ["OB_ACCOUNT_IDENTITY_TRUTH_V1"]
    assert "OB_EFFECTIVE_POLICY_V1" not in record["inputs"]
    assert "OB_CAPITAL_POLICY_V1" not in record["inputs"]
    assert resolve_authority_reference(SCHEMA_VERSION)["resolution"] == "ACTIVE_AUTHORITY_ID"
    assert policy_source_registry()["CAPITAL_POLICY"]["source_authority"] == "OB_CAPITAL_POLICY_V1"
    assert all(key not in importlib.import_module("web.ob_capital_truth").__dict__
               for key in ("buybox_client", "teller_client", "broker_client"))
