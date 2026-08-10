from ob_owner_experience.six_room_walkthrough_evidence_capture_plan import (
    FALSE_FLAGS,
    TRUE_FLAGS,
    build_six_room_walkthrough_evidence_capture_matrix,
    build_six_room_walkthrough_evidence_capture_plan_bundle,
    build_six_room_walkthrough_evidence_capture_plan_handoff,
    build_six_room_walkthrough_evidence_capture_status,
)
from ob_owner_experience.six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER


def test_gp019_capture_matrix_planned_not_started():
    matrix = build_six_room_walkthrough_evidence_capture_matrix()
    assert len(matrix) == 6
    assert [item["room"] for item in matrix] == list(SIX_ROOM_REAL_SURFACE_ORDER)
    for item in matrix:
        assert item["capture_required"] is True
        assert item["capture_started"] is False
        assert item["capture_completed"] is False
        assert item["evidence_finalized"] is False
        assert item["owner_acceptance_recorded"] is False


def test_gp019_status_locked():
    status = build_six_room_walkthrough_evidence_capture_status()
    assert status["gp018_opening_gate_prepared"] is True
    assert status["capture_plan_prepared"] is True
    assert status["all_six_rooms_planned"] is True
    for key in FALSE_FLAGS:
        assert status[key] is False
    for key in TRUE_FLAGS:
        assert status[key] is True


def test_gp019_bundle_and_handoff():
    bundle = build_six_room_walkthrough_evidence_capture_plan_bundle()
    assert bundle["package"] == "ob_six_room_walkthrough_evidence_capture_plan_gp019"
    assert bundle["capture_plan_prepared"] is True
    assert bundle["source_dependency"] == "GP018"
    assert bundle["release_boundary"]["evidence_capture_started"] is False
    assert bundle["release_boundary"]["live_auto_locked"] is True
    assert "STAGING_READY" in bundle["must_not_claim"]

    handoff = build_six_room_walkthrough_evidence_capture_plan_handoff()
    assert "Do not start evidence capture from this package." in handoff["next_builder_notes"]
    assert "Do not claim STAGING_READY." in handoff["next_builder_notes"]
