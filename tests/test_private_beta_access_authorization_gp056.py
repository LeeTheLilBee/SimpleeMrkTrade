from ob_owner_experience.private_beta_access_authorization import (
    authorize_private_beta_access,
)


def baseline_state():
    return {
        "staging_ready": True,
        "tower_staging_accepted": True,
        "beta_launch_preparation_closeout_ready": True,
        "private_beta_access_opened": False,
        "tester_credentials_issued": False,
        "production_deploy_disabled": True,
        "broker_submission_locked": True,
        "real_capital_movement_locked": True,
        "direct_execution_disabled": True,
        "automated_execution_disabled": True,
        "permission_mutations_disabled": True,
        "secret_reveal_disabled": True,
        "live_auto_locked": True,
    }


def test_gp056_authorization_ready():
    result = authorize_private_beta_access(
        baseline_state()
    )

    assert (
        result["access_authorization_ready"]
        is True
    )

    assert (
        result["private_beta_access_opened"]
        is False
    )

    assert (
        result["tester_credentials_issued"]
        is False
    )

    assert (
        result["tester_session_created"]
        is False
    )

    assert (
        result["permission_mutation_performed"]
        is False
    )

    assert result["recommendation"] == (
        "GO_FOR_PRIVATE_BETA_TESTER_ELIGIBILITY_REVIEW"
    )


def test_gp056_fails_closed_if_direct_execution_unlocked():
    state = baseline_state()

    state[
        "direct_execution_disabled"
    ] = False

    result = authorize_private_beta_access(
        state
    )

    assert (
        result["access_authorization_ready"]
        is False
    )

    assert (
        result["private_beta_access_opened"]
        is False
    )

    assert (
        "direct_execution_disabled_required_true"
        in result["failures"]
    )
