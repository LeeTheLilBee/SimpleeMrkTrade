from __future__ import annotations

import json

from datetime import (
    datetime,
    timedelta,
    timezone,
)

from urllib.parse import (
    parse_qs,
    urlsplit,
)

from flask import Flask

import tower.identity_authority as identity

from tower.app_publication_authority import (
    TOWER_APP_PUBLICATION_STATE_PATH_ENV,
    publication_document,
)

from tower.app_registry import (
    registered_apps,
    route_by_path,
)

from tower.app_truth_projection import (
    app_truth_by_id,
)

from tower.teller_handoff_web import (
    TOWER_TELLER_ALLOWED_ORIGIN_ENV,
    TOWER_TELLER_EXCHANGE_PATH,
    register_teller_handoff_web,
)

from tower.teller_owner_entitlement_reservation import (
    teller_owner_entitlement_reservation,
)

from tower.teller_owner_launch import (
    TELLER_LAUNCH_PATH,
    TELLER_STEP_UP_PATH,
    TOWER_TELLER_WEB_URL_ENV,
    register_teller_owner_launch_web,
)

from tower.tower_human_login_ob_launch import (
    SESSION_AUTHENTICATED,
    SESSION_AUTH_TIME,
    SESSION_OWNER_ID,
    SESSION_ROLE,
    SESSION_STEP_UP_UNTIL,
    SESSION_USERNAME,
    tower_human_login_bp,
)


TELLER_ORIGIN = (
    "https://teller.example.test"
)

TELLER_WEB_URL = (
    "https://teller.example.test/teller"
)


def configure_owner(
    monkeypatch,
):

    monkeypatch.setenv(
        identity.TOWER_OWNER_USERNAME_ENV,
        "twr190-owner",
    )

    monkeypatch.setenv(
        identity.TOWER_OWNER_PASSWORD_HASH_ENV,
        "test-hash",
    )

    monkeypatch.setenv(
        identity.TOWER_OWNER_ID_ENV,
        "twr190-owner-id",
    )

    monkeypatch.delenv(
        identity.TOWER_LOCAL_WALKTHROUGH_MODE_ENV,
        raising=False,
    )

    monkeypatch.setenv(
        "TOWER_SESSION_SECRET",
        (
            "twr190-session-secret-"
            "0123456789abcdef"
            "0123456789abcdef"
        ),
    )

    monkeypatch.setenv(
        TOWER_TELLER_ALLOWED_ORIGIN_ENV,
        TELLER_ORIGIN,
    )

    monkeypatch.setenv(
        TOWER_TELLER_WEB_URL_ENV,
        TELLER_WEB_URL,
    )


