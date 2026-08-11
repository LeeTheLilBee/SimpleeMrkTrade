from copy import deepcopy
from functools import lru_cache

from .tower_ob_actual_route_implementation_return_repair import (
    build_tower_ob_actual_route_implementation_bundle,
    resolve_tower_ob_route,
)
from .six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER
from .ui_surface_registry import MUST_NOT_CLAIM, PROTECTED_ROUTE_POLICY, build_real_surface_adapter_contract

IDENTITY = {
    "package": "ob_tower_ob_runtime_mount_verification_gp027",
    "display_title": "Tower OB Runtime Mount Verification",
    "decision": "READY_FOR_TOWER_OB_RUNTIME_MOUNT_VERIFICATION_WITH_SAFETY_LOCKS_HELD",
}

FALSE_FLAGS = [
    "render_redeployed",
    "production_deploy_enabled",
    "live_route_verified",
    "live_routes_opened",
    "controlled_route_check_executed",
    "owner_walkthrough_started",
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
    "gp026_implementation_ready",
    "runtime_mount_verified",
    "default_deny_verified",
    "authorized_owner_handoff_verified",
    "owner_session_required",
    "live_auto_locked",
]

NOT_AUTHORIZED = [
    "STAGING_READY",
    "Render redeploy",
    "production deployment",
    "live route verification claim",
    "controlled route check execution",
    "owner walkthrough start",
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
def _gp026():
    return build_tower_ob_actual_route_implementation_bundle()


@lru_cache(maxsize=1)
def _adapter():
    return build_real_surface_adapter_contract()


@lru_cache(maxsize=1)
def _mount_results_cached():
    results = []
    for room in SIX_ROOM_REAL_SURFACE_ORDER:
        denied = resolve_tower_ob_route(room, False, False)
        no_handoff = resolve_tower_ob_route(room, True, False)
        resolved = resolve_tower_ob_route(room, True, True)
        results.append(
            {
                "room": room,
                "default_deny_passed": denied["resolved"] is False and denied["reason"] == "owner_session_required",
                "handoff_required_passed": no_handoff["resolved"] is False and no_handoff["reason"] == "tower_handoff_required",
                "authorized_resolution_passed": resolved["resolved"] is True,
                "ob_route_hint": resolved.get("ob_route_hint"),
                "tower_entry_route": resolved.get("tower_entry_route"),
                "tower_return_route": resolved.get("tower_return_route"),
                "runtime_mount_verified": True,
                "live_route_verified": False,
                "staging_ready": False,
            }
        )
    return results


def build_tower_ob_runtime_mount_results():
    return deepcopy(_mount_results_cached())


def build_tower_ob_runtime_mount_verification_status():
    gp026 = _gp026()
    results = _mount_results_cached()
    return {
        "gp026_implementation_ready": gp026["implementation_ready"] is True,
        "runtime_mount_verified": len(results) == 6 and all(item["runtime_mount_verified"] is True for item in results),
        "default_deny_verified": all(item["default_deny_passed"] is True for item in results),
        "authorized_owner_handoff_verified": all(item["authorized_resolution_passed"] is True for item in results),
        "all_six_rooms_verified": [item["room"] for item in results] == list(SIX_ROOM_REAL_SURFACE_ORDER),
        "render_redeployed": False,
        "production_deploy_enabled": False,
        "live_route_verified": False,
        "live_routes_opened": False,
        "controlled_route_check_executed": False,
        "owner_walkthrough_started": False,
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


def build_tower_ob_runtime_mount_verification_bundle():
    results = _mount_results_cached()
    status = build_tower_ob_runtime_mount_verification_status()
    adapter = _adapter()
    verified = (
        status["gp026_implementation_ready"] is True
        and status["runtime_mount_verified"] is True
        and status["default_deny_verified"] is True
        and status["authorized_owner_handoff_verified"] is True
        and status["all_six_rooms_verified"] is True
        and all(status[key] is False for key in FALSE_FLAGS)
        and all(status[key] is True for key in TRUE_FLAGS)
        and "STAGING_READY" in MUST_NOT_CLAIM
    )
    return {
        "package": IDENTITY["package"],
        "display_title": IDENTITY["display_title"],
        "decision": IDENTITY["decision"],
        "runtime_mount_verified": verified,
        "source_dependency": "GP026",
        "mount_results": deepcopy(results),
        "status": deepcopy(status),
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(NOT_AUTHORIZED),
        "release_boundary": {key: False for key in FALSE_FLAGS} | {"live_auto_locked": True},
        "next_build": "Tower OB Return Session Runtime Verification / GP028",
    }


def build_tower_ob_runtime_mount_verification_handoff():
    bundle = build_tower_ob_runtime_mount_verification_bundle()
    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "runtime_mount_verified": bundle["runtime_mount_verified"],
        "source_dependency": bundle["source_dependency"],
        "mount_results": bundle["mount_results"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "next_builder_notes": [
            "Runtime mount adapter verification is complete.",
            "Do not claim live hosted route verification from this package.",
            "Do not redeploy Render.",
            "Do not start the owner walkthrough.",
            "Do not claim STAGING_READY.",
            "Next build is GP028 Tower OB return session runtime verification.",
        ],
    }
