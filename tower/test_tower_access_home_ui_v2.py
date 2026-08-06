import pytest
from flask import Flask

from tower.tower_human_login_ob_launch import (
    ACCESS_HOME_PATH,
    LOGIN_PATH,
    OBSERVATORY_LAUNCH_PATH,
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
    app.config.update(TESTING=True)

    register_tower_human_login(app)

    @app.get(
        "/tower/observatory-walkthrough"
    )
    def walkthrough():
        return """
        <html>
        <body>
            <h1>Observatory Walkthrough</h1>
        </body>
        </html>
        """

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


def test_access_home_v2_requires_owner(client):
    response = client.get(
        ACCESS_HOME_PATH
    )

    assert response.status_code == 302
    assert "/tower/login" in response.headers[
        "Location"
    ]


def test_access_home_v2_renders_front_door(client):
    login(client)

    response = client.get(
        ACCESS_HOME_PATH
    )

    assert response.status_code == 200

    body = response.get_data(
        as_text=True
    )

    assert "Tower Access Command Center" in body
    assert "Welcome back, solice." in body
    assert "Access Hub" in body
    assert "The Observatory" in body
    assert "Archive Vault" in body
    assert "The Teller" in body
    assert "The Grounds" in body
    assert "The Clouds" in body
    assert "Owner Actions" in body
    assert "Quick Launch" in body
    assert "Evidence drawers" in body
    assert "<details" in body
    assert "Proof stays available" in body
    assert "Open Observatory" in body


def test_ob_return_preserves_owner_session(client):
    login(client)

    response = client.get(
        "/tower/return/observatory?last_room=Market%20Map",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers[
        "Location"
    ].endswith(
        ACCESS_HOME_PATH
    )

    home = client.get(
        ACCESS_HOME_PATH
    )

    assert home.status_code == 200

    body = home.get_data(
        as_text=True
    )

    assert (
        "Returned from The Observatory. Owner session preserved."
        in body
    )

    assert "Market Map" in body


def test_ob_return_json_receipt(client):
    login(client)

    response = client.get(
        "/tower/return/observatory.json?last_room=Review%20Center"
    )

    assert response.status_code == 200

    payload = response.get_json()

    assert payload["allowed"] is True
    assert payload[
        "owner_session_preserved"
    ] is True
    assert payload[
        "clearance_preserved"
    ] is True
    assert payload[
        "dangerous_action_unlocked"
    ] is False
    assert payload[
        "broker_submission"
    ] is False
    assert payload[
        "capital_movement"
    ] is False

    receipt = payload["return_receipt"]

    assert receipt[
        "last_room"
    ] == "Review Center"

    assert receipt[
        "owner_session_preserved"
    ] is True

    assert receipt[
        "receipt_hash"
    ]


def test_access_home_v2_contract_json(client):
    login(client)

    response = client.get(
        "/tower/access-home/v2-contract.json"
    )

    assert response.status_code == 200

    payload = response.get_json()

    assert payload[
        "clean_access_home"
    ] is True
    assert payload[
        "app_launch_cards"
    ] is True
    assert payload[
        "hidden_evidence_drawers"
    ] is True
    assert payload[
        "proof_page_main_experience"
    ] is False
    assert payload[
        "list_heavy_main_surface"
    ] is False
    assert payload[
        "broker_submission"
    ] is False


def test_ob_pages_get_return_chip_after_login_and_stepup(client):
    login(client)

    client.post(
        "/tower/step-up/observatory",
        data={
            "password": (
                "local-test-password"
            ),
        },
        follow_redirects=False,
    )

    launch = client.get(
        OBSERVATORY_LAUNCH_PATH,
        follow_redirects=False,
    )

    assert launch.status_code == 302

    walkthrough = client.get(
        "/tower/observatory-walkthrough"
    )

    assert walkthrough.status_code == 200

    body = walkthrough.get_data(
        as_text=True
    )

    assert "Go back to Tower" in body
    assert "/tower/return/observatory" in body
