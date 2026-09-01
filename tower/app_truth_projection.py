"""Authoritative Tower application truth projection / TWR124 + TWR141-TWR145.

Registration, implementation, publication, availability, health,
entitlement, request authorization, enabled state, and safety locks are
deliberately independent facts.

Registry presence never manufactures operational availability.
"""

from __future__ import annotations

from typing import Any, Mapping

from tower.app_publication_authority import (
    ENVIRONMENT_AVAILABLE,
    HEALTH_VERIFIED,
    IMPLEMENTED,
    PUBLISHED as PUBLICATION_DIMENSION,
    app_dimension_truth,
    app_publication_authority_snapshot,
    publication_authority_configured_truth,
)
from tower.app_registry import registered_apps
from tower.identity_authority import (
    hosted_owner_identity_authority,
)
from tower.truth_contract import (
    AUTHORITATIVE,
    DERIVED,
    AUTHORIZED,
    AVAILABLE,
    CONFIGURED,
    ENABLED,
    ENTITLED,
    LOCKED,
    NOT_CONFIGURED,
    PUBLISHED,
    REGISTERED,
    UNKNOWN,
    VERIFIED,
    TowerTruthEnvelope,
    not_configured_truth,
    product_display_projection,
    unavailable_truth,
    unknown_truth,
    verified_truth,
)


REGISTRY_SOURCE_ID = (
    "tower.app_registry:TOWER_APP_REGISTRY"
)

OWNER_ENTITLEMENT_SOURCE_ID = (
    "tower.identity.current_owner_app_access_policy"
)


def _registry_truth(
    value: Any,
    *,
    reason: str,
) -> TowerTruthEnvelope:

    return verified_truth(
        value=value,
        source_id=REGISTRY_SOURCE_ID,
        source_class=AUTHORITATIVE,
        reason=reason,
    )


def _unknown(
    dimension: str,
    *,
    reason: str,
) -> TowerTruthEnvelope:

    return unknown_truth(
        source_id=(
            f"tower.runtime:"
            f"{dimension.lower()}"
        ),
        reason=reason,
    )


def _owner_entitlement_truth(
    app_id: str,
) -> TowerTruthEnvelope:

    identity = (
        hosted_owner_identity_authority()
    )

    if identity.get(
        "verification_state"
    ) != VERIFIED:

        return not_configured_truth(
            source_id=(
                f"{OWNER_ENTITLEMENT_SOURCE_ID}:"
                f"{app_id}"
            ),
            reason=(
                "hosted_owner_identity_not_configured"
            ),
        )

    entitlements = identity.get(
        "app_entitlements",
        [],
    )

    for entitlement in entitlements:

        if entitlement.get(
            "app_id"
        ) != app_id:
            continue

        if (
            entitlement.get(
                "verification_state"
            ) == VERIFIED
            and entitlement.get(
                "access_policy"
            ) == "GRANTED"
        ):
            return verified_truth(
                value=True,
                source_id=(
                    f"{OWNER_ENTITLEMENT_SOURCE_ID}:"
                    f"{app_id}"
                ),
                source_class=DERIVED,
                reason=(
                    "verified_current_owner_app_access_policy"
                ),
            )

        return unavailable_truth(
            source_id=(
                f"{OWNER_ENTITLEMENT_SOURCE_ID}:"
                f"{app_id}"
            ),
            reason=(
                "owner_app_entitlement_present_but_not_verified"
            ),
        )

    return verified_truth(
        value=False,
        source_id=(
            f"{OWNER_ENTITLEMENT_SOURCE_ID}:"
            f"{app_id}"
        ),
        source_class=DERIVED,
        reason=(
            "verified_owner_identity_has_no_granted_app_entitlement"
        ),
    )


def _real_tower_launch_route_truth(
    app: Mapping[str, Any],
) -> TowerTruthEnvelope:

    route = str(
        app.get(
            "tower_launch_route"
        )
        or ""
    ).strip()

    configured = bool(
        route.startswith(
            "/tower/launch/"
        )
        and route
        != "/tower/app-registry"
    )

    return _registry_truth(
        configured,
        reason=(
            "canonical_registry_real_tower_launch_route_check"
        ),
    )


def _fresh_verified_true(
    envelope: TowerTruthEnvelope,
    *,
    now_utc: str | None = None,
) -> bool:

    display = product_display_projection(
        envelope,
        now_utc=now_utc,
    )

    return bool(
        display[
            "display_state"
        ] == VERIFIED
        and display[
            "display_value"
        ] is True
    )


