from pathlib import Path

import tower.owner_person_event_ledger as ledger
import tower.owner_person_decision_workflow as decisions
import tower.owner_person_vault_handoff_adapter as adapter


def setup(monkeypatch, tmp_path):

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

    monkeypatch.setattr(
        adapter,
        "read_event_by_id",
        ledger.read_event_by_id,
    )

    monkeypatch.setattr(
        adapter,
        "append_person_event",
        ledger.append_person_event,
    )

    monkeypatch.setattr(
        adapter,
        "latest_decision_for_event",
        decisions.latest_decision_for_event,
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


def approve(event):
    return decisions.build_owner_decision(
        "future-manager-seat",
        event["event_id"],
        "APPROVED",
    )


def test_summary():
    summary = adapter.person_vault_handoff_adapter_summary()

    assert summary["creates_new_vault_transport"] is False
    assert summary["browser_direct_vault_access"] is False
    assert summary["fail_closed_when_handoff_unresolved"] is True


def test_unapproved_cannot_send(monkeypatch, tmp_path):
    event = setup(monkeypatch, tmp_path)

    result = adapter.deliver_person_event_to_existing_vault_handoff(
        "future-manager-seat",
        event["event_id"],
        handoff_callable=lambda packet: {
            "accepted": True,
        },
    )

    assert result["status"] == "owner_decision_required"
    assert result["vault_delivery_performed"] is False


def test_approved_reuses_callable(monkeypatch, tmp_path):
    event = setup(monkeypatch, tmp_path)

    approve(event)

    seen = {}

    def existing_handoff(packet):
        seen["packet"] = packet

        return {
            "status": "vault_accepted",
            "accepted": True,
            "vault_record_reference": "vault-record-123",
        }

    result = adapter.deliver_person_event_to_existing_vault_handoff(
        "future-manager-seat",
        event["event_id"],
        handoff_callable=existing_handoff,
    )

    assert result["status"] == "person_vault_handoff_sealed"
    assert result["existing_handoff_reused"] is True
    assert result["creates_new_vault_transport"] is False
    assert result["vault_status"] == "VAULT_SEALED"
    assert result["vault_record_reference"] == "vault-record-123"

    assert seen["packet"]["packet_type"] == "TOWER_PERSON_CHANGE_PROOF"


def test_ambiguous_result_does_not_claim_sealed(monkeypatch, tmp_path):
    event = setup(monkeypatch, tmp_path)

    approve(event)

    def existing_handoff(packet):
        return {
            "status": "processed",
        }

    result = adapter.deliver_person_event_to_existing_vault_handoff(
        "future-manager-seat",
        event["event_id"],
        handoff_callable=existing_handoff,
    )

    assert result["status"] == "person_vault_handoff_failed"
    assert result["vault_status"] == "VAULT_DELIVERY_FAILED"


def test_explicit_sealed_result():
    normalized = adapter.normalize_vault_handoff_result(
        {
            "sealed": True,
            "record_id": "abc",
        }
    )

    assert normalized["vault_status"] == "VAULT_SEALED"
    assert normalized["vault_record_reference"] == "abc"


def test_unresolved_is_fail_closed(monkeypatch):
    monkeypatch.delenv(
        "TOWER_VAULT_HANDOFF_CALLABLE",
        raising=False,
    )

    result = adapter.resolve_existing_vault_handoff()

    assert result["status"] == "existing_vault_handoff_not_resolved"
    assert result["callable"] is None
