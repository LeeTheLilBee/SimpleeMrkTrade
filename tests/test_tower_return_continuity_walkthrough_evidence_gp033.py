from ob_owner_experience.tower_return_continuity_walkthrough_evidence import (
    FALSE_FLAGS,
    TRUE_FLAGS,
    build_tower_return_continuity_walkthrough_evidence,
    build_tower_return_continuity_walkthrough_evidence_bundle,
    build_tower_return_continuity_walkthrough_evidence_handoff,
    build_tower_return_continuity_walkthrough_evidence_status,
)
from ob_owner_experience.six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER


def test_gp033_return_evidence_all_six():
    evidence = build_tower_return_continuity_walkthrough_evidence()
    assert len(evidence) == 6
    assert [item["room"] for item in evidence] == list(SIX_ROOM_REAL_SURFACE_ORDER)
    for item in evidence:
        assert item["owner_walkthrough_started"] is True
        assert item["return_ready"] is True
        assert item["tower_return_route"] == "/tower/access-home"
        assert item["return_control_observed"] is True
        assert item["session_continuity_observed"] is True
        assert item["tower_return_continuity_evidence_captured"] is True
        assert item["owner_acceptance_recorded"] is False
        assert item["staging_ready"] is False


def test_gp033_status_bundle_handoff():
    status = build_tower_return_continuity_walkthrough_evidence_status()
    for key in FALSE_FLAGS:
        assert status[key] is False
    for key in TRUE_FLAGS:
        assert status[key] is True

    bundle = build_tower_return_continuity_walkthrough_evidence_bundle()
    assert bundle["package"] == "ob_tower_return_continuity_walkthrough_evidence_gp033"
    assert bundle["return_continuity_evidence_ready"] is True
    assert bundle["source_dependency"] == "GP032"
    assert bundle["release_boundary"]["owner_walkthrough_started"] is True
    assert bundle["release_boundary"]["owner_walkthrough_accepted"] is False
    assert "STAGING_READY" in bundle["must_not_claim"]

    handoff = build_tower_return_continuity_walkthrough_evidence_handoff()
    assert "Tower return continuity walkthrough evidence is captured." in handoff["next_builder_notes"]
