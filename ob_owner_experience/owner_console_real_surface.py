from copy import deepcopy

from .ui_surface_registry import (
    MUST_NOT_CLAIM,
    OB_REAL_SURFACE_THEME,
    PROTECTED_ROUTE_POLICY,
    build_real_surface_adapter_contract,
    build_surface_registry_entry,
)

OWNER_CONSOLE_REAL_SURFACE_IDENTITY = {
    "package": "ob_owner_console_real_surface_wiring_gp007",
    "room": "owner_console",
    "display_title": "Owner Console",
    "primary_question": "What is unlocked, what is blocked, and what needs owner attention?",
    "decision": "READY_FOR_OWNER_CONSOLE_REAL_SURFACE_WIRING_WITH_SAFETY_LOCKS_HELD",
}

OWNER_CONSOLE_SURFACE_ORDER = [
    "hero",
    "soulaana",
    "owner_status",
    "access_controls",
    "mode_locks",
    "safety_locks",
    "tower_handoffs",
    "audit_receipts",
    "drawers",
    "owner_drawer",
]

_LABELS = {
    "hero": ("🛡️ Owner Console", "Owner Console", "Protected owner command room."),
    "soulaana": ("🧭 Soulaana Owner Brief", "Soulaana Owner Brief", "Plain-language owner interpretation."),
    "owner_status": ("👑 Owner Status", "Owner Status", "Owner session, clearance, and mode status."),
    "access_controls": ("🚪 Access Controls", "Access Controls", "Read-only access review."),
    "mode_locks": ("🔒 Mode Locks", "Mode Locks", "Survey, Paper, Manual Live, Hybrid, and Auto locks."),
    "safety_locks": ("🚨 Safety Locks", "Safety Locks", "Broker, money, execution, and Live Auto locks."),
    "tower_handoffs": ("🗼 Tower Handoffs", "Tower Handoffs", "Tower-controlled handoff status."),
    "audit_receipts": ("🧾 Audit Receipts", "Audit Receipts", "Owner-visible safety and access receipts."),
    "drawers": ("🗂️ Console Detail Drawers", "Console Detail Drawers", "Details stay collapsed by default."),
    "owner_drawer": ("🔐 Owner Drawer", "Owner Drawer", "Owner controls stay collapsed and safety-gated."),
}

OWNER_CONSOLE_SECTION_HEADINGS = {
    key: {"label": value[0], "plain_label": value[1], "explainer": value[2]}
    for key, value in _LABELS.items()
}

OWNER_CONSOLE_COMPONENT_HINTS = {
    "hero": "OwnerConsoleHeroCard",
    "soulaana": "OwnerConsoleSoulaanaCard",
    "owner_status": "OwnerConsoleStatusCard",
    "access_controls": "OwnerConsoleAccessControlsCard",
    "mode_locks": "OwnerConsoleModeLocksCard",
    "safety_locks": "OwnerConsoleSafetyLocksCard",
    "tower_handoffs": "OwnerConsoleTowerHandoffCard",
    "audit_receipts": "OwnerConsoleAuditReceiptTimeline",
    "drawers": "OwnerConsoleDetailDrawerGroup",
    "owner_drawer": "OwnerConsoleOwnerDrawer",
}

OWNER_CONSOLE_DATA_PATHS = {
    "hero": ["owner_summary", "system_summary"],
    "soulaana": ["soulaana"],
    "owner_status": ["owner_status", "owner_session", "clearance"],
    "access_controls": ["access_controls", "permissions", "tester_access"],
    "mode_locks": ["mode_locks", "mode_gate", "mode_controls"],
    "safety_locks": ["safety_locks", "kill_switches", "broker_locks"],
    "tower_handoffs": ["tower_handoffs", "tower_return", "tower_session"],
    "audit_receipts": ["audit_receipts", "receipt_timeline", "logs"],
    "drawers": ["drawers", "detail_drawers", "details_hidden_by_default"],
    "owner_drawer": ["owner_controls", "owner_drawer_default_state"],
}

