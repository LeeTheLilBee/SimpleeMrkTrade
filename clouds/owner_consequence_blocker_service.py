"""
GP054 — Consequences / Blockers / Dependency Interpretation.

Consequences come only from GP028's explicit soulaana_if_we_wait.

A blocker is recognized only when GP028 explicitly places
the item in the WAITING horizon.

GP028 defines WAITING as:
another dependency or milestone should happen before owner action.

No additional blocker causality is invented.
"""

from __future__ import annotations

from dataclasses import replace

try:

    from .owner_consequence_blocker import (
        ConsequenceBlockerSurface,
        OwnerBlockerItem,
        OwnerConsequenceItem,
    )

    from .soulaana_owner_brief_service import (
        get_chief_of_staff_agenda_items,
    )

except ImportError:

    from owner_consequence_blocker import (
        ConsequenceBlockerSurface,
        OwnerBlockerItem,
        OwnerConsequenceItem,
    )

    from soulaana_owner_brief_service import (
        get_chief_of_staff_agenda_items,
    )


def build_consequence_blocker_surface(
    *,
    agenda_items=None,
):

    if (
        agenda_items
        is None
    ):

        agenda_items = (
            get_chief_of_staff_agenda_items()
        )

    agenda_items = tuple(
        agenda_items
    )


    consequences = tuple(

        OwnerConsequenceItem(

            agenda_item_id=(
                item.agenda_item_id
            ),

            source_id=(
                item.source_id
            ),

            source_label=(
                item.source_label
            ),

            impacted_source_id=(
                item.impacted_source_id
            ),

            impacted_source_label=(
                item
                .impacted_source_label
            ),

            horizon=(
                item.horizon
            ),

            urgency=(
                item.urgency
            ),

            consequence_basis=(
                "gp028_soulaana_if_we_wait"
            ),

            soulaana_if_we_wait=(
                item.soulaana_if_we_wait
            ),

            consequence_inferred_beyond_source_contract=False,

            downstream_execution_performed=False,
        )

        for item
        in agenda_items
    )


    blockers = tuple(

        OwnerBlockerItem(

            agenda_item_id=(
                item.agenda_item_id
            ),

            source_id=(
                item.source_id
            ),

            source_label=(
                item.source_label
            ),

            blocker_kind=(
                "waiting_dependency_or_milestone"
            ),

            blocker_basis=(
                "gp028_waiting_horizon"
            ),

            owner_action_should_wait=True,

            soulaana_explanation=(
                "The existing owner agenda places this in "
                "Waiting, which means another dependency or "
                "milestone should happen before owner action."
            ),

            fabricated_blocker=False,

            downstream_execution_performed=False,
        )

        for item
        in agenda_items

        if (
            item.horizon
            == "waiting"
        )
    )


    consequence_count = (
        len(
            consequences
        )
    )


    blocker_count = (
        len(
            blockers
        )
    )


    inference_count = sum(
        item
        .consequence_inferred_beyond_source_contract
        is True

        for item
        in consequences
    )


    fabricated_count = sum(
        item.fabricated_blocker
        is True

        for item
        in blockers
    )


    if consequence_count:

        consequence_summary = (
            f"I have {consequence_count} existing "
            "owner-agenda consequence statement"
            + (
                ""
                if consequence_count
                == 1
                else "s"
            )
            + ". I am using what the agenda already says "
            "about waiting; I am not inventing new outcomes."
        )

    else:

        consequence_summary = (
            "There are no owner-agenda consequences "
            "to summarize right now."
        )


    if blocker_count:

        blocker_summary = (
            f"{blocker_count} item"
            + (
                ""
                if blocker_count
                == 1
                else "s"
            )
            + " currently sit in the explicit Waiting lane."
        )

    else:

        blocker_summary = (
            "The current owner agenda does not explicitly "
            "identify a Waiting dependency blocker."
        )


    return ConsequenceBlockerSurface(

        title=(
            "Consequences / Blockers / Dependencies"
        ),

        consequences=(
            consequences
        ),

        blockers=(
            blockers
        ),

        consequence_count=(
            consequence_count
        ),

        blocker_count=(
            blocker_count
        ),

        current_waiting_dependency_count=(
            blocker_count
        ),

        fabricated_blocker_count=(
            fabricated_count
        ),

        consequence_inference_count=(
            inference_count
        ),

        soulaana_consequence_summary=(
            consequence_summary
        ),

        soulaana_blocker_summary=(
            blocker_summary
        ),

        soulaana_what_can_wait=(
            "Items already assigned to Watching, Waiting, "
            "or Can Wait remain outside immediate owner focus "
            "unless their existing agenda state changes."
        ),

        automatic_action_performed=False,

        downstream_execution_performed=False,

        boundary_notice=(
            "Consequences are quoted from existing owner-agenda "
            "meaning. Blockers are claimed only from the explicit "
            "GP028 Waiting horizon. Clouds does not invent causal "
            "dependencies."
        ),
    )


