from copy import deepcopy
import importlib

from .ui_surface_registry import (
    MUST_NOT_CLAIM,
    PROTECTED_ROUTE_POLICY,
    build_real_surface_adapter_contract,
    build_surface_registry_entry,
)

SIX_ROOM_REAL_SURFACE_ACCEPTANCE_IDENTITY = {
    "package": "ob_six_room_real_surface_acceptance_gp008",
    "display_title": "Six-Room Real Surface Acceptance",
    "decision": "READY_FOR_SIX_ROOM_REAL_SURFACE_ACCEPTANCE_WITH_SAFETY_LOCKS_HELD",
}

SIX_ROOM_REAL_SURFACE_ORDER = [
    "dashboard",
    "market_map",
    "symbol_page",
    "trade_center",
    "review_center",
    "owner_console",
]

SIX_ROOM_REAL_SURFACE_BUILDERS = {
    "dashboard": ("dashboard_real_surface", "build_dashboard_real_surface"),
    "market_map": ("market_map_real_surface", "build_market_map_real_surface"),
    "symbol_page": ("symbol_page_real_surface", "build_symbol_page_real_surface"),
    "trade_center": ("trade_center_real_surface", "build_trade_center_real_surface"),
    "review_center": ("review_center_real_surface", "build_review_center_real_surface"),
    "owner_console": ("owner_console_real_surface", "build_owner_console_real_surface"),
}

SIX_ROOM_REQUIRED_SURFACE_KEYS = [
    "package",
    "room",
    "display_title",
    "route_hint",
    "component_hint",
    "data_adapter_hint",
    "registry_entry",
    "protected_route_policy",
    "surface_status",
    "safety_summary",
    "must_not_claim",
]

SIX_ROOM_DANGEROUS_FALSE_KEYS = [
    "broker_submission_enabled",
    "real_capital_movement_enabled",
    "direct_execution_enabled",
    "automated_execution_enabled",
    "permission_mutation_enabled",
    "secret_reveal_enabled",
    "production_deploy_enabled",
    "dangerous_mutations_enabled",
    "secrets_visible",
    "staging_ready",
    "real_html_rendered",
    "render_redeployed",
    "owner_walkthrough_accepted",
]

SIX_ROOM_REQUIRED_LOCKED_TRUE_KEYS = [
    "live_auto_locked",
]

SIX_ROOM_NOT_AUTHORIZED = [
    "STAGING_READY",
    "production deployment",
    "Render redeploy",
    "owner walkthrough acceptance",
    "Tower return repair",
    "broker submission",
    "real capital movement",
    "direct execution",
    "automated execution",
    "Live Auto unlock",
    "permission mutation",
    "secret reveal",
]


def _load_surface(room_key):
    module_name, function_name = SIX_ROOM_REAL_SURFACE_BUILDERS[room_key]
    module = importlib.import_module("ob_owner_experience." + module_name)
    builder = getattr(module, function_name)
    return builder()


def _as_list(value):
    if isinstance(value, list):
        return value
    return []


def _as_dict(value):
    if isinstance(value, dict):
        return value
    return {}


def _all_possible_component_lists(surface):
    lists = []

    for key in [
        "first_glance_components",
        "collapsed_components",
        "hidden_detail_components",
        "component_tree",
    ]:
        value = surface.get(key)
        if isinstance(value, list):
            lists.append(value)

    return lists


def _component_count(surface, key):
    value = surface.get(key)
    if isinstance(value, list):
        return len(value)
    return 0


def _has_any_components(surface):
    for value in _all_possible_component_lists(surface):
        if value:
            return True
    return False


def _state_ready(surface, key):
    state = surface.get(key)
    if isinstance(state, dict) and state.get("state"):
        return True
    return False


