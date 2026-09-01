
from datetime import datetime, timedelta, timezone
from pathlib import Path
import pytest


ROOT = (
    Path(__file__).resolve().parents[1]
)

PROFILE_SERVICE = (
    ROOT
    / "web/ob_owner_operating_profile.py"
)

TRADE_INTENT = (
    ROOT
    / "web/ob_trade_intent.py"
)

AUTHORITY = (
    ROOT
    / "web/ob_engine_account_authority.py"
)

APP = (
    ROOT
    / "web/app.py"
)

TOWER_GUARD = (
    ROOT
    / "tower/ob_web_route_enforcement.py"
)


def text(path):
    return path.read_text(
        encoding="utf-8",
        errors="replace",
    )


def owner_step_up(client):
    with client.session_transaction() as session:
        session[
            "tower_authenticated"
        ] = True

        session[
            "tower_role"
        ] = "owner"

        session[
            "owner_id"
        ] = "simplee_owner"

        session[
            "tower_username"
        ] = "owner"

        session[
            "tower_authenticated_at"
        ] = (
            datetime.now(
                timezone.utc
            ).isoformat()
        )

        session[
            "tower_step_up_until"
        ] = (
            datetime.now(
                timezone.utc
            )
            + timedelta(
                minutes=10
            )
        ).isoformat()


def candidate_fixture():
    return {
        "candidate_id":
            "obrisk-fixture-amd-001",

        "symbol":
            "AMD",

        "source":
            "obrisk_acceptance_fixture",

        "as_of":
            "2026-09-01T14:00:00+00:00",

        "strategy":
            "continuation",

        "direction":
            "CALL",

        "score":
            91.0,

        "entry":
            100.0,

        "target":
            110.0,

        "invalidation":
            96.0,
    }


def options_fixture():
    return {
        "schema_version":
            "OB_OPTIONS_RESEARCH_V1",

        "authority":
            "ENGINE_RESEARCH_PROJECTION",

        "selection_authority":
            "OWNER",

        "research_contracts": [
            {
                "symbol":
                    "AMD",

                "contract_symbol":
                    "AMD_OBRISK_FIXTURE_CALL",

                "right":
                    "CALL",

                "strike":
                    100,

                "expiration":
                    "2026-09-18",

                "bid":
                    4.9,

                "ask":
                    5.1,

                "volume":
                    500,

                "open_interest":
                    1500,

                "implied_volatility":
                    0.45,

                "research_only":
                    True,

                "ob_selected_contract":
                    False,

                "owner_selected_contract":
                    False,

                "automatic_contract_selection":
                    False,

                "brokerage_execution":
                    False,

                "automatic_execution":
                    False,
            }
        ],

        "ranked_contracts": [],

        "diagnostics": {
            "no_fake_fallback":
                True,

            "automatic_contract_selection":
                False,

            "brokerage_execution":
                False,

            "automatic_execution":
                False,
        },
    }


def test_obrisk001_growth_and_risk_are_independent():
    from web.ob_owner_operating_profile import (
        draft_operating_profile,
    )

    draft = draft_operating_profile(
        "trust",
        "AGGRESSIVE_GROWTH",
        "MODERATE",
    )

    assert (
        draft[
            "growth_objective"
        ][
            "key"
        ]
        ==
        "AGGRESSIVE_GROWTH"
    )

    assert (
        draft[
            "risk_envelope"
        ][
            "key"
        ]
        ==
        "MODERATE"
    )

    assert (
        draft[
            "growth_objective"
        ][
            "risk_level_implied"
        ]
        is False
    )


def test_obrisk001_account_is_explicit_and_has_no_default():
    from web.ob_owner_operating_profile import (
        draft_operating_profile,
    )

    with pytest.raises(
        ValueError,
        match="Explicit account_key",
    ):
        draft_operating_profile(
            "",
            "GROWTH",
            "MODERATE",
        )

    with pytest.raises(
        ValueError,
        match="Unknown account_key",
    ):
        draft_operating_profile(
            "whatever_account",
            "GROWTH",
            "MODERATE",
        )


