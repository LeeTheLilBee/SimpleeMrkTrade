
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
    from tower.owner_action_review_focus_lanes import (
        OWNER_ACTION_REVIEW_FOCUS_LANES_PANEL_PATH,
        OWNER_ACTION_REVIEW_FOCUS_LANES_STATUS_PATH,
        build_owner_action_review_focus_lanes,
        load_owner_action_review_focus_lanes_status,
        owner_action_review_focus_lanes_status_card,
        render_owner_action_review_focus_lanes_section,
        reset_owner_action_review_focus_lanes_for_test,
        write_owner_action_review_focus_lanes_panel,
    )
    from tower.security_command_owner_quick_actions import build_owner_quick_actions_status
    from tower.security_command_unified_owner_page import (
        render_unified_owner_security_command_html,
        write_unified_owner_security_command_html,
    )
    from tower.tower_status import pack149_owner_action_review_focus_lanes_status_bridge
    from tower.ob_route_coverage_report import build_ob_route_coverage_report
    from tower.ob_object_permission_integration_checkpoint import build_object_permission_integration_checkpoint

    reset = reset_owner_action_review_focus_lanes_for_test()
    show("RESET PACK 149 FOCUS LANES", reset)
    assert reset.get("ok") is True

    dashboard = build_owner_action_review_dashboard_cards(write_panel=True)
    assert dashboard.get("ok") is True
    assert dashboard.get("card_count") == 7

    run_fast(
        "FAST PACK 149 FOCUS LANES",
        "from tower.owner_action_review_focus_lanes import build_owner_action_review_focus_lanes; "
        "s=build_owner_action_review_focus_lanes(lane='all', write_panel=False); "
        "print(s.get('status'), s.get('pack'), s.get('filtered_card_count'), s.get('readiness_score'))",
        timeout=15,
    )

    run_fast(
        "FAST PACK 149 QUICK ACTIONS",
        "from tower.security_command_owner_quick_actions import build_owner_quick_actions_status; "
        "s=build_owner_quick_actions_status(write_panel=False); "
        "print(s.get('status'), s.get('action_count'), s.get('pack149_focus_lanes_link_present'))",
        timeout=15,
    )

    run_fast(
        "FAST PACK 149 UNIFIED HTML",
        "from tower.security_command_unified_owner_page import render_unified_owner_security_command_html; "
        "h=render_unified_owner_security_command_html(); "
        "print(len(h), 'PACK149_UNIFIED_OWNER_PAGE_INCLUDES_OWNER_ACTION_REVIEW_FOCUS_LANES' in h, 'PACK149_OWNER_ACTION_REVIEW_FOCUS_LANES_SECTION' in h)",
        timeout=25,
    )

    all_lane = build_owner_action_review_focus_lanes(lane="all", write_panel=True)
    route_lane = build_owner_action_review_focus_lanes(lane="route", write_panel=False)
    notes_lane = build_owner_action_review_focus_lanes(lane="notes", write_panel=False)
    attention_lane = build_owner_action_review_focus_lanes(lane="attention", write_panel=False)
    card_filter = build_owner_action_review_focus_lanes(card_id="review_health", write_panel=False)
    severity_filter = build_owner_action_review_focus_lanes(severity="success", write_panel=False)
    status_filter = build_owner_action_review_focus_lanes(status="ready", write_panel=False)
    top_only = build_owner_action_review_focus_lanes(top_only=True, write_panel=False)

    card = owner_action_review_focus_lanes_status_card()
    bridge = pack149_owner_action_review_focus_lanes_status_bridge()
    loaded = load_owner_action_review_focus_lanes_status()
    section = render_owner_action_review_focus_lanes_section(all_lane)
    panel = write_owner_action_review_focus_lanes_panel(all_lane)

    quick = build_owner_quick_actions_status(write_panel=True)
    actions = quick.get("actions", []) if isinstance(quick.get("actions"), list) else []
    action_ids = {action.get("action_id") for action in actions if isinstance(action, dict)}
    hrefs = {action.get("href") for action in actions if isinstance(action, dict)}

    unified_html = render_unified_owner_security_command_html()
    unified_write = write_unified_owner_security_command_html()

    show("PACK 149 ALL LANE", {
        "ok": all_lane.get("ok"),
        "pack": all_lane.get("pack"),
        "status": all_lane.get("status"),
        "lane": all_lane.get("lane"),
        "base_card_count": all_lane.get("base_card_count"),
        "filtered_card_count": all_lane.get("filtered_card_count"),
        "filter_options": all_lane.get("filter_options"),
        "summary": all_lane.get("summary"),
        "failed_checks": all_lane.get("failed_checks"),
        "no_secret_leakage": all_lane.get("no_secret_leakage"),
    })

    show("PACK 149 FILTER CHECKS", {
        "route_lane": {
            "lane": route_lane.get("lane"),
            "filtered_card_count": route_lane.get("filtered_card_count"),
            "cards": [card.get("card_id") for card in route_lane.get("cards", []) if isinstance(card, dict)],
        },
        "notes_lane": {
            "lane": notes_lane.get("lane"),
            "filtered_card_count": notes_lane.get("filtered_card_count"),
            "cards": [card.get("card_id") for card in notes_lane.get("cards", []) if isinstance(card, dict)],
        },
        "attention_lane": {
            "lane": attention_lane.get("lane"),
            "filtered_card_count": attention_lane.get("filtered_card_count"),
        },
        "card_filter": {
            "card_id": card_filter.get("active_filters", {}).get("card_id"),
            "filtered_card_count": card_filter.get("filtered_card_count"),
            "cards": [card.get("card_id") for card in card_filter.get("cards", []) if isinstance(card, dict)],
        },
        "severity_filter": {
            "severity": severity_filter.get("active_filters", {}).get("severity"),
            "filtered_card_count": severity_filter.get("filtered_card_count"),
        },
        "status_filter": {
            "status": status_filter.get("active_filters", {}).get("status"),
            "filtered_card_count": status_filter.get("filtered_card_count"),
        },
        "top_only": {
            "top_only": top_only.get("active_filters", {}).get("top_only"),
            "filtered_card_count": top_only.get("filtered_card_count"),
        },
    })

    show("PACK 149 STATUS CARD", card)
    show("PACK 149 TOWER STATUS BRIDGE", bridge)

    show("PACK 149 QUICK ACTIONS", {
        "ok": quick.get("ok"),
        "status": quick.get("status"),
        "action_count": quick.get("action_count"),
        "has_focus_action": "review_owner_action_focus_lanes" in action_ids,
        "has_focus_href": "/tower/owner-action-review-focus-lanes.json" in hrefs,
        "pack149_marker": quick.get("pack149_marker"),
        "no_secret_leakage": quick.get("no_secret_leakage"),
    })

    show("PACK 149 SECTION CHECK", {
        "html_length": len(section),
        "has_marker": "PACK149_OWNER_ACTION_REVIEW_FOCUS_LANES_SECTION" in section,
        "has_title": "Owner Action Review Focus Lanes" in section or "All Review Cards" in section,
        "has_route_link": "lane=route" in section,
        "has_attention_link": "lane=attention" in section,
    })

    show("PACK 149 PANEL WRITE", panel)

    show("PACK 149 UNIFIED HTML CHECK", {
        "html_length": len(unified_html),
        "has_pack149_marker": "PACK149_UNIFIED_OWNER_PAGE_INCLUDES_OWNER_ACTION_REVIEW_FOCUS_LANES" in unified_html,
        "has_pack149_section": "PACK149_OWNER_ACTION_REVIEW_FOCUS_LANES_SECTION" in unified_html,
        "has_pack148_section": "PACK148_OWNER_ACTION_REVIEW_COMPACT_CARD_SECTION" in unified_html,
        "has_pack147_section": "PACK147_OWNER_ACTION_REVIEW_DASHBOARD_CARDS_SECTION" in unified_html,
        "has_pack145_section": "PACK145_OWNER_ACTION_REVIEW_CHECKPOINT_SECTION" in unified_html,
    })

    show("PACK 149 WRITE UNIFIED HTML", unified_write)

    assert all_lane.get("ok") is True
    assert all_lane.get("pack") == "149"
    assert all_lane.get("status") == "passed"
    assert all_lane.get("readiness_score") == 100
    assert all_lane.get("base_card_count") == 7
    assert all_lane.get("filtered_card_count") == 7
    assert all_lane.get("failed_checks") == []
    assert all_lane.get("no_secret_leakage") is True

    assert "all" in all_lane.get("available_lanes", {})
    assert "attention" in all_lane.get("available_lanes", {})
    assert "route" in all_lane.get("available_lanes", {})
    assert all_lane.get("filter_options", {}).get("lane", {}).get("all") == 7

    assert route_lane.get("ok") is True
    assert route_lane.get("lane") == "route"
    assert route_lane.get("filtered_card_count") == 1
    assert route_lane.get("cards", [])[0].get("card_id") == "route_wall"

    assert notes_lane.get("ok") is True
    assert notes_lane.get("lane") == "notes"
    assert notes_lane.get("filtered_card_count") == 1
    assert notes_lane.get("cards", [])[0].get("card_id") == "notes"

    assert attention_lane.get("ok") is True
    assert attention_lane.get("lane") == "attention"
    assert attention_lane.get("filtered_card_count") >= 0

    assert card_filter.get("ok") is True
    assert card_filter.get("filtered_card_count") == 1
    assert card_filter.get("cards", [])[0].get("card_id") == "review_health"

    assert severity_filter.get("ok") is True
    assert severity_filter.get("active_filters", {}).get("severity") == "success"
    assert severity_filter.get("filtered_card_count") >= 1

    assert status_filter.get("ok") is True
    assert status_filter.get("active_filters", {}).get("status") == "ready"
    assert status_filter.get("filtered_card_count") >= 1

    assert top_only.get("ok") is True
    assert top_only.get("active_filters", {}).get("top_only") is True
    assert top_only.get("filtered_card_count") == 1

    assert card.get("ok") is True
    assert card.get("pack") == "149"
    assert card.get("readiness_score") == 100
    assert card.get("base_card_count") == 7
    assert card.get("filtered_card_count") == 7

    assert bridge.get("ok") is True
    assert bridge.get("pack") == "149"
    assert bridge.get("readiness_score") == 100

    assert loaded.get("ok") is True
    assert loaded.get("status") == "passed"
    assert loaded.get("base_card_count") == 7

    assert OWNER_ACTION_REVIEW_FOCUS_LANES_STATUS_PATH.exists()
    assert OWNER_ACTION_REVIEW_FOCUS_LANES_PANEL_PATH.exists()

    assert quick.get("ok") is True
    assert quick.get("status") == "passed"
    assert quick.get("pack149_focus_lanes_link_present") is True
    assert quick.get("pack149_marker") == "PACK149_OWNER_ACTION_REVIEW_FOCUS_LANES_QUICK_LINK"
    assert "review_owner_action_focus_lanes" in action_ids
    assert "/tower/owner-action-review-focus-lanes.json" in hrefs
    assert quick.get("no_secret_leakage") is True

    assert "PACK149_OWNER_ACTION_REVIEW_FOCUS_LANES_SECTION" in section
    assert "lane=route" in section
    assert "lane=attention" in section
    assert "SHOULD_NOT_SURVIVE" not in section
    assert "tower_keycard=" not in section

    assert panel.get("ok") is True
    assert panel.get("pack") == "149"

    assert "PACK149_UNIFIED_OWNER_PAGE_INCLUDES_OWNER_ACTION_REVIEW_FOCUS_LANES" in unified_html
    assert "PACK149_OWNER_ACTION_REVIEW_FOCUS_LANES_SECTION" in unified_html
    assert "PACK148_OWNER_ACTION_REVIEW_COMPACT_CARD_SECTION" in unified_html
    assert "PACK147_OWNER_ACTION_REVIEW_DASHBOARD_CARDS_SECTION" in unified_html
    assert "PACK145_OWNER_ACTION_REVIEW_CHECKPOINT_SECTION" in unified_html
    assert "SHOULD_NOT_SURVIVE" not in unified_html
    assert "tower_keycard=" not in unified_html

    assert unified_write.get("ok") is True
    assert unified_write.get("pack") == "149"
    assert unified_write.get("html_length", 0) > 1000

    no_secret(all_lane)
    no_secret(route_lane)
    no_secret(notes_lane)
    no_secret(attention_lane)
    no_secret(card_filter)
    no_secret(severity_filter)
    no_secret(status_filter)
    no_secret(top_only)
    no_secret(card)
    no_secret(bridge)
    no_secret(loaded)
    no_secret(quick)

    route_report = build_ob_route_coverage_report(write_panel=True)
    object_checkpoint = build_object_permission_integration_checkpoint(write_panel=True)

    show("PACK 149 FINAL HEALTH", {
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
        "pack149_route_marker": "PACK149_OWNER_ACTION_REVIEW_FOCUS_LANES_ROUTE" in app_text,
        "pack149_route_path": "/tower/owner-action-review-focus-lanes.json" in app_text,
        "pack149_route_guard": "pack149_owner_action_review_focus_lanes_route" in app_text,
        "pack148_route_still_present": "/tower/owner-action-review-compact-card.json" in app_text,
    }
    show("PACK 149 WEB APP ROUTE CHECKS", route_checks)
    assert all(route_checks.values())

    for path in [
        PROJECT_ROOT / "tower" / "owner_action_review_focus_lanes.py",
        PROJECT_ROOT / "tower" / "security_command_owner_quick_actions.py",
        PROJECT_ROOT / "tower" / "security_command_unified_owner_page.py",
        PROJECT_ROOT / "tower" / "tower_status.py",
        PROJECT_ROOT / "tower" / "test_tower_pack_149.py",
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
        "pack": "149",
        "status": "passed",
        "readiness_score": 100,
        "base_card_count": all_lane.get("base_card_count"),
        "filtered_card_count": all_lane.get("filtered_card_count"),
        "available_lane_count": len(all_lane.get("available_lanes", {})),
        "attention_count": all_lane.get("summary", {}).get("attention_count"),
        "route_lane_count": route_lane.get("filtered_card_count"),
        "notes_lane_count": notes_lane.get("filtered_card_count"),
        "quick_action_count": quick.get("action_count"),
        "focus_link_present": True,
        "route_coverage_pct": route_report.get("coverage_pct"),
        "guarded_needed_count": route_report.get("guarded_needed_count"),
        "needs_guard_count": route_report.get("needs_guard_count"),
        "helper_wrapped_count": object_checkpoint.get("helper_wrapped_count"),
        "human_reason": "Owner Action review dashboard card filters / focus lanes are working.",
    }
    show("PACK 149 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
