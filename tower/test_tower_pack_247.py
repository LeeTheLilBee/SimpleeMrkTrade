"""
SEARCHABLE LABEL: TOWER_PACK_247_ONE_CELL_REBUILD_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_247_payload_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_decision_detail_evidence_drawer_v247")
    payload = mod.build_receipt_chain_saved_view_owner_review_governance_decision_detail_evidence_drawer_preview()

    assert payload["pack"] == "247"
    assert payload["pack_number"] == 247
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-owner-review-governance-decision-detail-evidence-drawer-v247.json"
    assert payload["tower_area"] == "The Tower"
    assert payload["tower_section"] == "Operational Containment"
    assert payload["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert payload["tower_sublayer"] == "Governance Index Preview layer"
    assert payload["save_batch"] == "246-250"
    assert payload["save_after_pack"] == 250
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["simulation_only"] is True
    assert payload["preview_only"] is True
    assert payload["safe_to_continue_to_pack_248"] is True

    assert payload["prepare_pack_248_receipt_chain_saved_view_owner_review_governance_decision_note_draft"]["next_pack"] == "248"


def test_pack_247_summary_safety_bridge_and_route():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_decision_detail_evidence_drawer_v247")
    payload = mod.build_receipt_chain_saved_view_owner_review_governance_decision_detail_evidence_drawer_preview()
    summary = payload["governance_decision_detail_summary"]

    assert summary["detail_drawer_count"] >= 6
    assert summary["decision_detail_ready"] is True
    assert summary["all_preview_only"] is True
    assert summary["all_no_writes"] is True
    assert summary["all_no_raw_evidence"] is True
    assert summary["real_governance_decision_write_enabled"] is False
    assert summary["real_policy_change_enabled"] is False
    assert summary["real_owner_review_execution_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["real_action_execution_enabled"] is False

    safety = payload["safety_invariants"]
    assert safety["no_real_governance_decision_write"] is True
    assert safety["no_raw_evidence_reveal"] is True
    assert safety["cached_non_recursive_builder"] is True

    bridge = mod.build_pack_247_status_bridge()
    assert bridge["pack"] == "247"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["safe_to_continue_to_pack_248"] is True

    prep = mod.prepare_pack_248_receipt_chain_saved_view_owner_review_governance_decision_note_draft()
    assert prep["ready"] is True
    assert prep["next_pack"] == "248"

    import web.app as web_app
    app = getattr(web_app, "app", None)
    assert app is not None
    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/receipt-chain-saved-view-owner-review-governance-decision-detail-evidence-drawer-v247.json" in rules
