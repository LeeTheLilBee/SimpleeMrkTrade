from pathlib import Path
import ast

import pytest

from clouds.today_surface import (
    TodayCardKind,
    TodayNavigationMode,
)
from clouds.today_surface_service import (
    get_clouds_gp005_status_payload,
    get_today_cards,
    get_today_detail,
    get_today_detail_payload,
    get_today_queue,
    get_today_surface,
    get_today_surface_payload,
)


def test_gp005_today_surface_has_expected_sections():
    surface = get_today_surface()

    assert surface.header.title == "Today"
    assert surface.header.focus_count == 1
    assert surface.header.watch_count == 1
    assert surface.header.target_count == 3

    assert len(surface.all_cards) == 5


def test_gp005_focus_contains_observatory_review():
    surface = get_today_surface()

    assert [
        card.card_id
        for card in surface.focus
    ] == [
        (
            "today-focus-"
            "clouds-attention-ob-readiness"
        ),
    ]

    card = surface.focus[0]

    assert card.source_app_id == "observatory"
    assert card.source_lane_id == (
        "investment_engine"
    )
    assert card.action_required is True
    assert card.priority == "high"


def test_gp005_watch_contains_atm_planning():
    surface = get_today_surface()

    assert [
        card.card_id
        for card in surface.watch
    ] == [
        (
            "today-watch-"
            "clouds-attention-atm-planning"
        ),
    ]

    card = surface.watch[0]

    assert card.source_app_id == "teller"
    assert card.source_lane_id == (
        "atm_operations"
    )
    assert card.action_required is False
    assert card.priority == "elevated"


def test_gp005_targets_include_reserved_apps_and_lane():
    targets = get_today_surface().targets

    assert [
        card.card_id
        for card in targets
    ] == [
        "today-target-app-teller",
        "today-target-app-grounds",
        (
            "today-target-lane-"
            "people_and_payments"
        ),
    ]


def test_gp005_header_reflects_owner_focus():
    header = get_today_surface().header

    assert header.action_required_count == 1
    assert header.overall_state == "focus"
    assert header.execution_performed is False


def test_gp005_all_cards_have_unique_ids():
    cards = get_today_cards()

    identifiers = [
        card.card_id
        for card in cards
    ]

    assert len(identifiers) == len(
        set(identifiers)
    )


def test_gp005_cards_are_deterministically_ordered():
    cards = get_today_cards()

    assert [
        card.card_id
        for card in cards
    ] == [
        (
            "today-focus-"
            "clouds-attention-ob-readiness"
        ),
        (
            "today-watch-"
            "clouds-attention-atm-planning"
        ),
        "today-target-app-teller",
        "today-target-app-grounds",
        (
            "today-target-lane-"
            "people_and_payments"
        ),
    ]


def test_gp005_focus_uses_tower_handoff():
    card = get_today_surface().focus[0]

    assert card.navigation_mode == (
        TodayNavigationMode
        .TOWER_HANDOFF
        .value
    )

    assert card.open_route == (
        "/tower/observatory"
    )

    assert card.execution_performed is False


def test_gp005_queue_filters_by_kind():
    cards = get_today_queue(
        kind=TodayCardKind.TARGET.value
    )

    assert len(cards) == 3

    assert all(
        card.kind == "target"
        for card in cards
    )


def test_gp005_queue_filters_by_app():
    cards = get_today_queue(
        source_app_id="teller"
    )

    assert [
        card.card_id
        for card in cards
    ] == [
        (
            "today-watch-"
            "clouds-attention-atm-planning"
        ),
        "today-target-app-teller",
        (
            "today-target-lane-"
            "people_and_payments"
        ),
    ]


def test_gp005_queue_filters_action_required():
    cards = get_today_queue(
        action_required=True
    )

    assert len(cards) == 1

    assert cards[0].card_id == (
        "today-focus-"
        "clouds-attention-ob-readiness"
    )


def test_gp005_detail_has_owner_questions():
    detail = get_today_detail(
        "today-focus-"
        "clouds-attention-ob-readiness"
    )

    assert len(detail.owner_questions) == 3

    questions = " ".join(
        detail.owner_questions
    ).lower()

    assert "owner attention" in questions
    assert "decision or review" in questions
    assert "operating app" in questions


def test_gp005_detail_preserves_nonexecution_boundary():
    detail = get_today_detail(
        "today-watch-"
        "clouds-attention-atm-planning"
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


def test_gp005_missing_card_fails_closed():
    with pytest.raises(KeyError):
        get_today_detail(
            "missing-today-card"
        )


def test_gp005_payloads_are_json_ready():
    surface_payload = (
        get_today_surface_payload()
    )

    detail_payload = (
        get_today_detail_payload(
            "today-target-app-grounds"
        )
    )

    assert isinstance(
        surface_payload["all_cards"],
        list,
    )

    assert detail_payload["card"][
        "source_app_id"
    ] == "grounds"

    assert (
        detail_payload[
            "downstream_execution_performed"
        ]
        is False
    )


def test_gp005_status_is_ready_and_safe():
    status = get_clouds_gp005_status_payload()

    assert status["pack"] == "GP005"
    assert status["status"] == "ready"
    assert status["safe_to_continue"] is True

    assert status["focus_count"] == 1
    assert status["watch_count"] == 1
    assert status["target_count"] == 3
    assert status["action_required_count"] == 1

    assert (
        status["source_integrity_verified"]
        is True
    )

    assert status["tower_boundary_preserved"] is True
    assert status["today_execution_performed"] is False
    assert status["cross_app_imports_used"] is False

    assert status["next_pack"] == (
        "GP006 — OWNER COMMAND PRIORITY BOARD"
    )


def test_gp005_production_has_no_cross_app_imports():
    clouds_root = Path(__file__).resolve().parents[1]

    production_files = [
        clouds_root / "today_surface.py",
        clouds_root / "today_surface_service.py",
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

def test_gp005_equal_priority_targets_use_owner_order():
    targets = get_today_surface().targets

    assert [
        card.card_id
        for card in targets
    ] == [
        "today-target-app-teller",
        "today-target-app-grounds",
        "today-target-lane-people_and_payments",
    ]

    assert all(
        card.kind == "target"
        for card in targets
    )

    assert all(
        card.priority == "routine"
        for card in targets
    )

    assert all(
        card.action_required is False
        for card in targets
    )

