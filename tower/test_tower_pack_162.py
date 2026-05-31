
"""
PACK 162 fast test - Approval Receipt Expiration Rules.
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_162_payload_ready_and_expiration_preview_only():
    mod = importlib.import_module("tower.policy_change_approval_receipt_expiration_rules")
    payload = mod.build_policy_change_approval_receipt_expiration_rules_payload(force_refresh=True)

    assert payload["pack_number"] == 162
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/policy-change-approval-receipt-expiration-rules.json"
    assert payload["source_endpoint"] == "/tower/policy-change-approval-receipt-vault-index.json"

    assert payload["simulated_only"] is True
    assert payload["expiration_preview_only"] is True
    assert payload["renewal_preview_only"] is True
    assert payload["recheck_preview_only"] is True
    assert payload["vault_preview_only"] is True
    assert payload["index_preview_only"] is True
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
    assert payload["real_vault_written"] is False
    assert payload["real_expiration_enforced"] is False
    assert payload["real_recheck_executed"] is False
    assert payload["real_renewal_executed"] is False
    assert payload["cached_non_recursive"] is True

    summary = payload["summary"]
    assert summary["readiness_score"] == 100
    assert summary["expiration_item_count"] >= 9
    assert summary["critical_count"] >= 1
    assert summary["high_count"] >= 1
    assert summary["medium_count"] >= 1
    assert summary["monitor_count"] >= 1
    assert summary["recheck_required_count"] >= 1
    assert summary["renewal_allowed_count"] >= 1
    assert summary["owner_review_required_count"] >= 1

    checks = payload["readiness_checks"]
    assert checks["pack_161_ready"] is True
    assert checks["has_expiration_items"] is True
    assert checks["expiration_count_matches_vault_items"] is True
    assert checks["all_simulated_only"] is True
    assert checks["all_expiration_preview_only"] is True
    assert checks["all_renewal_preview_only"] is True
    assert checks["all_recheck_preview_only"] is True
    assert checks["all_vault_preview_only"] is True
    assert checks["all_index_preview_only"] is True
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
    assert checks["no_real_vault_written"] is True
    assert checks["no_real_expiration_enforced"] is True
    assert checks["no_real_recheck_executed"] is True
    assert checks["no_real_renewal_executed"] is True

    assert checks["expiration_enforcement_never_allowed_now"] is True
    assert checks["auto_renewal_never_allowed_now"] is True
    assert checks["all_expiration_ids_present"] is True
    assert checks["all_rules_present"] is True
    assert checks["all_windows_present"] is True
    assert checks["all_states_present"] is True

    assert checks["critical_items_present"] is True
    assert checks["high_items_present"] is True
    assert checks["medium_items_present"] is True
    assert checks["monitor_items_present"] is True
    assert checks["recheck_required_items_present"] is True
    assert checks["renewal_allowed_items_present"] is True
    assert checks["owner_review_required_items_present"] is True
    assert checks["required_bucket_coverage"] is True
    assert checks["required_state_coverage"] is True
    assert checks["cached_non_recursive"] is True


def test_pack_162_expiration_items_have_required_fields():
    mod = importlib.import_module("tower.policy_change_approval_receipt_expiration_rules")
    payload = mod.build_policy_change_approval_receipt_expiration_rules_payload(force_refresh=True)

    required_buckets = {
        "critical_denials",
        "quarantine_reviews",
        "privacy_reviews",
        "owner_step_up",
        "owner_reviews",
        "monitor_acknowledgements",
    }
    observed_buckets = set()

    for item in payload["expiration_items"]:
        observed_buckets.add(item["vault_bucket"])

        assert item["expiration_preview_id"].startswith("approval_receipt_expiration_preview_")
        assert item["vault_preview_id"].startswith("approval_receipt_vault_preview_")
        assert item["ledger_index_id"].startswith("approval_receipt_ledger_index_")
        assert item["approval_receipt_preview_id"].startswith("approval_receipt_preview_")
        assert item["approval_gate_id"].startswith("approval_gate_preview_")
        assert item["risk_score_id"].startswith("policy_change_risk_")
        assert item["recommendation_id"].startswith("least_privilege_preview_")

        assert item["scenario_id"]
        assert item["matched_policy_id"]
        assert item["decision"]
        assert isinstance(item["risk_score"], int)
        assert 0 <= item["risk_score"] <= 100
        assert item["risk_band"] in {"critical", "high", "medium", "low", "monitor"}
        assert item["approval_path"]
        assert item["receipt_type"]
        assert item["receipt_severity"]
        assert item["vault_bucket"]
        assert item["retention_class"]
        assert item["index_status"]

        assert item["expiration_rule_bucket"]
        assert item["expiration_rule_label"]
        assert item["priority"] in {"critical", "high", "medium", "monitor"}
        assert isinstance(item["ttl_hours"], int)
        assert item["ttl_hours"] > 0
        assert isinstance(item["warning_hours"], int)
        assert item["warning_hours"] > 0
        assert item["created_at"].endswith("Z")
        assert item["warning_at"].endswith("Z")
        assert item["expires_at"].endswith("Z")
        assert item["expiration_state"]
        assert isinstance(item["recheck_required"], bool)
        assert isinstance(item["renewal_allowed"], bool)
        assert isinstance(item["owner_review_required"], bool)

        assert item["expiration_enforcement_allowed_now"] is False
        assert item["auto_renewal_allowed_now"] is False
        assert item["real_expiration_enforced"] is False
        assert item["real_recheck_executed"] is False
        assert item["real_renewal_executed"] is False

        assert item["soulaana_expiration_translation"]
        assert item["source_endpoint"] == "/tower/policy-change-approval-receipt-vault-index.json"

        assert item["simulated_only"] is True
        assert item["expiration_preview_only"] is True
        assert item["renewal_preview_only"] is True
        assert item["recheck_preview_only"] is True
        assert item["vault_preview_only"] is True
        assert item["index_preview_only"] is True
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
        assert item["real_vault_written"] is False

    assert required_buckets.issubset(observed_buckets)


def test_pack_162_bucket_specific_rules():
    mod = importlib.import_module("tower.policy_change_approval_receipt_expiration_rules")
    payload = mod.build_policy_change_approval_receipt_expiration_rules_payload(force_refresh=True)

    by_bucket = payload["indexes"]["by_bucket"]

    critical = by_bucket["critical_denials"][0]
    assert critical["priority"] == "critical"
    assert critical["ttl_hours"] == 12
    assert critical["recheck_required"] is True
    assert critical["renewal_allowed"] is False
    assert critical["expiration_state"] == "expires_fast_recheck_required"

    quarantine = by_bucket["quarantine_reviews"][0]
    assert quarantine["priority"] == "high"
    assert quarantine["ttl_hours"] == 24
    assert quarantine["recheck_required"] is True
    assert quarantine["renewal_allowed"] is False
    assert quarantine["expiration_state"] == "expires_soon_recheck_required"

    privacy = by_bucket["privacy_reviews"][0]
    assert privacy["priority"] == "medium"
    assert privacy["ttl_hours"] == 48
    assert privacy["recheck_required"] is True
    assert privacy["renewal_allowed"] is True
    assert privacy["expiration_state"] == "recheck_required_before_reuse"

    owner_step_up = by_bucket["owner_step_up"][0]
    assert owner_step_up["priority"] == "medium"
    assert owner_step_up["ttl_hours"] == 24
    assert owner_step_up["recheck_required"] is True
    assert owner_step_up["renewal_allowed"] is False

    owner_review = by_bucket["owner_reviews"][0]
    assert owner_review["priority"] == "medium"
    assert owner_review["ttl_hours"] == 72
    assert owner_review["recheck_required"] is False
    assert owner_review["renewal_allowed"] is True
    assert owner_review["expiration_state"] == "renewal_allowed_before_expiration"

    monitor = by_bucket["monitor_acknowledgements"][0]
    assert monitor["priority"] == "monitor"
    assert monitor["ttl_hours"] == 168
    assert monitor["owner_review_required"] is False
    assert monitor["renewal_allowed"] is True
    assert monitor["expiration_state"] == "renewal_allowed_before_expiration"


def test_pack_162_indexes_and_special_lists_are_present():
    mod = importlib.import_module("tower.policy_change_approval_receipt_expiration_rules")
    payload = mod.build_policy_change_approval_receipt_expiration_rules_payload(force_refresh=True)

    indexes = payload["indexes"]
    assert indexes["by_priority"]
    assert indexes["by_bucket"]
    assert indexes["by_expiration_state"]
    assert indexes["by_receipt_type"]
    assert indexes["by_renewal_allowed"]
    assert indexes["by_recheck_required"]

    assert payload["critical_items"]
    assert payload["high_items"]
    assert payload["medium_items"]
    assert payload["monitor_items"]
    assert payload["recheck_required_items"]
    assert payload["renewal_allowed_items"]
    assert payload["owner_review_required_items"]

    for item in payload["critical_items"]:
        assert item["priority"] == "critical"

    for item in payload["high_items"]:
        assert item["priority"] == "high"

    for item in payload["medium_items"]:
        assert item["priority"] == "medium"

    for item in payload["monitor_items"]:
        assert item["priority"] == "monitor"

    for item in payload["recheck_required_items"]:
        assert item["recheck_required"] is True

    for item in payload["renewal_allowed_items"]:
        assert item["renewal_allowed"] is True

    for item in payload["owner_review_required_items"]:
        assert item["owner_review_required"] is True


def test_pack_162_status_bridge_quick_action_and_unified_section():
    mod = importlib.import_module("tower.policy_change_approval_receipt_expiration_rules")

    bridge = mod.build_policy_change_approval_receipt_expiration_rules_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 162
    assert bridge["status"] == "ready"
    assert bridge["endpoint"] == "/tower/policy-change-approval-receipt-expiration-rules.json"
    assert bridge["readiness_score"] == 100
    assert bridge["expiration_item_count"] >= 9
    assert bridge["critical_count"] >= 1
    assert bridge["high_count"] >= 1
    assert bridge["medium_count"] >= 1
    assert bridge["monitor_count"] >= 1
    assert bridge["recheck_required_count"] >= 1
    assert bridge["renewal_allowed_count"] >= 1
    assert bridge["owner_review_required_count"] >= 1

    assert bridge["simulated_only"] is True
    assert bridge["expiration_preview_only"] is True
    assert bridge["renewal_preview_only"] is True
    assert bridge["recheck_preview_only"] is True
    assert bridge["real_expiration_enforced"] is False
    assert bridge["real_recheck_executed"] is False
    assert bridge["real_renewal_executed"] is False
    assert bridge["cached_non_recursive"] is True

    action = mod.build_policy_change_approval_receipt_expiration_rules_quick_action()
    assert action["id"] == "policy_change_approval_receipt_expiration_rules"
    assert action["href"] == "/tower/policy-change-approval-receipt-expiration-rules.json"
    assert action["simulated_only"] is True
    assert action["expiration_preview_only"] is True

    section = mod.build_policy_change_approval_receipt_expiration_rules_unified_owner_section()
    assert section["section_id"] == "policy_change_approval_receipt_expiration_rules"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/policy-change-approval-receipt-expiration-rules.json"
    assert section["simulated_only"] is True
    assert section["expiration_preview_only"] is True
    assert section["cached_non_recursive"] is True
    assert len(section["cards"]) >= 6


def test_pack_162_tower_status_bridge_available():
    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_162_policy_change_approval_receipt_expiration_rules_status_bridge")

    bridge = status.build_pack_162_policy_change_approval_receipt_expiration_rules_status_bridge()
    assert bridge["pack_number"] == 162
    assert bridge["status"] == "ready"
    assert bridge["endpoint"] == "/tower/policy-change-approval-receipt-expiration-rules.json"
    assert bridge["readiness_score"] == 100


def test_pack_162_quick_action_helper_available():
    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_162_policy_change_approval_receipt_expiration_rules_quick_action")
    assert hasattr(qa, "append_pack_162_policy_change_approval_receipt_expiration_rules_quick_action")

    action = qa.build_pack_162_policy_change_approval_receipt_expiration_rules_quick_action()
    assert action["id"] == "policy_change_approval_receipt_expiration_rules"
    assert action["href"] == "/tower/policy-change-approval-receipt-expiration-rules.json"

    actions = qa.append_pack_162_policy_change_approval_receipt_expiration_rules_quick_action([])
    assert isinstance(actions, list)
    assert any(item.get("id") == "policy_change_approval_receipt_expiration_rules" for item in actions)


def test_pack_162_unified_section_helper_available():
    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_162_policy_change_approval_receipt_expiration_rules_unified_section")
    assert hasattr(unified, "build_pack_162_policy_change_approval_receipt_expiration_rules_html_section")
    assert hasattr(unified, "append_pack_162_policy_change_approval_receipt_expiration_rules_section")

    section = unified.build_pack_162_policy_change_approval_receipt_expiration_rules_unified_section()
    assert section["section_id"] == "policy_change_approval_receipt_expiration_rules"
    assert section["href"] == "/tower/policy-change-approval-receipt-expiration-rules.json"

    sections = unified.append_pack_162_policy_change_approval_receipt_expiration_rules_section([])
    assert isinstance(sections, list)
    assert any(item.get("section_id") == "policy_change_approval_receipt_expiration_rules" for item in sections)


def test_pack_162_web_route_present_and_route_scanner_recognizes_it():
    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-expiration-rules.json" in app_text
    assert "tower_policy_change_approval_receipt_expiration_rules_json" in app_text
    assert "_pack_162_policy_change_approval_receipt_expiration_rules_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-expiration-rules.json" in route_text
    assert "_pack_162_policy_change_approval_receipt_expiration_rules_route_guard" in route_text


def test_pack_162_no_secret_leakage_in_payload():
    mod = importlib.import_module("tower.policy_change_approval_receipt_expiration_rules")
    payload_text = str(mod.build_policy_change_approval_receipt_expiration_rules_payload(force_refresh=True)).lower()

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
