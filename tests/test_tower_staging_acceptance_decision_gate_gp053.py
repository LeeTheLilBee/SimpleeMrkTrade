from ob_owner_experience.tower_staging_acceptance_decision_gate import (
    FALSE_FLAGS,
    TRUE_FLAGS,
    build_tower_staging_acceptance_decision_gate_bundle,
    build_tower_staging_acceptance_decision_gate_handoff,
    build_tower_staging_acceptance_decision_gate_record,
    build_tower_staging_acceptance_decision_gate_status,
)


def test_gp053_decision_gate_record():
    record = build_tower_staging_acceptance_decision_gate_record()
    assert record["gp052_review_packet_ready"] is True
    assert record["staging_ready"] is True
    assert record["acceptance_decision_gate_ready"] is True
    assert record["acceptance_decision_record_required"] is True
    assert "ACCEPT_TOWER_OB_STAGING" in record["allowed_decisions"]
    assert record["default_decision"] == "HOLD_TOWER_OB_STAGING"
    assert record["tower_acceptance_decision_recorded"] is False
    assert record["tower_staging_accepted"] is False


def test_gp053_status_bundle_handoff():
    status = build_tower_staging_acceptance_decision_gate_status()
    for key in FALSE_FLAGS:
        assert status[key] is False
    for key in TRUE_FLAGS:
        assert status[key] is True

    bundle = build_tower_staging_acceptance_decision_gate_bundle()
    assert bundle["package"] == "ob_tower_staging_acceptance_decision_gate_gp053"
    assert bundle["acceptance_decision_gate_ready"] is True
    assert bundle["source_dependency"] == "GP052"
    assert bundle["recommendation"] == "GO_FOR_TOWER_STAGING_ACCEPTANCE_DECISION_RECEIPT"
    assert bundle["release_boundary"]["tower_staging_accepted"] is False
    assert bundle["release_boundary"]["private_beta_access_opened"] is False

    handoff = build_tower_staging_acceptance_decision_gate_handoff()
    assert "Tower staging acceptance is not recorded in this package." in handoff["next_builder_notes"]
