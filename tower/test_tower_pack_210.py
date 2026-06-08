import importlib


def test_pack_210_bridge_ready():
    mod = importlib.import_module("tower.receipt_chain_post_batch_checkpoint_v210")
    bridge = mod.build_receipt_chain_post_batch_checkpoint_v210_status_bridge(force_refresh=True)

    assert bridge["pack_number"] == 210
    assert bridge["status"] == "ready"
    assert bridge["readiness_score"] == 100
    assert bridge["source_pack_count"] == 4
    assert bridge["next_batch_handoff_count"] == 5
    assert bridge["safe_to_continue_to_pack_211"] is True

    for key, value in bridge.items():
        if key.startswith("real_") and key.endswith("_count"):
            assert value == 0

    assert bridge.get("raw_evidence_revealed_count", 0) == 0
