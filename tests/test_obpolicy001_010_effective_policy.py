
from __future__ import annotations

from copy import deepcopy

import pytest

from web.ob_authority_registry import (
    ACTIVE_AUTHORITY_RECORDS,
    PENDING_AUTHORITY_SLOTS,
    build_canonical_authority_registry,
    resolve_authority_reference,
)

from web.ob_effective_policy import (
    CAPABILITY_KEYS,
    MOST_RESTRICTIVE_PRIMITIVE,
    POLICY_SOURCE_REGISTRY,
    SCHEMA_VERSION,
    effective_policy_contract,
    explicit_owner_restriction_layer,
    owner_profile_policy_layer,
    policy_source_registry,
    product_phase_policy_layer,
    resolve_effective_policy,
    resolve_effective_policy_for_intent,
    resolve_effective_policy_for_profile,
    validate_policy_layer,
)

from web.ob_owner_fit_eligibility import (
    evaluate_owner_fit,
    owner_fit_eligibility_contract,
)

from web.ob_owner_operating_profile import (
    activate_operating_profile,
    draft_operating_profile,
    most_restrictive_limits,
)

from web.ob_trade_intent import (
    bind_owner_operating_profile,
    create_trade_intent,
)


def _profile(
    tmp_path,
    *,
    risk="MODERATE",
    growth="GROWTH",
    account="trust",
):
    db = (
        tmp_path
        / (
            "profile_"
            + account
            + "_"
            + risk.lower()
            + ".sqlite3"
        )
    )

    draft = draft_operating_profile(
        account,
        growth,
        risk,
    )

    return activate_operating_profile(
        "owner-solice",
        draft,
        owner_confirmed=True,
        path=db,
    )["profile"]


def _contract(
    symbol="AMD",
):
    return {
        "symbol":
            symbol,

        "contract_symbol":
            symbol
            + "_OBPOLICY_CALL",

        "option_type":
            "CALL",

        "strike":
            100,

        "expiration":
            "2099-12-19",

        "bid":
            4.90,

        "ask":
            5.00,

        "spread_pct":
            0.02,

        "volume":
            1000,

        "open_interest":
            2500,

        "implied_volatility":
            0.50,

        "source_backed":
            True,

        "current_market_truth":
            True,

        "is_executable":
            True,

        "automatic_contract_selection":
            False,

        "brokerage_execution":
            False,

        "automatic_execution":
            False,
    }


def _bound_intent(
    tmp_path,
    *,
    risk="MODERATE",
    account="trust",
):
    trade_db = (
        tmp_path
        / "trade_intents.sqlite3"
    )

    profile = _profile(
        tmp_path,
        risk=risk,
        account=account,
    )

    created = create_trade_intent(
        {
            "candidate": {
                "candidate_id":
                    "obpolicy-amd-001",

                "symbol":
                    "AMD",

                "source":
                    "canonical_engine_feed",

                "verified":
                    True,

                "current_eligible":
                    True,

                "display_eligible":
                    True,

                "projection_status":
                    "fresh",

                "actionable_state":
                    "ready",

                "instrument_type":
                    "option",

                "strategy":
                    "continuation",

                "direction":
                    "CALL",

                "score":
                    90.0,

                "rank":
                    1,

                "expected_hold_minutes":
                    120,
            },

            "options_research": {
                "schema_version":
                    "OB_OPTIONS_RESEARCH_V1",

                "authority":
                    "ENGINE_RESEARCH_PROJECTION",

                "ranked_contracts": [
                    _contract()
                ],

                "research_contracts":
                    [],

                "options_by_symbol":
                    {},

                "automatic_contract_selection":
                    False,

                "brokerage_execution":
                    False,

                "automatic_execution":
                    False,
            },
        },
        path=trade_db,
    )

    intent_id = (
        created[
            "intent"
        ][
            "intent_id"
        ]
    )

    bound = bind_owner_operating_profile(
        intent_id,
        profile,
        path=trade_db,
    )

    return {
        "profile":
            profile,

        "intent":
            bound[
                "intent"
            ],

        "intent_id":
            intent_id,

        "trade_db":
            trade_db,
    }


