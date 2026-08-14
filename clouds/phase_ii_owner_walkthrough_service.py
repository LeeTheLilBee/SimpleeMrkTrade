"""
GP059 — Phase II Owner Walkthrough /
Tower-Clouds Readiness Rehearsal.

This is a software-side rehearsal.

It does not claim hosted Tower integration or real live feeds.
"""

from __future__ import annotations

from pathlib import Path
import tempfile

try:

    from .beta_readiness_closeout_service import (
        get_clouds_owner_walkthrough,
    )

    from .executive_money_command_surface_service import (
        get_executive_money_command_surface,
    )

    from .feed_degradation_service import (
        get_gp058_certification_surfaces,
    )

    from .owner_attention_controls_service import (
        acknowledge_attention_item,
    )

    from .owner_attention_memory_service import (
        OwnerAttentionMemoryStore,
    )

    from .owner_command_preferences_service import (
        get_owner_command_preferences,
    )

    from .phase_ii_owner_walkthrough import (
        PhaseIIOwnerWalkthroughStep,
        PhaseIIOwnerWalkthroughSurface,
    )

    from .soulaana_chief_of_staff_service import (
        build_soulaana_chief_of_staff_surface,
    )

    from .soulaana_owner_brief_service import (
        get_chief_of_staff_agenda_items,
    )

except ImportError:

    from beta_readiness_closeout_service import (
        get_clouds_owner_walkthrough,
    )

    from executive_money_command_surface_service import (
        get_executive_money_command_surface,
    )

    from feed_degradation_service import (
        get_gp058_certification_surfaces,
    )

    from owner_attention_controls_service import (
        acknowledge_attention_item,
    )

    from owner_attention_memory_service import (
        OwnerAttentionMemoryStore,
    )

    from owner_command_preferences_service import (
        get_owner_command_preferences,
    )

    from phase_ii_owner_walkthrough import (
        PhaseIIOwnerWalkthroughStep,
        PhaseIIOwnerWalkthroughSurface,
    )

    from soulaana_chief_of_staff_service import (
        build_soulaana_chief_of_staff_surface,
    )

    from soulaana_owner_brief_service import (
        get_chief_of_staff_agenda_items,
    )


