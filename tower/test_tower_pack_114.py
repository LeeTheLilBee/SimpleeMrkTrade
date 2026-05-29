
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
    from tower.security_command_composition_smoke import (
        COMPOSITION_HTML_PATH,
        COMPOSITION_STATUS_PATH,
        build_security_command_composition_status,
        load_security_command_composition_status,
        render_security_command_composition_html,
        reset_security_command_composition_smoke_for_test,
        write_security_command_composition_html,
    )

    reset_comp = reset_security_command_composition_smoke_for_test()
    reset_obj = reset_ob_object_permissions_for_test()
    show("RESET PACK 114 COMPOSITION", reset_comp)
    show("RESET OBJECT PERMISSIONS", reset_obj)
    assert reset_comp.get("ok") is True
    assert reset_obj.get("ok") is True

    # Seed object permission activity so the Security Command composition has real cards.
    seed = {
        "symbol": check_symbol_permission(user_id="public_user", role="public", symbol="QQQ").get("decision"),
        "position_deny": check_position_permission(
            user_id="beta_114",
            role="beta",
            position_id="pos_other_114",
            object_payload={"owner_user_id": "other_user"},
        ).get("decision"),
        "position_step": check_position_permission(
            user_id="beta_114",
            role="beta",
            position_id="pos_mine_114",
            action="close",
            object_payload={"owner_user_id": "beta_114"},
        ).get("decision"),
        "trade_deny": check_trade_permission(
            user_id="beta_114",
            role="beta",
            trade_id="trade_other_114",
            object_payload={"owner_user_id": "other_user"},
        ).get("decision"),
        "export_step": check_export_permission(
            user_id="owner_solice",
            role="owner",
            export_id="export_114",
        ).get("decision"),
        "analysis_summary": evaluate_ob_object_permission(
            user_id="beta_114",
            role="beta",
            object_type="analysis",
            object_id="analysis_114",
            action="view",
        ).get("decision"),
        "admin_step": evaluate_ob_object_permission(
            user_id="owner_solice",
            role="owner",
            object_type="admin_panel",
            object_id="tower_admin_panel_114",
            action="view",
        ).get("decision"),
    }
    show("PACK 114 SEEDED OBJECT DECISIONS", seed)

    assert seed["symbol"] == "allow"
    assert seed["position_deny"] == "deny"
    assert seed["position_step"] == "step_up_required"
    assert seed["trade_deny"] == "deny"
    assert seed["export_step"] == "step_up_required"
    assert seed["analysis_summary"] == "summary_only"
    assert seed["admin_step"] == "step_up_required"

    status = build_security_command_composition_status(write_html=True)
    show("PACK 114 COMPOSITION STATUS", {
        "ok": status.get("ok"),
        "status": status.get("status"),
        "readiness_score": status.get("readiness_score"),
        "failed_checks": status.get("failed_checks"),
        "route_coverage_summary": status.get("route_coverage_summary"),
        "object_checkpoint_summary": status.get("object_checkpoint_summary"),
        "object_visibility_summary": status.get("object_visibility_summary"),
        "security_object_summary": status.get("security_object_summary"),
        "bridge_status": status.get("bridge_status"),
        "no_secret_leakage": status.get("no_secret_leakage"),
    })

    assert status.get("ok") is True
    assert status.get("status") == "passed"
    assert status.get("readiness_score") == 100
    assert status.get("failed_checks") == []
    assert status.get("route_coverage_summary", {}).get("coverage_pct") == 100
    assert status.get("route_coverage_summary", {}).get("unguarded_needed_count") == 0
    assert status.get("route_coverage_summary", {}).get("unguarded_high_risk_count") == 0
    assert status.get("object_checkpoint_summary", {}).get("status") == "passed"
    assert status.get("object_checkpoint_summary", {}).get("helper_wrapped_count") == 0
    assert status.get("object_visibility_summary", {}).get("readiness_score") == 100
    assert status.get("security_object_summary", {}).get("readiness_score") == 100
    assert status.get("bridge_status", {}).get("object_visibility_html_ok") is True
    assert status.get("bridge_status", {}).get("tower_status_bridge_ok") is True
    assert status.get("bridge_status", {}).get("security_command_bridge_ok") is True
    assert status.get("no_secret_leakage") is True
    assert COMPOSITION_STATUS_PATH.exists()
    assert COMPOSITION_HTML_PATH.exists()
    no_secret(status)

    html = render_security_command_composition_html(status)
    show("PACK 114 HTML CHECK", {
        "html_length": len(html),
        "has_page_marker": "PACK114_SECURITY_COMMAND_COMPOSITION_SMOKE_PAGE" in html,
        "has_pack113_section": "PACK113_SECURITY_COMMAND_OBJECT_VISIBILITY_SECTION" in html,
        "has_object_title": "Object Permission Visibility" in html,
        "has_security_command_title": "The Tower Security Command" in html,
    })

    assert "PACK114_SECURITY_COMMAND_COMPOSITION_SMOKE_PAGE" in html
    assert "PACK113_SECURITY_COMMAND_OBJECT_VISIBILITY_SECTION" in html
    assert "Object Permission Visibility" in html
    assert "The Tower Security Command" in html
    assert "SHOULD_NOT_SURVIVE" not in html
    assert "tower_keycard=" not in html

    write_result = write_security_command_composition_html(status)
    show("PACK 114 WRITE HTML", write_result)
    assert write_result.get("ok") is True
    assert COMPOSITION_HTML_PATH.exists()

    html_file = COMPOSITION_HTML_PATH.read_text(encoding="utf-8")
    assert "PACK114_SECURITY_COMMAND_COMPOSITION_SMOKE_PAGE" in html_file
    assert "PACK113_SECURITY_COMMAND_OBJECT_VISIBILITY_SECTION" in html_file
    assert "SHOULD_NOT_SURVIVE" not in html_file
    assert "tower_keycard=" not in html_file

    loaded = load_security_command_composition_status()
    show("PACK 114 LOADED STATUS", {
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

    app_text = WEB_APP.read_text(encoding="utf-8", errors="replace")
    app_checks = {
        "pack114_route_marker": "PACK114_SECURITY_COMMAND_COMPOSITION_SMOKE_ROUTE" in app_text,
        "pack114_route_path": "/tower/security-command-smoke" in app_text,
    }
    show("PACK 114 WEB APP ROUTE CHECKS", app_checks)
    assert all(app_checks.values())

    for path in [
        PROJECT_ROOT / "tower" / "security_command_composition_smoke.py",
        PROJECT_ROOT / "tower" / "test_tower_pack_114.py",
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
        "pack": "114",
        "status": "passed",
        "readiness_score": status.get("readiness_score"),
        "route_coverage_pct": status.get("route_coverage_summary", {}).get("coverage_pct"),
        "helper_wrapped_count": status.get("object_checkpoint_summary", {}).get("helper_wrapped_count"),
        "object_visibility_events": status.get("object_visibility_summary", {}).get("event_count"),
        "human_reason": "Security Command page composition smoke can render with object visibility attached.",
    }
    show("PACK 114 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