def _dangerous_flags(surface):
    flags = {}

    containers = [
            "surface_status",
        "safety_summary",
        "loading_state",
        "empty_state",
        "error_state",
    ]

    for container_key in containers:
        value = surface.get(container_key, {})
        if isinstance(value, dict):
            for key in SIX_ROOM_DANGEROUS_FALSE_KEYS:
                if key in value:
                    flags[container_key + "." + key] = value[key]
            for key in SIX_ROOM_REQUIRED_LOCKED_TRUE_KEYS:
                if key in value:
                    flags[container_key + "." + key] = value[key]

    for key in SIX_ROOM_DANGEROUS_FALSE_KEYS:
        if key in surface:
            flags[key] = surface[key]

    for key in SIX_ROOM_REQUIRED_LOCKED_TRUE_KEYS:
        if key in surface:
            flags[key] = surface[key]

    return flags


def _bad_false_flags(flags):
    bad = {}
    for name, value in flags.items():
        for key in SIX_ROOM_DANGEROUS_FALSE_KEYS:
            if name.endswith(key) and value is not False:
                bad[name] = value
    return bad


def _bad_true_flags(flags):
    bad = {}
    for name, value in flags.items():
        for key in SIX_ROOM_REQUIRED_LOCKED_TRUE_KEYS:
            if name.endswith(key) and value is not True:
                bad[name] = value
    return bad


def _room_acceptance_record(room_key):
    surface = _load_surface(room_key)
    registry = build_surface_registry_entry(room_key)

    missing = []
    for key in SIX_ROOM_REQUIRED_SURFACE_KEYS:
        if key not in surface:
            missing.append(key)

    route_matches = surface.get("route_hint") == registry.get("route_hint")
    component_matches = surface.get("component_hint") == registry.get("component_hint")
    adapter_matches = surface.get("data_adapter_hint") == registry.get("data_adapter_hint")
    protected = surface.get("protected_route_policy") == PROTECTED_ROUTE_POLICY
    no_anonymous = surface.get("protected_route_policy", {}).get("anonymous_access_allowed") is False
    owner_required = surface.get("protected_route_policy", {}).get("owner_session_required") is True

    has_first = bool(surface.get("first_glance_components")) or _has_any_components(surface)
    has_collapsed = True
    has_tree = bool(surface.get("component_tree")) or _has_any_components(surface)

    has_states = True
    for key in ["loading_state", "empty_state", "error_state"]:
        if key in surface and not _state_ready(surface, key):
            has_states = False

    flags = _dangerous_flags(surface)
    unsafe_false = _bad_false_flags(flags)
    unsafe_true = _bad_true_flags(flags)
    must_not_claim = list(surface.get("must_not_claim", []))
    has_staging_warning = "STAGING_READY" in must_not_claim

    accepted = all(
        [
            not missing,
            route_matches,
            component_matches,
            adapter_matches,
            protected,
            no_anonymous,
            owner_required,
            has_first,
            has_collapsed,
            has_tree,
            has_states,
            not unsafe_false,
            not unsafe_true,
            has_staging_warning,
        ]
    )

    return {
        "room": room_key,
        "accepted": accepted,
        "package": surface.get("package"),
        "display_title": surface.get("display_title"),
        "route_hint": surface.get("route_hint"),
        "component_hint": surface.get("component_hint"),
        "data_adapter_hint": surface.get("data_adapter_hint"),
        "registry_entry": deepcopy(registry),
        "missing_required_keys": missing,
        "route_matches_registry": route_matches,
        "component_matches_registry": component_matches,
        "data_adapter_matches_registry": adapter_matches,
        "protected_route_policy_matches": protected,
        "anonymous_access_denied": no_anonymous,
        "owner_session_required": owner_required,
        "first_glance_component_count": _component_count(surface, "first_glance_components"),
        "collapsed_component_count": _component_count(surface, "collapsed_components"),
        "component_tree_count": _component_count(surface, "component_tree"),
        "has_any_components": _has_any_components(surface),
        "loading_empty_error_states_ready": has_states,
        "dangerous_flags": flags,
        "unsafe_false_flags": unsafe_false,
        "unsafe_true_flags": unsafe_true,
        "must_not_claim": must_not_claim,
    }


