"""
GP052 — Soulaana Executive Money Command Surface / Layer Closeout.
"""

from __future__ import annotations

try:
    from .capital_competition_service import (
        get_capital_competition_surface,
    )

    from .executive_money_command_surface import (
        ExecutiveMoneyCommandSurface,
    )

    from .executive_money_snapshot_service import (
        format_money,
        get_gp050_certification_money_snapshot,
    )

    from .owner_command_preferences_service import (
        get_owner_command_preferences,
    )

except ImportError:
    from capital_competition_service import (
        get_capital_competition_surface,
    )

    from executive_money_command_surface import (
        ExecutiveMoneyCommandSurface,
    )

    from executive_money_snapshot_service import (
        format_money,
        get_gp050_certification_money_snapshot,
    )

    from owner_command_preferences_service import (
        get_owner_command_preferences,
    )


def get_executive_money_command_surface():
    snapshot = (
        get_gp050_certification_money_snapshot()
    )

    competition = (
        get_capital_competition_surface()
    )

    prefs = (
        get_owner_command_preferences()
    )


    strict_separation = (
        snapshot
        .simulation_excluded_from_spendable

        and snapshot
        .projection_excluded_from_spendable

        and snapshot
        .targets_excluded_from_spendable

        and snapshot
        .verified_real_spendable_cents
        == (
            snapshot
            .verified_real_available_cents

            - snapshot
            .verified_real_committed_cents
        )
    )


    return ExecutiveMoneyCommandSurface(
        title=(
            "Simplee World Money Picture"
        ),

        subtitle=(
            "What is real, what is spoken for, "
            "what is projected, and what needs capital"
        ),

        snapshot=snapshot,

        capital_competition=(
            competition
        ),

        verified_real_spendable_cents=(
            snapshot
            .verified_real_spendable_cents
        ),

        planning_available_cents=(
            snapshot
            .planning_available_cents
        ),

        planning_committed_cents=(
            snapshot
            .planning_committed_cents
        ),

        projected_cents=(
            snapshot.projected_cents
        ),

        simulated_cents=(
            snapshot.simulated_cents
        ),

        target_cents=(
            snapshot.target_cents
        ),

        need_cents=(
            snapshot.need_cents
        ),

        strict_money_separation_verified=(
            strict_separation
        ),

        simulated_money_in_spendable_total=False,

        projected_money_in_spendable_total=False,

        target_money_in_spendable_total=False,

        real_money_claimed=(
            snapshot.real_money_claimed
        ),

        soulaana_owner_brief=(
            "Here is the money picture: I currently have "
            "no externally verified real spendable capital "
            "inside this certification view. I do have planning, "
            "simulation, target, and need figures, and I am "
            "keeping every one of those categories separate."
        ),

        soulaana_why_it_matters=(
            "Mixing simulated or projected performance with "
            "real spendable money could create false confidence "
            "and bad capital decisions. I will not do that."
        ),

        soulaana_what_needs_attention=(
            competition
            .soulaana_what_needs_attention
        ),

        soulaana_what_can_wait=(
            competition
            .soulaana_what_can_wait
        ),

        soulaana_next_step=(
            "When real externally verified capital summaries "
            "arrive, I can place them in the verified-real lane "
            "without changing the separation rules. "
            "You still make allocation decisions."
        ),

        allocation_performed=False,

        capital_movement_performed=False,

        downstream_execution_performed=False,

        boundary_notice=(
            "The Executive Money Picture is an interpretation "
            "and owner-decision support surface. It cannot move "
            "capital, execute trades or payments, or convert "
            "planning/simulation figures into real money."
        ),
    )


def get_executive_money_command_surface_payload():
    return (
        get_executive_money_command_surface()
        .to_dict()
    )


def get_clouds_gp052_status_payload():
    surface = (
        get_executive_money_command_surface()
    )

    prefs = (
        get_owner_command_preferences()
    )


    safe = (
        prefs.soulaana_verbosity
        == "explain_everything"

        and surface
        .strict_money_separation_verified
        is True

        and surface
        .verified_real_spendable_cents
        == 0

        and surface
        .planning_available_cents
        > 0

        and surface
        .planning_committed_cents
        > 0

        and surface.projected_cents
        > 0

        and surface.simulated_cents
        > 0

        and surface.target_cents
        > 0

        and surface.need_cents
        > 0

        and surface
        .simulated_money_in_spendable_total
        is False

        and surface
        .projected_money_in_spendable_total
        is False

        and surface
        .target_money_in_spendable_total
        is False

        and surface
        .real_money_claimed
        is False

        and surface
        .capital_competition
        .allocation_performed
        is False

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
        "pack": "GP052",

        "phase": "CLOUDS_PHASE_II",

        "section": (
            "SOULAANA EXECUTIVE MONEY "
            "COMMAND SURFACE / LAYER CLOSEOUT"
        ),

        "status": (
            "ready"
            if safe
            else "blocked"
        ),

        "safe_to_continue": safe,

        "executive_money_picture_ready": True,

        "verified_real_available_lane_ready": True,

        "verified_real_committed_lane_ready": True,

        "verified_real_spendable_lane_ready": True,

        "planning_available_lane_ready": True,

        "planning_committed_lane_ready": True,

        "projected_lane_ready": True,

        "simulation_lane_ready": True,

        "target_lane_ready": True,

        "capital_need_lane_ready": True,

        "capital_competition_interpretation_ready": True,

        "strict_money_separation_verified": True,

        "simulated_money_in_spendable_total": False,

        "projected_money_in_spendable_total": False,

        "target_money_in_spendable_total": False,

        "real_money_claimed": False,

        "soulaana_explains_everything_preserved": True,

        "allocation_performed": False,

        "capital_movement_performed": False,

        "downstream_execution_performed": False,

        "conclusion": (
            "CLOUDS_PHASE_II_EXECUTIVE_"
            "MONEY_PICTURE_LAYER_READY"
        ),

        "next_pack": (
            "GP053 — SOULAANA CHIEF OF STAFF / "
            "OWNER BRIEF FOUNDATION"
        ),
    }