def write_teller_publication(
    tmp_path,
    monkeypatch,
):

    now = datetime.now(
        timezone.utc
    )

    observed = (
        now
        - timedelta(
            minutes=1
        )
    ).isoformat()

    fresh_until = (
        now
        + timedelta(
            minutes=30
        )
    ).isoformat()

    document = publication_document({
        "teller": {
            "app_id":
                "teller",

            "implemented": {
                "value":
                    True,

                "evidence_id":
                    "twr190-teller-implemented",
            },

            "published": {
                "value":
                    True,

                "evidence_id":
                    "twr190-teller-published",
            },

            "environment_available": {
                "value":
                    True,

                "receipt_id":
                    "twr190-teller-availability",

                "observed_at_utc":
                    observed,

                "fresh_until_utc":
                    fresh_until,
            },

            "health_verified": {
                "value":
                    True,

                "receipt_id":
                    "twr190-teller-health",

                "observed_at_utc":
                    observed,

                "fresh_until_utc":
                    fresh_until,
            },
        },
    })

    path = (
        tmp_path
        / "twr190-publication.json"
    )

    path.write_text(
        json.dumps(
            document,
            sort_keys=True,
            indent=2,
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv(
        TOWER_APP_PUBLICATION_STATE_PATH_ENV,
        str(path),
    )


def app():

    value = Flask(
        __name__
    )

    value.config[
        "TESTING"
    ] = True

    value.secret_key = (
        "twr190-flask-secret"
    )

    value.register_blueprint(
        tower_human_login_bp
    )

    register_teller_handoff_web(
        value
    )

    register_teller_owner_launch_web(
        value
    )

    return value


def establish_owner_session(
    client,
    *,
    step_up=True,
):

    now = datetime.now(
        timezone.utc
    )

    with client.session_transaction() as sess:

        sess[
            SESSION_AUTHENTICATED
        ] = True

        sess[
            SESSION_ROLE
        ] = "owner"

        sess[
            SESSION_OWNER_ID
        ] = "twr190-owner-id"

        sess[
            SESSION_USERNAME
        ] = "twr190-owner"

        sess[
            SESSION_AUTH_TIME
        ] = (
            now
            - timedelta(
                minutes=1
            )
        ).isoformat()

        if step_up:

            sess[
                SESSION_STEP_UP_UNTIL
            ] = (
                now
                + timedelta(
                    minutes=10
                )
            ).isoformat()


def test_twr190_registry_route_and_entitlement_are_active(
    monkeypatch,
):

    configure_owner(
        monkeypatch
    )

    teller = next(
        app
        for app in registered_apps()
        if app["app_id"]
        == "teller"
    )

    route = route_by_path(
        TELLER_LAUNCH_PATH
    )

    entitlement = (
        teller_owner_entitlement_reservation()
    )

    authority = (
        identity
        .hosted_owner_identity_authority()
    )

    app_ids = [
        item["app_id"]
        for item in authority[
            "app_entitlements"
        ]
    ]

    assert teller["app_status"] == "protected_hosted"
    assert teller["tower_launch_route"] == TELLER_LAUNCH_PATH

    assert route is not None
    assert route["temporary_placeholder"] is False
    assert route["requires_owner_session"] is True
    assert route["requires_step_up"] is True

    assert entitlement["reservation_state"] == "ACTIVATED"
    assert entitlement["effective_entitlement"] is True

    assert app_ids == [
        "observatory",
        "teller",
    ]


def test_twr190_publication_truth_can_make_teller_product_launchable(
    tmp_path,
    monkeypatch,
):

    configure_owner(
        monkeypatch
    )

    write_teller_publication(
        tmp_path,
        monkeypatch,
    )

    truth = app_truth_by_id(
        "teller"
    )

    assert truth["registry_status"] == "protected_hosted"

    assert (
        truth["dimensions"]
        ["user_entitled"]
        ["value"]
        is True
    )

    assert (
        truth["dimensions"]
        ["launch_route_configured"]
        ["value"]
        is True
    )

    assert truth["launchable"] is True

    assert (
        truth["safety"]
        ["live_auto_locked"]
        ["value"]
        is True
    )

    assert (
        truth["safety"]
        ["broker_execution_enabled"]
        ["value"]
        is False
    )

    assert (
        truth["safety"]
        ["capital_action_enabled"]
        ["value"]
        is False
    )


def test_twr190_missing_publication_truth_blocks_external_launch(
    monkeypatch,
):

    configure_owner(
        monkeypatch
    )

    monkeypatch.delenv(
        TOWER_APP_PUBLICATION_STATE_PATH_ENV,
        raising=False,
    )

    with app().test_client() as client:

        establish_owner_session(
            client,
            step_up=True,
        )

        response = client.get(
            TELLER_LAUNCH_PATH
        )

    assert response.status_code == 503

    assert (
        b"tower_teller_publication_truth_not_launchable"
        in response.data
    )


def test_twr190_missing_step_up_redirects_to_teller_step_up(
    tmp_path,
    monkeypatch,
):

    configure_owner(
        monkeypatch
    )

    write_teller_publication(
        tmp_path,
        monkeypatch,
    )

    with app().test_client() as client:

        establish_owner_session(
            client,
            step_up=False,
        )

        response = client.get(
            TELLER_LAUNCH_PATH
        )

    assert response.status_code == 302

    assert (
        TELLER_STEP_UP_PATH
        in response.headers[
            "Location"
        ]
    )


def test_twr190_real_launch_issues_exchangeable_one_time_handoff(
    tmp_path,
    monkeypatch,
):

    configure_owner(
        monkeypatch
    )

    write_teller_publication(
        tmp_path,
        monkeypatch,
    )

    with app().test_client() as client:

        establish_owner_session(
            client,
            step_up=True,
        )

        launched = client.get(
            TELLER_LAUNCH_PATH
        )

        assert launched.status_code == 302

        location = (
            launched.headers[
                "Location"
            ]
        )

        parsed = urlsplit(
            location
        )

        assert (
            f"{parsed.scheme}://{parsed.netloc}"
            == TELLER_ORIGIN
        )

        assert parsed.path == "/teller"

        fragment = parse_qs(
            parsed.fragment
        )

        code = fragment[
            "tower_handoff"
        ][0]

        exchanged = client.post(
            TOWER_TELLER_EXCHANGE_PATH,

            headers={
                "Origin":
                    TELLER_ORIGIN,
            },

            json={
                "handoff_code":
                    code,

                "client":
                    "the-teller",

                "exchange_version":
                    "tower-teller-exchange.v1",
            },
        )

        assert exchanged.status_code == 200

        body = exchanged.get_json()

        assert body["access_verified"] is True
        assert body["app_id"] == "teller"
        assert body["role"] == "owner"
        assert body["target_path"] == "/teller"

        assert (
            body["navigation_context"]
            ["source_app"]
            == "tower"
        )

        assert (
            body["navigation_context"]
            ["destination"]
            == "owner_money_workspace"
        )

        assert (
            body["navigation_context"]
            ["return_app"]
            == "tower"
        )

        assert (
            body["navigation_context"]
            ["return_destination"]
            == "access_home"
        )

        replay = client.post(
            TOWER_TELLER_EXCHANGE_PATH,

            headers={
                "Origin":
                    TELLER_ORIGIN,
            },

            json={
                "handoff_code":
                    code,

                "client":
                    "the-teller",

                "exchange_version":
                    "tower-teller-exchange.v1",
            },
        )

        assert replay.status_code == 403


def test_twr190_unsafe_teller_web_url_fails_closed(
    tmp_path,
    monkeypatch,
):

    configure_owner(
        monkeypatch
    )

    write_teller_publication(
        tmp_path,
        monkeypatch,
    )

    monkeypatch.setenv(
        TOWER_TELLER_WEB_URL_ENV,
        "http://teller.example.test/teller",
    )

    with app().test_client() as client:

        establish_owner_session(
            client,
            step_up=True,
        )

        response = client.get(
            TELLER_LAUNCH_PATH
        )

    assert response.status_code == 503

    assert (
        b"tower_teller_web_url_invalid"
        in response.data
    )


def test_twr190_access_home_exposes_real_teller_door(
    monkeypatch,
):

    configure_owner(
        monkeypatch
    )

    with app().test_client() as client:

        establish_owner_session(
            client,
            step_up=False,
        )

        response = client.get(
            "/tower/access-home"
        )

    assert response.status_code == 200

    html = response.get_data(
        as_text=True
    )

    assert "The Teller" in html
    assert "/tower/launch/teller" in html
    assert "Enter The Teller" in html
