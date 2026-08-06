# Symbol Page real surface wiring adapter for The Observatory.
#
# GP004 acceptance question:
#
#   Can the real OB app wire Symbol Page as Asset Storybook safely?
#
# This adapter derives section order and headings from the existing Symbol
# Page contract so it does not guess or rename canonical keys. Friendly UI
# component hints are mapped on top of those canonical contract keys.

from copy import deepcopy

from .symbol_page import (
    SYMBOL_PAGE_IDENTITY,
    SYMBOL_PAGE_SECTION_HEADINGS,
    SYMBOL_PAGE_SURFACE_ORDER,
    empty_symbol_page_surface,
)
from .ui_surface_registry import (
    MUST_NOT_CLAIM,
    OB_REAL_SURFACE_THEME,
    PROTECTED_ROUTE_POLICY,
    build_real_surface_adapter_contract,
    build_surface_registry_entry,
)


SYMBOL_PAGE_REAL_SURFACE_IDENTITY = {
    "package": "ob_symbol_page_real_surface_wiring_gp004",
    "room": "symbol_page",
    "display_title": "Asset Storybook",
    "emoji": "🔎",
    "primary_question": "What do I need to understand about this asset?",
    "decision": "READY_FOR_SYMBOL_PAGE_REAL_SURFACE_WIRING_WITH_SAFETY_LOCKS_HELD",
    "plain_language": (
        "Symbol Page can now be wired as a real owner-facing Asset Storybook "
        "surface using the simplified asset story contract."
    ),
}

SYMBOL_PAGE_COMPONENT_HINTS = {
    "hero": "AssetStorybookHeroCard",
    "soulaana": "AssetStorybookSoulaanaCard",
    "story": "AssetStorybookNarrativeCard",
    "asset_story": "AssetStorybookNarrativeCard",
    "asset_context": "AssetStorybookNarrativeCard",
    "risk": "AssetStorybookRiskBeforeShineCard",
    "risk_before_shine": "AssetStorybookRiskBeforeShineCard",
    "decision": "AssetStorybookDecisionPostureCard",
    "decision_posture": "AssetStorybookDecisionPostureCard",
    "signals": "AssetStorybookTinySignalsStrip",
    "indicators": "AssetStorybookTinySignalsStrip",
    "tiny_signals": "AssetStorybookTinySignalsStrip",
    "tiny_asset_signals": "AssetStorybookTinySignalsStrip",
    "drawers": "AssetStorybookDetailDrawerGroup",
    "details": "AssetStorybookDetailDrawerGroup",
    "detail_drawers": "AssetStorybookDetailDrawerGroup",
    "owner_drawer": "AssetStorybookOwnerDrawer",
            "thesis": "AssetStorybookNarrativeCard",
            "asset_thesis": "AssetStorybookNarrativeCard",
}

SYMBOL_PAGE_DATA_PATHS = {
    "hero": ["symbol", "display_symbol", "dominant_summary", "critical_indicators"],
    "soulaana": ["soulaana"],
    "story": ["asset_story", "story", "thesis", "summary"],
    "asset_story": ["asset_story", "story", "thesis", "summary"],
    "asset_context": ["asset_story", "story", "thesis", "summary"],
    "risk": ["risk_summary", "risk", "warnings"],
    "risk_before_shine": ["risk_summary", "risk", "warnings"],
    "decision": ["decision_state", "decision_label", "decision_posture", "next_action"],
    "decision_posture": ["decision_state", "decision_label", "decision_posture", "next_action"],
    "signals": ["tiny_signals", "asset_indicators", "evidence"],
    "indicators": ["tiny_signals", "asset_indicators", "evidence"],
    "tiny_signals": ["tiny_signals", "asset_indicators", "evidence"],
    "tiny_asset_signals": ["tiny_signals", "asset_indicators", "evidence"],
    "drawers": ["drawers", "detail_drawers", "details_hidden_by_default"],
    "details": ["drawers", "detail_drawers", "details_hidden_by_default"],
    "detail_drawers": ["drawers", "detail_drawers", "details_hidden_by_default"],
    "owner_drawer": ["owner_controls", "owner_drawer_default_state"],
            "thesis": ["asset_story", "story", "thesis", "summary"],
            "asset_thesis": ["asset_story", "story", "thesis", "summary"],
}

SYMBOL_PAGE_COLLAPSED_KEYS = [
    key
    for key in SYMBOL_PAGE_SURFACE_ORDER
    if "drawer" in key or "detail" in key or key in {"drawers", "details"}
]

SYMBOL_PAGE_FIRST_GLANCE_KEYS = [
    key
    for key in SYMBOL_PAGE_SURFACE_ORDER
    if key not in SYMBOL_PAGE_COLLAPSED_KEYS
]

SYMBOL_PAGE_REAL_SURFACE_STATUS = {
    "contract_ready": True,
    "registry_ready": True,
    "real_surface_adapter_ready": True,
    "symbol_context_route_ready": True,
    "real_html_rendered": False,
    "tower_return_repaired": False,
    "render_redeployed": False,
    "owner_walkthrough_accepted": False,
    "staging_ready": False,
}


