
"""Truthful Tower Owner Headquarters identity projection / TWR131-TWR135."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List

from tower.owner_people_registry import (
    owner_people_authority_snapshot,
    owner_people_records,
)
from tower.truth_contract import (
    LOCKED,
    NOT_CONFIGURED,
    VERIFIED,
)


@dataclass(frozen=True)
class TowerOwnerDashboardSummary:
    status: str
    generated_at_utc: str

    people_authority_state: str
    invitation_authority_state: str
    access_authority_state: str
    entitlement_authority_state: str
    organization_authority_state: str

    people_count: int | None
    invitation_count: int | None
    pending_access_count: int | None

    live_auto: str
    broker_execution: bool
    capital_action: bool
    release_execution: bool

    tower_meaning: str
    owner_next_action: str


def build_tower_owner_dashboard() -> Dict[str, Any]:
    authority = (
        owner_people_authority_snapshot()
    )

    people = (
        owner_people_records()
    )

    people_verified = (
        authority[
            "people"
        ][
            "verification_state"
        ]
        == VERIFIED
    )

    if people_verified:

        status = (
            "tower_owner_dashboard_identity_authority_verified"
        )

        people_count = len(
            people
        )

        role_counts = {
            "owner":
                sum(
                    1
                    for person
                    in people
                    if person.get(
                        "role"
                    )
                    == "owner"
                ),
        }

        people_groups = {
            # Do not claim account lifecycle ACTIVE.
            "active":
                [],

            "verified_identity":
                list(
                    people
                ),

            "staged":
                [],

            "pending_owner_review":
                [],
        }

        app_attention = {}

        for person in people:

            for entitlement in person.get(
                "app_entitlements",
                [],
            ):

                app_id = entitlement.get(
                    "app_id"
                )

                if not app_id:
                    continue

                app_attention[
                    app_id
                ] = {
                    "owner_access_policy":
                        entitlement.get(
                            "access_policy"
                        ),

                    "verification_state":
                        entitlement.get(
                            "verification_state"
                        ),

                    "runtime_availability_state":
                        entitlement.get(
                            "runtime_availability_state"
                        ),
                }

        tower_meaning = (
            "Owner Headquarters is projecting the configured "
            "hosted owner identity and current owner-role access "
            "policy. Invitation, access-mutation, and account "
            "lifecycle authorities remain separate."
        )

        owner_next_action = (
            "Connect the invitation and access-mutation lifecycle "
            "without changing the verified hosted owner identity."
        )

    else:

        status = (
            "tower_owner_dashboard_authority_not_configured"
        )

        people_count = None

        role_counts = {}

        people_groups = {
            "active":
                [],

            "verified_identity":
                [],

            "staged":
                [],

            "pending_owner_review":
                [],
        }

        app_attention = {}

        tower_meaning = (
            "Owner Headquarters shows only state Tower can support. "
            "Hosted owner identity remains unavailable until its "
            "hashed credential configuration is present."
        )

        owner_next_action = (
            "Configure the hosted owner identity contract. "
            "Tower will not manufacture people or counts."
        )

    summary = TowerOwnerDashboardSummary(
        status=
            status,

        generated_at_utc=(
            datetime.now(
                timezone.utc
            ).isoformat()
        ),

        people_authority_state=(
            authority[
                "people"
            ][
                "verification_state"
            ]
        ),

        invitation_authority_state=(
            authority[
                "invitations"
            ][
                "verification_state"
            ]
        ),

        access_authority_state=(
            authority[
                "access_control"
            ][
                "verification_state"
            ]
        ),

        entitlement_authority_state=(
            authority[
                "app_entitlements"
            ][
                "verification_state"
            ]
        ),

        organization_authority_state=(
            authority[
                "organization_membership"
            ][
                "verification_state"
            ]
        ),

        people_count=
            people_count,

        # No invitation provider yet:
        # missing is not zero.
        invitation_count=
            None,

        # No access-mutation queue yet:
        # missing is not zero.
        pending_access_count=
            None,

        live_auto=
            LOCKED,

        broker_execution=
            False,

        capital_action=
            False,

        release_execution=
            False,

        tower_meaning=
            tower_meaning,

        owner_next_action=
            owner_next_action,
    )

    return {
        "summary":
            asdict(
                summary
            ),

        "people_authority":
            authority,

        "people":
            list(
                people
            ),

        "access_requests":
            [],

        "people_groups":
            people_groups,

        "role_counts":
            role_counts,

        "app_attention":
            app_attention,

        "danger_locks": {
            "live_auto":
                LOCKED,

            "broker_execution":
                False,

            "capital_action":
                False,

            "release_execution":
                False,
        },
    }


def owner_dashboard_status_cards() -> List[Dict[str, Any]]:
    dashboard = (
        build_tower_owner_dashboard()
    )

    summary = dashboard[
        "summary"
    ]

    cards: List[
        Dict[str, Any]
    ] = []

    if (
        summary[
            "people_authority_state"
        ]
        == VERIFIED
    ):
        cards.append({
            "card_id":
                "owner-card-people",

            "title":
                "People",

            "value":
                (
                    f"{summary['people_count']} VERIFIED"
                ),

            "status":
                "verified",

            "meaning":
                "Hosted owner identity is verified from configured Tower authority.",
        })

    else:
        cards.append({
            "card_id":
                "owner-card-people",

            "title":
                "People",

            "value":
                summary[
                    "people_authority_state"
                ],

            "status":
                "not-configured",

            "meaning":
                "Hosted owner identity authority is not configured.",
        })

    cards.append({
        "card_id":
            "owner-card-invitations",

        "title":
            "Invitations",

        "value":
            summary[
                "invitation_authority_state"
            ],

        "status":
            "not-configured",

        "meaning":
            "Invitation lifecycle authority is not configured.",
    })

    cards.append({
        "card_id":
            "owner-card-access",

        "title":
            "Access control",

        "value":
            summary[
                "access_authority_state"
            ],

        "status":
            "not-configured",

        "meaning":
            "Access-mutation lifecycle authority is not configured.",
    })

    if (
        summary[
            "entitlement_authority_state"
        ]
        == VERIFIED
    ):
        observatory = dashboard[
            "app_attention"
        ].get(
            "observatory"
        )

        if observatory:
            cards.append({
                "card_id":
                    "owner-card-observatory-policy",

                "title":
                    "Observatory policy",

                "value":
                    observatory[
                        "owner_access_policy"
                    ],

                "status":
                    "verified",

                "meaning":
                    (
                        "Owner access policy is verified. "
                        "Runtime availability is not inferred."
                    ),
            })

    cards.append({
        "card_id":
            "owner-card-danger-locks",

        "title":
            "Execution safety",

        "value":
            LOCKED,

        "status":
            "locked",

        "meaning":
            "Broker, capital, release execution, and Live Auto remain closed.",
    })

    return cards
