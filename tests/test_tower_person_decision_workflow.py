from pathlib import Path

import tower.owner_person_decision_workflow as decisions
import tower.owner_person_event_ledger as ledger


def seed_event(monkeypatch, tmp_path):
    path = tmp_path / "ledger.jsonl"

    monkeypatch.setattr(
        ledger,
        "_runtime_ledger_path",
        lambda: path,
    )

    monkeypatch.setattr(
        decisions,
        "read_person_events",
        ledger.read_person_events,
    )

    monkeypatch.setattr(
        decisions,
        "read_event_by_id",
        ledger.read_event_by_id,
    )

    monkeypatch.setattr(
        decisions,
        "append_person_event",
        ledger.append_person_event,
    )

    event = ledger.build_person_event(
        "future-manager-seat",
        event_type="PERSON_CONTROL_DRAFT",
        action="designation",
        requested_state={
            "designation": "Manager",
        },
    )["event"]

    ledger.append_person_event(event)

    return event


def test_summary():
    summary = decisions.person_owner_decision_summary()

    assert summary["source_event_mutation"] is False
    assert summary["vault_delivery_enabled"] is False
    assert summary["approved_effective_vault_status"] == "READY_FOR_VAULT"


def test_pending_event(monkeypatch, tmp_path):
    event = seed_event(monkeypatch, tmp_path)

    pending = decisions.pending_owner_decisions(
        "future-manager-seat"
    )

    assert len(pending) == 1
    assert pending[0]["event_id"] == event["event_id"]


def test_approve(monkeypatch, tmp_path):
    event = seed_event(monkeypatch, tmp_path)

    result = decisions.build_owner_decision(
        "future-manager-seat",
        event["event_id"],
        "APPROVED",
        reason="Approved",
    )

    assert result["status"] == "person_owner_decision_recorded"
    assert result["decision"] == "APPROVED"
    assert result["decision_receipt"]["effective_vault_status"] == "READY_FOR_VAULT"
    assert result["decision_receipt"]["source_event_mutated"] is False
    assert result["vault_packet_preview"]["status"] == "vault_person_packet_ready"
    assert result["vault_packet_preview"]["vault_delivery_performed"] is False


def test_reject_stays_not_ready(monkeypatch, tmp_path):
    event = seed_event(monkeypatch, tmp_path)

    result = decisions.build_owner_decision(
        "future-manager-seat",
        event["event_id"],
        "REJECTED",
    )

    assert result["decision_receipt"]["effective_vault_status"] == "NOT_READY_FOR_VAULT"


def test_hold(monkeypatch, tmp_path):
    event = seed_event(monkeypatch, tmp_path)

    result = decisions.build_owner_decision(
        "future-manager-seat",
        event["event_id"],
        "HOLD",
    )

    assert result["status"] == "person_owner_decision_recorded"


def test_return_for_changes(monkeypatch, tmp_path):
    event = seed_event(monkeypatch, tmp_path)

    result = decisions.build_owner_decision(
        "future-manager-seat",
        event["event_id"],
        "RETURN_FOR_CHANGES",
    )

    assert result["status"] == "person_owner_decision_recorded"


def test_second_decision_blocked(monkeypatch, tmp_path):
    event = seed_event(monkeypatch, tmp_path)

    decisions.build_owner_decision(
        "future-manager-seat",
        event["event_id"],
        "APPROVED",
    )

    result = decisions.build_owner_decision(
        "future-manager-seat",
        event["event_id"],
        "REJECTED",
    )

    assert result["status"] == "owner_decision_already_exists"
