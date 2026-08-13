"""
GP026 — Operating Snapshot History / Change Memory Foundation.

Uses deterministic projection history to prove delta behavior.
"""

from __future__ import annotations

from dataclasses import replace

try:
    from .operating_feed_ingestion_service import (
        build_projection_feed_envelopes,
        get_clouds_gp025_status_payload,
    )

    from .operating_snapshot_history import (
        ChangeDirection,
        ChangeMateriality,
        ChangeState,
        HistoricalMetricSnapshot,
        MetricDelta,
        MetricDeltaKind,
        OperatingHistorySurface,
        OperatingSnapshotDelta,
        OperatingSourceSnapshot,
    )

except ImportError:
    from operating_feed_ingestion_service import (
        build_projection_feed_envelopes,
        get_clouds_gp025_status_payload,
    )

    from operating_snapshot_history import (
        ChangeDirection,
        ChangeMateriality,
        ChangeState,
        HistoricalMetricSnapshot,
        MetricDelta,
        MetricDeltaKind,
        OperatingHistorySurface,
        OperatingSnapshotDelta,
        OperatingSourceSnapshot,
    )


HEALTH_RANK = {
    "healthy": 0,
    "watch": 1,
    "attention": 2,
    "blocked": 3,
    "unknown": 4,
}


READINESS_RANK = {
    "ready": 0,
    "building": 1,
    "planning": 2,
    "reserved": 3,
    "blocked": 4,
}


ATTENTION_RANK = {
    "none": 0,
    "informational": 1,
    "review": 2,
    "action_required": 3,
}


def _metric_snapshot(metric):
    return HistoricalMetricSnapshot(
        metric_id=metric.metric_id,
        label=metric.label,
        value=metric.value,
        unit=metric.unit,
    )


def _snapshot_from_feed(
    feed,
    *,
    snapshot_suffix,
):
    return OperatingSourceSnapshot(
        snapshot_id=(
            f"{feed.source_id}-"
            f"{snapshot_suffix}-"
            f"{feed.source_sequence:04d}"
        ),
        source_id=feed.source_id,
        source_label=feed.source_label,
        sequence=feed.source_sequence,
        observed_at=feed.observed_at,
        mode=feed.mode,
        health=feed.health,
        readiness=feed.readiness,
        attention=feed.attention,
        headline=feed.headline,
        explanation=feed.explanation,
        owner_message=feed.owner_message,
        metrics=tuple(
            _metric_snapshot(metric)
            for metric in feed.metrics
        ),
        source_integrity_verified=True,
        live_feed_claimed=False,
    )


def get_current_projection_snapshots():
    return tuple(
        _snapshot_from_feed(
            feed,
            snapshot_suffix="current",
        )
        for feed
        in build_projection_feed_envelopes()
    )


def _prior_projection_for_source(feed):
    """
    Build deterministic prior state.

    This is test/history scaffolding, not a live historical source.
    """

    if feed.source_id == "observatory":
        return replace(
            feed,
            source_sequence=(
                feed.source_sequence
                + 100
            ),
            observed_at="projection-prior",
            health="watch",
            readiness="planning",
            attention="review",
            headline=(
                "The Observatory was still "
                "in an earlier readiness posture."
            ),
            explanation=(
                "The prior projection placed Observatory "
                "one readiness stage earlier with lower "
                "owner urgency."
            ),
            owner_message=(
                "Keep preparing Observatory."
            ),
        )

    if feed.source_id == "atm_operations":
        return replace(
            feed,
            source_sequence=(
                feed.source_sequence
                + 100
            ),
            observed_at="projection-prior",
            health="healthy",
            readiness="planning",
            attention="informational",
            headline=(
                "ATM Operations previously needed "
                "less owner review."
            ),
            explanation=(
                "The prior projection showed no active "
                "review requirement."
            ),
            owner_message=(
                "No immediate ATM review."
            ),
        )

    if feed.source_id == "tower":
        return replace(
            feed,
            source_sequence=(
                feed.source_sequence
                + 100
            ),
            observed_at="projection-prior",
        )

    if feed.source_id == "teller":
        return replace(
            feed,
            source_sequence=(
                feed.source_sequence
                + 100
            ),
            observed_at="projection-prior",
        )

    if feed.source_id == "grounds":
        return replace(
            feed,
            source_sequence=(
                feed.source_sequence
                + 100
            ),
            observed_at="projection-prior",
        )

    if feed.source_id == "archive_vault":
        return replace(
            feed,
            source_sequence=(
                feed.source_sequence
                + 100
            ),
            observed_at="projection-prior",
        )

    raise KeyError(
        "Unknown projection-history source: "
        f"{feed.source_id}"
    )


