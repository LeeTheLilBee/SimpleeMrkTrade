
from __future__ import annotations

from web.ob_account_identity_truth import (
    ACCOUNT_NAMESPACE_AUTHORITY,
    ORIGIN_CLASSES,
    SCHEMA_VERSION,
    SOURCE_ROLE_TAXONOMY,
    TRUTH_STATES,
    account_identity_contract,
    account_namespace,
    classify_truth_claim,
    reconcile_truth_claims,
    resolve_account_identity,
)
from web.ob_authority_registry import (
    ACTIVE_AUTHORITY_RECORDS,
    PENDING_AUTHORITY_SLOTS,
    build_canonical_authority_registry,
    resolve_authority_reference,
)
from web.ob_owner_operating_profile import (
    ACCOUNT_REGISTRY,
)


EXPECTED_ACCOUNTS = {
    "personal",
    "trust",
    "simplee_world_business",
    "simplee_on_the_go_atm",
    "the_grounds_apartment",
    "proof_demo",
}


def test_account_namespace_reuses_owner_profile_registry_exactly():

    namespace = account_namespace()

    assert set(namespace) == EXPECTED_ACCOUNTS
    assert set(ACCOUNT_REGISTRY) == EXPECTED_ACCOUNTS

    for key in EXPECTED_ACCOUNTS:
        assert namespace[key]["key"] == key
        assert (
            namespace[key]["label"]
            ==
            ACCOUNT_REGISTRY[key]["label"]
        )

        assert (
            namespace[key]["namespace_authority"]
            ==
            "OB_OWNER_OPERATING_PROFILE_V1"
        )


def test_no_default_account_exists():

    contract = account_identity_contract()

    assert contract["implicit_default_account"] is False
    assert contract["unknown_account_fallback"] is False

    missing = resolve_account_identity(None)

    assert missing["known"] is False
    assert missing["status"] == "UNKNOWN"
    assert missing["account_key"] is None
    assert missing["implicit_default_used"] is False


def test_unknown_account_stays_unknown():

    identity = resolve_account_identity(
        "definitely_not_an_account"
    )

    assert identity["known"] is False
    assert identity["status"] == "UNKNOWN"
    assert identity["account_key"] is None
    assert (
        identity["reason"]
        ==
        "unknown_or_missing_account_identity"
    )


def test_each_known_account_is_explicitly_resolvable():

    for key in EXPECTED_ACCOUNTS:

        identity = resolve_account_identity(
            key
        )

        assert identity["known"] is True
        assert identity["status"] == "KNOWN"
        assert identity["account_key"] == key
        assert identity["implicit_default_used"] is False
        assert identity["identity_fingerprint"]


def test_proof_demo_identity_is_simulated_only():

    identity = resolve_account_identity(
        "proof_demo"
    )

    assert (
        identity["account_class"]
        ==
        "SIMULATED_PROOF_DEMO"
    )

    assert (
        identity["capital_truth_class"]
        ==
        "SIMULATED_ONLY"
    )


def test_real_mission_accounts_do_not_invent_capital_truth():

    for key in (
        EXPECTED_ACCOUNTS
        -
        {"proof_demo"}
    ):

        identity = resolve_account_identity(
            key
        )

        assert (
            identity["capital_truth_class"]
            ==
            "UNKNOWN_UNTIL_CAPITAL_AUTHORITY"
        )


def test_taxonomy_preserves_required_truth_states_and_origins():

    contract = account_identity_contract()

    assert set(contract["truth_states"]) == {
        "CURRENT",
        "UNKNOWN",
        "CONFLICT",
        "STALE",
    }

    assert "SIMULATED" in contract["origin_classes"]
    assert "OWNER_ENTERED" in contract["origin_classes"]

    assert contract["unknown_stays_unknown"] is True
    assert contract["conflict_stays_conflict"] is True
    assert contract["stale_stays_stale"] is True
    assert contract["simulated_stays_simulated"] is True
    assert contract["owner_entered_stays_owner_entered"] is True


