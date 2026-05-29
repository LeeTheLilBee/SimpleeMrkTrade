
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
    from tower.ob_object_permission_tightening import (
        check_export_permission,
        check_position_permission,
        evaluate_ob_object_permission,
        reset_ob_object_permissions_for_test,
    )
    from tower.security_inbox_owner_queue import build_security_inbox_owner_queue
    from tower.security_inbox_review_actions import (
        apply_security_inbox_review_action,
        build_security_inbox_review_status,
        reset_security_inbox_review_actions_for_test,
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

    show("RESET OBJECT PERMISSIONS", reset_objects)
    show("RESET REVIEW ACTIONS", reset_review)

    assert reset_objects.get("ok") is True
    assert reset_review.get("ok") is True

    # Seed security activity so inbox/review sections have content.
    position_deny = check_position_permission(
        user_id="beta_123",
        role="beta",
        position_id="pos_other_123",
        object_payload={"owner_user_id": "other_user"},
    )
    position_step = check_position_permission(
        user_id="beta_123",
        role="beta",
        position_id="pos_mine_123",
        action="close",
        object_payload={"owner_user_id": "beta_123"},
    )
    export_step = check_export_permission(
        user_id="owner_solice",
        role="owner",
        export_id="export_123",
    )
    analysis_summary = evaluate_ob_object_permission(
        user_id="beta_123",
        role="beta",
        object_type="analysis",
        object_id="analysis_123",
        action="view",
    )

    show("PACK 123 SEEDED EVENTS", {
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

    target_id = review_candidates[0].get("inbox_item_id")
    assert target_id

    review_result = apply_security_inbox_review_action(
        inbox_item_id=target_id,
        review_state="acknowledged",
        actor_user_id="owner_solice",
        note="Pack 123 UI integration test.",
        reason="Pack 123 review action seed.",
        metadata={"pack": "123", "token": "SHOULD_NOT_SURVIVE_TOKEN"},
    )

    show("PACK 123 REVIEW SEED", {
        "ok": review_result.get("ok"),
        "new_review_state": review_result.get("new_review_state"),
        "no_secret_leakage": review_result.get("no_secret_leakage"),
    })

    assert review_result.get("ok") is True
    assert review_result.get("new_review_state") == "acknowledged"
    assert review_result.get("no_secret_leakage") is True
    no_secret(review_result)

    review_status = build_security_inbox_review_status(write_panel=True)
    quick_status = build_owner_quick_actions_status(write_panel=True)
    unified = build_unified_owner_security_command_status(write_html=True)

    show("PACK 123 REVIEW STATUS", {
        "ok": review_status.get("ok"),
        "status": review_status.get("status"),
        "readiness_score": review_status.get("readiness_score"),
        "tracked_state_count": review_status.get("tracked_state_count"),
        "receipt_count": review_status.get("receipt_count"),
    })
    show("PACK 123 QUICK ACTION STATUS", {
        "ok": quick_status.get("ok"),
        "status": quick_status.get("status"),
        "action_count": quick_status.get("action_count"),
        "readiness_score": quick_status.get("readiness_score"),
    })
    show("PACK 123 UNIFIED STATUS", {
        "ok": unified.get("ok"),
        "status": unified.get("status"),
        "readiness_score": unified.get("readiness_score"),
        "failed_checks": unified.get("failed_checks"),
    })

    assert review_status.get("ok") is True
    assert review_status.get("status") == "passed"
    assert review_status.get("readiness_score") == 100
    assert review_status.get("tracked_state_count", 0) >= 1
    assert review_status.get("receipt_count", 0) >= 1

    assert quick_status.get("ok") is True
    assert quick_status.get("status") == "passed"
    assert quick_status.get("readiness_score") == 100
    assert quick_status.get("action_count", 0) >= 9

    hrefs = {action.get("href") for action in quick_status.get("actions", []) if isinstance(action, dict)}
    assert "/tower/security-inbox.json" in hrefs
    assert "/tower/security-inbox-review-status.json" in hrefs
    assert "/tower/security-inbox-review-action.json" in hrefs

    assert unified.get("ok") is True
    assert unified.get("status") == "passed"
    assert unified.get("readiness_score") == 100
    no_secret(review_status)
    no_secret(quick_status)
    no_secret(unified)

    unified_html = render_unified_owner_security_command_html(unified)

    show("PACK 123 UNIFIED HTML CHECK", {
        "html_length": len(unified_html),
        "has_pack123": "PACK123_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_INBOX_AND_REVIEW" in unified_html,
        "has_pack121": "PACK121_SECURITY_INBOX_OWNER_QUEUE_SECTION" in unified_html,
        "has_pack122": "PACK122_SECURITY_INBOX_REVIEW_ACTIONS_SECTION" in unified_html,
        "has_pack119": "PACK119_OWNER_QUICK_ACTION_RAIL_SECTION" in unified_html,
        "has_pack117": "PACK117_SECURITY_COMMAND_PREFERRED_DESTINATION_SECTION" in unified_html,
        "has_pack115": "PACK115_SECURITY_COMMAND_NAVIGATION_LINKS_SECTION" in unified_html,
        "has_pack113": "PACK113_SECURITY_COMMAND_OBJECT_VISIBILITY_SECTION" in unified_html,
        "has_security_inbox_link": "/tower/security-inbox.json" in unified_html,
        "has_review_status_link": "/tower/security-inbox-review-status.json" in unified_html,
    })

    assert "PACK123_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_INBOX_AND_REVIEW" in unified_html
    assert "PACK121_SECURITY_INBOX_OWNER_QUEUE_SECTION" in unified_html
    assert "PACK122_SECURITY_INBOX_REVIEW_ACTIONS_SECTION" in unified_html
    assert "PACK119_OWNER_QUICK_ACTION_RAIL_SECTION" in unified_html
    assert "PACK117_SECURITY_COMMAND_PREFERRED_DESTINATION_SECTION" in unified_html
    assert "PACK115_SECURITY_COMMAND_NAVIGATION_LINKS_SECTION" in unified_html
    assert "PACK113_SECURITY_COMMAND_OBJECT_VISIBILITY_SECTION" in unified_html
    assert "/tower/security-inbox.json" in unified_html
    assert "/tower/security-inbox-review-status.json" in unified_html
    assert "SHOULD_NOT_SURVIVE" not in unified_html
    assert "tower_keycard=" not in unified_html

    write_result = write_unified_owner_security_command_html(unified)
    show("PACK 123 WRITE UNIFIED HTML", write_result)
    assert write_result.get("ok") is True

    from tower.tower_status import (
        pack123_security_inbox_owner_queue_status_bridge,
        pack123_security_inbox_review_status_bridge,
    )
    from tower.security_command_page import (
        pack123_security_inbox_owner_queue_html_section,
        pack123_security_inbox_review_html_section,
    )

    inbox_bridge = pack123_security_inbox_owner_queue_status_bridge()
    review_bridge = pack123_security_inbox_review_status_bridge()
    inbox_html = pack123_security_inbox_owner_queue_html_section()
    review_html = pack123_security_inbox_review_html_section()

    show("PACK 123 BRIDGE CHECKS", {
        "inbox_bridge_ok": inbox_bridge.get("ok"),
        "review_bridge_ok": review_bridge.get("ok"),
        "inbox_html_marker": "PACK121_SECURITY_INBOX_OWNER_QUEUE_SECTION" in inbox_html,
        "review_html_marker": "PACK122_SECURITY_INBOX_REVIEW_ACTIONS_SECTION" in review_html,
    })

    assert inbox_bridge.get("ok") is True
    assert review_bridge.get("ok") is True
    assert "PACK121_SECURITY_INBOX_OWNER_QUEUE_SECTION" in inbox_html
    assert "PACK122_SECURITY_INBOX_REVIEW_ACTIONS_SECTION" in review_html
    assert "SHOULD_NOT_SURVIVE" not in inbox_html
    assert "SHOULD_NOT_SURVIVE" not in review_html

    route_report = build_ob_route_coverage_report(write_panel=True)
    checkpoint = build_object_permission_integration_checkpoint(write_panel=True)

    show("PACK 123 FINAL HEALTH", {
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
        PROJECT_ROOT / "tower" / "test_tower_pack_123.py",
        PROJECT_ROOT / "tower" / "security_inbox_review_actions.py",
        PROJECT_ROOT / "tower" / "security_inbox_owner_queue.py",
        PROJECT_ROOT / "tower" / "security_command_owner_quick_actions.py",
        PROJECT_ROOT / "tower" / "security_command_unified_owner_page.py",
        PROJECT_ROOT / "tower" / "security_command_preferred_destination.py",
        PROJECT_ROOT / "tower" / "security_command_navigation_links.py",
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
        "pack": "123",
        "status": "passed",
        "quick_action_count": quick_status.get("action_count"),
        "review_receipt_count": review_status.get("receipt_count"),
        "tracked_state_count": review_status.get("tracked_state_count"),
        "route_coverage_pct": route_report.get("coverage_pct"),
        "guarded_needed_count": route_report.get("guarded_needed_count"),
        "needs_guard_count": route_report.get("needs_guard_count"),
        "helper_wrapped_count": checkpoint.get("helper_wrapped_count"),
        "human_reason": "Security Inbox and review actions are integrated into the unified Security Command UI.",
    }
    show("PACK 123 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
