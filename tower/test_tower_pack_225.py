"""
SEARCHABLE LABEL: TOWER_PACK_225_REBUILT_OWNER_REVIEW_BATCH_CLOSE_READINESS_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_225_contract_and_summary_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_batch_close_readiness_v225")
    payload = mod.build_receipt_chain_saved_view_owner_review_batch_close_readiness_preview()

    assert payload["pack"] == "225"
    assert payload["pack_number"] == 225
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-owner-review-batch-close-readiness-v225.json"
    assert payload["tower_area"] == "The Tower"
    assert payload["tower_section"] == "Operational Containment"
    assert payload["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert payload["save_batch"] == "221-225"
    assert payload["save_after_pack"] == 225
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["simulation_only"] is True
    assert payload["preview_only"] is True
    assert payload["source_pack"] == "224"
    assert payload["safe_to_push_packs_221_to_225"] is True
    assert payload["safe_to_continue_to_pack_226"] is True

    summary = payload["owner_review_batch_close_summary"]
    assert summary["pack_card_count"] >= 5
    assert summary["batch_close_check_count"] >= 9
    assert summary["save_manifest_preview_count"] >= 5
    assert summary["commit_manifest_count"] >= 5
    assert summary["batch_ready_to_save"] is True
    assert summary["real_batch_close_write_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["real_action_execution_enabled"] is False


def test_pack_225_parts_and_bridge_safe():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_batch_close_readiness_v225")
    payload = mod.build_receipt_chain_saved_view_owner_review_batch_close_readiness_preview()
    bridge = mod.build_pack_225_status_bridge()
    prep = mod.prepare_pack_226_receipt_chain_saved_view_owner_review_followup_queue()

    assert all(row["status"] == "ready" for row in payload["owner_review_batch_pack_cards"])
    assert all(row["preview_only"] is True for row in payload["owner_review_batch_pack_cards"])
    assert all(row["passed"] is True for row in payload["owner_review_batch_close_checks"])
    assert all(row["writes_state"] is False for row in payload["owner_review_batch_close_checks"])
    assert all(row["allowed"] is False for row in payload["blocked_action_matrix"])

    assert bridge["pack"] == "225"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["batch_ready_to_save"] is True
    assert bridge["safe_to_continue_to_pack_226"] is True

    assert prep["ready"] is True
    assert prep["next_pack"] == "226"


def test_pack_225_endpoint_registered_if_app_imports():
    import web.app as web_app

    app = getattr(web_app, "app", None)
    assert app is not None

    endpoint = "/tower/receipt-chain-saved-view-owner-review-batch-close-readiness-v225.json"
    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert endpoint in rules

    response = app.test_client().get(endpoint)
    assert response.status_code in {200, 302, 401, 403}

    if response.status_code == 200:
        data = response.get_json()
        assert data["pack"] == "225"
        assert data["status"] == "ready"
        assert data["readiness"] == 100
        assert data["preview_only"] is True
