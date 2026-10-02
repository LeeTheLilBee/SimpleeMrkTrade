import tower.identity_authority as identity

from tower.teller_owner_entitlement_reservation import (
    teller_owner_entitlement_reservation,
    teller_owner_entitlement_reservation_ready,
)


def _configure_owner(monkeypatch):
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


def test_twr187_reservation_is_promoted_to_effective_activation():
    value = teller_owner_entitlement_reservation()

    assert value["policy_contract_verified"] is True
    assert value["reservation_state"] == "ACTIVATED"
    assert value["intended_access_policy"] == "GRANTED"
    assert value["effective_entitlement"] is True
    assert value["activation_gate"] == "TWR190"
    assert value["failures"] == []

    assert teller_owner_entitlement_reservation_ready() is True


def test_twr190_owner_identity_receives_teller_entitlement(monkeypatch):
    _configure_owner(monkeypatch)

    authority = (
        identity
        .hosted_owner_identity_authority()
    )

    entitlements = {
        item["app_id"]:
            item
        for item in authority["app_entitlements"]
    }

    assert "observatory" in entitlements
    assert "teller" in entitlements

    assert (
        entitlements["teller"]["access_policy"]
        == "GRANTED"
    )

    assert (
        entitlements["teller"]["verification_state"]
        == "VERIFIED"
    )
