from ob_owner_experience import (
    LOCK_STATE,
    REVIEW_CENTER_DETAIL_DRAWERS,
    REVIEW_CENTER_SECTION_HEADINGS,
    REVIEW_CENTER_SURFACE_ORDER,
    build_receipt_summary,
    build_review_center_surface,
    build_review_drawers,
    empty_review_center_surface,
    rank_review_items,
    review_center_acceptance_contract,
    review_center_takeover_handoff,
)


def test_review_center_keeps_cute_informative_headings():
    contract = review_center_acceptance_contract()

    assert contract["room"] == "review_center"
    assert contract["display_title"] == "Reflection Library"
    assert contract["primary_question"] == "What did we learn and what needs review?"
    assert "plain-language section headings" in contract["must_show_at_first_glance"]
    assert contract["section_headings"]["hero"]["label"] == "📚 Reflection Library"
    assert contract["section_headings"]["soulaana"]["label"] == "🧭 Soulaana Reflects"
    assert contract["section_headings"]["receipts"]["label"] == "🧾 Receipt Check"
    assert contract["section_headings"]["lessons"]["label"] == "🧠 Lesson Shelf"
    assert contract["section_headings"]["patterns"]["label"] == "🪞 Pattern Mirror"


def test_review_center_surface_is_learning_not_execution():
    surface = build_review_center_surface(
        review_items=[
            {
                "review_id": "review-001",
                "title": "AAPL continuation review",
                "symbol": "aapl",
                "priority": "critical",
                "outcome": "mixed",
                "receipt_status": "verified",
                "what_happened": "Candidate moved but confirmation was late.",
                "lesson": "Wait for cleaner confirmation.",
                "recommended_review": "Read the lesson shelf.",
            }
        ],
        outcome_summary="AAPL moved, but confirmation quality was mixed.",
        overall_learning="Confirmation timing matters more than excitement.",
        receipt_status="verified",
        lessons=["Wait for cleaner confirmation."],
        patterns=["Chasing leadership too early."],
        warnings=["Do not repeat late confirmation."],
        evidence=["verified receipt"],
    )

    assert surface["room"] == "review_center"
    assert surface["display_title"] == "Reflection Library"
    assert surface["surface_order"] == REVIEW_CENTER_SURFACE_ORDER
    assert surface["section_headings"] == REVIEW_CENTER_SECTION_HEADINGS
    assert surface["question_answered"] == "What did we learn and what needs review?"
    assert surface["dominant_summary"] == "One review is waiting: AAPL continuation review."
    assert surface["outcome_summary"] == "AAPL moved, but confirmation quality was mixed."
    assert surface["overall_learning"] == "Confirmation timing matters more than excitement."
    assert surface["receipt_summary"]["verified"] is True
    assert surface["review_queue"][0]["symbol"] == "AAPL"
    assert surface["principal_recommendation"] == "Read the lesson shelf."
    assert surface["details_hidden_by_default"] is True
    assert surface["owner_drawer_default_state"] == "collapsed"
    assert surface["safety_locks"]["broker_submission_enabled"] is False


def test_review_center_limits_first_screen_detail():
    surface = build_review_center_surface(
        review_items=[
            {"title": "A", "priority": "critical"},
            {"title": "B", "priority": "high"},
            {"title": "C", "priority": "medium"},
            {"title": "D", "priority": "low"},
            {"title": "E", "priority": "info"},
        ],
        receipt_status="pending",
        lessons=[
            "lesson one",
            "lesson two",
            "lesson three",
            "lesson four",
            "hidden lesson",
        ],
        patterns=[
            "pattern one",
            "pattern two",
            "pattern three",
            "pattern four",
            "hidden pattern",
        ],
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

    assert len(surface["review_queue"]) == 3
    assert surface["hidden_review_count"] == 2
    assert len(surface["lessons"]) == 4
    assert len(surface["patterns"]) == 4
    assert len(surface["warnings"]) == 3
    assert len(surface["evidence"]) == 5


def test_review_center_soulaana_explains_and_hides_detail():
    surface = build_review_center_surface(
        review_items=[
            {
                "title": "Loss review",
                "priority": "critical",
                "outcome": "loss",
                "receipt_status": "verified",
                "lesson": "Cut faster when the thesis breaks.",
            }
        ],
        overall_learning="Cut faster when the thesis breaks.",
        receipt_status="verified",
    )

    assert surface["soulaana"]["soulaana_visible"] is True
    assert surface["soulaana"]["what_you_are_looking_at"] == (
        "One review is waiting: Loss review."
    )
    assert surface["soulaana"]["focus_on"] == "Cut faster when the thesis breaks."
    assert "mistake_context" in surface["soulaana"]["safe_to_ignore_for_now"]
    assert surface["next_action"] == (
        "Read the lesson and mistake drawer before changing behavior."
    )


def test_review_drawers_are_named_and_explained():
    drawers = build_review_drawers()

    assert [drawer["drawer_id"] for drawer in drawers] == REVIEW_CENTER_DETAIL_DRAWERS
    assert all(drawer["label"] for drawer in drawers)
    assert all(drawer["explainer"] for drawer in drawers)
    assert all(drawer["default_state"] == "collapsed" for drawer in drawers)


def test_empty_review_center_has_safe_observation_state():
    surface = empty_review_center_surface()

    assert surface["dominant_summary"] == "No owner reviews are waiting right now."
    assert surface["principal_recommendation"] == (
        "Stay in observation mode until a review packet is ready."
    )
    assert surface["review_queue"] == []
    assert surface["hidden_review_count"] == 0
    assert surface["receipt_summary"]["receipt_status"] == "not_required"


def test_reviews_rank_by_priority():
    ranked = rank_review_items(
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


def test_receipt_summary_flags_attention_states():
    verified = build_receipt_summary("verified")
    missing = build_receipt_summary("missing")

    assert verified["verified"] is True
    assert verified["needs_attention"] is False
    assert missing["verified"] is False
    assert missing["needs_attention"] is True


def test_takeover_handoff_contains_builder_notes_and_safety_locks():
    handoff = review_center_takeover_handoff()

    assert handoff["room"] == "review_center"
    assert handoff["display_title"] == "Reflection Library"
    assert handoff["primary_question"] == "What did we learn and what needs review?"
    assert handoff["safety_locks"]["broker_submission_enabled"] is False
    assert LOCK_STATE["real_capital_movement_enabled"] is False
    assert len(handoff["next_builder_notes"]) >= 9
    assert "Make this a learning surface, not an execution surface." in handoff["next_builder_notes"]
    assert "Show lessons before raw evidence." in handoff["next_builder_notes"]
