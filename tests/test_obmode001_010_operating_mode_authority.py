from __future__ import annotations

from copy import deepcopy

import pytest

from web.ob_authority_registry import (
    PENDING_AUTHORITY_SLOTS,
    build_canonical_authority_registry,
    resolve_authority_reference,
)

from web.ob_effective_policy import (
    CAPABILITY_KEYS,
    mode_policy_layer,
    owner_profile_policy_layer,
    product_phase_policy_layer,
    resolve_effective_policy,
)

from web.ob_operating_mode import (
    FUTURE_LOCKED_MODES,
    MODES,
    activate_operating_mode,
    build_initial_mode_state,
    get_operating_mode,
    mode_allows_trade_intent_state,
    mode_policy_projection,
    mode_state_reference,
    operating_mode_contract,
    transition_mode_state,
    validate_mode_state,
)

from web.ob_owner_operating_profile import (
    activate_operating_profile,
    draft_operating_profile,
)

from web.ob_trade_intent import (
    bind_operating_mode,
    bind_owner_operating_profile,
    create_trade_intent,
)


def profile(tmp_path, account="trust"):

    draft = draft_operating_profile(
        account_key=account,
        growth_objective="GROWTH",
        risk_level="MODERATE",
    )

    return activate_operating_profile(
        "owner-solice",
        draft,
        owner_confirmed=True,
        path=(
            tmp_path
            / (
                "profile_"
                + account
                + ".sqlite3"
            )
        ),
    )[
        "profile"
    ]


def intent(tmp_path, account="trust"):

    trade_db = (
        tmp_path
        / (
            "intent_"
            + account
            + ".sqlite3"
        )
    )

    created = create_trade_intent(
        {
            "candidate": {
                "candidate_id":
                    "mode_candidate_"
                    + account,

                "symbol":
                    "AMD",

                "source":
                    "canonical_engine_feed",

                "verified":
                    True,

                "source_backed":
                    True,

                "actionable_state":
                    "ready",

                "strategy":
                    "continuation",

                "direction":
                    "CALL",

                "score":
                    90.0,
            },

            "options_research": {
                "schema_version":
                    "OB_OPTIONS_RESEARCH_V1",

                "authority":
                    "ENGINE_RESEARCH_PROJECTION",

                "research_contracts":
                    [],

                "ranked_contracts":
                    [],
            },
        },
        path=trade_db,
    )

    p = profile(
        tmp_path,
        account=account,
    )

    bound = bind_owner_operating_profile(
        created[
            "intent"
        ][
            "intent_id"
        ],
        p,
        path=trade_db,
    )

    return {
        "intent":
            bound[
                "intent"
            ],

        "intent_id":
            created[
                "intent"
            ][
                "intent_id"
            ],

        "profile":
            p,

        "trade_db":
            trade_db,
    }


def test_canonical_mode_contract():

    contract = operating_mode_contract()

    assert (
        contract[
            "authority"
        ]
        ==
        "OB_OPERATING_MODE_V1"
    )

    assert tuple(
        contract[
            "modes"
        ]
    ) == MODES

    assert set(
        contract[
            "future_locked_modes"
        ]
    ) == FUTURE_LOCKED_MODES

    assert (
        contract[
            "implicit_default_mode"
        ]
        is False
    )

    assert (
        contract[
            "account_bound"
        ]
        is True
    )

    assert (
        contract[
            "operating_mode_is_capital_mode"
        ]
        is False
    )


def test_no_implicit_mode():

    with pytest.raises(
        ValueError
    ):
        build_initial_mode_state(
            account_key="trust",
            mode=None,
            owner_authorized=True,
            reason="missing",
        )


def test_mode_requires_known_account():

    with pytest.raises(
        ValueError,
        match="known account",
    ):
        build_initial_mode_state(
            account_key="fake_account",
            mode="PAPER",
            owner_authorized=True,
            reason="bad-account",
        )


def test_mode_requires_owner_authorization():

    with pytest.raises(
        ValueError,
        match="owner authorization",
    ):
        build_initial_mode_state(
            account_key="trust",
            mode="PAPER",
            owner_authorized=False,
            reason="no-owner",
        )


