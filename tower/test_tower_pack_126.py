
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
    from tower.security_incident_desk import (
        ALLOWED_INCIDENT_SEVERITIES,
        ALLOWED_INCIDENT_STATUSES,
        INCIDENT_PANEL_PATH,
        INCIDENT_RECEIPTS_PATH,
        INCIDENT_STATE_PATH,
        INCIDENT_STATUS_PATH,
        apply_security_incident_action,
        build_security_incident_desk_status,
        load_security_incident_desk_status,
        render_security_incident_desk_section,
        reset_security_incident_desk_for_test,
        security_incident_desk_status_card,
        write_security_incident_desk_panel,
    )
    from tower.security_inbox_filters_priorities import build_security_inbox_filters_priorities_status
    from tower.security_inbox_review_actions import (
        apply_security_inbox_review_action,
        build_security_inbox_review_status,
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

    reset_incidents = reset_security_incident_desk_for_test()
    reset_review = reset_security_inbox_review_actions_for_test()
    reset_objects = reset_ob_object_permissions_for_test()

    show("RESET PACK 126 INCIDENT DESK", reset_incidents)
    show("RESET REVIEW ACTIONS", reset_review)
    show("RESET OBJECT PERMISSIONS", reset_objects)

    assert reset_incidents.get("ok") is True
    assert reset_review.get("ok") is True
    assert reset_objects.get("ok") is True
    assert "investigating" in ALLOWED_INCIDENT_STATUSES
    assert "resolved" in ALLOWED_INCIDENT_STATUSES
    assert "critical" in ALLOWED_INCIDENT_SEVERITIES
    assert "high" in ALLOWED_INCIDENT_SEVERITIES

    # Seed security activity.
    position_deny = check_position_permission(
        user_id="beta_126",
        role="beta",
        position_id="pos_other_126",
        object_payload={"owner_user_id": "other_user"},
    )
    position_step = check_position_permission(
        user_id="beta_126",
        role="beta",
        position_id="pos_mine_126",
        action="close",
        object_payload={"owner_user_id": "beta_126"},
    )
    export_step = check_export_permission(
        user_id="owner_solice",
        role="owner",
        export_id="export_126",
    )
    analysis_summary = evaluate_ob_object_permission(
        user_id="beta_126",
        role="beta",
        object_type="analysis",
        object_id="analysis_126",
        action="view",
    )

    show("PACK 126 SEEDED EVENTS", {
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
        note="Pack 126 incident desk seed.",
        reason="Pack 126 incident desk seed.",
        metadata={"pack": "126", "token": "SHOULD_NOT_SURVIVE_TOKEN"},
    )
    assert ack.get("ok") is True
    no_secret(ack)

    if len(target_ids) > 1:
        inv = apply_security_inbox_review_action(
            inbox_item_id=target_ids[1],
            review_state="investigating",
            actor_user_id="owner_solice",
            note="Pack 126 investigation seed.",
            reason="Pack 126 incident desk seed.",
            metadata={"pack": "126"},
        )
        assert inv.get("ok") is True

    review_status = build_security_inbox_review_status(write_panel=True)
    filters_status = build_security_inbox_filters_priorities_status(write_panel=True)
    desk = build_security_incident_desk_status(write_panel=True)

    show("PACK 126 REVIEW STATUS", {
        "ok": review_status.get("ok"),
        "status": review_status.get("status"),
        "tracked_state_count": review_status.get("tracked_state_count"),
        "receipt_count": review_status.get("receipt_count"),
    })
    show("PACK 126 FILTER STATUS", {
        "ok": filters_status.get("ok"),
        "status": filters_status.get("status"),
        "inbox_count": filters_status.get("inbox_count"),
        "high_priority_count": filters_status.get("high_priority_count"),
        "open_review_count": filters_status.get("open_review_count"),
    })
    show("PACK 126 INCIDENT DESK STATUS BEFORE ACTION", {
        "ok": desk.get("ok"),
        "status": desk.get("status"),
        "readiness_score": desk.get("readiness_score"),
        "priority_item_count": desk.get("priority_item_count"),
        "incident_count": desk.get("incident_count"),
        "open_incident_count": desk.get("open_incident_count"),
        "critical_incident_count": desk.get("critical_incident_count"),
        "tracked_incident_count": desk.get("tracked_incident_count"),
        "receipt_count": desk.get("receipt_count"),
        "by_status": desk.get("by_status"),
        "by_severity": desk.get("by_severity"),
        "failed_checks": desk.get("failed_checks"),
        "no_secret_leakage": desk.get("no_secret_leakage"),
    })

    assert review_status.get("ok") is True
    assert filters_status.get("ok") is True

    assert desk.get("ok") is True
    assert desk.get("status") == "passed"
    assert desk.get("readiness_score") == 100
    assert desk.get("priority_item_count", 0) >= 1
    assert desk.get("incident_count", 0) >= 1
    assert desk.get("open_incident_count", 0) >= 1
    assert desk.get("failed_checks") == []
    assert desk.get("no_secret_leakage") is True
    assert INCIDENT_STATUS_PATH.exists()
    assert INCIDENT_PANEL_PATH.exists()
    no_secret(desk)

    candidates = desk.get("incident_candidates", [])
    assert isinstance(candidates, list)
    assert len(candidates) >= 1

    target_incident_id = candidates[0].get("incident_id")
    assert target_incident_id

    missing = apply_security_incident_action(
        incident_id="",
        incident_status="triaged",
        actor_user_id="owner_solice",
    )
    invalid_status = apply_security_incident_action(
        incident_id=target_incident_id,
        incident_status="not_a_real_status",
        actor_user_id="owner_solice",
    )
    invalid_severity = apply_security_incident_action(
        incident_id=target_incident_id,
        incident_status="triaged",
        severity="mega_bad",
        actor_user_id="owner_solice",
    )
    triaged = apply_security_incident_action(
        incident_id=target_incident_id,
        incident_status="triaged",
        severity="high",
        actor_user_id="owner_solice",
        assigned_to="owner_solice",
        note="Triaged in Pack 126. Secret should_not_survive.",
        reason="Pack 126 triage test.",
        metadata={"pack": "126", "token": "SHOULD_NOT_SURVIVE_TOKEN"},
    )
    investigating = apply_security_incident_action(
        incident_id=target_incident_id,
        incident_status="investigating",
        severity="high",
        actor_user_id="owner_solice",
        assigned_to="owner_solice",
        note="Investigating in Pack 126.",
        reason="Pack 126 investigation test.",
        metadata={"pack": "126"},
    )
    contained = apply_security_incident_action(
        incident_id=target_incident_id,
        incident_status="contained",
        severity="medium",
        actor_user_id="owner_solice",
        assigned_to="owner_solice",
        note="Contained in Pack 126.",
        reason="Pack 126 containment test.",
        metadata={"pack": "126"},
    )

    show("PACK 126 INCIDENT ACTION RESULTS", {
        "missing": missing,
        "invalid_status": invalid_status,
        "invalid_severity": invalid_severity,
        "triaged": {
            "ok": triaged.get("ok"),
            "prior": triaged.get("prior_incident_status"),
            "new": triaged.get("new_incident_status"),
            "no_secret_leakage": triaged.get("no_secret_leakage"),
        },
        "investigating": {
            "ok": investigating.get("ok"),
            "prior": investigating.get("prior_incident_status"),
            "new": investigating.get("new_incident_status"),
            "no_secret_leakage": investigating.get("no_secret_leakage"),
        },
        "contained": {
            "ok": contained.get("ok"),
            "prior": contained.get("prior_incident_status"),
            "new": contained.get("new_incident_status"),
            "no_secret_leakage": contained.get("no_secret_leakage"),
        },
    })

    assert missing.get("ok") is False
    assert missing.get("reason_code") == "missing_incident_id"
    assert invalid_status.get("ok") is False
    assert invalid_status.get("reason_code") == "invalid_incident_status"
    assert invalid_severity.get("ok") is False
    assert invalid_severity.get("reason_code") == "invalid_incident_severity"

    assert triaged.get("ok") is True
    assert triaged.get("new_incident_status") == "triaged"
    assert triaged.get("no_secret_leakage") is True
    assert investigating.get("ok") is True
    assert investigating.get("prior_incident_status") == "triaged"
    assert investigating.get("new_incident_status") == "investigating"
    assert contained.get("ok") is True
    assert contained.get("prior_incident_status") == "investigating"
    assert contained.get("new_incident_status") == "contained"

    no_secret(triaged)
    no_secret(investigating)
    no_secret(contained)

    desk_after = build_security_incident_desk_status(write_panel=True)

    show("PACK 126 INCIDENT DESK STATUS AFTER ACTION", {
        "ok": desk_after.get("ok"),
        "status": desk_after.get("status"),
        "readiness_score": desk_after.get("readiness_score"),
        "incident_count": desk_after.get("incident_count"),
        "open_incident_count": desk_after.get("open_incident_count"),
        "tracked_incident_count": desk_after.get("tracked_incident_count"),
        "receipt_count": desk_after.get("receipt_count"),
        "by_status": desk_after.get("by_status"),
        "by_severity": desk_after.get("by_severity"),
    })

    assert desk_after.get("ok") is True
    assert desk_after.get("status") == "passed"
    assert desk_after.get("readiness_score") == 100
    assert desk_after.get("tracked_incident_count", 0) >= 1
    assert desk_after.get("receipt_count", 0) >= 3
    assert desk_after.get("by_status", {}).get("contained", 0) >= 1
    assert INCIDENT_STATE_PATH.exists()
    assert INCIDENT_RECEIPTS_PATH.exists()
    no_secret(desk_after)

    section = render_security_incident_desk_section(desk_after)

    show("PACK 126 INCIDENT HTML CHECK", {
        "html_length": len(section),
        "has_marker": "PACK126_SECURITY_INCIDENT_DESK_SECTION" in section,
        "has_title": "Tower Incident Desk" in section,
        "has_open": "Open" in section,
        "has_receipts": "Receipts" in section,
    })

    assert "PACK126_SECURITY_INCIDENT_DESK_SECTION" in section
    assert "Tower Incident Desk" in section
    assert "Open" in section
    assert "Receipts" in section
    assert "SHOULD_NOT_SURVIVE" not in section
    assert "tower_keycard=" not in section

    panel = write_security_incident_desk_panel(desk_after)
    show("PACK 126 PANEL WRITE", panel)
    assert panel.get("ok") is True
    assert INCIDENT_PANEL_PATH.exists()

    card = security_incident_desk_status_card()
    loaded = load_security_incident_desk_status()

    show("PACK 126 STATUS CARD", card)
    show("PACK 126 LOADED STATUS", {
        "ok": loaded.get("ok"),
        "status": loaded.get("status"),
        "readiness_score": loaded.get("readiness_score"),
        "incident_count": loaded.get("incident_count"),
        "open_incident_count": loaded.get("open_incident_count"),
        "tracked_incident_count": loaded.get("tracked_incident_count"),
        "receipt_count": loaded.get("receipt_count"),
    })

    assert card.get("ok") is True
    assert card.get("pack") == "126"
    assert card.get("readiness_score") == 100
    assert card.get("incident_count", 0) >= 1
    assert card.get("tracked_incident_count", 0) >= 1
    assert card.get("receipt_count", 0) >= 3
    assert loaded.get("ok") is True
    assert loaded.get("status") == "passed"
    assert loaded.get("readiness_score") == 100
    no_secret(card)
    no_secret(loaded)

    route_report = build_ob_route_coverage_report(write_panel=True)
    checkpoint = build_object_permission_integration_checkpoint(write_panel=True)

    show("PACK 126 FINAL HEALTH", {
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
        "pack126_route_marker": "PACK126_SECURITY_INCIDENT_DESK_ROUTES" in app_text,
        "pack126_desk_route_path": "/tower/security-incident-desk.json" in app_text,
        "pack126_action_route_path": "/tower/security-incident-action.json" in app_text,
        "pack126_desk_route_guard": "pack126_security_incident_desk_route" in app_text,
        "pack126_action_route_guard": "pack126_security_incident_action_route" in app_text,
    }
    show("PACK 126 WEB APP ROUTE CHECKS", app_checks)
    assert all(app_checks.values())

    for path in [
        PROJECT_ROOT / "tower" / "security_incident_desk.py",
        PROJECT_ROOT / "tower" / "test_tower_pack_126.py",
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
        "pack": "126",
        "status": "passed",
        "readiness_score": desk_after.get("readiness_score"),
        "incident_count": desk_after.get("incident_count"),
        "open_incident_count": desk_after.get("open_incident_count"),
        "tracked_incident_count": desk_after.get("tracked_incident_count"),
        "receipt_count": desk_after.get("receipt_count"),
        "route_coverage_pct": route_report.get("coverage_pct"),
        "guarded_needed_count": route_report.get("guarded_needed_count"),
        "needs_guard_count": route_report.get("needs_guard_count"),
        "helper_wrapped_count": checkpoint.get("helper_wrapped_count"),
        "human_reason": "Tower Incident Desk foundation is working with separate incident state and receipt tracking.",
    }
    show("PACK 126 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