OWNER_CONSOLE_REQUIRED_FIRST_GLANCE_COMPONENTS = [
    "OwnerConsoleHeroCard",
    "OwnerConsoleSoulaanaCard",
    "OwnerConsoleStatusCard",
    "OwnerConsoleAccessControlsCard",
    "OwnerConsoleModeLocksCard",
    "OwnerConsoleSafetyLocksCard",
    "OwnerConsoleTowerHandoffCard",
    "OwnerConsoleAuditReceiptTimeline",
]

OWNER_CONSOLE_REQUIRED_COLLAPSED_COMPONENTS = [
    "OwnerConsoleDetailDrawerGroup",
    "OwnerConsoleOwnerDrawer",
]

OWNER_CONSOLE_COLLAPSED_KEYS = ["drawers", "owner_drawer"]
OWNER_CONSOLE_FIRST_GLANCE_KEYS = [
    key for key in OWNER_CONSOLE_SURFACE_ORDER if key not in OWNER_CONSOLE_COLLAPSED_KEYS
]

OWNER_CONSOLE_ACTION_LOCKS = {
    "owner_status_read_allowed": True,
    "access_review_allowed": True,
    "mode_lock_review_allowed": True,
    "safety_lock_review_allowed": True,
    "tower_handoff_review_allowed": True,
    "audit_receipt_review_allowed": True,
    "permission_mutation_enabled": False,
    "secret_reveal_enabled": False,
    "production_deploy_enabled": False,
    "broker_submission_enabled": False,
    "real_capital_movement_enabled": False,
    "direct_execution_enabled": False,
    "automated_execution_enabled": False,
    "live_auto_locked": True,
}

