import pytest
from flask import Flask

from tower.tower_observatory_walkthrough_web import (
    owner_access_allowed,
    room_by_id,
    room_request_context,
    tower_ob_walkthrough_bp,
)


@pytest.fixture()
def app():
    app = Flask(__name__)
    app.secret_key = "walkthrough-test-secret"

    app.register_blueprint(
        tower_ob_walkthrough_bp
    )

    app.config.update(
        TESTING=True,
    )

    return app


@pytest.fixture()
def client(app):
    return app.test_client()


def set_owner_session(client):
    with client.session_transaction() as session:
        session["tower_role"] = "owner"
        session["owner_id"] = "owner_test"


def test_walkthrough_default_denies_without_owner(client):
    response = client.get(
        "/tower/observatory-walkthrough"
    )

    assert response.status_code == 403


def test_walkthrough_home_lists_six_rooms(client):
    set_owner_session(client)

    response = client.get(
        "/tower/observatory-walkthrough"
    )

    assert response.status_code == 200

    body = response.get_data(as_text=True)

    for room_name in [
        "Dashboard",
        "Market Map",
        "Symbol Page",
        "Trade Center",
        "Review Center",
        "Owner Console",
    ]:
        assert room_name in body


def test_room_review_page(client):
    set_owner_session(client)

    response = client.get(
        "/tower/observatory-walkthrough/"
        "room/ob_room_dashboard"
    )

    assert response.status_code == 200

    body = response.get_data(as_text=True)

    assert "Dashboard" in body
    assert "ob_owner_command" in body
    assert "Launch protected preview" in body


def test_dashboard_preview_launch_and_receipt(client):
    set_owner_session(client)

    response = client.post(
        "/tower/observatory-walkthrough/"
        "room/ob_room_dashboard/launch",
        follow_redirects=True,
    )

    assert response.status_code == 200

    body = response.get_data(as_text=True)

    assert "Protected launch passed" in body
    assert "Lockback verified" in body
    assert "Default deny restored" in body


def test_symbol_preview_launch(client):
    set_owner_session(client)

    response = client.post(
        "/tower/observatory-walkthrough/"
        "room/ob_room_symbol_page/launch",
        data={
            "symbol": "amd",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    body = response.get_data(as_text=True)

    assert "/symbol/AMD" in body


def test_owner_console_preview_launch(client):
    set_owner_session(client)

    response = client.post(
        "/tower/observatory-walkthrough/"
        "room/ob_room_owner_console/launch",
        data={
            "mission_account_id": "proof_demo",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    body = response.get_data(as_text=True)

    assert "Owner Console" in body
    assert "validated" in body


def test_walkthrough_close_returns_locked_back(client):
    set_owner_session(client)

    client.post(
        "/tower/observatory-walkthrough/"
        "room/ob_room_dashboard/launch",
    )

    response = client.post(
        "/tower/observatory-walkthrough/close",
        follow_redirects=True,
    )

    assert response.status_code == 200

    body = response.get_data(as_text=True)

    assert "Returned to Tower" in body
    assert "Replay blocked" in body
    assert "Default deny restored" in body


def test_room_helpers():
    room = room_by_id(
        "ob_room_symbol_page"
    )

    assert room is not None

    context = room_request_context(
        room,
        {
            "symbol": "nvda",
        },
    )

    assert context["path"] == "/symbol/NVDA"

    assert context["object_context"] == {
        "symbol": "NVDA",
    }
