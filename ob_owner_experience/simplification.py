from copy import deepcopy

ROOM_PURPOSES = {
    "dashboard": {
        "title": "Today",
        "question": "What needs my attention today?",
        "plain_language": "A short command view of what matters now.",
        "primary_action": "Review the one highest-priority item.",
    },
    "market_map": {
        "title": "Market",
        "question": "What is happening in the market?",
        "plain_language": "The overall market condition without every metric at once.",
        "primary_action": "Check risk first, then the strongest opportunity.",
    },
    "symbol_page": {
        "title": "Asset",
        "question": "What do I need to understand about this asset?",
        "plain_language": "A focused explanation of one symbol or asset.",
        "primary_action": "Read the thesis, risk, and next decision.",
    },
    "trade_center": {
        "title": "Decisions",
        "question": "What decisions or actions are waiting?",
        "plain_language": "A gated queue of pending review items.",
        "primary_action": "Approve nothing dangerous without step-up.",
    },
    "review_center": {
        "title": "Review",
        "question": "What happened, and what should I learn?",
        "plain_language": "A learning room for outcomes, receipts, and lessons.",
        "primary_action": "Review the most important result and lesson.",
    },
    "owner_console": {
        "title": "Owner",
        "question": "What owner-level controls, approvals, and settings exist?",
        "plain_language": "The proper home for global owner settings and controls.",
        "primary_action": "Use step-up before any dangerous owner action.",
    },
}

SOULAANA_GLOBAL_POLICY = {
    "visible_on_every_protected_room": True,
    "not_optional_chatbot": True,
    "role": "owner guide and command interpreter",
    "must_answer": [
        "What am I looking at?",
        "Why does it matter?",
        "What should I focus on?",
        "What can I safely ignore?",
        "What should I do next?",
    ],
}

OWNER_CONTROL_POLICY = {
    "blanket_owner_visibility": True,
    "global_owner_controls_home": "owner_console",
    "per_room_owner_drawer": "collapsed_by_default",
    "ordinary_pages_must_not_scatter_global_settings": True,
    "dangerous_actions_require_step_up": True,
}

DANGEROUS_ACTION_POLICY = {
    "deployment": "separately_gated",
    "secrets": "separately_gated",
    "trading": "separately_gated",
    "broker_submission": "separately_gated",
    "money_movement": "separately_gated",
    "destructive_controls": "separately_gated",
    "default_state": "disabled_until_authorized",
}

MARKET_MAP_DEEP_DIVES = [
    "sector_details",
    "market_breadth",
    "correlations",
    "volatility",
    "flows",
    "technical_signals",
    "symbol_level_data",
    "evidence",
    "research_detail",
    "historical_comparisons",
]

DEFAULT_ROOM_POLICY = {
    "initial_surface": {
        "dominant_summary_count": 1,
        "principal_recommendation_count": 1,
        "critical_indicator_limit": 4,
        "obvious_next_action_count": 1,
        "soulaana_interpretation_required": True,
    },
    "progressive_disclosure": [
        "drawers",
        "tabs",
        "expanders",
        "dedicated_deep_dive_rooms",
        "show_details_controls",
    ],
    "visual_hierarchy": {
        "wall_of_cards_allowed": False,
        "every_component_equal_weight": False,
        "plain_headings_required": True,
        "short_subtitles_required_for_technical_terms": True,
    },
    "owner_drawer": {
        "present": True,
        "default_state": "collapsed",
        "scope": "room_specific_controls_only",
    },
}

ROOM_EXTRA_POLICY = {
    "market_map": {
        "first_glance_fields": [
            "overall_market_condition",
            "current_risk_level",
            "most_important_movement",
            "strongest_opportunities",
            "most_important_warnings",
            "soulaana_plain_language_interpretation",
        ],
        "deep_dive_tabs": MARKET_MAP_DEEP_DIVES,
    },
    "owner_console": {
        "allowed_global_controls": [
            "settings",
            "approvals",
            "security_controls",
            "permissions",
            "deployment_controls",
            "ecosystem_owner_decisions",
        ],
    },
}

