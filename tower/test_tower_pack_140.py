
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
    from tower.owner_action_center_checkpoint import (
        OWNER_ACTION_CENTER_CHECKPOINT_PANEL_PATH,
        OWNER_ACTION_CENTER_CHECKPOINT_STATUS_PATH,
        build_owner_action_center_checkpoint,
        load_owner_action_center_checkpoint,
        owner_action_center_checkpoint_status_card,
        render_owner_action_center_checkpoint_section,
        reset_owner_action_center_checkpoint_for_test,
        write_owner_action_center_checkpoint_panel,
    )
    from tower.owner_action_center import (
        build_owner_action_center_status,
        build_owner_action_center_lane_summary,
        build_owner_action_filters_status,
        build_owner_action_detail_status,
    )
    from tower.security_command_owner_quick_actions import build_owner_quick_actions_status
    from tower.ob_route_coverage_report import build_ob_route_coverage_report
    from tower.ob_object_permission_integration_checkpoint import build_object_permission_integration_checkpoint

    reset = reset_owner_action_center_checkpoint_for_test()
    show("RESET PACK 140 CHECKPOINT", reset)
    assert reset.get("ok") is True

    run_fast(
        "FAST OWNER ACTION CHECKPOINT",
        "from tower.owner_action_center_checkpoint import build_owner_action_center_checkpoint; "
        "s=build_owner_action_center_checkpoint(write_panel=False); "
        "print(s.get('status'), s.get('pack'), s.get('readiness_score'))",
        timeout=15,
    )

    action_status = build_owner_action_center_status(write_panel=True)
    lane_status = build_owner_action_center_lane_summary(action_status)
    filters = build_owner_action_filters_status(write_panel=True)
    detail = build_owner_action_detail_status(write_panel=True)
    quick = build_owner_quick_actions_status(write_panel=True)
    checkpoint = build_owner_action_center_checkpoint(write_panel=True)

    show("PACK 140 ACTION CENTER STATUS", {
        "ok": action_status.get("ok"),
        "status": action_status.get("status"),
        "readiness_score": action_status.get("readiness_score"),
        "action_count": action_status.get("action_count"),
        "top_action": action_status.get("top_action"),
    })

    show("PACK 140 CHECKPOINT STATUS", {
        "ok": checkpoint.get("ok"),
        "pack": checkpoint.get("pack"),
        "status": checkpoint.get("status"),
        "readiness_score": checkpoint.get("readiness_score"),
        "failed_checks": checkpoint.get("failed_checks"),
        "owner_action_center": checkpoint.get("owner_action_center"),
        "lane_summary": checkpoint.get("lane_summary"),
        "filters": checkpoint.get("filters"),
        "detail": checkpoint.get("detail"),
        "quick_actions": checkpoint.get("quick_actions"),
        "route_health": checkpoint.get("route_health"),
        "object_checkpoint": checkpoint.get("object_checkpoint"),
        "no_secret_leakage": checkpoint.get("no_secret_leakage"),
    })

    assert action_status.get("ok") is True
    assert action_status.get("status") == "passed"
    assert action_status.get("readiness_score") == 100
    assert action_status.get("action_count", 0) >= 3

    assert lane_status.get("ok") is True
    assert lane_status.get("status") == "passed"
    assert lane_status.get("lane_count", 0) >= 2

    assert filters.get("ok") is True
    assert filters.get("status") == "passed"
    assert filters.get("pack") == "138"
    assert filters.get("filtered_action_count", 0) >= 3

    assert detail.get("ok") is True
    assert detail.get("status") == "passed"
    assert detail.get("pack") == "139"
    assert detail.get("found_action_id")

    assert quick.get("ok") is True
    assert quick.get("status") == "passed"

    assert checkpoint.get("ok") is True
    assert checkpoint.get("pack") == "140"
    assert checkpoint.get("status") == "passed"
    assert checkpoint.get("readiness_score") == 100
    assert checkpoint.get("failed_checks") == []
    assert checkpoint.get("owner_action_center", {}).get("action_count", 0) >= 3
    assert checkpoint.get("owner_action_center", {}).get("open_action_count", 0) >= 3
    assert checkpoint.get("lane_summary", {}).get("lane_count", 0) >= 2
    assert checkpoint.get("filters", {}).get("filtered_action_count", 0) >= 3
    assert checkpoint.get("filters", {}).get("top_only_count") == 1
    assert checkpoint.get("detail", {}).get("found_action_id")
    assert checkpoint.get("quick_actions", {}).get("has_owner_action_center") is True
    assert checkpoint.get("route_health", {}).get("coverage_pct") == 100
    assert checkpoint.get("route_health", {}).get("unguarded_needed_count") == 0
    assert checkpoint.get("route_health", {}).get("unguarded_high_risk_count") == 0
    assert checkpoint.get("object_checkpoint", {}).get("helper_wrapped_count") == 0
    assert checkpoint.get("no_secret_leakage") is True
    assert OWNER_ACTION_CENTER_CHECKPOINT_STATUS_PATH.exists()
    assert OWNER_ACTION_CENTER_CHECKPOINT_PANEL_PATH.exists()

    no_secret(checkpoint)

    section = render_owner_action_center_checkpoint_section(checkpoint)
    show("PACK 140 CHECKPOINT HTML CHECK", {
        "html_length": len(section),
        "has_marker": "PACK140_OWNER_ACTION_CENTER_CHECKPOINT_SECTION" in section,
        "has_title": "Owner Action Center Readiness Checkpoint" in section,
        "has_top_action": "Top action" in section,
    })

    assert "PACK140_OWNER_ACTION_CENTER_CHECKPOINT_SECTION" in section
    assert "Owner Action Center Readiness Checkpoint" in section
    assert "Top action" in section
    assert "SHOULD_NOT_SURVIVE" not in section
    assert "tower_keycard=" not in section

    panel = write_owner_action_center_checkpoint_panel(checkpoint)
    show("PACK 140 PANEL WRITE", panel)
    assert panel.get("ok") is True

    card = owner_action_center_checkpoint_status_card()
    loaded = load_owner_action_center_checkpoint()

    show("PACK 140 STATUS CARD", card)
    show("PACK 140 LOADED STATUS", {
        "ok": loaded.get("ok"),
        "status": loaded.get("status"),
        "readiness_score": loaded.get("readiness_score"),
        "action_count": loaded.get("owner_action_center", {}).get("action_count") if isinstance(loaded.get("owner_action_center"), dict) else 0,
    })

    assert card.get("ok") is True
    assert card.get("pack") == "140"
    assert card.get("readiness_score") == 100
    assert card.get("action_count", 0) >= 3
    assert loaded.get("ok") is True
    assert loaded.get("status") == "passed"
    assert loaded.get("readiness_score") == 100

    route_report = build_ob_route_coverage_report(write_panel=True)
    object_checkpoint = build_object_permission_integration_checkpoint(write_panel=True)

    show("PACK 140 FINAL HEALTH", {
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
        "pack140_route_marker": "PACK140_OWNER_ACTION_CENTER_CHECKPOINT_ROUTE" in app_text,
        "pack140_route_path": "/tower/owner-action-checkpoint.json" in app_text,
        "pack140_route_guard": "pack140_owner_action_center_checkpoint_route" in app_text,
    }
    show("PACK 140 WEB APP ROUTE CHECKS", route_checks)
    assert all(route_checks.values())

    for path in [
        PROJECT_ROOT / "tower" / "owner_action_center_checkpoint.py",
        PROJECT_ROOT / "tower" / "test_tower_pack_140.py",
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
        "pack": "140",
        "status": "passed",
        "readiness_score": checkpoint.get("readiness_score"),
        "action_count": checkpoint.get("owner_action_center", {}).get("action_count"),
        "open_action_count": checkpoint.get("owner_action_center", {}).get("open_action_count"),
        "lane_count": checkpoint.get("lane_summary", {}).get("lane_count"),
        "filtered_action_count": checkpoint.get("filters", {}).get("filtered_action_count"),
        "top_only_count": checkpoint.get("filters", {}).get("top_only_count"),
        "detail_action_type": checkpoint.get("detail", {}).get("detail_action_type"),
        "route_coverage_pct": route_report.get("coverage_pct"),
        "guarded_needed_count": route_report.get("guarded_needed_count"),
        "needs_guard_count": route_report.get("needs_guard_count"),
        "helper_wrapped_count": object_checkpoint.get("helper_wrapped_count"),
        "human_reason": "Owner Action Center checkpoint/readiness summary is working.",
    }
    show("PACK 140 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
