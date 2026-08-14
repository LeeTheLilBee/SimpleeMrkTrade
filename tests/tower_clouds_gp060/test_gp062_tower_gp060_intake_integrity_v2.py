from copy import deepcopy

from tower.tower_clouds_gp060_intake_service import (
    build_tower_clouds_gp060_intake,
    validate_tower_clouds_gp060_intake,
    get_clouds_gp062_status_payload,
)


def test_gp062_valid():

    intake = (
        build_tower_clouds_gp060_intake()
    )

    valid, errors = (
        validate_tower_clouds_gp060_intake(
            intake
        )
    )

    assert valid is True
    assert errors == ()


def test_gp062_tamper_fails():

    intake = deepcopy(
        build_tower_clouds_gp060_intake()
    )

    intake[
        "source_commit"
    ] = "tampered"

    valid, errors = (
        validate_tower_clouds_gp060_intake(
            intake
        )
    )

    assert valid is False

    assert (
        "integrity_hash_invalid"
        in errors
    )


def test_gp062_status():

    p = (
        get_clouds_gp062_status_payload()
    )

    assert p["status"] == "ready"

    assert (
        p[
            "legacy_gp016_gp017_contract_preserved"
        ]
        is True
    )

    assert (
        p["source_branch_merged"]
        is False
    )
