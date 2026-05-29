
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
    from tower.security_command_owner_ui_checkpoint import (
        OWNER_UI_CHECKPOINT_PANEL_PATH,
        OWNER_UI_CHECKPOINT_STATUS_PATH,
        build_security_command_owner_ui_checkpoint,
        load_security_command_owner_ui_checkpoint,
        owner_ui_checkpoint_status_card,
        render_security_command_owner_ui_checkpoint_section,
        reset_security_command_owner_ui_checkpoint_for_test,
        write_security_command_owner_ui_checkpoint_panel,
    )
    from tower.ob_route_coverage_report import build_ob_route_coverage_report
    from tower.ob_object_permission_integration_checkpoint import build_object_permission_integration_checkpoint

    reset = reset_security_command_owner_ui_checkpoint_for_test()
    show("RESET PACK 120 OWNER UI CHECKPOINT", reset)
    assert reset.get("ok") is True

    status = build_security_command_owner_ui_checkpoint(write_panel=True)
    show("PACK 120 OWNER UI CHECKPOINT STATUS", {
        "ok": status.get("ok"),
        "status": status.get("status"),
        "readiness_score": status.get("readiness_score"),
        "failed_checks": status.get("failed_checks"),
        "route_health": status.get("route_health"),
        "object_checkpoint": status.get("object_checkpoint"),
        "object_visibility": status.get("object_visibility"),
        "composition": status.get("composition"),
        "navigation": status.get("navigation"),
        "preferred": status.get("preferred"),
        "unified": status.get("unified"),
        "quick_actions": status.get("quick_actions"),
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
    assert status.get("preferred", {}).get("status") == "passed"
    assert status.get("preferred", {}).get("preferred_route") == "/tower/security-command-unified"
    assert status.get("unified", {}).get("status") == "passed"
    assert status.get("quick_actions", {}).get("status") == "passed"
    assert status.get("quick_actions", {}).get("action_count", 0) >= 6
    assert status.get("no_secret_leakage") is True
    assert OWNER_UI_CHECKPOINT_STATUS_PATH.exists()
    assert OWNER_UI_CHECKPOINT_PANEL_PATH.exists()
    no_secret(status)

    section = render_security_command_owner_ui_checkpoint_section(status)
    show("PACK 120 CHECKPOINT HTML SECTION", {
        "html_length": len(section),
        "has_marker": "PACK120_SECURITY_COMMAND_OWNER_UI_CHECKPOINT_SECTION" in section,
        "has_title": "Security Command UI Checkpoint" in section,
        "has_route_coverage": "Route Coverage" in section,
        "has_preferred_route": "/tower/security-command-unified" in section,
    })

    assert "PACK120_SECURITY_COMMAND_OWNER_UI_CHECKPOINT_SECTION" in section
    assert "Security Command UI Checkpoint" in section
    assert "Route Coverage" in section
    assert "/tower/security-command-unified" in section
    assert "SHOULD_NOT_SURVIVE" not in section
    assert "tower_keycard=" not in section

    panel = write_security_command_owner_ui_checkpoint_panel(status)
    show("PACK 120 CHECKPOINT PANEL WRITE", panel)
    assert panel.get("ok") is True
    assert OWNER_UI_CHECKPOINT_PANEL_PATH.exists()

    panel_html = OWNER_UI_CHECKPOINT_PANEL_PATH.read_text(encoding="utf-8")
    assert "PACK120_SECURITY_COMMAND_OWNER_UI_CHECKPOINT_SECTION" in panel_html
    assert "Security Command UI Checkpoint" in panel_html
    assert "SHOULD_NOT_SURVIVE" not in panel_html
    assert "tower_keycard=" not in panel_html

    card = owner_ui_checkpoint_status_card()
    loaded = load_security_command_owner_ui_checkpoint()

    show("PACK 120 STATUS CARD", card)
    show("PACK 120 LOADED STATUS", {
        "ok": loaded.get("ok"),
        "status": loaded.get("status"),
        "readiness_score": loaded.get("readiness_score"),
        "preferred_route": loaded.get("preferred", {}).get("preferred_route") if isinstance(loaded.get("preferred"), dict) else "",
    })

    assert card.get("ok") is True
    assert card.get("pack") == "120"
    assert card.get("readiness_score") == 100
    assert card.get("route_coverage_pct") == 100
    assert card.get("helper_wrapped_count") == 0
    assert card.get("preferred_route") == "/tower/security-command-unified"
    assert card.get("quick_action_count", 0) >= 6
    assert loaded.get("ok") is True
    assert loaded.get("status") == "passed"
    assert loaded.get("readiness_score") == 100
    no_secret(card)
    no_secret(loaded)

    route_report = build_ob_route_coverage_report(write_panel=True)
    checkpoint = build_object_permission_integration_checkpoint(write_panel=True)

    show("PACK 120 FINAL HEALTH", {
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
        "pack120_route_marker": "PACK120_SECURITY_COMMAND_OWNER_UI_CHECKPOINT_ROUTE" in app_text,
        "pack120_route_path": "/tower/security-command-ui-checkpoint.json" in app_text,
        "pack120_route_guard": "pack120_security_command_owner_ui_checkpoint_route" in app_text,
    }
    show("PACK 120 WEB APP ROUTE CHECKS", app_checks)
    assert all(app_checks.values())

    for path in [
        PROJECT_ROOT / "tower" / "security_command_owner_ui_checkpoint.py",
        PROJECT_ROOT / "tower" / "test_tower_pack_120.py",
        PROJECT_ROOT / "tower" / "security_command_owner_quick_actions.py",
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
        "pack": "120",
        "status": "passed",
        "readiness_score": status.get("readiness_score"),
        "route_coverage_pct": route_report.get("coverage_pct"),
        "guarded_needed_count": route_report.get("guarded_needed_count"),
        "needs_guard_count": route_report.get("needs_guard_count"),
        "helper_wrapped_count": checkpoint.get("helper_wrapped_count"),
        "preferred_route": status.get("preferred", {}).get("preferred_route"),
        "quick_action_count": status.get("quick_actions", {}).get("action_count"),
        "human_reason": "Security Command owner UI checkpoint board proves the full Packs 112-119 UI block is healthy.",
    }
    show("PACK 120 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
