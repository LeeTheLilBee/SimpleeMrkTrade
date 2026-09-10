from __future__ import annotations

from copy import deepcopy

import pytest

from web.ob_account_identity_truth import (
    resolve_account_identity,
)

from web.ob_authority_registry import (
    ACTIVE_AUTHORITY_RECORDS,
    PENDING_AUTHORITY_SLOTS,
    build_canonical_authority_registry,
    resolve_authority_reference,
)

from web.ob_decision_context import (
    build_decision_context,
    decision_context_contract,
    decision_context_reference,
    stable_hash,
    validate_decision_context,
)

from web.ob_effective_policy import (
    mode_policy_layer,
    resolve_effective_policy_for_intent,
)

from web.ob_owner_operating_profile import (
    activate_operating_profile,
    draft_operating_profile,
)

from web.ob_trade_intent import (
    bind_operating_mode,
    bind_owner_operating_profile,
    create_trade_intent,
    validate_trade_intent,
)

from web.ob_operating_mode import (
    build_initial_mode_state,
)


DEFERRED_CONTEXT_CONCEPTS = (
    "market_candidate_truth",
    "options_research",
    "account_reconciliation",
    "owner_operating_profile",
    "trade_intent",
    "owner_fit_eligibility",
    "proof_demo_account",
    "account_identity_truth_taxonomy",
    "effective_policy",
    "event_authority",
)


def _real_bound_inputs(tmp_path):

    candidate = {
        "candidate_id":
            "obctx_test_candidate",

        "symbol":
            "AAPL",

        "candidate_source":
            "canonical_engine",

        "as_of":
            "2026-09-10T13:30:00+00:00",

        "strategy":
            "continuation",

        "direction":
            "CALL",

        "score":
            91.25,

        "rank":
            1,

        "confidence":
            "HIGH",

        "actionable_state":
            "ready",

        "verified":
            True,

        "source_backed":
            True,
    }

    research = {
        "schema_version":
            "OB_OPTIONS_RESEARCH_V1",

        "authority":
            "ENGINE_RESEARCH_PROJECTION",

        "research_contracts":
            [],

        "ranked_contracts":
            [],

        "diagnostics": {
            "source_backed":
                True,
        },
    }

    trade_db = (
        tmp_path
        / "obctx_trade_intents.sqlite3"
    )

    created = create_trade_intent(
        {
            "candidate":
                candidate,

            "options_research":
                research,
        },
        path=trade_db,
    )

    intent_id = created[
        "intent"
    ][
        "intent_id"
    ]

    identity = resolve_account_identity(
        "trust"
    )

    assert identity[
        "known"
    ] is True

    draft = draft_operating_profile(
        account_key="trust",
        growth_objective="GROWTH",
        risk_level="MODERATE",
    )

    activation = activate_operating_profile(
        "obctx_test_owner",
        draft,
        owner_confirmed=True,
        path=(
            tmp_path
            / "owner_profiles.sqlite3"
        ),
    )

    profile = activation[
        "profile"
    ]

    profile_bound = (
        bind_owner_operating_profile(
            intent_id,
            profile,
            path=trade_db,
        )
    )

    mode_state = build_initial_mode_state(
        account_key="trust",
        mode="PAPER",
        owner_authorized=True,
        reason="obctx_test_paper_mode",
        recorded_at="2026-09-10T13:31:00+00:00",
    )

    mode_bound = bind_operating_mode(
        intent_id,
        mode_state,
        path=trade_db,
    )

    intent = mode_bound[
        "intent"
    ]

    validation = validate_trade_intent(
        intent
    )

    assert validation[
        "ok"
    ] is True

    policy = (
        resolve_effective_policy_for_intent(
            intent,
            extra_layers=[
                mode_policy_layer(
                    mode_state
                )
            ],
        )
    )

    fit_material = {
        "schema_version":
            "OB_OWNER_FIT_ELIGIBILITY_V1",

        "account_key":
            "trust",

        "bucket":
            "WATCH",

        "effective_policy_ref": {
            "account_key":
                "trust",

            "policy_id":
                policy[
                    "policy_id"
                ],

            "policy_fingerprint":
                policy[
                    "policy_fingerprint"
                ],
        },

        "owner_profile_ref": {
            "profile_id":
                profile[
                    "profile_id"
                ],

            "profile_hash":
                profile[
                    "profile_hash"
                ],
        },

        "execution_authority":
            False,

        "broker_submission":
            False,

        "capital_movement":
            False,

        "automatic_execution":
            False,
    }

    owner_fit = {
        **fit_material,

        "evaluation_fingerprint":
            stable_hash(
                fit_material
            ),
    }

    return {
        "intent":
            intent,

        "identity":
            identity,

        "profile":
            profile,

        "policy":
            policy,

        "owner_fit":
            owner_fit,

        "mode_state":
            mode_state,
    }


