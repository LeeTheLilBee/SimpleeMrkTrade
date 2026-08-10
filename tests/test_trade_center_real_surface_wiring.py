from ob_owner_experience.trade_center_real_surface import (
    TRADE_CENTER_ACTION_LOCKS,
    TRADE_CENTER_COLLAPSED_KEYS,
    TRADE_CENTER_FIRST_GLANCE_KEYS,
    TRADE_CENTER_REAL_SURFACE_IDENTITY,
    TRADE_CENTER_REAL_SURFACE_STATUS,
    TRADE_CENTER_SECTION_HEADINGS,
    TRADE_CENTER_SURFACE_ORDER,
    build_trade_center_component_tree,
    build_trade_center_empty_state,
    build_trade_center_error_state,
    build_trade_center_loading_state,
    build_trade_center_real_surface,
    build_trade_center_real_surface_acceptance_contract,
    build_trade_center_real_surface_takeover_handoff,
    build_trade_center_section_component,
)
from ob_owner_experience.ui_surface_registry import PROTECTED_ROUTE_POLICY


def test_trade_center_real_surface_identity_is_gp005():
    assert TRADE_CENTER_REAL_SURFACE_IDENTITY["package"] == "ob_trade_center_real_surface_wiring_gp005"
    assert TRADE_CENTER_REAL_SURFACE_IDENTITY["room"] == "trade_center"
    assert TRADE_CENTER_REAL_SURFACE_IDENTITY["display_title"] == "Decision Garden"
    assert TRADE_CENTER_REAL_SURFACE_IDENTITY["primary_question"] == "What decision is waiting and is it safe?"
    assert TRADE_CENTER_REAL_SURFACE_IDENTITY["decision"] == "READY_FOR_TRADE_CENTER_REAL_SURFACE_WIRING_WITH_SAFETY_LOCKS_HELD"


def test_trade_center_component_tree_preserves_contract_order_and_headings():
    tree = build_trade_center_component_tree()
    keys = [component["section_key"] for component in tree]
    headings = {component["section_key"]: component["heading"] for component in tree}

    assert keys == list(TRADE_CENTER_SURFACE_ORDER)

    for key in TRADE_CENTER_SURFACE_ORDER:
        assert key in headings
        assert headings[key] == TRADE_CENTER_SECTION_HEADINGS[key]["label"]

    assert headings["hero"] == "🌸 Decision Garden"
    assert headings["soulaana"] == "🧭 Soulaana Guides"


def test_trade_center_section_component_fails_closed_for_unknown_section():
    try:
        build_trade_center_section_component("unknown")
    except KeyError as exc:
        assert "Unknown Trade Center section" in str(exc)
    else:
        raise AssertionError("Unknown Trade Center section should fail closed.")


def test_trade_center_real_surface_uses_registry_and_protected_policy():
    surface = build_trade_center_real_surface()

    assert surface["package"] == "ob_trade_center_real_surface_wiring_gp005"
    assert surface["room"] == "trade_center"
    assert surface["display_title"] == "Decision Garden"
    assert surface["route_hint"] == "/ob/trade-center"
    assert surface["component_hint"] == "DecisionGardenSurface"
    assert surface["data_adapter_hint"] == "build_trade_center_surface"
    assert surface["protected_route_policy"] == PROTECTED_ROUTE_POLICY
    assert surface["protected_route_policy"]["anonymous_access_allowed"] is False
    assert surface["protected_route_policy"]["owner_session_required"] is True


def test_trade_center_first_glance_and_collapsed_components_are_dynamic():
    surface = build_trade_center_real_surface()

    assert TRADE_CENTER_FIRST_GLANCE_KEYS == [
        key
        for key in TRADE_CENTER_SURFACE_ORDER
        if key not in TRADE_CENTER_COLLAPSED_KEYS
    ]

    assert "DecisionGardenHeroCard" in surface["first_glance_components"]
    assert "DecisionGardenSoulaanaCard" in surface["first_glance_components"]
    assert "DecisionGardenWaitingDecisionsList" in surface["first_glance_components"]
    assert "DecisionGardenRiskGateCard" in surface["first_glance_components"]
    assert "DecisionGardenReadinessChecklist" in surface["first_glance_components"]
    assert "DecisionGardenOwnerNextMoveCard" in surface["first_glance_components"]

    assert "DecisionGardenDetailDrawerGroup" in surface["collapsed_components"]
    assert "DecisionGardenOwnerDrawer" in surface["collapsed_components"]

    collapsed_states = {
        component["section_key"]: component["default_state"]
        for component in surface["component_tree"]
    }

    assert "owner_drawer" in collapsed_states
    assert collapsed_states["owner_drawer"] == "collapsed"


