
"""Honest Tower application truth projection / TWR124.

This module deliberately does not treat app registration as runtime availability
or user entitlement.
"""

from __future__ import annotations

from typing import Any, Mapping

from tower.app_registry import registered_apps
from tower.truth_contract import (
    AUTHORITATIVE,
    DERIVED,
    AUTHORIZED,
    AVAILABLE,
    CONFIGURED,
    ENABLED,
    ENTITLED,
    LOCKED,
    PUBLISHED,
    REGISTERED,
    TowerTruthEnvelope,
    unknown_truth,
    verified_truth,
)


REGISTRY_SOURCE_ID = (
    "tower.app_registry:TOWER_APP_REGISTRY"
)


def _known(
    value: Any,
    *,
    reason: str,
    source_class: str = DERIVED,
) -> TowerTruthEnvelope:

    return verified_truth(
        value=value,
        source_id=REGISTRY_SOURCE_ID,
        source_class=source_class,
        reason=reason,
    )


def _unknown(
    dimension: str,
    *,
    reason: str,
) -> TowerTruthEnvelope:

    return unknown_truth(
        source_id=f"tower.runtime:{dimension.lower()}",
        reason=reason,
    )


def project_registered_app_truth(
    app: Mapping[str, Any],
) -> dict[str, Any]:

    app_id = str(
        app.get("app_id") or ""
    ).strip()

    if not app_id:
        raise ValueError(
            "Tower app registration requires app_id."
        )

    registry_status = str(
        app.get("app_status") or ""
    ).strip()

    if not registry_status:
        raise ValueError(
            f"Tower app {app_id!r} has no app_status."
        )

    is_future_registration = (
        registry_status == "registered_future_room"
    )

    is_ob_protected_staging = (
        app_id == "observatory"
        and registry_status == "protected_staging"
    )

    registered = _known(
        True,
        reason="present_in_canonical_app_registry",
        source_class=AUTHORITATIVE,
    )

    configured = _unknown(
        CONFIGURED,
        reason=(
            "registry_presence_does_not_verify_runtime_configuration"
        ),
    )

    if is_future_registration:
        published = _known(
            False,
            reason=(
                "registered_future_room_is_not_published_product"
            ),
        )

    elif is_ob_protected_staging:
        published = _known(
            True,
            reason=(
                "observatory_registry_contract_exposes_protected_owner_launch"
            ),
        )

    else:
        published = _unknown(
            PUBLISHED,
            reason=(
                "publication_state_requires_authoritative_product_provider"
            ),
        )

    entitled = _unknown(
        ENTITLED,
        reason=(
            "user_specific_entitlement_requires_identity_authority"
        ),
    )

    authorized = _unknown(
        AUTHORIZED,
        reason=(
            "authorization_requires_current_session_and_policy"
        ),
    )

    available = _unknown(
        AVAILABLE,
        reason=(
            "runtime_availability_requires_current_health_or_reachability_provider"
        ),
    )

    enabled = _unknown(
        ENABLED,
        reason=(
            "enabled_state_requires_authoritative_runtime_or_policy_provider"
        ),
    )

    locked = _known(
        bool(
            app.get(
                "dangerous_actions_locked",
                True,
            )
        ),
        reason=(
            "registry_dangerous_actions_lock_contract"
        ),
        source_class=AUTHORITATIVE,
    )

    live_auto_locked = _known(
        bool(
            app.get(
                "live_auto_locked",
                True,
            )
        ),
        reason=(
            "registry_live_auto_lock_contract"
        ),
        source_class=AUTHORITATIVE,
    )

    broker_execution_enabled = _known(
        bool(
            app.get(
                "broker_execution_enabled",
                False,
            )
        ),
        reason=(
            "registry_broker_execution_contract"
        ),
        source_class=AUTHORITATIVE,
    )

    capital_action_enabled = _known(
        bool(
            app.get(
                "capital_action_enabled",
                False,
            )
        ),
        reason=(
            "registry_capital_action_contract"
        ),
        source_class=AUTHORITATIVE,
    )

    states = {
        REGISTERED: registered,
        CONFIGURED: configured,
        PUBLISHED: published,
        ENTITLED: entitled,
        AUTHORIZED: authorized,
        AVAILABLE: available,
        ENABLED: enabled,
        LOCKED: locked,
    }

    return {
        "app_id": app_id,
        "app_name": str(
            app.get("app_name") or app_id
        ),
        "registry_status": registry_status,
        "states": {
            key: value.as_dict()
            for key, value in states.items()
        },
        "safety": {
            "live_auto_locked":
                live_auto_locked.as_dict(),

            "broker_execution_enabled":
                broker_execution_enabled.as_dict(),

            "capital_action_enabled":
                capital_action_enabled.as_dict(),
        },
        "launchable": False,
        "launchability_reason": (
            "Tower registry alone cannot prove "
            "current entitlement, authorization, "
            "availability, and enabled state."
        ),
    }


def registered_app_truth_projection() -> list[dict[str, Any]]:

    return [
        project_registered_app_truth(app)
        for app in registered_apps()
    ]


def app_truth_by_id(
    app_id: str,
) -> dict[str, Any] | None:

    normalized = str(
        app_id or ""
    ).strip()

    for projection in registered_app_truth_projection():
        if projection["app_id"] == normalized:
            return projection

    return None


def future_registered_apps() -> list[dict[str, Any]]:

    return [
        projection
        for projection
        in registered_app_truth_projection()
        if projection["registry_status"]
        == "registered_future_room"
    ]
