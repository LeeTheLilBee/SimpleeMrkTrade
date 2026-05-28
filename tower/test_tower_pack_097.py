
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

from tower.redaction_reveal_system import (
    build_redacted_summary,
    build_revealed_payload,
    evaluate_reveal_request,
    redact_payload_for_summary,
    reset_reveal_system_for_test,
    summarize_reveal_system,
)
from tower.step_up_auth import create_step_up_challenge, verify_step_up_challenge


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
    reset = reset_reveal_system_for_test()
    _print("RESET REVEAL SYSTEM", reset)
    assert reset.get("ok") is True

    payload = {
        "object_id": "worker_001",
        "object_type": "worker_profile",
        "title": "Worker profile",
        "status": "active",
        "category": "people",
        "email": "worker@example.com",
        "phone_number": "404-555-1212",
        "address": "123 Secret Lane",
        "payroll_amount": 2500.75,
        "bank_account": "123456789",
        "routing_number": "061000052",
        "private_notes": "Sensitive manager note",
        "raw_token": "SHOULD_NOT_SURVIVE",
        "api_key": "SHOULD_NOT_SURVIVE",
        "nested": {
            "safe": "visible",
            "password": "SHOULD_NOT_SURVIVE",
            "incident_detail": "Sensitive incident detail",
        },
    }

    redacted = redact_payload_for_summary(payload)
    _print("REDACTED PAYLOAD", redacted)

    assert redacted.get("email") == "[REDACTED_SENSITIVE]"
    assert redacted.get("phone_number") == "[REDACTED_SENSITIVE]"
    assert redacted.get("address") == "[REDACTED_SENSITIVE]"
    assert redacted.get("payroll_amount") == "[REDACTED_NUMBER]"
    assert "raw_token" not in redacted
    assert "api_key" not in redacted
    _assert_no_secret_leakage(redacted)

    summary = build_redacted_summary(
        object_type="worker_profile",
        object_id="worker_001",
        payload=payload,
        actor_user_id="owner_solice",
        app_id="teller",
        reason="pack097_summary_test",
    )
    _print("DEFAULT REDACTED SUMMARY", summary)

    assert summary.get("ok") is True
    assert summary.get("decision") == "summary_only"
    assert summary.get("mode") == "redacted_summary"
    assert summary.get("redacted_payload", {}).get("email") == "[REDACTED_SENSITIVE]"
    assert summary.get("leakage_scan", {}).get("ok") is True
    _assert_no_secret_leakage(summary)

    denied_base = evaluate_reveal_request(
        actor_user_id="owner_solice",
        action="reveal_payroll_detail",
        object_type="worker_profile",
        object_id="worker_001",
        app_id="teller",
        payload=payload,
        clearance_decision={"allowed": False, "decision": "deny"},
        object_permission={"allowed": True, "decision": "allow"},
        reveal_fields=["email", "payroll_amount", "bank_account"],
        metadata={"session_id": "sess_reveal_097", "tower_keycard": "SHOULD_NOT_SURVIVE"},
    )
    _print("REVEAL DENIED BASE CLEARANCE", denied_base)

    assert denied_base.get("decision") == "summary_only"
    assert denied_base.get("reveal_allowed") is False
    assert denied_base.get("reason_code") == "base_clearance_required_for_reveal"
    assert "obtain_base_clearance" in denied_base.get("required_actions", [])
    _assert_no_secret_leakage(denied_base)

    denied_object = evaluate_reveal_request(
        actor_user_id="owner_solice",
        action="reveal_payroll_detail",
        object_type="worker_profile",
        object_id="worker_001",
        app_id="teller",
        payload=payload,
        clearance_decision={"allowed": True, "decision": "allow"},
        object_permission={"allowed": False, "decision": "deny"},
        reveal_fields=["email", "payroll_amount", "bank_account"],
        metadata={"session_id": "sess_reveal_097"},
    )
    _print("REVEAL DENIED OBJECT PERMISSION", denied_object)

    assert denied_object.get("decision") == "summary_only"
    assert denied_object.get("reveal_allowed") is False
    assert denied_object.get("reason_code") == "object_permission_required_for_reveal"
    assert "obtain_object_permission" in denied_object.get("required_actions", [])
    _assert_no_secret_leakage(denied_object)

    needs_step = evaluate_reveal_request(
        actor_user_id="owner_solice",
        action="reveal_payroll_detail",
        object_type="worker_profile",
        object_id="worker_001",
        app_id="teller",
        payload=payload,
        clearance_decision={"allowed": True, "decision": "allow"},
        object_permission={"allowed": True, "decision": "allow"},
        reveal_fields=["email", "payroll_amount", "bank_account"],
        metadata={"session_id": "sess_reveal_097"},
    )
    _print("REVEAL NEEDS STEP-UP", needs_step)

    assert needs_step.get("decision") == "step_up_required"
    assert needs_step.get("reveal_allowed") is False
    assert needs_step.get("reason_code") == "step_up_required_for_sensitive_reveal"
    assert "complete_step_up_auth" in needs_step.get("required_actions", [])
    _assert_no_secret_leakage(needs_step)

    challenge = create_step_up_challenge(
        user_id="owner_solice",
        action="sensitive_reveal",
        object_type="worker_profile",
        object_id="worker_001",
        session_id="sess_reveal_097",
        route_path="/tower/security-command",
        method="owner_pin",
        reason="Pack 097 reveal step-up test.",
    )
    _print("REVEAL STEP-UP CHALLENGE", challenge)
    assert challenge.get("ok") is True

    verified = verify_step_up_challenge(
        challenge_id=challenge.get("challenge_id"),
        user_id="owner_solice",
        method="owner_pin",
        verification_note="Pack 097 owner verified reveal.",
    )
    _print("REVEAL STEP-UP VERIFIED", verified)
    assert verified.get("ok") is True

    allowed = evaluate_reveal_request(
        actor_user_id="owner_solice",
        action="reveal_payroll_detail",
        object_type="worker_profile",
        object_id="worker_001",
        app_id="teller",
        payload=payload,
        clearance_decision={"allowed": True, "decision": "allow"},
        object_permission={"allowed": True, "decision": "allow"},
        step_up_decision={"ok": True, "decision": "allow", "reason_code": "recent_step_up_verified"},
        reveal_fields=["email", "payroll_amount", "bank_account", "routing_number", "raw_token"],
        metadata={"session_id": "sess_reveal_097"},
    )
    _print("REVEAL ALLOWED", allowed)

    assert allowed.get("decision") == "reveal_allowed"
    assert allowed.get("reveal_allowed") is True
    assert allowed.get("revealed", {}).get("payload", {}).get("email") == "worker@example.com"
    assert allowed.get("revealed", {}).get("payload", {}).get("payroll_amount") == 2500.75
    assert allowed.get("revealed", {}).get("payload", {}).get("bank_account") == "123456789"
    assert "raw_token" not in allowed.get("revealed", {}).get("payload", {})
    assert allowed.get("revealed", {}).get("secret_values_never_revealed") is True
    _assert_no_secret_leakage(allowed)

    partial = build_revealed_payload(
        payload=payload,
        reveal_fields=["email"],
    )
    _print("PARTIAL REVEAL PAYLOAD", partial)

    assert partial.get("payload", {}).get("email") == "worker@example.com"
    assert partial.get("payload", {}).get("phone_number") == "[NOT_REQUESTED]"
    assert "raw_token" not in partial.get("payload", {})
    _assert_no_secret_leakage(partial)

    summary_report = summarize_reveal_system(limit=50)
    _print("REVEAL SYSTEM SUMMARY", summary_report)

    assert summary_report.get("ok") is True
    assert summary_report.get("readiness_score") == 100
    assert summary_report.get("readiness_label") == "Redaction-by-default reveal system ready"
    assert summary_report.get("receipt_count", 0) >= 4
    assert summary_report.get("by_decision", {}).get("reveal_denied", 0) >= 2
    assert summary_report.get("by_decision", {}).get("reveal_step_up_required", 0) >= 1
    assert summary_report.get("by_decision", {}).get("reveal_allowed", 0) >= 1
    assert summary_report.get("no_secret_leakage") is True
    _assert_no_secret_leakage(summary_report)

    final = {
        "pack": "097",
        "status": "passed",
        "human_reason": "Redaction-by-default reveal system returns summaries first, gates sensitive reveal by clearance/object permission/step-up, and records receipts without leaking secrets.",
    }
    _print("PACK 097 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
