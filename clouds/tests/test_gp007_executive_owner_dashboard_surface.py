from pathlib import Path
import ast

import pytest

from clouds.executive_dashboard import (
    ExecutiveHealth,
    ExecutiveRecommendationKind,
    ExecutiveSection,
    calculate_readiness_score,
    determine_executive_health,
    determine_readiness_state,
)
from clouds.executive_dashboard_service import (
    get_clouds_gp007_status_payload,
    get_executive_dashboard,
    get_executive_dashboard_card,
    get_executive_dashboard_cards,
    get_executive_dashboard_detail,
    get_executive_dashboard_detail_payload,
    get_executive_dashboard_health,
    get_executive_dashboard_payload,
    get_executive_dashboard_summary,
    get_executive_recommendations,
)


def test_gp007_dashboard_has_six_fixed_sections():
    dashboard = get_executive_dashboard()

    assert len(dashboard.cards) == 6

    assert [
        card.section
        for card in dashboard.cards
    ] == [
        "today",
        "priorities",
        "attention",
        "mission_lanes",
        "applications",
        "readiness",
    ]


def test_gp007_section_order_is_not_alphabetical():
    sections = [
        card.section
        for card in get_executive_dashboard().cards
    ]

    assert sections != sorted(sections)

    assert sections[0] == (
        ExecutiveSection.TODAY.value
    )

    assert sections[-1] == (
        ExecutiveSection.READINESS.value
    )


def test_gp007_summary_rolls_up_all_surfaces():
    summary = get_executive_dashboard_summary()

    assert (
        summary.monitored_application_count
        == 6
    )

    assert (
        summary.monitored_mission_lane_count
        == 6
    )

    assert summary.today_card_count == 5
    assert summary.priority_count == 4
    assert summary.attention_count == 2
    assert summary.action_required_count == 1
    assert summary.blocked_priority_count == 1


def test_gp007_readiness_score_is_exact():
    summary = get_executive_dashboard_summary()

    assert summary.readiness_score == 42
    assert summary.readiness_state == "building"


def test_gp007_readiness_score_function():
    score = calculate_readiness_score(
        [
            "building",
            "foundation",
            "held",
            "ready",
        ]
    )

    assert score == 54


def test_gp007_readiness_score_requires_values():
    with pytest.raises(ValueError):
        calculate_readiness_score([])

    with pytest.raises(ValueError):
        calculate_readiness_score(
            ["not-a-readiness-state"]
        )


def test_gp007_readiness_state_bands():
    assert determine_readiness_state(90) == "ready"
    assert determine_readiness_state(70) == "advancing"
    assert determine_readiness_state(50) == "building"
    assert determine_readiness_state(25) == "foundation"
    assert determine_readiness_state(10) == "held"


def test_gp007_overall_health_is_blocked():
    health = get_executive_dashboard_health()

    assert health.overall_health == (
        ExecutiveHealth.BLOCKED.value
    )

    assert health.blocked_priority_count == 1
    assert health.action_required_count == 1


def test_gp007_health_precedence_is_deterministic():
    assert determine_executive_health(
        blocked_priority_count=1,
        action_required_count=10,
        attention_system_count=10,
        watch_system_count=10,
    ) == "blocked"

    assert determine_executive_health(
        blocked_priority_count=0,
        action_required_count=1,
        attention_system_count=0,
        watch_system_count=10,
    ) == "attention"

    assert determine_executive_health(
        blocked_priority_count=0,
        action_required_count=0,
        attention_system_count=0,
        watch_system_count=1,
    ) == "watch"

    assert determine_executive_health(
        blocked_priority_count=0,
        action_required_count=0,
        attention_system_count=0,
        watch_system_count=0,
    ) == "healthy"


def test_gp007_health_rollup_counts_apps():
    health = get_executive_dashboard_health()

    assert health.healthy_application_count == 3
    assert health.watch_application_count == 1
    assert health.attention_application_count == 0
    assert health.blocked_application_count == 0
    assert health.unknown_application_count == 2


