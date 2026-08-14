import ast
from pathlib import Path

from clouds.beta_readiness_closeout_service import (
    get_clouds_beta_readiness_record,
    get_clouds_beta_readiness_surface,
    get_clouds_beta_readiness_surface_payload,
    get_clouds_gp024_status_payload,
    get_clouds_owner_walkthrough,
)


def test_gp024_walkthrough_has_11_steps():
    assert len(
        get_clouds_owner_walkthrough()
    ) == 11


def test_gp024_walkthrough_all_pass():
    assert all(
        step.passed
        for step
        in get_clouds_owner_walkthrough()
    )


def test_gp024_walkthrough_executes_nothing():
    assert all(
        step.execution_performed
        is False
        for step
        in get_clouds_owner_walkthrough()
    )


def test_gp024_clouds_side_ready():
    record = (
        get_clouds_beta_readiness_record()
    )

    assert (
        record.clouds_side_ready
        is True
    )


def test_gp024_not_externally_beta_ready():
    record = (
        get_clouds_beta_readiness_record()
    )

    assert (
        record.externally_beta_ready
        is False
    )


def test_gp024_no_live_feed_claim():
    record = (
        get_clouds_beta_readiness_record()
    )

    assert (
        record.live_downstream_feeds_connected
        is False
    )


def test_gp024_no_hosted_tower_claim():
    record = (
        get_clouds_beta_readiness_record()
    )

    assert (
        record.hosted_tower_integration_verified
        is False
    )


def test_gp024_no_staging_claim():
    record = (
        get_clouds_beta_readiness_record()
    )

    assert (
        record.hosted_staging_verified
        is False
    )


def test_gp024_no_external_acceptance_claim():
    record = (
        get_clouds_beta_readiness_record()
    )

    assert (
        record.external_beta_acceptance_recorded
        is False
    )


def test_gp024_conclusion():
    record = (
        get_clouds_beta_readiness_record()
    )

    assert record.conclusion == (
        "CLOUDS_CORE_V1_READY_FOR_"
        "TOWER_INTEGRATION_AND_OWNER_WALKTHROUGH"
    )


def test_gp024_surface_counts():
    surface = (
        get_clouds_beta_readiness_surface()
    )

    assert (
        surface.walkthrough_step_count
        == 11
    )

    assert (
        surface.walkthrough_pass_count
        == 11
    )


def test_gp024_payload():
    payload = (
        get_clouds_beta_readiness_surface_payload()
    )

    assert (
        payload["walkthrough_step_count"]
        == 11
    )


def test_gp024_status():
    status = (
        get_clouds_gp024_status_payload()
    )

    assert status["pack"] == "GP024"
    assert status["status"] == "ready"
    assert status["safe_to_continue"] is True

    assert (
        status["core_pack_start"]
        == "GP001"
    )

    assert (
        status["core_pack_end"]
        == "GP024"
    )

    assert (
        status["clouds_side_ready"]
        is True
    )

    assert (
        status["externally_beta_ready"]
        is False
    )

    assert (
        status["tower_boundary_preserved"]
        is True
    )

    assert (
        status["live_downstream_feeds_connected"]
        is False
    )

    assert (
        status["hosted_tower_integration_verified"]
        is False
    )

    assert (
        status["hosted_staging_verified"]
        is False
    )

    assert (
        status["external_beta_acceptance_recorded"]
        is False
    )

    assert status["next_action"] == (
        "MOVE_TO_TOWER_CLOUDS_INTEGRATION_"
        "AND_REAL_OWNER_WALKTHROUGH"
    )


def test_gp024_no_cross_app_imports():
    root = Path(__file__).resolve().parents[2]

    files = (
        root / "clouds" / "beta_readiness_closeout.py",
        root / "clouds" / "beta_readiness_closeout_service.py",
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