def test_policy_contract_promotes_existing_restrictive_primitive():

    contract = effective_policy_contract()

    assert (
        contract[
            "schema_version"
        ]
        ==
        "OB_EFFECTIVE_POLICY_V1"
    )

    assert (
        contract[
            "most_restrictive_primitive"
        ]
        ==
        (
            "OB_OWNER_OPERATING_PROFILE_V1."
            "most_restrictive_limits"
        )
    )

    assert (
        contract[
            "upper_bound_rule"
        ]
        ==
        "LOWER_WINS"
    )

    assert (
        contract[
            "minimum_requirement_rule"
        ]
        ==
        "HIGHER_WINS"
    )

    assert (
        contract[
            "permission_rule"
        ]
        ==
        "FALSE_WINS"
    )

    assert (
        contract[
            "missing_capability_rule"
        ]
        ==
        "DEFAULT_DENY"
    )


def test_existing_primitive_is_still_the_composition_math():

    result = most_restrictive_limits(
        {
            "max_loss_per_trade_pct":
                1.5,

            "min_option_volume":
                25,

            "overnight_allowed":
                True,
        },

        {
            "max_loss_per_trade_pct":
                0.5,

            "min_option_volume":
                250,

            "overnight_allowed":
                False,
        },
    )

    assert (
        result[
            "max_loss_per_trade_pct"
        ]
        ==
        0.5
    )

    assert (
        result[
            "min_option_volume"
        ]
        ==
        250
    )

    assert (
        result[
            "overnight_allowed"
        ]
        is False
    )


def test_policy_source_registry_has_active_and_future_sources():

    registry = policy_source_registry()

    assert (
        registry[
            "PRODUCT_PHASE_LOCK"
        ][
            "status"
        ]
        ==
        "ACTIVE"
    )

    assert (
        registry[
            "OWNER_OPERATING_PROFILE"
        ][
            "status"
        ]
        ==
        "ACTIVE"
    )

    assert (
        registry[
            "EXPLICIT_OWNER_RESTRICTION"
        ][
            "status"
        ]
        ==
        "ACTIVE"
    )

    assert (
        registry[
            "MODE_POLICY"
        ][
            "status"
        ]
        ==
        "PENDING"
    )

    assert (
        registry[
            "CAPITAL_POLICY"
        ][
            "status"
        ]
        ==
        "PENDING"
    )

    assert (
        registry[
            "SAFETY_KERNEL_POLICY"
        ][
            "status"
        ]
        ==
        "PENDING"
    )


def test_product_phase_layer_is_account_bound_and_default_deny():

    layer = product_phase_policy_layer(
        "trust"
    )

    assert (
        layer[
            "account_key"
        ]
        ==
        "trust"
    )

    assert (
        layer[
            "limits"
        ][
            "live_automation_allowed"
        ]
        is False
    )

    assert all(
        layer[
            "capabilities"
        ][
            key
        ]
        is False
        for key
        in CAPABILITY_KEYS
    )

    assert (
        layer[
            "execution_authority"
        ]
        is False
    )


def test_unknown_account_cannot_receive_policy():

    with pytest.raises(
        ValueError,
        match="known account",
    ):
        product_phase_policy_layer(
            "fake_account"
        )


def test_active_owner_profile_becomes_policy_layer(tmp_path):

    profile = _profile(
        tmp_path,
        risk="MODERATE",
    )

    layer = owner_profile_policy_layer(
        profile
    )

    assert (
        layer[
            "layer_class"
        ]
        ==
        "OWNER_OPERATING_PROFILE"
    )

    assert (
        layer[
            "account_key"
        ]
        ==
        "trust"
    )

    assert (
        layer[
            "source_ref"
        ][
            "profile_id"
        ]
        ==
        profile[
            "profile_id"
        ]
    )

    assert (
        layer[
            "owner_confirmed"
        ]
        is True
    )


def test_owner_restriction_requires_explicit_confirmation():

    with pytest.raises(
        ValueError,
        match="confirmation",
    ):
        explicit_owner_restriction_layer(
            account_key="trust",
            restriction_id="no-confirm",
            restrictions={
                "max_loss_per_trade_pct":
                    0.5,
            },
            owner_confirmed=False,
        )


