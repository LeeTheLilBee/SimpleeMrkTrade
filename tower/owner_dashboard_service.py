
"""Truthful Tower Owner Headquarters projection / TWR127."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List

from tower.owner_people_registry import (
    owner_people_authority_snapshot,
)
from tower.truth_contract import (
    LOCKED,
    NOT_CONFIGURED,
)


@dataclass(frozen=True)
class TowerOwnerDashboardSummary:
    status: str
    generated_at_utc: str

    people_authority_state: str
    invitation_authority_state: str
    access_authority_state: str
    entitlement_authority_state: str

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
    authority = owner_people_authority_snapshot()

    summary = TowerOwnerDashboardSummary(
        status=(
            "tower_owner_dashboard_authority_not_configured"
        ),

        generated_at_utc=(
            datetime.now(timezone.utc).isoformat()
        ),

        people_authority_state=(
            authority["people"]["verification_state"]
        ),

        invitation_authority_state=(
            authority["invitations"]["verification_state"]
        ),

        access_authority_state=(
            authority["access_control"]["verification_state"]
        ),

        entitlement_authority_state=(
            authority["app_entitlements"]["verification_state"]
        ),

        # These are intentionally None.
        # Tower has no authoritative provider from which to count them.
        people_count=None,
        invitation_count=None,
        pending_access_count=None,

        live_auto=LOCKED,
        broker_execution=False,
        capital_action=False,
        release_execution=False,

        tower_meaning=(
            "Owner Headquarters shows only state Tower can support. "
            "People, invitation, and access totals remain unavailable "
            "until their authoritative providers are connected."
        ),

        owner_next_action=(
            "People and access authority will be connected in the "
            "dedicated identity and invitation lifecycle layers. "
            "Until then Tower will not manufacture records or counts."
        ),
    )

    return {
        "summary":
            asdict(summary),

        "people_authority":
            authority,

        # Compatibility collections remain empty and must not be
        # interpreted as authoritative zero counts.
        "people":
            [],

        "access_requests":
            [],

        "people_groups": {
            "active": [],
            "staged": [],
            "pending_owner_review": [],
        },

        "role_counts":
            {},

        "app_attention":
            {},

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
    summary = build_tower_owner_dashboard()[
        "summary"
    ]

    return [
        {
            "card_id":
                "owner-card-people",

            "title":
                "People",

            "value":
                summary["people_authority_state"],

            "status":
                "not-configured",

            "meaning":
                "No authoritative people provider is connected.",
        },

        {
            "card_id":
                "owner-card-invitations",

            "title":
                "Invitations",

            "value":
                summary["invitation_authority_state"],

            "status":
                "not-configured",

            "meaning":
                "No authoritative invitation provider is connected.",
        },

        {
            "card_id":
                "owner-card-access",

            "title":
                "Access control",

            "value":
                summary["access_authority_state"],

            "status":
                "not-configured",

            "meaning":
                "No authoritative access provider is connected.",
        },

        {
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
        },
    ]