def get_prior_projection_snapshots():
    feeds = (
        build_projection_feed_envelopes()
    )

    return tuple(
        _snapshot_from_feed(
            _prior_projection_for_source(
                feed
            ),
            snapshot_suffix="prior",
        )
        for feed in feeds
    )


def _metric_delta(
    prior_metric,
    current_metric,
):
    if (
        prior_metric is not None
        and current_metric is not None
    ):
        changed = (
            prior_metric.value
            != current_metric.value
            or prior_metric.unit
            != current_metric.unit
        )

        return MetricDelta(
            metric_id=(
                current_metric.metric_id
            ),
            label=current_metric.label,
            prior_value=(
                prior_metric.value
            ),
            current_value=(
                current_metric.value
            ),
            unit=current_metric.unit,
            delta_kind=(
                MetricDeltaKind
                .CHANGED.value
                if changed
                else MetricDeltaKind
                .UNCHANGED.value
            ),
            changed=changed,
            explanation=(
                "Metric value changed."
                if changed
                else "Metric is unchanged."
            ),
        )

    if prior_metric is None:
        return MetricDelta(
            metric_id=(
                current_metric.metric_id
            ),
            label=current_metric.label,
            prior_value=None,
            current_value=(
                current_metric.value
            ),
            unit=current_metric.unit,
            delta_kind=(
                MetricDeltaKind
                .ADDED.value
            ),
            changed=True,
            explanation=(
                "Metric appeared in the current snapshot."
            ),
        )

    return MetricDelta(
        metric_id=prior_metric.metric_id,
        label=prior_metric.label,
        prior_value=prior_metric.value,
        current_value=None,
        unit=prior_metric.unit,
        delta_kind=(
            MetricDeltaKind
            .REMOVED.value
        ),
        changed=True,
        explanation=(
            "Metric is no longer present."
        ),
    )


def _metric_deltas(
    prior,
    current,
):
    prior_map = {
        item.metric_id: item
        for item in prior.metrics
    }

    current_map = {
        item.metric_id: item
        for item in current.metrics
    }

    ids = sorted(
        set(prior_map)
        | set(current_map)
    )

    return tuple(
        _metric_delta(
            prior_map.get(metric_id),
            current_map.get(metric_id),
        )
        for metric_id in ids
    )


def _direction(
    prior,
    current,
):
    movements = []

    for field, rank in (
        ("health", HEALTH_RANK),
        ("readiness", READINESS_RANK),
        ("attention", ATTENTION_RANK),
    ):
        prior_value = getattr(
            prior,
            field,
        )

        current_value = getattr(
            current,
            field,
        )

        if prior_value == current_value:
            continue

        prior_rank = rank[
            prior_value
        ]

        current_rank = rank[
            current_value
        ]

        if field == "attention":
            # More attention is more owner burden.
            movement = (
                "worsening"
                if current_rank
                > prior_rank
                else "improving"
            )

        else:
            # Lower rank is better.
            movement = (
                "improving"
                if current_rank
                < prior_rank
                else "worsening"
            )

        movements.append(
            movement
        )

    if not movements:
        return (
            ChangeDirection
            .STABLE.value
        )

    if all(
        item == "improving"
        for item in movements
    ):
        return (
            ChangeDirection
            .IMPROVING.value
        )

    if all(
        item == "worsening"
        for item in movements
    ):
        return (
            ChangeDirection
            .WORSENING.value
        )

    return (
        ChangeDirection
        .MIXED.value
    )