def test_owner_restriction_is_nonpersistent():

    layer = explicit_owner_restriction_layer(
        account_key="trust",
        restriction_id="tighten-loss",
        restrictions={
            "max_loss_per_trade_pct":
                0.5,
        },
        owner_confirmed=True,
    )

    assert (
        layer[
            "persistent_here"
        ]
        is False
    )

    assert (
        layer[
            "source_ref"
        ][
            "adoption_persisted"
        ]
        is False
    )

    assert (
        layer[
            "source_ref"
        ][
            "future_event_authority"
        ]
        ==
        "PENDING_OBEVENT"
    )


def test_upper_bound_lower_wins_with_provenance(tmp_path):

    profile = _profile(
        tmp_path,
        risk="ELEVATED",
    )

    owner = owner_profile_policy_layer(
        profile
    )

    phase = product_phase_policy_layer(
        "trust"
    )

    restriction = explicit_owner_restriction_layer(
        account_key="trust",
        restriction_id="loss-tighten",
        restrictions={
            "max_loss_per_trade_pct":
                0.5,

            "max_position_allocation_pct":
                7.5,
        },
        owner_confirmed=True,
    )

    policy = resolve_effective_policy(
        account_key="trust",
        layers=[
            owner,
            phase,
            restriction,
        ],
    )

    assert (
        policy[
            "effective_limits"
        ][
            "max_loss_per_trade_pct"
        ]
        ==
        0.5
    )

    assert (
        policy[
            "effective_limits"
        ][
            "max_position_allocation_pct"
        ]
        ==
        7.5
    )

    resolution = (
        policy[
            "per_limit_resolution"
        ][
            "max_loss_per_trade_pct"
        ]
    )

    assert (
        resolution[
            "rule"
        ]
        ==
        "LOWER_WINS"
    )

    assert (
        restriction[
            "layer_id"
        ]
        in
        resolution[
            "winning_layer_ids"
        ]
    )


def test_minimum_requirement_higher_wins(tmp_path):

    profile = _profile(
        tmp_path,
        risk="ELEVATED",
    )

    restriction = explicit_owner_restriction_layer(
        account_key="trust",
        restriction_id="liquidity-tighten",
        restrictions={
            "min_option_volume":
                500,

            "min_open_interest":
                1500,
        },
        owner_confirmed=True,
    )

    policy = resolve_effective_policy(
        account_key="trust",
        layers=[
            owner_profile_policy_layer(
                profile
            ),
            product_phase_policy_layer(
                "trust"
            ),
            restriction,
        ],
    )

    assert (
        policy[
            "effective_limits"
        ][
            "min_option_volume"
        ]
        ==
        500
    )

    assert (
        policy[
            "effective_limits"
        ][
            "min_open_interest"
        ]
        ==
        1500
    )

    assert (
        policy[
            "per_limit_resolution"
        ][
            "min_option_volume"
        ][
            "rule"
        ]
        ==
        "HIGHER_WINS"
    )


def test_false_permission_wins(tmp_path):

    profile = _profile(
        tmp_path,
        risk="ELEVATED",
    )

    assert (
        profile[
            "risk_envelope"
        ][
            "effective_limits"
        ][
            "overnight_allowed"
        ]
        is True
    )

    restriction = explicit_owner_restriction_layer(
        account_key="trust",
        restriction_id="no-overnight",
        restrictions={
            "overnight_allowed":
                False,
        },
        owner_confirmed=True,
    )

    policy = resolve_effective_policy(
        account_key="trust",
        layers=[
            owner_profile_policy_layer(
                profile
            ),
            product_phase_policy_layer(
                "trust"
            ),
            restriction,
        ],
    )

    assert (
        policy[
            "effective_limits"
        ][
            "overnight_allowed"
        ]
        is False
    )

    assert (
        policy[
            "per_limit_resolution"
        ][
            "overnight_allowed"
        ][
            "rule"
        ]
        ==
        "FALSE_WINS"
    )


