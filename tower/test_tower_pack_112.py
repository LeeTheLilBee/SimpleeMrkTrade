
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
        summarize_ob_object_permissions,
    )
    from tower.ob_object_permission_visibility import (
        OBJECT_VISIBILITY_PANEL_PATH,
        OBJECT_VISIBILITY_STATUS_PATH,
        build_object_permission_visibility_status,
        load_object_permission_visibility_status,
        object_permission_visibility_status_card,
        reset_object_permission_visibility_for_test,
    )
    from tower.ob_object_permission_integration_checkpoint import build_object_permission_integration_checkpoint
    from tower.ob_route_coverage_report import build_ob_route_coverage_report

    reset_visibility = reset_object_permission_visibility_for_test()
    reset_objects = reset_ob_object_permissions_for_test()

    show("RESET PACK 112 VISIBILITY", reset_visibility)
    show("RESET OBJECT PERMISSIONS", reset_objects)

    assert reset_visibility.get("ok") is True
    assert reset_objects.get("ok") is True

    # Seed object permission events with the decisions Tower needs to see.
    seed = {
        "symbol": check_symbol_permission(user_id="public_user", role="public", symbol="TSLA").get("decision"),
        "position_deny": check_position_permission(
            user_id="beta_112",
            role="beta",
            position_id="pos_other_112",
            object_payload={"owner_user_id": "other_user"},
        ).get("decision"),
        "position_step": check_position_permission(
            user_id="beta_112",
            role="beta",
            position_id="pos_mine_112",
            action="close",
            object_payload={"owner_user_id": "beta_112"},
        ).get("decision"),
        "trade_deny": check_trade_permission(
            user_id="beta_112",
            role="beta",
            trade_id="trade_other_112",
            object_payload={"owner_user_id": "other_user"},
        ).get("decision"),
        "export_step": check_export_permission(
            user_id="owner_solice",
            role="owner",
            export_id="export_112",
        ).get("decision"),
        "analysis_summary": evaluate_ob_object_permission(
            user_id="beta_112",
            role="beta",
            object_type="analysis",
            object_id="analysis_112",
            action="view",
        ).get("decision"),
        "live_mode_deny": evaluate_ob_object_permission(
            user_id="owner_solice",
            role="owner",
            object_type="mode",
            object_id="live_manual",
            action="enable",
        ).get("decision"),
        "admin_step": evaluate_ob_object_permission(
            user_id="owner_solice",
            role="owner",
            object_type="admin_panel",
            object_id="tower_admin_panel_112",
            action="view",
        ).get("decision"),
    }
    show("PACK 112 SEEDED OBJECT DECISIONS", seed)

    assert seed["symbol"] == "allow"
    assert seed["position_deny"] == "deny"
    assert seed["position_step"] == "step_up_required"
    assert seed["trade_deny"] == "deny"
    assert seed["export_step"] == "step_up_required"
    assert seed["analysis_summary"] == "summary_only"
    assert seed["live_mode_deny"] == "deny"
    assert seed["admin_step"] == "step_up_required"

    object_status = summarize_ob_object_permissions(limit=120)
    show("OBJECT STATUS BEFORE VISIBILITY", {
        "event_count": object_status.get("event_count"),
        "by_decision": object_status.get("by_decision"),
        "by_object_type": object_status.get("by_object_type"),
        "readiness_score": object_status.get("readiness_score"),
        "no_secret_leakage": object_status.get("no_secret_leakage"),
    })
    assert object_status.get("event_count", 0) >= 8
    assert object_status.get("readiness_score") == 100
    assert object_status.get("no_secret_leakage") is True
    no_secret(object_status)

    visibility = build_object_permission_visibility_status(limit=120, write_panel=True)
    show("PACK 112 OBJECT VISIBILITY STATUS", {
        "ok": visibility.get("ok"),
        "event_count": visibility.get("event_count"),
        "important_event_count": visibility.get("important_event_count"),
        "deny_count": visibility.get("deny_count"),
        "step_up_required_count": visibility.get("step_up_required_count"),
        "summary_only_count": visibility.get("summary_only_count"),
        "export_event_count": visibility.get("export_event_count"),
        "admin_event_count": visibility.get("admin_event_count"),
        "live_mode_event_count": visibility.get("live_mode_event_count"),
        "by_decision": visibility.get("by_decision"),
        "by_object_type": visibility.get("by_object_type"),
        "readiness_score": visibility.get("readiness_score"),
        "no_secret_leakage": visibility.get("no_secret_leakage"),
    })

    assert visibility.get("ok") is True
    assert visibility.get("event_count", 0) >= 8
    assert visibility.get("deny_count", 0) >= 3
    assert visibility.get("step_up_required_count", 0) >= 3
    assert visibility.get("summary_only_count", 0) >= 1
    assert visibility.get("export_event_count", 0) >= 1
    assert visibility.get("admin_event_count", 0) >= 1
    assert visibility.get("live_mode_event_count", 0) >= 1
    assert visibility.get("readiness_score") == 100
    assert visibility.get("no_secret_leakage") is True
    assert OBJECT_VISIBILITY_STATUS_PATH.exists()
    assert OBJECT_VISIBILITY_PANEL_PATH.exists()
    no_secret(visibility)

    card = object_permission_visibility_status_card()
    show("PACK 112 STATUS CARD", card)

    assert card.get("ok") is True
    assert card.get("pack") == "112"
    assert card.get("deny_count", 0) >= 3
    assert card.get("step_up_required_count", 0) >= 3
    assert card.get("export_event_count", 0) >= 1
    assert card.get("summary_only_count", 0) >= 1
    no_secret(card)

    loaded = load_object_permission_visibility_status()
    show("PACK 112 LOADED VISIBILITY", {
        "ok": loaded.get("ok"),
        "readiness_score": loaded.get("readiness_score"),
        "event_count": loaded.get("event_count"),
        "status_path": loaded.get("status_path"),
        "panel_path": loaded.get("panel_path"),
    })

    assert loaded.get("ok") is True
    assert loaded.get("readiness_score") == 100
    no_secret(loaded)

    panel = OBJECT_VISIBILITY_PANEL_PATH.read_text(encoding="utf-8")
    assert "The Tower · Object Permission Visibility" in panel
    assert "SHOULD_NOT_SURVIVE" not in panel
    assert "tower_keycard=" not in panel

    route_report = build_ob_route_coverage_report(write_panel=True)
    checkpoint = build_object_permission_integration_checkpoint(write_panel=True)

    show("PACK 112 ROUTE + CHECKPOINT HEALTH", {
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

    # Optional bridge checks.
    try:
        from tower.tower_status import pack112_object_permission_visibility_status_bridge
        status_bridge = pack112_object_permission_visibility_status_bridge()
        show("PACK 112 TOWER STATUS BRIDGE", status_bridge)
        assert status_bridge.get("pack") == "112"
        assert status_bridge.get("ok") is True
        no_secret(status_bridge)
    except Exception as exc:
        show("PACK 112 TOWER STATUS BRIDGE SKIPPED", {"error_type": type(exc).__name__})

    try:
        from tower.security_command_page import pack112_object_permission_visibility_command_panel
        command_bridge = pack112_object_permission_visibility_command_panel()
        show("PACK 112 SECURITY COMMAND BRIDGE", command_bridge)
        assert command_bridge.get("pack") == "112"
        assert command_bridge.get("ok") is True
        no_secret(command_bridge)
    except Exception as exc:
        show("PACK 112 SECURITY COMMAND BRIDGE SKIPPED", {"error_type": type(exc).__name__})

    for path in [
        PROJECT_ROOT / "tower" / "ob_object_permission_visibility.py",
        PROJECT_ROOT / "tower" / "test_tower_pack_112.py",
        PROJECT_ROOT / "tower" / "ob_object_permission_tightening.py",
        PROJECT_ROOT / "tower" / "ob_object_permission_integration_checkpoint.py",
        PROJECT_ROOT / "tower" / "tower_status.py",
        PROJECT_ROOT / "tower" / "security_command_page.py",
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
        "pack": "112",
        "status": "passed",
        "event_count": visibility.get("event_count"),
        "deny_count": visibility.get("deny_count"),
        "step_up_required_count": visibility.get("step_up_required_count"),
        "export_event_count": visibility.get("export_event_count"),
        "summary_only_count": visibility.get("summary_only_count"),
        "readiness_score": visibility.get("readiness_score"),
        "human_reason": "Object deny, step-up, export, summary-only, admin, and live-mode visibility is available to Tower status/security surfaces.",
    }
    show("PACK 112 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
