from ob_owner_experience.owner_walkthrough_acceptance_decision_record import (
    FALSE_FLAGS,
    TRUE_FLAGS,
    build_owner_walkthrough_acceptance_decision_bundle,
    build_owner_walkthrough_acceptance_decision_handoff,
    build_owner_walkthrough_acceptance_decision_record,
    build_owner_walkthrough_acceptance_decision_status,
)
from ob_owner_experience.six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER


def test_gp034_acceptance_record():
    record = build_owner_walkthrough_acceptance_decision_record()
    assert record["acceptance_decision"] == "ACCEPT_OWNER_WALKTHROUGH"
    assert record["owner_acceptance_decision_recorded"] is True
    assert record["owner_walkthrough_started"] is True
    assert record["owner_walkthrough_accepted"] is True
    assert record["six_room_evidence_present"] is True
    assert record["tower_return_evidence_present"] is True
    assert record["rooms_accepted"] == list(SIX_ROOM_REAL_SURFACE_ORDER)
    assert record["staging_ready"] is False


def test_gp034_status_bundle_handoff():
    status = build_owner_walkthrough_acceptance_decision_status()
    for key in FALSE_FLAGS:
        assert status[key] is False
    for key in TRUE_FLAGS:
        assert status[key] is True

    bundle = build_owner_walkthrough_acceptance_decision_bundle()
    assert bundle["package"] == "ob_owner_walkthrough_acceptance_decision_record_gp034"
    assert bundle["acceptance_decision_recorded"] is True
    assert bundle["source_dependency"] == "GP033"
    assert bundle["release_boundary"]["owner_walkthrough_started"] is True
    assert bundle["release_boundary"]["owner_walkthrough_accepted"] is True
    assert bundle["release_boundary"]["staging_ready"] is False
    assert "STAGING_READY" in bundle["must_not_claim"]

    handoff = build_owner_walkthrough_acceptance_decision_handoff()
    assert "Owner walkthrough has been accepted." in handoff["next_builder_notes"]
    assert "Do not claim STAGING_READY." in handoff["next_builder_notes"]
