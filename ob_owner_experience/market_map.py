# Market Map simplification surface for The Observatory.
#
# This module is UI-framework neutral. It gives the eventual Market Map
# page a clear contract so the first screen can stay understandable.
#
# Owner-experience target:
#
#   The Market Map should answer:
#
#       What is happening in the market?
#
# It should not open with sector walls, technical-signal walls, breadth
# walls, or symbol-level detail. The owner first needs one market read:
#
# 1. Overall condition.
# 2. Current risk level.
# 3. Most important movement.
# 4. Strongest opportunities.
# 5. Most important warnings.
# 6. Soulaana explaining the market in plain language.
#
# Deep details move into named rooms. This keeps the Market Map useful
# today and gives the next builder a clean handoff.

from copy import deepcopy

from .simplification import (
    DANGEROUS_ACTION_POLICY,
    MARKET_MAP_DEEP_DIVES,
    OWNER_CONTROL_POLICY,
    get_room_policy,
    soulaana_interpretation,
)


MARKET_MAP_ROOM = "market_map"

MARKET_MAP_PAGE_IDENTITY = {
    "room": MARKET_MAP_ROOM,
    "route_hint": "/ob/market-map",
    "owner_question": "What is happening in the market?",
    "plain_title": "Market",
    "display_title": "Market Weather",
    "emoji": "🌦️",
    "subtitle": (
        "A simple first-glance read of market condition, risk, "
        "movement, opportunities, warnings, and what Soulaana thinks."
    ),
}

MARKET_MAP_SECTION_HEADINGS = {
    "hero": {
        "label": "🌦️ Market Weather",
        "plain_label": "Market condition",
        "explainer": (
            "This is the top-level market read. It should tell the "
            "owner whether the market feels calm, mixed, risky, or "
            "constructive before any detail appears."
        ),
    },
    "soulaana": {
        "label": "🧭 Soulaana Reads the Room",
        "plain_label": "Soulaana interpretation",
        "explainer": (
            "Soulaana explains what the market read means in plain "
            "language and tells the owner what to focus on first."
        ),
    },
    "risk": {
        "label": "🛡️ Risk First",
        "plain_label": "Current risk level",
        "explainer": (
            "Risk comes before opportunity. This helps the owner avoid "
            "chasing movement before understanding danger."
        ),
    },
    "movement": {
        "label": "🌊 Biggest Movement",
        "plain_label": "Most important movement",
        "explainer": (
            "The single most important market movement right now."
        ),
    },
    "opportunities": {
        "label": "🌱 Strongest Opportunities",
        "plain_label": "Top opportunities",
        "explainer": (
            "A short list only. Do not turn this into a full symbol wall."
        ),
    },
    "warnings": {
        "label": "⚠️ Watch Your Step",
        "plain_label": "Warnings",
        "explainer": (
            "The most important market warnings. Keep this short so "
            "the owner can process risk quickly."
        ),
    },
    "deep_dives": {
        "label": "🗺️ Deep-Dive Rooms",
        "plain_label": "Deep market details",
        "explainer": (
            "Sector detail, breadth, volatility, flows, evidence, and "
            "research go here instead of crowding the first screen."
        ),
    },
    "owner_drawer": {
        "label": "🔐 Owner Drawer",
        "plain_label": "Owner room controls",
        "explainer": (
            "Room-specific owner controls stay collapsed by default. "
            "Global owner settings belong in Owner Console."
        ),
    },
}

MARKET_MAP_SURFACE_ORDER = [
    "hero",
    "soulaana",
    "risk",
    "movement",
    "opportunities",
    "warnings",
    "deep_dives",
    "owner_drawer",
]

MARKET_MAP_FIRST_GLANCE_FIELDS = [
    "overall_market_condition",
    "current_risk_level",
    "most_important_movement",
    "strongest_opportunities",
    "most_important_warnings",
    "soulaana_plain_language_interpretation",
]

MARKET_MAP_LIMITS = {
    "opportunities": 3,
    "warnings": 3,
    "signals": 4,
    "deep_dive_key_points": 5,
    "deep_dive_evidence": 5,
}

RISK_ORDER = {
    "extreme": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
    "unknown": 4,
}

SIGNAL_IMPORTANCE_ORDER = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
    "info": 4,
}

