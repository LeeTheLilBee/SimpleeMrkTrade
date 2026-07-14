from tower.tower_ir_cert_p2400 import (
    build_enforcement_readiness,
    build_ir_cert_p2400_preview,
)


def test_pack_2400_enforcement_readiness():
    readiness = build_enforcement_readiness()

    assert readiness["ready"] is True
    assert readiness["recommendation"] == (
        "GO_TOWER_OB_PROTECTED_ENFORCEMENT_READY"
    )
    assert all(readiness["checks"].values())


def test_pack_2400_next_handoff():
    payload = build_ir_cert_p2400_preview()

    assert payload["protected_enforcement_ready"] is True
    assert payload["safe_to_continue_to_pack_2401"] is True
