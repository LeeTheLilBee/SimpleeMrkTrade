"""
GP031 — Owner Decision Choice / Intent Recording Boundary.

Explicit intent-recording only.
"""

from __future__ import annotations

try:
    from .owner_decision_choice import (
        OwnerChoiceRecord,
        OwnerChoiceState,
        OwnerChoiceSurface,
    )

    from .owner_decision_packet_service import (
        get_owner_decision_packet,
    )

    from .owner_decision_review_service import (
        get_clouds_gp030_status_payload,
        get_owner_decision_review,
        get_owner_decision_reviews,
    )

except ImportError:
    from owner_decision_choice import (
        OwnerChoiceRecord,
        OwnerChoiceState,
        OwnerChoiceSurface,
    )

    from owner_decision_packet_service import (
        get_owner_decision_packet,
    )

    from owner_decision_review_service import (
        get_clouds_gp030_status_payload,
        get_owner_decision_review,
        get_owner_decision_reviews,
    )


def _pending_choice_record(
    review,
):
    packet = get_owner_decision_packet(
        review.packet_id
    )

    return OwnerChoiceRecord(
        choice_record_id=(
            "choice-record-"
            f"{review.review_id}"
        ),

        review_id=review.review_id,
        packet_id=review.packet_id,
        agenda_item_id=(
            review.agenda_item_id
        ),

        source_id=packet.source_id,
        source_label=(
            packet.source_label
        ),

        impacted_source_id=(
            packet.impacted_source_id
        ),

        impacted_source_label=(
            packet.impacted_source_label
        ),

        selected_option_id=None,
        selected_option_kind=None,
        selected_option_label=None,

        owner_intent=None,

        choice_state=(
            OwnerChoiceState
            .PENDING.value
        ),

        owning_application_id=(
            packet
            .owning_application_id
        ),

        owning_application_label=(
            packet
            .owning_application_label
        ),

        requires_tower_mediation=(
            packet
            .requires_tower_mediation
        ),

        owner_choice_recorded=False,

        approval_performed=False,
        automatic_decision_performed=False,
        capital_movement_performed=False,
        downstream_execution_performed=False,

        soulaana_choice_summary=(
            "You have not recorded a choice for "
            f"{packet.source_label} yet."
        ),

        soulaana_what_this_means=(
            "The decision packet is ready, but Clouds "
            "is still waiting for your explicit intent."
        ),

        soulaana_what_did_not_happen=(
            "No decision was approved and no downstream "
            "action was executed."
        ),

        soulaana_next_step=(
            "Choose one of the options in the prepared "
            "decision packet when you are ready."
        ),
    )


def get_pending_owner_choice_records():
    return tuple(
        _pending_choice_record(
            review
        )
        for review
        in get_owner_decision_reviews()
    )


def record_owner_choice(
    review_id,
    selected_option_id,
):
    """
    Record explicit owner intent.

    This function does not approve or execute the selected option.
    """

    review = get_owner_decision_review(
        review_id
    )

    if (
        review.review_state
        != "ready_for_owner_choice"
        or review.owner_ready_to_choose
        is not True
    ):
        raise ValueError(
            "Decision review is not ready for owner choice."
        )

    packet = get_owner_decision_packet(
        review.packet_id
    )

    options = {
        option.option_id: option
        for option in packet.options
    }

    if selected_option_id not in options:
        raise ValueError(
            "Selected option is not part of the "
            "prepared decision packet."
        )

    option = options[
        selected_option_id
    ]

    if (
        option.requires_owner_choice
        is not True
    ):
        raise ValueError(
            "Selected option is not an owner-choice option."
        )

    if (
        option.executes_automatically
        is not False
    ):
        raise ValueError(
            "Automatic execution is prohibited at GP031."
        )

    return OwnerChoiceRecord(
        choice_record_id=(
            "choice-record-"
            f"{review.review_id}"
        ),

        review_id=review.review_id,
        packet_id=review.packet_id,
        agenda_item_id=(
            review.agenda_item_id
        ),

        source_id=packet.source_id,
        source_label=(
            packet.source_label
        ),

        impacted_source_id=(
            packet.impacted_source_id
        ),

        impacted_source_label=(
            packet.impacted_source_label
        ),

        selected_option_id=(
            option.option_id
        ),

        selected_option_kind=(
            option.kind
        ),

        selected_option_label=(
            option.label
        ),

        owner_intent=(
            option.kind
        ),

        choice_state=(
            OwnerChoiceState
            .RECORDED.value
        ),

        owning_application_id=(
            packet
            .owning_application_id
        ),

        owning_application_label=(
            packet
            .owning_application_label
        ),

        requires_tower_mediation=(
            packet
            .requires_tower_mediation
        ),

        owner_choice_recorded=True,

        approval_performed=False,
        automatic_decision_performed=False,
        capital_movement_performed=False,
        downstream_execution_performed=False,

        soulaana_choice_summary=(
            "You selected "
            f"“{option.label}” "
            f"for the {packet.source_label} decision."
        ),

        soulaana_what_this_means=(
            "Clouds has recorded your intent so the next "
            "review layer can prepare the correct handoff."
        ),

        soulaana_what_did_not_happen=(
            "Your choice has not been approved, executed, "
            "sent downstream, or treated as completed work."
        ),

        soulaana_next_step=(
            "Review the recorded intent before any "
            "handoff or authorization boundary."
        ),
    )


