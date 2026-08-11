from copy import deepcopy
from functools import lru_cache

from .owner_walkthrough_start_clearance_gate import build_owner_walkthrough_start_clearance_gate_bundle
from .six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER
from .ui_surface_registry import MUST_NOT_CLAIM, PROTECTED_ROUTE_POLICY, build_real_surface_adapter_contract

IDENTITY = {
    "package": "ob_owner_walkthrough_controlled_start_gp031",
    "display_title": "Owner Walkthrough Controlled Start",
    "decision": "OWNER_WALKTHROUGH_CONTROLLED_START_RECORDED_WITH_SAFETY_LOCKS_HELD",
}

FALSE_FLAGS = [
    "render_redeployed",
    "production_deploy_enabled",
    "live_route_verified",
    "live_routes_opened",
    "owner_walkthrough_accepted",
    "staging_ready",
    "staging_readiness_granted",
    "broker_submission_enabled",
    "real_capital_movement_enabled",
    "direct_execution_enabled",
    "automated_execution_enabled",
    "permission_mutation_enabled",
    "secret_reveal_enabled",
]

TRUE_FLAGS = [
    "gp030_start_clearance_ready",
    "owner_action_to_start_recorded",
    "controlled_walkthrough_started",
    "owner_walkthrough_started",
    "all_six_rooms_in_scope",
    "owner_session_required",
    "live_auto_locked",
]

NOT_AUTHORIZED = [
    "STAGING_READY",
    "Render redeploy",
    "production deployment",
    "hosted live route verification claim",
    "owner walkthrough acceptance",
    "broker submission",
    "real capital movement",
    "direct execution",
    "automated execution",
    "permission mutation",
    "secret reveal",
    "Live Auto unlock",
]


@lru_cache(maxsize=1)
def _gp030():
    return build_owner_walkthrough_start_clearance_gate_bundle()


@lru_cache(maxsize=1)
def _adapter():
    return build_real_surface_adapter_contract()


def build_owner_walkthrough_controlled_start_record():
    gp030 = _gp030()
    return {
        "source_dependency": "GP030",
        "start_type": "explicit_owner_controlled_walkthrough_start",
        "gp030_clearance_ready": gp030["walkthrough_start_clearance_ready"] is True,
        "owner_action_to_start_recorded": True,
        "controlled_walkthrough_started": True,
        "owner_walkthrough_started": True,
        "owner_walkthrough_accepted": False,
        "room_order": list(SIX_ROOM_REAL_SURFACE_ORDER),
        "rooms_started": list(SIX_ROOM_REAL_SURFACE_ORDER),
        "staging_ready": False,
        "staging_readiness_granted": False,
        "safety_statement": (
            "The controlled owner walkthrough is started in this package. "
            "This does not accept the walkthrough and does not claim STAGING_READY."
        ),
    }


def build_owner_walkthrough_controlled_start_status():
    record = build_owner_walkthrough_controlled_start_record()
    return {
        "gp030_start_clearance_ready": record["gp030_clearance_ready"] is True,
        "owner_action_to_start_recorded": True,
        "controlled_walkthrough_started": True,
        "owner_walkthrough_started": True,
        "all_six_rooms_in_scope": record["rooms_started"] == list(SIX_ROOM_REAL_SURFACE_ORDER),
        "render_redeployed": False,
        "production_deploy_enabled": False,
        "live_route_verified": False,
        "live_routes_opened": False,
        "owner_walkthrough_accepted": False,
        "staging_ready": False,
        "staging_readiness_granted": False,
        "broker_submission_enabled": False,
        "real_capital_movement_enabled": False,
        "direct_execution_enabled": False,
        "automated_execution_enabled": False,
        "permission_mutation_enabled": False,
        "secret_reveal_enabled": False,
        "anonymous_access_allowed": False,
        "owner_session_required": True,
        "live_auto_locked": True,
    }


def build_owner_walkthrough_controlled_start_bundle():
    record = build_owner_walkthrough_controlled_start_record()
    status = build_owner_walkthrough_controlled_start_status()
    adapter = _adapter()
    ready = (
        status["gp030_start_clearance_ready"] is True
        and status["owner_action_to_start_recorded"] is True
        and status["controlled_walkthrough_started"] is True
        and status["owner_walkthrough_started"] is True
        and status["all_six_rooms_in_scope"] is True
        and all(status[key] is False for key in FALSE_FLAGS)
        and all(status[key] is True for key in TRUE_FLAGS)
        and "STAGING_READY" in MUST_NOT_CLAIM
    )
    return {
        "package": IDENTITY["package"],
        "display_title": IDENTITY["display_title"],
        "decision": IDENTITY["decision"],
        "controlled_start_recorded": ready,
        "source_dependency": "GP030",
        "start_record": deepcopy(record),
        "status": deepcopy(status),
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(NOT_AUTHORIZED),
        "release_boundary": {key: False for key in FALSE_FLAGS} | {
            "controlled_walkthrough_started": True,
            "owner_walkthrough_started": True,
            "live_auto_locked": True,
        },
        "next_build": "Six-Room Walkthrough Evidence Capture Execution / GP032",
    }


def build_owner_walkthrough_controlled_start_handoff():
    bundle = build_owner_walkthrough_controlled_start_bundle()
    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "controlled_start_recorded": bundle["controlled_start_recorded"],
        "source_dependency": bundle["source_dependency"],
        "start_record": bundle["start_record"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "next_builder_notes": [
            "Controlled owner walkthrough start is recorded.",
            "Owner walkthrough has started.",
            "Owner walkthrough has not been accepted.",
            "Do not claim STAGING_READY.",
            "Keep broker submission locked.",
            "Keep real capital movement locked.",
            "Keep Live Auto locked.",
            "Next build is GP032 six-room walkthrough evidence capture execution.",
        ],
    }
