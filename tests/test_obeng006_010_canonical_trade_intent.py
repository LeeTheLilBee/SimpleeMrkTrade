
from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import pytest


ROOT = (
    Path(__file__).resolve().parents[1]
)

TRADE_INTENT = (
    ROOT
    / "web/ob_trade_intent.py"
)

AUTHORITY = (
    ROOT
    / "web/ob_engine_account_authority.py"
)

OPTIONS = (
    ROOT
    / "web/static/ob/ob_options_research_contract.js"
)

MANUAL = (
    ROOT
    / "web/ob_manual_live_candidate_decision_handoff.py"
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


def candidate_fixture():
    return {
        "candidate_id":
            "fixture-candidate-amd-001",

        "symbol":
            "AMD",

        "source":
            "acceptance_fixture",

        "as_of":
            "2026-09-01T14:00:00+00:00",

        "strategy":
            "continuation",

        "direction":
            "CALL",

        "score":
            91.0,

        "confidence":
            "HIGH",

        "entry":
            100.0,

        "target":
            110.0,

        "invalidation":
            96.0,

        "expected_hold":
            "intraday",
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
                    "AMD_TEST_CALL",

                "right":
                    "CALL",

                "strike":
                    100.0,

                "expiration":
                    "2026-09-18",

                "bid":
                    4.9,

                "ask":
                    5.1,

                "contract_score":
                    88.0,

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

        "ranked_contracts": [
            {
                "symbol":
                    "AMD",

                "contract_symbol":
                    "AMD_TEST_CALL",

                "contract_score":
                    88.0,

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


def test_obeng006_trade_intent_is_mode_neutral_and_reuses_existing_authorities():
    from web.ob_trade_intent import (
        trade_intent_contract,
    )

    contract = (
        trade_intent_contract()
    )

    assert (
        contract[
            "authority"
        ]
        ==
        "CANONICAL_OB_TRADE_INTENT"
    )

    assert (
        contract[
            "mode_neutral"
        ]
        is True
    )

    assert (
        contract[
            "candidate_authority"
        ]
        ==
        "EXISTING_CANONICAL_ENGINE"
    )

    assert (
        contract[
            "options_research_authority"
        ]
        ==
        "OB_OPTIONS_RESEARCH_V1"
    )

    assert (
        contract[
            "account_authority"
        ]
        ==
        "OB_ENGINE_ACCOUNT_AUTHORITY_V1"
    )

    assert (
        contract[
            "owner_fit_authority"
        ]
        ==
        "PENDING_OBRISK"
    )

    assert (
        contract[
            "mode_authority"
        ]
        ==
        "PENDING_OBMODE"
    )


def test_obeng006_same_candidate_creates_same_intent_identity():
    from web.ob_trade_intent import (
        build_trade_intent,
    )

    one = build_trade_intent(
        {
            "candidate":
                candidate_fixture(),

            "options_research":
                options_fixture(),
        }
    )

    two = build_trade_intent(
        {
            "candidate":
                candidate_fixture(),

            "options_research":
                options_fixture(),
        }
    )

    assert (
        one[
            "intent_id"
        ]
        ==
        two[
            "intent_id"
        ]
    )

    assert (
        one[
            "candidate"
        ][
            "candidate_fingerprint"
        ]
        ==
        two[
            "candidate"
        ][
            "candidate_fingerprint"
        ]
    )


def test_obeng007_research_rank_does_not_become_selected_contract():
    from web.ob_trade_intent import (
        build_trade_intent,
    )

    intent = build_trade_intent(
        {
            "candidate":
                candidate_fixture(),

            "options_research":
                options_fixture(),
        }
    )

    research = (
        intent[
            "options_research"
        ]
    )

    assert (
        research[
            "status"
        ]
        ==
        "RESEARCH_BOUND"
    )

    assert (
        research[
            "selection_authority"
        ]
        ==
        "OWNER"
    )

    assert (
        research[
            "selected_contract"
        ]
        is None
    )

    assert (
        research[
            "automatic_contract_selection"
        ]
        is False
    )

    assert (
        research[
            "brokerage_execution"
        ]
        is False
    )

    assert (
        research[
            "automatic_execution"
        ]
        is False
    )


def test_obeng007_selected_contract_authority_is_rejected():
    from web.ob_trade_intent import (
        build_trade_intent,
    )

    bad = options_fixture()

    bad[
        "owner_selected_contract"
    ] = True

    with pytest.raises(
        ValueError
    ):
        build_trade_intent(
            {
                "candidate":
                    candidate_fixture(),

                "options_research":
                    bad,
            }
        )


def test_obeng007_owner_fit_account_and_mode_are_not_silently_assumed():
    from web.ob_trade_intent import (
        build_trade_intent,
    )

    intent = build_trade_intent(
        {
            "candidate":
                candidate_fixture(),

            "options_research":
                options_fixture(),
        }
    )

    assert (
        intent[
            "lifecycle_state"
        ]
        ==
        "OWNER_FIT_PENDING"
    )

    assert (
        intent[
            "owner_fit"
        ][
            "evaluated"
        ]
        is False
    )

    assert (
        intent[
            "owner_fit"
        ][
            "status"
        ]
        ==
        "PENDING_OBRISK"
    )

    assert (
        intent[
            "account_context"
        ][
            "status"
        ]
        ==
        "UNBOUND"
    )

    assert (
        intent[
            "account_context"
        ][
            "implicit_default_allowed"
        ]
        is False
    )

    assert (
        intent[
            "mode_authority"
        ][
            "status"
        ]
        ==
        "PENDING_OBMODE"
    )


def test_obeng008_account_authority_is_reference_not_synthetic_account():
    from web.ob_trade_intent import (
        build_trade_intent,
    )

    intent = build_trade_intent(
        {
            "candidate":
                candidate_fixture(),

            "options_research":
                options_fixture(),
        }
    )

    account = (
        intent[
            "account_authority"
        ]
    )

    assert (
        account[
            "authority_contract"
        ]
        ==
        "OB_ENGINE_ACCOUNT_AUTHORITY_V1"
    )

    assert (
        account[
            "cross_source_resolved_account"
        ]
        is None
    )

    assert (
        account[
            "no_silent_merge"
        ]
        is True
    )


def test_obeng008_trade_intent_persistence_round_trip(tmp_path):
    from web.ob_trade_intent import (
        create_trade_intent,
        get_trade_intent,
        list_trade_intent_events,
    )

    database = (
        tmp_path
        / "trade_intents.sqlite3"
    )

    created = create_trade_intent(
        {
            "candidate":
                candidate_fixture(),

            "options_research":
                options_fixture(),
        },
        path=database,
    )

    assert (
        created[
            "created"
        ]
        is True
    )

    intent = (
        created[
            "intent"
        ]
    )

    loaded = get_trade_intent(
        intent[
            "intent_id"
        ],
        path=database,
    )

    assert (
        loaded[
            "intent_hash"
        ]
        ==
        intent[
            "intent_hash"
        ]
    )

    events = (
        list_trade_intent_events(
            intent[
                "intent_id"
            ],
            path=database,
        )
    )

    assert len(
        events
    ) == 1

    assert (
        events[0][
            "event_type"
        ]
        ==
        "INTENT_CREATED"
    )


def test_obeng008_creation_is_idempotent_for_same_candidate(tmp_path):
    from web.ob_trade_intent import (
        create_trade_intent,
    )

    database = (
        tmp_path
        / "trade_intents.sqlite3"
    )

    payload = {
        "candidate":
            candidate_fixture(),

        "options_research":
            options_fixture(),
    }

    first = create_trade_intent(
        payload,
        path=database,
    )

    second = create_trade_intent(
        payload,
        path=database,
    )

    assert (
        first[
            "created"
        ]
        is True
    )

    assert (
        second[
            "created"
        ]
        is False
    )

    assert (
        second[
            "idempotent"
        ]
        is True
    )

    assert (
        first[
            "intent"
        ][
            "intent_id"
        ]
        ==
        second[
            "intent"
        ][
            "intent_id"
        ]
    )


def test_obeng009_research_can_be_bound_after_candidate_creation(tmp_path):
    from web.ob_trade_intent import (
        bind_options_research,
        create_trade_intent,
    )

    database = (
        tmp_path
        / "trade_intents.sqlite3"
    )

    created = create_trade_intent(
        {
            "candidate":
                candidate_fixture(),
        },
        path=database,
    )

    assert (
        created[
            "intent"
        ][
            "lifecycle_state"
        ]
        ==
        "RESEARCH_PENDING"
    )

    result = bind_options_research(
        created[
            "intent"
        ][
            "intent_id"
        ],
        options_fixture(),
        path=database,
    )

    assert (
        result[
            "intent"
        ][
            "lifecycle_state"
        ]
        ==
        "OWNER_FIT_PENDING"
    )

    assert (
        result[
            "intent"
        ][
            "options_research"
        ][
            "status"
        ]
        ==
        "RESEARCH_BOUND"
    )


def test_obeng009_owner_review_cannot_start_before_obrisk(tmp_path):
    from web.ob_trade_intent import (
        create_trade_intent,
        transition_trade_intent,
    )

    database = (
        tmp_path
        / "trade_intents.sqlite3"
    )

    created = create_trade_intent(
        {
            "candidate":
                candidate_fixture(),

            "options_research":
                options_fixture(),
        },
        path=database,
    )

    with pytest.raises(
        ValueError,
        match="OBRISK"
    ):
        transition_trade_intent(
            created[
                "intent"
            ][
                "intent_id"
            ],
            "OWNER_REVIEW_READY",
            reason=(
                "attempt_before_risk"
            ),
            path=database,
        )


def test_obeng009_manual_live_bridge_is_reused_but_locked_until_fit_and_mode():
    from web.ob_trade_intent import (
        build_trade_intent,
        manual_live_handoff_payload,
    )

    intent = build_trade_intent(
        {
            "candidate":
                candidate_fixture(),

            "options_research":
                options_fixture(),
        }
    )

    with pytest.raises(
        ValueError,
        match="Manual Live bridge is locked"
    ):
        manual_live_handoff_payload(
            intent,
            owner_id="owner",
        )

    manual_source = text(
        MANUAL
    )

    assert (
        "candidate_fingerprint"
        in manual_source
    )

    assert (
        "handoff_hash"
        in manual_source
    )

    assert (
        "real_owner_decision_state"
        in manual_source
    )


def test_obeng010_existing_authority_feed_exposes_trade_intent_contract():
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

    payload = (
        response.get_json()
    )

    trade_intent = (
        payload[
            "authority_registry"
        ][
            "trade_intent"
        ]
    )

    assert (
        trade_intent[
            "authority"
        ]
        ==
        "OB_TRADE_INTENT_V1"
    )

    assert (
        trade_intent[
            "candidate_authority"
        ]
        ==
        "existing_canonical_engine_feed"
    )

    assert (
        trade_intent[
            "options_research_authority"
        ]
        ==
        "OB_OPTIONS_RESEARCH_V1"
    )

    assert (
        trade_intent[
            "automatic_contract_selection"
        ]
        is False
    )

    assert (
        trade_intent[
            "broker_submission"
        ]
        is False
    )

    assert (
        trade_intent[
            "automatic_execution"
        ]
        is False
    )


def test_obeng010_old_unapproved_engine_url_stays_fail_closed():
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


def test_obeng010_no_trade_intent_public_route_or_tower_change():
    app_source = text(
        APP
    )

    intent_source = text(
        TRADE_INTENT
    )

    guard_source = text(
        TOWER_GUARD
    )

    assert (
        '@app.route("/ob/trade-intent'
        not in app_source
    )

    assert (
        "@app.route("
        not in intent_source
    )

    assert (
        '"/ob/engine-feed-snapshot.json"'
        not in guard_source
    )

    assert (
        "if not is_approved_ob_web_room(path):"
        in guard_source
    )

    assert (
        "abort(403)"
        in guard_source
    )


def test_obeng010_execution_boundaries_remain_locked():
    from web.ob_trade_intent import (
        trade_intent_contract,
    )

    boundaries = (
        trade_intent_contract()[
            "boundaries"
        ]
    )

    assert (
        boundaries[
            "second_engine_created"
        ]
        is False
    )

    assert (
        boundaries[
            "candidate_recalculation"
        ]
        is False
    )

    assert (
        boundaries[
            "owner_fit_auto_assumed"
        ]
        is False
    )

    assert (
        boundaries[
            "implicit_account_selection"
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
