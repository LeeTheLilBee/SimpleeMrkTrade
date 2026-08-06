from ob_owner_experience import (
    DASHBOARD_DETAIL_DRAWERS,
    DASHBOARD_SECTION_HEADINGS,
    DASHBOARD_SURFACE_ORDER,
    build_dashboard_surface,
    dashboard_acceptance_contract,
    dashboard_takeover_handoff,
    empty_dashboard_surface,
    rank_attention_items,
)


def test_dashboard_keeps_cute_informative_headings():
    contract = dashboard_acceptance_contract()

    assert contract["room"] == "dashboard"
    assert contract["display_title"] == "Today’s Command Nest"
    assert contract["primary_question"] == "What needs my attention today?"
    assert "plain-language section headings" in contract["must_show_at_first_glance"]
    assert contract["section_headings"]["hero"]["label"] == "🌙 Today’s Command Nest"
    assert contract["section_headings"]["soulaana"]["label"] == "🧭 Soulaana Says"
    assert contract["section_headings"]["attention"]["label"] == "🔥 Needs Your Eyes"
    assert contract["section_headings"]["next_action"]["label"] == "👑 Owner Next Move"


def test_dashboard_surface_has_takeover_structure():
    surface = build_dashboard_surface(
        attention_items=[
            {
                "title": "Owner decision required",
                "severity": "critical",
                "why_it_matters": "This blocks today's next step.",
                "recommended_action": "Open the decision now.",
            }
        ],
        market_condition="mixed",
        risk_level="medium",
        account_note="No account issue surfaced.",
    )

    assert surface["display_title"] == "Today’s Command Nest"
    assert surface["surface_order"] == DASHBOARD_SURFACE_ORDER
    assert surface["section_headings"] == DASHBOARD_SECTION_HEADINGS
    assert surface["question_answered"] == "What needs my attention today?"
    assert surface["dominant_summary"] == (
        "One item needs attention: Owner decision required."
    )
    assert surface["principal_recommendation"] == "Open the decision now."
    assert surface["next_action"] == "Open the decision now."
    assert surface["details_hidden_by_default"] is True
    assert surface["owner_drawer_default_state"] == "collapsed"


def test_dashboard_prioritizes_highest_attention_item():
    surface = build_dashboard_surface(
        attention_items=[
            {
                "title": "Low watchlist note",
                "severity": "low",
                "why_it_matters": "Not urgent.",
                "recommended_action": "Read later.",
            },
            {
                "title": "Owner decision required",
                "severity": "critical",
                "why_it_matters": "This blocks today's next step.",
                "recommended_action": "Open the decision now.",
            },
            {
                "title": "Medium risk note",
                "severity": "medium",
                "why_it_matters": "May matter later.",
                "recommended_action": "Monitor.",
            },
        ],
        market_condition="mixed",
        risk_level="medium",
        account_note="No account issue surfaced.",
    )

    assert surface["attention_queue"][0]["title"] == "Owner decision required"
    assert surface["principal_recommendation"] == "Open the decision now."
    assert surface["critical_indicators"][0] == "Market: mixed"
    assert surface["critical_indicators"][1] == "Risk: medium"


def test_dashboard_keeps_default_surface_small():
    surface = build_dashboard_surface(
        attention_items=[
            {"title": "A", "severity": "critical"},
            {"title": "B", "severity": "high"},
            {"title": "C", "severity": "medium"},
            {"title": "D", "severity": "low"},
            {"title": "E", "severity": "info"},
        ],
        market_condition="constructive",
        risk_level="low",
        account_note="Normal",
        warnings=[
            "warning one",
            "warning two",
            "warning three",
            "warning four",
        ],
    )

    assert len(surface["attention_queue"]) == 3
    assert surface["hidden_attention_count"] == 2
    assert len(surface["critical_indicators"]) <= 4
    assert len(surface["warnings"]) == 3
    assert surface["hidden_warning_count"] == 1


def test_dashboard_soulaana_explains_and_hides_deep_detail():
    surface = build_dashboard_surface(
        attention_items=[
            {
                "title": "Review market risk",
                "severity": "high",
                "recommended_action": "Open risk drawer.",
            }
        ],
        market_condition="cautious",
        risk_level="medium",
    )

    assert surface["soulaana"]["soulaana_visible"] is True
    assert surface["soulaana"]["what_you_are_looking_at"]
    assert surface["soulaana"]["why_it_matters"]
    assert surface["soulaana"]["focus_on"] == "Open risk drawer."
    assert "risk_context" in surface["soulaana"]["safe_to_ignore_for_now"]


def test_dashboard_drawers_are_named_and_explained():
    surface = build_dashboard_surface(
        attention_items=[],
        market_condition="quiet",
        risk_level="low",
    )

    drawer_ids = [drawer["drawer_id"] for drawer in surface["drawers"]]

    assert drawer_ids == DASHBOARD_DETAIL_DRAWERS
    assert all(drawer["label"] for drawer in surface["drawers"])
    assert all(drawer["explainer"] for drawer in surface["drawers"])
    assert all(drawer["default_state"] == "collapsed" for drawer in surface["drawers"])


def test_empty_dashboard_has_calm_observation_state():
    surface = empty_dashboard_surface()

    assert surface["dominant_summary"] == (
        "Nothing urgent needs owner attention right now."
    )
    assert surface["principal_recommendation"] == (
        "Stay in observation mode and wait for a clearer priority."
    )
    assert surface["attention_queue"] == []
    assert surface["hidden_attention_count"] == 0


def test_attention_ranking_is_stable_and_plain():
    ranked = rank_attention_items(
        [
            {"title": "Info item", "severity": "info"},
            {"title": "Critical item", "severity": "critical"},
            {"title": "High item", "severity": "high"},
        ]
    )

    assert [item["title"] for item in ranked] == [
        "Critical item",
        "High item",
        "Info item",
    ]


def test_takeover_handoff_contains_builder_notes():
    handoff = dashboard_takeover_handoff()

    assert handoff["room"] == "dashboard"
    assert handoff["display_title"] == "Today’s Command Nest"
    assert handoff["primary_question"] == "What needs my attention today?"
    assert len(handoff["next_builder_notes"]) >= 6
    assert "Keep Soulaana visible near the top of the page." in handoff["next_builder_notes"]
