
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
    from tower.security_command_navigation_links import (
        NAV_PANEL_PATH,
        NAV_STATUS_PATH,
        build_security_command_navigation_links_status,
        load_security_command_navigation_links_status,
        render_security_command_navigation_links_section,
        reset_security_command_navigation_links_for_test,
        security_command_navigation_links_status_card,
        write_security_command_navigation_links_panel,
    )
    from tower.security_command_composition_smoke import build_security_command_composition_status
    from tower.ob_route_coverage_report import build_ob_route_coverage_report
    from tower.ob_object_permission_integration_checkpoint import build_object_permission_integration_checkpoint

    reset_links = reset_security_command_navigation_links_for_test()
    reset_objects = reset_ob_object_permissions_for_test()

    show("RESET PACK 115 LINKS", reset_links)
    show("RESET OBJECT PERMISSIONS", reset_objects)

    assert reset_links.get("ok") is True
    assert reset_objects.get("ok") is True

    # Seed object events so composition/visibility has data.
    seed = {
        "symbol": check_symbol_permission(user_id="public_user", role="public", symbol="SPY").get("decision"),
        "position_deny": check_position_permission(
            user_id="beta_115",
            role="beta",
            position_id="pos_other_115",
            object_payload={"owner_user_id": "other_user"},
        ).get("decision"),
        "position_step": check_position_permission(
            user_id="beta_115",
            role="beta",
            position_id="pos_mine_115",
            action="close",
            object_payload={"owner_user_id": "beta_115"},
        ).get("decision"),
        "trade_deny": check_trade_permission(
            user_id="beta_115",
            role="beta",
            trade_id="trade_other_115",
            object_payload={"owner_user_id": "other_user"},
        ).get("decision"),
        "export_step": check_export_permission(
            user_id="owner_solice",
            role="owner",
            export_id="export_115",
        ).get("decision"),
        "analysis_summary": evaluate_ob_object_permission(
            user_id="beta_115",
            role="beta",
            object_type="analysis",
            object_id="analysis_115",
            action="view",
        ).get("decision"),
        "admin_step": evaluate_ob_object_permission(
            user_id="owner_solice",
            role="owner",
            object_type="admin_panel",
            object_id="tower_admin_panel_115",
            action="view",
        ).get("decision"),
    }
    show("PACK 115 SEEDED OBJECT DECISIONS", seed)

    assert seed["symbol"] == "allow"
    assert seed["position_deny"] == "deny"
    assert seed["position_step"] == "step_up_required"
    assert seed["trade_deny"] == "deny"
    assert seed["export_step"] == "step_up_required"
    assert seed["analysis_summary"] == "summary_only"
    assert seed["admin_step"] == "step_up_required"

    status = build_security_command_navigation_links_status(write_panel=True)
    show("PACK 115 NAV STATUS", {
        "ok": status.get("ok"),
        "status": status.get("status"),
        "readiness_score": status.get("readiness_score"),
        "link_count": status.get("link_count"),
        "failed_checks": status.get("failed_checks"),
        "links": status.get("links"),
        "route_health": status.get("route_health"),
        "composition_health": status.get("composition_health"),
        "object_checkpoint_health": status.get("object_checkpoint_health"),
        "no_secret_leakage": status.get("no_secret_leakage"),
    })

    assert status.get("ok") is True
    assert status.get("status") == "passed"
    assert status.get("readiness_score") == 100
    assert status.get("failed_checks") == []
    assert status.get("link_count") >= 3
    assert status.get("route_health", {}).get("coverage_pct") == 100
    assert status.get("route_health", {}).get("unguarded_needed_count") == 0
    assert status.get("route_health", {}).get("unguarded_high_risk_count") == 0
    assert status.get("composition_health", {}).get("status") == "passed"
    assert status.get("object_checkpoint_health", {}).get("status") == "passed"
    assert status.get("object_checkpoint_health", {}).get("helper_wrapped_count") == 0
    assert status.get("no_secret_leakage") is True
    assert NAV_STATUS_PATH.exists()
    assert NAV_PANEL_PATH.exists()
    no_secret(status)

    hrefs = {link.get("href") for link in status.get("links", [])}
    assert "/tower/security-command" in hrefs
    assert "/tower/security-command-smoke" in hrefs
    assert "/tower/ob-guard-status.json" in hrefs

    section = render_security_command_navigation_links_section(status)
    show("PACK 115 HTML SECTION CHECK", {
        "html_length": len(section),
        "has_marker": "PACK115_SECURITY_COMMAND_NAVIGATION_LINKS_SECTION" in section,
        "has_smoke_link": "/tower/security-command-smoke" in section,
        "has_status_json_link": "/tower/ob-guard-status.json" in section,
        "has_title": "Security Command Links" in section,
    })

    assert "PACK115_SECURITY_COMMAND_NAVIGATION_LINKS_SECTION" in section
    assert "/tower/security-command-smoke" in section
    assert "/tower/ob-guard-status.json" in section
    assert "Security Command Links" in section
    assert "SHOULD_NOT_SURVIVE" not in section
    assert "tower_keycard=" not in section

    panel = write_security_command_navigation_links_panel(status)
    show("PACK 115 PANEL WRITE", panel)
    assert panel.get("ok") is True
    assert NAV_PANEL_PATH.exists()

    panel_html = NAV_PANEL_PATH.read_text(encoding="utf-8")
    assert "PACK115_SECURITY_COMMAND_NAVIGATION_LINKS_SECTION" in panel_html
    assert "/tower/security-command-smoke" in panel_html
    assert "SHOULD_NOT_SURVIVE" not in panel_html
    assert "tower_keycard=" not in panel_html

    card = security_command_navigation_links_status_card()
    show("PACK 115 STATUS CARD", {
        "ok": card.get("ok"),
        "pack": card.get("pack"),
        "link_count": card.get("link_count"),
        "route_coverage_pct": card.get("route_coverage_pct"),
        "readiness_score": card.get("readiness_score"),
    })
    assert card.get("ok") is True
    assert card.get("pack") == "115"
    assert card.get("link_count") >= 3
    assert card.get("route_coverage_pct") == 100
    assert card.get("readiness_score") == 100
    no_secret(card)

    loaded = load_security_command_navigation_links_status()
    show("PACK 115 LOADED STATUS", {
        "ok": loaded.get("ok"),
        "status": loaded.get("status"),
        "readiness_score": loaded.get("readiness_score"),
        "status_path": loaded.get("status_path"),
        "panel_path": loaded.get("panel_path"),
    })
    assert loaded.get("ok") is True
    assert loaded.get("status") == "passed"
    assert loaded.get("readiness_score") == 100
    no_secret(loaded)

    # Bridge checks.
    from tower.tower_status import pack115_security_command_navigation_links_status_bridge
    from tower.security_command_page import pack115_security_command_navigation_links_html_section

    bridge_card = pack115_security_command_navigation_links_status_bridge()
    bridge_html = pack115_security_command_navigation_links_html_section()

    show("PACK 115 TOWER STATUS BRIDGE", {
        "ok": bridge_card.get("ok"),
        "pack": bridge_card.get("pack"),
        "link_count": bridge_card.get("link_count"),
        "route_coverage_pct": bridge_card.get("route_coverage_pct"),
    })
    show("PACK 115 SECURITY COMMAND HTML BRIDGE", {
        "html_length": len(bridge_html),
        "has_marker": "PACK115_SECURITY_COMMAND_NAVIGATION_LINKS_SECTION" in bridge_html,
        "has_smoke_link": "/tower/security-command-smoke" in bridge_html,
    })

    assert bridge_card.get("ok") is True
    assert bridge_card.get("pack") == "115"
    assert bridge_card.get("route_coverage_pct") == 100
    assert "PACK115_SECURITY_COMMAND_NAVIGATION_LINKS_SECTION" in bridge_html
    assert "/tower/security-command-smoke" in bridge_html
    assert "SHOULD_NOT_SURVIVE" not in bridge_html
    assert "tower_keycard=" not in bridge_html

    # Final health checks.
    route_report = build_ob_route_coverage_report(write_panel=True)
    checkpoint = build_object_permission_integration_checkpoint(write_panel=True)
    composition = build_security_command_composition_status(write_html=True)

    show("PACK 115 FINAL HEALTH", {
        "route_coverage_pct": route_report.get("coverage_pct"),
        "unguarded_needed_count": route_report.get("unguarded_needed_count"),
        "unguarded_high_risk_count": route_report.get("unguarded_high_risk_count"),
        "checkpoint_status": checkpoint.get("status"),
        "checkpoint_readiness": checkpoint.get("readiness_score"),
        "helper_wrapped_count": checkpoint.get("helper_wrapped_count"),
        "composition_status": composition.get("status"),
        "composition_readiness": composition.get("readiness_score"),
    })

    assert route_report.get("coverage_pct") == 100
    assert route_report.get("unguarded_needed_count") == 0
    assert route_report.get("unguarded_high_risk_count") == 0
    assert checkpoint.get("status") == "passed"
    assert checkpoint.get("readiness_score") == 100
    assert checkpoint.get("helper_wrapped_count") == 0
    assert composition.get("status") == "passed"
    assert composition.get("readiness_score") == 100

    app_text = WEB_APP.read_text(encoding="utf-8", errors="replace")
    app_checks = {
        "pack115_route_marker": "PACK115_SECURITY_COMMAND_NAVIGATION_LINKS_ROUTE" in app_text,
        "pack115_route_path": "/tower/security-command-links.json" in app_text,
        "pack115_route_guard": "pack115_security_command_links_route" in app_text,
    }
    show("PACK 115 WEB APP ROUTE CHECKS", app_checks)
    assert all(app_checks.values())

    for path in [
        PROJECT_ROOT / "tower" / "security_command_navigation_links.py",
        PROJECT_ROOT / "tower" / "test_tower_pack_115.py",
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
        "pack": "115",
        "status": "passed",
        "link_count": status.get("link_count"),
        "readiness_score": status.get("readiness_score"),
        "route_coverage_pct": route_report.get("coverage_pct"),
        "human_reason": "Security Command smoke/status links are discoverable from Tower navigation/status surfaces.",
    }
    show("PACK 115 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
