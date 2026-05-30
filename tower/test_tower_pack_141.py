
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
    from tower.owner_action_state_tracking import (
        OWNER_ACTION_STATE_PANEL_PATH,
        OWNER_ACTION_STATE_RECEIPTS_PATH,
        OWNER_ACTION_STATE_STATUS_PATH,
        apply_owner_action_state,
        build_owner_action_state_status,
        owner_action_state_status_card,
        render_owner_action_state_section,
        reset_owner_action_state_tracking_for_test,
        write_owner_action_state_panel,
    )
    from tower.ob_route_coverage_report import build_ob_route_coverage_report
    from tower.ob_object_permission_integration_checkpoint import build_object_permission_integration_checkpoint

    reset = reset_owner_action_state_tracking_for_test()
    show("RESET PACK 141 STATE TRACKING", reset)
    assert reset.get("ok") is True

    run_fast(
        "FAST OWNER ACTION STATE STATUS",
        "from tower.owner_action_state_tracking import build_owner_action_state_status; "
        "s=build_owner_action_state_status(write_panel=False); "
        "print(s.get('status'), s.get('pack'), s.get('action_count'))",
        timeout=10,
    )

    action_status = build_owner_action_center_status(write_panel=True)
    actions = action_status.get("actions", []) if isinstance(action_status.get("actions"), list) else []
    assert actions

    target_action = actions[0]
    action_id = target_action.get("action_id")
    assert action_id

    missing = apply_owner_action_state(
        action_id="",
        new_state="acknowledged",
        actor_user_id="owner_solice",
        reason="Pack 141 missing action test.",
    )

    invalid = apply_owner_action_state(
        action_id=action_id,
        new_state="sleeping",
        actor_user_id="owner_solice",
        reason="Pack 141 invalid state test.",
    )

    not_found = apply_owner_action_state(
        action_id="missing_owner_action_141",
        new_state="acknowledged",
        actor_user_id="owner_solice",
        reason="Pack 141 not found test.",
    )

    ack = apply_owner_action_state(
        action_id=action_id,
        new_state="acknowledged",
        actor_user_id="owner_solice",
        reason="Pack 141 acknowledge test.",
        note="Acknowledge owner action. Secret should_not_survive.",
        metadata={"pack": "141", "token": "SHOULD_NOT_SURVIVE_TOKEN"},
    )

    investigate = apply_owner_action_state(
        action_id=action_id,
        new_state="investigating",
        actor_user_id="owner_solice",
        reason="Pack 141 investigate test.",
        note="Move into investigation.",
        metadata={"pack": "141"},
    )

    resolved = apply_owner_action_state(
        action_id=action_id,
        new_state="resolved",
        actor_user_id="owner_solice",
        reason="Pack 141 resolved test.",
        note="Close this owner command.",
        metadata={"pack": "141"},
    )

    show("PACK 141 STATE ACTION RESULTS", {
        "missing": missing,
        "invalid": invalid,
        "not_found": not_found,
        "ack": ack,
        "investigate": investigate,
        "resolved": resolved,
    })

    assert missing.get("ok") is False
    assert missing.get("reason_code") == "missing_action_id"

    assert invalid.get("ok") is False
    assert invalid.get("reason_code") == "invalid_owner_action_state"

    assert not_found.get("ok") is False
    assert not_found.get("reason_code") == "owner_action_not_found"

    assert ack.get("ok") is True
    assert ack.get("prior_state") == "open"
    assert ack.get("new_state") == "acknowledged"
    assert ack.get("no_secret_leakage") is True

    assert investigate.get("ok") is True
    assert investigate.get("prior_state") == "acknowledged"
    assert investigate.get("new_state") == "investigating"

    assert resolved.get("ok") is True
    assert resolved.get("prior_state") == "investigating"
    assert resolved.get("new_state") == "resolved"

    no_secret(ack)
    no_secret(investigate)
    no_secret(resolved)

    status = build_owner_action_state_status(write_panel=True)
    card = owner_action_state_status_card()

    show("PACK 141 STATE STATUS", {
        "ok": status.get("ok"),
        "pack": status.get("pack"),
        "status": status.get("status"),
        "readiness_score": status.get("readiness_score"),
        "action_count": status.get("action_count"),
        "tracked_action_count": status.get("tracked_action_count"),
        "open_action_count": status.get("open_action_count"),
        "closed_action_count": status.get("closed_action_count"),
        "receipt_count": status.get("receipt_count"),
        "by_state": status.get("by_state"),
        "no_secret_leakage": status.get("no_secret_leakage"),
    })

    show("PACK 141 STATUS CARD", card)

    assert status.get("ok") is True
    assert status.get("pack") == "141"
    assert status.get("status") == "passed"
    assert status.get("readiness_score") == 100
    assert status.get("action_count", 0) >= 1
    assert status.get("tracked_action_count", 0) >= 1
    assert status.get("closed_action_count", 0) >= 1
    assert status.get("receipt_count", 0) >= 3
    assert status.get("by_state", {}).get("resolved", 0) >= 1
    assert status.get("no_secret_leakage") is True
    assert OWNER_ACTION_STATE_STATUS_PATH.exists()
    assert OWNER_ACTION_STATE_RECEIPTS_PATH.exists()

    assert card.get("ok") is True
    assert card.get("pack") == "141"
    assert card.get("readiness_score") == 100
    assert card.get("receipt_count", 0) >= 3

    no_secret(status)
    no_secret(card)

    section = render_owner_action_state_section(status)
    show("PACK 141 STATE HTML CHECK", {
        "html_length": len(section),
        "has_marker": "PACK141_OWNER_ACTION_STATE_SECTION" in section,
        "has_title": "Owner Action State Tracking" in section,
        "has_resolved": "resolved" in section,
    })

    assert "PACK141_OWNER_ACTION_STATE_SECTION" in section
    assert "Owner Action State Tracking" in section
    assert "resolved" in section
    assert "SHOULD_NOT_SURVIVE" not in section
    assert "tower_keycard=" not in section

    panel = write_owner_action_state_panel(status)
    show("PACK 141 PANEL WRITE", panel)
    assert panel.get("ok") is True
    assert OWNER_ACTION_STATE_PANEL_PATH.exists()

    route_report = build_ob_route_coverage_report(write_panel=True)
    checkpoint = build_object_permission_integration_checkpoint(write_panel=True)

    show("PACK 141 FINAL HEALTH", {
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
        "pack141_route_marker": "PACK141_OWNER_ACTION_STATE_ROUTE" in app_text,
        "pack141_route_path": "/tower/owner-action-state.json" in app_text,
        "pack141_route_guard": "pack141_owner_action_state_route" in app_text,
    }
    show("PACK 141 WEB APP ROUTE CHECKS", route_checks)
    assert all(route_checks.values())

    for path in [
        PROJECT_ROOT / "tower" / "owner_action_state_tracking.py",
        PROJECT_ROOT / "tower" / "test_tower_pack_141.py",
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
        "pack": "141",
        "status": "passed",
        "readiness_score": status.get("readiness_score"),
        "action_count": status.get("action_count"),
        "tracked_action_count": status.get("tracked_action_count"),
        "open_action_count": status.get("open_action_count"),
        "closed_action_count": status.get("closed_action_count"),
        "receipt_count": status.get("receipt_count"),
        "route_coverage_pct": route_report.get("coverage_pct"),
        "guarded_needed_count": route_report.get("guarded_needed_count"),
        "needs_guard_count": route_report.get("needs_guard_count"),
        "helper_wrapped_count": checkpoint.get("helper_wrapped_count"),
        "human_reason": "Owner Action Center action state tracking is working.",
    }
    show("PACK 141 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
