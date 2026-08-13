import ast
from pathlib import Path

import pytest

from clouds.owner_command_detail_drawers_service import (
    filter_owner_command_detail_experiences,
    get_clouds_gp022_status_payload,
    get_guided_attention_surface,
    get_guided_attention_surface_payload,
    get_owner_command_detail_experience,
    get_owner_command_detail_experiences,
)


def test_gp022_six_experiences():
    assert len(
        get_owner_command_detail_experiences()
    ) == 6


def test_gp022_seven_drawers_each():
    for item in (
        get_owner_command_detail_experiences()
    ):
        assert item.drawer_count == 7


def test_gp022_drawer_kinds_complete():
    expected = {
        "explanation",
        "why_it_matters",
        "current_state",
        "can_wait",
        "next_step",
        "status_details",
        "evidence",
    }

    for item in (
        get_owner_command_detail_experiences()
    ):
        assert {
            drawer.kind
            for drawer in item.drawers
        } == expected


def test_gp022_soulaana_explanation_first():
    for item in (
        get_owner_command_detail_experiences()
    ):
        assert (
            item.drawers[0].kind
            == "explanation"
        )


def test_gp022_evidence_last():
    for item in (
        get_owner_command_detail_experiences()
    ):
        assert (
            item.drawers[-1].kind
            == "evidence"
        )

        assert (
            item.drawers[-1].technical
            is True
        )


def test_gp022_evidence_hidden():
    surface = (
        get_guided_attention_surface()
    )

    assert (
        surface.evidence_hidden_by_default
        is True
    )


def test_gp022_observatory_review_now():
    item = (
        get_owner_command_detail_experience(
            "observatory"
        )
    )

    actions = {
        step.action
        for step in item.guided_steps
    }

    assert "review_now" in actions


def test_gp022_atm_keep_watching():
    item = (
        get_owner_command_detail_experience(
            "atm_operations"
        )
    )

    actions = {
        step.action
        for step in item.guided_steps
    }

    assert "keep_watching" in actions
    assert "snooze" in actions


def test_gp022_quiet_sources_no_action():
    surface = (
        get_guided_attention_surface()
    )

    assert len(
        surface.quiet_source_ids
    ) == 4

    for source_id in (
        surface.quiet_source_ids
    ):
        item = (
            get_owner_command_detail_experience(
                source_id
            )
        )

        actions = {
            step.action
            for step in item.guided_steps
        }

        assert "no_action" in actions


def test_gp022_snooze_does_not_mutate():
    experiences = (
        filter_owner_command_detail_experiences(
            action="snooze"
        )
    )

    assert experiences

    for item in experiences:
        for step in item.guided_steps:
            if step.action == "snooze":
                assert (
                    step.mutates_persistent_state
                    is False
                )


def test_gp022_dismiss_does_not_mutate():
    experiences = (
        filter_owner_command_detail_experiences(
            action="dismiss_informational"
        )
    )

    assert experiences

    for item in experiences:
        for step in item.guided_steps:
            if (
                step.action
                == "dismiss_informational"
            ):
                assert (
                    step.mutates_persistent_state
                    is False
                )


def test_gp022_no_drawer_execution():
    for item in (
        get_owner_command_detail_experiences()
    ):
        assert all(
            drawer.execution_performed
            is False
            for drawer in item.drawers
        )


def test_gp022_no_guided_execution():
    for item in (
        get_owner_command_detail_experiences()
    ):
        assert all(
            step.executes_downstream_action
            is False
            for step in item.guided_steps
        )


def test_gp022_no_persistence_mutation():
    surface = (
        get_guided_attention_surface()
    )

    assert (
        surface.persistent_state_mutated
        is False
    )


def test_gp022_primary_focus_observatory():
    assert (
        get_guided_attention_surface()
        .primary_attention_source_id
        == "observatory"
    )


def test_gp022_watch_atm():
    assert (
        get_guided_attention_surface()
        .watch_source_ids
        == ("atm_operations",)
    )


def test_gp022_filter_evidence():
    experiences = (
        filter_owner_command_detail_experiences(
            drawer_kind="evidence"
        )
    )

    assert len(experiences) == 6


def test_gp022_unknown_fails_closed():
    with pytest.raises(KeyError):
        get_owner_command_detail_experience(
            "missing"
        )


def test_gp022_payload():
    payload = (
        get_guided_attention_surface_payload()
    )

    assert payload["source_count"] == 6

    assert (
        payload[
            "primary_attention_source_id"
        ]
        == "observatory"
    )


def test_gp022_status():
    status = (
        get_clouds_gp022_status_payload()
    )

    assert status["pack"] == "GP022"
    assert status["status"] == "ready"
    assert status["safe_to_continue"] is True

    assert status["source_count"] == 6

    assert (
        status["drawer_count_per_source"]
        == 7
    )

    assert (
        status["primary_attention_source"]
        == "observatory"
    )

    assert (
        status["watch_source_ids"]
        == ("atm_operations",)
    )

    assert (
        status["quiet_source_count"]
        == 4
    )

    assert (
        status["persistent_state_mutated"]
        is False
    )

    assert (
        status["downstream_execution_performed"]
        is False
    )


def test_gp022_no_cross_app_imports():
    root = Path(__file__).resolve().parents[2]

    production_files = (
        root / "clouds" / "owner_command_detail_drawers.py",
        root / "clouds" / "owner_command_detail_drawers_service.py",
    )

    forbidden = {
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
                    assert (
                        alias.name
                        .split(".")[0]
                        .lower()
                        not in forbidden
                    )

            if isinstance(
                node,
                ast.ImportFrom,
            ):
                module = (
                    node.module
                    or ""
                )

                assert (
                    module
                    .lstrip(".")
                    .split(".")[0]
                    .lower()
                    not in forbidden
                )
