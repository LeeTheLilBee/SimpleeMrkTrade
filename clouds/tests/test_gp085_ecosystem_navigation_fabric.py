from clouds.owner_command_experience_service import (
    SOURCE_DESTINATIONS,
    get_owner_command_cards,
)


def test_every_external_clouds_card_routes_through_tower():
    for source_id in (
        "observatory",
        "teller",
        "grounds",
        "archive_vault",
        "atm_operations",
    ):
        config = (
            SOURCE_DESTINATIONS[
                source_id
            ]
        )

        assert (
            config["kind"]
            == "tower_handoff"
        )

        assert (
            config["requires_tower"]
            is True
        )

        assert (
            config[
                "requires_owner_permission"
            ]
            is True
        )

        assert (
            config["route_reference"]
            .startswith(
                "/tower/ecosystem/launch/"
            )
        )


def test_atm_operations_is_not_clouds_internal_anymore():
    config = (
        SOURCE_DESTINATIONS[
            "atm_operations"
        ]
    )

    assert config["requires_tower"] is True
    assert config["requires_step_up"] is True

    assert (
        config["route_reference"]
        .startswith(
            "/tower/ecosystem/launch/"
            "atm_operations"
        )
    )


def test_owner_cards_remain_non_executing():
    cards = (
        get_owner_command_cards()
    )

    for card in cards:
        assert (
            card.execution_performed
            is False
        )

        assert (
            card.navigation
            .clouds_executes_navigation
            is False
        )

        assert (
            card.navigation
            .downstream_execution_performed
            is False
        )
