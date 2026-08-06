from ob_owner_experience.market_map import (
    MARKET_MAP_SECTION_HEADINGS,
    MARKET_MAP_SURFACE_ORDER,
)
from ob_owner_experience.market_map_real_surface import (
    MARKET_MAP_COLLAPSED_KEYS,
    MARKET_MAP_FIRST_GLANCE_KEYS,
    MARKET_MAP_REAL_SURFACE_IDENTITY,
    MARKET_MAP_REAL_SURFACE_STATUS,
    build_market_deep_dive_room_tabs,
    build_market_map_component_tree,
    build_market_map_empty_state,
    build_market_map_error_state,
    build_market_map_loading_state,
    build_market_map_real_surface,
    build_market_map_real_surface_acceptance_contract,
    build_market_map_real_surface_takeover_handoff,
    build_market_map_section_component,
)
from ob_owner_experience.ui_surface_registry import PROTECTED_ROUTE_POLICY


def test_market_map_real_surface_identity_is_gp003():
    assert MARKET_MAP_REAL_SURFACE_IDENTITY["package"] == (
        "ob_market_map_real_surface_wiring_gp003"
    )
    assert MARKET_MAP_REAL_SURFACE_IDENTITY["room"] == "market_map"
    assert MARKET_MAP_REAL_SURFACE_IDENTITY["display_title"] == "Market Weather"
    assert MARKET_MAP_REAL_SURFACE_IDENTITY["primary_question"] == (
        "What is happening in the market?"
    )
    assert MARKET_MAP_REAL_SURFACE_IDENTITY["decision"] == (
        "READY_FOR_MARKET_MAP_REAL_SURFACE_WIRING_WITH_SAFETY_LOCKS_HELD"
    )


def test_market_map_component_tree_preserves_contract_order_and_headings():
    tree = build_market_map_component_tree()

    keys = [component["section_key"] for component in tree]
    headings = {
        component["section_key"]: component["heading"]
        for component in tree
    }

    assert keys == list(MARKET_MAP_SURFACE_ORDER)

    for key in MARKET_MAP_SURFACE_ORDER:
        assert headings[key] == MARKET_MAP_SECTION_HEADINGS[key]["label"]

    assert headings["hero"] == "🌦️ Market Weather"
    assert headings["soulaana"] == "🧭 Soulaana Reads the Room"


def test_market_map_section_component_fails_closed_for_unknown_section():
    try:
        build_market_map_section_component("unknown")
    except KeyError as exc:
        assert "Unknown Market Map section" in str(exc)
    else:
        raise AssertionError("Unknown Market Map section should fail closed.")


def test_market_map_real_surface_uses_registry_and_protected_policy():
    surface = build_market_map_real_surface()

    assert surface["package"] == "ob_market_map_real_surface_wiring_gp003"
    assert surface["room"] == "market_map"
    assert surface["display_title"] == "Market Weather"
    assert surface["route_hint"] == "/ob/market-map"
    assert surface["component_hint"] == "MarketWeatherSurface"
    assert surface["data_adapter_hint"] == "build_market_map_surface"
    assert surface["protected_route_policy"] == PROTECTED_ROUTE_POLICY
    assert surface["protected_route_policy"]["anonymous_access_allowed"] is False
    assert surface["protected_route_policy"]["owner_session_required"] is True


def test_market_map_first_glance_and_collapsed_components_are_dynamic():
    surface = build_market_map_real_surface()

    assert MARKET_MAP_FIRST_GLANCE_KEYS == [
        key
        for key in MARKET_MAP_SURFACE_ORDER
        if key not in MARKET_MAP_COLLAPSED_KEYS
    ]

    assert "MarketWeatherHeroCard" in surface["first_glance_components"]
    assert "MarketWeatherSoulaanaCard" in surface["first_glance_components"]
    assert "MarketWeatherRiskFirstCard" in surface["first_glance_components"]
    assert "MarketWeatherBiggestMovementCard" in surface["first_glance_components"]
    assert "MarketWeatherOpportunityGarden" in surface["first_glance_components"]

    assert "MarketWeatherDeepDiveRoomTabs" in surface["collapsed_components"]
    assert "MarketWeatherOwnerDrawer" in surface["collapsed_components"]

    collapsed_states = {
        component["section_key"]: component["default_state"]
        for component in surface["component_tree"]
    }

    assert any(
        value == "collapsed"
        for key, value in collapsed_states.items()
        if "deep" in key or "drawer" in key
    )


