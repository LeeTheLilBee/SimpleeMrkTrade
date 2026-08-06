from ob_owner_experience import (
    LOCK_STATE,
    OWNER_CONSOLE_DETAIL_DRAWERS,
    OWNER_CONSOLE_SECTION_HEADINGS,
    OWNER_CONSOLE_SURFACE_ORDER,
    OWNER_GLOBAL_CONTROL_POLICY,
    build_mode_gate_summary,
    build_owner_console_drawers,
    build_owner_console_surface,
    build_safety_lock_summary,
    empty_owner_console_surface,
    owner_console_acceptance_contract,
    owner_console_takeover_handoff,
    rank_control_items,
)


def test_owner_console_keeps_cute_informative_headings():
    contract = owner_console_acceptance_contract()

    assert contract["room"] == "owner_console"
    assert contract["display_title"] == "Owner Crown Room"
    assert contract["primary_question"] == "What controls need owner attention?"
    assert "plain-language section headings" in contract["must_show_at_first_glance"]
    assert contract["section_headings"]["hero"]["label"] == "👑 Owner Crown Room"
    assert contract["section_headings"]["soulaana"]["label"] == "🧭 Soulaana Advises"
    assert contract["section_headings"]["approvals"]["label"] == "🪄 Approval Basket"
    assert contract["section_headings"]["modes"]["label"] == "🚦 Mode Gates"
    assert contract["section_headings"]["locks"]["label"] == "🔒 Safety Locks"


def test_owner_console_surface_centralizes_global_controls():
    surface = build_owner_console_surface(
        control_items=[
            {
                "control_id": "approval-001",
                "title": "Review staging owner gate",
                "priority": "critical",
                "control_state": "approval_waiting",
                "control_kind": "approval",
                "why_it_matters": "This determines whether staging can continue.",
                "recommended_review": "Open the approval basket.",
                "requires_step_up": True,
            }
        ],
        approval_items=[
            "Approve or hold staging owner gate",
            "Confirm Tower return stays separate",
        ],
        mode_state={
            "survey_enabled": True,
            "paper_enabled": True,
            "manual_live_level_1_owner_only": True,
            "hybrid_locked": True,
        },
        access_notes=["Owner session is active"],
        session_notes=["Step-up may be required for dangerous controls"],
        warnings=["Do not unlock Live Auto"],
        evidence=["owner-console receipt"],
    )

    assert surface["room"] == "owner_console"
    assert surface["display_title"] == "Owner Crown Room"
    assert surface["surface_order"] == OWNER_CONSOLE_SURFACE_ORDER
    assert surface["section_headings"] == OWNER_CONSOLE_SECTION_HEADINGS
    assert surface["question_answered"] == "What controls need owner attention?"
    assert surface["dominant_summary"] == (
        "One owner control needs attention: Review staging owner gate."
    )
    assert surface["principal_recommendation"] == (
        "Review the approval basket before any gate changes."
    )
    assert surface["global_control_policy"] == OWNER_GLOBAL_CONTROL_POLICY
    assert surface["global_control_policy"]["owner_console_is_control_center"] is True
    assert surface["global_control_policy"]["dashboard_global_controls_allowed"] is False
    assert surface["details_hidden_by_default"] is True
    assert surface["owner_drawer_default_state"] == "not_applicable_global_room"


