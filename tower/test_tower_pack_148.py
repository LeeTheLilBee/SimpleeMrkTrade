
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
    from tower.owner_action_review_dashboard_cards import build_owner_action_review_dashboard_cards
    from tower.owner_action_review_compact_card import (
        OWNER_ACTION_REVIEW_COMPACT_CARD_PANEL_PATH,
        OWNER_ACTION_REVIEW_COMPACT_CARD_STATUS_PATH,
        build_owner_action_review_compact_card,
        load_owner_action_review_compact_card_status,
        owner_action_review_compact_card_status_card,
        render_owner_action_review_compact_card_section,
        reset_owner_action_review_compact_card_for_test,
        write_owner_action_review_compact_card_panel,
    )
    from tower.security_command_owner_quick_actions import build_owner_quick_actions_status
    from tower.security_command_unified_owner_page import (
        render_unified_owner_security_command_html,
        write_unified_owner_security_command_html,
    )
    from tower.tower_status import pack148_owner_action_review_compact_card_status_bridge
    from tower.ob_route_coverage_report import build_ob_route_coverage_report
    from tower.ob_object_permission_integration_checkpoint import build_object_permission_integration_checkpoint

    reset = reset_owner_action_review_compact_card_for_test()
    show("RESET PACK 148 COMPACT CARD", reset)
    assert reset.get("ok") is True

    dashboard = build_owner_action_review_dashboard_cards(write_panel=True)
    assert dashboard.get("ok") is True
    assert dashboard.get("status") == "passed"
    assert dashboard.get("card_count") == 7

    run_fast(
        "FAST PACK 148 COMPACT CARD",
        "from tower.owner_action_review_compact_card import build_owner_action_review_compact_card; "
        "s=build_owner_action_review_compact_card(write_panel=False); "
        "print(s.get('status'), s.get('pack'), s.get('compact_status'), s.get('readiness_score'))",
        timeout=15,
    )

    run_fast(
        "FAST PACK 148 QUICK ACTIONS",
        "from tower.security_command_owner_quick_actions import build_owner_quick_actions_status; "
        "s=build_owner_quick_actions_status(write_panel=False); "
        "print(s.get('status'), s.get('action_count'), s.get('pack148_owner_action_dashboard_link_present'), s.get('pack148_compact_card_link_present'))",
        timeout=15,
    )

    run_fast(
        "FAST PACK 148 UNIFIED HTML",
        "from tower.security_command_unified_owner_page import render_unified_owner_security_command_html; "
        "h=render_unified_owner_security_command_html(); "
        "print(len(h), 'PACK148_UNIFIED_OWNER_PAGE_INCLUDES_COMPACT_OWNER_ACTION_REVIEW_CARD' in h, 'PACK148_OWNER_ACTION_REVIEW_COMPACT_CARD_SECTION' in h)",
        timeout=25,
    )

    compact = build_owner_action_review_compact_card(write_panel=True)
    card = owner_action_review_compact_card_status_card()
    bridge = pack148_owner_action_review_compact_card_status_bridge()
    loaded = load_owner_action_review_compact_card_status()
    section = render_owner_action_review_compact_card_section(compact)
    panel = write_owner_action_review_compact_card_panel(compact)

    quick = build_owner_quick_actions_status(write_panel=True)
    actions = quick.get("actions", []) if isinstance(quick.get("actions"), list) else []
    action_ids = {action.get("action_id") for action in actions if isinstance(action, dict)}
    hrefs = {action.get("href") for action in actions if isinstance(action, dict)}

    unified_html = render_unified_owner_security_command_html()
    unified_write = write_unified_owner_security_command_html()

    show("PACK 148 COMPACT STATUS", {
        "ok": compact.get("ok"),
        "pack": compact.get("pack"),
        "status": compact.get("status"),
        "readiness_score": compact.get("readiness_score"),
        "compact_status": compact.get("compact_status"),
        "compact_label": compact.get("compact_label"),
        "recommended_action": compact.get("recommended_action"),
        "metrics": compact.get("metrics"),
        "failed_checks": compact.get("failed_checks"),
        "no_secret_leakage": compact.get("no_secret_leakage"),
    })

    show("PACK 148 STATUS CARD", card)
    show("PACK 148 TOWER STATUS BRIDGE", bridge)

    show("PACK 148 QUICK ACTIONS", {
        "ok": quick.get("ok"),
        "status": quick.get("status"),
        "action_count": quick.get("action_count"),
        "has_dashboard_action": "review_owner_action_review_dashboard_cards" in action_ids,
        "has_compact_action": "review_owner_action_compact_card" in action_ids,
        "has_dashboard_href": "/tower/owner-action-review-dashboard-cards.json" in hrefs,
        "has_compact_href": "/tower/owner-action-review-compact-card.json" in hrefs,
        "pack148_marker": quick.get("pack148_marker"),
        "no_secret_leakage": quick.get("no_secret_leakage"),
    })

    show("PACK 148 SECTION CHECK", {
        "html_length": len(section),
        "has_marker": "PACK148_OWNER_ACTION_REVIEW_COMPACT_CARD_SECTION" in section,
        "has_title": "COMPACT OWNER ACTION REVIEW" in section or "Compact Owner Action Review" in section,
        "has_dashboard_link": "/tower/owner-action-review-dashboard-cards.json" in section,
    })

    show("PACK 148 PANEL WRITE", panel)

    show("PACK 148 UNIFIED HTML CHECK", {
        "html_length": len(unified_html),
        "has_pack148_marker": "PACK148_UNIFIED_OWNER_PAGE_INCLUDES_COMPACT_OWNER_ACTION_REVIEW_CARD" in unified_html,
        "has_pack148_section": "PACK148_OWNER_ACTION_REVIEW_COMPACT_CARD_SECTION" in unified_html,
        "has_pack147_section": "PACK147_OWNER_ACTION_REVIEW_DASHBOARD_CARDS_SECTION" in unified_html,
        "has_pack145_section": "PACK145_OWNER_ACTION_REVIEW_CHECKPOINT_SECTION" in unified_html,
    })

    show("PACK 148 WRITE UNIFIED HTML", unified_write)

    assert compact.get("ok") is True
    assert compact.get("pack") == "148"
    assert compact.get("status") == "passed"
    assert compact.get("readiness_score") == 100
    assert compact.get("compact_status") == "ready"
    assert compact.get("compact_label") == "Owner Review Ready"
    assert compact.get("recommended_action") == "review_dashboard_cards"
    assert compact.get("failed_checks") == []
    assert compact.get("no_secret_leakage") is True

    metrics = compact.get("metrics", {})
    assert metrics.get("card_count") == 7
    assert metrics.get("review_depth_score") == 100
    assert metrics.get("route_coverage_pct") == 100
    assert metrics.get("helper_wrapped_count") == 0

    assert card.get("ok") is True
    assert card.get("pack") == "148"
    assert card.get("readiness_score") == 100
    assert card.get("compact_status") == "ready"
    assert card.get("card_count") == 7

    assert bridge.get("ok") is True
    assert bridge.get("pack") == "148"
    assert bridge.get("readiness_score") == 100
    assert bridge.get("compact_status") == "ready"

    assert loaded.get("ok") is True
    assert loaded.get("status") == "passed"
    assert loaded.get("compact_status") == "ready"

    assert OWNER_ACTION_REVIEW_COMPACT_CARD_STATUS_PATH.exists()
    assert OWNER_ACTION_REVIEW_COMPACT_CARD_PANEL_PATH.exists()

    assert quick.get("ok") is True
    assert quick.get("status") == "passed"
    assert quick.get("pack148_owner_action_dashboard_link_present") is True
    assert quick.get("pack148_compact_card_link_present") is True
    assert quick.get("pack148_marker") == "PACK148_OWNER_ACTION_REVIEW_DASHBOARD_QUICK_LINK"
    assert "review_owner_action_review_dashboard_cards" in action_ids
    assert "review_owner_action_compact_card" in action_ids
    assert "/tower/owner-action-review-dashboard-cards.json" in hrefs
    assert "/tower/owner-action-review-compact-card.json" in hrefs
    assert quick.get("no_secret_leakage") is True

    assert "PACK148_OWNER_ACTION_REVIEW_COMPACT_CARD_SECTION" in section
    assert "/tower/owner-action-review-dashboard-cards.json" in section
    assert "SHOULD_NOT_SURVIVE" not in section
    assert "tower_keycard=" not in section

    assert panel.get("ok") is True
    assert panel.get("pack") == "148"

    assert "PACK148_UNIFIED_OWNER_PAGE_INCLUDES_COMPACT_OWNER_ACTION_REVIEW_CARD" in unified_html
    assert "PACK148_OWNER_ACTION_REVIEW_COMPACT_CARD_SECTION" in unified_html
    assert "PACK147_OWNER_ACTION_REVIEW_DASHBOARD_CARDS_SECTION" in unified_html
    assert "PACK145_OWNER_ACTION_REVIEW_CHECKPOINT_SECTION" in unified_html
    assert "SHOULD_NOT_SURVIVE" not in unified_html
    assert "tower_keycard=" not in unified_html

    assert unified_write.get("ok") is True
    assert unified_write.get("pack") == "148"
    assert unified_write.get("html_length", 0) > 1000

    no_secret(compact)
    no_secret(card)
    no_secret(bridge)
    no_secret(loaded)
    no_secret(quick)

    route_report = build_ob_route_coverage_report(write_panel=True)
    object_checkpoint = build_object_permission_integration_checkpoint(write_panel=True)

    show("PACK 148 FINAL HEALTH", {
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
        "pack148_route_marker": "PACK148_OWNER_ACTION_REVIEW_COMPACT_CARD_ROUTE" in app_text,
        "pack148_route_path": "/tower/owner-action-review-compact-card.json" in app_text,
        "pack148_route_guard": "pack148_owner_action_review_compact_card_route" in app_text,
        "pack147_route_still_present": "/tower/owner-action-review-dashboard-cards.json" in app_text,
    }
    show("PACK 148 WEB APP ROUTE CHECKS", route_checks)
    assert all(route_checks.values())

    for path in [
        PROJECT_ROOT / "tower" / "owner_action_review_compact_card.py",
        PROJECT_ROOT / "tower" / "security_command_owner_quick_actions.py",
        PROJECT_ROOT / "tower" / "security_command_unified_owner_page.py",
        PROJECT_ROOT / "tower" / "tower_status.py",
        PROJECT_ROOT / "tower" / "test_tower_pack_148.py",
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
        "pack": "148",
        "status": "passed",
        "readiness_score": 100,
        "compact_status": compact.get("compact_status"),
        "compact_label": compact.get("compact_label"),
        "quick_action_count": quick.get("action_count"),
        "dashboard_link_present": True,
        "compact_link_present": True,
        "card_count": metrics.get("card_count"),
        "review_depth_score": metrics.get("review_depth_score"),
        "route_coverage_pct": route_report.get("coverage_pct"),
        "guarded_needed_count": route_report.get("guarded_needed_count"),
        "needs_guard_count": route_report.get("needs_guard_count"),
        "helper_wrapped_count": object_checkpoint.get("helper_wrapped_count"),
        "human_reason": "Owner Action review compact card and quick links are working.",
    }
    show("PACK 148 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
