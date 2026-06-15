"""
SEARCHABLE LABEL: TOWER_PACK_275_HANDOFF_EVIDENCE_ROUTE_READINESS_BATCH_CLOSE_READINESS_PREVIEW_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_275_batch_close_contract_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_evidence_route_readiness_batch_close_readiness_v275")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_evidence_route_readiness_batch_close_readiness_preview()

    assert payload["pack"] == "275"
    assert payload["pack_number"] == 275
    assert payload["pack_name"] == "Receipt Chain Saved View Owner Review Handoff Evidence Route Readiness Batch Close Readiness Preview"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-owner-review-handoff-evidence-route-readiness-batch-close-readiness-v275.json"

    assert payload["tower_area"] == "The Tower"
    assert payload["tower_section"] == "Operational Containment"
    assert payload["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert payload["tower_sublayer"] == "Handoff Evidence / Route Readiness layer"

    assert payload["source_closed_batch"] == "266-270"
    assert payload["save_batch"] == "271-275"
    assert payload["save_after_pack"] == 275
    assert payload["next_batch"] == "276-280"
    assert payload["next_pack"] == "276"

    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["simulation_only"] is True
    assert payload["preview_only"] is True

    for pack in ["271", "272", "273", "274"]:
        assert payload["source_packs"][pack]["pack"] == pack
        assert payload["source_packs"][pack]["status"] == "ready"
        assert payload["source_packs"][pack]["readiness"] == 100
        assert payload["source_packs"][pack]["preview_only"] is True

    assert payload["safe_to_push_packs_271_to_275"] is True
    assert payload["safe_to_continue_to_pack_276"] is True
    assert payload["prepare_pack_276_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_index"]["pack"] == "276"


def test_pack_275_batch_close_summary_ready_to_push():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_evidence_route_readiness_batch_close_readiness_v275")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_evidence_route_readiness_batch_close_readiness_preview()

    summary = payload["handoff_evidence_route_batch_close_summary"]

    assert summary["source_closed_batch"] == "266-270"
    assert summary["save_batch"] == "271-275"
    assert summary["save_after_pack"] == 275
    assert summary["next_batch"] == "276-280"
    assert summary["next_pack"] == "276"
    assert summary["pack_card_count"] >= 5
    assert summary["close_check_count"] >= 17
    assert summary["save_manifest_preview_count"] >= 11
    assert summary["transition_preview_count"] >= 3
    assert summary["commit_manifest_count"] >= 11

    assert summary["all_cards_ready"] is True
    assert summary["all_cards_preview_only"] is True
    assert summary["all_cards_cached"] is True
    assert summary["all_cards_non_recursive"] is True
    assert summary["all_cards_safe_to_continue"] is True
    assert summary["all_checks_passed"] is True
    assert summary["all_checks_no_writes"] is True
    assert summary["all_transitions_preview_only"] is True
    assert summary["all_transitions_no_writes"] is True
    assert summary["all_transitions_safe"] is True
    assert summary["handoff_evidence_route_batch_ready_to_push"] is True

    assert summary["real_batch_close_write_enabled"] is False
    assert summary["real_evidence_write_enabled"] is False
    assert summary["real_evidence_export_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["real_route_change_enabled"] is False
    assert summary["real_route_activation_enabled"] is False
    assert summary["real_route_deactivation_enabled"] is False
    assert summary["real_handoff_execute_enabled"] is False
    assert summary["real_handoff_write_enabled"] is False
    assert summary["real_note_write_enabled"] is False
    assert summary["real_note_version_write_enabled"] is False
    assert summary["real_note_version_restore_enabled"] is False
    assert summary["real_note_version_apply_enabled"] is False
    assert summary["real_app_registry_write_enabled"] is False
    assert summary["real_room_registry_write_enabled"] is False
    assert summary["real_mission_account_registry_write_enabled"] is False
    assert summary["real_ob_route_change_enabled"] is False
    assert summary["real_teller_route_change_enabled"] is False
    assert summary["real_tower_route_change_enabled"] is False
    assert summary["real_clearance_write_enabled"] is False
    assert summary["real_permission_write_enabled"] is False
    assert summary["real_billing_write_enabled"] is False
    assert summary["real_subscription_write_enabled"] is False
    assert summary["real_receipt_write_enabled"] is False
    assert summary["real_archive_write_enabled"] is False
    assert summary["real_action_execution_enabled"] is False


def test_pack_275_cards_checks_manifest_and_transitions():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_evidence_route_readiness_batch_close_readiness_v275")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_evidence_route_readiness_batch_close_readiness_preview()

    cards = payload["handoff_evidence_route_batch_pack_cards"]
    checks = payload["handoff_evidence_route_batch_close_checks"]
    manifest = payload["handoff_evidence_route_save_manifest_preview"]
    transitions = payload["handoff_evidence_route_transition_previews"]

    packs = {card["pack"] for card in cards}
    assert {"271", "272", "273", "274", "275"}.issubset(packs)

    assert all(card["status"] == "ready" for card in cards)
    assert all(card["readiness"] == 100 for card in cards)
    assert all(card["preview_only"] is True for card in cards)
    assert all(card["cached"] is True for card in cards)
    assert all(card["non_recursive"] is True for card in cards)
    assert all(card["safe_to_continue"] is True for card in cards)

    assert all(check["passed"] is True for check in checks)
    assert all(check["writes_state"] is False for check in checks)

    manifest_paths = {row["path"] for row in manifest}
    expected_paths = {
        "tower/receipt_chain_saved_view_owner_review_handoff_evidence_route_readiness_index_v271.py",
        "tower/test_tower_pack_271.py",
        "tower/receipt_chain_saved_view_owner_review_handoff_evidence_route_readiness_detail_drawer_v272.py",
        "tower/test_tower_pack_272.py",
        "tower/receipt_chain_saved_view_owner_review_handoff_evidence_route_readiness_note_draft_v273.py",
        "tower/test_tower_pack_273.py",
        "tower/receipt_chain_saved_view_owner_review_handoff_evidence_route_readiness_note_version_v274.py",
        "tower/test_tower_pack_274.py",
        "tower/receipt_chain_saved_view_owner_review_handoff_evidence_route_readiness_batch_close_readiness_v275.py",
        "tower/test_tower_pack_275.py",
        "web/app.py",
    }
    assert expected_paths.issubset(manifest_paths)
    assert all(row["include_in_commit"] is True for row in manifest)

    assert transitions
    assert all(row["transition_mode"] == "preview_only" for row in transitions)
    assert all(row["writes_state"] is False for row in transitions)
    assert all(row["safe_to_continue"] is True for row in transitions)


def test_pack_275_safety_invariants_and_blocked_actions():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_evidence_route_readiness_batch_close_readiness_v275")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_evidence_route_readiness_batch_close_readiness_preview()

    safety = payload["safety_invariants"]

    assert safety["no_real_batch_close_write"] is True
    assert safety["no_real_evidence_write"] is True
    assert safety["no_real_evidence_export"] is True
    assert safety["no_raw_evidence_reveal"] is True
    assert safety["no_real_route_change"] is True
    assert safety["no_real_route_activation"] is True
    assert safety["no_real_route_deactivation"] is True
    assert safety["no_real_handoff_execute"] is True
    assert safety["no_real_handoff_write"] is True
    assert safety["no_real_note_write"] is True
    assert safety["no_real_note_version_write"] is True
    assert safety["no_real_note_version_restore"] is True
    assert safety["no_real_note_version_apply"] is True
    assert safety["no_real_app_registry_write"] is True
    assert safety["no_real_room_registry_write"] is True
    assert safety["no_real_mission_account_registry_write"] is True
    assert safety["no_real_clearance_write"] is True
    assert safety["no_real_permission_write"] is True
    assert safety["no_real_billing_write"] is True
    assert safety["no_real_subscription_write"] is True
    assert safety["no_real_receipt_write"] is True
    assert safety["no_real_archive_write"] is True
    assert safety["no_real_action_execution"] is True
    assert safety["cached_non_recursive_builder"] is True
    assert safety["ob_ui_not_built_in_tower_pack"] is True
    assert safety["teller_ui_not_built_in_tower_pack"] is True

    blocked = payload["blocked_action_matrix"]
    assert blocked
    assert all(row["allowed"] is False for row in blocked)
    assert all(row["result"] == "blocked_preview_only" for row in blocked)


def test_pack_275_public_builder_returns_defensive_copy():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_evidence_route_readiness_batch_close_readiness_v275")

    first = mod.build_receipt_chain_saved_view_owner_review_handoff_evidence_route_readiness_batch_close_readiness_preview()
    second = mod.build_receipt_chain_saved_view_owner_review_handoff_evidence_route_readiness_batch_close_readiness_preview()

    assert first == second
    assert first is not second

    first["status"] = "mutated_by_test"
    third = mod.build_receipt_chain_saved_view_owner_review_handoff_evidence_route_readiness_batch_close_readiness_preview()

    assert third["status"] == "ready"


def test_pack_275_status_bridge_and_next_prep():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_evidence_route_readiness_batch_close_readiness_v275")

    bridge = mod.build_pack_275_status_bridge()
    assert bridge["pack"] == "275"
    assert bridge["pack_number"] == 275
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["preview_only"] is True
    assert bridge["tower_section"] == "Operational Containment"
    assert bridge["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert bridge["tower_sublayer"] == "Handoff Evidence / Route Readiness layer"
    assert bridge["source_closed_batch"] == "266-270"
    assert bridge["save_batch"] == "271-275"
    assert bridge["save_after_pack"] == 275
    assert bridge["next_batch"] == "276-280"
    assert bridge["next_pack"] == "276"
    assert bridge["pack_card_count"] >= 5
    assert bridge["close_check_count"] >= 17
    assert bridge["save_manifest_preview_count"] >= 11
    assert bridge["handoff_evidence_route_batch_ready_to_push"] is True
    assert bridge["safe_to_push_packs_271_to_275"] is True
    assert bridge["safe_to_continue_to_pack_276"] is True

    prep = mod.prepare_pack_276_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_index()
    assert prep["ready"] is True
    assert prep["next_pack"] == "276"
    assert prep["mode"] == "simulated_preview_only"
    assert prep["tower_section"] == "Operational Containment"
    assert prep["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert prep["tower_sublayer"] == "Handoff Evidence / Route Readiness layer"
    assert prep["source_closed_batch"] == "266-270"
    assert prep["closed_batch"] == "271-275"
    assert prep["next_batch"] == "276-280"
    assert prep["save_after_pack"] == 280
    assert prep["safe_to_continue"] is True


def test_pack_275_endpoint_is_registered_if_app_imports():
    import web.app as web_app

    app = getattr(web_app, "app", None)
    assert app is not None

    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/receipt-chain-saved-view-owner-review-handoff-evidence-route-readiness-batch-close-readiness-v275.json" in rules

    client = app.test_client()
    response = client.get("/tower/receipt-chain-saved-view-owner-review-handoff-evidence-route-readiness-batch-close-readiness-v275.json")

    assert response.status_code in {200, 302, 401, 403}

    if response.status_code == 200:
        data = response.get_json()
        assert data["pack"] == "275"
        assert data["status"] == "ready"
        assert data["readiness"] == 100
        assert data["preview_only"] is True
        assert data["tower_section"] == "Operational Containment"
        assert data["tower_layer"] == "Receipt Chain Saved View Review Layer"
        assert data["tower_sublayer"] == "Handoff Evidence / Route Readiness layer"
        assert data["source_closed_batch"] == "266-270"
        assert data["save_batch"] == "271-275"
        assert data["next_batch"] == "276-280"
        assert data["next_pack"] == "276"
        assert data["safe_to_push_packs_271_to_275"] is True
        assert data["safe_to_continue_to_pack_276"] is True
