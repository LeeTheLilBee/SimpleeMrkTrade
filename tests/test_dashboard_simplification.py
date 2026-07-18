from ob_owner_experience import (
    DASHBOARD_DETAIL_DRAWERS,
    build_dashboard_surface,
    dashboard_acceptance_contract,
    empty_dashboard_surface,
    rank_attention_items,
)


def test_dashboard_answers_one_primary_question():
    contract = dashboard_acceptance_contract()

    assert contract["room"] == "dashboard"
    assert contract["primary_question"] == "What needs my attention today?"
    assert contract["owner_drawer_default_state"] == "collapsed"
    assert "one dominant summary" in contract["must_show_at_first_glance"]
    assert "Soulaana interpretation" in contract["must_show_at_first_glance"]
    assert "wall of equally weighted cards" in contract["must_not_show"]


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

    assert surface["question_answered"] == "What needs my attention today?"
    assert surface["attention_queue"][0]["title"] == "Owner decision required"
    assert surface["principal_recommendation"] == "Open the decision now."
    assert surface["next_action"] == "Open the decision now."
    assert surface["details_hidden_by_default"] is True
    assert surface["owner_drawer_default_state"] == "collapsed"


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
    assert DASHBOARD_DETAIL_DRAWERS[0] in surface["soulaana"]["safe_to_ignore_for_now"]


def test_empty_dashboard_has_calm_observation_state():
    surface = empty_dashboard_surface()

    assert surface["dominant_summary"] == "Nothing urgent needs owner attention right now."
    assert surface["principal_recommendation"] == "Stay in observation mode and wait for a clearer priority."
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
