
"""
PACK 205 fast test - Receipt Chain Operational Batch Checkpoint.

Uses short safe module:
    tower.receipt_chain_operational_batch_checkpoint_v205
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_205_payload_ready_and_preview_only():
    mod = importlib.import_module("tower.receipt_chain_operational_batch_checkpoint_v205")
    payload = mod.build_receipt_chain_operational_batch_checkpoint_v205_payload(force_refresh=True)

    assert payload["pack_number"] == 205
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/receipt-chain-operational-batch-checkpoint-v205.json"

    required_true = [
        "simulated_only",
        "batch_checkpoint_preview_only",
        "operational_batch_checkpoint_preview_only",
        "operational_handoff_preview_only",
        "receipt_chain_handoff_preview_only",
        "saved_view_preview_only",
        "filter_preset_preview_only",
        "evidence_packet_preview_only",
        "evidence_bundle_preview_only",
        "export_request_preview_only",
        "export_blocked",
        "raw_evidence_redacted",
        "recheck_expiration_handoff_preview_only",
        "cached_non_recursive",
    ]

    for key in required_true:
        assert payload[key] is True, key

    required_false = [
        "real_action_executed",
        "real_handoff_executed",
        "real_owner_action_executed",
        "real_evidence_exported",
        "real_export_request_created",
        "real_packet_written",
        "real_packet_sealed",
        "real_recheck_executed",
        "real_renewal_executed",
        "real_expiration_enforced",
        "real_owner_followup_executed",
        "real_filter_preference_saved",
        "real_navigation_state_persisted",
        "real_drawer_selection_saved",
        "real_saved_view_written",
        "real_user_preference_written",
        "real_history_written",
        "real_version_written",
        "real_version_saved",
        "real_rollback_executed",
        "real_restore_executed",
        "real_edit_persisted",
        "real_raw_evidence_revealed",
    ]

    for key in required_false:
        assert payload[key] is False, key

    summary = payload["summary"]
    assert summary["readiness_score"] == 100
    assert summary["source_pack_count"] == 4
    assert summary["operational_batch_pack_card_count"] == 4
    assert summary["ready_pack_count"] == 4
    assert summary["review_pack_count"] == 0
    assert summary["batch_group_count"] == 3
    assert summary["final_checkpoint_count"] == 1
    assert summary["safe_to_save_packs_201_to_205"] is True
    assert summary["safe_to_continue_to_pack_206"] is True
    assert summary["ready_pack_numbers"] == [201, 202, 203, 204]
    assert summary["review_pack_numbers"] == []
    assert summary["real_action_executed_count"] == 0
    assert summary["real_handoff_executed_count"] == 0
    assert summary["real_owner_action_executed_count"] == 0
    assert summary["real_evidence_exported_count"] == 0
    assert summary["real_export_request_created_count"] == 0
    assert summary["real_packet_written_count"] == 0
    assert summary["real_packet_sealed_count"] == 0
    assert summary["real_recheck_executed_count"] == 0
    assert summary["real_renewal_executed_count"] == 0
    assert summary["real_expiration_enforced_count"] == 0
    assert summary["real_owner_followup_executed_count"] == 0
    assert summary["raw_evidence_revealed_count"] == 0
    assert summary["save_batch"] == "201-205"
    assert summary["save_after_pack"] == 205

    checks = payload["readiness_checks"]
    required_checks = [
        "has_four_source_packs",
        "pack_201_ready",
        "pack_202_ready",
        "pack_203_ready",
        "pack_204_ready",
        "all_pack_cards_ready",
        "all_pack_metrics_ready",
        "all_pack_safety_flags_ok",
        "has_batch_groups",
        "all_batch_groups_ready",
        "safety_summary_ready",
        "final_checkpoint_ready",
        "safe_to_save_packs_201_to_205",
        "safe_to_continue_to_pack_206",
        "indexes_present",
        "checkpoint_index_present",
        "all_simulated_only",
        "all_batch_checkpoint_preview_only",
        "no_real_action_executed",
        "no_real_handoff_executed",
        "no_real_owner_action_executed",
        "no_real_evidence_exported",
        "no_real_export_request_created",
        "no_real_packet_written",
        "no_real_packet_sealed",
        "no_real_recheck_executed",
        "no_real_renewal_executed",
        "no_real_expiration_enforced",
        "no_real_raw_evidence_revealed",
        "all_action_execution_blocked",
        "all_handoff_execution_blocked",
        "all_evidence_export_blocked",
        "all_recheck_execution_blocked",
        "all_renewal_execution_blocked",
        "all_expiration_enforcement_blocked",
        "all_raw_evidence_reveal_blocked",
        "cached_non_recursive",
    ]

    for key in required_checks:
        assert checks[key] is True, key


def test_pack_205_pack_cards_metrics_groups_and_final_checkpoint():
    mod = importlib.import_module("tower.receipt_chain_operational_batch_checkpoint_v205")
    payload = mod.build_receipt_chain_operational_batch_checkpoint_v205_payload(force_refresh=True)

    cards = payload["operational_batch_pack_cards"]
    groups = payload["operational_batch_groups"]
    safety = payload["operational_batch_safety_summary"]
    checkpoint = payload["final_operational_batch_checkpoint"]

    assert len(cards) == 4
    card_by_pack = {card["pack_number"]: card for card in cards}
    assert set(card_by_pack) == {201, 202, 203, 204}

    for pack_number, card in card_by_pack.items():
        assert card["operational_batch_pack_card_id"].startswith("receipt_chain_operational_batch_pack_")
        assert card["pack_number"] == pack_number
        assert card["pack_id"] == f"PACK_{pack_number}"
        assert card["title"]
        assert card["endpoint"]
        assert card["sequence"] in {1, 2, 3, 4}
        assert card["status"] == "ready"
        assert card["readiness_score"] == 100
        assert card["metric_checks"]
        assert card["status_ready"] is True
        assert card["readiness_ready"] is True
        assert card["all_metric_checks_ok"] is True
        assert card["safety_flags_ok"] is True
        assert card["pack_checkpoint_ok"] is True
        assert card["card_status"] == "receipt_chain_operational_batch_pack_card_ready"
        assert card["card_result_type"] == "tower_receipt_chain_operational_batch_pack_card_preview"
        assert card["safe_preview_only"] is True

        assert card["simulated_only"] is True
        assert card["batch_checkpoint_preview_only"] is True
        assert card["operational_batch_checkpoint_preview_only"] is True
        assert card["real_action_executed"] is False
        assert card["real_handoff_executed"] is False
        assert card["real_owner_action_executed"] is False
        assert card["real_evidence_exported"] is False
        assert card["real_raw_evidence_revealed"] is False
        assert card["action_execution_allowed_now"] is False
        assert card["handoff_execution_allowed_now"] is False
        assert card["evidence_export_allowed_now"] is False
        assert card["raw_evidence_reveal_allowed"] is False

        for metric in card["metric_checks"].values():
            assert metric["ok"] is True

    assert card_by_pack[201]["metric_checks"]["handoff_route_count"]["actual"] == 5
    assert card_by_pack[201]["metric_checks"]["owner_action_menu_item_count"]["actual"] == 6
    assert card_by_pack[201]["metric_checks"]["allowed_preview_action_count"]["actual"] == 3
    assert card_by_pack[201]["metric_checks"]["blocked_action_count"]["actual"] == 3
    assert card_by_pack[201]["metric_checks"]["evidence_map_item_count"]["actual"] == 4
    assert card_by_pack[201]["metric_checks"]["next_batch_card_count"]["actual"] == 5
    assert card_by_pack[201]["metric_checks"]["safe_to_continue_to_pack_202"]["actual"] is True

    assert card_by_pack[202]["metric_checks"]["handoff_saved_view_preview_count"]["actual"] == 6
    assert card_by_pack[202]["metric_checks"]["handoff_filter_preset_preview_count"]["actual"] == 8
    assert card_by_pack[202]["metric_checks"]["selected_handoff_saved_view_preview_count"]["actual"] == 1
    assert card_by_pack[202]["metric_checks"]["selected_saved_view_id"]["actual"] == "default_full_handoff"
    assert card_by_pack[202]["metric_checks"]["selected_filter_preset_id"]["actual"] == "all_handoff_items"
    assert card_by_pack[202]["metric_checks"]["selected_handoff_route_count"]["actual"] == 5
    assert card_by_pack[202]["metric_checks"]["selected_owner_action_count"]["actual"] == 6
    assert card_by_pack[202]["metric_checks"]["selected_evidence_map_item_count"]["actual"] == 4
    assert card_by_pack[202]["metric_checks"]["selected_next_batch_card_count"]["actual"] == 5

    assert card_by_pack[203]["metric_checks"]["packet_section_count"]["actual"] == 6
    assert card_by_pack[203]["metric_checks"]["evidence_bundle_packet_count"]["actual"] == 3
    assert card_by_pack[203]["metric_checks"]["export_request_preview_count"]["actual"] == 3
    assert card_by_pack[203]["metric_checks"]["owner_review_checklist_item_count"]["actual"] == 5
    assert card_by_pack[203]["metric_checks"]["raw_item_count"]["actual"] == 0
    assert card_by_pack[203]["metric_checks"]["real_export_request_created_count"]["actual"] == 0
    assert card_by_pack[203]["metric_checks"]["real_evidence_exported_count"]["actual"] == 0
    assert card_by_pack[203]["metric_checks"]["real_packet_written_count"]["actual"] == 0
    assert card_by_pack[203]["metric_checks"]["real_packet_sealed_count"]["actual"] == 0
    assert card_by_pack[203]["metric_checks"]["raw_evidence_revealed_count"]["actual"] == 0

    assert card_by_pack[204]["metric_checks"]["freshness_lane_count"]["actual"] == 5
    assert card_by_pack[204]["metric_checks"]["recheck_hook_count"]["actual"] == 4
    assert card_by_pack[204]["metric_checks"]["expiration_trigger_count"]["actual"] == 4
    assert card_by_pack[204]["metric_checks"]["renewal_trigger_count"]["actual"] == 3
    assert card_by_pack[204]["metric_checks"]["owner_followup_queue_item_count"]["actual"] == 5
    assert card_by_pack[204]["metric_checks"]["safe_to_continue_to_pack_205"]["actual"] is True
    assert card_by_pack[204]["metric_checks"]["real_recheck_executed_count"]["actual"] == 0
    assert card_by_pack[204]["metric_checks"]["real_renewal_executed_count"]["actual"] == 0
    assert card_by_pack[204]["metric_checks"]["real_expiration_enforced_count"]["actual"] == 0
    assert card_by_pack[204]["metric_checks"]["real_owner_followup_executed_count"]["actual"] == 0
    assert card_by_pack[204]["metric_checks"]["real_evidence_exported_count"]["actual"] == 0
    assert card_by_pack[204]["metric_checks"]["raw_evidence_revealed_count"]["actual"] == 0

    assert len(groups) == 3
    group_by_key = {group["operational_batch_group_key"]: group for group in groups}
    assert set(group_by_key) == {
        "ready_operational_batch_packs",
        "review_operational_batch_packs",
        "all_operational_batch_packs",
    }

    assert group_by_key["ready_operational_batch_packs"]["pack_card_count"] == 4
    assert group_by_key["ready_operational_batch_packs"]["pack_numbers"] == [201, 202, 203, 204]
    assert group_by_key["review_operational_batch_packs"]["pack_card_count"] == 0
    assert group_by_key["review_operational_batch_packs"]["pack_numbers"] == []
    assert group_by_key["all_operational_batch_packs"]["pack_card_count"] == 4
    assert group_by_key["all_operational_batch_packs"]["pack_numbers"] == [201, 202, 203, 204]

    for group in groups:
        assert group["operational_batch_group_id"].startswith("receipt_chain_operational_batch_group_")
        assert group["label"]
        assert group["sequence"] in {1, 2, 3}
        assert group["pack_card_count"] == len(group["pack_card_ids"])
        assert group["group_status"] == "receipt_chain_operational_batch_group_preview_ready"
        assert group["group_result_type"] == "tower_receipt_chain_operational_batch_group_preview"
        assert group["safe_preview_only"] is True

    assert safety["operational_batch_safety_summary_id"].startswith("receipt_chain_operational_batch_safety_")
    assert safety["source_pack_count"] == 4
    assert safety["ready_pack_count"] == 4
    assert safety["review_pack_count"] == 0
    assert safety["real_action_executed_count"] == 0
    assert safety["real_handoff_executed_count"] == 0
    assert safety["real_owner_action_executed_count"] == 0
    assert safety["real_evidence_exported_count"] == 0
    assert safety["real_export_request_created_count"] == 0
    assert safety["real_packet_written_count"] == 0
    assert safety["real_packet_sealed_count"] == 0
    assert safety["real_recheck_executed_count"] == 0
    assert safety["real_renewal_executed_count"] == 0
    assert safety["real_expiration_enforced_count"] == 0
    assert safety["real_owner_followup_executed_count"] == 0
    assert safety["real_saved_view_written_count"] == 0
    assert safety["real_user_preference_written_count"] == 0
    assert safety["raw_evidence_revealed_count"] == 0
    assert safety["all_packs_ready"] is True
    assert safety["all_metrics_ready"] is True
    assert safety["all_safety_flags_ok"] is True
    assert safety["summary_status"] == "receipt_chain_operational_batch_safety_summary_preview_ready"

    assert checkpoint["operational_batch_checkpoint_id"].startswith("receipt_chain_operational_batch_checkpoint_")
    assert checkpoint["checkpoint_ok"] is True
    assert checkpoint["checkpoint_status"] == "receipt_chain_operational_batch_checkpoint_preview_ready"
    assert checkpoint["checkpoint_result_type"] == "tower_receipt_chain_operational_batch_checkpoint_preview"
    assert checkpoint["ready_pack_numbers"] == [201, 202, 203, 204]
    assert checkpoint["review_pack_numbers"] == []
    assert checkpoint["safe_to_save_packs_201_to_205"] is True
    assert checkpoint["safe_to_continue_to_pack_206"] is True
    assert checkpoint["save_batch"] == "201-205"
    assert checkpoint["save_after_pack"] == 205
    assert checkpoint["safe_preview_only"] is True
    assert checkpoint["real_raw_evidence_revealed"] is False


def test_pack_205_indexes_bridge_integrations_route_and_no_secrets():
    mod = importlib.import_module("tower.receipt_chain_operational_batch_checkpoint_v205")
    payload = mod.build_receipt_chain_operational_batch_checkpoint_v205_payload(force_refresh=True)

    indexes = payload["operational_batch_indexes"]
    checkpoint = payload["final_operational_batch_checkpoint"]

    assert indexes["pack_cards_by_id"]
    assert indexes["pack_cards_by_number"]
    assert indexes["pack_cards_by_status"]
    assert indexes["batch_groups_by_id"]
    assert indexes["batch_groups_by_key"]
    assert indexes["final_checkpoint_by_id"]

    assert set(indexes["pack_cards_by_number"]) == {"201", "202", "203", "204"}
    assert "receipt_chain_operational_batch_pack_card_ready" in indexes["pack_cards_by_status"]
    assert len(indexes["pack_cards_by_status"]["receipt_chain_operational_batch_pack_card_ready"]) == 4
    assert "ready_operational_batch_packs" in indexes["batch_groups_by_key"]
    assert "review_operational_batch_packs" in indexes["batch_groups_by_key"]
    assert "all_operational_batch_packs" in indexes["batch_groups_by_key"]
    assert checkpoint["operational_batch_checkpoint_id"] in indexes["final_checkpoint_by_id"]

    bridge = mod.build_receipt_chain_operational_batch_checkpoint_v205_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 205
    assert bridge["status"] == "ready"
    assert bridge["readiness_score"] == 100
    assert bridge["endpoint"] == "/tower/receipt-chain-operational-batch-checkpoint-v205.json"
    assert bridge["source_pack_count"] == 4
    assert bridge["operational_batch_pack_card_count"] == 4
    assert bridge["ready_pack_count"] == 4
    assert bridge["review_pack_count"] == 0
    assert bridge["batch_group_count"] == 3
    assert bridge["final_checkpoint_count"] == 1
    assert bridge["safe_to_save_packs_201_to_205"] is True
    assert bridge["safe_to_continue_to_pack_206"] is True
    assert bridge["ready_pack_numbers"] == [201, 202, 203, 204]
    assert bridge["review_pack_numbers"] == []
    assert bridge["real_action_executed_count"] == 0
    assert bridge["real_handoff_executed_count"] == 0
    assert bridge["real_owner_action_executed_count"] == 0
    assert bridge["real_evidence_exported_count"] == 0
    assert bridge["real_export_request_created_count"] == 0
    assert bridge["real_packet_written_count"] == 0
    assert bridge["real_packet_sealed_count"] == 0
    assert bridge["real_recheck_executed_count"] == 0
    assert bridge["real_renewal_executed_count"] == 0
    assert bridge["real_expiration_enforced_count"] == 0
    assert bridge["real_owner_followup_executed_count"] == 0
    assert bridge["raw_evidence_revealed_count"] == 0
    assert bridge["save_batch"] == "201-205"
    assert bridge["save_after_pack"] == 205

    action = mod.build_receipt_chain_operational_batch_checkpoint_v205_quick_action()
    assert action["id"] == "receipt_chain_operational_batch_checkpoint_v205"
    assert action["href"] == "/tower/receipt-chain-operational-batch-checkpoint-v205.json"
    assert action["status"] == "ready"

    section = mod.build_receipt_chain_operational_batch_checkpoint_v205_unified_owner_section()
    assert section["section_id"] == "receipt_chain_operational_batch_checkpoint_v205"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/receipt-chain-operational-batch-checkpoint-v205.json"
    assert len(section["cards"]) >= 6

    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_205_receipt_chain_operational_batch_checkpoint_v205_status_bridge")
    tower_bridge = status.build_pack_205_receipt_chain_operational_batch_checkpoint_v205_status_bridge()
    assert tower_bridge["status"] == "ready"
    assert tower_bridge["readiness_score"] == 100
    assert tower_bridge["safe_to_save_packs_201_to_205"] is True
    assert tower_bridge["safe_to_continue_to_pack_206"] is True

    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_205_receipt_chain_operational_batch_checkpoint_v205_quick_action")
    assert hasattr(qa, "append_pack_205_receipt_chain_operational_batch_checkpoint_v205_quick_action")
    actions = qa.append_pack_205_receipt_chain_operational_batch_checkpoint_v205_quick_action([])
    assert any(item.get("id") == "receipt_chain_operational_batch_checkpoint_v205" for item in actions)

    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_205_receipt_chain_operational_batch_checkpoint_v205_unified_section")
    assert hasattr(unified, "append_pack_205_receipt_chain_operational_batch_checkpoint_v205_section")
    sections = unified.append_pack_205_receipt_chain_operational_batch_checkpoint_v205_section([])
    assert any(item.get("section_id") == "receipt_chain_operational_batch_checkpoint_v205" for item in sections)

    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/receipt-chain-operational-batch-checkpoint-v205.json" in app_text
    assert "tower_receipt_chain_operational_batch_checkpoint_v205_json" in app_text
    assert "_pack_205_receipt_chain_operational_batch_checkpoint_v205_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/receipt-chain-operational-batch-checkpoint-v205.json" in route_text
    assert "_pack_205_receipt_chain_operational_batch_checkpoint_v205_route_guard" in route_text

    payload_text = str(payload).lower()
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
