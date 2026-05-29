
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
    from tower.security_command_preferred_destination import (
        PREFERRED_PANEL_PATH,
        PREFERRED_SECURITY_COMMAND_ROUTE,
        PREFERRED_STATUS_PATH,
        build_security_command_preferred_destination_status,
        load_security_command_preferred_destination_status,
        preferred_security_command_links,
        render_security_command_preferred_destination_section,
        reset_security_command_preferred_destination_for_test,
        security_command_preferred_destination_status_card,
        write_security_command_preferred_destination_panel,
    )
    from tower.security_command_navigation_links import build_security_command_navigation_links_status
    from tower.security_command_unified_owner_page import build_unified_owner_security_command_status
    from tower.ob_route_coverage_report import build_ob_route_coverage_report
    from tower.ob_object_permission_integration_checkpoint import build_object_permission_integration_checkpoint

    reset_pref = reset_security_command_preferred_destination_for_test()
    reset_objects = reset_ob_object_permissions_for_test()

    show("RESET PACK 117 PREFERRED DESTINATION", reset_pref)
    show("RESET OBJECT PERMISSIONS", reset_objects)

    assert reset_pref.get("ok") is True
    assert reset_objects.get("ok") is True

    seed = {
        "symbol": check_symbol_permission(user_id="public_user", role="public", symbol="IWM").get("decision"),
        "position_deny": check_position_permission(
            user_id="beta_117",
            role="beta",
            position_id="pos_other_117",
            object_payload={"owner_user_id": "other_user"},
        ).get("decision"),
        "position_step": check_position_permission(
            user_id="beta_117",
            role="beta",
            position_id="pos_mine_117",
            action="close",
            object_payload={"owner_user_id": "beta_117"},
        ).get("decision"),
        "trade_deny": check_trade_permission(
            user_id="beta_117",
            role="beta",
            trade_id="trade_other_117",
            object_payload={"owner_user_id": "other_user"},
        ).get("decision"),
        "export_step": check_export_permission(
            user_id="owner_solice",
            role="owner",
            export_id="export_117",
        ).get("decision"),
        "analysis_summary": evaluate_ob_object_permission(
            user_id="beta_117",
            role="beta",
            object_type="analysis",
            object_id="analysis_117",
            action="view",
        ).get("decision"),
        "admin_step": evaluate_ob_object_permission(
            user_id="owner_solice",
            role="owner",
            object_type="admin_panel",
            object_id="tower_admin_panel_117",
            action="view",
        ).get("decision"),
    }
    show("PACK 117 SEEDED OBJECT DECISIONS", seed)

    assert seed["symbol"] == "allow"
    assert seed["position_deny"] == "deny"
    assert seed["position_step"] == "step_up_required"
    assert seed["trade_deny"] == "deny"
    assert seed["export_step"] == "step_up_required"
    assert seed["analysis_summary"] == "summary_only"
    assert seed["admin_step"] == "step_up_required"

    links = preferred_security_command_links()
    show("PACK 117 PREFERRED LINKS", links)

    hrefs = {link.get("href") for link in links}
    assert "/tower/security-command-unified" in hrefs
    assert "/tower/security-command" in hrefs
    assert "/tower/security-command-smoke" in hrefs
    assert "/tower/security-command-links.json" in hrefs
    assert "/tower/ob-guard-status.json" in hrefs

    status = build_security_command_preferred_destination_status(write_panel=True)
    show("PACK 117 PREFERRED STATUS", {
        "ok": status.get("ok"),
        "status": status.get("status"),
        "preferred_route": status.get("preferred_route"),
        "legacy_route": status.get("legacy_route"),
        "link_count": status.get("link_count"),
        "readiness_score": status.get("readiness_score"),
        "failed_checks": status.get("failed_checks"),
        "route_health": status.get("route_health"),
        "unified_health": status.get("unified_health"),
        "navigation_health": status.get("navigation_health"),
        "no_secret_leakage": status.get("no_secret_leakage"),
    })

    assert status.get("ok") is True
    assert status.get("status") == "passed"
    assert status.get("preferred_route") == PREFERRED_SECURITY_COMMAND_ROUTE
    assert status.get("preferred_route") == "/tower/security-command-unified"
    assert status.get("legacy_route") == "/tower/security-command"
    assert status.get("link_count") >= 5
    assert status.get("readiness_score") == 100
    assert status.get("failed_checks") == []
    assert status.get("route_health", {}).get("coverage_pct") == 100
    assert status.get("route_health", {}).get("unguarded_needed_count") == 0
    assert status.get("route_health", {}).get("unguarded_high_risk_count") == 0
    assert status.get("unified_health", {}).get("status") == "passed"
    assert status.get("navigation_health", {}).get("status") == "passed"
    assert status.get("no_secret_leakage") is True
    assert PREFERRED_STATUS_PATH.exists()
    assert PREFERRED_PANEL_PATH.exists()
    no_secret(status)

    nav_status = build_security_command_navigation_links_status(write_panel=True)
    show("PACK 117 NAVIGATION STATUS AFTER OVERRIDE", {
        "ok": nav_status.get("ok"),
        "status": nav_status.get("status"),
        "link_count": nav_status.get("link_count"),
        "links": nav_status.get("links"),
        "readiness_score": nav_status.get("readiness_score"),
        "failed_checks": nav_status.get("failed_checks"),
    })

    nav_hrefs = {link.get("href") for link in nav_status.get("links", [])}
    assert nav_status.get("ok") is True
    assert nav_status.get("status") == "passed"
    assert "/tower/security-command-unified" in nav_hrefs
    assert "/tower/security-command" in nav_hrefs
    assert nav_status.get("link_count", 0) >= 5
    assert nav_status.get("readiness_score") == 100

    unified = build_unified_owner_security_command_status(write_html=True)
    show("PACK 117 UNIFIED HEALTH", {
        "ok": unified.get("ok"),
        "status": unified.get("status"),
        "readiness_score": unified.get("readiness_score"),
        "failed_checks": unified.get("failed_checks"),
    })
    assert unified.get("ok") is True
    assert unified.get("status") == "passed"
    assert unified.get("readiness_score") == 100

    section = render_security_command_preferred_destination_section(status)
    show("PACK 117 HTML SECTION CHECK", {
        "html_length": len(section),
        "has_marker": "PACK117_SECURITY_COMMAND_PREFERRED_DESTINATION_SECTION" in section,
        "has_unified_link": "/tower/security-command-unified" in section,
        "has_legacy_link": "/tower/security-command" in section,
        "has_title": "Preferred Security Command Destination" in section,
    })

    assert "PACK117_SECURITY_COMMAND_PREFERRED_DESTINATION_SECTION" in section
    assert "/tower/security-command-unified" in section
    assert "/tower/security-command" in section
    assert "Preferred Security Command Destination" in section
    assert "SHOULD_NOT_SURVIVE" not in section
    assert "tower_keycard=" not in section

    panel = write_security_command_preferred_destination_panel(status)
    show("PACK 117 PANEL WRITE", panel)
    assert panel.get("ok") is True
    assert PREFERRED_PANEL_PATH.exists()

    panel_html = PREFERRED_PANEL_PATH.read_text(encoding="utf-8")
    assert "PACK117_SECURITY_COMMAND_PREFERRED_DESTINATION_SECTION" in panel_html
    assert "/tower/security-command-unified" in panel_html
    assert "SHOULD_NOT_SURVIVE" not in panel_html
    assert "tower_keycard=" not in panel_html

    card = security_command_preferred_destination_status_card()
    show("PACK 117 STATUS CARD", card)
    assert card.get("ok") is True
    assert card.get("pack") == "117"
    assert card.get("preferred_route") == "/tower/security-command-unified"
    assert card.get("readiness_score") == 100
    no_secret(card)

    loaded = load_security_command_preferred_destination_status()
    show("PACK 117 LOADED STATUS", {
        "ok": loaded.get("ok"),
        "status": loaded.get("status"),
        "preferred_route": loaded.get("preferred_route"),
        "readiness_score": loaded.get("readiness_score"),
        "status_path": loaded.get("status_path"),
        "panel_path": loaded.get("panel_path"),
    })
    assert loaded.get("ok") is True
    assert loaded.get("status") == "passed"
    assert loaded.get("preferred_route") == "/tower/security-command-unified"
    assert loaded.get("readiness_score") == 100
    no_secret(loaded)

    # Bridge checks.
    from tower.tower_status import pack117_security_command_preferred_destination_status_bridge
    from tower.security_command_page import pack117_security_command_preferred_destination_html_section

    bridge_card = pack117_security_command_preferred_destination_status_bridge()
    bridge_html = pack117_security_command_preferred_destination_html_section()

    show("PACK 117 TOWER STATUS BRIDGE", {
        "ok": bridge_card.get("ok"),
        "pack": bridge_card.get("pack"),
        "preferred_route": bridge_card.get("preferred_route"),
        "readiness_score": bridge_card.get("readiness_score"),
    })
    show("PACK 117 SECURITY COMMAND HTML BRIDGE", {
        "html_length": len(bridge_html),
        "has_marker": "PACK117_SECURITY_COMMAND_PREFERRED_DESTINATION_SECTION" in bridge_html,
        "has_unified_link": "/tower/security-command-unified" in bridge_html,
    })

    assert bridge_card.get("ok") is True
    assert bridge_card.get("pack") == "117"
    assert bridge_card.get("preferred_route") == "/tower/security-command-unified"
    assert bridge_card.get("readiness_score") == 100
    assert "PACK117_SECURITY_COMMAND_PREFERRED_DESTINATION_SECTION" in bridge_html
    assert "/tower/security-command-unified" in bridge_html
    assert "SHOULD_NOT_SURVIVE" not in bridge_html
    assert "tower_keycard=" not in bridge_html

    # Final route and object health.
    route_report = build_ob_route_coverage_report(write_panel=True)
    checkpoint = build_object_permission_integration_checkpoint(write_panel=True)

    show("PACK 117 FINAL HEALTH", {
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
        "pack117_route_marker": "PACK117_SECURITY_COMMAND_PREFERRED_DESTINATION_ROUTE" in app_text,
        "pack117_route_path": "/tower/security-command-preferred.json" in app_text,
        "pack117_route_guard": "pack117_preferred_security_command_destination_route" in app_text,
    }
    show("PACK 117 WEB APP ROUTE CHECKS", app_checks)
    assert all(app_checks.values())

    for path in [
        PROJECT_ROOT / "tower" / "security_command_preferred_destination.py",
        PROJECT_ROOT / "tower" / "test_tower_pack_117.py",
        PROJECT_ROOT / "tower" / "security_command_unified_owner_page.py",
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
        "pack": "117",
        "status": "passed",
        "preferred_route": status.get("preferred_route"),
        "legacy_route": status.get("legacy_route"),
        "link_count": status.get("link_count"),
        "readiness_score": status.get("readiness_score"),
        "route_coverage_pct": route_report.get("coverage_pct"),
        "human_reason": "Unified Security Command is now the preferred Security Command destination while legacy routes remain available.",
    }
    show("PACK 117 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
