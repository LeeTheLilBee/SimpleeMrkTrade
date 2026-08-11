from ob_owner_experience.private_beta_access_activation_gate import (
    evaluate_private_beta_access_activation_gate,
)


def grant_package():
    return {
        "grant_prepared": True,
        "grant": {
            "allowed_modes": [
                "Survey",
                "Paper",
            ],
            "owner_console_access": False,
            "manual_live_access": False,
            "live_auto_access": False,
            "broker_submission_access": False,
            "real_capital_access": False,
            "permission_admin_access": False,
            "secret_access": False,
        },
    }


def runtime_state():
    return {
        "tower_authenticated_session_required": True,
        "tower_authorization_required": True,
        "revocation_ready": True,
        "access_receipt_logging_ready": True,
        "production_deploy_disabled": True,
        "broker_submission_locked": True,
        "real_capital_movement_locked": True,
        "direct_execution_disabled": True,
        "automated_execution_disabled": True,
        "permission_mutations_disabled": True,
        "secret_reveal_disabled": True,
        "live_auto_locked": True,
    }


def test_gp059_seals_gate_without_activating_access():
    result = (
        evaluate_private_beta_access_activation_gate(
            grant_package(),
            runtime_state(),
        )
    )

    assert (
        result["activation_authorizable"]
        is True
    )

    assert (
        result["access_activation_performed"]
        is False
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


def test_gp059_fails_if_broker_lock_missing():
    state = runtime_state()

    state[
        "broker_submission_locked"
    ] = False

    result = (
        evaluate_private_beta_access_activation_gate(
            grant_package(),
            state,
        )
    )

    assert (
        result["activation_authorizable"]
        is False
    )

    assert (
        result["private_beta_access_opened"]
        is False
    )

    assert (
        "broker_submission_locked_required_true"
        in result["failures"]
    )


def test_gp059_rejects_live_auto_grant():
    package = grant_package()

    package["grant"][
        "live_auto_access"
    ] = True

    result = (
        evaluate_private_beta_access_activation_gate(
            package,
            runtime_state(),
        )
    )

    assert (
        result["activation_authorizable"]
        is False
    )

    assert (
        "live_auto_access_must_be_false"
        in result["failures"]
    )
