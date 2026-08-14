"""
GP024 — Clouds core-v1 beta-readiness closeout.

No hosted or external readiness is invented.
"""

from __future__ import annotations

try:
    from .beta_readiness_closeout import (
        CloudsBetaReadinessRecord,
        CloudsBetaReadinessSurface,
        OwnerWalkthroughStep,
    )

    from .owner_command_experience_service import (
        get_owner_command_experience,
    )

    from .owner_command_detail_drawers_service import (
        get_guided_attention_surface,
    )

    from .owner_command_preferences_service import (
        get_clouds_gp023_status_payload,
        get_owner_command_preferences,
    )

    from .operating_data_adapter_service import (
        get_operating_adapter_surface,
    )

except ImportError:
    from beta_readiness_closeout import (
        CloudsBetaReadinessRecord,
        CloudsBetaReadinessSurface,
        OwnerWalkthroughStep,
    )

    from owner_command_experience_service import (
        get_owner_command_experience,
    )

    from owner_command_detail_drawers_service import (
        get_guided_attention_surface,
    )

    from owner_command_preferences_service import (
        get_clouds_gp023_status_payload,
        get_owner_command_preferences,
    )

    from operating_data_adapter_service import (
        get_operating_adapter_surface,
    )


def get_clouds_owner_walkthrough():
    experience = get_owner_command_experience()
    detail = get_guided_attention_surface()
    prefs = get_owner_command_preferences()
    adapter = get_operating_adapter_surface()

    return (
        OwnerWalkthroughStep(
            step_id="walkthrough-01",
            label="Protected Tower launch reference exists",
            expected_state=(
                "Tower remains the protected "
                "application entry authority."
            ),
            passed=all(
                (
                    card.navigation.requires_tower
                    or card.source_id
                    == "atm_operations"
                )
                for card
                in experience.sections[-1].cards
            ),
            execution_performed=False,
            display_order=10,
        ),

        OwnerWalkthroughStep(
            step_id="walkthrough-02",
            label="Clouds owner command opens",
            expected_state=(
                "Owner sees The Clouds command surface."
            ),
            passed=(
                experience.title == "The Clouds"
                and experience.card_count == 6
            ),
            execution_performed=False,
            display_order=20,
        ),

        OwnerWalkthroughStep(
            step_id="walkthrough-03",
            label="Soulaana explains first",
            expected_state=(
                "Interpretation appears before evidence."
            ),
            passed=(
                bool(experience.hero.headline)
                and bool(experience.hero.explanation)
                and experience
                .evidence_hidden_by_default
            ),
            execution_performed=False,
            display_order=30,
        ),

        OwnerWalkthroughStep(
            step_id="walkthrough-04",
            label="Needs You identifies top focus",
            expected_state=(
                "Observatory is current top focus."
            ),
            passed=(
                experience.hero
                .top_focus_source_id
                == "observatory"
            ),
            execution_performed=False,
            display_order=40,
        ),

        OwnerWalkthroughStep(
            step_id="walkthrough-05",
            label="Keep Watching identifies ATM lane",
            expected_state=(
                "ATM Operations remains visible "
                "without outranking Observatory."
            ),
            passed=(
                detail.watch_source_ids
                == ("atm_operations",)
            ),
            execution_performed=False,
            display_order=50,
        ),

        OwnerWalkthroughStep(
            step_id="walkthrough-06",
            label="Quiet work remains collapsed",
            expected_state=(
                "Low-attention work does not dominate "
                "the owner experience."
            ),
            passed=(
                prefs.collapse_quiet_section
                is True
                and len(
                    detail.quiet_source_ids
                ) == 4
            ),
            execution_performed=False,
            display_order=60,
        ),

        OwnerWalkthroughStep(
            step_id="walkthrough-07",
            label="Detail drawers are progressive",
            expected_state=(
                "Seven detail drawers exist per source "
                "with technical evidence last."
            ),
            passed=all(
                item.drawer_count == 7
                and item.drawers[-1].kind
                == "evidence"
                for item
                in detail.experiences
            ),
            execution_performed=False,
            display_order=70,
        ),

        OwnerWalkthroughStep(
            step_id="walkthrough-08",
            label="Soulaana explains everything preference",
            expected_state=(
                "Owner preference requests full explanation."
            ),
            passed=(
                prefs.soulaana_verbosity
                == "explain_everything"
            ),
            execution_performed=False,
            display_order=80,
        ),

        OwnerWalkthroughStep(
            step_id="walkthrough-09",
            label="Operating source boundary is explicit",
            expected_state=(
                "Six approved projections exist; "
                "no fake live-feed claim."
            ),
            passed=(
                adapter.source_count == 6
                and adapter.live_source_count
                == 0
                and adapter
                .projected_source_count
                == 6
            ),
            execution_performed=False,
            display_order=90,
        ),

        OwnerWalkthroughStep(
            step_id="walkthrough-10",
            label="Protected handoff remains non-executing",
            expected_state=(
                "Clouds provides references only."
            ),
            passed=all(
                card.navigation
                .clouds_executes_navigation
                is False
                and card.execution_performed
                is False
                for card
                in experience.sections[-1].cards
            ),
            execution_performed=False,
            display_order=100,
        ),

        OwnerWalkthroughStep(
            step_id="walkthrough-11",
            label="No raw downstream execution",
            expected_state=(
                "Clouds remains interpretation "
                "and command only."
            ),
            passed=(
                experience
                .raw_source_access_performed
                is False
                and experience
                .downstream_execution_performed
                is False
                and detail
                .downstream_execution_performed
                is False
            ),
            execution_performed=False,
            display_order=110,
        ),
    )


