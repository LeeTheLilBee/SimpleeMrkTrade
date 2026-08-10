from ob_owner_experience.owner_authorization_decision_recording_gate import (
    OWNER_AUTHORIZATION_DECISION_RECORDING_ALLOWED_DECISION_VALUES,
    OWNER_AUTHORIZATION_DECISION_RECORDING_DEFAULT_DECISION,
    OWNER_AUTHORIZATION_DECISION_RECORDING_GATE_IDENTITY,
    OWNER_AUTHORIZATION_DECISION_RECORDING_GATE_REQUIRED_INPUTS,
    OWNER_AUTHORIZATION_DECISION_RECORDING_NOT_AUTHORIZED,
    OWNER_AUTHORIZATION_DECISION_RECORDING_REQUIRED_ACKS,
    OWNER_AUTHORIZATION_DECISION_RECORDING_REQUIRED_FALSE_FLAGS,
    OWNER_AUTHORIZATION_DECISION_RECORDING_REQUIRED_TRUE_FLAGS,
    build_owner_authorization_decision_recording_acknowledgements,
    build_owner_authorization_decision_recording_candidate_values,
    build_owner_authorization_decision_recording_gate_bundle,
    build_owner_authorization_decision_recording_gate_handoff,
    build_owner_authorization_decision_recording_gate_status,
    build_owner_authorization_decision_recording_room_scope,
    build_owner_authorization_decision_recording_schema,
)
from ob_owner_experience.six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER
from ob_owner_experience.ui_surface_registry import PROTECTED_ROUTE_POLICY


def test_gp014_identity_and_required_inputs():
    assert OWNER_AUTHORIZATION_DECISION_RECORDING_GATE_IDENTITY["package"] == (
        "ob_owner_authorization_decision_recording_gate_gp014"
    )
    assert OWNER_AUTHORIZATION_DECISION_RECORDING_GATE_IDENTITY["decision"] == (
        "READY_FOR_OWNER_AUTHORIZATION_DECISION_RECORDING_GATE_WITH_SAFETY_LOCKS_HELD"
    )
    for key in [
        "gp013_authorization_packet_prepared",
        "gp013_gate_state_closed",
        "owner_identity_required",
        "tower_owner_session_required",
        "step_up_required",
        "explicit_owner_authorization_required",
        "decision_record_schema_prepared",
        "append_only_receipt_required",
        "safety_acknowledgements_required",
        "staging_ready_not_claimed",
    ]:
        assert key in OWNER_AUTHORIZATION_DECISION_RECORDING_GATE_REQUIRED_INPUTS


def test_gp014_decision_schema_candidate_values_and_acknowledgements():
    schema = build_owner_authorization_decision_recording_schema()
    values = build_owner_authorization_decision_recording_candidate_values()
    acknowledgements = build_owner_authorization_decision_recording_acknowledgements()

    assert schema["record_type"] == "owner_walkthrough_authorization_decision"
    assert schema["append_only"] is True
    assert schema["redaction_required"] is True
    assert schema["secret_values_forbidden"] is True
    assert schema["broker_payload_forbidden"] is True
    assert schema["money_movement_forbidden"] is True
    assert schema["allowed_decision_values"] == list(OWNER_AUTHORIZATION_DECISION_RECORDING_ALLOWED_DECISION_VALUES)
    assert schema["default_decision"] == OWNER_AUTHORIZATION_DECISION_RECORDING_DEFAULT_DECISION

    for field in [
        "decision_id",
        "owner_identity_confirmation",
        "tower_owner_session_confirmation",
        "step_up_confirmation",
        "decision_value",
        "decision_reason",
        "bounded_walkthrough_window",
        "evidence_capture_plan",
        "six_room_scope_confirmation",
        "safety_lock_acknowledgement",
        "created_at",
    ]:
        assert field in schema["required_fields"]

    assert len(values) == 3
    assert [item["decision_value"] for item in values] == [
        "AUTHORIZE_CONTROLLED_RUN",
        "HOLD_CONTROLLED_RUN",
        "REQUEST_MORE_PREP",
    ]
    for item in values:
        assert item["registered"] is True
        assert item["available_in_gp013_packet"] is True
        assert item["available_now"] is False
        assert item["recording_allowed_now"] is False

    assert acknowledgements == OWNER_AUTHORIZATION_DECISION_RECORDING_REQUIRED_ACKS
    assert "This gate does not record authorization." in acknowledgements
    assert "No authorization decision is recorded in this package." in acknowledgements
    assert "The authorization packet is not signed in this package." in acknowledgements
    assert "The controlled-run gate remains closed." in acknowledgements
    assert "STAGING_READY is not claimed." in acknowledgements
    assert "Broker submission remains locked." in acknowledgements
    assert "Real capital movement remains locked." in acknowledgements
    assert "Live Auto remains locked." in acknowledgements


