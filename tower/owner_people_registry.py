from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Tuple


@dataclass(frozen=True)
class TowerPersonRecord:
    person_id: str
    display_name: str
    relationship: str
    contact_status: str
    access_status: str
    primary_role: str
    clearance_level: str
    allowed_apps: Tuple[str, ...]
    pending_apps: Tuple[str, ...]
    blocked_apps: Tuple[str, ...]
    notes: str


@dataclass(frozen=True)
class TowerInviteDraft:
    invite_id: str
    display_name: str
    invite_type: str
    target_role: str
    target_apps: Tuple[str, ...]
    status: str
    owner_decision_required: bool
    message: str


@dataclass(frozen=True)
class TowerAccessRequest:
    request_id: str
    person_id: str
    request_type: str
    requested_role: str
    requested_apps: Tuple[str, ...]
    risk_level: str
    status: str
    can_auto_grant: bool
    tower_reason: str


OWNER_PERSON_RECORDS: Tuple[TowerPersonRecord, ...] = (
    TowerPersonRecord(
        person_id="owner-solice",
        display_name="Solice Bowdre",
        relationship="owner",
        contact_status="verified_owner",
        access_status="active_owner",
        primary_role="owner",
        clearance_level="tower_owner",
        allowed_apps=(
            "tower",
            "observatory",
        ),
        pending_apps=(),
        blocked_apps=(),
        notes="Primary owner. Tower owner session required for protected control rooms.",
    ),
    TowerPersonRecord(
        person_id="future-manager-seat",
        display_name="Future Manager Seat",
        relationship="future_team",
        contact_status="not_invited",
        access_status="staged_only",
        primary_role="manager_candidate",
        clearance_level="none",
        allowed_apps=(),
        pending_apps=(
            "teller",
        ),
        blocked_apps=(
            "observatory",
            "vault",
            "clouds",
            "grounds",
        ),
        notes="Placeholder seat for future manager access. No real account is created by this layer.",
    ),
    TowerPersonRecord(
        person_id="future-family-seat",
        display_name="Future Family / Friend Seat",
        relationship="future_invite",
        contact_status="not_invited",
        access_status="staged_only",
        primary_role="limited_member",
        clearance_level="none",
        allowed_apps=(),
        pending_apps=(
            "observatory",
        ),
        blocked_apps=(
            "vault",
            "clouds",
            "grounds",
        ),
        notes="Placeholder seat for future family/friend access with sliding-scale/payment rules later.",
    ),
)


OWNER_INVITE_DRAFTS: Tuple[TowerInviteDraft, ...] = (
    TowerInviteDraft(
        invite_id="draft-manager-teller",
        display_name="Manager Teller Access Draft",
        invite_type="role_invite",
        target_role="manager",
        target_apps=(
            "teller",
        ),
        status="draft_not_sent",
        owner_decision_required=True,
        message="Draft for future manager access to Teller workflows. No invite is sent yet.",
    ),
    TowerInviteDraft(
        invite_id="draft-family-ob-limited",
        display_name="Family / Friend OB Limited Draft",
        invite_type="limited_platform_invite",
        target_role="limited_member",
        target_apps=(
            "observatory",
        ),
        status="draft_not_sent",
        owner_decision_required=True,
        message="Draft for future limited OB access. Billing/sliding scale belongs to a later layer.",
    ),
)


OWNER_ACCESS_REQUESTS: Tuple[TowerAccessRequest, ...] = (
    TowerAccessRequest(
        request_id="access-request-teller-manager-seat",
        person_id="future-manager-seat",
        request_type="future_access",
        requested_role="manager",
        requested_apps=(
            "teller",
        ),
        risk_level="medium",
        status="pending_owner_review",
        can_auto_grant=False,
        tower_reason="Tower can stage this request but cannot grant real Teller access yet.",
    ),
    TowerAccessRequest(
        request_id="access-request-family-ob-limited",
        person_id="future-family-seat",
        request_type="future_access",
        requested_role="limited_member",
        requested_apps=(
            "observatory",
        ),
        risk_level="high",
        status="pending_owner_review",
        can_auto_grant=False,
        tower_reason="OB access requires future policy, billing, terms, and owner approval.",
    ),
)


def owner_people_records() -> List[Dict[str, Any]]:
    return [
        asdict(person)
        for person in OWNER_PERSON_RECORDS
    ]


def owner_invite_drafts() -> List[Dict[str, Any]]:
    return [
        asdict(invite)
        for invite in OWNER_INVITE_DRAFTS
    ]


def owner_access_requests() -> List[Dict[str, Any]]:
    return [
        asdict(request)
        for request in OWNER_ACCESS_REQUESTS
    ]


def active_people() -> List[Dict[str, Any]]:
    return [
        person
        for person in owner_people_records()
        if person["access_status"].startswith("active")
    ]


def staged_people() -> List[Dict[str, Any]]:
    return [
        person
        for person in owner_people_records()
        if person["access_status"] == "staged_only"
    ]


def pending_owner_review_requests() -> List[Dict[str, Any]]:
    return [
        request
        for request in owner_access_requests()
        if request["status"] == "pending_owner_review"
    ]


def person_by_id(person_id: str) -> Dict[str, Any] | None:
    normalized = str(person_id or "").strip()

    for person in owner_people_records():
        if person["person_id"] == normalized:
            return person

    return None
