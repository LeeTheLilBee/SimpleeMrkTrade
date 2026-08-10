from copy import deepcopy
from functools import lru_cache

from .ob_tower_return_session_continuity_repair import build_ob_tower_return_session_continuity_repair_bundle
from .six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER
from .ui_surface_registry import MUST_NOT_CLAIM, PROTECTED_ROUTE_POLICY, build_real_surface_adapter_contract

IDENTITY = {
    "package": "ob_integrated_owner_walkthrough_controlled_route_check_gp024",
    "display_title": "Integrated Owner Walkthrough Controlled Route Check",
    "decision": "READY_FOR_INTEGRATED_OWNER_WALKTHROUGH_CONTROLLED_ROUTE_CHECK_WITH_SAFETY_LOCKS_HELD",
}

FALSE_FLAGS = [
    "controlled_route_check_executed",
    "live_route_opened",
    "owner_walkthrough_started",
    "owner_walkthrough_accepted",
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

TRUE_FLAGS = [
    "gp023_return_contract_ready",
    "controlled_route_check_ready",
    "six_room_check_plan_present",
    "owner_session_required",
    "live_auto_locked",
]

NOT_AUTHORIZED = [
    "STAGING_READY",
    "controlled route check execution",
    "live route opening",
    "owner walkthrough start",
    "owner walkthrough acceptance",
    "Tower return/session continuity repair live claim",
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
def _gp023():
    return build_ob_tower_return_session_continuity_repair_bundle()


@lru_cache(maxsize=1)
def _adapter():
    return build_real_surface_adapter_contract()


def build_integrated_owner_walkthrough_controlled_route_check():
    gp023 = _gp023()
    check = []
    for item in gp023["return_contract"]:
        check.append(
            {
                "room": item["room"],
                "step": item.get("step"),
                "display_title": item.get("display_title"),
                "ob_route_hint": item["ob_route_hint"],
                "tower_entry_route_hint": item["tower_entry_route_hint"],
                "tower_return_route_hint": item["tower_return_route_hint"],
                "check_required": True,
                "check_executed": False,
                "live_route_opened": False,
                "tower_return_repaired": False,
                "owner_walkthrough_started": False,
                "owner_walkthrough_accepted": False,
                "must_confirm_later": [
                    "Tower owner session is active.",
                    "OB route opens through Tower handoff.",
                    "Return to Tower is visible.",
                    "Session continuity is preserved.",
                    "Dangerous actions remain locked.",
                    "STAGING_READY is not claimed.",
                ],
            }
        )
    return check


def build_integrated_owner_walkthrough_controlled_route_check_status():
    gp023 = _gp023()
    check = build_integrated_owner_walkthrough_controlled_route_check()
    return {
        "gp023_return_contract_ready": gp023["return_repair_contract_ready"] is True,
        "controlled_route_check_ready": True,
        "six_room_check_plan_present": len(check) == 6 and [item["room"] for item in check] == list(SIX_ROOM_REAL_SURFACE_ORDER),
        "controlled_route_check_executed": False,
        "live_route_opened": False,
        "owner_walkthrough_started": False,
        "owner_walkthrough_accepted": False,
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


def build_integrated_owner_walkthrough_controlled_route_check_bundle():
    check = build_integrated_owner_walkthrough_controlled_route_check()
    status = build_integrated_owner_walkthrough_controlled_route_check_status()
    adapter = _adapter()
    ready = (
        status["gp023_return_contract_ready"] is True
        and status["controlled_route_check_ready"] is True
        and status["six_room_check_plan_present"] is True
        and all(item["check_required"] is True for item in check)
        and all(item["check_executed"] is False for item in check)
        and all(status[key] is False for key in FALSE_FLAGS)
        and all(status[key] is True for key in TRUE_FLAGS)
        and "STAGING_READY" in MUST_NOT_CLAIM
    )
    return {
        "package": IDENTITY["package"],
        "display_title": IDENTITY["display_title"],
        "decision": IDENTITY["decision"],
        "controlled_route_check_ready": ready,
        "source_dependency": "GP023",
        "controlled_route_check": check,
        "status": status,
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(NOT_AUTHORIZED),
        "release_boundary": {key: False for key in FALSE_FLAGS} | {"live_auto_locked": True},
        "next_build": "Staging Readiness Decision Gate / GP025",
    }


def build_integrated_owner_walkthrough_controlled_route_check_handoff():
    bundle = build_integrated_owner_walkthrough_controlled_route_check_bundle()
    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "controlled_route_check_ready": bundle["controlled_route_check_ready"],
        "source_dependency": bundle["source_dependency"],
        "controlled_route_check": bundle["controlled_route_check"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "next_builder_notes": [
            "Treat this as controlled route check preparation only.",
            "Do not execute the controlled route check from this package.",
            "Do not open live routes.",
            "Do not start or accept the owner walkthrough.",
            "Do not claim Tower return/session continuity repaired.",
            "Do not redeploy Render.",
            "Do not claim STAGING_READY.",
            "Keep broker submission locked.",
            "Keep real capital movement locked.",
            "Keep Live Auto locked.",
            "Next build is GP025 staging readiness decision gate.",
        ],
    }
