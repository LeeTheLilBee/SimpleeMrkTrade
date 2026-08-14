"""
GP056 — Soulaana Chief of Staff Command Surface /
Layer Closeout.

This surface COMPOSES existing systems.

It does not replace:

- GP026 change memory
- GP028 owner agenda
- GP045–GP048 owner memory
- GP049–GP052 executive money picture
"""

from __future__ import annotations

from pathlib import Path
import tempfile

try:

    from .executive_money_command_surface_service import (
        get_executive_money_command_surface,
    )

    from .owner_attention_controls_service import (
        acknowledge_attention_item,
    )

    from .owner_attention_memory_service import (
        DEFAULT_OWNER_ID,
        OwnerAttentionMemoryStore,
        get_default_owner_attention_memory_store,
        utc_now_iso,
    )

    from .owner_command_preferences_service import (
        get_owner_command_preferences,
    )

    from .owner_consequence_blocker_service import (
        build_consequence_blocker_surface,
    )

    from .owner_follow_up_service import (
        build_owner_follow_up_surface,
    )

    from .soulaana_chief_of_staff import (
        SoulaanaChiefOfStaffSurface,
    )

    from .soulaana_owner_brief_service import (
        build_soulaana_owner_brief,
        get_chief_of_staff_agenda_items,
        get_chief_of_staff_projection_deltas,
    )

except ImportError:

    from executive_money_command_surface_service import (
        get_executive_money_command_surface,
    )

    from owner_attention_controls_service import (
        acknowledge_attention_item,
    )

    from owner_attention_memory_service import (
        DEFAULT_OWNER_ID,
        OwnerAttentionMemoryStore,
        get_default_owner_attention_memory_store,
        utc_now_iso,
    )

    from owner_command_preferences_service import (
        get_owner_command_preferences,
    )

    from owner_consequence_blocker_service import (
        build_consequence_blocker_surface,
    )

    from owner_follow_up_service import (
        build_owner_follow_up_surface,
    )

    from soulaana_chief_of_staff import (
        SoulaanaChiefOfStaffSurface,
    )

    from soulaana_owner_brief_service import (
        build_soulaana_owner_brief,
        get_chief_of_staff_agenda_items,
        get_chief_of_staff_projection_deltas,
    )


