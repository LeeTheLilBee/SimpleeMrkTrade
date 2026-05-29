
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
        "sk_live_should",
        "ghp_should",
    ]
    for item in bad:
        assert item not in s, item


def run_tests():
    from tower.ob_object_permission_tightening import (
        check_export_permission,
        check_position_permission,
        evaluate_ob_object_permission,
        reset_ob_object_permissions_for_test,
    )
    from tower.security_inbox_owner_queue import build_security_inbox_owner_queue
    from tower.security_inbox_review_actions import (
        apply_security_inbox_review_action,
        reset_security_inbox_review_actions_for_test,
    )
    from tower.security_inbox_filters_priorities import build_security_inbox_filters_priorities_status
    from tower.security_incident_desk import (
        apply_security_incident_action,
        build_security_incident_desk_status,
        reset_security_incident_desk_for_test,
    )
    from tower.security_incident_filters_escalation import build_security_incident_filters_escalation_status
    from tower.security_incident_checkpoint import build_security_incident_checkpoint
    from tower.security_watch_owner_posture import (
        build_security_watch_owner_posture,
        reset_security_watch_owner_posture_for_test,
    )
    from tower.security_command_owner_quick_actions import build_owner_quick_actions_status
    from tower.security_command_unified_owner_page import (
        build_unified_owner_security_command_status,
        render_unified_owner_security_command_html,
        write_unified_owner_security_command_html,
    )
    from tower.ob_route_coverage_report import build_ob_route_coverage_report
    from tower.ob_object_permission_integration_checkpoint import build_object_permission_integration_checkpoint

    reset_objects = reset_ob_object_permissions_for_test()
    reset_review = reset_security_inbox_review_actions_for_test()
    reset_incidents = reset_security_incident_desk_for_test()
    reset_watch = reset_security_watch_owner_posture_for_test()

    show("RESET OBJECT PERMISSIONS", reset_objects)
    show("RESET REVIEW ACTIONS", reset_review)
    show("RESET INCIDENT DESK", reset_incidents)
    show("RESET SECURITY WATCH", reset_watch)

    assert reset_objects.get("ok") is True
    assert reset_review.get("ok") is True
    assert reset_incidents.get("ok") is True
    assert reset_watch.get("ok") is True

    # Seed security activity.
    position_deny = check_position_permission(
        user_id="beta_132",
        role="beta",
        position_id="pos_other_132",
        object_payload={"owner_user_id": "other_user"},
    )
    position_step = check_position_permission(
        user_id="beta_132",
        role="beta",
        position_id="pos_mine_132",
        action="close",
        object_payload={"owner_user_id": "beta_132"},
    )
    export_step = check_export_permission(
        user_id="owner_solice",
        role="owner",
        export_id="export_132",
    )
    analysis_summary = evaluate_ob_object_permission(
        user_id="beta_132",
        role="beta",
        object_type="analysis",
        object_id="analysis_132",
        action="view",
    )

    show("PACK 132 SEEDED EVENTS", {
        "position_deny": position_deny.get("decision"),
        "position_step": position_step.get("decision"),
        "export_step": export_step.get("decision"),
        "analysis_summary": analysis_summary.get("decision"),
    })

    assert position_deny.get("decision") == "deny"
    assert position_step.get("decision") == "step_up_required"
    assert export_step.get("decision") == "step_up_required"
    assert analysis_summary.get("decision") == "summary_only"

    inbox = build_security_inbox_owner_queue(limit_per_source=80, write_panel=True)
    items = inbox.get("recent_items", []) if isinstance(inbox.get("recent_items"), list) else []
    review_candidates = [item for item in items if isinstance(item, dict) and item.get("needs_owner_review")]

    assert inbox.get("ok") is True
    assert len(review_candidates) >= 1

    target_ids = [item.get("inbox_item_id") for item in review_candidates[:3] if item.get("inbox_item_id")]
    assert target_ids

    ack = apply_security_inbox_review_action(
        inbox_item_id=target_ids[0],
        review_state="acknowledged",
        actor_user_id="owner_solice",
        note="Pack 132 Security Watch UI integration test.",
        reason="Pack 132 seed.",
        metadata={"pack": "132", "token": "SHOULD_NOT_SURVIVE_TOKEN"},
    )
    assert ack.get("ok") is True
    no_secret(ack)

    if len(target_ids) > 1:
        inv = apply_security_inbox_review_action(
            inbox_item_id=target_ids[1],
            review_state="investigating",
            actor_user_id="owner_solice",
            note="Pack 132 investigation seed.",
            reason="Pack 132 seed.",
            metadata={"pack": "132"},
        )
        assert inv.get("ok") is True

    inbox_filters = build_security_inbox_filters_priorities_status(write_panel=True)
    incident_desk = build_security_incident_desk_status(write_panel=True)

    assert inbox_filters.get("ok") is True
    assert incident_desk.get("ok") is True
    assert incident_desk.get("incident_count", 0) >= 1

    incidents = incident_desk.get("incident_candidates", [])
    assert isinstance(incidents, list)
    assert len(incidents) >= 1

    incident_id = incidents[0].get("incident_id")
    assert incident_id

    triaged = apply_security_incident_action(
        incident_id=incident_id,
        incident_status="triaged",
        severity="high",
        actor_user_id="owner_solice",
        assigned_to="owner_solice",
        note="Pack 132 triage seed. Secret should_not_survive.",
        reason="Pack 132 Security Watch UI seed.",
        metadata={"pack": "132", "token": "SHOULD_NOT_SURVIVE_TOKEN"},
    )
    assert triaged.get("ok") is True
    assert triaged.get("no_secret_leakage") is True
    no_secret(triaged)

    incident_filters = build_security_incident_filters_escalation_status(write_panel=True)
    incident_checkpoint = build_security_incident_checkpoint(write_panel=True)
    watch = build_security_watch_owner_posture(write_panel=True)
    quick_status = build_owner_quick_actions_status(write_panel=True)
    unified = build_unified_owner_security_command_status(write_html=True)

    show("PACK 132 WATCH STATUS", {
        "ok": watch.get("ok"),
        "status": watch.get("status"),
        "readiness_score": watch.get("readiness_score"),
        "posture": watch.get("posture"),
        "failed_checks": watch.get("failed_checks"),
    })

    show("PACK 132 QUICK ACTION STATUS", {
        "ok": quick_status.get("ok"),
        "status": quick_status.get("status"),
        "action_count": quick_status.get("action_count"),
        "readiness_score": quick_status.get("readiness_score"),
    })

    show("PACK 132 UNIFIED STATUS", {
        "ok": unified.get("ok"),
        "status": unified.get("status"),
        "readiness_score": unified.get("readiness_score"),
        "failed_checks": unified.get("failed_checks"),
    })

    assert incident_filters.get("ok") is True
    assert incident_filters.get("status") == "passed"
    assert incident_checkpoint.get("ok") is True
    assert incident_checkpoint.get("status") == "passed"

    assert watch.get("ok") is True
    assert watch.get("status") == "passed"
    assert watch.get("readiness_score") == 100
    assert watch.get("posture", {}).get("recommended_first_action") in {
        "review_incident_escalation",
        "review_high_priority_inbox",
        "review_route_health",
        "monitor",
    }

    assert quick_status.get("ok") is True
    assert quick_status.get("status") == "passed"
    assert quick_status.get("readiness_score") == 100
    assert quick_status.get("action_count", 0) >= 14

    hrefs = {action.get("href") for action in quick_status.get("actions", []) if isinstance(action, dict)}
    assert "/tower/security-watch.json" in hrefs
    assert "/tower/security-incident-checkpoint.json" in hrefs
    assert "/tower/security-incident-filters.json" in hrefs

    assert unified.get("ok") is True
    assert unified.get("status") == "passed"
    assert unified.get("readiness_score") == 100

    no_secret(watch)
    no_secret(quick_status)
    no_secret(unified)

    unified_html = render_unified_owner_security_command_html(unified)

    show("PACK 132 UNIFIED HTML CHECK", {
        "html_length": len(unified_html),
        "has_pack132": "PACK132_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_WATCH" in unified_html,
        "has_pack131": "PACK131_SECURITY_WATCH_OWNER_POSTURE_SECTION" in unified_html,
        "has_pack129": "PACK129_UNIFIED_OWNER_PAGE_INCLUDES_INCIDENT_FILTERS_ESCALATION" in unified_html,
        "has_pack128": "PACK128_SECURITY_INCIDENT_FILTERS_ESCALATION_SECTION" in unified_html,
        "has_pack127": "PACK127_UNIFIED_OWNER_PAGE_INCLUDES_INCIDENT_DESK" in unified_html,
        "has_pack126": "PACK126_SECURITY_INCIDENT_DESK_SECTION" in unified_html,
        "has_watch_link": "/tower/security-watch.json" in unified_html,
    })

    assert "PACK132_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_WATCH" in unified_html
    assert "PACK131_SECURITY_WATCH_OWNER_POSTURE_SECTION" in unified_html
    assert "PACK129_UNIFIED_OWNER_PAGE_INCLUDES_INCIDENT_FILTERS_ESCALATION" in unified_html
    assert "PACK128_SECURITY_INCIDENT_FILTERS_ESCALATION_SECTION" in unified_html
    assert "PACK127_UNIFIED_OWNER_PAGE_INCLUDES_INCIDENT_DESK" in unified_html
    assert "PACK126_SECURITY_INCIDENT_DESK_SECTION" in unified_html
    assert "/tower/security-watch.json" in unified_html
    assert "SHOULD_NOT_SURVIVE" not in unified_html
    assert "tower_keycard=" not in unified_html

    write_result = write_unified_owner_security_command_html(unified)
    show("PACK 132 WRITE UNIFIED HTML", write_result)
    assert write_result.get("ok") is True

    from tower.tower_status import pack132_security_watch_owner_posture_status_bridge
    from tower.security_command_page import pack132_security_watch_owner_posture_html_section

    watch_bridge = pack132_security_watch_owner_posture_status_bridge()
    watch_html = pack132_security_watch_owner_posture_html_section()

    show("PACK 132 BRIDGE CHECKS", {
        "watch_bridge_ok": watch_bridge.get("ok"),
        "watch_bridge_pack": watch_bridge.get("pack"),
        "watch_html_marker": "PACK131_SECURITY_WATCH_OWNER_POSTURE_SECTION" in watch_html,
    })

    assert watch_bridge.get("ok") is True
    assert watch_bridge.get("pack") == "131"
    assert "PACK131_SECURITY_WATCH_OWNER_POSTURE_SECTION" in watch_html
    assert "SHOULD_NOT_SURVIVE" not in watch_html

    route_report = build_ob_route_coverage_report(write_panel=True)
    checkpoint = build_object_permission_integration_checkpoint(write_panel=True)

    show("PACK 132 FINAL HEALTH", {
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

    for path in [
        PROJECT_ROOT / "tower" / "test_tower_pack_132.py",
        PROJECT_ROOT / "tower" / "security_watch_owner_posture.py",
        PROJECT_ROOT / "tower" / "security_incident_checkpoint.py",
        PROJECT_ROOT / "tower" / "security_incident_filters_escalation.py",
        PROJECT_ROOT / "tower" / "security_incident_desk.py",
        PROJECT_ROOT / "tower" / "security_inbox_filters_priorities.py",
        PROJECT_ROOT / "tower" / "security_inbox_review_actions.py",
        PROJECT_ROOT / "tower" / "security_inbox_owner_queue.py",
        PROJECT_ROOT / "tower" / "security_command_owner_quick_actions.py",
        PROJECT_ROOT / "tower" / "security_command_unified_owner_page.py",
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
        "pack": "132",
        "status": "passed",
        "quick_action_count": quick_status.get("action_count"),
        "watch_posture": watch.get("posture", {}).get("posture"),
        "watch_risk_points": watch.get("posture", {}).get("risk_points"),
        "recommended_first_action": watch.get("posture", {}).get("recommended_first_action"),
        "open_incident_count": watch.get("incident_watch", {}).get("open_incident_count"),
        "escalation_ready_count": watch.get("incident_watch", {}).get("escalation_ready_count"),
        "route_coverage_pct": route_report.get("coverage_pct"),
        "guarded_needed_count": route_report.get("guarded_needed_count"),
        "needs_guard_count": route_report.get("needs_guard_count"),
        "helper_wrapped_count": checkpoint.get("helper_wrapped_count"),
        "human_reason": "Security Watch is integrated into unified Security Command UI.",
    }
    show("PACK 132 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
