# Six-room real surface registry and UI contract adapter for The Observatory.
#
# This module is UI-framework neutral. It is the first work-ahead bridge
# between the completed owner-experience contracts and the real OB app.
#
# GP001 acceptance question:
#
#   Can the real OB app discover the six simplified owner rooms safely?
#
# This module does not render HTML, call Tower, deploy, submit trades, move
# money, unlock modes, or create secrets. It gives the next builder a stable
# route/component/data manifest for actual UI wiring.

from copy import deepcopy

from .consolidation import (
    SIX_ROOM_ORDER,
    SIX_ROOM_DISPLAY_TITLES,
    SIX_ROOM_PRIMARY_QUESTIONS,
    SIX_ROOM_ROUTE_HINTS,
    build_consolidated_acceptance_contract,
    build_consolidated_safety_summary,
    build_room_card,
    build_six_room_readiness_report,
    six_room_takeover_handoff,
)
from .owner_console import OWNER_GLOBAL_CONTROL_POLICY
from .simplification import (
    DANGEROUS_ACTION_POLICY,
    SOULAANA_GLOBAL_POLICY,
    soulaana_interpretation,
)


UI_SURFACE_REGISTRY_IDENTITY = {
    "package": "ob_six_room_real_surface_registry",
    "display_title": "Six-Room Real Surface Registry",
    "emoji": "🧩",
    "primary_question": (
        "Can the real OB app discover the six simplified owner rooms safely?"
    ),
    "decision": "READY_FOR_OB_UI_WIRING_WITH_SAFETY_LOCKS_HELD",
    "plain_language": (
        "The completed six-room owner-experience contracts are now exposed "
        "through a real-app registry, route manifest, component adapter, "
        "and owner walkthrough hooks."
    ),
}

OB_REAL_SURFACE_THEME = {
    "visual_system": "dark_glass_starfield",
    "background": "black glass / deep violet / star accents",
    "tone": "cute, calm, informative, owner-first",
    "soulaana_position": "visible_near_top",
    "detail_policy": "drawers_or_deep_dives_collapsed_by_default",
    "global_controls_policy": "owner_console_only",
}

ROOM_COMPONENT_HINTS = {
    "dashboard": "DashboardTodayCommandNest",
    "market_map": "MarketWeatherSurface",
    "symbol_page": "AssetStorybookSurface",
    "trade_center": "DecisionGardenSurface",
    "review_center": "ReflectionLibrarySurface",
    "owner_console": "OwnerCrownRoomSurface",
}

ROOM_DATA_ADAPTER_HINTS = {
    "dashboard": "build_dashboard_surface",
    "market_map": "build_market_map_surface",
    "symbol_page": "build_symbol_page_surface",
    "trade_center": "build_trade_center_surface",
    "review_center": "build_review_center_surface",
    "owner_console": "build_owner_console_surface",
}

ROOM_EMPTY_STATE_HINTS = {
    "dashboard": "empty_dashboard_surface",
    "market_map": "build_market_map_surface_with_empty_market_read",
    "symbol_page": "empty_symbol_page_surface",
    "trade_center": "empty_trade_center_surface",
    "review_center": "empty_review_center_surface",
    "owner_console": "empty_owner_console_surface",
}

REAL_SURFACE_STATUS = {
    "contract_ready": True,
    "real_ui_component_wired": False,
    "tower_return_repaired": False,
    "render_redeployed": False,
    "owner_walkthrough_accepted": False,
    "staging_ready": False,
}

PROTECTED_ROUTE_POLICY = {
    "anonymous_access_allowed": False,
    "owner_session_required": True,
    "tower_handoff_required": True,
    "step_up_required_for_dangerous_actions": True,
    "broker_submission_allowed": False,
    "money_movement_allowed": False,
    "live_auto_allowed": False,
}

NEXT_OB_BUILD_ORDER = [
    "GP002 Dashboard real surface wiring",
    "GP003 Market Map real surface wiring",
    "GP004 Symbol Page real surface wiring",
    "GP005 Trade Center real surface wiring",
    "GP006 Review Center real surface wiring",
    "GP007 Owner Console real surface wiring",
    "GP008 visual polish pass",
    "GP009 Tower handoff adapter",
    "GP010 OB pre-integration closeout",
]