MARKET_MAP_DEEP_DIVE_ROOM_CONFIGS = {
    "sector_details": {
        "title": "Sector Garden",
        "heading": "🌿 Sector Garden",
        "plain_title": "Sectors",
        "question": "Which parts of the market are leading or lagging?",
        "plain_language": (
            "Shows the market groups moving the day without crowding "
            "the first screen."
        ),
    },
    "market_breadth": {
        "title": "Breadth Check",
        "heading": "🫧 Breadth Check",
        "plain_title": "Breadth",
        "question": "Is the whole market participating or only a few names?",
        "plain_language": (
            "Shows whether market strength is broad and healthier or "
            "narrow and fragile."
        ),
    },
    "correlations": {
        "title": "Together Map",
        "heading": "🧲 Together Map",
        "plain_title": "Correlations",
        "question": "What is moving together?",
        "plain_language": (
            "Shows when assets are acting connected instead of independent."
        ),
    },
    "volatility": {
        "title": "Storm Meter",
        "heading": "⛈️ Storm Meter",
        "plain_title": "Volatility",
        "question": "How unstable is the market right now?",
        "plain_language": (
            "Shows whether the market is calm, jumpy, or dangerous."
        ),
    },
    "flows": {
        "title": "Money River",
        "heading": "💧 Money River",
        "plain_title": "Flows",
        "question": "Where does money appear to be moving?",
        "plain_language": (
            "Shows where attention and capital are concentrating."
        ),
    },
    "technical_signals": {
        "title": "Signal Lanterns",
        "heading": "🏮 Signal Lanterns",
        "plain_title": "Technical signals",
        "question": "What do price and trend signals suggest?",
        "plain_language": (
            "Shows price-action clues without making them the whole page."
        ),
    },
    "symbol_level_data": {
        "title": "Symbol Nest",
        "heading": "🪺 Symbol Nest",
        "plain_title": "Symbols",
        "question": "Which assets need a closer look?",
        "plain_language": (
            "Shows symbol-level detail after the main market read is clear."
        ),
    },
    "evidence": {
        "title": "Receipts Table",
        "heading": "📎 Receipts Table",
        "plain_title": "Evidence",
        "question": "What supports this market read?",
        "plain_language": (
            "Shows receipts, sources, and reasoning behind the market view."
        ),
    },
    "research_detail": {
        "title": "Research Library",
        "heading": "📚 Research Library",
        "plain_title": "Research",
        "question": "What deeper research matters?",
        "plain_language": (
            "Holds deeper notes for later review without cluttering the first screen."
        ),
    },
    "historical_comparisons": {
        "title": "Time Mirror",
        "heading": "🪞 Time Mirror",
        "plain_title": "History",
        "question": "What past market setups look similar?",
        "plain_language": (
            "Compares the current environment to prior market conditions."
        ),
    },
}


def clean_text(value, fallback):
    text = str(value or "").strip()

    if text:
        return text

    return fallback


def normalize_importance(value):
    text = str(value or "info").strip().lower()

    if text not in SIGNAL_IMPORTANCE_ORDER:
        return "info"

    return text


def normalize_risk_level(value):
    text = str(value or "unknown").strip().lower()

    if text not in RISK_ORDER:
        return "unknown"

    return text


def clean_limited_list(values, limit):
    cleaned = []

    for value in values:
        text = str(value or "").strip()

        if text:
            cleaned.append(text)

    return cleaned[:limit]


def normalize_market_signal(signal):
    importance = normalize_importance(
        signal.get("importance", "info")
    )

    return {
        "title": clean_text(signal.get("title"), "Untitled market signal"),
        "plain_language": clean_text(
            signal.get("plain_language"),
            "This may affect how the market should be read.",
        ),
        "importance": importance,
        "source": clean_text(signal.get("source"), "market_map"),
        "deep_dive": clean_text(signal.get("deep_dive"), "evidence"),
    }


def rank_market_signals(signals):
    normalized = [
        normalize_market_signal(signal)
        for signal in signals
    ]

    return sorted(
        normalized,
        key=lambda item: (
            SIGNAL_IMPORTANCE_ORDER[item["importance"]],
            item["title"].lower(),
        ),
    )


