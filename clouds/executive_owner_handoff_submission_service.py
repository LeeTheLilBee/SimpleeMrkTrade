"""
GP015 — Handoff Submission / Tower Intake Preparation service.

No Tower network, API, session, delivery, or execution occurs.
"""

from __future__ import annotations

import hashlib
import json

try:
    from .executive_owner_handoff_submission import (
        HandoffSubmissionPacket,
        SubmissionPreparationState,
        TowerIntakePreparationSurface,
        TowerIntakeRequirement,
        TowerIntakeRequirementKind,
    )

    from .executive_owner_handoff_request_draft_service import (
        get_handoff_request_drafts,
        get_tower_delivery_envelopes,
    )

    from .executive_owner_handoff_submission_authorization_service import (
        get_clouds_gp014_status_payload,
        get_owner_handoff_decisions,
        get_submission_authorizations,
    )

except ImportError:
    from executive_owner_handoff_submission import (
        HandoffSubmissionPacket,
        SubmissionPreparationState,
        TowerIntakePreparationSurface,
        TowerIntakeRequirement,
        TowerIntakeRequirementKind,
    )

    from executive_owner_handoff_request_draft_service import (
        get_handoff_request_drafts,
        get_tower_delivery_envelopes,
    )

    from executive_owner_handoff_submission_authorization_service import (
        get_clouds_gp014_status_payload,
        get_owner_handoff_decisions,
        get_submission_authorizations,
    )


def _hash(payload: dict) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()


def _requirements(
    draft,
    envelope,
    decision,
    authorization,
):
    return (
        TowerIntakeRequirement(
            requirement_id=(
                f"{draft.draft_id}-owner-approval"
            ),
            kind="owner_approval",
            label="Owner approval recorded",
            required=True,
            preserved=True,
            satisfied_for_preparation=(
                decision.approval_recorded
            ),
            explanation=(
                "Clouds records the approved owner-side "
                "decision but does not represent Tower acceptance."
            ),
            display_order=10,
        ),

        TowerIntakeRequirement(
            requirement_id=(
                f"{draft.draft_id}-authorization"
            ),
            kind="submission_authorization",
            label="Submission authorization",
            required=True,
            preserved=True,
            satisfied_for_preparation=(
                authorization.submission_authorized
            ),
            explanation=(
                "The owner has authorized future submission."
            ),
            display_order=20,
        ),

        TowerIntakeRequirement(
            requirement_id=(
                f"{draft.draft_id}-destination"
            ),
            kind="destination",
            label="Protected destination",
            required=True,
            preserved=bool(
                draft.destination_id
                and draft.open_route
            ),
            satisfied_for_preparation=bool(
                draft.destination_id
                and draft.open_route
            ),
            explanation=(
                "Tower intake must know the protected destination."
            ),
            display_order=30,
        ),

        TowerIntakeRequirement(
            requirement_id=(
                f"{draft.draft_id}-permission"
            ),
            kind="permission",
            label="Owner permission requirement preserved",
            required=(
                draft.requires_owner_permission
            ),
            preserved=(
                authorization
                .owner_permission_requirement_preserved
            ),
            satisfied_for_preparation=True,
            explanation=(
                "Clouds preserves the permission requirement. "
                "Tower evaluates permission later."
            ),
            display_order=40,
        ),

        TowerIntakeRequirement(
            requirement_id=(
                f"{draft.draft_id}-step-up"
            ),
            kind="step_up",
            label="Step-up requirement preserved",
            required=draft.requires_step_up,
            preserved=(
                authorization
                .step_up_requirement_preserved
            ),
            satisfied_for_preparation=True,
            explanation=(
                "Clouds preserves step-up requirements. "
                "Tower performs step-up later."
            ),
            display_order=50,
        ),

        TowerIntakeRequirement(
            requirement_id=(
                f"{draft.draft_id}-integrity"
            ),
            kind="integrity",
            label="Envelope integrity preserved",
            required=True,
            preserved=(
                len(envelope.payload_hash) == 64
            ),
            satisfied_for_preparation=(
                len(envelope.payload_hash) == 64
            ),
            explanation=(
                "The GP013 envelope integrity hash remains valid."
            ),
            display_order=60,
        ),
    )


