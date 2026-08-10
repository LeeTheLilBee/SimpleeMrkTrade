from copy import deepcopy
import importlib

from .ui_surface_registry import (
    MUST_NOT_CLAIM,
    OB_REAL_SURFACE_THEME,
    PROTECTED_ROUTE_POLICY,
    build_real_surface_adapter_contract,
    build_surface_registry_entry,
)


_review_center = importlib.import_module("ob_owner_experience.review_center")


def _rc_attr(name, fallback):
    return deepcopy(getattr(_review_center, name, fallback))


REVIEW_CENTER_SECTION_HEADINGS = _rc_attr(
    "REVIEW_CENTER_SECTION_HEADINGS",
    {
        "hero": {
            "label": "🧾 Review Center",
            "plain_label": "Review Center",
            "explainer": "A calm place to understand what happened after decisions.",
        },
        "soulaana": {
            "label": "🧭 Soulaana Reviews",
            "plain_label": "Soulaana Reviews",
            "explainer": "Plain-language reflection before any next decision.",
        },
        "recent_reviews": {
            "label": "📚 Recent Reviews",
            "plain_label": "Recent Reviews",
            "explainer": "Recent decision reviews and outcomes.",
        },
        "decision_replay": {
            "label": "🎞️ Decision Replay",
            "plain_label": "Decision Replay",
            "explainer": "Replay the original decision without turning it into execution.",
        },
        "lesson_patterns": {
            "label": "🧠 Lesson Patterns",
            "plain_label": "Lesson Patterns",
            "explainer": "Patterns, lessons, and corrections from prior decisions.",
        },
        "correction_queue": {
            "label": "🛠️ Correction Queue",
            "plain_label": "Correction Queue",
            "explainer": "Items to improve before future decision flow.",
        },
        "drawers": {
            "label": "🗂️ Review Detail Drawers",
            "plain_label": "Review Detail Drawers",
            "explainer": "Receipts and details stay collapsed until needed.",
        },
        "owner_drawer": {
            "label": "🔐 Owner Drawer",
            "plain_label": "Owner Drawer",
            "explainer": "Owner-only review controls remain collapsed.",
        },
    },
)

REVIEW_CENTER_SURFACE_ORDER = list(
    _rc_attr("REVIEW_CENTER_SURFACE_ORDER", list(REVIEW_CENTER_SECTION_HEADINGS.keys()))
)

for required_key in ["hero", "soulaana"]:
    if required_key not in REVIEW_CENTER_SURFACE_ORDER:
        insert_at = 0 if required_key == "hero" else 1
        REVIEW_CENTER_SURFACE_ORDER.insert(insert_at, required_key)

for required_key in [
    "recent_reviews",
    "decision_replay",
    "lesson_patterns",
    "correction_queue",
    "drawers",
    "owner_drawer",
]:
    if required_key not in REVIEW_CENTER_SURFACE_ORDER:
        REVIEW_CENTER_SURFACE_ORDER.append(required_key)

for key in list(REVIEW_CENTER_SURFACE_ORDER):
    REVIEW_CENTER_SECTION_HEADINGS.setdefault(
        key,
        {
            "label": key.replace("_", " ").title(),
            "plain_label": key.replace("_", " ").title(),
            "explainer": "",
        },
    )


REVIEW_CENTER_REAL_SURFACE_IDENTITY = {
    "package": "ob_review_center_real_surface_wiring_gp006",
    "room": "review_center",
    "display_title": "Review Center",
    "emoji": "🧾",
    "primary_question": "What happened, what did we learn, and what should improve?",
    "decision": "READY_FOR_REVIEW_CENTER_REAL_SURFACE_WIRING_WITH_SAFETY_LOCKS_HELD",
    "plain_language": (
        "Review Center is route-ready as a real owner-facing reflection surface "
        "while execution, broker submission, real capital movement, and Live Auto stay locked."
    ),
}

