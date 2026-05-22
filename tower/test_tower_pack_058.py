
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
    OBJECT_SECURITY_INBOX_PATH,
    bridge_recent_object_audit_capsules_to_security_inbox,
    list_ob_object_security_inbox,
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
    before = summarize_ob_object_security_inbox(limit=5)
    before_total = before.get("total", 0)
    _print("BEFORE OBJECT SECURITY INBOX", {
        "total": before_total,
        "open": before.get("open"),
        "path": str(OBJECT_SECURITY_INBOX_PATH),
    })

    # Allowed view should be quiet or info-only, not necessarily create owner task.
    allowed = evaluate_ob_object_guard(
        user_id="owner_solice",
        role="owner",
        object_kind="symbol",
        object_id="MSFT",
        action="view",
        route_key="symbol_detail",
        current_risk_score=5,
    )
    _print("ALLOWED SYMBOL DECISION", allowed)
    assert allowed.get("allowed") is True
    assert allowed.get("metadata", {}).get("object_audit_capsule_id")

    # Denied export should create inbox item.
    denied_export = evaluate_ob_object_guard(
        user_id="beta_001",
        role="user",
        object_kind="export",
        object_id="export_058",
        action="download",
        route_key="export",
        current_risk_score=5,
    )
    _print("DENIED EXPORT DECISION", denied_export)
    assert denied_export.get("allowed") is False
    assert denied_export.get("metadata", {}).get("object_audit_capsule_id")

    # Unmapped object should create inbox item.
    unmapped = evaluate_ob_object_guard(
        user_id="owner_solice",
        role="owner",
        object_kind="unknown_drawer_058",
        object_id="secret_058",
        action="view",
        current_risk_score=5,
    )
    _print("UNMAPPED OBJECT DECISION", unmapped)
    assert unmapped.get("allowed") is False
    assert unmapped.get("reason_code") == "ob_object_unmapped_default_deny"

    bridge = bridge_recent_object_audit_capsules_to_security_inbox(limit=25)
    _print("BRIDGE RECENT RESULT", bridge)
    assert bridge.get("ok") is True

    after = summarize_ob_object_security_inbox(limit=10)
    _print("AFTER OBJECT SECURITY INBOX", after)

    assert after.get("ok") is True
    assert after.get("total", 0) >= before_total + 1
    assert after.get("open", 0) >= 1
    assert isinstance(after.get("by_reason"), dict)
    assert isinstance(after.get("by_object_type"), dict)
    assert "export" in after.get("by_object_type", {}) or "unknown_drawer_058" in after.get("by_object_type", {})

    listed = list_ob_object_security_inbox(limit=10)
    _print("LIST OBJECT SECURITY INBOX", {
        "total": listed.get("total"),
        "recent_count": len(listed.get("recent", [])),
    })
    assert listed.get("ok") is True
    assert len(listed.get("recent", [])) >= 1

    serialized = json.dumps(after, sort_keys=True, default=str)
    assert "raw_token" not in serialized
    assert "tower_keycard" not in serialized
    assert "tower_keycard=" not in serialized
    assert "Soulaana:" in serialized

    final = {
        "pack": "058",
        "status": "passed",
        "human_reason": "Review-worthy OB object audit capsules now become actionable object security inbox items.",
    }
    _print("PACK 058 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
