
"""Tower Owner people + invitation authority projection / TWR136-TWR140."""

from __future__ import annotations

from typing import Any, Dict, List

from tower.identity_authority import (
    hosted_owner_identity_authority,
    hosted_owner_person_record,
)
from tower.invitation_access_lifecycle import (
    invitation_authority_snapshot,
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

ACCESS_LIFECYCLE_SOURCE_ID = (
    "tower.identity.access_onboarding_lifecycle"
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


def _invitation_truth(
    invitation_lifecycle: Dict[str, Any],
) -> Dict[str, Any]:

    if (
        invitation_lifecycle[
            "verification_state"
        ]
        == VERIFIED
    ):
        return verified_truth(
            value=list(
                invitation_lifecycle[
                    "invitations"
                ]
            ),
            source_id=INVITATION_AUTHORITY_SOURCE_ID,
            source_class=DERIVED,
            reason="durable_invitation_lifecycle_projection",
        ).as_dict()

    return not_configured_truth(
        source_id=INVITATION_AUTHORITY_SOURCE_ID,
        reason="invitation_store_not_configured",
    ).as_dict()


def _access_lifecycle_truth(
    invitation_lifecycle: Dict[str, Any],
) -> Dict[str, Any]:

    if (
        invitation_lifecycle[
            "verification_state"
        ]
        == VERIFIED
    ):
        return verified_truth(
            value={
                "state_counts":
                    dict(
                        invitation_lifecycle[
                            "state_counts"
                        ]
                    ),

                "pending_invitation_count":
                    invitation_lifecycle[
                        "pending_invitation_count"
                    ],

                "access_activation_state":
                    invitation_lifecycle[
                        "access_activation"
                    ][
                        "verification_state"
                    ],
            },
            source_id=ACCESS_LIFECYCLE_SOURCE_ID,
            source_class=DERIVED,
            reason="durable_invitation_onboarding_lifecycle",
        ).as_dict()

    return not_configured_truth(
        source_id=ACCESS_LIFECYCLE_SOURCE_ID,
        reason="invitation_access_lifecycle_not_configured",
    ).as_dict()


def owner_people_authority_snapshot() -> Dict[str, Any]:
    identity = (
        hosted_owner_identity_authority()
    )

    invitation_lifecycle = (
        invitation_authority_snapshot()
    )

    invitation_truth = (
        _invitation_truth(
            invitation_lifecycle
        )
    )

    access_lifecycle_truth = (
        _access_lifecycle_truth(
            invitation_lifecycle
        )
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
                    reason="hosted_owner_identity_not_configured",
                ).as_dict(),

            "invitations":
                invitation_truth,

            # Entitlement/account mutation is still separate.
            "access_control":
                not_configured_truth(
                    source_id=ACCESS_AUTHORITY_SOURCE_ID,
                    reason="access_mutation_authority_not_configured",
                ).as_dict(),

            "access_lifecycle":
                access_lifecycle_truth,

            "role_assignments":
                not_configured_truth(
                    source_id=ROLE_AUTHORITY_SOURCE_ID,
                    reason="hosted_owner_identity_not_configured",
                ).as_dict(),

            "app_entitlements":
                not_configured_truth(
                    source_id=ENTITLEMENT_AUTHORITY_SOURCE_ID,
                    reason="hosted_owner_identity_not_configured",
                ).as_dict(),

            "organization_membership":
                not_configured_truth(
                    source_id=ORGANIZATION_AUTHORITY_SOURCE_ID,
                    reason="organization_membership_not_configured",
                ).as_dict(),

            "identity_authority":
                identity,

            "invitation_lifecycle":
                invitation_lifecycle,
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
                source_id=ORGANIZATION_AUTHORITY_SOURCE_ID,
                source_class=DERIVED,
                reason="hosted_owner_organization_projection",
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
                source_id=ORGANIZATION_AUTHORITY_SOURCE_ID,
                reason=organization[
                    "reason"
                ],
            ).as_dict()
        )

    else:
        organization_truth = (
            unknown_truth(
                source_id=ORGANIZATION_AUTHORITY_SOURCE_ID,
                reason=organization[
                    "reason"
                ],
            ).as_dict()
        )

    if entitlements:
        entitlement_truth = (
            verified_truth(
                value=entitlements,
                source_id=ENTITLEMENT_AUTHORITY_SOURCE_ID,
                source_class=DERIVED,
                reason="current_owner_role_access_policy",
            ).as_dict()
        )

    else:
        entitlement_truth = (
            unknown_truth(
                source_id=ENTITLEMENT_AUTHORITY_SOURCE_ID,
                reason="current_owner_app_access_policy_not_resolved",
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
                reason="hosted_owner_identity_projection",
            ).as_dict(),

        "invitations":
            invitation_truth,

        # Still not entitlement/account mutation authority.
        "access_control":
            not_configured_truth(
                source_id=ACCESS_AUTHORITY_SOURCE_ID,
                reason="access_mutation_authority_not_configured",
            ).as_dict(),

        "access_lifecycle":
            access_lifecycle_truth,

        "role_assignments":
            verified_truth(
                value=[
                    role_assignment,
                ],
                source_id=ROLE_AUTHORITY_SOURCE_ID,
                source_class=DERIVED,
                reason="current_hosted_owner_role_policy",
            ).as_dict(),

        "app_entitlements":
            entitlement_truth,

        "organization_membership":
            organization_truth,

        "identity_authority":
            identity,

        "invitation_lifecycle":
            invitation_lifecycle,
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
    # Account ACTIVE still requires a real activation authority.
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
