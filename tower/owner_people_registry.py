
"""Tower Owner people authority backed by hosted identity configuration.

TWR131-TWR135 binds the secret-free Owner People projection to the same
hosted owner configuration contract used by Tower authentication.

Invitation delivery, access mutation, and account lifecycle mutation remain
separate authority boundaries.
"""

from __future__ import annotations

from typing import Any, Dict, List

from tower.identity_authority import (
    hosted_owner_identity_authority,
    hosted_owner_person_record,
)
from tower.truth_contract import (
    DERIVED,
    NOT_CONFIGURED,
    UNKNOWN,
    VERIFIED,
    not_configured_truth,
    unknown_truth,
    verified_truth,
)


PEOPLE_AUTHORITY_SOURCE_ID = (
    "tower.identity.people_authority"
)

INVITATION_AUTHORITY_SOURCE_ID = (
    "tower.identity.invitation_authority"
)

ACCESS_AUTHORITY_SOURCE_ID = (
    "tower.identity.access_authority"
)

ROLE_AUTHORITY_SOURCE_ID = (
    "tower.identity.role_authority"
)

ENTITLEMENT_AUTHORITY_SOURCE_ID = (
    "tower.identity.entitlement_authority"
)

ORGANIZATION_AUTHORITY_SOURCE_ID = (
    "tower.identity.organization_authority"
)


def owner_people_authority_snapshot() -> Dict[str, Any]:
    identity = (
        hosted_owner_identity_authority()
    )

    if (
        identity["verification_state"]
        != VERIFIED
        or identity["record"]
        is None
    ):
        return {
            "status":
                "tower_people_authority_not_configured",

            "verification_state":
                NOT_CONFIGURED,

            "authoritative_provider_configured":
                False,

            "people":
                not_configured_truth(
                    source_id=PEOPLE_AUTHORITY_SOURCE_ID,
                    reason=(
                        "hosted_owner_identity_not_configured"
                    ),
                ).as_dict(),

            "invitations":
                not_configured_truth(
                    source_id=INVITATION_AUTHORITY_SOURCE_ID,
                    reason=(
                        "invitation_lifecycle_not_configured"
                    ),
                ).as_dict(),

            "access_control":
                not_configured_truth(
                    source_id=ACCESS_AUTHORITY_SOURCE_ID,
                    reason=(
                        "access_mutation_lifecycle_not_configured"
                    ),
                ).as_dict(),

            "role_assignments":
                not_configured_truth(
                    source_id=ROLE_AUTHORITY_SOURCE_ID,
                    reason=(
                        "hosted_owner_identity_not_configured"
                    ),
                ).as_dict(),

            "app_entitlements":
                not_configured_truth(
                    source_id=ENTITLEMENT_AUTHORITY_SOURCE_ID,
                    reason=(
                        "hosted_owner_identity_not_configured"
                    ),
                ).as_dict(),

            "organization_membership":
                not_configured_truth(
                    source_id=ORGANIZATION_AUTHORITY_SOURCE_ID,
                    reason=(
                        "organization_membership_not_configured"
                    ),
                ).as_dict(),

            "identity_authority":
                identity,
        }

    record = identity[
        "record"
    ]

    role_assignment = identity[
        "role_assignment"
    ]

    entitlements = list(
        identity[
            "app_entitlements"
        ]
    )

    organization = identity[
        "organization_membership"
    ]

    if (
        organization[
            "verification_state"
        ]
        == VERIFIED
    ):
        organization_truth = (
            verified_truth(
                value=organization[
                    "organization"
                ],
                source_id=(
                    ORGANIZATION_AUTHORITY_SOURCE_ID
                ),
                source_class=DERIVED,
                reason=(
                    "hosted_owner_organization_projection"
                ),
            ).as_dict()
        )

    elif (
        organization[
            "verification_state"
        ]
        == NOT_CONFIGURED
    ):
        organization_truth = (
            not_configured_truth(
                source_id=(
                    ORGANIZATION_AUTHORITY_SOURCE_ID
                ),
                reason=organization[
                    "reason"
                ],
            ).as_dict()
        )

    else:
        organization_truth = (
            unknown_truth(
                source_id=(
                    ORGANIZATION_AUTHORITY_SOURCE_ID
                ),
                reason=organization[
                    "reason"
                ],
            ).as_dict()
        )

    if entitlements:
        entitlement_truth = (
            verified_truth(
                value=entitlements,
                source_id=(
                    ENTITLEMENT_AUTHORITY_SOURCE_ID
                ),
                source_class=DERIVED,
                reason=(
                    "current_owner_role_access_policy"
                ),
            ).as_dict()
        )

    else:
        entitlement_truth = (
            unknown_truth(
                source_id=(
                    ENTITLEMENT_AUTHORITY_SOURCE_ID
                ),
                reason=(
                    "current_owner_app_access_policy_not_resolved"
                ),
            ).as_dict()
        )

    return {
        "status":
            "tower_people_authority_verified",

        "verification_state":
            VERIFIED,

        "authoritative_provider_configured":
            True,

        "people":
            verified_truth(
                value=[
                    record,
                ],
                source_id=PEOPLE_AUTHORITY_SOURCE_ID,
                source_class=DERIVED,
                reason=(
                    "hosted_owner_identity_projection"
                ),
            ).as_dict(),

        # These remain intentionally unconfigured.
        "invitations":
            not_configured_truth(
                source_id=INVITATION_AUTHORITY_SOURCE_ID,
                reason=(
                    "invitation_lifecycle_not_configured"
                ),
            ).as_dict(),

        "access_control":
            not_configured_truth(
                source_id=ACCESS_AUTHORITY_SOURCE_ID,
                reason=(
                    "access_mutation_lifecycle_not_configured"
                ),
            ).as_dict(),

        "role_assignments":
            verified_truth(
                value=[
                    role_assignment,
                ],
                source_id=ROLE_AUTHORITY_SOURCE_ID,
                source_class=DERIVED,
                reason=(
                    "current_hosted_owner_role_policy"
                ),
            ).as_dict(),

        "app_entitlements":
            entitlement_truth,

        "organization_membership":
            organization_truth,

        "identity_authority":
            identity,
    }


def owner_people_records() -> List[Dict[str, Any]]:
    record = (
        hosted_owner_person_record()
    )

    if record is None:
        return []

    return [
        record,
    ]


def owner_invite_drafts() -> List[Dict[str, Any]]:  # tower-truth-compatibility-symbol
    return []


def owner_access_requests() -> List[Dict[str, Any]]:
    return []


def active_people() -> List[Dict[str, Any]]:
    # "Active" is a lifecycle claim.
    #
    # TWR131-TWR135 does not have suspend/disable
    # lifecycle authority yet, so this remains empty.
    return []


def staged_people() -> List[Dict[str, Any]]:
    return []


def pending_owner_review_requests() -> List[Dict[str, Any]]:
    return []


def person_by_id(
    person_id: str,
) -> Dict[str, Any] | None:

    normalized = str(
        person_id
        or ""
    ).strip()

    if not normalized:
        return None

    for record in owner_people_records():

        if (
            record.get(
                "person_id"
            )
            == normalized
        ):
            return record

    return None
