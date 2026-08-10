from copy import deepcopy

from .owner_experience_integration_closeout import (
    build_owner_experience_integration_closeout_bundle,
)
from .six_room_real_surface_acceptance import (
    SIX_ROOM_REAL_SURFACE_ORDER,
    build_six_room_real_surface_acceptance_bundle,
)
from .ui_surface_registry import (
    MUST_NOT_CLAIM,
    PROTECTED_ROUTE_POLICY,
    build_real_surface_adapter_contract,
    build_surface_registry_entry,
)

ROUTE_OWNER_WALKTHROUGH_PREPARATION_IDENTITY = {
    "package": "ob_route_owner_walkthrough_preparation_gp010",
    "display_title": "Route and Owner Walkthrough Preparation",
    "decision": "READY_FOR_ROUTE_AND_OWNER_WALKTHROUGH_PREPARATION_WITH_SAFETY_LOCKS_HELD",
    "plain_language": (
        "The six accepted OB owner-experience rooms now have a prepared route "
        "checklist and owner walkthrough script. This is preparation only. It does "
        "not start the walkthrough, accept the walkthrough, repair Tower return, "
        "redeploy Render, claim staging readiness, or unlock dangerous actions."
    ),
}

ROUTE_OWNER_WALKTHROUGH_ROOM_SEQUENCE = [
    {
        "step": 1,
        "room": "dashboard",
        "owner_goal": "Confirm the owner can understand what needs attention today.",
    },
    {
        "step": 2,
        "room": "market_map",
        "owner_goal": "Confirm the owner can read market condition and risk before opportunity.",
    },
    {
        "step": 3,
        "room": "symbol_page",
        "owner_goal": "Confirm the owner can understand one asset without raw quote-wall noise.",
    },
    {
        "step": 4,
        "room": "trade_center",
        "owner_goal": "Confirm the owner sees review-only trade intent with execution locked.",
    },
    {
        "step": 5,
        "room": "review_center",
        "owner_goal": "Confirm the owner can review decisions, lessons, and corrections safely.",
    },
    {
        "step": 6,
        "room": "owner_console",
        "owner_goal": "Confirm the owner can see locks, access, receipts, and Tower handoff status.",
    },
]

ROUTE_OWNER_WALKTHROUGH_REQUIRED_CHECKS = [
    "route_hint_present",
    "component_hint_present",
    "data_adapter_hint_present",
    "registry_route_match",
    "registry_component_match",
    "registry_data_adapter_match",
    "anonymous_access_denied",
    "owner_session_required",
    "broker_submission_locked",
    "real_capital_movement_locked",
    "direct_execution_disabled",
    "automated_execution_disabled",
    "live_auto_locked",
    "staging_ready_not_claimed",
]