REVIEW_CENTER_COMPONENT_HINTS = {
    "hero": "ReviewCenterHeroCard",
    "soulaana": "ReviewCenterSoulaanaCard",
    "recent_reviews": "ReviewCenterRecentReviewsList",
    "review_queue": "ReviewCenterRecentReviewsList",
    "reviews": "ReviewCenterRecentReviewsList",
    "review_history": "ReviewCenterRecentReviewsList",
    "decision_replay": "ReviewCenterDecisionReplayCard",
    "replay": "ReviewCenterDecisionReplayCard",
    "trade_replay": "ReviewCenterDecisionReplayCard",
    "receipt_replay": "ReviewCenterDecisionReplayCard",
    "lesson_patterns": "ReviewCenterLessonPatternCard",
    "lessons": "ReviewCenterLessonPatternCard",
    "patterns": "ReviewCenterLessonPatternCard",
    "outcome_patterns": "ReviewCenterLessonPatternCard",
    "correction_queue": "ReviewCenterCorrectionQueueCard",
    "corrections": "ReviewCenterCorrectionQueueCard",
    "next_corrections": "ReviewCenterCorrectionQueueCard",
    "performance": "ReviewCenterOutcomePatternCard",
    "outcomes": "ReviewCenterOutcomePatternCard",
    "receipts": "ReviewCenterReceiptTimeline",
    "receipt_timeline": "ReviewCenterReceiptTimeline",
    "drawers": "ReviewCenterDetailDrawerGroup",
    "details": "ReviewCenterDetailDrawerGroup",
    "detail_drawers": "ReviewCenterDetailDrawerGroup",
    "review_detail_drawers": "ReviewCenterDetailDrawerGroup",
    "receipt_context": "ReviewCenterDetailDrawerGroup",
    "owner_drawer": "ReviewCenterOwnerDrawer",
}

REVIEW_CENTER_DATA_PATHS = {
    "hero": ["review_summary", "dominant_summary", "outcome_summary"],
    "soulaana": ["soulaana"],
    "recent_reviews": ["recent_reviews", "review_queue", "review_history"],
    "review_queue": ["recent_reviews", "review_queue", "review_history"],
    "reviews": ["recent_reviews", "review_queue", "review_history"],
    "review_history": ["recent_reviews", "review_queue", "review_history"],
    "decision_replay": ["decision_replay", "trade_replay", "original_decision"],
    "replay": ["decision_replay", "trade_replay", "original_decision"],
    "trade_replay": ["decision_replay", "trade_replay", "original_decision"],
    "receipt_replay": ["receipt_replay", "receipts", "evidence"],
    "lesson_patterns": ["lesson_patterns", "lessons", "patterns"],
    "lessons": ["lesson_patterns", "lessons", "patterns"],
    "patterns": ["lesson_patterns", "lessons", "patterns"],
    "outcome_patterns": ["outcome_patterns", "performance", "outcomes"],
    "performance": ["outcome_patterns", "performance", "outcomes"],
    "outcomes": ["outcome_patterns", "performance", "outcomes"],
    "correction_queue": ["correction_queue", "corrections", "next_corrections"],
    "corrections": ["correction_queue", "corrections", "next_corrections"],
    "next_corrections": ["correction_queue", "corrections", "next_corrections"],
    "receipts": ["receipts", "receipt_timeline", "evidence"],
    "receipt_timeline": ["receipts", "receipt_timeline", "evidence"],
    "drawers": ["drawers", "detail_drawers", "details_hidden_by_default"],
    "details": ["drawers", "detail_drawers", "details_hidden_by_default"],
    "detail_drawers": ["drawers", "detail_drawers", "details_hidden_by_default"],
    "review_detail_drawers": ["drawers", "detail_drawers", "details_hidden_by_default"],
    "receipt_context": ["receipts", "receipt_context", "evidence"],
    "owner_drawer": ["owner_controls", "owner_drawer_default_state"],
}

REVIEW_CENTER_REQUIRED_FIRST_GLANCE_COMPONENTS = [
    "ReviewCenterHeroCard",
    "ReviewCenterSoulaanaCard",
    "ReviewCenterRecentReviewsList",
    "ReviewCenterDecisionReplayCard",
    "ReviewCenterLessonPatternCard",
    "ReviewCenterCorrectionQueueCard",
]

