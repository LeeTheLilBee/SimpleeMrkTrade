"""
GP049 — Capital Classification / Money Reality Foundation.

Verified-real classification is fail-closed.
"""

from __future__ import annotations

try:
    from .capital_classification import (
        CapitalClassification,
        CapitalEntry,
        CapitalReality,
    )

except ImportError:
    from capital_classification import (
        CapitalClassification,
        CapitalEntry,
        CapitalReality,
    )


VALID_CLASSIFICATIONS = {
    item.value
    for item
    in CapitalClassification
}


VALID_REALITIES = {
    item.value
    for item
    in CapitalReality
}


def build_capital_entry(
    *,
    entry_id,
    source_id,
    source_label,
    classification,
    reality,
    amount_cents,
    currency="USD",
    external_source_connected=False,
    external_connection_verified=False,
    source_claims_real=False,
    certification_fixture_only=False,
    evidence_reference=None,
    note="",
):
    if not entry_id:
        raise ValueError(
            "Capital entry ID is required."
        )

    if not source_id:
        raise ValueError(
            "Capital source ID is required."
        )

    if classification not in VALID_CLASSIFICATIONS:
        raise ValueError(
            "Unknown capital classification."
        )

    if reality not in VALID_REALITIES:
        raise ValueError(
            "Unknown capital reality."
        )

    if (
        not isinstance(
            amount_cents,
            int,
        )
        or amount_cents < 0
    ):
        raise ValueError(
            "Capital amounts must be non-negative integer cents."
        )

    if currency != "USD":
        raise ValueError(
            "GP049 certification supports USD only."
        )


    verified_real = (
        reality
        == CapitalReality
        .VERIFIED_REAL.value
    )


    if verified_real:
        if (
            source_claims_real
            is not True
        ):
            raise ValueError(
                "Verified-real money must explicitly claim real source state."
            )

        if (
            external_source_connected
            is not True
        ):
            raise ValueError(
                "Verified-real money requires an external source connection."
            )

        if (
            external_connection_verified
            is not True
        ):
            raise ValueError(
                "Verified-real money requires verified external connection."
            )

        if (
            certification_fixture_only
            is True
        ):
            raise ValueError(
                "Certification fixtures cannot count as verified real money."
            )


    if (
        source_claims_real
        and not verified_real
    ):
        raise ValueError(
            "A source claiming real money must use verified_real reality."
        )


    if (
        certification_fixture_only
        and source_claims_real
    ):
        raise ValueError(
            "Certification fixtures cannot claim real money."
        )


    available = (
        classification
        == CapitalClassification
        .AVAILABLE.value
    )

    committed = (
        classification
        == CapitalClassification
        .COMMITTED.value
    )

    projected = (
        classification
        == CapitalClassification
        .PROJECTED.value
    )

    target = (
        classification
        == CapitalClassification
        .TARGET.value
    )

    need = (
        classification
        == CapitalClassification
        .NEED.value
    )

    planning = (
        reality
        == CapitalReality
        .PLANNING_PROJECTION.value
    )

    simulated = (
        reality
        == CapitalReality
        .SIMULATION.value
    )


    return CapitalEntry(
        entry_id=entry_id,

        source_id=source_id,
        source_label=source_label,

        classification=classification,
        reality=reality,

        amount_cents=amount_cents,
        currency=currency,

        external_source_connected=(
            external_source_connected
        ),

        external_connection_verified=(
            external_connection_verified
        ),

        source_claims_real=(
            source_claims_real
        ),

        certification_fixture_only=(
            certification_fixture_only
        ),

        evidence_reference=(
            evidence_reference
        ),

        note=note,

        counts_as_verified_real_available=(
            verified_real
            and available
        ),

        counts_as_verified_real_committed=(
            verified_real
            and committed
        ),

        counts_as_planning_available=(
            planning
            and available
        ),

        counts_as_planning_committed=(
            planning
            and committed
        ),

        counts_as_projected=(
            planning
            and projected
        ),

        counts_as_simulated=(
            simulated
        ),

        counts_as_target=(
            target
        ),

        counts_as_need=(
            need
        ),

        capital_movement_performed=False,

        downstream_execution_performed=False,
    )


