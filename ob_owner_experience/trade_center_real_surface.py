from copy import deepcopy
import importlib

from .ui_surface_registry import (
    MUST_NOT_CLAIM,
    OB_REAL_SURFACE_THEME,
    PROTECTED_ROUTE_POLICY,
    build_real_surface_adapter_contract,
    build_surface_registry_entry,
)


_trade_center = importlib.import_module("ob_owner_experience.trade_center")


def _tc_attr(name, fallback):
    return deepcopy(getattr(_trade_center, name, fallback))


TRADE_CENTER_SECTION_HEADINGS = _tc_attr(
    "TRADE_CENTER_SECTION_HEADINGS",
    {
        "hero": {
            "label": "🌸 Decision Garden",
            "plain_label": "Decision Garden",
            "explainer": "The simple owner-first decision room.",
        },
        "soulaana": {
            "label": "🧭 Soulaana Guides",
            "plain_label": "Soulaana Guides",
            "explainer": "Plain-language guidance before action.",
        },
        "waiting_decisions": {
            "label": "📬 Waiting Decisions",
            "plain_label": "Waiting Decisions",
            "explainer": "Owner-reviewed decisions waiting safely.",
        },
        "risk_gate": {
            "label": "🛡️ Risk Gate",
            "plain_label": "Risk Gate",
            "explainer": "Risk appears before readiness or next move.",
        },
        "readiness_checklist": {
            "label": "✅ Readiness Checklist",
            "plain_label": "Readiness Checklist",
            "explainer": "Checklist preview only; not execution.",
        },
        "owner_next_move": {
            "label": "👑 Owner Next Move",
            "plain_label": "Owner Next Move",
            "explainer": "The next safe owner step.",
        },
        "drawers": {
            "label": "🗂️ Decision Detail Drawers",
            "plain_label": "Decision Detail Drawers",
            "explainer": "Detailed context stays collapsed until needed.",
        },
        "owner_drawer": {
            "label": "🔐 Owner Drawer",
            "plain_label": "Owner Drawer",
            "explainer": "Owner-only controls remain collapsed.",
        },
    },
)

TRADE_CENTER_SURFACE_ORDER = list(
    _tc_attr("TRADE_CENTER_SURFACE_ORDER", list(TRADE_CENTER_SECTION_HEADINGS.keys()))
)

for required_key in ["hero", "soulaana"]:
    if required_key not in TRADE_CENTER_SURFACE_ORDER:
        insert_at = 0 if required_key == "hero" else 1
        TRADE_CENTER_SURFACE_ORDER.insert(insert_at, required_key)

for required_key in [
    "waiting_decisions",
    "risk_gate",
    "readiness_checklist",
    "owner_next_move",
    "drawers",
    "owner_drawer",
]:
    if required_key not in TRADE_CENTER_SURFACE_ORDER:
        TRADE_CENTER_SURFACE_ORDER.append(required_key)

for key in list(TRADE_CENTER_SURFACE_ORDER):
    TRADE_CENTER_SECTION_HEADINGS.setdefault(
        key,
        {
            "label": key.replace("_", " ").title(),
            "plain_label": key.replace("_", " ").title(),
            "explainer": "",
        },
    )

TRADE_CENTER_LOCK_STATE = _tc_attr(
    "LOCK_STATE",
    _tc_attr(
        "TRADE_CENTER_LOCK_STATE",
        {
            "production_manual_live_authorized": False,
            "broker_submission_enabled": False,
            "real_capital_movement_enabled": False,
            "direct_vault_upload_enabled": False,
            "live_auto_locked": True,
        },
    ),
)

TRADE_CENTER_REAL_SURFACE_IDENTITY = {
    "package": "ob_trade_center_real_surface_wiring_gp005",
    "room": "trade_center",
    "display_title": "Decision Garden",
    "emoji": "🌸",
    "primary_question": "What decision is waiting and is it safe?",
    "decision": "READY_FOR_TRADE_CENTER_REAL_SURFACE_WIRING_WITH_SAFETY_LOCKS_HELD",
    "plain_language": (
        "Trade Center is route-ready as Decision Garden while execution, "
        "broker submission, real capital movement, and Live Auto stay locked."
    ),
}

