import ast
from pathlib import Path

import pytest

from clouds.executive_owner_workspace import (
    WorkspaceNavigationMode,
    WorkspacePanelKind,
)

from clouds.executive_owner_workspace_service import (
    filter_executive_owner_workspace_items,
    get_clouds_gp010_status_payload,
    get_executive_owner_workspace,
    get_executive_owner_workspace_item,
    get_executive_owner_workspace_item_payload,
    get_executive_owner_workspace_items,
    get_executive_owner_workspace_panel,
    get_executive_owner_workspace_panel_payload,
    get_executive_owner_workspace_panels,
    get_executive_owner_workspace_payload,
    get_executive_owner_workspace_summary,
)


EXPECTED_PANEL_IDS = (
    "workspace-panel-now",
    "workspace-panel-next",
    "workspace-panel-watch",
    "workspace-panel-sections",
    "workspace-panel-applications",
    "workspace-panel-readiness",
)


def test_gp010_workspace_exists():
    workspace = (
        get_executive_owner_workspace()
    )

    assert (
        workspace.title
        == "Executive Owner Command Workspace"
    )

    assert len(workspace.panels) == 6


def test_gp010_panel_order_is_deterministic():
    panels = (
        get_executive_owner_workspace_panels()
    )

    assert tuple(
        panel.panel_id
        for panel in panels
    ) == EXPECTED_PANEL_IDS


def test_gp010_panel_kinds_are_fixed():
    panels = (
        get_executive_owner_workspace_panels()
    )

    assert tuple(
        panel.kind
        for panel in panels
    ) == (
        WorkspacePanelKind.NOW.value,
        WorkspacePanelKind.NEXT.value,
        WorkspacePanelKind.WATCH.value,
        WorkspacePanelKind.SECTIONS.value,
        WorkspacePanelKind.APPLICATIONS.value,
        WorkspacePanelKind.READINESS.value,
    )


def test_gp010_now_panel_contains_two_items():
    panel = (
        get_executive_owner_workspace_panel(
            "workspace-panel-now"
        )
    )

    assert panel.item_count == 2

    assert tuple(
        item.item_id
        for item in panel.items
    ) == (
        "workspace-now-focus",
        "workspace-now-priority",
    )


def test_gp010_now_focus_is_observatory():
    item = (
        get_executive_owner_workspace_item(
            "workspace-now-focus"
        )
    )

    assert item.source_app_id == "observatory"
    assert item.source_lane_id == "investment_engine"
    assert item.priority == "critical"
    assert item.execution_performed is False


def test_gp010_now_focus_uses_tower_handoff():
    item = (
        get_executive_owner_workspace_item(
            "workspace-now-focus"
        )
    )

    action = item.navigation_action

    assert action is not None
    assert action.destination_id == "tower-observatory"

    assert (
        action.navigation_mode
        == WorkspaceNavigationMode
        .TOWER_HANDOFF.value
    )

    assert action.requires_tower is True
    assert action.requires_owner_permission is True
    assert action.requires_step_up is True

    assert (
        action.clouds_executes_navigation
        is False
    )


def test_gp010_next_panel_has_three_items():
    panel = (
        get_executive_owner_workspace_panel(
            "workspace-panel-next"
        )
    )

    assert panel.item_count == 3


def test_gp010_watch_panel_has_two_items():
    panel = (
        get_executive_owner_workspace_panel(
            "workspace-panel-watch"
        )
    )

    assert panel.item_count == 2


def test_gp010_sections_panel_has_six_items():
    panel = (
        get_executive_owner_workspace_panel(
            "workspace-panel-sections"
        )
    )

    assert panel.item_count == 6

    assert tuple(
        item.source_section_id
        for item in panel.items
    ) == (
        "today",
        "priorities",
        "attention",
        "mission_lanes",
        "applications",
        "readiness",
    )


def test_gp010_section_items_are_internal_navigation():
    panel = (
        get_executive_owner_workspace_panel(
            "workspace-panel-sections"
        )
    )

    for item in panel.items:
        assert item.navigation_action is not None

        assert (
            item.navigation_action
            .navigation_mode
            == WorkspaceNavigationMode
            .CLOUDS_INTERNAL.value
        )

        assert (
            item.navigation_action
            .requires_tower
            is False
        )


