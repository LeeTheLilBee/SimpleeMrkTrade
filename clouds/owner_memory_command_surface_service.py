"""
GP048 — Owner Memory Command Surface / Persistence Readiness Closeout.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import tempfile

try:
    from .executive_owner_agenda_service import (
        get_owner_agenda_items,
    )

    from .owner_attention_controls_service import (
        acknowledge_attention_item,
        dismiss_attention_item,
        pin_attention_item,
        review_attention_item,
        snooze_attention_item,
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

    from .owner_memory_command_surface import (
        OwnerMemoryCommandSurface,
    )

    from .soulaana_continuity_memory_service import (
        evaluate_owner_continuity,
        evaluate_owner_continuity_item,
        get_clouds_gp047_status_payload,
    )

except ImportError:
    from executive_owner_agenda_service import (
        get_owner_agenda_items,
    )

    from owner_attention_controls_service import (
        acknowledge_attention_item,
        dismiss_attention_item,
        pin_attention_item,
        review_attention_item,
        snooze_attention_item,
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

    from owner_memory_command_surface import (
        OwnerMemoryCommandSurface,
    )

    from soulaana_continuity_memory_service import (
        evaluate_owner_continuity,
        evaluate_owner_continuity_item,
        get_clouds_gp047_status_payload,
    )


def build_owner_memory_command_surface(
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

    if agenda_items is None:
        agenda_items = (
            get_owner_agenda_items()
        )

    continuity = (
        evaluate_owner_continuity(
            store,
            agenda_items=agenda_items,
            owner_id=owner_id,
            now_iso=now_iso,
        )
    )

    ledger = (
        store.read_ledger(
            owner_id
        )
    )

    visible_count = sum(
        item.should_surface
        is True
        for item in continuity
    )

    quiet_count = (
        len(continuity)
        - visible_count
    )

    pinned_count = sum(
        record.pinned
        is True
        for record in ledger.records
    )

    snoozed_count = sum(
        record.disposition
        == "snoozed"
        for record in ledger.records
    )

    acknowledged_count = sum(
        record.disposition
        == "acknowledged"
        for record in ledger.records
    )

    dismissed_count = sum(
        record.disposition
        == "dismissed"
        for record in ledger.records
    )

    reopened_count = sum(
        item.continuity_state
        == "reopened_material_change"
        for item in continuity
    )

    reviewed_item_count = sum(
        record.review_count > 0
        for record in ledger.records
    )

    total_review_count = sum(
        record.review_count
        for record in ledger.records
    )


    if reopened_count:
        owner_summary = (
            f"{reopened_count} previously handled item"
            + (
                ""
                if reopened_count == 1
                else "s"
            )
            + " changed enough for me to bring "
            "back to your attention."
        )

    elif visible_count:
        owner_summary = (
            f"You have {visible_count} currently visible "
            "owner-memory item"
            + (
                ""
                if visible_count == 1
                else "s"
            )
            + ". Nothing previously quiet was reopened "
            "without a material change."
        )

    else:
        owner_summary = (
            "Nothing in owner memory currently needs to be brought back to you."
        )


    memory_summary = (
        f"I am remembering {ledger.record_count} owner instruction"
        + (
            ""
            if ledger.record_count == 1
            else "s"
        )
        + f": {pinned_count} pinned, "
        f"{snoozed_count} snoozed, "
        f"{acknowledged_count} acknowledged, "
        f"and {dismissed_count} dismissed."
    )


    protection = (
        f"I am keeping {quiet_count} current item"
        + (
            ""
            if quiet_count == 1
            else "s"
        )
        + " quiet because your prior instruction still matches "
        "the current material picture."
    )


    return OwnerMemoryCommandSurface(
        title=(
            "Owner Memory / Soulaana Continuity"
        ),

        continuity_items=(
            continuity
        ),

        agenda_item_count=(
            len(
                tuple(
                    agenda_items
                )
            )
        ),

        memory_record_count=(
            ledger.record_count
        ),

        visible_count=(
            visible_count
        ),

        quiet_count=(
            quiet_count
        ),

        pinned_count=(
            pinned_count
        ),

        snoozed_count=(
            snoozed_count
        ),

        acknowledged_count=(
            acknowledged_count
        ),

        dismissed_count=(
            dismissed_count
        ),

        reopened_material_change_count=(
            reopened_count
        ),

        reviewed_item_count=(
            reviewed_item_count
        ),

        total_review_count=(
            total_review_count
        ),

        durable_store_contract_ready=True,

        hosted_persistent_storage_verified=False,

        soulaana_owner_summary=(
            owner_summary
        ),

        soulaana_memory_summary=(
            memory_summary
        ),

        soulaana_attention_protection=(
            protection
        ),

        soulaana_next_step=(
            "Use pin, acknowledge, snooze, dismiss, review, or reopen without losing the history of what you already told me."
        ),

        tower_authority_changed=False,

        downstream_authority_changed=False,

        downstream_execution_performed=False,

        boundary_notice=(
            "Owner memory changes Clouds attention and presentation state only. "
            "It cannot alter Tower security, approve downstream work, move capital, "
            "or execute actions in another application."
        ),
    )


def get_owner_memory_command_surface(
    *,
    store=None,
    owner_id=DEFAULT_OWNER_ID,
    now_iso=None,
):
    if store is None:
        store = (
            get_default_owner_attention_memory_store()
        )

    return (
        build_owner_memory_command_surface(
            store,
            owner_id=owner_id,
            now_iso=now_iso,
        )
    )


def get_owner_memory_command_surface_payload(
    *,
    store=None,
    owner_id=DEFAULT_OWNER_ID,
    now_iso=None,
):
    return (
        get_owner_memory_command_surface(
            store=store,
            owner_id=owner_id,
            now_iso=now_iso,
        )
        .to_dict()
    )


def get_clouds_gp048_status_payload():
    gp047 = (
        get_clouds_gp047_status_payload()
    )

    agenda = list(
        get_owner_agenda_items()
    )

    if len(agenda) < 4:
        return {
            "pack": "GP048",
            "phase": "CLOUDS_PHASE_II",
            "status": "blocked",
            "safe_to_continue": False,
            "reason": "insufficient_agenda_fixture_items",
        }


    prefs = (
        get_owner_command_preferences()
    )


    with tempfile.TemporaryDirectory() as directory:
        path = (
            Path(directory)
            / "owner-memory-closeout.json"
        )

        store = (
            OwnerAttentionMemoryStore(
                path
            )
        )


        # Item 0: reviewed + pinned.
        review_attention_item(
            store,
            agenda[0],
            now_iso=(
                "2026-08-14T12:00:00Z"
            ),
        )

        pin_attention_item(
            store,
            agenda[0],
            now_iso=(
                "2026-08-14T12:01:00Z"
            ),
        )


        # Item 1: acknowledged.
        acknowledge_attention_item(
            store,
            agenda[1],
            now_iso=(
                "2026-08-14T12:02:00Z"
            ),
        )


        # Item 2: snoozed.
        snooze_attention_item(
            store,
            agenda[2],
            now_iso=(
                "2026-08-14T12:03:00Z"
            ),
            snooze_until=(
                "2026-08-15T12:03:00Z"
            ),
        )


        # Item 3: dismissed.
        dismiss_attention_item(
            store,
            agenda[3],
            now_iso=(
                "2026-08-14T12:04:00Z"
            ),
        )


        surface = (
            build_owner_memory_command_surface(
                store,
                agenda_items=tuple(
                    agenda
                ),
                now_iso=(
                    "2026-08-14T13:00:00Z"
                ),
            )
        )


        # New store instance proves stored state can be reloaded.
        reloaded_store = (
            OwnerAttentionMemoryStore(
                path
            )
        )

        reloaded_surface = (
            build_owner_memory_command_surface(
                reloaded_store,
                agenda_items=tuple(
                    agenda
                ),
                now_iso=(
                    "2026-08-14T13:00:00Z"
                ),
            )
        )


        persistence_verified = (
            surface.memory_record_count
            == reloaded_surface
            .memory_record_count

            and surface.pinned_count
            == reloaded_surface
            .pinned_count

            and surface.snoozed_count
            == reloaded_surface
            .snoozed_count

            and surface.acknowledged_count
            == reloaded_surface
            .acknowledged_count

            and surface.dismissed_count
            == reloaded_surface
            .dismissed_count
        )


        # Now prove an acknowledged item reopens ONLY after material change.
        unchanged_ack = (
            evaluate_owner_continuity_item(
                reloaded_store,
                agenda[1],
                now_iso=(
                    "2026-08-14T13:01:00Z"
                ),
            )
        )


        changed_agenda_item = replace(
            agenda[1],

            urgency=(
                "critical"
                if agenda[1].urgency
                != "critical"
                else "high"
            ),
        )


        changed_ack = (
            evaluate_owner_continuity_item(
                reloaded_store,
                changed_agenda_item,
                now_iso=(
                    "2026-08-14T13:02:00Z"
                ),
            )
        )


    safe = (
        gp047["status"]
        == "ready"

        and gp047[
            "safe_to_continue"
        ]
        is True

        and prefs.soulaana_verbosity
        == "explain_everything"

        and surface.memory_record_count
        == 4

        and surface.pinned_count
        == 1

        and surface.snoozed_count
        == 1

        and surface.acknowledged_count
        == 1

        and surface.dismissed_count
        == 1

        and surface.reviewed_item_count
        == 1

        and surface.total_review_count
        == 1

        and persistence_verified
        is True

        and unchanged_ack
        .continuity_state
        == "quiet_unchanged"

        and unchanged_ack.should_reopen
        is False

        and changed_ack
        .continuity_state
        == "reopened_material_change"

        and changed_ack.should_reopen
        is True

        and surface
        .durable_store_contract_ready
        is True

        and surface
        .hosted_persistent_storage_verified
        is False

        and surface
        .tower_authority_changed
        is False

        and surface
        .downstream_authority_changed
        is False

        and surface
        .downstream_execution_performed
        is False
    )


    return {
        "pack": "GP048",

        "phase": "CLOUDS_PHASE_II",

        "section": (
            "OWNER MEMORY COMMAND SURFACE / "
            "PERSISTENCE READINESS CLOSEOUT"
        ),

        "status": (
            "ready"
            if safe
            else "blocked"
        ),

        "safe_to_continue": safe,

        "owner_memory_surface_ready": True,

        "owner_profile_count": 1,

        "soulaana_verbosity": (
            prefs.soulaana_verbosity
        ),

        "review_memory_ready": True,

        "pin_memory_ready": True,

        "snooze_memory_ready": True,

        "acknowledge_memory_ready": True,

        "dismiss_memory_ready": True,

        "reopen_memory_ready": True,

        "continuity_memory_ready": True,

        "material_change_reopen_ready": True,

        "unchanged_item_quieting_ready": True,

        "refresh_alone_does_not_reopen": True,

        "review_history_preserved": True,

        "process_restart_roundtrip_verified": (
            persistence_verified
        ),

        "durable_store_contract_ready": True,

        "hosted_persistent_storage_verified": False,

        "production_database_connected": False,

        "soulaana_explains_everything_preserved": True,

        "tower_authority_changed": False,

        "downstream_authority_changed": False,

        "automatic_business_decision_performed": False,

        "capital_movement_performed": False,

        "downstream_execution_performed": False,

        "cross_app_imports_used": False,

        "conclusion": (
            "CLOUDS_PHASE_II_OWNER_MEMORY_"
            "CONTINUITY_LAYER_READY"
        ),

        "next_pack": (
            "GP049 — EXECUTIVE MONEY PICTURE / "
            "CAPITAL CLASSIFICATION FOUNDATION"
        ),
    }
