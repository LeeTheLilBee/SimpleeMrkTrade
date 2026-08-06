from ob_owner_experience import (
    DECISION_STATE_LABELS,
    SYMBOL_PAGE_DETAIL_DRAWERS,
    SYMBOL_PAGE_SECTION_HEADINGS,
    SYMBOL_PAGE_SURFACE_ORDER,
    build_symbol_drawers,
    build_symbol_page_surface,
    empty_symbol_page_surface,
    rank_asset_indicators,
    symbol_page_acceptance_contract,
    symbol_page_takeover_handoff,
)


def test_symbol_page_keeps_cute_informative_headings():
    contract = symbol_page_acceptance_contract()

    assert contract["room"] == "symbol_page"
    assert contract["display_title"] == "Asset Storybook"
    assert contract["primary_question"] == "What do I need to understand about this asset?"
    assert "plain-language section headings" in contract["must_show_at_first_glance"]
    assert contract["section_headings"]["hero"]["label"] == "🔎 Asset Storybook"
    assert contract["section_headings"]["soulaana"]["label"] == "🧭 Soulaana Explains"
    assert contract["section_headings"]["thesis"]["label"] == "📖 The Asset Story"
    assert contract["section_headings"]["risk"]["label"] == "🛡️ Risk Before Shine"
    assert contract["section_headings"]["decision"]["label"] == "👑 Decision Posture"


def test_symbol_page_surface_tells_asset_story_first():
    surface = build_symbol_page_surface(
        symbol="aapl",
        asset_name="Apple Inc.",
        asset_type="stock",
        thesis="Apple is being watched for leadership continuation.",
        risk_level="medium",
        decision_state="review",
        indicators=[
            {
                "title": "Trend improving",
                "importance": "high",
                "plain_language": "Price action is improving.",
            },
            {
                "title": "Volume rising",
                "importance": "medium",
            },
        ],
        warnings=["Do not chase without confirmation."],
        evidence=["watchlist receipt"],
        related_notes=["large-cap technology leadership"],
    )

    assert surface["room"] == "symbol_page"
    assert surface["symbol"] == "AAPL"
    assert surface["asset_name"] == "Apple Inc."
    assert surface["display_title"] == "Asset Storybook"
    assert surface["surface_order"] == SYMBOL_PAGE_SURFACE_ORDER
    assert surface["section_headings"] == SYMBOL_PAGE_SECTION_HEADINGS
    assert surface["question_answered"] == "What do I need to understand about this asset?"
    assert surface["asset_thesis"] == "Apple is being watched for leadership continuation."
    assert surface["current_risk_level"] == "medium"
    assert surface["decision_state"] == "review"
    assert surface["decision_label"] == DECISION_STATE_LABELS["review"]
    assert surface["principal_recommendation"] == "Review the thesis and risk before deciding."
    assert surface["details_hidden_by_default"] is True
    assert surface["owner_drawer_default_state"] == "collapsed"


def test_symbol_page_limits_first_screen_detail():
    surface = build_symbol_page_surface(
        symbol="NVDA",
        asset_name="NVIDIA",
        asset_type="stock",
        thesis="AI leadership watch.",
        risk_level="high",
        decision_state="review",
        indicators=[
            {"title": "A", "importance": "critical"},
            {"title": "B", "importance": "high"},
            {"title": "C", "importance": "medium"},
            {"title": "D", "importance": "low"},
            {"title": "E", "importance": "info"},
        ],
        warnings=[
            "valuation risk",
            "volatility risk",
            "news risk",
            "hidden risk",
        ],
        evidence=[
            "receipt one",
            "receipt two",
            "receipt three",
            "receipt four",
            "receipt five",
            "hidden receipt",
        ],
    )

    assert len(surface["visible_indicators"]) == 4
    assert surface["hidden_indicator_count"] == 1
    assert len(surface["warnings"]) == 3
    assert len(surface["evidence"]) == 5
    assert surface["principal_recommendation"] == "Review risk first: valuation risk."


def test_symbol_page_soulaana_explains_and_hides_deep_detail():
    surface = build_symbol_page_surface(
        symbol="MSFT",
        asset_name="Microsoft",
        asset_type="stock",
        thesis="Quality leadership watch.",
        risk_level="low",
        decision_state="wait",
        indicators=[
            {
                "title": "Trend steady",
                "importance": "medium",
            }
        ],
    )

    assert surface["soulaana"]["soulaana_visible"] is True
    assert surface["soulaana"]["what_you_are_looking_at"] == (
        "MSFT is a stock page for Microsoft."
    )
    assert surface["soulaana"]["focus_on"] == "Quality leadership watch."
    assert "technical_context" in surface["soulaana"]["safe_to_ignore_for_now"]
    assert surface["next_action"] == "Wait for confirmation before acting."


def test_symbol_drawers_are_named_and_explained():
    drawers = build_symbol_drawers()

    assert [drawer["drawer_id"] for drawer in drawers] == SYMBOL_PAGE_DETAIL_DRAWERS
    assert all(drawer["label"] for drawer in drawers)
    assert all(drawer["explainer"] for drawer in drawers)
    assert all(drawer["default_state"] == "collapsed" for drawer in drawers)


def test_empty_symbol_page_has_safe_observation_state():
    surface = empty_symbol_page_surface("tsla")

    assert surface["symbol"] == "TSLA"
    assert surface["asset_thesis"] == "No thesis has been written for this asset yet."
    assert surface["current_risk_level"] == "unknown"
    assert surface["decision_state"] == "observe"
    assert surface["principal_recommendation"] == (
        "Stay in observation mode until the asset read becomes clearer."
    )


def test_asset_indicators_rank_by_importance():
    ranked = rank_asset_indicators(
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


def test_takeover_handoff_contains_builder_notes():
    handoff = symbol_page_takeover_handoff()

    assert handoff["room"] == "symbol_page"
    assert handoff["display_title"] == "Asset Storybook"
    assert handoff["primary_question"] == "What do I need to understand about this asset?"
    assert len(handoff["next_builder_notes"]) >= 8
    assert "Put the thesis before chart noise." in handoff["next_builder_notes"]
    assert "Use drawers for heavy asset detail." in handoff["next_builder_notes"]