def project_registered_app_truth(
    app: Mapping[str, Any],
    *,
    now_utc: str | None = None,
) -> dict[str, Any]:

    app_id = str(
        app.get(
            "app_id"
        )
        or ""
    ).strip()

    if not app_id:
        raise ValueError(
            "Tower app registration requires app_id."
        )

    registry_status = str(
        app.get(
            "app_status"
        )
        or ""
    ).strip()

    if not registry_status:
        raise ValueError(
            f"Tower app {app_id!r} has no app_status."
        )

    authority = (
        app_publication_authority_snapshot()
    )

    registered = _registry_truth(
        True,
        reason=(
            "present_in_canonical_app_registry"
        ),
    )

    configured = (
        publication_authority_configured_truth(
            snapshot=authority
        )
    )

    implemented = app_dimension_truth(
        app_id,
        IMPLEMENTED,
        snapshot=authority,
    )

    published = app_dimension_truth(
        app_id,
        PUBLICATION_DIMENSION,
        snapshot=authority,
    )

    environment_available = (
        app_dimension_truth(
            app_id,
            ENVIRONMENT_AVAILABLE,
            snapshot=authority,
        )
    )

    health_verified = (
        app_dimension_truth(
            app_id,
            HEALTH_VERIFIED,
            snapshot=authority,
        )
    )

    user_entitled = (
        _owner_entitlement_truth(
            app_id
        )
    )

    authorized = _unknown(
        AUTHORIZED,
        reason=(
            "authorization_requires_current_request_session_and_policy"
        ),
    )

    enabled = _unknown(
        ENABLED,
        reason=(
            "enabled_state_requires_authoritative_runtime_or_policy_provider"
        ),
    )

    locked = _registry_truth(
        bool(
            app.get(
                "dangerous_actions_locked",
                True,
            )
        ),
        reason=(
            "registry_dangerous_actions_lock_contract"
        ),
    )

    live_auto_locked = _registry_truth(
        bool(
            app.get(
                "live_auto_locked",
                True,
            )
        ),
        reason=(
            "registry_live_auto_lock_contract"
        ),
    )

    broker_execution_enabled = (
        _registry_truth(
            bool(
                app.get(
                    "broker_execution_enabled",
                    False,
                )
            ),
            reason=(
                "registry_broker_execution_contract"
            ),
        )
    )

    capital_action_enabled = (
        _registry_truth(
            bool(
                app.get(
                    "capital_action_enabled",
                    False,
                )
            ),
            reason=(
                "registry_capital_action_contract"
            ),
        )
    )

    launch_route_configured = (
        _real_tower_launch_route_truth(
            app
        )
    )

    launchable = all((
        _fresh_verified_true(
            registered,
            now_utc=now_utc,
        ),

        _fresh_verified_true(
            implemented,
            now_utc=now_utc,
        ),

        _fresh_verified_true(
            published,
            now_utc=now_utc,
        ),

        _fresh_verified_true(
            environment_available,
            now_utc=now_utc,
        ),

        _fresh_verified_true(
            health_verified,
            now_utc=now_utc,
        ),

        _fresh_verified_true(
            user_entitled,
            now_utc=now_utc,
        ),

        _fresh_verified_true(
            launch_route_configured,
            now_utc=now_utc,
        ),
    ))

    states = {
        REGISTERED:
            registered,

        CONFIGURED:
            configured,

        PUBLISHED:
            published,

        ENTITLED:
            user_entitled,

        AUTHORIZED:
            authorized,

        AVAILABLE:
            environment_available,

        ENABLED:
            enabled,

        LOCKED:
            locked,
    }

    dimensions = {
        "registered":
            registered,

        "implemented":
            implemented,

        "published":
            published,

        "environment_available":
            environment_available,

        "health_verified":
            health_verified,

        "user_entitled":
            user_entitled,

        "launch_route_configured":
            launch_route_configured,
    }

    return {
        "app_id":
            app_id,

        "app_name":
            str(
                app.get(
                    "app_name"
                )
                or app_id
            ),

        "registry_status":
            registry_status,

        "states": {
            key:
                value.as_dict()
            for key, value
            in states.items()
        },

        "dimensions": {
            key:
                value.as_dict()
            for key, value
            in dimensions.items()
        },

        "display_dimensions": {
            key:
                product_display_projection(
                    value,
                    now_utc=now_utc,
                )
            for key, value
            in dimensions.items()
        },

        "safety": {
            "live_auto_locked":
                live_auto_locked.as_dict(),

            "broker_execution_enabled":
                broker_execution_enabled.as_dict(),

            "capital_action_enabled":
                capital_action_enabled.as_dict(),
        },

        "launchable":
            launchable,

        "launchability_reason":
            (
                "all_product_launch_requirements_verified"
                if launchable
                else
                "authoritative_app_launch_requirements_not_fully_verified"
            ),

        # Product-level launchability is not request authorization.
        "request_authorization_required":
            True,

        "request_authorization_state":
            UNKNOWN,

        "owner_session_gate_bypassed":
            False,

        "step_up_gate_bypassed":
            False,
    }


def registered_app_truth_projection(
    *,
    now_utc: str | None = None,
) -> list[dict[str, Any]]:

    return [
        project_registered_app_truth(
            app,
            now_utc=now_utc,
        )
        for app in registered_apps()
    ]


def app_truth_by_id(
    app_id: str,
    *,
    now_utc: str | None = None,
) -> dict[str, Any] | None:

    normalized = str(
        app_id
        or ""
    ).strip()

    for projection in (
        registered_app_truth_projection(
            now_utc=now_utc
        )
    ):
        if projection[
            "app_id"
        ] == normalized:
            return projection

    return None


def future_registered_apps(
    *,
    now_utc: str | None = None,
) -> list[dict[str, Any]]:

    return [
        projection
        for projection
        in registered_app_truth_projection(
            now_utc=now_utc
        )
        if projection[
            "registry_status"
        ]
        == "registered_future_room"
    ]


def verified_launchable_app_ids(
    *,
    now_utc: str | None = None,
) -> list[str]:

    return [
        projection[
            "app_id"
        ]
        for projection
        in registered_app_truth_projection(
            now_utc=now_utc
        )
        if projection[
            "launchable"
        ]
        is True
    ]
