import pytest

from ob_owner_experience import (
    MARKET_MAP_DEEP_DIVE_ROOM_CONFIGS,
    MARKET_MAP_DEEP_DIVES,
    MARKET_MAP_FIRST_GLANCE_FIELDS,
    MARKET_MAP_SECTION_HEADINGS,
    MARKET_MAP_SURFACE_ORDER,
    build_all_market_deep_dive_rooms,
    build_deep_dive_cards,
    build_market_deep_dive_room,
    build_market_map_surface,
    market_map_acceptance_contract,
    market_map_takeover_handoff,
    rank_market_signals,
)


def test_market_map_keeps_cute_informative_headings():
    contract = market_map_acceptance_contract()

    assert contract["room"] == "market_map"
    assert contract["display_title"] == "Market Weather"
    assert contract["primary_question"] == "What is happening in the market?"
    assert "plain-language section headings" in contract["must_show_at_first_glance"]
    assert "risk before opportunity" in contract["must_show_at_first_glance"]
    assert contract["section_headings"]["hero"]["label"] == "🌦️ Market Weather"
    assert contract["section_headings"]["soulaana"]["label"] == "🧭 Soulaana Reads the Room"
    assert contract["section_headings"]["risk"]["label"] == "🛡️ Risk First"
    assert contract["section_headings"]["deep_dives"]["label"] == "🗺️ Deep-Dive Rooms"


def test_market_map_first_glance_surface_is_small_and_plain():
    surface = build_market_map_surface(
        overall_market_condition="cautious but constructive",
        current_risk_level="medium",
        most_important_movement="large-cap technology is leading while breadth is thin",
        strongest_opportunities=[
            "AAPL continuation watch",
            "MSFT leadership",
            "NVDA strength",
            "hidden extra opportunity",
        ],
        most_important_warnings=[
            "volatility is rising",
            "market breadth is weak",
            "rates are moving",
            "hidden extra warning",
        ],
        signals=[
            {"title": "Breadth warning", "importance": "high"},
            {"title": "Sector rotation", "importance": "medium"},
            {"title": "Volatility alert", "importance": "critical"},
            {"title": "Flow clue", "importance": "low"},
            {"title": "Hidden detail", "importance": "info"},
        ],
    )

    assert surface["room"] == "market_map"
    assert surface["display_title"] == "Market Weather"
    assert surface["surface_order"] == MARKET_MAP_SURFACE_ORDER
    assert surface["section_headings"] == MARKET_MAP_SECTION_HEADINGS
    assert surface["question_answered"] == "What is happening in the market?"
    assert surface["dominant_summary"] == "Market is cautious but constructive with medium risk."
    assert len(surface["strongest_opportunities"]) == 3
    assert len(surface["most_important_warnings"]) == 3
    assert len(surface["visible_signals"]) == 4
    assert surface["hidden_signal_count"] == 1
    assert surface["details_hidden_by_default"] is True
    assert surface["owner_drawer_default_state"] == "collapsed"


def test_market_map_soulaana_interprets_without_metric_wall():
    surface = build_market_map_surface(
        overall_market_condition="mixed",
        current_risk_level="high",
        most_important_movement="defensive sectors are leading",
        strongest_opportunities=[],
        most_important_warnings=["risk is elevated"],
    )

    assert surface["soulaana"]["soulaana_visible"] is True
    assert surface["soulaana"]["what_you_are_looking_at"] == "Market is mixed with high risk."
    assert surface["soulaana"]["focus_on"] == "defensive sectors are leading"
    assert "sector_details" in surface["soulaana"]["safe_to_ignore_for_now"]
    assert "technical_signals" in surface["deep_dive_rooms_hidden_by_default"]
    assert "Review risk first" in surface["next_action"]


def test_deep_dive_cards_are_named_and_explained():
    cards = build_deep_dive_cards()

    assert len(cards) == 10
    assert [card["room_id"] for card in cards] == MARKET_MAP_DEEP_DIVES
    assert all(card["heading"] for card in cards)
    assert all(card["title"] for card in cards)
    assert all(card["question"] for card in cards)
    assert all(card["explainer"] for card in cards)
    assert all(card["default_state"] == "hidden_until_opened" for card in cards)


def test_all_market_map_deep_dive_rooms_exist():
    rooms = build_all_market_deep_dive_rooms()

    assert list(rooms) == MARKET_MAP_DEEP_DIVES
    assert len(rooms) == 10

    for room_id, room in rooms.items():
        assert room["room"] == room_id
        assert room["parent_room"] == "market_map"
        assert room["heading"]
        assert room["title"]
        assert room["plain_title"]
        assert room["question_answered"]
        assert room["plain_language"]
        assert room["soulaana"]["soulaana_visible"] is True
        assert room["owner_drawer_default_state"] == "collapsed"


def test_specific_deep_dive_room_limits_detail():
    room = build_market_deep_dive_room(
        "sector_details",
        summary="Technology leads while utilities lag.",
        key_points=[
            "Technology is leading",
            "Utilities are lagging",
            "Financials are neutral",
            "Energy is mixed",
            "Industrials are improving",
            "Hidden extra point",
        ],
        evidence=[
            "sector heatmap",
            "relative strength table",
            "volume dashboard",
            "weekly trend view",
            "receipt log",
            "hidden extra evidence",
        ],
        next_action="Return to Market Weather after checking leadership.",
    )

    assert room["room"] == "sector_details"
    assert room["heading"] == "🌿 Sector Garden"
    assert room["title"] == "Sector Garden"
    assert len(room["key_points"]) == 5
    assert len(room["evidence"]) == 5
    assert room["next_action"] == "Return to Market Weather after checking leadership."
    assert room["details_hidden_by_default"] is False


def test_unknown_deep_dive_fails_closed():
    with pytest.raises(KeyError):
        build_market_deep_dive_room("unknown_room")


def test_market_signals_rank_by_importance():
    ranked = rank_market_signals(
        [
            {"title": "Low", "importance": "low"},
            {"title": "Critical", "importance": "critical"},
            {"title": "High", "importance": "high"},
        ]
    )

    assert [item["title"] for item in ranked] == [
        "Critical",
        "High",
        "Low",
    ]


def test_market_map_deep_dive_configs_match_locked_doctrine():
    assert set(MARKET_MAP_DEEP_DIVE_ROOM_CONFIGS) == set(MARKET_MAP_DEEP_DIVES)
    assert MARKET_MAP_DEEP_DIVE_ROOM_CONFIGS["market_breadth"]["heading"] == "🫧 Breadth Check"
    assert MARKET_MAP_DEEP_DIVE_ROOM_CONFIGS["volatility"]["heading"] == "⛈️ Storm Meter"
    assert MARKET_MAP_DEEP_DIVE_ROOM_CONFIGS["technical_signals"]["heading"] == "🏮 Signal Lanterns"


def test_takeover_handoff_contains_builder_notes():
    handoff = market_map_takeover_handoff()

    assert handoff["room"] == "market_map"
    assert handoff["display_title"] == "Market Weather"
    assert handoff["primary_question"] == "What is happening in the market?"
    assert len(handoff["next_builder_notes"]) >= 8
    assert "Show risk before opportunity." in handoff["next_builder_notes"]
    assert "Use deep-dive rooms for heavy market detail." in handoff["next_builder_notes"]
