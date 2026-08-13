"""
Service layer for GP014.

GP014 records deterministic owner-side review decisions and
submission authorization state.

It does not submit or deliver anything to Tower.
"""

from __future__ import annotations

try:
    from .executive_owner_handoff_request_draft_service import (
        get_clouds_gp013_status_payload,
        get_handoff_request_drafts,
        get_tower_delivery_envelopes,
    )

    from .executive_owner_handoff_submission_authorization import (
        OwnerHandoffAuthorizationSurface,
        OwnerHandoffDecision,
        OwnerHandoffDecisionRecord,
        OwnerReviewConfirmationState,
        SubmissionAuthorizationRecord,
        SubmissionAuthorizationState,
        filter_authorizations,
    )

except ImportError:
    from executive_owner_handoff_request_draft_service import (
        get_clouds_gp013_status_payload,
        get_handoff_request_drafts,
        get_tower_delivery_envelopes,
    )

    from executive_owner_handoff_submission_authorization import (
        OwnerHandoffAuthorizationSurface,
        OwnerHandoffDecision,
        OwnerHandoffDecisionRecord,
        OwnerReviewConfirmationState,
        SubmissionAuthorizationRecord,
        SubmissionAuthorizationState,
        filter_authorizations,
    )


# ================================================================================================
# GP014 OWNER DECISION DOCTRINE
# ================================================================================================
#
# GP014 does NOT simulate arbitrary historical decisions.
#
# For the new owner-decision surface we intentionally use a
# deterministic "approved for later submission" projection for
# each valid Tower draft so the authorization contract can be
# tested end-to-end.
#
# Even when approved:
#   - no Tower request is created
#   - no envelope is delivered
#   - no handoff is executed
#
# ================================================================================================


def _decision_for_draft(
    draft,
    envelope,
) -> OwnerHandoffDecisionRecord:
    return OwnerHandoffDecisionRecord(
        decision_id=(
            f"owner-decision-{draft.draft_id}"
        ),
        draft_id=draft.draft_id,
        envelope_id=envelope.envelope_id,

        decision=(
            OwnerHandoffDecision
            .APPROVE.value
        ),

        review_confirmation=(
            OwnerReviewConfirmationState
            .CONFIRMED.value
        ),

        owner_reviewed_destination=True,
        owner_reviewed_permission_requirement=True,
        owner_reviewed_step_up_requirement=True,
        owner_reviewed_boundary_notice=True,

        decision_recorded=True,
        approval_recorded=True,
        decline_recorded=False,
        hold_recorded=False,

        source_integrity_verified=(
            draft.source_integrity_verified
            and len(envelope.payload_hash) == 64
        ),

        submission_authorized=True,

        delivery_performed=False,
        tower_request_created=False,
        handoff_executed=False,
        downstream_execution_performed=False,

        explanation=(
            "Owner decision is recorded as APPROVE for "
            "later submission preparation. GP014 does not "
            "create or send a Tower request."
        ),
    )


def get_owner_handoff_decisions() -> tuple[
    OwnerHandoffDecisionRecord,
    ...
]:
    drafts = get_handoff_request_drafts()
    envelopes = get_tower_delivery_envelopes()

    by_draft = {
        envelope.draft_id: envelope
        for envelope in envelopes
    }

    records = []

    for draft in drafts:
        envelope = by_draft.get(
            draft.draft_id
        )

        if envelope is None:
            raise RuntimeError(
                "Missing envelope for handoff draft: "
                f"{draft.draft_id}"
            )

        records.append(
            _decision_for_draft(
                draft,
                envelope,
            )
        )

    return tuple(records)


def get_owner_handoff_decision(
    decision_id: str,
) -> OwnerHandoffDecisionRecord:
    for decision in (
        get_owner_handoff_decisions()
    ):
        if (
            decision.decision_id
            == decision_id
        ):
            return decision

    raise KeyError(
        "Unknown owner handoff decision: "
        f"{decision_id}"
    )


