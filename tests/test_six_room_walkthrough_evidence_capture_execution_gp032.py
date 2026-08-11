from ob_owner_experience.six_room_walkthrough_evidence_capture_execution import (
    FALSE_FLAGS,
    TRUE_FLAGS,
    build_six_room_walkthrough_evidence_capture_execution_bundle,
    build_six_room_walkthrough_evidence_capture_execution_handoff,
    build_six_room_walkthrough_evidence_capture_status,
    build_six_room_walkthrough_evidence_matrix,
)
from ob_owner_experience.six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER


def test_gp032_evidence_matrix_all_six():
    matrix = build_six_room_walkthrough_evidence_matrix()
    assert len(matrix) == 6
    assert [item["room"] for item in matrix] == list(SIX_ROOM_REAL_SURFACE_ORDER)
    for item in matrix:
        assert item["owner_walkthrough_started"] is True
        assert item["room_reached"] is True
        assert item["owner_view_confirmed"] is True
        assert item["dangerous_actions_locked"] is True
        assert item["tower_return_visible"] is True
        assert item["evidence_captured"] is True
        assert item["owner_acceptance_recorded"] is False
        assert item["staging_ready"] is False


def test_gp032_status_bundle_handoff():
    status = build_six_room_walkthrough_evidence_capture_status()
    for key in FALSE_FLAGS:
        assert status[key] is False
    for key in TRUE_FLAGS:
        assert status[key] is True

    bundle = build_six_room_walkthrough_evidence_capture_execution_bundle()
    assert bundle["package"] == "ob_six_room_walkthrough_evidence_capture_execution_gp032"
    assert bundle["evidence_capture_executed"] is True
    assert bundle["source_dependency"] == "GP031"
    assert bundle["release_boundary"]["owner_walkthrough_started"] is True
    assert bundle["release_boundary"]["owner_walkthrough_accepted"] is False
    assert "STAGING_READY" in bundle["must_not_claim"]

    handoff = build_six_room_walkthrough_evidence_capture_execution_handoff()
    assert "Six-room walkthrough evidence capture is complete." in handoff["next_builder_notes"]
