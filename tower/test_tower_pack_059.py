
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
from tower.ob_object_audit_capsules import summarize_ob_object_security_inbox
from tower.tower_status import get_tower_status
from tower.security_command_page import generate_security_command_dashboard


def _print(title, payload=None):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def run_tests():
    # Ensure a fresh object inbox item exists.
    decision = evaluate_ob_object_guard(
        user_id="beta_001",
        role="user",
        object_kind="export",
        object_id="export_059",
        action="download",
        route_key="export",
        current_risk_score=5,
    )
    _print("FRESH OBJECT DECISION", decision)
    assert decision.get("metadata", {}).get("object_audit_capsule_id")

    inbox = summarize_ob_object_security_inbox(limit=8)
    _print("DIRECT OBJECT SECURITY INBOX SUMMARY", inbox)
    assert inbox.get("ok") is True
    assert inbox.get("total", 0) >= 1
    assert inbox.get("open", 0) >= 1

    status = get_tower_status()
    status_fields = {
        "ob_object_security_inbox_ok": status.get("ob_object_security_inbox_ok"),
        "ob_object_security_inbox_total": status.get("ob_object_security_inbox_total"),
        "ob_object_security_inbox_open": status.get("ob_object_security_inbox_open"),
        "ob_object_security_inbox_by_status": status.get("ob_object_security_inbox_by_status"),
        "ob_object_security_inbox_by_reason": status.get("ob_object_security_inbox_by_reason"),
        "ob_object_security_inbox_by_severity": status.get("ob_object_security_inbox_by_severity"),
        "ob_object_security_inbox_by_object_type": status.get("ob_object_security_inbox_by_object_type"),
        "recent_count": len(status.get("ob_object_security_inbox_recent", [])),
    }
    _print("TOWER STATUS OBJECT SECURITY INBOX FIELDS", status_fields)

    assert status.get("ob_object_security_inbox_ok") is True
    assert status.get("ob_object_security_inbox_total", 0) >= inbox.get("total", 0)
    assert status.get("ob_object_security_inbox_open", 0) >= 1
    assert isinstance(status.get("ob_object_security_inbox_by_status"), dict)
    assert isinstance(status.get("ob_object_security_inbox_by_reason"), dict)
    assert isinstance(status.get("ob_object_security_inbox_by_severity"), dict)
    assert isinstance(status.get("ob_object_security_inbox_by_object_type"), dict)

    dashboard = generate_security_command_dashboard()
    _print("DASHBOARD RESULT", dashboard)

    assert isinstance(dashboard, dict)
    assert dashboard.get("ok") is True
    assert dashboard.get("ob_object_security_inbox_ok") is True
    assert dashboard.get("ob_object_security_inbox_total", 0) >= 1

    html_path = Path(dashboard.get("path", ""))
    assert html_path.exists()

    html = html_path.read_text(encoding="utf-8", errors="replace")
    assert "OB OBJECT SECURITY INBOX" in html
    assert "Drawer Review Queue" in html

    serialized = json.dumps([status_fields, dashboard], sort_keys=True, default=str)
    assert "raw_token" not in serialized
    assert "tower_keycard" not in serialized
    assert "tower_keycard=" not in serialized

    final = {
        "pack": "059",
        "status": "passed",
        "human_reason": "Tower status and Security Command UI now surface OB object security inbox totals, groups, and recent drawer-review tasks.",
    }
    _print("PACK 059 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
