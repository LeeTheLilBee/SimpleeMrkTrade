
"""Canonical secret-free hosted Tower identity projection / TWR131-TWR134.

The existing Tower login accepts hosted owner credentials from environment
configuration. This module projects that same configuration into product-safe
identity truth.

It does not authenticate passwords itself.
It does not expose credential material.
It does not create accounts.
It does not create organization membership.
It does not claim runtime availability.
"""

from __future__ import annotations

import hashlib
import os
from typing import Any, Dict, List

from tower.app_registry import registered_apps
from tower.truth_contract import (
    AUTHORITATIVE,
    DERIVED,
    NOT_CONFIGURED,
    UNKNOWN,
    UNVERIFIED,
    VERIFIED,
)


TOWER_OWNER_USERNAME_ENV = (
    "TOWER_OWNER_USERNAME"
)

TOWER_OWNER_PASSWORD_HASH_ENV = (
    "TOWER_OWNER_PASSWORD_HASH"
)

TOWER_OWNER_ID_ENV = (
    "TOWER_OWNER_ID"
)

TOWER_LOCAL_WALKTHROUGH_MODE_ENV = (
    "TOWER_LOCAL_WALKTHROUGH_MODE"
)

TOWER_OWNER_DISPLAY_NAME_ENV = (
    "TOWER_OWNER_DISPLAY_NAME"
)

TOWER_ORGANIZATION_ID_ENV = (
    "TOWER_ORGANIZATION_ID"
)

TOWER_ORGANIZATION_NAME_ENV = (
    "TOWER_ORGANIZATION_NAME"
)


OWNER_ROLE = "owner"

HOSTED_OWNER_IDENTITY_SOURCE_ID = (
    "tower.identity.hosted_owner_configuration"
)

OWNER_ROLE_POLICY_SOURCE_ID = (
    "tower.identity.current_owner_role_policy"
)

OWNER_ORGANIZATION_SOURCE_ID = (
    "tower.identity.owner_organization_configuration"
)

OWNER_APP_ACCESS_SOURCE_ID = (
    "tower.identity.current_owner_app_access_policy"
)


def _clean_env(
    name: str,
) -> str:
    return str(
        os.environ.get(
            name,
            "",
        )
        or ""
    ).strip()


def _flag_enabled(
    name: str,
) -> bool:
    return _clean_env(
        name
    ).lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def _stable_identifier(
    prefix: str,
    source: str,
) -> str:
    digest = hashlib.sha256(
        source.casefold().encode(
            "utf-8"
        )
    ).hexdigest()

    return (
        f"{prefix}_{digest[:24]}"
    )


def hosted_owner_identity_config_status() -> Dict[str, Any]:
    username = _clean_env(
        TOWER_OWNER_USERNAME_ENV
    )

    credential_hash_present = bool(
        _clean_env(
            TOWER_OWNER_PASSWORD_HASH_ENV
        )
    )

    local_mode = _flag_enabled(
        TOWER_LOCAL_WALKTHROUGH_MODE_ENV
    )

    configured = bool(
        username
        and credential_hash_present
        and not local_mode
    )

    if local_mode:
        reason = (
            "local_walkthrough_configuration_excluded_"
            "from_product_identity"
        )

    elif not username:
        reason = (
            "hosted_owner_username_not_configured"
        )

    elif not credential_hash_present:
        reason = (
            "hosted_owner_credential_hash_not_configured"
        )

    else:
        reason = (
            "hosted_owner_identity_configuration_present"
        )

    return {
        "configured":
            configured,

        "verification_state":
            (
                VERIFIED
                if configured
                else NOT_CONFIGURED
            ),

        "reason":
            reason,

        "username_configured":
            bool(username),

        "credential_hash_configured":
            credential_hash_present,

        "local_mode_excluded":
            local_mode,

        "credential_hash_value_exposed":
            False,

        "plaintext_password_exposed":
            False,

        "session_secret_exposed":
            False,
    }


def _organization_membership_projection(
) -> Dict[str, Any]:

    organization_id = _clean_env(
        TOWER_ORGANIZATION_ID_ENV
    )

    organization_name = _clean_env(
        TOWER_ORGANIZATION_NAME_ENV
    )

    if (
        not organization_id
        and not organization_name
    ):
        return {
            "verification_state":
                NOT_CONFIGURED,

            "source_class":
                None,

            "source_id":
                OWNER_ORGANIZATION_SOURCE_ID,

            "organization":
                None,

            "reason":
                "organization_membership_not_configured",
        }

    if not (
        organization_id
        and organization_name
    ):
        return {
            "verification_state":
                UNVERIFIED,

            "source_class":
                None,

            "source_id":
                OWNER_ORGANIZATION_SOURCE_ID,

            "organization":
                None,

            "reason":
                "organization_membership_configuration_partial",
        }

    return {
        "verification_state":
            VERIFIED,

        "source_class":
            AUTHORITATIVE,

        "source_id":
            OWNER_ORGANIZATION_SOURCE_ID,

        "organization": {
            "organization_id":
                organization_id,

            "organization_name":
                organization_name,

            "role":
                OWNER_ROLE,
        },

        "reason":
            "explicit_organization_membership_configuration",
    }


