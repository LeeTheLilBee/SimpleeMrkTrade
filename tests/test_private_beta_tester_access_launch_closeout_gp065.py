from ob_owner_experience.private_beta_tester_access_launch_closeout import (
    closeout_private_beta_tester_access_launch,
)


def corridor():
    gp061 = {
        "entitlement_record_issued": True,
    }

    gp062 = {
        "credential_boundary_ready": True,
        "credential_material_created": False,
    }

    gp063 = {
        "session_activation_gate_ready": True,
        "tester_session_activated": False,
        "external_beta_access_opened": False,
    }

    gp064 = {
        "first_access_audit_ready": True,
        "first_access_occurred": False,
        "receipt_recorded": False,
    }

    return (
        gp061,
        gp062,
        gp063,
        gp064,
    )


def test_gp065_closes_at_owner_walkthrough_boundary():
    result = (
        closeout_private_beta_tester_access_launch(
            *corridor()
        )
    )

    assert (
        result["launch_preparation_closeout_ready"]
        is True
    )

    assert (
        result["owner_walkthrough_required"]
        is True
    )

    assert (
        result["owner_walkthrough_completed"]
        is False
    )

    assert (
        result["first_external_tester_launch_authorized"]
        is False
    )

    assert (
        result["external_beta_access_opened"]
        is False
    )

    assert (
        result["manual_live_owner_only"]
        is True
    )

    assert (
        result["live_auto_locked"]
        is True
    )

    assert result["recommendation"] == (
        "GO_FOR_OWNER_PRIVATE_BETA_WALKTHROUGH_BEFORE_FIRST_TESTER"
    )

    assert result["walkthrough_timing"] == (
        "NOW_AFTER_GP065_REMOTE_VERIFICATION_BEFORE_FIRST_EXTERNAL_TESTER"
    )


def test_gp065_fails_if_session_was_activated_early():
    gp061, gp062, gp063, gp064 = (
        corridor()
    )

    gp063[
        "tester_session_activated"
    ] = True

    result = (
        closeout_private_beta_tester_access_launch(
            gp061,
            gp062,
            gp063,
            gp064,
        )
    )

    assert (
        result["launch_preparation_closeout_ready"]
        is False
    )

    assert (
        "tester_session_activated_must_be_false"
        in result["failures"]
    )
