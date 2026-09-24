"""
TWR195 — Resolve Teller persistence authority from Tower-owned truth.

First hosted crossing remains owner-only.

actor_id:
    current verified Tower owner person_id

business_key:
    current verified Tower organization_id

tower_session_id:
    Tower-generated authenticated-session identifier carried through
    the signed one-time handoff and signed access receipt.

receipt_id:
    Tower-generated access receipt ID from the consumed handoff.

Browser/request-body actor, role, business, session, and receipt values
are never authoritative.
"""

from __future__ import annotations

import hmac

from collections.abc import Mapping

from tower.identity_authority import (
    hosted_owner_identity_authority,
)


class TellerPersistenceAuthorityError(
    ValueError
):

    def __init__(
        self,
        code,
    ):
        self.code = str(
            code
            or
            "teller_persistence_authority_error"
        )

        super().__init__(
            self.code
        )


def _clean(
    value,
):
    return str(
        value
        if value is not None
        else ""
    ).strip()


def resolve_owner_teller_persistence_authority(
    receipt,
):

    if not isinstance(
        receipt,
        Mapping,
    ):
        raise TellerPersistenceAuthorityError(
            "teller_persistence_receipt_missing"
        )

    if (
        _clean(
            receipt.get(
                "role"
            )
        )
        != "owner"
    ):
        raise TellerPersistenceAuthorityError(
            "teller_persistence_role_not_authorized"
        )

    tower_session_id = _clean(
        receipt.get(
            "tower_session_id"
        )
    )

    receipt_id = _clean(
        receipt.get(
            "receipt_id"
        )
    )

    receipt_owner_id = _clean(
        receipt.get(
            "owner_id"
        )
    )

    if not all(
        (
            tower_session_id,
            receipt_id,
            receipt_owner_id,
        )
    ):
        raise TellerPersistenceAuthorityError(
            "teller_persistence_receipt_authority_incomplete"
        )

    authority = (
        hosted_owner_identity_authority()
    )

    if (
        authority.get(
            "verification_state"
        )
        != "VERIFIED"
        or authority.get(
            "configured"
        )
        is not True
    ):
        raise TellerPersistenceAuthorityError(
            "teller_persistence_owner_identity_not_verified"
        )

    record = authority.get(
        "record"
    )

    if not isinstance(
        record,
        Mapping,
    ):
        raise TellerPersistenceAuthorityError(
            "teller_persistence_owner_record_missing"
        )

    actor_id = _clean(
        record.get(
            "person_id"
        )
    )

    role = _clean(
        record.get(
            "role"
        )
    ).lower()

    if (
        not actor_id
        or role
        != "owner"
    ):
        raise TellerPersistenceAuthorityError(
            "teller_persistence_owner_record_invalid"
        )

    if not hmac.compare_digest(
        actor_id,
        receipt_owner_id,
    ):
        raise TellerPersistenceAuthorityError(
            "teller_persistence_receipt_actor_mismatch"
        )

    organization_membership = (
        authority.get(
            "organization_membership"
        )
    )

    if not isinstance(
        organization_membership,
        Mapping,
    ):
        raise TellerPersistenceAuthorityError(
            "teller_persistence_business_authority_missing"
        )

    if (
        organization_membership.get(
            "verification_state"
        )
        != "VERIFIED"
    ):
        raise TellerPersistenceAuthorityError(
            "teller_persistence_business_authority_not_verified"
        )

    organization = (
        organization_membership.get(
            "organization"
        )
    )

    if not isinstance(
        organization,
        Mapping,
    ):
        raise TellerPersistenceAuthorityError(
            "teller_persistence_business_record_missing"
        )

    business_key = _clean(
        organization.get(
            "organization_id"
        )
    )

    if not business_key:
        raise TellerPersistenceAuthorityError(
            "teller_persistence_business_key_missing"
        )

    return {
        "tower_session_id":
            tower_session_id,

        "tower_receipt_id":
            receipt_id,

        "actor_id":
            actor_id,

        "actor_role":
            "owner",

        "business_key":
            business_key,

        "authority_source":
            "tower.identity.hosted_owner_configuration",

        "business_authority_source":
            organization_membership.get(
                "source_id"
            ),

        "browser_authority":
            False,
    }
