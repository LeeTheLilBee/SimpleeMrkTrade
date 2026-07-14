import os

import pytest
from flask import Flask

from tower.tower_human_login_ob_launch import (
    ACCESS_HOME_PATH,
    LOGIN_PATH,
    LOGOUT_PATH,
    OBSERVATORY_LAUNCH_PATH,
    OBSERVATORY_STEP_UP_PATH,
    SESSION_AUTHENTICATED,
    SESSION_OB_LAUNCH_RECEIPT,
    SESSION_OWNER_ID,
    SESSION_ROLE,
    register_tower_human_login,
)


@pytest.fixture()
def app(monkeypatch):
    monkeypatch.setenv(
        "TOWER_LOCAL_WALKTHROUGH_MODE",
        "true",
    )

    monkeypatch.setenv(
        "TOWER_OWNER_USERNAME",
        "solice",
    )

    monkeypatch.setenv(
        "TOWER_LOCAL_OWNER_PASSWORD",
        "local-test-password",
    )

    monkeypatch.setenv(
        "TOWER_SESSION_SECRET",
        "test-session-secret",
    )

    monkeypatch.setenv(
        "TOWER_OWNER_ID",
        "owner_solice",
    )

    app = Flask(__name__)

    app.config.update(
        TESTING=True,
    )

    register_tower_human_login(
        app
    )

    @app.get(
        "/tower/observatory-walkthrough"
    )
    def walkthrough():
        return "Protected Observatory Walkthrough"

    return app


@pytest.fixture()
def client(app):
    return app.test_client()


def login(client):
    return client.post(
        LOGIN_PATH,
        data={
            "username": "solice",
            "password": (
                "local-test-password"
            ),
        },
        follow_redirects=False,
    )


def test_real_login_form(client):
    response = client.get(
        LOGIN_PATH
    )

    assert response.status_code == 200

    body = response.get_data(
        as_text=True
    )

    assert "Enter The Tower" in body
    assert "Owner username" in body
    assert "Owner password" in body


def test_invalid_login_is_denied(client):
    response = client.post(
        LOGIN_PATH,
        data={
            "username": "solice",
            "password": "wrong",
        },
    )

    assert response.status_code == 200

    assert (
        "could not verify"
        in response.get_data(
            as_text=True
        )
    )

    with client.session_transaction() as session:
        assert session.get(
            SESSION_AUTHENTICATED
        ) is not True


def test_login_establishes_owner_session(client):
    response = login(
        client
    )

    assert response.status_code == 302
    assert response.headers[
        "Location"
    ].endswith(
        ACCESS_HOME_PATH
    )

    with client.session_transaction() as session:
        assert session[
            SESSION_AUTHENTICATED
        ] is True

        assert session[
            SESSION_ROLE
        ] == "owner"

        assert session[
            SESSION_OWNER_ID
        ] == "owner_solice"


def test_access_home_requires_login(client):
    response = client.get(
        ACCESS_HOME_PATH
    )

    assert response.status_code == 302
    assert LOGIN_PATH in response.headers[
        "Location"
    ]


def test_access_home_has_ob_launch(client):
    login(
        client
    )

    response = client.get(
        ACCESS_HOME_PATH
    )

    assert response.status_code == 200

    body = response.get_data(
        as_text=True
    )

    assert "Tower Access Home" in body
    assert "The Observatory" in body
    assert "Open The Observatory" in body
    assert OBSERVATORY_LAUNCH_PATH in body


def test_ob_launch_requires_step_up(client):
    login(
        client
    )

    response = client.get(
        OBSERVATORY_LAUNCH_PATH
    )

    assert response.status_code == 302
    assert OBSERVATORY_STEP_UP_PATH in (
        response.headers["Location"]
    )


def test_step_up_then_launches_ob(client):
    login(
        client
    )

    response = client.post(
        OBSERVATORY_STEP_UP_PATH,
        data={
            "password": (
                "local-test-password"
            ),
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers[
        "Location"
    ].endswith(
        OBSERVATORY_LAUNCH_PATH
    )

    launch = client.get(
        OBSERVATORY_LAUNCH_PATH,
        follow_redirects=False,
    )

    assert launch.status_code == 302

    assert launch.headers[
        "Location"
    ].endswith(
        "/tower/observatory-walkthrough"
    )

    with client.session_transaction() as session:
        receipt = session[
            SESSION_OB_LAUNCH_RECEIPT
        ]

        assert receipt[
            "step_up_verified"
        ] is True

        assert receipt[
            "broker_submission"
        ] is False

        assert receipt[
            "capital_movement"
        ] is False


def test_logout_clears_session(client):
    login(
        client
    )

    response = client.get(
        LOGOUT_PATH
    )

    assert response.status_code == 302

    with client.session_transaction() as session:
        assert session.get(
            SESSION_AUTHENTICATED
        ) is None

        assert session.get(
            SESSION_ROLE
        ) is None

        assert session.get(
            SESSION_OWNER_ID
        ) is None

# BEGIN HUMAN LOGIN CERT ROUTE TESTS

def test_human_login_cert_routes_deny_anonymous(
    client,
):
    for pack in range(
        2503,
        2513,
    ):
        response = client.get(
            f"/tower/ir-cert-v{pack}.json"
        )

        assert response.status_code == 403

        payload = response.get_json()

        assert payload[
            "allowed"
        ] is False

        assert payload[
            "reason_code"
        ] == (
            "tower_owner_session_required"
        )


def test_human_login_cert_routes_allow_owner(
    client,
):
    login(
        client
    )

    for pack in range(
        2503,
        2513,
    ):
        response = client.get(
            f"/tower/ir-cert-v{pack}.json"
        )

        assert response.status_code == 200

        payload = response.get_json()

        assert payload[
            "pack"
        ] == str(pack)

        assert payload[
            "status"
        ] == "ready"

        assert payload[
            "readiness"
        ] == 100

        assert payload[
            "credentials_committed"
        ] is False

        assert payload[
            "test_session_injection_required"
        ] is False


# END HUMAN LOGIN CERT ROUTE TESTS
