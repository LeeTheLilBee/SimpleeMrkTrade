"""
GP018 — approved Clouds-side operating summary adapters.

These are explicit sample projections for the adapter contract.
They are NOT live downstream integrations.
"""

from __future__ import annotations

try:
    from .clouds_handoff_delivery_boundary_service import (
        get_clouds_gp017_status_payload,
    )

    from .operating_data_adapter import (
        OperatingAdapterSurface,
        OperatingAttention,
        OperatingAuthority,
        OperatingHealth,
        OperatingMetric,
        OperatingReadiness,
        OperatingSourceKind,
        OperatingSummary,
    )

except ImportError:
    from clouds_handoff_delivery_boundary_service import (
        get_clouds_gp017_status_payload,
    )

    from operating_data_adapter import (
        OperatingAdapterSurface,
        OperatingAttention,
        OperatingAuthority,
        OperatingHealth,
        OperatingMetric,
        OperatingReadiness,
        OperatingSourceKind,
        OperatingSummary,
    )


SOURCE_ORDER = (
    "observatory",
    "tower",
    "teller",
    "grounds",
    "archive_vault",
    "atm_operations",
)


def _metric(
    metric_id,
    label,
    value,
    explanation,
    order,
    unit=None,
):
    return OperatingMetric(
        metric_id=metric_id,
        label=label,
        value=str(value),
        unit=unit,
        explanation=explanation,
        display_order=order,
    )


def _summary(
    *,
    source_id,
    source_label,
    source_kind,
    health,
    readiness,
    attention,
    headline,
    explanation,
    owner_message,
    metrics,
    order,
):
    return OperatingSummary(
        source_id=source_id,
        source_label=source_label,
        source_kind=source_kind,
        health=health,
        readiness=readiness,
        attention=attention,
        headline=headline,
        explanation=explanation,
        owner_message=owner_message,
        metrics=tuple(metrics),
        source_authority=(
            OperatingAuthority.SOURCE.value
        ),
        clouds_authority=(
            OperatingAuthority.CLOUDS.value
        ),
        freshness_label="approved_projection",
        live_feed_connected=False,
        approved_summary_projection=True,
        source_integrity_verified=True,
        downstream_execution_performed=False,
        display_order=order,
    )