def test_survey_to_paper_to_manual_live():

    survey = build_initial_mode_state(
        account_key="trust",
        mode="SURVEY",
        owner_authorized=True,
        reason="survey",
        recorded_at="2026-09-10T13:00:00+00:00",
    )

    paper = transition_mode_state(
        survey,
        next_mode="PAPER",
        owner_authorized=True,
        reason="paper",
        recorded_at="2026-09-10T13:01:00+00:00",
    )

    manual = transition_mode_state(
        paper,
        next_mode="MANUAL_LIVE_1",
        owner_authorized=True,
        reason="manual",
        recorded_at="2026-09-10T13:02:00+00:00",
    )

    assert survey["revision"] == 1
    assert paper["revision"] == 2
    assert manual["revision"] == 3

    assert paper["previous_mode"] == "SURVEY"
    assert manual["previous_mode"] == "PAPER"

    assert manual["mode"] == "MANUAL_LIVE_1"

    assert (
        manual[
            "capabilities"
        ][
            "owner_manual_broker_action_outside_ob_allowed"
        ]
        is True
    )

    assert (
        manual[
            "broker_submission"
        ]
        is False
    )


def test_hybrid_and_automated_are_locked():

    for mode in (
        "HYBRID",
        "AUTOMATED",
    ):

        with pytest.raises(
            ValueError,
            match="future locked",
        ):

            build_initial_mode_state(
                account_key="trust",
                mode=mode,
                owner_authorized=True,
                reason="future",
            )


def test_manual_live_cannot_transition_to_hybrid_today():

    manual = build_initial_mode_state(
        account_key="trust",
        mode="MANUAL_LIVE_1",
        owner_authorized=True,
        reason="manual",
    )

    with pytest.raises(
        ValueError,
        match="future locked",
    ):

        transition_mode_state(
            manual,
            next_mode="HYBRID",
            owner_authorized=True,
            reason="future",
        )


def test_modes_are_account_isolated(tmp_path):

    mode_db = (
        tmp_path
        / "mode.sqlite3"
    )

    activate_operating_mode(
        account_key="trust",
        mode="PAPER",
        owner_authorized=True,
        reason="trust-paper",
        path=mode_db,
    )

    activate_operating_mode(
        account_key="personal",
        mode="SURVEY",
        owner_authorized=True,
        reason="personal-survey",
        path=mode_db,
    )

    trust = get_operating_mode(
        "trust",
        path=mode_db,
    )

    personal = get_operating_mode(
        "personal",
        path=mode_db,
    )

    assert trust["mode"] == "PAPER"
    assert personal["mode"] == "SURVEY"

    assert (
        trust[
            "mode_state_fingerprint"
        ]
        !=
        personal[
            "mode_state_fingerprint"
        ]
    )


def test_mode_state_is_hash_bound():

    state = build_initial_mode_state(
        account_key="trust",
        mode="PAPER",
        owner_authorized=True,
        reason="hash-test",
    )

    validate_mode_state(
        state
    )

    tampered = deepcopy(
        state
    )

    tampered[
        "mode"
    ] = "SURVEY"

    with pytest.raises(
        ValueError
    ):
        validate_mode_state(
            tampered
        )


def test_mode_policy_is_restriction_only(tmp_path):

    state = build_initial_mode_state(
        account_key="trust",
        mode="PAPER",
        owner_authorized=True,
        reason="policy",
    )

    layer = mode_policy_layer(
        state
    )

    assert (
        layer[
            "layer_class"
        ]
        ==
        "MODE_POLICY"
    )

    assert (
        layer[
            "source_authority"
        ]
        ==
        "OB_OPERATING_MODE_V1"
    )

    assert (
        layer[
            "restriction_only"
        ]
        is True
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
        ][key]
        is False
        for key
        in CAPABILITY_KEYS
    )


def test_mode_policy_uses_existing_effective_policy(tmp_path):

    p = profile(
        tmp_path
    )

    mode = build_initial_mode_state(
        account_key="trust",
        mode="PAPER",
        owner_authorized=True,
        reason="policy",
    )

    policy = resolve_effective_policy(
        account_key="trust",
        layers=[
            owner_profile_policy_layer(
                p
            ),
            product_phase_policy_layer(
                "trust"
            ),
            mode_policy_layer(
                mode
            ),
        ],
    )

    classes = {
        item[
            "layer_class"
        ]
        for item
        in policy[
            "source_layers"
        ]
    }

    assert "MODE_POLICY" in classes

    assert (
        policy[
            "owner_profile_widened"
        ]
        is False
    )

    assert (
        policy[
            "effective_limits"
        ][
            "live_automation_allowed"
        ]
        is False
    )