def test_obrisk002_draft_exposes_numeric_limits_but_is_not_active():
    from web.ob_owner_operating_profile import (
        draft_operating_profile,
    )

    draft = draft_operating_profile(
        "trust",
        "AGGRESSIVE_GROWTH",
        "MODERATE",
    )

    limits = (
        draft[
            "risk_envelope"
        ][
            "effective_limits"
        ]
    )

    assert (
        limits[
            "max_loss_per_trade_pct"
        ]
        ==
        1.0
    )

    assert (
        limits[
            "max_position_allocation_pct"
        ]
        ==
        10.0
    )

    assert (
        limits[
            "max_concurrent_positions"
        ]
        ==
        3
    )

    assert (
        limits[
            "live_automation_allowed"
        ]
        is False
    )

    assert (
        draft[
            "owner_confirmed"
        ]
        is False
    )

    assert (
        draft[
            "active"
        ]
        is False
    )

    assert (
        draft[
            "status"
        ]
        ==
        "DRAFT"
    )


def test_obrisk002_activation_requires_explicit_owner_confirmation(tmp_path):
    from web.ob_owner_operating_profile import (
        activate_operating_profile,
        draft_operating_profile,
    )

    draft = draft_operating_profile(
        "trust",
        "GROWTH",
        "MODERATE",
    )

    with pytest.raises(
        ValueError,
        match="Explicit owner confirmation",
    ):
        activate_operating_profile(
            "owner",
            draft,
            owner_confirmed=False,
            path=(
                tmp_path
                / "profiles.sqlite3"
            ),
        )


def test_obrisk002_custom_risk_requires_every_limit():
    from web.ob_owner_operating_profile import (
        draft_operating_profile,
    )

    with pytest.raises(
        ValueError,
        match="CUSTOM risk requires every",
    ):
        draft_operating_profile(
            "personal",
            "CUSTOM",
            "CUSTOM",
            {
                "max_loss_per_trade_pct":
                    1.0,
            },
        )


def test_obrisk002_growth_objective_does_not_define_profit_target():
    from web.ob_owner_operating_profile import (
        draft_operating_profile,
    )

    draft = draft_operating_profile(
        "trust",
        "AGGRESSIVE_GROWTH",
        "MODERATE",
    )

    growth = (
        draft[
            "growth_objective"
        ]
    )

    assert (
        "target_return"
        not in growth
    )

    assert (
        "cagr"
        not in growth
    )

    assert (
        "profit_goal"
        not in growth
    )

    assert (
        growth[
            "numeric_return_target_defined"
        ]
        is False
    )

    assert (
        growth[
            "return_guarantee"
        ]
        is False
    )


def test_obrisk003_profiles_are_isolated_per_account(tmp_path):
    from web.ob_owner_operating_profile import (
        activate_operating_profile,
        draft_operating_profile,
        get_active_operating_profile,
    )

    database = (
        tmp_path
        / "profiles.sqlite3"
    )

    personal = activate_operating_profile(
        "owner",
        draft_operating_profile(
            "personal",
            "GROWTH",
            "MODERATE",
        ),
        owner_confirmed=True,
        path=database,
    )[
        "profile"
    ]

    trust = activate_operating_profile(
        "owner",
        draft_operating_profile(
            "trust",
            "STEADY",
            "LOW",
        ),
        owner_confirmed=True,
        path=database,
    )[
        "profile"
    ]

    assert (
        personal[
            "account"
        ][
            "account_key"
        ]
        ==
        "personal"
    )

    assert (
        trust[
            "account"
        ][
            "account_key"
        ]
        ==
        "trust"
    )

    assert (
        personal[
            "profile_id"
        ]
        !=
        trust[
            "profile_id"
        ]
    )

    assert (
        get_active_operating_profile(
            "owner",
            "personal",
            path=database,
        )[
            "profile_id"
        ]
        ==
        personal[
            "profile_id"
        ]
    )

    assert (
        get_active_operating_profile(
            "owner",
            "trust",
            path=database,
        )[
            "profile_id"
        ]
        ==
        trust[
            "profile_id"
        ]
    )


