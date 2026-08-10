from ob_owner_experience.owner_walkthrough_authorization_packet import (
    OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_DECISION_OPTIONS,
    OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_IDENTITY,
    OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_NOT_AUTHORIZED,
    OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_REQUIRED_ACKS,
    OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_REQUIRED_FALSE_FLAGS,
    OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_REQUIRED_FIELDS,
    OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_REQUIRED_TRUE_FLAGS,
    build_owner_walkthrough_authorization_packet_bundle,
    build_owner_walkthrough_authorization_packet_handoff,
    build_owner_walkthrough_authorization_packet_requirements,
    build_owner_walkthrough_authorization_packet_room_scope,
    build_owner_walkthrough_authorization_packet_status,
)
from ob_owner_experience.six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER
from ob_owner_experience.ui_surface_registry import PROTECTED_ROUTE_POLICY


def test_gp013_identity():
    assert OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_IDENTITY["package"] == (
        "ob_owner_walkthrough_authorization_packet_gp013"
    )
    assert OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_IDENTITY["decision"] == (
        "READY_FOR_OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_WITH_SAFETY_LOCKS_HELD"
    )


def test_gp013_decision_options_do_not_grant_authorization_now():
    assert len(OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_DECISION_OPTIONS) == 3

    options = {
        item["decision"]: item["available_now"]
        for item in OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_DECISION_OPTIONS
    }

    assert options["AUTHORIZE_CONTROLLED_RUN"] is False
    assert options["HOLD_CONTROLLED_RUN"] is True
    assert options["REQUEST_MORE_PREP"] is True


def test_gp013_required_fields_and_acknowledgements_are_registered():
    for key in [
        "owner_identity_confirmation",
        "tower_owner_session_confirmation",
        "step_up_confirmation",
        "explicit_owner_authorization_decision",
        "bounded_walkthrough_window",
        "evidence_capture_plan",
        "six_room_scope_confirmation",
        "safety_lock_acknowledgement",
        "staging_ready_not_claimed",
        "live_auto_lock_acknowledgement",
    ]:
        assert key in OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_REQUIRED_FIELDS

    for text in [
        "This packet does not authorize the controlled run.",
        "The controlled-run gate remains closed.",
        "Owner walkthrough has not started.",
        "Owner walkthrough has not been accepted.",
        "Tower return/session continuity has not been repaired.",
        "Render has not been redeployed.",
        "STAGING_READY is not claimed.",
        "Broker submission remains locked.",
        "Real capital movement remains locked.",
        "Live Auto remains locked.",
    ]:
        assert text in OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_REQUIRED_ACKS


def test_gp013_authorization_requirements_are_unsatisfied_now():
    requirements = build_owner_walkthrough_authorization_packet_requirements()

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
        assert item["source"] == "GP012 controlled-run gate"


def test_gp013_room_scope_includes_all_six_without_live_route_opening():
    scope = build_owner_walkthrough_authorization_packet_room_scope()

    assert len(scope) == 6
    assert [item["room"] for item in scope] == list(SIX_ROOM_REAL_SURFACE_ORDER)

    for item in scope:
        assert item["included_in_future_authorization_scope"] is True
        assert item["eligible_for_future_controlled_run"] is True
        assert item["controlled_run_started"] is False
        assert item["controlled_run_completed"] is False
        assert item["owner_acceptance_recorded"] is False
        assert item["live_route_opened"] is False
        assert item["gate_state"] == "closed_pending_explicit_owner_authorization"
        assert item["route_hint"]
        assert item["component_hint"]
        assert item["data_adapter_hint"]


