
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
    from tower.security_command_owner_quick_actions import (
        QUICK_ACTIONS_PANEL_PATH,
        QUICK_ACTIONS_STATUS_PATH,
        build_owner_quick_actions_status,
        load_owner_quick_actions_status,
        owner_quick_actions_status_card,
        render_owner_quick_actions_section,
        reset_owner_quick_actions_for_test,
        write_owner_quick_actions_panel,
    )
    from tower.security_command_unified_owner_page import (
        build_unified_owner_security_command_status,
        render_unified_owner_security_command_html,
        write_unified_owner_security_command_html,
    )
    from tower.ob_route_coverage_report import build_ob_route_coverage_report
    from tower.ob_object_permission_integration_checkpoint import build_object_permission_integration_checkpoint

    reset_quick = reset_owner_quick_actions_for_test()
    reset_objects = reset_ob_object_permissions_for_test()

    show("RESET PACK 119 QUICK ACTIONS", reset_quick)
    show("RESET OBJECT PERMISSIONS", reset_objects)

    assert reset_quick.get("ok") is True
    assert reset_objects.get("ok") is True

    seed = {
        "symbol": check_symbol_permission(user_id="public_user", role="public", symbol="XLE").get("decision"),
        "position_deny": check_position_permission(
            user_id="beta_119",
            role="beta",
            position_id="pos_other_119",
            object_payload={"owner_user_id": "other_user"},
        ).get("decision"),
        "position_step": check_position_permission(
            user_id="beta_119",
            role="beta",
            position_id="pos_mine_119",
            action="close",
            object_payload={"owner_user_id": "beta_119"},
        ).get("decision"),
        "trade_deny": check_trade_permission(
            user_id="beta_119",
            role="beta",
            trade_id="trade_other_119",
            object_payload={"owner_user_id": "other_user"},
        ).get("decision"),
        "export_step": check_export_permission(
            user_id="owner_solice",
            role="owner",
            export_id="export_119",
        ).get("decision"),
        "analysis_summary": evaluate_ob_object_permission(
            user_id="beta_119",
            role="beta",
            object_type="analysis",
            object_id="analysis_119",
            action="view",
        ).get("decision"),
        "admin_step": evaluate_ob_object_permission(
            user_id="owner_solice",
            role="owner",
            object_type="admin_panel",
            object_id="tower_admin_panel_119",
            action="view",
        ).get("decision"),
    }
    show("PACK 119 SEEDED OBJECT DECISIONS", seed)

    assert seed["symbol"] == "allow"
    assert seed["position_deny"] == "deny"
    assert seed["position_step"] == "step_up_required"
    assert seed["trade_deny"] == "deny"
    assert seed["export_step"] == "step_up_required"
    assert seed["analysis_summary"] == "summary_only"
    assert seed["admin_step"] == "step_up_required"

    quick = build_owner_quick_actions_status(write_panel=True)
    show("PACK 119 QUICK ACTIONS STATUS", {
        "ok": quick.get("ok"),
        "status": quick.get("status"),
        "action_count": quick.get("action_count"),
        "readiness_score": quick.get("readiness_score"),
        "failed_checks": quick.get("failed_checks"),
        "actions": quick.get("actions"),
        "route_health": quick.get("route_health"),
        "preferred_health": quick.get("preferred_health"),
        "unified_health": quick.get("unified_health"),
        "no_secret_leakage": quick.get("no_secret_leakage"),
    })

    assert quick.get("ok") is True
    assert quick.get("status") == "passed"
    assert quick.get("action_count", 0) >= 6
    assert quick.get("readiness_score") == 100
    assert quick.get("failed_checks") == []
    assert quick.get("route_health", {}).get("coverage_pct") == 100
    assert quick.get("route_health", {}).get("unguarded_needed_count") == 0
    assert quick.get("route_health", {}).get("unguarded_high_risk_count") == 0
    assert quick.get("preferred_health", {}).get("preferred_route") == "/tower/security-command-unified"
    assert quick.get("unified_health", {}).get("status") == "passed"
    assert quick.get("no_secret_leakage") is True
    assert QUICK_ACTIONS_STATUS_PATH.exists()
    assert QUICK_ACTIONS_PANEL_PATH.exists()
    no_secret(quick)

    hrefs = {action.get("href") for action in quick.get("actions", [])}
    assert "/tower/security-command-unified" in hrefs
    assert "/tower/security-command-preferred.json" in hrefs
    assert "/tower/security-command-links.json" in hrefs
    assert "/tower/security-command-smoke" in hrefs
    assert "/tower/ob-guard-status.json" in hrefs
    assert "/tower/security-command" in hrefs

    section = render_owner_quick_actions_section(quick)
    show("PACK 119 QUICK ACTION HTML CHECK", {
        "html_length": len(section),
        "has_marker": "PACK119_OWNER_QUICK_ACTION_RAIL_SECTION" in section,
        "has_unified_link": "/tower/security-command-unified" in section,
        "has_preferred_json": "/tower/security-command-preferred.json" in section,
        "has_links_json": "/tower/security-command-links.json" in section,
        "has_title": "Owner Quick Actions" in section,
    })

    assert "PACK119_OWNER_QUICK_ACTION_RAIL_SECTION" in section
    assert "/tower/security-command-unified" in section
    assert "/tower/security-command-preferred.json" in section
    assert "/tower/security-command-links.json" in section
    assert "Owner Quick Actions" in section
    assert "SHOULD_NOT_SURVIVE" not in section
    assert "tower_keycard=" not in section

    panel = write_owner_quick_actions_panel(quick)
    show("PACK 119 QUICK ACTION PANEL WRITE", panel)
    assert panel.get("ok") is True
    assert QUICK_ACTIONS_PANEL_PATH.exists()

    card = owner_quick_actions_status_card()
    loaded = load_owner_quick_actions_status()
    show("PACK 119 STATUS CARD", card)
    show("PACK 119 LOADED STATUS", {
        "ok": loaded.get("ok"),
        "status": loaded.get("status"),
        "action_count": loaded.get("action_count"),
        "readiness_score": loaded.get("readiness_score"),
    })

    assert card.get("ok") is True
    assert card.get("pack") == "119"
    assert card.get("action_count", 0) >= 6
    assert card.get("readiness_score") == 100
    assert loaded.get("ok") is True
    assert loaded.get("status") == "passed"
    assert loaded.get("readiness_score") == 100
    no_secret(card)
    no_secret(loaded)

    from tower.tower_status import pack119_owner_quick_actions_status_bridge
    from tower.security_command_page import pack119_owner_quick_actions_html_section

    bridge_card = pack119_owner_quick_actions_status_bridge()
    bridge_html = pack119_owner_quick_actions_html_section()

    show("PACK 119 TOWER STATUS BRIDGE", bridge_card)
    show("PACK 119 SECURITY COMMAND HTML BRIDGE", {
        "html_length": len(bridge_html),
        "has_marker": "PACK119_OWNER_QUICK_ACTION_RAIL_SECTION" in bridge_html,
        "has_unified_link": "/tower/security-command-unified" in bridge_html,
    })

    assert bridge_card.get("ok") is True
    assert bridge_card.get("pack") == "119"
    assert bridge_card.get("readiness_score") == 100
    assert "PACK119_OWNER_QUICK_ACTION_RAIL_SECTION" in bridge_html
    assert "/tower/security-command-unified" in bridge_html
    assert "SHOULD_NOT_SURVIVE" not in bridge_html
    assert "tower_keycard=" not in bridge_html

    unified = build_unified_owner_security_command_status(write_html=True)
    unified_html = render_unified_owner_security_command_html(unified)

    show("PACK 119 UNIFIED HTML CHECK", {
        "html_length": len(unified_html),
        "has_pack119": "PACK119_UNIFIED_OWNER_PAGE_INCLUDES_QUICK_ACTION_RAIL" in unified_html,
        "has_quick_rail": "PACK119_OWNER_QUICK_ACTION_RAIL_SECTION" in unified_html,
        "has_preferred": "PACK117_SECURITY_COMMAND_PREFERRED_DESTINATION_SECTION" in unified_html,
        "has_nav": "PACK115_SECURITY_COMMAND_NAVIGATION_LINKS_SECTION" in unified_html,
        "has_object": "PACK113_SECURITY_COMMAND_OBJECT_VISIBILITY_SECTION" in unified_html,
    })

    assert unified.get("ok") is True
    assert unified.get("status") == "passed"
    assert unified.get("readiness_score") == 100
    assert "PACK119_UNIFIED_OWNER_PAGE_INCLUDES_QUICK_ACTION_RAIL" in unified_html
    assert "PACK119_OWNER_QUICK_ACTION_RAIL_SECTION" in unified_html
    assert "PACK117_SECURITY_COMMAND_PREFERRED_DESTINATION_SECTION" in unified_html
    assert "PACK115_SECURITY_COMMAND_NAVIGATION_LINKS_SECTION" in unified_html
    assert "PACK113_SECURITY_COMMAND_OBJECT_VISIBILITY_SECTION" in unified_html
    assert "SHOULD_NOT_SURVIVE" not in unified_html
    assert "tower_keycard=" not in unified_html

    write_unified = write_unified_owner_security_command_html(unified)
    show("PACK 119 WRITE UNIFIED HTML", write_unified)
    assert write_unified.get("ok") is True

    route_report = build_ob_route_coverage_report(write_panel=True)
    checkpoint = build_object_permission_integration_checkpoint(write_panel=True)

    show("PACK 119 FINAL HEALTH", {
        "route_coverage_pct": route_report.get("coverage_pct"),
        "guarded_needed_count": route_report.get("guarded_needed_count"),
        "needs_guard_count": route_report.get("needs_guard_count"),
        "unguarded_needed_count": route_report.get("unguarded_needed_count"),
        "unguarded_high_risk_count": route_report.get("unguarded_high_risk_count"),
        "checkpoint_status": checkpoint.get("status"),
        "checkpoint_readiness": checkpoint.get("readiness_score"),
        "helper_wrapped_count": checkpoint.get("helper_wrapped_count"),
    })

    assert route_report.get("coverage_pct") == 100
    assert route_report.get("unguarded_needed_count") == 0
    assert route_report.get("unguarded_high_risk_count") == 0
    assert checkpoint.get("status") == "passed"
    assert checkpoint.get("readiness_score") == 100
    assert checkpoint.get("helper_wrapped_count") == 0

    app_text = WEB_APP.read_text(encoding="utf-8", errors="replace")
    app_checks = {
        "pack119_route_marker": "PACK119_OWNER_QUICK_ACTIONS_ROUTE" in app_text,
        "pack119_route_path": "/tower/security-command-quick-actions.json" in app_text,
        "pack119_route_guard": "pack119_owner_quick_actions_route" in app_text,
    }
    show("PACK 119 WEB APP ROUTE CHECKS", app_checks)
    assert all(app_checks.values())

    for path in [
        PROJECT_ROOT / "tower" / "security_command_owner_quick_actions.py",
        PROJECT_ROOT / "tower" / "test_tower_pack_119.py",
        PROJECT_ROOT / "tower" / "security_command_unified_owner_page.py",
        PROJECT_ROOT / "tower" / "security_command_preferred_destination.py",
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
        "pack": "119",
        "status": "passed",
        "action_count": quick.get("action_count"),
        "readiness_score": quick.get("readiness_score"),
        "route_coverage_pct": route_report.get("coverage_pct"),
        "helper_wrapped_count": checkpoint.get("helper_wrapped_count"),
        "human_reason": "Unified owner Security Command page now includes an owner quick-action rail.",
    }
    show("PACK 119 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
