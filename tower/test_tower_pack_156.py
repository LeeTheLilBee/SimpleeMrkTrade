
"""
PACK 156 fast test - Policy Renewal / Recheck Queue foundation.
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_156_payload_ready_and_simulated_only():
    mod = importlib.import_module("tower.policy_renewal_recheck_queue")
    payload = mod.build_policy_renewal_recheck_queue_payload(force_refresh=True)

    assert payload["pack_number"] == 156
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/policy-renewal-recheck-queue.json"
    assert payload["source_endpoint"] == "/tower/policy-expiration-rules.json"

    assert payload["simulated_only"] is True
    assert payload["real_renewal_executed"] is False
    assert payload["real_recheck_executed"] is False
    assert payload["real_expiration_enforced"] is False
    assert payload["real_enforcement_executed"] is False
    assert payload["real_audit_written"] is False
    assert payload["real_receipt_written"] is False
    assert payload["cached_non_recursive"] is True

    summary = payload["summary"]
    assert summary["readiness_score"] == 100
    assert summary["queue_item_count"] >= 9
    assert summary["owner_review_required_count"] >= 1
    assert summary["fresh_recheck_required_count"] >= 1
    assert summary["renewal_candidate_count"] >= 1
    assert summary["monitor_only_count"] >= 1
    assert summary["lane_count"] >= 4
    assert summary["priority_count"] >= 5

    checks = payload["readiness_checks"]
    assert checks["pack_155_ready"] is True
    assert checks["has_queue_items"] is True
    assert checks["queue_count_matches_expiration_entries"] is True
    assert checks["all_simulated_only"] is True
    assert checks["no_real_renewal_executed"] is True
    assert checks["no_real_recheck_executed"] is True
    assert checks["no_real_expiration_enforced"] is True
    assert checks["no_real_enforcement"] is True
    assert checks["no_real_receipt_written"] is True
    assert checks["no_real_audit_written"] is True
    assert checks["all_recheck_ids_present"] is True
    assert checks["all_queue_positions_present"] is True
    assert checks["lane_index_present"] is True
    assert checks["priority_index_present"] is True
    assert checks["renewal_status_index_present"] is True
    assert checks["recommended_action_index_present"] is True
    assert checks["bucket_index_present"] is True
    assert checks["owner_review_required_present"] is True
    assert checks["fresh_recheck_required_present"] is True
    assert checks["renewal_candidates_present"] is True
    assert checks["monitor_only_items_present"] is True
    assert checks["required_lane_coverage"] is True
    assert checks["required_priority_coverage"] is True
    assert checks["cached_non_recursive"] is True


def test_pack_156_queue_items_have_required_fields():
    mod = importlib.import_module("tower.policy_renewal_recheck_queue")
    payload = mod.build_policy_renewal_recheck_queue_payload(force_refresh=True)

    required_lanes = {
        "owner_recheck_required",
        "renewal_eligible_review_soon",
        "recheck_required_soon",
        "monitor_only_no_action",
    }
    observed_lanes = set()

    required_priorities = {"critical", "high", "medium", "low", "monitor"}
    observed_priorities = set()

    for item in payload["queue_items"]:
        observed_lanes.add(item["lane"])
        observed_priorities.add(item["priority"])

        assert item["recheck_item_id"].startswith("recheck_preview_")
        assert isinstance(item["queue_position"], int)
        assert item["queue_position"] >= 1
        assert item["lane"]
        assert item["priority"]
        assert isinstance(item["priority_rank"], int)
        assert isinstance(item["state_rank"], int)
        assert isinstance(item["severity_rank"], int)
        assert item["recommended_action"]
        assert item["renewal_status"]
        assert isinstance(item["renewal_allowed"], bool)
        assert isinstance(item["requires_owner_review"], bool)
        assert isinstance(item["requires_fresh_recheck"], bool)
        assert isinstance(item["can_prepare_renewal"], bool)
        assert isinstance(item["is_monitor_only"], bool)

        assert item["expiration_check_id"].startswith("expiration_preview_")
        assert item["vault_entry_id"].startswith("vault_preview_")
        assert item["ledger_entry_id"].startswith("ledger_preview_")
        assert item["receipt_preview_id"].startswith("receipt_preview_")
        assert item["scenario_id"]
        assert item["matched_policy_id"]
        assert item["decision"]
        assert item["severity"]
        assert item["bucket"]
        assert item["expiration_state"] in {"fresh", "warning", "expired"}
        assert item["owner_prompt"]
        assert item["owner_message_from_expiration"]
        assert item["soulaana_queue_translation"]
        assert item["proof_bundle_hint"]

        assert item["simulated_only"] is True
        assert item["real_renewal_executed"] is False
        assert item["real_recheck_executed"] is False
        assert item["real_expiration_enforced"] is False
        assert item["real_enforcement_executed"] is False
        assert item["real_receipt_written"] is False
        assert item["real_audit_written"] is False
        assert item["source_endpoint"] == "/tower/policy-expiration-rules.json"

        if item["lane"] == "owner_recheck_required":
            assert item["requires_fresh_recheck"] is True
            assert item["requires_owner_review"] is True
            assert item["renewal_status"] == "renewal_blocked_recheck_required"

        if item["lane"] == "renewal_eligible_review_soon":
            assert item["can_prepare_renewal"] is True
            assert item["requires_owner_review"] is True

        if item["lane"] == "monitor_only_no_action":
            assert item["is_monitor_only"] is True
            assert item["recommended_action"] == "continue_monitoring"

    assert required_lanes.issubset(observed_lanes)
    assert required_priorities.issubset(observed_priorities)


def test_pack_156_indexes_and_specialized_lists_are_present():
    mod = importlib.import_module("tower.policy_renewal_recheck_queue")
    payload = mod.build_policy_renewal_recheck_queue_payload(force_refresh=True)

    indexes = payload["indexes"]
    assert indexes["by_lane"]
    assert indexes["by_priority"]
    assert indexes["by_renewal_status"]
    assert indexes["by_recommended_action"]
    assert indexes["by_bucket"]

    assert payload["owner_review_required"]
    assert payload["fresh_recheck_required"]
    assert payload["renewal_candidates"]
    assert payload["monitor_only_items"]

    for item in payload["owner_review_required"]:
        assert item["requires_owner_review"] is True

    for item in payload["fresh_recheck_required"]:
        assert item["requires_fresh_recheck"] is True

    for item in payload["renewal_candidates"]:
        assert item["can_prepare_renewal"] is True

    for item in payload["monitor_only_items"]:
        assert item["is_monitor_only"] is True

    # Top queue item should be the critical expired item.
    top = payload["queue_items"][0]
    assert top["priority"] == "critical"
    assert top["expiration_state"] == "expired"


def test_pack_156_status_bridge_quick_action_and_unified_section():
    mod = importlib.import_module("tower.policy_renewal_recheck_queue")

    bridge = mod.build_policy_renewal_recheck_queue_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 156
    assert bridge["status"] == "ready"
    assert bridge["endpoint"] == "/tower/policy-renewal-recheck-queue.json"
    assert bridge["readiness_score"] == 100
    assert bridge["queue_item_count"] >= 9
    assert bridge["owner_review_required_count"] >= 1
    assert bridge["fresh_recheck_required_count"] >= 1
    assert bridge["renewal_candidate_count"] >= 1
    assert bridge["monitor_only_count"] >= 1
    assert bridge["simulated_only"] is True
    assert bridge["real_renewal_executed"] is False
    assert bridge["real_recheck_executed"] is False
    assert bridge["real_expiration_enforced"] is False
    assert bridge["real_enforcement_executed"] is False
    assert bridge["real_audit_written"] is False
    assert bridge["real_receipt_written"] is False
    assert bridge["cached_non_recursive"] is True

    action = mod.build_policy_renewal_recheck_queue_quick_action()
    assert action["id"] == "policy_renewal_recheck_queue"
    assert action["href"] == "/tower/policy-renewal-recheck-queue.json"
    assert action["simulated_only"] is True

    section = mod.build_policy_renewal_recheck_queue_unified_owner_section()
    assert section["section_id"] == "policy_renewal_recheck_queue"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/policy-renewal-recheck-queue.json"
    assert section["simulated_only"] is True
    assert section["cached_non_recursive"] is True
    assert len(section["cards"]) >= 6


def test_pack_156_tower_status_bridge_available():
    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_156_policy_renewal_recheck_queue_status_bridge")

    bridge = status.build_pack_156_policy_renewal_recheck_queue_status_bridge()
    assert bridge["pack_number"] == 156
    assert bridge["status"] == "ready"
    assert bridge["endpoint"] == "/tower/policy-renewal-recheck-queue.json"
    assert bridge["readiness_score"] == 100


def test_pack_156_quick_action_helper_available():
    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_156_policy_renewal_recheck_queue_quick_action")
    assert hasattr(qa, "append_pack_156_policy_renewal_recheck_queue_quick_action")

    action = qa.build_pack_156_policy_renewal_recheck_queue_quick_action()
    assert action["id"] == "policy_renewal_recheck_queue"
    assert action["href"] == "/tower/policy-renewal-recheck-queue.json"

    actions = qa.append_pack_156_policy_renewal_recheck_queue_quick_action([])
    assert isinstance(actions, list)
    assert any(item.get("id") == "policy_renewal_recheck_queue" for item in actions)


def test_pack_156_unified_section_helper_available():
    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_156_policy_renewal_recheck_queue_unified_section")
    assert hasattr(unified, "build_pack_156_policy_renewal_recheck_queue_html_section")
    assert hasattr(unified, "append_pack_156_policy_renewal_recheck_queue_section")

    section = unified.build_pack_156_policy_renewal_recheck_queue_unified_section()
    assert section["section_id"] == "policy_renewal_recheck_queue"
    assert section["href"] == "/tower/policy-renewal-recheck-queue.json"

    sections = unified.append_pack_156_policy_renewal_recheck_queue_section([])
    assert isinstance(sections, list)
    assert any(item.get("section_id") == "policy_renewal_recheck_queue" for item in sections)


def test_pack_156_web_route_present_in_app_file():
    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/policy-renewal-recheck-queue.json" in app_text
    assert "tower_policy_renewal_recheck_queue_json" in app_text
    assert "_pack_156_policy_renewal_recheck_queue_route_guard" in app_text


def test_pack_156_no_secret_leakage_in_payload():
    mod = importlib.import_module("tower.policy_renewal_recheck_queue")
    payload_text = str(mod.build_policy_renewal_recheck_queue_payload(force_refresh=True)).lower()

    forbidden_fragments = [
        "sk-",
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
