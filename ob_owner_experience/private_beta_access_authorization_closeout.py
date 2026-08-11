from __future__ import annotations

from typing import Any, Mapping


PACKAGE = "GP060"

TITLE = (
    "Private Beta Access Authorization "
    "Closeout"
)


def closeout_private_beta_access_authorization(
    gp056: Mapping[str, Any],
    gp057: Mapping[str, Any],
    gp058: Mapping[str, Any],
    gp059: Mapping[str, Any],
) -> dict[str, Any]:

    failures: list[str] = []

    checks = (
        (
            "gp056_private_beta_access_authorization",
            gp056.get(
                "access_authorization_ready"
            ),
        ),
        (
            "gp057_private_beta_tester_eligibility",
            gp057.get(
                "eligibility_ready"
            ),
        ),
        (
            "gp058_private_beta_tester_access_grant",
            gp058.get(
                "grant_prepared"
            ),
        ),
        (
            "gp059_private_beta_access_activation_gate",
            gp059.get(
                "activation_authorizable"
            ),
        ),
    )

    for label, passed in checks:
        if passed is not True:
            failures.append(
                f"{label}_required"
            )

    if (
        gp059.get(
            "private_beta_access_opened"
        )
        is not False
    ):
        failures.append(
            "private_beta_access_must_remain_closed"
        )

    if (
        gp059.get(
            "tester_credentials_issued"
        )
        is not False
    ):
        failures.append(
            "tester_credentials_must_remain_unissued"
        )

    if (
        gp059.get(
            "tester_session_created"
        )
        is not False
    ):
        failures.append(
            "tester_session_must_not_be_created"
        )

    if (
        gp059.get(
            "permission_mutation_performed"
        )
        is not False
    ):
        failures.append(
            "permission_mutation_must_not_occur"
        )

    ready = not failures

    return {
        "package": PACKAGE,
        "title": TITLE,
        "gate_state": (
            "private_beta_access_authorization_closeout_sealed"
            if ready
            else
            "private_beta_access_authorization_closeout_hold"
        ),
        "closeout_ready": ready,
        "staging_ready": True,
        "tower_staging_accepted": True,
        "beta_launch_preparation_closeout_ready": True,
        "private_beta_access_opened": False,
        "tester_credentials_issued": False,
        "tester_session_created": False,
        "permission_mutation_performed": False,
        "production_deploy_disabled": True,
        "broker_submission_locked": True,
        "real_capital_movement_locked": True,
        "direct_execution_disabled": True,
        "automated_execution_disabled": True,
        "permission_mutations_disabled": True,
        "secret_reveal_disabled": True,
        "manual_live_owner_only": True,
        "live_auto_locked": True,
        "allowed_private_beta_modes": [
            "Survey",
            "Paper",
        ],
        "next_build": (
            "Private Beta Tester Access Issuance / GP061"
        ),
        "failures": failures,
        "recommendation": (
            "GO_FOR_PRIVATE_BETA_TESTER_ACCESS_ISSUANCE"
            if ready
            else
            "NO_GO_HOLD_PRIVATE_BETA_ACCESS_AUTHORIZATION_CLOSEOUT"
        ),
    }
