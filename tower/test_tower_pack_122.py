
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
    from tower.security_inbox_review_actions import (
        ALLOWED_REVIEW_STATES,
        REVIEW_PANEL_PATH,
        REVIEW_RECEIPTS_PATH,
        REVIEW_STATE_PATH,
        REVIEW_STATUS_PATH,
        apply_security_inbox_review_action,
        build_security_inbox_review_status,
        load_security_inbox_review_status,
        render_security_inbox_review_section,
        reset_security_inbox_review_actions_for_test,
        security_inbox_review_status_card,
        write_security_inbox_review_panel,
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

    reset = reset_security_inbox_review_actions_for_test()
    reset_objects = reset_ob_object_permissions_for_test()

    show("RESET PACK 122 REVIEW ACTIONS", reset)
    show("RESET OBJECT PERMISSIONS", reset_objects)

    assert reset.get("ok") is True
    assert reset_objects.get("ok") is True
    assert "acknowledged" in ALLOWED_REVIEW_STATES
    assert "investigating" in ALLOWED_REVIEW_STATES
    assert "resolved" in ALLOWED_REVIEW_STATES

    # Seed inbox-worthy events.
    position_deny = check_position_permission(
        user_id="beta_122",
        role="beta",
        position_id="pos_other_122",
        object_payload={"owner_user_id": "other_user"},
    )
    position_step = check_position_permission(
        user_id="beta_122",
        role="beta",
        position_id="pos_mine_122",
        action="close",
        object_payload={"owner_user_id": "beta_122"},
    )
    export_step = check_export_permission(
        user_id="owner_solice",
        role="owner",
        export_id="export_122",
    )
    analysis_summary = evaluate_ob_object_permission(
        user_id="beta_122",
        role="beta",
        object_type="analysis",
        object_id="analysis_122",
        action="view",
    )

    show("PACK 122 SEEDED OBJECT EVENTS", {
        "position_deny": position_deny.get("decision"),
        "position_step": position_step.get("decision"),
        "export_step": export_step.get("decision"),
        "analysis_summary": analysis_summary.get("decision"),
    })

    inbox = build_security_inbox_owner_queue(limit_per_source=80, write_panel=True)
    items = inbox.get("recent_items", []) if isinstance(inbox.get("recent_items"), list) else []
    review_candidates = [item for item in items if isinstance(item, dict) and item.get("needs_owner_review")]

    show("PACK 122 INBOX BEFORE REVIEW", {
        "inbox_count": inbox.get("inbox_count"),
        "owner_review_count": inbox.get("owner_review_count"),
        "candidate_count": len(review_candidates),
    })

    assert inbox.get("ok") is True
    assert len(review_candidates) >= 1

    target = review_candidates[0]
    target_id = target.get("inbox_item_id")
    assert target_id

    missing = apply_security_inbox_review_action(
        inbox_item_id="",
        review_state="acknowledged",
        actor_user_id="owner_solice",
    )
    invalid = apply_security_inbox_review_action(
        inbox_item_id=target_id,
        review_state="not_a_real_state",
        actor_user_id="owner_solice",
    )
    ack = apply_security_inbox_review_action(
        inbox_item_id=target_id,
        review_state="acknowledged",
        actor_user_id="owner_solice",
        note="Owner saw this item. No secret should_not_survive value.",
        reason="Pack 122 test acknowledgement.",
        metadata={"pack": "122", "token": "SHOULD_NOT_SURVIVE_TOKEN"},
    )
    investigate = apply_security_inbox_review_action(
        inbox_item_id=target_id,
        review_state="investigating",
        actor_user_id="owner_solice",
        note="Looking closer.",
        reason="Pack 122 test investigation.",
        metadata={"pack": "122"},
    )
    resolved = apply_security_inbox_review_action(
        inbox_item_id=target_id,
        review_state="resolved",
        actor_user_id="owner_solice",
        note="Resolved after review.",
        reason="Pack 122 test resolved.",
        metadata={"pack": "122"},
    )

    show("PACK 122 REVIEW ACTION RESULTS", {
        "missing": missing,
        "invalid": invalid,
        "ack": {
            "ok": ack.get("ok"),
            "prior": ack.get("prior_review_state"),
            "new": ack.get("new_review_state"),
            "no_secret_leakage": ack.get("no_secret_leakage"),
        },
        "investigate": {
            "ok": investigate.get("ok"),
            "prior": investigate.get("prior_review_state"),
            "new": investigate.get("new_review_state"),
            "no_secret_leakage": investigate.get("no_secret_leakage"),
        },
        "resolved": {
            "ok": resolved.get("ok"),
            "prior": resolved.get("prior_review_state"),
            "new": resolved.get("new_review_state"),
            "no_secret_leakage": resolved.get("no_secret_leakage"),
        },
    })

    assert missing.get("ok") is False
    assert missing.get("reason_code") == "missing_inbox_item_id"
    assert invalid.get("ok") is False
    assert invalid.get("reason_code") == "invalid_review_state"
    assert ack.get("ok") is True
    assert ack.get("new_review_state") == "acknowledged"
    assert ack.get("no_secret_leakage") is True
    assert investigate.get("ok") is True
    assert investigate.get("prior_review_state") == "acknowledged"
    assert investigate.get("new_review_state") == "investigating"
    assert resolved.get("ok") is True
    assert resolved.get("prior_review_state") == "investigating"
    assert resolved.get("new_review_state") == "resolved"

    no_secret(ack)
    no_secret(investigate)
    no_secret(resolved)

    status = build_security_inbox_review_status(write_panel=True)

    show("PACK 122 REVIEW STATUS", {
        "ok": status.get("ok"),
        "status": status.get("status"),
        "readiness_score": status.get("readiness_score"),
        "inbox_count": status.get("inbox_count"),
        "tracked_state_count": status.get("tracked_state_count"),
        "receipt_count": status.get("receipt_count"),
        "open_review_count": status.get("open_review_count"),
        "by_state": status.get("by_state"),
        "failed_checks": status.get("failed_checks"),
        "no_secret_leakage": status.get("no_secret_leakage"),
    })

    assert status.get("ok") is True
    assert status.get("status") == "passed"
    assert status.get("readiness_score") == 100
    assert status.get("tracked_state_count", 0) >= 1
    assert status.get("receipt_count", 0) >= 3
    assert status.get("by_state", {}).get("resolved", 0) >= 1
    assert status.get("failed_checks") == []
    assert status.get("no_secret_leakage") is True
    assert REVIEW_STATE_PATH.exists()
    assert REVIEW_RECEIPTS_PATH.exists()
    assert REVIEW_STATUS_PATH.exists()
    assert REVIEW_PANEL_PATH.exists()
    no_secret(status)

    section = render_security_inbox_review_section(status)
    show("PACK 122 REVIEW HTML CHECK", {
        "html_length": len(section),
        "has_marker": "PACK122_SECURITY_INBOX_REVIEW_ACTIONS_SECTION" in section,
        "has_title": "Security Inbox Review Actions" in section,
        "has_open_review": "Open Review" in section,
        "has_resolved": "Resolved" in section,
    })

    assert "PACK122_SECURITY_INBOX_REVIEW_ACTIONS_SECTION" in section
    assert "Security Inbox Review Actions" in section
    assert "Open Review" in section
    assert "Resolved" in section
    assert "SHOULD_NOT_SURVIVE" not in section
    assert "tower_keycard=" not in section

    panel = write_security_inbox_review_panel(status)
    show("PACK 122 PANEL WRITE", panel)
    assert panel.get("ok") is True
    assert REVIEW_PANEL_PATH.exists()

    card = security_inbox_review_status_card()
    loaded = load_security_inbox_review_status()

    show("PACK 122 STATUS CARD", card)
    show("PACK 122 LOADED STATUS", {
        "ok": loaded.get("ok"),
        "status": loaded.get("status"),
        "readiness_score": loaded.get("readiness_score"),
        "tracked_state_count": loaded.get("tracked_state_count"),
        "receipt_count": loaded.get("receipt_count"),
    })

    assert card.get("ok") is True
    assert card.get("pack") == "122"
    assert card.get("readiness_score") == 100
    assert card.get("tracked_state_count", 0) >= 1
    assert card.get("receipt_count", 0) >= 3
    assert loaded.get("ok") is True
    assert loaded.get("status") == "passed"
    assert loaded.get("readiness_score") == 100
    no_secret(card)
    no_secret(loaded)

    route_report = build_ob_route_coverage_report(write_panel=True)
    checkpoint = build_object_permission_integration_checkpoint(write_panel=True)

    show("PACK 122 FINAL HEALTH", {
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
        "pack122_route_marker": "PACK122_SECURITY_INBOX_REVIEW_ROUTES" in app_text,
        "pack122_status_route_path": "/tower/security-inbox-review-status.json" in app_text,
        "pack122_action_route_path": "/tower/security-inbox-review-action.json" in app_text,
        "pack122_status_route_guard": "pack122_security_inbox_review_status_route" in app_text,
        "pack122_action_route_guard": "pack122_security_inbox_review_action_route" in app_text,
    }
    show("PACK 122 WEB APP ROUTE CHECKS", app_checks)
    assert all(app_checks.values())

    for path in [
        PROJECT_ROOT / "tower" / "security_inbox_review_actions.py",
        PROJECT_ROOT / "tower" / "test_tower_pack_122.py",
        PROJECT_ROOT / "tower" / "security_inbox_owner_queue.py",
        PROJECT_ROOT / "tower" / "security_command_owner_ui_checkpoint.py",
        PROJECT_ROOT / "tower" / "security_command_owner_quick_actions.py",
        PROJECT_ROOT / "tower" / "security_command_unified_owner_page.py",
        PROJECT_ROOT / "tower" / "security_command_preferred_destination.py",
        PROJECT_ROOT / "tower" / "security_command_navigation_links.py",
        PROJECT_ROOT / "tower" / "security_command_composition_smoke.py",
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
        "pack": "122",
        "status": "passed",
        "readiness_score": status.get("readiness_score"),
        "tracked_state_count": status.get("tracked_state_count"),
        "receipt_count": status.get("receipt_count"),
        "open_review_count": status.get("open_review_count"),
        "route_coverage_pct": route_report.get("coverage_pct"),
        "guarded_needed_count": route_report.get("guarded_needed_count"),
        "needs_guard_count": route_report.get("needs_guard_count"),
        "helper_wrapped_count": checkpoint.get("helper_wrapped_count"),
        "human_reason": "Security Inbox owner review states/actions are working with separate review receipts.",
    }
    show("PACK 122 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
