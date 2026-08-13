from pathlib import Path
import ast

import pytest

from clouds.executive_dashboard_detail import (
    ExecutiveSectionHealth,
    ExecutiveSectionId,
    ExecutiveSectionNavigationMode,
    ExecutiveSectionReadiness,
    ExecutiveSectionRecommendationKind,
)
from clouds.executive_dashboard_detail_service import (
    filter_executive_dashboard_sections,
    get_clouds_gp008_status_payload,
    get_executive_dashboard_section,
    get_executive_dashboard_section_detail,
    get_executive_dashboard_section_detail_payload,
    get_executive_dashboard_section_surface,
    get_executive_dashboard_section_surface_payload,
    get_executive_dashboard_sections,
    get_executive_section_metrics,
    get_executive_section_navigation_targets,
    get_executive_section_recommendations,
    get_executive_section_summary,
)


FIXED_SECTION_IDS = [
    "today",
    "priorities",
    "attention",
    "mission_lanes",
    "applications",
    "readiness",
]


def test_gp008_has_six_fixed_sections():
    sections = (
        get_executive_dashboard_sections()
    )

    assert len(sections) == 6

    assert [
        item.summary.section_id
        for item in sections
    ] == FIXED_SECTION_IDS


def test_gp008_section_order_is_not_alphabetical():
    section_ids = [
        item.summary.section_id
        for item
        in get_executive_dashboard_sections()
    ]

    assert section_ids != sorted(section_ids)
    assert section_ids[0] == "today"
    assert section_ids[-1] == "readiness"


def test_gp008_section_ids_are_unique():
    sections = (
        get_executive_dashboard_sections()
    )

    identifiers = [
        item.summary.section_id
        for item in sections
    ]

    assert len(identifiers) == len(
        set(identifiers)
    )


def test_gp008_section_enum_is_immutable_and_complete():
    assert [
        item.value
        for item in ExecutiveSectionId
    ] == FIXED_SECTION_IDS


def test_gp008_today_section_summary():
    summary = get_executive_section_summary(
        "today"
    )

    assert summary.section_id == "today"
    assert summary.title == "Today"
    assert summary.health == (
        ExecutiveSectionHealth
        .ATTENTION
        .value
    )
    assert summary.readiness == (
        ExecutiveSectionReadiness
        .ADVANCING
        .value
    )
    assert summary.readiness_score == 70
    assert summary.primary_metric == 1
    assert summary.secondary_metric == 1


def test_gp008_priorities_section_summary():
    summary = get_executive_section_summary(
        "priorities"
    )

    assert summary.health == "blocked"
    assert summary.readiness == "building"
    assert summary.readiness_score == 60
    assert summary.primary_metric == 2
    assert summary.secondary_metric == 1


def test_gp008_attention_section_summary():
    summary = get_executive_section_summary(
        "attention"
    )

    assert summary.health == "attention"
    assert summary.readiness == "advancing"
    assert summary.primary_metric == 1
    assert summary.secondary_metric == 1


def test_gp008_mission_lanes_section_summary():
    summary = get_executive_section_summary(
        "mission_lanes"
    )

    assert summary.health == "watch"
    assert summary.readiness == "building"
    assert summary.primary_metric == 5
    assert summary.secondary_metric == 1


def test_gp008_applications_section_summary():
    summary = get_executive_section_summary(
        "applications"
    )

    assert summary.health == "watch"
    assert summary.readiness == "building"
    assert summary.primary_metric == 4
    assert summary.secondary_metric == 2


def test_gp008_readiness_section_summary():
    summary = get_executive_section_summary(
        "readiness"
    )

    assert summary.section_id == "readiness"
    assert summary.health == "blocked"
    assert summary.readiness == "building"
    assert summary.readiness_score == 42
    assert summary.primary_metric == 42
    assert summary.secondary_metric == 1


def test_gp008_today_metrics_are_ordered():
    metrics = get_executive_section_metrics(
        "today"
    )

    assert [
        item.metric_id
        for item in metrics
    ] == [
        "today-focus-count",
        "today-watch-count",
        "today-target-count",
        "today-action-required-count",
    ]

    assert [
        item.value
        for item in metrics
    ] == [
        1,
        1,
        3,
        1,
    ]


