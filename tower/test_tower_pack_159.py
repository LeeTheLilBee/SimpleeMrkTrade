
"""
PACK 159 fast test - Policy Change Approval Gate foundation.
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_159_payload_ready_and_gate_preview_only():
    mod = importlib.import_module("tower.policy_change_approval_gate")
    payload = mod.build_policy_change_approval_gate_payload(force_refresh=True)

    assert payload["pack_number"] == 159
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/policy-change-approval-gate.json"
    assert payload["source_endpoint"] == "/tower/policy-change-risk-score.json"

    assert payload["simulated_only"] is True
    assert payload["approval_preview_only"] is True
    assert payload["gate_preview_only"] is True
    assert payload["real_policy_change_executed"] is False
    assert payload["real_permission_change_executed"] is False
    assert payload["real_access_granted"] is False
    assert payload["real_enforcement_executed"] is False
    assert payload["real_audit_written"] is False
    assert payload["real_receipt_written"] is False
    assert payload["cached_non_recursive"] is True

    summary = payload["summary"]
    assert summary["readiness_score"] == 100
    assert summary["approval_gate_count"] >= 9
    assert summary["deny_auto_change_count"] >= 1
    assert summary["owner_review_required_count"] >= 1
    assert summary["step_up_required_count"] >= 1
    assert summary["privacy_review_required_count"] >= 1
    assert summary["quarantine_review_required_count"] >= 1
    assert summary["monitor_only_approval_count"] >= 1

    checks = payload["readiness_checks"]
    assert checks["pack_158_ready"] is True
    assert checks["has_gate_items"] is True
    assert checks["gate_count_matches_risk_items"] is True
    assert checks["all_simulated_only"] is True
    assert checks["all_approval_preview_only"] is True
    assert checks["all_gate_preview_only"] is True
    assert checks["no_real_policy_change"] is True
    assert checks["no_real_permission_change"] is True
    assert checks["no_real_access_granted"] is True
    assert checks["no_real_enforcement"] is True
    assert checks["no_real_audit_written"] is True
    assert checks["no_real_receipt_written"] is True
    assert checks["all_gate_ids_present"] is True
    assert checks["all_paths_present"] is True
    assert checks["all_reasons_present"] is True
    assert checks["all_required_approval_lists_present"] is True
    assert checks["auto_policy_change_never_allowed"] is True
    assert checks["real_policy_change_allowed_now_never"] is True
    assert checks["deny_auto_change_present"] is True
    assert checks["owner_review_required_present"] is True
    assert checks["step_up_required_present"] is True
    assert checks["privacy_review_required_present"] is True
    assert checks["quarantine_review_required_present"] is True
    assert checks["monitor_only_approval_present"] is True
    assert checks["required_path_coverage"] is True
    assert checks["cached_non_recursive"] is True


def test_pack_159_gate_items_have_required_fields():
    mod = importlib.import_module("tower.policy_change_approval_gate")
    payload = mod.build_policy_change_approval_gate_payload(force_refresh=True)

    required_paths = {
        "deny_automatic_change",
        "quarantine_review_required",
        "privacy_review_required",
        "owner_step_up_required",
        "owner_review_required",
        "monitor_only_approval",
    }
    observed_paths = set()

    for item in payload["approval_gate_items"]:
        observed_paths.add(item["approval_path"])

        assert item["approval_gate_id"].startswith("approval_gate_preview_")
        assert item["risk_score_id"].startswith("policy_change_risk_")
        assert item["recommendation_id"].startswith("least_privilege_preview_")
        assert item["recheck_item_id"].startswith("recheck_preview_")
        assert item["expiration_check_id"].startswith("expiration_preview_")
        assert item["vault_entry_id"].startswith("vault_preview_")
        assert item["ledger_entry_id"].startswith("ledger_preview_")
        assert item["receipt_preview_id"].startswith("receipt_preview_")

        assert item["scenario_id"]
        assert item["matched_policy_id"]
        assert item["decision"]
        assert isinstance(item["risk_score"], int)
        assert 0 <= item["risk_score"] <= 100
        assert item["risk_band"] in {"critical", "high", "medium", "low", "monitor"}
        assert item["recommended_access_level"]
        assert item["recommended_action"]

        assert item["approval_path"]
        assert item["approval_label"]
        assert item["approval_reason"]
        assert isinstance(item["required_approvals"], list)
        assert isinstance(item["blocked_until"], list)

        assert isinstance(item["owner_required"], bool)
        assert isinstance(item["step_up_required"], bool)
        assert isinstance(item["privacy_review_required"], bool)
        assert isinstance(item["quarantine_review_required"], bool)
        assert isinstance(item["auto_approval_allowed"], bool)

        assert item["auto_policy_change_allowed"] is False
        assert item["real_policy_change_allowed_now"] is False
        assert item["approval_preview_only"] is True
        assert item["gate_preview_only"] is True
        assert item["soulaana_approval_translation"]
        assert item["source_endpoint"] == "/tower/policy-change-risk-score.json"

        assert item["simulated_only"] is True
        assert item["real_policy_change_executed"] is False
        assert item["real_permission_change_executed"] is False
        assert item["real_access_granted"] is False
        assert item["real_enforcement_executed"] is False
        assert item["real_audit_written"] is False
        assert item["real_receipt_written"] is False

    assert required_paths.issubset(observed_paths)


def test_pack_159_decision_specific_approval_paths():
    mod = importlib.import_module("tower.policy_change_approval_gate")
    payload = mod.build_policy_change_approval_gate_payload(force_refresh=True)

    by_decision = payload["indexes"]["by_decision"]

    fail_closed = by_decision["fail_closed"][0]
    assert fail_closed["approval_path"] == "deny_automatic_change"
    assert fail_closed["owner_required"] is True
    assert fail_closed["step_up_required"] is True
    assert fail_closed["auto_policy_change_allowed"] is False

    quarantine = by_decision["quarantine"][0]
    assert quarantine["approval_path"] == "quarantine_review_required"
    assert quarantine["quarantine_review_required"] is True
    assert quarantine["owner_required"] is True

    redact = by_decision["redact"][0]
    assert redact["approval_path"] == "privacy_review_required"
    assert redact["privacy_review_required"] is True
    assert redact["step_up_required"] is True

    step_up = by_decision["step_up"][0]
    assert step_up["approval_path"] == "owner_step_up_required"
    assert step_up["step_up_required"] is True
    assert step_up["owner_required"] is True

    allow = by_decision["allow"][0]
    assert allow["approval_path"] == "monitor_only_approval"
    assert allow["auto_approval_allowed"] is True
    assert allow["auto_policy_change_allowed"] is False
    assert allow["real_policy_change_allowed_now"] is False

    deny_items = by_decision["deny"]
    assert all(item["approval_path"] == "owner_review_required" for item in deny_items)
    assert all(item["owner_required"] is True for item in deny_items)


def test_pack_159_indexes_and_special_lists_are_present():
    mod = importlib.import_module("tower.policy_change_approval_gate")
    payload = mod.build_policy_change_approval_gate_payload(force_refresh=True)

    indexes = payload["indexes"]
    assert indexes["by_approval_path"]
    assert indexes["by_risk_band"]
    assert indexes["by_decision"]
    assert indexes["by_required_approval"]

    assert payload["deny_auto_change"]
    assert payload["owner_review_required"]
    assert payload["step_up_required"]
    assert payload["privacy_review_required"]
    assert payload["quarantine_review_required"]
    assert payload["monitor_only_approval"]

    for item in payload["deny_auto_change"]:
        assert item["approval_path"] == "deny_automatic_change"

    for item in payload["owner_review_required"]:
        assert item["owner_required"] is True

    for item in payload["step_up_required"]:
        assert item["step_up_required"] is True

    for item in payload["privacy_review_required"]:
        assert item["privacy_review_required"] is True

    for item in payload["quarantine_review_required"]:
        assert item["quarantine_review_required"] is True

    for item in payload["monitor_only_approval"]:
        assert item["approval_path"] == "monitor_only_approval"


def test_pack_159_status_bridge_quick_action_and_unified_section():
    mod = importlib.import_module("tower.policy_change_approval_gate")

    bridge = mod.build_policy_change_approval_gate_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 159
    assert bridge["status"] == "ready"
    assert bridge["endpoint"] == "/tower/policy-change-approval-gate.json"
    assert bridge["readiness_score"] == 100
    assert bridge["approval_gate_count"] >= 9
    assert bridge["deny_auto_change_count"] >= 1
    assert bridge["owner_review_required_count"] >= 1
    assert bridge["step_up_required_count"] >= 1
    assert bridge["privacy_review_required_count"] >= 1
    assert bridge["quarantine_review_required_count"] >= 1
    assert bridge["monitor_only_approval_count"] >= 1
    assert bridge["simulated_only"] is True
    assert bridge["approval_preview_only"] is True
    assert bridge["gate_preview_only"] is True
    assert bridge["real_policy_change_executed"] is False
    assert bridge["real_permission_change_executed"] is False
    assert bridge["real_access_granted"] is False
    assert bridge["real_enforcement_executed"] is False
    assert bridge["real_audit_written"] is False
    assert bridge["real_receipt_written"] is False
    assert bridge["cached_non_recursive"] is True

    action = mod.build_policy_change_approval_gate_quick_action()
    assert action["id"] == "policy_change_approval_gate"
    assert action["href"] == "/tower/policy-change-approval-gate.json"
    assert action["simulated_only"] is True
    assert action["approval_preview_only"] is True
    assert action["gate_preview_only"] is True

    section = mod.build_policy_change_approval_gate_unified_owner_section()
    assert section["section_id"] == "policy_change_approval_gate"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/policy-change-approval-gate.json"
    assert section["simulated_only"] is True
    assert section["approval_preview_only"] is True
    assert section["gate_preview_only"] is True
    assert section["cached_non_recursive"] is True
    assert len(section["cards"]) >= 6


def test_pack_159_tower_status_bridge_available():
    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_159_policy_change_approval_gate_status_bridge")

    bridge = status.build_pack_159_policy_change_approval_gate_status_bridge()
    assert bridge["pack_number"] == 159
    assert bridge["status"] == "ready"
    assert bridge["endpoint"] == "/tower/policy-change-approval-gate.json"
    assert bridge["readiness_score"] == 100


def test_pack_159_quick_action_helper_available():
    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_159_policy_change_approval_gate_quick_action")
    assert hasattr(qa, "append_pack_159_policy_change_approval_gate_quick_action")

    action = qa.build_pack_159_policy_change_approval_gate_quick_action()
    assert action["id"] == "policy_change_approval_gate"
    assert action["href"] == "/tower/policy-change-approval-gate.json"

    actions = qa.append_pack_159_policy_change_approval_gate_quick_action([])
    assert isinstance(actions, list)
    assert any(item.get("id") == "policy_change_approval_gate" for item in actions)


def test_pack_159_unified_section_helper_available():
    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_159_policy_change_approval_gate_unified_section")
    assert hasattr(unified, "build_pack_159_policy_change_approval_gate_html_section")
    assert hasattr(unified, "append_pack_159_policy_change_approval_gate_section")

    section = unified.build_pack_159_policy_change_approval_gate_unified_section()
    assert section["section_id"] == "policy_change_approval_gate"
    assert section["href"] == "/tower/policy-change-approval-gate.json"

    sections = unified.append_pack_159_policy_change_approval_gate_section([])
    assert isinstance(sections, list)
    assert any(item.get("section_id") == "policy_change_approval_gate" for item in sections)


def test_pack_159_web_route_present_and_route_scanner_recognizes_it():
    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-gate.json" in app_text
    assert "tower_policy_change_approval_gate_json" in app_text
    assert "_pack_159_policy_change_approval_gate_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-gate.json" in route_text
    assert "_pack_159_policy_change_approval_gate_route_guard" in route_text


def test_pack_159_no_secret_leakage_in_payload():
    mod = importlib.import_module("tower.policy_change_approval_gate")
    payload_text = str(mod.build_policy_change_approval_gate_payload(force_refresh=True)).lower()

    forbidden_fragments = [
        "sk_live_",
        "sk_test_",
        "github_pat_",
        "ghp_",
        "xoxb-",
        "aws_secret_access_key",
        "private_key-----",
        "broker_token_value",
        "api_secret_value",
    ]

    for fragment in forbidden_fragments:
        assert fragment not in payload_text
