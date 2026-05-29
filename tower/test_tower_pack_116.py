
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
    )
    from tower.security_command_unified_owner_page import (
        UNIFIED_HTML_PATH,
        UNIFIED_STATUS_PATH,
        build_unified_owner_security_command_status,
        load_unified_owner_security_command_status,
        render_unified_owner_security_command_html,
        reset_unified_owner_security_command_for_test,
        write_unified_owner_security_command_html,
    )
    from tower.ob_route_coverage_report import build_ob_route_coverage_report
    from tower.ob_object_permission_integration_checkpoint import build_object_permission_integration_checkpoint
    from tower.security_command_composition_smoke import build_security_command_composition_status
    from tower.security_command_navigation_links import build_security_command_navigation_links_status

    reset_unified = reset_unified_owner_security_command_for_test()
    reset_objects = reset_ob_object_permissions_for_test()

    show("RESET PACK 116 UNIFIED PAGE", reset_unified)
    show("RESET OBJECT PERMISSIONS", reset_objects)

    assert reset_unified.get("ok") is True
    assert reset_objects.get("ok") is True

    seed = {
        "symbol": check_symbol_permission(user_id="public_user", role="public", symbol="DIA").get("decision"),
        "position_deny": check_position_permission(
            user_id="beta_116",
            role="beta",
            position_id="pos_other_116",
            object_payload={"owner_user_id": "other_user"},
        ).get("decision"),
        "position_step": check_position_permission(
            user_id="beta_116",
            role="beta",
            position_id="pos_mine_116",
            action="close",
            object_payload={"owner_user_id": "beta_116"},
        ).get("decision"),
        "trade_deny": check_trade_permission(
            user_id="beta_116",
            role="beta",
            trade_id="trade_other_116",
            object_payload={"owner_user_id": "other_user"},
        ).get("decision"),
        "export_step": check_export_permission(
            user_id="owner_solice",
            role="owner",
            export_id="export_116",
        ).get("decision"),
        "analysis_summary": evaluate_ob_object_permission(
            user_id="beta_116",
            role="beta",
            object_type="analysis",
            object_id="analysis_116",
            action="view",
        ).get("decision"),
        "admin_step": evaluate_ob_object_permission(
            user_id="owner_solice",
            role="owner",
            object_type="admin_panel",
            object_id="tower_admin_panel_116",
            action="view",
        ).get("decision"),
    }
    show("PACK 116 SEEDED OBJECT DECISIONS", seed)

    assert seed["symbol"] == "allow"
    assert seed["position_deny"] == "deny"
    assert seed["position_step"] == "step_up_required"
    assert seed["trade_deny"] == "deny"
    assert seed["export_step"] == "step_up_required"
    assert seed["analysis_summary"] == "summary_only"
    assert seed["admin_step"] == "step_up_required"

    status = build_unified_owner_security_command_status(write_html=True)
    show("PACK 116 UNIFIED STATUS", {
        "ok": status.get("ok"),
        "status": status.get("status"),
        "readiness_score": status.get("readiness_score"),
        "failed_checks": status.get("failed_checks"),
        "route_health": status.get("route_health"),
        "object_checkpoint": status.get("object_checkpoint"),
        "object_visibility": status.get("object_visibility"),
        "composition": status.get("composition"),
        "navigation": status.get("navigation"),
        "no_secret_leakage": status.get("no_secret_leakage"),
    })

    assert status.get("ok") is True
    assert status.get("status") == "passed"
    assert status.get("readiness_score") == 100
    assert status.get("failed_checks") == []
    assert status.get("route_health", {}).get("coverage_pct") == 100
    assert status.get("route_health", {}).get("unguarded_needed_count") == 0
    assert status.get("route_health", {}).get("unguarded_high_risk_count") == 0
    assert status.get("object_checkpoint", {}).get("status") == "passed"
    assert status.get("object_checkpoint", {}).get("helper_wrapped_count") == 0
    assert status.get("object_visibility", {}).get("readiness_score") == 100
    assert status.get("composition", {}).get("status") == "passed"
    assert status.get("navigation", {}).get("status") == "passed"
    assert status.get("navigation", {}).get("link_count", 0) >= 3
    assert status.get("no_secret_leakage") is True
    assert UNIFIED_STATUS_PATH.exists()
    assert UNIFIED_HTML_PATH.exists()
    no_secret(status)

    html = render_unified_owner_security_command_html(status)
    show("PACK 116 HTML CHECK", {
        "html_length": len(html),
        "has_page_marker": "PACK116_UNIFIED_OWNER_SECURITY_COMMAND_PAGE" in html,
        "has_owner_title": "The Tower Security Command" in html,
        "has_nav_section": "PACK115_SECURITY_COMMAND_NAVIGATION_LINKS_SECTION" in html,
        "has_object_section": "PACK113_SECURITY_COMMAND_OBJECT_VISIBILITY_SECTION" in html,
        "has_route_coverage": "Route Coverage" in html,
        "has_helper_wraps": "Helper Wraps" in html,
    })

    assert "PACK116_UNIFIED_OWNER_SECURITY_COMMAND_PAGE" in html
    assert "The Tower Security Command" in html
    assert "PACK115_SECURITY_COMMAND_NAVIGATION_LINKS_SECTION" in html
    assert "PACK113_SECURITY_COMMAND_OBJECT_VISIBILITY_SECTION" in html
    assert "Route Coverage" in html
    assert "Helper Wraps" in html
    assert "SHOULD_NOT_SURVIVE" not in html
    assert "tower_keycard=" not in html

    write_result = write_unified_owner_security_command_html(status)
    show("PACK 116 WRITE HTML", write_result)
    assert write_result.get("ok") is True
    assert UNIFIED_HTML_PATH.exists()

    html_file = UNIFIED_HTML_PATH.read_text(encoding="utf-8")
    assert "PACK116_UNIFIED_OWNER_SECURITY_COMMAND_PAGE" in html_file
    assert "PACK115_SECURITY_COMMAND_NAVIGATION_LINKS_SECTION" in html_file
    assert "PACK113_SECURITY_COMMAND_OBJECT_VISIBILITY_SECTION" in html_file
    assert "SHOULD_NOT_SURVIVE" not in html_file
    assert "tower_keycard=" not in html_file

    loaded = load_unified_owner_security_command_status()
    show("PACK 116 LOADED STATUS", {
        "ok": loaded.get("ok"),
        "status": loaded.get("status"),
        "readiness_score": loaded.get("readiness_score"),
        "status_path": loaded.get("status_path"),
        "html_path": loaded.get("html_path"),
    })
    assert loaded.get("ok") is True
    assert loaded.get("status") == "passed"
    assert loaded.get("readiness_score") == 100
    no_secret(loaded)

    # Final health after adding unified route.
    route_report = build_ob_route_coverage_report(write_panel=True)
    checkpoint = build_object_permission_integration_checkpoint(write_panel=True)
    composition = build_security_command_composition_status(write_html=True)
    navigation = build_security_command_navigation_links_status(write_panel=True)

    show("PACK 116 FINAL HEALTH", {
        "route_coverage_pct": route_report.get("coverage_pct"),
        "guarded_needed_count": route_report.get("guarded_needed_count"),
        "needs_guard_count": route_report.get("needs_guard_count"),
        "unguarded_needed_count": route_report.get("unguarded_needed_count"),
        "unguarded_high_risk_count": route_report.get("unguarded_high_risk_count"),
        "checkpoint_status": checkpoint.get("status"),
        "checkpoint_readiness": checkpoint.get("readiness_score"),
        "helper_wrapped_count": checkpoint.get("helper_wrapped_count"),
        "composition_status": composition.get("status"),
        "composition_readiness": composition.get("readiness_score"),
        "navigation_status": navigation.get("status"),
        "navigation_readiness": navigation.get("readiness_score"),
    })

    assert route_report.get("coverage_pct") == 100
    assert route_report.get("unguarded_needed_count") == 0
    assert route_report.get("unguarded_high_risk_count") == 0
    assert checkpoint.get("status") == "passed"
    assert checkpoint.get("readiness_score") == 100
    assert checkpoint.get("helper_wrapped_count") == 0
    assert composition.get("status") == "passed"
    assert composition.get("readiness_score") == 100
    assert navigation.get("status") == "passed"
    assert navigation.get("readiness_score") == 100

    app_text = WEB_APP.read_text(encoding="utf-8", errors="replace")
    app_checks = {
        "pack116_route_marker": "PACK116_UNIFIED_OWNER_SECURITY_COMMAND_ROUTE" in app_text,
        "pack116_route_path": "/tower/security-command-unified" in app_text,
        "pack116_route_guard": "pack116_unified_owner_security_command_route" in app_text,
    }
    show("PACK 116 WEB APP ROUTE CHECKS", app_checks)
    assert all(app_checks.values())

    for path in [
        PROJECT_ROOT / "tower" / "security_command_unified_owner_page.py",
        PROJECT_ROOT / "tower" / "test_tower_pack_116.py",
        PROJECT_ROOT / "tower" / "security_command_navigation_links.py",
        PROJECT_ROOT / "tower" / "security_command_composition_smoke.py",
        PROJECT_ROOT / "tower" / "security_command_object_visibility_integration.py",
        PROJECT_ROOT / "tower" / "ob_object_permission_visibility.py",
        PROJECT_ROOT / "tower" / "ob_object_permission_tightening.py",
        PROJECT_ROOT / "tower" / "ob_object_permission_integration_checkpoint.py",
        PROJECT_ROOT / "tower" / "security_command_page.py",
        PROJECT_ROOT / "tower" / "tower_status.py",
        PROJECT_ROOT / "web" / "app.py",
    ]:
        if path.exists():
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
        "pack": "116",
        "status": "passed",
        "readiness_score": status.get("readiness_score"),
        "route_coverage_pct": route_report.get("coverage_pct"),
        "guarded_needed_count": route_report.get("guarded_needed_count"),
        "needs_guard_count": route_report.get("needs_guard_count"),
        "helper_wrapped_count": checkpoint.get("helper_wrapped_count"),
        "human_reason": "Unified owner Security Command page composes navigation, object visibility, route coverage, object checkpoint, and smoke health into one command page.",
    }
    show("PACK 116 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
