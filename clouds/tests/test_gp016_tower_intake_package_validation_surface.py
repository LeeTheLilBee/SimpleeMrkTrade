import ast
from pathlib import Path

import pytest

from clouds.tower_intake_package_service import (
    get_clouds_gp016_status_payload,
    get_tower_intake_package,
    get_tower_intake_package_by_submission,
    get_tower_intake_packages,
    get_tower_intake_validation_surface,
    get_tower_intake_validation_surface_payload,
)


def test_gp016_package_inventory():
    packages = get_tower_intake_packages()
    assert len(packages) == 11


def test_gp016_all_packages_valid():
    assert all(
        item.validation_state == "valid"
        for item in get_tower_intake_packages()
    )


def test_gp016_checks_all_pass():
    for package in get_tower_intake_packages():
        assert len(package.checks) == 5

        assert all(
            check.passed
            for check in package.checks
        )


def test_gp016_package_hashes():
    for package in get_tower_intake_packages():
        assert len(package.package_hash) == 64
        int(package.package_hash, 16)


def test_gp016_deterministic():
    first = [
        item.package_hash
        for item in get_tower_intake_packages()
    ]

    second = [
        item.package_hash
        for item in get_tower_intake_packages()
    ]

    assert first == second


def test_gp016_permission_and_step_up_present():
    for package in get_tower_intake_packages():
        assert (
            package.requires_owner_permission
            is True
        )

        assert package.requires_step_up is True


def test_gp016_no_delivery_authorization():
    assert all(
        item.delivery_authorized is False
        for item in get_tower_intake_packages()
    )


def test_gp016_no_delivery():
    assert all(
        item.delivered_to_tower is False
        for item in get_tower_intake_packages()
    )


def test_gp016_no_tower_request():
    assert all(
        item.tower_request_created is False
        for item in get_tower_intake_packages()
    )


def test_gp016_no_receipt():
    assert all(
        item.tower_receipt_created is False
        for item in get_tower_intake_packages()
    )


def test_gp016_no_handoff():
    assert all(
        item.handoff_executed is False
        for item in get_tower_intake_packages()
    )


def test_gp016_no_execution():
    assert all(
        item.downstream_execution_performed
        is False
        for item in get_tower_intake_packages()
    )


def test_gp016_lookup():
    item = get_tower_intake_packages()[0]

    assert (
        get_tower_intake_package(
            item.package_id
        )
        == item
    )

    assert (
        get_tower_intake_package_by_submission(
            item.submission_id
        )
        == item
    )


def test_gp016_unknown_fails_closed():
    with pytest.raises(KeyError):
        get_tower_intake_package("missing")

    with pytest.raises(KeyError):
        get_tower_intake_package_by_submission(
            "missing"
        )


def test_gp016_surface():
    surface = (
        get_tower_intake_validation_surface()
    )

    assert surface.package_count == 11
    assert surface.valid_count == 11
    assert surface.invalid_count == 0


def test_gp016_surface_payload():
    payload = (
        get_tower_intake_validation_surface_payload()
    )

    assert payload["package_count"] == 11
    assert len(payload["packages"]) == 11


def test_gp016_status():
    status = get_clouds_gp016_status_payload()

    assert status["pack"] == "GP016"
    assert status["status"] == "ready"
    assert status["safe_to_continue"] is True
    assert status["package_count"] == 11
    assert status["valid_count"] == 11
    assert status["invalid_count"] == 0
    assert status["delivery_authorized"] is False
    assert status["delivery_performed"] is False
    assert status["tower_request_created"] is False
    assert status["tower_receipt_created"] is False
    assert status["handoff_executed"] is False


def test_gp016_no_cross_app_imports():
    root = Path(__file__).resolve().parents[2]

    files = (
        root / "clouds" / "tower_intake_package.py",
        root / "clouds" / "tower_intake_package_service.py",
    )

    forbidden = {
        "tower",
        "observatory",
        "vault",
        "teller",
        "grounds",
    }

    for path in files:
        tree = ast.parse(
            path.read_text(
                encoding="utf-8"
            )
        )

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert (
                        alias.name.split(".")[0].lower()
                        not in forbidden
                    )

            if isinstance(node, ast.ImportFrom):
                module = node.module or ""

                assert (
                    module.lstrip(".")
                    .split(".")[0]
                    .lower()
                    not in forbidden
                )
