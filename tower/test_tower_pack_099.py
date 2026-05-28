
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path("/content/SimpleeMrkTrade_REAL_CLONE")
os.chdir(PROJECT_ROOT)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

for name in list(sys.modules.keys()):
    if name == "tower" or name.startswith("tower.") or name == "web.app":
        sys.modules.pop(name, None)

from tower.owner_admin_action_receipts import (
    HIGH_POWER_ACTIONS,
    OWNER_ADMIN_ACTION_TYPES,
    OWNER_ADMIN_PANEL_PATH,
    create_archive_handoff_from_receipt,
    create_owner_admin_receipt,
    record_archive_handoff_receipt,
    record_export_approval_receipt,
    record_lockdown_change_receipt,
    record_mode_access_grant_receipt,
    record_note_receipt,
    record_resolve_receipt,
    record_route_policy_change_receipt,
    record_user_clearance_change_receipt,
    reset_owner_admin_receipts_for_test,
    summarize_owner_admin_receipts,
    write_owner_admin_receipts_panel,
)


def _print(title, payload=None):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def _assert_no_secret_leakage(payload):
    serialized = json.dumps(payload, sort_keys=True, default=str).lower()
    forbidden = [
        "tower_keycard=",
        "should_not_survive",
        '"raw_token":',
        '"tower_keycard":',
        '"access_token":',
        '"refresh_token":',
        '"api_key":',
        '"github_token":',
        '"stripe_secret":',
        '"password":',
        '"private_key":',
        "bearer should_not_survive",
        "ghp_should_not_survive",
        "sk_live_should_not_survive",
        "-----begin private key-----",
    ]
    for item in forbidden:
        assert item not in serialized, item


def _verified_step_up():
    return {
        "ok": True,
        "decision": "verified",
        "recent_step_up_verified": True,
        "challenge_id": "stepup_test_099",
        "method": "owner_pin",
    }


