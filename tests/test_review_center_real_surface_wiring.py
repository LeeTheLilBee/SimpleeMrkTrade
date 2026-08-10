from ob_owner_experience.review_center_real_surface import (
    REVIEW_CENTER_ACTION_LOCKS,
    REVIEW_CENTER_COLLAPSED_KEYS,
    REVIEW_CENTER_FIRST_GLANCE_KEYS,
    REVIEW_CENTER_REAL_SURFACE_IDENTITY,
    REVIEW_CENTER_REAL_SURFACE_STATUS,
    REVIEW_CENTER_SECTION_HEADINGS,
    REVIEW_CENTER_SURFACE_ORDER,
    build_review_center_component_tree,
    build_review_center_empty_state,
    build_review_center_error_state,
    build_review_center_loading_state,
    build_review_center_real_surface,
    build_review_center_real_surface_acceptance_contract,
    build_review_center_real_surface_takeover_handoff,
    build_review_center_section_component,
)
from ob_owner_experience.ui_surface_registry import PROTECTED_ROUTE_POLICY


def test_review_center_real_surface_identity_is_gp006():
    assert REVIEW_CENTER_REAL_SURFACE_IDENTITY["package"] == "ob_review_center_real_surface_wiring_gp006"
    assert REVIEW_CENTER_REAL_SURFACE_IDENTITY["room"] == "review_center"
    assert REVIEW_CENTER_REAL_SURFACE_IDENTITY["display_title"] == "Review Center"
    assert REVIEW_CENTER_REAL_SURFACE_IDENTITY["primary_question"] == (
        "What happened, what did we learn, and what should improve?"
    )
    assert REVIEW_CENTER_REAL_SURFACE_IDENTITY["decision"] == (
        "READY_FOR_REVIEW_CENTER_REAL_SURFACE_WIRING_WITH_SAFETY_LOCKS_HELD"
    )


def test_review_center_component_tree_preserves_gp006_order_and_headings():
    tree = build_review_center_component_tree()
    keys = [component["section_key"] for component in tree]
    headings = {component["section_key"]: component["heading"] for component in tree}

    assert keys == list(REVIEW_CENTER_SURFACE_ORDER)

    for key in REVIEW_CENTER_SURFACE_ORDER:
        assert key in headings
        assert headings[key] == REVIEW_CENTER_SECTION_HEADINGS[key]["label"]

    assert "hero" in headings
    assert "soulaana" in headings


def test_review_center_section_component_fails_closed_for_unknown_section():
    try:
        build_review_center_section_component("unknown")
    except KeyError as exc:
        assert "Unknown Review Center section" in str(exc)
    else:
        raise AssertionError("Unknown Review Center section should fail closed.")


def test_review_center_real_surface_uses_registry_and_protected_policy():
    surface = build_review_center_real_surface()
    registry = surface["registry_entry"]

    assert surface["package"] == "ob_review_center_real_surface_wiring_gp006"
    assert surface["room"] == "review_center"
    assert surface["display_title"] == "Review Center"
    assert surface["route_hint"] == registry["route_hint"]
    assert surface["component_hint"] == registry["component_hint"]
    assert surface["data_adapter_hint"] == registry["data_adapter_hint"]
    assert surface["protected_route_policy"] == PROTECTED_ROUTE_POLICY
    assert surface["protected_route_policy"]["anonymous_access_allowed"] is False
    assert surface["protected_route_policy"]["owner_session_required"] is True


def test_review_center_first_glance_and_collapsed_components_are_dynamic():
    surface = build_review_center_real_surface()

    assert REVIEW_CENTER_FIRST_GLANCE_KEYS == [
        key
        for key in REVIEW_CENTER_SURFACE_ORDER
        if key not in REVIEW_CENTER_COLLAPSED_KEYS
    ]

    assert "ReviewCenterHeroCard" in surface["first_glance_components"]
    assert "ReviewCenterSoulaanaCard" in surface["first_glance_components"]
    assert "ReviewCenterRecentReviewsList" in surface["first_glance_components"]
    assert "ReviewCenterDecisionReplayCard" in surface["first_glance_components"]
    assert "ReviewCenterLessonPatternCard" in surface["first_glance_components"]
    assert "ReviewCenterCorrectionQueueCard" in surface["first_glance_components"]
    assert "ReviewCenterDetailDrawerGroup" in surface["collapsed_components"]
    assert "ReviewCenterOwnerDrawer" in surface["collapsed_components"]

    collapsed_states = {
        component["section_key"]: component["default_state"]
        for component in surface["component_tree"]
    }

    assert "owner_drawer" in collapsed_states
    assert collapsed_states["owner_drawer"] == "collapsed"