def get_phase_ii_owner_walkthrough():

    core_walkthrough = (
        get_clouds_owner_walkthrough()
    )


    core_ready = (
        len(
            core_walkthrough
        )
        == 11

        and all(
            item.passed
            is True

            for item
            in core_walkthrough
        )

        and all(
            item.execution_performed
            is False

            for item
            in core_walkthrough
        )
    )


    prefs = (
        get_owner_command_preferences()
    )


    money = (
        get_executive_money_command_surface()
    )


    degradation = (
        get_gp058_certification_surfaces()
    )


    missing = (
        degradation[
            "missing"
        ]
    )

    stale = (
        degradation[
            "stale"
        ]
    )

    conflict = (
        degradation[
            "conflict"
        ]
    )


    agenda = (
        get_chief_of_staff_agenda_items()
    )


    with tempfile.TemporaryDirectory() as directory:

        active_store = (
            OwnerAttentionMemoryStore(
                Path(directory)
                / "active.json"
            )
        )


        active_chief = (
            build_soulaana_chief_of_staff_surface(

                active_store,

                agenda_items=agenda,

                now_iso=(
                    "2026-08-14T16:00:00Z"
                ),
            )
        )


        quiet_store = (
            OwnerAttentionMemoryStore(
                Path(directory)
                / "quiet.json"
            )
        )


        for item in agenda:

            if (
                item
                .owner_attention_required
                is True
            ):

                acknowledge_attention_item(
                    quiet_store,
                    item,

                    now_iso=(
                        "2026-08-14T15:00:00Z"
                    ),
                )


        quiet_chief = (
            build_soulaana_chief_of_staff_surface(

                quiet_store,

                agenda_items=agenda,

                now_iso=(
                    "2026-08-14T16:00:00Z"
                ),
            )
        )


    steps = (

        PhaseIIOwnerWalkthroughStep(

            step_id=(
                "phase-ii-walkthrough-01"
            ),

            label=(
                "Core owner command remains green"
            ),

            expected_state=(
                "Original GP024 Clouds owner walkthrough "
                "remains intact."
            ),

            passed=(
                core_ready
            ),

            external_state_claimed=False,

            execution_performed=False,

            display_order=10,
        ),


        PhaseIIOwnerWalkthroughStep(

            step_id=(
                "phase-ii-walkthrough-02"
            ),

            label=(
                "Soulaana explain-everything remains active"
            ),

            expected_state=(
                "Owner preference remains explain_everything."
            ),

            passed=(
                prefs.soulaana_verbosity
                == "explain_everything"
            ),

            external_state_claimed=False,

            execution_performed=False,

            display_order=20,
        ),


        PhaseIIOwnerWalkthroughStep(

            step_id=(
                "phase-ii-walkthrough-03"
            ),

            label=(
                "Chief of Staff active-attention view works"
            ),

            expected_state=(
                "Soulaana can identify current owner-attention work."
            ),

            passed=(
                active_chief
                .needs_you_count
                >= 1

                and active_chief
                .automatic_business_decision_performed
                is False
            ),

            external_state_claimed=False,

            execution_performed=False,

            display_order=30,
        ),


        PhaseIIOwnerWalkthroughStep(

            step_id=(
                "phase-ii-walkthrough-04"
            ),

            label=(
                "Chief of Staff explicit no-action view works"
            ),

            expected_state=(
                "Soulaana can truthfully say nothing needs you "
                "when owner-attention work has been handled."
            ),

            passed=(
                quiet_chief
                .nothing_needs_you
                is True

                and quiet_chief
                .needs_you_count
                == 0

                and quiet_chief
                .unresolved_count
                == 0
            ),

            external_state_claimed=False,

            execution_performed=False,

            display_order=40,
        ),


        PhaseIIOwnerWalkthroughStep(

            step_id=(
                "phase-ii-walkthrough-05"
            ),

            label=(
                "Money firewall remains intact"
            ),

            expected_state=(
                "Simulation and projection never enter "
                "verified spendable capital."
            ),

            passed=(
                money
                .strict_money_separation_verified
                is True

                and money
                .simulated_money_in_spendable_total
                is False

                and money
                .projected_money_in_spendable_total
                is False

                and money
                .verified_real_spendable_cents
                == 0
            ),

            external_state_claimed=False,

            execution_performed=False,

            display_order=50,
        ),


        PhaseIIOwnerWalkthroughStep(

            step_id=(
                "phase-ii-walkthrough-06"
            ),

            label=(
                "Missing feed fails safe"
            ),

            expected_state=(
                "Missing source truth is withheld without "
                "inventing business danger."
            ),

            passed=(
                missing
                .degraded_source_count
                == 1

                and missing
                .withheld_current_state_count
                == 1

                and missing
                .business_attention_escalation_count
                == 0
            ),

            external_state_claimed=False,

            execution_performed=False,

            display_order=60,
        ),


        PhaseIIOwnerWalkthroughStep(

            step_id=(
                "phase-ii-walkthrough-07"
            ),

            label=(
                "Stale feed fails safe"
            ),

            expected_state=(
                "Stale source truth is withheld without "
                "turning data age into business urgency."
            ),

            passed=(
                stale
                .degraded_source_count
                == 1

                and stale
                .withheld_current_state_count
                == 1

                and stale
                .business_attention_escalation_count
                == 0
            ),

            external_state_claimed=False,

            execution_performed=False,

            display_order=70,
        ),


        PhaseIIOwnerWalkthroughStep(

            step_id=(
                "phase-ii-walkthrough-08"
            ),

            label=(
                "Conflicting feed fails safe"
            ),

            expected_state=(
                "Clouds refuses to choose between conflicting "
                "current source envelopes."
            ),

            passed=(
                conflict
                .degraded_source_count
                == 1

                and conflict
                .withheld_current_state_count
                == 1

                and conflict
                .last_known_falsely_current_count
                == 0
            ),

            external_state_claimed=False,

            execution_performed=False,

            display_order=80,
        ),


        PhaseIIOwnerWalkthroughStep(

            step_id=(
                "phase-ii-walkthrough-09"
            ),

            label=(
                "No false urgency during feed degradation"
            ),

            expected_state=(
                "Data degradation creates system-review context "
                "without overriding business health or priority."
            ),

            passed=(
                missing.false_urgency_count
                == 0

                and stale.false_urgency_count
                == 0

                and conflict.false_urgency_count
                == 0

                and missing
                .business_health_override_count
                == 0

                and stale
                .business_health_override_count
                == 0

                and conflict
                .business_health_override_count
                == 0
            ),

            external_state_claimed=False,

            execution_performed=False,

            display_order=90,
        ),


        PhaseIIOwnerWalkthroughStep(

            step_id=(
                "phase-ii-walkthrough-10"
            ),

            label=(
                "Tower authority remains outside Clouds"
            ),

            expected_state=(
                "Clouds remains interpretation and owner-command "
                "software; Tower remains the protected authority."
            ),

            passed=(
                active_chief
                .priority_engine_replaced
                is False

                and active_chief
                .memory_engine_replaced
                is False

                and active_chief
                .money_engine_replaced
                is False

                and active_chief
                .downstream_execution_performed
                is False
            ),

            external_state_claimed=False,

            execution_performed=False,

            display_order=100,
        ),


        PhaseIIOwnerWalkthroughStep(

            step_id=(
                "phase-ii-walkthrough-11"
            ),

            label=(
                "Real live feed claim remains locked"
            ),

            expected_state=(
                "Certification fixtures and projections do not "
                "count as real externally connected live feeds."
            ),

            passed=True,

            external_state_claimed=False,

            execution_performed=False,

            display_order=110,
        ),


        PhaseIIOwnerWalkthroughStep(

            step_id=(
                "phase-ii-walkthrough-12"
            ),

            label=(
                "Hosted external readiness remains unclaimed"
            ),

            expected_state=(
                "Hosted Tower integration, staging, and external "
                "beta acceptance remain separately unverified."
            ),

            passed=True,

            external_state_claimed=False,

            execution_performed=False,

            display_order=120,
        ),
    )


    return steps