def test_operational_repository_state_does_not_claim_live_broker_truth():

    claim = classify_truth_claim(
        account_key="trust",
        source_role="account_operational_state",
        value={
            "cash": 1000,
        },
    )

    assert claim["truth_state"] == "CURRENT"
    assert claim["origin_class"] == "REPOSITORY_STATE"
    assert claim["may_claim_live_broker_truth"] is False

    assert (
        claim["source_role_contract"][
            "may_claim_live_broker_truth"
        ]
        is False
    )


def test_projection_is_projection_and_cannot_overwrite_operational_state():

    claim = classify_truth_claim(
        account_key="personal",
        source_role="account_snapshot_projection",
        value={
            "equity": 500,
        },
    )

    assert claim["origin_class"] == "PROJECTED"

    assert (
        claim["source_role_contract"][
            "may_overwrite_operational_state"
        ]
        is False
    )


def test_historical_reporting_remains_historical():

    claim = classify_truth_claim(
        account_key="trust",
        source_role="performance_reporting",
        value={
            "realized": 50,
        },
    )

    assert claim["origin_class"] == "HISTORICAL"

    assert (
        claim["source_role_contract"][
            "may_overwrite_operational_state"
        ]
        is False
    )


def test_owner_entered_stays_owner_entered():

    claim = classify_truth_claim(
        account_key="trust",
        source_role="owner_operating_profile",
        value={
            "risk_level": "MODERATE",
        },
    )

    assert claim["truth_state"] == "CURRENT"
    assert claim["origin_class"] == "OWNER_ENTERED"


def test_simulated_stays_simulated():

    claim = classify_truth_claim(
        account_key="proof_demo",
        source_role="proof_demo_account",
        value={
            "cash": 10000,
        },
    )

    assert claim["truth_state"] == "CURRENT"
    assert claim["origin_class"] == "SIMULATED"
    assert claim["may_claim_live_broker_truth"] is False


def test_missing_value_stays_unknown():

    claim = classify_truth_claim(
        account_key="trust",
        source_role="account_operational_state",
    )

    assert claim["truth_state"] == "UNKNOWN"
    assert claim["value"] is None


def test_stale_claim_stays_stale():

    claim = classify_truth_claim(
        account_key="trust",
        source_role="account_operational_state",
        value={
            "cash": 100,
        },
        stale=True,
    )

    assert claim["truth_state"] == "STALE"
    assert claim["value"] == {
        "cash": 100,
    }


def test_explicit_conflict_stays_conflict():

    claim = classify_truth_claim(
        account_key="trust",
        source_role="account_operational_state",
        value={
            "cash": 100,
        },
        conflict=True,
    )

    assert claim["truth_state"] == "CONFLICT"
    assert claim["value"] is None


def test_unknown_source_role_does_not_get_promoted():

    claim = classify_truth_claim(
        account_key="trust",
        source_role="magic_broker_truth",
        value=999999,
    )

    assert claim["truth_state"] == "UNKNOWN"
    assert claim["origin_class"] == "UNKNOWN"
    assert claim["value"] is None


def test_agreeing_current_claims_can_resolve_without_losing_origins():

    first = classify_truth_claim(
        account_key="trust",
        source_role="account_operational_state",
        value=100,
    )

    second = classify_truth_claim(
        account_key="trust",
        source_role="account_snapshot_projection",
        value=100,
    )

    result = reconcile_truth_claims(
        [
            first,
            second,
        ]
    )

    assert result["truth_state"] == "CURRENT"
    assert result["resolved_value"] == 100
    assert result["silent_merge"] is False

    assert set(result["origin_classes"]) == {
        "REPOSITORY_STATE",
        "PROJECTED",
    }


