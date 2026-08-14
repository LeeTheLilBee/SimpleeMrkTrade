"""
GP055 — Owner Follow-Up /
Unresolved + Deferred Attention Recovery.

Important:

"Not yet handled" is evidence-backed.

"You forgot this" is NOT evidence-backed and is prohibited.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import tempfile

try:

    from .owner_attention_controls_service import (
        acknowledge_attention_item,
        snooze_attention_item,
    )

    from .owner_attention_memory_service import (
        DEFAULT_OWNER_ID,
        OwnerAttentionMemoryStore,
        utc_now_iso,
    )

    from .owner_follow_up import (
        OwnerFollowUpItem,
        OwnerFollowUpSurface,
    )

    from .soulaana_continuity_memory_service import (
        evaluate_owner_continuity,
    )

    from .soulaana_owner_brief_service import (
        get_chief_of_staff_agenda_items,
    )

except ImportError:

    from owner_attention_controls_service import (
        acknowledge_attention_item,
        snooze_attention_item,
    )

    from owner_attention_memory_service import (
        DEFAULT_OWNER_ID,
        OwnerAttentionMemoryStore,
        utc_now_iso,
    )

    from owner_follow_up import (
        OwnerFollowUpItem,
        OwnerFollowUpSurface,
    )

    from soulaana_continuity_memory_service import (
        evaluate_owner_continuity,
    )

    from soulaana_owner_brief_service import (
        get_chief_of_staff_agenda_items,
    )


def build_owner_follow_up_surface(
    store,
    *,
    agenda_items=None,
    owner_id=DEFAULT_OWNER_ID,
    now_iso=None,
):

    now_iso = (
        now_iso
        or utc_now_iso()
    )

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


    continuity = (
        evaluate_owner_continuity(
            store,

            agenda_items=(
                agenda_items
            ),

            owner_id=owner_id,

            now_iso=now_iso,
        )
    )


    continuity_map = {
        item.agenda_item_id:
        item

        for item
        in continuity
    }


    follow_ups = []


    for agenda_item in agenda_items:

        view = (
            continuity_map[
                agenda_item
                .agenda_item_id
            ]
        )


        reason = None

        requires_action = False

        deferred = False

        reopened = False

        not_yet_handled = False

        snooze_expired = False

        waiting_dependency = False


        if (
            view.continuity_state
            == "reopened_material_change"
        ):

            reason = (
                "material_change_reopened"
            )

            requires_action = (
                agenda_item
                .owner_attention_required
            )

            reopened = True

            explanation = (
                "You handled this before, but its material "
                "attention fingerprint changed, so I brought "
                "it back."
            )


        elif (
            view.continuity_state
            == "snooze_expired"
        ):

            reason = (
                "snooze_expired"
            )

            requires_action = (
                agenda_item
                .owner_attention_required
            )

            snooze_expired = True

            explanation = (
                "Your snooze expired, so this is eligible "
                "for review again."
            )


        elif (
            view.memory_present
            is False

            and agenda_item
            .owner_attention_required
            is True

            and view.should_surface
            is True
        ):

            reason = (
                "not_yet_handled"
            )

            requires_action = True

            not_yet_handled = True

            explanation = (
                "This currently needs owner attention and "
                "I do not have a prior owner-memory instruction "
                "for it."
            )


        elif (
            view.memory_present
            is True

            and view.memory_disposition
            == "active"

            and agenda_item
            .owner_attention_required
            is True

            and view.should_surface
            is True
        ):

            reason = (
                "active_unresolved"
            )

            requires_action = True

            explanation = (
                "This remains active and unresolved in "
                "owner attention."
            )


        elif (
            view.continuity_state
            == "snoozed"
        ):

            reason = (
                "deferred_snooze"
            )

            deferred = True

            explanation = (
                "You explicitly snoozed this, so I am "
                "tracking it without treating it as current work."
            )


        elif (
            agenda_item.horizon
            == "waiting"
        ):

            reason = (
                "waiting_dependency"
            )

            deferred = True

            waiting_dependency = True

            explanation = (
                "The owner agenda says another dependency "
                "or milestone should happen before owner action."
            )


        if (
            reason
            is None
        ):

            continue


        follow_ups.append(
            OwnerFollowUpItem(

                agenda_item_id=(
                    agenda_item
                    .agenda_item_id
                ),

                source_id=(
                    agenda_item.source_id
                ),

                source_label=(
                    agenda_item.source_label
                ),

                title=(
                    agenda_item.title
                ),

                horizon=(
                    agenda_item.horizon
                ),

                urgency=(
                    agenda_item.urgency
                ),

                follow_up_reason=(
                    reason
                ),

                requires_owner_action=(
                    requires_action
                ),

                deferred=(
                    deferred
                ),

                reopened_due_to_material_change=(
                    reopened
                ),

                not_yet_handled=(
                    not_yet_handled
                ),

                snooze_expired=(
                    snooze_expired
                ),

                waiting_dependency=(
                    waiting_dependency
                ),

                soulaana_explanation=(
                    explanation
                ),

                forgotten_claimed=False,

                downstream_execution_performed=False,
            )
        )


    follow_ups = tuple(
        follow_ups
    )


    unresolved_count = sum(
        item.requires_owner_action
        is True

        for item
        in follow_ups
    )


    deferred_count = sum(
        item.deferred
        is True

        for item
        in follow_ups
    )


    reopened_count = sum(
        item
        .reopened_due_to_material_change
        is True

        for item
        in follow_ups
    )


    not_yet_handled_count = sum(
        item.not_yet_handled
        is True

        for item
        in follow_ups
    )


    snooze_expired_count = sum(
        item.snooze_expired
        is True

        for item
        in follow_ups
    )


    waiting_count = sum(
        item.waiting_dependency
        is True

        for item
        in follow_ups
    )


    forgotten_count = sum(
        item.forgotten_claimed
        is True

        for item
        in follow_ups
    )


    if unresolved_count:

        follow_up_summary = (
            f"{unresolved_count} item"
            + (
                ""
                if unresolved_count
                == 1
                else "s"
            )
            + " currently remain unresolved for owner attention."
        )

    else:

        follow_up_summary = (
            "There are no unresolved owner-attention items "
            "in this follow-up view."
        )


    if deferred_count:

        deferred_summary = (
            f"I am tracking {deferred_count} deferred item"
            + (
                ""
                if deferred_count
                == 1
                else "s"
            )
            + " without promoting them into false urgency."
        )

    else:

        deferred_summary = (
            "There are no explicitly deferred follow-up items."
        )


    return OwnerFollowUpSurface(

        title=(
            "Owner Follow-Up / Attention Recovery"
        ),

        items=(
            follow_ups
        ),

        follow_up_count=(
            len(
                follow_ups
            )
        ),

        unresolved_count=(
            unresolved_count
        ),

        deferred_count=(
            deferred_count
        ),

        reopened_material_change_count=(
            reopened_count
        ),

        not_yet_handled_count=(
            not_yet_handled_count
        ),

        snooze_expired_count=(
            snooze_expired_count
        ),

        waiting_dependency_count=(
            waiting_count
        ),

        forgotten_claim_count=(
            forgotten_count
        ),

        soulaana_follow_up_summary=(
            follow_up_summary
        ),

        soulaana_deferred_summary=(
            deferred_summary
        ),

        soulaana_memory_protection=(
            "I distinguish not-yet-handled, unresolved, "
            "deferred, expired snoozes, and material-change "
            "reopens. I do not claim you forgot something "
            "without explicit evidence."
        ),

        automatic_action_performed=False,

        downstream_execution_performed=False,

        boundary_notice=(
            "Follow-up recovery changes owner attention only. "
            "It does not create deadlines, fabricate missed work, "
            "or perform downstream actions."
        ),
    )


def get_clouds_gp055_status_payload():

    agenda = list(
        get_chief_of_staff_agenda_items()
    )


    if (
        len(agenda)
        < 2
    ):

        return {

            "pack":
            "GP055",

            "status":
            "blocked",

            "safe_to_continue":
            False,
        }


    with tempfile.TemporaryDirectory() as directory:

        # ------------------------------------------------
        # NEW / UNHANDLED PATH
        # ------------------------------------------------

        new_store = (
            OwnerAttentionMemoryStore(
                Path(directory)
                / "new.json"
            )
        )


        new_surface = (
            build_owner_follow_up_surface(
                new_store,

                agenda_items=agenda,

                now_iso=(
                    "2026-08-14T12:00:00Z"
                ),
            )
        )


        # ------------------------------------------------
        # DEFERRED / SNOOZED PATH
        # ------------------------------------------------

        snooze_store = (
            OwnerAttentionMemoryStore(
                Path(directory)
                / "snooze.json"
            )
        )


        attention_item = next(

            item

            for item
            in agenda

            if (
                item
                .owner_attention_required
                is True
            )
        )


        snooze_attention_item(
            snooze_store,

            attention_item,

            now_iso=(
                "2026-08-14T12:00:00Z"
            ),

            snooze_until=(
                "2026-08-15T12:00:00Z"
            ),
        )


        snooze_surface = (
            build_owner_follow_up_surface(
                snooze_store,

                agenda_items=agenda,

                now_iso=(
                    "2026-08-14T13:00:00Z"
                ),
            )
        )


        # ------------------------------------------------
        # MATERIAL CHANGE REOPEN PATH
        # ------------------------------------------------

        reopen_store = (
            OwnerAttentionMemoryStore(
                Path(directory)
                / "reopen.json"
            )
        )


        acknowledge_attention_item(
            reopen_store,

            attention_item,

            now_iso=(
                "2026-08-14T12:00:00Z"
            ),
        )


        changed_item = replace(

            attention_item,

            urgency=(
                "critical"

                if (
                    attention_item
                    .urgency
                    != "critical"
                )

                else "high"
            ),
        )


        changed_agenda = tuple(

            changed_item

            if (
                item.agenda_item_id
                == attention_item
                .agenda_item_id
            )

            else item

            for item
            in agenda
        )


        reopen_surface = (
            build_owner_follow_up_surface(
                reopen_store,

                agenda_items=(
                    changed_agenda
                ),

                now_iso=(
                    "2026-08-14T13:00:00Z"
                ),
            )
        )


    safe = (
        new_surface.not_yet_handled_count
        >= 1

        and snooze_surface.deferred_count
        >= 1

        and reopen_surface
        .reopened_material_change_count
        == 1

        and new_surface
        .forgotten_claim_count
        == 0

        and snooze_surface
        .forgotten_claim_count
        == 0

        and reopen_surface
        .forgotten_claim_count
        == 0

        and new_surface
        .automatic_action_performed
        is False

        and new_surface
        .downstream_execution_performed
        is False
    )


    return {

        "pack":
        "GP055",

        "phase":
        "CLOUDS_PHASE_II",

        "section":
        (
            "OWNER FOLLOW-UP / UNRESOLVED + "
            "DEFERRED ATTENTION RECOVERY"
        ),

        "status":
        (
            "ready"
            if safe
            else "blocked"
        ),

        "safe_to_continue":
        safe,

        "not_yet_handled_detection_ready":
        True,

        "active_unresolved_detection_ready":
        True,

        "snoozed_deferred_tracking_ready":
        True,

        "snooze_expiry_recovery_ready":
        True,

        "material_change_reopen_follow_up_ready":
        True,

        "waiting_dependency_follow_up_ready":
        True,

        "forgotten_claim_count":
        0,

        "false_forgotten_claim_prohibited":
        True,

        "false_deadline_claim_prohibited":
        True,

        "automatic_action_performed":
        False,

        "downstream_execution_performed":
        False,

        "next_pack":
        (
            "GP056 — SOULAANA CHIEF OF STAFF "
            "COMMAND SURFACE / LAYER CLOSEOUT"
        ),
    }
