from ob_owner_experience.owner_console_real_surface import (
    OWNER_CONSOLE_ACTION_LOCKS,
    OWNER_CONSOLE_COLLAPSED_KEYS,
    OWNER_CONSOLE_FIRST_GLANCE_KEYS,
    OWNER_CONSOLE_REAL_SURFACE_IDENTITY,
    OWNER_CONSOLE_REAL_SURFACE_STATUS,
    OWNER_CONSOLE_SECTION_HEADINGS,
    OWNER_CONSOLE_SURFACE_ORDER,
    build_owner_console_component_tree,
    build_owner_console_empty_state,
    build_owner_console_error_state,
    build_owner_console_loading_state,
    build_owner_console_real_surface,
    build_owner_console_real_surface_acceptance_contract,
    build_owner_console_real_surface_takeover_handoff,
    build_owner_console_section_component,
)
from ob_owner_experience.ui_surface_registry import PROTECTED_ROUTE_POLICY


def test_owner_console_real_surface_identity_is_gp007():
    assert OWNER_CONSOLE_REAL_SURFACE_IDENTITY["package"] == "ob_owner_console_real_surface_wiring_gp007"
    assert OWNER_CONSOLE_REAL_SURFACE_IDENTITY["room"] == "owner_console"
    assert OWNER_CONSOLE_REAL_SURFACE_IDENTITY["display_title"] == "Owner Console"
    assert OWNER_CONSOLE_REAL_SURFACE_IDENTITY["decision"] == (
        "READY_FOR_OWNER_CONSOLE_REAL_SURFACE_WIRING_WITH_SAFETY_LOCKS_HELD"
    )


def test_owner_console_tree_order_headings_and_unknown_section():
    tree = build_owner_console_component_tree()
    keys = [component["section_key"] for component in tree]

    assert keys == list(OWNER_CONSOLE_SURFACE_ORDER)
    assert "hero" in keys
    assert "soulaana" in keys
    assert "owner_drawer" in keys

    for component in tree:
        key = component["section_key"]
        assert component["heading"] == OWNER_CONSOLE_SECTION_HEADINGS[key]["label"]

    try:
        build_owner_console_section_component("unknown")
    except KeyError as exc:
        assert "Unknown Owner Console section" in str(exc)
    else:
        raise AssertionError("Unknown section should fail closed.")


def test_owner_console_surface_uses_registry_and_protected_policy():
    surface = build_owner_console_real_surface()
    registry = surface["registry_entry"]

    assert surface["package"] == "ob_owner_console_real_surface_wiring_gp007"
    assert surface["room"] == "owner_console"
    assert surface["display_title"] == "Owner Console"
    assert surface["route_hint"] == registry["route_hint"]
    assert surface["component_hint"] == registry["component_hint"]
    assert surface["data_adapter_hint"] == registry["data_adapter_hint"]
    assert surface["protected_route_policy"] == PROTECTED_ROUTE_POLICY
    assert surface["protected_route_policy"]["anonymous_access_allowed"] is False
    assert surface["protected_route_policy"]["owner_session_required"] is True


def test_owner_console_components_are_visible_or_collapsed_correctly():
    surface = build_owner_console_real_surface()

    assert OWNER_CONSOLE_FIRST_GLANCE_KEYS == [
        key for key in OWNER_CONSOLE_SURFACE_ORDER if key not in OWNER_CONSOLE_COLLAPSED_KEYS
    ]

    for name in [
        "OwnerConsoleHeroCard",
        "OwnerConsoleSoulaanaCard",
        "OwnerConsoleStatusCard",
        "OwnerConsoleAccessControlsCard",
        "OwnerConsoleModeLocksCard",
        "OwnerConsoleSafetyLocksCard",
        "OwnerConsoleTowerHandoffCard",
        "OwnerConsoleAuditReceiptTimeline",
    ]:
        assert name in surface["first_glance_components"]

    assert "OwnerConsoleDetailDrawerGroup" in surface["collapsed_components"]
    assert "OwnerConsoleOwnerDrawer" in surface["collapsed_components"]

    states = {item["section_key"]: item["default_state"] for item in surface["component_tree"]}
    assert states["drawers"] == "collapsed"
    assert states["owner_drawer"] == "collapsed"