def run_tests():
    reset = reset_owner_admin_receipts_for_test()
    _print("RESET OWNER/ADMIN RECEIPTS", reset)
    assert reset.get("ok") is True

    assert "note_added" in OWNER_ADMIN_ACTION_TYPES
    assert "security_item_resolved" in OWNER_ADMIN_ACTION_TYPES
    assert "route_policy_changed" in OWNER_ADMIN_ACTION_TYPES
    assert "user_clearance_changed" in OWNER_ADMIN_ACTION_TYPES
    assert "export_approved" in OWNER_ADMIN_ACTION_TYPES
    assert "lockdown_enabled" in OWNER_ADMIN_ACTION_TYPES
    assert "lockdown_disabled" in OWNER_ADMIN_ACTION_TYPES
    assert "mode_access_granted" in OWNER_ADMIN_ACTION_TYPES
    assert "archive_handoff_created" in OWNER_ADMIN_ACTION_TYPES
    assert "admin_override_recorded" in OWNER_ADMIN_ACTION_TYPES
    assert "route_policy_changed" in HIGH_POWER_ACTIONS

    note = record_note_receipt(
        actor_user_id="owner_solice",
        target_type="security_item",
        target_id="sec_note_099",
        note="Owner note with secret marker SHOULD_NOT_SURVIVE should redact.",
        metadata={"raw_token": "SHOULD_NOT_SURVIVE"},
    )
    _print("NOTE RECEIPT", note)
    assert note.get("ok") is True
    assert note.get("action_type") == "note_added"
    assert note.get("action_power") == "normal"
    _assert_no_secret_leakage(note)

    resolved = record_resolve_receipt(
        actor_user_id="owner_solice",
        target_type="security_item",
        target_id="sec_resolve_099",
        resolution="Resolved after review.",
        metadata={"tower_keycard": "SHOULD_NOT_SURVIVE"},
    )
    _print("RESOLVE RECEIPT", resolved)
    assert resolved.get("action_type") == "security_item_resolved"
    _assert_no_secret_leakage(resolved)

    route = record_route_policy_change_receipt(
        actor_user_id="owner_solice",
        route_path="/tower/admin-sensitive",
        old_policy={"policy": "needs_owner_review", "private_notes": "sensitive old"},
        new_policy={"policy": "tower_only", "allowed_roles": ["owner"]},
        reason="Pack 099 route policy test.",
        step_up=_verified_step_up(),
        metadata={"api_key": "SHOULD_NOT_SURVIVE"},
    )
    _print("ROUTE POLICY RECEIPT", route)
    assert route.get("action_type") == "route_policy_changed"
    assert route.get("action_power") == "high"
    assert route.get("step_up_present") is True
    _assert_no_secret_leakage(route)

    clearance = record_user_clearance_change_receipt(
        actor_user_id="owner_solice",
        user_id="beta_user_099",
        old_clearance={"level": "basic"},
        new_clearance={"level": "beta", "apps": ["teller"]},
        reason="Pack 099 user clearance test.",
        step_up=_verified_step_up(),
        object_permission={"allowed": True, "decision": "allow"},
    )
    _print("USER CLEARANCE RECEIPT", clearance)
    assert clearance.get("action_type") == "user_clearance_changed"
    assert clearance.get("step_up_present") is True
    _assert_no_secret_leakage(clearance)

    export = record_export_approval_receipt(
        actor_user_id="owner_solice",
        export_id="export_099",
        export_scope={"category": "payroll_proof", "contains_sensitive": True},
        reason="Pack 099 export approval test.",
        step_up=_verified_step_up(),
        metadata={"stripe_secret": "sk_live_SHOULD_NOT_SURVIVE"},
    )
    _print("EXPORT APPROVAL RECEIPT", export)
    assert export.get("action_type") == "export_approved"
    assert export.get("step_up_present") is True
    _assert_no_secret_leakage(export)

    lock_on = record_lockdown_change_receipt(
        actor_user_id="owner_solice",
        lockdown_id="lockdown_099",
        enabled=True,
        reason="Pack 099 lockdown enable test.",
        before_state={"lockdown_active": False},
        after_state={"lockdown_active": True, "reason_code": "test"},
    )
    _print("LOCKDOWN ENABLE RECEIPT", lock_on)
    assert lock_on.get("action_type") == "lockdown_enabled"
    _assert_no_secret_leakage(lock_on)

    lock_off = record_lockdown_change_receipt(
        actor_user_id="owner_solice",
        lockdown_id="lockdown_099",
        enabled=False,
        reason="Pack 099 lockdown disable test.",
        before_state={"lockdown_active": True},
        after_state={"lockdown_active": False},
        step_up=_verified_step_up(),
    )
    _print("LOCKDOWN DISABLE RECEIPT", lock_off)
    assert lock_off.get("action_type") == "lockdown_disabled"
    assert lock_off.get("step_up_present") is True
    _assert_no_secret_leakage(lock_off)

    mode = record_mode_access_grant_receipt(
        actor_user_id="owner_solice",
        user_id="beta_user_099",
        mode_name="Paper Mode",
        grant_scope={"app_id": "observatory", "mode": "paper", "expires": "beta_end"},
        reason="Pack 099 mode access grant test.",
        step_up=_verified_step_up(),
    )
    _print("MODE ACCESS GRANT RECEIPT", mode)
    assert mode.get("action_type") == "mode_access_granted"
    _assert_no_secret_leakage(mode)

    archive_receipt = record_archive_handoff_receipt(
        actor_user_id="owner_solice",
        handoff_id="archive_handoff_099",
        handoff_payload={
            "category": "tower_receipts",
            "document_text": "Sensitive text should redact",
            "raw_token": "SHOULD_NOT_SURVIVE",
        },
        reason="Pack 099 archive handoff receipt test.",
        step_up=_verified_step_up(),
    )
    _print("ARCHIVE HANDOFF RECEIPT", archive_receipt)
    assert archive_receipt.get("action_type") == "archive_handoff_created"
    _assert_no_secret_leakage(archive_receipt)

    admin_override = create_owner_admin_receipt(
        action_type="admin_override_recorded",
        actor_user_id="owner_solice",
        target_type="admin_override",
        target_id="override_099",
        reason="Pack 099 admin override test.",
        before_state={"status": "blocked"},
        after_state={"status": "approved"},
        step_up=_verified_step_up(),
        metadata={"password": "SHOULD_NOT_SURVIVE"},
    )
    _print("ADMIN OVERRIDE RECEIPT", admin_override)
    assert admin_override.get("action_type") == "admin_override_recorded"
    assert admin_override.get("action_power") == "high"
    _assert_no_secret_leakage(admin_override)

    handoff = create_archive_handoff_from_receipt(
        receipt=admin_override,
        archive_category="tower_owner_admin_receipts",
        actor_user_id="owner_solice",
    )
    _print("ARCHIVE HANDOFF FROM RECEIPT", handoff)
    assert handoff.get("ok") is True
    assert handoff.get("archive_ready") is True
    assert handoff.get("source_receipt_id") == admin_override.get("receipt_id")
    _assert_no_secret_leakage(handoff)

    summary = summarize_owner_admin_receipts(limit=80)
    _print("OWNER/ADMIN RECEIPT SUMMARY", summary)

    assert summary.get("ok") is True
    assert summary.get("readiness_score") == 100
    assert summary.get("readiness_label") == "Owner/admin action receipt coverage ready"
    assert summary.get("receipt_count") >= 10
    assert summary.get("archive_ready_count") >= 10
    assert summary.get("by_action", {}).get("note_added", 0) >= 1
    assert summary.get("by_action", {}).get("security_item_resolved", 0) >= 1
    assert summary.get("by_action", {}).get("route_policy_changed", 0) >= 1
    assert summary.get("by_action", {}).get("user_clearance_changed", 0) >= 1
    assert summary.get("by_action", {}).get("export_approved", 0) >= 1
    assert summary.get("by_action", {}).get("lockdown_enabled", 0) >= 1
    assert summary.get("by_action", {}).get("lockdown_disabled", 0) >= 1
    assert summary.get("by_action", {}).get("mode_access_granted", 0) >= 1
    assert summary.get("by_action", {}).get("archive_handoff_created", 0) >= 1
    assert summary.get("by_action", {}).get("admin_override_recorded", 0) >= 1
    assert summary.get("no_secret_leakage") is True
    _assert_no_secret_leakage(summary)

    panel = write_owner_admin_receipts_panel(summary)
    _print("OWNER/ADMIN RECEIPTS PANEL", panel)

    assert panel.get("ok") is True
    assert OWNER_ADMIN_PANEL_PATH.exists()

    html = OWNER_ADMIN_PANEL_PATH.read_text(encoding="utf-8")
    assert "The Tower · Owner/Admin Receipts" in html
    assert "route_policy_changed" in html
    assert "admin_override_recorded" in html
    assert "SHOULD_NOT_SURVIVE" not in html
    assert "tower_keycard=" not in html

    final = {
        "pack": "099",
        "status": "passed",
        "human_reason": "Owner/admin action receipt coverage records notes, resolves, route policy changes, clearance changes, export approvals, lockdown changes, mode grants, and Archive handoffs without leaking secrets.",
    }
    _print("PACK 099 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
