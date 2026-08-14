import ast
from pathlib import Path

import pytest

from clouds.owner_command_experience_service import (
    filter_owner_command_experience_cards,
    get_clouds_gp021_status_payload,
    get_owner_command_card,
    get_owner_command_cards,
    get_owner_command_experience,
    get_owner_command_experience_payload,
    get_owner_command_sections,
)


def test_gp021_six_cards():
    assert len(
        get_owner_command_cards()
    ) == 6


def test_gp021_four_sections():
    assert len(
        get_owner_command_sections()
    ) == 4


def test_gp021_soulaana_leads():
    experience = (
        get_owner_command_experience()
    )

    assert experience.hero.headline
    assert experience.hero.explanation
    assert (
        experience.hero.top_focus_source_id
        == "observatory"
    )


def test_gp021_needs_you_count():
    experience = (
        get_owner_command_experience()
    )

    assert (
        experience.hero.needs_you_count
        == 1
    )


def test_gp021_watch_count():
    experience = (
        get_owner_command_experience()
    )

    assert (
        experience.hero.watching_count
        == 1
    )


def test_gp021_quiet_count():
    experience = (
        get_owner_command_experience()
    )

    assert (
        experience.hero.quiet_count
        == 4
    )


def test_gp021_observatory_is_needs_you():
    card = get_owner_command_card(
        "observatory"
    )

    assert card.section_kind == (
        "needs_you"
    )

    assert card.state == "action"


def test_gp021_atm_is_watching():
    card = get_owner_command_card(
        "atm_operations"
    )

    assert card.section_kind == (
        "watching"
    )

    assert card.state == "watch"


def test_gp021_cards_have_soulaana_message():
    for card in get_owner_command_cards():
        assert card.soulaana_message
        assert card.why_it_matters
        assert card.what_needs_attention
        assert card.what_can_wait
        assert card.owner_next_step


def test_gp021_cards_have_three_chips():
    for card in get_owner_command_cards():
        assert len(card.chips) == 3


def test_gp021_proof_page_not_primary():
    assert (
        get_owner_command_experience()
        .proof_page_primary_experience
        is False
    )


def test_gp021_evidence_hidden():
    assert (
        get_owner_command_experience()
        .evidence_hidden_by_default
        is True
    )


def test_gp021_progressive_disclosure():
    assert (
        get_owner_command_experience()
        .progressive_disclosure_enabled
        is True
    )


def test_gp021_tower_handoff_cards():
    cards = (
        filter_owner_command_experience_cards(
            requires_tower=True
        )
    )

    assert len(cards) == 5

    assert all(
        item.navigation.kind
        == "tower_handoff"
        for item in cards
    )


def test_gp021_clouds_internal_atm():
    card = get_owner_command_card(
        "atm_operations"
    )

    assert (
        card.navigation.kind
        == "clouds_internal"
    )

    assert (
        card.navigation.requires_tower
        is False
    )


def test_gp021_no_navigation_execution():
    for card in get_owner_command_cards():
        assert (
            card.navigation
            .clouds_executes_navigation
            is False
        )

        assert (
            card.navigation
            .downstream_execution_performed
            is False
        )


def test_gp021_unknown_source_fails_closed():
    with pytest.raises(KeyError):
        get_owner_command_card(
            "missing"
        )


def test_gp021_payload():
    payload = (
        get_owner_command_experience_payload()
    )

    assert payload["card_count"] == 6
    assert payload["section_count"] == 4


def test_gp021_status():
    status = (
        get_clouds_gp021_status_payload()
    )

    assert status["pack"] == "GP021"
    assert status["status"] == "ready"
    assert status["safe_to_continue"] is True

    assert status["section_count"] == 4
    assert status["card_count"] == 6
    assert status["needs_you_count"] == 1
    assert status["watching_count"] == 1
    assert status["quiet_count"] == 4

    assert status["soulaana_leads"] is True

    assert (
        status["proof_page_primary_experience"]
        is False
    )

    assert (
        status["evidence_hidden_by_default"]
        is True
    )


def test_gp021_no_cross_app_imports():
    root = Path(__file__).resolve().parents[2]

    production_files = (
        root / "clouds" / "owner_command_experience.py",
        root / "clouds" / "owner_command_experience_service.py",
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