def test_obctx_is_active_and_pending_slot_is_retired():

    registry = (
        build_canonical_authority_registry()
    )

    assert (
        registry[
            "authority_records"
        ][
            "decision_context"
        ][
            "authority_id"
        ]
        ==
        "OB_DECISION_CONTEXT_V1"
    )

    assert (
        "decision_context"
        not in
        PENDING_AUTHORITY_SLOTS
    )

    resolution = (
        resolve_authority_reference(
            "PENDING_OBCTX"
        )
    )

    assert (
        resolution["resolution"]
        ==
        "RETIRED_ALIAS"
    )

    assert (
        resolution[
            "resolved_authority_id"
        ]
        ==
        "OB_DECISION_CONTEXT_V1"
    )


def test_exact_ten_authorities_no_longer_defer_decision_context():

    for concept in (
        DEFERRED_CONTEXT_CONCEPTS
    ):
        assert (
            "decision_context"
            not in
            ACTIVE_AUTHORITY_RECORDS[
                concept
            ][
                "deferred_integrations"
            ]
        )


def test_decision_context_builds_from_real_bound_authorities(
    tmp_path,
):

    inputs = _real_bound_inputs(
        tmp_path
    )

    originals = deepcopy(
        inputs
    )

    causal_event = {
        "schema_version":
            "OB_DOMAIN_EVENT_V1",

        "event_id":
            "obevt_obctx_test",

        "event_fingerprint":
            "event_fingerprint_obctx_test",

        "source_authority":
            "OB_OWNER_OPERATING_PROFILE_V1",
    }

    invalidation_plan = {
        "schema_version":
            "OB_CAUSAL_INVALIDATION_PLAN_V1",

        "invalidation_plan_fingerprint":
            "plan_fingerprint_obctx_test",

        "recompute_required": [
            "OB_DECISION_CONTEXT_V1",
        ],
    }

    context = build_decision_context(
        trade_intent=
            inputs["intent"],

        account_identity=
            inputs["identity"],

        owner_profile=
            inputs["profile"],

        effective_policy=
            inputs["policy"],

        owner_fit=
            inputs["owner_fit"],

        causal_event=
            causal_event,

        invalidation_plan=
            invalidation_plan,
    )

    validation = (
        validate_decision_context(
            context
        )
    )

    assert validation["ok"] is True
    assert (
        validation[
            "integrity_verified"
        ]
        is True
    )

    assert (
        context["account_key"]
        ==
        "trust"
    )

    assert (
        context[
            "trade_intent_reference"
        ][
            "intent_id"
        ]
        ==
        inputs[
            "intent"
        ][
            "intent_id"
        ]
    )

    assert (
        context[
            "trade_intent_reference"
        ][
            "intent_hash"
        ]
        ==
        inputs[
            "intent"
        ][
            "intent_hash"
        ]
    )

    assert (
        context[
            "candidate_snapshot"
        ][
            "candidate_fingerprint"
        ]
        ==
        inputs[
            "intent"
        ][
            "candidate"
        ][
            "candidate_fingerprint"
        ]
    )

    assert (
        context[
            "owner_profile_snapshot"
        ][
            "profile_hash"
        ]
        ==
        inputs[
            "profile"
        ][
            "profile_hash"
        ]
    )

    assert (
        context[
            "effective_policy_snapshot"
        ][
            "policy_fingerprint"
        ]
        ==
        inputs[
            "policy"
        ][
            "policy_fingerprint"
        ]
    )

    assert (
        context[
            "owner_fit_snapshot"
        ][
            "evaluation_fingerprint"
        ]
        ==
        inputs[
            "owner_fit"
        ][
            "evaluation_fingerprint"
        ]
    )

    assert (
        context[
            "causal_lineage"
        ][
            "event_fingerprint"
        ]
        ==
        "event_fingerprint_obctx_test"
    )

    assert (
        context[
            "causal_lineage"
        ][
            "invalidation_plan_fingerprint"
        ]
        ==
        "plan_fingerprint_obctx_test"
    )

    # Source objects were snapshotted, not mutated.
    assert inputs == originals


