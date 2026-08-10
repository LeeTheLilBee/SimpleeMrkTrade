from ob_owner_experience.owner_walkthrough_controlled_run_gate import (
    OWNER_WALKTHROUGH_CONTROLLED_RUN_AUTHORIZATION_REQUIREMENTS,
    OWNER_WALKTHROUGH_CONTROLLED_RUN_GATE_IDENTITY,
    OWNER_WALKTHROUGH_CONTROLLED_RUN_GATE_REQUIRED_INPUTS,
    OWNER_WALKTHROUGH_CONTROLLED_RUN_NOT_AUTHORIZED,
    OWNER_WALKTHROUGH_CONTROLLED_RUN_REQUIRED_FALSE_FLAGS,
    OWNER_WALKTHROUGH_CONTROLLED_RUN_REQUIRED_TRUE_FLAGS,
    build_owner_walkthrough_controlled_run_authorization_requirements,
    build_owner_walkthrough_controlled_run_gate_bundle,
    build_owner_walkthrough_controlled_run_gate_handoff,
    build_owner_walkthrough_controlled_run_gate_status,
    build_owner_walkthrough_controlled_run_room_gate_matrix,
)
from ob_owner_experience.six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER
from ob_owner_experience.ui_surface_registry import PROTECTED_ROUTE_POLICY


def test_gp012_identity():
    assert OWNER_WALKTHROUGH_CONTROLLED_RUN_GATE_IDENTITY["package"] == (
        "ob_owner_walkthrough_controlled_run_gate_gp012"
    )
    assert OWNER_WALKTHROUGH_CONTROLLED_RUN_GATE_IDENTITY["decision"] == (
        "READY_FOR_OWNER_WALKTHROUGH_CONTROLLED_RUN_GATE_WITH_SAFETY_LOCKS_HELD"
    )


def test_gp012_required_inputs_and_authorization_requirements_declared():
    assert "gp010_route_preparation_ready" in OWNER_WALKTHROUGH_CONTROLLED_RUN_GATE_REQUIRED_INPUTS
    assert "gp011_dry_run_evidence_ready" in OWNER_WALKTHROUGH_CONTROLLED_RUN_GATE_REQUIRED_INPUTS
    assert "explicit_owner_authorization_required" in OWNER_WALKTHROUGH_CONTROLLED_RUN_GATE_REQUIRED_INPUTS
    assert "dangerous_actions_locked" in OWNER_WALKTHROUGH_CONTROLLED_RUN_GATE_REQUIRED_INPUTS
    assert "staging_ready_not_claimed" in OWNER_WALKTHROUGH_CONTROLLED_RUN_GATE_REQUIRED_INPUTS

    requirements = build_owner_walkthrough_controlled_run_authorization_requirements()

    assert requirements == OWNER_WALKTHROUGH_CONTROLLED_RUN_AUTHORIZATION_REQUIREMENTS
    assert len(requirements) == 6

    keys = [item["key"] for item in requirements]

    assert "owner_identity" in keys
    assert "tower_owner_session" in keys
    assert "step_up" in keys
    assert "explicit_owner_authorization" in keys
    assert "walkthrough_window" in keys
    assert "evidence_capture" in keys

    for item in requirements:
        assert item["required"] is True
        assert item["satisfied_now"] is False


def test_gp012_room_gate_matrix_prepares_all_rooms_without_starting_run():
    matrix = build_owner_walkthrough_controlled_run_room_gate_matrix()

    assert len(matrix) == 6
    assert [item["room"] for item in matrix] == list(SIX_ROOM_REAL_SURFACE_ORDER)

    for item in matrix:
        assert item["dry_run_evidence_ready"] is True
        assert item["eligible_for_future_controlled_run"] is True
        assert item["controlled_run_started"] is False
        assert item["controlled_run_completed"] is False
        assert item["owner_acceptance_recorded"] is False
        assert item["live_route_opened"] is False
        assert item["gate_state"] == "closed_pending_explicit_owner_authorization"
        assert item["route_hint"]
        assert item["component_hint"]
        assert item["data_adapter_hint"]


def test_gp012_gate_status_prepared_but_closed():
    status = build_owner_walkthrough_controlled_run_gate_status()

    assert status["gp010_route_preparation_ready"] is True
    assert status["gp011_dry_run_evidence_ready"] is True
    assert status["all_six_rooms_present"] is True
    assert status["all_room_gates_prepared"] is True
    assert status["controlled_run_gate_prepared"] is True
    assert status["controlled_run_gate_closed"] is True
    assert status["owner_identity_required"] is True
    assert status["tower_owner_session_required"] is True
    assert status["step_up_required"] is True
    assert status["explicit_owner_authorization_required"] is True
    assert status["owner_authorization_present"] is False
    assert status["walkthrough_window_bound"] is False
    assert status["evidence_capture_started"] is False
    assert status["anonymous_access_allowed"] is False

    for key in OWNER_WALKTHROUGH_CONTROLLED_RUN_REQUIRED_FALSE_FLAGS:
        assert status[key] is False

    for key in OWNER_WALKTHROUGH_CONTROLLED_RUN_REQUIRED_TRUE_FLAGS:
        assert status[key] is True


