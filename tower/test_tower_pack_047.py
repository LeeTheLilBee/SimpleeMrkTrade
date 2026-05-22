
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path("/content/SimpleeMrkTrade_REAL_CLONE")
os.chdir(PROJECT_ROOT)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

for name in list(sys.modules.keys()):
    if name == "tower" or name.startswith("tower.") or name == "web.app":
        sys.modules.pop(name, None)

from web.app import app
from tower.ob_route_exposure_report import build_ob_route_exposure_report


def _print(title, payload=None):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def run_tests():
    report = build_ob_route_exposure_report(app=app)

    _print("REPORT SUMMARY", {
        "ok": report.get("ok"),
        "counts": report.get("counts"),
        "attention_count": report.get("attention_count"),
        "default_deny_active": report.get("default_deny_active"),
    })

    assert report.get("ok") is True
    counts = report.get("counts", {})
    assert counts.get("total", 0) >= 1
    assert report.get("default_deny_active") is True
    assert "Soulaana:" in report.get("soulaana_translation", "")

    categories = {item.get("category") for item in report.get("routes", [])}
    _print("CATEGORIES", sorted(categories))
    assert "tower_owned" in categories or counts.get("tower_owned", 0) >= 1
    assert "static_or_asset" in categories or counts.get("static_or_asset", 0) >= 1

    serialized = json.dumps(report, sort_keys=True, default=str)
    assert "tower_keycard=" not in serialized
    assert "raw_token" not in serialized

    final = {
        "pack": "047",
        "status": "passed",
        "human_reason": "OB route exposure report maps Flask routes into public-safe, Tower-owned, guarded, static, and unmapped default-deny categories.",
    }
    _print("PACK 047 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
