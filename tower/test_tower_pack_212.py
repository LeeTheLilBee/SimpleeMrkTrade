import importlib


def test_pack_212_bridge_ready():
    mod = importlib.import_module("tower.receipt_chain_checkpoint_filter_search_v212")
    bridge = mod.build_receipt_chain_checkpoint_filter_search_v212_status_bridge(force_refresh=True)

    assert bridge["pack_number"] == 212
    assert bridge["status"] == "ready"
    assert bridge["readiness_score"] == 100
    assert bridge["query_preset_count"] == 6
    assert bridge["filter_lane_count"] == 7
    assert bridge["safe_to_continue_to_pack_213"] is True

    for key, value in bridge.items():
        if key.startswith("real_") and key.endswith("_count"):
            assert value == 0

    assert bridge.get("raw_evidence_revealed_count", 0) == 0
