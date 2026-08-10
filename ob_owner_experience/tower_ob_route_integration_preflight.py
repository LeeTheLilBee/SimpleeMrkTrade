from copy import deepcopy
from functools import lru_cache

from .owner_walkthrough_acceptance_hold_closeout import build_owner_walkthrough_acceptance_hold_closeout_bundle
from .six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER
from .ui_surface_registry import MUST_NOT_CLAIM, PROTECTED_ROUTE_POLICY, build_real_surface_adapter_contract

IDENTITY = {
    "package": "ob_tower_ob_route_integration_preflight_gp021",
    "display_title": "Tower OB Route Integration Preflight",
    "decision": "READY_FOR_TOWER_OB_ROUTE_INTEGRATION_PREFLIGHT_WITH_SAFETY_LOCKS_HELD",
}

FALSE_FLAGS = [
    "tower_routes_modified",
    "ob_routes_modified",
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
    "gp020_closeout_ready",
    "tower_ob_preflight_ready",
    "six_room_scope_present",
    "owner_session_required",
    "live_auto_locked",
]

NOT_AUTHORIZED = [
    "STAGING_READY",
    "Tower route mutation",
    "OB route mutation",
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


EXPECTED_ROUTE_HINTS = {
    "dashboard": "/ob/dashboard",
    "market_map": "/ob/market-map",
    "symbol_page": "/ob/symbol/<symbol>",
    "trade_center": "/ob/trade-center",
    "review_center": "/ob/review-center",
    "owner_console": "/ob/owner-console",
}


@lru_cache(maxsize=1)
def _gp020():
    return build_owner_walkthrough_acceptance_hold_closeout_bundle()


@lru_cache(maxsize=1)
def _adapter():
    return build_real_surface_adapter_contract()


def build_tower_ob_route_integration_preflight_matrix():
    gp020 = _gp020()
    matrix = []
    for item in gp020["room_scope"]:
        room = item["room"]
        matrix.append(
            {
                "room": room,
                "step": item.get("step"),
                "display_title": item.get("display_title"),
                "ob_route_hint": item.get("route_hint"),
                "expected_ob_route_hint": EXPECTED_ROUTE_HINTS[room],
                "tower_entry_route_hint": "/tower/access/observatory",
                "tower_return_route_hint": "/tower/access-home",
                "route_contract_ready": item.get("route_hint") == EXPECTED_ROUTE_HINTS[room],
                "tower_route_modified": False,
                "ob_route_modified": False,
                "live_route_opened": False,
                "owner_walkthrough_started": False,
                "owner_walkthrough_accepted": False,
            }
        )
    return matrix


def build_tower_ob_route_integration_preflight_status():
    gp020 = _gp020()
    matrix = build_tower_ob_route_integration_preflight_matrix()
    return {
        "gp020_closeout_ready": gp020["closeout_ready"] is True,
        "tower_ob_preflight_ready": True,
        "six_room_scope_present": len(matrix) == 6 and [item["room"] for item in matrix] == list(SIX_ROOM_REAL_SURFACE_ORDER),
        "all_route_contracts_ready": all(item["route_contract_ready"] is True for item in matrix),
        "tower_routes_modified": False,
        "ob_routes_modified": False,
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


def build_tower_ob_route_integration_preflight_bundle():
    matrix = build_tower_ob_route_integration_preflight_matrix()
    status = build_tower_ob_route_integration_preflight_status()
    adapter = _adapter()
    ready = (
        status["gp020_closeout_ready"] is True
        and status["tower_ob_preflight_ready"] is True
        and status["six_room_scope_present"] is True
        and status["all_route_contracts_ready"] is True
        and all(status[key] is False for key in FALSE_FLAGS)
        and all(status[key] is True for key in TRUE_FLAGS)
        and "STAGING_READY" in MUST_NOT_CLAIM
    )
    return {
        "package": IDENTITY["package"],
        "display_title": IDENTITY["display_title"],
        "decision": IDENTITY["decision"],
        "preflight_ready": ready,
        "source_dependency": "GP020",
        "route_matrix": matrix,
        "status": status,
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(NOT_AUTHORIZED),
        "release_boundary": {key: False for key in FALSE_FLAGS} | {"live_auto_locked": True},
        "next_build": "Tower OB Protected Route Wiring Contract / GP022",
    }


def build_tower_ob_route_integration_preflight_handoff():
    bundle = build_tower_ob_route_integration_preflight_bundle()
    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "preflight_ready": bundle["preflight_ready"],
        "source_dependency": bundle["source_dependency"],
        "route_matrix": bundle["route_matrix"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "next_builder_notes": [
            "Treat this as Tower OB route integration preflight only.",
            "Do not modify Tower routes from this package.",
            "Do not modify OB routes from this package.",
            "Do not open live routes.",
            "Do not start or accept the owner walkthrough.",
            "Do not claim Tower return/session continuity repaired.",
            "Do not redeploy Render.",
            "Do not claim STAGING_READY.",
            "Keep broker submission locked.",
            "Keep real capital movement locked.",
            "Keep Live Auto locked.",
            "Next build is GP022 Tower OB protected route wiring contract.",
        ],
    }
