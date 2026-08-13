from __future__ import annotations

from typing import Any, Mapping


PACKAGE = "OBUX003"

TITLE = (
    "Soulaana Universal Context and Permission Adapter"
)


ROOMS = (
    "Dashboard",
    "Market Map",
    "Symbol Page",
    "Trade Center",
    "Review Center",
    "Owner Console",
)


MODES = (
    "Survey",
    "Paper",
    "Manual Live",
    "Live Auto",
)


SENSITIVE_KEY_FRAGMENTS = (
    "secret",
    "token",
    "password",
    "credential",
    "api_key",
    "apikey",
    "private_key",
)


def _safe_mapping(
    value: Mapping[str, Any] | None,
) -> dict[str, Any]:

    value = dict(
        value
        or {}
    )

    cleaned = {}

    for key, item in value.items():

        lowered = str(
            key
        ).lower()

        if any(
            fragment in lowered
            for fragment in SENSITIVE_KEY_FRAGMENTS
        ):

            continue

        cleaned[
            key
        ] = item

    return cleaned


def apply_soulaana_context_permissions(
    universal_result: Mapping[str, Any],
    context: Mapping[str, Any],
) -> dict[str, Any]:

    role = str(
        context.get(
            "role"
        )
        or ""
    ).strip().lower()

    mode = str(
        context.get(
            "mode"
        )
        or ""
    ).strip()

    room = str(
        context.get(
            "room"
        )
        or ""
    ).strip()

    account = str(
        context.get(
            "account"
        )
        or ""
    ).strip()

    tower_clearance = bool(
        context.get(
            "tower_clearance",
            False,
        )
    )

    emotional_state = str(
        context.get(
            "emotional_state"
        )
        or ""
    ).strip().lower()


    failures: list[str] = []


    if role not in {
        "owner",
        "tester",
    }:

        failures.append(
            "recognized_role_required"
        )


    if mode not in MODES:

        failures.append(
            "recognized_mode_required"
        )


    if room not in ROOMS:

        failures.append(
            "recognized_room_required"
        )


    if not account:

        failures.append(
            "account_context_required"
        )


    if not tower_clearance:

        failures.append(
            "tower_clearance_required"
        )


    if (
        role == "tester"
        and
        room == "Owner Console"
    ):

        failures.append(
            "tester_owner_console_denied"
        )


    if (
        role == "tester"
        and
        mode == "Manual Live"
    ):

        failures.append(
            "tester_manual_live_denied"
        )


    if mode == "Live Auto":

        failures.append(
            "live_auto_locked"
        )


    tester_safe = _safe_mapping(
        context.get(
            "tester_safe_context"
        )
    )

    owner_only = _safe_mapping(
        context.get(
            "owner_only_context"
        )
    )


    if role == "owner":

        visible_context = {
            **tester_safe,
            **owner_only,
        }

    else:

        visible_context = dict(
            tester_safe
        )


    allowed = not failures


    if allowed:

        soulaana_access_explanation = (
            "Soulaana can explain this room using only the context "
            "this user is cleared to see."
        )

    else:

        if (
            "tester_owner_console_denied"
            in failures
        ):

            soulaana_access_explanation = (
                "Soulaana: Owner Console is an owner room. "
                "Your Observatory access stays inside your approved beta rooms."
            )

        elif (
            "tester_manual_live_denied"
            in failures
        ):

            soulaana_access_explanation = (
                "Soulaana: Manual Live is owner-only right now. "
                "Your beta session stays in Survey or Paper."
            )

        elif (
            "live_auto_locked"
            in failures
        ):

            soulaana_access_explanation = (
                "Soulaana: Live Auto is still sealed. "
                "No automated live execution is available."
            )

        elif (
            "tower_clearance_required"
            in failures
        ):

            soulaana_access_explanation = (
                "Soulaana: The Tower has not cleared this Observatory context."
            )

        else:

            soulaana_access_explanation = (
                "Soulaana: This context did not clear the Observatory permission contract."
            )


    return {
        "package": PACKAGE,
        "title": TITLE,
        "gate_state": (
            "soulaana_context_permission_adapter_sealed"
        ),
        "allowed": allowed,
        "failures": failures,
        "role": role or None,
        "mode": mode or None,
        "room": room or None,
        "account": account or None,
        "tower_clearance": tower_clearance,
        "emotional_state": emotional_state or None,
        "visible_context": visible_context,
        "owner_only_context_exposed_to_tester": False,
        "raw_secrets_exposed": False,
        "tester_manual_live_allowed": False,
        "live_auto_allowed": False,
        "soulaana_access_explanation": (
            soulaana_access_explanation
        ),
        "universal": dict(
            universal_result
        ),
        "recommendation": (
            "GO_FOR_SOULAANA_SIX_ROOM_COVERAGE_ADAPTER"
            if allowed
            else
            "HOLD_CONTEXT_OR_PERMISSION"
        ),
    }
