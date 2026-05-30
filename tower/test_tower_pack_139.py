
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
        build_owner_action_detail_status,
        build_owner_action_filters_status,
        render_owner_action_detail_section,
        write_owner_action_detail_panel,
    )
    from tower.tower_status import pack139_owner_action_detail_status_bridge
    from tower.ob_route_coverage_report import build_ob_route_coverage_report
    from tower.ob_object_permission_integration_checkpoint import build_object_permission_integration_checkpoint

    run_fast(
        "FAST OWNER ACTION DETAIL",
        "from tower.owner_action_center import build_owner_action_detail_status; "
        "s=build_owner_action_detail_status(write_panel=False); "
        "print(s.get('status'), s.get('pack'), s.get('detail', {}).get('action_type'))",
    )

    action_center = build_owner_action_center_status(write_panel=True)
    all_filters = build_owner_action_filters_status(write_panel=True)

    top_action = action_center.get("top_action", {}) if isinstance(action_center.get("top_action"), dict) else {}
    top_action_id = top_action.get("action_id", "")

    assert top_action_id

    detail = build_owner_action_detail_status(action_id=top_action_id, write_panel=True)
    fallback_detail = build_owner_action_detail_status(action_id="", write_panel=False)
    missing_detail = build_owner_action_detail_status(action_id="missing_owner_action_139", write_panel=False)
    bridge = pack139_owner_action_detail_status_bridge(top_action_id)

    show("PACK 139 ACTION CENTER STATUS", {
        "ok": action_center.get("ok"),
        "status": action_center.get("status"),
        "readiness_score": action_center.get("readiness_score"),
        "action_count": action_center.get("action_count"),
        "top_action": top_action,
    })

    show("PACK 139 DETAIL", {
        "ok": detail.get("ok"),
        "status": detail.get("status"),
        "pack": detail.get("pack"),
        "requested_action_id": detail.get("requested_action_id"),
        "found_action_id": detail.get("found_action_id"),
        "detail": detail.get("detail"),
        "no_secret_leakage": detail.get("no_secret_leakage"),
    })

    show("PACK 139 FALLBACK DETAIL", {
        "ok": fallback_detail.get("ok"),
        "status": fallback_detail.get("status"),
        "found_action_id": fallback_detail.get("found_action_id"),
        "detail": fallback_detail.get("detail"),
    })

    show("PACK 139 MISSING DETAIL", {
        "ok": missing_detail.get("ok"),
        "status": missing_detail.get("status"),
        "requested_action_id": missing_detail.get("requested_action_id"),
        "found_action_id": missing_detail.get("found_action_id"),
        "readiness_score": missing_detail.get("readiness_score"),
    })

    show("PACK 139 BRIDGE", {
        "ok": bridge.get("ok"),
        "status": bridge.get("status"),
        "pack": bridge.get("pack"),
        "found_action_id": bridge.get("found_action_id"),
        "detail": bridge.get("detail"),
    })

    assert action_center.get("ok") is True
    assert action_center.get("status") == "passed"
    assert action_center.get("action_count", 0) >= 3

    assert all_filters.get("ok") is True
    assert all_filters.get("status") == "passed"
    assert all_filters.get("filtered_action_count", 0) >= 3

    assert detail.get("ok") is True
    assert detail.get("status") == "passed"
    assert detail.get("pack") == "139"
    assert detail.get("requested_action_id") == top_action_id
    assert detail.get("found_action_id") == top_action_id
    assert detail.get("detail", {}).get("action_id") == top_action_id
    assert detail.get("detail", {}).get("title")
    assert detail.get("detail", {}).get("lane") in {
        "incident",
        "inbox",
        "route",
        "watch",
        "monitor",
        "command",
    }
    assert detail.get("detail", {}).get("lane_label")
    assert detail.get("detail", {}).get("source_label")
    assert detail.get("detail", {}).get("recommended_action")
    assert detail.get("detail", {}).get("href")
    assert detail.get("no_secret_leakage") is True

    assert fallback_detail.get("ok") is True
    assert fallback_detail.get("status") == "passed"
    assert fallback_detail.get("found_action_id")

    assert missing_detail.get("ok") is False
    assert missing_detail.get("status") == "not_found"
    assert missing_detail.get("readiness_score") == 80

    assert bridge.get("ok") is True
    assert bridge.get("status") == "passed"
    assert bridge.get("pack") == "139"
    assert bridge.get("found_action_id") == top_action_id

    no_secret(detail)
    no_secret(fallback_detail)
    no_secret(missing_detail)
    no_secret(bridge)

    section = render_owner_action_detail_section(detail)
    show("PACK 139 DETAIL HTML CHECK", {
        "html_length": len(section),
        "has_marker": "PACK139_OWNER_ACTION_DETAIL_SECTION" in section,
        "has_title": detail.get("detail", {}).get("title") in section,
        "has_recommended_move": "Recommended move" in section,
        "has_open_source": "Open source" in section,
    })

    assert "PACK139_OWNER_ACTION_DETAIL_SECTION" in section
    assert "Recommended move" in section
    assert "Open source" in section
    assert "SHOULD_NOT_SURVIVE" not in section
    assert "tower_keycard=" not in section

    panel = write_owner_action_detail_panel(detail)
    show("PACK 139 PANEL WRITE", panel)
    assert panel.get("ok") is True

    route_report = build_ob_route_coverage_report(write_panel=True)
    checkpoint = build_object_permission_integration_checkpoint(write_panel=True)

    show("PACK 139 FINAL HEALTH", {
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
        "pack139_route_marker": "PACK139_OWNER_ACTION_DETAIL_ROUTE" in app_text,
        "pack139_route_path": "/tower/owner-action-detail.json" in app_text,
        "pack139_route_guard": "pack139_owner_action_detail_route" in app_text,
    }
    show("PACK 139 WEB APP ROUTE CHECKS", route_checks)
    assert all(route_checks.values())

    for path in [
        PROJECT_ROOT / "tower" / "test_tower_pack_139.py",
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
        "pack": "139",
        "status": "passed",
        "readiness_score": 100,
        "base_action_count": action_center.get("action_count"),
        "top_action_type": top_action.get("action_type"),
        "detail_action_type": detail.get("detail", {}).get("action_type"),
        "detail_lane": detail.get("detail", {}).get("lane"),
        "detail_source_label": detail.get("detail", {}).get("source_label"),
        "route_coverage_pct": route_report.get("coverage_pct"),
        "guarded_needed_count": route_report.get("guarded_needed_count"),
        "needs_guard_count": route_report.get("needs_guard_count"),
        "helper_wrapped_count": checkpoint.get("helper_wrapped_count"),
        "human_reason": "Owner Action Center detail cards are working.",
    }
    show("PACK 139 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
