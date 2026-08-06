# Dashboard simplification surface for The Observatory.
#
# This module is intentionally UI-framework neutral. It gives the eventual
# web page a clear data contract instead of hard-coding a visual framework.
#
# Owner-experience target:
#
#   The Dashboard is the Today room. Its first screen should answer:
#
#       What needs my attention today?
#
# It should not look like a wall of every signal in the system. It should
# feel like a calm owner command card:
#
# 1. One cute/plain heading.
# 2. One dominant summary.
# 3. One principal recommendation.
# 4. A tiny set of critical indicators.
# 5. One obvious next action.
# 6. Soulaana explaining the page.
# 7. Details tucked behind drawers.
#
# The module keeps enough metadata and section headings for a future
# builder to understand exactly how to wire this into the actual OB UI.

from copy import deepcopy

from .simplification import (
    DANGEROUS_ACTION_POLICY,
    OWNER_CONTROL_POLICY,
    get_room_policy,
    soulaana_interpretation,
)


DASHBOARD_ROOM = "dashboard"

DASHBOARD_PAGE_IDENTITY = {
    "room": DASHBOARD_ROOM,
    "route_hint": "/ob/dashboard",
    "owner_question": "What needs my attention today?",
    "plain_title": "Today",
    "display_title": "Today’s Command Nest",
    "emoji": "🌙",
    "subtitle": (
        "A calm first-glance owner view for what matters now, "
        "what can wait, and what Soulaana recommends next."
    ),
}