def _observatory_access_policy(
) -> Dict[str, Any] | None:

    observatory = None

    for app in registered_apps():

        if (
            app.get("app_id")
            == "observatory"
        ):
            observatory = app
            break

    if observatory is None:
        return None

    if (
        observatory.get("owner_only")
        is not True
    ):
        return None

    launch_route = str(
        observatory.get(
            "tower_launch_route",
            "",
        )
        or ""
    ).strip()

    if not launch_route:
        return None

    return {
        "app_id":
            "observatory",

        "app_name":
            str(
                observatory.get(
                    "app_name",
                    "The Observatory",
                )
            ),

        "access_policy":
            "GRANTED",

        "verification_state":
            VERIFIED,

        "source_class":
            DERIVED,

        "source_id":
            OWNER_APP_ACCESS_SOURCE_ID,

        "policy_basis":
            "current_owner_role_policy",

        "registry_status":
            str(
                observatory.get(
                    "app_status",
                    "",
                )
            ),

        "launch_route":
            launch_route,

        # IMPORTANT:
        # Access-policy truth is not runtime-health truth.
        "runtime_availability":
            None,

        "runtime_availability_state":
            UNKNOWN,

        "runtime_availability_reason":
            "runtime_provider_not_evaluated_by_identity_authority",
    }


def hosted_owner_identity_authority() -> Dict[str, Any]:
    configuration = (
        hosted_owner_identity_config_status()
    )

    organization = (
        _organization_membership_projection()
    )

    if not configuration[
        "configured"
    ]:
        return {
            "status":
                "tower_hosted_owner_identity_not_configured",

            "verification_state":
                NOT_CONFIGURED,

            "configured":
                False,

            "source_id":
                HOSTED_OWNER_IDENTITY_SOURCE_ID,

            "record":
                None,

            "role_assignment":
                None,

            "organization_membership":
                organization,

            "app_entitlements":
                [],

            "configuration":
                configuration,

            "credential_hash_value_exposed":
                False,

            "plaintext_password_exposed":
                False,

            "session_secret_exposed":
                False,
        }

    username = _clean_env(
        TOWER_OWNER_USERNAME_ENV
    )

    explicit_owner_id = _clean_env(
        TOWER_OWNER_ID_ENV
    )

    explicit_display_name = _clean_env(
        TOWER_OWNER_DISPLAY_NAME_ENV
    )

    if explicit_owner_id:
        person_id = explicit_owner_id
        person_id_source_class = (
            AUTHORITATIVE
        )
        session_subject_alignment = (
            VERIFIED
        )

    else:
        person_id = _stable_identifier(
            "tower_person",
            username,
        )
        person_id_source_class = (
            DERIVED
        )

        # The existing launcher still owns its own
        # legacy session-subject fallback until the
        # dedicated launcher cutover.
        session_subject_alignment = (
            UNKNOWN
        )

    account_id = _stable_identifier(
        "tower_account",
        username,
    )

    display_name = (
        explicit_display_name
        or username
    )

    display_name_source_class = (
        AUTHORITATIVE
        if explicit_display_name
        else DERIVED
    )

    role_assignment = {
        "person_id":
            person_id,

        "role":
            OWNER_ROLE,

        "verification_state":
            VERIFIED,

        "source_class":
            DERIVED,

        "source_id":
            OWNER_ROLE_POLICY_SOURCE_ID,

        "reason":
            "current_hosted_owner_login_policy",
    }

    observatory_access = (
        _observatory_access_policy()
    )

    entitlements: List[
        Dict[str, Any]
    ] = []

    if observatory_access is not None:
        entitlements.append(
            observatory_access
        )

    record = {
        "person_id":
            person_id,

        "person_id_source_class":
            person_id_source_class,

        "account_id":
            account_id,

        "account_id_source_class":
            DERIVED,

        "username":
            username,

        "username_source_class":
            AUTHORITATIVE,

        "display_name":
            display_name,

        "display_name_source_class":
            display_name_source_class,

        "role":
            OWNER_ROLE,

        "role_verification_state":
            VERIFIED,

        # TWR133:
        # We can prove hosted authentication configuration,
        # but we do not yet have an account suspension /
        # disablement lifecycle authority.
        "account_state":
            "AUTHENTICATION_CONFIGURED",

        "account_state_scope":
            "authentication_configuration_only",

        "authentication_state":
            "CONFIGURED",

        "authentication_state_verification":
            VERIFIED,

        "account_lifecycle_state":
            NOT_CONFIGURED,

        "suspension_state":
            None,

        "session_subject_alignment":
            session_subject_alignment,

        "organization":
            organization[
                "organization"
            ],

        "organization_membership_state":
            organization[
                "verification_state"
            ],

        "app_entitlements":
            entitlements,

        "credential_hash_configured":
            True,

        "credential_hash_value_exposed":
            False,

        "plaintext_password_exposed":
            False,

        "session_secret_exposed":
            False,

        "verification_state":
            VERIFIED,

        "source_id":
            HOSTED_OWNER_IDENTITY_SOURCE_ID,
    }

    return {
        "status":
            "tower_hosted_owner_identity_verified",

        "verification_state":
            VERIFIED,

        "configured":
            True,

        "source_id":
            HOSTED_OWNER_IDENTITY_SOURCE_ID,

        "record":
            record,

        "role_assignment":
            role_assignment,

        "organization_membership":
            organization,

        "app_entitlements":
            entitlements,

        "configuration":
            configuration,

        "credential_hash_value_exposed":
            False,

        "plaintext_password_exposed":
            False,

        "session_secret_exposed":
            False,
    }


def hosted_owner_person_record(
) -> Dict[str, Any] | None:
    return hosted_owner_identity_authority()[
        "record"
    ]


def hosted_owner_role_assignment(
) -> Dict[str, Any] | None:
    return hosted_owner_identity_authority()[
        "role_assignment"
    ]


def hosted_owner_app_entitlements(
) -> List[Dict[str, Any]]:
    return list(
        hosted_owner_identity_authority()[
            "app_entitlements"
        ]
    )
