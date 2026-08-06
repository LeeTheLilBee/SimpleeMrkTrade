# Symbol Page simplification surface for The Observatory.
#
# This module is UI-framework neutral. It gives the eventual Symbol Page
# a clean owner-first data contract instead of a quote-data dump.
#
# Owner-experience target:
#
#   The Symbol Page should answer:
#
#       What do I need to understand about this asset?
#
# It should not open with every candle, indicator, headline, risk note,
# receipt, and owner control at the same time. The owner first needs the
# asset story:
#
# 1. What asset is this?
# 2. What is the thesis?
# 3. What is the risk?
# 4. What is the current decision state?
# 5. What indicators matter most?
# 6. What should Soulaana explain?
# 7. What details can stay tucked away?
#
# Deep details move into drawers. This keeps the Symbol Page readable
# and gives the next builder a clear handoff.

from copy import deepcopy

from .simplification import (
    DANGEROUS_ACTION_POLICY,
    OWNER_CONTROL_POLICY,
    get_room_policy,
    soulaana_interpretation,
)


SYMBOL_PAGE_ROOM = "symbol_page"

SYMBOL_PAGE_IDENTITY = {
    "room": SYMBOL_PAGE_ROOM,
    "route_hint": "/ob/symbol/<symbol>",
    "owner_question": "What do I need to understand about this asset?",
    "plain_title": "Asset",
    "display_title": "Asset Storybook",
    "emoji": "🔎",
    "subtitle": (
        "A simple first-glance read of one asset: thesis, risk, "
        "decision state, key signals, and Soulaana's plain-language explanation."
    ),
}