def _heading_for(section_key):
    heading = SYMBOL_PAGE_SECTION_HEADINGS.get(section_key, {})

    return {
        "label": heading.get("label", section_key.replace("_", " ").title()),
        "plain_label": heading.get("plain_label", section_key.replace("_", " ").title()),
        "explainer": heading.get("explainer", ""),
    }


def _component_hint_for(section_key):
    return SYMBOL_PAGE_COMPONENT_HINTS.get(
        section_key,
        "AssetStorybook" + section_key.replace("_", " ").title().replace(" ", "") + "Section",
    )


def _data_paths_for(section_key):
    return list(
        SYMBOL_PAGE_DATA_PATHS.get(section_key, [section_key])
    )


def normalize_symbol(value):
    symbol = str(value or "UNKNOWN").strip().upper()

    if not symbol:
        return "UNKNOWN"

    return symbol


def build_symbol_context(symbol="UNKNOWN"):
    normalized = normalize_symbol(symbol)

    return {
        "symbol": normalized,
        "route_param": normalized,
        "display_symbol": normalized,
        "symbol_required": True,
        "destination_only": True,
        "safe_fallback_route": "/ob/market-map",
    }


def normalize_symbol_page_surface_payload(surface_payload=None, symbol="UNKNOWN"):
    if surface_payload is None:
        try:
            surface = empty_symbol_page_surface(symbol=symbol)
        except TypeError:
            surface = empty_symbol_page_surface()
    else:
        surface = deepcopy(surface_payload)

    context = build_symbol_context(
        surface.get("symbol")
        or surface.get("display_symbol")
        or symbol
    )

    surface.setdefault("room", "symbol_page")
    surface.setdefault("display_title", "Asset Storybook")
    surface.setdefault(
        "question_answered",
        "What do I need to understand about this asset?",
    )
    surface.setdefault("section_headings", deepcopy(SYMBOL_PAGE_SECTION_HEADINGS))
    surface.setdefault("surface_order", list(SYMBOL_PAGE_SURFACE_ORDER))
    surface.setdefault("details_hidden_by_default", True)
    surface.setdefault("owner_drawer_default_state", "collapsed")
    surface.setdefault("symbol", context["symbol"])
    surface.setdefault("display_symbol", context["display_symbol"])
    surface.setdefault("symbol_context", context)

    return surface


def build_symbol_page_section_component(section_key, surface_payload=None, symbol="UNKNOWN"):
    surface = normalize_symbol_page_surface_payload(surface_payload, symbol=symbol)
    key = str(section_key or "").strip()

    if key not in SYMBOL_PAGE_SURFACE_ORDER:
        raise KeyError("Unknown Symbol Page section: " + str(section_key))

    heading = _heading_for(key)
    default_state = "collapsed" if key in SYMBOL_PAGE_COLLAPSED_KEYS else "visible"

    return {
        "section_key": key,
        "component_hint": _component_hint_for(key),
        "heading": heading["label"],
        "plain_heading": heading["plain_label"],
        "explainer": heading["explainer"],
        "data_paths": _data_paths_for(key),
        "first_glance": key in SYMBOL_PAGE_FIRST_GLANCE_KEYS,
        "default_state": default_state,
        "source_room": surface["room"],
        "source_display_title": surface["display_title"],
        "symbol_context": deepcopy(surface["symbol_context"]),
    }


def build_symbol_page_component_tree(surface_payload=None, symbol="UNKNOWN"):
    surface = normalize_symbol_page_surface_payload(surface_payload, symbol=symbol)

    return [
        build_symbol_page_section_component(section_key, surface, symbol=symbol)
        for section_key in surface["surface_order"]
    ]


def build_symbol_page_loading_state(symbol="UNKNOWN"):
    context = build_symbol_context(symbol)

    return {
        "state": "loading",
        "display_title": "Asset Storybook",
        "symbol_context": context,
        "message": "Opening the asset storybook for " + context["display_symbol"] + "...",
        "show_soulaana_placeholder": True,
        "show_skeleton_cards": [
            "AssetStorybookHeroCard",
            "AssetStorybookSoulaanaCard",
            "AssetStorybookNarrativeCard",
            "AssetStorybookRiskBeforeShineCard",
            "AssetStorybookDecisionPostureCard",
            "AssetStorybookTinySignalsStrip",
        ],
        "dangerous_actions_available": False,
    }


def build_symbol_page_empty_state(symbol="UNKNOWN"):
    context = build_symbol_context(symbol)

    return {
        "state": "empty",
        "display_title": "Asset Storybook",
        "symbol_context": context,
        "message": "No asset story is ready for " + context["display_symbol"] + " yet.",
        "soulaana_hint": "Return to Market Weather or wait for a fresh symbol read.",
        "next_action": "Return to Market Weather.",
        "details_hidden_by_default": True,
        "dangerous_actions_available": False,
    }


