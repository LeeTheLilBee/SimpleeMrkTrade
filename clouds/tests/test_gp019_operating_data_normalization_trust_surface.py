import ast
from pathlib import Path

import pytest

from clouds.operating_data_trust_service import (
    get_clouds_gp019_status_payload,
    get_operating_trust_record,
    get_operating_trust_records,
    get_operating_trust_surface,
    get_operating_trust_surface_payload,
)


def test_gp019_six_sources():
    assert len(
        get_operating_trust_records()
    ) == 6


def test_gp019_all_normalized():
    assert all(
        item.normalization_state
        == "normalized"
        for item in get_operating_trust_records()
    )


def test_gp019_all_trusted_projection():
    assert all(
        item.trust_state
        == "trusted_projection"
        for item in get_operating_trust_records()
    )


def test_gp019_confidence():
    assert all(
        item.confidence_score == 100
        for item in get_operating_trust_records()
    )


def test_gp019_projection_freshness():
    assert all(
        item.freshness_score == 60
        for item in get_operating_trust_records()
    )


def test_gp019_no_live_claim():
    assert all(
        item.live_feed_connected is False
        for item in get_operating_trust_records()
    )


def test_gp019_owner_visibility():
    assert all(
        item.owner_visible is True
        for item in get_operating_trust_records()
    )


def test_gp019_attention_count():
    surface = get_operating_trust_surface()

    assert surface.owner_attention_count == 2


def test_gp019_no_raw_access():
    assert all(
        item.raw_source_access_performed
        is False
        for item in get_operating_trust_records()
    )


def test_gp019_no_execution():
    assert all(
        item.downstream_execution_performed
        is False
        for item in get_operating_trust_records()
    )


def test_gp019_unknown_fails_closed():
    with pytest.raises(KeyError):
        get_operating_trust_record("missing")


def test_gp019_surface():
    surface = get_operating_trust_surface()

    assert surface.source_count == 6
    assert surface.trusted_count == 6
    assert surface.rejected_count == 0


def test_gp019_payload():
    payload = get_operating_trust_surface_payload()

    assert payload["trusted_count"] == 6


def test_gp019_status():
    status = get_clouds_gp019_status_payload()

    assert status["pack"] == "GP019"
    assert status["status"] == "ready"
    assert status["safe_to_continue"] is True
    assert status["trusted_count"] == 6
    assert status["rejected_count"] == 0
    assert (
        status["raw_source_access_performed"]
        is False
    )


def test_gp019_no_cross_app_imports():
    root = Path(__file__).resolve().parents[2]

    files = (
        root / "clouds" / "operating_data_trust.py",
        root / "clouds" / "operating_data_trust_service.py",
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
