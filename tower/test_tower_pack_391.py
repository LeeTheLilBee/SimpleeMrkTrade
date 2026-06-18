"""
SEARCHABLE LABEL: TOWER_PACK_391_HANDOFF_POLICY_ROUTE_ENFORCEMENT_OWNER_ACCEPTANCE_FINAL_CLOSEOUT_ARCHIVE_VERIFICATION_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_391_contract_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_archive_verification_index_v391")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_archive_verification_index_preview()

    assert payload["pack"] == "391"
    assert payload["pack_number"] == 391
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-owner-acceptance-final-closeout-archive-verification-index-v391.json"
    assert payload["tower_sublayer"] == "Handoff Policy Route Enforcement Owner Acceptance Final Closeout Archive Verification layer"
    assert payload["source_pack"] == "390"
    assert payload["source_closed_batch"] == "386-390"
    assert payload["save_batch"] == "391-395"
    assert payload["save_after_pack"] == 395
    assert payload["next_pack"] == "392"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["simulation_only"] is True
    assert payload["preview_only"] is True
    assert payload["archive_verification_preview_only"] is True
    assert payload["archive_preview_only"] is True
    assert payload["final_closeout_archive_preview_only"] is True
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True
    assert payload["safe_to_continue_to_pack_392"] is True
    assert payload["prepare_pack_392_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_archive_verification_detail_drawer"]["pack"] == "392"


def test_pack_391_summary_safety_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_archive_verification_index_v391")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_archive_verification_index_preview()
    summary = payload["owner_acceptance_final_closeout_archive_verification_index_summary"]

    assert summary["row_count"] >= 120
    assert summary["action_count"] >= 15
    assert summary["checkpoint_count"] >= 18
    assert summary["enabled_action_count"] >= 15
    assert summary["blocked_action_count"] >= 15
    assert summary["redacted_row_count"] >= 30

    assert summary["all_rows_preview_only"] is True
    assert summary["all_rows_pointer_only"] is True
    assert summary["all_rows_archive_verification_pointer_only"] is True
    assert summary["all_rows_no_writes"] is True
    assert summary["all_rows_non_executable"] is True
    assert summary["all_rows_non_verifiable"] is True
    assert summary["all_rows_non_passable"] is True
    assert summary["all_rows_non_failable"] is True
    assert summary["all_rows_non_archivable"] is True
    assert summary["all_rows_non_restorable"] is True
    assert summary["all_rows_non_purgable"] is True
    assert summary["all_rows_no_raw_evidence"] is True
    assert summary["all_actions_safe"] is True
    assert summary["all_actions_no_writes"] is True
    assert summary["all_checkpoints_passed"] is True
    assert summary["all_checkpoints_no_writes"] is True
    assert summary["owner_acceptance_final_closeout_archive_verification_index_ready"] is True

    assert summary["real_archive_verification_execute_enabled"] is False
    assert summary["real_archive_verification_pass_enabled"] is False
    assert summary["real_archive_verification_fail_enabled"] is False
    assert summary["real_archive_write_enabled"] is False
    assert summary["real_archive_restore_enabled"] is False
    assert summary["real_archive_delete_enabled"] is False
    assert summary["real_archive_purge_enabled"] is False
    assert summary["real_archive_export_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["real_action_execution_enabled"] is False


def test_pack_391_payload_shapes_endpoint_and_defensive_copy():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_archive_verification_index_v391")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_archive_verification_index_preview()

    rows = payload["owner_acceptance_final_closeout_archive_verification_index_rows"]
    actions = payload["owner_acceptance_final_closeout_archive_verification_index_actions"]
    checkpoints = payload["owner_acceptance_final_closeout_archive_verification_index_checkpoints"]

    assert rows
    assert actions
    assert checkpoints

    assert all(row["preview_only"] is True for row in rows)
    assert all(row["archive_verification_pointer_only"] is True for row in rows)
    assert all(row["writes_state"] is False for row in rows)
    assert all(row["raw_evidence_visible"] is False for row in rows)
    assert all(row["verifiable"] is False for row in rows)
    assert all(row["passable"] is False for row in rows)
    assert all(row["failable"] is False for row in rows)
    assert all(row["archivable"] is False for row in rows)

    preview_actions = [row for row in actions if row["result"] == "preview_allowed"]
    blocked_actions = [row for row in actions if row["result"] == "blocked_preview_only"]
    assert preview_actions
    assert blocked_actions
    assert all(row["enabled"] is True for row in preview_actions)
    assert all(row["enabled"] is False for row in blocked_actions)
    assert all(row["writes_state"] is False for row in actions)

    assert all(row["passed"] is True for row in checkpoints)
    assert all(row["writes_state"] is False for row in checkpoints)

    bridge = mod.build_pack_391_status_bridge()
    assert bridge["pack"] == "391"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["owner_acceptance_final_closeout_archive_verification_index_ready"] is True
    assert bridge["safe_to_continue_to_pack_392"] is True

    prep = mod.prepare_pack_392_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_archive_verification_detail_drawer()
    assert prep["ready"] is True
    assert prep["next_pack"] == "392"
    assert prep["source_pack"] == "391"

    import web.app as web_app
    app = getattr(web_app, "app", None)
    assert app is not None
    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-owner-acceptance-final-closeout-archive-verification-index-v391.json" in rules

    response = app.test_client().get("/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-owner-acceptance-final-closeout-archive-verification-index-v391.json")
    assert response.status_code in {200, 302, 401, 403}
    if response.status_code == 200:
        data = response.get_json()
        assert data["pack"] == "391"
        assert data["status"] == "ready"
        assert data["readiness"] == 100
        assert data["archive_verification_preview_only"] is True
        assert data["safe_to_continue_to_pack_392"] is True

    first = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_archive_verification_index_preview()
    second = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_archive_verification_index_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_archive_verification_index_preview()
    assert third["status"] == "ready"