def test_looser_layer_cannot_widen_owner_profile(tmp_path):

    profile = _profile(
        tmp_path,
        risk="MODERATE",
    )

    baseline = (
        profile[
            "risk_envelope"
        ][
            "effective_limits"
        ]
    )

    restriction = explicit_owner_restriction_layer(
        account_key="trust",
        restriction_id="attempt-looser",
        restrictions={
            "max_loss_per_trade_pct":
                2.0,

            "min_option_volume":
                1,

            "overnight_allowed":
                True,
        },
        owner_confirmed=True,
    )

    policy = resolve_effective_policy(
        account_key="trust",
        layers=[
            owner_profile_policy_layer(
                profile
            ),
            product_phase_policy_layer(
                "trust"
            ),
            restriction,
        ],
    )

    assert (
        policy[
            "effective_limits"
        ][
            "max_loss_per_trade_pct"
        ]
        ==
        baseline[
            "max_loss_per_trade_pct"
        ]
    )

    assert (
        policy[
            "effective_limits"
        ][
            "min_option_volume"
        ]
        ==
        baseline[
            "min_option_volume"
        ]
    )

    assert (
        policy[
            "effective_limits"
        ][
            "overnight_allowed"
        ]
        ==
        baseline[
            "overnight_allowed"
        ]
    )

    assert (
        policy[
            "owner_profile_widened"
        ]
        is False
    )

    assert (
        policy[
            "widened_keys"
        ]
        ==
        []
    )


def test_policy_requires_exactly_one_owner_profile_baseline(tmp_path):

    profile = _profile(
        tmp_path
    )

    phase = product_phase_policy_layer(
        "trust"
    )

    with pytest.raises(
        ValueError,
        match="exactly one",
    ):
        resolve_effective_policy(
            account_key="trust",
            layers=[
                phase,
            ],
        )

    owner = owner_profile_policy_layer(
        profile
    )

    with pytest.raises(
        ValueError,
        match="exactly one",
    ):
        resolve_effective_policy(
            account_key="trust",
            layers=[
                owner,
                deepcopy(
                    owner
                ),
                phase,
            ],
        )


def test_policy_requires_exactly_one_phase_lock(tmp_path):

    profile = _profile(
        tmp_path
    )

    with pytest.raises(
        ValueError,
        match="product-phase",
    ):
        resolve_effective_policy(
            account_key="trust",
            layers=[
                owner_profile_policy_layer(
                    profile
                ),
            ],
        )


def test_policy_layers_cannot_cross_accounts(tmp_path):

    profile = _profile(
        tmp_path,
        account="trust",
    )

    owner = owner_profile_policy_layer(
        profile
    )

    wrong_phase = product_phase_policy_layer(
        "personal"
    )

    with pytest.raises(
        ValueError,
        match="cross account",
    ):
        resolve_effective_policy(
            account_key="trust",
            layers=[
                owner,
                wrong_phase,
            ],
        )


def test_policy_layer_fingerprint_detects_tampering(tmp_path):

    profile = _profile(
        tmp_path
    )

    layer = owner_profile_policy_layer(
        profile
    )

    layer[
        "limits"
    ][
        "max_loss_per_trade_pct"
    ] = 99

    with pytest.raises(
        ValueError,
        match="fingerprint",
    ):
        validate_policy_layer(
            layer
        )


def test_policy_resolution_is_order_independent(tmp_path):

    profile = _profile(
        tmp_path,
        risk="ELEVATED",
    )

    owner = owner_profile_policy_layer(
        profile
    )

    phase = product_phase_policy_layer(
        "trust"
    )

    restriction = explicit_owner_restriction_layer(
        account_key="trust",
        restriction_id="order-test",
        restrictions={
            "max_loss_per_trade_pct":
                0.75,

            "min_option_volume":
                250,
        },
        owner_confirmed=True,
    )

    first = resolve_effective_policy(
        account_key="trust",
        layers=[
            owner,
            phase,
            restriction,
        ],
    )

    second = resolve_effective_policy(
        account_key="trust",
        layers=[
            restriction,
            owner,
            phase,
        ],
    )

    assert (
        first[
            "policy_fingerprint"
        ]
        ==
        second[
            "policy_fingerprint"
        ]
    )


def test_policy_resolution_does_not_mutate_profile(tmp_path):

    profile = _profile(
        tmp_path
    )

    before = deepcopy(
        profile
    )

    resolve_effective_policy_for_profile(
        profile
    )

    assert profile == before


