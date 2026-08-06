# Six-room owner-experience consolidation for The Observatory.
#
# This module is UI-framework neutral. It closes the first owner-facing
# simplification corridor by turning six separate room contracts into one
# acceptance package that Tower/integration can review.
#
# Consolidated owner-experience target:
#
#   Are the six protected Observatory rooms ready for Tower integration review?
#
# Included rooms:
#
#   1. Dashboard       → Today’s Command Nest
#   2. Market Map      → Market Weather
#   3. Symbol Page     → Asset Storybook
#   4. Trade Center    → Decision Garden
#   5. Review Center   → Reflection Library
#   6. Owner Console   → Owner Crown Room
#
# This consolidation does not deploy, execute trades, submit broker orders,
# move money, unlock Live Auto, or create production access. It creates a
# clear owner-experience acceptance contract for the next build stage.

from copy import deepcopy

from .dashboard import (
    DASHBOARD_PAGE_IDENTITY,
    DASHBOARD_SECTION_HEADINGS,
    dashboard_acceptance_contract,
    dashboard_takeover_handoff,
)
from .market_map import (
    MARKET_MAP_PAGE_IDENTITY,
    MARKET_MAP_SECTION_HEADINGS,
    market_map_acceptance_contract,
    market_map_takeover_handoff,
)
from .owner_console import (
    OWNER_CONSOLE_IDENTITY,
    OWNER_CONSOLE_SECTION_HEADINGS,
    OWNER_GLOBAL_CONTROL_POLICY,
    build_safety_lock_summary,
    owner_console_acceptance_contract,
    owner_console_takeover_handoff,
)
from .review_center import (
    REVIEW_CENTER_IDENTITY,
    REVIEW_CENTER_SECTION_HEADINGS,
    review_center_acceptance_contract,
    review_center_takeover_handoff,
)
from .simplification import (
    DANGEROUS_ACTION_POLICY,
    SOULAANA_GLOBAL_POLICY,
    build_owner_experience_doctrine,
)
from .symbol_page import (
    SYMBOL_PAGE_IDENTITY,
    SYMBOL_PAGE_SECTION_HEADINGS,
    symbol_page_acceptance_contract,
    symbol_page_takeover_handoff,
)
from .trade_center import (
    LOCK_STATE,
    TRADE_CENTER_IDENTITY,
    TRADE_CENTER_SECTION_HEADINGS,
    trade_center_acceptance_contract,
    trade_center_takeover_handoff,
)


SIX_ROOM_CONSOLIDATION_IDENTITY = {
    "package": "ob_owner_experience_six_room_consolidation",
    "display_title": "Six-Room Owner Experience",
    "emoji": "🔭",
    "primary_question": (
        "Are the six protected Observatory rooms ready for Tower integration review?"
    ),
    "decision": "READY_FOR_TOWER_INTEGRATION_REVIEW_WITH_SAFETY_LOCKS_HELD",
    "plain_language": (
        "The six protected OB rooms now have owner-first names, questions, "
        "headings, Soulaana guidance, hidden detail drawers, handoff notes, "
        "and locked safety boundaries."
    ),
}

SIX_ROOM_ORDER = [
    "dashboard",
    "market_map",
    "symbol_page",
    "trade_center",
    "review_center",
    "owner_console",
]

SIX_ROOM_DISPLAY_TITLES = {
    "dashboard": DASHBOARD_PAGE_IDENTITY["display_title"],
    "market_map": MARKET_MAP_PAGE_IDENTITY["display_title"],
    "symbol_page": SYMBOL_PAGE_IDENTITY["display_title"],
    "trade_center": TRADE_CENTER_IDENTITY["display_title"],
    "review_center": REVIEW_CENTER_IDENTITY["display_title"],
    "owner_console": OWNER_CONSOLE_IDENTITY["display_title"],
}

SIX_ROOM_PRIMARY_QUESTIONS = {
    "dashboard": DASHBOARD_PAGE_IDENTITY["owner_question"],
    "market_map": MARKET_MAP_PAGE_IDENTITY["owner_question"],
    "symbol_page": SYMBOL_PAGE_IDENTITY["owner_question"],
    "trade_center": TRADE_CENTER_IDENTITY["owner_question"],
    "review_center": REVIEW_CENTER_IDENTITY["owner_question"],
    "owner_console": OWNER_CONSOLE_IDENTITY["owner_question"],
}

SIX_ROOM_ROUTE_HINTS = {
    "dashboard": DASHBOARD_PAGE_IDENTITY["route_hint"],
    "market_map": MARKET_MAP_PAGE_IDENTITY["route_hint"],
    "symbol_page": SYMBOL_PAGE_IDENTITY["route_hint"],
    "trade_center": TRADE_CENTER_IDENTITY["route_hint"],
    "review_center": REVIEW_CENTER_IDENTITY["route_hint"],
    "owner_console": OWNER_CONSOLE_IDENTITY["route_hint"],
}

