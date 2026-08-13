import ast
from pathlib import Path

import pytest

from clouds.executive_navigation_map import (
    ExecutiveNavigationAuthority,
    ExecutiveNavigationAvailability,
    ExecutiveNavigationDestinationKind,
    ExecutiveNavigationMode,
    filter_navigation_destinations,
)

from clouds.executive_navigation_map_service import (
    filter_executive_navigation_destinations,
    get_clouds_gp009_status_payload,
    get_executive_navigation_destination,
    get_executive_navigation_destination_payload,
    get_executive_navigation_destinations,
    get_executive_navigation_map,
    get_executive_navigation_map_payload,
    get_executive_navigation_map_summary,
    get_executive_navigation_section,
    get_executive_navigation_section_payload,
    get_executive_navigation_sections,
)


FIXED_SECTION_IDS = (
    "today",
    "priorities",
    "attention",
    "mission_lanes",
    "applications",
    "readiness",
)


EXPECTED_DESTINATION_IDS = (
    "clouds-executive-dashboard",
    "clouds-today",
    "clouds-priority-board",
    "clouds-owner-attention",
    "clouds-mission-lanes",
    "clouds-applications",
    "clouds-readiness",
    "tower-observatory",
    "tower-teller",
    "tower-grounds",
    "tower-vault",
)


def test_gp009_navigation_map_is_ready():
    navigation_map = (
        get_executive_navigation_map()
    )

    assert (
        navigation_map.title
        == "Executive Navigation Map"
    )

    assert len(
        navigation_map.destinations
    ) == 11

    assert len(
        navigation_map.sections
    ) == 6


def test_gp009_destination_order_is_deterministic():
    destinations = (
        get_executive_navigation_destinations()
    )

    assert tuple(
        item.destination_id
        for item in destinations
    ) == EXPECTED_DESTINATION_IDS


def test_gp009_has_six_fixed_dashboard_sections():
    sections = (
        get_executive_navigation_sections()
    )

    assert tuple(
        item.section_id
        for item in sections
    ) == FIXED_SECTION_IDS


def test_gp009_clouds_internal_destinations():
    destinations = (
        filter_executive_navigation_destinations(
            navigation_mode=(
                ExecutiveNavigationMode
                .CLOUDS_INTERNAL.value
            )
        )
    )

    assert len(destinations) == 7

    assert all(
        item.requires_tower is False
        for item in destinations
    )


def test_gp009_tower_handoff_destinations():
    destinations = (
        filter_executive_navigation_destinations(
            navigation_mode=(
                ExecutiveNavigationMode
                .TOWER_HANDOFF.value
            )
        )
    )

    assert tuple(
        item.destination_id
        for item in destinations
    ) == (
        "tower-observatory",
        "tower-teller",
        "tower-grounds",
        "tower-vault",
    )

    assert all(
        item.requires_tower is True
        for item in destinations
    )

    assert all(
        item.authority
        == ExecutiveNavigationAuthority
        .TOWER.value
        for item in destinations
    )


def test_gp009_clouds_never_executes_navigation():
    destinations = (
        get_executive_navigation_destinations()
    )

    assert all(
        item.clouds_executes_navigation
        is False
        for item in destinations
    )


def test_gp009_no_downstream_execution():
    destinations = (
        get_executive_navigation_destinations()
    )

    assert all(
        item.downstream_execution_performed
        is False
        for item in destinations
    )

    assert (
        get_executive_navigation_map()
        .summary
        .downstream_execution_performed
        is False
    )


def test_gp009_observatory_requires_tower():
    destination = (
        get_executive_navigation_destination(
            "tower-observatory"
        )
    )

    assert (
        destination.source_app_id
        == "observatory"
    )

    assert (
        destination.source_lane_id
        == "investment_engine"
    )

    assert destination.requires_tower is True

    assert (
        destination.requires_owner_permission
        is True
    )

    assert destination.requires_step_up is True

    assert (
        destination.navigation_mode
        == ExecutiveNavigationMode
        .TOWER_HANDOFF.value
    )


def test_gp009_reserved_apps_are_visible_but_reserved():
    teller = (
        get_executive_navigation_destination(
            "tower-teller"
        )
    )

    grounds = (
        get_executive_navigation_destination(
            "tower-grounds"
        )
    )

    assert (
        teller.availability
        == ExecutiveNavigationAvailability
        .RESERVED.value
    )

    assert (
        grounds.availability
        == ExecutiveNavigationAvailability
        .RESERVED.value
    )


def test_gp009_applications_section_maps_destinations():
    section = (
        get_executive_navigation_section(
            "applications"
        )
    )

    assert (
        "clouds-applications"
        in section.destination_ids
    )

    assert (
        "tower-observatory"
        in section.destination_ids
    )

    assert (
        "tower-teller"
        in section.destination_ids
    )

    assert (
        "tower-grounds"
        in section.destination_ids
    )

    assert (
        "tower-vault"
        in section.destination_ids
    )

    assert section.clouds_internal_count == 1
    assert section.tower_handoff_count == 4


def test_gp009_today_section_default_destination():
    section = (
        get_executive_navigation_section(
            "today"
        )
    )

    assert (
        section.default_destination_id
        == "clouds-today"
    )


def test_gp009_priority_section_default_destination():
    section = (
        get_executive_navigation_section(
            "priorities"
        )
    )

    assert (
        section.default_destination_id
        == "clouds-priority-board"
    )


def test_gp009_attention_section_default_destination():
    section = (
        get_executive_navigation_section(
            "attention"
        )
    )

    assert (
        section.default_destination_id
        == "clouds-owner-attention"
    )


def test_gp009_mission_lane_section_default_destination():
    section = (
        get_executive_navigation_section(
            "mission_lanes"
        )
    )

    assert (
        section.default_destination_id
        == "clouds-mission-lanes"
    )


