
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = (
    Path(__file__).resolve().parents[1]
)

MODULE = (
    ROOT
    / "web/ob_engine_account_authority.py"
)

APP = (
    ROOT / "web/app.py"
)

ADAPTER = (
    ROOT
    / "web/static/ob/ob_engine_feed_adapter.js"
)

OPTIONS = (
    ROOT
    / "web/static/ob/ob_options_research_contract.js"
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
    expires = (
        datetime.now(timezone.utc)
        + timedelta(minutes=10)
    ).isoformat()

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
        ] = expires


def test_obeng001_existing_engine_remains_only_market_candidate_projection():
    from web.ob_engine_account_authority import (
        build_authority_bundle,
    )

    bundle = build_authority_bundle(
        root=ROOT,
    )

    authority = (
        bundle[
            "authority_registry"
        ][
            "market_candidate_truth"
        ]
    )

    assert (
        authority[
            "authority"
        ]
        ==
        "existing_canonical_engine_feed"
    )

    assert (
        authority[
            "adapter_no_second_engine_boundary"
        ]
        is True
    )

    assert (
        authority[
            "calculates_new_candidates"
        ]
        is False
    )

    assert (
        authority[
            "calculates_new_market_scores"
        ]
        is False
    )

    assert (
        authority[
            "second_engine_created"
        ]
        is False
    )


def test_obeng001_options_research_authority_remains_research_only():
    from web.ob_engine_account_authority import (
        build_authority_bundle,
    )

    bundle = build_authority_bundle(
        root=ROOT,
    )

    authority = (
        bundle[
            "authority_registry"
        ][
            "options_research"
        ]
    )

    assert (
        authority[
            "authority"
        ]
        ==
        "OB_OPTIONS_RESEARCH_V1"
    )

    assert (
        authority[
            "research_only"
        ]
        is True
    )

    assert (
        authority[
            "owner_selection_authority"
        ]
        is True
    )

    assert (
        authority[
            "automatic_contract_selection"
        ]
        is False
    )

    assert (
        authority[
            "brokerage_execution"
        ]
        is False
    )

    assert (
        authority[
            "fake_option_fallback"
        ]
        is False
    )


def test_obeng002_account_sources_have_separate_roles():
    from web.ob_engine_account_authority import (
        build_authority_bundle,
    )

    bundle = build_authority_bundle(
        root=ROOT,
    )

    account = (
        bundle[
            "account_authority"
        ]
    )

    assert (
        account[
            "operational_repository_authority"
        ][
            "source"
        ]
        ==
        "data/account_state.json"
    )

    assert (
        account[
            "operational_repository_authority"
        ][
            "claimed_live_broker_truth"
        ]
        is False
    )

    assert (
        account[
            "operational_repository_authority"
        ][
            "broker_reconciled"
        ]
        is False
    )

    assert (
        account[
            "lightweight_snapshot"
        ][
            "may_overwrite_durable_state"
        ]
        is False
    )

    assert (
        account[
            "reporting_account"
        ][
            "may_overwrite_durable_state"
        ]
        is False
    )


