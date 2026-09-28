from __future__ import annotations

import base64
import hashlib
import hmac
import json

import pytest

from tower.buybox_owner_handoff_issuer import (
    HANDOFF_KEYS, PREFIX, SCHEMA_VERSION,
    TowerBuyBoxIssuerUnavailable,
    inspect_current_buybox_issue_preflight,
    issue_buybox_owner_handoff,
)

SECRET = "x" * 64
SESSION = {
    "authenticated": True,
    "role": "owner",
    "owner_id": "tower_owner_fixture_000000000001",
    "tower_session_ref": "tower_session_fixture_000000000001",
    "step_up_active": True,
}
IDENTITY = {
    "verification_state": "VERIFIED",
    "record": {
        "person_id": "tower_person_fixture_000000000001",
        "account_id": "tower_account_fixture_000000000001",
        "organization": None,
    },
    "app_entitlements": [{
        "app_id": "buybox",
        "verification_state": "VERIFIED",
        "access_policy": "GRANTED",
        "source_id": "tower.identity.buybox.fixture_000001",
    }],
}
TRUTH = {"launchable": True}


def decode_and_verify(token):
    prefix, payload_b64, mac_b64 = token.split(".")
    assert prefix == PREFIX
    pad = "=" * (-len(payload_b64) % 4)
    payload = base64.urlsafe_b64decode(payload_b64 + pad)
    sig = base64.urlsafe_b64decode(mac_b64 + "=" * (-len(mac_b64) % 4))
    expected = hmac.new(
        SECRET.encode(), (PREFIX + "." + payload_b64).encode(), hashlib.sha256
    ).digest()
    assert hmac.compare_digest(sig, expected)
    return json.loads(payload)


def test_preflight_default_blocks_missing_real_entitlement_truth_and_secret(monkeypatch):
    monkeypatch.delenv("TOWER_BUYBOX_HANDOFF_SIGNING_SECRET", raising=False)
    result = inspect_current_buybox_issue_preflight(
        session_context={},
        identity={"verification_state": "NOT_CONFIGURED", "app_entitlements": []},
        app_truth={"launchable": False},
    )
    assert result["state"] == "BLOCKED"
    assert result["can_issue_handoff"] is False
    assert "BUYBOX_OWNER_ENTITLEMENT_NOT_GRANTED" not in result["reason_codes"]
    assert "HOSTED_OWNER_IDENTITY_NOT_VERIFIED" in result["reason_codes"]
    assert "BUYBOX_PUBLICATION_HEALTH_OR_LAUNCH_NOT_VERIFIED" in result["reason_codes"]
    assert "BUYBOX_HANDOFF_SIGNING_SECRET_NOT_CONFIGURED" in result["reason_codes"]


def test_exact_receiver_compatible_token_shape_and_no_financial_grants(monkeypatch):
    monkeypatch.setenv("TOWER_BUYBOX_HANDOFF_SIGNING_SECRET", SECRET)
    issued = issue_buybox_owner_handoff(
        session_context=SESSION,
        identity=IDENTITY,
        app_truth=TRUTH,
        now_epoch=1_800_000_000,
        shared_secret=SECRET,
    )
    claims = decode_and_verify(issued["token"])
    assert set(claims) == HANDOFF_KEYS
    assert claims["schema_version"] == SCHEMA_VERSION
    assert claims["issuer"] == "tower"
    assert claims["audience"] == "buybox-owner"
    assert claims["purpose"] == "owner_entry"
    assert claims["target_path"] == "/"
    assert claims["return_path"] == "/tower/access-home"
    assert claims["expires_at_epoch"] - claims["issued_at_epoch"] == 60
    assert issued["broker_submission_authorized"] is False
    assert issued["capital_movement_authorized"] is False
    assert issued["closing_authorized"] is False
    assert issued["vault_access_authorized"] is False


@pytest.mark.parametrize("patch", [
    {"authenticated": False},
    {"role": "manager"},
    {"step_up_active": False},
    {"tower_session_ref": ""},
])
def test_current_session_gate_is_mandatory(monkeypatch, patch):
    monkeypatch.setenv("TOWER_BUYBOX_HANDOFF_SIGNING_SECRET", SECRET)
    session = {**SESSION, **patch}
    with pytest.raises(TowerBuyBoxIssuerUnavailable):
        issue_buybox_owner_handoff(
            session_context=session, identity=IDENTITY, app_truth=TRUTH,
            now_epoch=1_800_000_000, shared_secret=SECRET,
        )


def test_launchability_and_entitlement_are_independent_mandatory_gates(monkeypatch):
    monkeypatch.setenv("TOWER_BUYBOX_HANDOFF_SIGNING_SECRET", SECRET)
    no_entitlement = {**IDENTITY, "app_entitlements": []}
    with pytest.raises(TowerBuyBoxIssuerUnavailable):
        issue_buybox_owner_handoff(
            session_context=SESSION, identity=no_entitlement, app_truth=TRUTH,
            now_epoch=1_800_000_000, shared_secret=SECRET,
        )
    with pytest.raises(TowerBuyBoxIssuerUnavailable):
        issue_buybox_owner_handoff(
            session_context=SESSION, identity=IDENTITY,
            app_truth={"launchable": False},
            now_epoch=1_800_000_000, shared_secret=SECRET,
        )


def test_handoff_contains_only_opaque_refs_not_username_or_password(monkeypatch):
    monkeypatch.setenv("TOWER_BUYBOX_HANDOFF_SIGNING_SECRET", SECRET)
    identity = {
        **IDENTITY,
        "record": {
            **IDENTITY["record"],
            "username": "owner-name-should-not-be-in-token",
            "display_name": "Owner Display",
        },
    }
    issued = issue_buybox_owner_handoff(
        session_context=SESSION, identity=identity, app_truth=TRUTH,
        now_epoch=1_800_000_000, shared_secret=SECRET,
    )
    raw = base64.urlsafe_b64decode(
        issued["token"].split(".")[1]
        + "=" * (-len(issued["token"].split(".")[1]) % 4)
    ).decode()
    assert "owner-name-should-not-be-in-token" not in raw
    assert "Owner Display" not in raw
    assert "password" not in raw.casefold()
