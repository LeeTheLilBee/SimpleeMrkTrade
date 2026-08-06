# Review Center simplification surface for The Observatory.
#
# This module is UI-framework neutral. It gives the eventual Review Center
# a clean owner-first data contract instead of a receipt/performance wall.
#
# Owner-experience target:
#
#   The Review Center should answer:
#
#       What did we learn and what needs review?
#
# The first screen should not drown the owner in raw logs, hashes,
# performance tables, trade history, or screenshots. It should show a
# calm reflection surface:
#
# 1. What happened?
# 2. What did we learn?
# 3. Are receipts verified?
# 4. What pattern or mistake needs attention?
# 5. What should the owner review next?
# 6. What does Soulaana recommend?
#
# This is a review and learning room, not an execution room.

from copy import deepcopy

from .simplification import (
    DANGEROUS_ACTION_POLICY,
    OWNER_CONTROL_POLICY,
    get_room_policy,
    soulaana_interpretation,
)

from .trade_center import LOCK_STATE


REVIEW_CENTER_ROOM = "review_center"

REVIEW_CENTER_IDENTITY = {
    "room": REVIEW_CENTER_ROOM,
    "route_hint": "/ob/review-center",
    "owner_question": "What did we learn and what needs review?",
    "plain_title": "Review",
    "display_title": "Reflection Library",
    "emoji": "📚",
    "subtitle": (
        "A calm owner review room for outcomes, lessons, receipts, "
        "patterns, mistakes, and Soulaana's plain-language reflection."
    ),
}

