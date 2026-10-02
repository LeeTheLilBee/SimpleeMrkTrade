"""TWR-OBML006–010: current Tower owner facts never imply Manual Live grant."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tower import obml_owner_review_preflight as preflight
from tower.app_registry import registered_apps, route_by_path

ROOT = Path(__file__).resolve().parents[1]
REQUEST_CONTRACT = (
    ROOT / "obml-request-source" / "tower" / "contracts"
    / "twr_obml_owner_handoff_request_v1.json"
)


@pytest.mark.parametrize("owner,stepped,operational,identity,entitled,launchable", [
    (False, False, False, False, False, False),
    (True, False, False, True, True, True),
    (True, True, False, True, True, True),
    (True, True, True, False, True, True),
    (True, True, True, True, False, True),
    (True, True, True, True, True, False),
    (True, True, True, True, True, True),
])
def test_current_owner_and_existing_ob_receipt_never_activate_obml(
    monkeypatch, owner, stepped, operational, identity, entitled, launchable
):
    monkeypatch.setattr(preflight, "owner_session_active", lambda: owner)
    monkeypatch.setattr(preflight, "step_up_active", lambda: stepped)
    monkeypatch.setattr(preflight, "operational_ob_access_active", lambda: operational)
    monkeypatch.setattr(preflight, "hosted_owner_identity_authority", lambda: {
        "verification_state": "VERIFIED" if identity else "NOT_CONFIGURED",
        "app_entitlements": [{
            "app_id": "observatory",
            "verification_state": "VERIFIED",
            "access_policy": "GRANTED",
        }] if entitled else [],
    })
    monkeypatch.setattr(
        preflight, "app_truth_by_id", lambda app: {
            "app_id": app, "launchable": launchable,
        },
    )
    result = preflight.inspect_current_obml_owner_review()
    assert result["state"] == "BLOCKED"
    assert result["review_clearance_issued"] is False
    assert result["manual_live_activated"] is False
    assert result["execution_authorized"] is False
    assert result["issued_token"] is False
    assert result["amount_data_returned"] is False
    assert result["owner_account_verified_for_obml"] is False
    assert result["forbidden_capabilities"]
    assert set(result["forbidden_capabilities"].values()) == {False}
    assert "OBML_PURPOSE_BOUND_STEP_UP_UNIMPLEMENTED" in result["reason_codes"]
    assert "CANONICAL_OB_ACCOUNT_IDENTITY_UNVERIFIED" in result["reason_codes"]
    assert "OBML_TOWER_ISSUER_AND_OB_RECEIVER_NOT_CONNECTED" in result["reason_codes"]
    serialized = json.dumps(result, sort_keys=True)
    assert "secret" not in serialized.lower()
    assert "balance" not in serialized.lower()


def test_existing_owner_launch_is_not_replaced_by_manual_review_route():
    assert preflight.CANONICAL_OB_ENTRY == "/tower/launch/observatory"
    assert preflight.PROTECTED_DESTINATION == "/ob/dashboard"
    assert any(app["app_id"] == "observatory" and app["tower_launch_route"] == "/tower/launch/observatory" for app in registered_apps())
    assert route_by_path("/tower/launch/obml") is None


def test_exact_independent_pr68_request_semantics_without_promoting_to_grant():
    assert REQUEST_CONTRACT.is_file()
    contract = json.loads(REQUEST_CONTRACT.read_text(encoding="utf-8"))
    assert contract["schema_version"] == "TOWER_OBML_OWNER_HANDOFF_REQUEST_V1"
    assert contract["status"] == "SOURCE_ONLY_UNIMPLEMENTED_NO_LIVE_GRANT"
    assert contract["purpose"] == preflight.PURPOSE
    assert contract["existing_launch_entry"] == preflight.CANONICAL_OB_ENTRY
    assert contract["protected_destination"] == preflight.PROTECTED_DESTINATION
    required = set(contract["handoff_required_fields"])
    assert {
        "owner_session_id", "account_key", "account_identity_fingerprint",
        "step_up_event_ref", "revocation_epoch", "nonce",
        "verified_tower_attestation",
    } <= required
    assert all(contract["capability_scope"][cap] is False
               for cap in preflight.FORBIDDEN_CAPABILITIES)


def test_source_review_registers_no_http_endpoint_or_execution_capability():
    source = Path(preflight.__file__).read_text(encoding="utf-8")
    for forbidden in (
        "@app.route(", "requests.post(", "issue_owner_observatory_handoff(",
        "from observatory.", "broker.place_order", "capital_movement(",
    ):
        assert forbidden not in source
    assert "OBML_TOWER_ISSUER_AND_OB_RECEIVER_NOT_CONNECTED" in source
