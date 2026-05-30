
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


def run_fast(label: str, code: str, timeout: int = 15):
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
    from tower.owner_action_state_tracking import (
        apply_owner_action_state,
        build_owner_action_state_status,
        reset_owner_action_state_tracking_for_test,
    )
    from tower.owner_action_state_receipts import (
        build_owner_action_state_receipts_status,
        reset_owner_action_state_receipts_for_test,
    )
    from tower.owner_action_notes import (
        build_owner_action_notes_status,
        create_owner_action_note,
        reset_owner_action_notes_for_test,
    )
    from tower.owner_action_assignments import (
        assign_owner_action,
        build_owner_action_assignments_status,
        reset_owner_action_assignments_for_test,
    )
    from tower.owner_action_review_checkpoint import (
        OWNER_ACTION_REVIEW_CHECKPOINT_PANEL_PATH,
        OWNER_ACTION_REVIEW_CHECKPOINT_STATUS_PATH,
        build_owner_action_review_checkpoint,
        load_owner_action_review_checkpoint,
        owner_action_review_checkpoint_status_card,
        render_owner_action_review_checkpoint_section,
        reset_owner_action_review_checkpoint_for_test,
        write_owner_action_review_checkpoint_panel,
    )
    from tower.ob_route_coverage_report import build_ob_route_coverage_report
    from tower.ob_object_permission_integration_checkpoint import build_object_permission_integration_checkpoint

    show("RESET PACK 145 REVIEW LAYERS", {
        "state": reset_owner_action_state_tracking_for_test(),
        "receipts": reset_owner_action_state_receipts_for_test(),
        "notes": reset_owner_action_notes_for_test(),
        "assignments": reset_owner_action_assignments_for_test(),
        "checkpoint": reset_owner_action_review_checkpoint_for_test(),
    })

    action_status = build_owner_action_center_status(write_panel=True)
    actions = action_status.get("actions", []) if isinstance(action_status.get("actions"), list) else []
    assert actions

    action_id = actions[0].get("action_id")
    assert action_id

    ack = apply_owner_action_state(
        action_id=action_id,
        new_state="acknowledged",
        actor_user_id="owner_solice",
        reason="Pack 145 checkpoint seed acknowledge.",
        note="Checkpoint state seed.",
        metadata={"pack": "145"},
    )
    investigating = apply_owner_action_state(
        action_id=action_id,
        new_state="investigating",
        actor_user_id="owner_solice",
        reason="Pack 145 checkpoint seed investigating.",
        note="Checkpoint state seed two.",
        metadata={"pack": "145"},
    )
    resolved = apply_owner_action_state(
        action_id=action_id,
        new_state="resolved",
        actor_user_id="owner_solice",
        reason="Pack 145 checkpoint seed resolved.",
        note="Checkpoint state seed three.",
        metadata={"pack": "145"},
    )

    note = create_owner_action_note(
        action_id=action_id,
        note_body="Pack 145 checkpoint note. Secret should_not_survive.",
        actor_user_id="owner_solice",
        note_type="resolution",
        visibility="owner_only",
        metadata={"pack": "145", "token": "SHOULD_NOT_SURVIVE_TOKEN"},
    )

    assignment = assign_owner_action(
        action_id=action_id,
        assigned_to="admin_review",
        assigned_role="future_admin",
        assignment_status="completed",
        actor_user_id="owner_solice",
        assignment_reason="Pack 145 checkpoint assignment.",
        metadata={"pack": "145"},
    )

    show("PACK 145 SEED RESULTS", {
        "ack": ack,
        "investigating": investigating,
        "resolved": resolved,
        "note": note,
        "assignment": assignment,
    })

    assert ack.get("ok") is True
    assert investigating.get("ok") is True
    assert resolved.get("ok") is True
    assert note.get("ok") is True
    assert assignment.get("ok") is True

    no_secret(ack)
    no_secret(investigating)
    no_secret(resolved)
    no_secret(note)
    no_secret(assignment)

    state_status = build_owner_action_state_status(write_panel=True)
    receipt_status = build_owner_action_state_receipts_status(write_panel=True)
    note_status = build_owner_action_notes_status(write_panel=True)
    assignment_status = build_owner_action_assignments_status(write_panel=True)

    assert state_status.get("status") == "passed"
    assert receipt_status.get("status") == "passed"
    assert note_status.get("status") == "passed"
    assert assignment_status.get("status") == "passed"

    run_fast(
        "FAST OWNER ACTION REVIEW CHECKPOINT",
        "from tower.owner_action_review_checkpoint import build_owner_action_review_checkpoint; "
        "s=build_owner_action_review_checkpoint(write_panel=False); "
        "print(s.get('status'), s.get('pack'), s.get('readiness_score'), s.get('review_depth', {}).get('score'))",
        timeout=20,
    )

    checkpoint = build_owner_action_review_checkpoint(write_panel=True)
    card = owner_action_review_checkpoint_status_card()
    loaded = load_owner_action_review_checkpoint()

    show("PACK 145 REVIEW CHECKPOINT", {
        "ok": checkpoint.get("ok"),
        "pack": checkpoint.get("pack"),
        "status": checkpoint.get("status"),
        "readiness_score": checkpoint.get("readiness_score"),
        "failed_checks": checkpoint.get("failed_checks"),
        "owner_action_center": checkpoint.get("owner_action_center"),
        "state_tracking": checkpoint.get("state_tracking"),
        "state_receipts": checkpoint.get("state_receipts"),
        "notes": checkpoint.get("notes"),
        "assignments": checkpoint.get("assignments"),
        "review_depth": checkpoint.get("review_depth"),
        "route_health": checkpoint.get("route_health"),
        "object_checkpoint": checkpoint.get("object_checkpoint"),
        "no_secret_leakage": checkpoint.get("no_secret_leakage"),
    })

    show("PACK 145 STATUS CARD", card)
    show("PACK 145 LOADED", {
        "ok": loaded.get("ok"),
        "status": loaded.get("status"),
        "readiness_score": loaded.get("readiness_score"),
        "review_depth": loaded.get("review_depth"),
    })

    assert checkpoint.get("ok") is True
    assert checkpoint.get("pack") == "145"
    assert checkpoint.get("status") == "passed"
    assert checkpoint.get("readiness_score") == 100
    assert checkpoint.get("failed_checks") == []
    assert checkpoint.get("no_secret_leakage") is True

    assert checkpoint.get("owner_action_center", {}).get("action_count", 0) >= 1
    assert checkpoint.get("state_tracking", {}).get("tracked_action_count", 0) >= 1
    assert checkpoint.get("state_tracking", {}).get("receipt_count", 0) >= 3
    assert checkpoint.get("state_receipts", {}).get("base_receipt_count", 0) >= 3
    assert checkpoint.get("notes", {}).get("base_note_count", 0) >= 1
    assert checkpoint.get("notes", {}).get("receipt_count", 0) >= 1
    assert checkpoint.get("assignments", {}).get("base_assignment_count", 0) >= 1
    assert checkpoint.get("assignments", {}).get("receipt_count", 0) >= 1
    assert checkpoint.get("review_depth", {}).get("score") == 100
    assert checkpoint.get("route_health", {}).get("coverage_pct") == 100
    assert checkpoint.get("route_health", {}).get("unguarded_needed_count") == 0
    assert checkpoint.get("route_health", {}).get("unguarded_high_risk_count") == 0
    assert checkpoint.get("object_checkpoint", {}).get("helper_wrapped_count") == 0

    assert OWNER_ACTION_REVIEW_CHECKPOINT_STATUS_PATH.exists()
    assert OWNER_ACTION_REVIEW_CHECKPOINT_PANEL_PATH.exists()

    assert card.get("ok") is True
    assert card.get("pack") == "145"
    assert card.get("readiness_score") == 100
    assert card.get("review_depth_score") == 100
    assert card.get("tracked_action_count", 0) >= 1
    assert card.get("note_count", 0) >= 1
    assert card.get("assignment_count", 0) >= 1

    assert loaded.get("ok") is True
    assert loaded.get("status") == "passed"
    assert loaded.get("readiness_score") == 100

    no_secret(checkpoint)
    no_secret(card)
    no_secret(loaded)

    section = render_owner_action_review_checkpoint_section(checkpoint)

    show("PACK 145 CHECKPOINT HTML CHECK", {
        "html_length": len(section),
        "has_marker": "PACK145_OWNER_ACTION_REVIEW_CHECKPOINT_SECTION" in section,
        "has_title": "Owner Action Review-State Checkpoint" in section,
        "has_top_assignment": "Top assignment" in section,
    })

    assert "PACK145_OWNER_ACTION_REVIEW_CHECKPOINT_SECTION" in section
    assert "Owner Action Review-State Checkpoint" in section
    assert "Top assignment" in section
    assert "SHOULD_NOT_SURVIVE" not in section
    assert "tower_keycard=" not in section

    panel = write_owner_action_review_checkpoint_panel(checkpoint)
    show("PACK 145 PANEL WRITE", panel)
    assert panel.get("ok") is True

    route_report = build_ob_route_coverage_report(write_panel=True)
    object_checkpoint = build_object_permission_integration_checkpoint(write_panel=True)

    show("PACK 145 FINAL HEALTH", {
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
    route_checks = {
        "pack145_route_marker": "PACK145_OWNER_ACTION_REVIEW_CHECKPOINT_ROUTE" in app_text,
        "pack145_route_path": "/tower/owner-action-review-checkpoint.json" in app_text,
        "pack145_route_guard": "pack145_owner_action_review_checkpoint_route" in app_text,
    }
    show("PACK 145 WEB APP ROUTE CHECKS", route_checks)
    assert all(route_checks.values())

    for path in [
        PROJECT_ROOT / "tower" / "owner_action_review_checkpoint.py",
        PROJECT_ROOT / "tower" / "test_tower_pack_145.py",
        PROJECT_ROOT / "tower" / "owner_action_state_tracking.py",
        PROJECT_ROOT / "tower" / "owner_action_state_receipts.py",
        PROJECT_ROOT / "tower" / "owner_action_notes.py",
        PROJECT_ROOT / "tower" / "owner_action_assignments.py",
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
        "pack": "145",
        "status": "passed",
        "readiness_score": 100,
        "review_depth_score": checkpoint.get("review_depth", {}).get("score"),
        "action_count": checkpoint.get("owner_action_center", {}).get("action_count"),
        "tracked_action_count": checkpoint.get("state_tracking", {}).get("tracked_action_count"),
        "state_receipt_count": checkpoint.get("state_receipts", {}).get("base_receipt_count"),
        "note_count": checkpoint.get("notes", {}).get("base_note_count"),
        "assignment_count": checkpoint.get("assignments", {}).get("base_assignment_count"),
        "route_coverage_pct": route_report.get("coverage_pct"),
        "guarded_needed_count": route_report.get("guarded_needed_count"),
        "needs_guard_count": route_report.get("needs_guard_count"),
        "helper_wrapped_count": object_checkpoint.get("helper_wrapped_count"),
        "human_reason": "Owner Action Center review-state checkpoint is working.",
    }
    show("PACK 145 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
