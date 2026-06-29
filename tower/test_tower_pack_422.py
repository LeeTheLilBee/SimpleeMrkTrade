"""
SEARCHABLE LABEL: TOWER_GIANT_PUSH_1_PACK_422_SHARED_CONNECTIVE_TISSUE_REGISTRY_CONTRACT_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_422_contract_ready():
    mod = importlib.import_module("tower.tower_shared_connective_tissue_registry_contract_v422")
    payload = mod.build_shared_connective_tissue_registry_contract_preview()

    assert payload["pack"] == "422"
    assert payload["pack_number"] == 422
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/shared-connective-tissue-registry-contract-v422.json"
    assert payload["tower_layer"] == "Giant Push 1"
    assert payload["tower_sublayer"] == "Shared Connective Tissue layer"
    assert payload["source_pack"] == "421"
    assert payload["source_closed_batch"] == "391-395"
    assert payload["giant_push"] == "396-450"
    assert payload["next_batch"] == "451-500"
    assert payload["next_pack"] == "423"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["simulation_only"] is True
    assert payload["preview_only"] is True
    assert payload["shared_connective_tissue_preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["socket_only"] is True
    assert payload["placeholder_only"] is True
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True
    assert payload["safe_to_continue_to_pack_423"] is True
    assert payload["prepare_pack_423_shared_connective_tissue_snapshot_contract"]["pack"] == "423"


def test_pack_422_summary_safety_ready():
    mod = importlib.import_module("tower.tower_shared_connective_tissue_registry_contract_v422")
    payload = mod.build_shared_connective_tissue_registry_contract_preview()
    summary = payload["shared_connective_tissue_registry_contract_summary"]

    assert summary["source_ready"] is True
    assert summary["row_count"] >= 5
    assert summary["check_count"] >= 15
    assert summary["action_count"] >= 7
    assert summary["foundation_standard_count"] >= 30
    assert summary["capital_safety_standard_count"] >= 9
    assert summary["all_rows_preview_only"] is True
    assert summary["all_rows_contract_only"] is True
    assert summary["all_rows_no_writes"] is True
    assert summary["all_rows_no_live_money"] is True
    assert summary["all_rows_no_broker_api"] is True
    assert summary["all_rows_no_uploads"] is True
    assert summary["all_rows_no_raw_evidence"] is True
    assert summary["all_checks_passed"] is True
    assert summary["all_checks_no_writes"] is True
    assert summary["all_actions_safe"] is True
    assert summary["all_actions_no_writes"] is True
    assert summary["shared_connective_tissue_registry_contract_ready"] is True
    assert summary["real_live_money_permission_enabled"] is False
    assert summary["real_broker_api_enabled"] is False
    assert summary["real_upload_enabled"] is False
    assert summary["real_ocr_enabled"] is False
    assert summary["real_external_share_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["real_action_execution_enabled"] is False


def test_pack_422_payload_shapes_endpoint_bridge_and_copy():
    mod = importlib.import_module("tower.tower_shared_connective_tissue_registry_contract_v422")
    payload = mod.build_shared_connective_tissue_registry_contract_preview()

    rows = payload["shared_connective_tissue_registry_contract_rows"]
    checks = payload["shared_connective_tissue_registry_contract_checks"]
    actions = payload["shared_connective_tissue_registry_contract_actions"]

    assert rows
    assert checks
    assert actions

    assert all(row["preview_only"] is True for row in rows)
    assert all(row["contract_only"] is True for row in rows)
    assert all(row["writes_state"] is False for row in rows)
    assert all(row["live_money_enabled"] is False for row in rows)
    assert all(row["broker_api_enabled"] is False for row in rows)
    assert all(row["upload_enabled"] is False for row in rows)
    assert all(row["raw_evidence_visible"] is False for row in rows)

    assert all(check["passed"] is True for check in checks)
    assert all(check["writes_state"] is False for check in checks)

    preview_actions = [row for row in actions if row["result"] == "preview_allowed"]
    blocked_actions = [row for row in actions if row["result"] == "blocked_preview_only"]
    assert preview_actions
    assert blocked_actions
    assert all(row["enabled"] is True for row in preview_actions)
    assert all(row["enabled"] is False for row in blocked_actions)
    assert all(row["writes_state"] is False for row in actions)

    bridge = mod.build_pack_422_status_bridge()
    assert bridge["pack"] == "422"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["shared_connective_tissue_registry_contract_ready"] is True
    assert bridge["safe_to_continue_to_pack_423"] is True

    prep = mod.prepare_pack_423_shared_connective_tissue_snapshot_contract()
    assert prep["ready"] is True
    assert prep["next_pack"] == "423"
    assert prep["source_pack"] == "422"

    import web.app as web_app
    app = getattr(web_app, "app", None)
    assert app is not None
    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/shared-connective-tissue-registry-contract-v422.json" in rules

    response = app.test_client().get("/tower/shared-connective-tissue-registry-contract-v422.json")
    assert response.status_code in {200, 302, 401, 403}
    if response.status_code == 200:
        data = response.get_json()
        assert data["pack"] == "422"
        assert data["status"] == "ready"
        assert data["readiness"] == 100
        assert data["preview_only"] is True
        assert data["safe_to_continue_to_pack_423"] is True

    first = mod.build_shared_connective_tissue_registry_contract_preview()
    second = mod.build_shared_connective_tissue_registry_contract_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = mod.build_shared_connective_tissue_registry_contract_preview()
    assert third["status"] == "ready"
