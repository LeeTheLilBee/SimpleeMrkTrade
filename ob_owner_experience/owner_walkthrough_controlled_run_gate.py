from copy import deepcopy

from .owner_walkthrough_dry_run_evidence import (
    build_owner_walkthrough_dry_run_evidence_bundle,
)
from .route_owner_walkthrough_preparation import (
    build_route_owner_walkthrough_preparation_bundle,
)
from .six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER
from .ui_surface_registry import (
    MUST_NOT_CLAIM,
    PROTECTED_ROUTE_POLICY,
    build_real_surface_adapter_contract,
)

OWNER_WALKTHROUGH_CONTROLLED_RUN_GATE_IDENTITY = {
    "package": "ob_owner_walkthrough_controlled_run_gate_gp012",
    "display_title": "Owner Walkthrough Controlled Run Gate",
    "decision": "READY_FOR_OWNER_WALKTHROUGH_CONTROLLED_RUN_GATE_WITH_SAFETY_LOCKS_HELD",
    "plain_language": (
        "The owner walkthrough controlled-run gate is prepared after GP011 dry-run "
        "evidence. The gate remains closed until a later explicit owner authorization "
        "package. This package does not start the walkthrough, accept the walkthrough, "
        "repair Tower return, redeploy Render, claim staging readiness, or unlock "
        "dangerous actions."
    ),
}

OWNER_WALKTHROUGH_CONTROLLED_RUN_GATE_REQUIRED_INPUTS = [
    "gp010_route_preparation_ready",
    "gp011_dry_run_evidence_ready",
    "six_room_order_present",
    "owner_identity_required",
    "tower_owner_session_required",
    "step_up_required",
    "explicit_owner_authorization_required",
    "controlled_run_scope_locked",
    "dangerous_actions_locked",
    "staging_ready_not_claimed",
]

OWNER_WALKTHROUGH_CONTROLLED_RUN_AUTHORIZATION_REQUIREMENTS = [
    {
        "key": "owner_identity",
        "label": "Owner identity must be verified",
        "required": True,
        "satisfied_now": False,
    },
    {
        "key": "tower_owner_session",
        "label": "Tower owner session must be active",
        "required": True,
        "satisfied_now": False,
    },
    {
        "key": "step_up",
        "label": "Step-up authentication must be completed",
        "required": True,
        "satisfied_now": False,
    },
    {
        "key": "explicit_owner_authorization",
        "label": "Owner must explicitly authorize controlled run",
        "required": True,
        "satisfied_now": False,
    },
    {
        "key": "walkthrough_window",
        "label": "Controlled run window must be named and bounded",
        "required": True,
        "satisfied_now": False,
    },
    {
        "key": "evidence_capture",
        "label": "Evidence capture plan must be active",
        "required": True,
        "satisfied_now": False,
    },
]

OWNER_WALKTHROUGH_CONTROLLED_RUN_SCOPE = {
    "source_dependency": "GP011",
    "gate_type": "authorization_gate_only",
    "controlled_run_gate_prepared": True,
    "controlled_run_gate_open": False,
    "controlled_run_authorized": False,
    "controlled_run_started": False,
    "controlled_run_completed": False,
    "owner_walkthrough_accepted": False,
    "live_route_opened": False,
    "tower_return_repaired": False,
    "render_redeployed": False,
    "staging_ready": False,
}