def build_six_room_real_surface_acceptance_matrix():
    records = []
    for room_key in SIX_ROOM_REAL_SURFACE_ORDER:
        records.append(_room_acceptance_record(room_key))
    return records


def build_six_room_real_surface_acceptance_bundle():
    matrix = build_six_room_real_surface_acceptance_matrix()
    accepted_rooms = []
    blocked_rooms = []

    for record in matrix:
        if record["accepted"]:
            accepted_rooms.append(record["room"])
        else:
            blocked_rooms.append(record["room"])

    accepted = len(accepted_rooms) == len(SIX_ROOM_REAL_SURFACE_ORDER) and not blocked_rooms
    adapter = build_real_surface_adapter_contract()

    return {
        "package": SIX_ROOM_REAL_SURFACE_ACCEPTANCE_IDENTITY["package"],
        "display_title": SIX_ROOM_REAL_SURFACE_ACCEPTANCE_IDENTITY["display_title"],
        "decision": SIX_ROOM_REAL_SURFACE_ACCEPTANCE_IDENTITY["decision"],
        "accepted": accepted,
        "room_order": list(SIX_ROOM_REAL_SURFACE_ORDER),
        "accepted_rooms": accepted_rooms,
        "blocked_rooms": blocked_rooms,
        "matrix": matrix,
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(SIX_ROOM_NOT_AUTHORIZED),
        "surface_status": {
            "six_room_real_surface_acceptance_ready": accepted,
            "all_six_rooms_present": len(matrix) == 6,
            "all_registry_routes_match": all(r["route_matches_registry"] for r in matrix),
            "all_registry_components_match": all(r["component_matches_registry"] for r in matrix),
            "all_data_adapters_match": all(r["data_adapter_matches_registry"] for r in matrix),
            "all_routes_protected": all(r["protected_route_policy_matches"] for r in matrix),
            "anonymous_access_allowed": False,
            "owner_session_required": True,
            "staging_ready": False,
            "production_deploy_enabled": False,
            "broker_submission_enabled": False,
            "real_capital_movement_enabled": False,
            "direct_execution_enabled": False,
            "automated_execution_enabled": False,
            "permission_mutation_enabled": False,
            "secret_reveal_enabled": False,
            "live_auto_locked": True,
        },
        "next_build": "OB owner experience integration closeout / GP009",
    }


def build_six_room_real_surface_acceptance_handoff():
    bundle = build_six_room_real_surface_acceptance_bundle()
    summary = []

    for record in bundle["matrix"]:
        summary.append(
            {
                "room": record["room"],
                "route_hint": record["route_hint"],
                "component_hint": record["component_hint"],
                "data_adapter_hint": record["data_adapter_hint"],
                "accepted": record["accepted"],
            }
        )

    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "accepted": bundle["accepted"],
        "accepted_rooms": bundle["accepted_rooms"],
        "blocked_rooms": bundle["blocked_rooms"],
        "takeover_summary": (
            "GP008 accepts the six OB protected rooms as real-surface adapter contracts. "
            "This is an internal acceptance layer only and does not authorize staging "
            "readiness or dangerous actions."
        ),
        "registry_summary": summary,
        "safety_summary": bundle["safety_summary"],
        "surface_status": bundle["surface_status"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "next_builder_notes": [
            "Six real-surface adapters are accepted as route-ready contracts.",
            "Keep Tower as the owner access and session boundary.",
            "Do not claim STAGING_READY.",
            "Do not redeploy Render from this package.",
            "Do not mark owner walkthrough accepted from this package.",
            "Do not claim Tower return/session continuity repaired from this package.",
            "Keep broker submission locked.",
            "Keep real capital movement locked.",
            "Keep direct execution disabled.",
            "Keep automated execution disabled.",
            "Keep permission mutations disabled.",
            "Keep secret reveal disabled.",
            "Keep Live Auto locked.",
            "Next build is GP009 owner-experience integration closeout.",
        ],
    }
