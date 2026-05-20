
# =============================================================================
# THE TOWER PACK 018 TEST
# Security Command Dashboard
# =============================================================================

from __future__ import annotations

import json
from pathlib import Path

from tower.security_command_dashboard import (
    build_security_command_dashboard,
    get_security_command_cards,
    save_security_command_dashboard,
)


PROJECT_ROOT = Path("/content/SimpleeMrkTrade_REAL_CLONE")


def _print_header(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def main() -> None:
    print(PROJECT_ROOT)

    _print_header("BUILD SECURITY COMMAND DASHBOARD")
    dashboard = build_security_command_dashboard(limit_groups=10)

    compact = {
        "dashboard_name": dashboard.get("dashboard_name"),
        "health": dashboard.get("health"),
        "inbox_open": dashboard.get("inbox", {}).get("open"),
        "critical_alerts": next(
            (c.get("value") for c in dashboard.get("summary_cards", []) if c.get("card") == "Critical Alerts"),
            None,
        ),
        "high_alerts": next(
            (c.get("value") for c in dashboard.get("summary_cards", []) if c.get("card") == "High Alerts"),
            None,
        ),
        "evidence_open": dashboard.get("evidence_capsules", {}).get("open"),
        "step_up_pending": dashboard.get("step_up", {}).get("pending"),
        "review_group_count": len(dashboard.get("top_review_groups", [])),
    }

    print(json.dumps(compact, indent=2, sort_keys=True))

    _print_header("SUMMARY CARDS")
    print(json.dumps(dashboard.get("summary_cards", []), indent=2, sort_keys=True))

    _print_header("TOP REVIEW GROUPS")
    top_groups = dashboard.get("top_review_groups", [])[:5]
    printable_groups = []
    for group in top_groups:
        printable_groups.append(
            {
                "priority": group.get("priority"),
                "priority_score": group.get("priority_score"),
                "app_name": group.get("app_name"),
                "source_type": group.get("source_type"),
                "reason_code": group.get("reason_code"),
                "open_count": group.get("open_count"),
                "summary": group.get("summary"),
                "sample_item_ids": group.get("sample_item_ids"),
            }
        )
    print(json.dumps(printable_groups, indent=2, sort_keys=True))

    _print_header("RECOMMENDED OWNER FOCUS")
    print(json.dumps(dashboard.get("recommended_owner_focus", []), indent=2, sort_keys=True))

    _print_header("SAVE DASHBOARD JSON")
    saved = save_security_command_dashboard()
    print(json.dumps(
        {
            "ok": saved.get("ok"),
            "status": saved.get("status"),
            "path": saved.get("path"),
            "dashboard_name": saved.get("dashboard", {}).get("dashboard_name"),
        },
        indent=2,
        sort_keys=True,
    ))

    _print_header("DASHBOARD CARDS API SHAPE")
    cards = get_security_command_cards(limit_groups=5)
    print(json.dumps(cards, indent=2, sort_keys=True))

    _print_header("PACK 018 RESULT")
    assert dashboard.get("dashboard_name") == "The Tower Security Command Dashboard"
    assert "summary_cards" in dashboard
    assert "top_review_groups" in dashboard
    assert saved.get("ok") is True

    print(json.dumps(
        {
            "pack": "018",
            "status": "passed",
            "human_reason": "Security Command Dashboard generated dashboard-ready cards, grouped review queues, owner focus tasks, and saved JSON output.",
        },
        indent=2,
        sort_keys=True,
    ))


if __name__ == "__main__":
    main()
