from copy import deepcopy
from functools import lru_cache

from .tower_ob_route_integration_preflight import build_tower_ob_route_integration_preflight_bundle
from .six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER
from .ui_surface_registry import MUST_NOT_CLAIM, PROTECTED_ROUTE_POLICY, build_real_surface_adapter_contract

IDENTITY = {
    "package": "ob_tower_ob_protected_route_wiring_gp022",
    "display_title": "Tower OB Protected Route Wiring Contract",
    "decision": "READY_FOR_TOWER_OB_PROTECTED_ROUTE_WIRING_CONTRACT_WITH_SAFETY_LOCKS_HELD",
}

FALSE_FLAGS = [
    "tower_route_code_changed",
    "ob_route_code_changed",
    "protected_route_wired_live",
    "live_routes_opened",
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
    "gp021_preflight_ready",
    "wiring_contract_ready",
    "default_deny_required",
    "tower_handoff_required",
    "owner_session_required",
    "live_auto_locked",
]

NOT_AUTHORIZED = [
    "STAGING_READY",
    "actual route code mutation",
    "protected route live wiring",
    "live route opening",
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
def _gp021():
    return build_tower_ob_route_integration_preflight_bundle()


@lru_cache(maxsize=1)
def _adapter():
    return build_real_surface_adapter_contract()


def build_tower_ob_protected_route_wiring_contract():
    gp021 = _gp021()
    contract = []
    for item in gp021["route_matrix"]:
        contract.append(
            {
                "room": item["room"],
                "ob_route_hint": item["ob_route_hint"],
                "tower_entry_route_hint": item["tower_entry_route_hint"],
                "tower_return_route_hint": item["tower_return_route_hint"],
                "default_deny_required": True,
                "tower_handoff_required": True,
                "owner_session_required": True,
                "step_up_required_for_dangerous_actions": True,
                "anonymous_access_allowed": False,
                "broker_submission_allowed": False,
                "money_movement_allowed": False,
                "live_auto_allowed": False,
                "actual_route_code_changed": False,
                "protected_route_wired_live": False,
            }
        )
    return contract


def build_tower_ob_protected_route_wiring_status():
    gp021 = _gp021()
    contract = build_tower_ob_protected_route_wiring_contract()
    return {
        "gp021_preflight_ready": gp021["preflight_ready"] is True,
        "wiring_contract_ready": True,
        "six_room_contract_present": len(contract) == 6 and [item["room"] for item in contract] == list(SIX_ROOM_REAL_SURFACE_ORDER),
        "default_deny_required": True,
        "tower_handoff_required": True,
        "tower_route_code_changed": False,
        "ob_route_code_changed": False,
        "protected_route_wired_live": False,
        "live_routes_opened": False,
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


def build_tower_ob_protected_route_wiring_bundle():
    contract = build_tower_ob_protected_route_wiring_contract()
    status = build_tower_ob_protected_route_wiring_status()
    adapter = _adapter()
    ready = (
        status["gp021_preflight_ready"] is True
        and status["wiring_contract_ready"] is True
        and status["six_room_contract_present"] is True
        and all(item["default_deny_required"] is True for item in contract)
        and all(item["anonymous_access_allowed"] is False for item in contract)
        and all(status[key] is False for key in FALSE_FLAGS)
        and all(status[key] is True for key in TRUE_FLAGS)
        and "STAGING_READY" in MUST_NOT_CLAIM
    )
    return {
        "package": IDENTITY["package"],
        "display_title": IDENTITY["display_title"],
        "decision": IDENTITY["decision"],
        "wiring_contract_ready": ready,
        "source_dependency": "GP021",
        "wiring_contract": contract,
        "status": status,
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(NOT_AUTHORIZED),
        "release_boundary": {key: False for key in FALSE_FLAGS} | {"live_auto_locked": True},
        "next_build": "OB Tower Return Session Continuity Repair Contract / GP023",
    }


def build_tower_ob_protected_route_wiring_handoff():
    bundle = build_tower_ob_protected_route_wiring_bundle()
    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "wiring_contract_ready": bundle["wiring_contract_ready"],
        "source_dependency": bundle["source_dependency"],
        "wiring_contract": bundle["wiring_contract"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "next_builder_notes": [
            "Treat this as protected route wiring contract only.",
            "Do not mutate actual route code from this package.",
            "Do not open live routes.",
            "Do not start or accept the owner walkthrough.",
            "Do not claim Tower return/session continuity repaired.",
            "Do not redeploy Render.",
            "Do not claim STAGING_READY.",
            "Keep broker submission locked.",
            "Keep real capital movement locked.",
            "Keep Live Auto locked.",
            "Next build is GP023 OB Tower return session continuity repair contract.",
        ],
    }
