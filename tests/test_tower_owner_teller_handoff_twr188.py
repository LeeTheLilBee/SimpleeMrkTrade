from datetime import datetime, timezone

import pytest

import tower.identity_authority as identity

from tower.owner_teller_handoff import (
    OwnerTellerHandoffError,
    consume_owner_teller_handoff,
    issue_owner_teller_handoff,
    reset_owner_teller_handoff_store_for_tests,
    validate_owner_teller_access_receipt,
)


NOW = 2_000_000_000.0


def iso(epoch):
    return datetime.fromtimestamp(
        epoch,
        tz=timezone.utc,
    ).isoformat()


def configure(monkeypatch):
    monkeypatch.setenv(
        identity.TOWER_OWNER_USERNAME_ENV,
        "twr188-owner",
    )

    monkeypatch.setenv(
        identity.TOWER_OWNER_PASSWORD_HASH_ENV,
        "test-hash",
    )

    monkeypatch.setenv(
        identity.TOWER_OWNER_ID_ENV,
        "twr188-owner-id",
    )

    monkeypatch.delenv(
        identity.TOWER_LOCAL_WALKTHROUGH_MODE_ENV,
        raising=False,
    )

    monkeypatch.setenv(
        "TOWER_SESSION_SECRET",
        (
            "twr188-session-secret-"
            "0123456789abcdef"
            "0123456789abcdef"
        ),
    )

    reset_owner_teller_handoff_store_for_tests()


def session():
    return {
        "authenticated": True,
        "role": "owner",
        "owner_id": "twr188-owner-id",
        "username": "twr188-owner",
        "authenticated_at": iso(NOW - 30),
        "step_up_until": iso(NOW + 300),
    }


def test_twr188_one_time_security_survives_twr190_activation(monkeypatch):
    configure(monkeypatch)

    issued = issue_owner_teller_handoff(
        session(),
        now_epoch=NOW,
    )

    assert issued["effective_entitlement"] is True
    assert issued["one_time"] is True
    assert issued["raw_code_persisted"] is False

    receipt = consume_owner_teller_handoff(
        issued["handoff_code"],
        now_epoch=NOW + 1,
    )

    validated = validate_owner_teller_access_receipt(
        receipt,
        now_epoch=NOW + 2,
    )

    assert validated["signature_valid"] is True
    assert validated["access_verified"] is True
    assert validated["app_id"] == "teller"
    assert validated["role"] == "owner"

    with pytest.raises(
        OwnerTellerHandoffError
    ):
        consume_owner_teller_handoff(
            issued["handoff_code"],
            now_epoch=NOW + 3,
        )


def test_twr188_active_step_up_still_required(monkeypatch):
    configure(monkeypatch)

    value = session()
    value["step_up_until"] = iso(NOW - 1)

    with pytest.raises(
        OwnerTellerHandoffError
    ) as exc:

        issue_owner_teller_handoff(
            value,
            now_epoch=NOW,
        )

    assert (
        exc.value.code
        == "owner_teller_step_up_not_active"
    )
