from ob_owner_experience import (
    LOCK_STATE,
    TRADE_CENTER_DETAIL_DRAWERS,
    TRADE_CENTER_SECTION_HEADINGS,
    TRADE_CENTER_SURFACE_ORDER,
    build_lock_summary,
    build_trade_center_surface,
    build_trade_drawers,
    empty_trade_center_surface,
    rank_decision_items,
    trade_center_acceptance_contract,
    trade_center_takeover_handoff,
)


def test_trade_center_keeps_cute_informative_headings():
    contract = trade_center_acceptance_contract()

    assert contract["room"] == "trade_center"
    assert contract["display_title"] == "Decision Garden"
    assert contract["primary_question"] == "What decisions or actions are waiting?"
    assert "plain-language section headings" in contract["must_show_at_first_glance"]
    assert contract["section_headings"]["hero"]["label"] == "🌸 Decision Garden"
    assert contract["section_headings"]["soulaana"]["label"] == "🧭 Soulaana Guides"
    assert contract["section_headings"]["queue"]["label"] == "📬 Waiting Decisions"
    assert contract["section_headings"]["risk"]["label"] == "🛡️ Risk Gate"
    assert contract["section_headings"]["checklist"]["label"] == "✅ Readiness Checklist"


def test_trade_center_surface_is_review_not_execution():
    surface = build_trade_center_surface(
        decision_items=[
            {
                "decision_id": "decision-001",
                "title": "Review AAPL continuation candidate",
                "symbol": "aapl",
                "priority": "critical",
                "decision_state": "ready_for_owner_review",
                "action_kind": "owner_decision",
                "why_it_matters": "This is the highest-priority candidate.",
                "recommended_review": "Open owner review packet.",
                "requires_step_up": True,
            }
        ],
        risk_level="medium",
        checklist_items=[
            "Confirm thesis",
            "Review risk",
            "Confirm no broker submission",
        ],
        warnings=["Do not submit through OB."],
        evidence=["candidate receipt"],
    )

    assert surface["room"] == "trade_center"
    assert surface["display_title"] == "Decision Garden"
    assert surface["surface_order"] == TRADE_CENTER_SURFACE_ORDER
    assert surface["section_headings"] == TRADE_CENTER_SECTION_HEADINGS
    assert surface["question_answered"] == "What decisions or actions are waiting?"
    assert surface["dominant_summary"] == (
        "One decision is waiting: Review AAPL continuation candidate."
    )
    assert surface["decision_queue"][0]["symbol"] == "AAPL"
    assert surface["principal_recommendation"] == "Open owner review packet."
    assert surface["details_hidden_by_default"] is True
    assert surface["owner_drawer_default_state"] == "collapsed"
    assert surface["safety_locks"]["broker_submission_enabled"] is False


def test_trade_center_limits_first_screen_detail():
    surface = build_trade_center_surface(
        decision_items=[
            {"title": "A", "priority": "critical"},
            {"title": "B", "priority": "high"},
            {"title": "C", "priority": "medium"},
            {"title": "D", "priority": "low"},
            {"title": "E", "priority": "info"},
        ],
        risk_level="high",
        warnings=[
            "warning one",
            "warning two",
            "warning three",
            "hidden warning",
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

    assert len(surface["decision_queue"]) == 3
    assert surface["hidden_decision_count"] == 2
    assert len(surface["critical_indicators"]) == 4
    assert len(surface["warnings"]) == 3
    assert len(surface["evidence"]) == 5


def test_trade_center_soulaana_explains_and_hides_detail():
    surface = build_trade_center_surface(
        decision_items=[
            {
                "title": "Blocked candidate",
                "priority": "critical",
                "decision_state": "blocked_by_risk",
                "recommended_review": "Review the risk drawer.",
            }
        ],
        risk_level="high",
    )

    assert surface["soulaana"]["soulaana_visible"] is True
    assert surface["soulaana"]["what_you_are_looking_at"] == (
        "One decision is waiting: Blocked candidate."
    )
    assert surface["soulaana"]["focus_on"] == (
        "Open the risk drawer before any owner decision."
    )
    assert "risk_context" in surface["soulaana"]["safe_to_ignore_for_now"]
    assert surface["next_action"] == "Open the risk drawer before any owner decision."


def test_trade_center_drawers_are_named_and_explained():
    drawers = build_trade_drawers()

    assert [drawer["drawer_id"] for drawer in drawers] == TRADE_CENTER_DETAIL_DRAWERS
    assert all(drawer["label"] for drawer in drawers)
    assert all(drawer["explainer"] for drawer in drawers)
    assert all(drawer["default_state"] == "collapsed" for drawer in drawers)


def test_empty_trade_center_has_safe_observation_state():
    surface = empty_trade_center_surface()

    assert surface["dominant_summary"] == "No owner trade decisions are waiting right now."
    assert surface["principal_recommendation"] == (
        "Stay in observation mode until a decision packet is ready."
    )
    assert surface["decision_queue"] == []
    assert surface["hidden_decision_count"] == 0
    assert surface["risk_level"] == "low"


def test_decisions_rank_by_priority():
    ranked = rank_decision_items(
        [
            {"title": "Low", "priority": "low"},
            {"title": "Critical", "priority": "critical"},
            {"title": "High", "priority": "high"},
        ]
    )

    assert [item["title"] for item in ranked] == [
        "Critical",
        "High",
        "Low",
    ]


def test_lock_summary_keeps_dangerous_actions_closed():
    summary = build_lock_summary()

    assert summary["production_manual_live_authorized"] is False
    assert summary["broker_submission_enabled"] is False
    assert summary["real_capital_movement_enabled"] is False
    assert summary["direct_vault_upload_enabled"] is False
    assert summary["live_auto_locked"] is True
    assert LOCK_STATE["broker_submission_enabled"] is False


def test_takeover_handoff_contains_builder_notes_and_safety_locks():
    handoff = trade_center_takeover_handoff()

    assert handoff["room"] == "trade_center"
    assert handoff["display_title"] == "Decision Garden"
    assert handoff["primary_question"] == "What decisions or actions are waiting?"
    assert handoff["safety_locks"]["broker_submission_enabled"] is False
    assert len(handoff["next_builder_notes"]) >= 8
    assert "Make this a review surface, not a broker terminal." in handoff["next_builder_notes"]
    assert "Keep broker submission and money movement locked." in handoff["next_builder_notes"]
