"""
SEARCHABLE LABEL: TOWER_PACK_382_OWNER_ACCEPTANCE_FINAL_CLOSEOUT_SEAL_VERIFICATION_DETAIL_DRAWER_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_382_contract_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_seal_verification_detail_drawer_v382")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_seal_verification_detail_drawer_preview()

    assert payload["pack"] == "382"
    assert payload["pack_number"] == 382
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-owner-acceptance-final-closeout-seal-verification-detail-drawer-v382.json"
    assert payload["tower_sublayer"] == "Handoff Policy Route Enforcement Owner Acceptance Final Closeout Seal Verification layer"
    assert payload["source_pack"] == "381"
    assert payload["source_closed_batch"] == "366-370"
    assert payload["local_build_batch"] == "381-385"
    assert payload["stacked_save_target"] == "366-385"
    assert payload["next_pack"] == "383"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["simulation_only"] is True
    assert payload["preview_only"] is True
    assert payload["owner_acceptance_final_closeout_seal_verification_preview_only"] is True
    assert payload["final_closeout_preview_only"] is True
    assert payload["closeout_preview_only"] is True
    assert payload["release_verification_preview_only"] is True
    assert payload["release_preview_only"] is True
    assert payload["seal_preview_only"] is True
    assert payload["receipt_preview_only"] is True
    assert payload["retrieval_preview_only"] is True
    assert payload["archive_preview_only"] is True
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True
    assert payload["safe_to_continue_to_pack_383"] is True
    assert payload["prepare_pack_383_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_seal_verification_note_draft"]["pack"] == "383"


def test_pack_382_summary_safety_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_seal_verification_detail_drawer_v382")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_seal_verification_detail_drawer_preview()
    summary = payload["owner_acceptance_final_closeout_seal_verification_detail_drawer_summary"]

    assert summary["source_ready"] is True
    assert summary["row_count"] >= 120
    assert summary["action_count"] >= 15
    assert summary["check_count"] >= 20
    assert summary["enabled_action_count"] >= 15
    assert summary["blocked_action_count"] >= 15
    assert summary["redacted_row_count"] >= 30

    assert summary["all_rows_preview_only"] is True
    assert summary["all_rows_layer_preview_only"] is True
    assert summary["all_rows_pointer_only"] is True
    assert summary["all_rows_no_writes"] is True
    assert summary["all_rows_no_raw_evidence"] is True
    assert summary["all_rows_non_executable"] is True
    assert summary["all_rows_real_actions_disabled"] is True
    assert summary["all_actions_safe"] is True
    assert summary["all_actions_no_writes"] is True
    assert summary["all_checks_passed"] is True
    assert summary["all_checks_no_writes"] is True
    assert summary["owner_acceptance_final_closeout_seal_verification_detail_drawer_ready"] is True

    assert summary["real_owner_acceptance_final_closeout_enabled"] is False
    assert summary["real_final_closeout_verification_enabled"] is False
    assert summary["real_final_closeout_seal_enabled"] is False
    assert summary["real_release_enabled"] is False
    assert summary["real_publish_enabled"] is False
    assert summary["real_sign_enabled"] is False
    assert summary["real_seal_enabled"] is False
    assert summary["real_export_enabled"] is False
    assert summary["real_delete_enabled"] is False
    assert summary["raw_evidence_visible"] is False


def test_pack_382_payload_shapes_endpoint_and_defensive_copy():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_seal_verification_detail_drawer_v382")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_seal_verification_detail_drawer_preview()

    rows = payload["owner_acceptance_final_closeout_seal_verification_detail_drawer_rows"]
    actions = payload["owner_acceptance_final_closeout_seal_verification_detail_drawer_actions"]
    checks = payload["owner_acceptance_final_closeout_seal_verification_detail_drawer_checks"]

    assert rows
    assert actions
    assert checks

    assert all(row["preview_only"] is True for row in rows)
    assert all(row["owner_acceptance_final_closeout_seal_verification_preview_only"] is True for row in rows)
    assert all(row["pointer_only"] is True for row in rows)
    assert all(row["writes_state"] is False for row in rows)
    assert all(row["raw_evidence_visible"] is False for row in rows)
    assert all(row["executable"] is False for row in rows)
    assert all(row["real_action_enabled"] is False for row in rows)

    preview_actions = [row for row in actions if row["result"] == "preview_allowed"]
    blocked_actions = [row for row in actions if row["result"] == "blocked_preview_only"]
    assert preview_actions
    assert blocked_actions
    assert all(row["enabled"] is True for row in preview_actions)
    assert all(row["enabled"] is False for row in blocked_actions)
    assert all(row["writes_state"] is False for row in actions)

    assert all(row["passed"] is True for row in checks)
    assert all(row["writes_state"] is False for row in checks)

    bridge = mod.build_pack_382_status_bridge()
    assert bridge["pack"] == "382"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["owner_acceptance_final_closeout_seal_verification_detail_drawer_ready"] is True
    assert bridge["safe_to_continue_to_pack_383"] is True

    prep = mod.prepare_pack_383_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_seal_verification_note_draft()
    assert prep["ready"] is True
    assert prep["next_pack"] == "383"
    assert prep["source_pack"] == "382"

    import web.app as web_app
    app = getattr(web_app, "app", None)
    assert app is not None
    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-owner-acceptance-final-closeout-seal-verification-detail-drawer-v382.json" in rules

    response = app.test_client().get("/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-owner-acceptance-final-closeout-seal-verification-detail-drawer-v382.json")
    assert response.status_code in {200, 302, 401, 403}
    if response.status_code == 200:
        data = response.get_json()
        assert data["pack"] == "382"
        assert data["status"] == "ready"
        assert data["readiness"] == 100
        assert data["preview_only"] is True
        assert data["owner_acceptance_final_closeout_seal_verification_preview_only"] is True
        assert data["safe_to_continue_to_pack_383"] is True

    first = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_seal_verification_detail_drawer_preview()
    second = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_seal_verification_detail_drawer_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_seal_verification_detail_drawer_preview()
    assert third["status"] == "ready"
