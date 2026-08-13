import ast
from pathlib import Path

import pytest

from clouds.operating_data_adapter_service import (
    get_clouds_gp018_status_payload,
    get_operating_adapter_surface,
    get_operating_adapter_surface_payload,
    get_operating_summaries,
    get_operating_summary,
    get_operating_summary_payload,
)


EXPECTED = (
    "observatory",
    "tower",
    "teller",
    "grounds",
    "archive_vault",
    "atm_operations",
)


def test_gp018_six_sources():
    summaries = get_operating_summaries()

    assert tuple(
        item.source_id
        for item in summaries
    ) == EXPECTED


def test_gp018_sources_are_unique():
    ids = [
        item.source_id
        for item in get_operating_summaries()
    ]

    assert len(ids) == len(set(ids))


def test_gp018_all_are_approved_projections():
    assert all(
        item.approved_summary_projection
        is True
        for item in get_operating_summaries()
    )


def test_gp018_no_live_feeds_claimed():
    assert all(
        item.live_feed_connected
        is False
        for item in get_operating_summaries()
    )


def test_gp018_source_integrity():
    assert all(
        item.source_integrity_verified
        is True
        for item in get_operating_summaries()
    )


def test_gp018_no_execution():
    assert all(
        item.downstream_execution_performed
        is False
        for item in get_operating_summaries()
    )


def test_gp018_every_source_explains_itself():
    for item in get_operating_summaries():
        assert item.headline
        assert item.explanation
        assert item.owner_message
        assert item.metrics


def test_gp018_observatory_requires_attention():
    item = get_operating_summary(
        "observatory"
    )

    assert item.health == "attention"
    assert item.attention == "action_required"


def test_gp018_tower_is_authority_boundary():
    item = get_operating_summary(
        "tower"
    )

    assert "authority" in (
        item.headline.lower()
    )


def test_gp018_unknown_source_fails_closed():
    with pytest.raises(KeyError):
        get_operating_summary("missing")


def test_gp018_payload():
    payload = get_operating_summary_payload(
        "observatory"
    )

    assert payload["source_id"] == "observatory"


def test_gp018_surface():
    surface = get_operating_adapter_surface()

    assert surface.source_count == 6
    assert surface.live_source_count == 0
    assert surface.projected_source_count == 6


def test_gp018_surface_payload():
    payload = (
        get_operating_adapter_surface_payload()
    )

    assert payload["source_count"] == 6
    assert len(payload["summaries"]) == 6


def test_gp018_status():
    status = get_clouds_gp018_status_payload()

    assert status["pack"] == "GP018"
    assert status["status"] == "ready"
    assert status["safe_to_continue"] is True
    assert status["source_count"] == 6
    assert status["live_source_count"] == 0
    assert status["projected_source_count"] == 6


def test_gp018_no_cross_app_imports():
    root = Path(__file__).resolve().parents[2]

    files = (
        root / "clouds" / "operating_data_adapter.py",
        root / "clouds" / "operating_data_adapter_service.py",
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
