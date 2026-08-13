import ast
from pathlib import Path

import pytest

from clouds.owner_command_preferences_service import (
    get_clouds_gp023_status_payload,
    get_owner_command_preferences,
    get_owner_command_preferences_payload,
    get_owner_command_preferences_surface,
    get_owner_command_preferences_surface_payload,
)


def test_gp023_owner_profile():
    prefs = get_owner_command_preferences()

    assert prefs.owner_id == "owner-primary"


def test_gp023_soulaana_explains_everything():
    prefs = get_owner_command_preferences()

    assert (
        prefs.soulaana_verbosity
        == "explain_everything"
    )


def test_gp023_evidence_on_request():
    prefs = get_owner_command_preferences()

    assert (
        prefs.evidence_disclosure
        == "on_request"
    )


def test_gp023_quiet_cards_collapsed():
    prefs = get_owner_command_preferences()

    assert (
        prefs.quiet_card_behavior
        == "collapsed"
    )

    assert (
        prefs.collapse_quiet_section
        is True
    )


def test_gp023_attention_threshold():
    prefs = get_owner_command_preferences()

    assert (
        prefs.attention_threshold
        == "review_and_action"
    )


def test_gp023_status_chips_visible():
    assert (
        get_owner_command_preferences()
        .show_status_chips
        is True
    )


def test_gp023_why_it_matters_visible():
    assert (
        get_owner_command_preferences()
        .show_why_it_matters
        is True
    )


def test_gp023_next_step_visible():
    assert (
        get_owner_command_preferences()
        .show_owner_next_step
        is True
    )


def test_gp023_tower_preserved():
    prefs = get_owner_command_preferences()

    assert (
        prefs.preserve_tower_handoffs
        is True
    )


def test_gp023_step_up_preserved():
    prefs = get_owner_command_preferences()

    assert (
        prefs.preserve_step_up_requirements
        is True
    )


def test_gp023_downstream_authority_preserved():
    prefs = get_owner_command_preferences()

    assert (
        prefs.preserve_downstream_authority
        is True
    )

    assert (
        prefs.downstream_authority_changed
        is False
    )


def test_gp023_no_execution():
    assert (
        get_owner_command_preferences()
        .execution_performed
        is False
    )


def test_gp023_unknown_owner_fails_closed():
    with pytest.raises(KeyError):
        get_owner_command_preferences(
            "unknown-owner"
        )


def test_gp023_payload():
    payload = (
        get_owner_command_preferences_payload()
    )

    assert (
        payload["soulaana_verbosity"]
        == "explain_everything"
    )


def test_gp023_surface():
    surface = (
        get_owner_command_preferences_surface()
    )

    assert surface.presentation_only is True
    assert (
        surface.tower_boundary_preserved
        is True
    )

    assert (
        surface.downstream_authority_preserved
        is True
    )


def test_gp023_surface_payload():
    payload = (
        get_owner_command_preferences_surface_payload()
    )

    assert (
        payload["presentation_only"]
        is True
    )


def test_gp023_status():
    status = (
        get_clouds_gp023_status_payload()
    )

    assert status["pack"] == "GP023"
    assert status["status"] == "ready"
    assert status["safe_to_continue"] is True

    assert (
        status["soulaana_verbosity"]
        == "explain_everything"
    )

    assert (
        status["presentation_only"]
        is True
    )

    assert (
        status["tower_boundary_preserved"]
        is True
    )

    assert (
        status["step_up_requirements_preserved"]
        is True
    )

    assert (
        status["downstream_authority_changed"]
        is False
    )


def test_gp023_no_cross_app_imports():
    root = Path(__file__).resolve().parents[2]

    files = (
        root / "clouds" / "owner_command_preferences.py",
        root / "clouds" / "owner_command_preferences_service.py",
    )

    forbidden = {
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
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert (
                        alias.name.split(".")[0].lower()
                        not in forbidden
                    )

            if isinstance(node, ast.ImportFrom):
                module = node.module or ""

                assert (
                    module.lstrip(".")
                    .split(".")[0]
                    .lower()
                    not in forbidden
                )