OWNER_WALKTHROUGH_CONTROLLED_RUN_REQUIRED_FALSE_FLAGS = [
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

OWNER_WALKTHROUGH_CONTROLLED_RUN_REQUIRED_TRUE_FLAGS = [
    "gp010_route_preparation_ready",
    "gp011_dry_run_evidence_ready",
    "controlled_run_gate_prepared",
    "controlled_run_gate_closed",
    "owner_identity_required",
    "tower_owner_session_required",
    "step_up_required",
    "explicit_owner_authorization_required",
    "owner_session_required",
    "live_auto_locked",
]

OWNER_WALKTHROUGH_CONTROLLED_RUN_NOT_AUTHORIZED = [
    "STAGING_READY",
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


def build_owner_walkthrough_controlled_run_authorization_requirements():
    return deepcopy(OWNER_WALKTHROUGH_CONTROLLED_RUN_AUTHORIZATION_REQUIREMENTS)


def build_owner_walkthrough_controlled_run_room_gate_matrix():
    dry_run = build_owner_walkthrough_dry_run_evidence_bundle()
    matrix = []

    for record in dry_run["dry_run_evidence_matrix"]:
        room = record["room"]
        matrix.append(
            {
                "room": room,
                "step": record["step"],
                "display_title": record["display_title"],
                "route_hint": record["route_hint"],
                "component_hint": record["component_hint"],
                "data_adapter_hint": record["data_adapter_hint"],
                "dry_run_evidence_ready": record["evidence_ready"] is True,
                "eligible_for_future_controlled_run": record["evidence_ready"] is True,
                "controlled_run_started": False,
                "controlled_run_completed": False,
                "owner_acceptance_recorded": False,
                "live_route_opened": False,
                "gate_state": "closed_pending_explicit_owner_authorization",
            }
        )

    return matrix


def build_owner_walkthrough_controlled_run_gate_status():
    prep = build_route_owner_walkthrough_preparation_bundle()
    dry_run = build_owner_walkthrough_dry_run_evidence_bundle()
    matrix = build_owner_walkthrough_controlled_run_room_gate_matrix()

    all_rooms_ready = (
        len(matrix) == 6
        and [item["room"] for item in matrix] == list(SIX_ROOM_REAL_SURFACE_ORDER)
        and all(item["eligible_for_future_controlled_run"] is True for item in matrix)
    )

    return {
        "gp010_route_preparation_ready": prep["prepared"] is True,
        "gp011_dry_run_evidence_ready": dry_run["ready"] is True,
        "all_six_rooms_present": all_rooms_ready,
        "all_room_gates_prepared": all_rooms_ready,
        "controlled_run_gate_prepared": True,
        "controlled_run_gate_open": False,
        "controlled_run_gate_closed": True,
        "controlled_run_authorized": False,
        "controlled_run_started": False,
        "controlled_run_completed": False,
        "owner_walkthrough_started": False,
        "owner_walkthrough_accepted": False,
        "live_route_opened": False,
        "owner_identity_required": True,
        "tower_owner_session_required": True,
        "step_up_required": True,
        "explicit_owner_authorization_required": True,
        "owner_authorization_present": False,
        "walkthrough_window_bound": False,
        "evidence_capture_started": False,
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


def build_owner_walkthrough_controlled_run_gate_bundle():
    status = build_owner_walkthrough_controlled_run_gate_status()
    matrix = build_owner_walkthrough_controlled_run_room_gate_matrix()
    requirements = build_owner_walkthrough_controlled_run_authorization_requirements()
    adapter = build_real_surface_adapter_contract()

    false_flags_ok = all(
        status.get(key) is False
        for key in OWNER_WALKTHROUGH_CONTROLLED_RUN_REQUIRED_FALSE_FLAGS
    )

    true_flags_ok = all(
        status.get(key) is True
        for key in OWNER_WALKTHROUGH_CONTROLLED_RUN_REQUIRED_TRUE_FLAGS
    )

    requirements_registered = all(
        item["required"] is True and item["satisfied_now"] is False
        for item in requirements
    )

    prepared = all(
        [
            status["gp010_route_preparation_ready"] is True,
            status["gp011_dry_run_evidence_ready"] is True,
            status["all_room_gates_prepared"] is True,
            status["controlled_run_gate_prepared"] is True,
            status["controlled_run_gate_closed"] is True,
            requirements_registered,
            false_flags_ok,
            true_flags_ok,
            "STAGING_READY" in MUST_NOT_CLAIM,
        ]
    )

    return {
        "package": OWNER_WALKTHROUGH_CONTROLLED_RUN_GATE_IDENTITY["package"],
        "display_title": OWNER_WALKTHROUGH_CONTROLLED_RUN_GATE_IDENTITY["display_title"],
        "decision": OWNER_WALKTHROUGH_CONTROLLED_RUN_GATE_IDENTITY["decision"],
        "prepared": prepared,
        "source_dependency": "GP011",
        "gate_state": "closed_pending_explicit_owner_authorization",
        "controlled_run_scope": deepcopy(OWNER_WALKTHROUGH_CONTROLLED_RUN_SCOPE),
        "required_inputs": list(OWNER_WALKTHROUGH_CONTROLLED_RUN_GATE_REQUIRED_INPUTS),
        "authorization_requirements": requirements,
        "room_gate_matrix": matrix,
        "gate_status": status,
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(OWNER_WALKTHROUGH_CONTROLLED_RUN_NOT_AUTHORIZED),
        "release_boundary": {
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
        "next_build": "OB owner walkthrough authorization packet / GP013",
    }


def build_owner_walkthrough_controlled_run_gate_handoff():
    bundle = build_owner_walkthrough_controlled_run_gate_bundle()

    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "prepared": bundle["prepared"],
        "source_dependency": bundle["source_dependency"],
        "gate_state": bundle["gate_state"],
        "controlled_run_scope": bundle["controlled_run_scope"],
        "required_inputs": bundle["required_inputs"],
        "authorization_requirements": bundle["authorization_requirements"],
        "room_gate_matrix": bundle["room_gate_matrix"],
        "gate_status": bundle["gate_status"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "takeover_summary": (
            "GP012 prepares the owner walkthrough controlled-run gate after GP011 "
            "dry-run evidence. The gate remains closed pending explicit owner "
            "authorization, Tower owner session, step-up, bounded run window, and "
            "evidence capture. It does not start or accept the walkthrough."
        ),
        "next_builder_notes": [
            "Treat this as the controlled-run gate only.",
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
            "Next build is GP013 owner walkthrough authorization packet.",
        ],
    }
