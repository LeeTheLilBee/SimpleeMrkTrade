from ob_owner_experience.owner_walkthrough_controlled_start import (
    FALSE_FLAGS,
    TRUE_FLAGS,
    build_owner_walkthrough_controlled_start_bundle,
    build_owner_walkthrough_controlled_start_handoff,
    build_owner_walkthrough_controlled_start_record,
    build_owner_walkthrough_controlled_start_status,
)
from ob_owner_experience.six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER


def test_gp031_start_record():
    record = build_owner_walkthrough_controlled_start_record()
    assert record["gp030_clearance_ready"] is True
    assert record["owner_action_to_start_recorded"] is True
    assert record["controlled_walkthrough_started"] is True
    assert record["owner_walkthrough_started"] is True
    assert record["owner_walkthrough_accepted"] is False
    assert record["rooms_started"] == list(SIX_ROOM_REAL_SURFACE_ORDER)
    assert record["staging_ready"] is False


def test_gp031_status_bundle_handoff():
    status = build_owner_walkthrough_controlled_start_status()
    for key in FALSE_FLAGS:
        assert status[key] is False
    for key in TRUE_FLAGS:
        assert status[key] is True

    bundle = build_owner_walkthrough_controlled_start_bundle()
    assert bundle["package"] == "ob_owner_walkthrough_controlled_start_gp031"
    assert bundle["controlled_start_recorded"] is True
    assert bundle["source_dependency"] == "GP030"
    assert bundle["release_boundary"]["owner_walkthrough_started"] is True
    assert bundle["release_boundary"]["owner_walkthrough_accepted"] is False
    assert bundle["release_boundary"]["staging_ready"] is False
    assert "STAGING_READY" in bundle["must_not_claim"]

    handoff = build_owner_walkthrough_controlled_start_handoff()
    assert "Owner walkthrough has started." in handoff["next_builder_notes"]
    assert "Owner walkthrough has not been accepted." in handoff["next_builder_notes"]