def test_gp010_application_panel_has_four_items():
    panel = (
        get_executive_owner_workspace_panel(
            "workspace-panel-applications"
        )
    )

    assert panel.item_count == 4

    assert {
        item.source_app_id
        for item in panel.items
    } == {
        "observatory",
        "teller",
        "grounds",
        "archive_vault",
    }


def test_gp010_application_panel_uses_tower():
    panel = (
        get_executive_owner_workspace_panel(
            "workspace-panel-applications"
        )
    )

    for item in panel.items:
        action = item.navigation_action

        assert action is not None
        assert action.requires_tower is True

        assert (
            action.navigation_mode
            == "tower_handoff"
        )

        assert (
            action.clouds_executes_navigation
            is False
        )


def test_gp010_readiness_panel_has_one_item():
    panel = (
        get_executive_owner_workspace_panel(
            "workspace-panel-readiness"
        )
    )

    assert panel.item_count == 1

    item = panel.items[0]

    assert item.item_id == (
        "workspace-readiness-overall"
    )

    assert item.source_section_id == "readiness"


def test_gp010_total_item_inventory_is_18():
    items = (
        get_executive_owner_workspace_items()
    )

    assert len(items) == 18


def test_gp010_item_ids_are_unique():
    items = (
        get_executive_owner_workspace_items()
    )

    ids = [
        item.item_id
        for item in items
    ]

    assert len(ids) == len(set(ids))


def test_gp010_headline_is_explanatory():
    headline = (
        get_executive_owner_workspace()
        .headline
    )

    assert headline.title == (
        "Owner Command Workspace"
    )

    assert "applications" in (
        headline.explanation.lower()
    )

    assert "mission lanes" in (
        headline.explanation.lower()
    )

    assert headline.readiness_score == 42
    assert headline.readiness_state == "building"


def test_gp010_headline_knows_top_focus():
    headline = (
        get_executive_owner_workspace()
        .headline
    )

    assert headline.top_focus_title
    assert headline.top_focus_app_id == (
        "observatory"
    )


def test_gp010_summary_is_correct():
    summary = (
        get_executive_owner_workspace_summary()
    )

    assert summary.panel_count == 6
    assert summary.item_count == 18

    assert summary.action_required_count == 1
    assert summary.blocked_priority_count == 1

    assert summary.readiness_score == 42
    assert summary.overall_health == "blocked"

    assert (
        summary.source_integrity_verified
        is True
    )

    assert (
        summary.tower_boundary_preserved
        is True
    )

    assert summary.execution_performed is False


def test_gp010_workspace_has_internal_navigation():
    summary = (
        get_executive_owner_workspace_summary()
    )

    assert summary.internal_navigation_count > 0


def test_gp010_workspace_has_tower_handoffs():
    summary = (
        get_executive_owner_workspace_summary()
    )

    assert summary.tower_handoff_count > 0


def test_gp010_clouds_executes_no_navigation():
    items = (
        get_executive_owner_workspace_items()
    )

    for item in items:
        action = item.navigation_action

        if action is None:
            continue

        assert (
            action.clouds_executes_navigation
            is False
        )

        assert (
            action.downstream_execution_performed
            is False
        )


def test_gp010_no_workspace_execution():
    workspace = (
        get_executive_owner_workspace()
    )

    assert (
        workspace.headline.execution_performed
        is False
    )

    assert (
        workspace.summary.execution_performed
        is False
    )

    for panel in workspace.panels:
        assert panel.execution_performed is False

        for item in panel.items:
            assert item.execution_performed is False


def test_gp010_filter_by_application():
    items = (
        filter_executive_owner_workspace_items(
            source_app_id="observatory"
        )
    )

    assert len(items) >= 3

    assert all(
        item.source_app_id == "observatory"
        for item in items
    )


def test_gp010_filter_by_lane():
    items = (
        filter_executive_owner_workspace_items(
            source_lane_id="investment_engine"
        )
    )

    assert items

    assert all(
        item.source_lane_id
        == "investment_engine"
        for item in items
    )


