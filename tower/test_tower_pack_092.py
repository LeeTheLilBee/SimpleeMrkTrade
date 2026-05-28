
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

from tower.step_up_auth import (
    STEP_UP_POLICY,
    create_step_up_challenge,
    evaluate_step_up_requirement,
    get_step_up_policy_for_action,
    has_recent_step_up,
    summarize_step_up_auth,
    verify_step_up_challenge,
)


def _print(title, payload=None):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def run_tests():
    export_policy = get_step_up_policy_for_action("export")
    route_policy = get_step_up_policy_for_action("route_policy_change")
    low_policy = get_step_up_policy_for_action("view_status")
    unknown_policy = get_step_up_policy_for_action("unknown_power_button")

    _print("STEP-UP POLICIES", {
        "export": export_policy,
        "route_policy_change": route_policy,
        "view_status": low_policy,
        "unknown_power_button": unknown_policy,
    })

    assert export_policy.get("required") is True
    assert route_policy.get("required") is True
    assert low_policy.get("required") is False
    assert unknown_policy.get("required") is True

    denied_base = evaluate_step_up_requirement(
        user_id="beta_001",
        action="export",
        object_type="export",
        object_id="export_092",
        session_id="sess_denied",
        route_path="/export",
        clearance_decision={
            "allowed": False,
            "decision": "deny",
            "risk_score": 70,
            "risk_state": "restricted",
            "required_actions": ["upgrade_clearance"],
        },
    )
    _print("BASE CLEARANCE DENIED BEFORE STEP-UP", denied_base)

    assert denied_base.get("decision") == "deny"
    assert denied_base.get("step_up_required") is False
    assert denied_base.get("reason_code") == "base_clearance_denied_before_step_up"

    low = evaluate_step_up_requirement(
        user_id="owner_solice",
        action="view_status",
        object_type="tower_status",
        object_id="status",
        session_id="sess_low",
        route_path="/tower/status.json",
        clearance_decision={"allowed": True, "decision": "allow"},
    )
    _print("LOW RISK ACTION", low)

    assert low.get("decision") == "allow"
    assert low.get("step_up_required") is False

    need_step = evaluate_step_up_requirement(
        user_id="owner_solice",
        action="route_policy_change",
        object_type="route_policy",
        object_id="/admin",
        session_id="sess_092",
        route_path="/tower/security-command",
        clearance_decision={"allowed": True, "decision": "allow"},
        risk_context={"device_known": True, "ip_risk": "normal"},
    )
    _print("ROUTE POLICY CHANGE NEEDS STEP-UP", need_step)

    assert need_step.get("decision") == "step_up_required"
    assert need_step.get("step_up_required") is True
    assert "complete_step_up_auth" in need_step.get("required_actions", [])
    assert "owner_pin" in need_step.get("allowed_methods", [])

    challenge = create_step_up_challenge(
        user_id="owner_solice",
        action="route_policy_change",
        object_type="route_policy",
        object_id="/admin",
        session_id="sess_092",
        route_path="/tower/security-command",
        method="owner_pin",
        reason="Pack 092 test challenge for route policy change.",
    )
    _print("STEP-UP CHALLENGE CREATED", challenge)

    assert challenge.get("ok") is True
    assert challenge.get("status") == "pending"
    assert challenge.get("challenge_id")

    recent_before = has_recent_step_up(
        user_id="owner_solice",
        action="route_policy_change",
        object_type="route_policy",
        object_id="/admin",
        session_id="sess_092",
    )
    _print("RECENT STEP-UP BEFORE VERIFY", recent_before)
    assert recent_before.get("has_recent_step_up") is False

    wrong_user = verify_step_up_challenge(
        challenge_id=challenge.get("challenge_id"),
        user_id="beta_001",
        method="owner_pin",
    )
    _print("WRONG USER VERIFY DENIED", wrong_user)
    assert wrong_user.get("ok") is False
    assert wrong_user.get("reason_code") == "step_up_wrong_user"

    verified = verify_step_up_challenge(
        challenge_id=challenge.get("challenge_id"),
        user_id="owner_solice",
        method="owner_pin",
        verification_note="owner verified in Pack 092 test",
    )
    _print("STEP-UP CHALLENGE VERIFIED", verified)

    assert verified.get("ok") is True
    assert verified.get("decision") == "verified"

    recent_after = has_recent_step_up(
        user_id="owner_solice",
        action="route_policy_change",
        object_type="route_policy",
        object_id="/admin",
        session_id="sess_092",
    )
    _print("RECENT STEP-UP AFTER VERIFY", recent_after)

    assert recent_after.get("has_recent_step_up") is True
    assert recent_after.get("challenge_id") == challenge.get("challenge_id")

    allowed_after = evaluate_step_up_requirement(
        user_id="owner_solice",
        action="route_policy_change",
        object_type="route_policy",
        object_id="/admin",
        session_id="sess_092",
        route_path="/tower/security-command",
        clearance_decision={"allowed": True, "decision": "allow"},
        risk_context={"device_known": True, "ip_risk": "normal"},
    )
    _print("ROUTE POLICY CHANGE ALLOWED AFTER RECENT STEP-UP", allowed_after)

    assert allowed_after.get("decision") == "allow"
    assert allowed_after.get("step_up_required") is False
    assert allowed_after.get("reason_code") == "recent_step_up_verified"

    unknown = evaluate_step_up_requirement(
        user_id="owner_solice",
        action="mystery_sensitive_action_092",
        object_type="unknown",
        object_id="mystery",
        session_id="sess_unknown",
        route_path="/tower/security-command",
        clearance_decision={"allowed": True, "decision": "allow"},
    )
    _print("UNKNOWN ACTION DEFAULTS TO STEP-UP", unknown)

    assert unknown.get("decision") == "step_up_required"
    assert unknown.get("step_up_required") is True
    assert unknown.get("reason_code") == "step_up_required_for_unknown_sensitive_action"

    summary = summarize_step_up_auth(limit=30)
    _print("STEP-UP AUTH SUMMARY", summary)

    assert summary.get("ok") is True
    assert summary.get("readiness_score") == 100
    assert summary.get("readiness_label") == "Step-up authentication framework ready"
    assert "route_policy_change" in summary.get("policy_actions", [])
    assert "view_status" in summary.get("low_risk_actions", [])
    assert summary.get("total_events", 0) >= 7
    assert summary.get("total_challenges", 0) >= 1
    assert summary.get("by_decision", {}).get("step_up_required", 0) >= 1
    assert summary.get("by_decision", {}).get("verified", 0) >= 1
    assert summary.get("by_challenge_status", {}).get("verified", 0) >= 1

    serialized = json.dumps([
        export_policy,
        route_policy,
        low_policy,
        unknown_policy,
        denied_base,
        low,
        need_step,
        challenge,
        recent_before,
        wrong_user,
        verified,
        recent_after,
        allowed_after,
        unknown,
        summary,
    ], sort_keys=True, default=str)

    assert "tower_keycard=" not in serialized
    assert "SHOULD_NOT_SURVIVE" not in serialized
    assert "raw_token=" not in serialized
    assert '"raw_token":' not in serialized
    assert "owner_pin_value" not in serialized
    assert "Bearer SHOULD_NOT_SURVIVE" not in serialized
    assert "Soulaana:" in serialized

    for required_action in [
        "export",
        "route_policy_change",
        "live_mode_enable",
        "automated_mode_enable",
        "sensitive_reveal",
        "admin_override",
        "lockdown_disable",
    ]:
        assert required_action in STEP_UP_POLICY
        assert STEP_UP_POLICY[required_action]["required"] is True

    final = {
        "pack": "092",
        "status": "passed",
        "human_reason": "Step-up authentication framework now evaluates sensitive actions, creates challenges, verifies them, and honors recent verification.",
    }
    _print("PACK 092 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
