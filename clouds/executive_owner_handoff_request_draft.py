"""
The Clouds — Executive Owner Handoff Request Draft /
Tower Delivery Envelope contracts.

GP013 prepares deterministic handoff request drafts.

Drafts are not submitted.
Drafts are not approved.
Drafts are not delivered.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class HandoffDraftState(str, Enum):
    DRAFT_READY = "draft_ready"
    NOT_DRAFTABLE = "not_draftable"
    INTERNAL_ONLY = "internal_only"


class HandoffDraftDecision(str, Enum):
    UNDECIDED = "undecided"


class DeliveryEnvelopeState(str, Enum):
    PREPARED = "prepared"
    NOT_PREPARED = "not_prepared"


@dataclass(frozen=True)
class HandoffRequestDraft:
    draft_id: str

    review_id: str
    item_id: str
    intent_id: str

    destination_id: str
    open_route: str

    source_section_id: str | None
    source_app_id: str | None
    source_lane_id: str | None

    requires_tower: bool
    requires_owner_permission: bool
    requires_step_up: bool

    draft_state: str
    owner_decision: str

    source_integrity_verified: bool

    owner_approval_recorded: bool
    submission_authorized: bool
    tower_request_created: bool
    delivered_to_tower: bool
    handoff_executed: bool
    downstream_execution_performed: bool

    explanation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "draft_id": self.draft_id,
            "review_id": self.review_id,
            "item_id": self.item_id,
            "intent_id": self.intent_id,
            "destination_id": self.destination_id,
            "open_route": self.open_route,
            "source_section_id": self.source_section_id,
            "source_app_id": self.source_app_id,
            "source_lane_id": self.source_lane_id,
            "requires_tower": self.requires_tower,
            "requires_owner_permission": (
                self.requires_owner_permission
            ),
            "requires_step_up": self.requires_step_up,
            "draft_state": self.draft_state,
            "owner_decision": self.owner_decision,
            "source_integrity_verified": (
                self.source_integrity_verified
            ),
            "owner_approval_recorded": (
                self.owner_approval_recorded
            ),
            "submission_authorized": (
                self.submission_authorized
            ),
            "tower_request_created": (
                self.tower_request_created
            ),
            "delivered_to_tower": (
                self.delivered_to_tower
            ),
            "handoff_executed": (
                self.handoff_executed
            ),
            "downstream_execution_performed": (
                self.downstream_execution_performed
            ),
            "explanation": self.explanation,
        }


@dataclass(frozen=True)
class TowerDeliveryEnvelope:
    envelope_id: str
    envelope_version: str

    draft_id: str
    review_id: str

    destination_id: str
    open_route: str

    source_app_id: str | None
    source_lane_id: str | None

    requires_owner_permission: bool
    requires_step_up: bool

    payload_hash: str

    state: str

    delivery_authorized: bool
    delivered: bool
    tower_receipt_created: bool
    execution_performed: bool

    boundary_notice: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "envelope_id": self.envelope_id,
            "envelope_version": self.envelope_version,
            "draft_id": self.draft_id,
            "review_id": self.review_id,
            "destination_id": self.destination_id,
            "open_route": self.open_route,
            "source_app_id": self.source_app_id,
            "source_lane_id": self.source_lane_id,
            "requires_owner_permission": (
                self.requires_owner_permission
            ),
            "requires_step_up": self.requires_step_up,
            "payload_hash": self.payload_hash,
            "state": self.state,
            "delivery_authorized": (
                self.delivery_authorized
            ),
            "delivered": self.delivered,
            "tower_receipt_created": (
                self.tower_receipt_created
            ),
            "execution_performed": (
                self.execution_performed
            ),
            "boundary_notice": self.boundary_notice,
        }


@dataclass(frozen=True)
class HandoffDraftSurface:
    title: str
    subtitle: str

    drafts: tuple[
        HandoffRequestDraft,
        ...
    ]

    envelopes: tuple[
        TowerDeliveryEnvelope,
        ...
    ]

    draft_count: int
    envelope_count: int

    boundary_notice: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "subtitle": self.subtitle,
            "drafts": [
                draft.to_dict()
                for draft in self.drafts
            ],
            "envelopes": [
                envelope.to_dict()
                for envelope in self.envelopes
            ],
            "draft_count": self.draft_count,
            "envelope_count": self.envelope_count,
            "boundary_notice": self.boundary_notice,
        }