def test_gp010_filter_internal_navigation():
    items = (
        filter_executive_owner_workspace_items(
            navigation_mode="clouds_internal"
        )
    )

    assert items

    assert all(
        item.navigation_action is not None
        and item.navigation_action.navigation_mode
        == "clouds_internal"
        for item in items
    )


def test_gp010_filter_tower_handoff():
    items = (
        filter_executive_owner_workspace_items(
            navigation_mode="tower_handoff"
        )
    )

    assert items

    assert all(
        item.navigation_action is not None
        and item.navigation_action.navigation_mode
        == "tower_handoff"
        for item in items
    )


def test_gp010_unknown_panel_fails_closed():
    with pytest.raises(KeyError):
        get_executive_owner_workspace_panel(
            "missing-panel"
        )


def test_gp010_unknown_item_fails_closed():
    with pytest.raises(KeyError):
        get_executive_owner_workspace_item(
            "missing-item"
        )


def test_gp010_workspace_payload_is_json_ready():
    payload = (
        get_executive_owner_workspace_payload()
    )

    assert payload["title"] == (
        "Executive Owner Command Workspace"
    )

    assert isinstance(
        payload["panels"],
        list,
    )

    assert len(payload["panels"]) == 6

    assert (
        payload["summary"]
        ["execution_performed"]
        is False
    )


def test_gp010_panel_payload():
    payload = (
        get_executive_owner_workspace_panel_payload(
            "workspace-panel-applications"
        )
    )

    assert payload["kind"] == "applications"
    assert payload["item_count"] == 4


def test_gp010_item_payload():
    payload = (
        get_executive_owner_workspace_item_payload(
            "workspace-now-focus"
        )
    )

    assert payload["source_app_id"] == (
        "observatory"
    )

    assert (
        payload["execution_performed"]
        is False
    )


def test_gp010_prohibited_actions_are_explicit():
    workspace = (
        get_executive_owner_workspace()
    )

    text = " ".join(
        workspace.prohibited_clouds_actions
    ).lower()

    assert "authenticate" in text
    assert "permission" in text
    assert "step-up" in text
    assert "approve" in text
    assert "trade" in text
    assert "move money" in text
    assert "vault" in text


def test_gp010_boundary_notice_is_explicit():
    notice = (
        get_executive_owner_workspace()
        .boundary_notice
        .lower()
    )

    assert "tower" in notice
    assert "authentication" in notice
    assert "permission" in notice
    assert "step-up" in notice
    assert "no operational execution" in notice


def test_gp010_status_is_ready_and_safe():
    status = (
        get_clouds_gp010_status_payload()
    )

    assert status["pack"] == "GP010"

    assert status["section"] == (
        "EXECUTIVE OWNER COMMAND "
        "WORKSPACE SURFACE"
    )

    assert status["status"] == "ready"
    assert status["safe_to_continue"] is True

    assert status["panel_count"] == 6
    assert status["item_count"] == 18

    assert status["readiness_score"] == 42
    assert status["overall_health"] == "blocked"

    assert (
        status["source_integrity_verified"]
        is True
    )

    assert (
        status["tower_boundary_preserved"]
        is True
    )

    assert (
        status["workspace_execution_performed"]
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

    assert status["next_pack"] == (
        "GP011 — EXECUTIVE OWNER WORKSPACE "
        "DETAIL / ACTION INTENT SURFACE"
    )


def test_gp010_no_cross_app_python_imports():
    root = Path(__file__).resolve().parents[2]

    production_files = (
        root
        / "clouds"
        / "executive_owner_workspace.py",
        root
        / "clouds"
        / "executive_owner_workspace_service.py",
    )

    forbidden_roots = {
        "tower",
        "observatory",
        "vault",
        "teller",
        "grounds",
    }

    for path in production_files:
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
                        not in forbidden_roots
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
                    not in forbidden_roots
                )


def test_gp010_workspace_is_repeatable():
    first = (
        get_executive_owner_workspace_payload()
    )

    second = (
        get_executive_owner_workspace_payload()
    )

    assert first == second
