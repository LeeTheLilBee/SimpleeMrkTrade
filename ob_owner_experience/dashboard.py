from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, List, Mapping, Optional

from .simplification import (
    DANGEROUS_ACTION_POLICY,
    OWNER_CONTROL_POLICY,
    get_room_policy,
    soulaana_interpretation,
)


DASHBOARD_ROOM = "dashboard"

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

DASHBOARD_PRIORITY_ORDER = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
    "info": 4,
}


def _normalize_severity(value: str) -> str:
    severity = str(value or "info").strip().lower()
    if severity not in DASHBOARD_PRIORITY_ORDER:
        return "info"
    return severity


def _clean_text(value: Any, fallback: str) -> str:
    text = str(value or "").strip()
    return text or fallback


def normalize_attention_item(item: Mapping[str, Any]) -> Dict[str, Any]:
    severity = _normalize_severity(str(item.get("severity", "info")))

    return {
        "title": _clean_text(item.get("title"), "Untitled attention item"),
        "why_it_matters": _clean_text(
            item.get("why_it_matters"),
            "This may affect today's owner decision.",
        ),
        "recommended_action": _clean_text(
            item.get("recommended_action"),
            "Review when available.",
        ),
        "severity": severity,
        "source": _clean_text(item.get("source"), "observatory"),
        "requires_owner_action": bool(item.get("requires_owner_action", True)),
    }


def rank_attention_items(items: Iterable[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    normalized = [normalize_attention_item(item) for item in items]

    return sorted(
        normalized,
        key=lambda item: (
            DASHBOARD_PRIORITY_ORDER[item["severity"]],
            not item["requires_owner_action"],
            item["title"].lower(),
        ),
    )


def select_dominant_summary(attention_items: List[Dict[str, Any]]) -> str:
    if not attention_items:
        return "Nothing urgent needs owner attention right now."

    top = attention_items[0]
    count = len(attention_items)

    if count == 1:
        return "One item needs attention: " + top["title"] + "."

    return (
        str(count)
        + " items need attention. Start with "
        + top["title"]
        + "."
    )


def select_principal_recommendation(attention_items: List[Dict[str, Any]]) -> str:
    if not attention_items:
        return "Stay in observation mode and wait for a clearer priority."

    return attention_items[0]["recommended_action"]


def build_dashboard_surface(
    attention_items: Iterable[Mapping[str, Any]],
    market_condition: str = "unknown",
    risk_level: str = "unknown",
    account_note: str = "No account issue surfaced.",
    warnings: Optional[Iterable[str]] = None,
) -> Dict[str, Any]:
    policy = get_room_policy(DASHBOARD_ROOM)
    ranked_items = rank_attention_items(attention_items)
    visible_items = ranked_items[: DASHBOARD_DEFAULT_LIMITS["attention_items"]]
    hidden_items = ranked_items[DASHBOARD_DEFAULT_LIMITS["attention_items"] :]

    warning_list = [
        str(item).strip()
        for item in (warnings or [])
        if str(item).strip()
    ]

    indicators = [
        "Market: " + str(market_condition),
        "Risk: " + str(risk_level),
        "Account: " + str(account_note),
    ]

    if warning_list:
        indicators.append("Warning: " + warning_list[0])

    indicators = indicators[: DASHBOARD_DEFAULT_LIMITS["critical_indicators"]]

    dominant_summary = select_dominant_summary(ranked_items)
    principal_recommendation = select_principal_recommendation(ranked_items)

    return {
        "room": DASHBOARD_ROOM,
        "title": policy["purpose"]["title"],
        "question_answered": policy["purpose"]["question"],
        "dominant_summary": dominant_summary,
        "principal_recommendation": principal_recommendation,
        "critical_indicators": indicators,
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
            ignore=DASHBOARD_DETAIL_DRAWERS + [item["title"] for item in hidden_items],
        ),
        "owner_drawer_default_state": "collapsed",
        "details_hidden_by_default": True,
        "detail_drawers": deepcopy(DASHBOARD_DETAIL_DRAWERS),
        "owner_controls": deepcopy(OWNER_CONTROL_POLICY),
        "dangerous_actions": deepcopy(DANGEROUS_ACTION_POLICY),
    }


def empty_dashboard_surface() -> Dict[str, Any]:
    return build_dashboard_surface(
        attention_items=[],
        market_condition="quiet",
        risk_level="low",
        account_note="No account issue surfaced.",
        warnings=[],
    )


def dashboard_acceptance_contract() -> Dict[str, Any]:
    return {
        "room": DASHBOARD_ROOM,
        "primary_question": "What needs my attention today?",
        "must_show_at_first_glance": [
            "one dominant summary",
            "one principal recommendation",
            "up to four critical indicators",
            "one next action",
            "Soulaana interpretation",
        ],
        "must_hide_by_default": deepcopy(DASHBOARD_DETAIL_DRAWERS),
        "must_not_show": [
            "wall of equally weighted cards",
            "global owner settings scattered on the Dashboard",
            "dangerous action controls without step-up",
        ],
        "owner_drawer_default_state": "collapsed",
        "dangerous_actions": deepcopy(DANGEROUS_ACTION_POLICY),
    }
