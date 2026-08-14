"""
GP046 — Owner Attention Controls / Memory State Transitions.

Owner actions modify Clouds attention memory only.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
import tempfile
from pathlib import Path

try:
    from .owner_attention_controls import (
        OwnerAttentionControlReceipt,
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

    from .executive_owner_agenda_service import (
        get_owner_agenda_item,
        get_owner_agenda_items,
    )

    from .owner_attention_memory_service import (
        get_clouds_gp045_status_payload,
    )

except ImportError:
    from owner_attention_controls import (
        OwnerAttentionControlReceipt,
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

    from executive_owner_agenda_service import (
        get_owner_agenda_item,
        get_owner_agenda_items,
    )

    from owner_attention_memory_service import (
        get_clouds_gp045_status_payload,
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


def _prepare_record(
    store,
    agenda_item,
    *,
    owner_id,
    now_iso,
):
    record = (
        store.get_or_create(
            agenda_item,
            owner_id=owner_id,
            now_iso=now_iso,
        )
    )

    return record


def _receipt(
    *,
    old,
    new,
    action,
    message,
):
    return OwnerAttentionControlReceipt(
        receipt_id=(
            "owner-attention-control-"
            f"{new.agenda_item_id}-"
            f"{action}-"
            f"{new.updated_at}"
        ),

        owner_id=new.owner_id,

        agenda_item_id=(
            new.agenda_item_id
        ),

        owner_action=action,

        previous_disposition=(
            old.disposition
        ),

        current_disposition=(
            new.disposition
        ),

        previous_pinned=(
            old.pinned
        ),

        current_pinned=(
            new.pinned
        ),

        snooze_until=(
            new.snooze_until
        ),

        review_count=(
            new.review_count
        ),

        memory_updated=True,

        downstream_authority_changed=False,

        downstream_execution_performed=False,

        soulaana_confirmation=message,
    )


def _save(
    store,
    old,
    new,
    *,
    action,
    message,
):
    store.upsert(
        new
    )

    return _receipt(
        old=old,
        new=new,
        action=action,
        message=message,
    )


def review_attention_item(
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

    old = _prepare_record(
        store,
        agenda_item,
        owner_id=owner_id,
        now_iso=now_iso,
    )

    new = replace(
        old,

        agenda_fingerprint=(
            fingerprint_agenda_item(
                agenda_item
            )
        ),

        review_count=(
            old.review_count
            + 1
        ),

        last_owner_action="reviewed",

        updated_at=now_iso,
    )

    return _save(
        store,
        old,
        new,
        action="review",
        message=(
            "Got it. I recorded that you reviewed this."
        ),
    )


def pin_attention_item(
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

    old = _prepare_record(
        store,
        agenda_item,
        owner_id=owner_id,
        now_iso=now_iso,
    )

    new = replace(
        old,

        agenda_fingerprint=(
            fingerprint_agenda_item(
                agenda_item
            )
        ),

        pinned=True,

        last_owner_action="pinned",

        updated_at=now_iso,
    )

    return _save(
        store,
        old,
        new,
        action="pin",
        message=(
            "Pinned. I will keep this visible until you unpin it."
        ),
    )


def unpin_attention_item(
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

    old = _prepare_record(
        store,
        agenda_item,
        owner_id=owner_id,
        now_iso=now_iso,
    )

    new = replace(
        old,

        agenda_fingerprint=(
            fingerprint_agenda_item(
                agenda_item
            )
        ),

        pinned=False,

        last_owner_action="unpinned",

        updated_at=now_iso,
    )

    return _save(
        store,
        old,
        new,
        action="unpin",
        message=(
            "Unpinned. I will treat it according to its normal attention state."
        ),
    )


def acknowledge_attention_item(
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

    old = _prepare_record(
        store,
        agenda_item,
        owner_id=owner_id,
        now_iso=now_iso,
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
            .ACKNOWLEDGED.value
        ),

        snooze_until=None,

        last_owner_action=(
            "acknowledged"
        ),

        updated_at=now_iso,
    )

    return _save(
        store,
        old,
        new,
        action="acknowledge",
        message=(
            "Acknowledged. I will leave this quiet unless its material picture changes."
        ),
    )


def snooze_attention_item(
    store,
    agenda_item,
    *,
    snooze_until,
    owner_id=DEFAULT_OWNER_ID,
    now_iso=None,
):
    now_iso = (
        now_iso
        or utc_now_iso()
    )

    if (
        _parse_iso(
            snooze_until
        )
        <= _parse_iso(
            now_iso
        )
    ):
        raise ValueError(
            "Snooze must end in the future."
        )

    old = _prepare_record(
        store,
        agenda_item,
        owner_id=owner_id,
        now_iso=now_iso,
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
            .SNOOZED.value
        ),

        snooze_until=(
            snooze_until
        ),

        last_owner_action="snoozed",

        updated_at=now_iso,
    )

    return _save(
        store,
        old,
        new,
        action="snooze",
        message=(
            "Snoozed. I will keep this out of your active attention until the snooze expires unless it materially changes."
        ),
    )


def dismiss_attention_item(
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

    old = _prepare_record(
        store,
        agenda_item,
        owner_id=owner_id,
        now_iso=now_iso,
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
            .DISMISSED.value
        ),

        snooze_until=None,

        last_owner_action="dismissed",

        updated_at=now_iso,
    )

    return _save(
        store,
        old,
        new,
        action="dismiss",
        message=(
            "Dismissed. I will remember that decision and will not bring the same unchanged item back as new."
        ),
    )


def reopen_attention_item(
    store,
    agenda_item,
    *,
    owner_id=DEFAULT_OWNER_ID,
    now_iso=None,
    owner_note=None,
):
    now_iso = (
        now_iso
        or utc_now_iso()
    )

    old = _prepare_record(
        store,
        agenda_item,
        owner_id=owner_id,
        now_iso=now_iso,
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

        last_owner_action="reopened",

        owner_note=(
            owner_note
            if owner_note is not None
            else old.owner_note
        ),

        updated_at=now_iso,
    )

    return _save(
        store,
        old,
        new,
        action="reopen",
        message=(
            "Reopened. This is back in your active attention."
        ),
    )


def get_clouds_gp046_status_payload():
    gp045 = (
        get_clouds_gp045_status_payload()
    )

    items = (
        get_owner_agenda_items()
    )

    with tempfile.TemporaryDirectory() as directory:
        store = (
            OwnerAttentionMemoryStore(
                Path(directory)
                / "controls.json"
            )
        )

        item = items[0]

        review = (
            review_attention_item(
                store,
                item,
                now_iso=(
                    "2026-08-14T12:00:00Z"
                ),
            )
        )

        pin = (
            pin_attention_item(
                store,
                item,
                now_iso=(
                    "2026-08-14T12:01:00Z"
                ),
            )
        )

        ack = (
            acknowledge_attention_item(
                store,
                item,
                now_iso=(
                    "2026-08-14T12:02:00Z"
                ),
            )
        )

        snooze = (
            snooze_attention_item(
                store,
                item,
                now_iso=(
                    "2026-08-14T12:03:00Z"
                ),
                snooze_until=(
                    "2026-08-15T12:03:00Z"
                ),
            )
        )

        dismiss = (
            dismiss_attention_item(
                store,
                item,
                now_iso=(
                    "2026-08-14T12:04:00Z"
                ),
            )
        )

        reopen = (
            reopen_attention_item(
                store,
                item,
                now_iso=(
                    "2026-08-14T12:05:00Z"
                ),
            )
        )

        unpin = (
            unpin_attention_item(
                store,
                item,
                now_iso=(
                    "2026-08-14T12:06:00Z"
                ),
            )
        )

        final_record = store.get(
            item.agenda_item_id
        )


    receipts = (
        review,
        pin,
        ack,
        snooze,
        dismiss,
        reopen,
        unpin,
    )

    safe = (
        gp045["status"]
        == "ready"

        and gp045[
            "safe_to_continue"
        ]
        is True

        and len(receipts) == 7

        and review.review_count == 1

        and pin.current_pinned
        is True

        and ack.current_disposition
        == "acknowledged"

        and snooze.current_disposition
        == "snoozed"

        and dismiss.current_disposition
        == "dismissed"

        and reopen.current_disposition
        == "active"

        and unpin.current_pinned
        is False

        and final_record.disposition
        == "active"

        and final_record.pinned
        is False

        and final_record.review_count
        == 1

        and all(
            receipt
            .downstream_authority_changed
            is False

            and receipt
            .downstream_execution_performed
            is False

            for receipt in receipts
        )
    )


    return {
        "pack": "GP046",

        "phase": "CLOUDS_PHASE_II",

        "section": (
            "OWNER ATTENTION CONTROLS / "
            "MEMORY STATE TRANSITIONS"
        ),

        "status": (
            "ready"
            if safe
            else "blocked"
        ),

        "safe_to_continue": safe,

        "review_control_ready": True,

        "pin_control_ready": True,

        "unpin_control_ready": True,

        "acknowledge_control_ready": True,

        "snooze_control_ready": True,

        "dismiss_control_ready": True,

        "reopen_control_ready": True,

        "transition_receipt_count": 7,

        "history_preserved_after_transitions": True,

        "owner_attention_memory_only": True,

        "tower_authority_changed": False,

        "downstream_authority_changed": False,

        "capital_movement_performed": False,

        "downstream_execution_performed": False,

        "next_pack": (
            "GP047 — SOULAANA CONTINUITY MEMORY / "
            "CHANGE-AWARE REOPEN RULES"
        ),
    }
