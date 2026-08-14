from dataclasses import replace

from clouds.owner_consequence_blocker_service import (
    build_consequence_blocker_surface,
    get_clouds_gp054_status_payload,
)

from clouds.soulaana_owner_brief_service import (
    get_chief_of_staff_agenda_items,
)


def test_gp054_consequences_use_existing_agenda():

    agenda = (
        get_chief_of_staff_agenda_items()
    )

    surface = (
        build_consequence_blocker_surface(
            agenda_items=agenda
        )
    )

    assert (
        surface.consequence_count
        == len(agenda)
    )

    assert (
        surface.consequence_inference_count
        == 0
    )


def test_gp054_waiting_horizon_is_only_blocker_basis():

    agenda = (
        get_chief_of_staff_agenda_items()
    )

    fixture = replace(
        agenda[0],

        agenda_item_id=(
            agenda[0].agenda_item_id
            + "-waiting"
        ),

        horizon="waiting",

        owner_attention_required=False,
    )

    surface = (
        build_consequence_blocker_surface(
            agenda_items=(
                fixture,
            )
        )
    )

    assert (
        surface.blocker_count
        == 1
    )

    assert (
        surface.blockers[0]
        .blocker_basis
        == "gp028_waiting_horizon"
    )

    assert (
        surface.blockers[0]
        .fabricated_blocker
        is False
    )


def test_gp054_status():

    status = (
        get_clouds_gp054_status_payload()
    )

    assert (
        status["status"]
        == "ready"
    )

    assert (
        status[
            "fabricated_blocker_count"
        ]
        == 0
    )

    assert (
        status[
            "consequence_inference_count"
        ]
        == 0
    )