TRADE_CENTER_COMPONENT_HINTS = {
    "hero": "DecisionGardenHeroCard",
    "soulaana": "DecisionGardenSoulaanaCard",
    "waiting_decisions": "DecisionGardenWaitingDecisionsList",
    "decision_queue": "DecisionGardenWaitingDecisionsList",
    "decision_basket": "DecisionGardenWaitingDecisionsList",
    "candidates": "DecisionGardenWaitingDecisionsList",
    "candidate_queue": "DecisionGardenWaitingDecisionsList",
    "approval_basket": "DecisionGardenWaitingDecisionsList",
    "risk": "DecisionGardenRiskGateCard",
    "risk_gate": "DecisionGardenRiskGateCard",
    "risk_first": "DecisionGardenRiskGateCard",
    "readiness": "DecisionGardenReadinessChecklist",
    "readiness_checklist": "DecisionGardenReadinessChecklist",
    "checklist": "DecisionGardenReadinessChecklist",
    "broker_checklist": "DecisionGardenBrokerChecklistPreview",
    "manual_broker_checklist": "DecisionGardenBrokerChecklistPreview",
    "owner_next_move": "DecisionGardenOwnerNextMoveCard",
    "next_action": "DecisionGardenOwnerNextMoveCard",
    "next_move": "DecisionGardenOwnerNextMoveCard",
    "drawers": "DecisionGardenDetailDrawerGroup",
    "details": "DecisionGardenDetailDrawerGroup",
    "detail_drawers": "DecisionGardenDetailDrawerGroup",
    "decision_detail_drawers": "DecisionGardenDetailDrawerGroup",
    "receipt_context": "DecisionGardenDetailDrawerGroup",
    "manual_live_context": "DecisionGardenDetailDrawerGroup",
    "owner_drawer": "DecisionGardenOwnerDrawer",
}

TRADE_CENTER_DATA_PATHS = {
    "hero": ["dominant_summary", "decision_summary", "critical_indicators"],
    "soulaana": ["soulaana"],
    "waiting_decisions": ["waiting_decisions", "decision_queue", "candidates"],
    "decision_queue": ["waiting_decisions", "decision_queue", "candidates"],
    "decision_basket": ["waiting_decisions", "decision_queue", "candidates"],
    "candidates": ["waiting_decisions", "decision_queue", "candidates"],
    "candidate_queue": ["waiting_decisions", "decision_queue", "candidates"],
    "approval_basket": ["waiting_decisions", "decision_queue", "candidates"],
    "risk": ["risk_gate", "risk_summary", "risk_reasons", "warnings"],
    "risk_gate": ["risk_gate", "risk_summary", "risk_reasons", "warnings"],
    "risk_first": ["risk_gate", "risk_summary", "risk_reasons", "warnings"],
    "readiness": ["readiness_checklist", "preflight", "missing_items"],
    "readiness_checklist": ["readiness_checklist", "preflight", "missing_items"],
    "checklist": ["readiness_checklist", "preflight", "missing_items"],
    "broker_checklist": ["broker_checklist", "manual_live_context", "not_submission"],
    "manual_broker_checklist": ["broker_checklist", "manual_live_context", "not_submission"],
    "owner_next_move": ["next_action", "owner_next_move", "recommendation"],
    "next_action": ["next_action", "owner_next_move", "recommendation"],
    "next_move": ["next_action", "owner_next_move", "recommendation"],
    "drawers": ["drawers", "detail_drawers", "details_hidden_by_default"],
    "details": ["drawers", "detail_drawers", "details_hidden_by_default"],
    "detail_drawers": ["drawers", "detail_drawers", "details_hidden_by_default"],
    "decision_detail_drawers": ["drawers", "detail_drawers", "details_hidden_by_default"],
    "receipt_context": ["receipts", "receipt_context", "evidence"],
    "manual_live_context": ["manual_live_context", "broker_checklist", "not_submission"],
    "owner_drawer": ["owner_controls", "owner_drawer_default_state"],
}

