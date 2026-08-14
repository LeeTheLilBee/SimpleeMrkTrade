"""
GP050 — Executive Money Snapshot / Strict Money-Separation Surface.
"""

from __future__ import annotations

try:
    from .capital_classification_service import (
        get_gp049_certification_entries,
    )

    from .executive_money_snapshot import (
        ExecutiveMoneySnapshot,
    )

except ImportError:
    from capital_classification_service import (
        get_gp049_certification_entries,
    )

    from executive_money_snapshot import (
        ExecutiveMoneySnapshot,
    )


def format_money(
    cents,
    currency="USD",
):
    if currency != "USD":
        return (
            f"{currency} "
            f"{cents / 100:,.2f}"
        )

    return (
        f"${cents / 100:,.2f}"
    )


def build_executive_money_snapshot(
    entries,
):
    entries = tuple(entries)

    if not entries:
        raise ValueError(
            "Money snapshot requires at least one entry."
        )

    currencies = {
        item.currency
        for item in entries
    }

    if len(currencies) != 1:
        raise ValueError(
            "Money snapshot cannot silently mix currencies."
        )

    currency = next(
        iter(currencies)
    )


    verified_available = sum(
        item.amount_cents
        for item in entries
        if (
            item
            .counts_as_verified_real_available
        )
    )


    verified_committed = sum(
        item.amount_cents
        for item in entries
        if (
            item
            .counts_as_verified_real_committed
        )
    )


    verified_spendable = max(
        verified_available
        - verified_committed,
        0,
    )


    planning_available = sum(
        item.amount_cents
        for item in entries
        if (
            item
            .counts_as_planning_available
        )
    )


    planning_committed = sum(
        item.amount_cents
        for item in entries
        if (
            item
            .counts_as_planning_committed
        )
    )


    projected = sum(
        item.amount_cents
        for item in entries
        if (
            item.counts_as_projected
        )
    )


    simulated = sum(
        item.amount_cents
        for item in entries
        if (
            item.counts_as_simulated
        )
    )


    targets = sum(
        item.amount_cents
        for item in entries
        if (
            item.counts_as_target
        )
    )


    needs = sum(
        item.amount_cents
        for item in entries
        if (
            item.counts_as_need
        )
    )


    real_money_claimed = any(
        item.source_claims_real
        for item in entries
    )


    return ExecutiveMoneySnapshot(
        title=(
            "Simplee World Executive Money Picture"
        ),

        entries=entries,

        currency=currency,

        verified_real_available_cents=(
            verified_available
        ),

        verified_real_committed_cents=(
            verified_committed
        ),

        verified_real_spendable_cents=(
            verified_spendable
        ),

        planning_available_cents=(
            planning_available
        ),

        planning_committed_cents=(
            planning_committed
        ),

        projected_cents=(
            projected
        ),

        simulated_cents=(
            simulated
        ),

        target_cents=(
            targets
        ),

        need_cents=(
            needs
        ),

        real_money_claimed=(
            real_money_claimed
        ),

        simulation_excluded_from_spendable=True,

        projection_excluded_from_spendable=True,

        targets_excluded_from_spendable=True,

        soulaana_what_you_have=(
            "I do not have any externally verified real "
            "available capital in this certification view."
            if verified_available == 0
            else
            (
                "Externally verified available capital is "
                f"{format_money(verified_available, currency)}."
            )
        ),

        soulaana_what_is_spoken_for=(
            "No externally verified real commitment is present "
            "in this certification view."
            if verified_committed == 0
            else
            (
                "Externally verified committed capital is "
                f"{format_money(verified_committed, currency)}."
            )
        ),

        soulaana_what_is_only_projected=(
            "Planning projections total "
            f"{format_money(projected, currency)}. "
            "I am not treating that as money you can spend."
        ),

        soulaana_what_is_simulated=(
            "Simulation-only value totals "
            f"{format_money(simulated, currency)}. "
            "Simulation is evidence about a model or scenario, "
            "not cash."
        ),

        soulaana_what_is_targeted=(
            "Planning targets total "
            f"{format_money(targets, currency)}. "
            "Targets describe where you want to go, not what you have."
        ),

        soulaana_what_is_needed=(
            "Certification capital needs total "
            f"{format_money(needs, currency)}. "
            "A need is not a commitment or authorization."
        ),

        capital_movement_performed=False,

        downstream_execution_performed=False,

        boundary_notice=(
            "Only externally connected and verified-real entries "
            "may enter the verified spendable calculation. "
            "Planning projections, simulations, targets, and needs "
            "remain separate."
        ),
    )


def get_gp050_certification_money_snapshot():
    return (
        build_executive_money_snapshot(
            get_gp049_certification_entries()
        )
    )


def get_clouds_gp050_status_payload():
    snapshot = (
        get_gp050_certification_money_snapshot()
    )


    safe = (
        snapshot
        .verified_real_available_cents
        == 0

        and snapshot
        .verified_real_committed_cents
        == 0

        and snapshot
        .verified_real_spendable_cents
        == 0

        and snapshot
        .planning_available_cents
        > 0

        and snapshot
        .planning_committed_cents
        > 0

        and snapshot.projected_cents
        > 0

        and snapshot.simulated_cents
        > 0

        and snapshot.target_cents
        > 0

        and snapshot.need_cents
        > 0

        and snapshot
        .real_money_claimed
        is False

        and snapshot
        .simulation_excluded_from_spendable
        is True

        and snapshot
        .projection_excluded_from_spendable
        is True

        and snapshot
        .targets_excluded_from_spendable
        is True

        and snapshot
        .capital_movement_performed
        is False

        and snapshot
        .downstream_execution_performed
        is False
    )


    return {
        "pack": "GP050",

        "phase": "CLOUDS_PHASE_II",

        "section": (
            "EXECUTIVE MONEY SNAPSHOT / "
            "STRICT MONEY-SEPARATION SURFACE"
        ),

        "status": (
            "ready"
            if safe
            else "blocked"
        ),

        "safe_to_continue": safe,

        "verified_real_available_cents": 0,

        "verified_real_committed_cents": 0,

        "verified_real_spendable_cents": 0,

        "planning_available_cents": (
            snapshot
            .planning_available_cents
        ),

        "planning_committed_cents": (
            snapshot
            .planning_committed_cents
        ),

        "projected_cents": (
            snapshot.projected_cents
        ),

        "simulated_cents": (
            snapshot.simulated_cents
        ),

        "target_cents": (
            snapshot.target_cents
        ),

        "need_cents": (
            snapshot.need_cents
        ),

        "real_money_claimed": False,

        "simulation_excluded_from_spendable": True,

        "projection_excluded_from_spendable": True,

        "target_excluded_from_spendable": True,

        "capital_movement_performed": False,

        "downstream_execution_performed": False,

        "next_pack": (
            "GP051 — CAPITAL NEED / "
            "COMPETITION INTERPRETATION"
        ),
    }
