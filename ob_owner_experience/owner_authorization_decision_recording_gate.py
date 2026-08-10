from copy import deepcopy
from functools import lru_cache

from .owner_walkthrough_authorization_packet import (
    build_owner_walkthrough_authorization_packet_bundle,
)
from .six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER
from .ui_surface_registry import (
    MUST_NOT_CLAIM,
    PROTECTED_ROUTE_POLICY,
    build_real_surface_adapter_contract,
)

OWNER_AUTHORIZATION_DECISION_RECORDING_GATE_IDENTITY = {
    "package": "ob_owner_authorization_decision_recording_gate_gp014",
    "display_title": "Owner Authorization Decision Recording Gate",
    "decision": "READY_FOR_OWNER_AUTHORIZATION_DECISION_RECORDING_GATE_WITH_SAFETY_LOCKS_HELD",
    "plain_language": (
        "The owner authorization decision recording gate is prepared after GP013. "
        "This package defines how a future owner authorization decision may be "
        "recorded, but it does not record a decision, sign the packet, open the "
        "controlled-run gate, authorize the controlled run, start or accept the "
        "walkthrough, repair Tower return, redeploy Render, claim staging readiness, "
        "or unlock dangerous actions."
    ),
}

OWNER_AUTHORIZATION_DECISION_RECORDING_GATE_REQUIRED_INPUTS = [
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
]

OWNER_AUTHORIZATION_DECISION_RECORDING_ALLOWED_DECISION_VALUES = [
    "AUTHORIZE_CONTROLLED_RUN",
    "HOLD_CONTROLLED_RUN",
    "REQUEST_MORE_PREP",
]

OWNER_AUTHORIZATION_DECISION_RECORDING_DEFAULT_DECISION = "HOLD_CONTROLLED_RUN"

OWNER_AUTHORIZATION_DECISION_RECORDING_SCHEMA = {
    "record_type": "owner_walkthrough_authorization_decision",
    "required_fields": [
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
    ],
    "allowed_decision_values": list(OWNER_AUTHORIZATION_DECISION_RECORDING_ALLOWED_DECISION_VALUES),
    "default_decision": OWNER_AUTHORIZATION_DECISION_RECORDING_DEFAULT_DECISION,
    "append_only": True,
    "redaction_required": True,
    "secret_values_forbidden": True,
    "broker_payload_forbidden": True,
    "money_movement_forbidden": True,
}

OWNER_AUTHORIZATION_DECISION_RECORDING_REQUIRED_ACKS = [
    "This gate does not record authorization.",
    "No authorization decision is recorded in this package.",
    "The authorization packet is not signed in this package.",
    "The controlled-run gate remains closed.",
    "The controlled run is not authorized in this package.",
    "The owner walkthrough has not started.",
    "The owner walkthrough has not been accepted.",
    "Tower return/session continuity has not been repaired.",
    "Render has not been redeployed.",
    "STAGING_READY is not claimed.",
    "Broker submission remains locked.",
    "Real capital movement remains locked.",
    "Direct execution remains disabled.",
    "Automated execution remains disabled.",
    "Permission mutations remain disabled.",
    "Secret reveal remains disabled.",
    "Live Auto remains locked.",
]

OWNER_AUTHORIZATION_DECISION_RECORDING_REQUIRED_FALSE_FLAGS = [
    "owner_authorization_granted",
    "authorization_packet_signed",
    "authorization_decision_recorded",
    "decision_recording_enabled",
    "decision_receipt_emitted",
    "controlled_run_gate_open",
    "controlled_run_authorized",
    "controlled_run_started",
    "controlled_run_completed",
    "owner_walkthrough_started",
    "owner_walkthrough_accepted",
    "live_route_opened",
    "tower_return_repaired",
    "render_redeployed",
    "production_deploy_enabled",
    "broker_submission_enabled",
    "real_capital_movement_enabled",
    "direct_execution_enabled",
    "automated_execution_enabled",
    "permission_mutation_enabled",
    "secret_reveal_enabled",
    "staging_ready",
]

OWNER_AUTHORIZATION_DECISION_RECORDING_REQUIRED_TRUE_FLAGS = [
    "gp013_authorization_packet_prepared",
    "gp013_gate_state_closed",
    "decision_recording_gate_prepared",
    "decision_recording_gate_closed",
    "decision_record_schema_prepared",
    "append_only_receipt_required",
    "owner_identity_required",
    "tower_owner_session_required",
    "step_up_required",
    "explicit_owner_authorization_required",
    "owner_session_required",
    "live_auto_locked",
]

OWNER_AUTHORIZATION_DECISION_RECORDING_NOT_AUTHORIZED = [
    "STAGING_READY",
    "owner authorization granted",
    "authorization packet signed",
    "authorization decision recorded",
    "decision receipt emitted",
    "controlled-run gate opening",
    "controlled run authorization",
    "controlled run start",
    "controlled run completion",
    "owner walkthrough start",
    "owner walkthrough acceptance",
    "Tower return/session continuity repair",
    "Render redeploy",
    "production deployment",
    "broker submission",
    "real capital movement",
    "direct execution",
    "automated execution",
    "permission mutation",
    "secret reveal",
    "Live Auto unlock",
]