def test_gp012_bundle_prepared_without_opening_gate():
    bundle = build_owner_walkthrough_controlled_run_gate_bundle()

    assert bundle["package"] == "ob_owner_walkthrough_controlled_run_gate_gp012"
    assert bundle["prepared"] is True
    assert bundle["source_dependency"] == "GP011"
    assert bundle["gate_state"] == "closed_pending_explicit_owner_authorization"
    assert len(bundle["authorization_requirements"]) == 6
    assert len(bundle["room_gate_matrix"]) == 6
    assert bundle["protected_route_policy"] == PROTECTED_ROUTE_POLICY
    assert "STAGING_READY" in bundle["must_not_claim"]
    assert "controlled run authorization" in bundle["not_authorized"]
    assert "controlled run start" in bundle["not_authorized"]
    assert "owner walkthrough acceptance" in bundle["not_authorized"]
    assert "Tower return/session continuity repair" in bundle["not_authorized"]
    assert "Render redeploy" in bundle["not_authorized"]
    assert "broker submission" in bundle["not_authorized"]
    assert "real capital movement" in bundle["not_authorized"]
    assert "Live Auto unlock" in bundle["not_authorized"]

    boundary = bundle["release_boundary"]

    assert boundary["controlled_run_gate_open"] is False
    assert boundary["controlled_run_authorized"] is False
    assert boundary["controlled_run_started"] is False
    assert boundary["controlled_run_completed"] is False
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


def test_gp012_not_authorized_terms_are_declared():
    assert "STAGING_READY" in OWNER_WALKTHROUGH_CONTROLLED_RUN_NOT_AUTHORIZED
    assert "controlled run authorization" in OWNER_WALKTHROUGH_CONTROLLED_RUN_NOT_AUTHORIZED
    assert "controlled run start" in OWNER_WALKTHROUGH_CONTROLLED_RUN_NOT_AUTHORIZED
    assert "controlled run completion" in OWNER_WALKTHROUGH_CONTROLLED_RUN_NOT_AUTHORIZED
    assert "owner walkthrough start" in OWNER_WALKTHROUGH_CONTROLLED_RUN_NOT_AUTHORIZED
    assert "owner walkthrough acceptance" in OWNER_WALKTHROUGH_CONTROLLED_RUN_NOT_AUTHORIZED
    assert "Tower return/session continuity repair" in OWNER_WALKTHROUGH_CONTROLLED_RUN_NOT_AUTHORIZED
    assert "Render redeploy" in OWNER_WALKTHROUGH_CONTROLLED_RUN_NOT_AUTHORIZED
    assert "broker submission" in OWNER_WALKTHROUGH_CONTROLLED_RUN_NOT_AUTHORIZED
    assert "real capital movement" in OWNER_WALKTHROUGH_CONTROLLED_RUN_NOT_AUTHORIZED
    assert "Live Auto unlock" in OWNER_WALKTHROUGH_CONTROLLED_RUN_NOT_AUTHORIZED


def test_gp012_handoff_has_gate_notes():
    handoff = build_owner_walkthrough_controlled_run_gate_handoff()

    assert handoff["package"] == "ob_owner_walkthrough_controlled_run_gate_gp012"
    assert handoff["prepared"] is True
    assert handoff["source_dependency"] == "GP011"
    assert handoff["gate_state"] == "closed_pending_explicit_owner_authorization"
    assert len(handoff["authorization_requirements"]) == 6
    assert len(handoff["room_gate_matrix"]) == 6
    assert "Do not open the controlled-run gate from this package." in handoff["next_builder_notes"]
    assert "Do not authorize the controlled run from this package." in handoff["next_builder_notes"]
    assert "Do not start the owner walkthrough from this package." in handoff["next_builder_notes"]
    assert "Do not mark owner walkthrough accepted from this package." in handoff["next_builder_notes"]
    assert "Do not claim Tower return/session continuity repaired from this package." in handoff["next_builder_notes"]
    assert "Do not redeploy Render from this package." in handoff["next_builder_notes"]
    assert "Do not claim STAGING_READY." in handoff["next_builder_notes"]
    assert "Keep broker submission locked." in handoff["next_builder_notes"]
    assert "Keep real capital movement locked." in handoff["next_builder_notes"]
    assert "Keep Live Auto locked." in handoff["next_builder_notes"]
