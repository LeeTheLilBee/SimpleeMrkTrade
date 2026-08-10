from copy import deepcopy
from functools import lru_cache

from .tower_ob_protected_route_wiring import build_tower_ob_protected_route_wiring_bundle
from .six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER
from .ui_surface_registry import MUST_NOT_CLAIM, PROTECTED_ROUTE_POLICY, build_real_surface_adapter_contract

IDENTITY = {
    "package": "ob_tower_return_session_continuity_repair_gp023",
    "display_title": "OB Tower Return Session Continuity Repair Contract",
    "decision": "READY_FOR_OB_TOWER_RETURN_SESSION_CONTINUITY_REPAIR_CONTRACT_WITH_SAFETY_LOCKS_HELD",
}

FALSE_FLAGS = [
    "actual_tower_return_code_changed",
    "tower_return_repaired",
    "session_continuity_repaired_live",
    "live_routes_opened",
    "owner_walkthrough_started",
    "owner_walkthrough_accepted",
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
    "gp022_wiring_contract_ready",
    "return_repair_contract_ready",
    "tower_return_required",
    "owner_session_required",
    "live_auto_locked",
]

NOT_AUTHORIZED = [
    "STAGING_READY",
    "actual Tower return code mutation",
    "Tower return/session continuity repair live claim",
    "live route opening",
    "owner walkthrough start",
    "owner walkthrough acceptance",
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
def _gp022():
    return build_tower_ob_protected_route_wiring_bundle()


@lru_cache(maxsize=1)
def _adapter():
    return build_real_surface_adapter_contract()


def build_ob_tower_return_session_continuity_contract():
    gp022 = _gp022()
    contract = []
    for item in gp022["wiring_contract"]:
        contract.append(
            {
                "room": item["room"],
                "ob_route_hint": item["ob_route_hint"],
                "tower_entry_route_hint": item["tower_entry_route_hint"],
                "tower_return_route_hint": item["tower_return_route_hint"],
                "return_control_required": True,
                "tower_session_reference_required": True,
                "session_continuity_check_required": True,
                "owner_session_required": True,
                "actual_tower_return_code_changed": False,
                "tower_return_repaired": False,
                "session_continuity_repaired_live": False,
            }
        )
    return contract


def build_ob_tower_return_session_continuity_status():
    gp022 = _gp022()
    contract = build_ob_tower_return_session_continuity_contract()
    return {
        "gp022_wiring_contract_ready": gp022["wiring_contract_ready"] is True,
        "return_repair_contract_ready": True,
        "six_room_return_contract_present": len(contract) == 6 and [item["room"] for item in contract] == list(SIX_ROOM_REAL_SURFACE_ORDER),
        "tower_return_required": True,
        "actual_tower_return_code_changed": False,
        "tower_return_repaired": False,
        "session_continuity_repaired_live": False,
        "live_routes_opened": False,
        "owner_walkthrough_started": False,
        "owner_walkthrough_accepted": False,
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


def build_ob_tower_return_session_continuity_repair_bundle():
    contract = build_ob_tower_return_session_continuity_contract()
    status = build_ob_tower_return_session_continuity_status()
    adapter = _adapter()
    ready = (
        status["gp022_wiring_contract_ready"] is True
        and status["return_repair_contract_ready"] is True
        and status["six_room_return_contract_present"] is True
        and all(item["return_control_required"] is True for item in contract)
        and all(item["tower_return_repaired"] is False for item in contract)
        and all(status[key] is False for key in FALSE_FLAGS)
        and all(status[key] is True for key in TRUE_FLAGS)
        and "STAGING_READY" in MUST_NOT_CLAIM
    )
    return {
        "package": IDENTITY["package"],
        "display_title": IDENTITY["display_title"],
        "decision": IDENTITY["decision"],
        "return_repair_contract_ready": ready,
        "source_dependency": "GP022",
        "return_contract": contract,
        "status": status,
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(NOT_AUTHORIZED),
        "release_boundary": {key: False for key in FALSE_FLAGS} | {"live_auto_locked": True},
        "next_build": "Integrated Owner Walkthrough Controlled Route Check / GP024",
    }


def build_ob_tower_return_session_continuity_repair_handoff():
    bundle = build_ob_tower_return_session_continuity_repair_bundle()
    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "return_repair_contract_ready": bundle["return_repair_contract_ready"],
        "source_dependency": bundle["source_dependency"],
        "return_contract": bundle["return_contract"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "next_builder_notes": [
            "Treat this as Tower return/session continuity repair contract only.",
            "Do not claim actual Tower return repaired from this package.",
            "Do not mutate Tower route code from this package.",
            "Do not open live routes.",
            "Do not start or accept the owner walkthrough.",
            "Do not redeploy Render.",
            "Do not claim STAGING_READY.",
            "Keep broker submission locked.",
            "Keep real capital movement locked.",
            "Keep Live Auto locked.",
            "Next build is GP024 integrated owner walkthrough controlled route check.",
        ],
    }
