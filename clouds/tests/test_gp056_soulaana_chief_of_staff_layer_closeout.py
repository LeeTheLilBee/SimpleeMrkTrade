from clouds.owner_attention_controls_service import (
    acknowledge_attention_item,
)

from clouds.owner_attention_memory_service import (
    OwnerAttentionMemoryStore,
)

from clouds.soulaana_chief_of_staff_service import (
    build_soulaana_chief_of_staff_surface,
    get_clouds_gp056_status_payload,
)

from clouds.soulaana_owner_brief_service import (
    get_chief_of_staff_agenda_items,
)


def test_gp056_chief_of_staff_composes_existing_layers(
    tmp_path,
):

    store = (
        OwnerAttentionMemoryStore(
            tmp_path
            / "memory.json"
        )
    )

    surface = (
        build_soulaana_chief_of_staff_surface(
            store,

            now_iso=(
                "2026-08-14T12:00:00Z"
            ),
        )
    )

    assert (
        surface.priority_engine_replaced
        is False
    )

    assert (
        surface.memory_engine_replaced
        is False
    )

    assert (
        surface.money_engine_replaced
        is False
    )

    assert (
        surface
        .money_surface
        .strict_money_separation_verified
        is True
    )

    assert (
        surface
        .verified_real_spendable_cents
        == 0
    )


def test_gp056_can_explicitly_say_nothing_needs_you(
    tmp_path,
):

    agenda = (
        get_chief_of_staff_agenda_items()
    )

    store = (
        OwnerAttentionMemoryStore(
            tmp_path
            / "memory.json"
        )
    )

    for item in agenda:

        if item.owner_attention_required:

            acknowledge_attention_item(
                store,
                item,

                now_iso=(
                    "2026-08-14T12:00:00Z"
                ),
            )

    surface = (
        build_soulaana_chief_of_staff_surface(
            store,

            agenda_items=agenda,

            now_iso=(
                "2026-08-14T13:00:00Z"
            ),
        )
    )

    assert (
        surface.nothing_needs_you
        is True
    )

    assert (
        surface.needs_you_count
        == 0
    )

    assert (
        surface.unresolved_count
        == 0
    )

    assert (
        "Nothing needs you"
        in surface.soulaana_no_action
    )


def test_gp056_no_fabricated_blockers_or_forgotten_claims(
    tmp_path,
):

    store = (
        OwnerAttentionMemoryStore(
            tmp_path
            / "memory.json"
        )
    )

    surface = (
        build_soulaana_chief_of_staff_surface(
            store,

            now_iso=(
                "2026-08-14T12:00:00Z"
            ),
        )
    )

    assert (
        surface
        .consequence_blocker_surface
        .fabricated_blocker_count
        == 0
    )

    assert (
        surface
        .follow_up_surface
        .forgotten_claim_count
        == 0
    )


def test_gp056_status():

    status = (
        get_clouds_gp056_status_payload()
    )

    assert (
        status["pack"]
        == "GP056"
    )

    assert (
        status["status"]
        == "ready"
    )

    assert (
        status[
            "explicit_no_action_ready"
        ]
        is True
    )

    assert (
        status[
            "soulaana_explains_everything_preserved"
        ]
        is True
    )

    assert (
        status["conclusion"]
        == (
            "CLOUDS_PHASE_II_SOULAANA_"
            "CHIEF_OF_STAFF_LAYER_READY"
        )
    )