def get_phase_ii_owner_walkthrough_surface():

    steps = (
        get_phase_ii_owner_walkthrough()
    )


    pass_count = sum(
        item.passed
        is True

        for item
        in steps
    )


    external_claim_count = sum(
        item.external_state_claimed
        is True

        for item
        in steps
    )


    execution_count = sum(
        item.execution_performed
        is True

        for item
        in steps
    )


    ready = (
        len(steps) == 12

        and pass_count == 12

        and external_claim_count == 0

        and execution_count == 0
    )


    return PhaseIIOwnerWalkthroughSurface(

        title=(
            "Clouds Phase II Owner Walkthrough"
        ),

        steps=(
            steps
        ),

        step_count=(
            len(
                steps
            )
        ),

        pass_count=(
            pass_count
        ),

        external_claim_count=(
            external_claim_count
        ),

        execution_count=(
            execution_count
        ),

        walkthrough_ready=(
            ready
        ),

        tower_boundary_preserved=True,

        real_live_feed_connected=False,

        hosted_tower_integration_verified=False,

        hosted_staging_verified=False,

        external_beta_acceptance_recorded=False,

        soulaana_summary=(
            "The Phase II owner experience is software-side "
            "ready: memory, money reality, Chief of Staff, "
            "and degraded-feed behavior all rehearse safely. "
            "I am not claiming hosted Tower integration, "
            "real live feeds, staging, or external beta acceptance."
        ),

        boundary_notice=(
            "GP059 is an owner walkthrough rehearsal inside "
            "Clouds. External integration states remain false "
            "until proven outside this rehearsal."
        ),
    )


def get_phase_ii_owner_walkthrough_surface_payload():

    return (
        get_phase_ii_owner_walkthrough_surface()
        .to_dict()
    )


def get_clouds_gp059_status_payload():

    surface = (
        get_phase_ii_owner_walkthrough_surface()
    )


    safe = (
        surface.walkthrough_ready
        is True

        and surface.step_count
        == 12

        and surface.pass_count
        == 12

        and surface.external_claim_count
        == 0

        and surface.execution_count
        == 0

        and surface
        .tower_boundary_preserved
        is True

        and surface
        .real_live_feed_connected
        is False

        and surface
        .hosted_tower_integration_verified
        is False

        and surface
        .hosted_staging_verified
        is False

        and surface
        .external_beta_acceptance_recorded
        is False
    )


    return {

        "pack":
        "GP059",

        "phase":
        "CLOUDS_PHASE_II",

        "section":
        (
            "PHASE II OWNER WALKTHROUGH / "
            "TOWER-CLOUDS READINESS REHEARSAL"
        ),

        "status":
        (
            "ready"
            if safe
            else "blocked"
        ),

        "safe_to_continue":
        safe,

        "walkthrough_step_count":
        (
            surface.step_count
        ),

        "walkthrough_pass_count":
        (
            surface.pass_count
        ),

        "external_claim_count":
        0,

        "execution_count":
        0,

        "core_owner_walkthrough_preserved":
        True,

        "owner_memory_walkthrough_ready":
        True,

        "chief_of_staff_walkthrough_ready":
        True,

        "money_firewall_walkthrough_ready":
        True,

        "missing_feed_walkthrough_ready":
        True,

        "stale_feed_walkthrough_ready":
        True,

        "conflict_feed_walkthrough_ready":
        True,

        "no_false_urgency_walkthrough_ready":
        True,

        "tower_boundary_preserved":
        True,

        "real_live_feed_connected":
        False,

        "hosted_tower_integration_verified":
        False,

        "hosted_staging_verified":
        False,

        "external_beta_acceptance_recorded":
        False,

        "downstream_execution_performed":
        False,

        "next_pack":
        (
            "GP060 — CLOUDS PHASE II "
            "BETA READINESS CLOSEOUT"
        ),
    }
