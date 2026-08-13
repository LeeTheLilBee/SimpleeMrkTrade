import pytest

from clouds.executive_owner_agenda_service import (
    get_executive_owner_agenda,
    get_owner_agenda_items,
)

from clouds.owner_decision_packet_service import (
    build_owner_decision_packet,
    get_clouds_gp029_status_payload,
    get_owner_decision_packet,
    get_owner_decision_packet_surface,
    get_owner_decision_packet_surface_payload,
    get_owner_decision_packets,
)


def test_gp029_one_packet_per_agenda_item():
    agenda = (
        get_executive_owner_agenda()
    )

    surface = (
        get_owner_decision_packet_surface()
    )

    assert (
        surface.packet_count
        == agenda.item_count
    )


def test_gp029_all_packets_ready():
    packets = (
        get_owner_decision_packets()
    )

    assert packets

    assert all(
        packet.packet_state
        == "ready_for_owner_review"
        for packet in packets
    )


def test_gp029_every_packet_has_decision_question():
    for packet in (
        get_owner_decision_packets()
    ):
        assert (
            packet.decision_question
        )

        assert (
            "?"
            in packet.decision_question
        )


def test_gp029_every_packet_has_choices():
    for packet in (
        get_owner_decision_packets()
    ):
        assert (
            len(packet.options)
            >= 3
        )


def test_gp029_every_option_is_nonexecuting():
    for packet in (
        get_owner_decision_packets()
    ):
        for option in packet.options:
            assert (
                option.requires_owner_choice
                is True
            )

            assert (
                option.executes_automatically
                is False
            )


def test_gp029_every_packet_has_evidence_checklist():
    for packet in (
        get_owner_decision_packets()
    ):
        assert (
            len(packet.evidence_items)
            >= 2
        )

        assert any(
            item.required_before_decision
            for item
            in packet.evidence_items
        )


def test_gp029_evidence_is_not_raw_loaded():
    for packet in (
        get_owner_decision_packets()
    ):
        assert all(
            item.raw_evidence_loaded
            is False
            for item
            in packet.evidence_items
        )


def test_gp029_every_packet_has_owner_review_prompts():
    for packet in (
        get_owner_decision_packets()
    ):
        assert (
            len(
                packet.owner_review_prompts
            )
            == 5
        )


def test_gp029_observatory_packet_requires_tower():
    packet = (
        build_owner_decision_packet(
            "agenda-change-observatory"
        )
    )

    assert (
        packet.owning_application_id
        == "observatory"
    )

    assert (
        packet.requires_tower_mediation
        is True
    )


def test_gp029_atm_packet_does_not_require_tower():
    packet = (
        build_owner_decision_packet(
            "agenda-change-atm_operations"
        )
    )

    assert (
        packet.owning_application_id
        == "atm_operations"
    )

    assert (
        packet.requires_tower_mediation
        is False
    )


def test_gp029_cross_business_packet_mentions_impact():
    packet = (
        build_owner_decision_packet(
            "agenda-impact-observatory-atm_operations"
        )
    )

    assert (
        packet.impacted_source_id
        == "atm_operations"
    )

    assert (
        "ATM"
        in packet.impact_summary
        or "atm"
        in packet.impact_summary.lower()
    )


def test_gp029_no_decisions_are_made():
    for packet in (
        get_owner_decision_packets()
    ):
        assert (
            packet.automatic_decision_performed
            is False
        )

        assert (
            packet.approval_performed
            is False
        )


def test_gp029_no_capital_movement():
    for packet in (
        get_owner_decision_packets()
    ):
        assert (
            packet.capital_movement_performed
            is False
        )


def test_gp029_no_execution():
    for packet in (
        get_owner_decision_packets()
    ):
        assert (
            packet.downstream_execution_performed
            is False
        )


def test_gp029_unknown_agenda_item_fails_closed():
    with pytest.raises(KeyError):
        build_owner_decision_packet(
            "missing-agenda-item"
        )


def test_gp029_unknown_packet_fails_closed():
    with pytest.raises(KeyError):
        get_owner_decision_packet(
            "missing-packet"
        )


def test_gp029_packet_lookup():
    packets = (
        get_owner_decision_packets()
    )

    first = packets[0]

    assert (
        get_owner_decision_packet(
            first.packet_id
        )
        == first
    )


def test_gp029_surface_counts():
    surface = (
        get_owner_decision_packet_surface()
    )

    assert (
        surface.packet_count
        == surface.ready_packet_count
    )

    assert (
        surface.blocked_packet_count
        == 0
    )

    assert (
        surface.owner_choice_required_count
        == surface.packet_count
    )


def test_gp029_surface_executes_nothing():
    surface = (
        get_owner_decision_packet_surface()
    )

    assert (
        surface.automatic_decision_performed
        is False
    )

    assert (
        surface.approval_performed
        is False
    )

    assert (
        surface.capital_movement_performed
        is False
    )

    assert (
        surface.downstream_execution_performed
        is False
    )


def test_gp029_payload_serializes():
    payload = (
        get_owner_decision_packet_surface_payload()
    )

    assert (
        payload["packet_count"]
        == len(payload["packets"])
    )


def test_gp029_status_ready():
    status = (
        get_clouds_gp029_status_payload()
    )

    assert status["pack"] == "GP029"

    assert (
        status["phase"]
        == "CLOUDS_PHASE_II"
    )

    assert (
        status["status"]
        == "ready"
    )

    assert (
        status["safe_to_continue"]
        is True
    )

    assert (
        status["packet_count"]
        == status[
            "ready_packet_count"
        ]
    )

    assert (
        status["blocked_packet_count"]
        == 0
    )

    assert (
        status[
            "owner_choice_required_count"
        ]
        == status["packet_count"]
    )

    assert (
        status[
            "decision_questions_present"
        ]
        is True
    )

    assert (
        status[
            "decision_options_present"
        ]
        is True
    )

    assert (
        status[
            "consequence_previews_present"
        ]
        is True
    )

    assert (
        status[
            "evidence_checklists_present"
        ]
        is True
    )

    assert (
        status[
            "automatic_decision_performed"
        ]
        is False
    )

    assert (
        status[
            "approval_performed"
        ]
        is False
    )

    assert (
        status[
            "capital_movement_performed"
        ]
        is False
    )

    assert (
        status[
            "downstream_execution_performed"
        ]
        is False
    )

    assert status["next_pack"] == (
        "GP030 — OWNER DECISION REVIEW / "
        "READINESS GATE"
    )
