"""
GP041 — Real Summary Feed Adapter Service.

Converts source-owned compact summaries into the canonical GP025
OperatingFeedEnvelope.

This service has no knowledge of downstream app internals.
"""

from __future__ import annotations

import hashlib
import json

try:
    from .operating_feed_ingestion import (
        CANONICAL_OPERATING_SOURCE_IDS,
        OperatingFeedEnvelope,
        OperatingFeedMetric,
        OperatingFeedMode,
    )

    from .operating_feed_ingestion_service import (
        SCHEMA_VERSION,
        build_projection_feed_envelopes,
        validate_operating_feed,
    )

    from .real_summary_feed_adapter import (
        ExternalOperatingSummaryPayload,
        ExternalSummaryMetric,
        RealSummaryFeedAdapterResult,
        RealSummaryFeedAdapterSpec,
    )

except ImportError:
    from operating_feed_ingestion import (
        CANONICAL_OPERATING_SOURCE_IDS,
        OperatingFeedEnvelope,
        OperatingFeedMetric,
        OperatingFeedMode,
    )

    from operating_feed_ingestion_service import (
        SCHEMA_VERSION,
        build_projection_feed_envelopes,
        validate_operating_feed,
    )

    from real_summary_feed_adapter import (
        ExternalOperatingSummaryPayload,
        ExternalSummaryMetric,
        RealSummaryFeedAdapterResult,
        RealSummaryFeedAdapterSpec,
    )


def _sha256(payload):
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(
        encoded
    ).hexdigest()


def _projection_for_source(
    source_id,
):
    for envelope in (
        build_projection_feed_envelopes()
    ):
        if envelope.source_id == source_id:
            return envelope

    raise KeyError(
        f"Unknown canonical source: {source_id}"
    )


def build_adapter_spec(
    *,
    adapter_id,
    source_id,
    source_contract_version,
):
    if (
        source_id
        not in CANONICAL_OPERATING_SOURCE_IDS
    ):
        raise ValueError(
            f"Unknown canonical source: {source_id}"
        )

    projection = (
        _projection_for_source(
            source_id
        )
    )

    return RealSummaryFeedAdapterSpec(
        adapter_id=adapter_id,

        source_id=source_id,

        source_label=(
            projection.source_label
        ),

        source_contract_version=(
            source_contract_version
        ),

        clouds_feed_schema_version=(
            SCHEMA_VERSION
        ),

        supports_projection=True,
        supports_live=True,

        external_connection_verification_required=True,

        raw_source_access_allowed=False,

        downstream_execution_allowed=False,

        cross_app_import_allowed=False,
    )


def _canonical_integrity_payload(
    *,
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
        "schema_version": SCHEMA_VERSION,

        "feed_id": feed_id,

        "source_id": source_id,
        "source_label": source_label,

        "mode": mode,

        "source_sequence": (
            source_sequence
        ),

        "observed_at": (
            observed_at
        ),

        "health": health,
        "readiness": readiness,
        "attention": attention,

        "headline": headline,
        "explanation": explanation,

        "owner_message": (
            owner_message
        ),

        "metrics": [
            metric.to_dict()
            for metric in metrics
        ],
    }


def _to_feed_metric(
    metric,
):
    return OperatingFeedMetric(
        metric_id=metric.metric_id,
        label=metric.label,
        value=metric.value,
        unit=metric.unit,
        explanation=metric.explanation,
    )


