
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


def run_fast_status(label: str, code: str, timeout: int = 20):
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
    return result.stdout


def run_tests():
    from tower.owner_action_center import build_owner_action_center_status
    from tower.security_watch_owner_posture import build_security_watch_owner_posture
    from tower.security_watch_checkpoint import build_security_watch_checkpoint
    from tower.security_command_owner_quick_actions import build_owner_quick_actions_status
    from tower.security_command_unified_owner_page import (
        build_unified_owner_security_command_status,
        render_unified_owner_security_command_html,
        write_unified_owner_security_command_html,
    )
    from tower.ob_route_coverage_report import build_ob_route_coverage_report
    from tower.ob_object_permission_integration_checkpoint import build_object_permission_integration_checkpoint

    run_fast_status(
        "FAST OWNER ACTION CENTER CHECK",
        "from tower.owner_action_center import build_owner_action_center_status; "
        "s=build_owner_action_center_status(write_panel=False); "
        "print(s.get('status'), s.get('pack'), s.get('readiness_score'), s.get('action_count'))",
        timeout=10,
    )

    run_fast_status(
        "FAST SECURITY WATCH CHECK",
        "from tower.security_watch_owner_posture import build_security_watch_owner_posture; "
        "s=build_security_watch_owner_posture(write_panel=False); "
        "print(s.get('status'), s.get('pack'), s.get('readiness_score'))",
        timeout=10,
    )

    run_fast_status(
        "FAST WATCH CHECKPOINT CHECK",
        "from tower.security_watch_checkpoint import build_security_watch_checkpoint; "
        "s=build_security_watch_checkpoint(write_panel=False); "
        "print(s.get('status'), s.get('pack'), s.get('readiness_score'))",
        timeout=10,
    )

    action_center = build_owner_action_center_status(write_panel=True)
    watch = build_security_watch_owner_posture(write_panel=True)
    watch_checkpoint = build_security_watch_checkpoint(write_panel=True)
    quick_status = build_owner_quick_actions_status(write_panel=True)
    unified = build_unified_owner_security_command_status(write_html=True)

    show("PACK 136 ACTION CENTER STATUS", {
        "ok": action_center.get("ok"),
        "pack": action_center.get("pack"),
        "status": action_center.get("status"),
        "readiness_score": action_center.get("readiness_score"),
        "action_count": action_center.get("action_count"),
        "open_action_count": action_center.get("open_action_count"),
        "top_action": action_center.get("top_action"),
        "failed_checks": action_center.get("failed_checks"),
        "no_secret_leakage": action_center.get("no_secret_leakage"),
    })

    show("PACK 136 QUICK ACTION STATUS", {
        "ok": quick_status.get("ok"),
        "status": quick_status.get("status"),
        "action_count": quick_status.get("action_count"),
        "readiness_score": quick_status.get("readiness_score"),
    })

    show("PACK 136 UNIFIED STATUS", {
        "ok": unified.get("ok"),
        "status": unified.get("status"),
        "readiness_score": unified.get("readiness_score"),
        "failed_checks": unified.get("failed_checks"),
    })

    assert action_center.get("ok") is True
    assert action_center.get("status") == "passed"
    assert action_center.get("readiness_score") == 100
    assert action_center.get("action_count", 0) >= 3
    assert action_center.get("top_action", {}).get("action_id")

    assert watch.get("ok") is True
    assert watch.get("status") == "passed"
    assert watch.get("readiness_score") == 100

    assert watch_checkpoint.get("ok") is True
    assert watch_checkpoint.get("status") == "passed"
    assert watch_checkpoint.get("readiness_score") == 100

    assert quick_status.get("ok") is True
    assert quick_status.get("status") == "passed"
    assert quick_status.get("readiness_score") == 100
    assert quick_status.get("action_count", 0) >= 17

    hrefs = {action.get("href") for action in quick_status.get("actions", []) if isinstance(action, dict)}
    assert "/tower/owner-action-center.json" in hrefs
    assert "/tower/security-watch.json" in hrefs
    assert "/tower/security-watch-checkpoint.json" in hrefs

    assert unified.get("ok") is True
    assert unified.get("status") == "passed"
    assert unified.get("readiness_score") == 100

    no_secret(action_center)
    no_secret(watch)
    no_secret(watch_checkpoint)
    no_secret(quick_status)
    no_secret(unified)

    unified_html = render_unified_owner_security_command_html(unified)

    show("PACK 136 UNIFIED HTML CHECK", {
        "html_length": len(unified_html),
        "has_pack136": "PACK136_UNIFIED_OWNER_PAGE_INCLUDES_OWNER_ACTION_CENTER" in unified_html,
        "has_pack135": "PACK135_OWNER_ACTION_CENTER_SECTION" in unified_html,
        "has_pack134": "PACK134_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_WATCH_CHECKPOINT" in unified_html,
        "has_pack133": "PACK133_SECURITY_WATCH_CHECKPOINT_SECTION" in unified_html,
        "has_pack132": "PACK132_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_WATCH" in unified_html,
        "has_pack131": "PACK131_SECURITY_WATCH_OWNER_POSTURE_SECTION" in unified_html,
        "has_owner_action_link": "/tower/owner-action-center.json" in unified_html,
    })

    assert "PACK136_UNIFIED_OWNER_PAGE_INCLUDES_OWNER_ACTION_CENTER" in unified_html
    assert "PACK135_OWNER_ACTION_CENTER_SECTION" in unified_html
    assert "PACK134_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_WATCH_CHECKPOINT" in unified_html
    assert "PACK133_SECURITY_WATCH_CHECKPOINT_SECTION" in unified_html
    assert "PACK132_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_WATCH" in unified_html
    assert "PACK131_SECURITY_WATCH_OWNER_POSTURE_SECTION" in unified_html
    assert "/tower/owner-action-center.json" in unified_html
    assert "SHOULD_NOT_SURVIVE" not in unified_html
    assert "tower_keycard=" not in unified_html

    write_result = write_unified_owner_security_command_html(unified)
    show("PACK 136 WRITE UNIFIED HTML", write_result)
    assert write_result.get("ok") is True

    from tower.tower_status import pack136_owner_action_center_status_bridge
    from tower.security_command_page import pack136_owner_action_center_html_section

    action_bridge = pack136_owner_action_center_status_bridge()
    action_html = pack136_owner_action_center_html_section()

    show("PACK 136 BRIDGE CHECKS", {
        "action_bridge_ok": action_bridge.get("ok"),
        "action_bridge_pack": action_bridge.get("pack"),
        "action_html_marker": "PACK135_OWNER_ACTION_CENTER_SECTION" in action_html,
    })

    assert action_bridge.get("ok") is True
    assert action_bridge.get("pack") == "135"
    assert "PACK135_OWNER_ACTION_CENTER_SECTION" in action_html
    assert "SHOULD_NOT_SURVIVE" not in action_html

    route_report = build_ob_route_coverage_report(write_panel=True)
    checkpoint = build_object_permission_integration_checkpoint(write_panel=True)

    show("PACK 136 FINAL HEALTH", {
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
        PROJECT_ROOT / "tower" / "test_tower_pack_136.py",
        PROJECT_ROOT / "tower" / "owner_action_center.py",
        PROJECT_ROOT / "tower" / "security_watch_checkpoint.py",
        PROJECT_ROOT / "tower" / "security_watch_owner_posture.py",
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
        "pack": "136",
        "status": "passed",
        "quick_action_count": quick_status.get("action_count"),
        "action_count": action_center.get("action_count"),
        "open_action_count": action_center.get("open_action_count"),
        "top_action_type": action_center.get("top_action", {}).get("action_type"),
        "top_recommended_action": action_center.get("top_action", {}).get("recommended_action"),
        "route_coverage_pct": route_report.get("coverage_pct"),
        "guarded_needed_count": route_report.get("guarded_needed_count"),
        "needs_guard_count": route_report.get("needs_guard_count"),
        "helper_wrapped_count": checkpoint.get("helper_wrapped_count"),
        "human_reason": "Owner Action Center is integrated into unified Security Command UI.",
    }
    show("PACK 136 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