def test_gp009_readiness_section_default_destination():
    section = (
        get_executive_navigation_section(
            "readiness"
        )
    )

    assert (
        section.default_destination_id
        == "clouds-readiness"
    )


def test_gp009_filter_by_application():
    destinations = (
        filter_executive_navigation_destinations(
            source_app_id="observatory"
        )
    )

    assert len(destinations) == 1

    assert (
        destinations[0].destination_id
        == "tower-observatory"
    )


def test_gp009_filter_by_mission_lane():
    destinations = (
        filter_executive_navigation_destinations(
            source_lane_id="investment_engine"
        )
    )

    assert len(destinations) == 1

    assert (
        destinations[0].destination_id
        == "tower-observatory"
    )


def test_gp009_filter_contract_directly():
    destinations = (
        get_executive_navigation_destinations()
    )

    filtered = filter_navigation_destinations(
        destinations,
        requires_tower=True,
    )

    assert len(filtered) == 4


def test_gp009_unknown_destination_fails_closed():
    with pytest.raises(KeyError):
        get_executive_navigation_destination(
            "not-a-real-destination"
        )


def test_gp009_unknown_section_fails_closed():
    with pytest.raises(KeyError):
        get_executive_navigation_section(
            "not-a-real-section"
        )


def test_gp009_destination_payload():
    payload = (
        get_executive_navigation_destination_payload(
            "tower-observatory"
        )
    )

    assert (
        payload["destination_id"]
        == "tower-observatory"
    )

    assert (
        payload["navigation_mode"]
        == "tower_handoff"
    )

    assert (
        payload["clouds_executes_navigation"]
        is False
    )


def test_gp009_section_payload():
    payload = (
        get_executive_navigation_section_payload(
            "applications"
        )
    )

    assert payload["section_id"] == "applications"

    assert payload["tower_handoff_count"] == 4


def test_gp009_map_payload():
    payload = (
        get_executive_navigation_map_payload()
    )

    assert (
        payload["summary"]
        ["destination_count"]
        == 11
    )

    assert len(
        payload["destinations"]
    ) == 11

    assert len(
        payload["sections"]
    ) == 6


def test_gp009_summary():
    summary = (
        get_executive_navigation_map_summary()
    )

    assert summary.destination_count == 11
    assert summary.section_count == 6
    assert summary.clouds_internal_count == 7
    assert summary.tower_handoff_count == 4
    assert summary.unavailable_count == 2

    assert (
        summary.source_integrity_verified
        is True
    )

    assert (
        summary.tower_boundary_preserved
        is True
    )


def test_gp009_prohibited_actions_are_explicit():
    navigation_map = (
        get_executive_navigation_map()
    )

    prohibited = " ".join(
        navigation_map.prohibited_clouds_actions
    ).lower()

    assert "authenticate" in prohibited
    assert "permission" in prohibited
    assert "step-up" in prohibited
    assert "trade" in prohibited
    assert "move money" in prohibited
    assert "vault" in prohibited


def test_gp009_tower_boundary_notice_is_explicit():
    navigation_map = (
        get_executive_navigation_map()
    )

    notice = (
        navigation_map.boundary_notice.lower()
    )

    assert "tower" in notice
    assert "authentication" in notice
    assert "permission" in notice
    assert "step-up" in notice


def test_gp009_status_is_ready_and_safe():
    status = (
        get_clouds_gp009_status_payload()
    )

    assert status["pack"] == "GP009"

    assert (
        status["section"]
        == "EXECUTIVE DASHBOARD NAVIGATION MAP"
    )

    assert status["status"] == "ready"
    assert status["safe_to_continue"] is True

    assert status["section_count"] == 6
    assert status["destination_count"] == 11

    assert (
        status["clouds_internal_count"]
        == 7
    )

    assert (
        status["tower_handoff_count"]
        == 4
    )

    assert status["unavailable_count"] == 2

    assert (
        status["source_integrity_verified"]
        is True
    )

    assert (
        status["tower_boundary_preserved"]
        is True
    )

    assert (
        status["navigation_execution_performed"]
        is False
    )

    assert (
        status["downstream_execution_performed"]
        is False
    )

    assert (
        status["cross_app_imports_used"]
        is False
    )


def test_gp009_no_cross_app_python_imports():
    root = Path(__file__).resolve().parents[2]

    files = (
        root
        / "clouds"
        / "executive_navigation_map.py",
        root
        / "clouds"
        / "executive_navigation_map_service.py",
    )

    prohibited_roots = {
        "tower",
        "observatory",
        "vault",
        "teller",
        "grounds",
    }

    for path in files:
        tree = ast.parse(
            path.read_text(
                encoding="utf-8"
            )
        )

        for node in ast.walk(tree):
            if isinstance(
                node,
                ast.Import,
            ):
                for alias in node.names:
                    root_name = (
                        alias.name
                        .split(".")[0]
                        .lower()
                    )

                    assert (
                        root_name
                        not in prohibited_roots
                    )

            if isinstance(
                node,
                ast.ImportFrom,
            ):
                module = (
                    node.module
                    or ""
                )

                root_name = (
                    module
                    .lstrip(".")
                    .split(".")[0]
                    .lower()
                )

                assert (
                    root_name
                    not in prohibited_roots
                )


def test_gp009_application_destination_kind():
    destination = (
        get_executive_navigation_destination(
            "tower-observatory"
        )
    )

    assert (
        destination.kind
        == ExecutiveNavigationDestinationKind
        .APPLICATION.value
    )


def test_gp009_navigation_map_is_repeatable():
    first = (
        get_executive_navigation_map_payload()
    )

    second = (
        get_executive_navigation_map_payload()
    )

    assert first == second
