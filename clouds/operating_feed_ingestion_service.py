"""
GP025 — Real Operating Feed Ingestion Foundation.

Converts existing GP018 approved projections into the new
canonical feed-envelope shape so the ingestion boundary can
be proven before real downstream feed adapters are connected.

No downstream app imports or calls occur.
"""

from __future__ import annotations

import hashlib
import json

try:
    from .beta_readiness_closeout_service import (
        get_clouds_gp024_status_payload,
    )

    from .operating_data_adapter_service import (
        get_operating_summaries,
    )

    from .operating_feed_ingestion import (
        CANONICAL_OPERATING_SOURCE_IDS,
        OperatingFeedEnvelope,
        OperatingFeedIngestionSurface,
        OperatingFeedMetric,
        OperatingFeedMode,
        OperatingFeedReplayState,
        OperatingFeedValidationReceipt,
        OperatingFeedValidationState,
    )

except ImportError:
    from beta_readiness_closeout_service import (
        get_clouds_gp024_status_payload,
    )

    from operating_data_adapter_service import (
        get_operating_summaries,
    )

    from operating_feed_ingestion import (
        CANONICAL_OPERATING_SOURCE_IDS,
        OperatingFeedEnvelope,
        OperatingFeedIngestionSurface,
        OperatingFeedMetric,
        OperatingFeedMode,
        OperatingFeedReplayState,
        OperatingFeedValidationReceipt,
        OperatingFeedValidationState,
    )


SCHEMA_VERSION = "clouds-operating-feed-v1"


VALID_HEALTH = {
    "healthy",
    "watch",
    "attention",
    "blocked",
    "unknown",
}


VALID_READINESS = {
    "ready",
    "building",
    "planning",
    "reserved",
    "blocked",
}


VALID_ATTENTION = {
    "none",
    "informational",
    "review",
    "action_required",
}


def _hash_payload(payload):
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(
        encoded
    ).hexdigest()


def _metric_from_projection(metric):
    return OperatingFeedMetric(
        metric_id=metric.metric_id,
        label=metric.label,
        value=metric.value,
        unit=metric.unit,
        explanation=metric.explanation,
    )


def _build_integrity_payload(
    *,
    schema_version,
    feed_id,
    source_id,
    source_label,
    mode,
    source_sequence,
    observed_at,
    health,
    readiness,
    attention,
    headline,
    explanation,
    owner_message,
    metrics,
):
    return {
        "schema_version": schema_version,
        "feed_id": feed_id,
        "source_id": source_id,
        "source_label": source_label,
        "mode": mode,
        "source_sequence": source_sequence,
        "observed_at": observed_at,
        "health": health,
        "readiness": readiness,
        "attention": attention,
        "headline": headline,
        "explanation": explanation,
        "owner_message": owner_message,
        "metrics": [
            metric.to_dict()
            for metric in metrics
        ],
    }


def build_projection_feed_envelopes():
    """
    Adapt GP018 approved projections into the GP025 feed contract.

    This does NOT make them live.
    """

    envelopes = []

    for index, summary in enumerate(
        get_operating_summaries(),
        start=1,
    ):
        metrics = tuple(
            _metric_from_projection(
                metric
            )
            for metric in summary.metrics
        )

        feed_id = (
            "projection-"
            f"{summary.source_id}-"
            f"{index:04d}"
        )

        observed_at = (
            "projection-not-live"
        )

        payload = _build_integrity_payload(
            schema_version=SCHEMA_VERSION,
            feed_id=feed_id,
            source_id=summary.source_id,
            source_label=summary.source_label,
            mode=OperatingFeedMode.PROJECTION.value,
            source_sequence=index,
            observed_at=observed_at,
            health=summary.health,
            readiness=summary.readiness,
            attention=summary.attention,
            headline=summary.headline,
            explanation=summary.explanation,
            owner_message=summary.owner_message,
            metrics=metrics,
        )

        envelopes.append(
            OperatingFeedEnvelope(
                schema_version=SCHEMA_VERSION,

                feed_id=feed_id,
                source_id=summary.source_id,
                source_label=summary.source_label,

                mode=(
                    OperatingFeedMode
                    .PROJECTION.value
                ),

                source_sequence=index,

                observed_at=observed_at,

                health=summary.health,
                readiness=summary.readiness,
                attention=summary.attention,

                headline=summary.headline,
                explanation=summary.explanation,
                owner_message=(
                    summary.owner_message
                ),

                metrics=metrics,

                source_integrity_hash=(
                    _hash_payload(payload)
                ),

                source_claims_live=False,

                downstream_execution_performed=False,
            )
        )

    return tuple(envelopes)