def test_gp008_priority_metrics_are_ordered():
    metrics = get_executive_section_metrics(
        "priorities"
    )

    assert [
        item.metric_id
        for item in metrics
    ] == [
        "priority-total-count",
        "priority-critical-count",
        "priority-high-count",
        "priority-blocked-count",
        "priority-highest-score",
    ]

    assert metrics[-1].value == 450


def test_gp008_readiness_metrics_are_ordered():
    metrics = get_executive_section_metrics(
        "readiness"
    )

    assert [
        item.metric_id
        for item in metrics
    ] == [
        "readiness-score",
        "readiness-state",
        "readiness-blocked-priorities",
        "readiness-action-required",
        "readiness-app-count",
        "readiness-lane-count",
    ]

    assert metrics[0].value == 42
    assert metrics[1].value == "building"


def test_gp008_today_recommendations_are_ordered():
    recommendations = (
        get_executive_section_recommendations(
            "today"
        )
    )

    assert [
        item.kind
        for item in recommendations
    ] == [
        (
            ExecutiveSectionRecommendationKind
            .TOP
            .value
        ),
        (
            ExecutiveSectionRecommendationKind
            .SECOND
            .value
        ),
        (
            ExecutiveSectionRecommendationKind
            .WATCH_NEXT
            .value
        ),
    ]


def test_gp008_priority_recommendations_are_ordered():
    recommendations = (
        get_executive_section_recommendations(
            "priorities"
        )
    )

    assert [
        item.kind
        for item in recommendations
    ] == [
        "top",
        "second",
        "watch_next",
    ]

    assert recommendations[0].source_app_id == (
        "observatory"
    )

    assert recommendations[1].source_lane_id == (
        "atm_operations"
    )

    assert recommendations[2].source_lane_id == (
        "people_and_payments"
    )


def test_gp008_readiness_recommendations_are_ordered():
    recommendations = (
        get_executive_section_recommendations(
            "readiness"
        )
    )

    assert [
        item.kind
        for item in recommendations
    ] == [
        "top",
        "second",
        "watch_next",
    ]


def test_gp008_navigation_targets_are_safe():
    for section in (
        get_executive_dashboard_sections()
    ):
        assert section.navigation_targets

        for target in section.navigation_targets:
            assert target.execution_performed is False

            assert target.navigation_mode in {
                (
                    ExecutiveSectionNavigationMode
                    .CLOUDS_INTERNAL
                    .value
                ),
                (
                    ExecutiveSectionNavigationMode
                    .TOWER_HANDOFF
                    .value
                ),
            }


def test_gp008_primary_navigation_is_clouds_internal():
    for section_id in FIXED_SECTION_IDS:
        targets = (
            get_executive_section_navigation_targets(
                section_id
            )
        )

        assert targets[0].navigation_mode == (
            ExecutiveSectionNavigationMode
            .CLOUDS_INTERNAL
            .value
        )

        assert targets[0].open_route.startswith(
            "/clouds/"
        )


def test_gp008_linked_apps_are_visible():
    priorities = (
        get_executive_dashboard_section(
            "priorities"
        )
    )

    assert priorities.linked_app_ids == (
        "grounds",
        "observatory",
        "teller",
    )

    applications = (
        get_executive_dashboard_section(
            "applications"
        )
    )

    assert applications.linked_app_ids == (
        "tower",
        "observatory",
        "archive_vault",
        "teller",
        "grounds",
        "clouds",
    )


def test_gp008_linked_lanes_are_visible():
    priorities = (
        get_executive_dashboard_section(
            "priorities"
        )
    )

    assert priorities.linked_mission_lane_ids == (
        "atm_operations",
        "investment_engine",
        "people_and_payments",
        "real_estate",
    )

    applications = (
        get_executive_dashboard_section(
            "applications"
        )
    )

    assert (
        applications.linked_mission_lane_ids
        == ()
    )


def test_gp008_owner_questions_exist():
    for section in (
        get_executive_dashboard_sections()
    ):
        assert len(section.owner_questions) == 3