def test_gp014_room_scope_and_status_are_prepared_but_not_recording():
    scope = build_owner_authorization_decision_recording_room_scope()
    status = build_owner_authorization_decision_recording_gate_status()

    assert len(scope) == 6
    assert [item["room"] for item in scope] == list(SIX_ROOM_REAL_SURFACE_ORDER)

    for item in scope:
        assert item["included_in_decision_scope"] is True
        assert item["eligible_for_future_controlled_run"] is True
        assert item["controlled_run_started"] is False
        assert item["controlled_run_completed"] is False
        assert item["owner_acceptance_recorded"] is False
        assert item["live_route_opened"] is False
        assert item["gate_state"] == "closed_pending_explicit_owner_authorization"
        assert item["route_hint"]
        assert item["component_hint"]
        assert item["data_adapter_hint"]

    assert status["gp013_authorization_packet_prepared"] is True
    assert status["gp013_gate_state_closed"] is True
    assert status["decision_recording_gate_prepared"] is True
    assert status["decision_recording_gate_closed"] is True
    assert status["decision_record_schema_prepared"] is True
    assert status["decision_values_registered"] is True
    assert status["all_six_rooms_scoped"] is True
    assert status["append_only_receipt_required"] is True
    assert status["anonymous_access_allowed"] is False

    for key in OWNER_AUTHORIZATION_DECISION_RECORDING_REQUIRED_FALSE_FLAGS:
        assert status[key] is False

    for key in OWNER_AUTHORIZATION_DECISION_RECORDING_REQUIRED_TRUE_FLAGS:
        assert status[key] is True


def test_gp014_bundle_prepared_without_decision_recording_or_gate_opening():
    bundle = build_owner_authorization_decision_recording_gate_bundle()

    assert bundle["package"] == "ob_owner_authorization_decision_recording_gate_gp014"
    assert bundle["gate_prepared"] is True
    assert bundle["source_dependency"] == "GP013"
    assert bundle["gate_state"] == "closed_pending_future_owner_decision_recording"
    assert len(bundle["required_inputs"]) == 10
    assert bundle["decision_record_schema"]["append_only"] is True
    assert len(bundle["decision_candidate_values"]) == 3
    assert len(bundle["required_acknowledgements"]) >= 10
    assert len(bundle["room_scope"]) == 6
    assert bundle["protected_route_policy"] == PROTECTED_ROUTE_POLICY
    assert "STAGING_READY" in bundle["must_not_claim"]
    assert "authorization decision recorded" in bundle["not_authorized"]
    assert "decision receipt emitted" in bundle["not_authorized"]
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
    assert boundary["decision_recording_enabled"] is False
    assert boundary["decision_receipt_emitted"] is False
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


def test_gp014_not_authorized_terms_and_handoff_notes():
    assert "STAGING_READY" in OWNER_AUTHORIZATION_DECISION_RECORDING_NOT_AUTHORIZED
    assert "owner authorization granted" in OWNER_AUTHORIZATION_DECISION_RECORDING_NOT_AUTHORIZED
    assert "authorization packet signed" in OWNER_AUTHORIZATION_DECISION_RECORDING_NOT_AUTHORIZED
    assert "authorization decision recorded" in OWNER_AUTHORIZATION_DECISION_RECORDING_NOT_AUTHORIZED
    assert "decision receipt emitted" in OWNER_AUTHORIZATION_DECISION_RECORDING_NOT_AUTHORIZED
    assert "controlled-run gate opening" in OWNER_AUTHORIZATION_DECISION_RECORDING_NOT_AUTHORIZED
    assert "controlled run authorization" in OWNER_AUTHORIZATION_DECISION_RECORDING_NOT_AUTHORIZED
    assert "owner walkthrough acceptance" in OWNER_AUTHORIZATION_DECISION_RECORDING_NOT_AUTHORIZED
    assert "Tower return/session continuity repair" in OWNER_AUTHORIZATION_DECISION_RECORDING_NOT_AUTHORIZED
    assert "Render redeploy" in OWNER_AUTHORIZATION_DECISION_RECORDING_NOT_AUTHORIZED
    assert "broker submission" in OWNER_AUTHORIZATION_DECISION_RECORDING_NOT_AUTHORIZED
    assert "real capital movement" in OWNER_AUTHORIZATION_DECISION_RECORDING_NOT_AUTHORIZED
    assert "Live Auto unlock" in OWNER_AUTHORIZATION_DECISION_RECORDING_NOT_AUTHORIZED

    handoff = build_owner_authorization_decision_recording_gate_handoff()

    assert handoff["package"] == "ob_owner_authorization_decision_recording_gate_gp014"
    assert handoff["gate_prepared"] is True
    assert handoff["source_dependency"] == "GP013"
    assert handoff["gate_state"] == "closed_pending_future_owner_decision_recording"
    assert len(handoff["decision_candidate_values"]) == 3
    assert len(handoff["room_scope"]) == 6
    assert "Do not record an owner authorization decision from this package." in handoff["next_builder_notes"]
    assert "Do not sign the authorization packet from this package." in handoff["next_builder_notes"]
    assert "Do not emit a decision receipt from this package." in handoff["next_builder_notes"]
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