REVIEW_CENTER_REQUIRED_COLLAPSED_COMPONENTS = [
    "ReviewCenterDetailDrawerGroup",
    "ReviewCenterOwnerDrawer",
]

REVIEW_CENTER_COLLAPSED_KEYS = [
    key
    for key in REVIEW_CENTER_SURFACE_ORDER
    if (
        "drawer" in key
        or "detail" in key
        or "context" in key
        or key in {"drawers", "details", "receipt_context"}
    )
]

REVIEW_CENTER_FIRST_GLANCE_KEYS = [
    key
    for key in REVIEW_CENTER_SURFACE_ORDER
    if key not in REVIEW_CENTER_COLLAPSED_KEYS
]

REVIEW_CENTER_REAL_SURFACE_STATUS = {
    "contract_ready": True,
    "registry_ready": True,
    "real_surface_adapter_ready": True,
    "receipt_review_ready": True,
    "lesson_capture_ready": True,
    "correction_queue_ready": True,
    "broker_submission_enabled": False,
    "real_capital_movement_enabled": False,
    "direct_execution_enabled": False,
    "automated_execution_enabled": False,
    "real_html_rendered": False,
    "tower_return_repaired": False,
    "render_redeployed": False,
    "owner_walkthrough_accepted": False,
    "staging_ready": False,
}

REVIEW_CENTER_ACTION_LOCKS = {
    "review_read_allowed": True,
    "lesson_capture_allowed": True,
    "correction_note_allowed": True,
    "broker_submission_enabled": False,
    "real_capital_movement_enabled": False,
    "direct_execution_enabled": False,
    "automated_execution_enabled": False,
    "live_auto_locked": True,
}


def _unique(values):
    output = []

    for value in values:
        if value not in output:
            output.append(value)

    return output


def _heading_for(section_key):
    heading = REVIEW_CENTER_SECTION_HEADINGS.get(section_key, {})

    return {
        "label": heading.get("label", section_key.replace("_", " ").title()),
        "plain_label": heading.get("plain_label", section_key.replace("_", " ").title()),
        "explainer": heading.get("explainer", ""),
    }


def _component_hint_for(section_key):
    return REVIEW_CENTER_COMPONENT_HINTS.get(
        section_key,
        "ReviewCenter" + section_key.replace("_", " ").title().replace(" ", "") + "Section",
    )


def _data_paths_for(section_key):
    return list(REVIEW_CENTER_DATA_PATHS.get(section_key, [section_key]))


def empty_review_center_real_surface_payload():
    empty_builder = getattr(_review_center, "empty_review_center_surface", None)

    if callable(empty_builder):
        try:
            payload = deepcopy(empty_builder())
        except TypeError:
            payload = {}
    else:
        payload = {}

    if not isinstance(payload, dict):
        payload = {}

    payload.setdefault("room", "review_center")
    payload.setdefault("display_title", "Review Center")
    payload.setdefault(
        "question_answered",
        "What happened, what did we learn, and what should improve?",
    )
    payload.setdefault("section_headings", deepcopy(REVIEW_CENTER_SECTION_HEADINGS))
    payload.setdefault("surface_order", list(REVIEW_CENTER_SURFACE_ORDER))
    payload.setdefault("details_hidden_by_default", True)
    payload.setdefault("owner_drawer_default_state", "collapsed")
    payload.setdefault("review_summary", "No review item is selected right now.")
    payload.setdefault("recent_reviews", [])
    payload.setdefault("decision_replay", {})
    payload.setdefault("lesson_patterns", [])
    payload.setdefault("correction_queue", [])
    payload.setdefault("soulaana", {})

    return payload


def normalize_review_center_surface_payload(surface_payload=None):
    if surface_payload is None:
        surface = empty_review_center_real_surface_payload()
    else:
        surface = deepcopy(surface_payload)

    if not isinstance(surface, dict):
        surface = {}

    surface.setdefault("room", "review_center")
    surface.setdefault("display_title", "Review Center")
    surface.setdefault(
        "question_answered",
        "What happened, what did we learn, and what should improve?",
    )
    surface.setdefault("section_headings", deepcopy(REVIEW_CENTER_SECTION_HEADINGS))
    surface.setdefault("surface_order", list(REVIEW_CENTER_SURFACE_ORDER))
    surface.setdefault("details_hidden_by_default", True)
    surface.setdefault("owner_drawer_default_state", "collapsed")
    surface.setdefault("action_locks", deepcopy(REVIEW_CENTER_ACTION_LOCKS))

    return surface