def get_operating_summaries():
    return (
        _summary(
            source_id="observatory",
            source_label="The Observatory",
            source_kind="application",
            health="attention",
            readiness="building",
            attention="action_required",
            headline=(
                "The Observatory is the current "
                "highest-priority operating system."
            ),
            explanation=(
                "OB is active in the build and owner "
                "readiness lane, but still requires "
                "owner attention before broader activation."
            ),
            owner_message=(
                "Review Observatory readiness before "
                "expanding operational scope."
            ),
            metrics=(
                _metric(
                    "ob-readiness",
                    "Readiness",
                    "42",
                    "Current approved Clouds projection.",
                    10,
                    "%",
                ),
                _metric(
                    "ob-attention",
                    "Owner attention",
                    "1",
                    "One current owner-level attention item.",
                    20,
                    "item",
                ),
            ),
            order=10,
        ),

        _summary(
            source_id="tower",
            source_label="The Tower",
            source_kind="infrastructure",
            health="healthy",
            readiness="ready",
            attention="informational",
            headline=(
                "Tower remains the protected access authority."
            ),
            explanation=(
                "Clouds recognizes Tower as the authority "
                "for authentication, permission, step-up, "
                "and protected application routing."
            ),
            owner_message=(
                "No Clouds-side Tower intervention is required."
            ),
            metrics=(
                _metric(
                    "tower-boundary",
                    "Protected boundary",
                    "preserved",
                    "Clouds does not impersonate Tower authority.",
                    10,
                ),
            ),
            order=20,
        ),

        _summary(
            source_id="teller",
            source_label="The Teller",
            source_kind="application",
            health="watch",
            readiness="reserved",
            attention="informational",
            headline=(
                "The Teller remains visible but reserved."
            ),
            explanation=(
                "The Teller is part of the Simplee operating "
                "map but is not yet treated as an active live feed."
            ),
            owner_message=(
                "Keep Teller visible; no immediate action."
            ),
            metrics=(
                _metric(
                    "teller-state",
                    "Operating state",
                    "reserved",
                    "Reserved operating projection.",
                    10,
                ),
            ),
            order=30,
        ),

        _summary(
            source_id="grounds",
            source_label="The Grounds",
            source_kind="business",
            health="watch",
            readiness="planning",
            attention="informational",
            headline=(
                "The Grounds remains in the planning lane."
            ),
            explanation=(
                "Property operations are visible to Clouds "
                "but remain outside Clouds execution authority."
            ),
            owner_message=(
                "Planning may continue without owner intervention."
            ),
            metrics=(
                _metric(
                    "grounds-state",
                    "Operating state",
                    "planning",
                    "Current approved planning projection.",
                    10,
                ),
            ),
            order=40,
        ),

        _summary(
            source_id="archive_vault",
            source_label="Archive Vault",
            source_kind="infrastructure",
            health="healthy",
            readiness="building",
            attention="informational",
            headline=(
                "Archive Vault remains protected and separate."
            ),
            explanation=(
                "Clouds may display archive-health summaries "
                "but does not retrieve raw Vault evidence."
            ),
            owner_message=(
                "No raw archive action belongs in Clouds."
            ),
            metrics=(
                _metric(
                    "vault-boundary",
                    "Raw evidence access",
                    "prohibited",
                    "Clouds summary boundary remains intact.",
                    10,
                ),
            ),
            order=50,
        ),

        _summary(
            source_id="atm_operations",
            source_label="ATM Operations",
            source_kind="business",
            health="watch",
            readiness="planning",
            attention="review",
            headline=(
                "ATM Operations remains an active strategic lane."
            ),
            explanation=(
                "Clouds can track route-planning and owner "
                "attention without executing financial operations."
            ),
            owner_message=(
                "Keep ATM planning visible behind Observatory work."
            ),
            metrics=(
                _metric(
                    "atm-phase",
                    "Operating phase",
                    "planning",
                    "Current Clouds operating projection.",
                    10,
                ),
            ),
            order=60,
        ),
    )


def get_operating_summary(source_id):
    for item in get_operating_summaries():
        if item.source_id == source_id:
            return item

    raise KeyError(
        f"Unknown operating source: {source_id}"
    )


def get_operating_summary_payload(source_id):
    return get_operating_summary(
        source_id
    ).to_dict()


def get_operating_adapter_surface():
    summaries = get_operating_summaries()

    return OperatingAdapterSurface(
        title="Simplee Operating Data Adapter",
        summaries=summaries,
        source_count=len(summaries),
        live_source_count=sum(
            item.live_feed_connected
            for item in summaries
        ),
        projected_source_count=sum(
            item.approved_summary_projection
            for item in summaries
        ),
        boundary_notice=(
            "GP018 establishes approved summary contracts "
            "only. These are not live downstream feeds."
        ),
    )


def get_operating_adapter_surface_payload():
    return (
        get_operating_adapter_surface()
        .to_dict()
    )


def get_clouds_gp018_status_payload():
    gp017 = get_clouds_gp017_status_payload()
    surface = get_operating_adapter_surface()

    summaries = surface.summaries

    safe = (
        gp017["status"] == "ready"
        and gp017["safe_to_continue"] is True
        and surface.source_count == 6
        and surface.live_source_count == 0
        and surface.projected_source_count == 6
        and tuple(
            item.source_id
            for item in summaries
        ) == SOURCE_ORDER
        and all(
            item.source_integrity_verified
            for item in summaries
        )
        and all(
            item.downstream_execution_performed
            is False
            for item in summaries
        )
    )

    return {
        "pack": "GP018",
        "section": (
            "SIMPLEE OPERATING DATA "
            "ADAPTER FOUNDATION"
        ),
        "status": "ready" if safe else "blocked",
        "safe_to_continue": safe,
        "source_count": surface.source_count,
        "live_source_count": (
            surface.live_source_count
        ),
        "projected_source_count": (
            surface.projected_source_count
        ),
        "source_ids": SOURCE_ORDER,
        "cross_app_imports_used": False,
        "downstream_execution_performed": False,
        "next_pack": (
            "GP019 — OPERATING DATA "
            "NORMALIZATION / TRUST SURFACE"
        ),
    }
