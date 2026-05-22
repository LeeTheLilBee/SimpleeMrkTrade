
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
    if name == "tower" or name.startswith("tower."):
        sys.modules.pop(name, None)

from tower.archive_vault_handoff import (
    ARCHIVE_HANDOFF_PATH,
    build_archive_vault_handoff_record,
    list_archive_vault_handoffs,
    queue_archive_vault_handoff,
    summarize_archive_vault_handoffs,
)
from tower.ob_object_guard import evaluate_ob_object_guard
from tower.ob_object_audit_capsules import (
    list_open_ob_object_security_inbox,
    queue_ob_object_security_inbox_item_for_archive,
)


def _print(title, payload=None):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def run_tests():
    before = summarize_archive_vault_handoffs(limit=5)
    _print("BEFORE ARCHIVE HANDOFF SUMMARY", before)

    manual = build_archive_vault_handoff_record(
        source_type="manual_test",
        source_id="manual_064",
        title="Manual Archive Handoff Test",
        summary="Testing safe Archive Vault handoff stub.",
        severity="medium",
        user_id="owner_solice",
        related_object={
            "object_type": "export",
            "object_id": "export_manual_064",
            "raw_token": "SHOULD_NOT_SURVIVE",
            "tower_keycard": "SHOULD_NOT_SURVIVE",
        },
        source_payload={
            "secret": "SHOULD_NOT_SURVIVE",
            "authorization": "Bearer SHOULD_NOT_SURVIVE",
            "safe": "yes",
        },
        owner_note="Pack 064 manual handoff test.",
    )
    _print("MANUAL HANDOFF RECORD", manual)

    assert manual.get("ok") is True
    serialized_manual = json.dumps(manual, sort_keys=True, default=str)
    assert "SHOULD_NOT_SURVIVE" not in serialized_manual
    assert "raw_token" not in serialized_manual
    assert "tower_keycard" not in serialized_manual
    assert "Bearer " not in serialized_manual

    queued_manual = queue_archive_vault_handoff(manual)
    _print("QUEUED MANUAL HANDOFF", queued_manual)
    assert queued_manual.get("ok") is True

    # Create a fresh object inbox item and queue it for Archive Vault.
    decision = evaluate_ob_object_guard(
        user_id="beta_001",
        role="user",
        object_kind="export",
        object_id="export_064",
        action="download",
        route_key="export",
        current_risk_score=5,
    )
    _print("FRESH OBJECT DECISION", decision)
    assert decision.get("allowed") is False

    open_items = list_open_ob_object_security_inbox(limit=80)
    target = None
    for item in reversed(open_items.get("items", [])):
        if item.get("object_id") == "export_064":
            target = item
            break

    assert target is not None
    target_id = target.get("inbox_item_id")
    assert target_id

    object_handoff = queue_ob_object_security_inbox_item_for_archive(
        target_id,
        actor_user_id="owner_solice",
        owner_note="Pack 064: queue this object security event for future Archive Vault evidence bundle.",
    )
    _print("OBJECT SECURITY ARCHIVE HANDOFF", object_handoff)

    assert object_handoff.get("ok") is True
    assert object_handoff.get("handoff_id")
    assert object_handoff.get("record", {}).get("destination") == "Archive Vault"

    after = summarize_archive_vault_handoffs(limit=10)
    _print("AFTER ARCHIVE HANDOFF SUMMARY", after)

    assert after.get("ok") is True
    assert after.get("total", 0) >= before.get("total", 0) + 2
    assert after.get("queued", 0) >= 2
    assert "ob_object_security_inbox" in after.get("by_source_type", {}) or "manual_test" in after.get("by_source_type", {})

    listed = list_archive_vault_handoffs(limit=10)
    _print("LIST ARCHIVE HANDOFFS", {
        "total": listed.get("total"),
        "recent_count": len(listed.get("recent", [])),
        "path": str(ARCHIVE_HANDOFF_PATH),
    })

    serialized = json.dumps([after, listed], sort_keys=True, default=str)
    assert "SHOULD_NOT_SURVIVE" not in serialized
    assert "raw_token" not in serialized
    assert "tower_keycard" not in serialized
    assert "tower_keycard=" not in serialized
    assert "Soulaana:" in serialized

    final = {
        "pack": "064",
        "status": "passed",
        "human_reason": "Archive Vault handoff stub queues safe evidence-bundle requests for object security events without exposing secrets.",
    }
    _print("PACK 064 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