def test_market_deep_dive_tabs_are_collapsed_and_owner_opened():
    tabs = build_market_deep_dive_room_tabs()

    assert len(tabs) >= 1

    for tab in tabs:
        assert tab["tab_index"] >= 1
        assert tab["room_id"]
        assert tab["display_title"]
        assert tab["component_hint"].startswith("MarketWeather")
        assert tab["default_state"] == "collapsed"
        assert tab["owner_opens_when_needed"] is True


def test_market_map_states_are_safe_and_owner_readable():
    loading = build_market_map_loading_state()
    empty = build_market_map_empty_state()
    error = build_market_map_error_state("bad market feed")

    assert loading["state"] == "loading"
    assert loading["show_soulaana_placeholder"] is True
    assert loading["dangerous_actions_available"] is False

    assert empty["state"] == "empty"
    assert empty["display_title"] == "Market Weather"
    assert empty["deep_dive_rooms_default_state"] == "collapsed"
    assert empty["dangerous_actions_available"] is False

    assert error["state"] == "error"
    assert error["message"] == "bad market feed"
    assert error["show_dashboard_link"] is True
    assert error["show_owner_console_link"] is True
    assert error["broker_submission_enabled"] is False
    assert error["real_capital_movement_enabled"] is False
    assert error["live_auto_locked"] is True


def test_market_map_real_surface_safety_locks_hold():
    surface = build_market_map_real_surface()

    assert surface["surface_status"] == MARKET_MAP_REAL_SURFACE_STATUS
    assert surface["surface_status"]["real_surface_adapter_ready"] is True
    assert surface["surface_status"]["deep_dive_rooms_tab_ready"] is True
    assert surface["surface_status"]["real_html_rendered"] is False
    assert surface["surface_status"]["staging_ready"] is False
    assert surface["safety_summary"]["broker_submission_enabled"] is False
    assert surface["safety_summary"]["real_capital_movement_enabled"] is False
    assert surface["safety_summary"]["live_auto_locked"] is True
    assert "STAGING_READY" in surface["must_not_claim"]


def test_market_map_real_surface_acceptance_contract():
    contract = build_market_map_real_surface_acceptance_contract()

    assert contract["package"] == "ob_market_map_real_surface_wiring_gp003"
    assert contract["display_title"] == "Market Weather"
    assert contract["route_hint"] == "/ob/market-map"
    assert "MarketWeatherHeroCard" in contract["must_show_at_first_glance"]
    assert "MarketWeatherSoulaanaCard" in contract["must_show_at_first_glance"]
    assert "MarketWeatherDeepDiveRoomTabs" in contract["must_hide_by_default"]
    assert "MarketWeatherOwnerDrawer" in contract["must_hide_by_default"]
    assert contract["must_include_states"] == ["loading", "empty", "error"]
    assert contract["safety_summary"]["broker_submission_enabled"] is False
    assert contract["deep_dive_room_tabs"]


def test_market_map_real_surface_takeover_handoff():
    handoff = build_market_map_real_surface_takeover_handoff()

    assert handoff["display_title"] == "Market Weather"
    assert handoff["route_hint"] == "/ob/market-map"
    assert handoff["component_tree"]
    assert handoff["deep_dive_room_tabs"]
    assert handoff["loading_state"]["state"] == "loading"
    assert handoff["empty_state"]["state"] == "empty"
    assert handoff["error_state"]["state"] == "error"
    assert "Show risk before opportunity." in handoff["next_builder_notes"]
    assert "Do not claim STAGING_READY." in handoff["next_builder_notes"]
