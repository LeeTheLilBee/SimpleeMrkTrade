from ob_owner_experience.private_beta_tester_access_grant_preparation import (
    prepare_private_beta_tester_access_grant,
)


def eligibility_state():
    return {
        "tester_id": "beta-tester-001",
        "eligibility_ready": True,
        "manual_live_allowed": False,
        "live_auto_allowed": False,
        "broker_execution_allowed": False,
        "permission_admin_allowed": False,
        "secret_access_allowed": False,
    }


def test_gp058_prepares_non_active_restricted_grant():
    result = (
        prepare_private_beta_tester_access_grant(
            {
                "tester_id": "beta-tester-001",
            },
            eligibility_state(),
        )
    )

    assert (
        result["grant_prepared"]
        is True
    )

    assert (
        result["credential_issued"]
        is False
    )

    assert (
        result["tester_session_created"]
        is False
    )

    assert (
        result["access_activated"]
        is False
    )

    assert (
        result["permission_mutation_performed"]
        is False
    )

    grant = result["grant"]

    assert grant["allowed_modes"] == [
        "Survey",
        "Paper",
    ]

    assert (
        "Owner Console"
        in grant["excluded_rooms"]
    )

    assert (
        grant["owner_console_access"]
        is False
    )

    assert (
        grant["manual_live_access"]
        is False
    )

    assert (
        grant["live_auto_access"]
        is False
    )

    assert (
        grant["broker_submission_access"]
        is False
    )

    assert (
        grant["real_capital_access"]
        is False
    )


def test_gp058_fails_without_gp057_eligibility():
    state = eligibility_state()

    state[
        "eligibility_ready"
    ] = False

    result = (
        prepare_private_beta_tester_access_grant(
            {
                "tester_id": "beta-tester-001",
            },
            state,
        )
    )

    assert (
        result["grant_prepared"]
        is False
    )

    assert (
        result["access_activated"]
        is False
    )

    assert (
        "gp057_eligibility_required"
        in result["failures"]
    )
