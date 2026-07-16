from pathlib import Path
import ast

import pytest

from clouds.owner_attention_surface import (
    AttentionCommandGroup,
    AttentionNavigationMode,
    AttentionSourceType,
)
from clouds.owner_attention_surface_service import (
    get_clouds_gp004_status_payload,
    get_owner_attention_commands,
    get_owner_attention_detail,
    get_owner_attention_detail_payload,
    get_owner_attention_queue,
    get_owner_attention_surface,
    get_owner_attention_surface_payload,
)


def test_gp004_unifies_owner_attention_without_duplicates():
    commands = get_owner_attention_commands()

    identifiers = [
        item.attention_id
        for item in commands
    ]

    assert len(identifiers) == len(
        set(identifiers)
    )

    assert [
        item.attention_id
        for item in commands
    ] == [
        "clouds-attention-ob-readiness",
        "clouds-attention-atm-planning",
    ]


def test_gp004_surface_groups_action_and_information():
    surface = get_owner_attention_surface()

    assert surface.summary.total_attention_count == 2
    assert surface.summary.action_required_count == 1
    assert surface.summary.informational_count == 1

    assert [
        item.attention_id
        for item in surface.action_required
    ] == [
        "clouds-attention-ob-readiness",
    ]

    assert [
        item.attention_id
        for item in surface.informational
    ] == [
        "clouds-attention-atm-planning",
    ]


def test_gp004_priority_summary_is_correct():
    summary = get_owner_attention_surface().summary

    assert summary.critical_count == 0
    assert summary.high_count == 1
    assert summary.elevated_count == 1
    assert summary.routine_count == 0

    assert (
        summary.source_integrity_verified
        is True
    )

    assert summary.execution_performed is False


def test_gp004_source_counts_are_owner_records():
    summary = get_owner_attention_surface().summary

    assert summary.owner_record_source_count == 2
    assert summary.application_source_count == 0
    assert summary.mission_lane_source_count == 0


def test_gp004_observatory_attention_has_verified_links():
    command = get_owner_attention_detail(
        "clouds-attention-ob-readiness"
    ).command

    assert command.source_type == (
        AttentionSourceType.OWNER_RECORD.value
    )

    assert command.source_app_id == "observatory"
    assert (
        command.source_app_name
        == "The Observatory"
    )

    assert command.source_lane_id == (
        "investment_engine"
    )

    assert command.source_lane_name == (
        "Investment Engine"
    )

    assert (
        command.source_integrity_verified
        is True
    )


def test_gp004_action_item_uses_tower_handoff():
    command = get_owner_attention_detail(
        "clouds-attention-ob-readiness"
    ).command

    assert command.command_group == (
        AttentionCommandGroup
        .ACTION_REQUIRED
        .value
    )

    assert command.action_required is True

    assert command.navigation_mode == (
        AttentionNavigationMode
        .TOWER_HANDOFF
        .value
    )

    assert command.open_route == (
        "/tower/observatory"
    )

    assert command.execution_performed is False


def test_gp004_informational_item_remains_nonexecuting():
    command = get_owner_attention_detail(
        "clouds-attention-atm-planning"
    ).command

    assert command.command_group == (
        AttentionCommandGroup
        .INFORMATIONAL
        .value
    )

    assert command.action_required is False

    assert command.owner_action_label == (
        "View information"
    )

    assert command.execution_performed is False


def test_gp004_queue_filters_by_action_required():
    queue = get_owner_attention_queue(
        action_required=True
    )

    assert [
        item.attention_id
        for item in queue
    ] == [
        "clouds-attention-ob-readiness",
    ]


def test_gp004_queue_filters_by_app_and_lane():
    app_queue = get_owner_attention_queue(
        source_app_id="teller"
    )

    lane_queue = get_owner_attention_queue(
        source_lane_id="atm_operations"
    )

    assert [
        item.attention_id
        for item in app_queue
    ] == [
        "clouds-attention-atm-planning",
    ]

    assert [
        item.attention_id
        for item in lane_queue
    ] == [
        "clouds-attention-atm-planning",
    ]


def test_gp004_queue_filters_by_priority():
    queue = get_owner_attention_queue(
        priority="high"
    )

    assert [
        item.attention_id
        for item in queue
    ] == [
        "clouds-attention-ob-readiness",
    ]


def test_gp004_detail_contains_owner_questions():
    detail = get_owner_attention_detail(
        "clouds-attention-ob-readiness"
    )

    assert len(detail.owner_questions) == 3

    questions = " ".join(
        detail.owner_questions
    ).lower()

    assert "review" in questions
    assert "source application" in questions
    assert "direction" in questions


def test_gp004_detail_preserves_authority_boundary():
    detail = get_owner_attention_detail(
        "clouds-attention-ob-readiness"
    )

    assert (
        "Observatory alone owns trading"
        in detail.owning_app_authority_boundary
    )

    prohibitions = " ".join(
        detail.prohibited_clouds_actions
    ).lower()

    assert "cannot approve" in prohibitions
    assert "cannot execute" in prohibitions
    assert "cannot perform tower step-up" in prohibitions
    assert "cannot trade capital" in prohibitions
    assert "cannot move money" in prohibitions

    assert (
        detail.downstream_execution_performed
        is False
    )


def test_gp004_missing_attention_fails_closed():
    with pytest.raises(KeyError):
        get_owner_attention_detail(
            "missing-attention"
        )


def test_gp004_payloads_are_json_ready():
    surface_payload = (
        get_owner_attention_surface_payload()
    )

    detail_payload = (
        get_owner_attention_detail_payload(
            "clouds-attention-atm-planning"
        )
    )

    assert isinstance(
        surface_payload["all_attention"],
        list,
    )

    assert detail_payload["command"][
        "attention_id"
    ] == "clouds-attention-atm-planning"

    assert (
        detail_payload[
            "downstream_execution_performed"
        ]
        is False
    )


def test_gp004_status_is_ready_and_safe_to_continue():
    status = get_clouds_gp004_status_payload()

    assert status["pack"] == "GP004"
    assert status["status"] == "ready"
    assert status["safe_to_continue"] is True

    assert status["total_attention_count"] == 2
    assert status["action_required_count"] == 1
    assert status["informational_count"] == 1

    assert (
        status["source_integrity_verified"]
        is True
    )

    assert status["tower_boundary_preserved"] is True

    assert (
        status["attention_execution_performed"]
        is False
    )

    assert status["cross_app_imports_used"] is False

    assert status["next_pack"] == (
        "GP005 — OWNER COMMAND TODAY SURFACE"
    )


def test_gp004_production_has_no_cross_app_imports():
    clouds_root = Path(__file__).resolve().parents[1]

    production_files = [
        clouds_root / "owner_attention_surface.py",
        (
            clouds_root
            / "owner_attention_surface_service.py"
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