def get_handoff_submission_packets():
    drafts = {
        item.draft_id: item
        for item in get_handoff_request_drafts()
    }

    envelopes = {
        item.draft_id: item
        for item in get_tower_delivery_envelopes()
    }

    decisions = {
        item.draft_id: item
        for item in get_owner_handoff_decisions()
    }

    authorizations = {
        item.draft_id: item
        for item in get_submission_authorizations()
    }

    packets = []

    for draft_id in sorted(drafts):
        draft = drafts[draft_id]
        envelope = envelopes.get(draft_id)
        decision = decisions.get(draft_id)
        authorization = authorizations.get(draft_id)

        if (
            envelope is None
            or decision is None
            or authorization is None
        ):
            raise RuntimeError(
                "Incomplete GP015 submission source chain "
                f"for {draft_id}"
            )

        requirements = _requirements(
            draft,
            envelope,
            decision,
            authorization,
        )

        ready = (
            decision.approval_recorded
            and authorization.submission_authorized
            and authorization.tower_boundary_preserved
            and all(
                (
                    not item.required
                    or item.satisfied_for_preparation
                )
                for item in requirements
            )
        )

        integrity_payload = {
            "draft_id": draft.draft_id,
            "envelope_id": envelope.envelope_id,
            "authorization_id": (
                authorization.authorization_id
            ),
            "destination_id": draft.destination_id,
            "open_route": draft.open_route,
            "owner_decision": decision.decision,
            "requires_owner_permission": (
                draft.requires_owner_permission
            ),
            "requires_step_up": (
                draft.requires_step_up
            ),
            "envelope_hash": envelope.payload_hash,
        }

        packets.append(
            HandoffSubmissionPacket(
                submission_id=(
                    f"tower-submission-{draft.draft_id}"
                ),
                authorization_id=(
                    authorization.authorization_id
                ),
                decision_id=decision.decision_id,
                draft_id=draft.draft_id,
                envelope_id=envelope.envelope_id,
                destination_id=(
                    draft.destination_id
                ),
                open_route=draft.open_route,
                owner_decision=decision.decision,
                owner_review_confirmed=(
                    authorization
                    .owner_review_confirmed
                ),
                submission_authorized=(
                    authorization
                    .submission_authorized
                ),
                requires_owner_permission=(
                    draft.requires_owner_permission
                ),
                requires_step_up=(
                    draft.requires_step_up
                ),
                source_integrity_verified=(
                    draft.source_integrity_verified
                    and len(
                        envelope.payload_hash
                    ) == 64
                ),
                tower_boundary_preserved=(
                    authorization
                    .tower_boundary_preserved
                ),
                requirements=requirements,
                preparation_state=(
                    SubmissionPreparationState
                    .READY.value
                    if ready
                    else SubmissionPreparationState
                    .BLOCKED.value
                ),
                submission_hash=_hash(
                    integrity_payload
                ),
                tower_request_created=False,
                delivered_to_tower=False,
                tower_receipt_created=False,
                handoff_executed=False,
                downstream_execution_performed=False,
            )
        )

    return tuple(packets)


def get_handoff_submission_packet(
    submission_id: str,
):
    for item in get_handoff_submission_packets():
        if item.submission_id == submission_id:
            return item

    raise KeyError(
        f"Unknown handoff submission: {submission_id}"
    )


def get_handoff_submission_packet_by_draft(
    draft_id: str,
):
    for item in get_handoff_submission_packets():
        if item.draft_id == draft_id:
            return item

    raise KeyError(
        f"No submission for draft: {draft_id}"
    )


def get_tower_intake_preparation_surface():
    packets = get_handoff_submission_packets()

    return TowerIntakePreparationSurface(
        title=(
            "Executive Owner Handoff Submission "
            "/ Tower Intake Preparation"
        ),
        subtitle=(
            "Authorized Clouds-side submission packets "
            "prepared for future protected Tower intake."
        ),
        submissions=packets,
        submission_count=len(packets),
        ready_count=sum(
            1
            for item in packets
            if item.preparation_state == "ready"
        ),
        blocked_count=sum(
            1
            for item in packets
            if item.preparation_state == "blocked"
        ),
        boundary_notice=(
            "Submission preparation does not create a "
            "Tower request and does not deliver data to Tower."
        ),
    )


def get_tower_intake_preparation_surface_payload():
    return (
        get_tower_intake_preparation_surface()
        .to_dict()
    )


def get_clouds_gp015_status_payload():
    gp014 = get_clouds_gp014_status_payload()
    surface = (
        get_tower_intake_preparation_surface()
    )

    packets = surface.submissions

    safe = (
        gp014["status"] == "ready"
        and gp014["safe_to_continue"] is True
        and surface.submission_count
        == gp014["authorized_count"]
        and surface.blocked_count == 0
        and surface.ready_count
        == surface.submission_count
        and all(
            len(item.submission_hash) == 64
            for item in packets
        )
        and all(
            item.tower_request_created is False
            and item.delivered_to_tower is False
            and item.tower_receipt_created is False
            and item.handoff_executed is False
            and item.downstream_execution_performed
            is False
            for item in packets
        )
    )

    return {
        "pack": "GP015",
        "section": (
            "EXECUTIVE OWNER HANDOFF SUBMISSION "
            "/ TOWER INTAKE PREPARATION SURFACE"
        ),
        "status": "ready" if safe else "blocked",
        "safe_to_continue": safe,
        "submission_count": (
            surface.submission_count
        ),
        "ready_count": surface.ready_count,
        "blocked_count": surface.blocked_count,
        "tower_boundary_preserved": True,
        "tower_request_created": False,
        "delivery_performed": False,
        "tower_receipt_created": False,
        "handoff_executed": False,
        "downstream_execution_performed": False,
        "cross_app_imports_used": False,
        "next_pack": (
            "GP016 — TOWER INTAKE PACKAGE "
            "/ VALIDATION SURFACE"
        ),
    }
