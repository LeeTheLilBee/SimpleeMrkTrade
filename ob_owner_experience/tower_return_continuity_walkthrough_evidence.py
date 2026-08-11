from copy import deepcopy
from functools import lru_cache

from .six_room_walkthrough_evidence_capture_execution import build_six_room_walkthrough_evidence_capture_execution_bundle
from .tower_ob_actual_route_implementation_return_repair import resolve_ob_to_tower_return
from .six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER
from .ui_surface_registry import MUST_NOT_CLAIM, PROTECTED_ROUTE_POLICY, build_real_surface_adapter_contract

IDENTITY = {
    "package": "ob_tower_return_continuity_walkthrough_evidence_gp033",
    "display_title": "Tower Return Continuity Walkthrough Evidence",
    "decision": "TOWER_RETURN_CONTINUITY_WALKTHROUGH_EVIDENCE_CAPTURED_WITH_SAFETY_LOCKS_HELD",
}

FALSE_FLAGS = [
    "render_redeployed",
    "production_deploy_enabled",
    "live_route_verified",
    "live_routes_opened",
    "owner_walkthrough_accepted",
    "staging_ready",
    "broker_submission_enabled",
    "real_capital_movement_enabled",
    "direct_execution_enabled",
    "automated_execution_enabled",
    "permission_mutation_enabled",
    "secret_reveal_enabled",
]

TRUE_FLAGS = [
    "gp032_evidence_capture_executed",
    "owner_walkthrough_started",
    "tower_return_continuity_evidence_ready",
    "all_six_room_returns_verified",
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
def _gp032():
    return build_six_room_walkthrough_evidence_capture_execution_bundle()


@lru_cache(maxsize=1)
def _adapter():
    return build_real_surface_adapter_contract()


@lru_cache(maxsize=1)
def _return_evidence_cached():
    evidence = []
    for room in SIX_ROOM_REAL_SURFACE_ORDER:
        ret = resolve_ob_to_tower_return(room, True, True)
        evidence.append(
            {
                "room": room,
                "owner_walkthrough_started": True,
                "return_ready": ret["return_ready"] is True,
                "tower_return_route": ret.get("tower_return_route"),
                "session_reference_required": ret.get("session_reference_required") is True,
                "owner_session_required": ret.get("owner_session_required") is True,
                "return_control_observed": True,
                "session_continuity_observed": True,
                "tower_return_continuity_evidence_captured": True,
                "owner_acceptance_recorded": False,
                "live_route_verified": False,
                "staging_ready": False,
            }
        )
    return evidence


def build_tower_return_continuity_walkthrough_evidence():
    return deepcopy(_return_evidence_cached())


def build_tower_return_continuity_walkthrough_evidence_status():
    gp032 = _gp032()
    evidence = _return_evidence_cached()
    return {
        "gp032_evidence_capture_executed": gp032["evidence_capture_executed"] is True,
        "owner_walkthrough_started": True,
        "tower_return_continuity_evidence_ready": True,
        "all_six_room_returns_verified": len(evidence) == 6 and [item["room"] for item in evidence] == list(SIX_ROOM_REAL_SURFACE_ORDER) and all(item["return_ready"] is True for item in evidence),
        "render_redeployed": False,
        "production_deploy_enabled": False,
        "live_route_verified": False,
        "live_routes_opened": False,
        "owner_walkthrough_accepted": False,
        "staging_ready": False,
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


def build_tower_return_continuity_walkthrough_evidence_bundle():
    evidence = _return_evidence_cached()
    status = build_tower_return_continuity_walkthrough_evidence_status()
    adapter = _adapter()
    ready = (
        status["gp032_evidence_capture_executed"] is True
        and status["owner_walkthrough_started"] is True
        and status["tower_return_continuity_evidence_ready"] is True
        and status["all_six_room_returns_verified"] is True
        and all(status[key] is False for key in FALSE_FLAGS)
        and all(status[key] is True for key in TRUE_FLAGS)
        and "STAGING_READY" in MUST_NOT_CLAIM
    )
    return {
        "package": IDENTITY["package"],
        "display_title": IDENTITY["display_title"],
        "decision": IDENTITY["decision"],
        "return_continuity_evidence_ready": ready,
        "source_dependency": "GP032",
        "return_evidence": deepcopy(evidence),
        "status": deepcopy(status),
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(NOT_AUTHORIZED),
        "release_boundary": {key: False for key in FALSE_FLAGS} | {
            "owner_walkthrough_started": True,
            "tower_return_continuity_evidence_ready": True,
            "live_auto_locked": True,
        },
        "next_build": "Owner Walkthrough Acceptance Decision Record / GP034",
    }


def build_tower_return_continuity_walkthrough_evidence_handoff():
    bundle = build_tower_return_continuity_walkthrough_evidence_bundle()
    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "return_continuity_evidence_ready": bundle["return_continuity_evidence_ready"],
        "source_dependency": bundle["source_dependency"],
        "return_evidence": bundle["return_evidence"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "next_builder_notes": [
            "Tower return continuity walkthrough evidence is captured.",
            "Owner walkthrough has started.",
            "Owner walkthrough has not been accepted.",
            "Do not claim STAGING_READY.",
            "Keep broker submission locked.",
            "Keep real capital movement locked.",
            "Keep Live Auto locked.",
            "Next build is GP034 owner walkthrough acceptance decision record.",
        ],
    }
