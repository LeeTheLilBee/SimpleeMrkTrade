from copy import deepcopy

from .owner_walkthrough_controlled_run_gate import (
    build_owner_walkthrough_controlled_run_gate_bundle,
)
from .six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER
from .ui_surface_registry import (
    MUST_NOT_CLAIM,
    PROTECTED_ROUTE_POLICY,
    build_real_surface_adapter_contract,
)

OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_IDENTITY = {
    "package": "ob_owner_walkthrough_authorization_packet_gp013",
    "display_title": "Owner Walkthrough Authorization Packet",
    "decision": "READY_FOR_OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_WITH_SAFETY_LOCKS_HELD",
    "plain_language": (
        "The controlled owner walkthrough now has an authorization packet prepared. "
        "This package records walkthrough now has an authorization packet prepared. "
        "This package records what the owner must approve later, but it does not "
        "grant authorization, open the controlled-run gate, start the walkthrough, "
        "accept the walkthrough, repair Tower return, redeploy Render, claim staging "
        "readiness, or unlock dangerous actions."
    ),
}

OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_DECISION_OPTIONS = [
    {
        "decision": "AUTHORIZE_CONTROLLED_RUN",
        "available_now": False,
        "reason": "Requires future explicit owner authorization with Tower owner session and step-up.",
    },
    {
        "decision": "HOLD_CONTROLLED_RUN",
        "available_now": True,
        "reason": "Safe default while authorization is not granted.",
    },
    {
        "decision": "REQUEST_MORE_PREP",
        "available_now": True,
        "reason": "Owner may request more preparation before any controlled run.",
    },
]

OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_REQUIRED_FIELDS = [
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
]

OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_REQUIRED_ACKS = [
    "This packet does not authorize the controlled run.",
    "The controlled-run gate remains closed.",
    "Owner walkthrough has not started.",
    "Owner walkthrough has not been accepted.",
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

OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_REQUIRED_FALSE_FLAGS = [
    "owner_authorization_granted",
    "authorization_packet_signed",
    "authorization_decision_recorded",
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

OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_REQUIRED_TRUE_FLAGS = [
    "gp012_gate_prepared",
    "gp012_gate_closed",
    "authorization_packet_prepared",
    "owner_identity_required",
    "tower_owner_session_required",
    "step_up_required",
    "explicit_owner_authorization_required",
    "owner_session_required",
    "live_auto_locked",
]

OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_NOT_AUTHORIZED = [
    "STAGING_READY",
    "owner authorization granted",
    "authorization packet signed",
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


def build_owner_walkthrough_authorization_packet_requirements():
    gate = build_owner_walkthrough_controlled_run_gate_bundle()
    requirements = []

    for item in gate["authorization_requirements"]:
        requirements.append(
            {
                "key": item["key"],
                "label": item["label"],
                "required": item["required"],
                "satisfied_now": False,
                "source": "GP012 controlled-run gate",
            }
        )

    return requirements


def build_owner_walkthrough_authorization_packet_room_scope():
    gate = build_owner_walkthrough_controlled_run_gate_bundle()
    scope = []

    for item in gate["room_gate_matrix"]:
        scope.append(
            {
                "room": item["room"],
                "step": item["step"],
                "display_title": item["display_title"],
                "route_hint": item["route_hint"],
                "component_hint": item["component_hint"],
                "data_adapter_hint": item["data_adapter_hint"],
                "included_in_future_authorization_scope": True,
                "eligible_for_future_controlled_run": item["eligible_for_future_controlled_run"],
                "controlled_run_started": False,
                "controlled_run_completed": False,
                "owner_acceptance_recorded": False,
                "live_route_opened": False,
                "gate_state": item["gate_state"],
            }
        )

    return scope


def build_owner_walkthrough_authorization_packet_status():
    gate = build_owner_walkthrough_controlled_run_gate_bundle()
    requirements = build_owner_walkthrough_authorization_packet_requirements()
    room_scope = build_owner_walkthrough_authorization_packet_room_scope()

    all_rooms_scoped = (
        len(room_scope) == 6
        and [item["room"] for item in room_scope] == list(SIX_ROOM_REAL_SURFACE_ORDER)
        and all(item["included_in_future_authorization_scope"] is True for item in room_scope)
    )

    requirements_registered = all(
        item["required"] is True and item["satisfied_now"] is False
        for item in requirements
    )

    return {
        "gp012_gate_prepared": gate["prepared"] is True,
        "gp012_gate_closed": gate["gate_state"] == "closed_pending_explicit_owner_authorization",
        "authorization_packet_prepared": True,
        "authorization_requirements_registered": requirements_registered,
        "all_six_rooms_scoped": all_rooms_scoped,
        "owner_identity_required": True,
        "tower_owner_session_required": True,
        "step_up_required": True,
        "explicit_owner_authorization_required": True,
        "owner_authorization_granted": False,
        "authorization_packet_signed": False,
        "authorization_decision_recorded": False,
        "bounded_walkthrough_window_named": False,
        "evidence_capture_plan_active": False,
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


def build_owner_walkthrough_authorization_packet_bundle():
    gate = build_owner_walkthrough_controlled_run_gate_bundle()
    requirements = build_owner_walkthrough_authorization_packet_requirements()
    room_scope = build_owner_walkthrough_authorization_packet_room_scope()
    status = build_owner_walkthrough_authorization_packet_status()
    adapter = build_real_surface_adapter_contract()

    false_flags_ok = all(
        status.get(key) is False
        for key in OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_REQUIRED_FALSE_FLAGS
    )

    true_flags_ok = all(
        status.get(key) is True
        for key in OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_REQUIRED_TRUE_FLAGS
    )

    decision_options_ready = (
        len(OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_DECISION_OPTIONS) == 3
        and OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_DECISION_OPTIONS[0]["available_now"] is False
        and OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_DECISION_OPTIONS[1]["available_now"] is True
        and OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_DECISION_OPTIONS[2]["available_now"] is True
    )

    requirements_ready = all(
        item["required"] is True and item["satisfied_now"] is False
        for item in requirements
    )

    packet_prepared = all(
        [
            gate["prepared"] is True,
            status["gp012_gate_closed"] is True,
            status["authorization_packet_prepared"] is True,
            status["authorization_requirements_registered"] is True,
            status["all_six_rooms_scoped"] is True,
            requirements_ready,
            decision_options_ready,
            false_flags_ok,
            true_flags_ok,
            "STAGING_READY" in MUST_NOT_CLAIM,
        ]
    )

    return {
        "package": OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_IDENTITY["package"],
        "display_title": OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_IDENTITY["display_title"],
        "decision": OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_IDENTITY["decision"],
        "packet_prepared": packet_prepared,
        "source_dependency": "GP012",
        "gate_state": "closed_pending_explicit_owner_authorization",
        "decision_options": deepcopy(OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_DECISION_OPTIONS),
        "required_fields": list(OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_REQUIRED_FIELDS),
        "required_acknowledgements": list(OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_REQUIRED_ACKS),
        "authorization_requirements": requirements,
        "room_scope": room_scope,
        "authorization_status": status,
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(OWNER_WALKTHROUGH_AUTHORIZATION_PACKET_NOT_AUTHORIZED),
        "release_boundary": {
            "owner_authorization_granted": False,
            "authorization_packet_signed": False,
            "authorization_decision_recorded": False,
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
        "next_build": "OB owner authorization decision recording gate / GP014",
    }


def build_owner_walkthrough_authorization_packet_handoff():
    bundle = build_owner_walkthrough_authorization_packet_bundle()

    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "packet_prepared": bundle["packet_prepared"],
        "source_dependency": bundle["source_dependency"],
        "gate_state": bundle["gate_state"],
        "decision_options": bundle["decision_options"],
        "required_fields": bundle["required_fields"],
        "required_acknowledgements": bundle["required_acknowledgements"],
        "authorization_requirements": bundle["authorization_requirements"],
        "room_scope": bundle["room_scope"],
        "authorization_status": bundle["authorization_status"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "takeover_summary": (
            "GP013 prepares the owner walkthrough authorization packet after GP012. "
            "The packet lists required fields, owner acknowledgements, decision "
            "options, authorization requirements, and six-room scope. It does not "
            "grant authorization, open the controlled-run gate, start or accept the "
            "walkthrough, repair Tower return, redeploy Render, claim staging "
            "readiness, or unlock dangerous actions."
        ),
        "next_builder_notes": [
            "Treat this as authorization packet preparation only.",
            "Do not grant owner authorization from this package.",
            "Do not sign or record an authorization decision from this package.",
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
            "Next build is GP014 owner authorization decision recording gate.",
        ],
    }
