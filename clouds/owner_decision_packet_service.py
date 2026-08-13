"""
GP029 — Owner Decision Prep / Decision Packet Surface.

Builds owner-review packets from GP028 agenda items.
"""

from __future__ import annotations

try:
    from .executive_owner_agenda_service import (
        get_clouds_gp028_status_payload,
        get_owner_agenda_item,
        get_owner_agenda_items,
    )

    from .owner_decision_packet import (
        DecisionEvidenceItem,
        DecisionOption,
        DecisionOptionKind,
        DecisionPacketState,
        OwnerDecisionPacket,
        OwnerDecisionPacketSurface,
    )

except ImportError:
    from executive_owner_agenda_service import (
        get_clouds_gp028_status_payload,
        get_owner_agenda_item,
        get_owner_agenda_items,
    )

    from owner_decision_packet import (
        DecisionEvidenceItem,
        DecisionOption,
        DecisionOptionKind,
        DecisionPacketState,
        OwnerDecisionPacket,
        OwnerDecisionPacketSurface,
    )


TOWER_MEDIATED_SOURCES = {
    "observatory",
    "tower",
    "teller",
    "grounds",
    "archive_vault",
}


def _decision_question(item):
    if item.source_kind == "operating_change":
        return (
            f"How do you want to respond to the "
            f"current {item.source_label} change?"
        )

    if item.impacted_source_label:
        return (
            f"Do you want to review how "
            f"{item.source_label} may affect "
            f"{item.impacted_source_label}?"
        )

    return (
        f"What do you want to do about "
        f"{item.title}?"
    )


def _options(item):
    options = [
        DecisionOption(
            option_id=(
                f"{item.agenda_item_id}-review"
            ),
            label="Review now",
            kind=(
                DecisionOptionKind
                .REVIEW_NOW.value
            ),
            explanation=(
                "Open the owning application's deeper "
                "context before making any operational decision."
            ),
            expected_benefit=(
                "You make the decision with the source-owned "
                "details instead of relying on Clouds alone."
            ),
            expected_cost_or_risk=(
                "Requires owner attention now."
            ),
            what_happens_next=(
                "Clouds prepares the protected navigation "
                "reference; Tower or the owning app remains "
                "responsible for the real workflow."
            ),
            requires_owner_choice=True,
            executes_automatically=False,
            display_order=10,
        ),

        DecisionOption(
            option_id=(
                f"{item.agenda_item_id}-defer"
            ),
            label="Defer",
            kind=(
                DecisionOptionKind
                .DEFER.value
            ),
            explanation=(
                "Leave the item in the owner agenda and "
                "review it later."
            ),
            expected_benefit=(
                "Protects current owner focus."
            ),
            expected_cost_or_risk=(
                item.soulaana_if_we_wait
            ),
            what_happens_next=(
                "No downstream action occurs. "
                "The decision remains unresolved."
            ),
            requires_owner_choice=True,
            executes_automatically=False,
            display_order=20,
        ),
    ]

    if item.source_kind == "cross_business_impact":
        options.append(
            DecisionOption(
                option_id=(
                    f"{item.agenda_item_id}-hold"
                ),
                label="Hold and watch",
                kind=(
                    DecisionOptionKind
                    .HOLD.value
                ),
                explanation=(
                    "Keep the relationship visible without "
                    "starting work in either affected application."
                ),
                expected_benefit=(
                    "Prevents advisory impact modeling from "
                    "turning into premature action."
                ),
                expected_cost_or_risk=(
                    "The owner may need to revisit the relationship "
                    "if either source changes again."
                ),
                what_happens_next=(
                    "Clouds continues to treat the relationship "
                    "as context only."
                ),
                requires_owner_choice=True,
                executes_automatically=False,
                display_order=30,
            )
        )

    options.append(
        DecisionOption(
            option_id=(
                f"{item.agenda_item_id}-no-action"
            ),
            label="No action",
            kind=(
                DecisionOptionKind
                .NO_ACTION.value
            ),
            explanation=(
                "Acknowledge that the item does not currently "
                "justify deeper owner work."
            ),
            expected_benefit=(
                "Avoids unnecessary owner effort."
            ),
            expected_cost_or_risk=(
                item.soulaana_if_we_wait
            ),
            what_happens_next=(
                "Nothing is executed. "
                "The source remains responsible for its own state."
            ),
            requires_owner_choice=True,
            executes_automatically=False,
            display_order=40,
        )
    )

    return tuple(options)


