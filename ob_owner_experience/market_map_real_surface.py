# Market Map real surface wiring adapter for The Observatory.
#
# GP003 acceptance question:
#
#   Can the real OB app wire Market Map as Market Weather safely?
#
# This adapter derives section order and headings from the existing Market
# Map contract so it does not guess or rename canonical keys. Friendly UI
# component hints are mapped on top of those canonical contract keys.

from copy import deepcopy

from .market_map import (
    MARKET_MAP_DEEP_DIVE_ROOM_CONFIGS,
    MARKET_MAP_PAGE_IDENTITY,
    MARKET_MAP_SECTION_HEADINGS,
    MARKET_MAP_SURFACE_ORDER,
)
from .ui_surface_registry import (
    MUST_NOT_CLAIM,
    OB_REAL_SURFACE_THEME,
    PROTECTED_ROUTE_POLICY,
    build_real_surface_adapter_contract,
    build_surface_registry_entry,
)


MARKET_MAP_REAL_SURFACE_IDENTITY = {
    "package": "ob_market_map_real_surface_wiring_gp003",
    "room": "market_map",
    "display_title": "Market Weather",
    "emoji": "🌦️",
    "primary_question": "What is happening in the market?",
    "decision": "READY_FOR_MARKET_MAP_REAL_SURFACE_WIRING_WITH_SAFETY_LOCKS_HELD",
    "plain_language": (
        "Market Map can now be wired as a real owner-facing Market Weather "
        "surface using the simplified first-glance contract and deep-dive rooms."
    ),
}

MARKET_MAP_COMPONENT_HINTS = {
    "hero": "MarketWeatherHeroCard",
    "soulaana": "MarketWeatherSoulaanaCard",
    "risk": "MarketWeatherRiskFirstCard",
    "risk_first": "MarketWeatherRiskFirstCard",
    "movement": "MarketWeatherBiggestMovementCard",
    "biggest_movement": "MarketWeatherBiggestMovementCard",
    "opportunities": "MarketWeatherOpportunityGarden",
    "strongest_opportunities": "MarketWeatherOpportunityGarden",
    "warnings": "MarketWeatherWatchYourStepCard",
    "watch_your_step": "MarketWeatherWatchYourStepCard",
    "deep_dives": "MarketWeatherDeepDiveRoomTabs",
    "deep_dive_rooms": "MarketWeatherDeepDiveRoomTabs",
    "owner_drawer": "MarketWeatherOwnerDrawer",
}

MARKET_MAP_DATA_PATHS = {
    "hero": ["market_summary", "dominant_summary", "critical_indicators"],
    "soulaana": ["soulaana"],
    "risk": ["risk_summary", "risk_first", "warnings"],
    "risk_first": ["risk_summary", "risk_first", "warnings"],
    "movement": ["biggest_movement", "movement", "market_signals"],
    "biggest_movement": ["biggest_movement", "movement", "market_signals"],
    "opportunities": ["opportunities", "strongest_opportunities", "market_signals"],
    "strongest_opportunities": ["opportunities", "strongest_opportunities", "market_signals"],
    "warnings": ["warnings", "watch_your_step", "risk_summary"],
    "watch_your_step": ["warnings", "watch_your_step", "risk_summary"],
    "deep_dives": ["deep_dive_rooms", "deep_dive_cards", "drawers"],
    "deep_dive_rooms": ["deep_dive_rooms", "deep_dive_cards", "drawers"],
    "owner_drawer": ["owner_controls", "owner_drawer_default_state"],
}

MARKET_MAP_COLLAPSED_KEYS = [
    key
    for key in MARKET_MAP_SURFACE_ORDER
    if "deep" in key or "drawer" in key or key in {"drawers", "details"}
]

MARKET_MAP_FIRST_GLANCE_KEYS = [
    key
    for key in MARKET_MAP_SURFACE_ORDER
    if key not in MARKET_MAP_COLLAPSED_KEYS
]

MARKET_MAP_REAL_SURFACE_STATUS = {
    "contract_ready": True,
    "registry_ready": True,
    "real_surface_adapter_ready": True,
    "deep_dive_rooms_tab_ready": True,
    "real_html_rendered": False,
    "tower_return_repaired": False,
    "render_redeployed": False,
    "owner_walkthrough_accepted": False,
    "staging_ready": False,
}


def _heading_for(section_key):
    heading = MARKET_MAP_SECTION_HEADINGS.get(section_key, {})

    return {
        "label": heading.get("label", section_key.replace("_", " ").title()),
        "plain_label": heading.get("plain_label", section_key.replace("_", " ").title()),
        "explainer": heading.get("explainer", ""),
    }


def _component_hint_for(section_key):
    return MARKET_MAP_COMPONENT_HINTS.get(
        section_key,
        "MarketWeather" + section_key.replace("_", " ").title().replace(" ", "") + "Section",
    )


def _data_paths_for(section_key):
    return list(
        MARKET_MAP_DATA_PATHS.get(section_key, [section_key])
    )


