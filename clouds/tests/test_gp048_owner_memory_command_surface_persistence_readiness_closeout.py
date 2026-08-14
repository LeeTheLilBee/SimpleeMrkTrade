from clouds.executive_owner_agenda_service import (
    get_owner_agenda_items,
)

from clouds.owner_attention_controls_service import (
    acknowledge_attention_item,
    pin_attention_item,
)

from clouds.owner_attention_memory_service import (
    OwnerAttentionMemoryStore,
)

from clouds.owner_memory_command_surface_service import (
    build_owner_memory_command_surface,
    get_clouds_gp048_status_payload,
)


def test_gp048_surface_remembers_owner_state(
    tmp_path,
):
    agenda = (
        get_owner_agenda_items()
    )

    store = (
        OwnerAttentionMemoryStore(
            tmp_path / "memory.json"
        )
    )

    pin_attention_item(
        store,
        agenda[0],
        now_iso=(
            "2026-08-14T12:00:00Z"
        ),
    )

    acknowledge_attention_item(
        store,
        agenda[1],
        now_iso=(
            "2026-08-14T12:01:00Z"
        ),
    )

    surface = (
        build_owner_memory_command_surface(
            store,
            agenda_items=agenda,
            now_iso=(
                "2026-08-14T13:00:00Z"
            ),
        )
    )

    assert (
        surface.memory_record_count
        == 2
    )

    assert (
        surface.pinned_count
        == 1
    )

    assert (
        surface.acknowledged_count
        == 1
    )


def test_gp048_new_store_reads_same_memory(
    tmp_path,
):
    path = (
        tmp_path
        / "memory.json"
    )

    agenda = (
        get_owner_agenda_items()
    )

    first = (
        OwnerAttentionMemoryStore(
            path
        )
    )

    pin_attention_item(
        first,
        agenda[0],
        now_iso=(
            "2026-08-14T12:00:00Z"
        ),
    )

    second = (
        OwnerAttentionMemoryStore(
            path
        )
    )

    assert (
        second.get(
            agenda[0]
            .agenda_item_id
        )
        .pinned
        is True
    )


def test_gp048_status_ready():
    status = (
        get_clouds_gp048_status_payload()
    )

    assert status["pack"] == "GP048"

    assert (
        status["status"]
        == "ready"
    )

    assert (
        status["safe_to_continue"]
        is True
    )

    assert (
        status[
            "owner_memory_surface_ready"
        ]
        is True
    )

    assert (
        status[
            "material_change_reopen_ready"
        ]
        is True
    )

    assert (
        status[
            "refresh_alone_does_not_reopen"
        ]
        is True
    )

    assert (
        status[
            "process_restart_roundtrip_verified"
        ]
        is True
    )

    assert (
        status[
            "hosted_persistent_storage_verified"
        ]
        is False
    )

    assert (
        status["conclusion"]
        == (
            "CLOUDS_PHASE_II_OWNER_MEMORY_"
            "CONTINUITY_LAYER_READY"
        )
    )
