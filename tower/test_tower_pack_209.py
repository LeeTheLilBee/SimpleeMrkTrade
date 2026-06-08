import importlib


def test_pack_209_bridge_ready():
    mod = importlib.import_module("tower.receipt_chain_archive_handoff_v209")
    bridge = mod.build_receipt_chain_archive_handoff_v209_status_bridge(force_refresh=True)

    assert bridge["pack_number"] == 209
    assert bridge["status"] == "ready"
    assert bridge["readiness_score"] == 100
    assert bridge["archive_section_count"] == 6
    assert bridge["archive_packet_count"] == 3
    assert bridge["safe_to_continue_to_pack_210"] is True

    for key, value in bridge.items():
        if key.startswith("real_") and key.endswith("_count"):
            assert value == 0

    assert bridge.get("raw_evidence_revealed_count", 0) == 0
