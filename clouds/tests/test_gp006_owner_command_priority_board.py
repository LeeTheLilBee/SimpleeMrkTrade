from pathlib import Path
import ast

import pytest

from clouds.priority_board import (
    EffortLevel,
    ImpactLevel,
    PriorityCategory,
    PriorityNavigationMode,
    PriorityState,
    StrategicPriority,
    calculate_priority_score,
)
from clouds.priority_board_service import (
    get_clouds_gp006_status_payload,
    get_priority_board,
    get_priority_board_payload,
    get_priority_card,
    get_priority_cards,
    get_priority_detail,
    get_priority_detail_payload,
    get_priority_queue,
    get_priority_summary,
)


OB_PRIORITY_ID = (
    "clouds-priority-ob-manual-live-readiness"
)

ATM_PRIORITY_ID = (
    "clouds-priority-atm-route-readiness"
)

TELLER_PRIORITY_ID = (
    "clouds-priority-teller-alignment"
)

GROUNDS_PRIORITY_ID = (
    "clouds-priority-grounds-planning"
)


def test_gp006_board_contains_four_strategic_priorities():
    board = get_priority_board()

    assert board.summary.total_priority_count == 4
    assert len(board.all_priorities) == 4


def test_gp006_priority_order_is_deterministic():
    cards = get_priority_cards()

    assert [
        card.priority_id
        for card in cards
    ] == [
        OB_PRIORITY_ID,
        ATM_PRIORITY_ID,
        TELLER_PRIORITY_ID,
        GROUNDS_PRIORITY_ID,
    ]


def test_gp006_priority_bands_are_correct():
    board = get_priority_board()

    assert [
        card.priority_id
        for card in board.critical
    ] == [
        OB_PRIORITY_ID,
    ]

    assert [
        card.priority_id
        for card in board.high
    ] == [
        ATM_PRIORITY_ID,
    ]

    assert [
        card.priority_id
        for card in board.medium
    ] == [
        TELLER_PRIORITY_ID,
        GROUNDS_PRIORITY_ID,
    ]

    assert board.low == ()


def test_gp006_blocked_medium_precedes_ready_medium():
    medium = get_priority_board().medium

    assert medium[0].state == (
        PriorityState.BLOCKED.value
    )

    assert medium[0].priority_id == (
        TELLER_PRIORITY_ID
    )

    assert medium[1].state == (
        PriorityState.READY.value
    )


def test_gp006_priority_scores_are_exact():
    cards = {
        card.priority_id: card
        for card in get_priority_cards()
    }

    assert cards[OB_PRIORITY_ID].priority_score == 450
    assert cards[ATM_PRIORITY_ID].priority_score == 345
    assert cards[TELLER_PRIORITY_ID].priority_score == 260
    assert cards[GROUNDS_PRIORITY_ID].priority_score == 230


def test_gp006_score_function_rewards_blocked_visibility():
    blocked = calculate_priority_score(
        strategic_priority="medium",
        expected_impact="high",
        estimated_effort="medium",
        state="blocked",
    )

    ready = calculate_priority_score(
        strategic_priority="medium",
        expected_impact="high",
        estimated_effort="medium",
        state="ready",
    )

    assert blocked == ready + 20


def test_gp006_score_function_fails_on_unknown_value():
    with pytest.raises(ValueError):
        calculate_priority_score(
            strategic_priority="impossible",
            expected_impact="high",
            estimated_effort="medium",
            state="ready",
        )

    with pytest.raises(ValueError):
        calculate_priority_score(
            strategic_priority="high",
            expected_impact="high",
            estimated_effort="medium",
            state="not-real",
        )


def test_gp006_summary_counts_priority_levels():
    summary = get_priority_summary()

    assert summary.critical_count == 1
    assert summary.high_count == 1
    assert summary.medium_count == 2
    assert summary.low_count == 0


def test_gp006_summary_counts_states():
    summary = get_priority_summary()

    assert summary.ready_count == 2
    assert summary.watch_count == 1
    assert summary.blocked_count == 1


def test_gp006_summary_counts_categories():
    payload = get_priority_summary().to_dict()

    assert payload["category_counts"] == {
        "revenue": 1,
        "risk": 0,
        "operations": 1,
        "growth": 1,
        "infrastructure": 1,
        "research": 0,
    }


def test_gp006_summary_score_rollup_is_correct():
    summary = get_priority_summary()

    assert summary.highest_priority_score == 450
    assert summary.average_priority_score == 321.25


def test_gp006_top_recommendations_are_correct():
    board = get_priority_board()

    assert board.top_recommendation is not None
    assert board.second_recommendation is not None

    assert (
        board.top_recommendation.priority_id
        == OB_PRIORITY_ID
    )

    assert (
        board.second_recommendation.priority_id
        == ATM_PRIORITY_ID
    )


def test_gp006_cards_link_apps_and_lanes():
    ob = get_priority_card(
        OB_PRIORITY_ID
    )

    assert ob.source_app_id == "observatory"
    assert ob.source_app_name == "The Observatory"
    assert ob.source_lane_id == "investment_engine"
    assert ob.source_lane_name == "Investment Engine"

    assert ob.source_integrity_verified is True


