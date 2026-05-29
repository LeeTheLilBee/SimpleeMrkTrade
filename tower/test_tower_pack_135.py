
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
    from tower.owner_action_center import (
        OWNER_ACTION_CENTER_PANEL_PATH,
        OWNER_ACTION_CENTER_STATUS_PATH,
        build_owner_action_center_status,
        load_owner_action_center_status,
        owner_action_center_status_card,
        render_owner_action_center_section,
        reset_owner_action_center_for_test,
        write_owner_action_center_panel,
    )
    from tower.security_watch_owner_posture import build_security_watch_owner_posture
    from tower.security_watch_checkpoint import build_security_watch_checkpoint
    from tower.ob_route_coverage_report import build_ob_route_coverage_report
    from tower.ob_object_permission_integration_checkpoint import build_object_permission_integration_checkpoint

    reset_action_center = reset_owner_action_center_for_test()
    show("RESET PACK 135 OWNER ACTION CENTER", reset_action_center)
    assert reset_action_center.get("ok") is True

    run_fast_status(
        "FAST WATCH CHECK",
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

    run_fast_status(
        "FAST OWNER ACTION CENTER CHECK",
        "from tower.owner_action_center import build_owner_action_center_status; "
        "s=build_owner_action_center_status(write_panel=False); "
        "print(s.get('status'), s.get('pack'), s.get('readiness_score'), s.get('action_count'))",
        timeout=10,
    )

    watch = build_security_watch_owner_posture(write_panel=True)
    checkpoint = build_security_watch_checkpoint(write_panel=True)
    action_center = build_owner_action_center_status(write_panel=True)

    show("PACK 135 WATCH STATUS", {
        "ok": watch.get("ok"),
        "pack": watch.get("pack"),
        "status": watch.get("status"),
        "readiness_score": watch.get("readiness_score"),
        "posture": watch.get("posture"),
        "failed_checks": watch.get("failed_checks"),
    })

    show("PACK 135 WATCH CHECKPOINT STATUS", {
        "ok": checkpoint.get("ok"),
        "pack": checkpoint.get("pack"),
        "status": checkpoint.get("status"),
        "readiness_score": checkpoint.get("readiness_score"),
        "security_watch": checkpoint.get("security_watch"),
        "failed_checks": checkpoint.get("failed_checks"),
    })

    show("PACK 135 ACTION CENTER STATUS", {
        "ok": action_center.get("ok"),
        "pack": action_center.get("pack"),
        "status": action_center.get("status"),
        "readiness_score": action_center.get("readiness_score"),
        "action_count": action_center.get("action_count"),
        "open_action_count": action_center.get("open_action_count"),
        "top_action": action_center.get("top_action"),
        "by_severity": action_center.get("by_severity"),
        "by_source": action_center.get("by_source"),
        "by_type": action_center.get("by_type"),
        "failed_checks": action_center.get("failed_checks"),
        "no_secret_leakage": action_center.get("no_secret_leakage"),
    })

    assert watch.get("ok") is True
    assert watch.get("status") == "passed"
    assert watch.get("readiness_score") == 100
    assert str(watch.get("pack", "")).endswith("135C") or "135C" in str(watch.get("pack", ""))

    assert checkpoint.get("ok") is True
    assert checkpoint.get("status") == "passed"
    assert checkpoint.get("readiness_score") == 100
    assert "135D" in str(checkpoint.get("pack", ""))

    assert action_center.get("ok") is True
    assert action_center.get("status") == "passed"
    assert action_center.get("readiness_score") == 100
    assert action_center.get("action_count", 0) >= 3
    assert action_center.get("open_action_count", 0) >= 3
    assert action_center.get("top_action", {}).get("action_id")
    assert action_center.get("top_action", {}).get("href")
    assert action_center.get("top_action", {}).get("recommended_action")
    assert action_center.get("failed_checks") == []
    assert action_center.get("route_health", {}).get("coverage_pct") == 100
    assert action_center.get("route_health", {}).get("unguarded_needed_count") == 0
    assert action_center.get("route_health", {}).get("unguarded_high_risk_count") == 0
    assert action_center.get("object_checkpoint", {}).get("helper_wrapped_count") == 0
    assert action_center.get("no_secret_leakage") is True
    assert OWNER_ACTION_CENTER_STATUS_PATH.exists()
    assert OWNER_ACTION_CENTER_PANEL_PATH.exists()

    no_secret(watch)
    no_secret(checkpoint)
    no_secret(action_center)

    actions = action_center.get("actions", [])
    assert isinstance(actions, list)
    assert any(action.get("action_type") == "recommended_first_action" for action in actions if isinstance(action, dict))
    assert any(action.get("action_type") == "monitor_route_health" for action in actions if isinstance(action, dict))
    assert any(action.get("href") == "/tower/security-watch-checkpoint.json" for action in actions if isinstance(action, dict))

    section = render_owner_action_center_section(action_center)
    show("PACK 135 ACTION CENTER HTML CHECK", {
        "html_length": len(section),
        "has_marker": "PACK135_OWNER_ACTION_CENTER_SECTION" in section,
        "has_title": "Owner Action Center" in section,
        "has_open_action": "Open action" in section,
        "has_total_actions": "Total Actions" in section,
    })

    assert "PACK135_OWNER_ACTION_CENTER_SECTION" in section
    assert "Owner Action Center" in section
    assert "Open action" in section
    assert "Total Actions" in section
    assert "SHOULD_NOT_SURVIVE" not in section
    assert "tower_keycard=" not in section

    panel = write_owner_action_center_panel(action_center)
    show("PACK 135 PANEL WRITE", panel)
    assert panel.get("ok") is True
    assert OWNER_ACTION_CENTER_PANEL_PATH.exists()

    card = owner_action_center_status_card()
    loaded = load_owner_action_center_status()

    show("PACK 135 STATUS CARD", card)
    show("PACK 135 LOADED STATUS", {
        "ok": loaded.get("ok"),
        "status": loaded.get("status"),
        "readiness_score": loaded.get("readiness_score"),
        "action_count": loaded.get("action_count"),
        "top_action_type": loaded.get("top_action", {}).get("action_type") if isinstance(loaded.get("top_action"), dict) else "",
    })

    assert card.get("ok") is True
    assert card.get("pack") == "135"
    assert card.get("readiness_score") == 100
    assert card.get("action_count", 0) >= 3
    assert loaded.get("ok") is True
    assert loaded.get("status") == "passed"
    assert loaded.get("readiness_score") == 100
    no_secret(card)
    no_secret(loaded)

    route_report = build_ob_route_coverage_report(write_panel=True)
    object_checkpoint = build_object_permission_integration_checkpoint(write_panel=True)

    show("PACK 135 FINAL HEALTH", {
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
    app_checks = {
        "pack135_route_marker": "PACK135_OWNER_ACTION_CENTER_ROUTE" in app_text,
        "pack135_route_path": "/tower/owner-action-center.json" in app_text,
        "pack135_route_guard": "pack135_owner_action_center_route" in app_text,
    }
    show("PACK 135 WEB APP ROUTE CHECKS", app_checks)
    assert all(app_checks.values())

    for path in [
        PROJECT_ROOT / "tower" / "owner_action_center.py",
        PROJECT_ROOT / "tower" / "test_tower_pack_135.py",
        PROJECT_ROOT / "tower" / "security_watch_checkpoint.py",
        PROJECT_ROOT / "tower" / "security_watch_owner_posture.py",
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
        "pack": "135+135D",
        "status": "passed",
        "readiness_score": action_center.get("readiness_score"),
        "action_count": action_center.get("action_count"),
        "open_action_count": action_center.get("open_action_count"),
        "top_action_type": action_center.get("top_action", {}).get("action_type"),
        "top_recommended_action": action_center.get("top_action", {}).get("recommended_action"),
        "posture": action_center.get("security_watch_summary", {}).get("posture"),
        "risk_points": action_center.get("security_watch_summary", {}).get("risk_points"),
        "route_coverage_pct": route_report.get("coverage_pct"),
        "guarded_needed_count": route_report.get("guarded_needed_count"),
        "needs_guard_count": route_report.get("needs_guard_count"),
        "helper_wrapped_count": object_checkpoint.get("helper_wrapped_count"),
        "human_reason": "Owner Action Center foundation is working from cached Tower posture without recursive builder calls.",
    }
    show("PACK 135 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
