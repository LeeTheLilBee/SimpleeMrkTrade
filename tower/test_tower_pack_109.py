
from __future__ import annotations

import json
import os
import sys
import subprocess
from pathlib import Path

PROJECT_ROOT = Path("/content/SimpleeMrkTrade_REAL_CLONE")
os.chdir(PROJECT_ROOT)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

WEB_APP = PROJECT_ROOT / "web" / "app.py"


def show(title, payload=None):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def no_secret(payload):
    s = json.dumps(payload, sort_keys=True, default=str).lower()
    bad = [
        "should_not_survive",
        "tower_keycard=",
        '"raw_token":',
        '"api_key":',
        '"password":',
        "ghp_should_not_survive",
        "sk_live_should_not_survive",
        "-----begin private key-----",
    ]
    for item in bad:
        assert item not in s, item


def run_tests():
    from tower.ob_object_permission_tightening import (
        check_export_permission,
        check_position_permission,
        check_symbol_permission,
        check_trade_permission,
        evaluate_ob_object_permission,
        reset_ob_object_permissions_for_test,
        summarize_ob_object_permissions,
    )
    from tower.ob_route_coverage_report import build_ob_route_coverage_report

    text = WEB_APP.read_text(encoding="utf-8", errors="replace")

    checks = {
        "pack109_helper_present": "PACK109_OBJECT_PERMISSION_ROUTE_HELPERS" in text,
        "pack109_marker_present": "PACK109: Tower object-level permission check." in text,
        "object_helper_present": "def _tower_object_permission_response_109" in text,
        "object_engine_import_present": "evaluate_ob_object_permission" in text,
        "pack104_helper_still_present": "PACK104_TOWER_OB_FLASK_GUARD_HELPERS" in text,
    }
    show("PACK 109 WEB APP CHECKS", checks)
    assert all(checks.values())

    object_guard_count = text.count("PACK109: Tower object-level permission check.")
    show("PACK 109 OBJECT GUARD COUNT", {"object_guard_count": object_guard_count})
    assert object_guard_count >= 5

    report = build_ob_route_coverage_report(write_panel=True)
    show("ROUTE COVERAGE STILL HEALTHY", {
        "coverage_pct": report.get("coverage_pct"),
        "guarded_needed_count": report.get("guarded_needed_count"),
        "needs_guard_count": report.get("needs_guard_count"),
        "unguarded_needed_count": report.get("unguarded_needed_count"),
        "unguarded_high_risk_count": report.get("unguarded_high_risk_count"),
        "readiness_score": report.get("readiness_score"),
    })
    assert report.get("coverage_pct") == 100
    assert report.get("unguarded_needed_count") == 0
    assert report.get("unguarded_high_risk_count") == 0

    reset = reset_ob_object_permissions_for_test()
    show("RESET OBJECT PERMISSIONS", reset)
    assert reset.get("ok") is True

    symbol = check_symbol_permission(user_id="public_user", role="public", symbol="MSFT")
    position_deny = check_position_permission(
        user_id="beta_109",
        role="beta",
        position_id="pos_not_mine_109",
        object_payload={"owner_user_id": "other_user"},
    )
    position_step = check_position_permission(
        user_id="beta_109",
        role="beta",
        position_id="pos_mine_109",
        action="close",
        object_payload={"owner_user_id": "beta_109"},
    )
    trade_deny = check_trade_permission(
        user_id="beta_109",
        role="beta",
        trade_id="trade_not_mine_109",
        object_payload={"owner_user_id": "other_user"},
    )
    export_step = check_export_permission(
        user_id="owner_solice",
        role="owner",
        export_id="export_109",
    )
    analysis_summary = evaluate_ob_object_permission(
        user_id="beta_109",
        role="beta",
        object_type="analysis",
        object_id="analysis_109",
        action="view",
    )

    smoke = {
        "symbol": symbol.get("decision"),
        "position_deny": position_deny.get("decision"),
        "position_step": position_step.get("decision"),
        "trade_deny": trade_deny.get("decision"),
        "export_step": export_step.get("decision"),
        "analysis_summary": analysis_summary.get("decision"),
    }
    show("PACK 109 OBJECT ENGINE SMOKE", smoke)

    assert smoke["symbol"] == "allow"
    assert smoke["position_deny"] == "deny"
    assert smoke["position_step"] == "step_up_required"
    assert smoke["trade_deny"] == "deny"
    assert smoke["export_step"] == "step_up_required"
    assert smoke["analysis_summary"] == "summary_only"

    status = summarize_ob_object_permissions(limit=80)
    show("PACK 109 OBJECT PERMISSION STATUS", {
        "event_count": status.get("event_count"),
        "by_decision": status.get("by_decision"),
        "by_object_type": status.get("by_object_type"),
        "readiness_score": status.get("readiness_score"),
        "no_secret_leakage": status.get("no_secret_leakage"),
    })

    assert status.get("ok") is True
    assert status.get("readiness_score") == 100
    assert status.get("event_count", 0) >= 6
    assert status.get("no_secret_leakage") is True
    no_secret(status)

    for path in [
        WEB_APP,
        PROJECT_ROOT / "tower" / "ob_object_permission_tightening.py",
        PROJECT_ROOT / "tower" / "test_tower_pack_109.py",
    ]:
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(path)],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
        )
        show("PY_COMPILE " + str(path), {
            "returncode": result.returncode,
            "stderr": result.stderr,
        })
        assert result.returncode == 0

    final = {
        "pack": "109",
        "status": "passed",
        "object_guard_count": object_guard_count,
        "human_reason": "Object-level permission checks are wired into selected route handlers while route coverage remains at 100%.",
    }
    show("PACK 109 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
