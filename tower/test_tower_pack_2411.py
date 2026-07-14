from tower.tower_ir_cert_p2411 import (
    build_protected_launch_evidence_bundle,
)


def test_pack_2411_evidence_bundle_complete():
    bundle = build_protected_launch_evidence_bundle()

    assert bundle["integration_rehearsal_status"] == "passed"
    assert bundle["enforcement_rehearsal_status"] == "passed"
    assert bundle["failure_rehearsal_status"] == "passed"
    assert bundle["default_deny_proven"] is True
    assert bundle["replay_blocking_proven"] is True
    assert bundle["receipt_chain_proven"] is True
    assert bundle["failure_recovery_proven"] is True
    assert len(bundle["integrity_hash"]) == 64