def test_trade_intent_validation_summary_is_never_substituted_for_intent(
    tmp_path,
):

    inputs = _real_bound_inputs(
        tmp_path
    )

    summary = validate_trade_intent(
        inputs["intent"]
    )

    assert "candidate" not in summary
    assert "intent_hash" not in summary

    context = build_decision_context(
        trade_intent=
            inputs["intent"],

        account_identity=
            inputs["identity"],

        owner_profile=
            inputs["profile"],

        effective_policy=
            inputs["policy"],

        owner_fit=
            inputs["owner_fit"],
    )

    # If build_decision_context had assigned:
    # intent = validate_trade_intent(intent)
    # this assertion could not pass.
    assert (
        context[
            "candidate_snapshot"
        ][
            "snapshot"
        ][
            "symbol"
        ]
        ==
        "AAPL"
    )


def test_context_is_hash_bound_and_tampering_fails(
    tmp_path,
):

    inputs = _real_bound_inputs(
        tmp_path
    )

    context = build_decision_context(
        trade_intent=
            inputs["intent"],

        account_identity=
            inputs["identity"],

        owner_profile=
            inputs["profile"],

        effective_policy=
            inputs["policy"],

        owner_fit=
            inputs["owner_fit"],
    )

    tampered = deepcopy(
        context
    )

    tampered[
        "candidate_snapshot"
    ][
        "snapshot"
    ][
        "symbol"
    ] = "MSFT"

    with pytest.raises(
        ValueError,
        match="fingerprint mismatch",
    ):
        validate_decision_context(
            tampered
        )


def test_cross_account_binding_fails_closed(
    tmp_path,
):

    inputs = _real_bound_inputs(
        tmp_path
    )

    wrong_identity = (
        resolve_account_identity(
            "personal"
        )
    )

    with pytest.raises(
        ValueError,
        match="account boundary",
    ):
        build_decision_context(
            trade_intent=
                inputs["intent"],

            account_identity=
                wrong_identity,

            owner_profile=
                inputs["profile"],

            effective_policy=
                inputs["policy"],

            owner_fit=
                inputs["owner_fit"],
        )


def test_future_authorities_remain_explicitly_pending(
    tmp_path,
):

    inputs = _real_bound_inputs(
        tmp_path
    )

    context = build_decision_context(
        trade_intent=
            inputs["intent"],

        account_identity=
            inputs["identity"],

        owner_profile=
            inputs["profile"],

        effective_policy=
            inputs["policy"],

        owner_fit=
            inputs["owner_fit"],
    )

    future = context[
        "future_authorities"
    ]

    assert (
        context[
            "operating_mode_snapshot"
        ][
            "authority"
        ]
        ==
        "OB_OPERATING_MODE_V1"
    )

    assert (
        context[
            "operating_mode_snapshot"
        ][
            "mode"
        ]
        ==
        "PAPER"
    )

    assert (
        future[
            "source_provenance"
        ][
            "authority_id"
        ]
        ==
        "PENDING_OBDATA011_015"
    )

    assert (
        future[
            "temporal_context"
        ][
            "authority_id"
        ]
        ==
        "PENDING_OBTIME"
    )

    assert (
        future[
            "source_provenance"
        ][
            "snapshot"
        ]
        is None
    )

    assert (
        future[
            "temporal_context"
        ][
            "snapshot"
        ]
        is None
    )


def test_obctx_grants_no_execution_or_money_authority():

    contract = (
        decision_context_contract()
    )

    assert (
        contract[
            "source_authorities_mutated"
        ]
        is False
    )

    assert (
        contract[
            "candidate_recalculated"
        ]
        is False
    )

    assert (
        contract[
            "market_score_recalculated"
        ]
        is False
    )

    assert (
        contract[
            "automatic_contract_selection"
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
            "broker_submission"
        ]
        is False
    )

    assert (
        contract[
            "capital_movement"
        ]
        is False
    )

    assert (
        contract[
            "hybrid_execution"
        ]
        is False
    )

    assert (
        contract[
            "automatic_execution"
        ]
        is False
    )

    assert (
        contract[
            "live_auto_locked"
        ]
        is True
    )


def test_context_reference_is_minimal_and_integrity_verified(
    tmp_path,
):

    inputs = _real_bound_inputs(
        tmp_path
    )

    context = build_decision_context(
        trade_intent=
            inputs["intent"],

        account_identity=
            inputs["identity"],

        owner_profile=
            inputs["profile"],

        effective_policy=
            inputs["policy"],

        owner_fit=
            inputs["owner_fit"],
    )

    reference = (
        decision_context_reference(
            context
        )
    )

    assert reference == {
        "authority":
            "OB_DECISION_CONTEXT_V1",

        "context_id":
            context[
                "context_id"
            ],

        "context_fingerprint":
            context[
                "context_fingerprint"
            ],

        "account_key":
            "trust",

        "integrity_verified":
            True,
    }
