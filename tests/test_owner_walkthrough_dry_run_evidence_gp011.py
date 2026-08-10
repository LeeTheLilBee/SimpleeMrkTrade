from ob_owner_experience.owner_walkthrough_dry_run_evidence import (
    OWNER_WALKTHROUGH_DRY_RUN_EVIDENCE_IDENTITY,
    OWNER_WALKTHROUGH_DRY_RUN_NOT_AUTHORIZED,
    OWNER_WALKTHROUGH_DRY_RUN_REQUIRED_CHECKS,
    OWNER_WALKTHROUGH_DRY_RUN_REQUIRED_FALSE_FLAGS,
    OWNER_WALKTHROUGH_DRY_RUN_REQUIRED_TRUE_FLAGS,
    build_owner_walkthrough_dry_run_evidence_bundle,
    build_owner_walkthrough_dry_run_evidence_handoff,
    build_owner_walkthrough_dry_run_evidence_matrix,
    build_owner_walkthrough_dry_run_evidence_status,
)
from ob_owner_experience.six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER
from ob_owner_experience.ui_surface_registry import PROTECTED_ROUTE_POLICY


def test_gp011_identity():
    assert OWNER_WALKTHROUGH_DRY_RUN_EVIDENCE_IDENTITY["package"] == (
        "ob_owner_walkthrough_dry_run_evidence_gp011"
    )
    assert OWNER_WALKTHROUGH_DRY_RUN_EVIDENCE_IDENTITY["decision"] == (
        "READY_FOR_OWNER_WALKTHROUGH_DRY_RUN_EVIDENCE_WITH_SAFETY_LOCKS_HELD"
    )


def test_gp011_dry_run_evidence_matrix_records_all_six_rooms():
    matrix = build_owner_walkthrough_dry_run_evidence_matrix()

    assert len(matrix) == 6
    assert [item["room"] for item in matrix] == list(SIX_ROOM_REAL_SURFACE_ORDER)

    for item in matrix:
        assert item["evidence_ready"] is True
        assert item["route_hint"]
        assert item["component_hint"]
        assert item["data_adapter_hint"]
        assert item["owner_goal"]
        assert item["owner_prompt"]
        assert item["actual_owner_session_started"] is False
        assert item["actual_owner_walkthrough_started"] is False
        assert item["actual_owner_walkthrough_accepted"] is False
        assert item["actual_route_opened_live"] is False
        assert item["dry_run_scope"]["dry_run_type"] == "script_only_no_live_owner_session"
        assert item["dry_run_scope"]["real_owner_session_started"] is False
        assert item["dry_run_scope"]["real_owner_walkthrough_started"] is False
        assert item["dry_run_scope"]["real_owner_walkthrough_accepted"] is False
        assert item["dry_run_scope"]["live_route_opened"] is False
        assert item["dry_run_scope"]["staging_ready"] is False

        for key in OWNER_WALKTHROUGH_DRY_RUN_REQUIRED_CHECKS:
            assert item["checks"][key] is True


def test_gp011_status_ready_but_real_walkthrough_not_started():
    status = build_owner_walkthrough_dry_run_evidence_status()

    assert status["gp010_preparation_ready"] is True
    assert status["all_six_rooms_present"] is True
    assert status["all_dry_run_records_ready"] is True
    assert status["dry_run_evidence_ready"] is True
    assert status["anonymous_access_allowed"] is False

    for key in OWNER_WALKTHROUGH_DRY_RUN_REQUIRED_FALSE_FLAGS:
        assert status[key] is False

    for key in OWNER_WALKTHROUGH_DRY_RUN_REQUIRED_TRUE_FLAGS:
        assert status[key] is True


