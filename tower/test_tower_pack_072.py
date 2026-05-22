
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
    if name == "web.app" or name == "web" or name.startswith("tower."):
        sys.modules.pop(name, None)

from web.app import app
from tower.ob_object_guard import evaluate_ob_object_guard
from tower.ob_object_audit_capsules import list_open_ob_object_security_inbox
from tower.ui_action_audit import (
    list_ui_action_audit_receipts,
    record_ui_action_audit_receipt,
    summarize_ui_action_audit_receipts,
)


def _print(title, payload=None):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def _json(resp):
    try:
        return resp.get_json()
    except Exception:
        return None


def run_tests():
    before = summarize_ui_action_audit_receipts(limit=5)
    _print("BEFORE UI ACTION AUDIT SUMMARY", before)

    manual = record_ui_action_audit_receipt(
        endpoint="/manual-pack-072",
        action_type="manual_test",
        actor_user_id="owner_solice",
        inbox_item_id="manual_072",
        ok=True,
        status_code=200,
        reason_code="manual_test_ok",
        human_reason="Manual Pack 072 test receipt.",
        request_payload={
            "safe": "yes",
            "raw_token": "SHOULD_NOT_SURVIVE",
            "tower_keycard": "SHOULD_NOT_SURVIVE",
        },
        result_payload={
            "safe_result": "yes",
            "authorization": "Bearer SHOULD_NOT_SURVIVE",
        },
    )
    _print("MANUAL RECEIPT", manual)

    serialized_manual = json.dumps(manual, sort_keys=True, default=str)
    assert "SHOULD_NOT_SURVIVE" not in serialized_manual
    assert "raw_token" not in serialized_manual
    assert "tower_keycard" not in serialized_manual
    assert "Bearer " not in serialized_manual

    client = app.test_client()

    decision = evaluate_ob_object_guard(
        user_id="beta_001",
        role="user",
        object_kind="export",
        object_id="export_072_resolve",
        action="download",
        route_key="export",
        current_risk_score=5,
    )
    _print("FRESH RESOLVE TARGET DECISION", decision)
    assert decision.get("allowed") is False

    open_items = list_open_ob_object_security_inbox(limit=120)
    target = None
    for item in reversed(open_items.get("items", [])):
        if item.get("object_id") == "export_072_resolve":
            target = item
            break
    assert target is not None
    target_id = target.get("inbox_item_id")
    assert target_id

    note_resp = client.post("/tower/security-command/object-inbox/action-audited", data={
        "inbox_item_id": target_id,
        "action_type": "note",
        "note": "Pack 072 audited endpoint test: owner note.",
        "actor_user_id": "owner_solice",
    })
    note_json = _json(note_resp)
    _print("AUDITED NOTE RESPONSE", {"status": note_resp.status_code, "json": note_json})
    assert note_resp.status_code == 200
    assert note_json.get("ok") is True
    assert note_json.get("ui_action_audit_receipt_id")

    review_resp = client.post("/tower/security-command/object-inbox/action-audited", data={
        "inbox_item_id": target_id,
        "action_type": "reviewing",
        "note": "Pack 072 audited endpoint test: reviewing.",
        "actor_user_id": "owner_solice",
    })
    review_json = _json(review_resp)
    _print("AUDITED REVIEW RESPONSE", {"status": review_resp.status_code, "json": review_json})
    assert review_resp.status_code == 200
    assert review_json.get("ok") is True
    assert review_json.get("ui_action_audit_receipt_id")
    assert review_json.get("result", {}).get("new_status") == "reviewing"

    resolve_resp = client.post("/tower/security-command/object-inbox/action-audited", data={
        "inbox_item_id": target_id,
        "action_type": "resolve",
        "note": "Pack 072 audited endpoint test: resolved.",
        "resolution_reason": "pack072_endpoint_resolved",
        "actor_user_id": "owner_solice",
    })
    resolve_json = _json(resolve_resp)
    _print("AUDITED RESOLVE RESPONSE", {"status": resolve_resp.status_code, "json": resolve_json})
    assert resolve_resp.status_code == 200
    assert resolve_json.get("ok") is True
    assert resolve_json.get("ui_action_audit_receipt_id")
    assert resolve_json.get("result", {}).get("new_status") == "resolved"

    bad_resp = client.post("/tower/security-command/object-inbox/action-audited", data={
        "inbox_item_id": target_id,
        "action_type": "explode",
    })
    bad_json = _json(bad_resp)
    _print("AUDITED BAD ACTION RESPONSE", {"status": bad_resp.status_code, "json": bad_json})
    assert bad_resp.status_code == 400
    assert bad_json.get("reason_code") == "invalid_object_inbox_action_type"
    assert bad_json.get("ui_action_audit_receipt_id")

    missing_resp = client.post("/tower/security-command/object-inbox/action-audited", data={
        "action_type": "note",
        "note": "No id.",
    })
    missing_json = _json(missing_resp)
    _print("AUDITED MISSING ID RESPONSE", {"status": missing_resp.status_code, "json": missing_json})
    assert missing_resp.status_code == 400
    assert missing_json.get("reason_code") == "object_inbox_item_id_required"
    assert missing_json.get("ui_action_audit_receipt_id")

    after = summarize_ui_action_audit_receipts(limit=12)
    _print("AFTER UI ACTION AUDIT SUMMARY", after)

    assert after.get("ok") is True
    assert after.get("total", 0) >= before.get("total", 0) + 6
    assert after.get("action_ok", 0) >= 4
    assert after.get("action_failed", 0) >= 2
    assert after.get("by_action", {}).get("note", 0) >= 1
    assert after.get("by_action", {}).get("reviewing", 0) >= 1
    assert after.get("by_action", {}).get("resolve", 0) >= 1
    assert after.get("by_action", {}).get("explode", 0) >= 1

    listed = list_ui_action_audit_receipts(limit=12)
    _print("LIST UI ACTION AUDIT RECEIPTS", {
        "total": listed.get("total"),
        "recent_count": len(listed.get("recent", [])),
        "path": listed.get("path"),
    })
    assert listed.get("ok") is True

    serialized = json.dumps([note_json, review_json, resolve_json, bad_json, missing_json, after, listed], sort_keys=True, default=str)
    assert "tower_keycard=" not in serialized
    assert "SHOULD_NOT_SURVIVE" not in serialized
    assert "raw_token=" not in serialized
    assert '"raw_token":' not in serialized
    assert "Bearer SHOULD_NOT_SURVIVE" not in serialized
    assert "Soulaana:" in serialized

    final = {
        "pack": "072",
        "status": "passed",
        "human_reason": "Object inbox UI actions now create audit receipts for successful and failed owner actions.",
    }
    _print("PACK 072 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
