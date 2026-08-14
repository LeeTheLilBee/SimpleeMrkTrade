"""
GP081 compatibility repair.

Tower must load the canonical Clouds GP060 owner experience
from its service module.

This test does not perform hosted deployment.
"""

from flask import Flask

from tower import (
    tower_clouds_native_launch
    as native
)


def test_gp081_service_module_is_first_candidate():

    assert (
        native
        .OWNER_EXPERIENCE_IMPORT_CANDIDATES[
            0
        ]
        == (
            "clouds."
            "owner_command_experience_service"
        )
    )


def test_gp081_tower_loads_gp060_owner_experience():

    app = Flask(
        "gp081-loader-regression"
    )

    app.secret_key = (
        "gp081-loader-regression-only"
    )


    with app.test_request_context(
        "/"
    ):

        experience = (
            native
            ._load_owner_command_experience()
        )


        assert (
            experience
            is not None
        )

        assert (
            type(
                experience
            ).__name__
            == "OwnerCommandExperience"
        )

        assert (
            experience.title
            == "The Clouds"
        )

        assert (
            experience.subtitle
            == (
                "Simplee World "
                "Owner Command"
            )
        )

        assert (
            experience.section_count
            == 4
        )

        assert (
            experience.card_count
            == 6
        )

        assert (
            experience
            .evidence_hidden_by_default
            is True
        )

        assert (
            experience
            .progressive_disclosure_enabled
            is True
        )

        assert (
            experience
            .downstream_execution_performed
            is False
        )