@lru_cache(maxsize=1)
def _gp013_packet():
    return build_owner_walkthrough_authorization_packet_bundle()


@lru_cache(maxsize=1)
def _adapter_contract():
    return build_real_surface_adapter_contract()


@lru_cache(maxsize=1)
def _schema_cached():
    return deepcopy(OWNER_AUTHORIZATION_DECISION_RECORDING_SCHEMA)


@lru_cache(maxsize=1)
def _candidate_values_cached():
    packet = _gp013_packet()
    packet_options = {
        item["decision"]: item["available_now"]
        for item in packet["decision_options"]
    }

    values = []
    for value in OWNER_AUTHORIZATION_DECISION_RECORDING_ALLOWED_DECISION_VALUES:
        values.append(
            {
                "decision_value": value,
                "registered": True,
                "available_in_gp013_packet": value in packet_options,
                "available_now": False,
                "recording_allowed_now": False,
                "reason": (
                    "Decision value is registered for a future package, but GP014 "
                    "does not record authorization decisions."
                ),
            }
        )
    return values


@lru_cache(maxsize=1)
def _room_scope_cached():
    packet = _gp013_packet()
    scope = []

    for item in packet["room_scope"]:
        scope.append(
            {
                "room": item["room"],
                "step": item["step"],
                "display_title": item["display_title"],
                "route_hint": item["route_hint"],
                "component_hint": item["component_hint"],
                "data_adapter_hint": item["data_adapter_hint"],
                "included_in_decision_scope": True,
                "eligible_for_future_controlled_run": item["eligible_for_future_controlled_run"],
                "controlled_run_started": False,
                "controlled_run_completed": False,
                "owner_acceptance_recorded": False,
                "live_route_opened": False,
                "gate_state": item["gate_state"],
            }
        )

    return scope


@lru_cache(maxsize=1)
def _status_cached():
    packet = _gp013_packet()
    schema = _schema_cached()
    values = _candidate_values_cached()
    room_scope = _room_scope_cached()

    all_rooms_scoped = (
        len(room_scope) == 6
        and [item["room"] for item in room_scope] == list(SIX_ROOM_REAL_SURFACE_ORDER)
        and all(item["included_in_decision_scope"] is True for item in room_scope)
    )

    values_registered = (
        len(values) == 3
        and all(item["registered"] is True for item in values)
        and all(item["recording_allowed_now"] is False for item in values)
    )

    schema_ready = (
        schema["record_type"] == "owner_walkthrough_authorization_decision"
        and schema["append_only"] is True
        and schema["redaction_required"] is True
        and schema["secret_values_forbidden"] is True
        and schema["broker_payload_forbidden"] is True
        and schema["money_movement_forbidden"] is True
    )

    return {
        "gp013_authorization_packet_prepared": packet["packet_prepared"] is True,
        "gp013_gate_state_closed": packet["gate_state"] == "closed_pending_explicit_owner_authorization",
        "decision_recording_gate_prepared": True,
        "decision_recording_gate_closed": True,
        "decision_record_schema_prepared": schema_ready,
        "decision_values_registered": values_registered,
        "all_six_rooms_scoped": all_rooms_scoped,
        "append_only_receipt_required": True,
        "owner_identity_required": True,
        "tower_owner_session_required": True,
        "step_up_required": True,
        "explicit_owner_authorization_required": True,
        "owner_authorization_granted": False,
        "authorization_packet_signed": False,
        "authorization_decision_recorded": False,
        "decision_recording_enabled": False,
        "decision_receipt_emitted": False,
        "controlled_run_gate_open": False,
        "controlled_run_authorized": False,
        "controlled_run_started": False,
        "controlled_run_completed": False,
        "owner_walkthrough_started": False,
        "owner_walkthrough_accepted": False,
        "live_route_opened": False,
        "tower_return_repaired": False,
        "render_redeployed": False,
        "production_deploy_enabled": False,
        "broker_submission_enabled": False,
        "real_capital_movement_enabled": False,
        "direct_execution_enabled": False,
        "automated_execution_enabled": False,
        "permission_mutation_enabled": False,
        "secret_reveal_enabled": False,
        "anonymous_access_allowed": False,
        "owner_session_required": True,
        "staging_ready": False,
        "live_auto_locked": True,
    }


def build_owner_authorization_decision_recording_schema():
    return deepcopy(_schema_cached())


def build_owner_authorization_decision_recording_acknowledgements():
    return list(OWNER_AUTHORIZATION_DECISION_RECORDING_REQUIRED_ACKS)


def build_owner_authorization_decision_recording_candidate_values():
    return deepcopy(_candidate_values_cached())


def build_owner_authorization_decision_recording_room_scope():
    return deepcopy(_room_scope_cached())


def build_owner_authorization_decision_recording_gate_status():
    return deepcopy(_status_cached())


