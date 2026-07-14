from tower.tower_ir_cert_p2390 import (
    build_ir_cert_p2390_preview,
    build_protected_launch_readiness,
)


def test_pack_2390_integration_readiness():
    readiness = build_protected_launch_readiness()

    assert readiness["ready"] is True
    assert readiness["recommendation"] == (
        "GO_TOWER_OB_PROTECTED_LAUNCH_INTEGRATION_READY"
    )

    assert all(readiness["checks"].values())


def test_pack_2390_checkpoint_handoff():
    payload = build_ir_cert_p2390_preview()

    assert payload["protected_launch_integration_ready"] is True
    assert payload["safe_to_continue_to_pack_2391"] is True
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