MUST_NOT_CLAIM = [
    "STAGING_READY",
    "production deployment authorized",
    "broker submission enabled",
    "real capital movement enabled",
    "Live Auto unlocked",
    "Tower return/session continuity repaired",
    "Render redeployed",
    "owner walkthrough accepted",
]


def normalize_room_id(room_id):
    room = (
        str(room_id or "")
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    if room not in SIX_ROOM_ORDER:
        raise KeyError("Unknown OB real surface room: " + str(room_id))

    return room


def build_surface_registry_entry(room_id):
    room = normalize_room_id(room_id)
    room_card = build_room_card(room)
    headings = room_card["section_headings"]

    hero_heading = headings.get("hero", {}).get("label", "")
    soulaana_heading = headings.get("soulaana", {}).get("label", "")

    return {
        "room": room,
        "display_title": SIX_ROOM_DISPLAY_TITLES[room],
        "primary_question": SIX_ROOM_PRIMARY_QUESTIONS[room],
        "route_hint": SIX_ROOM_ROUTE_HINTS[room],
        "component_hint": ROOM_COMPONENT_HINTS[room],
        "data_adapter_hint": ROOM_DATA_ADAPTER_HINTS[room],
        "empty_state_hint": ROOM_EMPTY_STATE_HINTS[room],
        "hero_heading": hero_heading,
        "soulaana_heading": soulaana_heading,
        "section_keys": list(headings.keys()),
        "section_headings": deepcopy(headings),
        "acceptance_contract": deepcopy(room_card["acceptance_contract"]),
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "surface_status": deepcopy(REAL_SURFACE_STATUS),
        "takeover_summary": room_card["takeover_summary"],
        "next_builder_notes": list(room_card["next_builder_notes"]),
    }


def build_route_manifest():
    return [
        {
            "room": room,
            "route_hint": SIX_ROOM_ROUTE_HINTS[room],
            "display_title": SIX_ROOM_DISPLAY_TITLES[room],
            "component_hint": ROOM_COMPONENT_HINTS[room],
            "owner_session_required": True,
            "anonymous_access_allowed": False,
            "tower_handoff_required": True,
            "dangerous_actions_require_step_up": True,
        }
        for room in SIX_ROOM_ORDER
    ]


def build_owner_walkthrough_hook_manifest():
    return [
        {
            "step": index + 1,
            "room": room,
            "display_title": SIX_ROOM_DISPLAY_TITLES[room],
            "route_hint": SIX_ROOM_ROUTE_HINTS[room],
            "acceptance_hook": "accept_" + room + "_owner_surface",
            "receipt_hook": "receipt_" + room + "_owner_surface",
            "resume_key": "ob_walkthrough_" + room,
            "requires_owner_session": True,
        }
        for index, room in enumerate(SIX_ROOM_ORDER)
    ]


def build_component_adapter_manifest():
    return {
        room: {
            "component_hint": ROOM_COMPONENT_HINTS[room],
            "data_adapter_hint": ROOM_DATA_ADAPTER_HINTS[room],
            "empty_state_hint": ROOM_EMPTY_STATE_HINTS[room],
            "route_hint": SIX_ROOM_ROUTE_HINTS[room],
            "status": "contract_ready_pending_real_component_wiring",
        }
        for room in SIX_ROOM_ORDER
    }


def build_soulaana_surface_summary():
    summary = (
        "Six simplified owner rooms are ready to be wired into real OB surfaces."
    )
    focus = (
        "Start with GP002 Dashboard real surface wiring, then continue room by room."
    )
    next_action = "Wire real UI components to the registry without unlocking safety gates."

    return soulaana_interpretation(
        room="owner_console",
        summary=summary,
        focus=focus,
        next_action=next_action,
        ignore=[
            "production deployment",
            "broker submission",
            "money movement",
            "Live Auto unlock",
            "STAGING_READY",
        ],
    )


def build_real_surface_registry():
    entries = [
        build_surface_registry_entry(room)
        for room in SIX_ROOM_ORDER
    ]

    return {
        "package": UI_SURFACE_REGISTRY_IDENTITY["package"],
        "display_title": UI_SURFACE_REGISTRY_IDENTITY["display_title"],
        "primary_question": UI_SURFACE_REGISTRY_IDENTITY["primary_question"],
        "decision": UI_SURFACE_REGISTRY_IDENTITY["decision"],
        "plain_language": UI_SURFACE_REGISTRY_IDENTITY["plain_language"],
        "room_count": len(entries),
        "room_order": list(SIX_ROOM_ORDER),
        "theme": deepcopy(OB_REAL_SURFACE_THEME),
        "entries": entries,
        "route_manifest": build_route_manifest(),
        "owner_walkthrough_hooks": build_owner_walkthrough_hook_manifest(),
        "safety_summary": build_consolidated_safety_summary(),
        "global_control_policy": deepcopy(OWNER_GLOBAL_CONTROL_POLICY),
        "soulaana_policy": deepcopy(SOULAANA_GLOBAL_POLICY),
        "dangerous_action_policy": deepcopy(DANGEROUS_ACTION_POLICY),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "next_ob_build_order": list(NEXT_OB_BUILD_ORDER),
    }


def build_real_surface_adapter_contract():
    acceptance = build_consolidated_acceptance_contract()
    readiness = build_six_room_readiness_report()
    registry = build_real_surface_registry()

    return {
        "package": UI_SURFACE_REGISTRY_IDENTITY["package"],
        "display_title": UI_SURFACE_REGISTRY_IDENTITY["display_title"],
        "primary_question": UI_SURFACE_REGISTRY_IDENTITY["primary_question"],
        "decision": UI_SURFACE_REGISTRY_IDENTITY["decision"],
        "source_acceptance_package": acceptance["package"],
        "source_acceptance_decision": acceptance["decision"],
        "ready_for_ob_ui_wiring": True,
        "ready_for_tower_integration_review": readiness[
            "ready_for_tower_integration_review"
        ],
        "ready_for_owner_walkthrough": False,
        "staging_ready": False,
        "room_order": list(SIX_ROOM_ORDER),
        "route_manifest": registry["route_manifest"],
        "component_adapter_manifest": build_component_adapter_manifest(),
        "owner_walkthrough_hooks": registry["owner_walkthrough_hooks"],
        "soulaana": build_soulaana_surface_summary(),
        "theme": deepcopy(OB_REAL_SURFACE_THEME),
        "safety_summary": registry["safety_summary"],
        "global_control_policy": deepcopy(OWNER_GLOBAL_CONTROL_POLICY),
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "must_show_for_next_builder": [
            "six room registry",
            "route manifest",
            "component adapter hints",
            "data adapter hints",
            "owner walkthrough hooks",
            "safety summary",
            "must-not-claim list",
        ],
        "must_not_claim": list(MUST_NOT_CLAIM),
        "next_ob_build_order": list(NEXT_OB_BUILD_ORDER),
    }


def build_ui_registry_takeover_handoff():
    contract = build_real_surface_adapter_contract()
    six_room_handoff = six_room_takeover_handoff()

    return {
        "package": contract["package"],
        "display_title": contract["display_title"],
        "takeover_summary": (
            "GP001 created the real-app discovery adapter for the six "
            "simplified OB owner rooms. Use this registry to wire actual "
            "UI components without reopening doctrine or weakening safety locks."
        ),
        "source_six_room_handoff": six_room_handoff["display_title"],
        "room_order": contract["room_order"],
        "component_adapter_manifest": contract["component_adapter_manifest"],
        "route_manifest": contract["route_manifest"],
        "owner_walkthrough_hooks": contract["owner_walkthrough_hooks"],
        "safety_summary": contract["safety_summary"],
        "must_not_claim": contract["must_not_claim"],
        "next_ob_build_order": contract["next_ob_build_order"],
        "next_builder_notes": [
            "Start GP002 with Dashboard real surface wiring.",
            "Use registry entries instead of hard-coded scattered room metadata.",
            "Keep Soulaana visible near the top of each room.",
            "Keep global controls in Owner Console.",
            "Keep protected routes owner-session-only.",
            "Do not claim STAGING_READY.",
            "Do not unlock broker submission.",
            "Do not enable real capital movement.",
            "Do not unlock Live Auto.",
        ],
    }
