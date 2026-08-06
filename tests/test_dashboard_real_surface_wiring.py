from ob_owner_experience.dashboard import (
    DASHBOARD_SECTION_HEADINGS,
    DASHBOARD_SURFACE_ORDER,
)
from ob_owner_experience.dashboard_real_surface import (
    DASHBOARD_COLLAPSED_KEYS,
    DASHBOARD_FIRST_GLANCE_KEYS,
    DASHBOARD_REAL_SURFACE_IDENTITY,
    DASHBOARD_REAL_SURFACE_STATUS,
    build_dashboard_component_tree,
    build_dashboard_empty_state,
    build_dashboard_error_state,
    build_dashboard_loading_state,
    build_dashboard_real_surface,
    build_dashboard_real_surface_acceptance_contract,
    build_dashboard_real_surface_takeover_handoff,
    build_dashboard_section_component,
)
from ob_owner_experience.ui_surface_registry import PROTECTED_ROUTE_POLICY


def test_dashboard_real_surface_identity_is_gp002():
    assert DASHBOARD_REAL_SURFACE_IDENTITY["package"] == (
        "ob_dashboard_real_surface_wiring_gp002"
    )
    assert DASHBOARD_REAL_SURFACE_IDENTITY["room"] == "dashboard"
    assert DASHBOARD_REAL_SURFACE_IDENTITY["display_title"] == "Today’s Command Nest"
    assert DASHBOARD_REAL_SURFACE_IDENTITY["primary_question"] == (
        "What needs my attention today?"
    )
    assert DASHBOARD_REAL_SURFACE_IDENTITY["decision"] == (
        "READY_FOR_DASHBOARD_REAL_SURFACE_WIRING_WITH_SAFETY_LOCKS_HELD"
    )


def test_dashboard_component_tree_preserves_dashboard_contract_order_and_headings():
    tree = build_dashboard_component_tree()

    keys = [component["section_key"] for component in tree]
    headings = {
        component["section_key"]: component["heading"]
        for component in tree
    }

    assert keys == list(DASHBOARD_SURFACE_ORDER)

    for key in DASHBOARD_SURFACE_ORDER:
        assert headings[key] == DASHBOARD_SECTION_HEADINGS[key]["label"]

    assert headings["hero"] == "🌙 Today’s Command Nest"
    assert headings["soulaana"] == "🧭 Soulaana Says"
    assert headings["attention"] == "🔥 Needs Your Eyes"
    assert "✨" in headings["indicators"]
    assert "🗂️" in headings["drawers"]
    assert headings["owner_drawer"] == "🔐 Owner Drawer"


def test_dashboard_section_component_fails_closed_for_unknown_section():
    try:
        build_dashboard_section_component("unknown")
    except KeyError as exc:
        assert "Unknown Dashboard section" in str(exc)
    else:
        raise AssertionError("Unknown Dashboard section should fail closed.")


def test_dashboard_real_surface_uses_registry_and_protected_policy():
    surface = build_dashboard_real_surface()

    assert surface["package"] == "ob_dashboard_real_surface_wiring_gp002"
    assert surface["room"] == "dashboard"
    assert surface["display_title"] == "Today’s Command Nest"
    assert surface["route_hint"] == "/ob/dashboard"
    assert surface["component_hint"] == "DashboardTodayCommandNest"
    assert surface["data_adapter_hint"] == "build_dashboard_surface"
    assert surface["protected_route_policy"] == PROTECTED_ROUTE_POLICY
    assert surface["protected_route_policy"]["anonymous_access_allowed"] is False
    assert surface["protected_route_policy"]["owner_session_required"] is True


def test_dashboard_first_glance_and_collapsed_components_are_correct():
    surface = build_dashboard_real_surface()

    assert DASHBOARD_FIRST_GLANCE_KEYS == [
        key
        for key in DASHBOARD_SURFACE_ORDER
        if key not in DASHBOARD_COLLAPSED_KEYS
    ]

    assert "DashboardHeroCard" in surface["first_glance_components"]
    assert "DashboardSoulaanaCard" in surface["first_glance_components"]
    assert "DashboardNeedsYourEyesList" in surface["first_glance_components"]
    assert "DashboardTinySignalsStrip" in surface["first_glance_components"]
    assert "DashboardOwnerNextMoveCard" in surface["first_glance_components"]

    assert "DashboardDetailsDrawerGroup" in surface["collapsed_components"]
    assert "DashboardOwnerDrawer" in surface["collapsed_components"]

    collapsed_states = {
        component["section_key"]: component["default_state"]
        for component in surface["component_tree"]
    }

    assert collapsed_states["drawers"] == "collapsed"
    assert collapsed_states["owner_drawer"] == "collapsed"


def test_dashboard_states_are_safe_and_owner_readable():
    loading = build_dashboard_loading_state()
    empty = build_dashboard_empty_state()
    error = build_dashboard_error_state("bad dashboard feed")

    assert loading["state"] == "loading"
    assert loading["show_soulaana_placeholder"] is True
    assert loading["dangerous_actions_available"] is False

    assert empty["state"] == "empty"
    assert empty["display_title"] == "Today’s Command Nest"
    assert empty["dangerous_actions_available"] is False

    assert error["state"] == "error"
    assert error["message"] == "bad dashboard feed"
    assert error["show_owner_console_link"] is True
    assert error["broker_submission_enabled"] is False
    assert error["real_capital_movement_enabled"] is False
    assert error["live_auto_locked"] is True


def test_dashboard_real_surface_safety_locks_hold():
    surface = build_dashboard_real_surface()

    assert surface["surface_status"] == DASHBOARD_REAL_SURFACE_STATUS
    assert surface["surface_status"]["real_surface_adapter_ready"] is True
    assert surface["surface_status"]["real_html_rendered"] is False
    assert surface["surface_status"]["staging_ready"] is False
    assert surface["safety_summary"]["broker_submission_enabled"] is False
    assert surface["safety_summary"]["real_capital_movement_enabled"] is False
    assert surface["safety_summary"]["live_auto_locked"] is True
    assert "STAGING_READY" in surface["must_not_claim"]


def test_dashboard_real_surface_acceptance_contract():
    contract = build_dashboard_real_surface_acceptance_contract()

    assert contract["package"] == "ob_dashboard_real_surface_wiring_gp002"
    assert contract["display_title"] == "Today’s Command Nest"
    assert contract["route_hint"] == "/ob/dashboard"
    assert "DashboardHeroCard" in contract["must_show_at_first_glance"]
    assert "DashboardSoulaanaCard" in contract["must_show_at_first_glance"]
    assert "DashboardDetailsDrawerGroup" in contract["must_hide_by_default"]
    assert "DashboardOwnerDrawer" in contract["must_hide_by_default"]
    assert contract["must_include_states"] == ["loading", "empty", "error"]
    assert contract["safety_summary"]["broker_submission_enabled"] is False


def test_dashboard_real_surface_takeover_handoff():
    handoff = build_dashboard_real_surface_takeover_handoff()

    assert handoff["display_title"] == "Today’s Command Nest"
    assert handoff["route_hint"] == "/ob/dashboard"
    assert handoff["component_tree"]
    assert handoff["loading_state"]["state"] == "loading"
    assert handoff["empty_state"]["state"] == "empty"
    assert handoff["error_state"]["state"] == "error"
    assert "Keep Soulaana near the top." in handoff["next_builder_notes"]
    assert "Do not claim STAGING_READY." in handoff["next_builder_notes"]
