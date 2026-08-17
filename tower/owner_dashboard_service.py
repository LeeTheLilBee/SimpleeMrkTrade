from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List

from tower.owner_people_registry import (
    active_people,
    owner_access_requests,
    owner_invite_drafts,
    owner_people_records,
    pending_owner_review_requests,
    staged_people,
)


@dataclass(frozen=True)
class TowerOwnerDashboardSummary:
    status: str
    generated_at_utc: str
    people_count: int
    active_people_count: int
    staged_people_count: int
    invite_draft_count: int
    pending_review_count: int
    real_account_creation: bool
    real_invites_sent: bool
    real_access_granted: bool
    live_auto: str
    broker_execution: bool
    capital_action: bool
    tower_meaning: str
    owner_next_action: str


def build_tower_owner_dashboard() -> Dict[str, Any]:
    people = owner_people_records()
    invites = owner_invite_drafts()
    requests = owner_access_requests()

    active = active_people()
    staged = staged_people()
    pending = pending_owner_review_requests()

    summary = TowerOwnerDashboardSummary(
        status="tower_owner_dashboard_ready",
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        people_count=len(people),
        active_people_count=len(active),
        staged_people_count=len(staged),
        invite_draft_count=len(invites),
        pending_review_count=len(pending),
        real_account_creation=False,
        real_invites_sent=False,
        real_access_granted=False,
        live_auto="LOCKED",
        broker_execution=False,
        capital_action=False,
        tower_meaning=(
            "Tower Owner Dashboard is the owner desk for people, roles, invites, "
            "and access requests. This layer makes the people/access workflow visible "
            "without granting real app access yet."
        ),
        owner_next_action=(
            "Review staged people and pending access requests. Real account creation, "
            "email invites, billing, and permission grants must be added in later gated layers."
        ),
    )

    role_counts: Dict[str, int] = {}

    for person in people:
        role = str(person["primary_role"])
        role_counts[role] = role_counts.get(role, 0) + 1

    app_attention: Dict[str, int] = {}

    for request in requests:
        for app_id in request["requested_apps"]:
            app_attention[app_id] = app_attention.get(app_id, 0) + 1

    return {
        "summary": asdict(summary),
        "people": people,
        "invite_drafts": invites,
        "access_requests": requests,
        "people_groups": {
            "active": active,
            "staged": staged,
            "pending_owner_review": pending,
        },
        "role_counts": role_counts,
        "app_attention": app_attention,
        "danger_locks": {
            "real_account_creation": False,
            "real_invites_sent": False,
            "real_access_granted": False,
            "live_auto": "LOCKED",
            "broker_execution": False,
            "capital_action": False,
        },
    }


def owner_dashboard_status_cards() -> List[Dict[str, Any]]:
    dashboard = build_tower_owner_dashboard()
    summary = dashboard["summary"]

    return [
        {
            "card_id": "owner-card-people",
            "title": "People",
            "value": summary["people_count"],
            "status": "mapped",
            "meaning": "People and future seats are visible to the owner.",
        },
        {
            "card_id": "owner-card-staged",
            "title": "Staged seats",
            "value": summary["staged_people_count"],
            "status": "staged",
            "meaning": "These are not real accounts yet.",
        },
        {
            "card_id": "owner-card-invites",
            "title": "Invite drafts",
            "value": summary["invite_draft_count"],
            "status": "draft",
            "meaning": "Invites are drafted but not sent.",
        },
        {
            "card_id": "owner-card-review",
            "title": "Needs owner review",
            "value": summary["pending_review_count"],
            "status": "review",
            "meaning": "Access requests require owner decision later.",
        },
        {
            "card_id": "owner-card-access-grants",
            "title": "Real access grants",
            "value": "OFF",
            "status": "locked",
            "meaning": "This layer cannot grant live app access.",
        },
        {
            "card_id": "owner-card-danger-locks",
            "title": "Danger locks",
            "value": "LOCKED",
            "status": "locked",
            "meaning": "Live Auto, broker execution, and capital action remain locked.",
        },
    ]
