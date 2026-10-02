from datetime import datetime, timezone

import time

from flask import Flask

import tower.identity_authority as identity

from tower.owner_teller_handoff import (
    issue_owner_teller_handoff,
    reset_owner_teller_handoff_store_for_tests,
)

from tower.teller_handoff_web import (
    TOWER_TELLER_ALLOWED_ORIGIN_ENV,
    TOWER_TELLER_EXCHANGE_PATH,
    register_teller_handoff_web,
)


NOW = time.time()

ORIGIN = "https://teller.example.test"


def iso(epoch):
    return datetime.fromtimestamp(
        epoch,
        tz=timezone.utc,
    ).isoformat()


def configure(monkeypatch):
    monkeypatch.setenv(
        identity.TOWER_OWNER_USERNAME_ENV,
        "twr189-owner",
    )

    monkeypatch.setenv(
        identity.TOWER_OWNER_PASSWORD_HASH_ENV,
        "test-hash",
    )

    monkeypatch.setenv(
        identity.TOWER_OWNER_ID_ENV,
        "twr189-owner-id",
    )

    monkeypatch.delenv(
        identity.TOWER_LOCAL_WALKTHROUGH_MODE_ENV,
        raising=False,
    )

    monkeypatch.setenv(
        "TOWER_SESSION_SECRET",
        (
            "twr189-session-secret-"
            "0123456789abcdef"
            "0123456789abcdef"
        ),
    )

    monkeypatch.setenv(
        TOWER_TELLER_ALLOWED_ORIGIN_ENV,
        ORIGIN,
    )

    reset_owner_teller_handoff_store_for_tests()


def session():
    return {
        "authenticated": True,
        "role": "owner",
        "owner_id": "twr189-owner-id",
        "username": "twr189-owner",
        "authenticated_at": iso(NOW - 30),
        "step_up_until": iso(NOW + 300),
    }


def app():
    value = Flask(__name__)
    value.config["TESTING"] = True
    register_teller_handoff_web(value)
    return value


def test_twr189_clouds_navigation_exchange(monkeypatch):
    configure(monkeypatch)

    issued = issue_owner_teller_handoff(
        session(),

        navigation_context={
            "source_app":
                "clouds",

            "destination":
                "payroll_review",

            "item_id":
                "PR-2044",

            "return_app":
                "clouds",

            "return_destination":
                "attention_queue",

            "correlation_id":
                "corr-clouds-pr-2044",
        },

        now_epoch=NOW,
    )

    with app().test_client() as client:

        response = client.post(
            TOWER_TELLER_EXCHANGE_PATH,

            headers={
                "Origin":
                    ORIGIN,
            },

            json={
                "handoff_code":
                    issued["handoff_code"],

                "client":
                    "the-teller",

                "exchange_version":
                    "tower-teller-exchange.v1",
            },
        )

    assert response.status_code == 200

    body = response.get_json()

    assert body["access_verified"] is True
    assert body["app_id"] == "teller"
    assert body["role"] == "owner"

    assert (
        body["navigation_context"]
        == {
            "source_app":
                "clouds",

            "destination_app":
                "teller",

            "destination":
                "payroll_review",

            "item_id":
                "PR-2044",

            "return_app":
                "clouds",

            "return_destination":
                "attention_queue",

            "correlation_id":
                "corr-clouds-pr-2044",
        }
    )

    assert "handoff_code" not in body
    assert "signature" not in body
    assert "owner_id" not in body


def test_twr189_wrong_origin_denied(monkeypatch):
    configure(monkeypatch)

    issued = issue_owner_teller_handoff(
        session(),
        now_epoch=NOW,
    )

    with app().test_client() as client:

        denied = client.post(
            TOWER_TELLER_EXCHANGE_PATH,

            headers={
                "Origin":
                    "https://evil.example",
            },

            json={
                "handoff_code":
                    issued["handoff_code"],

                "client":
                    "the-teller",

                "exchange_version":
                    "tower-teller-exchange.v1",
            },
        )

    assert denied.status_code == 403
