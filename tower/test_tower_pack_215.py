
"""
PACK 215 fast test - Receipt Chain Batch 211-215 Checkpoint Preview.

Uses short safe module:
    tower.receipt_chain_batch_211_215_checkpoint_v215
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_215_payload_ready_and_preview_only():
    mod = importlib.import_module("tower.receipt_chain_batch_211_215_checkpoint_v215")
    payload = mod.build_receipt_chain_batch_211_215_checkpoint_v215_payload(force_refresh=True)

    assert payload["pack_number"] == 215
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/receipt-chain-batch-211-215-checkpoint-v215.json"
    assert payload["source_endpoint"] == "/tower/receipt-chain-evidence-detail-drawer-v214.json"

    required_true = [
        "simulated_only",
        "batch_checkpoint_preview_only",
        "source_pack_readiness_preview_only",
        "recovered_dependency_awareness_preview_only",
        "evidence_detail_rollup_preview_only",
        "batch_safety_rollup_preview_only",
        "save_push_readiness_preview_only",
        "next_batch_handoff_preview_only",
        "raw_evidence_redacted",
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
        "real_save_executed",
        "real_push_executed",
        "real_commit_executed",
        "real_git_write_executed",
        "real_batch_checkpoint_written",
        "real_batch_checkpoint_sealed",
        "real_archive_written",
        "real_archive_packet_written",
        "real_archive_packet_sealed",
        "real_archive_exported",
        "real_gateway_access_granted",
        "real_raw_evidence_revealed",
    ]

    for key in required_false:
        assert payload[key] is False, key

    summary = payload["summary"]

    assert summary["readiness_score"] == 100
    assert summary["source_pack_count"] == 4
    assert summary["ready_source_pack_count"] == 4
    assert summary["recovered_dependency_count"] == 3
    assert summary["ready_recovered_dependency_count"] == 3
    assert summary["evidence_detail_rollup_count"] == 1
    assert summary["batch_safety_rollup_count"] == 1
    assert summary["save_push_readiness_count"] == 1
    assert summary["next_batch_handoff_count"] == 5
    assert summary["final_checkpoint_count"] == 1
    assert summary["total_real_flag_count"] == 0
    assert summary["total_raw_evidence_revealed_count"] == 0
    assert summary["raw_field_count"] == 0
    assert summary["real_save_executed_count"] == 0
    assert summary["real_push_executed_count"] == 0
    assert summary["real_commit_executed_count"] == 0
    assert summary["real_batch_checkpoint_written_count"] == 0
    assert summary["real_batch_checkpoint_sealed_count"] == 0
    assert summary["real_evidence_exported_count"] == 0
    assert summary["real_archive_written_count"] == 0
    assert summary["real_archive_packet_sealed_count"] == 0
    assert summary["raw_evidence_revealed_count"] == 0
    assert summary["safe_to_save_recovered_packs_208_to_215"] is True
    assert summary["safe_to_push_recovered_packs_208_to_215"] is True
    assert summary["safe_to_continue_to_pack_216"] is True
    assert summary["closed_batch"] == "211-215"
    assert summary["recovered_dependency_batch"] == "208-210"
    assert summary["save_batch"] == "208-215"
    assert summary["save_after_pack"] == 215
    assert summary["next_batch"] == "216-220"

    checks = payload["readiness_checks"]
    required_checks = [
        "has_four_source_packs_211_214",
        "pack_211_ready",
        "pack_212_ready",
        "pack_213_ready",
        "pack_214_ready",
        "has_recovered_dependencies_208_210",
        "pack_208_recovered_ready",
        "pack_209_recovered_ready",
        "pack_210_recovered_ready",
        "evidence_rollup_ready",
        "safety_rollup_ready",
        "save_push_readiness_ready",
        "safe_to_save_recovered_packs_208_to_215",
        "safe_to_push_recovered_packs_208_to_215",
        "has_next_batch_handoffs_216_220",
        "all_next_batch_handoffs_ready",
        "checkpoint_ready",
        "safe_to_continue_to_pack_216",
        "indexes_present",
        "checkpoint_index_present",
        "all_simulated_only",
        "all_batch_checkpoint_preview_only",
        "no_real_save_executed",
        "no_real_push_executed",
        "no_real_commit_executed",
        "no_real_evidence_exported",
        "no_real_archive_written",
        "no_real_archive_sealed",
        "no_real_raw_evidence_revealed",
        "all_real_flags_zero",
        "all_raw_fields_zero",
        "cached_non_recursive",
    ]

    for key in required_checks:
        assert checks[key] is True, key


def test_pack_215_source_cards_recovered_dependencies_rollups_save_push_and_handoffs():
    mod = importlib.import_module("tower.receipt_chain_batch_211_215_checkpoint_v215")
    payload = mod.build_receipt_chain_batch_211_215_checkpoint_v215_payload(force_refresh=True)

    source_cards = payload["source_pack_readiness_cards"]
    dependency_cards = payload["recovered_dependency_awareness_cards"]
    evidence_rollup = payload["evidence_detail_rollup"]
    safety_rollup = payload["batch_safety_rollup"]
    save_push = payload["save_push_readiness_preview"]
    handoffs = payload["next_batch_handoff_previews"]
    checkpoint = payload["batch_checkpoint"]
    indexes = payload["batch_checkpoint_indexes"]

    assert len(source_cards) == 4
    assert len(dependency_cards) == 3
    assert len(handoffs) == 5

    source_pack_numbers = {item["pack_number"] for item in source_cards}
    assert source_pack_numbers == {211, 212, 213, 214}

    for item in source_cards:
        assert item["source_pack_readiness_card_id"].startswith("receipt_chain_batch_211_215_source_pack_")
        assert item["pack_number"] in {211, 212, 213, 214}
        assert item["pack_id"] == f"PACK_{item['pack_number']}"
        assert item["sequence"] in {1, 2, 3, 4}
        assert item["endpoint"].startswith("/tower/")
        assert item["source_status"] == "ready"
        assert item["source_readiness_score"] == 100
        assert item["source_pack_ready"] is True
        assert item["real_flag_count"] == 0
        assert item["raw_evidence_revealed_count"] == 0
        assert item["source_safe_to_continue"] is True
        assert item["card_status"] == "receipt_chain_batch_211_215_source_pack_card_ready"
        assert item["safe_preview_only"] is True
        assert item["real_raw_evidence_revealed"] is False

    dependency_pack_numbers = {item["pack_number"] for item in dependency_cards}
    assert dependency_pack_numbers == {208, 209, 210}

    for item in dependency_cards:
        assert item["recovered_dependency_card_id"].startswith("receipt_chain_recovered_dependency_")
        assert item["pack_number"] in {208, 209, 210}
        assert item["pack_id"] == f"PACK_{item['pack_number']}"
        assert item["sequence"] in {1, 2, 3}
        assert item["endpoint"].startswith("/tower/")
        assert item["source_status"] == "ready"
        assert item["source_readiness_score"] == 100
        assert item["dependency_ready"] is True
        assert item["dependency_recovered_locally"] is True
        assert item["must_save_push_to_remote"] is True
        assert item["real_flag_count"] == 0
        assert item["raw_evidence_revealed_count"] == 0
        assert item["card_status"] == "receipt_chain_recovered_dependency_awareness_preview_ready"
        assert item["safe_preview_only"] is True
        assert item["real_raw_evidence_revealed"] is False

    assert evidence_rollup["rollup_status"] == "receipt_chain_evidence_detail_rollup_preview_ready"
    assert evidence_rollup["redacted_evidence_panel_count"] == 6
    assert evidence_rollup["evidence_source_trace_card_count"] == 6
    assert evidence_rollup["evidence_comparison_row_count"] == 8
    assert evidence_rollup["evidence_review_tab_count"] == 6
    assert evidence_rollup["evidence_action_menu_item_count"] == 8
    assert evidence_rollup["raw_field_count"] == 0
    assert evidence_rollup["real_evidence_exported_count"] == 0
    assert evidence_rollup["real_archive_packet_written_count"] == 0
    assert evidence_rollup["real_archive_packet_sealed_count"] == 0
    assert evidence_rollup["raw_evidence_revealed_count"] == 0
    assert evidence_rollup["safe_preview_only"] is True

    assert safety_rollup["safety_status"] == "receipt_chain_batch_211_215_safety_rollup_preview_ready"
    assert safety_rollup["source_pack_count"] == 4
    assert safety_rollup["ready_source_pack_count"] == 4
    assert safety_rollup["recovered_dependency_count"] == 3
    assert safety_rollup["ready_recovered_dependency_count"] == 3
    assert safety_rollup["total_real_flag_count"] == 0
    assert safety_rollup["total_raw_evidence_revealed_count"] == 0
    assert safety_rollup["raw_field_count"] == 0
    assert safety_rollup["all_source_packs_ready"] is True
    assert safety_rollup["all_recovered_dependencies_ready"] is True
    assert safety_rollup["all_real_flags_zero"] is True
    assert safety_rollup["all_raw_reveals_zero"] is True
    assert safety_rollup["all_raw_fields_zero"] is True
    assert safety_rollup["safe_preview_only"] is True

    assert save_push["readiness_status"] == "receipt_chain_batch_211_215_save_push_readiness_preview_ready"
    assert save_push["safe_to_save_recovered_packs_208_to_215"] is True
    assert save_push["safe_to_push_recovered_packs_208_to_215"] is True
    assert save_push["must_include_recovered_packs_208_to_210"] is True
    assert save_push["must_include_batch_211_to_215"] is True
    assert "Pack 207" in save_push["remote_recovery_note"]
    assert "208-215" in save_push["recommended_commit_message"] or "208-212" in save_push["recommended_commit_message"]
    assert save_push["real_save_executed"] is False
    assert save_push["real_push_executed"] is False
    assert save_push["real_commit_executed"] is False
    assert save_push["save_allowed_now"] is False
    assert save_push["push_allowed_now"] is False
    assert save_push["commit_allowed_now"] is False

    handoff_pack_numbers = {item["pack_number"] for item in handoffs}
    assert handoff_pack_numbers == {216, 217, 218, 219, 220}

    for item in handoffs:
        assert item["next_batch_handoff_preview_id"].startswith("receipt_chain_next_batch_")
        assert item["pack_number"] in {216, 217, 218, 219, 220}
        assert item["pack_id"] == f"PACK_{item['pack_number']}"
        assert item["sequence"] in {1, 2, 3, 4, 5}
        assert item["target_batch"] == "216-220"
        assert item["planned_endpoint_preview"].startswith("/tower/")
        assert item["handoff_status"] == "receipt_chain_next_batch_216_220_handoff_preview_ready"
        assert item["safe_preview_only"] is True

    assert checkpoint["checkpoint_ok"] is True
    assert checkpoint["checkpoint_status"] == "receipt_chain_batch_211_215_checkpoint_preview_ready"
    assert checkpoint["safe_to_save_recovered_packs_208_to_215"] is True
    assert checkpoint["safe_to_push_recovered_packs_208_to_215"] is True
    assert checkpoint["safe_to_continue_to_pack_216"] is True
    assert checkpoint["closed_batch"] == "211-215"
    assert checkpoint["recovered_dependency_batch"] == "208-210"
    assert checkpoint["save_batch"] == "208-215"
    assert checkpoint["save_after_pack"] == 215
    assert checkpoint["next_batch"] == "216-220"

    assert indexes["source_pack_cards_by_pack_number"]
    assert indexes["recovered_dependency_cards_by_pack_number"]
    assert indexes["next_batch_handoffs_by_pack_number"]
    assert indexes["checkpoint_by_id"]
    assert set(indexes["source_pack_cards_by_pack_number"].keys()) == {"211", "212", "213", "214"}
    assert set(indexes["recovered_dependency_cards_by_pack_number"].keys()) == {"208", "209", "210"}
    assert set(indexes["next_batch_handoffs_by_pack_number"].keys()) == {"216", "217", "218", "219", "220"}
    assert checkpoint["batch_checkpoint_id"] in indexes["checkpoint_by_id"]


def test_pack_215_bridge_integrations_route_and_no_secrets():
    mod = importlib.import_module("tower.receipt_chain_batch_211_215_checkpoint_v215")
    payload = mod.build_receipt_chain_batch_211_215_checkpoint_v215_payload(force_refresh=True)
    bridge = mod.build_receipt_chain_batch_211_215_checkpoint_v215_status_bridge(force_refresh=True)

    assert bridge["pack_number"] == 215
    assert bridge["status"] == "ready"
    assert bridge["readiness_score"] == 100
    assert bridge["endpoint"] == "/tower/receipt-chain-batch-211-215-checkpoint-v215.json"
    assert bridge["source_pack_count"] == 4
    assert bridge["ready_source_pack_count"] == 4
    assert bridge["recovered_dependency_count"] == 3
    assert bridge["ready_recovered_dependency_count"] == 3
    assert bridge["evidence_detail_rollup_count"] == 1
    assert bridge["batch_safety_rollup_count"] == 1
    assert bridge["save_push_readiness_count"] == 1
    assert bridge["next_batch_handoff_count"] == 5
    assert bridge["final_checkpoint_count"] == 1
    assert bridge["total_real_flag_count"] == 0
    assert bridge["total_raw_evidence_revealed_count"] == 0
    assert bridge["raw_field_count"] == 0
    assert bridge["real_save_executed_count"] == 0
    assert bridge["real_push_executed_count"] == 0
    assert bridge["real_commit_executed_count"] == 0
    assert bridge["real_batch_checkpoint_written_count"] == 0
    assert bridge["real_batch_checkpoint_sealed_count"] == 0
    assert bridge["real_evidence_exported_count"] == 0
    assert bridge["real_archive_written_count"] == 0
    assert bridge["real_archive_packet_sealed_count"] == 0
    assert bridge["raw_evidence_revealed_count"] == 0
    assert bridge["safe_to_save_recovered_packs_208_to_215"] is True
    assert bridge["safe_to_push_recovered_packs_208_to_215"] is True
    assert bridge["safe_to_continue_to_pack_216"] is True
    assert bridge["closed_batch"] == "211-215"
    assert bridge["recovered_dependency_batch"] == "208-210"
    assert bridge["save_batch"] == "208-215"
    assert bridge["save_after_pack"] == 215
    assert bridge["next_batch"] == "216-220"

    action = mod.build_receipt_chain_batch_211_215_checkpoint_v215_quick_action()
    assert action["id"] == "receipt_chain_batch_211_215_checkpoint_v215"
    assert action["href"] == "/tower/receipt-chain-batch-211-215-checkpoint-v215.json"
    assert action["status"] == "ready"

    section = mod.build_receipt_chain_batch_211_215_checkpoint_v215_unified_owner_section()
    assert section["section_id"] == "receipt_chain_batch_211_215_checkpoint_v215"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/receipt-chain-batch-211-215-checkpoint-v215.json"
    assert len(section["cards"]) >= 6

    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_215_receipt_chain_batch_211_215_checkpoint_v215_status_bridge")
    tower_bridge = status.build_pack_215_receipt_chain_batch_211_215_checkpoint_v215_status_bridge()
    assert tower_bridge["status"] == "ready"
    assert tower_bridge["readiness_score"] == 100
    assert tower_bridge["safe_to_continue_to_pack_216"] is True

    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_215_receipt_chain_batch_211_215_checkpoint_v215_quick_action")
    assert hasattr(qa, "append_pack_215_receipt_chain_batch_211_215_checkpoint_v215_quick_action")
    actions = qa.append_pack_215_receipt_chain_batch_211_215_checkpoint_v215_quick_action([])
    assert any(item.get("id") == "receipt_chain_batch_211_215_checkpoint_v215" for item in actions)

    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_215_receipt_chain_batch_211_215_checkpoint_v215_unified_section")
    assert hasattr(unified, "append_pack_215_receipt_chain_batch_211_215_checkpoint_v215_section")
    sections = unified.append_pack_215_receipt_chain_batch_211_215_checkpoint_v215_section([])
    assert any(item.get("section_id") == "receipt_chain_batch_211_215_checkpoint_v215" for item in sections)

    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/receipt-chain-batch-211-215-checkpoint-v215.json" in app_text
    assert "tower_receipt_chain_batch_211_215_checkpoint_v215_json" in app_text
    assert "_pack_215_receipt_chain_batch_211_215_checkpoint_v215_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/receipt-chain-batch-211-215-checkpoint-v215.json" in route_text
    assert "_pack_215_receipt_chain_batch_211_215_checkpoint_v215_route_guard" in route_text

    payload_text = str(payload).lower()
    forbidden_fragments = [
        "sk_" + "live_",
        "sk_" + "test_",
        "github_" + "pat_",
        "g" + "hp_",
        "xox" + "b-",
        "aws_" + "secret_access_key",
        "private_key" + "-----",
        "broker_" + "token_value",
        "api_" + "secret_value",
    ]

    for fragment in forbidden_fragments:
        assert fragment not in payload_text
