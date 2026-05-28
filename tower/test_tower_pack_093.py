
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

from tower.emergency_lockdown import (
    LOCKDOWN_BLOCKED_ACTIONS,
    LOCKDOWN_ALLOWED_RECOVERY_ACTIONS,
    activate_emergency_lockdown,
    add_lockdown_owner_note,
    disable_emergency_lockdown,
    evaluate_lockdown_gate,
    load_emergency_lockdown_state,
    request_lockdown_disable,
    reset_emergency_lockdown_for_test,
    summarize_emergency_lockdown,
)
from tower.step_up_auth import create_step_up_challenge, verify_step_up_challenge


def _print(title, payload=None):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def run_tests():
    reset = reset_emergency_lockdown_for_test()
    _print("RESET LOCKDOWN FOR TEST", reset)
    assert reset.get("ok") is True

    inactive_gate = evaluate_lockdown_gate(
        action="export",
        user_id="owner_solice",
        route_path="/export",
        object_type="export",
        object_id="export_093",
    )
    _print("INACTIVE LOCKDOWN GATE", inactive_gate)

    assert inactive_gate.get("decision") == "allow"
    assert inactive_gate.get("lockdown_active") is False

    activated = activate_emergency_lockdown(
        actor_user_id="owner_solice",
        reason_code="pack093_manual_test_lockdown",
        human_reason="Pack 093 test activated emergency lockdown.",
        severity="critical",
        metadata={"test": True, "raw_token": "SHOULD_NOT_SURVIVE"},
    )
    _print("LOCKDOWN ACTIVATED", activated)

    assert activated.get("ok") is True
    assert activated.get("decision") == "lockdown_activated"
    assert activated.get("lockdown_active") is True
    assert activated.get("lockdown_id")

    state = load_emergency_lockdown_state()
    _print("LOCKDOWN STATE", state)

    assert state.get("lockdown_active") is True
    assert state.get("severity") == "critical"
    assert state.get("lockdown_id") == activated.get("lockdown_id")
    assert "export" in state.get("blocked_actions", [])
    assert "owner_recovery" in state.get("allowed_recovery_actions", [])

    blocked_checks = {}
    for action in [
        "ob_app_entry",
        "export",
        "route_policy_change",
        "live_mode_enable",
        "broker_action",
        "sensitive_reveal",
        "admin_override",
        "object_reveal",
    ]:
        decision = evaluate_lockdown_gate(
            action=action,
            user_id="beta_001",
            route_path=f"/{action}",
            object_type="test_object",
            object_id=f"{action}_093",
            metadata={"pack": "093", "tower_keycard": "SHOULD_NOT_SURVIVE"},
        )
        blocked_checks[action] = decision
        assert decision.get("decision") == "deny", action
        assert decision.get("allowed") is False, action
        assert decision.get("lockdown_active") is True, action
        assert decision.get("reason_code") == "action_blocked_by_emergency_lockdown", action

    _print("BLOCKED ACTION CHECKS", blocked_checks)

    recovery_checks = {}
    for action in [
        "view_status",
        "view_lockdown_status",
        "create_lockdown_note",
        "owner_recovery",
        "tamper_chain_verify",
    ]:
        decision = evaluate_lockdown_gate(
            action=action,
            user_id="owner_solice",
            route_path="/tower/security-command",
            object_type="tower_recovery",
            object_id=action,
        )
        recovery_checks[action] = decision
        assert decision.get("decision") == "allow_recovery", action
        assert decision.get("lockdown_active") is True, action

    _print("RECOVERY ACTION CHECKS", recovery_checks)

    note = add_lockdown_owner_note(
        actor_user_id="owner_solice",
        note="Pack 093 owner note. token SHOULD_NOT_SURVIVE should redact.",
        metadata={"reason": "test note"},
    )
    _print("LOCKDOWN OWNER NOTE", note)

    assert note.get("ok") is True
    assert note.get("decision") == "owner_note_added"

    disable_missing_step = disable_emergency_lockdown(
        actor_user_id="owner_solice",
        reason="Trying to disable without fresh step-up should fail.",
        session_id="sess_lock_093",
    )
    _print("DISABLE WITHOUT STEP-UP", disable_missing_step)

    assert disable_missing_step.get("ok") is False
    assert disable_missing_step.get("decision") == "step_up_required"
    assert disable_missing_step.get("lockdown_active") is True

    disable_request = request_lockdown_disable(
        actor_user_id="owner_solice",
        reason="Pack 093 disable request should demand step-up.",
        session_id="sess_lock_093",
        metadata={"pack": "093"},
    )
    _print("REQUEST LOCKDOWN DISABLE", disable_request)

    assert disable_request.get("ok") is True
    assert disable_request.get("decision") == "step_up_required"
    assert disable_request.get("lockdown_active") is True

    challenge = create_step_up_challenge(
        user_id="owner_solice",
        action="lockdown_disable",
        object_type="emergency_lockdown",
        object_id=state.get("lockdown_id"),
        session_id="sess_lock_093",
        route_path="/tower/security-command",
        method="owner_pin",
        reason="Pack 093 owner step-up before disabling lockdown.",
    )
    _print("LOCKDOWN DISABLE STEP-UP CHALLENGE", challenge)

    assert challenge.get("ok") is True
    assert challenge.get("status") == "pending"

    verified = verify_step_up_challenge(
        challenge_id=challenge.get("challenge_id"),
        user_id="owner_solice",
        method="owner_pin",
        verification_note="Pack 093 verified owner for lockdown disable.",
    )
    _print("LOCKDOWN DISABLE STEP-UP VERIFIED", verified)

    assert verified.get("ok") is True

    disable_allowed = request_lockdown_disable(
        actor_user_id="owner_solice",
        reason="Pack 093 disable request after step-up should be allowed.",
        session_id="sess_lock_093",
        metadata={"pack": "093", "after_step_up": True},
    )
    _print("REQUEST LOCKDOWN DISABLE AFTER STEP-UP", disable_allowed)

    assert disable_allowed.get("ok") is True
    assert disable_allowed.get("decision") == "disable_allowed"
    assert disable_allowed.get("step_up", {}).get("decision") == "allow"

    disabled = disable_emergency_lockdown(
        actor_user_id="owner_solice",
        reason="Pack 093 verified disable after step-up.",
        session_id="sess_lock_093",
        metadata={"pack": "093"},
    )
    _print("LOCKDOWN DISABLED", disabled)

    assert disabled.get("ok") is True
    assert disabled.get("decision") == "lockdown_disabled"
    assert disabled.get("lockdown_active") is False

    after_disable_gate = evaluate_lockdown_gate(
        action="export",
        user_id="owner_solice",
        route_path="/export",
        object_type="export",
        object_id="export_093_after",
    )
    _print("GATE AFTER LOCKDOWN DISABLED", after_disable_gate)

    assert after_disable_gate.get("decision") == "allow"
    assert after_disable_gate.get("lockdown_active") is False

    summary = summarize_emergency_lockdown(limit=50)
    _print("EMERGENCY LOCKDOWN SUMMARY", summary)

    assert summary.get("ok") is True
    assert summary.get("readiness_score") == 100
    assert summary.get("readiness_label") == "Emergency lockdown system ready"
    assert summary.get("lockdown_active") is False
    assert summary.get("total_events", 0) >= 10
    assert summary.get("by_decision", {}).get("lockdown_activated", 0) >= 1
    assert summary.get("by_decision", {}).get("lockdown_block", 0) >= 1
    assert summary.get("by_decision", {}).get("lockdown_disabled", 0) >= 1

    for action in [
        "export",
        "route_policy_change",
        "live_mode_enable",
        "automated_mode_enable",
        "broker_action",
        "object_reveal",
    ]:
        assert action in LOCKDOWN_BLOCKED_ACTIONS

    for action in [
        "view_status",
        "owner_recovery",
        "tamper_chain_verify",
    ]:
        assert action in LOCKDOWN_ALLOWED_RECOVERY_ACTIONS

    serialized = json.dumps([
        reset,
        inactive_gate,
        activated,
        state,
        blocked_checks,
        recovery_checks,
        note,
        disable_missing_step,
        disable_request,
        challenge,
        verified,
        disable_allowed,
        disabled,
        after_disable_gate,
        summary,
    ], sort_keys=True, default=str)

    assert "tower_keycard=" not in serialized
    assert "raw_token=" not in serialized
    assert '"raw_token":' not in serialized
    assert "Bearer SHOULD_NOT_SURVIVE" not in serialized
    assert "SHOULD_NOT_SURVIVE" not in serialized
    assert "Soulaana:" in serialized

    final = {
        "pack": "093",
        "status": "passed",
        "human_reason": "Emergency lockdown system can activate, block dangerous actions, preserve recovery actions, require step-up for disable, and reopen with receipts.",
    }
    _print("PACK 093 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
