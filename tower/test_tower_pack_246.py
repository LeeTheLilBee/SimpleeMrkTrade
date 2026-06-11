"""
SEARCHABLE LABEL: TOWER_PACK_246_ONE_CELL_REBUILD_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_246_payload_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_decision_trace_v246")
    payload = mod.build_receipt_chain_saved_view_owner_review_governance_decision_trace_preview()

    assert payload["pack"] == "246"
    assert payload["pack_number"] == 246
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-owner-review-governance-decision-trace-v246.json"
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
    assert payload["safe_to_continue_to_pack_247"] is True

    assert payload["prepare_pack_247_receipt_chain_saved_view_owner_review_governance_decision_detail_evidence_drawer"]["next_pack"] == "247"


def test_pack_246_summary_safety_bridge_and_route():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_decision_trace_v246")
    payload = mod.build_receipt_chain_saved_view_owner_review_governance_decision_trace_preview()
    summary = payload["governance_decision_trace_summary"]

    assert summary["decision_trace_card_count"] >= 6
    assert summary["decision_trace_ready"] is True
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

    bridge = mod.build_pack_246_status_bridge()
    assert bridge["pack"] == "246"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["safe_to_continue_to_pack_247"] is True

    prep = mod.prepare_pack_247_receipt_chain_saved_view_owner_review_governance_decision_detail_evidence_drawer()
    assert prep["ready"] is True
    assert prep["next_pack"] == "247"

    import web.app as web_app
    app = getattr(web_app, "app", None)
    assert app is not None
    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/receipt-chain-saved-view-owner-review-governance-decision-trace-v246.json" in rules