def validate_operating_feed(
    envelope,
    *,
    prior_feed_id=None,
    prior_sequence=None,
):
    rejection_reasons = []

    schema_valid = (
        envelope.schema_version
        == SCHEMA_VERSION
    )

    if not schema_valid:
        rejection_reasons.append(
            "unsupported_schema_version"
        )

    source_known = (
        envelope.source_id
        in CANONICAL_OPERATING_SOURCE_IDS
    )

    if not source_known:
        rejection_reasons.append(
            "unknown_source"
        )

    source_sequence_valid = (
        isinstance(
            envelope.source_sequence,
            int,
        )
        and envelope.source_sequence > 0
    )

    if not source_sequence_valid:
        rejection_reasons.append(
            "invalid_source_sequence"
        )

    timestamp_present = bool(
        envelope.observed_at
    )

    if not timestamp_present:
        rejection_reasons.append(
            "missing_observed_at"
        )

    health_valid = (
        envelope.health
        in VALID_HEALTH
    )

    if not health_valid:
        rejection_reasons.append(
            "invalid_health"
        )

    readiness_valid = (
        envelope.readiness
        in VALID_READINESS
    )

    if not readiness_valid:
        rejection_reasons.append(
            "invalid_readiness"
        )

    attention_valid = (
        envelope.attention
        in VALID_ATTENTION
    )

    if not attention_valid:
        rejection_reasons.append(
            "invalid_attention"
        )

    explanations_present = all(
        (
            bool(envelope.headline),
            bool(envelope.explanation),
            bool(envelope.owner_message),
        )
    )

    if not explanations_present:
        rejection_reasons.append(
            "missing_explanation_layer"
        )

    integrity_payload = (
        _build_integrity_payload(
            schema_version=(
                envelope.schema_version
            ),
            feed_id=envelope.feed_id,
            source_id=envelope.source_id,
            source_label=(
                envelope.source_label
            ),
            mode=envelope.mode,
            source_sequence=(
                envelope.source_sequence
            ),
            observed_at=(
                envelope.observed_at
            ),
            health=envelope.health,
            readiness=envelope.readiness,
            attention=envelope.attention,
            headline=envelope.headline,
            explanation=(
                envelope.explanation
            ),
            owner_message=(
                envelope.owner_message
            ),
            metrics=envelope.metrics,
        )
    )

    integrity_hash_valid = (
        envelope.source_integrity_hash
        == _hash_payload(
            integrity_payload
        )
    )

    if not integrity_hash_valid:
        rejection_reasons.append(
            "integrity_hash_mismatch"
        )

    live_claim_consistent = (
        (
            envelope.mode
            == OperatingFeedMode
            .LIVE.value
            and envelope.source_claims_live
            is True
        )
        or
        (
            envelope.mode
            == OperatingFeedMode
            .PROJECTION.value
            and envelope.source_claims_live
            is False
        )
    )

    if not live_claim_consistent:
        rejection_reasons.append(
            "live_claim_inconsistent"
        )

    replay_state = (
        OperatingFeedReplayState
        .NEW.value
    )

    if (
        prior_feed_id is not None
        and envelope.feed_id
        == prior_feed_id
    ):
        replay_state = (
            OperatingFeedReplayState
            .DUPLICATE.value
        )

        rejection_reasons.append(
            "duplicate_feed"
        )

    elif (
        prior_sequence is not None
        and envelope.source_sequence
        <= prior_sequence
    ):
        replay_state = (
            OperatingFeedReplayState
            .STALE_SEQUENCE.value
        )

        rejection_reasons.append(
            "stale_sequence"
        )

    accepted = (
        schema_valid
        and source_known
        and source_sequence_valid
        and timestamp_present
        and health_valid
        and readiness_valid
        and attention_valid
        and explanations_present
        and integrity_hash_valid
        and live_claim_consistent
        and replay_state
        == OperatingFeedReplayState.NEW.value
        and envelope.downstream_execution_performed
        is False
    )

    return OperatingFeedValidationReceipt(
        receipt_id=(
            "feed-validation-"
            f"{envelope.feed_id}"
        ),

        feed_id=envelope.feed_id,
        source_id=envelope.source_id,

        validation_state=(
            OperatingFeedValidationState
            .ACCEPTED.value
            if accepted
            else OperatingFeedValidationState
            .REJECTED.value
        ),

        replay_state=replay_state,

        schema_valid=schema_valid,
        source_known=source_known,
        source_sequence_valid=(
            source_sequence_valid
        ),
        timestamp_present=(
            timestamp_present
        ),
        health_valid=health_valid,
        readiness_valid=readiness_valid,
        attention_valid=attention_valid,
        explanations_present=(
            explanations_present
        ),
        integrity_hash_valid=(
            integrity_hash_valid
        ),
        live_claim_consistent=(
            live_claim_consistent
        ),

        accepted_for_clouds_interpretation=(
            accepted
        ),

        raw_source_access_performed=False,
        downstream_execution_performed=False,

        rejection_reasons=tuple(
            rejection_reasons
        ),
    )


