# Dashboard real surface wiring adapter for The Observatory.
#
# GP002 acceptance question:
#
#   Can the real OB app wire Dashboard as Today’s Command Nest safely?
#
# This adapter intentionally derives its section order from the existing
# Dashboard contract. The Dashboard contract uses canonical keys such as
# `indicators` and `drawers`; the UI adapter maps those keys to friendly
# component names like DashboardTinySignalsStrip and DashboardDetailsDrawerGroup.

from copy import deepcopy

from .dashboard import (
    DASHBOARD_PAGE_IDENTITY,
    DASHBOARD_SECTION_HEADINGS,
    DASHBOARD_SURFACE_ORDER,
    empty_dashboard_surface,
)
from .ui_surface_registry import (
    MUST_NOT_CLAIM,
    OB_REAL_SURFACE_THEME,
    PROTECTED_ROUTE_POLICY,
    build_real_surface_adapter_contract,
    build_surface_registry_entry,
)


DASHBOARD_REAL_SURFACE_IDENTITY = {
    "package": "ob_dashboard_real_surface_wiring_gp002",
    "room": "dashboard",
    "display_title": "Today’s Command Nest",
    "emoji": "🌙",
    "primary_question": "What needs my attention today?",
    "decision": "READY_FOR_DASHBOARD_REAL_SURFACE_WIRING_WITH_SAFETY_LOCKS_HELD",
    "plain_language": (
        "Dashboard can now be wired as a real owner-facing surface using "
        "the simplified Today’s Command Nest contract."
    ),
}

DASHBOARD_COMPONENT_HINTS = {
    "hero": "DashboardHeroCard",
    "soulaana": "DashboardSoulaanaCard",
    "attention": "DashboardNeedsYourEyesList",
    "indicators": "DashboardTinySignalsStrip",
    "tiny_signals": "DashboardTinySignalsStrip",
    "next_action": "DashboardOwnerNextMoveCard",
    "owner_next_move": "DashboardOwnerNextMoveCard",
    "drawers": "DashboardDetailsDrawerGroup",
    "details": "DashboardDetailsDrawerGroup",
    "owner_drawer": "DashboardOwnerDrawer",
}

DASHBOARD_DATA_PATHS = {
    "hero": ["dominant_summary", "critical_indicators"],
    "soulaana": ["soulaana"],
    "attention": ["attention_queue", "needs_attention", "visible_attention_items"],
    "indicators": ["tiny_signals", "quiet_signals", "evidence", "critical_indicators"],
    "tiny_signals": ["tiny_signals", "quiet_signals", "evidence"],
    "next_action": ["next_action", "principal_recommendation"],
    "owner_next_move": ["next_action", "principal_recommendation"],
    "drawers": ["drawers", "hidden_detail_count", "details_hidden_by_default"],
    "details": ["drawers", "hidden_detail_count", "details_hidden_by_default"],
    "owner_drawer": ["owner_controls", "owner_drawer_default_state"],
}

DASHBOARD_COLLAPSED_KEYS = [
    key
    for key in ["drawers", "details", "owner_drawer"]
    if key in DASHBOARD_SURFACE_ORDER
]

DASHBOARD_FIRST_GLANCE_KEYS = [
    key
    for key in DASHBOARD_SURFACE_ORDER
    if key not in DASHBOARD_COLLAPSED_KEYS
]

DASHBOARD_REAL_SURFACE_STATUS = {
    "contract_ready": True,
    "registry_ready": True,
    "real_surface_adapter_ready": True,
    "real_html_rendered": False,
    "tower_return_repaired": False,
    "render_redeployed": False,
    "owner_walkthrough_accepted": False,
    "staging_ready": False,
}


def _heading_for(section_key):
    heading = DASHBOARD_SECTION_HEADINGS.get(section_key, {})

    return {
        "label": heading.get("label", section_key.replace("_", " ").title()),
        "plain_label": heading.get("plain_label", section_key.replace("_", " ").title()),
        "explainer": heading.get("explainer", ""),
    }


