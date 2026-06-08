import importlib


def test_pack_208_bridge_ready():
    mod = importlib.import_module("tower.receipt_chain_incident_lane_v208")
    bridge = mod.build_receipt_chain_incident_lane_v208_status_bridge(force_refresh=True)

    assert bridge["pack_number"] == 208
    assert bridge["status"] == "ready"
    assert bridge["readiness_score"] == 100
    assert bridge["incident_timeline_event_count"] == 6
    assert bridge["incident_runbook_count"] == 5
    assert bridge["safe_to_continue_to_pack_209"] is True

    for key, value in bridge.items():
        if key.startswith("real_") and key.endswith("_count"):
            assert value == 0

    assert bridge.get("raw_evidence_revealed_count", 0) == 0
