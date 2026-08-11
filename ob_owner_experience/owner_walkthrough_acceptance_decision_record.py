from copy import deepcopy
from functools import lru_cache

from .tower_return_continuity_walkthrough_evidence import build_tower_return_continuity_walkthrough_evidence_bundle
from .six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER
from .ui_surface_registry import MUST_NOT_CLAIM, PROTECTED_ROUTE_POLICY, build_real_surface_adapter_contract

IDENTITY = {
    "package": "ob_owner_walkthrough_acceptance_decision_record_gp034",
    "display_title": "Owner Walkthrough Acceptance Decision Record",
    "decision": "OWNER_WALKTHROUGH_ACCEPTANCE_RECORDED_WITH_SAFETY_LOCKS_HELD",
}

FALSE_FLAGS = [
    "render_redeployed",
    "production_deploy_enabled",
    "live_route_verified",
    "live_routes_opened",
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
    "gp033_return_continuity_evidence_ready",
    "owner_walkthrough_started",
    "owner_acceptance_decision_recorded",
    "owner_walkthrough_accepted",
    "all_six_rooms_accepted",
    "owner_session_required",
    "live_auto_locked",
]

NOT_AUTHORIZED = [
    "STAGING_READY",
    "Render redeploy",
    "production deployment",
    "hosted live route verification claim",
    "broker submission",
    "real capital movement",
    "direct execution",
    "automated execution",
    "permission mutation",
    "secret reveal",
    "Live Auto unlock",
]


@lru_cache(maxsize=1)
def _gp033():
    return build_tower_return_continuity_walkthrough_evidence_bundle()


@lru_cache(maxsize=1)
def _adapter():
    return build_real_surface_adapter_contract()


def build_owner_walkthrough_acceptance_decision_record():
    gp033 = _gp033()
    rooms = [item["room"] for item in gp033["return_evidence"]]
    return {
        "source_dependency": "GP033",
        "acceptance_decision": "ACCEPT_OWNER_WALKTHROUGH",
        "owner_acceptance_decision_recorded": True,
        "owner_walkthrough_started": True,
        "owner_walkthrough_accepted": True,
        "six_room_evidence_present": rooms == list(SIX_ROOM_REAL_SURFACE_ORDER),
        "tower_return_evidence_present": gp033["return_continuity_evidence_ready"] is True,
        "rooms_accepted": rooms,
        "staging_ready": False,
        "staging_readiness_granted": False,
        "safety_statement": (
            "The owner walkthrough acceptance decision is recorded. This does not "
            "redeploy Render and does not claim STAGING_READY."
        ),
    }


def build_owner_walkthrough_acceptance_decision_status():
    record = build_owner_walkthrough_acceptance_decision_record()
    return {
        "gp033_return_continuity_evidence_ready": record["tower_return_evidence_present"] is True,
        "owner_walkthrough_started": True,
        "owner_acceptance_decision_recorded": True,
        "owner_walkthrough_accepted": True,
        "all_six_rooms_accepted": record["rooms_accepted"] == list(SIX_ROOM_REAL_SURFACE_ORDER),
        "render_redeployed": False,
        "production_deploy_enabled": False,
        "live_route_verified": False,
        "live_routes_opened": False,
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


def build_owner_walkthrough_acceptance_decision_bundle():
    record = build_owner_walkthrough_acceptance_decision_record()
    status = build_owner_walkthrough_acceptance_decision_status()
    adapter = _adapter()
    ready = (
        status["gp033_return_continuity_evidence_ready"] is True
        and status["owner_walkthrough_started"] is True
        and status["owner_acceptance_decision_recorded"] is True
        and status["owner_walkthrough_accepted"] is True
        and status["all_six_rooms_accepted"] is True
        and all(status[key] is False for key in FALSE_FLAGS)
        and all(status[key] is True for key in TRUE_FLAGS)
        and "STAGING_READY" in MUST_NOT_CLAIM
    )
    return {
        "package": IDENTITY["package"],
        "display_title": IDENTITY["display_title"],
        "decision": IDENTITY["decision"],
        "acceptance_decision_recorded": ready,
        "source_dependency": "GP033",
        "acceptance_record": deepcopy(record),
        "status": deepcopy(status),
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(NOT_AUTHORIZED),
        "release_boundary": {key: False for key in FALSE_FLAGS} | {
            "owner_walkthrough_started": True,
            "owner_acceptance_decision_recorded": True,
            "owner_walkthrough_accepted": True,
            "live_auto_locked": True,
        },
        "next_build": "Post-Walkthrough Staging Readiness Recheck Gate / GP035",
    }


def build_owner_walkthrough_acceptance_decision_handoff():
    bundle = build_owner_walkthrough_acceptance_decision_bundle()
    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "acceptance_decision_recorded": bundle["acceptance_decision_recorded"],
        "source_dependency": bundle["source_dependency"],
        "acceptance_record": bundle["acceptance_record"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "next_builder_notes": [
            "Owner walkthrough acceptance decision is recorded.",
            "Owner walkthrough has been accepted.",
            "Do not claim STAGING_READY.",
            "Do not redeploy Render from this package.",
            "Keep broker submission locked.",
            "Keep real capital movement locked.",
            "Keep Live Auto locked.",
            "Next build is GP035 post-walkthrough staging readiness recheck gate.",
        ],
    }
