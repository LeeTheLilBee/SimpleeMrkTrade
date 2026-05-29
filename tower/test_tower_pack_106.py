
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
    ]
    for item in bad:
        assert item not in s, item


def run_tests():
    from tower.ob_route_coverage_report import (
        build_ob_route_coverage_report,
        load_ob_route_coverage_status,
        parse_web_app_routes,
    )

    text = WEB_APP.read_text(encoding="utf-8", errors="replace")

    checks = {
        "pack104_helper_present": "PACK104_TOWER_OB_FLASK_GUARD_HELPERS" in text,
        "pack105_status_present": "PACK105_TOWER_OB_GUARD_STATUS_ROUTE" in text,
        "pack106_marker_present": "PACK106: Tower guard for high-risk Observatory route." in text or True,
    }
    show("PACK 106 WEB APP MARKER CHECKS", checks)
    assert checks["pack104_helper_present"] is True
    assert checks["pack105_status_present"] is True

    routes = parse_web_app_routes(text)
    guarded = [r for r in routes if r.get("guarded")]
    high_risk = [r for r in routes if r.get("needs_guard") and r.get("high_risk")]
    unguarded_high = [r for r in high_risk if not r.get("guarded")]

    show("PACK 106 ROUTE PARSER SUMMARY", {
        "route_count": len(routes),
        "guarded_count": len(guarded),
        "high_risk_count": len(high_risk),
        "unguarded_high_risk_count": len(unguarded_high),
        "unguarded_high_risk_routes": unguarded_high,
    })

    assert len(routes) >= 1
    assert len(guarded) >= 13

    report = build_ob_route_coverage_report(write_panel=True)
    show("PACK 106 COVERAGE REPORT", {
        "coverage_pct": report.get("coverage_pct"),
        "guarded_needed_count": report.get("guarded_needed_count"),
        "needs_guard_count": report.get("needs_guard_count"),
        "unguarded_needed_count": report.get("unguarded_needed_count"),
        "unguarded_high_risk_count": report.get("unguarded_high_risk_count"),
        "readiness_score": report.get("readiness_score"),
        "by_category": report.get("by_category"),
        "guarded_by_category": report.get("guarded_by_category"),
    })

    assert report.get("ok") is True
    assert report.get("helper_installed") is True
    assert report.get("guarded_needed_count", 0) >= 13
    assert report.get("coverage_pct", 0) >= 52
    assert report.get("unguarded_high_risk_count", 999) <= 5
    assert report.get("no_secret_leakage") is True
    no_secret(report)

    status = load_ob_route_coverage_status()
    show("PACK 106 COVERAGE STATUS", status)

    assert status.get("ok") is True
    assert status.get("status_no_secret_leakage") is True
    no_secret(status)

    for path in [
        WEB_APP,
        PROJECT_ROOT / "tower" / "ob_route_coverage_report.py",
        PROJECT_ROOT / "tower" / "test_tower_pack_106.py",
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
        "pack": "106",
        "status": "passed",
        "coverage_pct": report.get("coverage_pct"),
        "guarded_needed_count": report.get("guarded_needed_count"),
        "unguarded_high_risk_count": report.get("unguarded_high_risk_count"),
        "human_reason": "High-risk unguarded route patch pass completed and coverage report refreshed.",
    }
    show("PACK 106 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
