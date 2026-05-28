
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

from tower.emergency_lockdown import load_emergency_lockdown_state, reset_emergency_lockdown_for_test
from tower.quarantine_mode import summarize_quarantine_mode, reset_quarantine_for_test
from tower.session_risk_scoring import (
    apply_session_risk_decision,
    evaluate_session_risk,
    register_known_session_baseline,
    reset_session_risk_for_test,
    sanitize_session_risk_event_store,
    summarize_session_risk,
)


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
    reset_risk = reset_session_risk_for_test()

    _print("RESET SECURITY STATES", {
        "lockdown": reset_lockdown,
        "quarantine": reset_quarantine,
        "risk": reset_risk,
    })

    assert reset_lockdown.get("ok") is True
    assert reset_quarantine.get("ok") is True
    assert reset_risk.get("ok") is True

    baseline = register_known_session_baseline(
        user_id="owner_solice",
        device_id="known_device_001",
        ip_address="10.0.0.5",
        location_hint="GA",
        actor_user_id="owner_solice",
        metadata={"raw_token": "SHOULD_NOT_SURVIVE", "pack": "095"},
    )
    _print("KNOWN SESSION BASELINE", baseline)

    assert baseline.get("ok") is True
    assert baseline.get("decision") == "baseline_registered"

    allow = evaluate_session_risk(
        user_id="owner_solice",
        session_id="sess_allow_095",
        device_id="known_device_001",
        ip_address="10.0.0.5",
        location_hint="GA",
        route_path="/tower/status.json",
        action="view_status",
        method="GET",
        request_count_1m=3,
        denied_count_5m=0,
        failed_keycard_count_5m=0,
        metadata={"tower_keycard": "SHOULD_NOT_SURVIVE"},
    )
    _print("RISK ALLOW", allow)

    assert allow.get("decision") == "allow"
    assert allow.get("allowed") is True
    assert allow.get("risk_score", 100) < 20

    step_up = evaluate_session_risk(
        user_id="owner_solice",
        session_id="sess_step_095",
        device_id="known_device_001",
        ip_address="10.0.0.5",
        location_hint="GA",
        route_path="/export",
        action="export",
        method="POST",
        request_count_1m=5,
        denied_count_5m=0,
        failed_keycard_count_5m=0,
    )
    _print("RISK STEP-UP", step_up)

    assert step_up.get("decision") == "step_up"
    assert step_up.get("risk_score", 0) >= 20
    assert "complete_step_up_auth" in step_up.get("required_actions", [])

    throttle = evaluate_session_risk(
        user_id="owner_solice",
        session_id="sess_throttle_095",
        device_id="known_device_001",
        ip_address="10.0.0.5",
        location_hint="GA",
        route_path="/signals",
        action="view_summary",
        method="GET",
        request_count_1m=65,
        denied_count_5m=3,
        failed_keycard_count_5m=0,
    )
    _print("RISK THROTTLE", throttle)

    assert throttle.get("decision") == "throttle"
    assert "slow_request_rate" in throttle.get("required_actions", [])

    quarantine = evaluate_session_risk(
        user_id="owner_solice",
        session_id="sess_quarantine_095",
        device_id="unknown_device_095",
        ip_address="10.0.0.99",
        location_hint="GA",
        route_path="/admin",
        action="admin_override",
        method="POST",
        request_count_1m=35,
        denied_count_5m=5,
        failed_keycard_count_5m=1,
        admin_action_count_10m=2,
    )
    _print("RISK QUARANTINE", quarantine)

    assert quarantine.get("decision") == "quarantine"
    assert "quarantine_subject" in quarantine.get("required_actions", [])

    lockdown = evaluate_session_risk(
        user_id="owner_solice",
        session_id="sess_lockdown_095",
        device_id="unknown_device_lock_095",
        ip_address="10.0.0.123",
        location_hint="UNKNOWN",
        route_path="/broker/live",
        action="broker_action",
        method="POST",
        request_count_1m=125,
        denied_count_5m=20,
        failed_keycard_count_5m=10,
        live_or_broker_attempt_count_10m=3,
        suspicious_pattern_count=5,
    )
    _print("RISK LOCKDOWN", lockdown)

    assert lockdown.get("decision") in {"lockdown", "deny"}
    assert lockdown.get("risk_score", 0) >= 80

    deny = evaluate_session_risk(
        user_id="beta_001",
        session_id="sess_deny_095",
        device_id="bad_device_095",
        ip_address="203.0.113.99",
        location_hint="UNKNOWN",
        route_path="/admin",
        action="admin_override",
        method="POST",
        request_count_1m=120,
        denied_count_5m=10,
        failed_keycard_count_5m=4,
        base_clearance_decision={"allowed": False, "decision": "deny"},
    )
    _print("RISK DENY", deny)

    assert deny.get("decision") == "deny"
    assert "deny_request" in deny.get("required_actions", [])

    auto_step = evaluate_session_risk(
        user_id="owner_solice",
        session_id="sess_auto_step_095",
        device_id="known_device_001",
        ip_address="10.0.0.5",
        location_hint="GA",
        route_path="/export",
        action="export",
        method="POST",
        request_count_1m=5,
        auto_apply=True,
    )
    _print("AUTO APPLY STEP-UP", auto_step)

    assert auto_step.get("decision") == "step_up"
    assert auto_step.get("auto_apply_result", {}).get("decision") == "step_up_requested"

    auto_quarantine = evaluate_session_risk(
        user_id="beta_auto_quar",
        session_id="sess_auto_quar_095",
        device_id="unknown_auto_quar",
        ip_address="198.51.100.50",
        location_hint="UNKNOWN",
        route_path="/admin",
        action="admin_override",
        method="POST",
        request_count_1m=35,
        denied_count_5m=5,
        failed_keycard_count_5m=1,
        admin_action_count_10m=2,
        auto_apply=True,
    )
    _print("AUTO APPLY QUARANTINE", auto_quarantine)

    assert auto_quarantine.get("decision") == "quarantine"
    assert auto_quarantine.get("auto_apply_result", {}).get("decision") == "quarantine_applied"

    quarantine_summary = summarize_quarantine_mode(limit=50)
    _print("QUARANTINE AFTER AUTO APPLY", quarantine_summary)

    assert quarantine_summary.get("active_case_count", 0) >= 1
    assert quarantine_summary.get("by_decision", {}).get("quarantine_activated", 0) >= 1

    auto_lockdown = evaluate_session_risk(
        user_id="beta_auto_lock",
        session_id="sess_auto_lock_095",
        device_id="bad_device_auto_lock",
        ip_address="203.0.113.200",
        location_hint="UNKNOWN",
        route_path="/disable-security",
        action="disable_security",
        method="POST",
        request_count_1m=150,
        denied_count_5m=25,
        failed_keycard_count_5m=12,
        suspicious_pattern_count=5,
        auto_apply=True,
    )
    _print("AUTO APPLY LOCKDOWN", auto_lockdown)

    assert auto_lockdown.get("decision") in {"lockdown", "deny"}
    if auto_lockdown.get("decision") == "lockdown":
        assert auto_lockdown.get("auto_apply_result", {}).get("decision") == "lockdown_applied"

    lockdown_state = load_emergency_lockdown_state()
    _print("LOCKDOWN STATE AFTER AUTO APPLY", lockdown_state)

    if auto_lockdown.get("decision") == "lockdown":
        assert lockdown_state.get("lockdown_active") is True

    # Reset lockdown after proving auto-apply so future packs are not stuck.
    reset_emergency_lockdown_for_test()

    store_clean = sanitize_session_risk_event_store()
    _print("SESSION RISK STORE SANITIZED", store_clean)

    assert store_clean.get("ok") is True

    summary = summarize_session_risk(limit=80)
    _print("SESSION RISK SUMMARY", summary)

    assert summary.get("ok") is True
    assert summary.get("readiness_score") == 100
    assert summary.get("readiness_label") == "Session/device/IP risk scoring foundation ready"
    assert summary.get("total_events", 0) >= 8
    assert summary.get("by_decision", {}).get("allow", 0) >= 1
    assert summary.get("by_decision", {}).get("step_up", 0) >= 1
    assert summary.get("by_decision", {}).get("throttle", 0) >= 1
    assert summary.get("by_decision", {}).get("quarantine", 0) >= 1
    assert summary.get("by_decision", {}).get("deny", 0) >= 1
    assert summary.get("no_sensitive_key_leakage") is True

    serialized = json.dumps([
        reset_lockdown,
        reset_quarantine,
        reset_risk,
        baseline,
        allow,
        step_up,
        throttle,
        quarantine,
        lockdown,
        deny,
        auto_step,
        auto_quarantine,
        quarantine_summary,
        auto_lockdown,
        lockdown_state,
        store_clean,
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
        "pack": "095",
        "status": "passed",
        "human_reason": "Session/device/IP risk scoring foundation can score requests and recommend allow, step_up, throttle, quarantine, lockdown, or deny.",
    }
    _print("PACK 095 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