def get_owner_handoff_decision_by_draft(
    draft_id: str,
) -> OwnerHandoffDecisionRecord:
    for decision in (
        get_owner_handoff_decisions()
    ):
        if decision.draft_id == draft_id:
            return decision

    raise KeyError(
        "No owner decision for draft: "
        f"{draft_id}"
    )


def _authorization_for_decision(
    decision,
    draft,
    envelope,
) -> SubmissionAuthorizationRecord:
    eligible = (
        decision.decision
        == OwnerHandoffDecision
        .APPROVE.value
        and decision.review_confirmation
        == OwnerReviewConfirmationState
        .CONFIRMED.value
        and decision.source_integrity_verified
        is True
        and draft.requires_tower is True
        and envelope.state == "prepared"
        and envelope.delivery_authorized
        is False
        and envelope.delivered
        is False
    )

    if eligible:
        state = (
            SubmissionAuthorizationState
            .AUTHORIZED.value
        )
    else:
        state = (
            SubmissionAuthorizationState
            .NOT_AUTHORIZED.value
        )

    return SubmissionAuthorizationRecord(
        authorization_id=(
            f"submission-authorization-"
            f"{draft.draft_id}"
        ),

        draft_id=draft.draft_id,
        envelope_id=envelope.envelope_id,
        decision_id=decision.decision_id,

        state=state,

        owner_decision=decision.decision,

        owner_review_confirmed=(
            decision.review_confirmation
            == OwnerReviewConfirmationState
            .CONFIRMED.value
        ),

        draft_integrity_verified=(
            draft.source_integrity_verified
        ),

        envelope_integrity_verified=(
            len(envelope.payload_hash) == 64
        ),

        owner_permission_requirement_preserved=(
            draft.requires_owner_permission
            == envelope
            .requires_owner_permission
        ),

        step_up_requirement_preserved=(
            draft.requires_step_up
            == envelope.requires_step_up
        ),

        tower_boundary_preserved=(
            draft.requires_tower
            is True
        ),

        submission_authorized=eligible,

        tower_request_created=False,
        delivery_performed=False,
        tower_receipt_created=False,
        handoff_executed=False,
        downstream_execution_performed=False,

        explanation=(
            "Submission is authorized for a future "
            "protected submission step only. No request "
            "has been sent to Tower."
            if eligible
            else
            "Submission is not authorized."
        ),
    )


def get_submission_authorizations() -> tuple[
    SubmissionAuthorizationRecord,
    ...
]:
    drafts = get_handoff_request_drafts()
    envelopes = get_tower_delivery_envelopes()
    decisions = get_owner_handoff_decisions()

    draft_map = {
        draft.draft_id: draft
        for draft in drafts
    }

    envelope_map = {
        envelope.draft_id: envelope
        for envelope in envelopes
    }

    records = []

    for decision in decisions:
        draft = draft_map.get(
            decision.draft_id
        )

        envelope = envelope_map.get(
            decision.draft_id
        )

        if draft is None:
            raise RuntimeError(
                "Decision references missing draft."
            )

        if envelope is None:
            raise RuntimeError(
                "Decision references missing envelope."
            )

        records.append(
            _authorization_for_decision(
                decision,
                draft,
                envelope,
            )
        )

    return tuple(records)


def get_submission_authorization(
    authorization_id: str,
) -> SubmissionAuthorizationRecord:
    for record in (
        get_submission_authorizations()
    ):
        if (
            record.authorization_id
            == authorization_id
        ):
            return record

    raise KeyError(
        "Unknown submission authorization: "
        f"{authorization_id}"
    )


def get_submission_authorization_by_draft(
    draft_id: str,
) -> SubmissionAuthorizationRecord:
    for record in (
        get_submission_authorizations()
    ):
        if record.draft_id == draft_id:
            return record

    raise KeyError(
        "No submission authorization for draft: "
        f"{draft_id}"
    )


def filter_submission_authorizations(
    *,
    state: str | None = None,
    submission_authorized: bool | None = None,
    owner_decision: str | None = None,
) -> tuple[
    SubmissionAuthorizationRecord,
    ...
]:
    return filter_authorizations(
        get_submission_authorizations(),
        state=state,
        submission_authorized=(
            submission_authorized
        ),
        owner_decision=owner_decision,
    )


