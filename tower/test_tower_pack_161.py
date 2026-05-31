
"""
PACK 161 fast test - Policy Change Approval Receipt Vault Preview / Index.
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_161_payload_ready_and_vault_index_preview_only():
    mod = importlib.import_module("tower.policy_change_approval_receipt_vault_index")
    payload = mod.build_policy_change_approval_receipt_vault_index_payload(force_refresh=True)

    assert payload["pack_number"] == 161
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/policy-change-approval-receipt-vault-index.json"
    assert payload["source_endpoint"] == "/tower/policy-change-approval-receipt-preview.json"

    assert payload["simulated_only"] is True
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
    assert payload["cached_non_recursive"] is True

    summary = payload["summary"]
    assert summary["readiness_score"] == 100
    assert summary["vault_item_count"] >= 9
    assert summary["ledger_index_count"] >= 9
    assert summary["critical_denial_count"] >= 1
    assert summary["quarantine_review_count"] >= 1
    assert summary["privacy_review_count"] >= 1
    assert summary["owner_step_up_count"] >= 1
    assert summary["owner_review_count"] >= 1
    assert summary["monitor_acknowledgement_count"] >= 1

    checks = payload["readiness_checks"]
    assert checks["pack_160_ready"] is True
    assert checks["has_vault_items"] is True
    assert checks["vault_count_matches_receipt_previews"] is True
    assert checks["all_simulated_only"] is True
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

    assert checks["all_vault_ids_present"] is True
    assert checks["all_ledger_index_ids_present"] is True
    assert checks["all_buckets_present"] is True
    assert checks["all_index_status_present"] is True
    assert checks["all_search_tokens_present"] is True
    assert checks["all_evidence_summaries_present"] is True

    assert checks["critical_denials_present"] is True
    assert checks["quarantine_reviews_present"] is True
    assert checks["privacy_reviews_present"] is True
    assert checks["owner_step_up_present"] is True
    assert checks["owner_reviews_present"] is True
    assert checks["monitor_acknowledgements_present"] is True
    assert checks["required_bucket_coverage"] is True
    assert checks["cached_non_recursive"] is True


def test_pack_161_vault_items_have_required_fields():
    mod = importlib.import_module("tower.policy_change_approval_receipt_vault_index")
    payload = mod.build_policy_change_approval_receipt_vault_index_payload(force_refresh=True)

    required_buckets = {
        "critical_denials",
        "quarantine_reviews",
        "privacy_reviews",
        "owner_step_up",
        "owner_reviews",
        "monitor_acknowledgements",
    }
    observed_buckets = set()

    for item in payload["vault_items"]:
        observed_buckets.add(item["vault_bucket"])

        assert item["vault_preview_id"].startswith("approval_receipt_vault_preview_")
        assert item["ledger_index_id"].startswith("approval_receipt_ledger_index_")
        assert item["approval_receipt_preview_id"].startswith("approval_receipt_preview_")
        assert item["approval_gate_id"].startswith("approval_gate_preview_")
        assert item["risk_score_id"].startswith("policy_change_risk_")
        assert item["recommendation_id"].startswith("least_privilege_preview_")
        assert item["recheck_item_id"].startswith("recheck_preview_")
        assert item["expiration_check_id"].startswith("expiration_preview_")
        assert item["source_vault_entry_id"].startswith("vault_preview_")
        assert item["source_ledger_entry_id"].startswith("ledger_preview_")
        assert item["source_receipt_preview_id"].startswith("receipt_preview_")

        assert item["scenario_id"]
        assert item["matched_policy_id"]
        assert item["decision"]
        assert isinstance(item["risk_score"], int)
        assert 0 <= item["risk_score"] <= 100
        assert item["risk_band"] in {"critical", "high", "medium", "low", "monitor"}
        assert item["approval_path"]
        assert item["receipt_type"]
        assert item["receipt_label"]
        assert item["receipt_severity"]

        assert item["vault_bucket"]
        assert item["vault_bucket_label"]
        assert item["vault_bucket_description"]
        assert item["retention_class"]
        assert item["index_status"]
        assert item["index_reason"]
        assert isinstance(item["bucket_owner_review_required"], bool)

        assert isinstance(item["search_tokens"], list)
        assert len(item["search_tokens"]) >= 1
        assert isinstance(item["evidence_summary"], dict)
        assert item["soulaana_vault_translation"]
        assert item["source_endpoint"] == "/tower/policy-change-approval-receipt-preview.json"

        assert item["simulated_only"] is True
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


def test_pack_161_receipt_type_specific_vault_buckets():
    mod = importlib.import_module("tower.policy_change_approval_receipt_vault_index")
    payload = mod.build_policy_change_approval_receipt_vault_index_payload(force_refresh=True)

    by_receipt_type = payload["indexes"]["by_receipt_type"]

    auto_denied = by_receipt_type["auto_change_denied"][0]
    assert auto_denied["vault_bucket"] == "critical_denials"
    assert auto_denied["index_status"] == "critical_denial_indexed"

    quarantine = by_receipt_type["quarantine_review_required"][0]
    assert quarantine["vault_bucket"] == "quarantine_reviews"
    assert quarantine["index_status"] == "quarantine_review_indexed"

    privacy = by_receipt_type["privacy_review_required"][0]
    assert privacy["vault_bucket"] == "privacy_reviews"
    assert privacy["index_status"] == "privacy_review_indexed"

    owner_step_up = by_receipt_type["owner_step_up_required"][0]
    assert owner_step_up["vault_bucket"] == "owner_step_up"
    assert owner_step_up["index_status"] == "owner_step_up_indexed"

    owner_review = by_receipt_type["owner_review_required"][0]
    assert owner_review["vault_bucket"] == "owner_reviews"
    assert owner_review["index_status"] == "owner_review_indexed"

    monitor = by_receipt_type["monitor_only_ack"][0]
    assert monitor["vault_bucket"] == "monitor_acknowledgements"
    assert monitor["index_status"] == "monitor_ack_indexed"


def test_pack_161_indexes_and_special_lists_are_present():
    mod = importlib.import_module("tower.policy_change_approval_receipt_vault_index")
    payload = mod.build_policy_change_approval_receipt_vault_index_payload(force_refresh=True)

    indexes = payload["indexes"]
    assert indexes["by_bucket"]
    assert indexes["by_receipt_type"]
    assert indexes["by_receipt_severity"]
    assert indexes["by_approval_path"]
    assert indexes["by_index_status"]
    assert indexes["by_retention_class"]
    assert indexes["by_decision"]

    assert payload["critical_denials"]
    assert payload["quarantine_reviews"]
    assert payload["privacy_reviews"]
    assert payload["owner_step_up"]
    assert payload["owner_reviews"]
    assert payload["monitor_acknowledgements"]

    for item in payload["critical_denials"]:
        assert item["vault_bucket"] == "critical_denials"

    for item in payload["quarantine_reviews"]:
        assert item["vault_bucket"] == "quarantine_reviews"

    for item in payload["privacy_reviews"]:
        assert item["vault_bucket"] == "privacy_reviews"

    for item in payload["owner_step_up"]:
        assert item["vault_bucket"] == "owner_step_up"

    for item in payload["owner_reviews"]:
        assert item["vault_bucket"] == "owner_reviews"

    for item in payload["monitor_acknowledgements"]:
        assert item["vault_bucket"] == "monitor_acknowledgements"


def test_pack_161_status_bridge_quick_action_and_unified_section():
    mod = importlib.import_module("tower.policy_change_approval_receipt_vault_index")

    bridge = mod.build_policy_change_approval_receipt_vault_index_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 161
    assert bridge["status"] == "ready"
    assert bridge["endpoint"] == "/tower/policy-change-approval-receipt-vault-index.json"
    assert bridge["readiness_score"] == 100
    assert bridge["vault_item_count"] >= 9
    assert bridge["ledger_index_count"] >= 9
    assert bridge["critical_denial_count"] >= 1
    assert bridge["quarantine_review_count"] >= 1
    assert bridge["privacy_review_count"] >= 1
    assert bridge["owner_step_up_count"] >= 1
    assert bridge["owner_review_count"] >= 1
    assert bridge["monitor_acknowledgement_count"] >= 1

    assert bridge["simulated_only"] is True
    assert bridge["vault_preview_only"] is True
    assert bridge["index_preview_only"] is True
    assert bridge["receipt_preview_only"] is True
    assert bridge["approval_preview_only"] is True
    assert bridge["evidence_preview_only"] is True
    assert bridge["real_vault_written"] is False
    assert bridge["cached_non_recursive"] is True

    action = mod.build_policy_change_approval_receipt_vault_index_quick_action()
    assert action["id"] == "policy_change_approval_receipt_vault_index"
    assert action["href"] == "/tower/policy-change-approval-receipt-vault-index.json"
    assert action["simulated_only"] is True
    assert action["vault_preview_only"] is True

    section = mod.build_policy_change_approval_receipt_vault_index_unified_owner_section()
    assert section["section_id"] == "policy_change_approval_receipt_vault_index"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/policy-change-approval-receipt-vault-index.json"
    assert section["simulated_only"] is True
    assert section["vault_preview_only"] is True
    assert section["cached_non_recursive"] is True
    assert len(section["cards"]) >= 6


def test_pack_161_tower_status_bridge_available():
    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_161_policy_change_approval_receipt_vault_index_status_bridge")

    bridge = status.build_pack_161_policy_change_approval_receipt_vault_index_status_bridge()
    assert bridge["pack_number"] == 161
    assert bridge["status"] == "ready"
    assert bridge["endpoint"] == "/tower/policy-change-approval-receipt-vault-index.json"
    assert bridge["readiness_score"] == 100


def test_pack_161_quick_action_helper_available():
    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_161_policy_change_approval_receipt_vault_index_quick_action")
    assert hasattr(qa, "append_pack_161_policy_change_approval_receipt_vault_index_quick_action")

    action = qa.build_pack_161_policy_change_approval_receipt_vault_index_quick_action()
    assert action["id"] == "policy_change_approval_receipt_vault_index"
    assert action["href"] == "/tower/policy-change-approval-receipt-vault-index.json"

    actions = qa.append_pack_161_policy_change_approval_receipt_vault_index_quick_action([])
    assert isinstance(actions, list)
    assert any(item.get("id") == "policy_change_approval_receipt_vault_index" for item in actions)


def test_pack_161_unified_section_helper_available():
    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_161_policy_change_approval_receipt_vault_index_unified_section")
    assert hasattr(unified, "build_pack_161_policy_change_approval_receipt_vault_index_html_section")
    assert hasattr(unified, "append_pack_161_policy_change_approval_receipt_vault_index_section")

    section = unified.build_pack_161_policy_change_approval_receipt_vault_index_unified_section()
    assert section["section_id"] == "policy_change_approval_receipt_vault_index"
    assert section["href"] == "/tower/policy-change-approval-receipt-vault-index.json"

    sections = unified.append_pack_161_policy_change_approval_receipt_vault_index_section([])
    assert isinstance(sections, list)
    assert any(item.get("section_id") == "policy_change_approval_receipt_vault_index" for item in sections)


def test_pack_161_web_route_present_and_route_scanner_recognizes_it():
    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-vault-index.json" in app_text
    assert "tower_policy_change_approval_receipt_vault_index_json" in app_text
    assert "_pack_161_policy_change_approval_receipt_vault_index_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-vault-index.json" in route_text
    assert "_pack_161_policy_change_approval_receipt_vault_index_route_guard" in route_text


def test_pack_161_no_secret_leakage_in_payload():
    mod = importlib.import_module("tower.policy_change_approval_receipt_vault_index")
    payload_text = str(mod.build_policy_change_approval_receipt_vault_index_payload(force_refresh=True)).lower()

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
