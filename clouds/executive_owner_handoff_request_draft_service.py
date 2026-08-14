"""
Service layer for The Clouds Executive Owner Handoff Request Draft /
Tower Delivery Envelope Surface.

GP013 prepares drafts only.

No Tower delivery or execution occurs.
"""

from __future__ import annotations

import hashlib
import json

try:
    from .executive_owner_action_intent_review import (
        HandoffPreparationState,
        IntentReviewState,
    )

    from .executive_owner_action_intent_review_service import (
        get_clouds_gp012_status_payload,
        get_owner_intent_review_packets,
    )

    from .executive_owner_handoff_request_draft import (
        DeliveryEnvelopeState,
        HandoffDraftDecision,
        HandoffDraftState,
        HandoffDraftSurface,
        HandoffRequestDraft,
        TowerDeliveryEnvelope,
    )

except ImportError:
    from executive_owner_action_intent_review import (
        HandoffPreparationState,
        IntentReviewState,
    )

    from executive_owner_action_intent_review_service import (
        get_clouds_gp012_status_payload,
        get_owner_intent_review_packets,
    )

    from executive_owner_handoff_request_draft import (
        DeliveryEnvelopeState,
        HandoffDraftDecision,
        HandoffDraftState,
        HandoffDraftSurface,
        HandoffRequestDraft,
        TowerDeliveryEnvelope,
    )


def _eligible_tower_reviews():
    return tuple(
        review
        for review in get_owner_intent_review_packets()
        if (
            review.review_state
            == IntentReviewState
            .TOWER_HANDOFF_PREPARED.value
            and review.preparation_state
            == HandoffPreparationState
            .PREPARED.value
            and review.handoff_preparation.requires_tower
            is True
        )
    )


def _payload_hash(payload: dict) -> str:
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    )

    return hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()


def _build_draft(
    review,
    *,
    display_index: int,
) -> HandoffRequestDraft:
    handoff = review.handoff_preparation

    if not handoff.destination_id:
        raise RuntimeError(
            "Tower handoff review missing destination."
        )

    if not handoff.open_route:
        raise RuntimeError(
            "Tower handoff review missing route."
        )

    return HandoffRequestDraft(
        draft_id=(
            f"handoff-draft-{display_index:03d}-"
            f"{review.item_id}"
        ),
        review_id=review.review_id,
        item_id=review.item_id,
        intent_id=review.intent_id,
        destination_id=handoff.destination_id,
        open_route=handoff.open_route,
        source_section_id=(
            review.source_section_id
        ),
        source_app_id=(
            review.source_app_id
        ),
        source_lane_id=(
            review.source_lane_id
        ),
        requires_tower=True,
        requires_owner_permission=(
            handoff.requires_owner_permission
        ),
        requires_step_up=(
            handoff.requires_step_up
        ),
        draft_state=(
            HandoffDraftState
            .DRAFT_READY.value
        ),
        owner_decision=(
            HandoffDraftDecision
            .UNDECIDED.value
        ),
        source_integrity_verified=(
            review.source_integrity_verified
        ),
        owner_approval_recorded=False,
        submission_authorized=False,
        tower_request_created=False,
        delivered_to_tower=False,
        handoff_executed=False,
        downstream_execution_performed=False,
        explanation=(
            "This handoff request exists only as a "
            "Clouds-side draft. Owner decision and "
            "submission authorization have not occurred."
        ),
    )


def get_handoff_request_drafts() -> tuple[
    HandoffRequestDraft,
    ...
]:
    reviews = _eligible_tower_reviews()

    drafts = tuple(
        _build_draft(
            review,
            display_index=index,
        )
        for index, review in enumerate(
            reviews,
            start=1,
        )
    )

    return drafts


def get_handoff_request_draft(
    draft_id: str,
) -> HandoffRequestDraft:
    for draft in get_handoff_request_drafts():
        if draft.draft_id == draft_id:
            return draft

    raise KeyError(
        "Unknown handoff request draft: "
        f"{draft_id}"
    )


def get_handoff_request_draft_by_item(
    item_id: str,
) -> HandoffRequestDraft:
    for draft in get_handoff_request_drafts():
        if draft.item_id == item_id:
            return draft

    raise KeyError(
        "No Tower handoff request draft for item: "
        f"{item_id}"
    )


def get_handoff_request_draft_payload(
    draft_id: str,
) -> dict:
    return (
        get_handoff_request_draft(
            draft_id
        ).to_dict()
    )


def _build_envelope(
    draft: HandoffRequestDraft,
) -> TowerDeliveryEnvelope:
    integrity_payload = {
        "draft_id": draft.draft_id,
        "review_id": draft.review_id,
        "item_id": draft.item_id,
        "intent_id": draft.intent_id,
        "destination_id": draft.destination_id,
        "open_route": draft.open_route,
        "source_section_id": (
            draft.source_section_id
        ),
        "source_app_id": (
            draft.source_app_id
        ),
        "source_lane_id": (
            draft.source_lane_id
        ),
        "requires_owner_permission": (
            draft.requires_owner_permission
        ),
        "requires_step_up": (
            draft.requires_step_up
        ),
    }

    digest = _payload_hash(
        integrity_payload
    )

    return TowerDeliveryEnvelope(
        envelope_id=(
            "tower-envelope-"
            f"{draft.draft_id}"
        ),
        envelope_version="clouds-gp013-v1",
        draft_id=draft.draft_id,
        review_id=draft.review_id,
        destination_id=(
            draft.destination_id
        ),
        open_route=draft.open_route,
        source_app_id=(
            draft.source_app_id
        ),
        source_lane_id=(
            draft.source_lane_id
        ),
        requires_owner_permission=(
            draft.requires_owner_permission
        ),
        requires_step_up=(
            draft.requires_step_up
        ),
        payload_hash=digest,
        state=(
            DeliveryEnvelopeState
            .PREPARED.value
        ),
        delivery_authorized=False,
        delivered=False,
        tower_receipt_created=False,
        execution_performed=False,
        boundary_notice=(
            "Envelope is prepared only. Clouds has not "
            "received owner submission authorization and "
            "has not delivered anything to Tower."
        ),
    )


