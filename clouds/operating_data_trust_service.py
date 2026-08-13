"""
GP019 — normalize and trust-classify GP018 summaries.
"""

from __future__ import annotations

try:
    from .operating_data_adapter_service import (
        get_clouds_gp018_status_payload,
        get_operating_summaries,
    )

    from .operating_data_trust import (
        NormalizationState,
        OperatingTrustRecord,
        OperatingTrustState,
        OperatingTrustSurface,
    )

except ImportError:
    from operating_data_adapter_service import (
        get_clouds_gp018_status_payload,
        get_operating_summaries,
    )

    from operating_data_trust import (
        NormalizationState,
        OperatingTrustRecord,
        OperatingTrustState,
        OperatingTrustSurface,
    )


def _confidence(summary):
    score = 0

    if summary.source_integrity_verified:
        score += 40

    if summary.approved_summary_projection:
        score += 35

    if summary.headline and summary.explanation:
        score += 15

    if summary.metrics:
        score += 10

    return min(score, 100)


def _freshness(summary):
    if summary.live_feed_connected:
        return 100

    if (
        summary.freshness_label
        == "approved_projection"
    ):
        return 60

    return 0


def _normalize(summary):
    confidence = _confidence(summary)
    freshness = _freshness(summary)

    normalized = (
        summary.source_integrity_verified
        and summary.approved_summary_projection
        and confidence >= 80
    )

    trust = (
        OperatingTrustState
        .TRUSTED_LIVE.value
        if summary.live_feed_connected
        and normalized
        else OperatingTrustState
        .TRUSTED_PROJECTION.value
        if normalized
        else OperatingTrustState
        .UNTRUSTED.value
    )

    return OperatingTrustRecord(
        source_id=summary.source_id,
        trust_state=trust,
        normalization_state=(
            NormalizationState
            .NORMALIZED.value
            if normalized
            else NormalizationState
            .REJECTED.value
        ),
        health=summary.health,
        readiness=summary.readiness,
        attention=summary.attention,
        confidence_score=confidence,
        freshness_score=freshness,
        live_feed_connected=(
            summary.live_feed_connected
        ),
        approved_projection=(
            summary.approved_summary_projection
        ),
        owner_visible=normalized,
        owner_attention_required=(
            normalized
            and summary.attention
            in {
                "review",
                "action_required",
            }
        ),
        source_integrity_verified=(
            summary.source_integrity_verified
        ),
        clouds_interpretation_allowed=normalized,
        raw_source_access_performed=False,
        downstream_execution_performed=False,
        explanation=(
            "Trusted approved projection. "
            "Clouds may interpret this summary "
            "but may not access raw downstream data."
            if normalized
            else
            "Source failed Clouds normalization."
        ),
    )


def get_operating_trust_records():
    return tuple(
        _normalize(item)
        for item in get_operating_summaries()
    )


def get_operating_trust_record(source_id):
    for item in get_operating_trust_records():
        if item.source_id == source_id:
            return item

    raise KeyError(
        f"Unknown trusted operating source: {source_id}"
    )


def get_operating_trust_surface():
    records = get_operating_trust_records()

    return OperatingTrustSurface(
        title=(
            "Operating Data Normalization / Trust"
        ),
        records=records,
        source_count=len(records),
        trusted_count=sum(
            item.normalization_state
            == "normalized"
            for item in records
        ),
        rejected_count=sum(
            item.normalization_state
            == "rejected"
            for item in records
        ),
        owner_attention_count=sum(
            item.owner_attention_required
            for item in records
        ),
        boundary_notice=(
            "Clouds interprets normalized summaries only. "
            "No raw downstream data access occurs."
        ),
    )


def get_operating_trust_surface_payload():
    return (
        get_operating_trust_surface()
        .to_dict()
    )


def get_clouds_gp019_status_payload():
    gp018 = get_clouds_gp018_status_payload()
    surface = get_operating_trust_surface()

    records = surface.records

    safe = (
        gp018["status"] == "ready"
        and gp018["safe_to_continue"] is True
        and surface.source_count == 6
        and surface.trusted_count == 6
        and surface.rejected_count == 0
        and all(
            item.clouds_interpretation_allowed
            for item in records
        )
        and all(
            item.raw_source_access_performed
            is False
            for item in records
        )
        and all(
            item.downstream_execution_performed
            is False
            for item in records
        )
    )

    return {
        "pack": "GP019",
        "section": (
            "OPERATING DATA NORMALIZATION "
            "/ TRUST SURFACE"
        ),
        "status": "ready" if safe else "blocked",
        "safe_to_continue": safe,
        "source_count": surface.source_count,
        "trusted_count": surface.trusted_count,
        "rejected_count": surface.rejected_count,
        "owner_attention_count": (
            surface.owner_attention_count
        ),
        "raw_source_access_performed": False,
        "downstream_execution_performed": False,
        "cross_app_imports_used": False,
        "next_pack": (
            "GP020 — EXECUTIVE OPERATING "
            "SNAPSHOT / SOULAANA INTERPRETATION "
            "FOUNDATION"
        ),
    }