def build_owner_authorization_decision_recording_gate_bundle():
    packet = _gp013_packet()
    schema = _schema_cached()
    values = _candidate_values_cached()
    room_scope = _room_scope_cached()
    acknowledgements = build_owner_authorization_decision_recording_acknowledgements()
    status = _status_cached()
    adapter = _adapter_contract()

    false_flags_ok = all(
        status.get(key) is False
        for key in OWNER_AUTHORIZATION_DECISION_RECORDING_REQUIRED_FALSE_FLAGS
    )

    true_flags_ok = all(
        status.get(key) is True
        for key in OWNER_AUTHORIZATION_DECISION_RECORDING_REQUIRED_TRUE_FLAGS
    )

    gate_prepared = all(
        [
            packet["packet_prepared"] is True,
            packet["gate_state"] == "closed_pending_explicit_owner_authorization",
            status["decision_recording_gate_prepared"] is True,
            status["decision_recording_gate_closed"] is True,
            status["decision_record_schema_prepared"] is True,
            status["decision_values_registered"] is True,
            status["all_six_rooms_scoped"] is True,
            len(acknowledgements) >= 10,
            false_flags_ok,
            true_flags_ok,
            "STAGING_READY" in MUST_NOT_CLAIM,
        ]
    )

    return {
        "package": OWNER_AUTHORIZATION_DECISION_RECORDING_GATE_IDENTITY["package"],
        "display_title": OWNER_AUTHORIZATION_DECISION_RECORDING_GATE_IDENTITY["display_title"],
        "decision": OWNER_AUTHORIZATION_DECISION_RECORDING_GATE_IDENTITY["decision"],
        "gate_prepared": gate_prepared,
        "source_dependency": "GP013",
        "gate_state": "closed_pending_future_owner_decision_recording",
        "required_inputs": list(OWNER_AUTHORIZATION_DECISION_RECORDING_GATE_REQUIRED_INPUTS),
        "decision_record_schema": deepcopy(schema),
        "decision_candidate_values": deepcopy(values),
        "required_acknowledgements": acknowledgements,
        "room_scope": deepcopy(room_scope),
        "recording_status": deepcopy(status),
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(OWNER_AUTHORIZATION_DECISION_RECORDING_NOT_AUTHORIZED),
        "release_boundary": {
            "owner_authorization_granted": False,
            "authorization_packet_signed": False,
            "authorization_decision_recorded": False,
            "decision_recording_enabled": False,
            "decision_receipt_emitted": False,
            "controlled_run_gate_open": False,
            "controlled_run_authorized": False,
            "controlled_run_started": False,
            "controlled_run_completed": False,
            "owner_walkthrough_started": False,
            "owner_walkthrough_accepted": False,
            "live_route_opened": False,
            "tower_return_repaired": False,
            "render_redeployed": False,
            "production_deploy_enabled": False,
            "broker_submission_enabled": False,
            "real_capital_movement_enabled": False,
            "direct_execution_enabled": False,
            "automated_execution_enabled": False,
            "permission_mutation_enabled": False,
            "secret_reveal_enabled": False,
            "staging_ready": False,
            "live_auto_locked": True,
        },
        "next_build": "OB owner authorization receipt draft / GP015",
    }


def build_owner_authorization_decision_recording_gate_handoff():
    bundle = build_owner_authorization_decision_recording_gate_bundle()

    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "gate_prepared": bundle["gate_prepared"],
        "source_dependency": bundle["source_dependency"],
        "gate_state": bundle["gate_state"],
        "required_inputs": bundle["required_inputs"],
        "decision_record_schema": bundle["decision_record_schema"],
        "decision_candidate_values": bundle["decision_candidate_values"],
        "required_acknowledgements": bundle["required_acknowledgements"],
        "room_scope": bundle["room_scope"],
        "recording_status": bundle["recording_status"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "takeover_summary": (
            "GP014 prepares the owner authorization decision recording gate after "
            "GP013. The gate defines a future append-only decision record schema, "
            "candidate values, acknowledgement requirements, and six-room scope. "
            "It does not record a decision, sign the authorization packet, open the "
            "controlled-run gate, authorize the run, start or accept the walkthrough, "
            "repair Tower return, redeploy Render, claim staging readiness, or unlock "
            "dangerous actions."
        ),
        "next_builder_notes": [
            "Treat this as decision recording gate preparation only.",
            "Do not record an owner authorization decision from this package.",
            "Do not sign the authorization packet from this package.",
            "Do not emit a decision receipt from this package.",
            "Do not open the controlled-run gate from this package.",
            "Do not authorize the controlled run from this package.",
            "Do not start the owner walkthrough from this package.",
            "Do not mark owner walkthrough accepted from this package.",
            "Do not open live routes as evidence from this package.",
            "Do not claim Tower return/session continuity repaired from this package.",
            "Do not redeploy Render from this package.",
            "Do not claim STAGING_READY.",
            "Keep production deploy disabled.",
            "Keep broker submission locked.",
            "Keep real capital movement locked.",
            "Keep direct execution disabled.",
            "Keep automated execution disabled.",
            "Keep permission mutations disabled.",
            "Keep secret reveal disabled.",
            "Keep Live Auto locked.",
            "Next build is GP015 owner authorization receipt draft.",
        ],
    }
