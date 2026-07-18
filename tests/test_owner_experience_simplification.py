from ob_owner_experience import (
    DANGEROUS_ACTION_POLICY,
    MARKET_MAP_DEEP_DIVES,
    OWNER_CONTROL_POLICY,
    build_owner_experience_doctrine,
    build_room_surface,
    get_room_policy,
    market_map_first_glance_surface,
    soulaana_interpretation,
)


def test_all_six_protected_rooms_have_one_clear_question():
    doctrine = build_owner_experience_doctrine()
    assert doctrine["protected_rooms"] == [
        "dashboard",
        "market_map",
        "symbol_page",
        "trade_center",
        "review_center",
        "owner_console",
    ]
    for room in doctrine["protected_rooms"]:
        policy = get_room_policy(room)
        assert policy["purpose"]["question"]
        assert policy["initial_surface"]["dominant_summary_count"] == 1
        assert policy["initial_surface"]["principal_recommendation_count"] == 1
        assert policy["initial_surface"]["obvious_next_action_count"] == 1
        assert policy["visual_hierarchy"]["wall_of_cards_allowed"] is False


def test_soulaana_is_page_level_interpretation_layer():
    data = soulaana_interpretation(
        room="dashboard",
        summary="Two items need attention today.",
        focus="Review the highest-priority owner decision.",
        next_action="Open the decision queue.",
        ignore=["low-priority market noise"],
    )
    assert data["soulaana_visible"] is True
    assert "owner guide" in data["role"]
    assert data["what_you_are_looking_at"]
    assert data["why_it_matters"]
    assert data["focus_on"]
    assert data["next_action"]
    assert data["safe_to_ignore_for_now"] == ["low-priority market noise"]


def test_owner_controls_are_not_scattered_into_normal_pages():
    assert OWNER_CONTROL_POLICY["blanket_owner_visibility"] is True
    assert OWNER_CONTROL_POLICY["global_owner_controls_home"] == "owner_console"
    assert OWNER_CONTROL_POLICY["per_room_owner_drawer"] == "collapsed_by_default"
    assert OWNER_CONTROL_POLICY["ordinary_pages_must_not_scatter_global_settings"] is True
    assert OWNER_CONTROL_POLICY["dangerous_actions_require_step_up"] is True
    dashboard = get_room_policy("dashboard")
    assert dashboard["owner_drawer"]["default_state"] == "collapsed"
    assert dashboard["owner_drawer"]["scope"] == "room_specific_controls_only"


def test_market_map_first_glance_hides_deep_dive_complexity():
    surface = market_map_first_glance_surface(
        overall_market_condition="cautious but constructive",
        current_risk_level="medium",
        most_important_movement="large-cap technology is leading",
        strongest_opportunities=["AAPL", "MSFT", "NVDA", "hidden"],
        most_important_warnings=["volatility rising", "weak breadth", "rates moving", "hidden"],
    )
    assert surface["room"] == "market_map"
    assert surface["overall_market_condition"] == "cautious but constructive"
    assert surface["current_risk_level"] == "medium"
    assert len(surface["strongest_opportunities"]) == 3
    assert len(surface["most_important_warnings"]) == 3
    assert surface["details_hidden_by_default"] is True
    assert surface["deep_dive_tabs_hidden_by_default"] == MARKET_MAP_DEEP_DIVES
    assert "sector_details" in surface["deep_dive_tabs_hidden_by_default"]
    assert "technical_signals" in surface["deep_dive_tabs_hidden_by_default"]


def test_room_surface_limits_default_indicator_count():
    surface = build_room_surface(
        room="symbol_page",
        dominant_summary="The asset is improving but not cleared.",
        principal_recommendation="Watch confirmation before action.",
        critical_indicators=[
            "trend improving",
            "risk medium",
            "volume rising",
            "news mixed",
            "deep valuation metric hidden",
        ],
        next_action="Open the thesis drawer.",
    )
    assert surface["room"] == "symbol_page"
    assert len(surface["critical_indicators"]) == 4
    assert surface["details_hidden_by_default"] is True
    assert surface["owner_drawer_default_state"] == "collapsed"
    assert surface["soulaana"]["safe_to_ignore_for_now"] == ["deep valuation metric hidden"]


def test_dangerous_actions_remain_separately_gated():
    assert DANGEROUS_ACTION_POLICY["deployment"] == "separately_gated"
    assert DANGEROUS_ACTION_POLICY["secrets"] == "separately_gated"
    assert DANGEROUS_ACTION_POLICY["trading"] == "separately_gated"
    assert DANGEROUS_ACTION_POLICY["broker_submission"] == "separately_gated"
    assert DANGEROUS_ACTION_POLICY["money_movement"] == "separately_gated"
    assert DANGEROUS_ACTION_POLICY["destructive_controls"] == "separately_gated"
    assert DANGEROUS_ACTION_POLICY["default_state"] == "disabled_until_authorized"