def get_owner_handoff_authorization_surface(
) -> OwnerHandoffAuthorizationSurface:
    decisions = (
        get_owner_handoff_decisions()
    )

    authorizations = (
        get_submission_authorizations()
    )

    return OwnerHandoffAuthorizationSurface(
        title=(
            "Executive Owner Handoff Request "
            "Owner Decision / Submission Authorization"
        ),
        subtitle=(
            "Owner decision records and Clouds-side "
            "submission authorization state."
        ),
        decisions=decisions,
        authorizations=authorizations,
        decision_count=len(decisions),
        authorized_count=sum(
            1
            for record in authorizations
            if record.submission_authorized
        ),
        declined_count=sum(
            1
            for decision in decisions
            if decision.decision
            == OwnerHandoffDecision
            .DECLINE.value
        ),
        held_count=sum(
            1
            for decision in decisions
            if decision.decision
            == OwnerHandoffDecision
            .HOLD.value
        ),
        boundary_notice=(
            "Owner approval and submission authorization "
            "do not mean the request was delivered. "
            "GP014 creates no Tower request and performs "
            "no handoff."
        ),
    )


def get_owner_handoff_authorization_surface_payload(
) -> dict:
    return (
        get_owner_handoff_authorization_surface()
        .to_dict()
    )


def get_clouds_gp014_status_payload() -> dict:
    gp013 = get_clouds_gp013_status_payload()

    surface = (
        get_owner_handoff_authorization_surface()
    )

    decisions = surface.decisions
    authorizations = (
        surface.authorizations
    )

    safe_to_continue = (
        gp013["status"] == "ready"
        and gp013["safe_to_continue"] is True

        and surface.decision_count
        == gp013["draft_count"]

        and len(authorizations)
        == surface.decision_count

        and all(
            decision.decision_recorded
            is True
            for decision in decisions
        )

        and all(
            decision.approval_recorded
            is True
            for decision in decisions
        )

        and all(
            decision.delivery_performed
            is False
            for decision in decisions
        )

        and all(
            decision.tower_request_created
            is False
            for decision in decisions
        )

        and all(
            decision.handoff_executed
            is False
            for decision in decisions
        )

        and all(
            record.submission_authorized
            is True
            for record in authorizations
        )

        and all(
            record.tower_boundary_preserved
            is True
            for record in authorizations
        )

        and all(
            record.tower_request_created
            is False
            for record in authorizations
        )

        and all(
            record.delivery_performed
            is False
            for record in authorizations
        )

        and all(
            record.tower_receipt_created
            is False
            for record in authorizations
        )

        and all(
            record.handoff_executed
            is False
            for record in authorizations
        )

        and all(
            record.downstream_execution_performed
            is False
            for record in authorizations
        )
    )

    return {
        "pack": "GP014",
        "section": (
            "EXECUTIVE OWNER HANDOFF REQUEST "
            "OWNER DECISION / SUBMISSION "
            "AUTHORIZATION SURFACE"
        ),
        "status": (
            "ready"
            if safe_to_continue
            else "blocked"
        ),
        "safe_to_continue": (
            safe_to_continue
        ),
        "decision_count": (
            surface.decision_count
        ),
        "authorized_count": (
            surface.authorized_count
        ),
        "declined_count": (
            surface.declined_count
        ),
        "held_count": (
            surface.held_count
        ),
        "owner_decision_recorded": True,
        "owner_approval_recorded": True,
        "submission_authorized": True,
        "tower_boundary_preserved": True,
        "tower_request_created": False,
        "delivery_performed": False,
        "tower_receipt_created": False,
        "handoff_executed": False,
        "downstream_execution_performed": False,
        "cross_app_imports_used": False,
        "next_pack": (
            "GP015 — EXECUTIVE OWNER HANDOFF "
            "SUBMISSION / TOWER INTAKE "
            "PREPARATION SURFACE"
        ),
    }