def test_gp008_boundaries_are_preserved():
    for section in (
        get_executive_dashboard_sections()
    ):
        prohibited = " ".join(
            section.prohibited_clouds_actions
        ).lower()

        assert "cannot authenticate" in prohibited
        assert "cannot perform tower step-up" in prohibited
        assert "cannot approve" in prohibited
        assert "cannot execute" in prohibited
        assert "cannot trade capital" in prohibited
        assert "cannot move money" in prohibited
        assert "cannot retrieve raw vault" in prohibited

        assert (
            section.downstream_execution_performed
            is False
        )


def test_gp008_source_integrity_is_verified():
    for section in (
        get_executive_dashboard_sections()
    ):
        assert (
            section.summary
            .source_integrity_verified
            is True
        )

        assert (
            section.summary.execution_performed
            is False
        )


def test_gp008_filter_by_section():
    sections = (
        filter_executive_dashboard_sections(
            section_id="attention"
        )
    )

    assert [
        item.summary.section_id
        for item in sections
    ] == [
        "attention",
    ]


def test_gp008_filter_by_health():
    sections = (
        filter_executive_dashboard_sections(
            health="blocked"
        )
    )

    assert [
        item.summary.section_id
        for item in sections
    ] == [
        "priorities",
        "readiness",
    ]


def test_gp008_filter_by_readiness():
    sections = (
        filter_executive_dashboard_sections(
            readiness="advancing"
        )
    )

    assert [
        item.summary.section_id
        for item in sections
    ] == [
        "today",
        "attention",
    ]


def test_gp008_filter_by_linked_app():
    sections = (
        filter_executive_dashboard_sections(
            linked_app_id="observatory"
        )
    )

    assert [
        item.summary.section_id
        for item in sections
    ] == [
        "today",
        "priorities",
        "attention",
        "mission_lanes",
        "applications",
        "readiness",
    ]


def test_gp008_filter_by_linked_lane():
    sections = (
        filter_executive_dashboard_sections(
            linked_mission_lane_id=(
                "investment_engine"
            )
        )
    )

    assert [
        item.summary.section_id
        for item in sections
    ] == [
        "today",
        "priorities",
        "attention",
        "mission_lanes",
        "readiness",
    ]


def test_gp008_missing_section_fails_closed():
    with pytest.raises(KeyError):
        get_executive_dashboard_section(
            "missing-section"
        )

    with pytest.raises(KeyError):
        get_executive_dashboard_section_detail(
            "missing-section"
        )

    with pytest.raises(KeyError):
        get_executive_section_metrics(
            "missing-section"
        )


def test_gp008_detail_payload_is_json_ready():
    payload = (
        get_executive_dashboard_section_detail_payload(
            "priorities"
        )
    )

    assert payload["summary"]["section_id"] == (
        "priorities"
    )

    assert isinstance(
        payload["metrics"],
        list,
    )

    assert isinstance(
        payload["recommendations"],
        list,
    )

    assert isinstance(
        payload["navigation_targets"],
        list,
    )

    assert (
        payload[
            "downstream_execution_performed"
        ]
        is False
    )


def test_gp008_surface_payload_is_json_ready():
    payload = (
        get_executive_dashboard_section_surface_payload()
    )

    assert payload["section_order"] == (
        FIXED_SECTION_IDS
    )

    assert len(payload["sections"]) == 6

    assert (
        "does not approve"
        in payload["boundary_notice"].lower()
    )


def test_gp008_status_is_ready_and_safe():
    status = get_clouds_gp008_status_payload()

    assert status["pack"] == "GP008"
    assert status["status"] == "ready"
    assert status["safe_to_continue"] is True

    assert status["section_count"] == 6

    assert status["section_ids"] == (
        FIXED_SECTION_IDS
    )

    assert status["metric_count"] == 29
    assert status["recommendation_count"] == 15
    assert status["navigation_target_count"] == 7

    assert (
        status["source_integrity_verified"]
        is True
    )

    assert status["tower_boundary_preserved"] is True

    assert (
        status["section_execution_performed"]
        is False
    )

    assert status["cross_app_imports_used"] is False

    assert status["next_pack"] == (
        "GP009 — EXECUTIVE DASHBOARD "
        "NAVIGATION MAP"
    )


def test_gp008_production_has_no_cross_app_imports():
    clouds_root = Path(__file__).resolve().parents[1]

    production_files = [
        (
            clouds_root
            / "executive_dashboard_detail.py"
        ),
        (
            clouds_root
            / "executive_dashboard_detail_service.py"
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
