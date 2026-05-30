
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


def run_fast(label: str, code: str, timeout: int = 20):
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
    from tower.owner_action_review_readiness_checkpoint import (
        OWNER_ACTION_REVIEW_READINESS_PANEL_PATH,
        OWNER_ACTION_REVIEW_READINESS_STATUS_PATH,
        build_owner_action_review_readiness_checkpoint,
        load_owner_action_review_readiness_checkpoint,
        owner_action_review_readiness_status_card,
        render_owner_action_review_readiness_section,
        reset_owner_action_review_readiness_checkpoint_for_test,
        write_owner_action_review_readiness_panel,
    )
    from tower.security_command_owner_quick_actions import build_owner_quick_actions_status
    from tower.security_command_unified_owner_page import (
        render_unified_owner_security_command_html,
        write_unified_owner_security_command_html,
    )
    from tower.tower_status import pack150_owner_action_review_readiness_status_bridge
    from tower.ob_route_coverage_report import build_ob_route_coverage_report
    from tower.ob_object_permission_integration_checkpoint import build_object_permission_integration_checkpoint

    reset = reset_owner_action_review_readiness_checkpoint_for_test()
    show("RESET PACK 150 READINESS", reset)
    assert reset.get("ok") is True

    run_fast(
        "FAST PACK 150 READINESS CHECKPOINT",
        "from tower.owner_action_review_readiness_checkpoint import build_owner_action_review_readiness_checkpoint; "
        "s=build_owner_action_review_readiness_checkpoint(write_panel=False); "
        "print(s.get('status'), s.get('pack'), s.get('readiness_score'), s.get('final_summary', {}).get('owner_action_block_complete'))",
        timeout=25,
    )

    run_fast(
        "FAST PACK 150 QUICK ACTIONS",
        "from tower.security_command_owner_quick_actions import build_owner_quick_actions_status; "
        "s=build_owner_quick_actions_status(write_panel=False); "
        "print(s.get('status'), s.get('action_count'), s.get('pack150_readiness_link_present'))",
        timeout=20,
    )

    run_fast(
        "FAST PACK 150 UNIFIED HTML",
        "from tower.security_command_unified_owner_page import render_unified_owner_security_command_html; "
        "h=render_unified_owner_security_command_html(); "
        "print(len(h), 'PACK150_UNIFIED_OWNER_PAGE_INCLUDES_FINAL_OWNER_ACTION_REVIEW_READINESS' in h, 'PACK150_OWNER_ACTION_REVIEW_READINESS_CHECKPOINT_SECTION' in h)",
        timeout=30,
    )

    readiness = build_owner_action_review_readiness_checkpoint(write_panel=True)
    card = owner_action_review_readiness_status_card()
    bridge = pack150_owner_action_review_readiness_status_bridge()
    loaded = load_owner_action_review_readiness_checkpoint()
    section = render_owner_action_review_readiness_section(readiness)
    panel = write_owner_action_review_readiness_panel(readiness)

    quick = build_owner_quick_actions_status(write_panel=True)
    actions = quick.get("actions", []) if isinstance(quick.get("actions"), list) else []
    action_ids = {action.get("action_id") for action in actions if isinstance(action, dict)}
    hrefs = {action.get("href") for action in actions if isinstance(action, dict)}

    unified_html = render_unified_owner_security_command_html()
    unified_write = write_unified_owner_security_command_html()

    show("PACK 150 READINESS STATUS", {
        "ok": readiness.get("ok"),
        "pack": readiness.get("pack"),
        "status": readiness.get("status"),
        "readiness_score": readiness.get("readiness_score"),
        "readiness_label": readiness.get("readiness_label"),
        "failed_checks": readiness.get("failed_checks"),
        "final_summary": readiness.get("final_summary"),
        "route_health": readiness.get("route_health"),
        "object_checkpoint": readiness.get("object_checkpoint"),
        "no_secret_leakage": readiness.get("no_secret_leakage"),
    })

    show("PACK 150 PACK STATUSES", readiness.get("pack_statuses"))
    show("PACK 150 STATUS CARD", card)
    show("PACK 150 TOWER STATUS BRIDGE", bridge)

    show("PACK 150 QUICK ACTIONS", {
        "ok": quick.get("ok"),
        "status": quick.get("status"),
        "action_count": quick.get("action_count"),
        "has_readiness_action": "review_owner_action_readiness_checkpoint" in action_ids,
        "has_readiness_href": "/tower/owner-action-review-readiness-checkpoint.json" in hrefs,
        "pack150_marker": quick.get("pack150_marker"),
        "no_secret_leakage": quick.get("no_secret_leakage"),
    })

    show("PACK 150 SECTION CHECK", {
        "html_length": len(section),
        "has_marker": "PACK150_OWNER_ACTION_REVIEW_READINESS_CHECKPOINT_SECTION" in section,
        "has_title": "FINAL OWNER ACTION REVIEW READINESS" in section or "Owner Action review block complete" in section,
        "has_depth": "Depth" in section,
        "has_focus_lanes": "Focus Lanes" in section,
    })

    show("PACK 150 PANEL WRITE", panel)

    show("PACK 150 UNIFIED HTML CHECK", {
        "html_length": len(unified_html),
        "has_pack150_marker": "PACK150_UNIFIED_OWNER_PAGE_INCLUDES_FINAL_OWNER_ACTION_REVIEW_READINESS" in unified_html,
        "has_pack150_section": "PACK150_OWNER_ACTION_REVIEW_READINESS_CHECKPOINT_SECTION" in unified_html,
        "has_pack149_section": "PACK149_OWNER_ACTION_REVIEW_FOCUS_LANES_SECTION" in unified_html,
        "has_pack148_section": "PACK148_OWNER_ACTION_REVIEW_COMPACT_CARD_SECTION" in unified_html,
        "has_pack147_section": "PACK147_OWNER_ACTION_REVIEW_DASHBOARD_CARDS_SECTION" in unified_html,
        "has_pack145_section": "PACK145_OWNER_ACTION_REVIEW_CHECKPOINT_SECTION" in unified_html,
    })

    show("PACK 150 WRITE UNIFIED HTML", unified_write)

    assert readiness.get("ok") is True
    assert readiness.get("pack") == "150"
    assert readiness.get("status") == "passed"
    assert readiness.get("readiness_score") == 100
    assert readiness.get("readiness_label") == "Owner Action review block complete"
    assert readiness.get("failed_checks") == []
    assert readiness.get("no_secret_leakage") is True

    summary = readiness.get("final_summary", {})
    assert summary.get("owner_action_block_complete") is True
    assert summary.get("review_depth_score") == 100
    assert summary.get("dashboard_card_count") == 7
    assert summary.get("compact_status") == "ready"
    assert summary.get("focus_lane_count", 0) >= 9
    assert summary.get("quick_action_count", 0) >= 18
    assert summary.get("route_coverage_pct") == 100
    assert summary.get("helper_wrapped_count") == 0

    route = readiness.get("route_health", {})
    assert route.get("coverage_pct") == 100
    assert route.get("unguarded_needed_count") == 0
    assert route.get("unguarded_high_risk_count") == 0

    obj = readiness.get("object_checkpoint", {})
    assert obj.get("status") == "passed"
    assert obj.get("helper_wrapped_count") == 0

    pack_statuses = readiness.get("pack_statuses", {})
    for key in [
        "141_state_tracking",
        "142_state_receipts",
        "143_notes",
        "144_assignments",
        "145_review_checkpoint",
        "146_quick_unified",
        "147_dashboard_cards",
        "148_compact_card",
        "149_focus_lanes",
    ]:
        assert key in pack_statuses

    assert card.get("ok") is True
    assert card.get("pack") == "150"
    assert card.get("readiness_score") == 100
    assert card.get("owner_action_block_complete") is True
    assert card.get("review_depth_score") == 100
    assert card.get("dashboard_card_count") == 7
    assert card.get("compact_status") == "ready"
    assert card.get("focus_lane_count", 0) >= 9
    assert card.get("route_coverage_pct") == 100
    assert card.get("helper_wrapped_count") == 0

    assert bridge.get("ok") is True
    assert bridge.get("pack") == "150"
    assert bridge.get("readiness_score") == 100
    assert bridge.get("owner_action_block_complete") is True

    assert loaded.get("ok") is True
    assert loaded.get("status") == "passed"
    assert loaded.get("readiness_score") == 100

    assert OWNER_ACTION_REVIEW_READINESS_STATUS_PATH.exists()
    assert OWNER_ACTION_REVIEW_READINESS_PANEL_PATH.exists()

    assert quick.get("ok") is True
    assert quick.get("status") == "passed"
    assert quick.get("pack150_readiness_link_present") is True
    assert quick.get("pack150_marker") == "PACK150_OWNER_ACTION_REVIEW_READINESS_QUICK_LINK"
    assert "review_owner_action_readiness_checkpoint" in action_ids
    assert "/tower/owner-action-review-readiness-checkpoint.json" in hrefs
    assert quick.get("no_secret_leakage") is True

    assert "PACK150_OWNER_ACTION_REVIEW_READINESS_CHECKPOINT_SECTION" in section
    assert "Depth" in section
    assert "Focus Lanes" in section
    assert "SHOULD_NOT_SURVIVE" not in section
    assert "tower_keycard=" not in section

    assert panel.get("ok") is True
    assert panel.get("pack") == "150"

    assert "PACK150_UNIFIED_OWNER_PAGE_INCLUDES_FINAL_OWNER_ACTION_REVIEW_READINESS" in unified_html
    assert "PACK150_OWNER_ACTION_REVIEW_READINESS_CHECKPOINT_SECTION" in unified_html
    assert "PACK149_OWNER_ACTION_REVIEW_FOCUS_LANES_SECTION" in unified_html
    assert "PACK148_OWNER_ACTION_REVIEW_COMPACT_CARD_SECTION" in unified_html
    assert "PACK147_OWNER_ACTION_REVIEW_DASHBOARD_CARDS_SECTION" in unified_html
    assert "PACK145_OWNER_ACTION_REVIEW_CHECKPOINT_SECTION" in unified_html
    assert "SHOULD_NOT_SURVIVE" not in unified_html
    assert "tower_keycard=" not in unified_html

    assert unified_write.get("ok") is True
    assert unified_write.get("pack") == "150"
    assert unified_write.get("html_length", 0) > 1000

    no_secret(readiness)
    no_secret(card)
    no_secret(bridge)
    no_secret(loaded)
    no_secret(quick)

    route_report = build_ob_route_coverage_report(write_panel=True)
    object_checkpoint = build_object_permission_integration_checkpoint(write_panel=True)

    show("PACK 150 FINAL HEALTH", {
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
        "pack150_route_marker": "PACK150_OWNER_ACTION_REVIEW_READINESS_CHECKPOINT_ROUTE" in app_text,
        "pack150_route_path": "/tower/owner-action-review-readiness-checkpoint.json" in app_text,
        "pack150_route_guard": "pack150_owner_action_review_readiness_checkpoint_route" in app_text,
        "pack149_route_still_present": "/tower/owner-action-review-focus-lanes.json" in app_text,
    }
    show("PACK 150 WEB APP ROUTE CHECKS", route_checks)
    assert all(route_checks.values())

    for path in [
        PROJECT_ROOT / "tower" / "owner_action_review_readiness_checkpoint.py",
        PROJECT_ROOT / "tower" / "security_command_owner_quick_actions.py",
        PROJECT_ROOT / "tower" / "security_command_unified_owner_page.py",
        PROJECT_ROOT / "tower" / "tower_status.py",
        PROJECT_ROOT / "tower" / "test_tower_pack_150.py",
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
        "pack": "150",
        "status": "passed",
        "readiness_score": 100,
        "owner_action_block_complete": True,
        "review_depth_score": summary.get("review_depth_score"),
        "dashboard_card_count": summary.get("dashboard_card_count"),
        "compact_status": summary.get("compact_status"),
        "focus_lane_count": summary.get("focus_lane_count"),
        "quick_action_count": summary.get("quick_action_count"),
        "route_coverage_pct": route_report.get("coverage_pct"),
        "guarded_needed_count": route_report.get("guarded_needed_count"),
        "needs_guard_count": route_report.get("needs_guard_count"),
        "helper_wrapped_count": object_checkpoint.get("helper_wrapped_count"),
        "human_reason": "Final Owner Action review readiness checkpoint is working.",
    }
    show("PACK 150 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
