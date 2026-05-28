
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

from tower.ob_exposure_mapping import (
    build_ob_exposure_mapping_pass,
    summarize_ob_exposure_mapping_pass,
)
from tower.tower_status import get_tower_status
from tower.security_command_page import generate_security_command_dashboard


def _print(title, payload=None):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def run_tests():
    mapping = build_ob_exposure_mapping_pass()
    summary = summarize_ob_exposure_mapping_pass(limit=12)

    _print("EXPOSURE MAPPING SUMMARY", {
        "ok": summary.get("ok"),
        "total": summary.get("total"),
        "counts": summary.get("counts"),
        "reason_counts": summary.get("reason_counts"),
        "priority_counts": summary.get("priority_counts"),
        "readiness_label": summary.get("readiness_label"),
        "readiness_score": summary.get("readiness_score"),
        "top_next_count": len(summary.get("top_next", [])),
        "retire_or_redirect_count": len(summary.get("retire_or_redirect", [])),
        "later_review_count": len(summary.get("later_review", [])),
        "path": mapping.get("path"),
    })

    assert summary.get("ok") is True
    assert summary.get("total", 0) >= 1
    assert isinstance(summary.get("counts"), dict)
    assert sum(summary.get("counts", {}).values()) == summary.get("total")
    assert summary.get("readiness_score") == 100
    assert summary.get("readiness_label") == "Exposure mapping pass ready"

    status = get_tower_status()
    _print("TOWER STATUS EXPOSURE MAPPING FIELDS", {
        "ob_exposure_mapping_ok": status.get("ob_exposure_mapping_ok"),
        "ob_exposure_mapping_total": status.get("ob_exposure_mapping_total"),
        "ob_exposure_mapping_counts": status.get("ob_exposure_mapping_counts"),
        "ob_exposure_mapping_reason_counts": status.get("ob_exposure_mapping_reason_counts"),
        "ob_exposure_mapping_priority_counts": status.get("ob_exposure_mapping_priority_counts"),
        "ob_exposure_mapping_readiness_label": status.get("ob_exposure_mapping_readiness_label"),
        "ob_exposure_mapping_readiness_score": status.get("ob_exposure_mapping_readiness_score"),
    })

    assert status.get("ob_exposure_mapping_ok") is True
    assert status.get("ob_exposure_mapping_total", 0) >= summary.get("total", 0)
    assert isinstance(status.get("ob_exposure_mapping_counts"), dict)
    assert status.get("ob_exposure_mapping_readiness_score") == 100
    assert status.get("ob_exposure_mapping_readiness_label") == "Exposure mapping pass ready"

    dashboard = generate_security_command_dashboard()
    _print("SECURITY COMMAND DASHBOARD EXPOSURE MAPPING FIELDS", {
        "ok": dashboard.get("ok"),
        "path": dashboard.get("path"),
        "bytes": dashboard.get("bytes"),
        "ob_exposure_mapping_ok": dashboard.get("ob_exposure_mapping_ok"),
        "ob_exposure_mapping_total": dashboard.get("ob_exposure_mapping_total"),
        "ob_exposure_mapping_counts": dashboard.get("ob_exposure_mapping_counts"),
        "ob_exposure_mapping_top_next_count": dashboard.get("ob_exposure_mapping_top_next_count"),
        "ob_exposure_mapping_retire_or_redirect_count": dashboard.get("ob_exposure_mapping_retire_or_redirect_count"),
        "ob_exposure_mapping_later_review_count": dashboard.get("ob_exposure_mapping_later_review_count"),
    })

    assert dashboard.get("ok") is True
    assert dashboard.get("ob_exposure_mapping_ok") is True
    assert dashboard.get("ob_exposure_mapping_total", 0) >= summary.get("total", 0)

    html_path = Path(dashboard.get("path", ""))
    assert html_path.exists()
    dashboard_html = html_path.read_text(encoding="utf-8", errors="replace")

    assert "OB EXPOSURE MAPPING PASS" in dashboard_html
    assert "Route Exposure Door Map" in dashboard_html
    assert 'data-pack="087"' in dashboard_html
    assert "Total Routes" in dashboard_html
    assert "By Category" in dashboard_html
    assert "By Reason" in dashboard_html
    assert "By Priority" in dashboard_html
    assert "Map Next" in dashboard_html
    assert "Retire or Redirect" in dashboard_html
    assert "Later Review" in dashboard_html

    serialized = json.dumps([mapping, summary, status, dashboard], sort_keys=True, default=str) + dashboard_html
    assert "tower_keycard=" not in serialized
    assert "SHOULD_NOT_SURVIVE" not in serialized
    assert "raw_token=" not in serialized
    assert '"raw_token":' not in serialized
    assert "Bearer SHOULD_NOT_SURVIVE" not in serialized
    assert "Soulaana:" in serialized

    final = {
        "pack": "087",
        "status": "passed",
        "human_reason": "Exposure mapping pass now appears in Tower status and Security Command UI.",
    }
    _print("PACK 087 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