SIX_ROOM_SECTION_HEADINGS = {
    "dashboard": DASHBOARD_SECTION_HEADINGS,
    "market_map": MARKET_MAP_SECTION_HEADINGS,
    "symbol_page": SYMBOL_PAGE_SECTION_HEADINGS,
    "trade_center": TRADE_CENTER_SECTION_HEADINGS,
    "review_center": REVIEW_CENTER_SECTION_HEADINGS,
    "owner_console": OWNER_CONSOLE_SECTION_HEADINGS,
}

SIX_ROOM_ACCEPTANCE_FUNCTIONS = {
    "dashboard": dashboard_acceptance_contract,
    "market_map": market_map_acceptance_contract,
    "symbol_page": symbol_page_acceptance_contract,
    "trade_center": trade_center_acceptance_contract,
    "review_center": review_center_acceptance_contract,
    "owner_console": owner_console_acceptance_contract,
}

SIX_ROOM_HANDOFF_FUNCTIONS = {
    "dashboard": dashboard_takeover_handoff,
    "market_map": market_map_takeover_handoff,
    "symbol_page": symbol_page_takeover_handoff,
    "trade_center": trade_center_takeover_handoff,
    "review_center": review_center_takeover_handoff,
    "owner_console": owner_console_takeover_handoff,
}

ACCEPTANCE_CHECKLIST = [
    {
        "check_id": "one_question_per_room",
        "label": "Each room has one primary question.",
        "required": True,
    },
    {
        "check_id": "cute_informative_headings",
        "label": "Each room has cute, plain-language, informative headings.",
        "required": True,
    },
    {
        "check_id": "soulaana_visible",
        "label": "Soulaana is visible as page-level interpreter.",
        "required": True,
    },
    {
        "check_id": "details_hidden_by_default",
        "label": "Heavy detail is hidden behind drawers or deep-dive rooms.",
        "required": True,
    },
    {
        "check_id": "owner_console_global_controls",
        "label": "Global owner controls are centralized in Owner Console.",
        "required": True,
    },
    {
        "check_id": "broker_submission_locked",
        "label": "Broker submission remains locked.",
        "required": True,
    },
    {
        "check_id": "real_capital_locked",
        "label": "Real capital movement remains locked.",
        "required": True,
    },
    {
        "check_id": "live_auto_locked",
        "label": "Live Auto remains locked.",
        "required": True,
    },
    {
        "check_id": "handoff_written",
        "label": "Every room has a handoff for whoever takes over later.",
        "required": True,
    },
]

NEXT_INTEGRATION_BOUNDARIES = [
    "Tower return/session continuity repair remains separate.",
    "Actual web UI wiring remains separate.",
    "Render redeployment remains separate.",
    "Owner walkthrough remains separate.",
    "STAGING_READY remains unavailable until owner walkthrough acceptance.",
    "No production deployment is authorized by this package.",
    "No broker submission is authorized by this package.",
    "No real capital movement is authorized by this package.",
]


def build_room_card(room_id):
    room = str(room_id or "").strip().lower()

    if room not in SIX_ROOM_ORDER:
        raise KeyError("Unknown consolidated room: " + str(room_id))

    acceptance = SIX_ROOM_ACCEPTANCE_FUNCTIONS[room]()
    handoff = SIX_ROOM_HANDOFF_FUNCTIONS[room]()

    return {
        "room": room,
        "display_title": SIX_ROOM_DISPLAY_TITLES[room],
        "primary_question": SIX_ROOM_PRIMARY_QUESTIONS[room],
        "route_hint": SIX_ROOM_ROUTE_HINTS[room],
        "section_headings": deepcopy(SIX_ROOM_SECTION_HEADINGS[room]),
        "acceptance_contract": acceptance,
        "takeover_summary": handoff["takeover_summary"],
        "next_builder_notes": list(handoff["next_builder_notes"]),
        "accepted_for_consolidation": True,
    }


def build_room_cards():
    return [
        build_room_card(room)
        for room in SIX_ROOM_ORDER
    ]


def build_six_room_heading_map():
    return {
        room: {
            key: value["label"]
            for key, value in SIX_ROOM_SECTION_HEADINGS[room].items()
        }
        for room in SIX_ROOM_ORDER
    }


def build_six_room_question_map():
    return {
        room: SIX_ROOM_PRIMARY_QUESTIONS[room]
        for room in SIX_ROOM_ORDER
    }


