
"""
PACK 164 fast test - Approval Receipt Owner Review Queue.
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_164_payload_ready_and_owner_review_preview_only():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_review_queue")
    payload = mod.build_policy_change_approval_receipt_owner_review_queue_payload(force_refresh=True)

    assert payload["pack_number"] == 164
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/policy-change-approval-receipt-owner-review-queue.json"
    assert payload["source_endpoint"] == "/tower/policy-change-approval-receipt-renewal-recheck-queue.json"

    assert payload["simulated_only"] is True
    assert payload["owner_review_preview_only"] is True
    assert payload["queue_preview_only"] is True
    assert payload["renewal_preview_only"] is True
    assert payload["recheck_preview_only"] is True
    assert payload["expiration_preview_only"] is True
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
    assert payload["real_queue_action_executed"] is False
    assert payload["real_owner_review_completed"] is False
    assert payload["real_owner_approval_executed"] is False
    assert payload["real_owner_rejection_executed"] is False
    assert payload["real_owner_acknowledgement_executed"] is False
    assert payload["cached_non_recursive"] is True

    summary = payload["summary"]
    assert summary["readiness_score"] == 100
    assert summary["owner_review_item_count"] >= 9
    assert summary["critical_owner_recheck_count"] >= 1
    assert summary["quarantine_owner_recheck_count"] >= 1
    assert summary["fresh_recheck_review_count"] >= 1
    assert summary["renewal_review_count"] >= 1
    assert summary["monitor_acknowledgement_count"] >= 1
    assert summary["owner_review_required_count"] >= 1
    assert summary["owner_step_up_required_count"] >= 1
    assert summary["monitor_acknowledgement_item_count"] >= 1

    checks = payload["readiness_checks"]
    assert checks["pack_163_ready"] is True
    assert checks["has_owner_review_items"] is True
    assert checks["owner_review_count_matches_queue_items"] is True
    assert checks["all_simulated_only"] is True
    assert checks["all_owner_review_preview_only"] is True
    assert checks["all_queue_preview_only"] is True
    assert checks["all_renewal_preview_only"] is True
    assert checks["all_recheck_preview_only"] is True
    assert checks["all_expiration_preview_only"] is True
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
    assert checks["no_real_queue_action_executed"] is True
    assert checks["no_real_owner_review_completed"] is True
    assert checks["no_real_owner_approval_executed"] is True
    assert checks["no_real_owner_rejection_executed"] is True
    assert checks["no_real_owner_acknowledgement_executed"] is True

    assert checks["owner_review_action_never_allowed_now"] is True
    assert checks["owner_step_up_never_allowed_now"] is True
    assert checks["all_owner_review_ids_present"] is True
    assert checks["all_categories_present"] is True
    assert checks["all_required_owner_actions_present"] is True
    assert checks["all_required_steps_present"] is True

    assert checks["critical_owner_recheck_present"] is True
    assert checks["quarantine_owner_recheck_present"] is True
    assert checks["fresh_recheck_review_present"] is True
    assert checks["renewal_review_present"] is True
    assert checks["monitor_acknowledgement_present"] is True
    assert checks["owner_review_required_items_present"] is True
    assert checks["owner_step_up_required_items_present"] is True
    assert checks["monitor_acknowledgement_items_present"] is True
    assert checks["required_category_coverage"] is True
    assert checks["required_action_coverage"] is True
    assert checks["cached_non_recursive"] is True


def test_pack_164_owner_review_items_have_required_fields():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_review_queue")
    payload = mod.build_policy_change_approval_receipt_owner_review_queue_payload(force_refresh=True)

    required_categories = {
        "critical_owner_recheck",
        "quarantine_owner_recheck",
        "fresh_recheck_review",
        "renewal_review",
        "monitor_acknowledgement",
    }
    observed_categories = set()

    for item in payload["owner_review_items"]:
        observed_categories.add(item["owner_review_category"])

        assert item["owner_review_item_id"].startswith("approval_receipt_owner_review_preview_")
        assert item["queue_item_id"].startswith("approval_receipt_queue_preview_")
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
        assert item["priority"]
        assert item["expiration_state"]
        assert item["queue_lane"]
        assert item["queue_priority"]
        assert item["recommended_action"]
        assert item["renewal_status"]

        assert item["owner_review_category"]
        assert item["owner_review_label"]
        assert item["owner_review_description"]
        assert item["owner_review_priority"] in {"critical", "high", "medium", "monitor"}
        assert item["required_owner_action"]
        assert isinstance(item["owner_step_up_required"], bool)
        assert isinstance(item["owner_review_required"], bool)
        assert item["owner_review_reason"]
        assert isinstance(item["required_owner_review_steps"], list)
        assert item["required_owner_review_steps"]
        assert item["owner_review_status"] in {"owner_review_pending", "monitor_acknowledgement_pending"}

        assert item["owner_review_action_allowed_now"] is False
        assert item["owner_step_up_allowed_now"] is False
        assert item["real_owner_review_completed"] is False
        assert item["real_owner_approval_executed"] is False
        assert item["real_owner_rejection_executed"] is False
        assert item["real_owner_acknowledgement_executed"] is False
        assert item["soulaana_owner_review_translation"]

        assert item["source_endpoint"] == "/tower/policy-change-approval-receipt-renewal-recheck-queue.json"

        assert item["simulated_only"] is True
        assert item["owner_review_preview_only"] is True
        assert item["queue_preview_only"] is True
        assert item["renewal_preview_only"] is True
        assert item["recheck_preview_only"] is True
        assert item["expiration_preview_only"] is True
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
        assert item["real_expiration_enforced"] is False
        assert item["real_recheck_executed"] is False
        assert item["real_renewal_executed"] is False
        assert item["real_queue_action_executed"] is False

    assert required_categories.issubset(observed_categories)


def test_pack_164_category_specific_owner_review_behavior():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_review_queue")
    payload = mod.build_policy_change_approval_receipt_owner_review_queue_payload(force_refresh=True)

    by_category = payload["indexes"]["by_owner_review_category"]

    critical = by_category["critical_owner_recheck"]
    assert len(critical) >= 1
    assert all(item["required_owner_action"] == "complete_owner_recheck" for item in critical)
    assert all(item["owner_step_up_required"] is True for item in critical)
    assert all(item["owner_review_required"] is True for item in critical)

    quarantine = by_category["quarantine_owner_recheck"]
    assert len(quarantine) >= 1
    assert all(item["required_owner_action"] == "complete_quarantine_recheck" for item in quarantine)
    assert all(item["owner_step_up_required"] is True for item in quarantine)
    assert all(item["owner_review_required"] is True for item in quarantine)

    fresh = by_category["fresh_recheck_review"]
    assert len(fresh) >= 1
    assert all(item["required_owner_action"] == "complete_fresh_recheck" for item in fresh)
    assert all(item["owner_step_up_required"] is True for item in fresh)
    assert all(item["owner_review_required"] is True for item in fresh)

    renewal = by_category["renewal_review"]
    assert len(renewal) >= 1
    assert all(item["required_owner_action"] == "review_renewal_preview" for item in renewal)
    assert all(item["owner_step_up_required"] is False for item in renewal)
    assert all(item["owner_review_required"] is True for item in renewal)

    monitor = by_category["monitor_acknowledgement"]
    assert len(monitor) >= 1
    assert all(item["required_owner_action"] == "acknowledge_monitor_only" for item in monitor)
    assert all(item["owner_step_up_required"] is False for item in monitor)
    assert all(item["owner_review_required"] is False for item in monitor)


def test_pack_164_indexes_and_special_lists_are_present():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_review_queue")
    payload = mod.build_policy_change_approval_receipt_owner_review_queue_payload(force_refresh=True)

    indexes = payload["indexes"]
    assert indexes["by_owner_review_category"]
    assert indexes["by_owner_review_priority"]
    assert indexes["by_required_owner_action"]
    assert indexes["by_owner_review_status"]
    assert indexes["by_queue_lane"]
    assert indexes["by_vault_bucket"]

    assert payload["critical_owner_recheck"]
    assert payload["quarantine_owner_recheck"]
    assert payload["fresh_recheck_review"]
    assert payload["renewal_review"]
    assert payload["monitor_acknowledgement"]
    assert payload["owner_review_required_items"]
    assert payload["owner_step_up_required_items"]
    assert payload["monitor_acknowledgement_items"]

    for item in payload["critical_owner_recheck"]:
        assert item["owner_review_category"] == "critical_owner_recheck"

    for item in payload["quarantine_owner_recheck"]:
        assert item["owner_review_category"] == "quarantine_owner_recheck"

    for item in payload["fresh_recheck_review"]:
        assert item["owner_review_category"] == "fresh_recheck_review"

    for item in payload["renewal_review"]:
        assert item["owner_review_category"] == "renewal_review"

    for item in payload["monitor_acknowledgement"]:
        assert item["owner_review_category"] == "monitor_acknowledgement"

    for item in payload["owner_review_required_items"]:
        assert item["owner_review_required"] is True

    for item in payload["owner_step_up_required_items"]:
        assert item["owner_step_up_required"] is True

    for item in payload["monitor_acknowledgement_items"]:
        assert item["owner_review_required"] is False


def test_pack_164_status_bridge_quick_action_and_unified_section():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_review_queue")

    bridge = mod.build_policy_change_approval_receipt_owner_review_queue_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 164
    assert bridge["status"] == "ready"
    assert bridge["endpoint"] == "/tower/policy-change-approval-receipt-owner-review-queue.json"
    assert bridge["readiness_score"] == 100
    assert bridge["owner_review_item_count"] >= 9
    assert bridge["critical_owner_recheck_count"] >= 1
    assert bridge["quarantine_owner_recheck_count"] >= 1
    assert bridge["fresh_recheck_review_count"] >= 1
    assert bridge["renewal_review_count"] >= 1
    assert bridge["monitor_acknowledgement_count"] >= 1
    assert bridge["owner_review_required_count"] >= 1
    assert bridge["owner_step_up_required_count"] >= 1

    assert bridge["simulated_only"] is True
    assert bridge["owner_review_preview_only"] is True
    assert bridge["queue_preview_only"] is True
    assert bridge["real_owner_review_completed"] is False
    assert bridge["real_owner_approval_executed"] is False
    assert bridge["real_owner_rejection_executed"] is False
    assert bridge["real_owner_acknowledgement_executed"] is False
    assert bridge["cached_non_recursive"] is True

    action = mod.build_policy_change_approval_receipt_owner_review_queue_quick_action()
    assert action["id"] == "policy_change_approval_receipt_owner_review_queue"
    assert action["href"] == "/tower/policy-change-approval-receipt-owner-review-queue.json"
    assert action["simulated_only"] is True
    assert action["owner_review_preview_only"] is True

    section = mod.build_policy_change_approval_receipt_owner_review_queue_unified_owner_section()
    assert section["section_id"] == "policy_change_approval_receipt_owner_review_queue"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/policy-change-approval-receipt-owner-review-queue.json"
    assert section["simulated_only"] is True
    assert section["owner_review_preview_only"] is True
    assert section["cached_non_recursive"] is True
    assert len(section["cards"]) >= 6


def test_pack_164_tower_status_bridge_available():
    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_164_policy_change_approval_receipt_owner_review_queue_status_bridge")

    bridge = status.build_pack_164_policy_change_approval_receipt_owner_review_queue_status_bridge()
    assert bridge["pack_number"] == 164
    assert bridge["status"] == "ready"
    assert bridge["endpoint"] == "/tower/policy-change-approval-receipt-owner-review-queue.json"
    assert bridge["readiness_score"] == 100


def test_pack_164_quick_action_helper_available():
    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_164_policy_change_approval_receipt_owner_review_queue_quick_action")
    assert hasattr(qa, "append_pack_164_policy_change_approval_receipt_owner_review_queue_quick_action")

    action = qa.build_pack_164_policy_change_approval_receipt_owner_review_queue_quick_action()
    assert action["id"] == "policy_change_approval_receipt_owner_review_queue"
    assert action["href"] == "/tower/policy-change-approval-receipt-owner-review-queue.json"

    actions = qa.append_pack_164_policy_change_approval_receipt_owner_review_queue_quick_action([])
    assert isinstance(actions, list)
    assert any(item.get("id") == "policy_change_approval_receipt_owner_review_queue" for item in actions)


def test_pack_164_unified_section_helper_available():
    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_164_policy_change_approval_receipt_owner_review_queue_unified_section")
    assert hasattr(unified, "build_pack_164_policy_change_approval_receipt_owner_review_queue_html_section")
    assert hasattr(unified, "append_pack_164_policy_change_approval_receipt_owner_review_queue_section")

    section = unified.build_pack_164_policy_change_approval_receipt_owner_review_queue_unified_section()
    assert section["section_id"] == "policy_change_approval_receipt_owner_review_queue"
    assert section["href"] == "/tower/policy-change-approval-receipt-owner-review-queue.json"

    sections = unified.append_pack_164_policy_change_approval_receipt_owner_review_queue_section([])
    assert isinstance(sections, list)
    assert any(item.get("section_id") == "policy_change_approval_receipt_owner_review_queue" for item in sections)


def test_pack_164_web_route_present_and_route_scanner_recognizes_it():
    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-owner-review-queue.json" in app_text
    assert "tower_policy_change_approval_receipt_owner_review_queue_json" in app_text
    assert "_pack_164_policy_change_approval_receipt_owner_review_queue_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-owner-review-queue.json" in route_text
    assert "_pack_164_policy_change_approval_receipt_owner_review_queue_route_guard" in route_text


def test_pack_164_no_secret_leakage_in_payload():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_review_queue")
    payload_text = str(mod.build_policy_change_approval_receipt_owner_review_queue_payload(force_refresh=True)).lower()

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
