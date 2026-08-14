"""
GP051 — Capital Need / Competition Interpretation.

Uses the existing GP028 owner agenda as the attention-priority source.

Capital prioritization here means REVIEW ORDER only.

It is not allocation.
"""

from __future__ import annotations

try:
    from .capital_classification_service import (
        get_gp049_certification_entries,
    )

    from .capital_competition import (
        CapitalCompetitionSurface,
        CapitalNeedView,
    )

    from .executive_money_snapshot_service import (
        format_money,
        get_gp050_certification_money_snapshot,
    )

    from .executive_owner_agenda_service import (
        get_owner_agenda_items,
    )

except ImportError:
    from capital_classification_service import (
        get_gp049_certification_entries,
    )

    from capital_competition import (
        CapitalCompetitionSurface,
        CapitalNeedView,
    )

    from executive_money_snapshot_service import (
        format_money,
        get_gp050_certification_money_snapshot,
    )

    from executive_owner_agenda_service import (
        get_owner_agenda_items,
    )


HORIZON_RANK = {
    "do_now": 10,
    "today": 20,
    "this_week": 30,
    "watching": 40,
    "waiting": 50,
    "can_wait": 60,
}


URGENCY_RANK = {
    "critical": 10,
    "high": 20,
    "elevated": 30,
    "routine": 40,
    "context": 50,
}


def _agenda_priority_for_source(
    source_id,
):
    agenda = (
        get_owner_agenda_items()
    )

    matches = tuple(
        item
        for item in agenda
        if (
            item.source_id
            == source_id

            or item.impacted_source_id
            == source_id
        )
    )


    if not matches:
        return (
            "can_wait",
            "context",
            False,
            6_050,
        )


    ordered = sorted(
        matches,
        key=lambda item: (
            HORIZON_RANK[
                item.horizon
            ],

            URGENCY_RANK[
                item.urgency
            ],

            0
            if item
            .owner_attention_required
            else 1,

            item.agenda_item_id,
        ),
    )


    best = ordered[0]


    rank = (
        HORIZON_RANK[
            best.horizon
        ]
        * 100

        + URGENCY_RANK[
            best.urgency
        ]
    )


    return (
        best.horizon,
        best.urgency,
        best.owner_attention_required,
        rank,
    )


def build_capital_need_views(
    entries=None,
):
    if entries is None:
        entries = (
            get_gp049_certification_entries()
        )


    needs = tuple(
        item
        for item in entries
        if item.counts_as_need
    )


    views = []


    for item in needs:
        (
            horizon,
            urgency,
            attention,
            rank,
        ) = (
            _agenda_priority_for_source(
                item.source_id
            )
        )


        views.append(
            CapitalNeedView(
                entry_id=(
                    item.entry_id
                ),

                source_id=(
                    item.source_id
                ),

                source_label=(
                    item.source_label
                ),

                amount_cents=(
                    item.amount_cents
                ),

                currency=(
                    item.currency
                ),

                horizon=horizon,

                urgency=urgency,

                priority_rank=rank,

                owner_attention_required=(
                    attention
                ),

                certification_fixture_only=(
                    item
                    .certification_fixture_only
                ),

                soulaana_reason=(
                    f"{item.source_label} currently maps "
                    f"to the {horizon.replace('_', ' ')} "
                    f"owner-attention horizon with "
                    f"{urgency} urgency."
                ),
            )
        )


    return tuple(
        sorted(
            views,
            key=lambda item: (
                item.priority_rank,
                item.source_id,
                item.entry_id,
            ),
        )
    )


def get_capital_competition_surface():
    snapshot = (
        get_gp050_certification_money_snapshot()
    )

    needs = (
        build_capital_need_views()
    )


    total_need = sum(
        item.amount_cents
        for item in needs
    )


    spendable = (
        snapshot
        .verified_real_spendable_cents
    )


    gap = max(
        total_need
        - spendable,
        0,
    )


    fully_covered = (
        spendable
        >= total_need
    )


    competition = (
        len(needs) > 1
    )


    review_order = tuple(
        item.source_id
        for item in needs
    )


    first = (
        needs[0]
        if needs
        else None
    )


    return CapitalCompetitionSurface(
        title=(
            "Capital Need / Competition"
        ),

        needs=needs,

        need_count=len(needs),

        total_need_cents=(
            total_need
        ),

        verified_real_spendable_cents=(
            spendable
        ),

        verified_coverage_gap_cents=(
            gap
        ),

        fully_covered_by_verified_real_capital=(
            fully_covered
        ),

        capital_competition_present=(
            competition
        ),

        review_order_source_ids=(
            review_order
        ),

        allocation_performed=False,

        capital_movement_performed=False,

        downstream_execution_performed=False,

        soulaana_what_is_competing=(
            (
                f"{len(needs)} certification capital needs "
                f"total {format_money(total_need)}."
            )
            if needs
            else
            "No capital needs are present."
        ),

        soulaana_what_it_means=(
            "I do not have verified real spendable capital "
            "in this certification picture, so I cannot tell "
            "you these needs are funded."
            if spendable == 0
            else
            (
                "The current verified spendable amount does "
                "not automatically authorize allocation."
            )
        ),

        soulaana_what_needs_attention=(
            (
                f"Review {first.source_label} first because "
                "its existing owner-agenda position currently "
                "ranks highest among these capital needs."
            )
            if first
            else
            "No capital review is needed."
        ),

        soulaana_what_can_wait=(
            "Lower-ranked capital needs can remain visible "
            "without becoming false urgency."
        ),

        soulaana_next_step=(
            "Review the owning business and verified capital "
            "source before making any allocation decision. "
            "I will not move money for you."
        ),

        boundary_notice=(
            "Clouds may rank capital needs for owner review. "
            "Review order is not an allocation, approval, "
            "commitment, transfer, payment, or trade."
        ),
    )


def get_clouds_gp051_status_payload():
    surface = (
        get_capital_competition_surface()
    )


    safe = (
        surface.need_count == 2

        and surface
        .total_need_cents
        > 0

        and surface
        .verified_real_spendable_cents
        == 0

        and surface
        .verified_coverage_gap_cents
        == surface
        .total_need_cents

        and surface
        .fully_covered_by_verified_real_capital
        is False

        and surface
        .capital_competition_present
        is True

        and len(
            surface
            .review_order_source_ids
        )
        == 2

        and all(
            item
            .certification_fixture_only
            is True
            for item in surface.needs
        )

        and surface
        .allocation_performed
        is False

        and surface
        .capital_movement_performed
        is False

        and surface
        .downstream_execution_performed
        is False
    )


    return {
        "pack": "GP051",

        "phase": "CLOUDS_PHASE_II",

        "section": (
            "CAPITAL NEED / "
            "COMPETITION INTERPRETATION"
        ),

        "status": (
            "ready"
            if safe
            else "blocked"
        ),

        "safe_to_continue": safe,

        "capital_need_count": (
            surface.need_count
        ),

        "capital_competition_present": (
            surface
            .capital_competition_present
        ),

        "verified_real_spendable_cents": 0,

        "fully_covered_by_verified_real_capital": False,

        "review_order_ready": True,

        "review_order_uses_existing_owner_agenda": True,

        "review_order_is_allocation": False,

        "allocation_performed": False,

        "capital_movement_performed": False,

        "downstream_execution_performed": False,

        "next_pack": (
            "GP052 — SOULAANA EXECUTIVE MONEY "
            "COMMAND SURFACE / LAYER CLOSEOUT"
        ),
    }
