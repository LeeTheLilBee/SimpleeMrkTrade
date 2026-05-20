
"""
PACK 025 TEST — Tower keycard passes.

Run:
    python tower/test_tower_pack_025.py
"""

import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tower.keycard_passes import (
    KEYCARD_DOOR_LOG_PATH,
    KEYCARD_REGISTRY_PATH,
    get_keycard_door_log,
    issue_keycard_pass,
    list_keycard_passes,
    make_door,
    purge_expired_keycard_passes,
    revoke_keycard_pass,
    summarize_keycard_health,
    validate_door_access,
    validate_keycard_pass,
)


def _print(title, payload=None):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True))


def _reset_test_files():
    # Keep this pack test deterministic.
    # This only resets the new keycard test files, not the rest of The Tower data.
    for path in [KEYCARD_REGISTRY_PATH, KEYCARD_DOOR_LOG_PATH]:
        if path.exists():
            path.unlink()


def run_tests():
    _reset_test_files()

    _print("ISSUE EXACT ROUTE PASS")
    issued = issue_keycard_pass(
        user_id="owner_solice",
        app_name="tower",
        door_type="route",
        door_id="/tower/security-command",
        actions=["view"],
        issuer_user_id="owner_solice",
        reason="Pack 025 owner route access test.",
        ttl_seconds=900,
        session_id="session_owner_001",
        device_id="device_owner_chromebook",
        role="owner",
        clearance_level="restricted",
        risk_score_at_issue=10,
    )
    _print("Issued", {
        "ok": issued["ok"],
        "pass_id": issued["pass_id"],
        "token_preview": issued["token_preview"],
        "expires_at": issued["expires_at"],
    })

    token = issued["token"]
    pass_id = issued["pass_id"]

    _print("VALIDATE CORRECT DOOR")
    allowed = validate_keycard_pass(
        token=token,
        app_name="tower",
        door_type="route",
        door_id="/tower/security-command",
        action="view",
        user_id="owner_solice",
        session_id="session_owner_001",
        device_id="device_owner_chromebook",
        required_clearance_level="restricted",
        current_risk_score=12,
    )
    _print("Allowed decision", allowed)
    assert allowed["allowed"] is True
    assert allowed["reason_code"] == "keycard_pass_allowed"

    _print("VALIDATE WRONG NEIGHBOR DOOR")
    wrong_door = validate_keycard_pass(
        token=token,
        app_name="tower",
        door_type="route",
        door_id="/tower/admin",
        action="view",
        user_id="owner_solice",
        session_id="session_owner_001",
        device_id="device_owner_chromebook",
        required_clearance_level="restricted",
    )
    _print("Wrong door decision", wrong_door)
    assert wrong_door["allowed"] is False
    assert wrong_door["reason_code"] == "wrong_door"

    _print("VALIDATE WRONG ACTION")
    wrong_action = validate_keycard_pass(
        token=token,
        app_name="tower",
        door_type="route",
        door_id="/tower/security-command",
        action="export",
        user_id="owner_solice",
        session_id="session_owner_001",
        device_id="device_owner_chromebook",
        required_clearance_level="restricted",
    )
    _print("Wrong action decision", wrong_action)
    assert wrong_action["allowed"] is False
    assert wrong_action["reason_code"] == "action_not_allowed"

    _print("VALIDATE WRONG USER")
    wrong_user = validate_keycard_pass(
        token=token,
        app_name="tower",
        door_type="route",
        door_id="/tower/security-command",
        action="view",
        user_id="beta_001",
        session_id="session_owner_001",
        device_id="device_owner_chromebook",
        required_clearance_level="restricted",
    )
    _print("Wrong user decision", wrong_user)
    assert wrong_user["allowed"] is False
    assert wrong_user["reason_code"] == "wrong_user"

    _print("VALIDATE WRONG DEVICE")
    wrong_device = validate_keycard_pass(
        token=token,
        app_name="tower",
        door_type="route",
        door_id="/tower/security-command",
        action="view",
        user_id="owner_solice",
        session_id="session_owner_001",
        device_id="unknown_device",
        required_clearance_level="restricted",
    )
    _print("Wrong device decision", wrong_device)
    assert wrong_device["allowed"] is False
    assert wrong_device["reason_code"] == "wrong_device"

    _print("VALIDATE INSUFFICIENT CLEARANCE")
    low = issue_keycard_pass(
        user_id="owner_solice",
        app_name="archive_vault",
        door_type="record",
        door_id="capsule_alpha",
        actions=["view"],
        issuer_user_id="owner_solice",
        reason="Pack 025 low clearance test.",
        ttl_seconds=900,
        session_id="session_owner_001",
        device_id="device_owner_chromebook",
        role="owner",
        clearance_level="internal",
    )
    low_decision = validate_keycard_pass(
        token=low["token"],
        app_name="archive_vault",
        door_type="record",
        door_id="capsule_alpha",
        action="view",
        user_id="owner_solice",
        session_id="session_owner_001",
        device_id="device_owner_chromebook",
        required_clearance_level="critical",
    )
    _print("Low clearance decision", low_decision)
    assert low_decision["allowed"] is False
    assert low_decision["reason_code"] == "clearance_level_too_low"

    _print("VALIDATE DOOR OBJECT WRAPPER")
    door = make_door(
        app_name="observatory",
        door_type="mode",
        door_id="paper",
        action="enter",
        classification="confidential",
    )
    ob = issue_keycard_pass(
        user_id="owner_solice",
        app_name="observatory",
        door_type="mode",
        door_id="paper",
        actions=["enter"],
        issuer_user_id="owner_solice",
        reason="Pack 025 OB paper mode door test.",
        ttl_seconds=900,
        session_id="session_owner_001",
        device_id="device_owner_chromebook",
        role="owner",
        clearance_level="confidential",
    )
    door_decision = validate_door_access(
        token=ob["token"],
        door=door,
        user_id="owner_solice",
        session_id="session_owner_001",
        device_id="device_owner_chromebook",
    )
    _print("Door wrapper decision", door_decision)
    assert door_decision["allowed"] is True

    _print("VALIDATE EXPIRED PASS")
    expired = issue_keycard_pass(
        user_id="owner_solice",
        app_name="tower",
        door_type="route",
        door_id="/tower/status.json",
        actions=["view"],
        issuer_user_id="owner_solice",
        reason="Pack 025 expired test.",
        ttl_seconds=-5,
        session_id="session_owner_001",
        device_id="device_owner_chromebook",
        role="owner",
        clearance_level="restricted",
    )
    expired_decision = validate_keycard_pass(
        token=expired["token"],
        app_name="tower",
        door_type="route",
        door_id="/tower/status.json",
        action="view",
        user_id="owner_solice",
        session_id="session_owner_001",
        device_id="device_owner_chromebook",
        required_clearance_level="restricted",
    )
    _print("Expired decision", expired_decision)
    assert expired_decision["allowed"] is False
    assert expired_decision["reason_code"] == "pass_expired"

    _print("VALIDATE REVOKED PASS")
    revoked = revoke_keycard_pass(
        pass_id=pass_id,
        revoked_by="owner_solice",
        reason="Pack 025 revocation test.",
    )
    _print("Revoked", revoked)
    assert revoked["ok"] is True

    revoked_decision = validate_keycard_pass(
        token=token,
        app_name="tower",
        door_type="route",
        door_id="/tower/security-command",
        action="view",
        user_id="owner_solice",
        session_id="session_owner_001",
        device_id="device_owner_chromebook",
        required_clearance_level="restricted",
    )
    _print("Revoked decision", revoked_decision)
    assert revoked_decision["allowed"] is False
    assert revoked_decision["reason_code"] == "pass_not_active"

    _print("ENSURE RAW TOKEN IS NOT STORED")
    registry = list_keycard_passes()
    _print("Registry summary", {
        "ok": registry["ok"],
        "total": registry["total"],
        "first_record_keys": sorted(registry["passes"][0].keys()) if registry["passes"] else [],
    })
    assert registry["ok"] is True
    assert registry["total"] >= 1
    for record in registry["passes"]:
        assert "token" not in record
        assert record.get("token_hash") == "stored_hash_redacted"

    _print("PURGE EXPIRED")
    purge = purge_expired_keycard_passes()
    _print("Purge result", purge)
    assert purge["ok"] is True

    _print("KEYCARD HEALTH")
    health = summarize_keycard_health()
    _print("Health", health)
    assert health["ok"] is True
    assert health["keycard_total"] >= 1

    _print("DOOR LOG")
    door_log = get_keycard_door_log(limit=20)
    _print("Door log", {
        "ok": door_log["ok"],
        "total": door_log["total"],
        "last_events": door_log["events"][-5:],
    })
    assert door_log["ok"] is True
    assert door_log["total"] >= 6

    result = {
        "pack": "025",
        "status": "passed",
        "human_reason": "Tower keycard pass layer works: exact-door scope, expiration, revocation, device/session binding, clearance levels, and door logging.",
        "registry_path": str(KEYCARD_REGISTRY_PATH),
        "door_log_path": str(KEYCARD_DOOR_LOG_PATH),
    }
    _print("PACK 025 RESULT", result)
    return result


if __name__ == "__main__":
    run_tests()