def get_gp031_fixture_choice_record():
    """
    Deterministic fixture used only to certify the intent boundary.

    Selects REVIEW NOW on the first ready review.
    """

    reviews = (
        get_owner_decision_reviews()
    )

    if not reviews:
        raise RuntimeError(
            "No GP030 decision reviews are available."
        )

    review = reviews[0]

    packet = get_owner_decision_packet(
        review.packet_id
    )

    review_now = tuple(
        option
        for option in packet.options
        if option.kind == "review_now"
    )

    if len(review_now) != 1:
        raise RuntimeError(
            "Expected exactly one review_now option."
        )

    return record_owner_choice(
        review.review_id,
        review_now[0].option_id,
    )


def get_owner_choice_surface():
    pending = list(
        get_pending_owner_choice_records()
    )

    fixture = (
        get_gp031_fixture_choice_record()
    )

    records = []

    replaced = False

    for record in pending:
        if (
            record.review_id
            == fixture.review_id
        ):
            records.append(
                fixture
            )

            replaced = True

        else:
            records.append(
                record
            )

    if not replaced:
        records.append(
            fixture
        )

    records = tuple(records)

    return OwnerChoiceSurface(
        title=(
            "Owner Decision Choice / "
            "Intent Recording"
        ),

        records=records,

        record_count=len(records),

        recorded_count=sum(
            item.choice_state
            == "recorded"
            for item in records
        ),

        pending_count=sum(
            item.choice_state
            == "pending"
            for item in records
        ),

        blocked_count=sum(
            item.choice_state
            == "blocked"
            for item in records
        ),

        owner_choice_recorded=any(
            item.owner_choice_recorded
            for item in records
        ),

        approval_performed=False,
        automatic_decision_performed=False,
        capital_movement_performed=False,
        downstream_execution_performed=False,

        boundary_notice=(
            "GP031 records explicit owner intent only. "
            "A recorded choice is not approval, authorization, "
            "capital movement, navigation, or downstream execution."
        ),
    )


def get_owner_choice_surface_payload():
    return (
        get_owner_choice_surface()
        .to_dict()
    )


def get_clouds_gp031_status_payload():
    gp030 = (
        get_clouds_gp030_status_payload()
    )

    surface = (
        get_owner_choice_surface()
    )

    fixture = (
        get_gp031_fixture_choice_record()
    )

    safe = (
        gp030["status"] == "ready"
        and gp030["safe_to_continue"]
        is True

        and gp030["owner_ready_to_choose"]
        is True

        and surface.record_count
        == gp030["review_count"]

        and surface.recorded_count == 1

        and surface.pending_count
        == (
            surface.record_count
            - 1
        )

        and surface.blocked_count == 0

        and fixture.choice_state
        == "recorded"

        and fixture.owner_choice_recorded
        is True

        and fixture.selected_option_kind
        == "review_now"

        and fixture.approval_performed
        is False

        and fixture
        .automatic_decision_performed
        is False

        and fixture
        .capital_movement_performed
        is False

        and fixture
        .downstream_execution_performed
        is False

        and surface.approval_performed
        is False

        and surface
        .automatic_decision_performed
        is False

        and surface
        .capital_movement_performed
        is False

        and surface
        .downstream_execution_performed
        is False
    )

    return {
        "pack": "GP031",

        "phase": "CLOUDS_PHASE_II",

        "section": (
            "OWNER DECISION CHOICE / "
            "INTENT RECORDING BOUNDARY"
        ),

        "status": (
            "ready"
            if safe
            else "blocked"
        ),

        "safe_to_continue": safe,

        "record_count": (
            surface.record_count
        ),

        "recorded_count": (
            surface.recorded_count
        ),

        "pending_count": (
            surface.pending_count
        ),

        "blocked_count": (
            surface.blocked_count
        ),

        "fixture_choice_kind": (
            fixture.selected_option_kind
        ),

        "explicit_owner_intent_required": True,

        "owner_choice_recorded": (
            surface.owner_choice_recorded
        ),

        "approval_performed": False,

        "automatic_decision_performed": False,

        "capital_movement_performed": False,

        "tower_authority_changed": False,

        "downstream_execution_performed": False,

        "cross_app_imports_used": False,

        "next_pack": (
            "GP032 — OWNER INTENT REVIEW / "
            "HANDOFF AUTHORIZATION PREPARATION"
        ),
    }
