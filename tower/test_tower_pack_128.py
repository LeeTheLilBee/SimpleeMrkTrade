
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
    from tower.security_incident_filters_escalation import (
        INCIDENT_FILTERS_PANEL_PATH,
        INCIDENT_FILTERS_STATUS_PATH,
        build_security_incident_filters_escalation_status,
        load_security_incident_filters_escalation_status,
        render_security_incident_filters_escalation_section,
        reset_security_incident_filters_escalation_for_test,
        security_incident_filters_escalation_status_card,
        write_security_incident_filters_escalation_panel,
    )
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
    from tower.ob_route_coverage_report import build_ob_route_coverage_report
    from tower.ob_object_permission_integration_checkpoint import build_object_permission_integration_checkpoint

    reset_filters = reset_security_incident_filters_escalation_for_test()
    reset_incidents = reset_security_incident_desk_for_test()
    reset_review = reset_security_inbox_review_actions_for_test()
    reset_objects = reset_ob_object_permissions_for_test()

    show("RESET PACK 128 INCIDENT FILTERS", reset_filters)
    show("RESET INCIDENT DESK", reset_incidents)
    show("RESET REVIEW ACTIONS", reset_review)
    show("RESET OBJECT PERMISSIONS", reset_objects)

    assert reset_filters.get("ok") is True
    assert reset_incidents.get("ok") is True
    assert reset_review.get("ok") is True
    assert reset_objects.get("ok") is True

    # Seed security activity.
    position_deny = check_position_permission(
        user_id="beta_128",
        role="beta",
        position_id="pos_other_128",
        object_payload={"owner_user_id": "other_user"},
    )
    position_step = check_position_permission(
        user_id="beta_128",
        role="beta",
        position_id="pos_mine_128",
        action="close",
        object_payload={"owner_user_id": "beta_128"},
    )
    export_step = check_export_permission(
        user_id="owner_solice",
        role="owner",
        export_id="export_128",
    )
    analysis_summary = evaluate_ob_object_permission(
        user_id="beta_128",
        role="beta",
        object_type="analysis",
        object_id="analysis_128",
        action="view",
    )

    show("PACK 128 SEEDED EVENTS", {
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
        note="Pack 128 incident filter seed.",
        reason="Pack 128 seed.",
        metadata={"pack": "128", "token": "SHOULD_NOT_SURVIVE_TOKEN"},
    )
    assert ack.get("ok") is True
    no_secret(ack)

    if len(target_ids) > 1:
        inv = apply_security_inbox_review_action(
            inbox_item_id=target_ids[1],
            review_state="investigating",
            actor_user_id="owner_solice",
            note="Pack 128 investigation seed.",
            reason="Pack 128 seed.",
            metadata={"pack": "128"},
        )
        assert inv.get("ok") is True

    filters = build_security_inbox_filters_priorities_status(write_panel=True)
    desk = build_security_incident_desk_status(write_panel=True)

    assert filters.get("ok") is True
    assert desk.get("ok") is True
    assert desk.get("incident_count", 0) >= 1

    candidates = desk.get("incident_candidates", [])
    assert isinstance(candidates, list)
    assert len(candidates) >= 1

    incident_id = candidates[0].get("incident_id")
    assert incident_id

    triaged = apply_security_incident_action(
        incident_id=incident_id,
        incident_status="triaged",
        severity="high",
        actor_user_id="owner_solice",
        assigned_to="owner_solice",
        note="Pack 128 triage seed. Secret should_not_survive.",
        reason="Pack 128 incident filter seed.",
        metadata={"pack": "128", "token": "SHOULD_NOT_SURVIVE_TOKEN"},
    )
    assert triaged.get("ok") is True
    no_secret(triaged)

    if len(candidates) > 1:
        inv_incident = apply_security_incident_action(
            incident_id=candidates[1].get("incident_id"),
            incident_status="investigating",
            severity="high",
            actor_user_id="owner_solice",
            assigned_to="owner_solice",
            note="Pack 128 incident investigating seed.",
            reason="Pack 128 incident filter seed.",
            metadata={"pack": "128"},
        )
        assert inv_incident.get("ok") is True

    if len(candidates) > 2:
        contained = apply_security_incident_action(
            incident_id=candidates[2].get("incident_id"),
            incident_status="contained",
            severity="medium",
            actor_user_id="owner_solice",
            assigned_to="owner_solice",
            note="Pack 128 contained seed.",
            reason="Pack 128 incident filter seed.",
            metadata={"pack": "128"},
        )
        assert contained.get("ok") is True

    desk_after = build_security_incident_desk_status(write_panel=True)
    status = build_security_incident_filters_escalation_status(write_panel=True)

    show("PACK 128 INCIDENT DESK STATUS", {
        "ok": desk_after.get("ok"),
        "status": desk_after.get("status"),
        "incident_count": desk_after.get("incident_count"),
        "open_incident_count": desk_after.get("open_incident_count"),
        "tracked_incident_count": desk_after.get("tracked_incident_count"),
        "receipt_count": desk_after.get("receipt_count"),
        "by_status": desk_after.get("by_status"),
        "by_severity": desk_after.get("by_severity"),
    })

    show("PACK 128 INCIDENT FILTERS STATUS", {
        "ok": status.get("ok"),
        "status": status.get("status"),
        "readiness_score": status.get("readiness_score"),
        "incident_count": status.get("incident_count"),
        "open_incident_count": status.get("open_incident_count"),
        "critical_count": status.get("critical_count"),
        "high_count": status.get("high_count"),
        "triaged_count": status.get("triaged_count"),
        "investigating_count": status.get("investigating_count"),
        "contained_count": status.get("contained_count"),
        "escalation_ready_count": status.get("escalation_ready_count"),
        "views_available": status.get("views_available"),
        "by_status": status.get("by_status"),
        "by_severity": status.get("by_severity"),
        "by_next_action": status.get("by_next_action"),
        "failed_checks": status.get("failed_checks"),
        "no_secret_leakage": status.get("no_secret_leakage"),
    })

    assert desk_after.get("ok") is True
    assert status.get("ok") is True
    assert status.get("status") == "passed"
    assert status.get("readiness_score") == 100
    assert status.get("incident_count", 0) >= 1
    assert status.get("open_incident_count", 0) >= 1
    assert status.get("high_count", 0) >= 1
    assert status.get("escalation_ready_count", 0) >= 1
    assert "all" in status.get("views_available", [])
    assert "open" in status.get("views_available", [])
    assert "escalation_ready" in status.get("views_available", [])
    assert "triaged" in status.get("views_available", [])
    assert isinstance(status.get("by_status"), dict)
    assert isinstance(status.get("by_severity"), dict)
    assert isinstance(status.get("by_next_action"), dict)
    assert status.get("failed_checks") == []
    assert status.get("no_secret_leakage") is True
    assert INCIDENT_FILTERS_STATUS_PATH.exists()
    assert INCIDENT_FILTERS_PANEL_PATH.exists()
    no_secret(status)

    top_incidents = status.get("top_incidents", [])
    assert isinstance(top_incidents, list)
    assert all("incident_sort_score" in item for item in top_incidents if isinstance(item, dict))
    assert all("is_escalation_ready" in item for item in top_incidents if isinstance(item, dict))

    if len(top_incidents) >= 2:
        assert int(top_incidents[0].get("incident_sort_score", 0)) >= int(top_incidents[-1].get("incident_sort_score", 0))

    section = render_security_incident_filters_escalation_section(status)

    show("PACK 128 INCIDENT FILTERS HTML CHECK", {
        "html_length": len(section),
        "has_marker": "PACK128_SECURITY_INCIDENT_FILTERS_ESCALATION_SECTION" in section,
        "has_title": "Incident Filters & Escalation Readiness" in section,
        "has_escalation_ready": "Escalation Ready" in section,
        "has_open": "Open" in section,
    })

    assert "PACK128_SECURITY_INCIDENT_FILTERS_ESCALATION_SECTION" in section
    assert "Incident Filters & Escalation Readiness" in section
    assert "Escalation Ready" in section
    assert "Open" in section
    assert "SHOULD_NOT_SURVIVE" not in section
    assert "tower_keycard=" not in section

    panel = write_security_incident_filters_escalation_panel(status)
    show("PACK 128 PANEL WRITE", panel)
    assert panel.get("ok") is True
    assert INCIDENT_FILTERS_PANEL_PATH.exists()

    card = security_incident_filters_escalation_status_card()
    loaded = load_security_incident_filters_escalation_status()

    show("PACK 128 STATUS CARD", card)
    show("PACK 128 LOADED STATUS", {
        "ok": loaded.get("ok"),
        "status": loaded.get("status"),
        "readiness_score": loaded.get("readiness_score"),
        "incident_count": loaded.get("incident_count"),
        "open_incident_count": loaded.get("open_incident_count"),
        "escalation_ready_count": loaded.get("escalation_ready_count"),
    })

    assert card.get("ok") is True
    assert card.get("pack") == "128"
    assert card.get("readiness_score") == 100
    assert card.get("incident_count", 0) >= 1
    assert card.get("open_incident_count", 0) >= 1
    assert card.get("escalation_ready_count", 0) >= 1
    assert loaded.get("ok") is True
    assert loaded.get("status") == "passed"
    assert loaded.get("readiness_score") == 100
    no_secret(card)
    no_secret(loaded)

    route_report = build_ob_route_coverage_report(write_panel=True)
    checkpoint = build_object_permission_integration_checkpoint(write_panel=True)

    show("PACK 128 FINAL HEALTH", {
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
        "pack128_route_marker": "PACK128_SECURITY_INCIDENT_FILTERS_ESCALATION_ROUTE" in app_text,
        "pack128_route_path": "/tower/security-incident-filters.json" in app_text,
        "pack128_route_guard": "pack128_security_incident_filters_escalation_route" in app_text,
    }
    show("PACK 128 WEB APP ROUTE CHECKS", app_checks)
    assert all(app_checks.values())

    for path in [
        PROJECT_ROOT / "tower" / "security_incident_filters_escalation.py",
        PROJECT_ROOT / "tower" / "test_tower_pack_128.py",
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
        "pack": "128",
        "status": "passed",
        "readiness_score": status.get("readiness_score"),
        "incident_count": status.get("incident_count"),
        "open_incident_count": status.get("open_incident_count"),
        "critical_count": status.get("critical_count"),
        "high_count": status.get("high_count"),
        "escalation_ready_count": status.get("escalation_ready_count"),
        "route_coverage_pct": route_report.get("coverage_pct"),
        "guarded_needed_count": route_report.get("guarded_needed_count"),
        "needs_guard_count": route_report.get("needs_guard_count"),
        "helper_wrapped_count": checkpoint.get("helper_wrapped_count"),
        "human_reason": "Incident Desk filters/escalation readiness are working and serious incidents rise to the top.",
    }
    show("PACK 128 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
