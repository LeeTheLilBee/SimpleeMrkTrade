
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
from tower.ob_object_audit_capsules import summarize_ob_object_audit_capsules
from tower.tower_status import get_tower_status


def _print(title, payload=None):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def run_tests():
    decision = evaluate_ob_object_guard(
        user_id="beta_001",
        role="user",
        object_kind="export",
        object_id="export_057",
        action="download",
        route_key="export",
        current_risk_score=5,
    )
    _print("FRESH OBJECT DECISION", decision)
    assert decision.get("metadata", {}).get("object_audit_capsule_id")

    direct_summary = summarize_ob_object_audit_capsules(limit=5)
    _print("DIRECT OBJECT AUDIT SUMMARY", direct_summary)
    assert direct_summary.get("ok") is True
    assert direct_summary.get("total", 0) >= 1

    status = get_tower_status()
    fields = {
        "ob_object_audit_ok": status.get("ob_object_audit_ok"),
        "ob_object_audit_total": status.get("ob_object_audit_total"),
        "ob_object_audit_allowed": status.get("ob_object_audit_allowed"),
        "ob_object_audit_denied": status.get("ob_object_audit_denied"),
        "ob_object_audit_by_reason": status.get("ob_object_audit_by_reason"),
        "ob_object_audit_by_object_type": status.get("ob_object_audit_by_object_type"),
        "ob_object_audit_by_severity": status.get("ob_object_audit_by_severity"),
        "recent_count": len(status.get("ob_object_audit_recent", [])),
    }
    _print("TOWER STATUS OBJECT AUDIT FIELDS", fields)

    assert status.get("ob_object_audit_ok") is True
    assert status.get("ob_object_audit_total", 0) >= direct_summary.get("total", 0)
    assert status.get("ob_object_audit_denied", 0) >= 1
    assert isinstance(status.get("ob_object_audit_by_reason"), dict)
    assert isinstance(status.get("ob_object_audit_by_object_type"), dict)
    assert isinstance(status.get("ob_object_audit_by_severity"), dict)
    assert isinstance(status.get("ob_object_audit_recent"), list)

    serialized = json.dumps(fields, sort_keys=True, default=str)
    assert "raw_token" not in serialized
    assert "tower_keycard" not in serialized
    assert "tower_keycard=" not in serialized

    final = {
        "pack": "057",
        "status": "passed",
        "human_reason": "Tower status now surfaces OB object audit totals, allowed/denied counts, reason/object/severity groups, and recent receipts.",
    }
    _print("PACK 057 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