def build_deep_dive_cards():
    cards = []

    for room_id in MARKET_MAP_DEEP_DIVES:
        config = MARKET_MAP_DEEP_DIVE_ROOM_CONFIGS[room_id]

        cards.append(
            {
                "room_id": room_id,
                "heading": config["heading"],
                "title": config["title"],
                "plain_title": config["plain_title"],
                "question": config["question"],
                "explainer": config["plain_language"],
                "default_state": "hidden_until_opened",
            }
        )

    return cards


def choose_market_recommendation(warnings, opportunities):
    if warnings:
        return "Review risk first: " + warnings[0] + "."

    if opportunities:
        return "Watch strongest opportunity: " + opportunities[0] + "."

    return (
        "Stay in observation mode until a clearer market signal appears."
    )


def build_market_map_surface(
    overall_market_condition,
    current_risk_level,
    most_important_movement,
    strongest_opportunities,
    most_important_warnings,
    signals=None,
    owner_mode="staging",
):
    policy = get_room_policy(MARKET_MAP_ROOM)
    risk = normalize_risk_level(current_risk_level)

    opportunities = clean_limited_list(
        strongest_opportunities,
        MARKET_MAP_LIMITS["opportunities"],
    )

    warnings = clean_limited_list(
        most_important_warnings,
        MARKET_MAP_LIMITS["warnings"],
    )

    ranked_signals = rank_market_signals(signals or [])
    visible_signals = ranked_signals[: MARKET_MAP_LIMITS["signals"]]
    hidden_signals = ranked_signals[MARKET_MAP_LIMITS["signals"] :]

    condition = clean_text(
        overall_market_condition,
        "market condition unknown",
    )

    movement = clean_text(
        most_important_movement,
        "No single market movement is dominant yet.",
    )

    dominant_summary = (
        "Market is "
        + condition
        + " with "
        + risk
        + " risk."
    )

    principal_recommendation = choose_market_recommendation(
        warnings=warnings,
        opportunities=opportunities,
    )

    safe_to_ignore = (
        MARKET_MAP_DEEP_DIVES
        + [item["title"] for item in hidden_signals]
    )

    return {
        "room": MARKET_MAP_ROOM,
        "page_identity": deepcopy(MARKET_MAP_PAGE_IDENTITY),
        "title": policy["purpose"]["title"],
        "display_title": MARKET_MAP_PAGE_IDENTITY["display_title"],
        "subtitle": MARKET_MAP_PAGE_IDENTITY["subtitle"],
        "question_answered": policy["purpose"]["question"],
        "surface_order": list(MARKET_MAP_SURFACE_ORDER),
        "section_headings": deepcopy(MARKET_MAP_SECTION_HEADINGS),
        "dominant_summary": dominant_summary,
        "overall_market_condition": condition,
        "current_risk_level": risk,
        "most_important_movement": movement,
        "principal_recommendation": principal_recommendation,
        "strongest_opportunities": opportunities,
        "most_important_warnings": warnings,
        "visible_signals": visible_signals,
        "hidden_signal_count": len(hidden_signals),
        "first_glance_fields": deepcopy(MARKET_MAP_FIRST_GLANCE_FIELDS),
        "deep_dive_cards": build_deep_dive_cards(),
        "deep_dive_rooms_hidden_by_default": deepcopy(MARKET_MAP_DEEP_DIVES),
        "soulaana": soulaana_interpretation(
            room=MARKET_MAP_ROOM,
            summary=dominant_summary,
            focus=movement,
            next_action=principal_recommendation,
            ignore=safe_to_ignore,
        ),
        "next_action": principal_recommendation,
        "owner_drawer_default_state": "collapsed",
        "details_hidden_by_default": True,
        "owner_mode": owner_mode,
        "owner_controls": deepcopy(OWNER_CONTROL_POLICY),
        "dangerous_actions": deepcopy(DANGEROUS_ACTION_POLICY),
    }