def test_gp007_health_rollup_counts_lanes():
    health = get_executive_dashboard_health()

    assert health.healthy_lane_count == 2
    assert health.watch_lane_count == 2
    assert health.attention_lane_count == 0
    assert health.blocked_lane_count == 0
    assert health.unknown_lane_count == 2


def test_gp007_today_card_rollup():
    card = get_executive_dashboard_card(
        "executive-card-today"
    )

    assert card.section == "today"
    assert card.primary_count == 1
    assert card.secondary_count == 4
    assert card.source_app_id == "observatory"
    assert card.source_lane_id == "investment_engine"


def test_gp007_priority_card_rollup():
    card = get_executive_dashboard_card(
        "executive-card-priorities"
    )

    assert card.section == "priorities"
    assert card.primary_count == 2
    assert card.secondary_count == 2
    assert card.health == "blocked"
    assert card.source_app_id == "observatory"


def test_gp007_attention_card_rollup():
    card = get_executive_dashboard_card(
        "executive-card-attention"
    )

    assert card.primary_count == 1
    assert card.secondary_count == 1
    assert card.health == "attention"


def test_gp007_mission_and_app_rollups():
    mission = get_executive_dashboard_card(
        "executive-card-mission-lanes"
    )

    applications = get_executive_dashboard_card(
        "executive-card-applications"
    )

    assert mission.primary_count == 5
    assert mission.secondary_count == 1

    assert applications.primary_count == 4
    assert applications.secondary_count == 2


def test_gp007_readiness_card_rollup():
    card = get_executive_dashboard_card(
        "executive-card-readiness"
    )

    assert card.primary_count == 42
    assert card.secondary_count == 1
    assert "42%" in card.summary
    assert "building" in card.summary


def test_gp007_cards_are_clouds_internal_navigation():
    for card in get_executive_dashboard().cards:
        assert card.navigation_mode == (
            "clouds_internal"
        )

        assert card.open_route.startswith(
            "/clouds/"
        )

        assert card.execution_performed is False


def test_gp007_dashboard_card_ids_are_unique():
    cards = get_executive_dashboard().cards

    identifiers = [
        card.card_id
        for card in cards
    ]

    assert len(identifiers) == len(
        set(identifiers)
    )


def test_gp007_card_filter_by_section():
    cards = get_executive_dashboard_cards(
        section="priorities"
    )

    assert [
        card.card_id
        for card in cards
    ] == [
        "executive-card-priorities",
    ]


def test_gp007_card_filter_by_health():
    cards = get_executive_dashboard_cards(
        health="blocked"
    )

    assert [
        card.card_id
        for card in cards
    ] == [
        "executive-card-priorities",
        "executive-card-readiness",
    ]


def test_gp007_card_filter_by_source_app():
    cards = get_executive_dashboard_cards(
        source_app_id="observatory"
    )

    assert [
        card.card_id
        for card in cards
    ] == [
        "executive-card-today",
        "executive-card-priorities",
        "executive-card-attention",
    ]


def test_gp007_recommendations_have_fixed_order():
    recommendations = (
        get_executive_recommendations()
    )

    assert [
        item.kind
        for item in recommendations
    ] == [
        ExecutiveRecommendationKind.TOP.value,
        ExecutiveRecommendationKind.SECOND.value,
        (
            ExecutiveRecommendationKind
            .WATCH_NEXT
            .value
        ),
        (
            ExecutiveRecommendationKind
            .FUTURE_OPPORTUNITY
            .value
        ),
    ]


def test_gp007_top_recommendation_is_observatory():
    recommendations = (
        get_executive_recommendations()
    )

    top = recommendations[0]

    assert top.source_priority_id == (
        "clouds-priority-"
        "ob-manual-live-readiness"
    )

    assert top.source_app_id == "observatory"
    assert top.source_lane_id == (
        "investment_engine"
    )

    assert top.execution_performed is False


def test_gp007_second_recommendation_is_atm():
    recommendations = (
        get_executive_recommendations()
    )

    second = recommendations[1]

    assert second.source_priority_id == (
        "clouds-priority-atm-route-readiness"
    )

    assert second.source_app_id == "teller"
    assert second.source_lane_id == (
        "atm_operations"
    )


