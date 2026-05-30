
from __future__ import annotations

import json
import os
import sys
import subprocess
import time
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


def run_fast(label: str, code: str, timeout: int = 10):
    start = time.time()
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    elapsed = round(time.time() - start, 2)
    show(label, {
        "elapsed": elapsed,
        "returncode": result.returncode,
        "stdout": result.stdout[-2000:],
        "stderr": result.stderr[-2000:],
    })
    assert result.returncode == 0
    assert elapsed < timeout


def run_tests():
    from tower.owner_action_center import build_owner_action_center_status
    from tower.owner_action_assignments import (
        OWNER_ACTION_ASSIGNMENT_DETAIL_PANEL_PATH,
        OWNER_ACTION_ASSIGNMENT_RECEIPTS_PATH,
        OWNER_ACTION_ASSIGNMENTS_PANEL_PATH,
        OWNER_ACTION_ASSIGNMENTS_PATH,
        OWNER_ACTION_ASSIGNMENTS_STATUS_PATH,
        assign_owner_action,
        build_owner_action_assignment_detail,
        build_owner_action_assignments_status,
        owner_action_assignments_status_card,
        render_owner_action_assignment_detail_section,
        render_owner_action_assignments_section,
        reset_owner_action_assignments_for_test,
        write_owner_action_assignment_detail_panel,
        write_owner_action_assignments_panel,
    )
    from tower.ob_route_coverage_report import build_ob_route_coverage_report
    from tower.ob_object_permission_integration_checkpoint import build_object_permission_integration_checkpoint

    reset_assignments = reset_owner_action_assignments_for_test()
    show("RESET PACK 144 ASSIGNMENTS", reset_assignments)
    assert reset_assignments.get("ok") is True

    action_status = build_owner_action_center_status(write_panel=True)
    actions = action_status.get("actions", []) if isinstance(action_status.get("actions"), list) else []
    assert actions

    action_id = actions[0].get("action_id")
    assert action_id

    missing_action_id = assign_owner_action(
        action_id="",
        assigned_to="owner_solice",
        assigned_role="owner",
        assignment_status="assigned",
        actor_user_id="owner_solice",
        assignment_reason="Missing action id test.",
    )

    missing_assigned_to = assign_owner_action(
        action_id=action_id,
        assigned_to="",
        assigned_role="owner",
        assignment_status="assigned",
        actor_user_id="owner_solice",
        assignment_reason="Missing assigned_to test.",
    )

    invalid_status = assign_owner_action(
        action_id=action_id,
        assigned_to="owner_solice",
        assigned_role="owner",
        assignment_status="floating",
        actor_user_id="owner_solice",
        assignment_reason="Invalid assignment status test.",
    )

    not_found = assign_owner_action(
        action_id="missing_owner_action_144",
        assigned_to="owner_solice",
        assigned_role="owner",
        assignment_status="assigned",
        actor_user_id="owner_solice",
        assignment_reason="Action not found test.",
    )

    assignment_one = assign_owner_action(
        action_id=action_id,
        assigned_to="owner_solice",
        assigned_role="owner",
        assignment_status="assigned",
        actor_user_id="owner_solice",
        assignment_reason="Assign owner review. Secret should_not_survive. tower_keycard=NOPE.",
        metadata={"pack": "144", "token": "SHOULD_NOT_SURVIVE_TOKEN"},
    )

    assignment_two = assign_owner_action(
        action_id=action_id,
        assigned_to="tower_system",
        assigned_role="system_monitor",
        assignment_status="in_progress",
        actor_user_id="owner_solice",
        assignment_reason="Move monitoring work into Tower system lane.",
        metadata={"pack": "144"},
    )

    assignment_three = assign_owner_action(
        action_id=action_id,
        assigned_to="admin_review",
        assigned_role="future_admin",
        assignment_status="completed",
        actor_user_id="owner_solice",
        assignment_reason="Completed assignment handoff for test.",
        metadata={"pack": "144"},
    )

    show("PACK 144 ASSIGNMENT RESULTS", {
        "missing_action_id": missing_action_id,
        "missing_assigned_to": missing_assigned_to,
        "invalid_status": invalid_status,
        "not_found": not_found,
        "assignment_one": assignment_one,
        "assignment_two": assignment_two,
        "assignment_three": assignment_three,
    })

    assert missing_action_id.get("ok") is False
    assert missing_action_id.get("reason_code") == "missing_action_id"

    assert missing_assigned_to.get("ok") is False
    assert missing_assigned_to.get("reason_code") == "missing_assigned_to"

    assert invalid_status.get("ok") is False
    assert invalid_status.get("reason_code") == "invalid_assignment_status"

    assert not_found.get("ok") is False
    assert not_found.get("reason_code") == "owner_action_not_found"

    for result in [assignment_one, assignment_two, assignment_three]:
        assert result.get("ok") is True
        assert result.get("pack") == "144"
        assert result.get("decision") == "owner_action_assignment_updated"
        assert result.get("assignment_id")
        assert result.get("receipt_id")
        assert result.get("no_secret_leakage") is True
        no_secret(result)

    assert assignment_one.get("assignment", {}).get("assignment_reason") == "[REDACTED_OWNER_ACTION_ASSIGNMENT_VALUE]"
    assert "token" not in assignment_one.get("assignment", {}).get("metadata", {})

    run_fast(
        "FAST OWNER ACTION ASSIGNMENTS",
        "from tower.owner_action_assignments import build_owner_action_assignments_status; "
        "s=build_owner_action_assignments_status(write_panel=False); "
        "print(s.get('status'), s.get('pack'), s.get('base_assignment_count'))",
        timeout=10,
    )

    all_assignments = build_owner_action_assignments_status(write_panel=True)
    completed_assignments = build_owner_action_assignments_status(assignment_status="completed", write_panel=False)
    owner_role_assignments = build_owner_action_assignments_status(assigned_role="future_admin", write_panel=False)
    action_assignments = build_owner_action_assignments_status(action_id=action_id, write_panel=False)
    top_only = build_owner_action_assignments_status(top_only=True, write_panel=False)

    top_assignment = all_assignments.get("top_assignment", {}) if isinstance(all_assignments.get("top_assignment"), dict) else {}
    top_assignment_id = top_assignment.get("assignment_id")
    assert top_assignment_id

    detail = build_owner_action_assignment_detail(assignment_id=top_assignment_id, write_panel=True)
    action_detail = build_owner_action_assignment_detail(action_id=action_id, write_panel=False)
    fallback_detail = build_owner_action_assignment_detail(write_panel=False)
    missing_detail = build_owner_action_assignment_detail(assignment_id="missing_owner_action_assignment_144", write_panel=False)
    card = owner_action_assignments_status_card()

    show("PACK 144 ALL ASSIGNMENTS", {
        "ok": all_assignments.get("ok"),
        "pack": all_assignments.get("pack"),
        "status": all_assignments.get("status"),
        "action_count": all_assignments.get("action_count"),
        "base_assignment_count": all_assignments.get("base_assignment_count"),
        "filtered_assignment_count": all_assignments.get("filtered_assignment_count"),
        "unassigned_action_count": all_assignments.get("unassigned_action_count"),
        "receipt_count": all_assignments.get("receipt_count"),
        "filter_options": all_assignments.get("filter_options"),
        "top_assignment": all_assignments.get("top_assignment"),
        "no_secret_leakage": all_assignments.get("no_secret_leakage"),
    })

    show("PACK 144 COMPLETED FILTER", {
        "filtered_assignment_count": completed_assignments.get("filtered_assignment_count"),
        "active_filters": completed_assignments.get("active_filters"),
        "top_assignment": completed_assignments.get("top_assignment"),
    })

    show("PACK 144 ROLE FILTER", {
        "filtered_assignment_count": owner_role_assignments.get("filtered_assignment_count"),
        "active_filters": owner_role_assignments.get("active_filters"),
        "top_assignment": owner_role_assignments.get("top_assignment"),
    })

    show("PACK 144 ACTION FILTER", {
        "filtered_assignment_count": action_assignments.get("filtered_assignment_count"),
        "active_filters": action_assignments.get("active_filters"),
    })

    show("PACK 144 TOP ONLY", {
        "filtered_assignment_count": top_only.get("filtered_assignment_count"),
        "active_filters": top_only.get("active_filters"),
        "top_assignment": top_only.get("top_assignment"),
    })

    show("PACK 144 DETAIL", {
        "ok": detail.get("ok"),
        "pack": detail.get("pack"),
        "status": detail.get("status"),
        "requested_assignment_id": detail.get("requested_assignment_id"),
        "found_assignment_id": detail.get("found_assignment_id"),
        "detail": detail.get("detail"),
        "no_secret_leakage": detail.get("no_secret_leakage"),
    })

    show("PACK 144 ACTION DETAIL", {
        "ok": action_detail.get("ok"),
        "status": action_detail.get("status"),
        "found_assignment_id": action_detail.get("found_assignment_id"),
        "detail": action_detail.get("detail"),
    })

    show("PACK 144 FALLBACK DETAIL", {
        "ok": fallback_detail.get("ok"),
        "status": fallback_detail.get("status"),
        "found_assignment_id": fallback_detail.get("found_assignment_id"),
    })

    show("PACK 144 MISSING DETAIL", {
        "ok": missing_detail.get("ok"),
        "status": missing_detail.get("status"),
        "found_assignment_id": missing_detail.get("found_assignment_id"),
        "readiness_score": missing_detail.get("readiness_score"),
    })

    show("PACK 144 STATUS CARD", card)

    assert all_assignments.get("ok") is True
    assert all_assignments.get("pack") == "144"
    assert all_assignments.get("status") == "passed"
    assert all_assignments.get("action_count", 0) >= 1
    assert all_assignments.get("base_assignment_count") == 1
    assert all_assignments.get("filtered_assignment_count") == 1
    assert all_assignments.get("receipt_count") == 3
    assert all_assignments.get("readiness_score") == 100
    assert all_assignments.get("no_secret_leakage") is True
    assert OWNER_ACTION_ASSIGNMENTS_PATH.exists()
    assert OWNER_ACTION_ASSIGNMENT_RECEIPTS_PATH.exists()
    assert OWNER_ACTION_ASSIGNMENTS_STATUS_PATH.exists()
    assert OWNER_ACTION_ASSIGNMENTS_PANEL_PATH.exists()

    options = all_assignments.get("filter_options", {})
    assert "assigned_to" in options
    assert "assigned_role" in options
    assert "assignment_status" in options
    assert "action_type" in options

    assert completed_assignments.get("ok") is True
    assert completed_assignments.get("active_filters", {}).get("assignment_status") == "completed"
    assert completed_assignments.get("filtered_assignment_count") == 1

    assert owner_role_assignments.get("ok") is True
    assert owner_role_assignments.get("active_filters", {}).get("assigned_role") == "future_admin"
    assert owner_role_assignments.get("filtered_assignment_count") == 1

    assert action_assignments.get("ok") is True
    assert action_assignments.get("active_filters", {}).get("action_id") == action_id.lower()
    assert action_assignments.get("filtered_assignment_count") == 1

    assert top_only.get("ok") is True
    assert top_only.get("active_filters", {}).get("top_only") is True
    assert top_only.get("filtered_assignment_count") == 1

    assert detail.get("ok") is True
    assert detail.get("pack") == "144"
    assert detail.get("status") == "passed"
    assert detail.get("requested_assignment_id") == top_assignment_id
    assert detail.get("found_assignment_id") == top_assignment_id
    assert detail.get("detail", {}).get("assignment_id") == top_assignment_id
    assert detail.get("detail", {}).get("assignment_status") == "completed"
    assert detail.get("detail", {}).get("receipt_count", 0) >= 1
    assert detail.get("no_secret_leakage") is True

    assert action_detail.get("ok") is True
    assert action_detail.get("status") == "passed"
    assert action_detail.get("found_action_id") == action_id

    assert fallback_detail.get("ok") is True
    assert fallback_detail.get("status") == "passed"
    assert fallback_detail.get("found_assignment_id")

    assert missing_detail.get("ok") is False
    assert missing_detail.get("status") == "not_found"
    assert missing_detail.get("readiness_score") == 80

    assert card.get("ok") is True
    assert card.get("pack") == "144"
    assert card.get("readiness_score") == 100
    assert card.get("base_assignment_count") == 1
    assert card.get("receipt_count") == 3

    no_secret(all_assignments)
    no_secret(completed_assignments)
    no_secret(owner_role_assignments)
    no_secret(action_assignments)
    no_secret(top_only)
    no_secret(detail)
    no_secret(action_detail)
    no_secret(fallback_detail)
    no_secret(missing_detail)
    no_secret(card)

    assignment_section = render_owner_action_assignments_section(all_assignments)
    detail_section = render_owner_action_assignment_detail_section(detail)

    show("PACK 144 ASSIGNMENTS HTML CHECK", {
        "html_length": len(assignment_section),
        "has_marker": "PACK144_OWNER_ACTION_ASSIGNMENTS_SECTION" in assignment_section,
        "has_title": "Owner Action Assignments" in assignment_section,
        "has_filtered_assignments": "Filtered assignments" in assignment_section,
    })

    show("PACK 144 DETAIL HTML CHECK", {
        "html_length": len(detail_section),
        "has_marker": "PACK144_OWNER_ACTION_ASSIGNMENT_DETAIL_SECTION" in detail_section,
        "has_assignment_detail": "Assignment Detail" in detail_section or "ASSIGNMENT DETAIL" in detail_section,
    })

    assert "PACK144_OWNER_ACTION_ASSIGNMENTS_SECTION" in assignment_section
    assert "Owner Action Assignments" in assignment_section
    assert "Filtered assignments" in assignment_section
    assert "SHOULD_NOT_SURVIVE" not in assignment_section
    assert "tower_keycard=" not in assignment_section

    assert "PACK144_OWNER_ACTION_ASSIGNMENT_DETAIL_SECTION" in detail_section
    assert "SHOULD_NOT_SURVIVE" not in detail_section
    assert "tower_keycard=" not in detail_section

    panel = write_owner_action_assignments_panel(all_assignments)
    detail_panel = write_owner_action_assignment_detail_panel(detail)

    show("PACK 144 PANEL WRITE", panel)
    show("PACK 144 DETAIL PANEL WRITE", detail_panel)

    assert panel.get("ok") is True
    assert detail_panel.get("ok") is True
    assert OWNER_ACTION_ASSIGNMENTS_PANEL_PATH.exists()
    assert OWNER_ACTION_ASSIGNMENT_DETAIL_PANEL_PATH.exists()

    route_report = build_ob_route_coverage_report(write_panel=True)
    checkpoint = build_object_permission_integration_checkpoint(write_panel=True)

    show("PACK 144 FINAL HEALTH", {
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
    route_checks = {
        "pack144_route_marker": "PACK144_OWNER_ACTION_ASSIGNMENTS_ROUTE" in app_text,
        "pack144_route_path": "/tower/owner-action-assignments.json" in app_text,
        "pack144_route_guard": "pack144_owner_action_assignments_route" in app_text,
    }
    show("PACK 144 WEB APP ROUTE CHECKS", route_checks)
    assert all(route_checks.values())

    for path in [
        PROJECT_ROOT / "tower" / "owner_action_assignments.py",
        PROJECT_ROOT / "tower" / "test_tower_pack_144.py",
        PROJECT_ROOT / "tower" / "owner_action_center.py",
        PROJECT_ROOT / "web" / "app.py",
    ]:
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
        "pack": "144",
        "status": "passed",
        "readiness_score": 100,
        "action_count": all_assignments.get("action_count"),
        "base_assignment_count": all_assignments.get("base_assignment_count"),
        "filtered_assignment_count": all_assignments.get("filtered_assignment_count"),
        "unassigned_action_count": all_assignments.get("unassigned_action_count"),
        "receipt_count": all_assignments.get("receipt_count"),
        "completed_filter_count": completed_assignments.get("filtered_assignment_count"),
        "role_filter_count": owner_role_assignments.get("filtered_assignment_count"),
        "top_only_count": top_only.get("filtered_assignment_count"),
        "detail_assignment_status": detail.get("detail", {}).get("assignment_status"),
        "route_coverage_pct": route_report.get("coverage_pct"),
        "guarded_needed_count": route_report.get("guarded_needed_count"),
        "needs_guard_count": route_report.get("needs_guard_count"),
        "helper_wrapped_count": checkpoint.get("helper_wrapped_count"),
        "human_reason": "Owner Action assignment fields are working.",
    }
    show("PACK 144 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
