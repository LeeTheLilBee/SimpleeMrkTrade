# Owner Console simplification surface for The Observatory.
#
# This module is UI-framework neutral. It gives the eventual Owner Console
# a clean owner-first data contract for global controls.
#
# Owner-experience target:
#
#   The Owner Console should answer:
#
#       What controls need owner attention?
#
# The first screen should not be a scattered admin panel. It should be a
# calm global control room:
#
# 1. What needs owner approval?
# 2. Which mode gates are locked?
# 3. What access/session state matters?
# 4. What safety locks are active?
# 5. What evidence or receipts support the control state?
# 6. What does Soulaana recommend?
#
# This is the global owner control room. Page-specific drawers live in
# each room, but global settings, approvals, access, mode gates, and
# safety locks belong here.

from copy import deepcopy

from .simplification import (
    DANGEROUS_ACTION_POLICY,
    OWNER_CONTROL_POLICY,
    SOULAANA_GLOBAL_POLICY,
    soulaana_interpretation,
)

from .trade_center import LOCK_STATE


OWNER_CONSOLE_ROOM = "owner_console"

OWNER_CONSOLE_IDENTITY = {
    "room": OWNER_CONSOLE_ROOM,
    "route_hint": "/ob/owner-console",
    "owner_question": "What controls need owner attention?",
    "plain_title": "Owner Controls",
    "display_title": "Owner Crown Room",
    "emoji": "👑",
    "subtitle": (
        "A calm global owner control room for approvals, mode gates, "
        "access, sessions, safety locks, evidence, and Soulaana's guidance."
    ),
}

OWNER_CONSOLE_SECTION_HEADINGS = {
    "hero": {
        "label": "👑 Owner Crown Room",
        "plain_label": "Owner control overview",
        "explainer": (
            "This is the global owner summary. It should show what "
            "needs owner attention without scattering controls across rooms."
        ),
    },
    "soulaana": {
        "label": "🧭 Soulaana Advises",
        "plain_label": "Soulaana owner guidance",
        "explainer": (
            "Soulaana explains approvals, gates, access, sessions, "
            "locks, and the safe next owner step in plain language."
        ),
    },
    "approvals": {
        "label": "🪄 Approval Basket",
        "plain_label": "Pending approvals",
        "explainer": (
            "Owner decisions and approvals waiting for review. Keep "
            "this short and move detail into drawers."
        ),
    },
    "modes": {
        "label": "🚦 Mode Gates",
        "plain_label": "Mode and gate state",
        "explainer": (
            "Shows Survey, Paper, Manual Live, Hybrid, and Live Auto "
            "state without opening dangerous controls."
        ),
    },
    "access": {
        "label": "🗝️ Access Watch",
        "plain_label": "Access and permissions",
        "explainer": (
            "Shows owner/session/access concerns that affect who can "
            "enter or use the protected rooms."
        ),
    },
    "sessions": {
        "label": "🕯️ Session Lanterns",
        "plain_label": "Session state",
        "explainer": (
            "Shows owner session continuity, step-up needs, and login "
            "health without exposing secrets."
        ),
    },
    "locks": {
        "label": "🔒 Safety Locks",
        "plain_label": "Safety lock state",
        "explainer": (
            "Shows production, broker, money, Vault upload, and Live "
            "Auto locks early so nobody mistakes review for execution."
        ),
    },
    "evidence": {
        "label": "📎 Proof Shelf",
        "plain_label": "Evidence and receipts",
        "explainer": (
            "Shows the evidence state without making the first screen "
            "a raw receipt wall."
        ),
    },
    "next_action": {
        "label": "👣 Owner Next Step",
        "plain_label": "Next owner step",
        "explainer": (
            "The one safe next step for the owner. This does not deploy, "
            "submit broker orders, move money, or bypass gates."
        ),
    },
    "drawers": {
        "label": "🗂️ Control Detail Drawers",
        "plain_label": "Hidden owner-control details",
        "explainer": (
            "Approval, mode, access, session, safety, deployment, and "
            "evidence detail stay tucked away by default."
        ),
    },
}

OWNER_CONSOLE_SURFACE_ORDER = [
    "hero",
    "soulaana",
    "approvals",
    "modes",
    "access",
    "sessions",
    "locks",
    "evidence",
    "next_action",
    "drawers",
]

OWNER_CONSOLE_LIMITS = {
    "control_items": 3,
    "approval_items": 3,
    "access_notes": 4,
    "session_notes": 4,
    "warnings": 3,
    "evidence": 5,
}