def test_gp007_watch_and_future_recommendations():
    recommendations = (
        get_executive_recommendations()
    )

    watch_next = recommendations[2]
    future = recommendations[3]

    assert watch_next.source_priority_id == (
        "clouds-priority-teller-alignment"
    )

    assert future.source_priority_id == (
        "clouds-priority-grounds-planning"
    )


def test_gp007_dashboard_detail_has_owner_questions():
    detail = get_executive_dashboard_detail(
        "executive-card-priorities"
    )

    assert len(detail.owner_questions) == 3

    questions = " ".join(
        detail.owner_questions
    ).lower()

    assert "strategic priority" in questions
    assert "blocked priority" in questions
    assert "owner action" in questions


def test_gp007_detail_preserves_execution_boundary():
    detail = get_executive_dashboard_detail(
        "executive-card-readiness"
    )

    prohibitions = " ".join(
        detail.prohibited_clouds_actions
    ).lower()

    assert "cannot approve" in prohibitions
    assert "cannot execute" in prohibitions
    assert "cannot perform tower step-up" in prohibitions
    assert "cannot trade capital" in prohibitions
    assert "cannot move money" in prohibitions
    assert "cannot retrieve raw vault" in prohibitions

    assert (
        detail.downstream_execution_performed
        is False
    )


def test_gp007_missing_card_fails_closed():
    with pytest.raises(KeyError):
        get_executive_dashboard_card(
            "missing-dashboard-card"
        )

    with pytest.raises(KeyError):
        get_executive_dashboard_detail(
            "missing-dashboard-card"
        )


def test_gp007_payloads_are_json_ready():
    dashboard_payload = (
        get_executive_dashboard_payload()
    )

    detail_payload = (
        get_executive_dashboard_detail_payload(
            "executive-card-applications"
        )
    )

    assert isinstance(
        dashboard_payload["cards"],
        list,
    )

    assert isinstance(
        dashboard_payload["recommendations"],
        list,
    )

    assert dashboard_payload["section_order"] == [
        "today",
        "priorities",
        "attention",
        "mission_lanes",
        "applications",
        "readiness",
    ]

    assert detail_payload["card"][
        "card_id"
    ] == "executive-card-applications"

    assert (
        detail_payload[
            "downstream_execution_performed"
        ]
        is False
    )


def test_gp007_dashboard_source_integrity():
    dashboard = get_executive_dashboard()

    assert (
        dashboard.summary
        .source_integrity_verified
        is True
    )

    assert all(
        card.source_integrity_verified
        for card in dashboard.cards
    )

    assert (
        dashboard.summary.execution_performed
        is False
    )


def test_gp007_boundary_notice_is_safe():
    notice = (
        get_executive_dashboard()
        .boundary_notice
        .lower()
    )

    assert "summarizes" in notice
    assert "does not approve" in notice
    assert "execute" in notice


def test_gp007_status_is_ready_and_safe():
    status = get_clouds_gp007_status_payload()

    assert status["pack"] == "GP007"
    assert status["status"] == "ready"
    assert status["safe_to_continue"] is True

    assert status["dashboard_card_count"] == 6
    assert status["recommendation_count"] == 4

    assert (
        status["monitored_application_count"]
        == 6
    )

    assert (
        status["monitored_mission_lane_count"]
        == 6
    )

    assert status["readiness_score"] == 42
    assert status["overall_health"] == "blocked"

    assert (
        status["source_integrity_verified"]
        is True
    )

    assert status["tower_boundary_preserved"] is True

    assert (
        status["dashboard_execution_performed"]
        is False
    )

    assert status["cross_app_imports_used"] is False

    assert status["next_pack"] == (
        "GP008 — EXECUTIVE DASHBOARD "
        "SECTION DETAIL SURFACE"
    )


def test_gp007_production_has_no_cross_app_imports():
    clouds_root = Path(__file__).resolve().parents[1]

    production_files = [
        clouds_root / "executive_dashboard.py",
        (
            clouds_root
            / "executive_dashboard_service.py"
        ),
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
