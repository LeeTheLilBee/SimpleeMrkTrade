"""
SEARCHABLE LABEL: TOWER_PACK_336_HANDOFF_POLICY_ROUTE_ENFORCEMENT_OWNER_ACCEPTANCE_RETRIEVAL_RECEIPT_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_336_contract_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_retrieval_receipt_index_v336")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_retrieval_receipt_index_preview()

    assert payload["pack"] == "336"
    assert payload["pack_number"] == 336
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-owner-acceptance-retrieval-receipt-index-v336.json"
    assert payload["tower_sublayer"] == "Handoff Policy Route Enforcement Owner Acceptance Retrieval Receipt layer"
    assert payload["source_pack"] == "335"
    assert payload["source_closed_batch"] == "331-335"
    assert payload["save_batch"] == "336-340"
    assert payload["save_after_pack"] == 340
    assert payload["next_pack"] == "337"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["preview_only"] is True
    assert payload["receipt_preview_only"] is True
    assert payload["retrieval_preview_only"] is True
    assert payload["archive_preview_only"] is True
    assert payload["simulation_only"] is True
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True
    assert payload["safe_to_continue_to_pack_337"] is True
    assert payload["prepare_pack_337_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_retrieval_receipt_detail_drawer"]["pack"] == "337"


def test_pack_336_summary_safety_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_retrieval_receipt_index_v336")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_retrieval_receipt_index_preview()
    summary = payload["owner_acceptance_retrieval_receipt_index_summary"]

    assert summary["card_count"] >= 15
    assert summary["field_count"] >= 120
    assert summary["action_count"] >= 15
    assert summary["checkpoint_count"] >= 13
    assert summary["enabled_action_count"] >= 15
    assert summary["blocked_action_count"] >= 15
    assert summary["redacted_field_count"] >= 30

    assert summary["all_cards_preview_only"] is True
    assert summary["all_cards_pointer_only"] is True
    assert summary["all_cards_receipt_pointer_only"] is True
    assert summary["all_cards_retrieval_pointer_only"] is True
    assert summary["all_cards_archive_pointer_only"] is True
    assert summary["all_cards_no_writes"] is True
    assert summary["all_cards_non_executable"] is True
    assert summary["all_cards_non_retrievable"] is True
    assert summary["all_cards_non_receiptable"] is True
    assert summary["all_cards_non_signable"] is True
    assert summary["all_cards_non_sealable"] is True
    assert summary["all_cards_non_restorable"] is True
    assert summary["all_cards_non_deletable"] is True
    assert summary["all_cards_non_purgeable"] is True
    assert summary["all_cards_non_exportable"] is True
    assert summary["all_cards_no_raw_evidence"] is True
    assert summary["all_fields_no_writes"] is True
    assert summary["all_fields_no_raw_evidence"] is True
    assert summary["all_actions_safe"] is True
    assert summary["all_checkpoints_passed"] is True
    assert summary["all_checkpoints_no_writes"] is True
    assert summary["owner_acceptance_retrieval_receipt_index_ready"] is True

    assert summary["real_owner_acceptance_retrieval_receipt_execute_enabled"] is False
    assert summary["real_owner_acceptance_retrieval_receipt_write_enabled"] is False
    assert summary["real_owner_acceptance_retrieval_receipt_apply_enabled"] is False
    assert summary["real_owner_acceptance_retrieval_receipt_sign_enabled"] is False
    assert summary["real_owner_acceptance_retrieval_receipt_seal_enabled"] is False
    assert summary["real_owner_acceptance_retrieval_receipt_export_enabled"] is False
    assert summary["real_owner_acceptance_retrieval_receipt_delete_enabled"] is False
    assert summary["real_retrieval_execute_enabled"] is False
    assert summary["real_archive_write_enabled"] is False
    assert summary["real_archive_restore_enabled"] is False
    assert summary["real_archive_delete_enabled"] is False
    assert summary["real_archive_purge_enabled"] is False
    assert summary["real_archive_export_enabled"] is False
    assert summary["real_evidence_reveal_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["real_receipt_write_enabled"] is False
    assert summary["real_receipt_sign_enabled"] is False
    assert summary["real_receipt_seal_enabled"] is False
    assert summary["real_receipt_export_enabled"] is False
    assert summary["real_action_execution_enabled"] is False


def test_pack_336_payload_shapes_and_endpoint():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_retrieval_receipt_index_v336")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_retrieval_receipt_index_preview()

    cards = payload["owner_acceptance_retrieval_receipt_index_cards"]
    fields = payload["owner_acceptance_retrieval_receipt_index_fields"]
    actions = payload["owner_acceptance_retrieval_receipt_index_actions"]
    checkpoints = payload["owner_acceptance_retrieval_receipt_index_checkpoints"]

    assert cards
    assert fields
    assert actions
    assert checkpoints

    assert all(row["preview_only"] is True for row in cards)
    assert all(row["pointer_only"] is True for row in cards)
    assert all(row["receipt_pointer_only"] is True for row in cards)
    assert all(row["retrieval_pointer_only"] is True for row in cards)
    assert all(row["archive_pointer_only"] is True for row in cards)
    assert all(row["writes_state"] is False for row in cards)
    assert all(row["executable"] is False for row in cards)
    assert all(row["retrievable"] is False for row in cards)
    assert all(row["receiptable"] is False for row in cards)
    assert all(row["signable"] is False for row in cards)
    assert all(row["sealable"] is False for row in cards)
    assert all(row["restorable"] is False for row in cards)
    assert all(row["deletable"] is False for row in cards)
    assert all(row["purgeable"] is False for row in cards)
    assert all(row["exportable"] is False for row in cards)
    assert all(row["raw_evidence_visible"] is False for row in cards)

    assert all(row["writes_state"] is False for row in fields)
    assert all(row["raw_evidence_visible"] is False for row in fields)

    preview_actions = [row for row in actions if row["result"] == "preview_allowed"]
    blocked_actions = [row for row in actions if row["result"] == "blocked_preview_only"]
    assert preview_actions
    assert blocked_actions
    assert all(row["enabled"] is True for row in preview_actions)
    assert all(row["enabled"] is False for row in blocked_actions)

    assert all(row["passed"] is True for row in checkpoints)
    assert all(row["writes_state"] is False for row in checkpoints)

    import web.app as web_app
    app = getattr(web_app, "app", None)
    assert app is not None
    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-owner-acceptance-retrieval-receipt-index-v336.json" in rules

    response = app.test_client().get("/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-owner-acceptance-retrieval-receipt-index-v336.json")
    assert response.status_code in {200, 302, 401, 403}
    if response.status_code == 200:
        data = response.get_json()
        assert data["pack"] == "336"
        assert data["status"] == "ready"
        assert data["readiness"] == 100
        assert data["receipt_preview_only"] is True
        assert data["retrieval_preview_only"] is True
        assert data["safe_to_continue_to_pack_337"] is True


def test_pack_336_bridge_prep_and_defensive_copy():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_retrieval_receipt_index_v336")

    bridge = mod.build_pack_336_status_bridge()
    assert bridge["pack"] == "336"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["card_count"] >= 15
    assert bridge["owner_acceptance_retrieval_receipt_index_ready"] is True
    assert bridge["safe_to_continue_to_pack_337"] is True

    prep = mod.prepare_pack_337_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_retrieval_receipt_detail_drawer()
    assert prep["ready"] is True
    assert prep["next_pack"] == "337"
    assert prep["source_pack"] == "336"
    assert prep["safe_to_continue"] is True

    first = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_retrieval_receipt_index_preview()
    second = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_retrieval_receipt_index_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_retrieval_receipt_index_preview()
    assert third["status"] == "ready"
