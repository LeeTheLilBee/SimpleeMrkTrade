
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
    from tower.owner_action_center import (
        build_owner_action_center_status,
        build_owner_action_center_lane_summary,
        build_owner_action_filters_status,
        render_owner_action_filters_section,
        write_owner_action_filters_panel,
    )
    from tower.tower_status import pack138_owner_action_filters_status_bridge
    from tower.ob_route_coverage_report import build_ob_route_coverage_report
    from tower.ob_object_permission_integration_checkpoint import build_object_permission_integration_checkpoint

    run_fast(
        "FAST OWNER ACTION FILTERS",
        "from tower.owner_action_center import build_owner_action_filters_status; "
        "s=build_owner_action_filters_status(write_panel=False); "
        "print(s.get('status'), s.get('pack'), s.get('filtered_action_count'))",
    )

    action_center = build_owner_action_center_status(write_panel=True)
    lane_summary = build_owner_action_center_lane_summary(action_center)
    all_filters = build_owner_action_filters_status(write_panel=True)
    high_filters = build_owner_action_filters_status(severity="high", write_panel=False)
    incident_filters = build_owner_action_filters_status(lane="incident", write_panel=False)
    route_filters = build_owner_action_filters_status(lane="route", write_panel=False)
    top_only = build_owner_action_filters_status(top_only=True, write_panel=False)
    bridge = pack138_owner_action_filters_status_bridge()

    show("PACK 138 ACTION CENTER STATUS", {
        "ok": action_center.get("ok"),
        "status": action_center.get("status"),
        "readiness_score": action_center.get("readiness_score"),
        "action_count": action_center.get("action_count"),
        "top_action": action_center.get("top_action"),
    })

    show("PACK 138 ALL FILTERS", {
        "ok": all_filters.get("ok"),
        "status": all_filters.get("status"),
        "filtered_action_count": all_filters.get("filtered_action_count"),
        "filter_options": all_filters.get("filter_options"),
        "active_filters": all_filters.get("active_filters"),
        "top_action": all_filters.get("top_action"),
        "no_secret_leakage": all_filters.get("no_secret_leakage"),
    })

    show("PACK 138 HIGH FILTERS", {
        "filtered_action_count": high_filters.get("filtered_action_count"),
        "active_filters": high_filters.get("active_filters"),
        "top_action": high_filters.get("top_action"),
    })

    show("PACK 138 INCIDENT FILTERS", {
        "filtered_action_count": incident_filters.get("filtered_action_count"),
        "active_filters": incident_filters.get("active_filters"),
        "top_action": incident_filters.get("top_action"),
    })

    show("PACK 138 ROUTE FILTERS", {
        "filtered_action_count": route_filters.get("filtered_action_count"),
        "active_filters": route_filters.get("active_filters"),
        "top_action": route_filters.get("top_action"),
    })

    show("PACK 138 TOP ONLY", {
        "filtered_action_count": top_only.get("filtered_action_count"),
        "active_filters": top_only.get("active_filters"),
        "top_action": top_only.get("top_action"),
    })

    show("PACK 138 BRIDGE", bridge)

    assert action_center.get("ok") is True
    assert action_center.get("status") == "passed"
    assert action_center.get("action_count", 0) >= 3

    assert lane_summary.get("ok") is True
    assert lane_summary.get("lane_count", 0) >= 2

    assert all_filters.get("ok") is True
    assert all_filters.get("status") == "passed"
    assert all_filters.get("pack") == "138"
    assert all_filters.get("filtered_action_count", 0) >= 3
    assert all_filters.get("readiness_score") == 100
    assert all_filters.get("no_secret_leakage") is True

    options = all_filters.get("filter_options", {})
    assert isinstance(options, dict)
    assert "severity" in options
    assert "lane" in options
    assert "status" in options
    assert "source" in options
    assert "action_type" in options

    assert high_filters.get("ok") is True
    assert high_filters.get("active_filters", {}).get("severity") == "high"
    assert high_filters.get("filtered_action_count", 0) >= 1
    assert all(
        action.get("severity") == "high"
        for action in high_filters.get("actions", [])
        if isinstance(action, dict)
    )

    assert incident_filters.get("ok") is True
    assert incident_filters.get("active_filters", {}).get("lane") == "incident"
    assert incident_filters.get("filtered_action_count", 0) >= 1

    assert route_filters.get("ok") is True
    assert route_filters.get("active_filters", {}).get("lane") == "route"
    assert route_filters.get("filtered_action_count", 0) >= 1

    assert top_only.get("ok") is True
    assert top_only.get("active_filters", {}).get("top_only") is True
    assert top_only.get("filtered_action_count") == 1

    assert bridge.get("ok") is True
    assert bridge.get("pack") == "138"

    no_secret(all_filters)
    no_secret(high_filters)
    no_secret(incident_filters)
    no_secret(route_filters)
    no_secret(top_only)
    no_secret(bridge)

    section = render_owner_action_filters_section(all_filters)
    show("PACK 138 FILTER HTML CHECK", {
        "html_length": len(section),
        "has_marker": "PACK138_OWNER_ACTION_FILTERS_SECTION" in section,
        "has_title": "Owner Action Filters" in section,
        "has_filtered_actions": "Filtered actions" in section,
    })

    assert "PACK138_OWNER_ACTION_FILTERS_SECTION" in section
    assert "Owner Action Filters" in section
    assert "Filtered actions" in section
    assert "SHOULD_NOT_SURVIVE" not in section
    assert "tower_keycard=" not in section

    panel = write_owner_action_filters_panel(all_filters)
    show("PACK 138 PANEL WRITE", panel)
    assert panel.get("ok") is True

    route_report = build_ob_route_coverage_report(write_panel=True)
    checkpoint = build_object_permission_integration_checkpoint(write_panel=True)

    show("PACK 138 FINAL HEALTH", {
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
        "pack138_route_marker": "PACK138_OWNER_ACTION_FILTERS_ROUTE" in app_text,
        "pack138_route_path": "/tower/owner-action-filters.json" in app_text,
        "pack138_route_guard": "pack138_owner_action_filters_route" in app_text,
    }
    show("PACK 138 WEB APP ROUTE CHECKS", route_checks)
    assert all(route_checks.values())

    for path in [
        PROJECT_ROOT / "tower" / "test_tower_pack_138.py",
        PROJECT_ROOT / "tower" / "owner_action_center.py",
        PROJECT_ROOT / "tower" / "tower_status.py",
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
        "pack": "138",
        "status": "passed",
        "readiness_score": 100,
        "base_action_count": action_center.get("action_count"),
        "filtered_action_count": all_filters.get("filtered_action_count"),
        "high_filter_count": high_filters.get("filtered_action_count"),
        "incident_filter_count": incident_filters.get("filtered_action_count"),
        "route_filter_count": route_filters.get("filtered_action_count"),
        "top_only_count": top_only.get("filtered_action_count"),
        "route_coverage_pct": route_report.get("coverage_pct"),
        "guarded_needed_count": route_report.get("guarded_needed_count"),
        "needs_guard_count": route_report.get("needs_guard_count"),
        "helper_wrapped_count": checkpoint.get("helper_wrapped_count"),
        "human_reason": "Owner Action Center action filters are working.",
    }
    show("PACK 138 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
