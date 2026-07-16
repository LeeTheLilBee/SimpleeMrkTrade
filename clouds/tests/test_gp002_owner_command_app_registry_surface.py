from pathlib import Path
import ast

import pytest

from clouds.app_registry_surface import (
    AppOpenMode,
    AppRegistryAttentionState,
    AppRegistryGroup,
)
from clouds.app_registry_surface_service import (
    get_app_registry_attention_queue,
    get_app_registry_cards,
    get_app_registry_detail,
    get_app_registry_detail_payload,
    get_app_registry_surface,
    get_app_registry_surface_payload,
    get_clouds_gp002_status_payload,
)


def test_gp002_surface_groups_active_and_reserved_apps():
    surface = get_app_registry_surface()

    assert surface.summary.total_app_count == 6
    assert surface.summary.active_app_count == 4
    assert surface.summary.reserved_app_count == 2

    assert [
        card.app_id
        for card in surface.active_apps
    ] == [
        "tower",
        "observatory",
        "archive_vault",
        "clouds",
    ]

    assert [
        card.app_id
        for card in surface.reserved_apps
    ] == [
        "teller",
        "grounds",
    ]


def test_gp002_surface_summary_counts_connection_states():
    surface = get_app_registry_surface()

    assert surface.summary.connected_app_count == 1
    assert (
        surface.summary.summary_ready_app_count
        == 3
    )

    assert surface.summary.healthy_app_count == 3
    assert surface.summary.watch_app_count == 1
    assert surface.summary.unknown_app_count == 2

    assert (
        surface.summary.owner_execution_performed
        is False
    )


def test_gp002_cards_preserve_tower_handoff_boundary():
    payload = get_app_registry_surface_payload()

    cards = {
        item["app_id"]: item
        for item in payload["all_apps"]
    }

    assert cards["tower"]["open_mode"] == (
        AppOpenMode.TOWER_HANDOFF.value
    )

    assert cards["observatory"]["open_mode"] == (
        AppOpenMode.TOWER_HANDOFF.value
    )

    assert cards["archive_vault"]["open_mode"] == (
        AppOpenMode.TOWER_HANDOFF.value
    )

    assert cards["clouds"]["open_mode"] == (
        AppOpenMode.CLOUDS_INTERNAL.value
    )

    assert (
        "Tower remains responsible"
        in payload["boundary_notice"]
    )


def test_gp002_reserved_cards_are_visible_not_connected():
    cards = get_app_registry_cards(
        group=AppRegistryGroup.RESERVED.value
    )

    assert [
        card.app_id
        for card in cards
    ] == [
        "teller",
        "grounds",
    ]

    for card in cards:
        assert card.group == "reserved"
        assert card.open_label == (
            "View reserved app"
        )


def test_gp002_attention_queue_surfaces_observatory():
    queue = get_app_registry_attention_queue()

    assert [
        card.app_id
        for card in queue
    ] == [
        "observatory",
    ]

    assert queue[0].attention_state == (
        AppRegistryAttentionState.WATCH.value
    )

    assert queue[0].attention_count == 1


def test_gp002_attention_only_filter_is_safe():
    cards = get_app_registry_cards(
        attention_only=True
    )

    assert [
        card.app_id
        for card in cards
    ] == [
        "observatory",
        "teller",
        "grounds",
    ]

    assert all(
        card.attention_state != "clear"
        for card in cards
    )


def test_gp002_detail_projects_capabilities_and_boundaries():
    detail = get_app_registry_detail(
        "observatory"
    )

    assert detail.card.app_id == "observatory"

    assert (
        "Investment intelligence"
        in detail.capabilities
    )

    assert detail.navigation_requires_tower is True

    assert (
        detail.downstream_execution_performed
        is False
    )

    prohibitions = " ".join(
        detail.clouds_prohibitions
    ).lower()

    assert "cannot authenticate" in prohibitions
    assert "cannot perform step-up" in prohibitions
    assert "cannot execute" in prohibitions
    assert "cannot bypass tower" in prohibitions


def test_gp002_clouds_detail_is_internal_navigation():
    detail = get_app_registry_detail(
        "clouds"
    )

    assert (
        detail.navigation_requires_tower
        is False
    )

    assert detail.card.open_mode == (
        AppOpenMode.CLOUDS_INTERNAL.value
    )


def test_gp002_missing_detail_fails_closed():
    with pytest.raises(KeyError):
        get_app_registry_detail(
            "not-a-real-app"
        )


def test_gp002_payload_is_json_ready():
    payload = get_app_registry_detail_payload(
        "archive_vault"
    )

    assert payload["card"]["app_id"] == (
        "archive_vault"
    )

    assert isinstance(
        payload["capabilities"],
        list,
    )

    assert (
        payload["downstream_execution_performed"]
        is False
    )


def test_gp002_status_is_ready_and_safe_to_continue():
    status = get_clouds_gp002_status_payload()

    assert status["pack"] == "GP002"
    assert status["status"] == "ready"
    assert status["safe_to_continue"] is True
    assert status["total_app_count"] == 6
    assert status["active_app_count"] == 4
    assert status["reserved_app_count"] == 2

    assert status["tower_boundary_preserved"] is True
    assert status["direct_app_execution"] is False
    assert status["cross_app_imports_used"] is False

    assert status["next_pack"] == (
        "GP003 — OWNER COMMAND MISSION LANE SURFACE"
    )


def test_gp002_production_has_no_cross_app_imports():
    clouds_root = Path(__file__).resolve().parents[1]

    production_files = [
        clouds_root / "app_registry_surface.py",
        (
            clouds_root
            / "app_registry_surface_service.py"
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