def _merge_dicts(base, extra):
    result = deepcopy(base)
    for key, value in extra.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _merge_dicts(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result

def _normalize_room(room):
    return room.strip().lower().replace("-", "_").replace(" ", "_")

def get_room_policy(room):
    normalized = _normalize_room(room)
    if normalized not in ROOM_PURPOSES:
        raise KeyError("Unknown Observatory room: " + room)
    policy = _merge_dicts(DEFAULT_ROOM_POLICY, ROOM_EXTRA_POLICY.get(normalized, {}))
    policy["room"] = normalized
    policy["purpose"] = deepcopy(ROOM_PURPOSES[normalized])
    policy["soulaana"] = deepcopy(SOULAANA_GLOBAL_POLICY)
    policy["owner_controls"] = deepcopy(OWNER_CONTROL_POLICY)
    policy["dangerous_actions"] = deepcopy(DANGEROUS_ACTION_POLICY)
    return policy

def build_owner_experience_doctrine():
    return {
        "doctrine": "ob_owner_experience_simplification",
        "version": "1.0",
        "staging_decision": "HOSTED_STAGING_FUNCTIONAL_HOLD_FOR_OWNER_UI_SIMPLIFICATION",
        "protected_rooms": list(ROOM_PURPOSES),
        "room_policies": {room: get_room_policy(room) for room in ROOM_PURPOSES},
        "soulaana_global_policy": deepcopy(SOULAANA_GLOBAL_POLICY),
        "owner_control_policy": deepcopy(OWNER_CONTROL_POLICY),
        "dangerous_action_policy": deepcopy(DANGEROUS_ACTION_POLICY),
    }

def soulaana_interpretation(room, summary, focus, next_action, ignore=None):
    policy = get_room_policy(room)
    return {
        "room": policy["room"],
        "soulaana_visible": True,
        "role": SOULAANA_GLOBAL_POLICY["role"],
        "what_you_are_looking_at": summary,
        "why_it_matters": policy["purpose"]["plain_language"],
        "focus_on": focus,
        "safe_to_ignore_for_now": list(ignore or []),
        "next_action": next_action,
    }

def build_room_surface(room, dominant_summary, principal_recommendation, critical_indicators, next_action):
    policy = get_room_policy(room)
    indicators = list(critical_indicators)
    limit = int(policy["initial_surface"]["critical_indicator_limit"])
    return {
        "room": policy["room"],
        "title": policy["purpose"]["title"],
        "question_answered": policy["purpose"]["question"],
        "dominant_summary": dominant_summary,
        "principal_recommendation": principal_recommendation,
        "critical_indicators": indicators[:limit],
        "next_action": next_action,
        "soulaana": soulaana_interpretation(
            room=policy["room"],
            summary=dominant_summary,
            focus=principal_recommendation,
            next_action=next_action,
            ignore=indicators[limit:],
        ),
        "owner_drawer_default_state": policy["owner_drawer"]["default_state"],
        "details_hidden_by_default": True,
    }

def market_map_first_glance_surface(
    overall_market_condition,
    current_risk_level,
    most_important_movement,
    strongest_opportunities,
    most_important_warnings,
):
    opportunities = list(strongest_opportunities)
    warnings = list(most_important_warnings)
    summary = "Market condition: " + overall_market_condition + ". Risk: " + current_risk_level + "."
    return {
        "room": "market_map",
        "title": ROOM_PURPOSES["market_map"]["title"],
        "question_answered": ROOM_PURPOSES["market_map"]["question"],
        "overall_market_condition": overall_market_condition,
        "current_risk_level": current_risk_level,
        "most_important_movement": most_important_movement,
        "strongest_opportunities": opportunities[:3],
        "most_important_warnings": warnings[:3],
        "soulaana": soulaana_interpretation(
            room="market_map",
            summary=summary,
            focus=most_important_movement,
            next_action="Review risk first, then open deep dives only if needed.",
            ignore=MARKET_MAP_DEEP_DIVES,
        ),
        "deep_dive_tabs_hidden_by_default": MARKET_MAP_DEEP_DIVES,
        "details_hidden_by_default": True,
    }
