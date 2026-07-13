"""
SEARCHABLE LABEL: TOWER_TEST_PACK_2388
"""

from tower.tower_ir_cert_p2388 import (
    build_ir_cert_p2388_preview,
    build_pack_2388_status_bridge,
    prepare_pack_2389_ir_cert_p2389,
)


def test_pack_2388_ready():
    payload = build_ir_cert_p2388_preview()

    assert payload["pack"] == "2388"
    assert payload["pack_number"] == 2388
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/ir-cert-v2388.json"
    assert payload["source_pack"] == "2387"
    assert payload["next_pack"] == "2389"
    assert payload["current_packs"] == "2372-2422"
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["safe_to_continue_to_pack_2389"] is True


def test_pack_2388_safety():
    payload = build_ir_cert_p2388_preview()
    summary = payload["tower_pack_2388_summary"]

    assert summary["row_count"] >= 36
    assert summary["check_count"] >= 15
    assert summary["all_rows_no_writes"] is True
    assert summary["all_checks_no_writes"] is True
    assert summary["tower_pack_2388_ready"] is True
    assert summary[
        "real_incident_response_execution_enabled"
    ] is False
    assert summary[
        "real_owner_decision_apply_enabled"
    ] is False
    assert summary["real_account_mutation_enabled"] is False
    assert summary["real_access_mutation_enabled"] is False
    assert summary["real_route_mutation_enabled"] is False
    assert summary["real_session_mutation_enabled"] is False
    assert summary["real_clouds_write_enabled"] is False
    assert summary["real_vault_write_enabled"] is False


def test_pack_2388_handoff_and_copy_safety():
    bridge_payload = build_pack_2388_status_bridge()

    assert bridge_payload["pack"] == "2388"
    assert bridge_payload["safe_to_continue_to_pack_2389"] is True

    handoff = prepare_pack_2389_ir_cert_p2389()

    assert handoff["ready"] is True
    assert handoff["source_pack"] == "2388"
    assert handoff["next_pack"] == "2389"
    assert handoff["writes_state"] is False

    first = build_ir_cert_p2388_preview()
    second = build_ir_cert_p2388_preview()

    assert first == second
    assert first is not second

    first["status"] = "mutated"

    assert build_ir_cert_p2388_preview()["status"] == "ready"