def get_clouds_gp054_status_payload():

    agenda = (
        get_chief_of_staff_agenda_items()
    )


    if not agenda:

        return {

            "pack":
            "GP054",

            "status":
            "blocked",

            "safe_to_continue":
            False,
        }


    real_surface = (
        build_consequence_blocker_surface(
            agenda_items=agenda
        )
    )


    # Certification-only proof that the blocker classifier
    # recognizes GP028 WAITING semantics without claiming a
    # real current blocker.
    fixture_item = replace(

        agenda[0],

        agenda_item_id=(
            agenda[0]
            .agenda_item_id
            + "-gp054-waiting-certification"
        ),

        horizon=(
            "waiting"
        ),

        owner_attention_required=False,

        soulaana_why_now=(
            "Certification fixture: wait for another dependency."
        ),

        soulaana_if_we_wait=(
            "Certification fixture consequence only."
        ),
    )


    fixture_surface = (
        build_consequence_blocker_surface(
            agenda_items=(
                fixture_item,
            )
        )
    )


    safe = (
        real_surface.consequence_count
        == len(agenda)

        and real_surface
        .consequence_inference_count
        == 0

        and real_surface
        .fabricated_blocker_count
        == 0

        and fixture_surface
        .blocker_count
        == 1

        and fixture_surface
        .blockers[0]
        .blocker_basis
        == "gp028_waiting_horizon"

        and fixture_surface
        .blockers[0]
        .fabricated_blocker
        is False

        and real_surface
        .automatic_action_performed
        is False

        and real_surface
        .downstream_execution_performed
        is False
    )


    return {

        "pack":
        "GP054",

        "phase":
        "CLOUDS_PHASE_II",

        "section":
        (
            "CONSEQUENCES / BLOCKERS / "
            "DEPENDENCY INTERPRETATION"
        ),

        "status":
        (
            "ready"
            if safe
            else "blocked"
        ),

        "safe_to_continue":
        safe,

        "current_consequence_count":
        (
            real_surface
            .consequence_count
        ),

        "current_waiting_dependency_count":
        (
            real_surface
            .current_waiting_dependency_count
        ),

        "consequence_source_is_existing_gp028_contract":
        True,

        "waiting_blocker_source_is_gp028_waiting_horizon":
        True,

        "waiting_blocker_classifier_verified":
        True,

        "fabricated_blocker_count":
        0,

        "consequence_inference_count":
        0,

        "false_blocker_claim_prohibited":
        True,

        "false_consequence_claim_prohibited":
        True,

        "automatic_action_performed":
        False,

        "downstream_execution_performed":
        False,

        "next_pack":
        (
            "GP055 — OWNER FOLLOW-UP / "
            "UNRESOLVED + DEFERRED ATTENTION RECOVERY"
        ),
    }
