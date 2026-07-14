from tower.tower_ir_cert_p2419 import (
    run_final_certification_rehearsal,
)


def test_pack_2419_final_certification():
    result = run_final_certification_rehearsal()

    assert result["status"] == "passed"
    assert result["recommendation"] == (
        "GO_TOWER_OB_PREVIEW_CONTRACT_CERTIFIED"
    )
    assert all(result["checks"].values())
    assert result["seal_verification"]["valid"] is True
    assert result["production_authorization_granted"] is False
