from dataclasses import replace

from clouds.executive_owner_agenda_service import (
    get_owner_agenda_items,
)

from clouds.owner_attention_controls_service import (
    acknowledge_attention_item,
    dismiss_attention_item,
    snooze_attention_item,
)

from clouds.owner_attention_memory_service import (
    OwnerAttentionMemoryStore,
)

from clouds.soulaana_continuity_memory_service import (
    apply_change_aware_reopens,
    evaluate_owner_continuity_item,
    get_clouds_gp047_status_payload,
)


def test_gp047_unchanged_ack_stays_quiet(
    tmp_path,
):
    item = (
        get_owner_agenda_items()[0]
    )

    store = (
        OwnerAttentionMemoryStore(
            tmp_path / "memory.json"
        )
    )

    acknowledge_attention_item(
        store,
        item,
        now_iso=(
            "2026-08-14T12:00:00Z"
        ),
    )

    result = (
        evaluate_owner_continuity_item(
            store,
            item,
            now_iso=(
                "2026-08-14T13:00:00Z"
            ),
        )
    )

    assert (
        result.continuity_state
        == "quiet_unchanged"
    )

    assert (
        result.should_surface
        is False
    )

    assert (
        result.should_reopen
        is False
    )


def test_gp047_material_change_reopens(
    tmp_path,
):
    item = (
        get_owner_agenda_items()[0]
    )

    store = (
        OwnerAttentionMemoryStore(
            tmp_path / "memory.json"
        )
    )

    acknowledge_attention_item(
        store,
        item,
        now_iso=(
            "2026-08-14T12:00:00Z"
        ),
    )

    changed = replace(
        item,
        urgency=(
            "critical"
            if item.urgency
            != "critical"
            else "high"
        ),
    )

    result = (
        evaluate_owner_continuity_item(
            store,
            changed,
            now_iso=(
                "2026-08-14T13:00:00Z"
            ),
        )
    )

    assert (
        result
        .continuity_state
        == "reopened_material_change"
    )

    assert (
        result.should_reopen
        is True
    )


def test_gp047_apply_reopen_updates_memory_only(
    tmp_path,
):
    item = (
        get_owner_agenda_items()[0]
    )

    store = (
        OwnerAttentionMemoryStore(
            tmp_path / "memory.json"
        )
    )

    dismiss_attention_item(
        store,
        item,
        now_iso=(
            "2026-08-14T12:00:00Z"
        ),
    )

    changed = replace(
        item,
        horizon=(
            "do_now"
            if item.horizon
            != "do_now"
            else "today"
        ),
    )

    reopened = (
        apply_change_aware_reopens(
            store,
            agenda_items=(
                changed,
            ),
            now_iso=(
                "2026-08-14T13:00:00Z"
            ),
        )
    )

    assert reopened == (
        item.agenda_item_id,
    )

    record = store.get(
        item.agenda_item_id
    )

    assert (
        record.disposition
        == "active"
    )

    assert (
        record
        .downstream_execution_performed
        is False
    )


def test_gp047_status_ready():
    status = (
        get_clouds_gp047_status_payload()
    )

    assert status["pack"] == "GP047"
    assert status["status"] == "ready"

    assert (
        status[
            "refresh_alone_does_not_reopen"
        ]
        is True
    )

    assert (
        status[
            "material_fingerprint_change_reopens"
        ]
        is True
    )

    assert (
        status[
            "downstream_execution_performed"
        ]
        is False
    )