def build_review_center_section_component(section_key, surface_payload=None):
    surface = normalize_review_center_surface_payload(surface_payload)
    key = str(section_key or "").strip()

    if key not in REVIEW_CENTER_SURFACE_ORDER:
        raise KeyError("Unknown Review Center section: " + str(section_key))

    heading = _heading_for(key)
    default_state = "collapsed" if key in REVIEW_CENTER_COLLAPSED_KEYS else "visible"

    return {
        "section_key": key,
        "component_hint": _component_hint_for(key),
        "heading": heading["label"],
        "plain_heading": heading["plain_label"],
        "explainer": heading["explainer"],
        "data_paths": _data_paths_for(key),
        "first_glance": key in REVIEW_CENTER_FIRST_GLANCE_KEYS,
        "default_state": default_state,
        "source_room": surface["room"],
        "source_display_title": surface["display_title"],
        "action_locks": deepcopy(REVIEW_CENTER_ACTION_LOCKS),
    }


def build_review_center_component_tree(surface_payload=None):
    surface = normalize_review_center_surface_payload(surface_payload)

    return [
        build_review_center_section_component(section_key, surface)
        for section_key in REVIEW_CENTER_SURFACE_ORDER
    ]


def build_review_center_loading_state():
    return {
        "state": "loading",
        "display_title": "Review Center",
        "message": "Gathering review receipts safely...",
        "show_soulaana_placeholder": True,
        "show_skeleton_cards": list(REVIEW_CENTER_REQUIRED_FIRST_GLANCE_COMPONENTS),
        "dangerous_actions_available": False,
        "broker_submission_enabled": False,
        "real_capital_movement_enabled": False,
        "direct_execution_enabled": False,
        "automated_execution_enabled": False,
        "live_auto_locked": True,
    }


def build_review_center_empty_state():
    return {
        "state": "empty",
        "display_title": "Review Center",
        "message": "No review item is selected right now.",
        "soulaana_hint": "Use Review Center after a decision has evidence to learn from.",
        "next_action": "Return to Dashboard, Market Weather, or Decision Garden.",
        "details_hidden_by_default": True,
        "owner_drawer_default_state": "collapsed",
        "dangerous_actions_available": False,
        "broker_submission_enabled": False,
        "real_capital_movement_enabled": False,
        "direct_execution_enabled": False,
        "automated_execution_enabled": False,
        "live_auto_locked": True,
    }


def build_review_center_error_state(error_message="Review Center data could not be loaded."):
    return {
        "state": "error",
        "display_title": "Review Center",
        "message": str(error_message or "Review Center data could not be loaded."),
        "safe_fallback": "Return to Dashboard or Owner Console.",
        "show_dashboard_link": True,
        "show_owner_console_link": True,
        "dangerous_actions_available": False,
        "broker_submission_enabled": False,
        "real_capital_movement_enabled": False,
        "direct_execution_enabled": False,
        "automated_execution_enabled": False,
        "live_auto_locked": True,
    }


def build_review_center_first_glance_components():
    dynamic = [
        _component_hint_for(key)
        for key in REVIEW_CENTER_FIRST_GLANCE_KEYS
    ]

    return _unique(dynamic + REVIEW_CENTER_REQUIRED_FIRST_GLANCE_COMPONENTS)


def build_review_center_collapsed_components():
    dynamic = [
        _component_hint_for(key)
        for key in REVIEW_CENTER_COLLAPSED_KEYS
    ]

    return _unique(dynamic + REVIEW_CENTER_REQUIRED_COLLAPSED_COMPONENTS)