def test_gp006_navigation_uses_tower_handoff():
    for card in get_priority_cards():
        assert card.navigation_mode == (
            PriorityNavigationMode
            .TOWER_HANDOFF
            .value
        )

        assert card.open_route.startswith(
            "/tower"
        )

        assert card.execution_performed is False


def test_gp006_filter_by_category():
    cards = get_priority_queue(
        category=PriorityCategory.GROWTH.value
    )

    assert [
        card.priority_id
        for card in cards
    ] == [
        ATM_PRIORITY_ID,
    ]


def test_gp006_filter_by_app():
    cards = get_priority_queue(
        source_app_id="teller"
    )

    assert [
        card.priority_id
        for card in cards
    ] == [
        ATM_PRIORITY_ID,
        TELLER_PRIORITY_ID,
    ]


def test_gp006_filter_by_lane():
    cards = get_priority_queue(
        source_lane_id="real_estate"
    )

    assert [
        card.priority_id
        for card in cards
    ] == [
        GROUNDS_PRIORITY_ID,
    ]


def test_gp006_blocked_only_filter():
    cards = get_priority_queue(
        blocked_only=True
    )

    assert [
        card.priority_id
        for card in cards
    ] == [
        TELLER_PRIORITY_ID,
    ]


def test_gp006_filter_by_impact_and_effort():
    cards = get_priority_queue(
        expected_impact=ImpactLevel.HIGH.value,
        estimated_effort=EffortLevel.LOW.value,
    )

    assert [
        card.priority_id
        for card in cards
    ] == [
        ATM_PRIORITY_ID,
    ]


def test_gp006_priority_detail_has_owner_questions():
    detail = get_priority_detail(
        OB_PRIORITY_ID
    )

    assert len(detail.owner_questions) == 3

    questions = " ".join(
        detail.owner_questions
    ).lower()

    assert "revenue or capital" in questions
    assert "owner action" in questions
    assert "operating application" in questions


def test_gp006_detail_preserves_execution_boundary():
    detail = get_priority_detail(
        TELLER_PRIORITY_ID
    )

    prohibitions = " ".join(
        detail.prohibited_clouds_actions
    ).lower()

    assert "cannot execute" in prohibitions
    assert "cannot approve" in prohibitions
    assert "cannot perform tower step-up" in prohibitions
    assert "cannot trade capital" in prohibitions
    assert "cannot move money" in prohibitions

    assert (
        detail.downstream_execution_performed
        is False
    )


def test_gp006_missing_priority_fails_closed():
    with pytest.raises(KeyError):
        get_priority_card(
            "missing-priority"
        )

    with pytest.raises(KeyError):
        get_priority_detail(
            "missing-priority"
        )


def test_gp006_priority_ids_are_unique():
    cards = get_priority_cards()

    identifiers = [
        card.priority_id
        for card in cards
    ]

    assert len(identifiers) == len(
        set(identifiers)
    )


def test_gp006_payloads_are_json_ready():
    board_payload = (
        get_priority_board_payload()
    )

    detail_payload = (
        get_priority_detail_payload(
            GROUNDS_PRIORITY_ID
        )
    )

    assert isinstance(
        board_payload["all_priorities"],
        list,
    )

    assert board_payload[
        "recommendations"
    ]["top"]["priority_id"] == OB_PRIORITY_ID

    assert detail_payload["card"][
        "priority_id"
    ] == GROUNDS_PRIORITY_ID

    assert (
        detail_payload[
            "downstream_execution_performed"
        ]
        is False
    )


def test_gp006_board_boundary_notice_is_safe():
    notice = (
        get_priority_board()
        .boundary_notice
        .lower()
    )

    assert "recommend" in notice
    assert "does not execute" in notice


def test_gp006_status_is_ready_and_safe():
    status = get_clouds_gp006_status_payload()

    assert status["pack"] == "GP006"
    assert status["status"] == "ready"
    assert status["safe_to_continue"] is True

    assert status["total_priority_count"] == 4
    assert status["critical_count"] == 1
    assert status["high_count"] == 1
    assert status["medium_count"] == 2
    assert status["blocked_count"] == 1

    assert status["top_recommendation_id"] == (
        OB_PRIORITY_ID
    )

    assert (
        status["source_integrity_verified"]
        is True
    )

    assert status["tower_boundary_preserved"] is True
    assert (
        status["priority_execution_performed"]
        is False
    )
    assert status["cross_app_imports_used"] is False

    assert status["next_pack"] == (
        "GP007 — EXECUTIVE OWNER DASHBOARD SURFACE"
    )


def test_gp006_production_has_no_cross_app_imports():
    clouds_root = Path(__file__).resolve().parents[1]

    production_files = [
        clouds_root / "priority_board.py",
        clouds_root / "priority_board_service.py",
    ]

    forbidden_roots = {
        "vault",
        "tower",
        "observatory",
        "teller",
        "grounds",
    }

    for path in production_files:
        tree = ast.parse(
            path.read_text(encoding="utf-8")
        )

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".")[0]
                    assert root not in forbidden_roots

            if isinstance(node, ast.ImportFrom):
                if node.module is None:
                    continue

                root = node.module.split(".")[0]
                assert root not in forbidden_roots
