"""
TWR187 reservation promoted by TWR190.

The owner Teller entitlement is effective only when the canonical
Teller app and owner launch route are in their activated states.

This remains a role/policy fact. It does not fabricate external
publication, environment availability, health, or request authorization.
"""

from __future__ import annotations

from typing import Any, Dict

from tower.app_registry import (
    registered_apps,
    route_by_path,
)


TELLER_OWNER_ENTITLEMENT_RESERVATION_ID = (
    "tower.teller.owner_entitlement.reservation.twr187"
)

TELLER_OWNER_ACTIVATION_GATE = (
    "TWR190"
)

TELLER_OWNER_LAUNCH_ROUTE = (
    "/tower/launch/teller"
)


def _registered_teller(
) -> Dict[str, Any] | None:

    for app in registered_apps():

        if (
            app.get("app_id")
            == "teller"
        ):
            return dict(
                app
            )

    return None


def teller_owner_entitlement_reservation(
) -> Dict[str, Any]:

    teller = (
        _registered_teller()
    )

    route = route_by_path(
        TELLER_OWNER_LAUNCH_ROUTE
    )

    failures = []

    if teller is None:

        failures.append(
            "teller_not_registered"
        )

    else:

        if (
            teller.get("app_status")
            != "protected_hosted"
        ):
            failures.append(
                "teller_not_activated"
            )

        if (
            teller.get("tower_launch_route")
            != TELLER_OWNER_LAUNCH_ROUTE
        ):
            failures.append(
                "teller_launch_route_not_active"
            )

        if (
            teller.get("requires_tower_handoff")
            is not True
        ):
            failures.append(
                "teller_handoff_requirement_missing"
            )

        # Teller itself stays multi-role.
        if (
            teller.get("owner_only")
            is not False
        ):
            failures.append(
                "teller_app_incorrectly_owner_only"
            )

        if (
            teller.get("dangerous_actions_locked")
            is not True
        ):
            failures.append(
                "teller_danger_lock_missing"
            )

        if (
            teller.get("live_auto_locked")
            is not True
        ):
            failures.append(
                "teller_live_auto_lock_missing"
            )

        if (
            teller.get("broker_execution_enabled")
            is not False
        ):
            failures.append(
                "teller_broker_authority_unexpected"
            )

        if (
            teller.get("capital_action_enabled")
            is not False
        ):
            failures.append(
                "teller_capital_authority_unexpected"
            )

    if route is None:

        failures.append(
            "teller_owner_route_missing"
        )

    else:

        checks = (
            (
                route.get("route_id")
                == "teller_owner_launch",
                "teller_owner_route_id_invalid",
            ),
            (
                route.get("app_id")
                == "teller",
                "teller_owner_route_wrong_app",
            ),
            (
                route.get("owner_only")
                is True,
                "teller_owner_route_not_owner_only",
            ),
            (
                route.get("requires_owner_session")
                is True,
                "teller_owner_route_missing_owner_session",
            ),
            (
                route.get("requires_step_up")
                is True,
                "teller_owner_route_missing_step_up",
            ),
            (
                route.get("default_denied_when_unknown")
                is True,
                "teller_owner_route_not_default_deny",
            ),
            (
                route.get("temporary_placeholder")
                is False,
                "teller_owner_route_still_placeholder",
            ),
            (
                route.get("lock_state")
                == "protected_owner_handoff",
                "teller_owner_route_wrong_lock_state",
            ),
        )

        for ok, reason in checks:

            if not ok:
                failures.append(
                    reason
                )

    activated = (
        not failures
    )

    return {
        "reservation_id":
            TELLER_OWNER_ENTITLEMENT_RESERVATION_ID,

        "app_id":
            "teller",

        "role":
            "owner",

        "policy_contract_verified":
            activated,

        "reservation_state":
            (
                "ACTIVATED"
                if activated
                else "NOT_READY"
            ),

        "intended_access_policy":
            (
                "GRANTED"
                if activated
                else "DENIED"
            ),

        "effective_entitlement":
            activated,

        "effective_entitlement_source":
            (
                "current_owner_role_policy_twr190"
                if activated
                else None
            ),

        "activation_gate":
            TELLER_OWNER_ACTIVATION_GATE,

        "launch_corridor":
            TELLER_OWNER_LAUNCH_ROUTE,

        "requires_owner_session":
            True,

        "requires_step_up":
            True,

        "requires_tower_handoff":
            True,

        "default_deny":
            True,

        "publication_truth_required_for_launch":
            True,

        "failures":
            failures,
    }


def teller_owner_entitlement_reservation_ready(
) -> bool:

    value = (
        teller_owner_entitlement_reservation()
    )

    return bool(
        value[
            "policy_contract_verified"
        ]
        and value[
            "reservation_state"
        ]
        == "ACTIVATED"
        and value[
            "effective_entitlement"
        ]
        is True
    )
