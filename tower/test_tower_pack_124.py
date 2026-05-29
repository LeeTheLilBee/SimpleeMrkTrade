
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
    from tower.security_inbox_filters_priorities import (
        FILTERS_PANEL_PATH,
        FILTERS_STATUS_PATH,
        build_security_inbox_filters_priorities_status,
        load_security_inbox_filters_priorities_status,
        render_security_inbox_filters_priorities_section,
        reset_security_inbox_filters_priorities_for_test,
        security_inbox_filters_priorities_status_card,
        write_security_inbox_filters_priorities_panel,
    )
    from tower.security_inbox_owner_queue import build_security_inbox_owner_queue
    from tower.security_inbox_review_actions import (
        apply_security_inbox_review_action,
        build_security_inbox_review_status,
        reset_security_inbox_review_actions_for_test,
    )
    from tower.ob_object_permission_tightening import (
        check_export_permission,
        check_position_permission,
        evaluate_ob_object_permission,
        reset_ob_object_permissions_for_test,
    )
    from tower.ob_route_coverage_report import build_ob_route_coverage_report
    from tower.ob_object_permission_integration_checkpoint import build_object_permission_integration_checkpoint

    reset_filters = reset_security_inbox_filters_priorities_for_test()
    reset_review = reset_security_inbox_review_actions_for_test()
    reset_objects = reset_ob_object_permissions_for_test()

    show("RESET PACK 124 FILTERS", reset_filters)
    show("RESET REVIEW ACTIONS", reset_review)
    show("RESET OBJECT PERMISSIONS", reset_objects)

    assert reset_filters.get("ok") is True
    assert reset_review.get("ok") is True
    assert reset_objects.get("ok") is True

    # Seed inbox-worthy events.
    position_deny = check_position_permission(
        user_id="beta_124",
        role="beta",
        position_id="pos_other_124",
        object_payload={"owner_user_id": "other_user"},
    )
    position_step = check_position_permission(
        user_id="beta_124",
        role="beta",
        position_id="pos_mine_124",
        action="close",
        object_payload={"owner_user_id": "beta_124"},
    )
    export_step = check_export_permission(
        user_id="owner_solice",
        role="owner",
        export_id="export_124",
    )
    analysis_summary = evaluate_ob_object_permission(
        user_id="beta_124",
        role="beta",
        object_type="analysis",
        object_id="analysis_124",
        action="view",
    )

    show("PACK 124 SEEDED OBJECT EVENTS", {
        "position_deny": position_deny.get("decision"),
        "position_step": position_step.get("decision"),
        "export_step": export_step.get("decision"),
        "analysis_summary": analysis_summary.get("decision"),
    })

    inbox = build_security_inbox_owner_queue(limit_per_source=80, write_panel=True)
    items = inbox.get("recent_items", []) if isinstance(inbox.get("recent_items"), list) else []
    review_candidates = [item for item in items if isinstance(item, dict) and item.get("needs_owner_review")]

    assert inbox.get("ok") is True
    assert len(review_candidates) >= 1

    # Apply several review states to create variety.
    target_ids = [item.get("inbox_item_id") for item in review_candidates[:3] if item.get("inbox_item_id")]
    assert target_ids

    ack = apply_security_inbox_review_action(
        inbox_item_id=target_ids[0],
        review_state="acknowledged",
        actor_user_id="owner_solice",
        note="Pack 124 acknowledgement.",
        reason="Pack 124 filter seed.",
        metadata={"pack": "124", "token": "SHOULD_NOT_SURVIVE_TOKEN"},
    )
    assert ack.get("ok") is True
    no_secret(ack)

    if len(target_ids) > 1:
        inv = apply_security_inbox_review_action(
            inbox_item_id=target_ids[1],
            review_state="investigating",
            actor_user_id="owner_solice",
            note="Pack 124 investigation.",
            reason="Pack 124 filter seed.",
            metadata={"pack": "124"},
        )
        assert inv.get("ok") is True

    if len(target_ids) > 2:
        res = apply_security_inbox_review_action(
            inbox_item_id=target_ids[2],
            review_state="resolved",
            actor_user_id="owner_solice",
            note="Pack 124 resolved.",
            reason="Pack 124 filter seed.",
            metadata={"pack": "124"},
        )
        assert res.get("ok") is True

    review_status = build_security_inbox_review_status(write_panel=True)
    status = build_security_inbox_filters_priorities_status(write_panel=True)

    show("PACK 124 REVIEW STATUS", {
        "ok": review_status.get("ok"),
        "status": review_status.get("status"),
        "inbox_count": review_status.get("inbox_count"),
        "tracked_state_count": review_status.get("tracked_state_count"),
        "receipt_count": review_status.get("receipt_count"),
        "by_state": review_status.get("by_state"),
    })

    show("PACK 124 FILTERS STATUS", {
        "ok": status.get("ok"),
        "status": status.get("status"),
        "readiness_score": status.get("readiness_score"),
        "inbox_count": status.get("inbox_count"),
        "high_priority_count": status.get("high_priority_count"),
        "open_review_count": status.get("open_review_count"),
        "unresolved_count": status.get("unresolved_count"),
        "resolved_count": status.get("resolved_count"),
        "archived_count": status.get("archived_count"),
        "views_available": status.get("views_available"),
        "by_source": status.get("by_source"),
        "by_severity": status.get("by_severity"),
        "by_review_state": status.get("by_review_state"),
        "failed_checks": status.get("failed_checks"),
        "no_secret_leakage": status.get("no_secret_leakage"),
    })

    assert review_status.get("ok") is True
    assert review_status.get("status") == "passed"

    assert status.get("ok") is True
    assert status.get("status") == "passed"
    assert status.get("readiness_score") == 100
    assert status.get("inbox_count", 0) >= 1
    assert status.get("open_review_count", 0) >= 1
    assert status.get("unresolved_count", 0) >= 1
    assert "all" in status.get("views_available", [])
    assert "high_priority" in status.get("views_available", [])
    assert "open_review" in status.get("views_available", [])
    assert "resolved" in status.get("views_available", [])
    assert isinstance(status.get("by_source"), dict)
    assert isinstance(status.get("by_severity"), dict)
    assert isinstance(status.get("by_review_state"), dict)
    assert status.get("failed_checks") == []
    assert status.get("no_secret_leakage") is True
    assert FILTERS_STATUS_PATH.exists()
    assert FILTERS_PANEL_PATH.exists()
    no_secret(status)

    top_items = status.get("top_priority_items", [])
    assert isinstance(top_items, list)
    assert all("priority_score" in item for item in top_items if isinstance(item, dict))

    if len(top_items) >= 2:
        assert int(top_items[0].get("priority_score", 0)) >= int(top_items[-1].get("priority_score", 0))

    section = render_security_inbox_filters_priorities_section(status)

    show("PACK 124 FILTERS HTML CHECK", {
        "html_length": len(section),
        "has_marker": "PACK124_SECURITY_INBOX_FILTERS_PRIORITIES_SECTION" in section,
        "has_title": "Security Inbox Filters & Priorities" in section,
        "has_high_priority": "High Priority" in section,
        "has_open_review": "Open Review" in section,
    })

    assert "PACK124_SECURITY_INBOX_FILTERS_PRIORITIES_SECTION" in section
    assert "Security Inbox Filters & Priorities" in section
    assert "High Priority" in section
    assert "Open Review" in section
    assert "SHOULD_NOT_SURVIVE" not in section
    assert "tower_keycard=" not in section

    panel = write_security_inbox_filters_priorities_panel(status)
    show("PACK 124 PANEL WRITE", panel)
    assert panel.get("ok") is True
    assert FILTERS_PANEL_PATH.exists()

    card = security_inbox_filters_priorities_status_card()
    loaded = load_security_inbox_filters_priorities_status()

    show("PACK 124 STATUS CARD", card)
    show("PACK 124 LOADED STATUS", {
        "ok": loaded.get("ok"),
        "status": loaded.get("status"),
        "readiness_score": loaded.get("readiness_score"),
        "inbox_count": loaded.get("inbox_count"),
        "high_priority_count": loaded.get("high_priority_count"),
        "open_review_count": loaded.get("open_review_count"),
    })

    assert card.get("ok") is True
    assert card.get("pack") == "124"
    assert card.get("readiness_score") == 100
    assert loaded.get("ok") is True
    assert loaded.get("status") == "passed"
    assert loaded.get("readiness_score") == 100
    no_secret(card)
    no_secret(loaded)

    route_report = build_ob_route_coverage_report(write_panel=True)
    checkpoint = build_object_permission_integration_checkpoint(write_panel=True)

    show("PACK 124 FINAL HEALTH", {
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
        "pack124_route_marker": "PACK124_SECURITY_INBOX_FILTERS_PRIORITIES_ROUTE" in app_text,
        "pack124_route_path": "/tower/security-inbox-filters.json" in app_text,
        "pack124_route_guard": "pack124_security_inbox_filters_priorities_route" in app_text,
    }
    show("PACK 124 WEB APP ROUTE CHECKS", app_checks)
    assert all(app_checks.values())

    for path in [
        PROJECT_ROOT / "tower" / "security_inbox_filters_priorities.py",
        PROJECT_ROOT / "tower" / "test_tower_pack_124.py",
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
        "pack": "124",
        "status": "passed",
        "readiness_score": status.get("readiness_score"),
        "inbox_count": status.get("inbox_count"),
        "high_priority_count": status.get("high_priority_count"),
        "open_review_count": status.get("open_review_count"),
        "unresolved_count": status.get("unresolved_count"),
        "route_coverage_pct": route_report.get("coverage_pct"),
        "guarded_needed_count": route_report.get("guarded_needed_count"),
        "needs_guard_count": route_report.get("needs_guard_count"),
        "helper_wrapped_count": checkpoint.get("helper_wrapped_count"),
        "human_reason": "Security Inbox filters/priorities are working and priority items rise to the top.",
    }
    show("PACK 124 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