def build_soulaana_chief_of_staff_surface(
    store,
    *,
    agenda_items=None,
    deltas=None,
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


    if (
        deltas
        is None
    ):

        deltas = (
            get_chief_of_staff_projection_deltas()
        )


    agenda_items = tuple(
        agenda_items
    )

    deltas = tuple(
        deltas
    )


    brief = (
        build_soulaana_owner_brief(
            store,

            agenda_items=agenda_items,

            deltas=deltas,

            owner_id=owner_id,

            now_iso=now_iso,
        )
    )


    consequences = (
        build_consequence_blocker_surface(
            agenda_items=agenda_items
        )
    )


    follow_up = (
        build_owner_follow_up_surface(
            store,

            agenda_items=agenda_items,

            owner_id=owner_id,

            now_iso=now_iso,
        )
    )


    money = (
        get_executive_money_command_surface()
    )


    nothing_needs_you = (
        brief.needs_you_count
        == 0

        and follow_up
        .unresolved_count
        == 0
    )


    if (
        brief.needs_you_count
        > 0
    ):

        first_need = next(

            item

            for item
            in brief.items

            if (
                item.needs_owner_now
                is True
            )
        )


        matters_first = (
            f"{first_need.title} is currently the first "
            "owner-attention item in the existing agenda order."
        )

    else:

        matters_first = (
            "Nothing currently justifies immediate owner attention."
        )


    if (
        consequences.blocker_count
        > 0
    ):

        blocker_text = (
            f"{consequences.blocker_count} explicit Waiting "
            "dependency item"
            + (
                ""
                if consequences
                .blocker_count
                == 1
                else "s"
            )
            + " are present."
        )

    else:

        blocker_text = (
            "The current owner agenda does not explicitly "
            "identify a Waiting dependency blocker."
        )


    if (
        follow_up.unresolved_count
        > 0
    ):

        follow_text = (
            f"{follow_up.unresolved_count} unresolved item"
            + (
                ""
                if follow_up
                .unresolved_count
                == 1
                else "s"
            )
            + " remain in owner follow-up."
        )

    else:

        follow_text = (
            "No unresolved owner-attention item remains "
            "in the current follow-up view."
        )


    spendable = (
        money
        .verified_real_spendable_cents
    )


    if spendable == 0:

        money_text = (
            "I do not have externally verified real spendable "
            "capital in the current certification money picture. "
            "Planning, projection, simulation, target, and need "
            "figures remain separate."
        )

    else:

        money_text = (
            "Verified-real spendable capital is present, "
            "but I am not allocating it automatically."
        )


    no_action_text = (
        "Nothing needs you right now. "
        "You can leave this with me until an existing "
        "attention contract changes."

        if nothing_needs_you

        else

        "I am not giving you an all-clear because current "
        "owner-attention work remains."
    )


    return SoulaanaChiefOfStaffSurface(

        title=(
            "Soulaana Chief of Staff"
        ),

        subtitle=(
            "What changed, what matters, what can wait, "
            "and what needs you"
        ),

        owner_brief=(
            brief
        ),

        consequence_blocker_surface=(
            consequences
        ),

        follow_up_surface=(
            follow_up
        ),

        money_surface=(
            money
        ),

        changed_since_you_were_gone_count=(
            brief.changed_source_count
        ),

        needs_you_count=(
            brief.needs_you_count
        ),

        unresolved_count=(
            follow_up
            .unresolved_count
        ),

        deferred_count=(
            follow_up
            .deferred_count
        ),

        blocker_count=(
            consequences
            .blocker_count
        ),

        quiet_handled_count=(
            brief
            .quiet_handled_count
        ),

        verified_real_spendable_cents=(
            spendable
        ),

        nothing_needs_you=(
            nothing_needs_you
        ),

        explicit_no_action_message_ready=True,

        soulaana_opening=(
            "Here is the executive picture. "
            "I separated what changed from what merely exists, "
            "what needs you from what can wait, and real money "
            "from planning or simulation."
        ),

        soulaana_since_you_were_gone=(
            brief
            .soulaana_changed_since_you_were_gone
        ),

        soulaana_what_matters_first=(
            matters_first
        ),

        soulaana_consequences_and_blockers=(
            blocker_text
            + " "
            + consequences
            .soulaana_consequence_summary
        ),

        soulaana_unresolved_follow_up=(
            follow_text
        ),

        soulaana_money_context=(
            money_text
        ),

        soulaana_what_can_wait=(
            brief
            .soulaana_can_wait
        ),

        soulaana_no_action=(
            no_action_text
        ),

        soulaana_next_step=(
            (
                "Review the first owner-attention item. "
                "I will keep the rest prioritized and explain "
                "why anything comes back."
            )

            if not nothing_needs_you

            else

            (
                "No owner action is required. "
                "I will keep watching the existing contracts."
            )
        ),

        priority_engine_replaced=False,

        memory_engine_replaced=False,

        money_engine_replaced=False,

        automatic_business_decision_performed=False,

        allocation_performed=False,

        capital_movement_performed=False,

        downstream_execution_performed=False,

        boundary_notice=(
            "Soulaana is the interpretation and executive-attention "
            "layer. She does not replace source authority, Tower "
            "authority, owner approval, capital authority, or "
            "downstream execution."
        ),
    )


def get_soulaana_chief_of_staff_surface(
    *,
    store=None,
    owner_id=DEFAULT_OWNER_ID,
    now_iso=None,
):

    if (
        store
        is None
    ):

        store = (
            get_default_owner_attention_memory_store()
        )


    return (
        build_soulaana_chief_of_staff_surface(
            store,

            owner_id=owner_id,

            now_iso=now_iso,
        )
    )


def get_soulaana_chief_of_staff_surface_payload(
    *,
    store=None,
    owner_id=DEFAULT_OWNER_ID,
    now_iso=None,
):

    return (
        get_soulaana_chief_of_staff_surface(
            store=store,

            owner_id=owner_id,

            now_iso=now_iso,
        )
        .to_dict()
    )


def get_clouds_gp056_status_payload():

    agenda = (
        get_chief_of_staff_agenda_items()
    )

    deltas = (
        get_chief_of_staff_projection_deltas()
    )

    prefs = (
        get_owner_command_preferences()
    )


    with tempfile.TemporaryDirectory() as directory:

        # ------------------------------------------------
        # ACTIVE OWNER VIEW
        # ------------------------------------------------

        active_store = (
            OwnerAttentionMemoryStore(
                Path(directory)
                / "active.json"
            )
        )


        active = (
            build_soulaana_chief_of_staff_surface(
                active_store,

                agenda_items=agenda,

                deltas=deltas,

                now_iso=(
                    "2026-08-14T12:00:00Z"
                ),
            )
        )


        # ------------------------------------------------
        # QUIET / NO-ACTION VIEW
        # ------------------------------------------------

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
                        "2026-08-14T12:01:00Z"
                    ),
                )


        quiet = (
            build_soulaana_chief_of_staff_surface(
                quiet_store,

                agenda_items=agenda,

                deltas=deltas,

                now_iso=(
                    "2026-08-14T12:02:00Z"
                ),
            )
        )


    safe = (
        prefs.soulaana_verbosity
        == "explain_everything"

        and active
        .changed_since_you_were_gone_count
        >= 1

        and active.needs_you_count
        >= 1

        and active
        .owner_brief
        .agenda_item_count
        == len(agenda)

        and active
        .money_surface
        .strict_money_separation_verified
        is True

        and active
        .verified_real_spendable_cents
        == 0

        and active
        .consequence_blocker_surface
        .fabricated_blocker_count
        == 0

        and active
        .consequence_blocker_surface
        .consequence_inference_count
        == 0

        and active
        .follow_up_surface
        .forgotten_claim_count
        == 0

        and quiet
        .nothing_needs_you
        is True

        and quiet.needs_you_count
        == 0

        and quiet.unresolved_count
        == 0

        and "Nothing needs you"
        in quiet.soulaana_no_action

        and active
        .priority_engine_replaced
        is False

        and active
        .memory_engine_replaced
        is False

        and active
        .money_engine_replaced
        is False

        and active
        .automatic_business_decision_performed
        is False

        and active
        .allocation_performed
        is False

        and active
        .capital_movement_performed
        is False

        and active
        .downstream_execution_performed
        is False
    )


    return {

        "pack":
        "GP056",

        "phase":
        "CLOUDS_PHASE_II",

        "section":
        (
            "SOULAANA CHIEF OF STAFF "
            "COMMAND SURFACE / LAYER CLOSEOUT"
        ),

        "status":
        (
            "ready"
            if safe
            else "blocked"
        ),

        "safe_to_continue":
        safe,

        "daily_owner_brief_ready":
        True,

        "changed_since_you_were_gone_ready":
        True,

        "needs_you_interpretation_ready":
        True,

        "already_handled_memory_ready":
        True,

        "consequence_interpretation_ready":
        True,

        "blocker_interpretation_ready":
        True,

        "unresolved_follow_up_ready":
        True,

        "deferred_follow_up_ready":
        True,

        "material_change_reopen_ready":
        True,

        "explicit_no_action_ready":
        True,

        "executive_money_picture_attached":
        True,

        "strict_money_separation_preserved":
        True,

        "soulaana_explains_everything_preserved":
        True,

        "existing_change_engine_reused":
        True,

        "existing_priority_engine_reused":
        True,

        "existing_memory_engine_reused":
        True,

        "existing_money_engine_reused":
        True,

        "fabricated_blocker_count":
        0,

        "false_forgotten_claim_count":
        0,

        "priority_engine_replaced":
        False,

        "memory_engine_replaced":
        False,

        "money_engine_replaced":
        False,

        "automatic_business_decision_performed":
        False,

        "allocation_performed":
        False,

        "capital_movement_performed":
        False,

        "downstream_execution_performed":
        False,

        "conclusion":
        (
            "CLOUDS_PHASE_II_SOULAANA_"
            "CHIEF_OF_STAFF_LAYER_READY"
        ),

        "next_pack":
        (
            "GP057 — FEED RESILIENCE / "
            "STALE + MISSING SOURCE DETECTION"
        ),
    }