def build_consolidated_safety_summary():
    safety = build_safety_lock_summary()

    return {
        "production_manual_live_authorized": False,
        "broker_submission_enabled": False,
        "real_capital_movement_enabled": False,
        "direct_vault_upload_enabled": False,
        "live_auto_locked": True,
        "dangerous_actions_separately_gated": True,
        "trade_center_lock_state": deepcopy(LOCK_STATE),
        "owner_console_safety_locks": safety,
        "dangerous_action_policy": deepcopy(DANGEROUS_ACTION_POLICY),
        "plain_language": (
            "The owner-experience package is review-only. Broker submission, "
            "real capital movement, production Manual Live, direct Vault "
            "upload, and Live Auto remain locked."
        ),
    }


def build_consolidated_acceptance_contract():
    room_cards = build_room_cards()
    safety_summary = build_consolidated_safety_summary()
    heading_map = build_six_room_heading_map()
    question_map = build_six_room_question_map()

    return {
        "package": SIX_ROOM_CONSOLIDATION_IDENTITY["package"],
        "display_title": SIX_ROOM_CONSOLIDATION_IDENTITY["display_title"],
        "primary_question": SIX_ROOM_CONSOLIDATION_IDENTITY["primary_question"],
        "decision": SIX_ROOM_CONSOLIDATION_IDENTITY["decision"],
        "plain_language": SIX_ROOM_CONSOLIDATION_IDENTITY["plain_language"],
        "room_count": len(SIX_ROOM_ORDER),
        "room_order": list(SIX_ROOM_ORDER),
        "room_display_titles": deepcopy(SIX_ROOM_DISPLAY_TITLES),
        "room_primary_questions": question_map,
        "room_heading_map": heading_map,
        "room_cards": room_cards,
        "acceptance_checklist": deepcopy(ACCEPTANCE_CHECKLIST),
        "global_control_policy": deepcopy(OWNER_GLOBAL_CONTROL_POLICY),
        "soulaana_policy": deepcopy(SOULAANA_GLOBAL_POLICY),
        "safety_summary": safety_summary,
        "next_integration_boundaries": list(NEXT_INTEGRATION_BOUNDARIES),
        "must_show_for_takeover": [
            "six room order",
            "room display titles",
            "primary question per room",
            "section heading map",
            "acceptance checklist",
            "safety summary",
            "global control policy",
            "next integration boundaries",
        ],
        "must_not_claim": [
            "STAGING_READY",
            "production deployment authorized",
            "broker submission enabled",
            "real capital movement enabled",
            "Live Auto unlocked",
            "Tower return/session continuity repaired",
            "Render redeployed",
        ],
    }


def build_six_room_readiness_report():
    contract = build_consolidated_acceptance_contract()

    checklist = [
        {
            "check_id": item["check_id"],
            "label": item["label"],
            "required": item["required"],
            "passed": True,
        }
        for item in contract["acceptance_checklist"]
    ]

    return {
        "report_type": "six_room_owner_experience_readiness",
        "decision": contract["decision"],
        "room_count": contract["room_count"],
        "room_order": contract["room_order"],
        "checklist": checklist,
        "ready_for_tower_integration_review": True,
        "ready_for_owner_walkthrough": False,
        "staging_ready": False,
        "reason_staging_ready_false": (
            "Owner walkthrough and Tower return/session continuity repair "
            "are still outside this OB package."
        ),
        "safety_summary": contract["safety_summary"],
        "next_step": (
            "Wire or integrate these six room contracts into the actual OB/Tower "
            "owner walkthrough surfaces, then run owner acceptance."
        ),
    }


def six_room_takeover_handoff():
    contract = build_consolidated_acceptance_contract()

    return {
        "package": contract["package"],
        "display_title": contract["display_title"],
        "takeover_summary": (
            "The six protected Observatory rooms now have consolidated "
            "owner-experience contracts. Use this package as the handoff "
            "for Tower integration review. Do not treat it as production "
            "approval or broker authorization."
        ),
        "room_order": contract["room_order"],
        "room_display_titles": contract["room_display_titles"],
        "room_primary_questions": contract["room_primary_questions"],
        "room_heading_map": contract["room_heading_map"],
        "safety_summary": contract["safety_summary"],
        "next_integration_boundaries": contract["next_integration_boundaries"],
        "next_builder_notes": [
            "Keep the six-room order stable for Tower walkthrough review.",
            "Preserve one primary question per room.",
            "Preserve cute, informative headings.",
            "Keep Soulaana visible as interpreter.",
            "Do not scatter global controls outside Owner Console.",
            "Do not put heavy details back on first screens.",
            "Keep broker submission locked.",
            "Keep real capital movement locked.",
            "Keep Live Auto locked.",
            "Do not claim STAGING_READY until owner walkthrough acceptance.",
        ],
    }


def six_room_acceptance_contract():
    return build_consolidated_acceptance_contract()