def _component_hint_for(section_key):
    return DASHBOARD_COMPONENT_HINTS.get(
        section_key,
        "Dashboard" + section_key.replace("_", " ").title().replace(" ", "") + "Section",
    )


def _data_paths_for(section_key):
    return list(
        DASHBOARD_DATA_PATHS.get(section_key, [section_key])
    )


def normalize_dashboard_surface_payload(surface_payload=None):
    if surface_payload is None:
        surface = empty_dashboard_surface()
    else:
        surface = deepcopy(surface_payload)

    surface.setdefault("room", "dashboard")
    surface.setdefault("display_title", "Today’s Command Nest")
    surface.setdefault("question_answered", "What needs my attention today?")
    surface.setdefault("section_headings", deepcopy(DASHBOARD_SECTION_HEADINGS))
    surface.setdefault("surface_order", list(DASHBOARD_SURFACE_ORDER))
    surface.setdefault("details_hidden_by_default", True)
    surface.setdefault("owner_drawer_default_state", "collapsed")

    return surface


def build_dashboard_section_component(section_key, surface_payload=None):
    surface = normalize_dashboard_surface_payload(surface_payload)
    key = str(section_key or "").strip()

    if key not in DASHBOARD_SURFACE_ORDER:
        raise KeyError("Unknown Dashboard section: " + str(section_key))

    heading = _heading_for(key)
    default_state = "collapsed" if key in DASHBOARD_COLLAPSED_KEYS else "visible"

    return {
        "section_key": key,
        "component_hint": _component_hint_for(key),
        "heading": heading["label"],
        "plain_heading": heading["plain_label"],
        "explainer": heading["explainer"],
        "data_paths": _data_paths_for(key),
        "first_glance": key in DASHBOARD_FIRST_GLANCE_KEYS,
        "default_state": default_state,
        "source_room": surface["room"],
        "source_display_title": surface["display_title"],
    }


def build_dashboard_component_tree(surface_payload=None):
    surface = normalize_dashboard_surface_payload(surface_payload)

    return [
        build_dashboard_section_component(section_key, surface)
        for section_key in surface["surface_order"]
    ]


def build_dashboard_loading_state():
    return {
        "state": "loading",
        "display_title": "Today’s Command Nest",
        "message": "Gathering today’s command nest...",
        "show_soulaana_placeholder": True,
        "show_skeleton_cards": [
            "DashboardHeroCard",
            "DashboardSoulaanaCard",
            "DashboardNeedsYourEyesList",
            "DashboardTinySignalsStrip",
            "DashboardOwnerNextMoveCard",
        ],
        "dangerous_actions_available": False,
    }


def build_dashboard_empty_state():
    surface = normalize_dashboard_surface_payload(empty_dashboard_surface())

    return {
        "state": "empty",
        "display_title": "Today’s Command Nest",
        "message": surface.get("dominant_summary", "No owner attention items are waiting."),
        "soulaana": surface.get("soulaana", {}),
        "next_action": surface.get("next_action", "Stay in observation mode."),
        "details_hidden_by_default": True,
        "dangerous_actions_available": False,
    }


def build_dashboard_error_state(error_message="Dashboard data could not be loaded."):
    return {
        "state": "error",
        "display_title": "Today’s Command Nest",
        "message": str(error_message or "Dashboard data could not be loaded."),
        "safe_fallback": "Return to Owner Console or refresh the Dashboard.",
        "show_owner_console_link": True,
        "dangerous_actions_available": False,
        "broker_submission_enabled": False,
        "real_capital_movement_enabled": False,
        "live_auto_locked": True,
    }


