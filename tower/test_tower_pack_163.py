
"""
PACK 163 fast test - Approval Receipt Renewal / Recheck Queue.
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_163_payload_ready_and_queue_preview_only():
    mod = importlib.import_module("tower.policy_change_approval_receipt_renewal_recheck_queue")
    payload = mod.build_policy_change_approval_receipt_renewal_recheck_queue_payload(force_refresh=True)

    assert payload["pack_number"] == 163
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/policy-change-approval-receipt-renewal-recheck-queue.json"
    assert payload["source_endpoint"] == "/tower/policy-change-approval-receipt-expiration-rules.json"

    assert payload["simulated_only"] is True
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
    assert payload["cached_non_recursive"] is True

    summary = payload["summary"]
    assert summary["readiness_score"] == 100
    assert summary["queue_item_count"] >= 9
    assert summary["owner_recheck_required_count"] >= 1
    assert summary["fresh_recheck_required_count"] >= 1
    assert summary["renewal_eligible_review_count"] >= 1
    assert summary["monitor_only_renewal_count"] >= 1
    assert summary["owner_review_required_count"] >= 1
    assert summary["fresh_recheck_item_count"] >= 1
    assert summary["renewal_candidate_count"] >= 1

    checks = payload["readiness_checks"]
    assert checks["pack_162_ready"] is True
    assert checks["has_queue_items"] is True
    assert checks["queue_count_matches_expiration_items"] is True
    assert checks["all_simulated_only"] is True
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

    assert checks["queue_action_never_allowed_now"] is True
    assert checks["real_recheck_never_allowed_now"] is True
    assert checks["real_renewal_never_allowed_now"] is True
    assert checks["all_queue_ids_present"] is True
    assert checks["all_lanes_present"] is True
    assert checks["all_recommended_actions_present"] is True
    assert checks["all_required_steps_present"] is True

    assert checks["owner_recheck_required_present"] is True
    assert checks["fresh_recheck_required_present"] is True
    assert checks["renewal_eligible_review_present"] is True
    assert checks["monitor_only_renewal_present"] is True
    assert checks["owner_review_required_items_present"] is True
    assert checks["fresh_recheck_items_present"] is True
    assert checks["renewal_candidate_items_present"] is True
    assert checks["required_lane_coverage"] is True
    assert checks["required_action_coverage"] is True
    assert checks["cached_non_recursive"] is True


def test_pack_163_queue_items_have_required_fields():
    mod = importlib.import_module("tower.policy_change_approval_receipt_renewal_recheck_queue")
    payload = mod.build_policy_change_approval_receipt_renewal_recheck_queue_payload(force_refresh=True)

    required_lanes = {
        "owner_recheck_required",
        "fresh_recheck_required",
        "renewal_eligible_review",
        "monitor_only_renewal",
    }
    observed_lanes = set()

    for item in payload["queue_items"]:
        observed_lanes.add(item["queue_lane"])

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

        assert isinstance(item["ttl_hours"], int)
        assert item["ttl_hours"] > 0
        assert item["created_at"].endswith("Z")
        assert item["warning_at"].endswith("Z")
        assert item["expires_at"].endswith("Z")

        assert item["queue_lane"]
        assert item["queue_lane_label"]
        assert item["queue_lane_description"]
        assert item["queue_priority"] in {"critical", "high", "medium", "monitor"}
        assert isinstance(item["queue_owner_review_required"], bool)
        assert isinstance(item["fresh_recheck_required"], bool)
        assert isinstance(item["renewal_candidate"], bool)
        assert item["recommended_action"]
        assert item["renewal_status"]
        assert item["queue_reason"]
        assert isinstance(item["required_queue_steps"], list)
        assert item["required_queue_steps"]

        assert isinstance(item["renewal_allowed_by_rule"], bool)
        assert isinstance(item["recheck_required_by_rule"], bool)
        assert isinstance(item["owner_review_required_by_rule"], bool)

        assert item["queue_action_allowed_now"] is False
        assert item["real_recheck_allowed_now"] is False
        assert item["real_renewal_allowed_now"] is False
        assert item["real_queue_action_executed"] is False
        assert item["soulaana_queue_translation"]

        assert item["source_endpoint"] == "/tower/policy-change-approval-receipt-expiration-rules.json"

        assert item["simulated_only"] is True
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

    assert required_lanes.issubset(observed_lanes)


def test_pack_163_lane_specific_queue_behavior():
    mod = importlib.import_module("tower.policy_change_approval_receipt_renewal_recheck_queue")
    payload = mod.build_policy_change_approval_receipt_renewal_recheck_queue_payload(force_refresh=True)

    by_lane = payload["indexes"]["by_queue_lane"]

    owner_recheck = by_lane["owner_recheck_required"]
    assert len(owner_recheck) >= 1
    assert all(item["recommended_action"] == "owner_recheck_before_reuse" for item in owner_recheck)
    assert all(item["queue_owner_review_required"] is True for item in owner_recheck)
    assert all(item["fresh_recheck_required"] is True for item in owner_recheck)
    assert all(item["renewal_candidate"] is False for item in owner_recheck)

    fresh_recheck = by_lane["fresh_recheck_required"]
    assert len(fresh_recheck) >= 1
    assert all(item["recommended_action"] == "prepare_fresh_recheck" for item in fresh_recheck)
    assert all(item["fresh_recheck_required"] is True for item in fresh_recheck)
    assert all(item["renewal_candidate"] is False for item in fresh_recheck)

    renewal_review = by_lane["renewal_eligible_review"]
    assert len(renewal_review) >= 1
    assert all(item["recommended_action"] == "prepare_renewal_review" for item in renewal_review)
    assert all(item["queue_owner_review_required"] is True for item in renewal_review)
    assert all(item["renewal_candidate"] is True for item in renewal_review)

    monitor = by_lane["monitor_only_renewal"]
    assert len(monitor) >= 1
    assert all(item["recommended_action"] == "continue_monitor_or_renew_preview" for item in monitor)
    assert all(item["queue_owner_review_required"] is False for item in monitor)
    assert all(item["renewal_candidate"] is True for item in monitor)


def test_pack_163_indexes_and_special_lists_are_present():
    mod = importlib.import_module("tower.policy_change_approval_receipt_renewal_recheck_queue")
    payload = mod.build_policy_change_approval_receipt_renewal_recheck_queue_payload(force_refresh=True)

    indexes = payload["indexes"]
    assert indexes["by_queue_lane"]
    assert indexes["by_queue_priority"]
    assert indexes["by_renewal_status"]
    assert indexes["by_recommended_action"]
    assert indexes["by_vault_bucket"]
    assert indexes["by_expiration_state"]
    assert indexes["by_receipt_type"]

    assert payload["owner_recheck_required"]
    assert payload["fresh_recheck_required"]
    assert payload["renewal_eligible_review"]
    assert payload["monitor_only_renewal"]
    assert payload["owner_review_required_items"]
    assert payload["fresh_recheck_items"]
    assert payload["renewal_candidate_items"]

    for item in payload["owner_recheck_required"]:
        assert item["queue_lane"] == "owner_recheck_required"

    for item in payload["fresh_recheck_required"]:
        assert item["queue_lane"] == "fresh_recheck_required"

    for item in payload["renewal_eligible_review"]:
        assert item["queue_lane"] == "renewal_eligible_review"

    for item in payload["monitor_only_renewal"]:
        assert item["queue_lane"] == "monitor_only_renewal"

    for item in payload["owner_review_required_items"]:
        assert item["queue_owner_review_required"] is True

    for item in payload["fresh_recheck_items"]:
        assert item["fresh_recheck_required"] is True

    for item in payload["renewal_candidate_items"]:
        assert item["renewal_candidate"] is True


def test_pack_163_status_bridge_quick_action_and_unified_section():
    mod = importlib.import_module("tower.policy_change_approval_receipt_renewal_recheck_queue")

    bridge = mod.build_policy_change_approval_receipt_renewal_recheck_queue_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 163
    assert bridge["status"] == "ready"
    assert bridge["endpoint"] == "/tower/policy-change-approval-receipt-renewal-recheck-queue.json"
    assert bridge["readiness_score"] == 100
    assert bridge["queue_item_count"] >= 9
    assert bridge["owner_recheck_required_count"] >= 1
    assert bridge["fresh_recheck_required_count"] >= 1
    assert bridge["renewal_eligible_review_count"] >= 1
    assert bridge["monitor_only_renewal_count"] >= 1
    assert bridge["owner_review_required_count"] >= 1
    assert bridge["fresh_recheck_item_count"] >= 1
    assert bridge["renewal_candidate_count"] >= 1

    assert bridge["simulated_only"] is True
    assert bridge["queue_preview_only"] is True
    assert bridge["renewal_preview_only"] is True
    assert bridge["recheck_preview_only"] is True
    assert bridge["real_recheck_executed"] is False
    assert bridge["real_renewal_executed"] is False
    assert bridge["real_queue_action_executed"] is False
    assert bridge["cached_non_recursive"] is True

    action = mod.build_policy_change_approval_receipt_renewal_recheck_queue_quick_action()
    assert action["id"] == "policy_change_approval_receipt_renewal_recheck_queue"
    assert action["href"] == "/tower/policy-change-approval-receipt-renewal-recheck-queue.json"
    assert action["simulated_only"] is True
    assert action["queue_preview_only"] is True

    section = mod.build_policy_change_approval_receipt_renewal_recheck_queue_unified_owner_section()
    assert section["section_id"] == "policy_change_approval_receipt_renewal_recheck_queue"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/policy-change-approval-receipt-renewal-recheck-queue.json"
    assert section["simulated_only"] is True
    assert section["queue_preview_only"] is True
    assert section["cached_non_recursive"] is True
    assert len(section["cards"]) >= 6


def test_pack_163_tower_status_bridge_available():
    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_163_policy_change_approval_receipt_renewal_recheck_queue_status_bridge")

    bridge = status.build_pack_163_policy_change_approval_receipt_renewal_recheck_queue_status_bridge()
    assert bridge["pack_number"] == 163
    assert bridge["status"] == "ready"
    assert bridge["endpoint"] == "/tower/policy-change-approval-receipt-renewal-recheck-queue.json"
    assert bridge["readiness_score"] == 100


def test_pack_163_quick_action_helper_available():
    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_163_policy_change_approval_receipt_renewal_recheck_queue_quick_action")
    assert hasattr(qa, "append_pack_163_policy_change_approval_receipt_renewal_recheck_queue_quick_action")

    action = qa.build_pack_163_policy_change_approval_receipt_renewal_recheck_queue_quick_action()
    assert action["id"] == "policy_change_approval_receipt_renewal_recheck_queue"
    assert action["href"] == "/tower/policy-change-approval-receipt-renewal-recheck-queue.json"

    actions = qa.append_pack_163_policy_change_approval_receipt_renewal_recheck_queue_quick_action([])
    assert isinstance(actions, list)
    assert any(item.get("id") == "policy_change_approval_receipt_renewal_recheck_queue" for item in actions)


def test_pack_163_unified_section_helper_available():
    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_163_policy_change_approval_receipt_renewal_recheck_queue_unified_section")
    assert hasattr(unified, "build_pack_163_policy_change_approval_receipt_renewal_recheck_queue_html_section")
    assert hasattr(unified, "append_pack_163_policy_change_approval_receipt_renewal_recheck_queue_section")

    section = unified.build_pack_163_policy_change_approval_receipt_renewal_recheck_queue_unified_section()
    assert section["section_id"] == "policy_change_approval_receipt_renewal_recheck_queue"
    assert section["href"] == "/tower/policy-change-approval-receipt-renewal-recheck-queue.json"

    sections = unified.append_pack_163_policy_change_approval_receipt_renewal_recheck_queue_section([])
    assert isinstance(sections, list)
    assert any(item.get("section_id") == "policy_change_approval_receipt_renewal_recheck_queue" for item in sections)


def test_pack_163_web_route_present_and_route_scanner_recognizes_it():
    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-renewal-recheck-queue.json" in app_text
    assert "tower_policy_change_approval_receipt_renewal_recheck_queue_json" in app_text
    assert "_pack_163_policy_change_approval_receipt_renewal_recheck_queue_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-renewal-recheck-queue.json" in route_text
    assert "_pack_163_policy_change_approval_receipt_renewal_recheck_queue_route_guard" in route_text


def test_pack_163_no_secret_leakage_in_payload():
    mod = importlib.import_module("tower.policy_change_approval_receipt_renewal_recheck_queue")
    payload_text = str(mod.build_policy_change_approval_receipt_renewal_recheck_queue_payload(force_refresh=True)).lower()

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