def test_review_center_states_are_safe_and_owner_readable():
    loading = build_review_center_loading_state()
    empty = build_review_center_empty_state()
    error = build_review_center_error_state("bad review feed")

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
    assert empty["display_title"] == "Review Center"
    assert empty["details_hidden_by_default"] is True
    assert empty["owner_drawer_default_state"] == "collapsed"
    assert empty["dangerous_actions_available"] is False

    assert error["state"] == "error"
    assert error["message"] == "bad review feed"
    assert error["show_dashboard_link"] is True
    assert error["show_owner_console_link"] is True


def test_review_center_action_locks_hold():
    surface = build_review_center_real_surface()

    assert surface["action_locks"] == REVIEW_CENTER_ACTION_LOCKS
    assert surface["action_locks"]["review_read_allowed"] is True
    assert surface["action_locks"]["lesson_capture_allowed"] is True
    assert surface["action_locks"]["correction_note_allowed"] is True
    assert surface["action_locks"]["broker_submission_enabled"] is False
    assert surface["action_locks"]["real_capital_movement_enabled"] is False
    assert surface["action_locks"]["direct_execution_enabled"] is False
    assert surface["action_locks"]["automated_execution_enabled"] is False
    assert surface["action_locks"]["live_auto_locked"] is True


def test_review_center_real_surface_safety_locks_hold():
    surface = build_review_center_real_surface()

    assert surface["surface_status"] == REVIEW_CENTER_REAL_SURFACE_STATUS
    assert surface["surface_status"]["real_surface_adapter_ready"] is True
    assert surface["surface_status"]["receipt_review_ready"] is True
    assert surface["surface_status"]["lesson_capture_ready"] is True
    assert surface["surface_status"]["correction_queue_ready"] is True
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


def test_review_center_real_surface_acceptance_contract():
    contract = build_review_center_real_surface_acceptance_contract()
    surface = build_review_center_real_surface()

    assert contract["package"] == "ob_review_center_real_surface_wiring_gp006"
    assert contract["display_title"] == "Review Center"
    assert contract["route_hint"] == surface["route_hint"]
    assert "ReviewCenterHeroCard" in contract["must_show_at_first_glance"]
    assert "ReviewCenterSoulaanaCard" in contract["must_show_at_first_glance"]
    assert "ReviewCenterDetailDrawerGroup" in contract["must_hide_by_default"]
    assert "ReviewCenterOwnerDrawer" in contract["must_hide_by_default"]
    assert contract["must_include_states"] == ["loading", "empty", "error"]
    assert contract["action_locks"]["broker_submission_enabled"] is False
    assert contract["action_locks"]["real_capital_movement_enabled"] is False
    assert contract["action_locks"]["direct_execution_enabled"] is False
    assert contract["action_locks"]["automated_execution_enabled"] is False
    assert contract["action_locks"]["live_auto_locked"] is True
    assert contract["safety_summary"]["broker_submission_enabled"] is False


def test_review_center_real_surface_takeover_handoff():
    handoff = build_review_center_real_surface_takeover_handoff()
    surface = build_review_center_real_surface()

    assert handoff["display_title"] == "Review Center"
    assert handoff["route_hint"] == surface["route_hint"]
    assert handoff["component_tree"]
    assert handoff["loading_state"]["state"] == "loading"
    assert handoff["empty_state"]["state"] == "empty"
    assert handoff["error_state"]["state"] == "error"
    assert "Show recent reviews without making them executable." in handoff["next_builder_notes"]
    assert "Keep broker submission locked." in handoff["next_builder_notes"]
    assert "Keep real capital movement locked." in handoff["next_builder_notes"]
    assert "Keep Live Auto locked." in handoff["next_builder_notes"]
    assert "Do not claim STAGING_READY." in handoff["next_builder_notes"]