def _evidence_items(item):
    evidence = [
        DecisionEvidenceItem(
            evidence_id=(
                f"{item.agenda_item_id}-source-state"
            ),
            label="Current source state",
            explanation=(
                "Review the current operating state in the "
                "source-owned application before deciding."
            ),
            source_id=item.source_id,
            required_before_decision=True,
            raw_evidence_loaded=False,
            display_order=10,
        ),

        DecisionEvidenceItem(
            evidence_id=(
                f"{item.agenda_item_id}-change-context"
            ),
            label="Change context",
            explanation=(
                "Review what changed from the prior Clouds "
                "snapshot and whether the change is material."
            ),
            source_id=item.source_id,
            required_before_decision=True,
            raw_evidence_loaded=False,
            display_order=20,
        ),
    ]

    if item.impacted_source_id:
        evidence.append(
            DecisionEvidenceItem(
                evidence_id=(
                    f"{item.agenda_item_id}-impact-context"
                ),
                label="Impacted source context",
                explanation=(
                    "Confirm the affected source's current "
                    "state before treating the modeled "
                    "relationship as actionable."
                ),
                source_id=(
                    item.impacted_source_id
                ),
                required_before_decision=False,
                raw_evidence_loaded=False,
                display_order=30,
            )
        )

    return tuple(evidence)


def _owning_application(item):
    return (
        item.source_id,
        item.source_label,
    )


def build_owner_decision_packet(
    agenda_item_id,
):
    item = get_owner_agenda_item(
        agenda_item_id
    )

    (
        app_id,
        app_label,
    ) = _owning_application(item)

    options = _options(item)
    evidence = _evidence_items(item)

    required_evidence_present = all(
        evidence_item.explanation
        and evidence_item.source_id
        for evidence_item in evidence
        if evidence_item.required_before_decision
    )

    options_ready = (
        len(options) >= 3
        and all(
            option.explanation
            and option.what_happens_next
            and option.requires_owner_choice
            is True
            and option.executes_automatically
            is False
            for option in options
        )
    )

    packet_ready = (
        bool(
            _decision_question(item)
        )
        and bool(
            item.soulaana_what_happened
        )
        and bool(
            item.soulaana_what_it_means
        )
        and required_evidence_present
        and options_ready
    )

    impact_summary = (
        (
            f"{item.source_label} may affect "
            f"{item.impacted_source_label}. "
            f"{item.soulaana_what_it_means}"
        )
        if item.impacted_source_id
        else
        (
            "No additional impacted source is attached "
            "to this agenda item."
        )
    )

    return OwnerDecisionPacket(
        packet_id=(
            "decision-packet-"
            f"{agenda_item_id}"
        ),

        agenda_item_id=agenda_item_id,

        source_id=item.source_id,
        source_label=item.source_label,

        impacted_source_id=(
            item.impacted_source_id
        ),

        impacted_source_label=(
            item.impacted_source_label
        ),

        horizon=item.horizon,
        urgency=item.urgency,

        decision_question=(
            _decision_question(item)
        ),

        soulaana_summary=(
            f"{item.soulaana_what_happened} "
            f"{item.soulaana_what_it_means}"
        ),

        why_this_decision_exists=(
            item.soulaana_why_now
        ),

        what_changed=(
            item.soulaana_what_happened
        ),

        impact_summary=(
            impact_summary
        ),

        do_nothing_consequence=(
            item.soulaana_if_we_wait
        ),

        options=options,
        evidence_items=evidence,

        owner_review_prompts=(
            (
                "Do I understand what changed?"
            ),
            (
                "Do I understand why this belongs "
                "in its current owner-attention horizon?"
            ),
            (
                "Am I looking at source-owned evidence "
                "instead of relying only on Clouds?"
            ),
            (
                "What happens if I choose to wait?"
            ),
            (
                "Does this decision affect another "
                "Simplee business or system?"
            ),
        ),

        owning_application_id=(
            app_id
        ),

        owning_application_label=(
            app_label
        ),

        requires_tower_mediation=(
            app_id
            in TOWER_MEDIATED_SOURCES
        ),

        requires_owner_choice=True,

        packet_state=(
            DecisionPacketState
            .READY_FOR_OWNER_REVIEW.value
            if packet_ready
            else DecisionPacketState
            .BLOCKED.value
        ),

        automatic_decision_performed=False,
        approval_performed=False,
        capital_movement_performed=False,
        downstream_execution_performed=False,
    )