def test_owner_console_limits_first_screen_detail():
    surface = build_owner_console_surface(
        control_items=[
            {"title": "A", "priority": "critical"},
            {"title": "B", "priority": "high"},
            {"title": "C", "priority": "medium"},
            {"title": "D", "priority": "low"},
            {"title": "E", "priority": "info"},
        ],
        approval_items=[
            "approval one",
            "approval two",
            "approval three",
            "hidden approval",
        ],
        access_notes=[
            "access one",
            "access two",
            "access three",
            "access four",
            "hidden access",
        ],
        session_notes=[
            "session one",
            "session two",
            "session three",
            "session four",
            "hidden session",
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

    assert len(surface["control_queue"]) == 3
    assert surface["hidden_control_count"] == 2
    assert len(surface["approval_basket"]) == 3
    assert len(surface["access_notes"]) == 4
    assert len(surface["session_notes"]) == 4
    assert len(surface["warnings"]) == 3
    assert len(surface["evidence"]) == 5


def test_owner_console_soulaana_explains_and_hides_detail():
    surface = build_owner_console_surface(
        control_items=[
            {
                "title": "Blocked gate",
                "priority": "critical",
                "control_state": "blocked",
                "recommended_review": "Open blocked gate detail.",
            }
        ],
        approval_items=["Blocked gate needs review"],
    )

    assert surface["soulaana"]["soulaana_visible"] is True
    assert surface["soulaana"]["what_you_are_looking_at"] == (
        "One owner control needs attention: Blocked gate."
    )
    assert surface["soulaana"]["focus_on"] == (
        "Open the blocked control drawer before changing anything."
    )
    assert "mode_gate_context" in surface["soulaana"]["safe_to_ignore_for_now"]
    assert surface["next_action"] == (
        "Open the blocked control drawer before changing anything."
    )


def test_owner_console_drawers_are_named_and_explained():
    drawers = build_owner_console_drawers()

    assert [drawer["drawer_id"] for drawer in drawers] == OWNER_CONSOLE_DETAIL_DRAWERS
    assert all(drawer["label"] for drawer in drawers)
    assert all(drawer["explainer"] for drawer in drawers)
    assert all(drawer["default_state"] == "collapsed" for drawer in drawers)


def test_empty_owner_console_has_safe_observation_state():
    surface = empty_owner_console_surface()

    assert surface["dominant_summary"] == (
        "No global owner controls need attention right now."
    )
    assert surface["principal_recommendation"] == (
        "Keep the system in observation and review mode."
    )
    assert surface["control_queue"] == []
    assert surface["hidden_control_count"] == 0
    assert surface["safety_locks"]["broker_submission_enabled"] is False


def test_control_items_rank_by_priority():
    ranked = rank_control_items(
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


def test_mode_gate_summary_keeps_live_auto_locked():
    summary = build_mode_gate_summary(
        {
            "survey_enabled": True,
            "paper_enabled": True,
            "manual_live_level_1_owner_only": True,
            "hybrid_locked": True,
            "live_auto_locked": False,
            "broker_submission_enabled": True,
            "real_capital_movement_enabled": True,
        }
    )

    assert summary["survey_enabled"] is True
    assert summary["paper_enabled"] is True
    assert summary["manual_live_level_1_owner_only"] is True
    assert summary["hybrid_locked"] is True
    assert summary["live_auto_locked"] is True
    assert summary["broker_submission_enabled"] is False
    assert summary["real_capital_movement_enabled"] is False


def test_safety_lock_summary_keeps_dangerous_actions_closed():
    summary = build_safety_lock_summary()

    assert summary["production_manual_live_authorized"] is False
    assert summary["broker_submission_enabled"] is False
    assert summary["real_capital_movement_enabled"] is False
    assert summary["direct_vault_upload_enabled"] is False
    assert summary["live_auto_locked"] is True
    assert summary["dangerous_actions_separately_gated"] is True
    assert LOCK_STATE["broker_submission_enabled"] is False


def test_takeover_handoff_contains_builder_notes_and_policy():
    handoff = owner_console_takeover_handoff()

    assert handoff["room"] == "owner_console"
    assert handoff["display_title"] == "Owner Crown Room"
    assert handoff["primary_question"] == "What controls need owner attention?"
    assert handoff["global_control_policy"]["owner_console_is_control_center"] is True
    assert handoff["safety_locks"]["broker_submission_enabled"] is False
    assert len(handoff["next_builder_notes"]) >= 9
    assert "Centralize global owner controls here." in handoff["next_builder_notes"]
    assert "Do not scatter global settings across protected rooms." in handoff["next_builder_notes"]