def compare_operating_snapshots(
    prior,
    current,
):
    if (
        prior.source_id
        != current.source_id
    ):
        raise ValueError(
            "Cannot compare snapshots from different sources."
        )

    metric_deltas = (
        _metric_deltas(
            prior,
            current,
        )
    )

    health_changed = (
        prior.health
        != current.health
    )

    readiness_changed = (
        prior.readiness
        != current.readiness
    )

    attention_changed = (
        prior.attention
        != current.attention
    )

    changed_metric_count = sum(
        item.changed
        for item in metric_deltas
    )

    changed = (
        health_changed
        or readiness_changed
        or attention_changed
        or changed_metric_count > 0
    )

    material = (
        health_changed
        or readiness_changed
        or attention_changed
    )

    direction = (
        _direction(
            prior,
            current,
        )
    )

    if not changed:
        what_changed = (
            f"{current.source_label} has no "
            "meaningful change in this comparison."
        )

        why_it_matters = (
            "You do not need to spend attention "
            "rechecking an unchanged source."
        )

        owner_attention = (
            "No additional owner attention is required "
            "because of change."
        )

        what_can_wait = (
            "This source can remain in its existing "
            "attention lane."
        )

    else:
        change_parts = []

        if health_changed:
            change_parts.append(
                "health moved from "
                f"{prior.health} to {current.health}"
            )

        if readiness_changed:
            change_parts.append(
                "readiness moved from "
                f"{prior.readiness} to "
                f"{current.readiness}"
            )

        if attention_changed:
            change_parts.append(
                "owner attention moved from "
                f"{prior.attention} to "
                f"{current.attention}"
            )

        if changed_metric_count:
            change_parts.append(
                f"{changed_metric_count} metric"
                + (
                    " changed"
                    if changed_metric_count == 1
                    else "s changed"
                )
            )

        what_changed = (
            f"{current.source_label}: "
            + "; ".join(change_parts)
            + "."
        )

        if direction == "worsening":
            why_it_matters = (
                "This source moved in a direction that "
                "deserves more owner awareness."
            )

        elif direction == "improving":
            why_it_matters = (
                "This source is moving toward a better "
                "operating posture."
            )

        elif direction == "mixed":
            why_it_matters = (
                "Some parts improved while others require "
                "more attention, so the change should be "
                "read in context."
            )

        else:
            why_it_matters = (
                "The material state is stable even though "
                "some supporting data changed."
            )

        owner_attention = (
            "Review this change now."
            if material
            and current.attention
            in {
                "review",
                "action_required",
            }
            else
            "No immediate owner action is required "
            "from this change."
        )

        what_can_wait = (
            "Supporting evidence and unchanged metrics "
            "can wait unless you want deeper detail."
        )

    owner_attention_required = (
        material
        and current.attention
        in {
            "review",
            "action_required",
        }
    )

    return OperatingSnapshotDelta(
        delta_id=(
            f"delta-{current.source_id}-"
            f"{prior.sequence}-"
            f"{current.sequence}"
        ),

        source_id=current.source_id,
        source_label=(
            current.source_label
        ),

        prior_snapshot_id=(
            prior.snapshot_id
        ),

        current_snapshot_id=(
            current.snapshot_id
        ),

        change_state=(
            ChangeState
            .CHANGED.value
            if changed
            else ChangeState
            .UNCHANGED.value
        ),

        direction=direction,

        materiality=(
            ChangeMateriality
            .MATERIAL.value
            if material
            else
            ChangeMateriality
            .INFORMATIONAL.value
            if changed
            else
            ChangeMateriality
            .NONE.value
        ),

        health_changed=health_changed,
        readiness_changed=(
            readiness_changed
        ),
        attention_changed=(
            attention_changed
        ),

        prior_health=prior.health,
        current_health=current.health,

        prior_readiness=(
            prior.readiness
        ),
        current_readiness=(
            current.readiness
        ),

        prior_attention=(
            prior.attention
        ),
        current_attention=(
            current.attention
        ),

        metric_deltas=(
            metric_deltas
        ),

        changed_metric_count=(
            changed_metric_count
        ),

        soulaana_what_changed=(
            what_changed
        ),

        soulaana_why_it_matters=(
            why_it_matters
        ),

        soulaana_owner_attention=(
            owner_attention
        ),

        soulaana_what_can_wait=(
            what_can_wait
        ),

        owner_attention_required=(
            owner_attention_required
        ),

        live_history_claimed=False,

        downstream_execution_performed=False,
    )


