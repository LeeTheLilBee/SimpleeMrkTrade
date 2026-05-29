
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

from tower.emergency_lockdown import reset_emergency_lockdown_for_test
from tower.quarantine_mode import activate_quarantine, reset_quarantine_for_test
from tower.ob_tower_bridge_adapter import reset_ob_tower_bridge_for_test
from tower.ob_tower_route_guard import (
    OB_ROUTE_GUARD_PANEL_PATH,
    classify_ob_route,
    guard_ob_route,
    render_ob_locked_page,
    reset_ob_route_guard_for_test,
    summarize_ob_route_guard,
)


def _print(title, payload=None):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def _assert_no_secret_leakage(payload):
    serialized = json.dumps(payload, sort_keys=True, default=str).lower()
    forbidden = [
        "tower_keycard=",
        "should_not_survive",
        '"raw_token":',
        '"tower_keycard":',
        '"access_token":',
        '"refresh_token":',
        '"api_key":',
        '"github_token":',
        '"stripe_secret":',
        '"password":',
        '"private_key":',
        "bearer should_not_survive",
        "ghp_should_not_survive",
        "sk_live_should_not_survive",
        "-----begin private key-----",
    ]
    for item in forbidden:
        assert item not in serialized, item


def run_tests():
    reset_all = {
        "lockdown": reset_emergency_lockdown_for_test(),
        "quarantine": reset_quarantine_for_test(),
        "bridge": reset_ob_tower_bridge_for_test(),
        "route_guard": reset_ob_route_guard_for_test(),
    }
    _print("RESET OB ROUTE GUARD DEPENDENCIES", reset_all)
    assert all(item.get("ok") for item in reset_all.values())

    classification_checks = {
        "/signals-spotlight": "public_route",
        "/observatory-private": "private_ob_entry",
        "/paper": "mode_route",
        "/signals/AAPL": "symbol_object_route",
        "/positions/pos_123": "position_object_route",
        "/trades/trade_123": "trade_object_route",
        "/export/report": "export_route",
        "/reveal/position": "reveal_route",
        "/live/manual": "mode_route",
        "/admin": "admin_route",
        "/mystery": "unknown_route",
    }

    for route, expected in classification_checks.items():
        classified = classify_ob_route(route)
        _print(f"CLASSIFY {route}", classified)
        assert classified.get("classification") == expected, (route, classified)

    public_route = guard_ob_route(
        user_id="anonymous",
        role="public",
        route_path="/signals-spotlight",
        metadata={"raw_token": "SHOULD_NOT_SURVIVE"},
    )
    _print("GUARD PUBLIC ROUTE", public_route)

    assert public_route.get("decision") == "allow"
    assert public_route.get("allowed") is True
    assert public_route.get("should_render_route") is True
    _assert_no_secret_leakage(public_route)

    owner_entry = guard_ob_route(
        user_id="owner_solice",
        role="owner",
        route_path="/observatory-private",
    )
    _print("GUARD OWNER OB ENTRY", owner_entry)

    assert owner_entry.get("decision") == "allow"
    assert owner_entry.get("allowed") is True
    assert owner_entry.get("classification", {}).get("classification") == "private_ob_entry"
    _assert_no_secret_leakage(owner_entry)

    beta_paper = guard_ob_route(
        user_id="beta_user_102",
        role="beta",
        route_path="/paper",
    )
    _print("GUARD BETA PAPER", beta_paper)

    assert beta_paper.get("decision") == "allow"
    assert beta_paper.get("allowed") is True
    assert beta_paper.get("classification", {}).get("mode") == "paper"
    _assert_no_secret_leakage(beta_paper)

    beta_live = guard_ob_route(
        user_id="beta_user_102",
        role="beta",
        route_path="/live/manual",
    )
    _print("GUARD BETA LIVE DENIED", beta_live)

    assert beta_live.get("decision") == "deny"
    assert beta_live.get("allowed") is False
    assert beta_live.get("locked_page_kind") == "denied"
    _assert_no_secret_leakage(beta_live)

    symbol = guard_ob_route(
        user_id="beta_user_102",
        role="beta",
        route_path="/signals/AAPL",
    )
    _print("GUARD SYMBOL ROUTE", symbol)

    assert symbol.get("decision") == "allow"
    assert symbol.get("allowed") is True
    assert symbol.get("classification", {}).get("object_type") == "symbol"
    assert symbol.get("classification", {}).get("object_id") == "AAPL"
    _assert_no_secret_leakage(symbol)

    export = guard_ob_route(
        user_id="owner_solice",
        role="owner",
        route_path="/export/report",
    )
    _print("GUARD EXPORT ROUTE STEP-UP", export)

    assert export.get("decision") == "step_up_required"
    assert export.get("allowed") is False
    assert export.get("requires_step_up") is True
    assert export.get("requires_receipt") is True
    assert export.get("requires_archive_handoff") is True
    assert export.get("locked_page_kind") == "step_up"
    _assert_no_secret_leakage(export)

    reveal = guard_ob_route(
        user_id="owner_solice",
        role="owner",
        route_path="/reveal/position",
    )
    _print("GUARD REVEAL ROUTE STEP-UP", reveal)

    assert reveal.get("decision") == "step_up_required"
    assert reveal.get("requires_step_up") is True
    assert reveal.get("requires_receipt") is True
    _assert_no_secret_leakage(reveal)

    live_owner = guard_ob_route(
        user_id="owner_solice",
        role="owner",
        route_path="/live/manual",
    )
    _print("GUARD OWNER LIVE LOCKED", live_owner)

    assert live_owner.get("decision") == "deny"
    assert live_owner.get("allowed") is False
    assert live_owner.get("bridge_response", {}).get("reason_code") in {
        "live_and_broker_locked_until_compliance",
        "mode_not_allowed_for_role",
    }
    _assert_no_secret_leakage(live_owner)

    admin = guard_ob_route(
        user_id="beta_user_102",
        role="beta",
        route_path="/admin",
        method="POST",
        metadata={"tower_keycard": "SHOULD_NOT_SURVIVE"},
    )
    _print("GUARD ADMIN ROUTE", admin)

    assert admin.get("decision") in {"deny", "step_up_required"}
    assert admin.get("allowed") is False
    _assert_no_secret_leakage(admin)

    quarantine_case = activate_quarantine(
        actor_user_id="owner_solice",
        scope="user",
        target={"user_id": "quarantined_route_user_102"},
        reason_code="pack102_route_guard_test",
        human_reason="Pack 102 route guard quarantine test.",
        severity="restricted",
    )
    _print("ACTIVATE QUARANTINE FOR ROUTE GUARD", quarantine_case)
    assert quarantine_case.get("ok") is True

    quarantined = guard_ob_route(
        user_id="quarantined_route_user_102",
        role="beta",
        route_path="/observatory-private",
    )
    _print("GUARD QUARANTINED USER", quarantined)

    assert quarantined.get("decision") == "quarantine"
    assert quarantined.get("allowed") is False
    assert quarantined.get("locked_page_kind") == "quarantine"
    _assert_no_secret_leakage(quarantined)

    locked_html = render_ob_locked_page(export)
    _print("LOCKED PAGE HTML SAMPLE", {"length": len(locked_html), "contains_step_up": "Tower Step-Up Required" in locked_html})

    assert "Tower Step-Up Required" in locked_html
    assert "SHOULD_NOT_SURVIVE" not in locked_html
    assert "tower_keycard=" not in locked_html

    summary = summarize_ob_route_guard(limit=80)
    _print("OB ROUTE GUARD SUMMARY", summary)

    assert summary.get("ok") is True
    assert summary.get("readiness_score") == 100
    assert summary.get("readiness_label") == "OB Tower route guard ready"
    assert summary.get("event_count", 0) >= 10
    assert summary.get("by_decision", {}).get("allow", 0) >= 4
    assert summary.get("by_decision", {}).get("deny", 0) >= 2
    assert summary.get("by_decision", {}).get("step_up_required", 0) >= 2
    assert summary.get("by_decision", {}).get("quarantine", 0) >= 1
    assert summary.get("no_secret_leakage") is True
    assert OB_ROUTE_GUARD_PANEL_PATH.exists()
    _assert_no_secret_leakage(summary)

    html = OB_ROUTE_GUARD_PANEL_PATH.read_text(encoding="utf-8")
    assert "The Tower · OB Route Guard" in html
    assert "SHOULD_NOT_SURVIVE" not in html
    assert "tower_keycard=" not in html

    final = {
        "pack": "102",
        "status": "passed",
        "human_reason": "OB route guard now wraps the Tower bridge for public/private app entry, mode, symbol, export, reveal, live, admin, quarantine, and locked-page decisions.",
    }
    _print("PACK 102 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
