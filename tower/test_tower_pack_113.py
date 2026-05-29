
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
    from tower.ob_object_permission_visibility import build_object_permission_visibility_status
    from tower.security_command_object_visibility_integration import (
        OBJECT_SECURITY_COMMAND_FRAGMENT_PATH,
        OBJECT_SECURITY_COMMAND_STATUS_PATH,
        build_security_command_object_visibility_status,
        load_security_command_object_visibility_status,
        render_security_command_object_visibility_section,
        reset_security_command_object_visibility_for_test,
        write_security_command_object_visibility_fragment,
    )
    from tower.ob_object_permission_integration_checkpoint import build_object_permission_integration_checkpoint
    from tower.ob_route_coverage_report import build_ob_route_coverage_report

    reset_security = reset_security_command_object_visibility_for_test()
    reset_objects = reset_ob_object_permissions_for_test()

    show("RESET PACK 113 SECURITY OBJECT VISIBILITY", reset_security)
    show("RESET OBJECT PERMISSIONS", reset_objects)

    assert reset_security.get("ok") is True
    assert reset_objects.get("ok") is True

    seed = {
        "symbol": check_symbol_permission(user_id="public_user", role="public", symbol="AMD").get("decision"),
        "position_deny": check_position_permission(
            user_id="beta_113",
            role="beta",
            position_id="pos_other_113",
            object_payload={"owner_user_id": "other_user"},
        ).get("decision"),
        "position_step": check_position_permission(
            user_id="beta_113",
            role="beta",
            position_id="pos_mine_113",
            action="close",
            object_payload={"owner_user_id": "beta_113"},
        ).get("decision"),
        "trade_deny": check_trade_permission(
            user_id="beta_113",
            role="beta",
            trade_id="trade_other_113",
            object_payload={"owner_user_id": "other_user"},
        ).get("decision"),
        "export_step": check_export_permission(
            user_id="owner_solice",
            role="owner",
            export_id="export_113",
        ).get("decision"),
        "analysis_summary": evaluate_ob_object_permission(
            user_id="beta_113",
            role="beta",
            object_type="analysis",
            object_id="analysis_113",
            action="view",
        ).get("decision"),
        "admin_step": evaluate_ob_object_permission(
            user_id="owner_solice",
            role="owner",
            object_type="admin_panel",
            object_id="tower_admin_panel_113",
            action="view",
        ).get("decision"),
    }
    show("PACK 113 SEEDED OBJECT DECISIONS", seed)

    assert seed["symbol"] == "allow"
    assert seed["position_deny"] == "deny"
    assert seed["position_step"] == "step_up_required"
    assert seed["trade_deny"] == "deny"
    assert seed["export_step"] == "step_up_required"
    assert seed["analysis_summary"] == "summary_only"
    assert seed["admin_step"] == "step_up_required"

    visibility = build_object_permission_visibility_status(limit=120, write_panel=True)
    show("PACK 113 BASE OBJECT VISIBILITY", {
        "event_count": visibility.get("event_count"),
        "deny_count": visibility.get("deny_count"),
        "step_up_required_count": visibility.get("step_up_required_count"),
        "export_event_count": visibility.get("export_event_count"),
        "summary_only_count": visibility.get("summary_only_count"),
        "readiness_score": visibility.get("readiness_score"),
        "no_secret_leakage": visibility.get("no_secret_leakage"),
    })

    assert visibility.get("event_count", 0) >= 7
    assert visibility.get("deny_count", 0) >= 2
    assert visibility.get("step_up_required_count", 0) >= 3
    assert visibility.get("summary_only_count", 0) >= 1
    assert visibility.get("export_event_count", 0) >= 1
    assert visibility.get("readiness_score") == 100
    assert visibility.get("no_secret_leakage") is True
    no_secret(visibility)

    status = build_security_command_object_visibility_status(write_fragment=True)
    show("PACK 113 SECURITY COMMAND OBJECT STATUS", {
        "ok": status.get("ok"),
        "event_count": status.get("event_count"),
        "important_event_count": status.get("important_event_count"),
        "deny_count": status.get("deny_count"),
        "step_up_required_count": status.get("step_up_required_count"),
        "export_event_count": status.get("export_event_count"),
        "summary_only_count": status.get("summary_only_count"),
        "readiness_score": status.get("readiness_score"),
        "no_secret_leakage": status.get("no_secret_leakage"),
    })

    assert status.get("ok") is True
    assert status.get("event_count", 0) >= 7
    assert status.get("deny_count", 0) >= 2
    assert status.get("step_up_required_count", 0) >= 3
    assert status.get("export_event_count", 0) >= 1
    assert status.get("summary_only_count", 0) >= 1
    assert status.get("readiness_score") == 100
    assert status.get("no_secret_leakage") is True
    assert OBJECT_SECURITY_COMMAND_STATUS_PATH.exists()
    assert OBJECT_SECURITY_COMMAND_FRAGMENT_PATH.exists()
    no_secret(status)

    html = render_security_command_object_visibility_section(status)
    show("PACK 113 HTML SECTION CHECK", {
        "html_length": len(html),
        "has_section_marker": "PACK113_SECURITY_COMMAND_OBJECT_VISIBILITY_SECTION" in html,
        "has_title": "Object Permission Visibility" in html,
        "has_denied": "Denied" in html,
        "has_step_up": "Step-up" in html,
        "has_exports": "Exports" in html,
    })

    assert "PACK113_SECURITY_COMMAND_OBJECT_VISIBILITY_SECTION" in html
    assert "Object Permission Visibility" in html
    assert "Denied" in html
    assert "Step-up" in html
    assert "Exports" in html
    assert "SHOULD_NOT_SURVIVE" not in html
    assert "tower_keycard=" not in html

    fragment = write_security_command_object_visibility_fragment(status)
    show("PACK 113 FRAGMENT WRITE", fragment)
    assert fragment.get("ok") is True
    assert OBJECT_SECURITY_COMMAND_FRAGMENT_PATH.exists()

    fragment_html = OBJECT_SECURITY_COMMAND_FRAGMENT_PATH.read_text(encoding="utf-8")
    assert "PACK113_SECURITY_COMMAND_OBJECT_VISIBILITY_SECTION" in fragment_html
    assert "Object Permission Visibility" in fragment_html
    assert "SHOULD_NOT_SURVIVE" not in fragment_html
    assert "tower_keycard=" not in fragment_html

    loaded = load_security_command_object_visibility_status()
    show("PACK 113 LOADED STATUS", {
        "ok": loaded.get("ok"),
        "event_count": loaded.get("event_count"),
        "readiness_score": loaded.get("readiness_score"),
        "status_path": loaded.get("security_command_status_path"),
        "fragment_path": loaded.get("security_command_fragment_path"),
    })
    assert loaded.get("ok") is True
    assert loaded.get("readiness_score") == 100
    no_secret(loaded)

    try:
        from tower.security_command_page import pack113_security_command_object_visibility_html_section
        bridge_html = pack113_security_command_object_visibility_html_section()
        show("PACK 113 SECURITY COMMAND HTML BRIDGE", {
            "html_length": len(bridge_html),
            "has_section_marker": "PACK113_SECURITY_COMMAND_OBJECT_VISIBILITY_SECTION" in bridge_html,
            "has_title": "Object Permission Visibility" in bridge_html,
        })
        assert "PACK113_SECURITY_COMMAND_OBJECT_VISIBILITY_SECTION" in bridge_html
        assert "Object Permission Visibility" in bridge_html
        assert "SHOULD_NOT_SURVIVE" not in bridge_html
        assert "tower_keycard=" not in bridge_html
    except Exception as exc:
        show("PACK 113 SECURITY COMMAND HTML BRIDGE FAILED", {"error_type": type(exc).__name__})
        raise

    route_report = build_ob_route_coverage_report(write_panel=True)
    checkpoint = build_object_permission_integration_checkpoint(write_panel=True)

    show("PACK 113 ROUTE + CHECKPOINT HEALTH", {
        "route_coverage_pct": route_report.get("coverage_pct"),
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

    for path in [
        PROJECT_ROOT / "tower" / "security_command_object_visibility_integration.py",
        PROJECT_ROOT / "tower" / "test_tower_pack_113.py",
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
        "pack": "113",
        "status": "passed",
        "event_count": status.get("event_count"),
        "deny_count": status.get("deny_count"),
        "step_up_required_count": status.get("step_up_required_count"),
        "export_event_count": status.get("export_event_count"),
        "summary_only_count": status.get("summary_only_count"),
        "readiness_score": status.get("readiness_score"),
        "human_reason": "Object permission visibility is renderable inside the main Tower Security Command HTML layer.",
    }
    show("PACK 113 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