def test_gp011_bundle_ready_and_safety_locked():
    bundle = build_owner_walkthrough_dry_run_evidence_bundle()

    assert bundle["package"] == "ob_owner_walkthrough_dry_run_evidence_gp011"
    assert bundle["ready"] is True
    assert bundle["source_dependency"] == "GP010"
    assert bundle["room_order"] == list(SIX_ROOM_REAL_SURFACE_ORDER)
    assert len(bundle["dry_run_evidence_matrix"]) == 6
    assert bundle["protected_route_policy"] == PROTECTED_ROUTE_POLICY
    assert "STAGING_READY" in bundle["must_not_claim"]
    assert "owner walkthrough start" in bundle["not_authorized"]
    assert "owner walkthrough acceptance" in bundle["not_authorized"]
    assert "Tower return/session continuity repair" in bundle["not_authorized"]
    assert "Render redeploy" in bundle["not_authorized"]
    assert "broker submission" in bundle["not_authorized"]
    assert "real capital movement" in bundle["not_authorized"]
    assert "Live Auto unlock" in bundle["not_authorized"]

    boundary = bundle["release_boundary"]

    assert boundary["real_owner_session_started"] is False
    assert boundary["real_owner_walkthrough_started"] is False
    assert boundary["real_owner_walkthrough_accepted"] is False
    assert boundary["owner_walkthrough_started"] is False
    assert boundary["owner_walkthrough_accepted"] is False
    assert boundary["live_route_opened"] is False
    assert boundary["tower_return_repaired"] is False
    assert boundary["render_redeployed"] is False
    assert boundary["production_deploy_enabled"] is False
    assert boundary["broker_submission_enabled"] is False
    assert boundary["real_capital_movement_enabled"] is False
    assert boundary["direct_execution_enabled"] is False
    assert boundary["automated_execution_enabled"] is False
    assert boundary["permission_mutation_enabled"] is False
    assert boundary["secret_reveal_enabled"] is False
    assert boundary["staging_ready"] is False
    assert boundary["live_auto_locked"] is True


def test_gp011_not_authorized_terms_are_declared():
    assert "STAGING_READY" in OWNER_WALKTHROUGH_DRY_RUN_NOT_AUTHORIZED
    assert "real owner session start" in OWNER_WALKTHROUGH_DRY_RUN_NOT_AUTHORIZED
    assert "owner walkthrough start" in OWNER_WALKTHROUGH_DRY_RUN_NOT_AUTHORIZED
    assert "owner walkthrough acceptance" in OWNER_WALKTHROUGH_DRY_RUN_NOT_AUTHORIZED
    assert "Tower return/session continuity repair" in OWNER_WALKTHROUGH_DRY_RUN_NOT_AUTHORIZED
    assert "Render redeploy" in OWNER_WALKTHROUGH_DRY_RUN_NOT_AUTHORIZED
    assert "production deployment" in OWNER_WALKTHROUGH_DRY_RUN_NOT_AUTHORIZED
    assert "broker submission" in OWNER_WALKTHROUGH_DRY_RUN_NOT_AUTHORIZED
    assert "real capital movement" in OWNER_WALKTHROUGH_DRY_RUN_NOT_AUTHORIZED
    assert "Live Auto unlock" in OWNER_WALKTHROUGH_DRY_RUN_NOT_AUTHORIZED


def test_gp011_handoff_has_next_builder_notes():
    handoff = build_owner_walkthrough_dry_run_evidence_handoff()

    assert handoff["package"] == "ob_owner_walkthrough_dry_run_evidence_gp011"
    assert handoff["ready"] is True
    assert handoff["source_dependency"] == "GP010"
    assert len(handoff["dry_run_evidence_matrix"]) == 6
    assert "Treat this as dry-run evidence only." in handoff["next_builder_notes"]
    assert "Do not start the real owner walkthrough from this package." in handoff["next_builder_notes"]
    assert "Do not mark owner walkthrough accepted from this package." in handoff["next_builder_notes"]
    assert "Do not claim Tower return/session continuity repaired from this package." in handoff["next_builder_notes"]
    assert "Do not open live routes as evidence from this package." in handoff["next_builder_notes"]
    assert "Do not redeploy Render from this package." in handoff["next_builder_notes"]
    assert "Do not claim STAGING_READY." in handoff["next_builder_notes"]
    assert "Keep broker submission locked." in handoff["next_builder_notes"]
    assert "Keep real capital movement locked." in handoff["next_builder_notes"]
    assert "Keep Live Auto locked." in handoff["next_builder_notes"]
