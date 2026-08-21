from pathlib import Path

from tower.owner_person_event_ledger import (
    PERSON_EVENT_SCHEMA_VERSION,
    VAULT_PACKET_TYPE,
    append_person_event,
    build_event_from_control_draft,
    build_person_event,
    build_vault_ready_person_packet,
    person_event_ledger_summary,
    read_event_by_id,
    read_person_events,
)


def test_summary_preserves_vault_boundary():
    summary = person_event_ledger_summary()

    assert summary["append_only_store"] is True
    assert summary["local_file_backing"] is True

    assert summary["production_archival_durability"] is False

    assert summary["vault_required_for_sealed_archive"] is True

    assert summary["vault_delivery_enabled"] is False

    assert summary["browser_direct_vault_access"] is False

    assert summary["real_permission_changes"] is False

    assert summary["live_auto"] == "LOCKED"


def test_build_person_event():
    result = build_person_event(
        "future-manager-seat",
        event_type="TEST_EVENT",
        action="designation",
        before_state={
            "designation": "Manager Candidate",
        },
        requested_state={
            "designation": "Manager",
        },
    )

    assert result["status"] == "person_event_built"

    event = result["event"]

    assert event["schema_version"] == PERSON_EVENT_SCHEMA_VERSION

    assert event["person_id"] == "future-manager-seat"

    assert event["vault_status"] == "NOT_READY_FOR_VAULT"

    assert event["integrity_hash"]


def test_append_only_round_trip(tmp_path):
    ledger = tmp_path / "ledger.jsonl"

    first = build_person_event(
        "future-manager-seat",
        event_type="FIRST",
        action="designation",
    )["event"]

    second = build_person_event(
        "future-manager-seat",
        event_type="SECOND",
        action="status",
    )["event"]

    assert append_person_event(
        first,
        ledger_path=ledger,
    )["appended"] is True

    assert append_person_event(
        second,
        ledger_path=ledger,
    )["appended"] is True

    events = read_person_events(
        "future-manager-seat",
        ledger_path=ledger,
    )

    assert len(events) == 2

    assert events[0]["event_id"] == first["event_id"]

    assert events[1]["event_id"] == second["event_id"]


def test_read_event_by_id(tmp_path):
    ledger = tmp_path / "ledger.jsonl"

    event = build_person_event(
        "future-manager-seat",
        event_type="TEST",
        action="freeze",
    )["event"]

    append_person_event(
        event,
        ledger_path=ledger,
    )

    found = read_event_by_id(
        event["event_id"],
        ledger_path=ledger,
    )

    assert found is not None

    assert found["event_id"] == event["event_id"]


def test_build_event_from_existing_control_draft(monkeypatch, tmp_path):
    import tower.owner_person_event_ledger as ledger_module

    ledger_path = tmp_path / "control-ledger.jsonl"

    monkeypatch.setattr(
        ledger_module,
        "_runtime_ledger_path",
        lambda: ledger_path,
    )

    result = build_event_from_control_draft(
        "future-manager-seat",
        {
            "action": "designation",
            "requested_designation": "Manager",
            "notes": "Owner review",
        },
    )

    assert result["status"] == "person_control_event_recorded"

    assert result["event"]["action"] == "designation"

    assert result["event"]["requested_state"]["designation"] == "Manager"

    assert result["event"]["vault_status"] == "NOT_READY_FOR_VAULT"

    assert result["append_result"]["production_archival_durability"] is False


def test_vault_packet_not_ready_before_approval():
    event = build_person_event(
        "future-manager-seat",
        event_type="PERSON_CONTROL_DRAFT",
        action="designation",
        requested_state={
            "designation": "Manager",
        },
    )["event"]

    result = build_vault_ready_person_packet(
        event,
        owner_decision="HOLD",
    )

    assert result["status"] == "vault_person_packet_not_ready"

    assert result["packet"]["packet_type"] == VAULT_PACKET_TYPE

    assert result["packet"]["archive_ready"] is False

    assert result["packet"]["vault_status"] == "NOT_READY_FOR_VAULT"

    assert result["vault_delivery_performed"] is False


def test_vault_packet_ready_only_when_approved():
    event = build_person_event(
        "future-manager-seat",
        event_type="PERSON_CONTROL_DRAFT",
        action="designation",
        requested_state={
            "designation": "Manager",
        },
    )["event"]

    result = build_vault_ready_person_packet(
        event,
        owner_decision="APPROVED",
        decision_reason="Approved by owner",
        decision_receipt_id="decision-123",
    )

    assert result["status"] == "vault_person_packet_ready"

    packet = result["packet"]

    assert packet["packet_type"] == "TOWER_PERSON_CHANGE_PROOF"

    assert packet["source_system"] == "TOWER"

    assert packet["destination_system"] == "VAULT"

    assert packet["archive_ready"] is True

    assert packet["vault_status"] == "READY_FOR_VAULT"

    assert packet["vault_delivery_performed"] is False

    assert packet["packet_integrity_hash"]


def test_unknown_person_event_fails_closed():
    result = build_person_event(
        "not-real",
        event_type="TEST",
        action="designation",
    )

    assert result["status"] == "not_found"

    assert result["real_permission_changes"] is False
