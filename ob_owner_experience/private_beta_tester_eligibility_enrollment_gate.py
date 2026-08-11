from __future__ import annotations

from typing import Any, Mapping


PACKAGE = "GP057"

TITLE = (
    "Private Beta Tester Eligibility "
    "& Enrollment Gate"
)


REQUIRED_CANDIDATE_TRUE = (
    "invite_approved",
    "tower_identity_ready",
    "beta_terms_acknowledged",
    "survey_allowed",
    "paper_allowed",
)


FORBIDDEN_CANDIDATE_TRUE = (
    "owner_role",
    "manual_live_allowed",
    "live_auto_allowed",
    "broker_execution_allowed",
    "permission_admin_allowed",
    "secret_access_allowed",
)


def evaluate_private_beta_tester_eligibility(
    candidate: Mapping[str, Any],
    authorization: Mapping[str, Any],
) -> dict[str, Any]:

    failures: list[str] = []

    tester_id = str(
        candidate.get("tester_id")
        or ""
    ).strip()

    if (
        authorization.get(
            "access_authorization_ready"
        )
        is not True
    ):
        failures.append(
            "gp056_access_authorization_required"
        )

    if not tester_id:
        failures.append(
            "tester_id_required"
        )

    for key in REQUIRED_CANDIDATE_TRUE:
        if candidate.get(key) is not True:
            failures.append(
                f"{key}_required_true"
            )

    for key in FORBIDDEN_CANDIDATE_TRUE:
        if candidate.get(key) is True:
            failures.append(
                f"{key}_must_be_false"
            )

    eligible = not failures

    return {
        "package": PACKAGE,
        "title": TITLE,
        "gate_state": (
            "private_beta_tester_eligibility_gate_sealed"
            if eligible
            else
            "private_beta_tester_eligibility_hold"
        ),
        "tester_id": (
            tester_id
            if tester_id
            else None
        ),
        "eligibility_ready": eligible,
        "tester_enrolled": False,
        "enrollment_mutation_performed": False,
        "credential_issued": False,
        "tester_session_created": False,
        "access_activated": False,
        "allowed_modes": [
            "Survey",
            "Paper",
        ],
        "manual_live_allowed": False,
        "live_auto_allowed": False,
        "broker_execution_allowed": False,
        "permission_admin_allowed": False,
        "secret_access_allowed": False,
        "failures": failures,
        "recommendation": (
            "GO_FOR_PRIVATE_BETA_TESTER_ACCESS_GRANT_PREPARATION"
            if eligible
            else
            "NO_GO_HOLD_PRIVATE_BETA_TESTER_ELIGIBILITY"
        ),
    }