TRADE_CENTER_REQUIRED_FIRST_GLANCE_COMPONENTS = [
    "DecisionGardenHeroCard",
    "DecisionGardenSoulaanaCard",
    "DecisionGardenWaitingDecisionsList",
    "DecisionGardenRiskGateCard",
    "DecisionGardenReadinessChecklist",
    "DecisionGardenOwnerNextMoveCard",
]

TRADE_CENTER_REQUIRED_COLLAPSED_COMPONENTS = [
    "DecisionGardenDetailDrawerGroup",
    "DecisionGardenOwnerDrawer",
]

TRADE_CENTER_COLLAPSED_KEYS = [
    key
    for key in TRADE_CENTER_SURFACE_ORDER
    if (
        "drawer" in key
        or "detail" in key
        or "context" in key
        or key in {"drawers", "details", "receipt_context", "manual_live_context"}
    )
]

TRADE_CENTER_FIRST_GLANCE_KEYS = [
    key
    for key in TRADE_CENTER_SURFACE_ORDER
    if key not in TRADE_CENTER_COLLAPSED_KEYS
]

TRADE_CENTER_REAL_SURFACE_STATUS = {
    "contract_ready": True,
    "registry_ready": True,
    "real_surface_adapter_ready": True,
    "manual_broker_checklist_preview_ready": True,
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

TRADE_CENTER_ACTION_LOCKS = {
    "candidate_review_allowed": True,
    "owner_decision_review_allowed": True,
    "manual_broker_checklist_preview_allowed": True,
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
    heading = TRADE_CENTER_SECTION_HEADINGS.get(section_key, {})

    return {
        "label": heading.get("label", section_key.replace("_", " ").title()),
        "plain_label": heading.get("plain_label", section_key.replace("_", " ").title()),
        "explainer": heading.get("explainer", ""),
    }


def _component_hint_for(section_key):
    return TRADE_CENTER_COMPONENT_HINTS.get(
        section_key,
        "DecisionGarden" + section_key.replace("_", " ").title().replace(" ", "") + "Section",
    )


def _data_paths_for(section_key):
    return list(TRADE_CENTER_DATA_PATHS.get(section_key, [section_key]))


def empty_trade_center_real_surface_payload():
    empty_builder = getattr(_trade_center, "empty_trade_center_surface", None)

    if callable(empty_builder):
        try:
            payload = deepcopy(empty_builder())
        except TypeError:
            payload = {}
    else:
        payload = {}

    if not isinstance(payload, dict):
        payload = {}

    payload.setdefault("room", "trade_center")
    payload.setdefault("display_title", "Decision Garden")
    payload.setdefault("question_answered", "What decision is waiting and is it safe?")
    payload.setdefault("section_headings", deepcopy(TRADE_CENTER_SECTION_HEADINGS))
    payload.setdefault("surface_order", list(TRADE_CENTER_SURFACE_ORDER))
    payload.setdefault("details_hidden_by_default", True)
    payload.setdefault("owner_drawer_default_state", "collapsed")
    payload.setdefault("dominant_summary", "No owner decision is waiting right now.")
    payload.setdefault("waiting_decisions", [])
    payload.setdefault("readiness_checklist", [])
    payload.setdefault(
        "risk_gate",
        {
            "status": "locked",
            "plain_language": "Risk gate is locked until a real candidate exists.",
        },
    )
    payload.setdefault("next_action", "Stay in observation mode.")
    payload.setdefault("soulaana", {})

    return payload


def normalize_trade_center_surface_payload(surface_payload=None):
    if surface_payload is None:
        surface = empty_trade_center_real_surface_payload()
    else:
        surface = deepcopy(surface_payload)

    if not isinstance(surface, dict):
        surface = {}

    surface.setdefault("room", "trade_center")
    surface.setdefault("display_title", "Decision Garden")
    surface.setdefault("question_answered", "What decision is waiting and is it safe?")
    surface.setdefault("section_headings", deepcopy(TRADE_CENTER_SECTION_HEADINGS))
    surface.setdefault("surface_order", list(TRADE_CENTER_SURFACE_ORDER))
    surface.setdefault("details_hidden_by_default", True)
    surface.setdefault("owner_drawer_default_state", "collapsed")
    surface.setdefault("action_locks", deepcopy(TRADE_CENTER_ACTION_LOCKS))

    return surface


def build_trade_center_section_component(section_key, surface_payload=None):
    surface = normalize_trade_center_surface_payload(surface_payload)
    key = str(section_key or "").strip()

    if key not in TRADE_CENTER_SURFACE_ORDER:
        raise KeyError("Unknown Trade Center section: " + str(section_key))

    heading = _heading_for(key)
    default_state = "collapsed" if key in TRADE_CENTER_COLLAPSED_KEYS else "visible"

    return {
        "section_key": key,
        "component_hint": _component_hint_for(key),
        "heading": heading["label"],
        "plain_heading": heading["plain_label"],
        "explainer": heading["explainer"],
        "data_paths": _data_paths_for(key),
        "first_glance": key in TRADE_CENTER_FIRST_GLANCE_KEYS,
        "default_state": default_state,
        "source_room": surface["room"],
        "source_display_title": surface["display_title"],
        "action_locks": deepcopy(TRADE_CENTER_ACTION_LOCKS),
    }


def build_trade_center_component_tree(surface_payload=None):
    surface = normalize_trade_center_surface_payload(surface_payload)

    return [
        build_trade_center_section_component(section_key, surface)
        for section_key in TRADE_CENTER_SURFACE_ORDER
    ]


def build_trade_center_loading_state():
    return {
        "state": "loading",
        "display_title": "Decision Garden",
        "message": "Gathering waiting decisions safely...",
        "show_soulaana_placeholder": True,
        "show_skeleton_cards": list(TRADE_CENTER_REQUIRED_FIRST_GLANCE_COMPONENTS),
        "dangerous_actions_available": False,
        "broker_submission_enabled": False,
        "real_capital_movement_enabled": False,
        "direct_execution_enabled": False,
        "automated_execution_enabled": False,
        "live_auto_locked": True,
    }


def build_trade_center_empty_state():
    return {
        "state": "empty",
        "display_title": "Decision Garden",
        "message": "No trade decision is waiting right now.",
        "soulaana_hint": "Stay in observation mode until a candidate is ready for review.",
        "next_action": "Return to Dashboard or Market Weather.",
        "details_hidden_by_default": True,
        "owner_drawer_default_state": "collapsed",
        "dangerous_actions_available": False,
        "broker_submission_enabled": False,
        "real_capital_movement_enabled": False,
        "direct_execution_enabled": False,
        "automated_execution_enabled": False,
        "live_auto_locked": True,
    }


def build_trade_center_error_state(error_message="Decision Garden data could not be loaded."):
    return {
        "state": "error",
        "display_title": "Decision Garden",
        "message": str(error_message or "Decision Garden data could not be loaded."),
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


def build_trade_center_first_glance_components():
    dynamic = [
        _component_hint_for(key)
        for key in TRADE_CENTER_FIRST_GLANCE_KEYS
    ]

    return _unique(dynamic + TRADE_CENTER_REQUIRED_FIRST_GLANCE_COMPONENTS)


def build_trade_center_collapsed_components():
    dynamic = [
        _component_hint_for(key)
        for key in TRADE_CENTER_COLLAPSED_KEYS
    ]

    return _unique(dynamic + TRADE_CENTER_REQUIRED_COLLAPSED_COMPONENTS)


def build_trade_center_real_surface(surface_payload=None):
    surface = normalize_trade_center_surface_payload(surface_payload)
    registry_entry = build_surface_registry_entry("trade_center")
    adapter_contract = build_real_surface_adapter_contract()

    return {
        "package": TRADE_CENTER_REAL_SURFACE_IDENTITY["package"],
        "room": "trade_center",
        "display_title": TRADE_CENTER_REAL_SURFACE_IDENTITY["display_title"],
        "primary_question": TRADE_CENTER_REAL_SURFACE_IDENTITY["primary_question"],
        "decision": TRADE_CENTER_REAL_SURFACE_IDENTITY["decision"],
        "route_hint": registry_entry["route_hint"],
        "component_hint": registry_entry["component_hint"],
        "data_adapter_hint": registry_entry["data_adapter_hint"],
        "source_contract": deepcopy(surface),
        "registry_entry": deepcopy(registry_entry),
        "component_tree": build_trade_center_component_tree(surface),
        "first_glance_components": build_trade_center_first_glance_components(),
        "collapsed_components": build_trade_center_collapsed_components(),
        "loading_state": build_trade_center_loading_state(),
        "empty_state": build_trade_center_empty_state(),
        "error_state": build_trade_center_error_state(),
        "theme": deepcopy(OB_REAL_SURFACE_THEME),
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "action_locks": deepcopy(TRADE_CENTER_ACTION_LOCKS),
        "trade_center_lock_state": deepcopy(TRADE_CENTER_LOCK_STATE),
        "surface_status": deepcopy(TRADE_CENTER_REAL_SURFACE_STATUS),
        "safety_summary": deepcopy(adapter_contract["safety_summary"]),
        "soulaana": surface.get("soulaana", {}),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "next_build": "OB Review Center real surface wiring / GP006",
    }


def build_trade_center_real_surface_acceptance_contract():
    real_surface = build_trade_center_real_surface()

    return {
        "package": TRADE_CENTER_REAL_SURFACE_IDENTITY["package"],
        "room": "trade_center",
        "display_title": TRADE_CENTER_REAL_SURFACE_IDENTITY["display_title"],
        "primary_question": TRADE_CENTER_REAL_SURFACE_IDENTITY["primary_question"],
        "decision": TRADE_CENTER_REAL_SURFACE_IDENTITY["decision"],
        "route_hint": real_surface["route_hint"],
        "component_hint": real_surface["component_hint"],
        "must_show_at_first_glance": list(TRADE_CENTER_REQUIRED_FIRST_GLANCE_COMPONENTS),
        "must_hide_by_default": list(TRADE_CENTER_REQUIRED_COLLAPSED_COMPONENTS),
        "must_include_states": ["loading", "empty", "error"],
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "action_locks": deepcopy(TRADE_CENTER_ACTION_LOCKS),
        "trade_center_lock_state": deepcopy(TRADE_CENTER_LOCK_STATE),
        "safety_summary": deepcopy(real_surface["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
    }


def build_trade_center_real_surface_takeover_handoff():
    contract = build_trade_center_real_surface_acceptance_contract()

    return {
        "package": contract["package"],
        "display_title": contract["display_title"],
        "takeover_summary": (
            "GP005 wired Trade Center as a real-app surface adapter. "
            "Decision Garden is route-ready while broker submission, "
            "real capital movement, direct execution, automated execution, "
            "and Live Auto remain locked."
        ),
        "route_hint": contract["route_hint"],
        "component_tree": build_trade_center_component_tree(),
        "loading_state": build_trade_center_loading_state(),
        "empty_state": build_trade_center_empty_state(),
        "error_state": build_trade_center_error_state(),
        "action_locks": contract["action_locks"],
        "trade_center_lock_state": contract["trade_center_lock_state"],
        "safety_summary": contract["safety_summary"],
        "must_not_claim": contract["must_not_claim"],
        "next_builder_notes": [
            "Use DecisionGardenHeroCard for the first card.",
            "Keep Soulaana near the top.",
            "Show waiting decisions without making them executable.",
            "Show risk before readiness.",
            "Show readiness checklist as preview only.",
            "Keep detail drawers collapsed by default.",
            "Keep Owner Drawer collapsed by default.",
            "Keep broker submission locked.",
            "Keep real capital movement locked.",
            "Keep direct execution disabled.",
            "Keep automated execution disabled.",
            "Keep Live Auto locked.",
            "Do not claim STAGING_READY.",
            "Next build is GP006 Review Center real surface wiring.",
        ],
    }
