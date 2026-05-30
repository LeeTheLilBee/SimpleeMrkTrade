
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
        build_owner_action_center_lane_summary,
        build_owner_action_center_quick_metadata,
        build_owner_action_center_status,
        load_owner_action_center_status,
        owner_action_center_status_card,
    )
    from tower.security_command_owner_quick_actions import build_owner_quick_actions_status
    from tower.security_command_unified_owner_page import build_unified_owner_security_command_status
    from tower.ob_route_coverage_report import build_ob_route_coverage_report
    from tower.ob_object_permission_integration_checkpoint import build_object_permission_integration_checkpoint
    from tower.tower_status import pack137_owner_action_center_lane_status_bridge

    run_fast(
        "FAST ACTION CENTER STATUS",
        "from tower.owner_action_center import build_owner_action_center_status; "
        "s=build_owner_action_center_status(write_panel=False); "
        "print(s.get('status'), s.get('pack'), s.get('action_count'))",
    )

    status = build_owner_action_center_status(write_panel=True)
    lane_summary = build_owner_action_center_lane_summary(status)
    quick_metadata = build_owner_action_center_quick_metadata(status)
    card = owner_action_center_status_card()
    bridge = pack137_owner_action_center_lane_status_bridge()
    quick = build_owner_quick_actions_status(write_panel=True)
    unified = build_unified_owner_security_command_status(write_html=True)

    show("PACK 137 ACTION CENTER STATUS", {
        "ok": status.get("ok"),
        "pack": status.get("pack"),
        "status": status.get("status"),
        "readiness_score": status.get("readiness_score"),
        "action_count": status.get("action_count"),
        "open_action_count": status.get("open_action_count"),
        "top_action": status.get("top_action"),
        "failed_checks": status.get("failed_checks"),
    })

    show("PACK 137 LANE SUMMARY", lane_summary)
    show("PACK 137 QUICK METADATA", quick_metadata)
    show("PACK 137 STATUS CARD", card)
    show("PACK 137 BRIDGE", bridge)

    assert status.get("ok") is True
    assert status.get("status") == "passed"
    assert status.get("readiness_score") == 100
    assert status.get("action_count", 0) >= 3

    assert lane_summary.get("ok") is True
    assert lane_summary.get("status") == "passed"
    assert lane_summary.get("lane_count", 0) >= 2
    assert isinstance(lane_summary.get("lanes"), list)
    assert lane_summary.get("top_lane", {}).get("lane") in {
        "incident",
        "inbox",
        "route",
        "watch",
        "monitor",
        "command",
    }

    lane_names = {lane.get("lane") for lane in lane_summary.get("lanes", []) if isinstance(lane, dict)}
    assert "incident" in lane_names or "inbox" in lane_names
    assert "route" in lane_names or "monitor" in lane_names or "watch" in lane_names

    assert quick_metadata.get("ok") is True
    assert quick_metadata.get("pack") == "137"
    assert quick_metadata.get("action_count", 0) >= 3
    assert quick_metadata.get("top_action_href")
    assert quick_metadata.get("top_recommended_action")
    assert quick_metadata.get("no_secret_leakage") is True

    assert card.get("ok") is True
    assert card.get("pack") == "135+137"
    assert card.get("lane_count", 0) >= 2
    assert card.get("top_lane")
    assert card.get("top_action_href")
    assert card.get("no_secret_leakage") is True

    assert bridge.get("ok") is True
    assert bridge.get("pack") == "137"
    assert bridge.get("quick_metadata", {}).get("ok") is True
    assert bridge.get("lane_summary", {}).get("ok") is True

    no_secret(status)
    no_secret(lane_summary)
    no_secret(quick_metadata)
    no_secret(card)
    no_secret(bridge)

    show("PACK 137 QUICK ACTION STATUS", {
        "ok": quick.get("ok"),
        "status": quick.get("status"),
        "readiness_score": quick.get("readiness_score"),
        "action_count": quick.get("action_count"),
    })

    hrefs = {action.get("href") for action in quick.get("actions", []) if isinstance(action, dict)}
    assert "/tower/owner-action-center.json" in hrefs

    owner_actions = [
        action for action in quick.get("actions", [])
        if isinstance(action, dict) and action.get("href") == "/tower/owner-action-center.json"
    ]
    assert owner_actions
    owner_action = owner_actions[0]
    assert owner_action.get("badge") == "Command Queue"
    assert owner_action.get("lane") == "owner_action_center"
    assert owner_action.get("priority_hint") == "top_owner_command"

    assert unified.get("ok") is True
    assert unified.get("status") == "passed"
    assert unified.get("readiness_score") == 100

    route_report = build_ob_route_coverage_report(write_panel=True)
    checkpoint = build_object_permission_integration_checkpoint(write_panel=True)

    show("PACK 137 FINAL HEALTH", {
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
        PROJECT_ROOT / "tower" / "test_tower_pack_137.py",
        PROJECT_ROOT / "tower" / "owner_action_center.py",
        PROJECT_ROOT / "tower" / "security_command_owner_quick_actions.py",
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
        "pack": "137",
        "status": "passed",
        "readiness_score": 100,
        "action_count": status.get("action_count"),
        "open_action_count": status.get("open_action_count"),
        "lane_count": lane_summary.get("lane_count"),
        "top_lane": lane_summary.get("top_lane", {}).get("lane"),
        "top_action_type": status.get("top_action", {}).get("action_type"),
        "top_recommended_action": status.get("top_action", {}).get("recommended_action"),
        "quick_action_count": quick.get("action_count"),
        "route_coverage_pct": route_report.get("coverage_pct"),
        "guarded_needed_count": route_report.get("guarded_needed_count"),
        "needs_guard_count": route_report.get("needs_guard_count"),
        "helper_wrapped_count": checkpoint.get("helper_wrapped_count"),
        "human_reason": "Owner Action Center quick-action/status polish is working.",
    }
    show("PACK 137 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
