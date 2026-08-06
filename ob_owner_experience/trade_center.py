# Trade Center simplification surface for The Observatory.
#
# This module is UI-framework neutral. It gives the eventual Trade Center
# a clean owner-first data contract instead of an execution-looking wall.
#
# Owner-experience target:
#
#   The Trade Center should answer:
#
#       What decisions or actions are waiting?
#
# The first screen must not look like a broker terminal. It should show a
# calm decision queue:
#
# 1. What decision is waiting?
# 2. Why does it matter?
# 3. What is the risk?
# 4. What gate is locked?
# 5. What should the owner review next?
# 6. What does Soulaana recommend?
#
# This is a review and decision surface, not broker execution.

from copy import deepcopy

from .simplification import (
    DANGEROUS_ACTION_POLICY,
    OWNER_CONTROL_POLICY,
    get_room_policy,
    soulaana_interpretation,
)


TRADE_CENTER_ROOM = "trade_center"

TRADE_CENTER_IDENTITY = {
    "room": TRADE_CENTER_ROOM,
    "route_hint": "/ob/trade-center",
    "owner_question": "What decisions or actions are waiting?",
    "plain_title": "Decisions",
    "display_title": "Decision Garden",
    "emoji": "🌸",
    "subtitle": (
        "A calm owner review room for pending decisions, risk, gates, "
        "checklists, and Soulaana's plain-language guidance."
    ),
}