def build_dashboard_real_surface(surface_payload=None):
    surface = normalize_dashboard_surface_payload(surface_payload)
    registry_entry = build_surface_registry_entry("dashboard")
    adapter_contract = build_real_surface_adapter_contract()

    return {
        "package": DASHBOARD_REAL_SURFACE_IDENTITY["package"],
        "room": "dashboard",
        "display_title": DASHBOARD_REAL_SURFACE_IDENTITY["display_title"],
        "primary_question": DASHBOARD_REAL_SURFACE_IDENTITY["primary_question"],
        "decision": DASHBOARD_REAL_SURFACE_IDENTITY["decision"],
        "route_hint": registry_entry["route_hint"],
        "component_hint": registry_entry["component_hint"],
        "data_adapter_hint": registry_entry["data_adapter_hint"],
        "source_contract": deepcopy(surface),
        "registry_entry": deepcopy(registry_entry),
        "component_tree": build_dashboard_component_tree(surface),
        "first_glance_components": [
            _component_hint_for(key)
            for key in DASHBOARD_FIRST_GLANCE_KEYS
        ],
        "collapsed_components": [
            _component_hint_for(key)
            for key in DASHBOARD_COLLAPSED_KEYS
        ],
        "loading_state": build_dashboard_loading_state(),
        "empty_state": build_dashboard_empty_state(),
        "error_state": build_dashboard_error_state(),
        "theme": deepcopy(OB_REAL_SURFACE_THEME),
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "surface_status": deepcopy(DASHBOARD_REAL_SURFACE_STATUS),
        "safety_summary": deepcopy(adapter_contract["safety_summary"]),
        "soulaana": surface.get("soulaana", {}),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "next_build": "OB Market Map real surface wiring / GP003",
    }


def build_dashboard_real_surface_acceptance_contract():
    real_surface = build_dashboard_real_surface()

    return {
        "package": DASHBOARD_REAL_SURFACE_IDENTITY["package"],
        "room": "dashboard",
        "display_title": DASHBOARD_REAL_SURFACE_IDENTITY["display_title"],
        "primary_question": DASHBOARD_REAL_SURFACE_IDENTITY["primary_question"],
        "decision": DASHBOARD_REAL_SURFACE_IDENTITY["decision"],
        "route_hint": real_surface["route_hint"],
        "component_hint": real_surface["component_hint"],
        "must_show_at_first_glance": [
            "DashboardHeroCard",
            "DashboardSoulaanaCard",
            "DashboardNeedsYourEyesList",
            "DashboardTinySignalsStrip",
            "DashboardOwnerNextMoveCard",
        ],
        "must_hide_by_default": [
            "DashboardDetailsDrawerGroup",
            "DashboardOwnerDrawer",
        ],
        "must_include_states": [
            "loading",
            "empty",
            "error",
        ],
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(real_surface["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
    }


def build_dashboard_real_surface_takeover_handoff():
    contract = build_dashboard_real_surface_acceptance_contract()

    return {
        "package": contract["package"],
        "display_title": contract["display_title"],
        "takeover_summary": (
            "GP002 wired Dashboard as a real-app surface adapter. The next "
            "builder should connect DashboardTodayCommandNest and related "
            "components to actual templates without changing doctrine or "
            "unlocking safety gates."
        ),
        "route_hint": contract["route_hint"],
        "component_tree": build_dashboard_component_tree(),
        "loading_state": build_dashboard_loading_state(),
        "empty_state": build_dashboard_empty_state(),
        "error_state": build_dashboard_error_state(),
        "safety_summary": contract["safety_summary"],
        "must_not_claim": contract["must_not_claim"],
        "next_builder_notes": [
            "Use DashboardHeroCard for the first card.",
            "Keep Soulaana near the top.",
            "Keep Needs Your Eyes limited and owner-readable.",
            "Keep Tiny Signals small.",
            "Keep Details and Owner Drawer collapsed by default.",
            "Keep broker submission locked.",
            "Keep real capital movement locked.",
            "Keep Live Auto locked.",
            "Do not claim STAGING_READY.",
            "Next build is GP003 Market Map real surface wiring.",
        ],
    }