def test_obeng002_current_account_disagreement_is_not_silently_merged():
    from web.ob_engine_account_authority import (
        build_authority_bundle,
    )

    bundle = build_authority_bundle(
        root=ROOT,
    )

    account = (
        bundle[
            "account_authority"
        ]
    )

    # At the sealed OBENG parent the lightweight account snapshot and
    # durable account state disagree on overlapping account fields.
    #
    # That disagreement is expected to remain visible until a later
    # explicit reconciliation layer resolves provenance.
    assert (
        account[
            "reconciliation_status"
        ]
        ==
        "conflict"
    )

    assert (
        account[
            "conflict_fields"
        ]
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

    for field in (
        account[
            "conflict_fields"
        ]
    ):
        result = (
            account[
                "overlap_checks"
            ][
                field
            ]
        )

        assert (
            result[
                "status"
            ]
            ==
            "conflict"
        )

        assert (
            result[
                "resolved_value"
            ]
            is None
        )


def test_obeng003_empty_position_sources_do_not_become_fake_zero_truth():
    from web.ob_engine_account_authority import (
        build_authority_bundle,
    )

    bundle = build_authority_bundle(
        root=ROOT,
    )

    positions = (
        bundle[
            "position_authority"
        ]
    )

    assert (
        positions[
            "open_position_records"
        ][
            "empty_or_unreadable_means_zero"
        ]
        is False
    )

    assert (
        positions[
            "closed_position_records"
        ][
            "empty_or_unreadable_means_zero"
        ]
        is False
    )

    assert (
        positions[
            "durable_account_open_position_count"
        ][
            "may_synthesize_position_records"
        ]
        is False
    )

    assert (
        positions[
            "no_synthetic_position_records"
        ]
        is True
    )


def test_obeng003_reporting_is_history_authority_not_operational_override():
    from web.ob_engine_account_authority import (
        build_authority_bundle,
    )

    bundle = build_authority_bundle(
        root=ROOT,
    )

    reporting = (
        bundle[
            "reporting_authority"
        ]
    )

    assert (
        reporting[
            "authority"
        ]
        ==
        "historical_performance_reporting"
    )

    assert (
        reporting[
            "may_override_operational_account_state"
        ]
        is False
    )

    assert (
        reporting[
            "may_authorize_execution"
        ]
        is False
    )

    assert isinstance(
        reporting[
            "ledger_count"
        ],
        int,
    )


def test_obeng004_existing_engine_feed_is_augmented_not_replaced():
    source = text(
        APP
    )

    assert (
        "# OBENG001-005_ENGINE_ACCOUNT_AUTHORITY_WRAP"
        in source
    )

    assert (
        "_obeng001_005_original_engine_feed"
        in source
    )

    assert (
        "_obeng001_005_augment_engine_feed_response"
        in source
    )

    # No new route is created by the OBENG marker block.
    marker_block = source.split(
        "# OBENG001-005_ENGINE_ACCOUNT_AUTHORITY_WRAP",
        1,
    )[1]

    assert (
        '@app.route('
        not in marker_block.split(
            'if __name__',
            1,
        )[0]
    )


def test_obeng004_adapter_projects_server_authority_without_calculation():
    source = text(
        ADAPTER
    )

    assert (
        "OBENG001-005_ACCOUNT_AUTHORITY_PROJECTION"
        in source
    )

    for field in [
        "authority_registry",
        "account_authority",
        "position_authority",
        "reporting_authority",
        "authority_source_registry",
        "authority_boundaries",
    ]:
        assert (
            field
            in source
        )

    assert (
        "This is NOT another engine"
        in source
    )


def test_obeng004_authenticated_market_map_feed_contains_authority_contract():
    from web.app import app

    app.config.update(
        TESTING=True,
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

    assert (
        payload[
            "authority_contract_version"
        ]
        ==
        "OB_ENGINE_ACCOUNT_AUTHORITY_V1"
    )

    assert isinstance(
        payload[
            "authority_registry"
        ],
        dict,
    )

    assert isinstance(
        payload[
            "account_authority"
        ],
        dict,
    )

    assert isinstance(
        payload[
            "position_authority"
        ],
        dict,
    )

    assert isinstance(
        payload[
            "reporting_authority"
        ],
        dict,
    )

    assert (
        payload[
            "authority_boundaries"
        ][
            "second_engine_created"
        ]
        is False
    )

    assert (
        payload[
            "authority_boundaries"
        ][
            "broker_submission"
        ]
        is False
    )

    assert (
        payload[
            "authority_boundaries"
        ][
            "capital_movement"
        ]
        is False
    )

    assert (
        payload[
            "authority_boundaries"
        ][
            "automatic_execution"
        ]
        is False
    )


def test_obeng004_old_unapproved_engine_feed_url_remains_fail_closed():
    from web.app import app

    app.config.update(
        TESTING=True,
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

    # OBFIX006–010 remains intact:
    # unknown /ob/* data URLs are not silently added to the Tower allowlist.
    assert (
        response.status_code
        ==
        403
    )


def test_obeng005_tower_guard_is_unchanged_by_contract():
    guard = text(
        TOWER_GUARD
    )

    assert (
        '"/ob/market-map"'
        in guard
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


def test_obeng005_options_source_preserves_owner_selection_boundary():
    source = text(
        OPTIONS
    )

    assert (
        "OB_OPTIONS_RESEARCH_V1"
        in source
    )

    assert (
        "This module DOES NOT select an option contract"
        in source
    )

    assert (
        "automatic selection"
        in source
    )

    assert (
        "brokerage execution"
        in source
    )

    assert (
        "fake option fallback"
        in source
    )


def test_obeng005_no_execution_authority_was_added():
    from web.ob_engine_account_authority import (
        build_authority_bundle,
    )

    bundle = build_authority_bundle(
        root=ROOT,
    )

    boundaries = (
        bundle[
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
            "market_score_recalculation"
        ]
        is False
    )

    assert (
        boundaries[
            "account_conflict_auto_resolution"
        ]
        is False
    )

    assert (
        boundaries[
            "synthetic_position_records"
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
