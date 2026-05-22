
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

from tower.ob_object_guard import evaluate_ob_object_guard
from tower.ob_object_audit_capsules import (
    add_note_to_ob_object_security_inbox_item,
    ignore_ob_object_security_inbox_item,
    list_open_ob_object_security_inbox,
    mark_ob_object_security_inbox_reviewing,
    resolve_ob_object_security_inbox_item,
    summarize_ob_object_security_inbox,
)


def _print(title, payload=None):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def run_tests():
    # Make sure we have a fresh open object inbox item for the workflow.
    decision = evaluate_ob_object_guard(
        user_id="beta_001",
        role="user",
        object_kind="export",
        object_id="export_061",
        action="download",
        route_key="export",
        current_risk_score=5,
    )
    _print("FRESH OBJECT DECISION", decision)
    assert decision.get("allowed") is False
    assert decision.get("metadata", {}).get("object_audit_capsule_id")

    open_items = list_open_ob_object_security_inbox(limit=20)
    _print("OPEN OBJECT INBOX ITEMS", {
        "total": open_items.get("total"),
        "count": open_items.get("count"),
    })

    assert open_items.get("ok") is True
    assert open_items.get("total", 0) >= 1

    target = None
    for item in reversed(open_items.get("items", [])):
        if item.get("object_id") == "export_061":
            target = item
            break

    if target is None:
        target = open_items.get("items", [])[-1]

    target_id = target.get("inbox_item_id")
    assert target_id

    note_result = add_note_to_ob_object_security_inbox_item(
        target_id,
        actor_user_id="owner_solice",
        note="Pack 061 test: adding owner note before review.",
    )
    _print("NOTE RESULT", note_result)
    assert note_result.get("ok") is True
    assert note_result.get("item", {}).get("owner_notes")

    reviewing = mark_ob_object_security_inbox_reviewing(
        target_id,
        actor_user_id="owner_solice",
        note="Pack 061 test: owner is reviewing this drawer event.",
    )
    _print("REVIEWING RESULT", reviewing)
    assert reviewing.get("ok") is True
    assert reviewing.get("new_status") == "reviewing"
    assert reviewing.get("item", {}).get("review_started_by") == "owner_solice"

    resolved = resolve_ob_object_security_inbox_item(
        target_id,
        actor_user_id="owner_solice",
        note="Pack 061 test: resolved as expected protected object block.",
        resolution_reason="expected_test_block",
    )
    _print("RESOLVED RESULT", resolved)
    assert resolved.get("ok") is True
    assert resolved.get("new_status") == "resolved"
    assert resolved.get("item", {}).get("resolved_by") == "owner_solice"
    assert resolved.get("item", {}).get("resolution_reason") == "expected_test_block"

    # Make a second item and ignore it to prove both terminal paths.
    second_decision = evaluate_ob_object_guard(
        user_id="owner_solice",
        role="owner",
        object_kind="unknown_drawer_061",
        object_id="secret_061",
        action="view",
        route_key="",
        current_risk_score=5,
    )
    _print("SECOND OBJECT DECISION", second_decision)
    assert second_decision.get("allowed") is False

    open_items_2 = list_open_ob_object_security_inbox(limit=30)
    ignore_target = None
    for item in reversed(open_items_2.get("items", [])):
        if item.get("object_id") == "secret_061":
            ignore_target = item
            break

    assert ignore_target is not None
    ignore_target_id = ignore_target.get("inbox_item_id")
    assert ignore_target_id

    ignored = ignore_ob_object_security_inbox_item(
        ignore_target_id,
        actor_user_id="owner_solice",
        note="Pack 061 test: ignored as test-generated unmapped object event.",
        resolution_reason="test_generated_noise",
    )
    _print("IGNORED RESULT", ignored)
    assert ignored.get("ok") is True
    assert ignored.get("new_status") == "ignored"
    assert ignored.get("item", {}).get("ignored_by") == "owner_solice"

    summary = summarize_ob_object_security_inbox(limit=10)
    _print("SUMMARY AFTER ACTIONS", summary)

    assert summary.get("ok") is True
    assert summary.get("by_status", {}).get("resolved", 0) >= 1
    assert summary.get("by_status", {}).get("ignored", 0) >= 1

    serialized = json.dumps(summary, sort_keys=True, default=str)
    assert "raw_token" not in serialized
    assert "tower_keycard" not in serialized
    assert "tower_keycard=" not in serialized
    assert "Soulaana:" in serialized

    final = {
        "pack": "061",
        "status": "passed",
        "human_reason": "OB object security inbox items can be noted, marked reviewing, resolved, and ignored with owner history.",
    }
    _print("PACK 061 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
