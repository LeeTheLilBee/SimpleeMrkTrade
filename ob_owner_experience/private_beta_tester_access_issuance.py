from __future__ import annotations

import hashlib

from typing import Any, Mapping


PACKAGE = "GP061"

TITLE = (
    "Private Beta Tester Access Issuance"
)


ALLOWED_MODES = (
    "Survey",
    "Paper",
)


ALLOWED_ROOMS = (
    "Dashboard",
    "Market Map",
    "Symbol Page",
    "Trade Center",
    "Review Center",
)


DENIED_ROOMS = (
    "Owner Console",
)


def _stable_access_id(
    tester_id: str,
) -> str:
    digest = hashlib.sha256(
        (
            "ob-private-beta:"
            + tester_id
        ).encode(
            "utf-8"
        )
    ).hexdigest()[:20]

    return (
        "ob-beta-access-"
        + digest
    )


def issue_private_beta_tester_access(
    authorization_closeout: Mapping[str, Any],
    tester: Mapping[str, Any],
) -> dict[str, Any]:

    failures: list[str] = []

    tester_id = str(
        tester.get(
            "tester_id"
        )
        or ""
    ).strip()

    if (
        authorization_closeout.get(
            "closeout_ready"
        )
        is not True
    ):
        failures.append(
            "gp060_closeout_required"
        )

    if (
        authorization_closeout.get(
            "recommendation"
        )
        !=
        "GO_FOR_PRIVATE_BETA_TESTER_ACCESS_ISSUANCE"
    ):
        failures.append(
            "gp060_issuance_recommendation_required"
        )

    if not tester_id:
        failures.append(
            "tester_id_required"
        )

    required_true = (
        "owner_approved_for_beta",
        "tower_identity_reference_ready",
        "beta_terms_acknowledged",
        "survey_approved",
        "paper_approved",
    )

    for key in required_true:
        if (
            tester.get(key)
            is not True
        ):
            failures.append(
                f"{key}_required_true"
            )

    forbidden_true = (
        "owner_role",
        "owner_console_allowed",
        "manual_live_allowed",
        "live_auto_allowed",
        "broker_submission_allowed",
        "real_capital_allowed",
        "permission_admin_allowed",
        "secret_access_allowed",
    )

    for key in forbidden_true:
        if (
            tester.get(key)
            is True
        ):
            failures.append(
                f"{key}_must_be_false"
            )

    ready = not failures

    access_id = (
        _stable_access_id(
            tester_id
        )
        if tester_id
        else None
    )

    return {
        "package": PACKAGE,
        "title": TITLE,
        "gate_state": (
            "private_beta_tester_access_issuance_sealed"
            if ready
            else
            "private_beta_tester_access_issuance_hold"
        ),
        "tester_id": (
            tester_id
            if tester_id
            else None
        ),
        "access_id": access_id,
        "entitlement_record_issued": ready,
        "allowed_modes": list(
            ALLOWED_MODES
        ),
        "allowed_rooms": list(
            ALLOWED_ROOMS
        ),
        "denied_rooms": list(
            DENIED_ROOMS
        ),
        "tower_managed": True,
        "revocable": True,
        "credential_material_issued": False,
        "password_generated": False,
        "token_generated": False,
        "secret_revealed": False,
        "tester_session_created": False,
        "tester_session_activated": False,
        "external_beta_access_opened": False,
        "manual_live_allowed": False,
        "live_auto_allowed": False,
        "broker_submission_allowed": False,
        "real_capital_allowed": False,
        "failures": failures,
        "recommendation": (
            "GO_FOR_TOWER_TESTER_CREDENTIAL_PROVISIONING_BOUNDARY"
            if ready
            else
            "NO_GO_HOLD_PRIVATE_BETA_TESTER_ACCESS_ISSUANCE"
        ),
    }