OWNER_CONSOLE_REAL_SURFACE_STATUS = {
    "contract_ready": True,
    "registry_ready": True,
    "real_surface_adapter_ready": True,
    "owner_status_ready": True,
    "access_review_ready": True,
    "mode_lock_review_ready": True,
    "safety_lock_review_ready": True,
    "tower_handoff_review_ready": True,
    "audit_receipt_review_ready": True,
    "permission_mutation_enabled": False,
    "secrets_visible": False,
    "production_deploy_enabled": False,
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


def _unique(values):
    out = []
    for value in values:
        if value not in out:
            out.append(value)
    return out


def empty_owner_console_real_surface_payload():
    return {
        "room": "owner_console",
        "display_title": "Owner Console",
        "question_answered": OWNER_CONSOLE_REAL_SURFACE_IDENTITY["primary_question"],
        "section_headings": deepcopy(OWNER_CONSOLE_SECTION_HEADINGS),
        "surface_order": list(OWNER_CONSOLE_SURFACE_ORDER),
        "details_hidden_by_default": True,
        "owner_drawer_default_state": "collapsed",
        "owner_summary": "Owner Console is ready for review.",
        "owner_status": {},
        "access_controls": {},
        "mode_locks": {},
        "safety_locks": {},
        "tower_handoffs": {},
        "audit_receipts": [],
        "soulaana": {},
    }


def normalize_owner_console_surface_payload(surface_payload=None):
    surface = empty_owner_console_real_surface_payload() if surface_payload is None else deepcopy(surface_payload)
    if not isinstance(surface, dict):
        surface = empty_owner_console_real_surface_payload()

    surface.setdefault("room", "owner_console")
    surface.setdefault("display_title", "Owner Console")
    surface.setdefault("question_answered", OWNER_CONSOLE_REAL_SURFACE_IDENTITY["primary_question"])
    surface.setdefault("section_headings", deepcopy(OWNER_CONSOLE_SECTION_HEADINGS))
    surface.setdefault("surface_order", list(OWNER_CONSOLE_SURFACE_ORDER))
    surface.setdefault("details_hidden_by_default", True)
    surface.setdefault("owner_drawer_default_state", "collapsed")
    surface.setdefault("action_locks", deepcopy(OWNER_CONSOLE_ACTION_LOCKS))
    return surface


def build_owner_console_section_component(section_key, surface_payload=None):
    key = str(section_key or "").strip()
    surface = normalize_owner_console_surface_payload(surface_payload)

    if key not in OWNER_CONSOLE_SURFACE_ORDER:
        raise KeyError("Unknown Owner Console section: " + str(section_key))

    heading = OWNER_CONSOLE_SECTION_HEADINGS[key]
    state = "collapsed" if key in OWNER_CONSOLE_COLLAPSED_KEYS else "visible"

    return {
        "section_key": key,
        "component_hint": OWNER_CONSOLE_COMPONENT_HINTS[key],
        "heading": heading["label"],
        "plain_heading": heading["plain_label"],
        "explainer": heading["explainer"],
        "data_paths": list(OWNER_CONSOLE_DATA_PATHS[key]),
        "first_glance": key in OWNER_CONSOLE_FIRST_GLANCE_KEYS,
        "default_state": state,
        "source_room": surface["room"],
        "source_display_title": surface["display_title"],
        "action_locks": deepcopy(OWNER_CONSOLE_ACTION_LOCKS),
    }


def build_owner_console_component_tree(surface_payload=None):
    surface = normalize_owner_console_surface_payload(surface_payload)
    return [
        build_owner_console_section_component(section_key, surface)
        for section_key in OWNER_CONSOLE_SURFACE_ORDER
    ]


def _safe_state(name, message):
    return {
        "state": name,
        "display_title": "Owner Console",
        "message": message,
        "dangerous_actions_available": False,
        "permission_mutation_enabled": False,
        "secret_reveal_enabled": False,
        "production_deploy_enabled": False,
        "broker_submission_enabled": False,
        "real_capital_movement_enabled": False,
        "direct_execution_enabled": False,
        "automated_execution_enabled": False,
        "live_auto_locked": True,
    }


def build_owner_console_loading_state():
    state = _safe_state("loading", "Checking owner session, locks, and handoffs safely...")
    state["show_soulaana_placeholder"] = True
    state["show_skeleton_cards"] = list(OWNER_CONSOLE_REQUIRED_FIRST_GLANCE_COMPONENTS)
    return state


def build_owner_console_empty_state():
    state = _safe_state("empty", "No owner-console issue needs action right now.")
    state["soulaana_hint"] = "Owner Console is calm. Review locks before changing any mode."
    state["next_action"] = "Return to Dashboard or Tower Access Home."
    state["details_hidden_by_default"] = True
    state["owner_drawer_default_state"] = "collapsed"
    return state


def build_owner_console_error_state(error_message="Owner Console data could not be loaded."):
    state = _safe_state("error", str(error_message or "Owner Console data could not be loaded."))
    state["safe_fallback"] = "Return to Dashboard or Tower Access Home."
    state["show_dashboard_link"] = True
    state["show_tower_link"] = True
    return state


def build_owner_console_first_glance_components():
    return _unique(
        [OWNER_CONSOLE_COMPONENT_HINTS[key] for key in OWNER_CONSOLE_FIRST_GLANCE_KEYS]
        + OWNER_CONSOLE_REQUIRED_FIRST_GLANCE_COMPONENTS
    )


def build_owner_console_collapsed_components():
    return _unique(
        [OWNER_CONSOLE_COMPONENT_HINTS[key] for key in OWNER_CONSOLE_COLLAPSED_KEYS]
        + OWNER_CONSOLE_REQUIRED_COLLAPSED_COMPONENTS
    )


def build_owner_console_real_surface(surface_payload=None):
    surface = normalize_owner_console_surface_payload(surface_payload)
    registry = build_surface_registry_entry("owner_console")
    adapter = build_real_surface_adapter_contract()

    return {
        "package": OWNER_CONSOLE_REAL_SURFACE_IDENTITY["package"],
        "room": "owner_console",
        "display_title": OWNER_CONSOLE_REAL_SURFACE_IDENTITY["display_title"],
        "primary_question": OWNER_CONSOLE_REAL_SURFACE_IDENTITY["primary_question"],
        "decision": OWNER_CONSOLE_REAL_SURFACE_IDENTITY["decision"],
        "route_hint": registry["route_hint"],
        "component_hint": registry["component_hint"],
        "data_adapter_hint": registry["data_adapter_hint"],
        "source_contract": deepcopy(surface),
        "registry_entry": deepcopy(registry),
        "component_tree": build_owner_console_component_tree(surface),
        "first_glance_components": build_owner_console_first_glance_components(),
        "collapsed_components": build_owner_console_collapsed_components(),
        "loading_state": build_owner_console_loading_state(),
        "empty_state": build_owner_console_empty_state(),
        "error_state": build_owner_console_error_state(),
        "theme": deepcopy(OB_REAL_SURFACE_THEME),
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "action_locks": deepcopy(OWNER_CONSOLE_ACTION_LOCKS),
        "surface_status": deepcopy(OWNER_CONSOLE_REAL_SURFACE_STATUS),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "soulaana": surface.get("soulaana", {}),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "next_build": "OB six-room real surface acceptance / GP008",
    }


def build_owner_console_real_surface_acceptance_contract():
    surface = build_owner_console_real_surface()
    return {
        "package": OWNER_CONSOLE_REAL_SURFACE_IDENTITY["package"],
        "room": "owner_console",
        "display_title": OWNER_CONSOLE_REAL_SURFACE_IDENTITY["display_title"],
        "primary_question": OWNER_CONSOLE_REAL_SURFACE_IDENTITY["primary_question"],
        "decision": OWNER_CONSOLE_REAL_SURFACE_IDENTITY["decision"],
        "route_hint": surface["route_hint"],
        "component_hint": surface["component_hint"],
        "must_show_at_first_glance": list(OWNER_CONSOLE_REQUIRED_FIRST_GLANCE_COMPONENTS),
        "must_hide_by_default": list(OWNER_CONSOLE_REQUIRED_COLLAPSED_COMPONENTS),
        "must_include_states": ["loading", "empty", "error"],
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "action_locks": deepcopy(OWNER_CONSOLE_ACTION_LOCKS),
        "safety_summary": deepcopy(surface["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
    }


def build_owner_console_real_surface_takeover_handoff():
    contract = build_owner_console_real_surface_acceptance_contract()
    return {
        "package": contract["package"],
        "display_title": contract["display_title"],
        "takeover_summary": (
            "GP007 wired Owner Console as a real-app surface adapter while dangerous "
            "mutations, secret reveal, production deploy, broker submission, real capital "
            "movement, direct execution, automated execution, and Live Auto remain locked."
        ),
        "route_hint": contract["route_hint"],
        "component_tree": build_owner_console_component_tree(),
        "loading_state": build_owner_console_loading_state(),
        "empty_state": build_owner_console_empty_state(),
        "error_state": build_owner_console_error_state(),
        "action_locks": contract["action_locks"],
        "safety_summary": contract["safety_summary"],
        "must_not_claim": contract["must_not_claim"],
        "next_builder_notes": [
            "Show owner session and clearance as read-only status.",
            "Show access controls as review-only in this package.",
            "Show mode locks before any mode-related control.",
            "Show safety locks prominently.",
            "Show Tower handoffs without bypassing Tower.",
            "Show audit receipts without exposing secrets.",
            "Keep detail drawers collapsed by default.",
            "Keep Owner Drawer collapsed by default.",
            "Keep permission mutations disabled.",
            "Keep secret reveal disabled.",
            "Keep production deploy disabled.",
            "Keep broker submission locked.",
            "Keep real capital movement locked.",
            "Keep direct execution disabled.",
            "Keep automated execution disabled.",
            "Keep Live Auto locked.",
            "Do not claim STAGING_READY.",
            "Next build is GP008 six-room real surface acceptance.",
        ],
    }
