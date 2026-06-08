import importlib


def test_pack_211_bridge_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_checkpoint_lookup_v211")
    bridge = mod.build_receipt_chain_saved_checkpoint_lookup_v211_status_bridge(force_refresh=True)

    assert bridge["pack_number"] == 211
    assert bridge["status"] == "ready"
    assert bridge["readiness_score"] == 100
    assert bridge["checkpoint_registry_count"] == 5
    assert bridge["checkpoint_lookup_card_count"] == 6
    assert bridge["safe_to_continue_to_pack_212"] is True

    for key, value in bridge.items():
        if key.startswith("real_") and key.endswith("_count"):
            assert value == 0

    assert bridge.get("raw_evidence_revealed_count", 0) == 0