ROUTE_OWNER_WALKTHROUGH_NOT_AUTHORIZED = [
    "STAGING_READY",
    "owner walkthrough started",
    "owner walkthrough accepted",
    "Tower return/session continuity repaired",
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

ROUTE_OWNER_WALKTHROUGH_REQUIRED_FALSE_FLAGS = [
    "staging_ready",
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
]

ROUTE_OWNER_WALKTHROUGH_REQUIRED_TRUE_FLAGS = [
    "owner_session_required",
    "live_auto_locked",
]


def _find_acceptance_record(room_key, acceptance_bundle):
    for record in acceptance_bundle["matrix"]:
        if record["room"] == room_key:
            return record
    raise KeyError("Missing acceptance record for room: " + str(room_key))


def _find_step(room_key):
    for item in ROUTE_OWNER_WALKTHROUGH_ROOM_SEQUENCE:
        if item["room"] == room_key:
            return item
    raise KeyError("Missing walkthrough step for room: " + str(room_key))


def _bool(value):
    return value is True


def _route_record(room_key, acceptance_bundle):
    acceptance = _find_acceptance_record(room_key, acceptance_bundle)
    registry = build_surface_registry_entry(room_key)
    step = _find_step(room_key)

    route_hint_present = bool(acceptance.get("route_hint"))
    component_hint_present = bool(acceptance.get("component_hint"))
    data_adapter_hint_present = bool(acceptance.get("data_adapter_hint"))
    registry_route_match = acceptance.get("route_hint") == registry.get("route_hint")
    registry_component_match = acceptance.get("component_hint") == registry.get("component_hint")
    registry_data_adapter_match = acceptance.get("data_adapter_hint") == registry.get("data_adapter_hint")
    anonymous_access_denied = acceptance.get("anonymous_access_denied") is True
    owner_session_required = acceptance.get("owner_session_required") is True
    broker_submission_locked = acceptance.get("unsafe_false_flags", {}) == {}
    real_capital_movement_locked = acceptance.get("unsafe_false_flags", {}) == {}
    direct_execution_disabled = acceptance.get("unsafe_false_flags", {}) == {}
    automated_execution_disabled = acceptance.get("unsafe_false_flags", {}) == {}
    live_auto_locked = acceptance.get("unsafe_true_flags", {}) == {}
    staging_ready_not_claimed = "STAGING_READY" in acceptance.get("must_not_claim", [])

    checks = {
        "route_hint_present": route_hint_present,
        "component_hint_present": component_hint_present,
        "data_adapter_hint_present": data_adapter_hint_present,
        "registry_route_match": registry_route_match,
        "registry_component_match": registry_component_match,
        "registry_data_adapter_match": registry_data_adapter_match,
        "anonymous_access_denied": anonymous_access_denied,
        "owner_session_required": owner_session_required,
        "broker_submission_locked": broker_submission_locked,
        "real_capital_movement_locked": real_capital_movement_locked,
        "direct_execution_disabled": direct_execution_disabled,
        "automated_execution_disabled": automated_execution_disabled,
        "live_auto_locked": live_auto_locked,
        "staging_ready_not_claimed": staging_ready_not_claimed,
    }

    ready = all(checks.get(key) is True for key in ROUTE_OWNER_WALKTHROUGH_REQUIRED_CHECKS)

    return {
        "step": step["step"],
        "room": room_key,
        "display_title": acceptance.get("display_title"),
        "route_hint": acceptance.get("route_hint"),
        "component_hint": acceptance.get("component_hint"),
        "data_adapter_hint": acceptance.get("data_adapter_hint"),
        "owner_goal": step["owner_goal"],
        "accepted_by_gp008": acceptance.get("accepted") is True,
        "checks": checks,
        "ready_for_walkthrough_preparation": ready and acceptance.get("accepted") is True,
    }


def build_route_owner_walkthrough_route_matrix():
    acceptance = build_six_room_real_surface_acceptance_bundle()
    records = []

    for room_key in SIX_ROOM_REAL_SURFACE_ORDER:
        records.append(_route_record(room_key, acceptance))

    return records


def build_route_owner_walkthrough_script():
    matrix = build_route_owner_walkthrough_route_matrix()
    steps = []

    for record in matrix:
        steps.append(
            {
                "step": record["step"],
                "room": record["room"],
                "display_title": record["display_title"],
                "route_hint": record["route_hint"],
                "owner_goal": record["owner_goal"],
                "owner_prompt": (
                    "Open " + record["display_title"] + " and confirm: " + record["owner_goal"]
                ),
                "must_confirm": [
                    "Owner session is required.",
                    "Anonymous access is denied.",
                    "The route opens the expected room.",
                    "The visible surface matches the room purpose.",
                    "Dangerous actions are not available.",
                    "No staging readiness is claimed.",
                ],
                "must_not_do": [
                    "Do not accept the owner walkthrough in this package.",
                    "Do not claim Tower return/session continuity repaired.",
                    "Do not redeploy Render.",
                    "Do not unlock execution or money movement.",
                ],
                "prepared": record["ready_for_walkthrough_preparation"],
            }
        )

    return steps


def build_route_owner_walkthrough_preparation_status():
    closeout = build_owner_experience_integration_closeout_bundle()
    acceptance = build_six_room_real_surface_acceptance_bundle()
    matrix = build_route_owner_walkthrough_route_matrix()

    all_routes_ready = all(item["ready_for_walkthrough_preparation"] is True for item in matrix)
    closeout_closed = closeout["closed"] is True
    six_room_acceptance_ready = acceptance["accepted"] is True

    return {
        "gp009_closeout_closed": closeout_closed,
        "gp008_six_room_acceptance_ready": six_room_acceptance_ready,
        "all_six_rooms_present": acceptance["surface_status"]["all_six_rooms_present"],
        "all_routes_ready_for_walkthrough_preparation": all_routes_ready,
        "walkthrough_script_prepared": all_routes_ready and closeout_closed,
        "route_owner_walkthrough_preparation_ready": all_routes_ready and closeout_closed,
        "anonymous_access_allowed": False,
        "owner_session_required": True,
        "staging_ready": False,
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
        "live_auto_locked": True,
    }


def build_route_owner_walkthrough_preparation_bundle():
    status = build_route_owner_walkthrough_preparation_status()
    matrix = build_route_owner_walkthrough_route_matrix()
    script = build_route_owner_walkthrough_script()
    closeout = build_owner_experience_integration_closeout_bundle()
    adapter = build_real_surface_adapter_contract()

    false_flags_ok = all(
        status.get(key) is False
        for key in ROUTE_OWNER_WALKTHROUGH_REQUIRED_FALSE_FLAGS
    )

    true_flags_ok = all(
        status.get(key) is True
        for key in ROUTE_OWNER_WALKTHROUGH_REQUIRED_TRUE_FLAGS
    )

    prepared = all(
        [
            closeout["closed"] is True,
            status["route_owner_walkthrough_preparation_ready"] is True,
            all(item["prepared"] is True for item in script),
            false_flags_ok,
            true_flags_ok,
            "STAGING_READY" in MUST_NOT_CLAIM,
        ]
    )

    return {
        "package": ROUTE_OWNER_WALKTHROUGH_PREPARATION_IDENTITY["package"],
        "display_title": ROUTE_OWNER_WALKTHROUGH_PREPARATION_IDENTITY["display_title"],
        "decision": ROUTE_OWNER_WALKTHROUGH_PREPARATION_IDENTITY["decision"],
        "prepared": prepared,
        "closed_dependency": "GP009",
        "route_matrix": matrix,
        "walkthrough_script": script,
        "preparation_status": status,
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(ROUTE_OWNER_WALKTHROUGH_NOT_AUTHORIZED),
        "release_boundary": {
            "staging_ready": False,
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
            "live_auto_locked": True,
        },
        "next_build": "OB owner walkthrough dry-run evidence / GP011",
    }


def build_route_owner_walkthrough_preparation_handoff():
    bundle = build_route_owner_walkthrough_preparation_bundle()

    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "prepared": bundle["prepared"],
        "closed_dependency": bundle["closed_dependency"],
        "route_matrix": bundle["route_matrix"],
        "walkthrough_script": bundle["walkthrough_script"],
        "preparation_status": bundle["preparation_status"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "takeover_summary": (
            "GP010 prepares the six-room route and owner walkthrough checklist "
            "after GP009 closeout. It creates preparation records only. It does "
            "not start or accept the walkthrough, repair Tower return, redeploy "
            "Render, claim staging readiness, or unlock dangerous actions."
        ),
        "next_builder_notes": [
            "Use this as the route checklist before any owner walkthrough run.",
            "Verify Dashboard at /ob/dashboard.",
            "Verify Market Map at /ob/market-map.",
            "Verify Symbol Page at /ob/symbol/<symbol>.",
            "Verify Trade Center at /ob/trade-center.",
            "Verify Review Center at /ob/review-center.",
            "Verify Owner Console at /ob/owner-console.",
            "Keep Tower as the owner access boundary.",
            "Do not claim STAGING_READY.",
            "Do not start the owner walkthrough from this package.",
            "Do not mark owner walkthrough accepted from this package.",
            "Do not claim Tower return/session continuity repaired from this package.",
            "Do not redeploy Render from this package.",
            "Keep production deploy disabled.",
            "Keep broker submission locked.",
            "Keep real capital movement locked.",
            "Keep direct execution disabled.",
            "Keep automated execution disabled.",
            "Keep permission mutations disabled.",
            "Keep secret reveal disabled.",
            "Keep Live Auto locked.",
            "Next build is GP011 owner walkthrough dry-run evidence.",
        ],
    }