def test_obrisk003_revision_increments_only_for_changed_account(tmp_path):
    from web.ob_owner_operating_profile import (
        activate_operating_profile,
        draft_operating_profile,
        get_active_operating_profile,
    )

    database = (
        tmp_path
        / "profiles.sqlite3"
    )

    personal_v1 = activate_operating_profile(
        "owner",
        draft_operating_profile(
            "personal",
            "GROWTH",
            "MODERATE",
        ),
        owner_confirmed=True,
        path=database,
    )[
        "profile"
    ]

    trust_v1 = activate_operating_profile(
        "owner",
        draft_operating_profile(
            "trust",
            "STEADY",
            "LOW",
        ),
        owner_confirmed=True,
        path=database,
    )[
        "profile"
    ]

    trust_v2 = activate_operating_profile(
        "owner",
        draft_operating_profile(
            "trust",
            "GROWTH",
            "MODERATE",
        ),
        owner_confirmed=True,
        path=database,
    )[
        "profile"
    ]

    assert (
        personal_v1[
            "revision"
        ]
        ==
        1
    )

    assert (
        trust_v1[
            "revision"
        ]
        ==
        1
    )

    assert (
        trust_v2[
            "revision"
        ]
        ==
        2
    )

    personal_active = (
        get_active_operating_profile(
            "owner",
            "personal",
            path=database,
        )
    )

    assert (
        personal_active[
            "revision"
        ]
        ==
        1
    )


def test_obrisk003_profile_history_preserves_retired_revision(tmp_path):
    from web.ob_owner_operating_profile import (
        activate_operating_profile,
        draft_operating_profile,
        list_operating_profile_history,
    )

    database = (
        tmp_path
        / "profiles.sqlite3"
    )

    activate_operating_profile(
        "owner",
        draft_operating_profile(
            "trust",
            "STEADY",
            "LOW",
        ),
        owner_confirmed=True,
        path=database,
    )

    activate_operating_profile(
        "owner",
        draft_operating_profile(
            "trust",
            "GROWTH",
            "MODERATE",
        ),
        owner_confirmed=True,
        path=database,
    )

    history = (
        list_operating_profile_history(
            "owner",
            "trust",
            path=database,
        )
    )

    assert len(
        history
    ) == 2

    assert (
        history[0][
            "revision"
        ]
        ==
        1
    )

    assert (
        history[0][
            "status"
        ]
        ==
        "RETIRED"
    )

    assert (
        history[0][
            "record_status"
        ]
        ==
        "RETIRED"
    )

    assert (
        history[1][
            "revision"
        ]
        ==
        2
    )

    assert (
        history[1][
            "status"
        ]
        ==
        "ACTIVE"
    )


def test_obrisk003_most_restrictive_policy_wins():
    from web.ob_owner_operating_profile import (
        most_restrictive_limits,
    )

    profile = {
        "max_loss_per_trade_pct":
            1.5,

        "max_position_allocation_pct":
            15.0,

        "daily_loss_cap_pct":
            4.0,

        "max_concurrent_positions":
            4,

        "max_spread_pct":
            15.0,

        "min_option_volume":
            25,

        "min_open_interest":
            100,

        "max_correlated_exposure_pct":
            35.0,

        "max_hold_minutes":
            1440,

        "overnight_allowed":
            True,

        "max_implied_volatility_pct":
            180.0,

        "live_automation_allowed":
            False,
    }

    account_policy = {
        "max_loss_per_trade_pct":
            1.0,

        "max_position_allocation_pct":
            10.0,

        "daily_loss_cap_pct":
            2.0,

        "max_concurrent_positions":
            3,

        "max_spread_pct":
            10.0,

        "min_option_volume":
            100,

        "min_open_interest":
            500,

        "max_correlated_exposure_pct":
            20.0,

        "max_hold_minutes":
            780,

        "overnight_allowed":
            False,

        "max_implied_volatility_pct":
            120.0,

        "live_automation_allowed":
            False,
    }

    result = (
        most_restrictive_limits(
            profile,
            account_policy,
        )
    )

    # Upper bound → lower wins.
    assert (
        result[
            "max_loss_per_trade_pct"
        ]
        ==
        1.0
    )

    assert (
        result[
            "max_concurrent_positions"
        ]
        ==
        3
    )

    # Minimum liquidity → higher wins.
    assert (
        result[
            "min_open_interest"
        ]
        ==
        500
    )

    assert (
        result[
            "min_option_volume"
        ]
        ==
        100
    )

    # Permission → False wins.
    assert (
        result[
            "overnight_allowed"
        ]
        is False
    )

    assert (
        result[
            "live_automation_allowed"
        ]
        is False
    )


