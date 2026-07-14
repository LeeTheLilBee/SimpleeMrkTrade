from tower.tower_ir_cert_p2410 import (
    build_assurance_readiness,
    build_ir_cert_p2410_preview,
)


def test_pack_2410_assurance_readiness():
    readiness = build_assurance_readiness()

    assert readiness["ready"] is True
    assert readiness["recommendation"] == (
        "GO_TOWER_OB_PROTECTED_ASSURANCE_CHECKPOINT_READY"
    )
    assert all(readiness["checks"].values())


def test_pack_2410_next_handoff():
    payload = build_ir_cert_p2410_preview()

    assert payload["protected_assurance_ready"] is True
    assert payload["safe_to_continue_to_pack_2411"] is True
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
