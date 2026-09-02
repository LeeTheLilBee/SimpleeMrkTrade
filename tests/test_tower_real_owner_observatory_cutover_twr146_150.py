from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse

import pytest
from flask import Flask

import tower.ob_web_route_enforcement as enforcement
import tower.owner_observatory_handoff as handoff
from tower.app_publication_authority import (
    publication_document,
)
from tower import tower_human_login_ob_launch as launch


def _session_context(
    *,
    now=None,
):

    now = (
        now
        or datetime.now(
            timezone.utc
        )
    )

    return {
        "authenticated":
            True,

        "role":
            "owner",

        "owner_id":
            "owner-test-001",

        "username":
            "owner@example.invalid",

        "authenticated_at":
            (
                now
                - timedelta(
                    minutes=2
                )
            ).isoformat(),

        "step_up_until":
            (
                now
                + timedelta(
                    minutes=10
                )
            ).isoformat(),
    }


def _verified_identity():

    return {
        "verification_state":
            "VERIFIED",

        "configured":
            True,

        "record": {
            "person_id":
                "person-owner-test",

            "account_id":
                "account-owner-test",

            "username":
                "owner@example.invalid",

            "role":
                "owner",
        },

        "app_entitlements": [
            {
                "app_id":
                    "observatory",

                "access_policy":
                    "GRANTED",

                "verification_state":
                    "VERIFIED",
            }
        ],
    }


def _launchable_ob():

    return {
        "app_id":
            "observatory",

        "launchable":
            True,

        "request_authorization_required":
            True,
    }


def _patch_verified_truth(
    monkeypatch,
):

    monkeypatch.setattr(
        handoff,
        "hosted_owner_identity_authority",
        _verified_identity,
    )

    monkeypatch.setattr(
        handoff,
        "app_truth_by_id",
        lambda app_id: (
            _launchable_ob()
            if app_id == "observatory"
            else None
        ),
    )


def _configure_handoff(
    tmp_path,
    monkeypatch,
):

    ledger = (
        tmp_path
        / "tower-ob-handoff.sqlite3"
    )

    monkeypatch.setenv(
        "TOWER_SESSION_SECRET",
        (
            "twr146-test-session-secret-"
            "0123456789abcdef0123456789abcdef"
        ),
    )

    monkeypatch.setenv(
        "TOWER_OB_HANDOFF_LEDGER_PATH",
        str(
            ledger
        ),
    )

    return ledger


def _provider_record(
    app_id,
):

    now = datetime.now(
        timezone.utc
    )

    return {
        "app_id":
            app_id,

        "implemented": {
            "value":
                True,

            "evidence_id":
                "twr146-implemented",
        },

        "published": {
            "value":
                True,

            "evidence_id":
                "twr146-published",
        },

        "environment_available": {
            "value":
                True,

            "receipt_id":
                "twr146-availability",

            "observed_at_utc":
                (
                    now
                    - timedelta(
                        minutes=1
                    )
                ).isoformat(),

            "fresh_until_utc":
                (
                    now
                    + timedelta(
                        minutes=15
                    )
                ).isoformat(),
        },

        "health_verified": {
            "value":
                True,

            "receipt_id":
                "twr146-health",

            "observed_at_utc":
                (
                    now
                    - timedelta(
                        minutes=1
                    )
                ).isoformat(),

            "fresh_until_utc":
                (
                    now
                    + timedelta(
                        minutes=15
                    )
                ).isoformat(),
        },
    }


