"""
GP053 — Soulaana Daily Owner Brief /
What Changed While You Were Gone.

Reuses:

GP026 change memory
GP028 owner agenda
GP047 owner continuity

No parallel priority engine is created.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import tempfile

try:

    from .executive_owner_agenda_service import (
        get_owner_agenda_items,
    )

    from .operating_snapshot_history_service import (
        get_projection_snapshot_deltas,
    )

    from .owner_attention_controls_service import (
        acknowledge_attention_item,
    )

    from .owner_attention_memory_service import (
        DEFAULT_OWNER_ID,
        OwnerAttentionMemoryStore,
        utc_now_iso,
    )

    from .soulaana_continuity_memory_service import (
        evaluate_owner_continuity,
    )

    from .soulaana_owner_brief import (
        SoulaanaBriefItem,
        SoulaanaOwnerBrief,
    )

except ImportError:

    from executive_owner_agenda_service import (
        get_owner_agenda_items,
    )

    from operating_snapshot_history_service import (
        get_projection_snapshot_deltas,
    )

    from owner_attention_controls_service import (
        acknowledge_attention_item,
    )

    from owner_attention_memory_service import (
        DEFAULT_OWNER_ID,
        OwnerAttentionMemoryStore,
        utc_now_iso,
    )

    from soulaana_continuity_memory_service import (
        evaluate_owner_continuity,
    )

    from soulaana_owner_brief import (
        SoulaanaBriefItem,
        SoulaanaOwnerBrief,
    )


@lru_cache(
    maxsize=1
)
def get_chief_of_staff_agenda_items():

    return tuple(
        get_owner_agenda_items()
    )


@lru_cache(
    maxsize=1
)
def get_chief_of_staff_projection_deltas():

    return tuple(
        get_projection_snapshot_deltas()
    )


def _value(
    item,
    name,
    default=None,
):

    if hasattr(
        item,
        name,
    ):

        return getattr(
            item,
            name,
        )

    if isinstance(
        item,
        dict,
    ):

        return item.get(
            name,
            default,
        )

    return default


def _delta_by_source(
    deltas,
):

    return {
        _value(
            item,
            "source_id",
        ):
        item

        for item
        in deltas

        if _value(
            item,
            "source_id",
        )
        is not None
    }


def build_soulaana_owner_brief(
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

    delta_map = (
        _delta_by_source(
            deltas
        )
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


    brief_items = []


    for agenda_item in agenda_items:

        view = (
            continuity_map[
                agenda_item
                .agenda_item_id
            ]
        )


        delta = (
            delta_map.get(
                agenda_item
                .source_id
            )
        )


        changed = (
            delta is not None

            and _value(
                delta,
                "change_state",
                "unchanged",
            )
            == "changed"
        )


        material = (
            delta is not None

            and _value(
                delta,
                "materiality",
                "none",
            )
            == "material"
        )


        direction = (
            _value(
                delta,
                "direction",
            )

            if delta
            is not None

            else None
        )


        needs_owner_now = (
            view.should_surface
            is True

            and agenda_item
            .owner_attention_required
            is True

            and agenda_item.horizon
            in {
                "do_now",
                "today",
            }
        )


        quiet_handled = (
            view.memory_present
            is True

            and view.should_surface
            is False

            and view.continuity_state
            in {
                "quiet_unchanged",
                "snoozed",
            }
        )


        waiting_dependency = (
            agenda_item.horizon
            == "waiting"
        )


        brief_items.append(
            SoulaanaBriefItem(

                agenda_item_id=(
                    agenda_item
                    .agenda_item_id
                ),

                source_id=(
                    agenda_item
                    .source_id
                ),

                source_label=(
                    agenda_item
                    .source_label
                ),

                impacted_source_id=(
                    agenda_item
                    .impacted_source_id
                ),

                impacted_source_label=(
                    agenda_item
                    .impacted_source_label
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

                changed_since_last_snapshot=(
                    changed
                ),

                material_change=(
                    material
                ),

                change_direction=(
                    direction
                ),

                memory_present=(
                    view.memory_present
                ),

                memory_disposition=(
                    view
                    .memory_disposition
                ),

                continuity_state=(
                    view
                    .continuity_state
                ),

                needs_owner_now=(
                    needs_owner_now
                ),

                quiet_because_already_handled=(
                    quiet_handled
                ),

                waiting_dependency=(
                    waiting_dependency
                ),

                soulaana_what_changed=(
                    (
                        _value(
                            delta,
                            "soulaana_what_changed",
                        )
                        if delta
                        is not None
                        else None
                    )
                    or
                    agenda_item
                    .soulaana_what_happened
                ),

                soulaana_what_it_means=(
                    agenda_item
                    .soulaana_what_it_means
                ),

                soulaana_why_now=(
                    agenda_item
                    .soulaana_why_now
                ),

                soulaana_if_we_wait=(
                    agenda_item
                    .soulaana_if_we_wait
                ),

                soulaana_next_review=(
                    agenda_item
                    .soulaana_next_review
                ),

                automatic_action_performed=False,

                downstream_execution_performed=False,
            )
        )


    brief_items = tuple(
        brief_items
    )


    changed_sources = {
        _value(
            item,
            "source_id",
        )

        for item
        in deltas

        if (
            _value(
                item,
                "change_state",
                "unchanged",
            )
            == "changed"
        )
    }


    material_sources = {
        _value(
            item,
            "source_id",
        )

        for item
        in deltas

        if (
            _value(
                item,
                "materiality",
                "none",
            )
            == "material"
        )
    }


    needs_you_count = sum(
        item.needs_owner_now
        for item
        in brief_items
    )


    quiet_count = sum(
        item
        .quiet_because_already_handled
        for item
        in brief_items
    )


    waiting_count = sum(
        item.waiting_dependency
        for item
        in brief_items
    )


    watching_count = sum(
        item.horizon
        == "watching"
        for item
        in brief_items
    )


    can_wait_count = sum(
        item.horizon
        == "can_wait"
        for item
        in brief_items
    )


    nothing_needs_you = (
        needs_you_count
        == 0
    )


    if changed_sources:

        changed_text = (
            f"{len(changed_sources)} operating source"
            + (
                ""
                if len(changed_sources)
                == 1
                else "s"
            )
            + " changed in the current change-memory comparison."
        )

    else:

        changed_text = (
            "Nothing changed in the current change-memory comparison."
        )


    if needs_you_count:

        needs_text = (
            f"{needs_you_count} item"
            + (
                ""
                if needs_you_count
                == 1
                else "s"
            )
            + " currently justify your direct attention."
        )

    else:

        needs_text = (
            "Nothing currently requires your direct attention."
        )


    if quiet_count:

        handled_text = (
            f"I am keeping {quiet_count} previously handled item"
            + (
                ""
                if quiet_count
                == 1
                else "s"
            )
            + " quiet because the current material picture "
            "still matches your earlier instruction."
        )

    else:

        handled_text = (
            "I am not suppressing any item as previously handled right now."
        )


    can_wait_total = (
        watching_count
        + can_wait_count
        + waiting_count
    )


    if can_wait_total:

        wait_text = (
            f"{can_wait_total} item"
            + (
                ""
                if can_wait_total
                == 1
                else "s"
            )
            + " can remain outside your immediate focus."
        )

    else:

        wait_text = (
            "There is no additional lower-priority context "
            "to protect your attention from right now."
        )


    no_action_text = (
        "Nothing needs you right now. "
        "I will keep watching and only bring something back "
        "when its current contract justifies owner attention."

        if nothing_needs_you

        else

        "You do have owner-attention items, so I am not "
        "giving you a false all-clear."
    )


    return SoulaanaOwnerBrief(

        title=(
            "Soulaana Owner Brief"
        ),

        items=(
            brief_items
        ),

        agenda_item_count=(
            len(
                brief_items
            )
        ),

        changed_source_count=(
            len(
                changed_sources
            )
        ),

        material_change_count=(
            len(
                material_sources
            )
        ),

        needs_you_count=(
            needs_you_count
        ),

        quiet_handled_count=(
            quiet_count
        ),

        waiting_dependency_count=(
            waiting_count
        ),

        watching_count=(
            watching_count
        ),

        can_wait_count=(
            can_wait_count
        ),

        nothing_needs_you=(
            nothing_needs_you
        ),

        soulaana_opening=(
            "Here is what changed, what needs you, "
            "and what I am intentionally leaving alone."
        ),

        soulaana_changed_since_you_were_gone=(
            changed_text
        ),

        soulaana_needs_you=(
            needs_text
        ),

        soulaana_already_handled=(
            handled_text
        ),

        soulaana_can_wait=(
            wait_text
        ),

        soulaana_no_action=(
            no_action_text
        ),

        automatic_action_performed=False,

        downstream_execution_performed=False,

        boundary_notice=(
            "The owner brief interprets existing Clouds change, "
            "agenda, and memory contracts. It does not create "
            "downstream authority or perform actions."
        ),
    )


def get_clouds_gp053_status_payload():

    agenda = (
        get_chief_of_staff_agenda_items()
    )

    deltas = (
        get_chief_of_staff_projection_deltas()
    )


    if not agenda:

        return {
            "pack":
            "GP053",

            "status":
            "blocked",

            "safe_to_continue":
            False,
        }


    with tempfile.TemporaryDirectory() as directory:

        store = (
            OwnerAttentionMemoryStore(
                Path(directory)
                / "brief.json"
            )
        )


        active_brief = (
            build_soulaana_owner_brief(
                store,

                agenda_items=agenda,

                deltas=deltas,

                now_iso=(
                    "2026-08-14T12:00:00Z"
                ),
            )
        )


        # Prove explicit no-action path without fabricating
        # a second agenda.
        for item in agenda:

            if (
                item.owner_attention_required
                is True
            ):

                acknowledge_attention_item(
                    store,
                    item,

                    now_iso=(
                        "2026-08-14T12:01:00Z"
                    ),
                )


        quiet_brief = (
            build_soulaana_owner_brief(
                store,

                agenda_items=agenda,

                deltas=deltas,

                now_iso=(
                    "2026-08-14T12:02:00Z"
                ),
            )
        )


    safe = (
        active_brief.agenda_item_count
        == len(agenda)

        and active_brief.changed_source_count
        >= 1

        and active_brief.material_change_count
        >= 1

        and active_brief.needs_you_count
        >= 1

        and quiet_brief.nothing_needs_you
        is True

        and quiet_brief.needs_you_count
        == 0

        and "Nothing needs you"
        in quiet_brief
        .soulaana_no_action

        and active_brief
        .automatic_action_performed
        is False

        and active_brief
        .downstream_execution_performed
        is False
    )


    return {

        "pack":
        "GP053",

        "phase":
        "CLOUDS_PHASE_II",

        "section":
        (
            "DAILY OWNER BRIEF / "
            "WHAT CHANGED WHILE YOU WERE GONE"
        ),

        "status":
        (
            "ready"
            if safe
            else "blocked"
        ),

        "safe_to_continue":
        safe,

        "change_memory_reused":
        True,

        "owner_agenda_reused":
        True,

        "owner_memory_reused":
        True,

        "changed_since_you_were_gone_ready":
        True,

        "needs_you_count_ready":
        True,

        "already_handled_quieting_ready":
        True,

        "what_can_wait_ready":
        True,

        "explicit_nothing_needs_you_ready":
        True,

        "false_all_clear_prohibited":
        True,

        "automatic_action_performed":
        False,

        "downstream_execution_performed":
        False,

        "next_pack":
        (
            "GP054 — CONSEQUENCES / BLOCKERS / "
            "DEPENDENCY INTERPRETATION"
        ),
    }