def get_owner_decision_packets():
    items = (
        get_owner_agenda_items()
    )

    packets = tuple(
        build_owner_decision_packet(
            item.agenda_item_id
        )
        for item in items
    )

    return tuple(
        sorted(
            packets,
            key=lambda packet: (
                packet.horizon,
                packet.urgency,
                packet.packet_id,
            ),
        )
    )


def get_owner_decision_packet(
    packet_id,
):
    for packet in (
        get_owner_decision_packets()
    ):
        if packet.packet_id == packet_id:
            return packet

    raise KeyError(
        "Unknown owner decision packet: "
        f"{packet_id}"
    )


def get_owner_decision_packet_surface():
    packets = (
        get_owner_decision_packets()
    )

    return OwnerDecisionPacketSurface(
        title=(
            "Owner Decision Prep / Decision Packets"
        ),

        packets=packets,

        packet_count=len(packets),

        ready_packet_count=sum(
            packet.packet_state
            == "ready_for_owner_review"
            for packet in packets
        ),

        blocked_packet_count=sum(
            packet.packet_state
            == "blocked"
            for packet in packets
        ),

        owner_choice_required_count=sum(
            packet.requires_owner_choice
            for packet in packets
        ),

        automatic_decision_performed=False,
        approval_performed=False,
        capital_movement_performed=False,
        downstream_execution_performed=False,

        boundary_notice=(
            "GP029 prepares owner decisions only. "
            "Clouds does not choose, approve, move capital, "
            "or execute downstream work."
        ),
    )


def get_owner_decision_packet_surface_payload():
    return (
        get_owner_decision_packet_surface()
        .to_dict()
    )


def get_clouds_gp029_status_payload():
    gp028 = (
        get_clouds_gp028_status_payload()
    )

    surface = (
        get_owner_decision_packet_surface()
    )

    packets = surface.packets

    safe = (
        gp028["status"] == "ready"
        and gp028["safe_to_continue"]
        is True

        and surface.packet_count
        == gp028["agenda_item_count"]

        and surface.ready_packet_count
        == surface.packet_count

        and surface.blocked_packet_count
        == 0

        and surface.owner_choice_required_count
        == surface.packet_count

        and all(
            packet.decision_question
            and packet.soulaana_summary
            and packet.why_this_decision_exists
            and packet.what_changed
            and packet.impact_summary
            and packet.do_nothing_consequence
            and len(packet.options) >= 3
            and len(packet.evidence_items) >= 2
            and packet.requires_owner_choice
            is True
            and packet
            .automatic_decision_performed
            is False
            and packet.approval_performed
            is False
            and packet.capital_movement_performed
            is False
            and packet
            .downstream_execution_performed
            is False
            for packet in packets
        )

        and surface
        .automatic_decision_performed
        is False

        and surface.approval_performed
        is False

        and surface.capital_movement_performed
        is False

        and surface
        .downstream_execution_performed
        is False
    )

    return {
        "pack": "GP029",

        "phase": "CLOUDS_PHASE_II",

        "section": (
            "OWNER DECISION PREP / "
            "DECISION PACKET SURFACE"
        ),

        "status": (
            "ready"
            if safe
            else "blocked"
        ),

        "safe_to_continue": safe,

        "packet_count": (
            surface.packet_count
        ),

        "ready_packet_count": (
            surface.ready_packet_count
        ),

        "blocked_packet_count": (
            surface.blocked_packet_count
        ),

        "owner_choice_required_count": (
            surface
            .owner_choice_required_count
        ),

        "decision_questions_present": True,
        "decision_options_present": True,
        "consequence_previews_present": True,
        "do_nothing_preview_present": True,
        "evidence_checklists_present": True,
        "owner_review_prompts_present": True,

        "automatic_decision_performed": False,
        "approval_performed": False,
        "capital_movement_performed": False,
        "downstream_execution_performed": False,

        "tower_authority_changed": False,
        "cross_app_imports_used": False,

        "next_pack": (
            "GP030 — OWNER DECISION REVIEW / "
            "READINESS GATE"
        ),
    }