def build_market_deep_dive_room(
    deep_dive,
    summary="",
    key_points=None,
    evidence=None,
    next_action="",
):
    room_id = (
        str(deep_dive or "")
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    if room_id not in MARKET_MAP_DEEP_DIVE_ROOM_CONFIGS:
        raise KeyError(
            "Unknown Market Map deep-dive room: " + str(deep_dive)
        )

    config = deepcopy(MARKET_MAP_DEEP_DIVE_ROOM_CONFIGS[room_id])

    points = clean_limited_list(
        key_points or [],
        MARKET_MAP_LIMITS["deep_dive_key_points"],
    )

    evidence_items = clean_limited_list(
        evidence or [],
        MARKET_MAP_LIMITS["deep_dive_evidence"],
    )

    room_summary = clean_text(
        summary,
        config["plain_language"],
    )

    room_next_action = clean_text(
        next_action,
        "Return to the Market Weather view when this detail is understood.",
    )

    return {
        "room": room_id,
        "parent_room": MARKET_MAP_ROOM,
        "heading": config["heading"],
        "title": config["title"],
        "plain_title": config["plain_title"],
        "question_answered": config["question"],
        "plain_language": config["plain_language"],
        "dominant_summary": room_summary,
        "key_points": points,
        "evidence": evidence_items,
        "next_action": room_next_action,
        "soulaana": {
            "soulaana_visible": True,
            "role": "owner guide and command interpreter",
            "what_you_are_looking_at": room_summary,
            "why_it_matters": config["plain_language"],
            "focus_on": points[0] if points else config["question"],
            "safe_to_ignore_for_now": [
                "other Market Map deep dives until this one is understood"
            ],
            "next_action": room_next_action,
        },
        "owner_drawer_default_state": "collapsed",
        "details_hidden_by_default": False,
        "dangerous_actions": deepcopy(DANGEROUS_ACTION_POLICY),
    }


def build_all_market_deep_dive_rooms():
    return {
        room_id: build_market_deep_dive_room(room_id)
        for room_id in MARKET_MAP_DEEP_DIVES
    }


def market_map_takeover_handoff():
    return {
        "room": MARKET_MAP_ROOM,
        "takeover_summary": (
            "Market Map is now a first-glance Market Weather surface "
            "with named deep-dive rooms. Wire actual UI components to "
            "this contract instead of rebuilding the doctrine."
        ),
        "primary_question": MARKET_MAP_PAGE_IDENTITY["owner_question"],
        "display_title": MARKET_MAP_PAGE_IDENTITY["display_title"],
        "surface_order": list(MARKET_MAP_SURFACE_ORDER),
        "section_headings": deepcopy(MARKET_MAP_SECTION_HEADINGS),
        "first_glance_fields": deepcopy(MARKET_MAP_FIRST_GLANCE_FIELDS),
        "deep_dive_rooms": build_deep_dive_cards(),
        "next_builder_notes": [
            "Keep Market Weather visually dominant.",
            "Show risk before opportunity.",
            "Keep Soulaana visible near the top of the page.",
            "Limit opportunities to three by default.",
            "Limit warnings to three by default.",
            "Do not put sector, breadth, volatility, or technical walls on the first screen.",
            "Use deep-dive rooms for heavy market detail.",
            "Keep the room Owner Drawer collapsed by default.",
            "Keep dangerous actions behind separate step-up gates.",
        ],
    }


def market_map_acceptance_contract():
    return {
        "room": MARKET_MAP_ROOM,
        "primary_question": MARKET_MAP_PAGE_IDENTITY["owner_question"],
        "display_title": MARKET_MAP_PAGE_IDENTITY["display_title"],
        "must_show_at_first_glance": deepcopy(
            MARKET_MAP_FIRST_GLANCE_FIELDS
        )
        + [
            "plain-language section headings",
            "risk before opportunity",
        ],
        "must_hide_by_default": deepcopy(MARKET_MAP_DEEP_DIVES),
        "deep_dive_room_count": len(MARKET_MAP_DEEP_DIVES),
        "must_not_show": [
            "sector details on first screen",
            "market breadth on first screen",
            "correlations on first screen",
            "volatility wall on first screen",
            "technical-signal wall on first screen",
            "symbol-level data wall on first screen",
            "global owner settings scattered inside Market Map",
            "dangerous action controls without step-up",
        ],
        "section_headings": deepcopy(MARKET_MAP_SECTION_HEADINGS),
        "owner_drawer_default_state": "collapsed",
        "dangerous_actions": deepcopy(DANGEROUS_ACTION_POLICY),
    }
