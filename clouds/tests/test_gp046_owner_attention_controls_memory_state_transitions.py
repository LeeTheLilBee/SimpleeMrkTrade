from clouds.executive_owner_agenda_service import (
    get_owner_agenda_items,
)

from clouds.owner_attention_controls_service import (
    acknowledge_attention_item,
    dismiss_attention_item,
    get_clouds_gp046_status_payload,
    pin_attention_item,
    reopen_attention_item,
    review_attention_item,
    snooze_attention_item,
    unpin_attention_item,
)

from clouds.owner_attention_memory_service import (
    OwnerAttentionMemoryStore,
)


def test_gp046_review_pin_ack_snooze_dismiss_reopen(
    tmp_path,
):
    store = (
        OwnerAttentionMemoryStore(
            tmp_path / "memory.json"
        )
    )

    item = (
        get_owner_agenda_items()[0]
    )

    review_attention_item(
        store,
        item,
        now_iso=(
            "2026-08-14T12:00:00Z"
        ),
    )

    pin_attention_item(
        store,
        item,
        now_iso=(
            "2026-08-14T12:01:00Z"
        ),
    )

    assert (
        store.get(
            item.agenda_item_id
        ).pinned
        is True
    )

    acknowledge_attention_item(
        store,
        item,
        now_iso=(
            "2026-08-14T12:02:00Z"
        ),
    )

    assert (
        store.get(
            item.agenda_item_id
        ).disposition
        == "acknowledged"
    )

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

    assert (
        store.get(
            item.agenda_item_id
        ).disposition
        == "snoozed"
    )

    dismiss_attention_item(
        store,
        item,
        now_iso=(
            "2026-08-14T12:04:00Z"
        ),
    )

    assert (
        store.get(
            item.agenda_item_id
        ).disposition
        == "dismissed"
    )

    reopen_attention_item(
        store,
        item,
        now_iso=(
            "2026-08-14T12:05:00Z"
        ),
    )

    unpin_attention_item(
        store,
        item,
        now_iso=(
            "2026-08-14T12:06:00Z"
        ),
    )

    final = store.get(
        item.agenda_item_id
    )

    assert (
        final.disposition
        == "active"
    )

    assert final.pinned is False
    assert final.review_count == 1


def test_gp046_status_ready():
    status = (
        get_clouds_gp046_status_payload()
    )

    assert status["pack"] == "GP046"
    assert status["status"] == "ready"

    assert (
        status["pin_control_ready"]
        is True
    )

    assert (
        status["snooze_control_ready"]
        is True
    )

    assert (
        status[
            "downstream_execution_performed"
        ]
        is False
    )