def get_gp049_certification_entries():
    """
    TEST DATA ONLY.

    No entry below is real owner/business capital.
    """

    return (
        build_capital_entry(
            entry_id=(
                "gp049-cert-ob-simulation"
            ),

            source_id="observatory",
            source_label=(
                "The Observatory"
            ),

            classification="projected",
            reality="simulation",

            amount_cents=1_234_500,

            certification_fixture_only=True,

            note=(
                "Certification-only simulated Observatory performance."
            ),
        ),

        build_capital_entry(
            entry_id=(
                "gp049-cert-ob-planning-projection"
            ),

            source_id="observatory",
            source_label=(
                "The Observatory"
            ),

            classification="projected",
            reality="planning_projection",

            amount_cents=2_000_000,

            certification_fixture_only=True,

            note=(
                "Certification-only planning projection."
            ),
        ),

        build_capital_entry(
            entry_id=(
                "gp049-cert-atm-planning-available"
            ),

            source_id="atm_operations",
            source_label=(
                "ATM Operations"
            ),

            classification="available",
            reality="planning_projection",

            amount_cents=500_000,

            certification_fixture_only=True,

            note=(
                "Planning-only available-capital fixture. "
                "Does not count as verified spendable money."
            ),
        ),

        build_capital_entry(
            entry_id=(
                "gp049-cert-grounds-planning-commitment"
            ),

            source_id="grounds",
            source_label=(
                "The Grounds"
            ),

            classification="committed",
            reality="planning_projection",

            amount_cents=750_000,

            certification_fixture_only=True,

            note=(
                "Planning-only commitment fixture."
            ),
        ),

        build_capital_entry(
            entry_id=(
                "gp049-cert-atm-need"
            ),

            source_id="atm_operations",
            source_label=(
                "ATM Operations"
            ),

            classification="need",
            reality="planning_projection",

            amount_cents=1_000_000,

            certification_fixture_only=True,

            note=(
                "Certification-only capital-need fixture."
            ),
        ),

        build_capital_entry(
            entry_id=(
                "gp049-cert-grounds-need"
            ),

            source_id="grounds",
            source_label=(
                "The Grounds"
            ),

            classification="need",
            reality="planning_projection",

            amount_cents=2_500_000,

            certification_fixture_only=True,

            note=(
                "Certification-only capital-need fixture."
            ),
        ),

        build_capital_entry(
            entry_id=(
                "gp049-cert-ecosystem-target"
            ),

            source_id="teller",
            source_label=(
                "The Teller"
            ),

            classification="target",
            reality="planning_projection",

            amount_cents=5_000_000,

            certification_fixture_only=True,

            note=(
                "Certification-only capital target fixture."
            ),
        ),
    )


def get_clouds_gp049_status_payload():
    entries = (
        get_gp049_certification_entries()
    )

    verified_real = tuple(
        item
        for item in entries
        if (
            item.reality
            == "verified_real"
        )
    )

    simulation = tuple(
        item
        for item in entries
        if (
            item.counts_as_simulated
        )
    )

    planning = tuple(
        item
        for item in entries
        if (
            item.reality
            == "planning_projection"
        )
    )


    fake_real_rejected = False

    try:
        build_capital_entry(
            entry_id="fake-real",
            source_id="observatory",
            source_label="The Observatory",
            classification="available",
            reality="verified_real",
            amount_cents=100,
            source_claims_real=True,
            external_source_connected=False,
            external_connection_verified=False,
        )

    except ValueError:
        fake_real_rejected = True


    fixture_real_rejected = False

    try:
        build_capital_entry(
            entry_id="fixture-real",
            source_id="observatory",
            source_label="The Observatory",
            classification="available",
            reality="verified_real",
            amount_cents=100,
            source_claims_real=True,
            external_source_connected=True,
            external_connection_verified=True,
            certification_fixture_only=True,
        )

    except ValueError:
        fixture_real_rejected = True


    safe = (
        len(entries) == 7

        and len(verified_real) == 0

        and len(simulation) == 1

        and len(planning) == 6

        and fake_real_rejected

        and fixture_real_rejected

        and all(
            item.certification_fixture_only
            is True
            for item in entries
        )

        and all(
            item.source_claims_real
            is False
            for item in entries
        )

        and all(
            item
            .capital_movement_performed
            is False
            for item in entries
        )

        and all(
            item
            .downstream_execution_performed
            is False
            for item in entries
        )
    )


    return {
        "pack": "GP049",

        "phase": "CLOUDS_PHASE_II",

        "section": (
            "CAPITAL CLASSIFICATION / "
            "MONEY REALITY FOUNDATION"
        ),

        "status": (
            "ready"
            if safe
            else "blocked"
        ),

        "safe_to_continue": safe,

        "certification_entry_count": (
            len(entries)
        ),

        "verified_real_entry_count": 0,

        "simulation_entry_count": (
            len(simulation)
        ),

        "planning_entry_count": (
            len(planning)
        ),

        "real_money_claimed": False,

        "verified_real_requires_external_connection": True,

        "verified_real_requires_verified_connection": True,

        "certification_fixture_real_claim_prohibited": True,

        "fake_real_claim_rejected": (
            fake_real_rejected
        ),

        "fixture_real_claim_rejected": (
            fixture_real_rejected
        ),

        "simulation_can_count_as_available": False,

        "capital_movement_performed": False,

        "downstream_execution_performed": False,

        "next_pack": (
            "GP050 — EXECUTIVE MONEY SNAPSHOT / "
            "STRICT MONEY-SEPARATION SURFACE"
        ),
    }