def test_trade_center_states_are_safe_and_owner_readable():
    loading = build_trade_center_loading_state()
    empty = build_trade_center_empty_state()
    error = build_trade_center_error_state("bad decision feed")

    for state in [loading, empty, error]:
        assert state["broker_submission_enabled"] is False
        assert state["real_capital_movement_enabled"] is False
        assert state["direct_execution_enabled"] is False
        assert state["automated_execution_enabled"] is False
        assert state["live_auto_locked"] is True

    assert loading["state"] == "loading"
    assert loading["show_soulaana_placeholder"] is True
    assert loading["dangerous_actions_available"] is False

    assert empty["state"] == "empty"
    assert empty["display_title"] == "Decision Garden"
    assert empty["details_hidden_by_default"] is True
    assert empty["owner_drawer_default_state"] == "collapsed"
    assert empty["dangerous_actions_available"] is False

    assert error["state"] == "error"
    assert error["message"] == "bad decision feed"
    assert error["show_dashboard_link"] is True
    assert error["show_owner_console_link"] is True


def test_trade_center_action_locks_hold():
    surface = build_trade_center_real_surface()

    assert surface["action_locks"] == TRADE_CENTER_ACTION_LOCKS
    assert surface["action_locks"]["candidate_review_allowed"] is True
    assert surface["action_locks"]["owner_decision_review_allowed"] is True
    assert surface["action_locks"]["manual_broker_checklist_preview_allowed"] is True
    assert surface["action_locks"]["broker_submission_enabled"] is False
    assert surface["action_locks"]["real_capital_movement_enabled"] is False
    assert surface["action_locks"]["direct_execution_enabled"] is False
    assert surface["action_locks"]["automated_execution_enabled"] is False
    assert surface["action_locks"]["live_auto_locked"] is True


def test_trade_center_real_surface_safety_locks_hold():
    surface = build_trade_center_real_surface()

    assert surface["surface_status"] == TRADE_CENTER_REAL_SURFACE_STATUS
    assert surface["surface_status"]["real_surface_adapter_ready"] is True
    assert surface["surface_status"]["manual_broker_checklist_preview_ready"] is True
    assert surface["surface_status"]["broker_submission_enabled"] is False
    assert surface["surface_status"]["real_capital_movement_enabled"] is False
    assert surface["surface_status"]["direct_execution_enabled"] is False
    assert surface["surface_status"]["automated_execution_enabled"] is False
    assert surface["surface_status"]["real_html_rendered"] is False
    assert surface["surface_status"]["staging_ready"] is False
    assert surface["safety_summary"]["broker_submission_enabled"] is False
    assert surface["safety_summary"]["real_capital_movement_enabled"] is False
    assert surface["safety_summary"]["live_auto_locked"] is True
    assert "STAGING_READY" in surface["must_not_claim"]


def test_trade_center_real_surface_acceptance_contract():
    contract = build_trade_center_real_surface_acceptance_contract()

    assert contract["package"] == "ob_trade_center_real_surface_wiring_gp005"
    assert contract["display_title"] == "Decision Garden"
    assert contract["route_hint"] == "/ob/trade-center"
    assert "DecisionGardenHeroCard" in contract["must_show_at_first_glance"]
    assert "DecisionGardenSoulaanaCard" in contract["must_show_at_first_glance"]
    assert "DecisionGardenDetailDrawerGroup" in contract["must_hide_by_default"]
    assert "DecisionGardenOwnerDrawer" in contract["must_hide_by_default"]
    assert contract["must_include_states"] == ["loading", "empty", "error"]
    assert contract["action_locks"]["broker_submission_enabled"] is False
    assert contract["action_locks"]["real_capital_movement_enabled"] is False
    assert contract["action_locks"]["direct_execution_enabled"] is False
    assert contract["action_locks"]["automated_execution_enabled"] is False
    assert contract["action_locks"]["live_auto_locked"] is True
    assert contract["safety_summary"]["broker_submission_enabled"] is False


def test_trade_center_real_surface_takeover_handoff():
    handoff = build_trade_center_real_surface_takeover_handoff()

    assert handoff["display_title"] == "Decision Garden"
    assert handoff["route_hint"] == "/ob/trade-center"
    assert handoff["component_tree"]
    assert handoff["loading_state"]["state"] == "loading"
    assert handoff["empty_state"]["state"] == "empty"
    assert handoff["error_state"]["state"] == "error"
    assert "Show waiting decisions without making them executable." in handoff["next_builder_notes"]
    assert "Keep broker submission locked." in handoff["next_builder_notes"]
    assert "Keep real capital movement locked." in handoff["next_builder_notes"]
    assert "Keep Live Auto locked." in handoff["next_builder_notes"]
    assert "Do not claim STAGING_READY." in handoff["next_builder_notes"]