OWNER_CONSOLE_DETAIL_DRAWERS = [
    "approval_context",
    "mode_gate_context",
    "access_context",
    "session_context",
    "deployment_context",
    "safety_lock_context",
    "evidence_context",
    "owner_notes",
]

OWNER_CONSOLE_DRAWER_EXPLAINERS = {
    "approval_context": "Pending owner approvals and decision context.",
    "mode_gate_context": "Survey, Paper, Manual Live, Hybrid, and Live Auto gate detail.",
    "access_context": "Access, permissions, onboarding, and protected-room visibility detail.",
    "session_context": "Login, step-up, continuity, and timeout detail.",
    "deployment_context": "Staging, Render, production, and release boundary notes.",
    "safety_lock_context": "Broker, money, Vault upload, production, and Live Auto lock detail.",
    "evidence_context": "Receipts, hashes, handoffs, and verification notes.",
    "owner_notes": "Owner-only notes, reminders, and Soulaana guidance history.",
}

CONTROL_PRIORITY_ORDER = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
    "info": 4,
}

CONTROL_STATE_LABELS = {
    "needs_owner_review": "Needs Owner Review",
    "approval_waiting": "Approval Waiting",
    "locked": "Locked",
    "healthy": "Healthy",
    "watch": "Watch",
    "blocked": "Blocked",
    "unknown": "Unknown",
}

CONTROL_KIND_LABELS = {
    "approval": "Approval",
    "mode_gate": "Mode Gate",
    "access": "Access",
    "session": "Session",
    "safety_lock": "Safety Lock",
    "evidence": "Evidence",
    "deployment": "Deployment",
    "owner_note": "Owner Note",
    "unknown": "Unknown",
}

OWNER_GLOBAL_CONTROL_POLICY = {
    "global_controls_live_here": True,
    "room_specific_drawers_live_in_rooms": True,
    "dashboard_global_controls_allowed": False,
    "market_map_global_controls_allowed": False,
    "symbol_page_global_controls_allowed": False,
    "trade_center_global_controls_allowed": False,
    "review_center_global_controls_allowed": False,
    "owner_console_is_control_center": True,
}


def clean_text(value, fallback):
    text = str(value or "").strip()

    if text:
        return text

    return fallback


def normalize_priority(value):
    text = str(value or "info").strip().lower()

    if text not in CONTROL_PRIORITY_ORDER:
        return "info"

    return text


