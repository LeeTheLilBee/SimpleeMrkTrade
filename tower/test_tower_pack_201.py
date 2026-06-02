
"""
PACK 201 fast test - Receipt Chain Operational Handoff Preview.

Uses short safe module:
    tower.receipt_chain_operational_handoff_v201
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_201_payload_ready_and_preview_only():
    mod = importlib.import_module("tower.receipt_chain_operational_handoff_v201")
    payload = mod.build_receipt_chain_operational_handoff_v201_payload(force_refresh=True)

    assert payload["pack_number"] == 201
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/receipt-chain-operational-handoff-v201.json"
    assert payload["source_endpoint"] == "/tower/owner-note-vc-nav-receipt-chain-checkpoint-v200.json"

    required_true = [
        "simulated_only",
        "operational_handoff_preview_only",
        "receipt_chain_handoff_preview_only",
        "checkpoint_preview_only",
        "receipt_chain_checkpoint_preview_only",
        "owner_action_menu_preview_only",
        "evidence_map_preview_only",
        "routing_preview_only",
        "cached_non_recursive",
    ]

    for key in required_true:
        assert payload[key] is True, key

    required_false = [
        "real_action_executed",
        "real_handoff_executed",
        "real_owner_action_executed",
        "real_evidence_exported",
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
    assert summary["handoff_route_count"] == 5
    assert summary["owner_action_menu_item_count"] == 6
    assert summary["allowed_preview_action_count"] == 3
    assert summary["blocked_action_count"] == 3
    assert summary["evidence_map_item_count"] == 4
    assert summary["next_batch_card_count"] == 5
    assert summary["save_batch"] == "201-205"
    assert summary["save_after_pack"] == 205
    assert summary["safe_to_continue_to_pack_202"] is True
    assert summary["real_action_executed_count"] == 0
    assert summary["real_handoff_executed_count"] == 0
    assert summary["real_owner_action_executed_count"] == 0
    assert summary["real_evidence_exported_count"] == 0
    assert summary["raw_evidence_revealed_count"] == 0
    assert summary["persistence_write_count"] == 0

    checks = payload["readiness_checks"]
    required_checks = [
        "pack_200_ready",
        "pack_200_safe_to_save",
        "has_handoff_routes",
        "all_handoff_routes_ready",
        "has_owner_action_menu",
        "has_allowed_preview_actions",
        "has_blocked_actions",
        "all_owner_actions_ready_or_blocked",
        "has_evidence_map",
        "all_evidence_items_ready",
        "has_next_batch_board",
        "next_batch_save_after_205",
        "safety_summary_ready",
        "handoff_checkpoint_ready",
        "safe_to_continue_to_pack_202",
        "indexes_present",
        "checkpoint_index_present",
        "all_simulated_only",
        "all_operational_handoff_preview_only",
        "all_receipt_chain_handoff_preview_only",
        "no_real_action_executed",
        "no_real_handoff_executed",
        "no_real_owner_action_executed",
        "no_real_evidence_exported",
        "no_real_filter_preference_saved",
        "no_real_navigation_state_persisted",
        "no_real_drawer_selection_saved",
        "no_real_raw_evidence_revealed",
        "all_action_execution_blocked",
        "all_handoff_execution_blocked",
        "all_owner_action_execution_blocked",
        "all_evidence_export_blocked",
        "all_raw_evidence_reveal_blocked",
        "cached_non_recursive",
    ]

    for key in required_checks:
        assert checks[key] is True, key


def test_pack_201_routes_actions_evidence_and_next_batch():
    mod = importlib.import_module("tower.receipt_chain_operational_handoff_v201")
    payload = mod.build_receipt_chain_operational_handoff_v201_payload(force_refresh=True)

    routes = payload["handoff_routes"]
    actions = payload["owner_action_menu_items"]
    evidence = payload["handoff_evidence_map_items"]
    next_batch = payload["next_batch_board"]

    assert len(routes) == 5
    assert len(actions) == 6
    assert len(evidence) == 4
    assert len(next_batch) == 5

    expected_routes = {
        "checkpoint_to_operational_hardening",
        "checkpoint_to_receipt_vault_expansion",
        "checkpoint_to_owner_workflow_surface",
        "checkpoint_to_recheck_expiration_hooks",
        "checkpoint_to_gateway_readiness",
    }

    route_keys = {route["route_key"] for route in routes}
    assert route_keys == expected_routes

    for route in routes:
        assert route["handoff_route_id"].startswith("receipt_chain_handoff_route_")
        assert route["route_key"] in expected_routes
        assert route["label"]
        assert route["description"]
        assert route["sequence"] in {1, 2, 3, 4, 5}
        assert route["route_state"] == "ready"
        assert route["source_checkpoint_endpoint"] == "/tower/owner-note-vc-nav-receipt-chain-checkpoint-v200.json"
        assert route["route_status"] == "receipt_chain_handoff_route_preview_ready"
        assert route["route_result_type"] == "tower_receipt_chain_operational_handoff_route_preview"
        assert route["safe_preview_only"] is True

        assert route["simulated_only"] is True
        assert route["operational_handoff_preview_only"] is True
        assert route["receipt_chain_handoff_preview_only"] is True
        assert route["real_action_executed"] is False
        assert route["real_handoff_executed"] is False
        assert route["real_owner_action_executed"] is False
        assert route["real_evidence_exported"] is False
        assert route["real_raw_evidence_revealed"] is False
        assert route["action_execution_allowed_now"] is False
        assert route["handoff_execution_allowed_now"] is False
        assert route["owner_action_execution_allowed_now"] is False
        assert route["evidence_export_allowed_now"] is False
        assert route["raw_evidence_reveal_allowed"] is False

    expected_actions = {
        "review_handoff_summary",
        "preview_next_batch",
        "open_receipt_chain_checkpoint",
        "blocked_execute_handoff",
        "blocked_export_evidence_bundle",
        "blocked_grant_gateway_access",
    }

    action_keys = {action["owner_action_key"] for action in actions}
    assert action_keys == expected_actions

    allowed = [action for action in actions if action["allowed_in_preview"] is True]
    blocked = [action for action in actions if action["blocked_in_preview"] is True]

    assert len(allowed) == 3
    assert len(blocked) == 3

    for action in actions:
        assert action["owner_action_menu_item_id"].startswith("receipt_chain_handoff_owner_action_")
        assert action["owner_action_key"] in expected_actions
        assert action["label"]
        assert action["description"]
        assert action["sequence"] in {1, 2, 3, 4, 5, 6}
        assert action["ready_route_count"] == 5
        assert action["executes_real_action"] is False
        assert action["action_status"] in {
            "receipt_chain_handoff_owner_action_preview_ready",
            "receipt_chain_handoff_owner_action_preview_blocked",
        }
        assert action["action_result_type"] == "tower_receipt_chain_operational_handoff_owner_action_preview"
        assert action["safe_preview_only"] is True
        assert action["real_action_executed"] is False
        assert action["real_handoff_executed"] is False
        assert action["real_owner_action_executed"] is False
        assert action["real_evidence_exported"] is False
        assert action["real_raw_evidence_revealed"] is False

    for action in allowed:
        assert action["owner_action_key"] in {
            "review_handoff_summary",
            "preview_next_batch",
            "open_receipt_chain_checkpoint",
        }
        assert action["blocked_in_preview"] is False
        assert action["action_status"] == "receipt_chain_handoff_owner_action_preview_ready"

    for action in blocked:
        assert action["owner_action_key"] in {
            "blocked_execute_handoff",
            "blocked_export_evidence_bundle",
            "blocked_grant_gateway_access",
        }
        assert action["allowed_in_preview"] is False
        assert action["action_status"] == "receipt_chain_handoff_owner_action_preview_blocked"

    pack_numbers = {item["source_pack_number"] for item in evidence}
    assert pack_numbers == {196, 197, 198, 199}

    for item in evidence:
        assert item["handoff_evidence_map_item_id"].startswith("receipt_chain_handoff_evidence_")
        assert item["source_pack_number"] in {196, 197, 198, 199}
        assert item["source_pack_id"] == f"PACK_{item['source_pack_number']}"
        assert item["source_endpoint"]
        assert item["source_card_id"]
        assert item["source_card_status"] == "version_compare_navigation_receipt_chain_pack_card_ready"
        assert item["metric_checks_ok"] is True
        assert item["safety_flags_ok"] is True
        assert item["sequence"] in {1, 2, 3, 4}
        assert len(item["mapped_route_keys"]) == 5
        assert set(item["mapped_route_keys"]) == expected_routes
        assert item["raw_evidence_redacted"] is True
        assert item["evidence_export_allowed_now"] is False
        assert item["map_status"] == "receipt_chain_handoff_evidence_map_item_preview_ready"
        assert item["map_result_type"] == "tower_receipt_chain_operational_handoff_evidence_map_preview"
        assert item["safe_preview_only"] is True
        assert item["real_evidence_exported"] is False
        assert item["real_raw_evidence_revealed"] is False

    next_pack_numbers = [card["pack_number"] for card in next_batch]
    assert next_pack_numbers == [201, 202, 203, 204, 205]

    for card in next_batch:
        assert card["next_batch_card_id"].startswith("receipt_chain_next_batch_card_")
        assert card["pack_number"] in {201, 202, 203, 204, 205}
        assert card["label"]
        assert card["lane_state"] in {"active_current_pack", "planned_preview_only", "planned_checkpoint"}
        assert card["sequence"] in {1, 2, 3, 4, 5}
        assert card["save_batch"] == "201-205"
        assert card["save_after_pack"] == 205
        assert card["card_status"] == "receipt_chain_next_batch_card_preview_ready"
        assert card["card_result_type"] == "tower_receipt_chain_next_batch_card_preview"
        assert card["safe_preview_only"] is True
        assert card["real_action_executed"] is False
        assert card["real_raw_evidence_revealed"] is False


def test_pack_201_safety_checkpoint_indexes_bridge_integrations_route_and_no_secrets():
    mod = importlib.import_module("tower.receipt_chain_operational_handoff_v201")
    payload = mod.build_receipt_chain_operational_handoff_v201_payload(force_refresh=True)

    safety = payload["handoff_safety_summary"]
    checkpoint = payload["operational_handoff_checkpoint"]
    indexes = payload["operational_handoff_indexes"]

    assert safety["handoff_safety_summary_id"].startswith("receipt_chain_handoff_safety_")
    assert safety["handoff_route_count"] == 5
    assert safety["ready_handoff_route_count"] == 5
    assert safety["owner_action_menu_item_count"] == 6
    assert safety["allowed_preview_action_count"] == 3
    assert safety["blocked_action_count"] == 3
    assert safety["evidence_map_item_count"] == 4
    assert safety["real_action_executed_count"] == 0
    assert safety["real_handoff_executed_count"] == 0
    assert safety["real_owner_action_executed_count"] == 0
    assert safety["real_evidence_exported_count"] == 0
    assert safety["raw_evidence_revealed_count"] == 0
    assert safety["persistence_write_count"] == 0
    assert safety["all_routes_preview_only"] is True
    assert safety["all_owner_actions_preview_only"] is True
    assert safety["all_evidence_maps_preview_only"] is True
    assert safety["all_real_execution_blocked"] is True
    assert safety["summary_status"] == "receipt_chain_handoff_safety_summary_preview_ready"
    assert safety["summary_result_type"] == "tower_receipt_chain_operational_handoff_safety_summary_preview"
    assert safety["safe_preview_only"] is True
    assert safety["real_action_executed"] is False
    assert safety["real_handoff_executed"] is False
    assert safety["real_owner_action_executed"] is False
    assert safety["real_evidence_exported"] is False
    assert safety["real_raw_evidence_revealed"] is False

    assert checkpoint["operational_handoff_checkpoint_id"].startswith("receipt_chain_operational_handoff_checkpoint_")
    assert checkpoint["checkpoint_ok"] is True
    assert checkpoint["checkpoint_status"] == "receipt_chain_operational_handoff_checkpoint_preview_ready"
    assert checkpoint["checkpoint_result_type"] == "tower_receipt_chain_operational_handoff_checkpoint_preview"
    assert checkpoint["safe_to_continue_to_pack_202"] is True
    assert checkpoint["save_batch"] == "201-205"
    assert checkpoint["save_after_pack"] == 205
    assert checkpoint["handoff_safety_summary_id"] == safety["handoff_safety_summary_id"]
    assert checkpoint["safe_preview_only"] is True
    assert checkpoint["real_action_executed"] is False
    assert checkpoint["real_handoff_executed"] is False
    assert checkpoint["real_owner_action_executed"] is False
    assert checkpoint["real_evidence_exported"] is False
    assert checkpoint["real_raw_evidence_revealed"] is False

    assert indexes["handoff_routes_by_id"]
    assert indexes["handoff_routes_by_key"]
    assert indexes["owner_action_menu_items_by_id"]
    assert indexes["owner_action_menu_items_by_key"]
    assert indexes["evidence_map_items_by_id"]
    assert indexes["evidence_map_items_by_pack_number"]
    assert indexes["next_batch_cards_by_id"]
    assert indexes["next_batch_cards_by_pack_number"]
    assert indexes["operational_handoff_checkpoint_by_id"]

    assert "checkpoint_to_operational_hardening" in indexes["handoff_routes_by_key"]
    assert "blocked_execute_handoff" in indexes["owner_action_menu_items_by_key"]
    assert set(indexes["evidence_map_items_by_pack_number"]) == {"196", "197", "198", "199"}
    assert set(indexes["next_batch_cards_by_pack_number"]) == {"201", "202", "203", "204", "205"}
    assert checkpoint["operational_handoff_checkpoint_id"] in indexes["operational_handoff_checkpoint_by_id"]

    bridge = mod.build_receipt_chain_operational_handoff_v201_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 201
    assert bridge["status"] == "ready"
    assert bridge["readiness_score"] == 100
    assert bridge["endpoint"] == "/tower/receipt-chain-operational-handoff-v201.json"
    assert bridge["handoff_route_count"] == 5
    assert bridge["owner_action_menu_item_count"] == 6
    assert bridge["allowed_preview_action_count"] == 3
    assert bridge["blocked_action_count"] == 3
    assert bridge["evidence_map_item_count"] == 4
    assert bridge["next_batch_card_count"] == 5
    assert bridge["save_batch"] == "201-205"
    assert bridge["save_after_pack"] == 205
    assert bridge["safe_to_continue_to_pack_202"] is True
    assert bridge["real_action_executed_count"] == 0
    assert bridge["real_handoff_executed_count"] == 0
    assert bridge["real_owner_action_executed_count"] == 0
    assert bridge["real_evidence_exported_count"] == 0
    assert bridge["raw_evidence_revealed_count"] == 0
    assert bridge["persistence_write_count"] == 0

    action = mod.build_receipt_chain_operational_handoff_v201_quick_action()
    assert action["id"] == "receipt_chain_operational_handoff_v201"
    assert action["href"] == "/tower/receipt-chain-operational-handoff-v201.json"
    assert action["status"] == "ready"

    section = mod.build_receipt_chain_operational_handoff_v201_unified_owner_section()
    assert section["section_id"] == "receipt_chain_operational_handoff_v201"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/receipt-chain-operational-handoff-v201.json"
    assert len(section["cards"]) >= 6

    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_201_receipt_chain_operational_handoff_v201_status_bridge")
    tower_bridge = status.build_pack_201_receipt_chain_operational_handoff_v201_status_bridge()
    assert tower_bridge["status"] == "ready"
    assert tower_bridge["readiness_score"] == 100
    assert tower_bridge["safe_to_continue_to_pack_202"] is True

    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_201_receipt_chain_operational_handoff_v201_quick_action")
    assert hasattr(qa, "append_pack_201_receipt_chain_operational_handoff_v201_quick_action")
    actions = qa.append_pack_201_receipt_chain_operational_handoff_v201_quick_action([])
    assert any(item.get("id") == "receipt_chain_operational_handoff_v201" for item in actions)

    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_201_receipt_chain_operational_handoff_v201_unified_section")
    assert hasattr(unified, "append_pack_201_receipt_chain_operational_handoff_v201_section")
    sections = unified.append_pack_201_receipt_chain_operational_handoff_v201_section([])
    assert any(item.get("section_id") == "receipt_chain_operational_handoff_v201" for item in sections)

    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/receipt-chain-operational-handoff-v201.json" in app_text
    assert "tower_receipt_chain_operational_handoff_v201_json" in app_text
    assert "_pack_201_receipt_chain_operational_handoff_v201_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/receipt-chain-operational-handoff-v201.json" in route_text
    assert "_pack_201_receipt_chain_operational_handoff_v201_route_guard" in route_text

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
