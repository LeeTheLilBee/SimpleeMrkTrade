
"""
PACK 200 fast test - Owner Note Version Compare Navigation Receipt Chain
Checkpoint.

Uses short safe module:
    tower.owner_note_vc_nav_receipt_chain_checkpoint_v200
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_200_payload_ready_and_preview_only():
    mod = importlib.import_module("tower.owner_note_vc_nav_receipt_chain_checkpoint_v200")
    payload = mod.build_owner_note_vc_nav_receipt_chain_checkpoint_v200_payload(force_refresh=True)

    assert payload["pack_number"] == 200
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/owner-note-vc-nav-receipt-chain-checkpoint-v200.json"

    required_true = [
        "simulated_only",
        "checkpoint_preview_only",
        "receipt_chain_checkpoint_preview_only",
        "receipt_detail_focus_preview_only",
        "receipt_safety_detail_preview_only",
        "receipt_action_panel_preview_only",
        "action_receipt_navigation_preview_only",
        "receipt_selection_preview_only",
        "action_receipt_filter_preview_only",
        "action_receipt_preview_only",
        "cached_non_recursive",
    ]

    for key in required_true:
        assert payload[key] is True, key

    required_false = [
        "real_action_executed",
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
    assert summary["receipt_chain_pack_card_count"] == 4
    assert summary["ready_pack_count"] == 4
    assert summary["review_pack_count"] == 0
    assert summary["checkpoint_group_count"] == 3
    assert summary["final_checkpoint_count"] == 1
    assert summary["safe_to_save_packs_196_to_200"] is True
    assert summary["real_action_executed_count"] == 0
    assert summary["raw_evidence_revealed_count"] == 0
    assert summary["persistence_write_count"] == 0
    assert summary["ready_pack_numbers"] == [196, 197, 198, 199]
    assert summary["review_pack_numbers"] == []

    checks = payload["readiness_checks"]
    required_checks = [
        "has_four_source_packs",
        "pack_196_ready",
        "pack_197_ready",
        "pack_198_ready",
        "pack_199_ready",
        "all_pack_cards_ready",
        "all_pack_metrics_ready",
        "all_pack_safety_flags_ok",
        "safety_summary_ready",
        "has_checkpoint_groups",
        "all_checkpoint_groups_ready",
        "final_checkpoint_ready",
        "safe_to_save_packs_196_to_200",
        "indexes_present",
        "checkpoint_indexes_present",
        "all_simulated_only",
        "all_checkpoint_preview_only",
        "all_receipt_chain_checkpoint_preview_only",
        "no_real_action_executed",
        "no_real_filter_preference_saved",
        "no_real_navigation_state_persisted",
        "no_real_drawer_selection_saved",
        "no_real_raw_evidence_revealed",
        "all_action_execution_blocked",
        "all_filter_preference_saves_blocked",
        "all_navigation_persistence_blocked",
        "all_drawer_selection_saves_blocked",
        "all_raw_evidence_reveal_blocked",
        "cached_non_recursive",
    ]

    for key in required_checks:
        assert checks[key] is True, key


def test_pack_200_pack_cards_safety_summary_groups_and_final_checkpoint():
    mod = importlib.import_module("tower.owner_note_vc_nav_receipt_chain_checkpoint_v200")
    payload = mod.build_owner_note_vc_nav_receipt_chain_checkpoint_v200_payload(force_refresh=True)

    cards = payload["receipt_chain_pack_cards"]
    safety = payload["receipt_chain_safety_summary"]
    groups = payload["receipt_chain_checkpoint_groups"]
    checkpoint = payload["final_receipt_chain_checkpoint"]

    assert len(cards) == 4

    card_by_pack = {card["pack_number"]: card for card in cards}
    assert set(card_by_pack) == {196, 197, 198, 199}

    for pack_number, card in card_by_pack.items():
        assert card["receipt_chain_pack_card_id"].startswith("version_compare_navigation_receipt_chain_pack_")
        assert card["pack_number"] == pack_number
        assert card["pack_id"] == f"PACK_{pack_number}"
        assert card["endpoint"]
        assert card["sequence"] in {1, 2, 3, 4}
        assert card["status"] == "ready"
        assert card["readiness_score"] == 100
        assert card["metric_checks"]
        assert card["all_metric_checks_ok"] is True
        assert card["status_ready"] is True
        assert card["readiness_ready"] is True
        assert card["safety_flags_ok"] is True
        assert card["pack_checkpoint_ok"] is True
        assert card["card_status"] == "version_compare_navigation_receipt_chain_pack_card_ready"
        assert card["card_result_type"] == "owner_note_version_compare_navigation_receipt_chain_pack_card_preview"
        assert card["safe_preview_only"] is True

        assert card["simulated_only"] is True
        assert card["checkpoint_preview_only"] is True
        assert card["receipt_chain_checkpoint_preview_only"] is True
        assert card["real_action_executed"] is False
        assert card["real_filter_preference_saved"] is False
        assert card["real_navigation_state_persisted"] is False
        assert card["real_drawer_selection_saved"] is False
        assert card["real_raw_evidence_revealed"] is False
        assert card["action_execution_allowed_now"] is False
        assert card["filter_preference_save_allowed_now"] is False
        assert card["navigation_persistence_allowed_now"] is False
        assert card["drawer_selection_save_allowed_now"] is False
        assert card["raw_evidence_reveal_allowed"] is False
        assert card["raw_evidence_lookup_allowed"] is False

        for metric in card["metric_checks"].values():
            assert metric["ok"] is True

    assert card_by_pack[196]["metric_checks"]["action_receipt_count"]["actual"] == 5
    assert card_by_pack[196]["metric_checks"]["preview_action_receipt_count"]["actual"] == 3
    assert card_by_pack[196]["metric_checks"]["blocked_action_receipt_count"]["actual"] == 2
    assert card_by_pack[196]["metric_checks"]["real_action_executed_count"]["actual"] == 0
    assert card_by_pack[196]["metric_checks"]["raw_evidence_revealed_count"]["actual"] == 0
    assert card_by_pack[196]["metric_checks"]["persistence_write_count"]["actual"] == 0

    assert card_by_pack[197]["metric_checks"]["action_receipt_filter_lane_count"]["actual"] == 8
    assert card_by_pack[197]["metric_checks"]["action_receipt_search_facet_count"]["actual"] == 5
    assert card_by_pack[197]["metric_checks"]["action_receipt_quick_filter_chip_count"]["actual"] == 8
    assert card_by_pack[197]["metric_checks"]["source_action_receipt_count"]["actual"] == 5
    assert card_by_pack[197]["metric_checks"]["selected_action_receipt_count"]["actual"] == 5

    assert card_by_pack[198]["metric_checks"]["action_receipt_navigation_item_count"]["actual"] == 8
    assert card_by_pack[198]["metric_checks"]["action_receipt_selection_preview_count"]["actual"] == 8
    assert card_by_pack[198]["metric_checks"]["action_receipt_navigation_group_count"]["actual"] == 8
    assert card_by_pack[198]["metric_checks"]["search_navigation_facet_count"]["actual"] == 5
    assert card_by_pack[198]["metric_checks"]["search_navigation_chip_count"]["actual"] == 8
    assert card_by_pack[198]["metric_checks"]["selected_action_receipt_count"]["actual"] == 5

    assert card_by_pack[199]["metric_checks"]["selected_receipt_detail_focus_count"]["actual"] == 1
    assert card_by_pack[199]["metric_checks"]["breadcrumb_count"]["actual"] == 4
    assert card_by_pack[199]["metric_checks"]["receipt_safety_detail_card_count"]["actual"] == 6
    assert card_by_pack[199]["metric_checks"]["blocked_safety_detail_card_count"]["actual"] == 5
    assert card_by_pack[199]["metric_checks"]["preview_scope_detail_card_count"]["actual"] == 1
    assert card_by_pack[199]["metric_checks"]["receipt_detail_focus_group_count"]["actual"] == 3
    assert card_by_pack[199]["metric_checks"]["receipt_action_count"]["actual"] == 6
    assert card_by_pack[199]["metric_checks"]["selected_action_receipt_count"]["actual"] == 5

    assert safety["receipt_chain_safety_summary_id"].startswith("version_compare_navigation_receipt_chain_safety_")
    assert safety["pack_card_count"] == 4
    assert safety["ready_pack_count"] == 4
    assert safety["review_pack_count"] == 0
    assert safety["real_action_executed_count"] == 0
    assert safety["raw_evidence_revealed_count"] == 0
    assert safety["persistence_write_count"] == 0
    assert safety["all_packs_ready"] is True
    assert safety["all_metrics_ready"] is True
    assert safety["all_safety_flags_ok"] is True
    assert safety["summary_status"] == "version_compare_navigation_receipt_chain_safety_summary_ready"
    assert safety["summary_result_type"] == "owner_note_version_compare_navigation_receipt_chain_safety_summary_preview"
    assert safety["safe_preview_only"] is True
    assert safety["real_action_executed"] is False
    assert safety["real_raw_evidence_revealed"] is False

    assert len(groups) == 3
    group_by_key = {group["receipt_chain_checkpoint_group_key"]: group for group in groups}
    assert set(group_by_key) == {
        "ready_receipt_chain_packs",
        "review_receipt_chain_packs",
        "all_receipt_chain_packs",
    }

    assert group_by_key["ready_receipt_chain_packs"]["pack_card_count"] == 4
    assert group_by_key["ready_receipt_chain_packs"]["pack_numbers"] == [196, 197, 198, 199]
    assert group_by_key["review_receipt_chain_packs"]["pack_card_count"] == 0
    assert group_by_key["review_receipt_chain_packs"]["pack_numbers"] == []
    assert group_by_key["all_receipt_chain_packs"]["pack_card_count"] == 4
    assert group_by_key["all_receipt_chain_packs"]["pack_numbers"] == [196, 197, 198, 199]

    for group in groups:
        assert group["receipt_chain_checkpoint_group_id"].startswith("version_compare_navigation_receipt_chain_group_")
        assert group["label"]
        assert group["sequence"] in {1, 2, 3}
        assert isinstance(group["pack_card_ids"], list)
        assert group["pack_card_count"] == len(group["pack_card_ids"])
        assert group["group_status"] == "version_compare_navigation_receipt_chain_checkpoint_group_ready"
        assert group["group_result_type"] == "owner_note_version_compare_navigation_receipt_chain_checkpoint_group_preview"
        assert group["safe_preview_only"] is True
        assert group["real_action_executed"] is False
        assert group["real_filter_preference_saved"] is False
        assert group["real_navigation_state_persisted"] is False
        assert group["real_drawer_selection_saved"] is False
        assert group["real_raw_evidence_revealed"] is False

    assert checkpoint["receipt_chain_checkpoint_id"].startswith("version_compare_navigation_receipt_chain_checkpoint_")
    assert checkpoint["checkpoint_ok"] is True
    assert checkpoint["checkpoint_status"] == "version_compare_navigation_receipt_chain_checkpoint_ready"
    assert checkpoint["checkpoint_result_type"] == "owner_note_version_compare_navigation_receipt_chain_checkpoint_preview"
    assert checkpoint["pack_card_count"] == 4
    assert checkpoint["checkpoint_group_count"] == 3
    assert checkpoint["ready_pack_numbers"] == [196, 197, 198, 199]
    assert checkpoint["review_pack_numbers"] == []
    assert checkpoint["safety_summary_id"] == safety["receipt_chain_safety_summary_id"]
    assert checkpoint["safe_to_save_packs_196_to_200"] is True
    assert checkpoint["safe_preview_only"] is True
    assert checkpoint["real_action_executed"] is False
    assert checkpoint["real_raw_evidence_revealed"] is False


def test_pack_200_indexes_bridge_integrations_route_and_no_secrets():
    mod = importlib.import_module("tower.owner_note_vc_nav_receipt_chain_checkpoint_v200")
    payload = mod.build_owner_note_vc_nav_receipt_chain_checkpoint_v200_payload(force_refresh=True)

    indexes = payload["receipt_chain_checkpoint_indexes"]
    checkpoint = payload["final_receipt_chain_checkpoint"]

    assert indexes["pack_cards_by_id"]
    assert indexes["pack_cards_by_number"]
    assert indexes["pack_cards_by_status"]
    assert indexes["checkpoint_groups_by_id"]
    assert indexes["checkpoint_groups_by_key"]
    assert indexes["final_checkpoint_by_id"]

    assert set(indexes["pack_cards_by_number"]) == {"196", "197", "198", "199"}
    assert "version_compare_navigation_receipt_chain_pack_card_ready" in indexes["pack_cards_by_status"]
    assert len(indexes["pack_cards_by_status"]["version_compare_navigation_receipt_chain_pack_card_ready"]) == 4
    assert "ready_receipt_chain_packs" in indexes["checkpoint_groups_by_key"]
    assert "review_receipt_chain_packs" in indexes["checkpoint_groups_by_key"]
    assert "all_receipt_chain_packs" in indexes["checkpoint_groups_by_key"]
    assert checkpoint["receipt_chain_checkpoint_id"] in indexes["final_checkpoint_by_id"]

    bridge = mod.build_owner_note_vc_nav_receipt_chain_checkpoint_v200_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 200
    assert bridge["status"] == "ready"
    assert bridge["readiness_score"] == 100
    assert bridge["endpoint"] == "/tower/owner-note-vc-nav-receipt-chain-checkpoint-v200.json"
    assert bridge["source_pack_count"] == 4
    assert bridge["receipt_chain_pack_card_count"] == 4
    assert bridge["ready_pack_count"] == 4
    assert bridge["review_pack_count"] == 0
    assert bridge["checkpoint_group_count"] == 3
    assert bridge["final_checkpoint_count"] == 1
    assert bridge["safe_to_save_packs_196_to_200"] is True
    assert bridge["real_action_executed_count"] == 0
    assert bridge["raw_evidence_revealed_count"] == 0
    assert bridge["persistence_write_count"] == 0
    assert bridge["ready_pack_numbers"] == [196, 197, 198, 199]
    assert bridge["review_pack_numbers"] == []

    action = mod.build_owner_note_vc_nav_receipt_chain_checkpoint_v200_quick_action()
    assert action["id"] == "owner_note_vc_nav_receipt_chain_checkpoint_v200"
    assert action["href"] == "/tower/owner-note-vc-nav-receipt-chain-checkpoint-v200.json"
    assert action["status"] == "ready"

    section = mod.build_owner_note_vc_nav_receipt_chain_checkpoint_v200_unified_owner_section()
    assert section["section_id"] == "owner_note_vc_nav_receipt_chain_checkpoint_v200"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/owner-note-vc-nav-receipt-chain-checkpoint-v200.json"
    assert len(section["cards"]) >= 6

    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_200_owner_note_vc_nav_receipt_chain_checkpoint_v200_status_bridge")
    tower_bridge = status.build_pack_200_owner_note_vc_nav_receipt_chain_checkpoint_v200_status_bridge()
    assert tower_bridge["status"] == "ready"
    assert tower_bridge["readiness_score"] == 100
    assert tower_bridge["safe_to_save_packs_196_to_200"] is True

    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_200_owner_note_vc_nav_receipt_chain_checkpoint_v200_quick_action")
    assert hasattr(qa, "append_pack_200_owner_note_vc_nav_receipt_chain_checkpoint_v200_quick_action")
    actions = qa.append_pack_200_owner_note_vc_nav_receipt_chain_checkpoint_v200_quick_action([])
    assert any(item.get("id") == "owner_note_vc_nav_receipt_chain_checkpoint_v200" for item in actions)

    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_200_owner_note_vc_nav_receipt_chain_checkpoint_v200_unified_section")
    assert hasattr(unified, "append_pack_200_owner_note_vc_nav_receipt_chain_checkpoint_v200_section")
    sections = unified.append_pack_200_owner_note_vc_nav_receipt_chain_checkpoint_v200_section([])
    assert any(item.get("section_id") == "owner_note_vc_nav_receipt_chain_checkpoint_v200" for item in sections)

    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/owner-note-vc-nav-receipt-chain-checkpoint-v200.json" in app_text
    assert "tower_owner_note_vc_nav_receipt_chain_checkpoint_v200_json" in app_text
    assert "_pack_200_owner_note_vc_nav_receipt_chain_checkpoint_v200_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/owner-note-vc-nav-receipt-chain-checkpoint-v200.json" in route_text
    assert "_pack_200_owner_note_vc_nav_receipt_chain_checkpoint_v200_route_guard" in route_text

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