def normalize_control_state(value):
    text = (
        str(value or "unknown")
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    if text not in CONTROL_STATE_LABELS:
        return "unknown"

    return text


def normalize_control_kind(value):
    text = (
        str(value or "unknown")
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    if text not in CONTROL_KIND_LABELS:
        return "unknown"

    return text


def clean_limited_list(values, limit):
    cleaned = []

    for value in values:
        text = str(value or "").strip()

        if text:
            cleaned.append(text)

    return cleaned[:limit]


def normalize_control_item(item):
    priority = normalize_priority(item.get("priority", "info"))
    state = normalize_control_state(item.get("control_state", "unknown"))
    kind = normalize_control_kind(item.get("control_kind", "unknown"))

    return {
        "control_id": clean_text(item.get("control_id"), "unassigned"),
        "title": clean_text(item.get("title"), "Untitled owner control"),
        "why_it_matters": clean_text(
            item.get("why_it_matters"),
            "This may affect owner access, approvals, modes, or safety.",
        ),
        "recommended_review": clean_text(
            item.get("recommended_review"),
            "Review the control detail.",
        ),
        "priority": priority,
        "control_state": state,
        "control_label": CONTROL_STATE_LABELS[state],
        "control_kind": kind,
        "control_kind_label": CONTROL_KIND_LABELS[kind],
        "requires_step_up": bool(item.get("requires_step_up", True)),
        "dangerous_action": bool(item.get("dangerous_action", False)),
        "source": clean_text(item.get("source"), "owner_console"),
    }


def rank_control_items(items):
    normalized = [
        normalize_control_item(item)
        for item in items
    ]

    return sorted(
        normalized,
        key=lambda item: (
            CONTROL_PRIORITY_ORDER[item["priority"]],
            not item["requires_step_up"],
            item["title"].lower(),
        ),
    )


def build_owner_console_drawers():
    drawers = []

    for drawer_id in OWNER_CONSOLE_DETAIL_DRAWERS:
        drawers.append(
            {
                "drawer_id": drawer_id,
                "label": drawer_id.replace("_", " ").title(),
                "explainer": OWNER_CONSOLE_DRAWER_EXPLAINERS[drawer_id],
                "default_state": "collapsed",
            }
        )

    return drawers


def build_mode_gate_summary(mode_state=None):
    state = dict(mode_state or {})

    return {
        "survey_enabled": bool(state.get("survey_enabled", True)),
        "paper_enabled": bool(state.get("paper_enabled", True)),
        "manual_live_level_1_owner_only": bool(
            state.get("manual_live_level_1_owner_only", True)
        ),
        "hybrid_locked": bool(state.get("hybrid_locked", True)),
        "live_auto_locked": True,
        "broker_submission_enabled": False,
        "real_capital_movement_enabled": False,
        "plain_language": (
            "Survey and Paper may be visible. Manual Live Level 1 stays "
            "owner-only when authorized. Hybrid and Live Auto remain locked."
        ),
    }


def build_safety_lock_summary():
    return {
        "production_manual_live_authorized": False,
        "broker_submission_enabled": False,
        "real_capital_movement_enabled": False,
        "direct_vault_upload_enabled": False,
        "live_auto_locked": True,
        "dangerous_actions_separately_gated": True,
        "plain_language": (
            "Review and owner visibility are allowed. Production Manual "
            "Live, broker submission, real capital movement, direct Vault "
            "upload, and Live Auto remain locked."
        ),
    }


def select_dominant_summary(control_items):
    if not control_items:
        return "No global owner controls need attention right now."

    top_item = control_items[0]
    count = len(control_items)

    if count == 1:
        return "One owner control needs attention: " + top_item["title"] + "."

    return (
        str(count)
        + " owner controls need attention. Start with "
        + top_item["title"]
        + "."
    )


def select_principal_recommendation(control_items):
    if not control_items:
        return "Keep the system in observation and review mode."

    top_item = control_items[0]

    if top_item["dangerous_action"]:
        return "Review only. Dangerous controls require separate step-up."

    if top_item["control_state"] == "blocked":
        return "Open the blocked control drawer before changing anything."

    if top_item["control_state"] == "approval_waiting":
        return "Review the approval basket before any gate changes."

    if top_item["control_state"] == "locked":
        return "Confirm the lock state before any owner action."

    return top_item["recommended_review"]


def build_owner_console_surface(
    control_items,
    approval_items=None,
    mode_state=None,
    access_notes=None,
    session_notes=None,
    warnings=None,
    evidence=None,
    owner_mode="staging",
):
    ranked_items = rank_control_items(control_items)

    visible_items = ranked_items[: OWNER_CONSOLE_LIMITS["control_items"]]
    hidden_items = ranked_items[OWNER_CONSOLE_LIMITS["control_items"] :]

    approvals = clean_limited_list(
        approval_items or [],
        OWNER_CONSOLE_LIMITS["approval_items"],
    )

    access = clean_limited_list(
        access_notes or [],
        OWNER_CONSOLE_LIMITS["access_notes"],
    )

    sessions = clean_limited_list(
        session_notes or [],
        OWNER_CONSOLE_LIMITS["session_notes"],
    )

    warning_list = clean_limited_list(
        warnings or [],
        OWNER_CONSOLE_LIMITS["warnings"],
    )

    evidence_items = clean_limited_list(
        evidence or [],
        OWNER_CONSOLE_LIMITS["evidence"],
    )

    mode_gates = build_mode_gate_summary(mode_state)
    safety_locks = build_safety_lock_summary()

    dominant_summary = select_dominant_summary(ranked_items)
    recommendation = select_principal_recommendation(ranked_items)

    critical_indicators = [
        "Approvals waiting: " + str(len(approvals)),
        "Mode gates: Hybrid locked / Live Auto locked",
        "Broker submission: locked",
        "Money movement: locked",
    ]

    safe_to_ignore = (
        OWNER_CONSOLE_DETAIL_DRAWERS
        + [item["title"] for item in hidden_items]
        + warning_list[OWNER_CONSOLE_LIMITS["warnings"] :]
    )

    return {
        "room": OWNER_CONSOLE_ROOM,
        "page_identity": deepcopy(OWNER_CONSOLE_IDENTITY),
        "title": OWNER_CONSOLE_IDENTITY["display_title"],
        "display_title": OWNER_CONSOLE_IDENTITY["display_title"],
        "subtitle": OWNER_CONSOLE_IDENTITY["subtitle"],
        "question_answered": OWNER_CONSOLE_IDENTITY["owner_question"],
        "surface_order": list(OWNER_CONSOLE_SURFACE_ORDER),
        "section_headings": deepcopy(OWNER_CONSOLE_SECTION_HEADINGS),
        "dominant_summary": dominant_summary,
        "principal_recommendation": recommendation,
        "control_queue": visible_items,
        "hidden_control_count": len(hidden_items),
        "approval_basket": approvals,
        "access_notes": access,
        "session_notes": sessions,
        "critical_indicators": critical_indicators,
        "mode_gate_summary": mode_gates,
        "safety_locks": safety_locks,
        "global_control_policy": deepcopy(OWNER_GLOBAL_CONTROL_POLICY),
        "warnings": warning_list,
        "evidence": evidence_items,
        "drawers": build_owner_console_drawers(),
        "soulaana": soulaana_interpretation(
            room=OWNER_CONSOLE_ROOM,
            summary=dominant_summary,
            focus=recommendation,
            next_action=recommendation,
            ignore=safe_to_ignore,
        ),
        "next_action": recommendation,
        "details_hidden_by_default": True,
        "owner_mode": owner_mode,
        "owner_controls": deepcopy(OWNER_CONTROL_POLICY),
        "dangerous_actions": deepcopy(DANGEROUS_ACTION_POLICY),
        "soulaana_policy": deepcopy(SOULAANA_GLOBAL_POLICY),
        "owner_drawer_default_state": "not_applicable_global_room",
    }


def empty_owner_console_surface():
    return build_owner_console_surface(
        control_items=[],
        approval_items=[],
        mode_state={},
        access_notes=[],
        session_notes=[],
        warnings=[],
        evidence=[],
        owner_mode="staging",
    )


def owner_console_takeover_handoff():
    return {
        "room": OWNER_CONSOLE_ROOM,
        "takeover_summary": (
            "Owner Console is now a first-glance Owner Crown Room. "
            "Wire actual UI components to this contract and keep global "
            "owner settings centralized here instead of scattering them "
            "through protected rooms."
        ),
        "primary_question": OWNER_CONSOLE_IDENTITY["owner_question"],
        "display_title": OWNER_CONSOLE_IDENTITY["display_title"],
        "surface_order": list(OWNER_CONSOLE_SURFACE_ORDER),
        "section_headings": deepcopy(OWNER_CONSOLE_SECTION_HEADINGS),
        "detail_drawers": build_owner_console_drawers(),
        "mode_gate_summary": build_mode_gate_summary(),
        "safety_locks": build_safety_lock_summary(),
        "global_control_policy": deepcopy(OWNER_GLOBAL_CONTROL_POLICY),
        "next_builder_notes": [
            "Keep Owner Crown Room visually dominant.",
            "Centralize global owner controls here.",
            "Do not scatter global settings across protected rooms.",
            "Keep Soulaana near the top of the page.",
            "Show approvals, mode gates, access, sessions, and locks at first glance.",
            "Keep broker submission and money movement locked.",
            "Keep Live Auto locked.",
            "Use drawers for detailed approval, mode, access, session, deployment, safety, evidence, and owner notes.",
            "Keep dangerous actions behind separate step-up gates.",
        ],
    }


def owner_console_acceptance_contract():
    return {
        "room": OWNER_CONSOLE_ROOM,
        "primary_question": OWNER_CONSOLE_IDENTITY["owner_question"],
        "display_title": OWNER_CONSOLE_IDENTITY["display_title"],
        "must_show_at_first_glance": [
            "global owner control summary",
            "Soulaana owner guidance",
            "pending approvals",
            "mode gate summary",
            "access and session state",
            "safety lock state",
            "one safe next owner step",
            "plain-language section headings",
        ],
        "must_hide_by_default": list(OWNER_CONSOLE_DETAIL_DRAWERS),
        "must_not_show": [
            "global owner settings scattered inside Dashboard",
            "global owner settings scattered inside Market Map",
            "global owner settings scattered inside Symbol Page",
            "global owner settings scattered inside Trade Center",
            "global owner settings scattered inside Review Center",
            "broker submission controls",
            "money movement controls",
            "production Manual Live controls",
            "Live Auto unlock controls",
            "raw evidence wall on first screen",
        ],
        "section_headings": deepcopy(OWNER_CONSOLE_SECTION_HEADINGS),
        "global_control_policy": deepcopy(OWNER_GLOBAL_CONTROL_POLICY),
        "mode_gate_summary": build_mode_gate_summary(),
        "safety_locks": build_safety_lock_summary(),
        "dangerous_actions": deepcopy(DANGEROUS_ACTION_POLICY),
    }