def test_trade_intent_mode_binding_is_account_bound(tmp_path):

    built = intent(
        tmp_path,
        account="trust",
    )

    state = build_initial_mode_state(
        account_key="trust",
        mode="PAPER",
        owner_authorized=True,
        reason="intent",
    )

    bound = bind_operating_mode(
        built[
            "intent_id"
        ],
        state,
        path=built[
            "trade_db"
        ],
    )[
        "intent"
    ]

    assert (
        bound[
            "mode_authority"
        ][
            "status"
        ]
        ==
        "BOUND"
    )

    assert (
        bound[
            "mode_authority"
        ][
            "mode"
        ]
        ==
        "PAPER"
    )

    assert (
        bound[
            "mode_authority"
        ][
            "authority"
        ]
        ==
        "OB_OPERATING_MODE_V1"
    )


def test_cross_account_mode_binding_fails(tmp_path):

    built = intent(
        tmp_path,
        account="trust",
    )

    wrong = build_initial_mode_state(
        account_key="personal",
        mode="PAPER",
        owner_authorized=True,
        reason="wrong-account",
    )

    with pytest.raises(
        ValueError,
        match="account boundary",
    ):

        bind_operating_mode(
            built[
                "intent_id"
            ],
            wrong,
            path=built[
                "trade_db"
            ],
        )


def test_survey_cannot_enter_selected_tracking_state():

    survey = build_initial_mode_state(
        account_key="trust",
        mode="SURVEY",
        owner_authorized=True,
        reason="survey",
    )

    assert (
        mode_allows_trade_intent_state(
            survey,
            "OWNER_SELECTED",
        )
        is False
    )

    assert (
        mode_allows_trade_intent_state(
            survey,
            "TRACKING",
        )
        is False
    )


def test_paper_and_manual_live_support_selected_tracking():

    for mode in (
        "PAPER",
        "MANUAL_LIVE_1",
    ):

        state = build_initial_mode_state(
            account_key="trust",
            mode=mode,
            owner_authorized=True,
            reason="lifecycle",
        )

        assert (
            mode_allows_trade_intent_state(
                state,
                "OWNER_SELECTED",
            )
            is True
        )

        assert (
            mode_allows_trade_intent_state(
                state,
                "TRACKING",
            )
            is True
        )


def test_mode_reference_is_minimal():

    state = build_initial_mode_state(
        account_key="trust",
        mode="PAPER",
        owner_authorized=True,
        reason="ref",
    )

    ref = mode_state_reference(
        state
    )

    assert ref["authority"] == "OB_OPERATING_MODE_V1"
    assert ref["account_key"] == "trust"
    assert ref["mode"] == "PAPER"
    assert ref["mode_state_fingerprint"]
    assert ref["broker_submission"] is False
    assert ref["capital_movement"] is False


def test_pending_obmode_is_retired_alias():

    resolution = resolve_authority_reference(
        "PENDING_OBMODE"
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
        "OB_OPERATING_MODE_V1"
    )


def test_registry_activates_mode():

    registry = (
        build_canonical_authority_registry()
    )

    assert (
        registry[
            "authority_records"
        ][
            "mode_authority"
        ][
            "authority_id"
        ]
        ==
        "OB_OPERATING_MODE_V1"
    )

    assert (
        "mode_authority"
        not in
        PENDING_AUTHORITY_SLOTS
    )

    assert (
        registry[
            "validation"
        ][
            "valid"
        ]
        is True
    )


def test_no_mode_grants_execution_or_money_authority():

    for mode in (
        "SURVEY",
        "PAPER",
        "MANUAL_LIVE_1",
    ):

        state = build_initial_mode_state(
            account_key="trust",
            mode=mode,
            owner_authorized=True,
            reason="safety",
        )

        assert state["execution_authority"] is False
        assert state["broker_submission"] is False
        assert state["capital_movement"] is False
        assert state["automatic_contract_selection"] is False
        assert state["hybrid_execution"] is False
        assert state["automatic_execution"] is False
        assert state["live_auto_locked"] is True

        projection = mode_policy_projection(
            state
        )

        assert projection["execution_authority"] is False
        assert projection["broker_submission"] is False
        assert projection["capital_movement"] is False
        assert projection["automatic_execution"] is False
