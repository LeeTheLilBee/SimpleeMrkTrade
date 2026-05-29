
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
    from tower.ob_object_permission_integration_checkpoint import (
        build_object_permission_integration_checkpoint,
        parse_functions_with_object_guards,
    )
    from tower.ob_route_coverage_report import build_ob_route_coverage_report
    from tower.ob_object_permission_tightening import (
        check_export_permission,
        check_position_permission,
        check_symbol_permission,
        check_trade_permission,
        evaluate_ob_object_permission,
        reset_ob_object_permissions_for_test,
        summarize_ob_object_permissions,
    )

    text = WEB_APP.read_text(encoding="utf-8", errors="replace")

    marker_checks = {
        "pack104_helper_present": "PACK104_TOWER_OB_FLASK_GUARD_HELPERS" in text,
        "pack105_status_present": "PACK105_TOWER_OB_GUARD_STATUS_ROUTE" in text,
        "pack106_marker_present": "PACK106: Tower guard for high-risk Observatory route." in text,
        "pack107_marker_present": "PACK107: Tower guard for remaining protected Observatory route." in text,
        "pack109_helper_present": "PACK109_OBJECT_PERMISSION_ROUTE_HELPERS" in text,
        "pack109_marker_present": "PACK109: Tower object-level permission check." in text,
    }
    show("PACK 111 MARKER CHECKS", marker_checks)
    assert all(marker_checks.values())

    guards = parse_functions_with_object_guards(text)
    helper_wrapped = [
        item for item in guards
        if item.get("looks_like_helper_or_internal") and not item.get("is_expected_route_target")
    ]

    show("PACK 111 OBJECT GUARD SCAN", {
        "object_guard_count": len(guards),
        "helper_wrapped_count": len(helper_wrapped),
        "helper_wrapped": helper_wrapped,
        "guards": guards,
    })

    assert len(guards) >= 8
    assert len(helper_wrapped) == 0

    expected_route_targets = {
        "signal_symbol_page",
        "my_position_detail_page",
        "edit_my_position",
        "close_my_position",
        "my_positions_archived_page",
        "analyze_my_trades_page",
        "trade_detail_page",
        "reports_page",
    }

    present = {item.get("function_name") for item in guards}
    missing = sorted(expected_route_targets - present)
    show("PACK 111 EXPECTED OBJECT TARGETS", {
        "missing": missing,
        "present_count": len(expected_route_targets & present),
    })
    assert missing == []

    route_report = build_ob_route_coverage_report(write_panel=True)
    show("PACK 111 ROUTE COVERAGE", {
        "coverage_pct": route_report.get("coverage_pct"),
        "guarded_needed_count": route_report.get("guarded_needed_count"),
        "needs_guard_count": route_report.get("needs_guard_count"),
        "unguarded_needed_count": route_report.get("unguarded_needed_count"),
        "unguarded_high_risk_count": route_report.get("unguarded_high_risk_count"),
        "readiness_score": route_report.get("readiness_score"),
    })

    assert route_report.get("coverage_pct") == 100
    assert route_report.get("unguarded_needed_count") == 0
    assert route_report.get("unguarded_high_risk_count") == 0
    assert route_report.get("readiness_score") == 100

    reset = reset_ob_object_permissions_for_test()
    show("RESET OBJECT PERMISSIONS", reset)
    assert reset.get("ok") is True

    smoke = {
        "symbol": check_symbol_permission(user_id="public_user", role="public", symbol="NVDA").get("decision"),
        "position_deny": check_position_permission(
            user_id="beta_111",
            role="beta",
            position_id="pos_other_111",
            object_payload={"owner_user_id": "other_user"},
        ).get("decision"),
        "position_step": check_position_permission(
            user_id="beta_111",
            role="beta",
            position_id="pos_mine_111",
            action="close",
            object_payload={"owner_user_id": "beta_111"},
        ).get("decision"),
        "trade_deny": check_trade_permission(
            user_id="beta_111",
            role="beta",
            trade_id="trade_other_111",
            object_payload={"owner_user_id": "other_user"},
        ).get("decision"),
        "export_step": check_export_permission(
            user_id="owner_solice",
            role="owner",
            export_id="export_111",
        ).get("decision"),
        "analysis_summary": evaluate_ob_object_permission(
            user_id="beta_111",
            role="beta",
            object_type="analysis",
            object_id="analysis_111",
            action="view",
        ).get("decision"),
    }
    show("PACK 111 OBJECT ENGINE SMOKE", smoke)

    assert smoke["symbol"] == "allow"
    assert smoke["position_deny"] == "deny"
    assert smoke["position_step"] == "step_up_required"
    assert smoke["trade_deny"] == "deny"
    assert smoke["export_step"] == "step_up_required"
    assert smoke["analysis_summary"] == "summary_only"

    object_status = summarize_ob_object_permissions(limit=80)
    show("PACK 111 OBJECT STATUS", {
        "event_count": object_status.get("event_count"),
        "by_decision": object_status.get("by_decision"),
        "by_object_type": object_status.get("by_object_type"),
        "readiness_score": object_status.get("readiness_score"),
        "no_secret_leakage": object_status.get("no_secret_leakage"),
    })

    assert object_status.get("ok") is True
    assert object_status.get("readiness_score") == 100
    assert object_status.get("no_secret_leakage") is True
    no_secret(object_status)

    checkpoint = build_object_permission_integration_checkpoint(write_panel=True)
    show("PACK 111 INTEGRATION CHECKPOINT", {
        "ok": checkpoint.get("ok"),
        "status": checkpoint.get("status"),
        "readiness_score": checkpoint.get("readiness_score"),
        "object_guard_count": checkpoint.get("object_guard_count"),
        "helper_wrapped_count": checkpoint.get("helper_wrapped_count"),
        "expected_missing": checkpoint.get("expected_missing"),
        "expected_wrong_type": checkpoint.get("expected_wrong_type"),
        "failed_checks": checkpoint.get("failed_checks"),
        "warnings": checkpoint.get("warnings"),
    })

    assert checkpoint.get("ok") is True
    assert checkpoint.get("status") == "passed"
    assert checkpoint.get("readiness_score") == 100
    assert checkpoint.get("helper_wrapped_count") == 0
    assert checkpoint.get("expected_missing") == []
    assert checkpoint.get("expected_wrong_type") == []
    assert checkpoint.get("failed_checks") == []
    assert checkpoint.get("no_secret_leakage") is True
    no_secret(checkpoint)

    for path in [
        WEB_APP,
        PROJECT_ROOT / "tower" / "ob_object_permission_integration_checkpoint.py",
        PROJECT_ROOT / "tower" / "ob_object_permission_tightening.py",
        PROJECT_ROOT / "tower" / "test_tower_pack_111.py",
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
        "pack": "111",
        "status": "passed",
        "object_guard_count": checkpoint.get("object_guard_count"),
        "helper_wrapped_count": checkpoint.get("helper_wrapped_count"),
        "route_coverage_pct": route_report.get("coverage_pct"),
        "readiness_score": checkpoint.get("readiness_score"),
        "human_reason": "Helper/internal object guards were cleaned while route and object coverage stayed healthy.",
    }
    show("PACK 111 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
