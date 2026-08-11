from ob_owner_experience.tower_ob_beta_launch_preparation_closeout import (
    FALSE_FLAGS,
    TRUE_FLAGS,
    build_tower_ob_beta_launch_preparation_closeout_bundle,
    build_tower_ob_beta_launch_preparation_closeout_handoff,
    build_tower_ob_beta_launch_preparation_closeout_record,
    build_tower_ob_beta_launch_preparation_closeout_status,
)


def test_gp055_closeout_record():
    record = build_tower_ob_beta_launch_preparation_closeout_record()
    assert record["gp054_acceptance_decision_receipt_recorded"] is True
    assert record["tower_staging_accepted"] is True
    assert record["staging_ready"] is True
    assert record["beta_launch_preparation_closeout_ready"] is True
    assert record["private_beta_access_authorization_required_next"] is True
    assert record["tester_credential_gate_required_next"] is True
    assert record["private_beta_access_opened"] is False
    assert record["tester_credentials_issued"] is False
    assert len(record["closed_items"]) == 5


def test_gp055_status_bundle_handoff():
    status = build_tower_ob_beta_launch_preparation_closeout_status()
    for key in FALSE_FLAGS:
        assert status[key] is False
    for key in TRUE_FLAGS:
        assert status[key] is True

    bundle = build_tower_ob_beta_launch_preparation_closeout_bundle()
    assert bundle["package"] == "ob_tower_ob_beta_launch_preparation_closeout_gp055"
    assert bundle["beta_launch_preparation_closeout_ready"] is True
    assert bundle["source_dependency"] == "GP054"
    assert bundle["recommendation"] == "GO_FOR_PRIVATE_BETA_ACCESS_AUTHORIZATION"
    assert bundle["gate_state"] == "tower_ob_beta_launch_preparation_closeout_sealed"
    assert bundle["release_boundary"]["staging_ready"] is True
    assert bundle["release_boundary"]["tower_staging_accepted"] is True
    assert bundle["release_boundary"]["private_beta_access_opened"] is False
    assert bundle["release_boundary"]["tester_credentials_issued"] is False

    handoff = build_tower_ob_beta_launch_preparation_closeout_handoff()
    assert "Private beta access is still not opened." in handoff["next_builder_notes"]
    assert "Tester credentials are still not issued." in handoff["next_builder_notes"]
    assert "Next build is GP056 Private Beta Access Authorization." in handoff["next_builder_notes"]