def _configure_real_authority(
    tmp_path,
    monkeypatch,
):

    monkeypatch.setenv(
        "TOWER_OWNER_USERNAME",
        "owner@example.invalid",
    )

    monkeypatch.setenv(
        "TOWER_OWNER_PASSWORD_HASH",
        "configured-secret-hash-not-projected",
    )

    monkeypatch.setenv(
        "TOWER_OWNER_ID",
        "owner-test-001",
    )

    monkeypatch.delenv(
        "TOWER_LOCAL_WALKTHROUGH_MODE",
        raising=False,
    )

    document = publication_document({
        "observatory":
            _provider_record(
                "observatory"
            )
    })

    provider = (
        tmp_path
        / "tower-app-publication.json"
    )

    provider.write_text(
        json.dumps(
            document,
            sort_keys=True,
            indent=2,
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv(
        "TOWER_APP_PUBLICATION_STATE_PATH",
        str(
            provider
        ),
    )


def _build_real_app():

    app = Flask(
        __name__
    )

    app.secret_key = (
        "twr146-flask-secret-"
        "0123456789abcdef0123456789abcdef"
    )

    app.config[
        "TESTING"
    ] = True

    app.register_blueprint(
        launch.tower_human_login_bp
    )

    @app.route(
        "/ob/dashboard"
    )
    def dashboard():

        return "REAL OBSERVATORY DASHBOARD"

    enforcement.register_ob_protected_route_enforcement(
        app
    )

    return app


def _seed_owner_session(
    client,
):

    now = datetime.now(
        timezone.utc
    )

    with client.session_transaction() as sess:

        sess[
            launch.SESSION_AUTHENTICATED
        ] = True

        sess[
            launch.SESSION_ROLE
        ] = "owner"

        sess[
            launch.SESSION_OWNER_ID
        ] = "owner-test-001"

        sess[
            launch.SESSION_USERNAME
        ] = "owner@example.invalid"

        sess[
            launch.SESSION_AUTH_TIME
        ] = (
            now
            - timedelta(
                minutes=2
            )
        ).isoformat()

        sess[
            launch.SESSION_STEP_UP_UNTIL
        ] = (
            now
            + timedelta(
                minutes=10
            )
        ).isoformat()


def test_twr146_operational_handoff_requires_explicit_configuration(
    monkeypatch,
):

    monkeypatch.delenv(
        "TOWER_SESSION_SECRET",
        raising=False,
    )

    monkeypatch.delenv(
        "TOWER_OB_HANDOFF_LEDGER_PATH",
        raising=False,
    )

    status = (
        handoff.handoff_configuration_status()
    )

    assert status[
        "configured"
    ] is False

    assert status[
        "session_secret_exposed"
    ] is False

    assert status[
        "ledger_path_exposed"
    ] is False

    assert status[
        "raw_handoff_code_persisted"
    ] is False


def test_twr146_issue_requires_verified_current_owner_truth(
    tmp_path,
    monkeypatch,
):

    _configure_handoff(
        tmp_path,
        monkeypatch,
    )

    monkeypatch.setattr(
        handoff,
        "hosted_owner_identity_authority",
        lambda: {
            "verification_state":
                "NOT_CONFIGURED",

            "configured":
                False,

            "record":
                None,
        },
    )

    monkeypatch.setattr(
        handoff,
        "app_truth_by_id",
        lambda _app_id:
            _launchable_ob(),
    )

    with pytest.raises(
        handoff.OwnerObservatoryHandoffError,
        match=(
            "owner_observatory_identity_not_verified"
        ),
    ):

        handoff.issue_owner_observatory_handoff(
            _session_context()
        )


def test_twr146_issue_requires_verified_app_launchability(
    tmp_path,
    monkeypatch,
):

    _configure_handoff(
        tmp_path,
        monkeypatch,
    )

    monkeypatch.setattr(
        handoff,
        "hosted_owner_identity_authority",
        _verified_identity,
    )

    monkeypatch.setattr(
        handoff,
        "app_truth_by_id",
        lambda _app_id: {
            "app_id":
                "observatory",

            "launchable":
                False,

            "request_authorization_required":
                True,
        },
    )

    with pytest.raises(
        handoff.OwnerObservatoryHandoffError,
        match=(
            "owner_observatory_app_not_launchable"
        ),
    ):

        handoff.issue_owner_observatory_handoff(
            _session_context()
        )


def test_twr147_opaque_code_hash_only_is_persisted(
    tmp_path,
    monkeypatch,
):

    ledger = _configure_handoff(
        tmp_path,
        monkeypatch,
    )

    _patch_verified_truth(
        monkeypatch
    )

    issued = (
        handoff.issue_owner_observatory_handoff(
            _session_context()
        )
    )

    raw_code = issued[
        "code"
    ]

    connection = sqlite3.connect(
        str(
            ledger
        )
    )

    row = connection.execute(
        """
        SELECT
            code_hash,
            payload_json,
            payload_signature
        FROM tower_owner_observatory_handoff
        """
    ).fetchone()

    connection.close()

    assert row is not None

    assert (
        row[0]
        != raw_code
    )

    assert (
        raw_code
        not in row[0]
    )

    assert (
        raw_code
        not in row[1]
    )

    assert (
        raw_code
        not in row[2]
    )

    assert (
        issued[
            "raw_code_persisted"
        ]
        is False
    )


def test_twr147_handoff_consumes_exactly_once(
    tmp_path,
    monkeypatch,
):

    _configure_handoff(
        tmp_path,
        monkeypatch,
    )

    _patch_verified_truth(
        monkeypatch
    )

    context = (
        _session_context()
    )

    issued = (
        handoff.issue_owner_observatory_handoff(
            context
        )
    )

    receipt = (
        handoff.consume_owner_observatory_handoff(
            issued[
                "code"
            ],
            context,
        )
    )

    assert (
        receipt[
            "payload"
        ][
            "handoff_consumed"
        ]
        is True
    )

    with pytest.raises(
        handoff.OwnerObservatoryHandoffError,
        match=(
            "owner_observatory_handoff_replay_rejected"
        ),
    ):

        handoff.consume_owner_observatory_handoff(
            issued[
                "code"
            ],
            context,
        )


def test_twr147_unknown_code_fails_closed(
    tmp_path,
    monkeypatch,
):

    _configure_handoff(
        tmp_path,
        monkeypatch,
    )

    _patch_verified_truth(
        monkeypatch
    )

    with pytest.raises(
        handoff.OwnerObservatoryHandoffError,
        match=(
            "owner_observatory_handoff_not_found"
        ),
    ):

        handoff.consume_owner_observatory_handoff(
            "not-a-real-handoff-code",
            _session_context(),
        )


def test_twr148_receipt_is_bound_to_exact_owner_session(
    tmp_path,
    monkeypatch,
):

    _configure_handoff(
        tmp_path,
        monkeypatch,
    )

    _patch_verified_truth(
        monkeypatch
    )

    context = (
        _session_context()
    )

    issued = (
        handoff.issue_owner_observatory_handoff(
            context
        )
    )

    receipt = (
        handoff.consume_owner_observatory_handoff(
            issued[
                "code"
            ],
            context,
        )
    )

    assert (
        handoff.validate_owner_observatory_access_receipt(
            receipt,
            context,
        )
        is True
    )

    changed = dict(
        context
    )

    changed[
        "owner_id"
    ] = (
        "different-owner-session"
    )

    assert (
        handoff.validate_owner_observatory_access_receipt(
            receipt,
            changed,
        )
        is False
    )


def test_twr148_receiver_rechecks_current_app_truth(
    tmp_path,
    monkeypatch,
):

    _configure_handoff(
        tmp_path,
        monkeypatch,
    )

    _patch_verified_truth(
        monkeypatch
    )

    context = (
        _session_context()
    )

    issued = (
        handoff.issue_owner_observatory_handoff(
            context
        )
    )

    monkeypatch.setattr(
        handoff,
        "app_truth_by_id",
        lambda _app_id: {
            "app_id":
                "observatory",

            "launchable":
                False,

            "request_authorization_required":
                True,
        },
    )

    with pytest.raises(
        handoff.OwnerObservatoryHandoffError,
        match=(
            "owner_observatory_app_not_launchable"
        ),
    ):

        handoff.consume_owner_observatory_handoff(
            issued[
                "code"
            ],
            context,
        )


def test_twr149_direct_normal_ob_room_requires_consumed_operational_handoff(
    monkeypatch,
):

    app = Flask(
        __name__
    )

    app.secret_key = (
        "twr149-route-test"
    )

    @app.route(
        "/ob/dashboard"
    )
    def dashboard():

        return "DASHBOARD"

    @app.route(
        "/tower/login"
    )
    def login():

        return "LOGIN"

    @app.route(
        "/tower/access-home"
    )
    def access_home():

        return "HOME"

    @app.route(
        "/tower/launch/observatory"
    )
    def launch_ob():

        return "LAUNCH"

    monkeypatch.setattr(
        enforcement,
        "owner_session_active",
        lambda:
            True,
    )

    monkeypatch.setattr(
        enforcement,
        "step_up_active",
        lambda:
            True,
    )

    monkeypatch.setattr(
        enforcement,
        "operational_ob_access_active",
        lambda:
            False,
    )

    enforcement.register_ob_protected_route_enforcement(
        app
    )

    response = (
        app.test_client().get(
            "/ob/dashboard",
            follow_redirects=False,
        )
    )

    assert response.status_code in {
        301,
        302,
        303,
        307,
        308,
    }

    assert response.headers[
        "Location"
    ].endswith(
        "/tower/launch/observatory"
    )


def test_twr150_real_end_to_end_owner_cutover_reaches_actual_ob_dashboard(
    tmp_path,
    monkeypatch,
):

    _configure_handoff(
        tmp_path,
        monkeypatch,
    )

    _configure_real_authority(
        tmp_path,
        monkeypatch,
    )

    app = (
        _build_real_app()
    )

    client = (
        app.test_client()
    )

    _seed_owner_session(
        client
    )

    # Even with owner session + step-up, direct normal OB entry
    # is denied until the real handoff is consumed.
    direct = client.get(
        "/ob/dashboard",
        follow_redirects=False,
    )

    assert direct.status_code in {
        301,
        302,
        303,
        307,
        308,
    }

    assert direct.headers[
        "Location"
    ].endswith(
        "/tower/launch/observatory"
    )

    launch_response = (
        client.get(
            "/tower/launch/observatory",
            follow_redirects=False,
        )
    )

    assert launch_response.status_code in {
        301,
        302,
        303,
        307,
        308,
    }

    location = (
        launch_response.headers[
            "Location"
        ]
    )

    parsed = urlparse(
        location
    )

    assert (
        parsed.path
        == launch.TOWER_OPERATIONAL_OB_RECEIVE_PATH
    )

    assert (
        "observatory-walkthrough"
        not in location
    )

    code = parse_qs(
        parsed.query
    )[
        "code"
    ][0]

    assert code

    receive = client.get(
        location,
        follow_redirects=False,
    )

    assert receive.status_code in {
        301,
        302,
        303,
        307,
        308,
    }

    assert receive.headers[
        "Location"
    ].endswith(
        "/ob/dashboard"
    )

    dashboard = client.get(
        "/ob/dashboard",
        follow_redirects=False,
    )

    assert dashboard.status_code == 200

    assert (
        b"REAL OBSERVATORY DASHBOARD"
        in dashboard.data
    )

    # One-time means one-time.
    replay = client.get(
        location,
        follow_redirects=False,
    )

    assert replay.status_code == 403


def test_twr150_public_launch_never_falls_back_to_walkthrough_when_app_truth_missing(
    tmp_path,
    monkeypatch,
):

    _configure_handoff(
        tmp_path,
        monkeypatch,
    )

    monkeypatch.setenv(
        "TOWER_OWNER_USERNAME",
        "owner@example.invalid",
    )

    monkeypatch.setenv(
        "TOWER_OWNER_PASSWORD_HASH",
        "configured-secret-hash-not-projected",
    )

    monkeypatch.setenv(
        "TOWER_OWNER_ID",
        "owner-test-001",
    )

    monkeypatch.delenv(
        "TOWER_APP_PUBLICATION_STATE_PATH",
        raising=False,
    )

    monkeypatch.delenv(
        "TOWER_LOCAL_WALKTHROUGH_MODE",
        raising=False,
    )

    app = (
        _build_real_app()
    )

    client = (
        app.test_client()
    )

    _seed_owner_session(
        client
    )

    response = client.get(
        "/tower/launch/observatory",
        follow_redirects=False,
    )

    assert response.status_code == 503

    assert (
        "observatory-walkthrough"
        not in response.headers.get(
            "Location",
            "",
        )
    )

    assert (
        b"Observatory launch is blocked"
        in response.data
    )


def test_twr150_historical_gp046_contract_remains_available_backstage():

    assert hasattr(
        launch,
        "launch_observatory_rehearsal_contract",
    )

    assert callable(
        launch.launch_observatory_rehearsal_contract
    )


def test_twr150_operational_access_receipt_never_unlocks_execution(
    tmp_path,
    monkeypatch,
):

    _configure_handoff(
        tmp_path,
        monkeypatch,
    )

    _patch_verified_truth(
        monkeypatch
    )

    context = (
        _session_context()
    )

    issued = (
        handoff.issue_owner_observatory_handoff(
            context
        )
    )

    receipt = (
        handoff.consume_owner_observatory_handoff(
            issued[
                "code"
            ],
            context,
        )
    )

    payload = receipt[
        "payload"
    ]

    assert (
        payload[
            "broker_submission_authorized"
        ]
        is False
    )

    assert (
        payload[
            "capital_movement_authorized"
        ]
        is False
    )

    assert (
        payload[
            "manual_live_authorized"
        ]
        is False
    )

    assert (
        payload[
            "live_auto_authorized"
        ]
        is False
    )