def test_gp013_status_packet_prepared_but_not_authorized():
    status = build_owner_walkthrough_authorization_packet_status()

    assert status["gp012_gate_prepared"] is True
    assert status["gp012_gate_closed"] is True
    assert status["authorization_packet_prepared"] is True
    assert status["authorization_requirements_registered"] is True
    assert status["all_six_rooms_scoped"] is True
    assert status["owner_identity_required"] is True
    assert status["tower_owner_session_required"] is True
    assert status["step_up_required"] is True
    assert status["explicit_owner_authorization_required"] is True
    assert status["owner_authorization_granted"] is False
    assert status["bounded_walkthrough_window_named"] is False
    assert status["evidence_capture_plan_active"] is False
    assert status["anonymous_access_allowed"] is False

    for key in OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_REQUIRED_FALSE_FLAGS:
        assert status[key] is False

    for key in OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_REQUIRED_TRUE_FLAGS:
        assert status[key] is True


def test_gp013_bundle_prepared_without_authorization_or_gate_opening():
    bundle = build_owner_walkthrough_authorization_packet_bundle()

    assert bundle["package"] == "ob_owner_walkthrough_authorization_packet_gp013"
    assert bundle["packet_prepared"] is True
    assert bundle["source_dependency"] == "GP012"
    assert bundle["gate_state"] == "closed_pending_explicit_owner_authorization"
    assert len(bundle["decision_options"]) == 3
    assert len(bundle["required_fields"]) == 10
    assert len(bundle["required_acknowledgements"]) >= 10
    assert len(bundle["authorization_requirements"]) == 6
    assert len(bundle["room_scope"]) == 6
    assert bundle["protected_route_policy"] == PROTECTED_ROUTE_POLICY
    assert "STAGING_READY" in bundle["must_not_claim"]
    assert "owner authorization granted" in bundle["not_authorized"]
    assert "controlled-run gate opening" in bundle["not_authorized"]
    assert "controlled run authorization" in bundle["not_authorized"]
    assert "owner walkthrough acceptance" in bundle["not_authorized"]
    assert "Tower return/session continuity repair" in bundle["not_authorized"]
    assert "Render redeploy" in bundle["not_authorized"]
    assert "broker submission" in bundle["not_authorized"]
    assert "real capital movement" in bundle["not_authorized"]
    assert "Live Auto unlock" in bundle["not_authorized"]

    boundary = bundle["release_boundary"]

    assert boundary["owner_authorization_granted"] is False
    assert boundary["authorization_packet_signed"] is False
    assert boundary["authorization_decision_recorded"] is False
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


def test_gp013_not_authorized_terms_are_declared():
    assert "STAGING_READY" in OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_NOT_AUTHORIZED
    assert "owner authorization granted" in OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_NOT_AUTHORIZED
    assert "authorization packet signed" in OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_NOT_AUTHORIZED
    assert "controlled-run gate opening" in OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_NOT_AUTHORIZED
    assert "controlled run authorization" in OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_NOT_AUTHORIZED
    assert "controlled run start" in OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_NOT_AUTHORIZED
    assert "owner walkthrough acceptance" in OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_NOT_AUTHORIZED
    assert "Tower return/session continuity repair" in OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_NOT_AUTHORIZED
    assert "Render redeploy" in OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_NOT_AUTHORIZED
    assert "broker submission" in OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_NOT_AUTHORIZED
    assert "real capital movement" in OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_NOT_AUTHORIZED
    assert "Live Auto unlock" in OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_NOT_AUTHORIZED


def test_gp013_handoff_has_packet_notes():
    handoff = build_owner_walkthrough_authorization_packet_handoff()

    assert handoff["package"] == "ob_owner_walkthrough_authorization_packet_gp013"
    assert handoff["packet_prepared"] is True
    assert handoff["source_dependency"] == "GP012"
    assert handoff["gate_state"] == "closed_pending_explicit_owner_authorization"
    assert len(handoff["decision_options"]) == 3
    assert len(handoff["authorization_requirements"]) == 6
    assert len(handoff["room_scope"]) == 6
    assert "Do not grant owner authorization from this package." in handoff["next_builder_notes"]
    assert "Do not sign or record an authorization decision from this package." in handoff["next_builder_notes"]
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