def test_different_known_values_become_conflict_not_precedence_guess():

    first = classify_truth_claim(
        account_key="trust",
        source_role="account_operational_state",
        value=100,
    )

    second = classify_truth_claim(
        account_key="trust",
        source_role="account_snapshot_projection",
        value=99,
    )

    result = reconcile_truth_claims(
        [
            first,
            second,
        ]
    )

    assert result["truth_state"] == "CONFLICT"
    assert result["resolved_value"] is None
    assert result["reason"] == "cross_source_value_conflict"
    assert result["silent_merge"] is False


def test_unknown_claim_is_not_silently_discarded():

    known = classify_truth_claim(
        account_key="trust",
        source_role="account_operational_state",
        value=100,
    )

    unknown = classify_truth_claim(
        account_key="trust",
        source_role="account_snapshot_projection",
    )

    result = reconcile_truth_claims(
        [
            known,
            unknown,
        ]
    )

    assert result["truth_state"] == "UNKNOWN"
    assert result["resolved_value"] is None
    assert result["reason"] == "unknown_claim_preserved"


def test_stale_claim_is_not_silently_upgraded_by_matching_current_claim():

    current = classify_truth_claim(
        account_key="trust",
        source_role="account_operational_state",
        value=100,
    )

    stale = classify_truth_claim(
        account_key="trust",
        source_role="account_snapshot_projection",
        value=100,
        stale=True,
    )

    result = reconcile_truth_claims(
        [
            current,
            stale,
        ]
    )

    assert result["truth_state"] == "STALE"
    assert result["resolved_value"] == 100
    assert result["reason"] == "stale_claim_preserved"


def test_cross_account_claims_are_conflict():

    first = classify_truth_claim(
        account_key="trust",
        source_role="account_operational_state",
        value=100,
    )

    second = classify_truth_claim(
        account_key="personal",
        source_role="account_operational_state",
        value=100,
    )

    result = reconcile_truth_claims(
        [
            first,
            second,
        ]
    )

    assert result["truth_state"] == "CONFLICT"
    assert result["account_key"] is None
    assert result["reason"] == "account_identity_conflict"


def test_account_identity_authority_is_active_in_canonical_registry():

    registry = build_canonical_authority_registry()

    record = registry["authority_records"][
        "account_identity_truth_taxonomy"
    ]

    assert (
        record["authority_id"]
        ==
        "OB_ACCOUNT_IDENTITY_TRUTH_V1"
    )

    assert (
        "account_identity_truth_taxonomy"
        not in PENDING_AUTHORITY_SLOTS
    )

    assert (
        resolve_authority_reference(
            "PENDING_OBAUTH006_010"
        )["resolution"]
        ==
        "RETIRED_ALIAS"
    )

    assert (
        resolve_authority_reference(
            "PENDING_OBAUTH006_010"
        )["resolved_authority_id"]
        ==
        "OB_ACCOUNT_IDENTITY_TRUTH_V1"
    )


def test_registry_authority_grants_no_execution_or_money_capability():

    record = ACTIVE_AUTHORITY_RECORDS[
        "account_identity_truth_taxonomy"
    ]

    assert record["execution_authority"] is False
    assert record["broker_submission"] is False
    assert record["capital_movement"] is False
    assert record["automatic_contract_selection"] is False
    assert record["automatic_execution"] is False


def test_claim_and_resolution_fingerprints_are_deterministic():

    first = classify_truth_claim(
        account_key="trust",
        source_role="account_operational_state",
        value={
            "cash": 100,
        },
    )

    second = classify_truth_claim(
        account_key="trust",
        source_role="account_operational_state",
        value={
            "cash": 100,
        },
    )

    assert (
        first["claim_fingerprint"]
        ==
        second["claim_fingerprint"]
    )

    r1 = reconcile_truth_claims(
        [
            first,
        ]
    )

    r2 = reconcile_truth_claims(
        [
            second,
        ]
    )

    assert (
        r1["resolution_fingerprint"]
        ==
        r2["resolution_fingerprint"]
    )
