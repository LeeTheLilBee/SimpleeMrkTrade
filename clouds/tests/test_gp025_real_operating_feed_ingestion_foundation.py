import ast
from dataclasses import replace
from pathlib import Path

import pytest

from clouds.operating_feed_ingestion_service import (
    build_projection_feed_envelopes,
    get_clouds_gp025_status_payload,
    get_operating_feed_envelope,
    get_operating_feed_ingestion_surface,
    get_operating_feed_ingestion_surface_payload,
    get_projection_feed_validation_receipts,
    validate_operating_feed,
)


EXPECTED_SOURCES = (
    "observatory",
    "tower",
    "teller",
    "grounds",
    "archive_vault",
    "atm_operations",
)


def test_gp025_six_feed_envelopes():
    feeds = (
        build_projection_feed_envelopes()
    )

    assert len(feeds) == 6


def test_gp025_canonical_sources():
    feeds = (
        build_projection_feed_envelopes()
    )

    assert tuple(
        feed.source_id
        for feed in feeds
    ) == EXPECTED_SOURCES


def test_gp025_all_current_inputs_are_projections():
    feeds = (
        build_projection_feed_envelopes()
    )

    assert all(
        feed.mode == "projection"
        for feed in feeds
    )

    assert all(
        feed.source_claims_live
        is False
        for feed in feeds
    )


def test_gp025_does_not_fake_live_feeds():
    surface = (
        get_operating_feed_ingestion_surface()
    )

    assert surface.live_count == 0
    assert surface.projection_count == 6


def test_gp025_all_projection_feeds_validate():
    receipts = (
        get_projection_feed_validation_receipts()
    )

    assert len(receipts) == 6

    assert all(
        receipt.validation_state
        == "accepted"
        for receipt in receipts
    )


def test_gp025_integrity_hashes_valid():
    receipts = (
        get_projection_feed_validation_receipts()
    )

    assert all(
        receipt.integrity_hash_valid
        is True
        for receipt in receipts
    )


def test_gp025_explanation_layer_required():
    feed = (
        build_projection_feed_envelopes()[0]
    )

    broken = replace(
        feed,
        explanation="",
    )

    receipt = (
        validate_operating_feed(
            broken
        )
    )

    assert (
        receipt.validation_state
        == "rejected"
    )

    assert (
        "missing_explanation_layer"
        in receipt.rejection_reasons
    )


def test_gp025_unknown_source_fails_closed():
    feed = (
        build_projection_feed_envelopes()[0]
    )

    broken = replace(
        feed,
        source_id="unknown-app",
    )

    receipt = (
        validate_operating_feed(
            broken
        )
    )

    assert (
        receipt.validation_state
        == "rejected"
    )

    assert (
        "unknown_source"
        in receipt.rejection_reasons
    )


def test_gp025_integrity_tamper_fails_closed():
    feed = (
        build_projection_feed_envelopes()[0]
    )

    broken = replace(
        feed,
        headline="tampered",
    )

    receipt = (
        validate_operating_feed(
            broken
        )
    )

    assert (
        receipt.validation_state
        == "rejected"
    )

    assert (
        "integrity_hash_mismatch"
        in receipt.rejection_reasons
    )


def test_gp025_fake_live_claim_rejected():
    feed = (
        build_projection_feed_envelopes()[0]
    )

    broken = replace(
        feed,
        source_claims_live=True,
    )

    receipt = (
        validate_operating_feed(
            broken
        )
    )

    assert (
        receipt.validation_state
        == "rejected"
    )

    assert (
        "live_claim_inconsistent"
        in receipt.rejection_reasons
    )


def test_gp025_duplicate_feed_rejected():
    feed = (
        build_projection_feed_envelopes()[0]
    )

    receipt = (
        validate_operating_feed(
            feed,
            prior_feed_id=feed.feed_id,
        )
    )

    assert (
        receipt.validation_state
        == "rejected"
    )

    assert (
        receipt.replay_state
        == "duplicate"
    )


def test_gp025_stale_sequence_rejected():
    feed = (
        build_projection_feed_envelopes()[0]
    )

    receipt = (
        validate_operating_feed(
            feed,
            prior_sequence=(
                feed.source_sequence
            ),
        )
    )

    assert (
        receipt.validation_state
        == "rejected"
    )

    assert (
        receipt.replay_state
        == "stale_sequence"
    )


def test_gp025_lookup():
    feed = (
        build_projection_feed_envelopes()[0]
    )

    assert (
        get_operating_feed_envelope(
            feed.feed_id
        )
        == feed
    )


def test_gp025_unknown_lookup_fails_closed():
    with pytest.raises(KeyError):
        get_operating_feed_envelope(
            "missing-feed"
        )


def test_gp025_surface_counts():
    surface = (
        get_operating_feed_ingestion_surface()
    )

    assert surface.feed_count == 6
    assert surface.accepted_count == 6
    assert surface.rejected_count == 0
    assert surface.projection_count == 6
    assert surface.live_count == 0


def test_gp025_surface_payload():
    payload = (
        get_operating_feed_ingestion_surface_payload()
    )

    assert payload["feed_count"] == 6
    assert len(
        payload["envelopes"]
    ) == 6
    assert len(
        payload["receipts"]
    ) == 6


def test_gp025_no_raw_source_access():
    receipts = (
        get_projection_feed_validation_receipts()
    )

    assert all(
        receipt.raw_source_access_performed
        is False
        for receipt in receipts
    )


def test_gp025_no_execution():
    feeds = (
        build_projection_feed_envelopes()
    )

    receipts = (
        get_projection_feed_validation_receipts()
    )

    assert all(
        feed.downstream_execution_performed
        is False
        for feed in feeds
    )

    assert all(
        receipt.downstream_execution_performed
        is False
        for receipt in receipts
    )


def test_gp025_status():
    status = (
        get_clouds_gp025_status_payload()
    )

    assert status["pack"] == "GP025"

    assert (
        status["phase"]
        == "CLOUDS_PHASE_II"
    )

    assert status["status"] == "ready"

    assert (
        status["safe_to_continue"]
        is True
    )

    assert status["feed_count"] == 6
    assert status["accepted_count"] == 6
    assert status["rejected_count"] == 0

    assert (
        status["projection_count"]
        == 6
    )

    assert status["live_count"] == 0

    assert (
        status["real_live_feed_connected"]
        is False
    )

    assert (
        status["live_feed_claimed"]
        is False
    )

    assert status["next_pack"] == (
        "GP026 — OPERATING SNAPSHOT HISTORY "
        "/ CHANGE MEMORY FOUNDATION"
    )


def test_gp025_no_cross_app_imports():
    root = (
        Path(__file__)
        .resolve()
        .parents[2]
    )

    files = (
        root
        / "clouds"
        / "operating_feed_ingestion.py",

        root
        / "clouds"
        / "operating_feed_ingestion_service.py",
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
