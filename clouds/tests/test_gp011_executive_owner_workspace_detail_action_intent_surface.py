import ast
from pathlib import Path

import pytest

from clouds.executive_owner_workspace_detail import (
    OwnerActionIntentAuthority,
    OwnerActionIntentKind,
    OwnerActionIntentState,
)

from clouds.executive_owner_workspace_detail_service import (
    filter_executive_owner_workspace_details,
    get_clouds_gp011_status_payload,
    get_executive_owner_workspace_detail,
    get_executive_owner_workspace_detail_payload,
    get_executive_owner_workspace_detail_surface,
    get_executive_owner_workspace_detail_surface_payload,
    get_executive_owner_workspace_details,
)


def test_gp011_has_18_details():
    details = (
        get_executive_owner_workspace_details()
    )

    assert len(details) == 18


def test_gp011_detail_ids_are_unique():
    details = (
        get_executive_owner_workspace_details()
    )

    ids = [
        detail.item_id
        for detail in details
    ]

    assert len(ids) == len(set(ids))


def test_gp011_focus_detail_explains_meaning():
    detail = (
        get_executive_owner_workspace_detail(
            "workspace-now-focus"
        )
    )

    assert (
        "immediate focus"
        in detail.what_it_means.lower()
    )

    assert (
        "review"
        in detail.what_to_do_now.lower()
        or "tower"
        in detail.what_to_do_now.lower()
    )


def test_gp011_focus_intent_requires_tower():
    detail = (
        get_executive_owner_workspace_detail(
            "workspace-now-focus"
        )
    )

    intent = detail.action_intent

    assert intent.kind == (
        OwnerActionIntentKind
        .REQUEST_TOWER_HANDOFF.value
    )

    assert intent.state == (
        OwnerActionIntentState
        .TOWER_REQUIRED.value
    )

    assert intent.requires_tower is True

    assert intent.authority == (
        OwnerActionIntentAuthority
        .TOWER.value
    )

    assert intent.clouds_can_execute is False
    assert intent.approval_performed is False
    assert intent.execution_performed is False


def test_gp011_internal_section_intent_stays_in_clouds():
    detail = (
        get_executive_owner_workspace_detail(
            "workspace-section-today"
        )
    )

    intent = detail.action_intent

    assert intent.kind == "open_clouds"
    assert intent.state == "available"
    assert intent.requires_tower is False
    assert intent.navigation_mode == "clouds_internal"
    assert intent.authority == "clouds"


def test_gp011_application_destination_requires_tower():
    detail = (
        get_executive_owner_workspace_detail(
            "workspace-app-tower-observatory"
        )
    )

    intent = detail.action_intent

    assert intent.requires_tower is True
    assert intent.requires_owner_permission is True
    assert intent.requires_step_up is True
    assert intent.navigation_mode == "tower_handoff"


def test_gp011_every_detail_has_prerequisites():
    for detail in (
        get_executive_owner_workspace_details()
    ):
        assert detail.prerequisites


def test_gp011_tower_items_have_tower_prerequisite():
    details = (
        filter_executive_owner_workspace_details(
            requires_tower=True
        )
    )

    assert details

    for detail in details:
        labels = {
            item.label
            for item in detail.prerequisites
        }

        assert "Tower mediation required" in labels


def test_gp011_blocked_item_has_blocker():
    details = (
        filter_executive_owner_workspace_details(
            health="blocked"
        )
    )

    assert details

    assert any(
        detail.blockers
        for detail in details
    )


def test_gp011_blockers_are_not_resolvable_in_clouds():
    for detail in (
        get_executive_owner_workspace_details()
    ):
        for blocker in detail.blockers:
            assert (
                blocker.resolvable_in_clouds
                is False
            )


def test_gp011_every_detail_has_owner_questions():
    for detail in (
        get_executive_owner_workspace_details()
    ):
        assert len(
            detail.owner_questions
        ) >= 3


def test_gp011_every_detail_explains_what_can_wait():
    for detail in (
        get_executive_owner_workspace_details()
    ):
        assert detail.what_can_wait


