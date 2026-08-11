from ob_owner_experience.private_beta_first_access_receipt_audit_trail import (
    prepare_private_beta_first_access_receipt_audit_trail,
)


def session_gate():
    return {
        "session_activation_gate_ready": True,
        "tester_session_activated": False,
        "external_beta_access_opened": False,
    }


def issuance():
    return {
        "tester_id": (
            "private-beta-evidence-candidate"
        ),
        "access_id": (
            "ob-beta-access-evidence"
        ),
    }


def test_gp064_prepares_audit_without_claiming_first_access():
    result = (
        prepare_private_beta_first_access_receipt_audit_trail(
            session_gate(),
            issuance(),
        )
    )

    assert (
        result["first_access_audit_ready"]
        is True
    )

    assert (
        result["first_access_occurred"]
        is False
    )

    assert (
        result["receipt_recorded"]
        is False
    )

    assert (
        result["external_beta_access_opened"]
        is False
    )

    assert (
        result["credential_secret_recorded"]
        is False
    )

    assert (
        result["receipt_schema"][
            "append_only"
        ]
        is True
    )

    assert (
        result["audit_schema"][
            "record_credentials"
        ]
        is False
    )


def test_gp064_requires_session_gate():
    gate = session_gate()

    gate[
        "session_activation_gate_ready"
    ] = False

    result = (
        prepare_private_beta_first_access_receipt_audit_trail(
            gate,
            issuance(),
        )
    )

    assert (
        result["first_access_audit_ready"]
        is False
    )

    assert (
        "gp063_session_gate_required"
        in result["failures"]
    )