def _deep_dive_id_from_config(config_item):
    if isinstance(config_item, dict):
        return str(
            config_item.get("room_id")
            or config_item.get("id")
            or config_item.get("key")
            or config_item.get("title")
            or "deep_dive"
        )

    return str(config_item or "deep_dive")


def _deep_dive_title_from_config(config_item):
    if isinstance(config_item, dict):
        return str(
            config_item.get("display_title")
            or config_item.get("title")
            or config_item.get("label")
            or config_item.get("room_id")
            or "Deep Dive"
        )

    return str(config_item or "Deep Dive").replace("_", " ").title()


def _iter_deep_dive_configs():
    configs = MARKET_MAP_DEEP_DIVE_ROOM_CONFIGS

    if isinstance(configs, dict):
        return list(configs.values())

    return list(configs)


def build_market_deep_dive_room_tabs():
    tabs = []

    for index, config in enumerate(_iter_deep_dive_configs()):
        room_id = _deep_dive_id_from_config(config)
        title = _deep_dive_title_from_config(config)

        tabs.append(
            {
                "tab_index": index + 1,
                "room_id": room_id,
                "display_title": title,
                "component_hint": (
                    "MarketWeather"
                    + room_id.replace("_", " ").replace("-", " ").title().replace(" ", "")
                    + "Tab"
                ),
                "default_state": "collapsed",
                "owner_opens_when_needed": True,
            }
        )

    return tabs


def normalize_market_map_surface_payload(surface_payload=None):
    if surface_payload is None:
        surface = {
            "room": "market_map",
            "display_title": "Market Weather",
            "question_answered": "What is happening in the market?",
            "section_headings": deepcopy(MARKET_MAP_SECTION_HEADINGS),
            "surface_order": list(MARKET_MAP_SURFACE_ORDER),
            "details_hidden_by_default": True,
            "owner_drawer_default_state": "collapsed",
            "deep_dive_rooms": build_market_deep_dive_room_tabs(),
            "dominant_summary": "Market Weather is ready for a fresh market read.",
            "next_action": "Review risk first, then open deep dives only if needed.",
            "soulaana": {},
        }
    else:
        surface = deepcopy(surface_payload)

    surface.setdefault("room", "market_map")
    surface.setdefault("display_title", "Market Weather")
    surface.setdefault("question_answered", "What is happening in the market?")
    surface.setdefault("section_headings", deepcopy(MARKET_MAP_SECTION_HEADINGS))
    surface.setdefault("surface_order", list(MARKET_MAP_SURFACE_ORDER))
    surface.setdefault("details_hidden_by_default", True)
    surface.setdefault("owner_drawer_default_state", "collapsed")
    surface.setdefault("deep_dive_rooms", build_market_deep_dive_room_tabs())

    return surface


def build_market_map_section_component(section_key, surface_payload=None):
    surface = normalize_market_map_surface_payload(surface_payload)
    key = str(section_key or "").strip()

    if key not in MARKET_MAP_SURFACE_ORDER:
        raise KeyError("Unknown Market Map section: " + str(section_key))

    heading = _heading_for(key)
    default_state = "collapsed" if key in MARKET_MAP_COLLAPSED_KEYS else "visible"

    return {
        "section_key": key,
        "component_hint": _component_hint_for(key),
        "heading": heading["label"],
        "plain_heading": heading["plain_label"],
        "explainer": heading["explainer"],
        "data_paths": _data_paths_for(key),
        "first_glance": key in MARKET_MAP_FIRST_GLANCE_KEYS,
        "default_state": default_state,
        "source_room": surface["room"],
        "source_display_title": surface["display_title"],
    }


def build_market_map_component_tree(surface_payload=None):
    surface = normalize_market_map_surface_payload(surface_payload)

    return [
        build_market_map_section_component(section_key, surface)
        for section_key in surface["surface_order"]
    ]


def build_market_map_loading_state():
    return {
        "state": "loading",
        "display_title": "Market Weather",
        "message": "Reading the market weather...",
        "show_soulaana_placeholder": True,
        "show_skeleton_cards": [
            "MarketWeatherHeroCard",
            "MarketWeatherSoulaanaCard",
            "MarketWeatherRiskFirstCard",
            "MarketWeatherBiggestMovementCard",
            "MarketWeatherOpportunityGarden",
            "MarketWeatherWatchYourStepCard",
        ],
        "dangerous_actions_available": False,
    }


def build_market_map_empty_state():
    return {
        "state": "empty",
        "display_title": "Market Weather",
        "message": "No market weather read is ready yet.",
        "soulaana_hint": "Stay in observation mode until the next market read arrives.",
        "next_action": "Wait for a fresh market read or open Dashboard.",
        "deep_dive_rooms_available": True,
        "deep_dive_rooms_default_state": "collapsed",
        "dangerous_actions_available": False,
    }


