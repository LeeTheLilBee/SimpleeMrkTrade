from __future__ import annotations

from typing import Any, Mapping


PACKAGE = "GP058"

TITLE = (
    "Private Beta Tester Access "
    "Grant Preparation"
)


BETA_ALLOWED_ROOMS = (
    "Dashboard",
    "Market Map",
    "Symbol Page",
    "Trade Center",
    "Review Center",
)


BETA_EXCLUDED_ROOMS = (
    "Owner Console",
)


def prepare_private_beta_tester_access_grant(
    candidate: Mapping[str, Any],
    eligibility: Mapping[str, Any],
) -> dict[str, Any]:

    failures: list[str] = []

    tester_id = str(
        eligibility.get("tester_id")
        or candidate.get("tester_id")
        or ""
    ).strip()

    if (
        eligibility.get(
            "eligibility_ready"
        )
        is not True
    ):
        failures.append(
            "gp057_eligibility_required"
        )

    if not tester_id:
        failures.append(
            "tester_id_required"
        )

    if (
        eligibility.get(
            "manual_live_allowed"
        )
        is not False
    ):
        failures.append(
            "manual_live_must_remain_denied"
        )

    if (
        eligibility.get(
            "live_auto_allowed"
        )
        is not False
    ):
        failures.append(
            "live_auto_must_remain_denied"
        )

    if (
        eligibility.get(
            "broker_execution_allowed"
        )
        is not False
    ):
        failures.append(
            "broker_execution_must_remain_denied"
        )

    if (
        eligibility.get(
            "permission_admin_allowed"
        )
        is not False
    ):
        failures.append(
            "permission_admin_must_remain_denied"
        )

    if (
        eligibility.get(
            "secret_access_allowed"
        )
        is not False
    ):
        failures.append(
            "secret_access_must_remain_denied"
        )

    prepared = not failures

    grant = {
        "tester_id": (
            tester_id
            if tester_id
            else None
        ),
        "allowed_modes": [
            "Survey",
            "Paper",
        ],
        "allowed_rooms": list(
            BETA_ALLOWED_ROOMS
        ),
        "excluded_rooms": list(
            BETA_EXCLUDED_ROOMS
        ),
        "tower_authentication_required": True,
        "tower_session_required": True,
        "tower_authorization_required": True,
        "revocable": True,
        "expires_or_revokes_fail_closed": True,
        "owner_console_access": False,
        "manual_live_access": False,
        "live_auto_access": False,
        "broker_submission_access": False,
        "real_capital_access": False,
        "permission_admin_access": False,
        "secret_access": False,
    }

    return {
        "package": PACKAGE,
        "title": TITLE,
        "gate_state": (
            "private_beta_tester_access_grant_prepared"
            if prepared
            else
            "private_beta_tester_access_grant_hold"
        ),
        "grant_prepared": prepared,
        "grant": grant,
        "credential_issued": False,
        "tester_session_created": False,
        "permission_mutation_performed": False,
        "access_activated": False,
        "failures": failures,
        "recommendation": (
            "GO_FOR_PRIVATE_BETA_ACCESS_ACTIVATION_GATE"
            if prepared
            else
            "NO_GO_HOLD_PRIVATE_BETA_TESTER_ACCESS_GRANT"
        ),
    }