def build_symbol_page_error_state(
    error_message="Asset Storybook data could not be loaded.",
    symbol="UNKNOWN",
):
    context = build_symbol_context(symbol)

    return {
        "state": "error",
        "display_title": "Asset Storybook",
        "symbol_context": context,
        "message": str(error_message or "Asset Storybook data could not be loaded."),
        "safe_fallback": "Return to Market Weather or Owner Console.",
        "show_market_map_link": True,
        "show_owner_console_link": True,
        "dangerous_actions_available": False,
        "broker_submission_enabled": False,
        "real_capital_movement_enabled": False,
        "live_auto_locked": True,
    }


def build_symbol_page_real_surface(surface_payload=None, symbol="UNKNOWN"):
    surface = normalize_symbol_page_surface_payload(surface_payload, symbol=symbol)
    registry_entry = build_surface_registry_entry("symbol_page")
    adapter_contract = build_real_surface_adapter_contract()

    return {
        "package": SYMBOL_PAGE_REAL_SURFACE_IDENTITY["package"],
        "room": "symbol_page",
        "display_title": SYMBOL_PAGE_REAL_SURFACE_IDENTITY["display_title"],
        "primary_question": SYMBOL_PAGE_REAL_SURFACE_IDENTITY["primary_question"],
        "decision": SYMBOL_PAGE_REAL_SURFACE_IDENTITY["decision"],
        "route_hint": registry_entry["route_hint"],
        "component_hint": registry_entry["component_hint"],
        "data_adapter_hint": registry_entry["data_adapter_hint"],
        "symbol_context": deepcopy(surface["symbol_context"]),
        "source_contract": deepcopy(surface),
        "registry_entry": deepcopy(registry_entry),
        "component_tree": build_symbol_page_component_tree(surface, symbol=surface["symbol"]),
        "first_glance_components": [
            _component_hint_for(key)
            for key in SYMBOL_PAGE_FIRST_GLANCE_KEYS
        ],
        "collapsed_components": [
            _component_hint_for(key)
            for key in SYMBOL_PAGE_COLLAPSED_KEYS
        ],
        "loading_state": build_symbol_page_loading_state(surface["symbol"]),
        "empty_state": build_symbol_page_empty_state(surface["symbol"]),
        "error_state": build_symbol_page_error_state(symbol=surface["symbol"]),
        "theme": deepcopy(OB_REAL_SURFACE_THEME),
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "surface_status": deepcopy(SYMBOL_PAGE_REAL_SURFACE_STATUS),
        "safety_summary": deepcopy(adapter_contract["safety_summary"]),
        "soulaana": surface.get("soulaana", {}),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "next_build": "OB Trade Center real surface wiring / GP005",
    }


def build_symbol_page_real_surface_acceptance_contract():
    real_surface = build_symbol_page_real_surface(symbol="AAPL")

    return {
        "package": SYMBOL_PAGE_REAL_SURFACE_IDENTITY["package"],
        "room": "symbol_page",
        "display_title": SYMBOL_PAGE_REAL_SURFACE_IDENTITY["display_title"],
        "primary_question": SYMBOL_PAGE_REAL_SURFACE_IDENTITY["primary_question"],
        "decision": SYMBOL_PAGE_REAL_SURFACE_IDENTITY["decision"],
        "route_hint": real_surface["route_hint"],
        "component_hint": real_surface["component_hint"],
        "symbol_context_required": True,
        "must_show_at_first_glance": [
            "AssetStorybookHeroCard",
            "AssetStorybookSoulaanaCard",
            "AssetStorybookNarrativeCard",
            "AssetStorybookRiskBeforeShineCard",
            "AssetStorybookDecisionPostureCard",
            "AssetStorybookTinySignalsStrip",
        ],
        "must_hide_by_default": [
            "AssetStorybookDetailDrawerGroup",
            "AssetStorybookOwnerDrawer",
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


def build_symbol_page_real_surface_takeover_handoff():
    contract = build_symbol_page_real_surface_acceptance_contract()

    return {
        "package": contract["package"],
        "display_title": contract["display_title"],
        "takeover_summary": (
            "GP004 wired Symbol Page as a real-app surface adapter. The next "
            "builder should connect AssetStorybookSurface and related cards "
            "to actual templates without changing doctrine or unlocking safety gates."
        ),
        "route_hint": contract["route_hint"],
        "symbol_context_required": True,
        "component_tree": build_symbol_page_component_tree(symbol="AAPL"),
        "loading_state": build_symbol_page_loading_state("AAPL"),
        "empty_state": build_symbol_page_empty_state("AAPL"),
        "error_state": build_symbol_page_error_state(symbol="AAPL"),
        "safety_summary": contract["safety_summary"],
        "must_not_claim": contract["must_not_claim"],
        "next_builder_notes": [
            "Use AssetStorybookHeroCard for the first card.",
            "Keep Soulaana near the top.",
            "Show story, risk, and decision posture before raw chart/news detail.",
            "Keep symbol context required and destination-only.",
            "Keep detail drawers collapsed by default.",
            "Keep broker submission locked.",
            "Keep real capital movement locked.",
            "Keep Live Auto locked.",
            "Do not claim STAGING_READY.",
            "Next build is GP005 Trade Center real surface wiring.",
        ],
    }
