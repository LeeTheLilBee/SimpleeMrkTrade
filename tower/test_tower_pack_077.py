
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
from tower.tower_status import get_tower_status
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
    before = summarize_ui_action_audit_receipts(limit=5)
    _print("BEFORE UI ACTION AUDIT SUMMARY", before)

    # Create one fresh audited action so the panel has obvious data.
    decision = evaluate_ob_object_guard(
        user_id="beta_001",
        role="user",
        object_kind="export",
        object_id="export_077_receipt_panel",
        action="download",
        route_key="export",
        current_risk_score=5,
    )
    _print("FRESH OBJECT DECISION", decision)
    assert decision.get("allowed") is False

    open_items = list_open_ob_object_security_inbox(limit=220)
    target = None
    for item in reversed(open_items.get("items", [])):
        if item.get("object_id") == "export_077_receipt_panel":
            target = item
            break
    assert target is not None
    target_id = target.get("inbox_item_id")
    assert target_id

    client = app.test_client()
    resp = client.post("/tower/security-command/object-inbox/action-audited", data={
        "inbox_item_id": target_id,
        "action_type": "note",
        "note": "Pack 077 test: receipt panel visible note.",
        "actor_user_id": "owner_solice",
    })
    data = _json(resp)
    _print("AUDITED ACTION RESPONSE", {"status": resp.status_code, "json": data})
    assert resp.status_code == 200
    assert data.get("ok") is True
    assert data.get("ui_action_audit_receipt_id")

    after = summarize_ui_action_audit_receipts(limit=10)
    _print("AFTER UI ACTION AUDIT SUMMARY", after)

    assert after.get("ok") is True
    assert after.get("total", 0) >= before.get("total", 0) + 1
    assert after.get("by_action", {}).get("note", 0) >= 1

    status = get_tower_status()
    _print("TOWER STATUS UI ACTION AUDIT FIELDS", {
        "ui_action_audit_ok": status.get("ui_action_audit_ok"),
        "ui_action_audit_total": status.get("ui_action_audit_total"),
        "ui_action_audit_action_ok": status.get("ui_action_audit_action_ok"),
        "ui_action_audit_action_failed": status.get("ui_action_audit_action_failed"),
        "ui_action_audit_by_action": status.get("ui_action_audit_by_action"),
        "ui_action_audit_by_reason": status.get("ui_action_audit_by_reason"),
        "ui_action_audit_by_severity": status.get("ui_action_audit_by_severity"),
        "ui_action_audit_by_status_code": status.get("ui_action_audit_by_status_code"),
    })

    assert status.get("ui_action_audit_ok") is True
    assert status.get("ui_action_audit_total", 0) >= after.get("total", 0)
    assert status.get("ui_action_audit_action_ok", 0) >= 1
    assert "note" in status.get("ui_action_audit_by_action", {})

    dashboard = generate_security_command_dashboard()
    _print("SECURITY COMMAND DASHBOARD UI ACTION AUDIT FIELDS", {
        "ok": dashboard.get("ok"),
        "path": dashboard.get("path"),
        "bytes": dashboard.get("bytes"),
        "ui_action_audit_ok": dashboard.get("ui_action_audit_ok"),
        "ui_action_audit_total": dashboard.get("ui_action_audit_total"),
        "ui_action_audit_action_ok": dashboard.get("ui_action_audit_action_ok"),
        "ui_action_audit_action_failed": dashboard.get("ui_action_audit_action_failed"),
    })

    assert dashboard.get("ok") is True
    assert dashboard.get("ui_action_audit_ok") is True
    assert dashboard.get("ui_action_audit_total", 0) >= after.get("total", 0)

    html_path = Path(dashboard.get("path", ""))
    assert html_path.exists()
    html = html_path.read_text(encoding="utf-8", errors="replace")

    assert "UI ACTION AUDIT RECEIPTS" in html
    assert "Owner Button-Click Receipts" in html
    assert 'data-pack="077"' in html
    assert "Successful" in html
    assert "Failed / Blocked" in html
    assert "By Action" in html
    assert "By Reason" in html
    assert "By Status Code" in html
    assert "uiaudit_" in html or "UI action receipt" in html

    serialized = json.dumps([after, status, dashboard], sort_keys=True, default=str) + html
    assert "tower_keycard=" not in serialized
    assert "SHOULD_NOT_SURVIVE" not in serialized
    assert "raw_token=" not in serialized
    assert '"raw_token":' not in serialized
    assert "Bearer SHOULD_NOT_SURVIVE" not in serialized
    assert "Soulaana:" in serialized

    final = {
        "pack": "077",
        "status": "passed",
        "human_reason": "UI action audit receipts now appear in Tower status and Security Command UI.",
    }
    _print("PACK 077 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
