from ob_owner_experience.private_beta_tester_session_activation_gate import (
    evaluate_private_beta_tester_session_activation_gate,
)


def credential_boundary():
    return {
        "credential_boundary_ready": True,
        "credential_material_created": False,
        "external_beta_access_opened": False,
    }


def runtime():
    return {
        "tower_identity_gate_ready": True,
        "tower_authentication_required": True,
        "mfa_required": True,
        "session_expiration_required": True,
        "session_revocation_ready": True,
        "access_receipt_required": True,
        "anonymous_default_deny": True,
        "non_owner_owner_console_deny": True,
        "manual_live_owner_only": True,
        "live_auto_locked": True,
        "broker_submission_locked": True,
        "real_capital_movement_locked": True,
        "direct_execution_disabled": True,
        "automated_execution_disabled": True,
        "production_deploy_disabled": True,
    }


def test_gp063_seals_session_gate_without_session_activation():
    result = (
        evaluate_private_beta_tester_session_activation_gate(
            credential_boundary(),
            runtime(),
        )
    )

    assert (
        result["session_activation_gate_ready"]
        is True
    )

    assert (
        result["tester_session_created"]
        is False
    )

    assert (
        result["tester_session_activated"]
        is False
    )

    assert (
        result["external_beta_access_opened"]
        is False
    )

    assert (
        result["owner_console_access_allowed"]
        is False
    )

    assert (
        result["manual_live_allowed"]
        is False
    )


def test_gp063_fails_without_default_deny():
    state = runtime()

    state[
        "anonymous_default_deny"
    ] = False

    result = (
        evaluate_private_beta_tester_session_activation_gate(
            credential_boundary(),
            state,
        )
    )

    assert (
        result["session_activation_gate_ready"]
        is False
    )

    assert (
        "anonymous_default_deny_required_true"
        in result["failures"]
    )
