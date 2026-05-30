
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


def run_fast(label: str, code: str, timeout: int = 15):
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
    from tower.owner_action_review_checkpoint import build_owner_action_review_checkpoint
    from tower.owner_action_review_dashboard_cards import (
        OWNER_ACTION_REVIEW_DASHBOARD_CARDS_PANEL_PATH,
        OWNER_ACTION_REVIEW_DASHBOARD_CARDS_STATUS_PATH,
        build_owner_action_review_dashboard_cards,
        load_owner_action_review_dashboard_cards_status,
        owner_action_review_dashboard_cards_status_card,
        render_owner_action_review_dashboard_cards_section,
        reset_owner_action_review_dashboard_cards_for_test,
        write_owner_action_review_dashboard_cards_panel,
    )
    from tower.security_command_unified_owner_page import (
        render_unified_owner_security_command_html,
        write_unified_owner_security_command_html,
    )
    from tower.ob_route_coverage_report import build_ob_route_coverage_report
    from tower.ob_object_permission_integration_checkpoint import build_object_permission_integration_checkpoint

    reset = reset_owner_action_review_dashboard_cards_for_test()
    show("RESET PACK 147 DASHBOARD CARDS", reset)
    assert reset.get("ok") is True

    checkpoint = build_owner_action_review_checkpoint(write_panel=True)
    assert checkpoint.get("ok") is True
    assert checkpoint.get("status") == "passed"
    assert checkpoint.get("review_depth", {}).get("score") == 100

    run_fast(
        "FAST PACK 147 DASHBOARD CARDS",
        "from tower.owner_action_review_dashboard_cards import build_owner_action_review_dashboard_cards; "
        "s=build_owner_action_review_dashboard_cards(write_panel=False); "
        "print(s.get('status'), s.get('pack'), s.get('card_count'), s.get('readiness_score'))",
        timeout=15,
    )

    run_fast(
        "FAST PACK 147 UNIFIED HTML",
        "from tower.security_command_unified_owner_page import render_unified_owner_security_command_html; "
        "h=render_unified_owner_security_command_html(); "
        "print(len(h), 'PACK147_UNIFIED_OWNER_PAGE_INCLUDES_OWNER_ACTION_REVIEW_DASHBOARD_CARDS' in h, 'PACK147_OWNER_ACTION_REVIEW_DASHBOARD_CARDS_SECTION' in h)",
        timeout=25,
    )

    dashboard = build_owner_action_review_dashboard_cards(write_panel=True)
    card = owner_action_review_dashboard_cards_status_card()
    loaded = load_owner_action_review_dashboard_cards_status()
    section = render_owner_action_review_dashboard_cards_section(dashboard)
    panel = write_owner_action_review_dashboard_cards_panel(dashboard)

    unified_html = render_unified_owner_security_command_html()
    unified_write = write_unified_owner_security_command_html()

    cards = dashboard.get("cards", []) if isinstance(dashboard.get("cards"), list) else []
    card_ids = {card.get("card_id") for card in cards if isinstance(card, dict)}

    show("PACK 147 DASHBOARD STATUS", {
        "ok": dashboard.get("ok"),
        "pack": dashboard.get("pack"),
        "status": dashboard.get("status"),
        "readiness_score": dashboard.get("readiness_score"),
        "card_count": dashboard.get("card_count"),
        "summary": dashboard.get("summary"),
        "failed_checks": dashboard.get("failed_checks"),
        "no_secret_leakage": dashboard.get("no_secret_leakage"),
    })

    show("PACK 147 DASHBOARD CARD", card)

    show("PACK 147 CARD IDS", {
        "card_ids": sorted(card_ids),
    })

    show("PACK 147 SECTION CHECK", {
        "html_length": len(section),
        "has_marker": "PACK147_OWNER_ACTION_REVIEW_DASHBOARD_CARDS_SECTION" in section,
        "has_title": "Owner Action Review Dashboard Cards" in section,
        "has_review_health": "Review Health" in section,
        "has_route_wall": "Route Wall" in section,
    })

    show("PACK 147 PANEL WRITE", panel)

    show("PACK 147 UNIFIED HTML CHECK", {
        "html_length": len(unified_html),
        "has_pack147_marker": "PACK147_UNIFIED_OWNER_PAGE_INCLUDES_OWNER_ACTION_REVIEW_DASHBOARD_CARDS" in unified_html,
        "has_pack147_section": "PACK147_OWNER_ACTION_REVIEW_DASHBOARD_CARDS_SECTION" in unified_html,
        "has_pack145_section": "PACK145_OWNER_ACTION_REVIEW_CHECKPOINT_SECTION" in unified_html,
        "has_title": "Owner Action Review Dashboard Cards" in unified_html,
    })

    show("PACK 147 WRITE UNIFIED HTML", unified_write)

    assert dashboard.get("ok") is True
    assert dashboard.get("pack") == "147"
    assert dashboard.get("status") == "passed"
    assert dashboard.get("readiness_score") == 100
    assert dashboard.get("card_count") == 7
    assert dashboard.get("failed_checks") == []
    assert dashboard.get("no_secret_leakage") is True

    required_cards = {
        "review_health",
        "action_state",
        "state_receipts",
        "notes",
        "assignments",
        "route_wall",
        "object_checkpoint",
    }
    assert required_cards.issubset(card_ids)

    summary = dashboard.get("summary", {})
    assert summary.get("review_depth_score") == 100
    assert summary.get("route_coverage_pct") == 100
    assert summary.get("helper_wrapped_count") == 0
    assert summary.get("tracked_action_count", 0) >= 1
    assert summary.get("state_receipt_count", 0) >= 1
    assert summary.get("note_count", 0) >= 1
    assert summary.get("assignment_count", 0) >= 1

    assert card.get("ok") is True
    assert card.get("pack") == "147"
    assert card.get("readiness_score") == 100
    assert card.get("card_count") == 7
    assert card.get("review_depth_score") == 100
    assert card.get("route_coverage_pct") == 100
    assert card.get("helper_wrapped_count") == 0

    assert loaded.get("ok") is True
    assert loaded.get("status") == "passed"
    assert loaded.get("card_count") == 7

    assert OWNER_ACTION_REVIEW_DASHBOARD_CARDS_STATUS_PATH.exists()
    assert OWNER_ACTION_REVIEW_DASHBOARD_CARDS_PANEL_PATH.exists()

    assert "PACK147_OWNER_ACTION_REVIEW_DASHBOARD_CARDS_SECTION" in section
    assert "Owner Action Review Dashboard Cards" in section
    assert "Review Health" in section
    assert "Route Wall" in section
    assert "SHOULD_NOT_SURVIVE" not in section
    assert "tower_keycard=" not in section

    assert panel.get("ok") is True
    assert panel.get("pack") == "147"

    assert "PACK147_UNIFIED_OWNER_PAGE_INCLUDES_OWNER_ACTION_REVIEW_DASHBOARD_CARDS" in unified_html
    assert "PACK147_OWNER_ACTION_REVIEW_DASHBOARD_CARDS_SECTION" in unified_html
    assert "PACK145_OWNER_ACTION_REVIEW_CHECKPOINT_SECTION" in unified_html
    assert "Owner Action Review Dashboard Cards" in unified_html
    assert "SHOULD_NOT_SURVIVE" not in unified_html
    assert "tower_keycard=" not in unified_html

    assert unified_write.get("ok") is True
    assert unified_write.get("pack") == "147"
    assert unified_write.get("html_length", 0) > 1000

    no_secret(dashboard)
    no_secret(card)
    no_secret(loaded)

    route_report = build_ob_route_coverage_report(write_panel=True)
    object_checkpoint = build_object_permission_integration_checkpoint(write_panel=True)

    show("PACK 147 FINAL HEALTH", {
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
        "pack147_route_marker": "PACK147_OWNER_ACTION_REVIEW_DASHBOARD_CARDS_ROUTE" in app_text,
        "pack147_route_path": "/tower/owner-action-review-dashboard-cards.json" in app_text,
        "pack147_route_guard": "pack147_owner_action_review_dashboard_cards_route" in app_text,
    }
    show("PACK 147 WEB APP ROUTE CHECKS", route_checks)
    assert all(route_checks.values())

    for path in [
        PROJECT_ROOT / "tower" / "owner_action_review_dashboard_cards.py",
        PROJECT_ROOT / "tower" / "security_command_unified_owner_page.py",
        PROJECT_ROOT / "tower" / "test_tower_pack_147.py",
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
        "pack": "147",
        "status": "passed",
        "readiness_score": 100,
        "card_count": dashboard.get("card_count"),
        "review_depth_score": summary.get("review_depth_score"),
        "tracked_action_count": summary.get("tracked_action_count"),
        "state_receipt_count": summary.get("state_receipt_count"),
        "note_count": summary.get("note_count"),
        "assignment_count": summary.get("assignment_count"),
        "route_coverage_pct": route_report.get("coverage_pct"),
        "guarded_needed_count": route_report.get("guarded_needed_count"),
        "needs_guard_count": route_report.get("needs_guard_count"),
        "helper_wrapped_count": object_checkpoint.get("helper_wrapped_count"),
        "human_reason": "Owner Action review dashboard cards are working.",
    }
    show("PACK 147 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