def get_clouds_beta_readiness_record():
    gp023 = get_clouds_gp023_status_payload()
    walkthrough = get_clouds_owner_walkthrough()

    clouds_ready = (
        gp023["status"] == "ready"
        and gp023["safe_to_continue"]
        is True
        and all(
            step.passed
            for step in walkthrough
        )
        and all(
            step.execution_performed
            is False
            for step in walkthrough
        )
    )

    # External states remain deliberately false.
    hosted_tower_verified = False
    hosted_staging_verified = False
    live_feeds = False
    external_acceptance = False

    external_ready = (
        clouds_ready
        and hosted_tower_verified
        and hosted_staging_verified
        and live_feeds
        and external_acceptance
    )

    return CloudsBetaReadinessRecord(
        checkpoint_id=(
            "clouds-core-v1-gp024"
        ),
        core_pack_start="GP001",
        core_pack_end="GP024",

        owner_command_ready=clouds_ready,
        soulaana_explanation_ready=clouds_ready,
        progressive_disclosure_ready=clouds_ready,
        owner_preferences_ready=clouds_ready,
        operating_summary_boundary_ready=clouds_ready,
        tower_boundary_preserved=True,

        live_downstream_feeds_connected=(
            live_feeds
        ),
        hosted_tower_integration_verified=(
            hosted_tower_verified
        ),
        hosted_staging_verified=(
            hosted_staging_verified
        ),
        external_beta_acceptance_recorded=(
            external_acceptance
        ),

        clouds_side_ready=clouds_ready,
        externally_beta_ready=external_ready,

        conclusion=(
            "CLOUDS_CORE_V1_READY_FOR_"
            "TOWER_INTEGRATION_AND_OWNER_WALKTHROUGH"
            if clouds_ready
            else
            "CLOUDS_CORE_V1_BLOCKED"
        ),
    )


def get_clouds_beta_readiness_surface():
    walkthrough = get_clouds_owner_walkthrough()
    readiness = get_clouds_beta_readiness_record()

    return CloudsBetaReadinessSurface(
        title=(
            "Clouds Beta Readiness / "
            "Tower-Clouds Owner Walkthrough Closeout"
        ),
        walkthrough=walkthrough,
        readiness=readiness,
        walkthrough_step_count=len(
            walkthrough
        ),
        walkthrough_pass_count=sum(
            step.passed
            for step in walkthrough
        ),
        boundary_notice=(
            "GP024 certifies Clouds-side core-v1 readiness only. "
            "Hosted Tower integration, real downstream feeds, "
            "staging verification, and external beta acceptance "
            "must be proven separately."
        ),
    )


def get_clouds_beta_readiness_surface_payload():
    return (
        get_clouds_beta_readiness_surface()
        .to_dict()
    )


def get_clouds_gp024_status_payload():
    surface = (
        get_clouds_beta_readiness_surface()
    )

    readiness = surface.readiness

    safe = (
        readiness.clouds_side_ready
        is True
        and readiness.externally_beta_ready
        is False
        and surface.walkthrough_step_count
        == 11
        and surface.walkthrough_pass_count
        == 11
        and readiness.tower_boundary_preserved
        is True
        and readiness
        .live_downstream_feeds_connected
        is False
        and readiness
        .hosted_tower_integration_verified
        is False
        and readiness
        .hosted_staging_verified
        is False
        and readiness
        .external_beta_acceptance_recorded
        is False
    )

    return {
        "pack": "GP024",
        "section": (
            "BETA READINESS "
            "/ TOWER-CLOUDS OWNER "
            "WALKTHROUGH CLOSEOUT"
        ),
        "status": (
            "ready"
            if safe
            else "blocked"
        ),
        "safe_to_continue": safe,

        "core_pack_start": "GP001",
        "core_pack_end": "GP024",

        "walkthrough_step_count": (
            surface.walkthrough_step_count
        ),
        "walkthrough_pass_count": (
            surface.walkthrough_pass_count
        ),

        "clouds_side_ready": (
            readiness.clouds_side_ready
        ),

        "externally_beta_ready": (
            readiness.externally_beta_ready
        ),

        "tower_boundary_preserved": True,

        "live_downstream_feeds_connected": False,
        "hosted_tower_integration_verified": False,
        "hosted_staging_verified": False,
        "external_beta_acceptance_recorded": False,

        "conclusion": readiness.conclusion,

        "cross_app_imports_used": False,
        "downstream_execution_performed": False,

        "next_action": (
            "MOVE_TO_TOWER_CLOUDS_INTEGRATION_"
            "AND_REAL_OWNER_WALKTHROUGH"
        ),
    }
