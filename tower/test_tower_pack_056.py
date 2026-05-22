
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

from tower.ob_object_audit_capsules import (
    OBJECT_AUDIT_PATH,
    list_ob_object_audit_capsules,
    record_ob_object_audit_capsule,
    summarize_ob_object_audit_capsules,
)
from tower.ob_object_guard import evaluate_ob_object_guard


def _print(title, payload=None):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def run_tests():
    before = list_ob_object_audit_capsules(limit=5)
    before_count = before.get("total", 0)
    _print("BEFORE OBJECT AUDIT", {
        "count": before_count,
        "path": str(OBJECT_AUDIT_PATH),
    })

    owner_symbol = evaluate_ob_object_guard(
        user_id="owner_solice",
        role="owner",
        object_kind="symbol",
        object_id="AAPL",
        action="view",
        route_key="symbol_detail",
        current_risk_score=5,
    )
    _print("OWNER SYMBOL DECISION", owner_symbol)
    assert owner_symbol.get("allowed") is True
    assert owner_symbol.get("metadata", {}).get("object_audit_capsule_id")

    beta_export = evaluate_ob_object_guard(
        user_id="beta_001",
        role="user",
        object_kind="export",
        object_id="export_056",
        action="download",
        route_key="export",
        current_risk_score=5,
    )
    _print("BETA EXPORT DECISION", beta_export)
    assert beta_export.get("allowed") is False
    assert beta_export.get("metadata", {}).get("object_audit_capsule_id")

    unmapped = evaluate_ob_object_guard(
        user_id="owner_solice",
        role="owner",
        object_kind="mystery_drawer",
        object_id="secret_056",
        action="view",
        current_risk_score=5,
    )
    _print("UNMAPPED OBJECT DECISION", unmapped)
    assert unmapped.get("allowed") is False
    assert unmapped.get("reason_code") == "ob_object_unmapped_default_deny"
    assert unmapped.get("metadata", {}).get("object_audit_capsule_id")

    manual_capsule = record_ob_object_audit_capsule(
        decision={
            "ok": True,
            "allowed": False,
            "decision": "deny",
            "reason_code": "manual_test_object_denied",
            "risk_score": 66,
            "risk_state": "restricted",
            "human_reason": "Manual test object decision.",
            "required_actions": ["owner_review"],
            "metadata": {
                "user_id": "beta_001",
                "object_type": "analysis_record",
                "object_id": "analysis_056",
                "action": "view",
                "tower_keycard": "SHOULD_NOT_SURVIVE",
                "raw_token": "SHOULD_NOT_SURVIVE",
            },
        },
        object_kind="analysis_record",
        object_type="analysis_record",
        object_id="analysis_056",
        action="view",
        route_key="analysis_vault",
        user_id="beta_001",
        metadata={"tower_keycard": "SHOULD_NOT_SURVIVE", "raw_token": "SHOULD_NOT_SURVIVE"},
    )
    _print("MANUAL CAPSULE", manual_capsule)
    assert manual_capsule.get("ok") is True
    assert manual_capsule.get("capsule_id")
    assert manual_capsule.get("allowed") is False

    after = summarize_ob_object_audit_capsules(limit=8)
    _print("AFTER SUMMARY", after)

    assert after.get("ok") is True
    assert after.get("total", 0) >= before_count + 4
    assert after.get("allowed", 0) >= 1
    assert after.get("denied", 0) >= 3
    assert "export" in after.get("by_object_type", {}) or "analysis_record" in after.get("by_object_type", {})

    serialized = json.dumps(after, sort_keys=True, default=str)
    assert "SHOULD_NOT_SURVIVE" not in serialized
    assert "tower_keycard=" not in serialized
    assert "raw_token" not in serialized
    assert "Soulaana:" in serialized

    final = {
        "pack": "056",
        "status": "passed",
        "human_reason": "OB object guard now writes audit capsules for allowed, denied, and unmapped object decisions without storing raw keycards or tokens.",
    }
    _print("PACK 056 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