def test_effective_capabilities_are_default_deny(tmp_path):

    profile = _profile(
        tmp_path
    )

    policy = resolve_effective_policy_for_profile(
        profile
    )

    assert all(
        policy[
            "effective_capabilities"
        ][
            key
        ]
        is False
        for key
        in CAPABILITY_KEYS
    )

    assert (
        policy[
            "execution_authority"
        ]
        is False
    )

    assert (
        policy[
            "broker_submission"
        ]
        is False
    )

    assert (
        policy[
            "capital_movement"
        ]
        is False
    )


def test_bound_trade_intent_resolves_same_owner_profile_policy(tmp_path):

    bundle = _bound_intent(
        tmp_path,
        risk="MODERATE",
    )

    policy = resolve_effective_policy_for_intent(
        bundle[
            "intent"
        ]
    )

    expected = (
        bundle[
            "profile"
        ][
            "risk_envelope"
        ][
            "effective_limits"
        ]
    )

    assert (
        policy[
            "account_key"
        ]
        ==
        "trust"
    )

    assert (
        policy[
            "effective_limits"
        ]
        ==
        expected
    )

    assert (
        policy[
            "source_layers"
        ][0]
        or
        policy[
            "source_layers"
        ][1]
    )


def test_owner_fit_consumes_effective_policy(tmp_path):

    bundle = _bound_intent(
        tmp_path,
        risk="MODERATE",
    )

    result = evaluate_owner_fit(
        bundle[
            "intent"
        ]
    )

    fit = result[
        "owner_fit"
    ]

    policy_ref = fit[
        "effective_policy_ref"
    ]

    assert (
        policy_ref[
            "authority"
        ]
        ==
        "OB_EFFECTIVE_POLICY_V1"
    )

    assert policy_ref[
        "policy_id"
    ]

    assert policy_ref[
        "policy_fingerprint"
    ]

    assert (
        policy_ref[
            "account_key"
        ]
        ==
        "trust"
    )

    assert (
        policy_ref[
            "effective_limits"
        ]
        ==
        bundle[
            "profile"
        ][
            "risk_envelope"
        ][
            "effective_limits"
        ]
    )

    assert (
        policy_ref[
            "owner_profile_widened"
        ]
        is False
    )


def test_owner_fit_contract_names_effective_policy_authority():

    contract = (
        owner_fit_eligibility_contract()
    )

    assert (
        contract[
            "effective_policy_authority"
        ]
        ==
        "OB_EFFECTIVE_POLICY_V1"
    )

    assert (
        contract[
            "direct_profile_policy_bypass"
        ]
        is False
    )

    assert (
        contract[
            "most_restrictive_policy"
        ]
        is True
    )


def test_canonical_authority_registry_activates_effective_policy():

    registry = build_canonical_authority_registry()

    record = registry[
        "authority_records"
    ][
        "effective_policy"
    ]

    assert (
        record[
            "authority_id"
        ]
        ==
        "OB_EFFECTIVE_POLICY_V1"
    )

    assert (
        "OB_EFFECTIVE_POLICY_V1"
        in
        registry[
            "authority_records"
        ][
            "owner_fit_eligibility"
        ][
            "inputs"
        ]
    )

    assert (
        registry[
            "authority_records"
        ][
            "owner_fit_eligibility"
        ][
            "policy_inputs"
        ]
        ==
        [
            "OB_EFFECTIVE_POLICY_V1"
        ]
    )

    assert (
        "effective_policy"
        not in
        PENDING_AUTHORITY_SLOTS
    )


def test_pending_obpolicy_becomes_retired_alias():

    resolution = resolve_authority_reference(
        "PENDING_OBPOLICY"
    )

    assert (
        resolution[
            "resolution"
        ]
        ==
        "RETIRED_ALIAS"
    )

    assert (
        resolution[
            "resolved_authority_id"
        ]
        ==
        "OB_EFFECTIVE_POLICY_V1"
    )


def test_effective_policy_authority_grants_no_execution():

    record = ACTIVE_AUTHORITY_RECORDS[
        "effective_policy"
    ]

    assert (
        record[
            "execution_authority"
        ]
        is False
    )

    assert (
        record[
            "broker_submission"
        ]
        is False
    )

    assert (
        record[
            "capital_movement"
        ]
        is False
    )

    assert (
        record[
            "automatic_contract_selection"
        ]
        is False
    )

    assert (
        record[
            "automatic_execution"
        ]
        is False
    )