def get_projection_snapshot_deltas():
    prior = {
        item.source_id: item
        for item
        in get_prior_projection_snapshots()
    }

    current = {
        item.source_id: item
        for item
        in get_current_projection_snapshots()
    }

    if set(prior) != set(current):
        raise RuntimeError(
            "Prior/current projection history source sets differ."
        )

    return tuple(
        compare_operating_snapshots(
            prior[source_id],
            current[source_id],
        )
        for source_id in current
    )


def get_projection_snapshot_delta(
    source_id,
):
    for item in (
        get_projection_snapshot_deltas()
    ):
        if item.source_id == source_id:
            return item

    raise KeyError(
        f"Unknown snapshot delta source: {source_id}"
    )


def get_operating_history_surface():
    prior = (
        get_prior_projection_snapshots()
    )

    current = (
        get_current_projection_snapshots()
    )

    deltas = (
        get_projection_snapshot_deltas()
    )

    return OperatingHistorySurface(
        title=(
            "Operating Snapshot History "
            "/ Change Memory"
        ),

        prior_snapshots=prior,
        current_snapshots=current,
        deltas=deltas,

        source_count=len(deltas),

        changed_source_count=sum(
            item.change_state
            == "changed"
            for item in deltas
        ),

        unchanged_source_count=sum(
            item.change_state
            == "unchanged"
            for item in deltas
        ),

        material_change_count=sum(
            item.materiality
            == "material"
            for item in deltas
        ),

        owner_attention_count=sum(
            item.owner_attention_required
            for item in deltas
        ),

        live_history_connected=False,

        boundary_notice=(
            "GP026 proves change-memory behavior using "
            "deterministic projection history. "
            "No live historical source is claimed."
        ),
    )


def get_operating_history_surface_payload():
    return (
        get_operating_history_surface()
        .to_dict()
    )


def get_clouds_gp026_status_payload():
    gp025 = (
        get_clouds_gp025_status_payload()
    )

    surface = (
        get_operating_history_surface()
    )

    deltas = surface.deltas

    safe = (
        gp025["status"] == "ready"
        and gp025["safe_to_continue"]
        is True

        and surface.source_count == 6

        and surface.changed_source_count == 2

        and surface.unchanged_source_count == 4

        and surface.material_change_count == 2

        and surface.owner_attention_count == 2

        and surface.live_history_connected
        is False

        and all(
            item.live_history_claimed
            is False
            for item in deltas
        )

        and all(
            item.downstream_execution_performed
            is False
            for item in deltas
        )
    )

    return {
        "pack": "GP026",

        "phase": "CLOUDS_PHASE_II",

        "section": (
            "OPERATING SNAPSHOT HISTORY "
            "/ CHANGE MEMORY FOUNDATION"
        ),

        "status": (
            "ready"
            if safe
            else "blocked"
        ),

        "safe_to_continue": safe,

        "source_count": (
            surface.source_count
        ),

        "changed_source_count": (
            surface.changed_source_count
        ),

        "unchanged_source_count": (
            surface.unchanged_source_count
        ),

        "material_change_count": (
            surface.material_change_count
        ),

        "owner_attention_count": (
            surface.owner_attention_count
        ),

        "observatory_changed": (
            get_projection_snapshot_delta(
                "observatory"
            ).change_state
            == "changed"
        ),

        "atm_operations_changed": (
            get_projection_snapshot_delta(
                "atm_operations"
            ).change_state
            == "changed"
        ),

        "live_history_connected": False,

        "live_history_claimed": False,

        "raw_source_access_performed": False,

        "downstream_execution_performed": False,

        "cross_app_imports_used": False,

        "next_pack": (
            "GP027 — CROSS-BUSINESS "
            "IMPACT GRAPH FOUNDATION"
        ),
    }