def build_market_map_error_state(error_message="Market Weather data could not be loaded."):
    return {
        "state": "error",
        "display_title": "Market Weather",
        "message": str(error_message or "Market Weather data could not be loaded."),
        "safe_fallback": "Return to Dashboard or Owner Console.",
        "show_dashboard_link": True,
        "show_owner_console_link": True,
        "dangerous_actions_available": False,
        "broker_submission_enabled": False,
        "real_capital_movement_enabled": False,
        "live_auto_locked": True,
    }


def build_market_map_real_surface(surface_payload=None):
    surface = normalize_market_map_surface_payload(surface_payload)
    registry_entry = build_surface_registry_entry("market_map")
    adapter_contract = build_real_surface_adapter_contract()

    return {
        "package": MARKET_MAP_REAL_SURFACE_IDENTITY["package"],
        "room": "market_map",
        "display_title": MARKET_MAP_REAL_SURFACE_IDENTITY["display_title"],
        "primary_question": MARKET_MAP_REAL_SURFACE_IDENTITY["primary_question"],
        "decision": MARKET_MAP_REAL_SURFACE_IDENTITY["decision"],
        "route_hint": registry_entry["route_hint"],
        "component_hint": registry_entry["component_hint"],
        "data_adapter_hint": registry_entry["data_adapter_hint"],
        "source_contract": deepcopy(surface),
        "registry_entry": deepcopy(registry_entry),
        "component_tree": build_market_map_component_tree(surface),
        "first_glance_components": [
            _component_hint_for(key)
            for key in MARKET_MAP_FIRST_GLANCE_KEYS
        ],
        "collapsed_components": [
            _component_hint_for(key)
            for key in MARKET_MAP_COLLAPSED_KEYS
        ],
        "deep_dive_room_tabs": build_market_deep_dive_room_tabs(),
        "loading_state": build_market_map_loading_state(),
        "empty_state": build_market_map_empty_state(),
        "error_state": build_market_map_error_state(),
        "theme": deepcopy(OB_REAL_SURFACE_THEME),
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "surface_status": deepcopy(MARKET_MAP_REAL_SURFACE_STATUS),
        "safety_summary": deepcopy(adapter_contract["safety_summary"]),
        "soulaana": surface.get("soulaana", {}),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "next_build": "OB Symbol Page real surface wiring / GP004",
    }


def build_market_map_real_surface_acceptance_contract():
    real_surface = build_market_map_real_surface()

    return {
        "package": MARKET_MAP_REAL_SURFACE_IDENTITY["package"],
        "room": "market_map",
        "display_title": MARKET_MAP_REAL_SURFACE_IDENTITY["display_title"],
        "primary_question": MARKET_MAP_REAL_SURFACE_IDENTITY["primary_question"],
        "decision": MARKET_MAP_REAL_SURFACE_IDENTITY["decision"],
        "route_hint": real_surface["route_hint"],
        "component_hint": real_surface["component_hint"],
        "must_show_at_first_glance": [
            "MarketWeatherHeroCard",
            "MarketWeatherSoulaanaCard",
            "MarketWeatherRiskFirstCard",
            "MarketWeatherBiggestMovementCard",
            "MarketWeatherOpportunityGarden",
            "MarketWeatherWatchYourStepCard",
        ],
        "must_hide_by_default": [
            "MarketWeatherDeepDiveRoomTabs",
            "MarketWeatherOwnerDrawer",
        ],
        "must_include_states": [
            "loading",
            "empty",
            "error",
        ],
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(real_surface["safety_summary"]),
        "deep_dive_room_tabs": real_surface["deep_dive_room_tabs"],
        "must_not_claim": list(MUST_NOT_CLAIM),
    }


def build_market_map_real_surface_takeover_handoff():
    contract = build_market_map_real_surface_acceptance_contract()

    return {
        "package": contract["package"],
        "display_title": contract["display_title"],
        "takeover_summary": (
            "GP003 wired Market Map as a real-app surface adapter. The next "
            "builder should connect MarketWeatherSurface and related cards "
            "to actual templates without changing doctrine or unlocking safety gates."
        ),
        "route_hint": contract["route_hint"],
        "component_tree": build_market_map_component_tree(),
        "deep_dive_room_tabs": contract["deep_dive_room_tabs"],
        "loading_state": build_market_map_loading_state(),
        "empty_state": build_market_map_empty_state(),
        "error_state": build_market_map_error_state(),
        "safety_summary": contract["safety_summary"],
        "must_not_claim": contract["must_not_claim"],
        "next_builder_notes": [
            "Use MarketWeatherHeroCard for the first card.",
            "Keep Soulaana near the top.",
            "Show risk before opportunity.",
            "Keep biggest movement and opportunities owner-readable.",
            "Keep Deep-Dive Rooms collapsed or tab-ready by default.",
            "Keep broker submission locked.",
            "Keep real capital movement locked.",
            "Keep Live Auto locked.",
            "Do not claim STAGING_READY.",
            "Next build is GP004 Symbol Page real surface wiring.",
        ],
    }