TRADE_CENTER_SECTION_HEADINGS = {
    "hero": {
        "label": "🌸 Decision Garden",
        "plain_label": "Decision overview",
        "explainer": (
            "This is the top-level decision summary. It should show "
            "what is waiting without looking like a broker terminal."
        ),
    },
    "soulaana": {
        "label": "🧭 Soulaana Guides",
        "plain_label": "Soulaana guidance",
        "explainer": (
            "Soulaana explains what decision is waiting, why it matters, "
            "what risk exists, and what should happen next."
        ),
    },
    "queue": {
        "label": "📬 Waiting Decisions",
        "plain_label": "Decision queue",
        "explainer": (
            "Only the most important pending decisions belong here. "
            "Keep the rest hidden behind drawers."
        ),
    },
    "risk": {
        "label": "🛡️ Risk Gate",
        "plain_label": "Risk and gate state",
        "explainer": (
            "Risk and lock state must be visible before the owner thinks "
            "about any action."
        ),
    },
    "checklist": {
        "label": "✅ Readiness Checklist",
        "plain_label": "Review checklist",
        "explainer": (
            "A small checklist showing what must be reviewed before any "
            "owner decision can move forward."
        ),
    },
    "next_action": {
        "label": "👑 Owner Next Move",
        "plain_label": "Next owner step",
        "explainer": (
            "The one safe next step. This does not submit orders, move "
            "money, or bypass gates."
        ),
    },
    "drawers": {
        "label": "🗂️ Decision Detail Drawers",
        "plain_label": "Hidden decision details",
        "explainer": (
            "Candidate details, broker checklist, receipts, risk notes, "
            "and owner notes stay tucked away by default."
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

TRADE_CENTER_SURFACE_ORDER = [
    "hero",
    "soulaana",
    "queue",
    "risk",
    "checklist",
    "next_action",
    "drawers",
    "owner_drawer",
]

TRADE_CENTER_LIMITS = {
    "decision_items": 3,
    "critical_indicators": 4,
    "checklist_items": 5,
    "warnings": 3,
    "evidence": 5,
}

TRADE_CENTER_DETAIL_DRAWERS = [
    "candidate_context",
    "thesis_context",
    "risk_context",
    "broker_checklist_context",
    "manual_live_context",
    "receipt_context",
    "owner_notes",
]

TRADE_CENTER_DRAWER_EXPLAINERS = {
    "candidate_context": "Candidate decision packet and source context.",
    "thesis_context": "Why this decision exists and what it depends on.",
    "risk_context": "Risk notes, sizing concerns, and failure reasons.",
    "broker_checklist_context": "Manual broker checklist information, not execution.",
    "manual_live_context": "Manual Live Level 1 review context and boundaries.",
    "receipt_context": "Evidence, receipts, hashes, and verification notes.",
    "owner_notes": "Owner-only notes, reminders, and Soulaana interpretation history.",
}

DECISION_PRIORITY_ORDER = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
    "info": 4,
}

DECISION_STATE_LABELS = {
    "review_required": "Review Required",
    "waiting_confirmation": "Waiting For Confirmation",
    "blocked_by_risk": "Blocked By Risk",
    "checklist_needed": "Checklist Needed",
    "ready_for_owner_review": "Ready For Owner Review",
    "not_ready": "Not Ready",
    "unknown": "Unknown",
}

ACTION_KIND_LABELS = {
    "observe": "Observe",
    "review": "Review",
    "checklist": "Checklist",
    "owner_decision": "Owner Decision",
    "hold": "Hold",
    "reject": "Reject",
    "unknown": "Unknown",
}

LOCK_STATE = {
    "production_manual_live_authorized": False,
    "broker_submission_enabled": False,
    "real_capital_movement_enabled": False,
    "direct_vault_upload_enabled": False,
    "live_auto_locked": True,
}


def clean_text(value, fallback):
    text = str(value or "").strip()

    if text:
        return text

    return fallback


def normalize_priority(value):
    text = str(value or "info").strip().lower()

    if text not in DECISION_PRIORITY_ORDER:
        return "info"

    return text


def normalize_decision_state(value):
    text = (
        str(value or "unknown")
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    if text not in DECISION_STATE_LABELS:
        return "unknown"

    return text


def normalize_action_kind(value):
    text = (
        str(value or "unknown")
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    if text not in ACTION_KIND_LABELS:
        return "unknown"

    return text


def clean_limited_list(values, limit):
    cleaned = []

    for value in values:
        text = str(value or "").strip()

        if text:
            cleaned.append(text)

    return cleaned[:limit]


def normalize_decision_item(item):
    priority = normalize_priority(item.get("priority", "info"))
    state = normalize_decision_state(item.get("decision_state", "unknown"))
    action_kind = normalize_action_kind(item.get("action_kind", "unknown"))

    return {
        "decision_id": clean_text(item.get("decision_id"), "unassigned"),
        "title": clean_text(item.get("title"), "Untitled decision"),
        "symbol": clean_text(item.get("symbol"), "UNKNOWN").upper(),
        "why_it_matters": clean_text(
            item.get("why_it_matters"),
            "This may affect an owner review decision.",
        ),
        "recommended_review": clean_text(
            item.get("recommended_review"),
            "Review the decision packet.",
        ),
        "priority": priority,
        "decision_state": state,
        "decision_label": DECISION_STATE_LABELS[state],
        "action_kind": action_kind,
        "action_label": ACTION_KIND_LABELS[action_kind],
        "requires_step_up": bool(item.get("requires_step_up", True)),
        "dangerous_action": bool(item.get("dangerous_action", False)),
        "source": clean_text(item.get("source"), "trade_center"),
    }


def rank_decision_items(items):
    normalized = [
        normalize_decision_item(item)
        for item in items
    ]

    return sorted(
        normalized,
        key=lambda item: (
            DECISION_PRIORITY_ORDER[item["priority"]],
            not item["requires_step_up"],
            item["title"].lower(),
        ),
    )


def select_dominant_summary(decision_items):
    if not decision_items:
        return "No owner trade decisions are waiting right now."

    top_item = decision_items[0]
    count = len(decision_items)

    if count == 1:
        return "One decision is waiting: " + top_item["title"] + "."

    return (
        str(count)
        + " decisions are waiting. Start with "
        + top_item["title"]
        + "."
    )


def select_principal_recommendation(decision_items):
    if not decision_items:
        return "Stay in observation mode until a decision packet is ready."

    top_item = decision_items[0]

    if top_item["dangerous_action"]:
        return "Review only. Dangerous actions require separate step-up."

    if top_item["decision_state"] == "blocked_by_risk":
        return "Open the risk drawer before any owner decision."

    if top_item["decision_state"] == "checklist_needed":
        return "Complete the readiness checklist before owner review."

    return top_item["recommended_review"]


def build_trade_drawers():
    drawers = []

    for drawer_id in TRADE_CENTER_DETAIL_DRAWERS:
        drawers.append(
            {
                "drawer_id": drawer_id,
                "label": drawer_id.replace("_", " ").title(),
                "explainer": TRADE_CENTER_DRAWER_EXPLAINERS[drawer_id],
                "default_state": "collapsed",
            }
        )

    return drawers


def build_checklist_items(raw_items):
    items = clean_limited_list(
        raw_items,
        TRADE_CENTER_LIMITS["checklist_items"],
    )

    return [
        {
            "label": item,
            "checked": False,
            "owner_visible": True,
        }
        for item in items
    ]


def build_lock_summary():
    return {
        "production_manual_live_authorized": False,
        "broker_submission_enabled": False,
        "real_capital_movement_enabled": False,
        "direct_vault_upload_enabled": False,
        "live_auto_locked": True,
        "plain_language": (
            "Viewing and review are allowed. Broker submission, real "
            "capital movement, production Manual Live, and Live Auto "
            "remain locked."
        ),
    }


def build_trade_center_surface(
    decision_items,
    risk_level="unknown",
    checklist_items=None,
    warnings=None,
    evidence=None,
    owner_mode="staging",
):
    policy = get_room_policy(TRADE_CENTER_ROOM)
    ranked_items = rank_decision_items(decision_items)

    visible_items = ranked_items[: TRADE_CENTER_LIMITS["decision_items"]]
    hidden_items = ranked_items[TRADE_CENTER_LIMITS["decision_items"] :]

    warning_list = clean_limited_list(
        warnings or [],
        TRADE_CENTER_LIMITS["warnings"],
    )

    evidence_items = clean_limited_list(
        evidence or [],
        TRADE_CENTER_LIMITS["evidence"],
    )

    checklist = build_checklist_items(
        checklist_items
        or [
            "Confirm thesis",
            "Review risk",
            "Review owner mission account",
            "Confirm no broker submission",
            "Confirm receipt path",
        ]
    )

    dominant_summary = select_dominant_summary(ranked_items)
    recommendation = select_principal_recommendation(ranked_items)

    critical_indicators = [
        "Risk: " + clean_text(risk_level, "unknown"),
        "Broker submission: locked",
        "Money movement: locked",
        "Live Auto: locked",
    ]

    safe_to_ignore = (
        TRADE_CENTER_DETAIL_DRAWERS
        + [item["title"] for item in hidden_items]
        + warning_list[TRADE_CENTER_LIMITS["warnings"] :]
    )

    return {
        "room": TRADE_CENTER_ROOM,
        "page_identity": deepcopy(TRADE_CENTER_IDENTITY),
        "title": policy["purpose"]["title"],
        "display_title": TRADE_CENTER_IDENTITY["display_title"],
        "subtitle": TRADE_CENTER_IDENTITY["subtitle"],
        "question_answered": policy["purpose"]["question"],
        "surface_order": list(TRADE_CENTER_SURFACE_ORDER),
        "section_headings": deepcopy(TRADE_CENTER_SECTION_HEADINGS),
        "dominant_summary": dominant_summary,
        "principal_recommendation": recommendation,
        "decision_queue": visible_items,
        "hidden_decision_count": len(hidden_items),
        "critical_indicators": critical_indicators,
        "risk_level": clean_text(risk_level, "unknown"),
        "lock_summary": build_lock_summary(),
        "readiness_checklist": checklist,
        "warnings": warning_list,
        "evidence": evidence_items,
        "drawers": build_trade_drawers(),
        "soulaana": soulaana_interpretation(
            room=TRADE_CENTER_ROOM,
            summary=dominant_summary,
            focus=recommendation,
            next_action=recommendation,
            ignore=safe_to_ignore,
        ),
        "next_action": recommendation,
        "owner_drawer_default_state": "collapsed",
        "details_hidden_by_default": True,
        "owner_mode": owner_mode,
        "owner_controls": deepcopy(OWNER_CONTROL_POLICY),
        "dangerous_actions": deepcopy(DANGEROUS_ACTION_POLICY),
        "safety_locks": deepcopy(LOCK_STATE),
    }


def empty_trade_center_surface():
    return build_trade_center_surface(
        decision_items=[],
        risk_level="low",
        checklist_items=[],
        warnings=[],
        evidence=[],
        owner_mode="staging",
    )


def trade_center_takeover_handoff():
    return {
        "room": TRADE_CENTER_ROOM,
        "takeover_summary": (
            "Trade Center is now a first-glance Decision Garden surface. "
            "Wire actual UI components to this contract without making "
            "the page look like broker execution."
        ),
        "primary_question": TRADE_CENTER_IDENTITY["owner_question"],
        "display_title": TRADE_CENTER_IDENTITY["display_title"],
        "surface_order": list(TRADE_CENTER_SURFACE_ORDER),
        "section_headings": deepcopy(TRADE_CENTER_SECTION_HEADINGS),
        "detail_drawers": build_trade_drawers(),
        "safety_locks": deepcopy(LOCK_STATE),
        "next_builder_notes": [
            "Keep Decision Garden visually dominant.",
            "Make this a review surface, not a broker terminal.",
            "Keep Soulaana near the top of the page.",
            "Show risk and lock state before action language.",
            "Limit visible waiting decisions to three by default.",
            "Use drawers for candidate, risk, checklist, receipt, and owner-note detail.",
            "Keep the room Owner Drawer collapsed by default.",
            "Keep broker submission and money movement locked.",
            "Keep dangerous actions behind separate step-up gates.",
        ],
    }


def trade_center_acceptance_contract():
    return {
        "room": TRADE_CENTER_ROOM,
        "primary_question": TRADE_CENTER_IDENTITY["owner_question"],
        "display_title": TRADE_CENTER_IDENTITY["display_title"],
        "must_show_at_first_glance": [
            "waiting decision summary",
            "Soulaana guidance",
            "visible decision queue",
            "risk and gate state",
            "readiness checklist",
            "one safe next action",
            "plain-language section headings",
        ],
        "must_hide_by_default": list(TRADE_CENTER_DETAIL_DRAWERS),
        "must_not_show": [
            "broker terminal on first screen",
            "submit order button without step-up",
            "money movement controls",
            "production Manual Live controls",
            "Live Auto unlock controls",
            "global owner settings scattered inside Trade Center",
            "raw evidence wall on first screen",
        ],
        "section_headings": deepcopy(TRADE_CENTER_SECTION_HEADINGS),
        "owner_drawer_default_state": "collapsed",
        "safety_locks": deepcopy(LOCK_STATE),
        "dangerous_actions": deepcopy(DANGEROUS_ACTION_POLICY),
    }
