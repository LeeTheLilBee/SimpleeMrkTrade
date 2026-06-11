"""
SEARCHABLE LABEL: TOWER_PACK_224_REBUILT_OWNER_REVIEW_NOTE_VERSION_PREVIEW_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_224_contract_and_summary_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_note_version_v224")
    payload = mod.build_receipt_chain_saved_view_owner_review_note_version_preview()

    assert payload["pack"] == "224"
    assert payload["pack_number"] == 224
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-owner-review-note-version-v224.json"
    assert payload["tower_area"] == "The Tower"
    assert payload["tower_section"] == "Operational Containment"
    assert payload["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert payload["save_batch"] == "221-225"
    assert payload["save_after_pack"] == 225
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["simulation_only"] is True
    assert payload["preview_only"] is True
    assert payload["source_pack"] == "223"
    assert payload["safe_to_continue_to_pack_225"] is True

    summary = payload["owner_note_version_summary"]
    assert summary["version_card_count"] >= 12
    assert summary["compare_row_count"] >= 48
    assert summary["version_action_count"] >= 72
    assert summary["note_version_preview_ready"] is True
    assert summary["real_owner_note_version_write_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["real_action_execution_enabled"] is False


def test_pack_224_parts_and_bridge_safe():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_note_version_v224")
    payload = mod.build_receipt_chain_saved_view_owner_review_note_version_preview()
    bridge = mod.build_pack_224_status_bridge()
    prep = mod.prepare_pack_225_saved_view_owner_review_batch_close_readiness()

    assert all(row["version_mode"] == "preview_only" for row in payload["owner_note_version_cards"])
    assert all(row["writes_state"] is False for row in payload["owner_note_version_cards"])
    assert all(row["writes_state"] is False for row in payload["owner_note_version_compare_rows"])
    assert all(row["result"] in {"preview_allowed", "blocked_preview_only"} for row in payload["owner_note_version_actions"])
    assert all(row["allowed"] is False for row in payload["blocked_action_matrix"])

    assert bridge["pack"] == "224"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["safe_to_continue_to_pack_225"] is True

    assert prep["ready"] is True
    assert prep["next_pack"] == "225"


def test_pack_224_endpoint_registered_if_app_imports():
    import web.app as web_app

    app = getattr(web_app, "app", None)
    assert app is not None

    endpoint = "/tower/receipt-chain-saved-view-owner-review-note-version-v224.json"
    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert endpoint in rules

    response = app.test_client().get(endpoint)
    assert response.status_code in {200, 302, 401, 403}

    if response.status_code == 200:
        data = response.get_json()
        assert data["pack"] == "224"
        assert data["status"] == "ready"
        assert data["readiness"] == 100
        assert data["preview_only"] is True