def adapt_external_summary(
    spec,
    payload,
    *,
    external_source_connected=False,
    external_connection_verified=False,
    certification_fixture_only=False,
    prior_feed_id=None,
    prior_sequence=None,
):
    """
    Convert an external source summary into GP025.

    LIVE claims fail closed unless a verified external source
    connection is explicitly present.
    """

    if (
        payload.source_id
        != spec.source_id
    ):
        raise ValueError(
            "Source ID does not match adapter specification."
        )

    if (
        payload.source_label
        != spec.source_label
    ):
        raise ValueError(
            "Source label does not match adapter specification."
        )

    if (
        payload.source_contract_version
        != spec.source_contract_version
    ):
        raise ValueError(
            "Unsupported source summary contract version."
        )

    if (
        spec.clouds_feed_schema_version
        != SCHEMA_VERSION
    ):
        raise ValueError(
            "Adapter does not target the canonical GP025 schema."
        )

    if (
        payload.mode
        not in {
            OperatingFeedMode.PROJECTION.value,
            OperatingFeedMode.LIVE.value,
        }
    ):
        raise ValueError(
            "Unsupported operating feed mode."
        )

    if (
        payload.mode
        == OperatingFeedMode.LIVE.value
    ):
        if (
            spec.supports_live
            is not True
        ):
            raise ValueError(
                "Adapter does not support live feeds."
            )

        if (
            payload.source_claims_live
            is not True
        ):
            raise ValueError(
                "Live mode requires explicit source live claim."
            )

        if (
            external_source_connected
            is not True
            or external_connection_verified
            is not True
        ):
            raise ValueError(
                "Live feed requires verified external source connection."
            )

        if (
            certification_fixture_only
            is True
        ):
            raise ValueError(
                "Certification fixtures cannot masquerade as live feeds."
            )

    else:
        if (
            spec.supports_projection
            is not True
        ):
            raise ValueError(
                "Adapter does not support projections."
            )

        if (
            payload.source_claims_live
            is not False
        ):
            raise ValueError(
                "Projection payload cannot claim live status."
            )


    metrics = tuple(
        _to_feed_metric(
            metric
        )
        for metric in payload.metrics
    )


    integrity_payload = (
        _canonical_integrity_payload(
            feed_id=payload.feed_id,

            source_id=(
                payload.source_id
            ),

            source_label=(
                payload.source_label
            ),

            mode=payload.mode,

            source_sequence=(
                payload.source_sequence
            ),

            observed_at=(
                payload.observed_at
            ),

            health=payload.health,

            readiness=payload.readiness,

            attention=payload.attention,

            headline=payload.headline,

            explanation=(
                payload.explanation
            ),

            owner_message=(
                payload.owner_message
            ),

            metrics=metrics,
        )
    )


    envelope = OperatingFeedEnvelope(
        schema_version=SCHEMA_VERSION,

        feed_id=payload.feed_id,

        source_id=payload.source_id,

        source_label=(
            payload.source_label
        ),

        mode=payload.mode,

        source_sequence=(
            payload.source_sequence
        ),

        observed_at=(
            payload.observed_at
        ),

        health=payload.health,

        readiness=payload.readiness,

        attention=payload.attention,

        headline=payload.headline,

        explanation=(
            payload.explanation
        ),

        owner_message=(
            payload.owner_message
        ),

        metrics=metrics,

        source_integrity_hash=(
            _sha256(
                integrity_payload
            )
        ),

        source_claims_live=(
            payload.source_claims_live
        ),

        downstream_execution_performed=False,
    )


    receipt = validate_operating_feed(
        envelope,
        prior_feed_id=prior_feed_id,
        prior_sequence=prior_sequence,
    )


    accepted = (
        receipt
        .accepted_for_clouds_interpretation
        is True
    )


    counts_as_live = (
        accepted
        and payload.mode
        == OperatingFeedMode.LIVE.value

        and payload.source_claims_live
        is True

        and external_source_connected
        is True

        and external_connection_verified
        is True

        and certification_fixture_only
        is False
    )


    return RealSummaryFeedAdapterResult(
        adapter_id=spec.adapter_id,

        source_id=spec.source_id,

        source_label=spec.source_label,

        source_contract_version=(
            spec.source_contract_version
        ),

        adapter_contract_ready=True,

        certification_fixture_only=(
            certification_fixture_only
        ),

        external_source_connected=(
            external_source_connected
        ),

        external_connection_verified=(
            external_connection_verified
        ),

        envelope_mode=(
            envelope.mode
        ),

        accepted_for_clouds_interpretation=(
            accepted
        ),

        validation_state=(
            receipt.validation_state
        ),

        replay_state=(
            receipt.replay_state
        ),

        source_integrity_verified=(
            receipt.integrity_hash_valid
        ),

        counts_as_real_live_connection=(
            counts_as_live
        ),

        raw_source_access_performed=False,

        downstream_execution_performed=False,

        cross_app_imports_used=False,

        envelope=envelope,

        validation_receipt=receipt,
    )


def build_certification_payload(
    spec,
    *,
    sequence,
):
    """
    Certification fixture derived from the existing approved
    GP025 projection.

    It remains explicitly non-live.
    """

    projection = (
        _projection_for_source(
            spec.source_id
        )
    )

    metrics = tuple(
        ExternalSummaryMetric(
            metric_id=metric.metric_id,
            label=metric.label,
            value=metric.value,
            unit=metric.unit,
            explanation=metric.explanation,
        )
        for metric
        in projection.metrics
    )

    return ExternalOperatingSummaryPayload(
        source_contract_version=(
            spec.source_contract_version
        ),

        feed_id=(
            "adapter-certification-"
            f"{spec.source_id}-"
            f"{sequence:04d}"
        ),

        source_id=spec.source_id,

        source_label=(
            spec.source_label
        ),

        mode=(
            OperatingFeedMode
            .PROJECTION.value
        ),

        source_sequence=(
            sequence
        ),

        observed_at=(
            "adapter-certification-projection-not-live"
        ),

        health=projection.health,

        readiness=(
            projection.readiness
        ),

        attention=(
            projection.attention
        ),

        headline=(
            projection.headline
        ),

        explanation=(
            projection.explanation
        ),

        owner_message=(
            projection.owner_message
        ),

        metrics=metrics,

        source_claims_live=False,
    )


def build_certification_result(
    spec,
    *,
    sequence,
):
    return adapt_external_summary(
        spec,

        build_certification_payload(
            spec,
            sequence=sequence,
        ),

        external_source_connected=False,

        external_connection_verified=False,

        certification_fixture_only=True,
    )