def get_tower_delivery_envelopes() -> tuple[
    TowerDeliveryEnvelope,
    ...
]:
    return tuple(
        _build_envelope(draft)
        for draft
        in get_handoff_request_drafts()
    )


def get_tower_delivery_envelope(
    envelope_id: str,
) -> TowerDeliveryEnvelope:
    for envelope in (
        get_tower_delivery_envelopes()
    ):
        if envelope.envelope_id == envelope_id:
            return envelope

    raise KeyError(
        "Unknown Tower delivery envelope: "
        f"{envelope_id}"
    )


def get_tower_delivery_envelope_by_draft(
    draft_id: str,
) -> TowerDeliveryEnvelope:
    for envelope in (
        get_tower_delivery_envelopes()
    ):
        if envelope.draft_id == draft_id:
            return envelope

    raise KeyError(
        "No Tower delivery envelope for draft: "
        f"{draft_id}"
    )


def get_tower_delivery_envelope_payload(
    envelope_id: str,
) -> dict:
    return (
        get_tower_delivery_envelope(
            envelope_id
        ).to_dict()
    )


def get_handoff_draft_surface(
) -> HandoffDraftSurface:
    drafts = get_handoff_request_drafts()
    envelopes = (
        get_tower_delivery_envelopes()
    )

    return HandoffDraftSurface(
        title=(
            "Executive Owner Handoff Request Draft "
            "/ Tower Delivery Envelope"
        ),
        subtitle=(
            "Clouds-side draft preparation for "
            "protected Tower-mediated handoffs."
        ),
        drafts=drafts,
        envelopes=envelopes,
        draft_count=len(drafts),
        envelope_count=len(envelopes),
        boundary_notice=(
            "Drafted does not mean approved, "
            "submission-authorized, delivered, "
            "Tower-accepted, or executed."
        ),
    )


def get_handoff_draft_surface_payload(
) -> dict:
    return (
        get_handoff_draft_surface()
        .to_dict()
    )


def get_clouds_gp013_status_payload() -> dict:
    gp012 = get_clouds_gp012_status_payload()

    surface = get_handoff_draft_surface()

    drafts = surface.drafts
    envelopes = surface.envelopes

    safe_to_continue = (
        gp012["status"] == "ready"
        and gp012["safe_to_continue"] is True
        and surface.draft_count
        == gp012["tower_prepared_count"]
        and surface.envelope_count
        == surface.draft_count
        and all(
            draft.draft_state
            == HandoffDraftState
            .DRAFT_READY.value
            for draft in drafts
        )
        and all(
            draft.owner_decision
            == HandoffDraftDecision
            .UNDECIDED.value
            for draft in drafts
        )
        and all(
            draft.owner_approval_recorded
            is False
            for draft in drafts
        )
        and all(
            draft.submission_authorized
            is False
            for draft in drafts
        )
        and all(
            draft.tower_request_created
            is False
            for draft in drafts
        )
        and all(
            draft.delivered_to_tower
            is False
            for draft in drafts
        )
        and all(
            draft.handoff_executed
            is False
            for draft in drafts
        )
        and all(
            draft.downstream_execution_performed
            is False
            for draft in drafts
        )
        and all(
            envelope.state
            == DeliveryEnvelopeState
            .PREPARED.value
            for envelope in envelopes
        )
        and all(
            envelope.delivery_authorized
            is False
            for envelope in envelopes
        )
        and all(
            envelope.delivered
            is False
            for envelope in envelopes
        )
        and all(
            envelope.tower_receipt_created
            is False
            for envelope in envelopes
        )
        and all(
            envelope.execution_performed
            is False
            for envelope in envelopes
        )
        and all(
            len(envelope.payload_hash) == 64
            for envelope in envelopes
        )
    )

    return {
        "pack": "GP013",
        "section": (
            "EXECUTIVE OWNER HANDOFF REQUEST DRAFT "
            "/ TOWER DELIVERY ENVELOPE SURFACE"
        ),
        "status": (
            "ready"
            if safe_to_continue
            else "blocked"
        ),
        "safe_to_continue": safe_to_continue,
        "draft_count": (
            surface.draft_count
        ),
        "envelope_count": (
            surface.envelope_count
        ),
        "source_integrity_verified": all(
            draft.source_integrity_verified
            for draft in drafts
        ),
        "tower_boundary_preserved": True,
        "owner_decision_recorded": False,
        "owner_approval_recorded": False,
        "submission_authorized": False,
        "tower_request_created": False,
        "delivery_performed": False,
        "tower_receipt_created": False,
        "handoff_executed": False,
        "downstream_execution_performed": False,
        "cross_app_imports_used": False,
        "next_pack": (
            "GP014 — EXECUTIVE OWNER HANDOFF REQUEST "
            "OWNER DECISION / SUBMISSION AUTHORIZATION SURFACE"
        ),
    }
