from pathlib import Path

from clouds.owner_attention_controls_service import (
    acknowledge_attention_item,
)

from clouds.owner_attention_memory_service import (
    OwnerAttentionMemoryStore,
)

from clouds.soulaana_owner_brief_service import (
    build_soulaana_owner_brief,
    get_chief_of_staff_agenda_items,
    get_clouds_gp053_status_payload,
)


def test_gp053_active_brief_has_owner_attention(
    tmp_path,
):

    store = (
        OwnerAttentionMemoryStore(
            tmp_path
            / "memory.json"
        )
    )

    brief = (
        build_soulaana_owner_brief(
            store,

            now_iso=(
                "2026-08-14T12:00:00Z"
            ),
        )
    )

    assert (
        brief.changed_source_count
        >= 1
    )

    assert (
        brief.needs_you_count
        >= 1
    )


def test_gp053_handled_items_can_produce_no_action(
    tmp_path,
):

    store = (
        OwnerAttentionMemoryStore(
            tmp_path
            / "memory.json"
        )
    )

    agenda = (
        get_chief_of_staff_agenda_items()
    )


    for item in agenda:

        if (
            item
            .owner_attention_required
        ):

            acknowledge_attention_item(
                store,
                item,

                now_iso=(
                    "2026-08-14T12:00:00Z"
                ),
            )


    brief = (
        build_soulaana_owner_brief(
            store,

            agenda_items=agenda,

            now_iso=(
                "2026-08-14T13:00:00Z"
            ),
        )
    )


    assert (
        brief.nothing_needs_you
        is True
    )

    assert (
        brief.needs_you_count
        == 0
    )

    assert (
        "Nothing needs you"
        in brief.soulaana_no_action
    )


def test_gp053_status():

    status = (
        get_clouds_gp053_status_payload()
    )

    assert (
        status["status"]
        == "ready"
    )

    assert (
        status[
            "explicit_nothing_needs_you_ready"
        ]
        is True
    )

    assert (
        status[
            "false_all_clear_prohibited"
        ]
        is True
    )
