
"""
PACK 160 fast test - Policy Change Approval Receipt Preview foundation.
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_160_payload_ready_and_receipt_preview_only():
    mod = importlib.import_module("tower.policy_change_approval_receipt_preview")
    payload = mod.build_policy_change_approval_receipt_preview_payload(force_refresh=True)

    assert payload["pack_number"] == 160
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/policy-change-approval-receipt-preview.json"
    assert payload["source_endpoint"] == "/tower/policy-change-approval-gate.json"

    assert payload["simulated_only"] is True
    assert payload["receipt_preview_only"] is True
    assert payload["approval_preview_only"] is True
    assert payload["evidence_preview_only"] is True
    assert payload["real_approval_executed"] is False
    assert payload["real_policy_change_executed"] is False
    assert payload["real_permission_change_executed"] is False
    assert payload["real_access_granted"] is False
    assert payload["real_enforcement_executed"] is False
    assert payload["real_audit_written"] is False
    assert payload["real_receipt_written"] is False
    assert payload["real_archive_written"] is False
    assert payload["cached_non_recursive"] is True

    summary = payload["summary"]
    assert summary["readiness_score"] == 100
    assert summary["receipt_preview_count"] >= 9
    assert summary["auto_change_denied_count"] >= 1
    assert summary["quarantine_review_receipt_count"] >= 1
    assert summary["privacy_review_receipt_count"] >= 1
    assert summary["owner_step_up_receipt_count"] >= 1
    assert summary["owner_review_receipt_count"] >= 1
    assert summary["monitor_only_receipt_count"] >= 1

    checks = payload["readiness_checks"]
    assert checks["pack_159_ready"] is True
    assert checks["has_receipt_previews"] is True
    assert checks["receipt_count_matches_gate_items"] is True
    assert checks["all_simulated_only"] is True
    assert checks["all_receipt_preview_only"] is True
    assert checks["all_approval_preview_only"] is True
    assert checks["all_evidence_preview_only"] is True
    assert checks["no_real_approval_executed"] is True
    assert checks["no_real_policy_change"] is True
    assert checks["no_real_permission_change"] is True
    assert checks["no_real_access_granted"] is True
    assert checks["no_real_enforcement"] is True
    assert checks["no_real_audit_written"] is True
    assert checks["no_real_receipt_written"] is True
    assert checks["no_real_archive_written"] is True
    assert checks["all_receipt_ids_present"] is True
    assert checks["all_receipt_types_present"] is True
    assert checks["all_receipt_reasons_present"] is True
    assert checks["all_evidence_preview_present"] is True
    assert checks["all_control_preview_present"] is True
    assert checks["auto_change_denied_present"] is True
    assert checks["quarantine_review_receipts_present"] is True
    assert checks["privacy_review_receipts_present"] is True
    assert checks["owner_step_up_receipts_present"] is True
    assert checks["owner_review_receipts_present"] is True
    assert checks["monitor_only_receipts_present"] is True
    assert checks["required_receipt_type_coverage"] is True
    assert checks["cached_non_recursive"] is True


def test_pack_160_receipt_previews_have_required_fields():
    mod = importlib.import_module("tower.policy_change_approval_receipt_preview")
    payload = mod.build_policy_change_approval_receipt_preview_payload(force_refresh=True)

    required_receipt_types = {
        "auto_change_denied",
        "quarantine_review_required",
        "privacy_review_required",
        "owner_step_up_required",
        "owner_review_required",
        "monitor_only_ack",
    }
    observed_receipt_types = set()

    for item in payload["receipt_previews"]:
        observed_receipt_types.add(item["receipt_type"])

        assert item["approval_receipt_preview_id"].startswith("approval_receipt_preview_")
        assert item["approval_gate_id"].startswith("approval_gate_preview_")
        assert item["risk_score_id"].startswith("policy_change_risk_")
        assert item["recommendation_id"].startswith("least_privilege_preview_")
        assert item["recheck_item_id"].startswith("recheck_preview_")
        assert item["expiration_check_id"].startswith("expiration_preview_")
        assert item["vault_entry_id"].startswith("vault_preview_")
        assert item["ledger_entry_id"].startswith("ledger_preview_")
        assert item["source_receipt_preview_id"].startswith("receipt_preview_")

        assert item["scenario_id"]
        assert item["matched_policy_id"]
        assert item["decision"]
        assert isinstance(item["risk_score"], int)
        assert 0 <= item["risk_score"] <= 100
        assert item["risk_band"] in {"critical", "high", "medium", "low", "monitor"}
        assert item["approval_path"]
        assert item["approval_label"]

        assert item["receipt_type"]
        assert item["receipt_label"]
        assert item["receipt_severity"]
        assert item["receipt_reason"]

        assert isinstance(item["evidence_preview"], dict)
        assert isinstance(item["control_preview"], dict)
        assert isinstance(item["required_approvals"], list)
        assert isinstance(item["blocked_until"], list)

        assert item["soulaana_receipt_translation"]
        assert item["source_endpoint"] == "/tower/policy-change-approval-gate.json"

        assert item["simulated_only"] is True
        assert item["receipt_preview_only"] is True
        assert item["approval_preview_only"] is True
        assert item["evidence_preview_only"] is True
        assert item["real_approval_executed"] is False
        assert item["real_policy_change_executed"] is False
        assert item["real_permission_change_executed"] is False
        assert item["real_access_granted"] is False
        assert item["real_enforcement_executed"] is False
        assert item["real_audit_written"] is False
        assert item["real_receipt_written"] is False
        assert item["real_archive_written"] is False

    assert required_receipt_types.issubset(observed_receipt_types)


def test_pack_160_approval_path_specific_receipt_types():
    mod = importlib.import_module("tower.policy_change_approval_receipt_preview")
    payload = mod.build_policy_change_approval_receipt_preview_payload(force_refresh=True)

    by_approval_path = payload["indexes"]["by_approval_path"]

    auto_denied = by_approval_path["deny_automatic_change"][0]
    assert auto_denied["receipt_type"] == "auto_change_denied"
    assert auto_denied["receipt_severity"] == "critical"

    quarantine = by_approval_path["quarantine_review_required"][0]
    assert quarantine["receipt_type"] == "quarantine_review_required"
    assert quarantine["control_preview"]["quarantine_review_required"] is True

    privacy = by_approval_path["privacy_review_required"][0]
    assert privacy["receipt_type"] == "privacy_review_required"
    assert privacy["control_preview"]["privacy_review_required"] is True

    owner_step_up = by_approval_path["owner_step_up_required"][0]
    assert owner_step_up["receipt_type"] == "owner_step_up_required"
    assert owner_step_up["control_preview"]["step_up_required"] is True

    owner_review = by_approval_path["owner_review_required"][0]
    assert owner_review["receipt_type"] == "owner_review_required"
    assert owner_review["control_preview"]["owner_review_required"] is True

    monitor = by_approval_path["monitor_only_approval"][0]
    assert monitor["receipt_type"] == "monitor_only_ack"
    assert monitor["control_preview"]["auto_approval_allowed"] is True
    assert monitor["control_preview"]["real_policy_change_allowed_now"] is False
    assert monitor["control_preview"]["receipt_write_allowed_now"] is False


def test_pack_160_indexes_and_special_lists_are_present():
    mod = importlib.import_module("tower.policy_change_approval_receipt_preview")
    payload = mod.build_policy_change_approval_receipt_preview_payload(force_refresh=True)

    indexes = payload["indexes"]
    assert indexes["by_receipt_type"]
    assert indexes["by_receipt_severity"]
    assert indexes["by_approval_path"]
    assert indexes["by_decision"]

    assert payload["auto_change_denied"]
    assert payload["quarantine_review_receipts"]
    assert payload["privacy_review_receipts"]
    assert payload["owner_step_up_receipts"]
    assert payload["owner_review_receipts"]
    assert payload["monitor_only_receipts"]

    for item in payload["auto_change_denied"]:
        assert item["receipt_type"] == "auto_change_denied"

    for item in payload["quarantine_review_receipts"]:
        assert item["receipt_type"] == "quarantine_review_required"

    for item in payload["privacy_review_receipts"]:
        assert item["receipt_type"] == "privacy_review_required"

    for item in payload["owner_step_up_receipts"]:
        assert item["receipt_type"] == "owner_step_up_required"

    for item in payload["owner_review_receipts"]:
        assert item["receipt_type"] == "owner_review_required"

    for item in payload["monitor_only_receipts"]:
        assert item["receipt_type"] == "monitor_only_ack"


def test_pack_160_status_bridge_quick_action_and_unified_section():
    mod = importlib.import_module("tower.policy_change_approval_receipt_preview")

    bridge = mod.build_policy_change_approval_receipt_preview_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 160
    assert bridge["status"] == "ready"
    assert bridge["endpoint"] == "/tower/policy-change-approval-receipt-preview.json"
    assert bridge["readiness_score"] == 100
    assert bridge["receipt_preview_count"] >= 9
    assert bridge["auto_change_denied_count"] >= 1
    assert bridge["quarantine_review_receipt_count"] >= 1
    assert bridge["privacy_review_receipt_count"] >= 1
    assert bridge["owner_step_up_receipt_count"] >= 1
    assert bridge["owner_review_receipt_count"] >= 1
    assert bridge["monitor_only_receipt_count"] >= 1

    assert bridge["simulated_only"] is True
    assert bridge["receipt_preview_only"] is True
    assert bridge["approval_preview_only"] is True
    assert bridge["evidence_preview_only"] is True
    assert bridge["real_approval_executed"] is False
    assert bridge["real_policy_change_executed"] is False
    assert bridge["real_permission_change_executed"] is False
    assert bridge["real_access_granted"] is False
    assert bridge["real_enforcement_executed"] is False
    assert bridge["real_audit_written"] is False
    assert bridge["real_receipt_written"] is False
    assert bridge["real_archive_written"] is False
    assert bridge["cached_non_recursive"] is True

    action = mod.build_policy_change_approval_receipt_preview_quick_action()
    assert action["id"] == "policy_change_approval_receipt_preview"
    assert action["href"] == "/tower/policy-change-approval-receipt-preview.json"
    assert action["simulated_only"] is True
    assert action["receipt_preview_only"] is True

    section = mod.build_policy_change_approval_receipt_preview_unified_owner_section()
    assert section["section_id"] == "policy_change_approval_receipt_preview"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/policy-change-approval-receipt-preview.json"
    assert section["simulated_only"] is True
    assert section["receipt_preview_only"] is True
    assert section["cached_non_recursive"] is True
    assert len(section["cards"]) >= 6


def test_pack_160_tower_status_bridge_available():
    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_160_policy_change_approval_receipt_preview_status_bridge")

    bridge = status.build_pack_160_policy_change_approval_receipt_preview_status_bridge()
    assert bridge["pack_number"] == 160
    assert bridge["status"] == "ready"
    assert bridge["endpoint"] == "/tower/policy-change-approval-receipt-preview.json"
    assert bridge["readiness_score"] == 100


def test_pack_160_quick_action_helper_available():
    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_160_policy_change_approval_receipt_preview_quick_action")
    assert hasattr(qa, "append_pack_160_policy_change_approval_receipt_preview_quick_action")

    action = qa.build_pack_160_policy_change_approval_receipt_preview_quick_action()
    assert action["id"] == "policy_change_approval_receipt_preview"
    assert action["href"] == "/tower/policy-change-approval-receipt-preview.json"

    actions = qa.append_pack_160_policy_change_approval_receipt_preview_quick_action([])
    assert isinstance(actions, list)
    assert any(item.get("id") == "policy_change_approval_receipt_preview" for item in actions)


def test_pack_160_unified_section_helper_available():
    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_160_policy_change_approval_receipt_preview_unified_section")
    assert hasattr(unified, "build_pack_160_policy_change_approval_receipt_preview_html_section")
    assert hasattr(unified, "append_pack_160_policy_change_approval_receipt_preview_section")

    section = unified.build_pack_160_policy_change_approval_receipt_preview_unified_section()
    assert section["section_id"] == "policy_change_approval_receipt_preview"
    assert section["href"] == "/tower/policy-change-approval-receipt-preview.json"

    sections = unified.append_pack_160_policy_change_approval_receipt_preview_section([])
    assert isinstance(sections, list)
    assert any(item.get("section_id") == "policy_change_approval_receipt_preview" for item in sections)


def test_pack_160_web_route_present_and_route_scanner_recognizes_it():
    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-preview.json" in app_text
    assert "tower_policy_change_approval_receipt_preview_json" in app_text
    assert "_pack_160_policy_change_approval_receipt_preview_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-preview.json" in route_text
    assert "_pack_160_policy_change_approval_receipt_preview_route_guard" in route_text


def test_pack_160_no_secret_leakage_in_payload():
    mod = importlib.import_module("tower.policy_change_approval_receipt_preview")
    payload_text = str(mod.build_policy_change_approval_receipt_preview_payload(force_refresh=True)).lower()

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