DASHBOARD_SECTION_HEADINGS = {
    "hero": {
        "label": "🌙 Today’s Command Nest",
        "plain_label": "Today",
        "explainer": (
            "This is the main owner summary. It should be the first "
            "thing the owner reads."
        ),
    },
    "soulaana": {
        "label": "🧭 Soulaana Says",
        "plain_label": "Soulaana interpretation",
        "explainer": (
            "Soulaana translates the Dashboard into plain language: "
            "what this is, why it matters, what to focus on, what to "
            "ignore, and what to do next."
        ),
    },
    "attention": {
        "label": "🔥 Needs Your Eyes",
        "plain_label": "Attention queue",
        "explainer": (
            "Only the highest-priority attention items belong here. "
            "The rest must stay hidden behind details."
        ),
    },
    "indicators": {
        "label": "✨ Tiny Signals",
        "plain_label": "Critical indicators",
        "explainer": (
            "A small set of key indicators. This section must never "
            "become a full metric wall."
        ),
    },
    "next_action": {
        "label": "👑 Owner Next Move",
        "plain_label": "Next action",
        "explainer": (
            "The one action the owner should understand first. "
            "Dangerous actions still require separate step-up."
        ),
    },
    "drawers": {
        "label": "🗂️ Details When Needed",
        "plain_label": "Detail drawers",
        "explainer": (
            "Secondary context lives here so the main Dashboard stays "
            "clean and understandable."
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

DASHBOARD_SURFACE_ORDER = [
    "hero",
    "soulaana",
    "attention",
    "indicators",
    "next_action",
    "drawers",
    "owner_drawer",
]

DASHBOARD_DEFAULT_LIMITS = {
    "attention_items": 3,
    "critical_indicators": 4,
    "warnings": 3,
    "next_actions": 1,
}

DASHBOARD_DETAIL_DRAWERS = [
    "market_context",
    "account_context",
    "watchlist_context",
    "risk_context",
    "receipt_context",
    "owner_notes",
]

DASHBOARD_DRAWER_EXPLAINERS = {
    "market_context": "Market details that support the main summary.",
    "account_context": "Mission/account context that may affect decisions.",
    "watchlist_context": "Symbols or assets worth watching later.",
    "risk_context": "Risk notes that should not crowd the first screen.",
    "receipt_context": "Evidence and receipts for audit or review.",
    "owner_notes": "Owner-only notes, reminders, and interpretation history.",
}

DASHBOARD_PRIORITY_ORDER = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
    "info": 4,
}


def normalize_severity(value):
    severity = str(value or "info").strip().lower()

    if severity not in DASHBOARD_PRIORITY_ORDER:
        return "info"

    return severity


def clean_text(value, fallback):
    text = str(value or "").strip()

    if text:
        return text

    return fallback


def normalize_attention_item(item):
    severity = normalize_severity(item.get("severity", "info"))

    return {
        "title": clean_text(item.get("title"), "Untitled attention item"),
        "why_it_matters": clean_text(
            item.get("why_it_matters"),
            "This may affect today's owner decision.",
        ),
        "recommended_action": clean_text(
            item.get("recommended_action"),
            "Review when available.",
        ),
        "severity": severity,
        "source": clean_text(item.get("source"), "observatory"),
        "requires_owner_action": bool(
            item.get("requires_owner_action", True)
        ),
    }


def rank_attention_items(items):
    normalized = [
        normalize_attention_item(item)
        for item in items
    ]

    return sorted(
        normalized,
        key=lambda item: (
            DASHBOARD_PRIORITY_ORDER[item["severity"]],
            not item["requires_owner_action"],
            item["title"].lower(),
        ),
    )


def select_dominant_summary(attention_items):
    if not attention_items:
        return "Nothing urgent needs owner attention right now."

    top_item = attention_items[0]
    count = len(attention_items)

    if count == 1:
        return "One item needs attention: " + top_item["title"] + "."

    return (
        str(count)
        + " items need attention. Start with "
        + top_item["title"]
        + "."
    )


def select_principal_recommendation(attention_items):
    if not attention_items:
        return (
            "Stay in observation mode and wait for a clearer priority."
        )

    return attention_items[0]["recommended_action"]


def build_indicator_list(market_condition, risk_level, account_note, warnings):
    warning_list = [
        str(item).strip()
        for item in warnings
        if str(item).strip()
    ]

    indicators = [
        "Market: " + clean_text(market_condition, "unknown"),
        "Risk: " + clean_text(risk_level, "unknown"),
        "Account: " + clean_text(
            account_note,
            "No account issue surfaced.",
        ),
    ]

    if warning_list:
        indicators.append("Warning: " + warning_list[0])

    return (
        indicators[: DASHBOARD_DEFAULT_LIMITS["critical_indicators"]],
        warning_list,
    )


def build_dashboard_drawers():
    return [
        {
            "drawer_id": drawer_id,
            "label": drawer_id.replace("_", " ").title(),
            "explainer": DASHBOARD_DRAWER_EXPLAINERS[drawer_id],
            "default_state": "collapsed",
        }
        for drawer_id in DASHBOARD_DETAIL_DRAWERS
    ]


def build_dashboard_surface(
    attention_items,
    market_condition="unknown",
    risk_level="unknown",
    account_note="No account issue surfaced.",
    warnings=None,
    owner_mode="staging",
):
    policy = get_room_policy(DASHBOARD_ROOM)

    ranked_items = rank_attention_items(attention_items)
    visible_items = ranked_items[: DASHBOARD_DEFAULT_LIMITS["attention_items"]]
    hidden_items = ranked_items[DASHBOARD_DEFAULT_LIMITS["attention_items"] :]

    critical_indicators, warning_list = build_indicator_list(
        market_condition=market_condition,
        risk_level=risk_level,
        account_note=account_note,
        warnings=warnings or [],
    )

    dominant_summary = select_dominant_summary(ranked_items)
    principal_recommendation = select_principal_recommendation(ranked_items)

    safe_to_ignore = (
        DASHBOARD_DETAIL_DRAWERS
        + [item["title"] for item in hidden_items]
        + warning_list[DASHBOARD_DEFAULT_LIMITS["warnings"] :]
    )

    return {
        "room": DASHBOARD_ROOM,
        "page_identity": deepcopy(DASHBOARD_PAGE_IDENTITY),
        "title": policy["purpose"]["title"],
        "display_title": DASHBOARD_PAGE_IDENTITY["display_title"],
        "subtitle": DASHBOARD_PAGE_IDENTITY["subtitle"],
        "question_answered": policy["purpose"]["question"],
        "surface_order": list(DASHBOARD_SURFACE_ORDER),
        "section_headings": deepcopy(DASHBOARD_SECTION_HEADINGS),
        "dominant_summary": dominant_summary,
        "principal_recommendation": principal_recommendation,
        "critical_indicators": critical_indicators,
        "attention_queue": visible_items,
        "hidden_attention_count": len(hidden_items),
        "warnings": warning_list[: DASHBOARD_DEFAULT_LIMITS["warnings"]],
        "hidden_warning_count": max(
            0,
            len(warning_list) - DASHBOARD_DEFAULT_LIMITS["warnings"],
        ),
        "next_action": principal_recommendation,
        "soulaana": soulaana_interpretation(
            room=DASHBOARD_ROOM,
            summary=dominant_summary,
            focus=principal_recommendation,
            next_action=principal_recommendation,
            ignore=safe_to_ignore,
        ),
        "drawers": build_dashboard_drawers(),
        "owner_drawer_default_state": "collapsed",
        "details_hidden_by_default": True,
        "owner_mode": owner_mode,
        "owner_controls": deepcopy(OWNER_CONTROL_POLICY),
        "dangerous_actions": deepcopy(DANGEROUS_ACTION_POLICY),
    }


def empty_dashboard_surface():
    return build_dashboard_surface(
        attention_items=[],
        market_condition="quiet",
        risk_level="low",
        account_note="No account issue surfaced.",
        warnings=[],
        owner_mode="staging",
    )


def dashboard_takeover_handoff():
    return {
        "room": DASHBOARD_ROOM,
        "takeover_summary": (
            "Dashboard is now a small first-glance owner surface. "
            "Wire actual UI components to this contract instead of "
            "rebuilding the doctrine from scratch."
        ),
        "primary_question": DASHBOARD_PAGE_IDENTITY["owner_question"],
        "display_title": DASHBOARD_PAGE_IDENTITY["display_title"],
        "surface_order": list(DASHBOARD_SURFACE_ORDER),
        "section_headings": deepcopy(DASHBOARD_SECTION_HEADINGS),
        "detail_drawers": build_dashboard_drawers(),
        "next_builder_notes": [
            "Keep the hero summary visually dominant.",
            "Keep Soulaana visible near the top of the page.",
            "Show no more than three attention items by default.",
            "Show no more than four critical indicators by default.",
            "Do not scatter global owner settings here.",
            "Use Owner Console for global settings and approvals.",
            "Keep the room Owner Drawer collapsed by default.",
            "Keep dangerous actions behind separate step-up gates.",
        ],
    }


def dashboard_acceptance_contract():
    return {
        "room": DASHBOARD_ROOM,
        "primary_question": DASHBOARD_PAGE_IDENTITY["owner_question"],
        "display_title": DASHBOARD_PAGE_IDENTITY["display_title"],
        "must_show_at_first_glance": [
            "one dominant summary",
            "one principal recommendation",
            "up to four critical indicators",
            "one obvious next action",
            "Soulaana interpretation",
            "plain-language section headings",
        ],
        "must_hide_by_default": list(DASHBOARD_DETAIL_DRAWERS),
        "must_not_show": [
            "wall of equally weighted cards",
            "global owner settings scattered on the Dashboard",
            "dangerous action controls without step-up",
            "full market map detail",
            "full symbol-level detail",
            "raw evidence wall",
        ],
        "section_headings": deepcopy(DASHBOARD_SECTION_HEADINGS),
        "owner_drawer_default_state": "collapsed",
        "dangerous_actions": deepcopy(DANGEROUS_ACTION_POLICY),
    }
