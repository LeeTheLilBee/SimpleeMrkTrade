
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

from web.app import app
from tower.ob_object_guard import evaluate_ob_object_guard
from tower.ob_object_audit_capsules import list_open_ob_object_security_inbox
from tower.security_command_page import generate_security_command_dashboard
from tower.ui_action_audit import summarize_ui_action_audit_receipts


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
    dashboard = generate_security_command_dashboard()
    _print("DASHBOARD RESULT", {
        "ok": dashboard.get("ok"),
        "path": dashboard.get("path"),
        "bytes": dashboard.get("bytes"),
        "archive_vault_handoff_ok": dashboard.get("archive_vault_handoff_ok"),
    })

    assert dashboard.get("ok") is True

    html_path = Path(dashboard.get("path", ""))
    assert html_path.exists()

    html = html_path.read_text(encoding="utf-8", errors="replace")

    _print("FORM ENDPOINT CHECK", {
        "has_audited_endpoint": "/tower/security-command/object-inbox/action-audited" in html,
        "has_old_endpoint": "/tower/security-command/object-inbox/action\"" in html or "/tower/security-command/object-inbox/action'" in html,
        "has_object_inbox": "OB OBJECT SECURITY INBOX" in html,
        "has_owner_actions": "Owner Actions" in html,
    })

    assert "OB OBJECT SECURITY INBOX" in html
    assert "Owner Actions" in html
    assert "/tower/security-command/object-inbox/action-audited" in html

    # The old endpoint may still appear as text in comments/code, but not as form action.
    assert 'action="/tower/security-command/object-inbox/action"' not in html
    assert "action='/tower/security-command/object-inbox/action'" not in html

    # Prove the visible endpoint creates audit receipts.
    before = summarize_ui_action_audit_receipts(limit=5)

    decision = evaluate_ob_object_guard(
        user_id="beta_001",
        role="user",
        object_kind="export",
        object_id="export_076_visible_form",
        action="download",
        route_key="export",
        current_risk_score=5,
    )
    _print("FRESH OBJECT DECISION", decision)
    assert decision.get("allowed") is False

    open_items = list_open_ob_object_security_inbox(limit=180)
    target = None
    for item in reversed(open_items.get("items", [])):
        if item.get("object_id") == "export_076_visible_form":
            target = item
            break

    assert target is not None
    target_id = target.get("inbox_item_id")
    assert target_id

    client = app.test_client()
    resp = client.post("/tower/security-command/object-inbox/action-audited", data={
        "inbox_item_id": target_id,
        "action_type": "note",
        "note": "Pack 076 test: audited visible-form endpoint note.",
        "actor_user_id": "owner_solice",
    })
    data = _json(resp)
    _print("AUDITED FORM ENDPOINT RESPONSE", {
        "status": resp.status_code,
        "json": data,
    })

    assert resp.status_code == 200
    assert data.get("ok") is True
    assert data.get("ui_action_audit_receipt_id")

    after = summarize_ui_action_audit_receipts(limit=10)
    _print("UI ACTION AUDIT AFTER", after)

    assert after.get("ok") is True
    assert after.get("total", 0) >= before.get("total", 0) + 1
    assert after.get("by_action", {}).get("note", 0) >= 1

    serialized = json.dumps([dashboard, data, after], sort_keys=True, default=str) + html
    assert "tower_keycard=" not in serialized
    assert "SHOULD_NOT_SURVIVE" not in serialized
    assert "raw_token=" not in serialized
    assert '"raw_token":' not in serialized
    assert "Bearer SHOULD_NOT_SURVIVE" not in serialized
    assert "Soulaana:" in serialized

    final = {
        "pack": "076",
        "status": "passed",
        "human_reason": "Security Command object inbox forms now use audited endpoint by default and create receipts.",
    }
    _print("PACK 076 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