def test_future_policy_layers_cannot_run_early():

    for key in (
        "MODE_POLICY",
        "CAPITAL_POLICY",
        "PORTFOLIO_POLICY",
        "SAFETY_KERNEL_POLICY",
    ):

        assert (
            POLICY_SOURCE_REGISTRY[
                key
            ][
                "status"
            ]
            ==
            "PENDING"
        )

        assert (
            POLICY_SOURCE_REGISTRY[
                key
            ][
                "runtime_allowed"
            ]
            is False
        )


def test_policy_contract_does_not_claim_persistence_or_safety_kernel():

    contract = effective_policy_contract()

    assert (
        contract[
            "policy_persistence"
        ]
        is False
    )

    assert (
        contract[
            "silent_policy_mutation"
        ]
        is False
    )

    assert (
        contract[
            "policy_widening"
        ]
        is False
    )

    assert (
        contract[
            "execution_authority"
        ]
        is False
    )

    assert (
        contract[
            "live_auto_locked"
        ]
        is True
    )


def test_account_identity_proof_demo_relationship_is_taxonomy_not_dependency():

    from web.ob_account_identity_truth import (
        SOURCE_ROLE_TAXONOMY,
    )

    registry = (
        build_canonical_authority_registry()
    )

    identity_record = (
        registry[
            "authority_records"
        ][
            "account_identity_truth_taxonomy"
        ]
    )

    proof_record = (
        registry[
            "authority_records"
        ][
            "proof_demo_account"
        ]
    )

    # Account identity is structurally upstream of effective policy.
    #
    # It must NOT structurally depend on Proof/Demo, because Proof/Demo
    # legitimately depends on Owner Fit:
    #
    #   account identity
    #       ↓
    #   effective policy
    #       ↓
    #   owner fit
    #       ↓
    #   proof/demo
    #
    # Proof/Demo still remains a valid simulated source-role taxonomy label.
    assert (
        "OB_PROOF_DEMO_ACCOUNT_V1"
        not in
        identity_record[
            "inputs"
        ]
    )

    assert (
        "OB_OWNER_OPERATING_PROFILE_V1"
        in
        identity_record[
            "inputs"
        ]
    )

    assert (
        "OB_ENGINE_ACCOUNT_AUTHORITY_V1"
        in
        identity_record[
            "inputs"
        ]
    )

    assert (
        SOURCE_ROLE_TAXONOMY[
            "proof_demo_account"
        ][
            "authority"
        ]
        ==
        "OB_PROOF_DEMO_ACCOUNT_V1"
    )

    assert (
        SOURCE_ROLE_TAXONOMY[
            "proof_demo_account"
        ][
            "origin_class"
        ]
        ==
        "SIMULATED"
    )

    # Proof/Demo legitimately consumes Owner Fit.
    assert (
        "OB_OWNER_FIT_ELIGIBILITY_V1"
        in
        proof_record[
            "inputs"
        ]
    )

    assert (
        registry[
            "validation"
        ][
            "dependency_cycle_free"
        ]
        is True
    )

    assert (
        registry[
            "validation"
        ][
            "valid"
        ]
        is True
    )


def test_duplicate_nonstructural_policy_layer_id_still_fails(tmp_path):

    profile = _profile(
        tmp_path,
        risk="MODERATE",
    )

    owner = owner_profile_policy_layer(
        profile
    )

    phase = product_phase_policy_layer(
        "trust"
    )

    restriction = explicit_owner_restriction_layer(
        account_key="trust",
        restriction_id="duplicate-id-proof",
        restrictions={
            "max_loss_per_trade_pct":
                0.5,
        },
        owner_confirmed=True,
    )

    duplicate_restriction = deepcopy(
        restriction
    )

    with pytest.raises(
        ValueError,
        match="Duplicate policy layer_id",
    ):
        resolve_effective_policy(
            account_key="trust",
            layers=[
                owner,
                phase,
                restriction,
                duplicate_restriction,
            ],
        )

