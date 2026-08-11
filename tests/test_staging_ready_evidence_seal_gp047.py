from ob_owner_experience.staging_ready_evidence_seal import (
    FALSE_FLAGS,
    TRUE_FLAGS,
    build_staging_ready_evidence_seal_bundle,
    build_staging_ready_evidence_seal_handoff,
    build_staging_ready_evidence_seal_record,
    build_staging_ready_evidence_seal_status,
)


def test_gp047_seal_record():
    record = build_staging_ready_evidence_seal_record()
    assert record["gp046_staging_ready_claim_released"] is True
    assert record["staging_ready"] is True
    assert record["staging_readiness_granted"] is True
    assert record["staging_ready_evidence_sealed"] is True
    assert record["evidence_append_only"] is True
    assert len(record["sealed_evidence_inputs"]) == 6
    assert record["production_deploy_enabled"] is False
    assert record["broker_submission_enabled"] is False
    assert record["real_capital_movement_enabled"] is False
    assert record["live_auto_locked"] is True


def test_gp047_status_bundle_handoff():
    status = build_staging_ready_evidence_seal_status()
    for key in FALSE_FLAGS:
        assert status[key] is False
    for key in TRUE_FLAGS:
        assert status[key] is True

    bundle = build_staging_ready_evidence_seal_bundle()
    assert bundle["package"] == "ob_staging_ready_evidence_seal_gp047"
    assert bundle["staging_ready_evidence_sealed"] is True
    assert bundle["source_dependency"] == "GP046"
    assert bundle["release_boundary"]["staging_ready"] is True
    assert bundle["release_boundary"]["production_deploy_enabled"] is False
    assert "PRODUCTION_READY" in bundle["must_not_claim"]

    handoff = build_staging_ready_evidence_seal_handoff()
    assert "Staging ready evidence is sealed." in handoff["next_builder_notes"]
    assert "Live Auto remains locked." in handoff["next_builder_notes"]
