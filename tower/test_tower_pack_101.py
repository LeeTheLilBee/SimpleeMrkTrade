
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
from tower.ob_tower_bridge_adapter import (
    BRIDGE_REQUEST_TYPES,
    OB_TOWER_BRIDGE_POLICY,
    make_ob_bridge_request,
    request_ob_action_clearance,
    request_ob_app_clearance,
    request_ob_archive_handoff_request,
    request_ob_export_clearance,
    request_ob_live_action_clearance,
    request_ob_mode_clearance,
    request_ob_object_clearance,
    request_ob_reveal_clearance,
    request_ob_route_clearance,
    reset_ob_tower_bridge_for_test,
    submit_ob_security_event,
    summarize_ob_tower_bridge,
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
    }
    _print("RESET OB BRIDGE DEPENDENCIES", reset_all)
    assert all(item.get("ok") for item in reset_all.values())

    assert "app_entry" in BRIDGE_REQUEST_TYPES
    assert "route_access" in BRIDGE_REQUEST_TYPES
    assert "mode_access" in BRIDGE_REQUEST_TYPES
    assert "object_access" in BRIDGE_REQUEST_TYPES
    assert "export_access" in BRIDGE_REQUEST_TYPES
    assert "reveal_access" in BRIDGE_REQUEST_TYPES
    assert "live_action_access" in BRIDGE_REQUEST_TYPES
    assert OB_TOWER_BRIDGE_POLICY["tower_is_outer_control_center"] is True
    assert OB_TOWER_BRIDGE_POLICY["ob_must_request_clearance_before_protected_load"] is True

    req = make_ob_bridge_request(
        user_id="owner_solice",
        role="owner",
        request_type="route_access",
        route_path="/observatory-private",
        metadata={
            "tower_keycard": "SHOULD_NOT_SURVIVE",
            "raw_token": "SHOULD_NOT_SURVIVE",
            "safe": "ok",
        },
    )
    _print("BRIDGE REQUEST SANITIZED", req)

    assert req.get("ok") is True
    assert req.get("app_id") == "observatory"
    assert req.get("request_type") == "route_access"
    assert "request_fingerprint" in req
    _assert_no_secret_leakage(req)

    public_route = request_ob_route_clearance(
        user_id="anonymous",
        role="public",
        route_path="/signals-spotlight",
        metadata={"api_key": "SHOULD_NOT_SURVIVE"},
    )
    _print("PUBLIC ROUTE CLEARANCE", public_route)

    assert public_route.get("decision") == "allow"
    assert public_route.get("allowed") is True
    assert public_route.get("reason_code") == "public_safe_ob_route"
    _assert_no_secret_leakage(public_route)

    owner_app = request_ob_app_clearance(
        user_id="owner_solice",
        role="owner",
        route_path="/observatory-private",
    )
    _print("OWNER APP CLEARANCE", owner_app)

    assert owner_app.get("decision") == "allow"
    assert owner_app.get("allowed") is True
    assert "continue_to_ob" in owner_app.get("required_actions", [])
    _assert_no_secret_leakage(owner_app)

    beta_paper = request_ob_mode_clearance(
        user_id="beta_user_101",
        role="beta",
        mode="paper",
    )
    _print("BETA PAPER MODE CLEARANCE", beta_paper)

    assert beta_paper.get("decision") == "allow"
    assert beta_paper.get("allowed") is True
    _assert_no_secret_leakage(beta_paper)

    beta_live = request_ob_mode_clearance(
        user_id="beta_user_101",
        role="beta",
        mode="live_manual",
    )
    _print("BETA LIVE MODE DENIED", beta_live)

    assert beta_live.get("decision") == "deny"
    assert beta_live.get("allowed") is False
    assert beta_live.get("reason_code") == "mode_not_allowed_for_role"
    _assert_no_secret_leakage(beta_live)

    owner_live = request_ob_live_action_clearance(
        user_id="owner_solice",
        role="owner",
        mode="live_manual",
        action="live_mode_enable",
    )
    _print("OWNER LIVE ACTION LOCKED", owner_live)

    assert owner_live.get("decision") == "deny"
    assert owner_live.get("reason_code") == "live_and_broker_locked_until_compliance"
    assert owner_live.get("requires_receipt") is True
    _assert_no_secret_leakage(owner_live)

    symbol = request_ob_object_clearance(
        user_id="beta_user_101",
        role="beta",
        object_type="symbol",
        object_id="AAPL",
        route_path="/signals/AAPL",
    )
    _print("SYMBOL OBJECT CLEARANCE", symbol)

    assert symbol.get("decision") == "allow"
    assert symbol.get("allowed") is True
    _assert_no_secret_leakage(symbol)

    unsupported_object = request_ob_object_clearance(
        user_id="beta_user_101",
        role="beta",
        object_type="secret_panel",
        object_id="bad",
    )
    _print("UNSUPPORTED OBJECT DENIED", unsupported_object)

    assert unsupported_object.get("decision") == "deny"
    assert unsupported_object.get("reason_code") == "unsupported_ob_object_type"
    _assert_no_secret_leakage(unsupported_object)

    export = request_ob_export_clearance(
        user_id="owner_solice",
        role="owner",
        export_id="trade_packet_101",
    )
    _print("EXPORT REQUIRES STEP-UP", export)

    assert export.get("decision") == "step_up_required"
    assert export.get("requires_step_up") is True
    assert export.get("requires_receipt") is True
    assert export.get("requires_archive_handoff") is True
    _assert_no_secret_leakage(export)

    reveal = request_ob_reveal_clearance(
        user_id="owner_solice",
        role="owner",
        object_type="position",
        object_id="pos_101",
    )
    _print("REVEAL REQUIRES STEP-UP", reveal)

    assert reveal.get("decision") == "step_up_required"
    assert reveal.get("requires_step_up") is True
    assert reveal.get("requires_receipt") is True
    _assert_no_secret_leakage(reveal)

    action = request_ob_action_clearance(
        user_id="owner_solice",
        role="owner",
        action="download",
        object_type="report",
        object_id="report_101",
    )
    _print("DOWNLOAD ACTION REQUIRES STEP-UP", action)

    assert action.get("decision") == "step_up_required"
    assert action.get("requires_step_up") is True
    assert action.get("requires_receipt") is True
    _assert_no_secret_leakage(action)

    security_event = submit_ob_security_event(
        user_id="beta_user_101",
        role="beta",
        event_name="denied_route_seen",
        severity="warning",
        metadata={"password": "SHOULD_NOT_SURVIVE"},
    )
    _print("OB SECURITY EVENT SUBMITTED", security_event)

    assert security_event.get("security_event_recorded") is True
    _assert_no_secret_leakage(security_event)

    archive_request = request_ob_archive_handoff_request(
        user_id="owner_solice",
        role="owner",
        handoff_id="ob_archive_101",
        metadata={"document_text": "Sensitive archive content should redact."},
    )
    _print("OB ARCHIVE HANDOFF REQUEST", archive_request)

    assert archive_request.get("decision") == "step_up_required"
    assert archive_request.get("requires_archive_handoff") is True
    assert archive_request.get("requires_receipt") is True
    _assert_no_secret_leakage(archive_request)

    quarantine_case = activate_quarantine(
        actor_user_id="owner_solice",
        scope="user",
        target={"user_id": "quarantined_ob_user_101"},
        reason_code="pack101_bridge_test",
        human_reason="Pack 101 bridge quarantine test.",
        severity="restricted",
    )
    _print("ACTIVATE QUARANTINE FOR BRIDGE TEST", quarantine_case)
    assert quarantine_case.get("ok") is True

    quarantined = request_ob_app_clearance(
        user_id="quarantined_ob_user_101",
        role="beta",
        route_path="/observatory-private",
    )
    _print("QUARANTINED OB APP CLEARANCE", quarantined)

    assert quarantined.get("decision") == "quarantine"
    assert quarantined.get("allowed") is False
    assert "show_quarantine_holding_state" in quarantined.get("required_actions", [])
    _assert_no_secret_leakage(quarantined)

    summary = summarize_ob_tower_bridge(limit=80)
    _print("OB TOWER BRIDGE SUMMARY", summary)

    assert summary.get("ok") is True
    assert summary.get("readiness_score") == 100
    assert summary.get("readiness_label") == "OB Tower Bridge adapter foundation ready"
    assert summary.get("event_count", 0) >= 12
    assert summary.get("by_decision", {}).get("allow", 0) >= 4
    assert summary.get("by_decision", {}).get("deny", 0) >= 3
    assert summary.get("by_decision", {}).get("step_up_required", 0) >= 3
    assert summary.get("by_decision", {}).get("quarantine", 0) >= 1
    assert summary.get("no_secret_leakage") is True
    _assert_no_secret_leakage(summary)

    final = {
        "pack": "101",
        "status": "passed",
        "human_reason": "OB Tower Bridge contract and adapter foundation created. OB can now ask Tower for app, route, mode, object, action, export, reveal, live, broker, quarantine, and receipt decisions.",
    }
    _print("PACK 101 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
