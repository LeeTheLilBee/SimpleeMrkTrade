from ob_owner_experience.tower_staging_acceptance_decision_receipt import (
    FALSE_FLAGS,
    TRUE_FLAGS,
    build_tower_staging_acceptance_decision_receipt,
    build_tower_staging_acceptance_decision_receipt_bundle,
    build_tower_staging_acceptance_decision_receipt_handoff,
    build_tower_staging_acceptance_decision_receipt_status,
)


def test_gp054_acceptance_receipt():
    receipt = build_tower_staging_acceptance_decision_receipt()
    assert receipt["gp053_acceptance_decision_gate_ready"] is True
    assert receipt["decision_value"] == "ACCEPT_TOWER_OB_STAGING"
    assert receipt["tower_acceptance_decision_recorded"] is True
    assert receipt["tower_staging_accepted"] is True
    assert receipt["staging_ready"] is True
    assert receipt["acceptance_receipt_append_only"] is True
    assert receipt["private_beta_access_opened"] is False
    assert receipt["tester_credentials_issued"] is False


def test_gp054_status_bundle_handoff():
    status = build_tower_staging_acceptance_decision_receipt_status()
    for key in FALSE_FLAGS:
        assert status[key] is False
    for key in TRUE_FLAGS:
        assert status[key] is True

    bundle = build_tower_staging_acceptance_decision_receipt_bundle()
    assert bundle["package"] == "ob_tower_staging_acceptance_decision_receipt_gp054"
    assert bundle["acceptance_decision_receipt_recorded"] is True
    assert bundle["source_dependency"] == "GP053"
    assert bundle["recommendation"] == "GO_FOR_TOWER_OB_BETA_LAUNCH_PREPARATION_CLOSEOUT"
    assert bundle["release_boundary"]["tower_staging_accepted"] is True
    assert bundle["release_boundary"]["private_beta_access_opened"] is False

    handoff = build_tower_staging_acceptance_decision_receipt_handoff()
    assert "Tower staging is accepted." in handoff["next_builder_notes"]
    assert "Tester credentials are not issued." in handoff["next_builder_notes"]
