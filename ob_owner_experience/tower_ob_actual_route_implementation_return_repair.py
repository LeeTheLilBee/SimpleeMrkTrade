from copy import deepcopy
from functools import lru_cache

from .staging_readiness_decision_gate import build_staging_readiness_decision_gate_bundle
from .six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER
from .ui_surface_registry import (
    MUST_NOT_CLAIM,
    PROTECTED_ROUTE_POLICY,
    build_real_surface_adapter_contract,
    build_surface_registry_entry,
)

IDENTITY = {
    "package": "ob_tower_ob_actual_route_implementation_return_repair_gp026",
    "display_title": "Tower OB Actual Route Implementation and Return Repair",
    "decision": "READY_FOR_TOWER_OB_ACTUAL_ROUTE_IMPLEMENTATION_RETURN_REPAIR_WITH_SAFETY_LOCKS_HELD",
}

TOWER_ENTRY_ROUTE = "/tower/access/observatory"
TOWER_RETURN_ROUTE = "/tower/access-home"

FALSE_FLAGS = [
    "render_redeployed",
    "production_deploy_enabled",
    "live_route_verified",
    "live_routes_opened",
    "controlled_route_check_executed",
    "owner_walkthrough_started",
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
    "gp025_no_go_hold_confirmed",
    "implementation_adapter_ready",
    "route_table_ready",
    "return_adapter_ready",
    "default_deny_required",
    "tower_handoff_required",
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
def _gp025():
    return build_staging_readiness_decision_gate_bundle()


@lru_cache(maxsize=1)
def _adapter():
    return build_real_surface_adapter_contract()


@lru_cache(maxsize=1)
def _route_table_cached():
    rows = []
    for room in SIX_ROOM_REAL_SURFACE_ORDER:
        registry = build_surface_registry_entry(room)
        rows.append(
            {
                "room": room,
                "display_title": registry["display_title"],
                "ob_route_hint": registry["route_hint"],
                "component_hint": registry["component_hint"],
                "data_adapter_hint": registry["data_adapter_hint"],
                "tower_entry_route": TOWER_ENTRY_ROUTE,
                "tower_return_route": TOWER_RETURN_ROUTE,
                "mount_key": "tower_ob_" + room,
                "route_adapter_name": "resolve_tower_ob_" + room + "_route",
                "implementation_adapter_ready": True,
                "actual_runtime_mount_verified": False,
                "live_route_verified": False,
                "default_deny_required": True,
                "tower_handoff_required": True,
                "owner_session_required": True,
                "anonymous_access_allowed": False,
                "broker_submission_allowed": False,
                "money_movement_allowed": False,
                "live_auto_allowed": False,
            }
        )
    return rows


@lru_cache(maxsize=1)
def _return_adapter_cached():
    rows = []
    for item in _route_table_cached():
        rows.append(
            {
                "room": item["room"],
                "ob_route_hint": item["ob_route_hint"],
                "tower_return_route": item["tower_return_route"],
                "return_adapter_name": "return_from_ob_" + item["room"] + "_to_tower",
                "session_reference_required": True,
                "tower_handoff_receipt_required": True,
                "owner_session_required": True,
                "return_control_visible": True,
                "return_control_destination": TOWER_RETURN_ROUTE,
                "repair_adapter_ready": True,
                "actual_runtime_return_verified": False,
                "live_route_verified": False,
                "staging_ready": False,
            }
        )
    return rows


def build_tower_ob_route_implementation_table():
    return deepcopy(_route_table_cached())


def build_tower_ob_return_session_continuity_repair_adapter():
    return deepcopy(_return_adapter_cached())


def resolve_tower_ob_route(room, owner_session_active=False, tower_handoff_present=False):
    matches = [item for item in _route_table_cached() if item["room"] == room]
    if not matches:
        return {
            "resolved": False,
            "room": room,
            "reason": "unknown_room",
            "anonymous_access_allowed": False,
            "owner_session_required": True,
        }

    item = matches[0]

    if owner_session_active is not True:
        return {
            "resolved": False,
            "room": room,
            "reason": "owner_session_required",
            "ob_route_hint": item["ob_route_hint"],
            "tower_entry_route": item["tower_entry_route"],
            "anonymous_access_allowed": False,
            "owner_session_required": True,
        }

    if tower_handoff_present is not True:
        return {
            "resolved": False,
            "room": room,
            "reason": "tower_handoff_required",
            "ob_route_hint": item["ob_route_hint"],
            "tower_entry_route": item["tower_entry_route"],
            "anonymous_access_allowed": False,
            "owner_session_required": True,
            "tower_handoff_required": True,
        }

    return {
        "resolved": True,
        "room": room,
        "reason": "route_resolved_for_authorized_tower_owner_session",
        "ob_route_hint": item["ob_route_hint"],
        "tower_entry_route": item["tower_entry_route"],
        "tower_return_route": item["tower_return_route"],
        "component_hint": item["component_hint"],
        "data_adapter_hint": item["data_adapter_hint"],
        "anonymous_access_allowed": False,
        "owner_session_required": True,
        "tower_handoff_required": True,
        "live_route_verified": False,
        "staging_ready": False,
    }


def resolve_ob_to_tower_return(room, owner_session_active=False, session_reference_present=False):
    matches = [item for item in _return_adapter_cached() if item["room"] == room]
    if not matches:
        return {
            "return_ready": False,
            "room": room,
            "reason": "unknown_room",
            "owner_session_required": True,
        }

    item = matches[0]

    if owner_session_active is not True:
        return {
            "return_ready": False,
            "room": room,
            "reason": "owner_session_required",
            "tower_return_route": item["tower_return_route"],
            "owner_session_required": True,
        }

    if session_reference_present is not True:
        return {
            "return_ready": False,
            "room": room,
            "reason": "session_reference_required",
            "tower_return_route": item["tower_return_route"],
            "session_reference_required": True,
        }

    return {
        "return_ready": True,
        "room": room,
        "reason": "return_session_continuity_resolved_for_authorized_owner_session",
        "tower_return_route": item["tower_return_route"],
        "session_reference_required": True,
        "owner_session_required": True,
        "actual_runtime_return_verified": False,
        "live_route_verified": False,
        "staging_ready": False,
    }


def build_tower_ob_actual_route_implementation_status():
    gp025 = _gp025()
    table = _route_table_cached()
    return_adapter = _return_adapter_cached()

    return {
        "gp025_no_go_hold_confirmed": gp025["recommendation"] == "NO_GO_HOLD",
        "gp025_gate_state_confirmed": gp025["gate_state"] == "closed_pending_actual_tower_route_work",
        "implementation_adapter_ready": True,
        "route_table_ready": len(table) == 6 and [item["room"] for item in table] == list(SIX_ROOM_REAL_SURFACE_ORDER),
        "return_adapter_ready": len(return_adapter) == 6 and [item["room"] for item in return_adapter] == list(SIX_ROOM_REAL_SURFACE_ORDER),
        "actual_tower_route_work_completed_in_package": True,
        "actual_return_repair_adapter_completed_in_package": True,
        "default_deny_required": True,
        "tower_handoff_required": True,
        "actual_runtime_mount_verified": False,
        "actual_runtime_return_verified": False,
        "render_redeployed": False,
        "production_deploy_enabled": False,
        "live_route_verified": False,
        "live_routes_opened": False,
        "controlled_route_check_executed": False,
        "owner_walkthrough_started": False,
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


def build_tower_ob_actual_route_implementation_bundle():
    table = _route_table_cached()
    return_adapter = _return_adapter_cached()
    status = build_tower_ob_actual_route_implementation_status()
    adapter = _adapter()

    ready = (
        status["gp025_no_go_hold_confirmed"] is True
        and status["implementation_adapter_ready"] is True
        and status["route_table_ready"] is True
        and status["return_adapter_ready"] is True
        and all(status[key] is False for key in FALSE_FLAGS)
        and all(status[key] is True for key in TRUE_FLAGS)
        and "STAGING_READY" in MUST_NOT_CLAIM
    )

    return {
        "package": IDENTITY["package"],
        "display_title": IDENTITY["display_title"],
        "decision": IDENTITY["decision"],
        "implementation_ready": ready,
        "source_dependency": "GP025",
        "tower_entry_route": TOWER_ENTRY_ROUTE,
        "tower_return_route": TOWER_RETURN_ROUTE,
        "route_table": deepcopy(table),
        "return_adapter": deepcopy(return_adapter),
        "status": deepcopy(status),
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(NOT_AUTHORIZED),
        "release_boundary": {key: False for key in FALSE_FLAGS} | {"live_auto_locked": True},
        "next_build": "Tower OB Runtime Mount Verification / GP027",
    }


def build_tower_ob_actual_route_implementation_handoff():
    bundle = build_tower_ob_actual_route_implementation_bundle()
    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "implementation_ready": bundle["implementation_ready"],
        "source_dependency": bundle["source_dependency"],
        "tower_entry_route": bundle["tower_entry_route"],
        "tower_return_route": bundle["tower_return_route"],
        "route_table": bundle["route_table"],
        "return_adapter": bundle["return_adapter"],
        "status": bundle["status"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "next_builder_notes": [
            "Route implementation adapter is ready.",
            "Return/session continuity adapter is ready.",
            "Do not claim live route verification from this package.",
            "Do not redeploy Render from this package.",
            "Do not start the owner walkthrough from this package.",
            "Do not claim STAGING_READY.",
            "Next build is GP027 Tower OB runtime mount verification.",
        ],
    }
