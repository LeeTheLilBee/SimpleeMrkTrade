from pathlib import Path
import ast

import pytest

from clouds.mission_lane_surface import (
    MissionLaneAttentionState,
    MissionLaneGroup,
    MissionLaneOpenMode,
)
from clouds.mission_lane_surface_service import (
    get_clouds_gp003_status_payload,
    get_mission_lane_attention_queue,
    get_mission_lane_cards,
    get_mission_lane_detail,
    get_mission_lane_detail_payload,
    get_mission_lane_surface,
    get_mission_lane_surface_payload,
)


def test_gp003_surface_groups_active_and_reserved_lanes():
    surface = get_mission_lane_surface()

    assert surface.summary.total_lane_count == 6
    assert surface.summary.active_lane_count == 5
    assert surface.summary.reserved_lane_count == 1

    assert [
        card.lane_id
        for card in surface.active_lanes
    ] == [
        "owner_command",
        "investment_engine",
        "trust_stewardship",
        "atm_operations",
        "real_estate",
    ]

    assert [
        card.lane_id
        for card in surface.reserved_lanes
    ] == [
        "people_and_payments",
    ]


def test_gp003_lane_summary_counts_health_and_readiness():
    summary = get_mission_lane_surface().summary

    assert summary.healthy_lane_count == 2
    assert summary.watch_lane_count == 2
    assert summary.unknown_lane_count == 2
    assert summary.attention_lane_count == 0
    assert summary.blocked_lane_count == 0

    assert summary.building_lane_count == 2
    assert summary.foundation_lane_count == 2
    assert summary.not_started_lane_count == 1
    assert summary.held_lane_count == 1

    assert summary.total_attention_count == 2
    assert (
        summary.clouds_execution_performed
        is False
    )


def test_gp003_cards_show_owning_application():
    payload = get_mission_lane_surface_payload()

    cards = {
        item["lane_id"]: item
        for item in payload["all_lanes"]
    }

    assert cards["investment_engine"][
        "owning_app_id"
    ] == "observatory"

    assert cards["trust_stewardship"][
        "owning_app_id"
    ] == "archive_vault"

    assert cards["atm_operations"][
        "owning_app_id"
    ] == "teller"

    assert cards["real_estate"][
        "owning_app_id"
    ] == "grounds"

    assert cards["owner_command"][
        "owning_app_id"
    ] == "clouds"


def test_gp003_open_modes_preserve_tower_boundary():
    cards = {
        card.lane_id: card
        for card in get_mission_lane_cards()
    }

    assert cards["owner_command"].open_mode == (
        MissionLaneOpenMode.CLOUDS_INTERNAL.value
    )

    for lane_id in (
        "investment_engine",
        "trust_stewardship",
        "atm_operations",
        "real_estate",
        "people_and_payments",
    ):
        assert cards[lane_id].open_mode == (
            MissionLaneOpenMode
            .TOWER_APP_HANDOFF
            .value
        )

    assert (
        cards["investment_engine"]
        .execution_owned_by_clouds
        is False
    )


def test_gp003_reserved_lane_is_visible_not_active():
    cards = get_mission_lane_cards(
        group=MissionLaneGroup.RESERVED.value
    )

    assert len(cards) == 1
    assert cards[0].lane_id == (
        "people_and_payments"
    )
    assert cards[0].active is False
    assert "reserved lane" in (
        cards[0].open_label.lower()
    )


def test_gp003_attention_queue_prioritizes_watch_lanes():
    queue = get_mission_lane_attention_queue()

    assert [
        card.lane_id
        for card in queue
    ] == [
        "investment_engine",
        "atm_operations",
    ]

    assert all(
        card.attention_state
        == MissionLaneAttentionState.WATCH.value
        for card in queue
    )


def test_gp003_attention_only_filter_includes_unknown_lanes():
    cards = get_mission_lane_cards(
        attention_only=True
    )

    assert [
        card.lane_id
        for card in cards
    ] == [
        "investment_engine",
        "atm_operations",
        "real_estate",
        "people_and_payments",
    ]

    assert all(
        card.attention_state != "clear"
        for card in cards
    )


def test_gp003_filters_by_owning_app():
    cards = get_mission_lane_cards(
        owning_app_id="teller"
    )

    assert [
        card.lane_id
        for card in cards
    ] == [
        "atm_operations",
        "people_and_payments",
    ]


def test_gp003_lane_detail_shows_owner_questions():
    detail = get_mission_lane_detail(
        "investment_engine"
    )

    assert detail.card.owning_app_id == (
        "observatory"
    )

    assert detail.navigation_requires_tower is True

    assert len(detail.owner_questions) == 3

    questions = " ".join(
        detail.owner_questions
    ).lower()

    assert "readiness" in questions
    assert "owner review" in questions
    assert "observatory" in questions


def test_gp003_lane_detail_preserves_app_authority():
    detail = get_mission_lane_detail(
        "trust_stewardship"
    )

    assert (
        "Vault is sealed memory"
        in detail.owning_app_authority_boundary
    )

    assert (
        detail.downstream_execution_performed
        is False
    )

    prohibitions = " ".join(
        detail.clouds_prohibitions
    ).lower()

    assert "cannot execute" in prohibitions
    assert "cannot perform tower step-up" in prohibitions
    assert "cannot trade capital" in prohibitions
    assert "cannot move money" in prohibitions
    assert "cannot retrieve raw vault" in prohibitions


def test_gp003_owner_command_lane_is_internal():
    detail = get_mission_lane_detail(
        "owner_command"
    )

    assert (
        detail.navigation_requires_tower
        is False
    )

    assert detail.card.open_mode == (
        MissionLaneOpenMode.CLOUDS_INTERNAL.value
    )


def test_gp003_missing_lane_fails_closed():
    with pytest.raises(KeyError):
        get_mission_lane_detail(
            "missing-lane"
        )


def test_gp003_detail_payload_is_json_ready():
    payload = get_mission_lane_detail_payload(
        "real_estate"
    )

    assert payload["card"]["lane_id"] == (
        "real_estate"
    )

    assert isinstance(
        payload["owner_questions"],
        list,
    )

    assert (
        payload["downstream_execution_performed"]
        is False
    )


def test_gp003_status_is_ready_and_safe_to_continue():
    status = get_clouds_gp003_status_payload()

    assert status["pack"] == "GP003"
    assert status["status"] == "ready"
    assert status["safe_to_continue"] is True

    assert status["total_lane_count"] == 6
    assert status["active_lane_count"] == 5
    assert status["reserved_lane_count"] == 1
    assert status["attention_lane_count"] == 2

    assert (
        status["owning_app_boundaries_visible"]
        is True
    )
    assert status["tower_boundary_preserved"] is True
    assert status["direct_lane_execution"] is False
    assert status["cross_app_imports_used"] is False

    assert status["next_pack"] == (
        "GP004 — OWNER ATTENTION COMMAND SURFACE"
    )


def test_gp003_production_has_no_cross_app_imports():
    clouds_root = Path(__file__).resolve().parents[1]

    production_files = [
        clouds_root / "mission_lane_surface.py",
        (
            clouds_root
            / "mission_lane_surface_service.py"
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

def test_gp003_equal_urgency_uses_owner_display_order():
    queue = get_mission_lane_attention_queue()

    assert [
        card.lane_id
        for card in queue
    ] == [
        "investment_engine",
        "atm_operations",
    ]

    investment = queue[0]
    atm = queue[1]

    assert investment.health == "watch"
    assert atm.health == "watch"

    assert investment.attention_count == 1
    assert atm.attention_count == 1

    assert (
        investment.display_order
        < atm.display_order
    )