def test_gp011_no_detail_executes():
    for detail in (
        get_executive_owner_workspace_details()
    ):
        assert (
            detail.downstream_execution_performed
            is False
        )

        assert (
            detail.action_intent
            .clouds_can_execute
            is False
        )

        assert (
            detail.action_intent
            .approval_performed
            is False
        )

        assert (
            detail.action_intent
            .execution_performed
            is False
        )


def test_gp011_filter_by_app():
    details = (
        filter_executive_owner_workspace_details(
            source_app_id="observatory"
        )
    )

    assert details

    assert all(
        detail.source_app_id == "observatory"
        for detail in details
    )


def test_gp011_filter_by_lane():
    details = (
        filter_executive_owner_workspace_details(
            source_lane_id="investment_engine"
        )
    )

    assert details

    assert all(
        detail.source_lane_id
        == "investment_engine"
        for detail in details
    )


def test_gp011_filter_by_intent_kind():
    details = (
        filter_executive_owner_workspace_details(
            intent_kind="request_tower_handoff"
        )
    )

    assert details

    assert all(
        detail.action_intent.kind
        == "request_tower_handoff"
        for detail in details
    )


def test_gp011_filter_by_intent_state():
    details = (
        filter_executive_owner_workspace_details(
            intent_state="tower_required"
        )
    )

    assert details

    assert all(
        detail.action_intent.state
        == "tower_required"
        for detail in details
    )


def test_gp011_unknown_detail_fails_closed():
    with pytest.raises(KeyError):
        get_executive_owner_workspace_detail(
            "missing-detail"
        )


def test_gp011_detail_payload_is_json_ready():
    payload = (
        get_executive_owner_workspace_detail_payload(
            "workspace-now-focus"
        )
    )

    assert payload["item_id"] == (
        "workspace-now-focus"
    )

    assert isinstance(
        payload["prerequisites"],
        list,
    )

    assert isinstance(
        payload["blockers"],
        list,
    )

    assert isinstance(
        payload["owner_questions"],
        list,
    )

    assert (
        payload["action_intent"]
        ["execution_performed"]
        is False
    )


def test_gp011_surface_payload_is_json_ready():
    payload = (
        get_executive_owner_workspace_detail_surface_payload()
    )

    assert len(
        payload["details"]
    ) == 18

    assert (
        "descriptive only"
        in payload["boundary_notice"].lower()
    )


def test_gp011_prohibited_actions_are_explicit():
    surface = (
        get_executive_owner_workspace_detail_surface()
    )

    text = " ".join(
        surface.details[0]
        .prohibited_clouds_actions
    ).lower()

    assert "authenticate" in text
    assert "permission" in text
    assert "step-up" in text
    assert "approve" in text
    assert "execute" in text
    assert "trade" in text
    assert "move money" in text
    assert "vault" in text


def test_gp011_status_is_ready_and_safe():
    status = (
        get_clouds_gp011_status_payload()
    )

    assert status["pack"] == "GP011"

    assert status["section"] == (
        "EXECUTIVE OWNER WORKSPACE DETAIL "
        "/ ACTION INTENT SURFACE"
    )

    assert status["status"] == "ready"
    assert status["safe_to_continue"] is True

    assert status["detail_count"] == 18

    assert (
        status["tower_intent_count"]
        > 0
    )

    assert (
        status["internal_intent_count"]
        > 0
    )

    assert (
        status["source_integrity_verified"]
        is True
    )

    assert (
        status["tower_boundary_preserved"]
        is True
    )

    assert status["approval_performed"] is False

    assert (
        status["intent_execution_performed"]
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
        "GP012 — EXECUTIVE OWNER ACTION INTENT "
        "REVIEW / HANDOFF PREPARATION SURFACE"
    )


def test_gp011_no_cross_app_python_imports():
    root = Path(__file__).resolve().parents[2]

    production_files = (
        root
        / "clouds"
        / "executive_owner_workspace_detail.py",
        root
        / "clouds"
        / "executive_owner_workspace_detail_service.py",
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


def test_gp011_surface_is_repeatable():
    first = (
        get_executive_owner_workspace_detail_surface_payload()
    )

    second = (
        get_executive_owner_workspace_detail_surface_payload()
    )

    assert first == second
