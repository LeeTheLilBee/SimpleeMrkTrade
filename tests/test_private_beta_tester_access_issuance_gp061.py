from ob_owner_experience.private_beta_tester_access_issuance import (
    issue_private_beta_tester_access,
)


def gp060_state():
    return {
        "closeout_ready": True,
        "recommendation": (
            "GO_FOR_PRIVATE_BETA_TESTER_ACCESS_ISSUANCE"
        ),
    }


def tester_state():
    return {
        "tester_id": (
            "private-beta-evidence-candidate"
        ),
        "owner_approved_for_beta": True,
        "tower_identity_reference_ready": True,
        "beta_terms_acknowledged": True,
        "survey_approved": True,
        "paper_approved": True,
        "owner_role": False,
        "owner_console_allowed": False,
        "manual_live_allowed": False,
        "live_auto_allowed": False,
        "broker_submission_allowed": False,
        "real_capital_allowed": False,
        "permission_admin_allowed": False,
        "secret_access_allowed": False,
    }


def test_gp061_issues_scoped_entitlement_without_credentials():
    result = (
        issue_private_beta_tester_access(
            gp060_state(),
            tester_state(),
        )
    )

    assert (
        result["entitlement_record_issued"]
        is True
    )

    assert (
        result["credential_material_issued"]
        is False
    )

    assert (
        result["password_generated"]
        is False
    )

    assert (
        result["token_generated"]
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
        "Owner Console"
        in result["denied_rooms"]
    )

    assert (
        result["allowed_modes"]
        == [
            "Survey",
            "Paper",
        ]
    )


def test_gp061_rejects_manual_live_permission():
    tester = tester_state()

    tester[
        "manual_live_allowed"
    ] = True

    result = (
        issue_private_beta_tester_access(
            gp060_state(),
            tester,
        )
    )

    assert (
        result["entitlement_record_issued"]
        is False
    )

    assert (
        "manual_live_allowed_must_be_false"
        in result["failures"]
    )