def test_owner_console_states_are_safe():
    states = [
        build_owner_console_loading_state(),
        build_owner_console_empty_state(),
        build_owner_console_error_state("bad owner console feed"),
    ]

    for state in states:
        assert state["permission_mutation_enabled"] is False
        assert state["secret_reveal_enabled"] is False
        assert state["production_deploy_enabled"] is False
        assert state["broker_submission_enabled"] is False
        assert state["real_capital_movement_enabled"] is False
        assert state["direct_execution_enabled"] is False
        assert state["automated_execution_enabled"] is False
        assert state["live_auto_locked"] is True

    assert states[0]["state"] == "loading"
    assert states[1]["state"] == "empty"
    assert states[2]["state"] == "error"


def test_owner_console_action_and_surface_locks_hold():
    surface = build_owner_console_real_surface()

    assert surface["action_locks"] == OWNER_CONSOLE_ACTION_LOCKS
    assert surface["surface_status"] == OWNER_CONSOLE_REAL_SURFACE_STATUS

    for key in [
        "permission_mutation_enabled",
        "secret_reveal_enabled",
        "production_deploy_enabled",
        "broker_submission_enabled",
        "real_capital_movement_enabled",
        "direct_execution_enabled",
        "automated_execution_enabled",
    ]:
        assert surface["action_locks"][key] is False

    assert surface["action_locks"]["live_auto_locked"] is True
    assert surface["surface_status"]["real_surface_adapter_ready"] is True
    assert surface["surface_status"]["owner_status_ready"] is True
    assert surface["surface_status"]["access_review_ready"] is True
    assert surface["surface_status"]["mode_lock_review_ready"] is True
    assert surface["surface_status"]["safety_lock_review_ready"] is True
    assert surface["surface_status"]["tower_handoff_review_ready"] is True
    assert surface["surface_status"]["audit_receipt_review_ready"] is True
    assert surface["surface_status"]["permission_mutation_enabled"] is False
    assert surface["surface_status"]["secrets_visible"] is False
    assert surface["surface_status"]["production_deploy_enabled"] is False
    assert surface["surface_status"]["staging_ready"] is False
    assert surface["safety_summary"]["broker_submission_enabled"] is False
    assert surface["safety_summary"]["real_capital_movement_enabled"] is False
    assert surface["safety_summary"]["live_auto_locked"] is True
    assert "STAGING_READY" in surface["must_not_claim"]


def test_owner_console_acceptance_contract_and_handoff():
    contract = build_owner_console_real_surface_acceptance_contract()
    handoff = build_owner_console_real_surface_takeover_handoff()
    surface = build_owner_console_real_surface()

    assert contract["package"] == "ob_owner_console_real_surface_wiring_gp007"
    assert contract["route_hint"] == surface["route_hint"]
    assert "OwnerConsoleHeroCard" in contract["must_show_at_first_glance"]
    assert "OwnerConsoleOwnerDrawer" in contract["must_hide_by_default"]
    assert contract["must_include_states"] == ["loading", "empty", "error"]
    assert contract["action_locks"]["permission_mutation_enabled"] is False
    assert contract["action_locks"]["secret_reveal_enabled"] is False
    assert contract["action_locks"]["production_deploy_enabled"] is False
    assert contract["action_locks"]["live_auto_locked"] is True

    assert handoff["display_title"] == "Owner Console"
    assert handoff["route_hint"] == surface["route_hint"]
    assert "Keep permission mutations disabled." in handoff["next_builder_notes"]
    assert "Keep secret reveal disabled." in handoff["next_builder_notes"]
    assert "Keep broker submission locked." in handoff["next_builder_notes"]
    assert "Keep Live Auto locked." in handoff["next_builder_notes"]
    assert "Do not claim STAGING_READY." in handoff["next_builder_notes"]