def build_review_center_real_surface(surface_payload=None):
    surface = normalize_review_center_surface_payload(surface_payload)
    registry_entry = build_surface_registry_entry("review_center")
    adapter_contract = build_real_surface_adapter_contract()

    return {
        "package": REVIEW_CENTER_REAL_SURFACE_IDENTITY["package"],
        "room": "review_center",
        "display_title": REVIEW_CENTER_REAL_SURFACE_IDENTITY["display_title"],
        "primary_question": REVIEW_CENTER_REAL_SURFACE_IDENTITY["primary_question"],
        "decision": REVIEW_CENTER_REAL_SURFACE_IDENTITY["decision"],
        "route_hint": registry_entry["route_hint"],
        "component_hint": registry_entry["component_hint"],
        "data_adapter_hint": registry_entry["data_adapter_hint"],
        "source_contract": deepcopy(surface),
        "registry_entry": deepcopy(registry_entry),
        "component_tree": build_review_center_component_tree(surface),
        "first_glance_components": build_review_center_first_glance_components(),
        "collapsed_components": build_review_center_collapsed_components(),
        "loading_state": build_review_center_loading_state(),
        "empty_state": build_review_center_empty_state(),
        "error_state": build_review_center_error_state(),
        "theme": deepcopy(OB_REAL_SURFACE_THEME),
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "action_locks": deepcopy(REVIEW_CENTER_ACTION_LOCKS),
        "surface_status": deepcopy(REVIEW_CENTER_REAL_SURFACE_STATUS),
        "safety_summary": deepcopy(adapter_contract["safety_summary"]),
        "soulaana": surface.get("soulaana", {}),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "next_build": "OB Owner Console real surface wiring / GP007",
    }


def build_review_center_real_surface_acceptance_contract():
    real_surface = build_review_center_real_surface()

    return {
        "package": REVIEW_CENTER_REAL_SURFACE_IDENTITY["package"],
        "room": "review_center",
        "display_title": REVIEW_CENTER_REAL_SURFACE_IDENTITY["display_title"],
        "primary_question": REVIEW_CENTER_REAL_SURFACE_IDENTITY["primary_question"],
        "decision": REVIEW_CENTER_REAL_SURFACE_IDENTITY["decision"],
        "route_hint": real_surface["route_hint"],
        "component_hint": real_surface["component_hint"],
        "must_show_at_first_glance": list(REVIEW_CENTER_REQUIRED_FIRST_GLANCE_COMPONENTS),
        "must_hide_by_default": list(REVIEW_CENTER_REQUIRED_COLLAPSED_COMPONENTS),
        "must_include_states": ["loading", "empty", "error"],
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "action_locks": deepcopy(REVIEW_CENTER_ACTION_LOCKS),
        "safety_summary": deepcopy(real_surface["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
    }


def build_review_center_real_surface_takeover_handoff():
    contract = build_review_center_real_surface_acceptance_contract()

    return {
        "package": contract["package"],
        "display_title": contract["display_title"],
        "takeover_summary": (
            "GP006 wired Review Center as a real-app surface adapter. "
            "Review Center is route-ready for receipts, replay, lessons, and corrections "
            "while broker submission, real capital movement, direct execution, "
            "automated execution, and Live Auto remain locked."
        ),
        "route_hint": contract["route_hint"],
        "component_tree": build_review_center_component_tree(),
        "loading_state": build_review_center_loading_state(),
        "empty_state": build_review_center_empty_state(),
        "error_state": build_review_center_error_state(),
        "action_locks": contract["action_locks"],
        "safety_summary": contract["safety_summary"],
        "must_not_claim": contract["must_not_claim"],
        "next_builder_notes": [
            "Use ReviewCenterHeroCard for the first card.",
            "Keep Soulaana near the top.",
            "Show recent reviews without making them executable.",
            "Show decision replay as read-only.",
            "Show lesson patterns before future corrections.",
            "Show correction queue as notes only.",
            "Keep detail drawers collapsed by default.",
            "Keep Owner Drawer collapsed by default.",
            "Keep broker submission locked.",
            "Keep real capital movement locked.",
            "Keep direct execution disabled.",
            "Keep automated execution disabled.",
            "Keep Live Auto locked.",
            "Do not claim STAGING_READY.",
            "Next build is GP007 Owner Console real surface wiring.",
        ],
    }
