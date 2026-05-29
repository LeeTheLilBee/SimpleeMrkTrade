
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
        "sk_live_should",
        "ghp_should",
    ]
    for item in bad:
        assert item not in s, item


def run_tests():
    from tower.security_incident_checkpoint import (
        INCIDENT_CHECKPOINT_PANEL_PATH,
        INCIDENT_CHECKPOINT_STATUS_PATH,
        build_security_incident_checkpoint,
        load_security_incident_checkpoint,
        render_security_incident_checkpoint_section,
        reset_security_incident_checkpoint_for_test,
        security_incident_checkpoint_status_card,
        write_security_incident_checkpoint_panel,
    )
    from tower.security_incident_filters_escalation import build_security_incident_filters_escalation_status
    from tower.security_incident_desk import (
        apply_security_incident_action,
        build_security_incident_desk_status,
        reset_security_incident_desk_for_test,
    )
    from tower.security_inbox_filters_priorities import build_security_inbox_filters_priorities_status
    from tower.security_inbox_review_actions import (
        apply_security_inbox_review_action,
        reset_security_inbox_review_actions_for_test,
    )
    from tower.security_inbox_owner_queue import build_security_inbox_owner_queue
    from tower.ob_object_permission_tightening import (
        check_export_permission,
        check_position_permission,
        evaluate_ob_object_permission,
        reset_ob_object_permissions_for_test,
    )
    from tower.security_command_owner_quick_actions import build_owner_quick_actions_status
    from tower.security_command_unified_owner_page import build_unified_owner_security_command_status
    from tower.ob_route_coverage_report import build_ob_route_coverage_report
    from tower.ob_object_permission_integration_checkpoint import build_object_permission_integration_checkpoint

    reset_checkpoint = reset_security_incident_checkpoint_for_test()
    reset_incidents = reset_security_incident_desk_for_test()
    reset_review = reset_security_inbox_review_actions_for_test()
    reset_objects = reset_ob_object_permissions_for_test()

    show("RESET PACK 130 INCIDENT CHECKPOINT", reset_checkpoint)
    show("RESET INCIDENT DESK", reset_incidents)
    show("RESET REVIEW ACTIONS", reset_review)
    show("RESET OBJECT PERMISSIONS", reset_objects)

    assert reset_checkpoint.get("ok") is True
    assert reset_incidents.get("ok") is True
    assert reset_review.get("ok") is True
    assert reset_objects.get("ok") is True

    # Seed security activity.
    position_deny = check_position_permission(
        user_id="beta_130",
        role="beta",
        position_id="pos_other_130",
        object_payload={"owner_user_id": "other_user"},
    )
    position_step = check_position_permission(
        user_id="beta_130",
        role="beta",
        position_id="pos_mine_130",
        action="close",
        object_payload={"owner_user_id": "beta_130"},
    )
    export_step = check_export_permission(
        user_id="owner_solice",
        role="owner",
        export_id="export_130",
    )
    analysis_summary = evaluate_ob_object_permission(
        user_id="beta_130",
        role="beta",
        object_type="analysis",
        object_id="analysis_130",
        action="view",
    )

    show("PACK 130 SEEDED EVENTS", {
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
        note="Pack 130 checkpoint seed.",
        reason="Pack 130 seed.",
        metadata={"pack": "130", "token": "SHOULD_NOT_SURVIVE_TOKEN"},
    )
    assert ack.get("ok") is True
    no_secret(ack)

    if len(target_ids) > 1:
        inv = apply_security_inbox_review_action(
            inbox_item_id=target_ids[1],
            review_state="investigating",
            actor_user_id="owner_solice",
            note="Pack 130 investigation seed.",
            reason="Pack 130 seed.",
            metadata={"pack": "130"},
        )
        assert inv.get("ok") is True

    inbox_filters = build_security_inbox_filters_priorities_status(write_panel=True)
    desk = build_security_incident_desk_status(write_panel=True)

    assert inbox_filters.get("ok") is True
    assert desk.get("ok") is True
    assert desk.get("incident_count", 0) >= 1

    incidents = desk.get("incident_candidates", [])
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
        note="Pack 130 triage seed. Secret should_not_survive.",
        reason="Pack 130 incident checkpoint seed.",
        metadata={"pack": "130", "token": "SHOULD_NOT_SURVIVE_TOKEN"},
    )
    assert triaged.get("ok") is True
    assert triaged.get("no_secret_leakage") is True
    no_secret(triaged)

    desk = build_security_incident_desk_status(write_panel=True)
    incident_filters = build_security_incident_filters_escalation_status(write_panel=True)
    quick = build_owner_quick_actions_status(write_panel=True)
    unified = build_unified_owner_security_command_status(write_html=True)
    checkpoint = build_security_incident_checkpoint(write_panel=True)

    show("PACK 130 INCIDENT DESK STATUS", {
        "ok": desk.get("ok"),
        "status": desk.get("status"),
        "readiness_score": desk.get("readiness_score"),
        "incident_count": desk.get("incident_count"),
        "open_incident_count": desk.get("open_incident_count"),
        "tracked_incident_count": desk.get("tracked_incident_count"),
        "receipt_count": desk.get("receipt_count"),
    })

    show("PACK 130 INCIDENT FILTERS STATUS", {
        "ok": incident_filters.get("ok"),
        "status": incident_filters.get("status"),
        "readiness_score": incident_filters.get("readiness_score"),
        "incident_count": incident_filters.get("incident_count"),
        "open_incident_count": incident_filters.get("open_incident_count"),
        "high_count": incident_filters.get("high_count"),
        "escalation_ready_count": incident_filters.get("escalation_ready_count"),
    })

    show("PACK 130 CHECKPOINT STATUS", {
        "ok": checkpoint.get("ok"),
        "status": checkpoint.get("status"),
        "readiness_score": checkpoint.get("readiness_score"),
        "failed_checks": checkpoint.get("failed_checks"),
        "incident_desk": checkpoint.get("incident_desk"),
        "incident_filters": checkpoint.get("incident_filters"),
        "quick_actions": checkpoint.get("quick_actions"),
        "route_health": checkpoint.get("route_health"),
        "object_checkpoint": checkpoint.get("object_checkpoint"),
        "no_secret_leakage": checkpoint.get("no_secret_leakage"),
    })

    assert desk.get("ok") is True
    assert desk.get("status") == "passed"
    assert desk.get("readiness_score") == 100

    assert incident_filters.get("ok") is True
    assert incident_filters.get("status") == "passed"
    assert incident_filters.get("readiness_score") == 100

    assert quick.get("ok") is True
    assert quick.get("status") == "passed"
    assert quick.get("readiness_score") == 100

    assert unified.get("ok") is True
    assert unified.get("status") == "passed"
    assert unified.get("readiness_score") == 100

    assert checkpoint.get("ok") is True
    assert checkpoint.get("status") == "passed"
    assert checkpoint.get("readiness_score") == 100
    assert checkpoint.get("failed_checks") == []
    assert checkpoint.get("incident_desk", {}).get("incident_count", 0) >= 1
    assert checkpoint.get("incident_filters", {}).get("escalation_ready_count", 0) >= 1
    assert checkpoint.get("quick_actions", {}).get("incident_links_present", {}).get("desk") is True
    assert checkpoint.get("quick_actions", {}).get("incident_links_present", {}).get("action") is True
    assert checkpoint.get("quick_actions", {}).get("incident_links_present", {}).get("filters") is True
    assert checkpoint.get("unified_security_command", {}).get("has_incident_desk_section") is True
    assert checkpoint.get("unified_security_command", {}).get("has_incident_filters_section") is True
    assert checkpoint.get("route_health", {}).get("coverage_pct") == 100
    assert checkpoint.get("route_health", {}).get("unguarded_needed_count") == 0
    assert checkpoint.get("route_health", {}).get("unguarded_high_risk_count") == 0
    assert checkpoint.get("object_checkpoint", {}).get("helper_wrapped_count") == 0
    assert checkpoint.get("no_secret_leakage") is True
    assert INCIDENT_CHECKPOINT_STATUS_PATH.exists()
    assert INCIDENT_CHECKPOINT_PANEL_PATH.exists()
    no_secret(checkpoint)

    section = render_security_incident_checkpoint_section(checkpoint)
    show("PACK 130 CHECKPOINT HTML CHECK", {
        "html_length": len(section),
        "has_marker": "PACK130_SECURITY_INCIDENT_CHECKPOINT_SECTION" in section,
        "has_title": "Incident Desk Readiness Checkpoint" in section,
        "has_escalation_ready": "Escalation Ready" in section,
        "has_route_coverage": "Route Coverage" in section,
    })

    assert "PACK130_SECURITY_INCIDENT_CHECKPOINT_SECTION" in section
    assert "Incident Desk Readiness Checkpoint" in section
    assert "Escalation Ready" in section
    assert "Route Coverage" in section
    assert "SHOULD_NOT_SURVIVE" not in section
    assert "tower_keycard=" not in section

    panel = write_security_incident_checkpoint_panel(checkpoint)
    show("PACK 130 PANEL WRITE", panel)
    assert panel.get("ok") is True
    assert INCIDENT_CHECKPOINT_PANEL_PATH.exists()

    card = security_incident_checkpoint_status_card()
    loaded = load_security_incident_checkpoint()

    show("PACK 130 STATUS CARD", card)
    show("PACK 130 LOADED STATUS", {
        "ok": loaded.get("ok"),
        "status": loaded.get("status"),
        "readiness_score": loaded.get("readiness_score"),
        "incident_count": loaded.get("incident_desk", {}).get("incident_count") if isinstance(loaded.get("incident_desk"), dict) else 0,
        "escalation_ready_count": loaded.get("incident_filters", {}).get("escalation_ready_count") if isinstance(loaded.get("incident_filters"), dict) else 0,
    })

    assert card.get("ok") is True
    assert card.get("pack") == "130"
    assert card.get("readiness_score") == 100
    assert card.get("route_coverage_pct") == 100
    assert loaded.get("ok") is True
    assert loaded.get("status") == "passed"
    assert loaded.get("readiness_score") == 100
    no_secret(card)
    no_secret(loaded)

    route_report = build_ob_route_coverage_report(write_panel=True)
    object_checkpoint = build_object_permission_integration_checkpoint(write_panel=True)

    show("PACK 130 FINAL HEALTH", {
        "route_coverage_pct": route_report.get("coverage_pct"),
        "guarded_needed_count": route_report.get("guarded_needed_count"),
        "needs_guard_count": route_report.get("needs_guard_count"),
        "unguarded_needed_count": route_report.get("unguarded_needed_count"),
        "unguarded_high_risk_count": route_report.get("unguarded_high_risk_count"),
        "checkpoint_status": object_checkpoint.get("status"),
        "checkpoint_readiness": object_checkpoint.get("readiness_score"),
        "helper_wrapped_count": object_checkpoint.get("helper_wrapped_count"),
    })

    assert route_report.get("coverage_pct") == 100
    assert route_report.get("unguarded_needed_count") == 0
    assert route_report.get("unguarded_high_risk_count") == 0
    assert object_checkpoint.get("status") == "passed"
    assert object_checkpoint.get("readiness_score") == 100
    assert object_checkpoint.get("helper_wrapped_count") == 0

    app_text = WEB_APP.read_text(encoding="utf-8", errors="replace")
    app_checks = {
        "pack130_route_marker": "PACK130_SECURITY_INCIDENT_CHECKPOINT_ROUTE" in app_text,
        "pack130_route_path": "/tower/security-incident-checkpoint.json" in app_text,
        "pack130_route_guard": "pack130_security_incident_checkpoint_route" in app_text,
    }
    show("PACK 130 WEB APP ROUTE CHECKS", app_checks)
    assert all(app_checks.values())

    for path in [
        PROJECT_ROOT / "tower" / "security_incident_checkpoint.py",
        PROJECT_ROOT / "tower" / "test_tower_pack_130.py",
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
        "pack": "130",
        "status": "passed",
        "readiness_score": checkpoint.get("readiness_score"),
        "incident_count": checkpoint.get("incident_desk", {}).get("incident_count"),
        "open_incident_count": checkpoint.get("incident_desk", {}).get("open_incident_count"),
        "escalation_ready_count": checkpoint.get("incident_filters", {}).get("escalation_ready_count"),
        "route_coverage_pct": route_report.get("coverage_pct"),
        "guarded_needed_count": route_report.get("guarded_needed_count"),
        "needs_guard_count": route_report.get("needs_guard_count"),
        "helper_wrapped_count": object_checkpoint.get("helper_wrapped_count"),
        "human_reason": "Incident Desk checkpoint proves incidents, escalation readiness, unified UI, quick actions, and route guards are healthy.",
    }
    show("PACK 130 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
