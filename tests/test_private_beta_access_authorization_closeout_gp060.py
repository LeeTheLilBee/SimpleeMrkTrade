from ob_owner_experience.private_beta_access_authorization_closeout import (
    closeout_private_beta_access_authorization,
)


def corridor_packages():
    gp056 = {
        "access_authorization_ready": True,
    }

    gp057 = {
        "eligibility_ready": True,
    }

    gp058 = {
        "grant_prepared": True,
    }

    gp059 = {
        "activation_authorizable": True,
        "private_beta_access_opened": False,
        "tester_credentials_issued": False,
        "tester_session_created": False,
        "permission_mutation_performed": False,
    }

    return (
        gp056,
        gp057,
        gp058,
        gp059,
    )


def test_gp060_closes_corridor_for_gp061():
    result = (
        closeout_private_beta_access_authorization(
            *corridor_packages()
        )
    )

    assert (
        result["closeout_ready"]
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

    assert (
        result["manual_live_owner_only"]
        is True
    )

    assert (
        result["live_auto_locked"]
        is True
    )

    assert result["recommendation"] == (
        "GO_FOR_PRIVATE_BETA_TESTER_ACCESS_ISSUANCE"
    )

    assert result["next_build"] == (
        "Private Beta Tester Access Issuance / GP061"
    )


def test_gp060_fails_if_gp059_not_authorizable():
    gp056, gp057, gp058, gp059 = (
        corridor_packages()
    )

    gp059[
        "activation_authorizable"
    ] = False

    result = (
        closeout_private_beta_access_authorization(
            gp056,
            gp057,
            gp058,
            gp059,
        )
    )

    assert (
        result["closeout_ready"]
        is False
    )

    assert (
        result["private_beta_access_opened"]
        is False
    )

    assert (
        "gp059_private_beta_access_activation_gate_required"
        in result["failures"]
    )