def test_obrisk004_active_profile_binds_account_and_risk_refs_to_trade_intent(tmp_path):
    from web.ob_owner_operating_profile import (
        activate_operating_profile,
        draft_operating_profile,
    )

    from web.ob_trade_intent import (
        bind_owner_operating_profile,
        create_trade_intent,
    )

    profile_database = (
        tmp_path
        / "profiles.sqlite3"
    )

    intent_database = (
        tmp_path
        / "intents.sqlite3"
    )

    profile = activate_operating_profile(
        "owner",
        draft_operating_profile(
            "trust",
            "AGGRESSIVE_GROWTH",
            "MODERATE",
        ),
        owner_confirmed=True,
        path=profile_database,
    )[
        "profile"
    ]

    intent = create_trade_intent(
        {
            "candidate":
                candidate_fixture(),

            "options_research":
                options_fixture(),
        },
        path=intent_database,
    )[
        "intent"
    ]

    assert (
        intent[
            "lifecycle_state"
        ]
        ==
        "OWNER_FIT_PENDING"
    )

    bound = bind_owner_operating_profile(
        intent[
            "intent_id"
        ],
        profile,
        path=intent_database,
    )[
        "intent"
    ]

    assert (
        bound[
            "account_context"
        ][
            "status"
        ]
        ==
        "BOUND"
    )

    assert (
        bound[
            "account_context"
        ][
            "account_key"
        ]
        ==
        "trust"
    )

    assert (
        bound[
            "account_context"
        ][
            "explicit_owner_choice"
        ]
        is True
    )

    assert (
        bound[
            "account_context"
        ][
            "implicit_default_allowed"
        ]
        is False
    )

    assert (
        bound[
            "owner_fit"
        ][
            "status"
        ]
        ==
        "PENDING_OBRISK_ELIGIBILITY"
    )

    assert (
        bound[
            "owner_fit"
        ][
            "evaluated"
        ]
        is False
    )

    assert (
        bound[
            "owner_fit"
        ][
            "eligible"
        ]
        is None
    )

    assert (
        bound[
            "owner_fit"
        ][
            "growth_objective_ref"
        ][
            "growth_key"
        ]
        ==
        "AGGRESSIVE_GROWTH"
    )

    assert (
        bound[
            "owner_fit"
        ][
            "risk_envelope_ref"
        ][
            "risk_key"
        ]
        ==
        "MODERATE"
    )

    # OBRISK001–005 does NOT advance candidate eligibility.
    assert (
        bound[
            "lifecycle_state"
        ]
        ==
        "OWNER_FIT_PENDING"
    )

    # OBMODE still owns mode authority.
    assert (
        bound[
            "mode_authority"
        ][
            "status"
        ]
        ==
        "PENDING_OBMODE"
    )


