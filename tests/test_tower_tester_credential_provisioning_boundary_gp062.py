from ob_owner_experience.tower_tester_credential_provisioning_boundary import (
    prepare_tower_tester_credential_boundary,
)


def issuance_state():
    return {
        "entitlement_record_issued": True,
        "tower_managed": True,
        "credential_material_issued": False,
        "secret_revealed": False,
        "external_beta_access_opened": False,
        "tester_id": (
            "private-beta-evidence-candidate"
        ),
        "access_id": (
            "ob-beta-access-evidence"
        ),
    }


def test_gp062_tower_owns_credential_boundary():
    result = (
        prepare_tower_tester_credential_boundary(
            issuance_state()
        )
    )

    assert (
        result["credential_boundary_ready"]
        is True
    )

    request = (
        result["provisioning_request"]
    )

    assert (
        request["credential_authority"]
        == "Tower"
    )

    assert (
        request["mfa_required"]
        is True
    )

    assert (
        request["plaintext_password_storage"]
        is False
    )

    assert (
        request["credential_secret_in_ob"]
        is False
    )

    assert (
        request["credential_secret_in_git"]
        is False
    )

    assert (
        result["credential_material_created"]
        is False
    )

    assert (
        result["external_beta_access_opened"]
        is False
    )


def test_gp062_fails_if_credentials_already_issued():
    state = issuance_state()

    state[
        "credential_material_issued"
    ] = True

    result = (
        prepare_tower_tester_credential_boundary(
            state
        )
    )

    assert (
        result["credential_boundary_ready"]
        is False
    )

    assert (
        "credential_material_must_not_already_exist"
        in result["failures"]
    )
