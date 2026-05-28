
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

from tower.emergency_lockdown import activate_emergency_lockdown, evaluate_lockdown_gate, reset_emergency_lockdown_for_test
from tower.quarantine_mode import (
    QUARANTINE_ALLOWED_ACTIONS,
    QUARANTINE_BLOCKED_ACTIONS,
    activate_quarantine,
    add_quarantine_owner_note,
    evaluate_quarantine_gate,
    find_matching_quarantine_cases,
    load_quarantine_state,
    release_quarantine,
    request_quarantine_release,
    reset_quarantine_for_test,
    summarize_quarantine_mode,
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
    reset_lockdown = reset_emergency_lockdown_for_test()
    reset_quarantine = reset_quarantine_for_test()

    _print("RESET LOCKDOWN + QUARANTINE", {
        "lockdown": reset_lockdown,
        "quarantine": reset_quarantine,
    })

    assert reset_lockdown.get("ok") is True
    assert reset_quarantine.get("ok") is True
    assert reset_quarantine.get("events_reset") is True

    no_match = evaluate_quarantine_gate(
        action="export",
        user_id="beta_001",
        session_id="sess_clean",
        device_id="device_clean",
        ip_address="127.0.0.1",
        route_path="/export",
        object_type="export",
        object_id="export_clean",
    )
    _print("NO QUARANTINE MATCH", no_match)

    assert no_match.get("decision") == "allow"
    assert no_match.get("quarantine_active") is False

    activated = activate_quarantine(
        actor_user_id="owner_solice",
        scope="session",
        target={
            "user_id": "beta_001",
            "session_id": "sess_quar_094",
            "device_id": "device_quar_094",
            "raw_token": "SHOULD_NOT_SURVIVE",
        },
        reason_code="pack094_suspicious_session",
        human_reason="Pack 094 test suspicious session contained.",
        severity="restricted",
        metadata={"pack": "094", "tower_keycard": "SHOULD_NOT_SURVIVE"},
    )
    _print("QUARANTINE ACTIVATED", activated)

    assert activated.get("ok") is True
    assert activated.get("decision") == "quarantine_activated"
    assert activated.get("quarantine_active") is True
    assert activated.get("quarantine_id")

    state = load_quarantine_state()
    _print("QUARANTINE STATE", state)

    assert len(state.get("active_cases", [])) == 1
    assert state.get("active_cases", [])[0].get("status") == "active"
    assert "export" in state.get("blocked_actions", [])
    assert "view_quarantine_status" in state.get("allowed_actions", [])

    matches = find_matching_quarantine_cases(
        user_id="beta_001",
        session_id="sess_quar_094",
        device_id="device_quar_094",
        ip_address="",
        object_type="",
        object_id="",
    )
    _print("MATCHING QUARANTINE CASES", matches)

    assert len(matches) == 1
    assert matches[0].get("quarantine_id") == activated.get("quarantine_id")

    blocked_checks = {}
    for action in [
        "export",
        "route_policy_change",
        "live_mode_enable",
        "broker_action",
        "sensitive_reveal",
        "admin_override",
        "object_reveal",
    ]:
        decision = evaluate_quarantine_gate(
            action=action,
            user_id="beta_001",
            session_id="sess_quar_094",
            device_id="device_quar_094",
            route_path=f"/{action}",
            object_type="test_object",
            object_id=f"{action}_094",
            metadata={"pack": "094", "tower_keycard": "SHOULD_NOT_SURVIVE"},
        )
        blocked_checks[action] = decision
        assert decision.get("decision") == "deny", action
        assert decision.get("allowed") is False, action
        assert decision.get("quarantine_active") is True, action
        assert decision.get("reason_code") == "action_blocked_by_quarantine", action

    _print("QUARANTINE BLOCKED ACTIONS", blocked_checks)

    recovery_checks = {}
    for action in [
        "view_status",
        "view_quarantine_status",
        "create_quarantine_note",
        "owner_read_only_review",
        "tamper_chain_verify",
        "appeal_quarantine",
    ]:
        decision = evaluate_quarantine_gate(
            action=action,
            user_id="beta_001",
            session_id="sess_quar_094",
            device_id="device_quar_094",
            route_path="/tower/security-command",
            object_type="tower_recovery",
            object_id=action,
        )
        recovery_checks[action] = decision
        assert decision.get("decision") == "allow_quarantine_recovery", action
        assert decision.get("allowed") is True, action
        assert decision.get("quarantine_active") is True, action

    _print("QUARANTINE RECOVERY ACTIONS", recovery_checks)

    note = add_quarantine_owner_note(
        actor_user_id="owner_solice",
        quarantine_id=activated.get("quarantine_id"),
        note="Pack 094 quarantine owner note. tower_keycard SHOULD_NOT_SURVIVE should redact.",
        metadata={"reason": "test note"},
    )
    _print("QUARANTINE OWNER NOTE", note)

    assert note.get("ok") is True
    assert note.get("decision") == "quarantine_owner_note_added"

    release_missing_step = release_quarantine(
        actor_user_id="owner_solice",
        quarantine_id=activated.get("quarantine_id"),
        reason="Trying to release without fresh step-up should fail.",
        session_id="sess_quar_release_094",
    )
    _print("RELEASE WITHOUT STEP-UP", release_missing_step)

    assert release_missing_step.get("ok") is False
    assert release_missing_step.get("decision") == "step_up_required"
    assert release_missing_step.get("quarantine_active") is True

    release_request = request_quarantine_release(
        actor_user_id="owner_solice",
        quarantine_id=activated.get("quarantine_id"),
        reason="Pack 094 release request should demand step-up.",
        session_id="sess_quar_release_094",
        metadata={"pack": "094"},
    )
    _print("REQUEST QUARANTINE RELEASE", release_request)

    assert release_request.get("ok") is True
    assert release_request.get("decision") == "step_up_required"
    assert release_request.get("quarantine_active") is True

    challenge = create_step_up_challenge(
        user_id="owner_solice",
        action="admin_override",
        object_type="quarantine_case",
        object_id=activated.get("quarantine_id"),
        session_id="sess_quar_release_094",
        route_path="/tower/security-command",
        method="owner_pin",
        reason="Pack 094 owner step-up before quarantine release.",
    )
    _print("QUARANTINE RELEASE STEP-UP CHALLENGE", challenge)

    assert challenge.get("ok") is True
    assert challenge.get("status") == "pending"

    verified = verify_step_up_challenge(
        challenge_id=challenge.get("challenge_id"),
        user_id="owner_solice",
        method="owner_pin",
        verification_note="Pack 094 verified owner for quarantine release.",
    )
    _print("QUARANTINE RELEASE STEP-UP VERIFIED", verified)

    assert verified.get("ok") is True

    release_allowed = request_quarantine_release(
        actor_user_id="owner_solice",
        quarantine_id=activated.get("quarantine_id"),
        reason="Pack 094 release request after step-up should be allowed.",
        session_id="sess_quar_release_094",
        metadata={"pack": "094", "after_step_up": True},
    )
    _print("REQUEST QUARANTINE RELEASE AFTER STEP-UP", release_allowed)

    assert release_allowed.get("ok") is True
    assert release_allowed.get("decision") == "release_allowed"
    assert release_allowed.get("step_up", {}).get("decision") == "allow"

    released = release_quarantine(
        actor_user_id="owner_solice",
        quarantine_id=activated.get("quarantine_id"),
        reason="Pack 094 verified quarantine release after step-up.",
        session_id="sess_quar_release_094",
        metadata={"pack": "094"},
    )
    _print("QUARANTINE RELEASED", released)

    assert released.get("ok") is True
    assert released.get("decision") == "quarantine_released"
    assert released.get("quarantine_active") is False

    after_release_gate = evaluate_quarantine_gate(
        action="export",
        user_id="beta_001",
        session_id="sess_quar_094",
        device_id="device_quar_094",
        route_path="/export",
        object_type="export",
        object_id="export_after_release",
    )
    _print("GATE AFTER QUARANTINE RELEASED", after_release_gate)

    assert after_release_gate.get("decision") == "allow"
    assert after_release_gate.get("quarantine_active") is False

    # Prove emergency lockdown outranks quarantine when both exist.
    activated_second = activate_quarantine(
        actor_user_id="owner_solice",
        scope="user",
        target={"user_id": "beta_lockdown_priority"},
        reason_code="pack094_lockdown_priority_case",
        human_reason="Pack 094 priority test quarantine.",
        severity="restricted",
    )
    assert activated_second.get("ok") is True

    lockdown = activate_emergency_lockdown(
        actor_user_id="owner_solice",
        reason_code="pack094_lockdown_priority",
        human_reason="Pack 094 proves lockdown outranks quarantine.",
        severity="critical",
    )
    assert lockdown.get("ok") is True

    priority = evaluate_quarantine_gate(
        action="export",
        user_id="beta_lockdown_priority",
        session_id="sess_priority",
        route_path="/export",
        object_type="export",
        object_id="export_priority",
    )
    _print("LOCKDOWN OUTRANKS QUARANTINE", priority)

    assert priority.get("quarantine_deferred_to_lockdown") is True
    assert priority.get("decision") == "deny"
    assert priority.get("lockdown_active") is True

    # Reset lockdown at the end so future packs don't inherit full lockdown.
    reset_emergency_lockdown_for_test()

    summary = summarize_quarantine_mode(limit=80)
    _print("QUARANTINE SUMMARY", summary)

    assert summary.get("ok") is True
    assert summary.get("readiness_score") == 100
    assert summary.get("readiness_label") == "Quarantine mode ready"
    assert summary.get("total_events", 0) >= 10
    assert summary.get("by_decision", {}).get("quarantine_activated", 0) >= 2
    assert summary.get("by_decision", {}).get("quarantine_block", 0) >= 7
    assert summary.get("by_decision", {}).get("quarantine_released", 0) >= 1
    assert summary.get("no_sensitive_key_leakage") is True

    for action in [
        "export",
        "route_policy_change",
        "live_mode_enable",
        "automated_mode_enable",
        "broker_action",
        "object_reveal",
    ]:
        assert action in QUARANTINE_BLOCKED_ACTIONS

    for action in [
        "view_status",
        "view_quarantine_status",
        "owner_read_only_review",
        "tamper_chain_verify",
    ]:
        assert action in QUARANTINE_ALLOWED_ACTIONS

    serialized = json.dumps([
        reset_lockdown,
        reset_quarantine,
        no_match,
        activated,
        state,
        matches,
        blocked_checks,
        recovery_checks,
        note,
        release_missing_step,
        release_request,
        challenge,
        verified,
        release_allowed,
        released,
        after_release_gate,
        activated_second,
        lockdown,
        priority,
        summary,
    ], sort_keys=True, default=str)

    assert "tower_keycard=" not in serialized
    assert "raw_token=" not in serialized
    assert '"raw_token":' not in serialized
    assert '"tower_keycard":' not in serialized
    assert "Bearer SHOULD_NOT_SURVIVE" not in serialized
    assert "SHOULD_NOT_SURVIVE" not in serialized
    assert "Soulaana:" in serialized

    final = {
        "pack": "094",
        "status": "passed",
        "human_reason": "Quarantine mode can contain suspicious sessions/users, block dangerous actions, preserve recovery actions, require step-up for release, and defer to full lockdown.",
    }
    _print("PACK 094 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
