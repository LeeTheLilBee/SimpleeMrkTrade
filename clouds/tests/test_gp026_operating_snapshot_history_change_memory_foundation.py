from dataclasses import replace

import pytest

from clouds.operating_snapshot_history_service import (
    compare_operating_snapshots,
    get_clouds_gp026_status_payload,
    get_current_projection_snapshots,
    get_operating_history_surface,
    get_operating_history_surface_payload,
    get_prior_projection_snapshots,
    get_projection_snapshot_delta,
    get_projection_snapshot_deltas,
)


def test_gp026_six_prior_snapshots():
    assert len(
        get_prior_projection_snapshots()
    ) == 6


def test_gp026_six_current_snapshots():
    assert len(
        get_current_projection_snapshots()
    ) == 6


def test_gp026_six_deltas():
    assert len(
        get_projection_snapshot_deltas()
    ) == 6


def test_gp026_observatory_changed():
    delta = (
        get_projection_snapshot_delta(
            "observatory"
        )
    )

    assert (
        delta.change_state
        == "changed"
    )

    assert delta.materiality == (
        "material"
    )

    assert (
        delta.owner_attention_required
        is True
    )


def test_gp026_atm_changed():
    delta = (
        get_projection_snapshot_delta(
            "atm_operations"
        )
    )

    assert (
        delta.change_state
        == "changed"
    )

    assert (
        delta.owner_attention_required
        is True
    )


def test_gp026_four_sources_unchanged():
    surface = (
        get_operating_history_surface()
    )

    assert (
        surface.unchanged_source_count
        == 4
    )


def test_gp026_two_material_changes():
    surface = (
        get_operating_history_surface()
    )

    assert (
        surface.material_change_count
        == 2
    )


def test_gp026_soulaana_explains_changes():
    for delta in (
        get_projection_snapshot_deltas()
    ):
        assert (
            delta.soulaana_what_changed
        )

        assert (
            delta.soulaana_why_it_matters
        )

        assert (
            delta.soulaana_owner_attention
        )

        assert (
            delta.soulaana_what_can_wait
        )


def test_gp026_unchanged_source_explains_no_change():
    delta = (
        get_projection_snapshot_delta(
            "tower"
        )
    )

    assert (
        delta.change_state
        == "unchanged"
    )

    assert (
        "no meaningful change"
        in delta.soulaana_what_changed.lower()
    )


def test_gp026_source_mismatch_fails_closed():
    prior = (
        get_prior_projection_snapshots()[0]
    )

    current = (
        get_current_projection_snapshots()[1]
    )

    with pytest.raises(ValueError):
        compare_operating_snapshots(
            prior,
            current,
        )


def test_gp026_unknown_delta_fails_closed():
    with pytest.raises(KeyError):
        get_projection_snapshot_delta(
            "missing"
        )


def test_gp026_no_live_history_claim():
    surface = (
        get_operating_history_surface()
    )

    assert (
        surface.live_history_connected
        is False
    )

    assert all(
        delta.live_history_claimed
        is False
        for delta in surface.deltas
    )


def test_gp026_no_execution():
    assert all(
        delta.downstream_execution_performed
        is False
        for delta
        in get_projection_snapshot_deltas()
    )


def test_gp026_surface_counts():
    surface = (
        get_operating_history_surface()
    )

    assert surface.source_count == 6
    assert (
        surface.changed_source_count
        == 2
    )
    assert (
        surface.unchanged_source_count
        == 4
    )
    assert (
        surface.material_change_count
        == 2
    )
    assert (
        surface.owner_attention_count
        == 2
    )


def test_gp026_surface_payload():
    payload = (
        get_operating_history_surface_payload()
    )

    assert payload["source_count"] == 6

    assert len(
        payload["prior_snapshots"]
    ) == 6

    assert len(
        payload["current_snapshots"]
    ) == 6

    assert len(
        payload["deltas"]
    ) == 6


def test_gp026_status():
    status = (
        get_clouds_gp026_status_payload()
    )

    assert status["pack"] == "GP026"

    assert (
        status["phase"]
        == "CLOUDS_PHASE_II"
    )

    assert (
        status["status"]
        == "ready"
    )

    assert (
        status["safe_to_continue"]
        is True
    )

    assert (
        status["source_count"]
        == 6
    )

    assert (
        status["changed_source_count"]
        == 2
    )

    assert (
        status["unchanged_source_count"]
        == 4
    )

    assert (
        status["material_change_count"]
        == 2
    )

    assert (
        status["owner_attention_count"]
        == 2
    )

    assert (
        status["observatory_changed"]
        is True
    )

    assert (
        status["atm_operations_changed"]
        is True
    )

    assert (
        status["live_history_connected"]
        is False
    )

    assert (
        status["live_history_claimed"]
        is False
    )

    assert (
        status["downstream_execution_performed"]
        is False
    )

    assert status["next_pack"] == (
        "GP027 — CROSS-BUSINESS "
        "IMPACT GRAPH FOUNDATION"
    )


def test_gp026_metric_delta_detects_change():
    prior = (
        get_prior_projection_snapshots()[0]
    )

    current = (
        get_current_projection_snapshots()[0]
    )

    if not prior.metrics:
        pytest.skip(
            "Source has no metrics."
        )

    changed_metric = replace(
        current.metrics[0],
        value="999999",
    )

    changed_current = replace(
        current,
        metrics=(
            changed_metric,
            *current.metrics[1:],
        ),
    )

    delta = (
        compare_operating_snapshots(
            prior,
            changed_current,
        )
    )

    assert (
        delta.changed_metric_count
        >= 1
    )
