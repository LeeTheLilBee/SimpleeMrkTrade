
"""Tower Owner people/access authority boundary.

TWR126 removes sample human records from hosted Tower truth.

No authoritative people, invitation, role-assignment, or app-entitlement
provider is configured by this layer. Tower reports that absence explicitly.
"""

from __future__ import annotations

from typing import Any, Dict, List

from tower.truth_contract import (
    NOT_CONFIGURED,
    not_configured_truth,
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


def owner_people_authority_snapshot() -> Dict[str, Any]:
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
                    "authoritative_people_provider_not_configured"
                ),
            ).as_dict(),

        "invitations":
            not_configured_truth(
                source_id=INVITATION_AUTHORITY_SOURCE_ID,
                reason=(
                    "authoritative_invitation_provider_not_configured"
                ),
            ).as_dict(),

        "access_control":
            not_configured_truth(
                source_id=ACCESS_AUTHORITY_SOURCE_ID,
                reason=(
                    "authoritative_access_provider_not_configured"
                ),
            ).as_dict(),

        "role_assignments":
            not_configured_truth(
                source_id=ROLE_AUTHORITY_SOURCE_ID,
                reason=(
                    "authoritative_role_provider_not_configured"
                ),
            ).as_dict(),

        "app_entitlements":
            not_configured_truth(
                source_id=ENTITLEMENT_AUTHORITY_SOURCE_ID,
                reason=(
                    "authoritative_entitlement_provider_not_configured"
                ),
            ).as_dict(),
    }


# Compatibility projections intentionally return no human/account records.
# They exist only so older internal imports fail closed while later packs
# replace them with the authoritative identity provider.

def owner_people_records() -> List[Dict[str, Any]]:
    return []


def owner_invite_drafts() -> List[Dict[str, Any]]:  # tower-truth-compatibility-symbol
    return []


def owner_access_requests() -> List[Dict[str, Any]]:
    return []


def active_people() -> List[Dict[str, Any]]:
    return []


def staged_people() -> List[Dict[str, Any]]:
    return []


def pending_owner_review_requests() -> List[Dict[str, Any]]:
    return []


def person_by_id(
    person_id: str,
) -> Dict[str, Any] | None:
    return None