def test_obrisk004_manual_live_bridge_remains_locked_after_profile_binding(tmp_path):
    from web.ob_owner_operating_profile import (
        activate_operating_profile,
        draft_operating_profile,
    )

    from web.ob_trade_intent import (
        bind_owner_operating_profile,
        create_trade_intent,
        manual_live_handoff_payload,
    )

    profile_database = (
        tmp_path
        / "profiles.sqlite3"
    )

    intent_database = (
        tmp_path
        / "intents.sqlite3"
    )

    profile = activate_operating_profile(
        "owner",
        draft_operating_profile(
            "trust",
            "AGGRESSIVE_GROWTH",
            "MODERATE",
        ),
        owner_confirmed=True,
        path=profile_database,
    )[
        "profile"
    ]

    intent = create_trade_intent(
        {
            "candidate":
                candidate_fixture(),

            "options_research":
                options_fixture(),
        },
        path=intent_database,
    )[
        "intent"
    ]

    bound = bind_owner_operating_profile(
        intent[
            "intent_id"
        ],
        profile,
        path=intent_database,
    )[
        "intent"
    ]

    with pytest.raises(
        ValueError,
        match="Manual Live bridge is locked",
    ):
        manual_live_handoff_payload(
            bound,
            owner_id="owner",
        )


def test_obrisk005_authority_registry_exposes_owner_operating_profile():
    from web.app import app

    app.config.update(
        TESTING=True
    )

    client = (
        app.test_client()
    )

    owner_step_up(
        client
    )

    response = client.get(
        "/ob/market-map?engine_feed=1",
        follow_redirects=False,
    )

    assert (
        response.status_code
        ==
        200
    )

    assert (
        response.is_json
        is True
    )

    payload = (
        response.get_json()
    )

    authority = (
        payload[
            "authority_registry"
        ][
            "owner_operating_profile"
        ]
    )

    assert (
        authority[
            "authority"
        ]
        ==
        "OB_OWNER_OPERATING_PROFILE_V1"
    )

    assert (
        authority[
            "per_account"
        ]
        is True
    )

    assert (
        authority[
            "growth_and_risk_independent"
        ]
        is True
    )

    assert (
        authority[
            "owner_fit_calculation"
        ]
        is False
    )

    assert (
        authority[
            "automatic_execution"
        ]
        is False
    )


def test_obrisk005_old_unapproved_engine_feed_remains_fail_closed():
    from web.app import app

    app.config.update(
        TESTING=True
    )

    client = (
        app.test_client()
    )

    owner_step_up(
        client
    )

    response = client.get(
        "/ob/engine-feed-snapshot.json",
        follow_redirects=False,
    )

    assert (
        response.status_code
        ==
        403
    )


def test_obrisk005_no_new_route_or_tower_policy_change():
    profile_source = text(
        PROFILE_SERVICE
    )

    intent_source = text(
        TRADE_INTENT
    )

    app_source = text(
        APP
    )

    guard = text(
        TOWER_GUARD
    )

    assert (
        "@app.route("
        not in profile_source
    )

    assert (
        '@app.route("/ob/owner-operating-profile'
        not in app_source
    )

    assert (
        "# OBRISK001-005_OWNER_OPERATING_PROFILE_BINDING"
        in intent_source
    )

    assert (
        '"/ob/engine-feed-snapshot.json"'
        not in guard
    )

    assert (
        "if not is_approved_ob_web_room(path):"
        in guard
    )

    assert (
        "abort(403)"
        in guard
    )


def test_obrisk005_execution_boundaries_remain_locked():
    from web.ob_owner_operating_profile import (
        operating_profile_contract,
        risk_templates,
    )

    contract = (
        operating_profile_contract()
    )

    boundaries = (
        contract[
            "boundaries"
        ]
    )

    assert (
        boundaries[
            "market_truth_modified"
        ]
        is False
    )

    assert (
        boundaries[
            "owner_fit_calculated_here"
        ]
        is False
    )

    assert (
        boundaries[
            "candidate_ranking_calculated_here"
        ]
        is False
    )

    assert (
        boundaries[
            "automatic_contract_selection"
        ]
        is False
    )

    assert (
        boundaries[
            "broker_submission"
        ]
        is False
    )

    assert (
        boundaries[
            "capital_movement"
        ]
        is False
    )

    assert (
        boundaries[
            "hybrid_execution"
        ]
        is False
    )

    assert (
        boundaries[
            "automatic_execution"
        ]
        is False
    )

    assert (
        boundaries[
            "live_auto_locked"
        ]
        is True
    )

    for name, template in (
        risk_templates().items()
    ):
        assert (
            template[
                "live_automation_allowed"
            ]
            is False
        ), name
