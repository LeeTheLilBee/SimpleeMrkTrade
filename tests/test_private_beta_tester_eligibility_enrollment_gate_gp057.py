from ob_owner_experience.private_beta_tester_eligibility_enrollment_gate import (
    evaluate_private_beta_tester_eligibility,
)


def authorization_state():
    return {
        "access_authorization_ready": True,
    }


def candidate_state():
    return {
        "tester_id": "beta-tester-001",
        "invite_approved": True,
        "tower_identity_ready": True,
        "beta_terms_acknowledged": True,
        "survey_allowed": True,
        "paper_allowed": True,
        "owner_role": False,
        "manual_live_allowed": False,
        "live_auto_allowed": False,
        "broker_execution_allowed": False,
        "permission_admin_allowed": False,
        "secret_access_allowed": False,
    }


def test_gp057_eligible_tester_stays_unenrolled():
    result = (
        evaluate_private_beta_tester_eligibility(
            candidate_state(),
            authorization_state(),
        )
    )

    assert (
        result["eligibility_ready"]
        is True
    )

    assert (
        result["tester_enrolled"]
        is False
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


def test_gp057_rejects_manual_live_for_beta_tester():
    candidate = candidate_state()

    candidate[
        "manual_live_allowed"
    ] = True

    result = (
        evaluate_private_beta_tester_eligibility(
            candidate,
            authorization_state(),
        )
    )

    assert (
        result["eligibility_ready"]
        is False
    )

    assert (
        result["tester_enrolled"]
        is False
    )

    assert (
        "manual_live_allowed_must_be_false"
        in result["failures"]
    )
