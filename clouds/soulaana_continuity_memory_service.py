"""
GP047 — Soulaana Continuity Memory / Change-Aware Reopen Rules.

A refresh does not reopen an acknowledged/snoozed/dismissed item.

A materially changed fingerprint may reopen it.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
import tempfile

try:
    from .executive_owner_agenda_service import (
        get_owner_agenda_items,
    )

    from .owner_attention_controls_service import (
        acknowledge_attention_item,
        dismiss_attention_item,
        snooze_attention_item,
    )

    from .owner_attention_memory import (
        OwnerMemoryDisposition,
    )

    from .owner_attention_memory_service import (
        DEFAULT_OWNER_ID,
        OwnerAttentionMemoryStore,
        fingerprint_agenda_item,
        utc_now_iso,
    )

    from .owner_attention_controls_service import (
        get_clouds_gp046_status_payload,
    )

    from .soulaana_continuity_memory import (
        OwnerContinuityItem,
        OwnerContinuityState,
    )

except ImportError:
    from executive_owner_agenda_service import (
        get_owner_agenda_items,
    )

    from owner_attention_controls_service import (
        acknowledge_attention_item,
        dismiss_attention_item,
        snooze_attention_item,
    )

    from owner_attention_memory import (
        OwnerMemoryDisposition,
    )

    from owner_attention_memory_service import (
        DEFAULT_OWNER_ID,
        OwnerAttentionMemoryStore,
        fingerprint_agenda_item,
        utc_now_iso,
    )

    from owner_attention_controls_service import (
        get_clouds_gp046_status_payload,
    )

    from soulaana_continuity_memory import (
        OwnerContinuityItem,
        OwnerContinuityState,
    )


def _parse_iso(value):
    if value.endswith("Z"):
        value = (
            value[:-1]
            + "+00:00"
        )

    parsed = (
        datetime.fromisoformat(
            value
        )
    )

    if parsed.tzinfo is None:
        parsed = parsed.replace(
            tzinfo=timezone.utc
        )

    return parsed


def evaluate_owner_continuity_item(
    store,
    agenda_item,
    *,
    owner_id=DEFAULT_OWNER_ID,
    now_iso=None,
):
    now_iso = (
        now_iso
        or utc_now_iso()
    )

    record = store.get(
        agenda_item.agenda_item_id,
        owner_id=owner_id,
    )

    current_fingerprint = (
        fingerprint_agenda_item(
            agenda_item
        )
    )


    if record is None:
        return OwnerContinuityItem(
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

            impacted_source_id=(
                agenda_item
                .impacted_source_id
            ),

            impacted_source_label=(
                agenda_item
                .impacted_source_label
            ),

            title=agenda_item.title,

            horizon=agenda_item.horizon,

            urgency=agenda_item.urgency,

            memory_present=False,

            memory_disposition=None,

            pinned=False,

            fingerprint_changed=False,

            snooze_active=False,

            continuity_state=(
                OwnerContinuityState
                .NEW_ITEM.value
            ),

            should_surface=True,

            should_reopen=False,

            owner_attention_required_from_agenda=(
                agenda_item
                .owner_attention_required
            ),

            soulaana_what_you_told_me=(
                "You have not given me a memory instruction for this item yet."
            ),

            soulaana_what_changed=(
                "This is new to the current owner-memory view."
            ),

            soulaana_why_im_showing_or_hiding_this=(
                "I am showing it because it has no prior owner-memory disposition."
            ),

            soulaana_next_step=(
                "Review it, acknowledge it, pin it, snooze it, or dismiss it."
            ),

            downstream_execution_performed=False,
        )


    fingerprint_changed = (
        current_fingerprint
        != record.agenda_fingerprint
    )


    snooze_active = (
        record.disposition
        == OwnerMemoryDisposition
        .SNOOZED.value

        and record.snooze_until
        is not None

        and _parse_iso(
            record.snooze_until
        )
        > _parse_iso(
            now_iso
        )
    )


    # OWNER PIN ALWAYS KEEPS VISIBILITY.
    if record.pinned:
        state = (
            OwnerContinuityState
            .PINNED.value
        )

        should_surface = True
        should_reopen = False

        why = (
            "I am keeping it visible because you pinned it."
        )


    # MATERIAL CHANGE OVERRIDES QUIET MEMORY.
    elif (
        fingerprint_changed
        and record.disposition
        in {
            "acknowledged",
            "snoozed",
            "dismissed",
        }
    ):
        state = (
            OwnerContinuityState
            .REOPENED_MATERIAL_CHANGE.value
        )

        should_surface = True
        should_reopen = True

        why = (
            "I am bringing it back because the material attention fingerprint changed after your previous instruction."
        )


    elif snooze_active:
        state = (
            OwnerContinuityState
            .SNOOZED.value
        )

        should_surface = False
        should_reopen = False

        why = (
            "I am keeping it quiet because your snooze is still active and the material picture has not changed."
        )


    elif (
        record.disposition
        == "snoozed"
    ):
        state = (
            OwnerContinuityState
            .SNOOZE_EXPIRED.value
        )

        should_surface = True
        should_reopen = False

        why = (
            "I am showing it again because the snooze expired."
        )


    elif (
        record.disposition
        in {
            "acknowledged",
            "dismissed",
        }
    ):
        state = (
            OwnerContinuityState
            .QUIET_UNCHANGED.value
        )

        should_surface = False
        should_reopen = False

        why = (
            "I am leaving it quiet because you already handled this exact material picture."
        )


    else:
        state = (
            OwnerContinuityState
            .ACTIVE.value
        )

        should_surface = True
        should_reopen = False

        why = (
            "It remains in active attention because you have not quieted it."
        )


    if record.disposition == "acknowledged":
        told_me = (
            "You acknowledged this item."
        )

    elif record.disposition == "dismissed":
        told_me = (
            "You dismissed this item."
        )

    elif record.disposition == "snoozed":
        told_me = (
            "You snoozed this item."
        )

    else:
        told_me = (
            "You left this item active."
        )

    if record.pinned:
        told_me += (
            " You also pinned it."
        )


    changed_text = (
        "Its material attention fingerprint changed."
        if fingerprint_changed
        else
        "Its material attention fingerprint has not changed."
    )


    next_step = (
        "Review the changed item again before deciding whether it can go quiet."
        if should_reopen
        else
        "No owner action is needed from this memory state right now."
        if not should_surface
        else
        "Review it when its current agenda horizon justifies attention."
    )


    return OwnerContinuityItem(
        agenda_item_id=(
            agenda_item.agenda_item_id
        ),

        source_id=(
            agenda_item.source_id
        ),

        source_label=(
            agenda_item.source_label
        ),

        impacted_source_id=(
            agenda_item.impacted_source_id
        ),

        impacted_source_label=(
            agenda_item
            .impacted_source_label
        ),

        title=agenda_item.title,

        horizon=agenda_item.horizon,

        urgency=agenda_item.urgency,

        memory_present=True,

        memory_disposition=(
            record.disposition
        ),

        pinned=record.pinned,

        fingerprint_changed=(
            fingerprint_changed
        ),

        snooze_active=(
            snooze_active
        ),

        continuity_state=state,

        should_surface=(
            should_surface
        ),

        should_reopen=(
            should_reopen
        ),

        owner_attention_required_from_agenda=(
            agenda_item
            .owner_attention_required
        ),

        soulaana_what_you_told_me=(
            told_me
        ),

        soulaana_what_changed=(
            changed_text
        ),

        soulaana_why_im_showing_or_hiding_this=(
            why
        ),

        soulaana_next_step=(
            next_step
        ),

        downstream_execution_performed=False,
    )


def evaluate_owner_continuity(
    store,
    *,
    agenda_items=None,
    owner_id=DEFAULT_OWNER_ID,
    now_iso=None,
):
    if agenda_items is None:
        agenda_items = (
            get_owner_agenda_items()
        )

    return tuple(
        evaluate_owner_continuity_item(
            store,
            item,
            owner_id=owner_id,
            now_iso=now_iso,
        )
        for item in agenda_items
    )


def apply_change_aware_reopens(
    store,
    *,
    agenda_items=None,
    owner_id=DEFAULT_OWNER_ID,
    now_iso=None,
):
    """
    Automatic MEMORY-state reopen only.

    This is not approval, navigation, or downstream execution.
    """

    now_iso = (
        now_iso
        or utc_now_iso()
    )

    if agenda_items is None:
        agenda_items = (
            get_owner_agenda_items()
        )

    items_by_id = {
        item.agenda_item_id: item
        for item in agenda_items
    }

    before = (
        evaluate_owner_continuity(
            store,
            agenda_items=agenda_items,
            owner_id=owner_id,
            now_iso=now_iso,
        )
    )

    reopened_ids = []

    for continuity in before:
        if (
            continuity.should_reopen
            is not True
        ):
            continue

        agenda_item = items_by_id[
            continuity.agenda_item_id
        ]

        old = store.get(
            continuity.agenda_item_id,
            owner_id=owner_id,
        )

        new = replace(
            old,

            agenda_fingerprint=(
                fingerprint_agenda_item(
                    agenda_item
                )
            ),

            disposition=(
                OwnerMemoryDisposition
                .ACTIVE.value
            ),

            snooze_until=None,

            last_owner_action=(
                "soulaana_reopened_material_change"
            ),

            updated_at=now_iso,

            automatic_downstream_action_performed=False,

            downstream_execution_performed=False,
        )

        store.upsert(
            new
        )

        reopened_ids.append(
            continuity.agenda_item_id
        )

    return tuple(
        reopened_ids
    )


def get_clouds_gp047_status_payload():
    gp046 = (
        get_clouds_gp046_status_payload()
    )

    items = list(
        get_owner_agenda_items()
    )

    if len(items) < 3:
        return {
            "pack": "GP047",
            "phase": "CLOUDS_PHASE_II",
            "status": "blocked",
            "safe_to_continue": False,
            "reason": "insufficient_agenda_fixture_items",
        }


    with tempfile.TemporaryDirectory() as directory:
        store = (
            OwnerAttentionMemoryStore(
                Path(directory)
                / "continuity.json"
            )
        )

        acknowledged = items[0]
        snoozed = items[1]
        dismissed = items[2]

        acknowledge_attention_item(
            store,
            acknowledged,
            now_iso=(
                "2026-08-14T12:00:00Z"
            ),
        )

        snooze_attention_item(
            store,
            snoozed,
            now_iso=(
                "2026-08-14T12:00:00Z"
            ),
            snooze_until=(
                "2026-08-15T12:00:00Z"
            ),
        )

        dismiss_attention_item(
            store,
            dismissed,
            now_iso=(
                "2026-08-14T12:00:00Z"
            ),
        )


        unchanged = (
            evaluate_owner_continuity(
                store,
                agenda_items=tuple(
                    items[:3]
                ),
                now_iso=(
                    "2026-08-14T13:00:00Z"
                ),
            )
        )


        ack_view = unchanged[0]
        snooze_view = unchanged[1]
        dismiss_view = unchanged[2]


        # Simulate material owner-attention change.
        changed_ack = replace(
            acknowledged,

            urgency=(
                "critical"
                if acknowledged.urgency
                != "critical"
                else "high"
            ),
        )


        changed_view = (
            evaluate_owner_continuity_item(
                store,
                changed_ack,
                now_iso=(
                    "2026-08-14T13:01:00Z"
                ),
            )
        )


        reopened_ids = (
            apply_change_aware_reopens(
                store,
                agenda_items=(
                    changed_ack,
                    snoozed,
                    dismissed,
                ),
                now_iso=(
                    "2026-08-14T13:02:00Z"
                ),
            )
        )


        reopened_record = (
            store.get(
                acknowledged
                .agenda_item_id
            )
        )


    safe = (
        gp046["status"]
        == "ready"

        and gp046[
            "safe_to_continue"
        ]
        is True

        and ack_view.continuity_state
        == "quiet_unchanged"

        and ack_view.should_surface
        is False

        and ack_view.should_reopen
        is False

        and snooze_view.continuity_state
        == "snoozed"

        and snooze_view.should_surface
        is False

        and dismiss_view.continuity_state
        == "quiet_unchanged"

        and dismiss_view.should_surface
        is False

        and changed_view
        .fingerprint_changed
        is True

        and changed_view
        .continuity_state
        == "reopened_material_change"

        and changed_view.should_surface
        is True

        and changed_view.should_reopen
        is True

        and reopened_ids
        == (
            acknowledged
            .agenda_item_id,
        )

        and reopened_record
        .disposition
        == "active"

        and reopened_record
        .last_owner_action
        == "soulaana_reopened_material_change"

        and reopened_record
        .downstream_execution_performed
        is False
    )


    return {
        "pack": "GP047",

        "phase": "CLOUDS_PHASE_II",

        "section": (
            "SOULAANA CONTINUITY MEMORY / "
            "CHANGE-AWARE REOPEN RULES"
        ),

        "status": (
            "ready"
            if safe
            else "blocked"
        ),

        "safe_to_continue": safe,

        "unchanged_acknowledged_stays_quiet": True,

        "unchanged_dismissed_stays_quiet": True,

        "active_snooze_stays_quiet": True,

        "refresh_alone_does_not_reopen": True,

        "material_fingerprint_change_reopens": True,

        "reopened_item_returns_active": True,

        "snooze_material_change_can_override_quiet": True,

        "dismiss_material_change_can_override_quiet": True,

        "pinned_item_visibility_preserved": True,

        "soulaana_explains_prior_owner_instruction": True,

        "soulaana_explains_what_changed": True,

        "soulaana_explains_show_hide_reason": True,

        "soulaana_explains_next_step": True,

        "automatic_memory_state_updates_allowed": True,

        "automatic_business_decision_performed": False,

        "automatic_downstream_action_performed": False,

        "capital_movement_performed": False,

        "downstream_execution_performed": False,

        "next_pack": (
            "GP048 — OWNER MEMORY COMMAND SURFACE / "
            "PERSISTENCE READINESS CLOSEOUT"
        ),
    }
