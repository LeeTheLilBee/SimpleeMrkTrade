from dataclasses import replace

from clouds.owner_attention_controls_service import (
    acknowledge_attention_item,
    snooze_attention_item,
)

from clouds.owner_attention_memory_service import (
    OwnerAttentionMemoryStore,
)

from clouds.owner_follow_up_service import (
    build_owner_follow_up_surface,
    get_clouds_gp055_status_payload,
)

from clouds.soulaana_owner_brief_service import (
    get_chief_of_staff_agenda_items,
)


def test_gp055_unhandled_is_not_called_forgotten(
    tmp_path,
):

    store = (
        OwnerAttentionMemoryStore(
            tmp_path
            / "memory.json"
        )
    )

    surface = (
        build_owner_follow_up_surface(
            store,

            now_iso=(
                "2026-08-14T12:00:00Z"
            ),
        )
    )

    assert (
        surface.not_yet_handled_count
        >= 1
    )

    assert (
        surface.forgotten_claim_count
        == 0
    )


def test_gp055_snooze_is_deferred(
    tmp_path,
):

    agenda = (
        get_chief_of_staff_agenda_items()
    )

    item = next(
        item

        for item
        in agenda

        if item.owner_attention_required
    )

    store = (
        OwnerAttentionMemoryStore(
            tmp_path
            / "memory.json"
        )
    )

    snooze_attention_item(
        store,
        item,

        now_iso=(
            "2026-08-14T12:00:00Z"
        ),

        snooze_until=(
            "2026-08-15T12:00:00Z"
        ),
    )

    surface = (
        build_owner_follow_up_surface(
            store,

            agenda_items=agenda,

            now_iso=(
                "2026-08-14T13:00:00Z"
            ),
        )
    )

    assert (
        surface.deferred_count
        >= 1
    )


def test_gp055_material_change_reappears(
    tmp_path,
):

    agenda = list(
        get_chief_of_staff_agenda_items()
    )

    item = next(
        item

        for item
        in agenda

        if item.owner_attention_required
    )

    store = (
        OwnerAttentionMemoryStore(
            tmp_path
            / "memory.json"
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

    changed_agenda = tuple(
        changed
        if (
            x.agenda_item_id
            == item.agenda_item_id
        )
        else x

        for x
        in agenda
    )

    surface = (
        build_owner_follow_up_surface(
            store,

            agenda_items=(
                changed_agenda
            ),

            now_iso=(
                "2026-08-14T13:00:00Z"
            ),
        )
    )

    assert (
        surface
        .reopened_material_change_count
        == 1
    )


def test_gp055_status():

    status = (
        get_clouds_gp055_status_payload()
    )

    assert (
        status["status"]
        == "ready"
    )

    assert (
        status[
            "false_forgotten_claim_prohibited"
        ]
        is True
    )

    assert (
        status[
            "material_change_reopen_follow_up_ready"
        ]
        is True
    )