SYMBOL_PAGE_SECTION_HEADINGS = {
    "hero": {
        "label": "🔎 Asset Storybook",
        "plain_label": "Asset overview",
        "explainer": (
            "This is the first-glance asset summary. It should identify "
            "the symbol and explain why the owner is looking at it."
        ),
    },
    "soulaana": {
        "label": "🧭 Soulaana Explains",
        "plain_label": "Soulaana interpretation",
        "explainer": (
            "Soulaana translates the asset page into plain language: "
            "what this asset is, why it matters, what to focus on, "
            "what to ignore, and what to do next."
        ),
    },
    "thesis": {
        "label": "📖 The Asset Story",
        "plain_label": "Asset thesis",
        "explainer": (
            "The short reason this asset matters. This should come "
            "before charts, indicators, or raw quote detail."
        ),
    },
    "risk": {
        "label": "🛡️ Risk Before Shine",
        "plain_label": "Risk read",
        "explainer": (
            "Risk must be visible before the owner thinks about action."
        ),
    },
    "decision": {
        "label": "👑 Decision Posture",
        "plain_label": "Decision state",
        "explainer": (
            "The current posture for the asset: observe, review, avoid, "
            "or wait for confirmation. This is not broker submission."
        ),
    },
    "signals": {
        "label": "✨ Tiny Asset Signals",
        "plain_label": "Key indicators",
        "explainer": (
            "A small set of asset indicators. This must never become a "
            "full technical wall."
        ),
    },
    "drawers": {
        "label": "🗂️ Asset Detail Drawers",
        "plain_label": "Hidden asset details",
        "explainer": (
            "Quote detail, technical detail, evidence, research, and "
            "history live here so the first screen stays readable."
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

SYMBOL_PAGE_SURFACE_ORDER = [
    "hero",
    "soulaana",
    "thesis",
    "risk",
    "decision",
    "signals",
    "drawers",
    "owner_drawer",
]

SYMBOL_PAGE_LIMITS = {
    "indicators": 4,
    "warnings": 3,
    "evidence": 5,
    "related_notes": 4,
}

SYMBOL_PAGE_DETAIL_DRAWERS = [
    "quote_context",
    "thesis_detail",
    "risk_detail",
    "technical_context",
    "news_context",
    "evidence_context",
    "history_context",
    "owner_notes",
]

SYMBOL_PAGE_DRAWER_EXPLAINERS = {
    "quote_context": "Current quote, pricing, volume, and snapshot detail.",
    "thesis_detail": "The longer thesis and why the asset is being watched.",
    "risk_detail": "Risk factors that should not crowd the first screen.",
    "technical_context": "Chart, trend, level, and technical signal detail.",
    "news_context": "News or catalyst context that may affect the asset.",
    "evidence_context": "Receipts, sources, and reasoning behind the asset read.",
    "history_context": "Prior observations, reviews, and comparable asset behavior.",
    "owner_notes": "Owner-only notes, reminders, and Soulaana interpretation history.",
}

RISK_ORDER = {
    "extreme": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
    "unknown": 4,
}

DECISION_STATE_LABELS = {
    "observe": "Observe",
    "review": "Review",
    "wait": "Wait For Confirmation",
    "avoid": "Avoid For Now",
    "ready": "Ready For Owner Review",
    "unknown": "Unknown",
}

SIGNAL_IMPORTANCE_ORDER = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
    "info": 4,
}


def clean_text(value, fallback):
    text = str(value or "").strip()

    if text:
        return text

    return fallback


def clean_symbol(value):
    text = str(value or "").strip().upper()

    if text:
        return text

    return "UNKNOWN"


def normalize_risk_level(value):
    text = str(value or "unknown").strip().lower()

    if text not in RISK_ORDER:
        return "unknown"

    return text


def normalize_decision_state(value):
    text = str(value or "unknown").strip().lower().replace("-", "_").replace(" ", "_")

    if text not in DECISION_STATE_LABELS:
        return "unknown"

    return text


def normalize_signal_importance(value):
    text = str(value or "info").strip().lower()

    if text not in SIGNAL_IMPORTANCE_ORDER:
        return "info"

    return text


def clean_limited_list(values, limit):
    cleaned = []

    for value in values:
        text = str(value or "").strip()

        if text:
            cleaned.append(text)

    return cleaned[:limit]


def normalize_asset_indicator(indicator):
    importance = normalize_signal_importance(
        indicator.get("importance", "info")
    )

    return {
        "title": clean_text(indicator.get("title"), "Untitled asset signal"),
        "plain_language": clean_text(
            indicator.get("plain_language"),
            "This may affect how the asset should be understood.",
        ),
        "importance": importance,
        "source": clean_text(indicator.get("source"), "symbol_page"),
        "drawer": clean_text(indicator.get("drawer"), "evidence_context"),
    }


def rank_asset_indicators(indicators):
    normalized = [
        normalize_asset_indicator(indicator)
        for indicator in indicators
    ]

    return sorted(
        normalized,
        key=lambda item: (
            SIGNAL_IMPORTANCE_ORDER[item["importance"]],
            item["title"].lower(),
        ),
    )


def build_symbol_drawers():
    drawers = []

    for drawer_id in SYMBOL_PAGE_DETAIL_DRAWERS:
        drawers.append(
            {
                "drawer_id": drawer_id,
                "label": drawer_id.replace("_", " ").title(),
                "explainer": SYMBOL_PAGE_DRAWER_EXPLAINERS[drawer_id],
                "default_state": "collapsed",
            }
        )

    return drawers


def choose_symbol_recommendation(risk_level, decision_state, warnings):
    if risk_level in {"extreme", "high"} and warnings:
        return "Review risk first: " + warnings[0] + "."

    if decision_state == "avoid":
        return "Avoid action for now and review the risk drawer."

    if decision_state == "ready":
        return "Open owner review before any action."

    if decision_state == "review":
        return "Review the thesis and risk before deciding."

    if decision_state == "wait":
        return "Wait for confirmation before acting."

    return "Stay in observation mode until the asset read becomes clearer."


def build_symbol_page_surface(
    symbol,
    asset_name="",
    asset_type="stock",
    thesis="",
    risk_level="unknown",
    decision_state="observe",
    indicators=None,
    warnings=None,
    evidence=None,
    related_notes=None,
    owner_mode="staging",
):
    policy = get_room_policy(SYMBOL_PAGE_ROOM)

    normalized_symbol = clean_symbol(symbol)
    asset_label = clean_text(asset_name, normalized_symbol)
    normalized_type = clean_text(asset_type, "asset")
    normalized_risk = normalize_risk_level(risk_level)
    normalized_decision = normalize_decision_state(decision_state)

    ranked_indicators = rank_asset_indicators(indicators or [])
    visible_indicators = ranked_indicators[: SYMBOL_PAGE_LIMITS["indicators"]]
    hidden_indicators = ranked_indicators[SYMBOL_PAGE_LIMITS["indicators"] :]

    warning_list = clean_limited_list(
        warnings or [],
        SYMBOL_PAGE_LIMITS["warnings"],
    )

    evidence_items = clean_limited_list(
        evidence or [],
        SYMBOL_PAGE_LIMITS["evidence"],
    )

    notes = clean_limited_list(
        related_notes or [],
        SYMBOL_PAGE_LIMITS["related_notes"],
    )

    asset_thesis = clean_text(
        thesis,
        "No thesis has been written for this asset yet.",
    )

    dominant_summary = (
        normalized_symbol
        + " is a "
        + normalized_type
        + " page for "
        + asset_label
        + "."
    )

    recommendation = choose_symbol_recommendation(
        risk_level=normalized_risk,
        decision_state=normalized_decision,
        warnings=warning_list,
    )

    safe_to_ignore = (
        SYMBOL_PAGE_DETAIL_DRAWERS
        + [item["title"] for item in hidden_indicators]
    )

    return {
        "room": SYMBOL_PAGE_ROOM,
        "page_identity": deepcopy(SYMBOL_PAGE_IDENTITY),
        "symbol": normalized_symbol,
        "asset_name": asset_label,
        "asset_type": normalized_type,
        "title": policy["purpose"]["title"],
        "display_title": SYMBOL_PAGE_IDENTITY["display_title"],
        "subtitle": SYMBOL_PAGE_IDENTITY["subtitle"],
        "question_answered": policy["purpose"]["question"],
        "surface_order": list(SYMBOL_PAGE_SURFACE_ORDER),
        "section_headings": deepcopy(SYMBOL_PAGE_SECTION_HEADINGS),
        "dominant_summary": dominant_summary,
        "asset_thesis": asset_thesis,
        "current_risk_level": normalized_risk,
        "decision_state": normalized_decision,
        "decision_label": DECISION_STATE_LABELS[normalized_decision],
        "principal_recommendation": recommendation,
        "visible_indicators": visible_indicators,
        "hidden_indicator_count": len(hidden_indicators),
        "warnings": warning_list,
        "evidence": evidence_items,
        "related_notes": notes,
        "drawers": build_symbol_drawers(),
        "soulaana": soulaana_interpretation(
            room=SYMBOL_PAGE_ROOM,
            summary=dominant_summary,
            focus=asset_thesis,
            next_action=recommendation,
            ignore=safe_to_ignore,
        ),
        "next_action": recommendation,
        "owner_drawer_default_state": "collapsed",
        "details_hidden_by_default": True,
        "owner_mode": owner_mode,
        "owner_controls": deepcopy(OWNER_CONTROL_POLICY),
        "dangerous_actions": deepcopy(DANGEROUS_ACTION_POLICY),
    }


def empty_symbol_page_surface(symbol="UNKNOWN"):
    return build_symbol_page_surface(
        symbol=symbol,
        asset_name=symbol,
        asset_type="asset",
        thesis="No thesis has been written for this asset yet.",
        risk_level="unknown",
        decision_state="observe",
        indicators=[],
        warnings=[],
        evidence=[],
        related_notes=[],
        owner_mode="staging",
    )


def symbol_page_takeover_handoff():
    return {
        "room": SYMBOL_PAGE_ROOM,
        "takeover_summary": (
            "Symbol Page is now a first-glance Asset Storybook surface. "
            "Wire actual UI components to this contract instead of "
            "returning to a raw quote-data wall."
        ),
        "primary_question": SYMBOL_PAGE_IDENTITY["owner_question"],
        "display_title": SYMBOL_PAGE_IDENTITY["display_title"],
        "surface_order": list(SYMBOL_PAGE_SURFACE_ORDER),
        "section_headings": deepcopy(SYMBOL_PAGE_SECTION_HEADINGS),
        "detail_drawers": build_symbol_drawers(),
        "next_builder_notes": [
            "Keep Asset Storybook visually dominant.",
            "Put the thesis before chart noise.",
            "Show risk before any action language.",
            "Keep Soulaana visible near the top of the page.",
            "Limit visible asset indicators to four by default.",
            "Do not put quote, technical, news, evidence, or history walls on the first screen.",
            "Use drawers for heavy asset detail.",
            "Keep the room Owner Drawer collapsed by default.",
            "Keep dangerous actions behind separate step-up gates.",
        ],
    }


def symbol_page_acceptance_contract():
    return {
        "room": SYMBOL_PAGE_ROOM,
        "primary_question": SYMBOL_PAGE_IDENTITY["owner_question"],
        "display_title": SYMBOL_PAGE_IDENTITY["display_title"],
        "must_show_at_first_glance": [
            "symbol",
            "asset name",
            "asset thesis",
            "current risk level",
            "decision state",
            "up to four visible indicators",
            "one obvious next action",
            "Soulaana interpretation",
            "plain-language section headings",
        ],
        "must_hide_by_default": list(SYMBOL_PAGE_DETAIL_DRAWERS),
        "must_not_show": [
            "quote wall on first screen",
            "technical indicator wall on first screen",
            "news wall on first screen",
            "raw evidence wall on first screen",
            "global owner settings scattered inside Symbol Page",
            "dangerous action controls without step-up",
            "broker submission controls",
            "money movement controls",
        ],
        "section_headings": deepcopy(SYMBOL_PAGE_SECTION_HEADINGS),
        "owner_drawer_default_state": "collapsed",
        "dangerous_actions": deepcopy(DANGEROUS_ACTION_POLICY),
    }