REVIEW_CENTER_SECTION_HEADINGS = {
    "hero": {
        "label": "📚 Reflection Library",
        "plain_label": "Review overview",
        "explainer": (
            "This is the top-level review summary. It should show what "
            "happened and what needs the owner's attention."
        ),
    },
    "soulaana": {
        "label": "🧭 Soulaana Reflects",
        "plain_label": "Soulaana reflection",
        "explainer": (
            "Soulaana explains the outcome, the lesson, the receipt "
            "state, and what the owner should review next."
        ),
    },
    "outcomes": {
        "label": "🪴 What Happened",
        "plain_label": "Outcome summary",
        "explainer": (
            "A short outcome read. This should not become a full trade "
            "history table."
        ),
    },
    "receipts": {
        "label": "🧾 Receipt Check",
        "plain_label": "Receipt status",
        "explainer": (
            "Shows whether evidence and receipts are verified, pending, "
            "missing, or failed."
        ),
    },
    "lessons": {
        "label": "🧠 Lesson Shelf",
        "plain_label": "Lessons learned",
        "explainer": (
            "The main lesson or improvement. The owner should not have "
            "to dig through raw receipts to find the takeaway."
        ),
    },
    "patterns": {
        "label": "🪞 Pattern Mirror",
        "plain_label": "Patterns and mistakes",
        "explainer": (
            "Shows repeated behavior, mistakes, strengths, or risks that "
            "need attention."
        ),
    },
    "next_review": {
        "label": "👑 Owner Next Review",
        "plain_label": "Next review step",
        "explainer": (
            "The one safe next review step. This does not submit broker "
            "orders, move money, or bypass gates."
        ),
    },
    "drawers": {
        "label": "🗂️ Review Detail Drawers",
        "plain_label": "Hidden review details",
        "explainer": (
            "Receipts, performance detail, mistake detail, pattern logs, "
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

REVIEW_CENTER_SURFACE_ORDER = [
    "hero",
    "soulaana",
    "outcomes",
    "receipts",
    "lessons",
    "patterns",
    "next_review",
    "drawers",
    "owner_drawer",
]

REVIEW_CENTER_LIMITS = {
    "review_items": 3,
    "lessons": 4,
    "patterns": 4,
    "warnings": 3,
    "evidence": 5,
}

REVIEW_CENTER_DETAIL_DRAWERS = [
    "outcome_context",
    "receipt_context",
    "performance_context",
    "mistake_context",
    "pattern_context",
    "improvement_context",
    "owner_notes",
]

REVIEW_CENTER_DRAWER_EXPLAINERS = {
    "outcome_context": "Outcome detail and review packet context.",
    "receipt_context": "Receipts, hashes, evidence, and verification notes.",
    "performance_context": "Performance detail that should not crowd the first screen.",
    "mistake_context": "Mistakes, misses, and avoid-repeat notes.",
    "pattern_context": "Repeated behavior, strengths, weaknesses, and market context.",
    "improvement_context": "What to improve next and how to adjust the process.",
    "owner_notes": "Owner-only notes, reminders, and Soulaana reflection history.",
}

REVIEW_PRIORITY_ORDER = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
    "info": 4,
}

REVIEW_OUTCOME_LABELS = {
    "win": "Win",
    "loss": "Loss",
    "mixed": "Mixed",
    "missed": "Missed",
    "avoided": "Avoided",
    "pending": "Pending",
    "unknown": "Unknown",
}

RECEIPT_STATUS_LABELS = {
    "verified": "Verified",
    "pending": "Pending",
    "missing": "Missing",
    "failed": "Failed",
    "not_required": "Not Required",
    "unknown": "Unknown",
}


def clean_text(value, fallback):
    text = str(value or "").strip()

    if text:
        return text

    return fallback


def normalize_priority(value):
    text = str(value or "info").strip().lower()

    if text not in REVIEW_PRIORITY_ORDER:
        return "info"

    return text


def normalize_outcome(value):
    text = (
        str(value or "unknown")
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    if text not in REVIEW_OUTCOME_LABELS:
        return "unknown"

    return text


def normalize_receipt_status(value):
    text = (
        str(value or "unknown")
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    if text not in RECEIPT_STATUS_LABELS:
        return "unknown"

    return text


def clean_limited_list(values, limit):
    cleaned = []

    for value in values:
        text = str(value or "").strip()

        if text:
            cleaned.append(text)

    return cleaned[:limit]


def normalize_review_item(item):
    priority = normalize_priority(item.get("priority", "info"))
    outcome = normalize_outcome(item.get("outcome", "unknown"))
    receipt_status = normalize_receipt_status(
        item.get("receipt_status", "unknown")
    )

    return {
        "review_id": clean_text(item.get("review_id"), "unassigned"),
        "title": clean_text(item.get("title"), "Untitled review"),
        "symbol": clean_text(item.get("symbol"), "UNKNOWN").upper(),
        "what_happened": clean_text(
            item.get("what_happened"),
            "Outcome detail has not been summarized yet.",
        ),
        "lesson": clean_text(
            item.get("lesson"),
            "No lesson has been written yet.",
        ),
        "recommended_review": clean_text(
            item.get("recommended_review"),
            "Review the outcome packet.",
        ),
        "priority": priority,
        "outcome": outcome,
        "outcome_label": REVIEW_OUTCOME_LABELS[outcome],
        "receipt_status": receipt_status,
        "receipt_label": RECEIPT_STATUS_LABELS[receipt_status],
        "needs_owner_review": bool(item.get("needs_owner_review", True)),
        "source": clean_text(item.get("source"), "review_center"),
    }


def rank_review_items(items):
    normalized = [
        normalize_review_item(item)
        for item in items
    ]

    return sorted(
        normalized,
        key=lambda item: (
            REVIEW_PRIORITY_ORDER[item["priority"]],
            not item["needs_owner_review"],
            item["title"].lower(),
        ),
    )


def select_dominant_summary(review_items):
    if not review_items:
        return "No owner reviews are waiting right now."

    top_item = review_items[0]
    count = len(review_items)

    if count == 1:
        return "One review is waiting: " + top_item["title"] + "."

    return (
        str(count)
        + " reviews are waiting. Start with "
        + top_item["title"]
        + "."
    )


def select_principal_recommendation(review_items, receipt_status):
    if not review_items:
        return "Stay in observation mode until a review packet is ready."

    if receipt_status in {"missing", "failed"}:
        return "Open the receipt drawer before closing this review."

    top_item = review_items[0]

    if top_item["receipt_status"] in {"missing", "failed"}:
        return "Open the receipt drawer before closing this review."

    if top_item["outcome"] == "loss":
        return "Read the lesson and mistake drawer before changing behavior."

    if top_item["outcome"] == "missed":
        return "Review the pattern mirror before the next similar setup."

    return top_item["recommended_review"]


def build_review_drawers():
    drawers = []

    for drawer_id in REVIEW_CENTER_DETAIL_DRAWERS:
        drawers.append(
            {
                "drawer_id": drawer_id,
                "label": drawer_id.replace("_", " ").title(),
                "explainer": REVIEW_CENTER_DRAWER_EXPLAINERS[drawer_id],
                "default_state": "collapsed",
            }
        )

    return drawers


def build_receipt_summary(receipt_status):
    status = normalize_receipt_status(receipt_status)

    return {
        "receipt_status": status,
        "receipt_label": RECEIPT_STATUS_LABELS[status],
        "verified": status == "verified",
        "needs_attention": status in {"missing", "failed", "pending"},
        "plain_language": (
            "Receipts are verified."
            if status == "verified"
            else "Receipt state needs review before this review is closed."
        ),
    }


def build_review_center_surface(
    review_items,
    outcome_summary="",
    overall_learning="",
    receipt_status="unknown",
    lessons=None,
    patterns=None,
    warnings=None,
    evidence=None,
    owner_mode="staging",
):
    try:
        policy = get_room_policy(REVIEW_CENTER_ROOM)
        title = policy["purpose"]["title"]
    except Exception:
        title = REVIEW_CENTER_IDENTITY["display_title"]

    ranked_items = rank_review_items(review_items)

    visible_items = ranked_items[: REVIEW_CENTER_LIMITS["review_items"]]
    hidden_items = ranked_items[REVIEW_CENTER_LIMITS["review_items"] :]

    lesson_list = clean_limited_list(
        lessons or [],
        REVIEW_CENTER_LIMITS["lessons"],
    )

    pattern_list = clean_limited_list(
        patterns or [],
        REVIEW_CENTER_LIMITS["patterns"],
    )

    warning_list = clean_limited_list(
        warnings or [],
        REVIEW_CENTER_LIMITS["warnings"],
    )

    evidence_items = clean_limited_list(
        evidence or [],
        REVIEW_CENTER_LIMITS["evidence"],
    )

    receipt_summary = build_receipt_summary(receipt_status)
    dominant_summary = select_dominant_summary(ranked_items)

    learning = clean_text(
        overall_learning,
        "No overall lesson has been written yet.",
    )

    outcome_read = clean_text(
        outcome_summary,
        "No outcome summary has been written yet.",
    )

    recommendation = select_principal_recommendation(
        ranked_items,
        receipt_summary["receipt_status"],
    )

    critical_indicators = [
        "Receipt: " + receipt_summary["receipt_label"],
        "Reviews waiting: " + str(len(ranked_items)),
        "Broker submission: locked",
        "Money movement: locked",
    ]

    safe_to_ignore = (
        REVIEW_CENTER_DETAIL_DRAWERS
        + [item["title"] for item in hidden_items]
        + warning_list[REVIEW_CENTER_LIMITS["warnings"] :]
    )

    return {
        "room": REVIEW_CENTER_ROOM,
        "page_identity": deepcopy(REVIEW_CENTER_IDENTITY),
        "title": title,
        "display_title": REVIEW_CENTER_IDENTITY["display_title"],
        "subtitle": REVIEW_CENTER_IDENTITY["subtitle"],
        "question_answered": REVIEW_CENTER_IDENTITY["owner_question"],
        "surface_order": list(REVIEW_CENTER_SURFACE_ORDER),
        "section_headings": deepcopy(REVIEW_CENTER_SECTION_HEADINGS),
        "dominant_summary": dominant_summary,
        "outcome_summary": outcome_read,
        "overall_learning": learning,
        "receipt_summary": receipt_summary,
        "review_queue": visible_items,
        "hidden_review_count": len(hidden_items),
        "critical_indicators": critical_indicators,
        "lessons": lesson_list,
        "patterns": pattern_list,
        "warnings": warning_list,
        "evidence": evidence_items,
        "drawers": build_review_drawers(),
        "soulaana": soulaana_interpretation(
            room=REVIEW_CENTER_ROOM,
            summary=dominant_summary,
            focus=learning,
            next_action=recommendation,
            ignore=safe_to_ignore,
        ),
        "principal_recommendation": recommendation,
        "next_action": recommendation,
        "owner_drawer_default_state": "collapsed",
        "details_hidden_by_default": True,
        "owner_mode": owner_mode,
        "owner_controls": deepcopy(OWNER_CONTROL_POLICY),
        "dangerous_actions": deepcopy(DANGEROUS_ACTION_POLICY),
        "safety_locks": deepcopy(LOCK_STATE),
    }


def empty_review_center_surface():
    return build_review_center_surface(
        review_items=[],
        outcome_summary="No outcome summary has been written yet.",
        overall_learning="No overall lesson has been written yet.",
        receipt_status="not_required",
        lessons=[],
        patterns=[],
        warnings=[],
        evidence=[],
        owner_mode="staging",
    )


def review_center_takeover_handoff():
    return {
        "room": REVIEW_CENTER_ROOM,
        "takeover_summary": (
            "Review Center is now a first-glance Reflection Library "
            "surface. Wire actual UI components to this contract without "
            "making the page a raw receipt, performance, or history wall."
        ),
        "primary_question": REVIEW_CENTER_IDENTITY["owner_question"],
        "display_title": REVIEW_CENTER_IDENTITY["display_title"],
        "surface_order": list(REVIEW_CENTER_SURFACE_ORDER),
        "section_headings": deepcopy(REVIEW_CENTER_SECTION_HEADINGS),
        "detail_drawers": build_review_drawers(),
        "safety_locks": deepcopy(LOCK_STATE),
        "next_builder_notes": [
            "Keep Reflection Library visually dominant.",
            "Make this a learning surface, not an execution surface.",
            "Keep Soulaana near the top of the page.",
            "Show receipt state early.",
            "Show lessons before raw evidence.",
            "Limit visible review items to three by default.",
            "Use drawers for outcome, receipt, performance, mistake, pattern, improvement, and owner-note detail.",
            "Keep the room Owner Drawer collapsed by default.",
            "Keep broker submission and money movement locked.",
            "Keep dangerous actions behind separate step-up gates.",
        ],
    }


def review_center_acceptance_contract():
    return {
        "room": REVIEW_CENTER_ROOM,
        "primary_question": REVIEW_CENTER_IDENTITY["owner_question"],
        "display_title": REVIEW_CENTER_IDENTITY["display_title"],
        "must_show_at_first_glance": [
            "review summary",
            "Soulaana reflection",
            "outcome summary",
            "receipt status",
            "lessons learned",
            "patterns or mistakes",
            "one safe next review step",
            "plain-language section headings",
        ],
        "must_hide_by_default": list(REVIEW_CENTER_DETAIL_DRAWERS),
        "must_not_show": [
            "raw receipt wall on first screen",
            "performance table wall on first screen",
            "full trade history wall on first screen",
            "broker terminal controls",
            "submit order button",
            "money movement controls",
            "Live Auto unlock controls",
            "global owner settings scattered inside Review Center",
        ],
        "section_headings": deepcopy(REVIEW_CENTER_SECTION_HEADINGS),
        "owner_drawer_default_state": "collapsed",
        "safety_locks": deepcopy(LOCK_STATE),
        "dangerous_actions": deepcopy(DANGEROUS_ACTION_POLICY),
    }