def get_projection_feed_validation_receipts():
    return tuple(
        validate_operating_feed(
            envelope
        )
        for envelope
        in build_projection_feed_envelopes()
    )


def get_operating_feed_envelope(
    feed_id,
):
    for envelope in (
        build_projection_feed_envelopes()
    ):
        if envelope.feed_id == feed_id:
            return envelope

    raise KeyError(
        f"Unknown operating feed: {feed_id}"
    )


def get_operating_feed_ingestion_surface():
    envelopes = (
        build_projection_feed_envelopes()
    )

    receipts = (
        get_projection_feed_validation_receipts()
    )

    return OperatingFeedIngestionSurface(
        title=(
            "Real Operating Feed "
            "Ingestion Foundation"
        ),

        envelopes=envelopes,
        receipts=receipts,

        feed_count=len(envelopes),

        accepted_count=sum(
            receipt.validation_state
            == "accepted"
            for receipt in receipts
        ),

        rejected_count=sum(
            receipt.validation_state
            == "rejected"
            for receipt in receipts
        ),

        projection_count=sum(
            envelope.mode
            == "projection"
            for envelope in envelopes
        ),

        live_count=sum(
            envelope.mode
            == "live"
            for envelope in envelopes
        ),

        boundary_notice=(
            "GP025 proves the feed ingestion contract "
            "using the existing approved projections. "
            "No source is claimed live until an external "
            "source actually publishes a valid live envelope."
        ),
    )


def get_operating_feed_ingestion_surface_payload():
    return (
        get_operating_feed_ingestion_surface()
        .to_dict()
    )


def get_clouds_gp025_status_payload():
    gp024 = (
        get_clouds_gp024_status_payload()
    )

    surface = (
        get_operating_feed_ingestion_surface()
    )

    receipts = surface.receipts

    safe = (
        gp024["status"] == "ready"
        and gp024["safe_to_continue"]
        is True

        and surface.feed_count == 6

        and surface.accepted_count == 6

        and surface.rejected_count == 0

        and surface.projection_count == 6

        and surface.live_count == 0

        and all(
            receipt
            .accepted_for_clouds_interpretation
            is True
            for receipt in receipts
        )

        and all(
            receipt
            .raw_source_access_performed
            is False
            for receipt in receipts
        )

        and all(
            receipt
            .downstream_execution_performed
            is False
            for receipt in receipts
        )
    )

    return {
        "pack": "GP025",

        "phase": "CLOUDS_PHASE_II",

        "section": (
            "REAL OPERATING FEED "
            "INGESTION FOUNDATION"
        ),

        "status": (
            "ready"
            if safe
            else "blocked"
        ),

        "safe_to_continue": safe,

        "canonical_source_count": 6,

        "feed_count": (
            surface.feed_count
        ),

        "accepted_count": (
            surface.accepted_count
        ),

        "rejected_count": (
            surface.rejected_count
        ),

        "projection_count": (
            surface.projection_count
        ),

        "live_count": (
            surface.live_count
        ),

        "real_live_feed_connected": False,

        "live_feed_claimed": False,

        "raw_source_access_performed": False,

        "downstream_execution_performed": False,

        "cross_app_imports_used": False,

        "next_pack": (
            "GP026 — OPERATING SNAPSHOT HISTORY "
            "/ CHANGE MEMORY FOUNDATION"
        ),
    }
