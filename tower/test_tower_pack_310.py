"""
SEARCHABLE LABEL: TOWER_PACK_310_HANDOFF_POLICY_ROUTE_ENFORCEMENT_OWNER_ACCEPTANCE_BATCH_CLOSE_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_310_contract_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_batch_close_readiness_v310")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_batch_close_readiness_preview()

    assert payload["pack"] == "310"
    assert payload["pack_number"] == 310
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-owner-acceptance-batch-close-readiness-v310.json"

    assert payload["tower_area"] == "The Tower"
    assert payload["tower_section"] == "Operational Containment"
    assert payload["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert payload["tower_sublayer"] == "Handoff Policy Route Enforcement Owner Acceptance layer"

    assert payload["source_closed_batch"] == "301-305"
    assert payload["save_batch"] == "306-310"
    assert payload["save_after_pack"] == 310
    assert payload["next_batch"] == "311-315"
    assert payload["next_pack"] == "311"

    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["simulation_only"] is True
    assert payload["preview_only"] is True

    assert payload["safe_to_push_packs_306_to_310"] is True
    assert payload["safe_to_continue_to_pack_311"] is True
    assert payload["prepare_pack_311_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_handoff_index"]["pack"] == "311"


def test_pack_310_source_packs_and_summary_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_batch_close_readiness_v310")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_batch_close_readiness_preview()

    for pack in ["306", "307", "308", "309"]:
        assert payload["source_packs"][pack]["pack"] == pack
        assert payload["source_packs"][pack]["status"] == "ready"
        assert payload["source_packs"][pack]["readiness"] == 100
        assert payload["source_packs"][pack]["preview_only"] is True

    summary = payload["owner_acceptance_batch_close_summary"]

    assert summary["source_closed_batch"] == "301-305"
    assert summary["save_batch"] == "306-310"
    assert summary["save_after_pack"] == 310
    assert summary["next_batch"] == "311-315"
    assert summary["next_pack"] == "311"

    assert summary["pack_card_count"] >= 5
    assert summary["close_check_count"] >= 14
    assert summary["save_manifest_preview_count"] >= 11
    assert summary["transition_count"] >= 6
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
    assert summary["owner_acceptance_batch_ready_to_push"] is True

    assert summary["real_owner_acceptance_execute_enabled"] is False
    assert summary["real_owner_acceptance_write_enabled"] is False
    assert summary["real_owner_acceptance_apply_enabled"] is False
    assert summary["real_owner_acceptance_reject_enabled"] is False
    assert summary["real_owner_acceptance_sign_enabled"] is False
    assert summary["real_evidence_transfer_enabled"] is False
    assert summary["real_evidence_write_enabled"] is False
    assert summary["real_evidence_reveal_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["real_note_write_enabled"] is False
    assert summary["real_note_version_write_enabled"] is False
    assert summary["real_policy_write_enabled"] is False
    assert summary["real_route_change_enabled"] is False
    assert summary["real_registry_write_enabled"] is False
    assert summary["real_clearance_write_enabled"] is False
    assert summary["real_billing_write_enabled"] is False
    assert summary["real_receipt_write_enabled"] is False
    assert summary["real_action_execution_enabled"] is False


def test_pack_310_manifest_endpoint_bridge_and_copy():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_batch_close_readiness_v310")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_batch_close_readiness_preview()

    manifest = payload["owner_acceptance_save_manifest_preview"]
    expected = {
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_index_v306.py",
        "tower/test_tower_pack_306.py",
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_detail_drawer_v307.py",
        "tower/test_tower_pack_307.py",
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_note_draft_v308.py",
        "tower/test_tower_pack_308.py",
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_note_version_v309.py",
        "tower/test_tower_pack_309.py",
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_batch_close_readiness_v310.py",
        "tower/test_tower_pack_310.py",
        "web/app.py",
    }
    assert expected.issubset({row["path"] for row in manifest})
    assert all(row["include_in_commit"] is True for row in manifest)

    bridge = mod.build_pack_310_status_bridge()
    assert bridge["pack"] == "310"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["owner_acceptance_batch_ready_to_push"] is True
    assert bridge["safe_to_push_packs_306_to_310"] is True
    assert bridge["safe_to_continue_to_pack_311"] is True

    prep = mod.prepare_pack_311_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_handoff_index()
    assert prep["ready"] is True
    assert prep["next_pack"] == "311"
    assert prep["closed_batch"] == "306-310"

    import web.app as web_app
    app = getattr(web_app, "app", None)
    assert app is not None
    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-owner-acceptance-batch-close-readiness-v310.json" in rules

    response = app.test_client().get("/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-owner-acceptance-batch-close-readiness-v310.json")
    assert response.status_code in {200, 302, 401, 403}
    if response.status_code == 200:
        data = response.get_json()
        assert data["pack"] == "310"
        assert data["status"] == "ready"
        assert data["safe_to_push_packs_306_to_310"] is True

    first = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_batch_close_readiness_preview()
    second = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_batch_close_readiness_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_batch_close_readiness_preview()
    assert third["status"] == "ready"
