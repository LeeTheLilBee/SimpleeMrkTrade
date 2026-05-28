
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
from tower.quarantine_mode import reset_quarantine_for_test
from tower.redaction_reveal_system import reset_reveal_system_for_test
from tower.secrets_vault_boundary import reset_secrets_boundary_for_test
from tower.security_rehearsal_panel import (
    REHEARSAL_SCENARIOS,
    SECURITY_REHEARSAL_PANEL_PATH,
    run_security_rehearsal,
    reset_security_rehearsal_for_test,
    summarize_security_rehearsal,
    write_security_rehearsal_panel,
)
from tower.session_risk_scoring import reset_session_risk_for_test


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
        "session_risk": reset_session_risk_for_test(),
        "secrets": reset_secrets_boundary_for_test(),
        "reveal": reset_reveal_system_for_test(),
        "rehearsal": reset_security_rehearsal_for_test(),
    }
    _print("RESET SECURITY REHEARSAL DEPENDENCIES", reset_all)

    assert all(item.get("ok") for item in reset_all.values())

    assert "wrong_keycard" in REHEARSAL_SCENARIOS
    assert "expired_keycard" in REHEARSAL_SCENARIOS
    assert "export_attempt" in REHEARSAL_SCENARIOS
    assert "unknown_route" in REHEARSAL_SCENARIOS
    assert "high_risk_session" in REHEARSAL_SCENARIOS
    assert "live_mode_request" in REHEARSAL_SCENARIOS
    assert "admin_attempt" in REHEARSAL_SCENARIOS
    assert "secret_payload_attempt" in REHEARSAL_SCENARIOS
    assert "sensitive_reveal_attempt" in REHEARSAL_SCENARIOS

    report = run_security_rehearsal(actor_user_id="owner_solice", write_panel=True)
    _print("SECURITY REHEARSAL REPORT", report)

    assert report.get("ok") is True
    assert report.get("scenario_count") == len(REHEARSAL_SCENARIOS)
    assert report.get("pass_count") == len(REHEARSAL_SCENARIOS)
    assert report.get("fail_count") == 0
    assert report.get("readiness_score") == 100
    assert report.get("readiness_label") == "Security rehearsal panel ready"
    assert report.get("no_secret_leakage") is True
    assert report.get("leakage_scan", {}).get("ok") is True
    assert SECURITY_REHEARSAL_PANEL_PATH.exists()

    results = report.get("results", [])
    by_scenario = {item.get("scenario_id"): item for item in results}

    expected_families = {
        "wrong_keycard": {"deny", "step_up"},
        "expired_keycard": {"step_up"},
        "export_attempt": {"step_up", "throttle", "quarantine"},
        "unknown_route": {"quarantine", "deny"},
        "high_risk_session": {"lockdown", "deny"},
        "live_mode_request": {"step_up", "quarantine", "lockdown", "deny"},
        "admin_attempt": {"quarantine", "deny", "step_up"},
        "secret_payload_attempt": {"reject_raw_secret", "deny"},
        "sensitive_reveal_attempt": {"step_up_required", "summary_only"},
    }

    for scenario_id, allowed in expected_families.items():
        assert scenario_id in by_scenario, scenario_id
        item = by_scenario[scenario_id]
        assert item.get("ok") is True, scenario_id
        assert item.get("decision_family") in allowed, (scenario_id, item.get("decision_family"))

    _assert_no_secret_leakage(report)

    panel_result = write_security_rehearsal_panel(report)
    _print("SECURITY REHEARSAL PANEL WRITE", panel_result)

    assert panel_result.get("ok") is True
    assert SECURITY_REHEARSAL_PANEL_PATH.exists()

    html = SECURITY_REHEARSAL_PANEL_PATH.read_text(encoding="utf-8")
    assert "The Tower · Security Rehearsal Panel" in html
    assert "Wrong keycard" in html
    assert "High-risk session" in html
    assert "PASS" in html
    assert "SHOULD_NOT_SURVIVE" not in html
    assert "tower_keycard=" not in html

    summary = summarize_security_rehearsal(limit=80)
    _print("SECURITY REHEARSAL SUMMARY", summary)

    assert summary.get("ok") is True
    assert summary.get("readiness_score") == 100
    assert summary.get("readiness_label") == "Security rehearsal panel ready"
    assert summary.get("scenario_count") == len(REHEARSAL_SCENARIOS)
    assert summary.get("pass_count") == len(REHEARSAL_SCENARIOS)
    assert summary.get("fail_count") == 0
    assert summary.get("no_secret_leakage") is True
    assert summary.get("leakage_scan", {}).get("ok") is True
    assert summary.get("by_decision", {}).get("rehearsal_passed", 0) >= len(REHEARSAL_SCENARIOS)

    _assert_no_secret_leakage(summary)

    final = {
        "pack": "098",
        "status": "passed",
        "human_reason": "Security rehearsal panel safely simulates key security scenarios and verifies expected Tower responses without leaking secrets.",
    }
    _print("PACK 098 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
