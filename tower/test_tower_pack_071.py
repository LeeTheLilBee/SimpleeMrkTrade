
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
from tower.ob_object_audit_capsules import list_open_ob_object_security_inbox, summarize_ob_object_security_inbox


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
    client = app.test_client()

    # Make a fresh target for note/review/resolve.
    decision = evaluate_ob_object_guard(
        user_id="beta_001",
        role="user",
        object_kind="export",
        object_id="export_071_resolve",
        action="download",
        route_key="export",
        current_risk_score=5,
    )
    _print("FRESH RESOLVE TARGET DECISION", decision)
    assert decision.get("allowed") is False

    open_items = list_open_ob_object_security_inbox(limit=100)
    target = None
    for item in reversed(open_items.get("items", [])):
        if item.get("object_id") == "export_071_resolve":
            target = item
            break
    assert target is not None
    target_id = target.get("inbox_item_id")
    assert target_id

    note_resp = client.post("/tower/security-command/object-inbox/action", data={
        "inbox_item_id": target_id,
        "action_type": "note",
        "note": "Pack 071 UI endpoint test: owner note.",
        "actor_user_id": "owner_solice",
    })
    note_json = _json(note_resp)
    _print("NOTE RESPONSE", {"status": note_resp.status_code, "json": note_json})
    assert note_resp.status_code == 200
    assert note_json.get("ok") is True
    assert note_json.get("action_type") == "note"

    review_resp = client.post("/tower/security-command/object-inbox/action", data={
        "inbox_item_id": target_id,
        "action_type": "reviewing",
        "note": "Pack 071 UI endpoint test: reviewing.",
        "actor_user_id": "owner_solice",
    })
    review_json = _json(review_resp)
    _print("REVIEW RESPONSE", {"status": review_resp.status_code, "json": review_json})
    assert review_resp.status_code == 200
    assert review_json.get("ok") is True
    assert review_json.get("result", {}).get("new_status") == "reviewing"

    resolve_resp = client.post("/tower/security-command/object-inbox/action", data={
        "inbox_item_id": target_id,
        "action_type": "resolve",
        "note": "Pack 071 UI endpoint test: resolved.",
        "resolution_reason": "pack071_endpoint_resolved",
        "actor_user_id": "owner_solice",
    })
    resolve_json = _json(resolve_resp)
    _print("RESOLVE RESPONSE", {"status": resolve_resp.status_code, "json": resolve_json})
    assert resolve_resp.status_code == 200
    assert resolve_json.get("ok") is True
    assert resolve_json.get("result", {}).get("new_status") == "resolved"
    assert resolve_json.get("result", {}).get("item", {}).get("resolution_reason") == "pack071_endpoint_resolved"

    # Make a fresh target for ignore.
    decision_2 = evaluate_ob_object_guard(
        user_id="owner_solice",
        role="owner",
        object_kind="unknown_drawer_071",
        object_id="secret_071_ignore",
        action="view",
        route_key="",
        current_risk_score=5,
    )
    _print("FRESH IGNORE TARGET DECISION", decision_2)
    assert decision_2.get("allowed") is False

    open_items_2 = list_open_ob_object_security_inbox(limit=120)
    ignore_target = None
    for item in reversed(open_items_2.get("items", [])):
        if item.get("object_id") == "secret_071_ignore":
            ignore_target = item
            break
    assert ignore_target is not None
    ignore_id = ignore_target.get("inbox_item_id")
    assert ignore_id

    ignore_resp = client.post("/tower/security-command/object-inbox/action", data={
        "inbox_item_id": ignore_id,
        "action_type": "ignore",
        "note": "Pack 071 UI endpoint test: ignored.",
        "resolution_reason": "pack071_endpoint_ignored",
        "actor_user_id": "owner_solice",
    })
    ignore_json = _json(ignore_resp)
    _print("IGNORE RESPONSE", {"status": ignore_resp.status_code, "json": ignore_json})
    assert ignore_resp.status_code == 200
    assert ignore_json.get("ok") is True
    assert ignore_json.get("result", {}).get("new_status") == "ignored"
    assert ignore_json.get("result", {}).get("item", {}).get("resolution_reason") == "pack071_endpoint_ignored"

    bad_action = client.post("/tower/security-command/object-inbox/action", data={
        "inbox_item_id": ignore_id,
        "action_type": "explode",
    })
    bad_json = _json(bad_action)
    _print("BAD ACTION RESPONSE", {"status": bad_action.status_code, "json": bad_json})
    assert bad_action.status_code == 400
    assert bad_json.get("reason_code") == "invalid_object_inbox_action_type"

    missing_id = client.post("/tower/security-command/object-inbox/action", data={
        "action_type": "note",
        "note": "No id.",
    })
    missing_json = _json(missing_id)
    _print("MISSING ID RESPONSE", {"status": missing_id.status_code, "json": missing_json})
    assert missing_id.status_code == 400
    assert missing_json.get("reason_code") == "object_inbox_item_id_required"

    summary = summarize_ob_object_security_inbox(limit=10)
    _print("SUMMARY AFTER UI ENDPOINT ACTIONS", summary)
    assert summary.get("by_status", {}).get("resolved", 0) >= 1
    assert summary.get("by_status", {}).get("ignored", 0) >= 1

    serialized = json.dumps([note_json, review_json, resolve_json, ignore_json, bad_json, missing_json, summary], sort_keys=True, default=str)
    assert "tower_keycard=" not in serialized
    assert "SHOULD_NOT_SURVIVE" not in serialized
    assert "raw_token=" not in serialized
    assert '"raw_token":' not in serialized
    assert "Soulaana:" in serialized

    final = {
        "pack": "071",
        "status": "passed",
        "human_reason": "Object inbox UI POST endpoint processes note, reviewing, resolve, and ignore actions safely.",
    }
    _print("PACK 071 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
