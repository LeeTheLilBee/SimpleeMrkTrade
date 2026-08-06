from ob_owner_experience import (
    SIX_ROOM_ORDER,
    build_consolidated_acceptance_contract,
    build_consolidated_safety_summary,
    build_room_card,
    build_room_cards,
    build_six_room_heading_map,
    build_six_room_question_map,
    build_six_room_readiness_report,
    six_room_acceptance_contract,
    six_room_takeover_handoff,
)


def test_six_room_contract_has_all_rooms_in_locked_order():
    contract = build_consolidated_acceptance_contract()

    assert contract["package"] == "ob_owner_experience_six_room_consolidation"
    assert contract["display_title"] == "Six-Room Owner Experience"
    assert contract["room_count"] == 6
    assert contract["room_order"] == [
        "dashboard",
        "market_map",
        "symbol_page",
        "trade_center",
        "review_center",
        "owner_console",
    ]
    assert contract["decision"] == (
        "READY_FOR_TOWER_INTEGRATION_REVIEW_WITH_SAFETY_LOCKS_HELD"
    )


def test_six_room_display_titles_are_preserved():
    contract = six_room_acceptance_contract()

    assert contract["room_display_titles"]["dashboard"] == "Today’s Command Nest"
    assert contract["room_display_titles"]["market_map"] == "Market Weather"
    assert contract["room_display_titles"]["symbol_page"] == "Asset Storybook"
    assert contract["room_display_titles"]["trade_center"] == "Decision Garden"
    assert contract["room_display_titles"]["review_center"] == "Reflection Library"
    assert contract["room_display_titles"]["owner_console"] == "Owner Crown Room"


def test_six_room_primary_questions_are_preserved():
    questions = build_six_room_question_map()

    assert questions["dashboard"] == "What needs my attention today?"
    assert questions["market_map"] == "What is happening in the market?"
    assert questions["symbol_page"] == "What do I need to understand about this asset?"
    assert questions["trade_center"] == "What decisions or actions are waiting?"
    assert questions["review_center"] == "What did we learn and what needs review?"
    assert questions["owner_console"] == "What controls need owner attention?"


def test_six_room_heading_map_keeps_cute_informative_headings():
    headings = build_six_room_heading_map()

    assert headings["dashboard"]["hero"] == "🌙 Today’s Command Nest"
    assert headings["market_map"]["hero"] == "🌦️ Market Weather"
    assert headings["symbol_page"]["hero"] == "🔎 Asset Storybook"
    assert headings["trade_center"]["hero"] == "🌸 Decision Garden"
    assert headings["review_center"]["hero"] == "📚 Reflection Library"
    assert headings["owner_console"]["hero"] == "👑 Owner Crown Room"

    assert headings["owner_console"]["locks"] == "🔒 Safety Locks"
    assert headings["review_center"]["receipts"] == "🧾 Receipt Check"
    assert headings["trade_center"]["risk"] == "🛡️ Risk Gate"


def test_room_cards_include_acceptance_and_handoff_notes():
    cards = build_room_cards()

    assert len(cards) == 6
    assert [card["room"] for card in cards] == SIX_ROOM_ORDER

    for card in cards:
        assert card["display_title"]
        assert card["primary_question"]
        assert card["route_hint"]
        assert card["section_headings"]
        assert card["acceptance_contract"]
        assert card["takeover_summary"]
        assert card["next_builder_notes"]
        assert card["accepted_for_consolidation"] is True


def test_unknown_room_card_fails_closed():
    try:
        build_room_card("unknown_room")
    except KeyError as exc:
        assert "Unknown consolidated room" in str(exc)
    else:
        raise AssertionError("Unknown room should fail closed.")


def test_safety_summary_keeps_execution_locked():
    safety = build_consolidated_safety_summary()

    assert safety["production_manual_live_authorized"] is False
    assert safety["broker_submission_enabled"] is False
    assert safety["real_capital_movement_enabled"] is False
    assert safety["direct_vault_upload_enabled"] is False
    assert safety["live_auto_locked"] is True
    assert safety["dangerous_actions_separately_gated"] is True
    assert safety["trade_center_lock_state"]["broker_submission_enabled"] is False
    assert safety["owner_console_safety_locks"]["broker_submission_enabled"] is False


def test_acceptance_checklist_all_required_items_present():
    contract = build_consolidated_acceptance_contract()
    checklist_ids = [
        item["check_id"]
        for item in contract["acceptance_checklist"]
    ]

    assert "one_question_per_room" in checklist_ids
    assert "cute_informative_headings" in checklist_ids
    assert "soulaana_visible" in checklist_ids
    assert "details_hidden_by_default" in checklist_ids
    assert "owner_console_global_controls" in checklist_ids
    assert "broker_submission_locked" in checklist_ids
    assert "real_capital_locked" in checklist_ids
    assert "live_auto_locked" in checklist_ids
    assert "handoff_written" in checklist_ids

    assert all(item["required"] is True for item in contract["acceptance_checklist"])


def test_readiness_report_is_ready_for_integration_not_staging_ready():
    report = build_six_room_readiness_report()

    assert report["report_type"] == "six_room_owner_experience_readiness"
    assert report["ready_for_tower_integration_review"] is True
    assert report["ready_for_owner_walkthrough"] is False
    assert report["staging_ready"] is False
    assert "Owner walkthrough" in report["reason_staging_ready_false"]
    assert report["safety_summary"]["live_auto_locked"] is True


def test_takeover_handoff_warns_not_to_claim_staging_ready():
    handoff = six_room_takeover_handoff()

    assert handoff["display_title"] == "Six-Room Owner Experience"
    assert handoff["room_order"] == SIX_ROOM_ORDER
    assert "Do not claim STAGING_READY until owner walkthrough acceptance." in handoff["next_builder_notes"]
    assert handoff["safety_summary"]["broker_submission_enabled"] is False
    assert handoff["safety_summary"]["real_capital_movement_enabled"] is False
    assert handoff["safety_summary"]["live_auto_locked"] is True


def test_contract_must_not_claim_forbidden_states():
    contract = six_room_acceptance_contract()

    assert "STAGING_READY" in contract["must_not_claim"]
    assert "production deployment authorized" in contract["must_not_claim"]
    assert "broker submission enabled" in contract["must_not_claim"]
    assert "real capital movement enabled" in contract["must_not_claim"]
    assert "Live Auto unlocked" in contract["must_not_claim"]
    assert "Tower return/session continuity repaired" in contract["must_not_claim"]
    assert "Render redeployed" in contract["must_not_claim"]
