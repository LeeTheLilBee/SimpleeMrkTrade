from pathlib import Path

import tower.archive_vault_handoff as archive
import tower.owner_person_archive_vault_queue_binding as binding
import tower.owner_person_decision_workflow as decisions
import tower.owner_person_event_ledger as ledger


def setup(monkeypatch, tmp_path):

    person_ledger = (
        tmp_path
        / "person-ledger.jsonl"
    )

    archive_queue = (
        tmp_path
        / "archive-queue.json"
    )


    monkeypatch.setattr(
        ledger,
        "_runtime_ledger_path",
        lambda: person_ledger,
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
        binding,
        "read_event_by_id",
        ledger.read_event_by_id,
    )


    monkeypatch.setattr(
        binding,
        "append_person_event",
        ledger.append_person_event,
    )


    monkeypatch.setattr(
        binding,
        "latest_decision_for_event",
        decisions.latest_decision_for_event,
    )


    monkeypatch.setattr(
        archive,
        "ARCHIVE_HANDOFF_PATH",
        archive_queue,
    )


    monkeypatch.setattr(
        binding,
        "queue_archive_vault_handoff",
        archive.queue_archive_vault_handoff,
    )


    event = (
        ledger.build_person_event(

            "future-manager-seat",

            event_type=(
                "PERSON_CONTROL_DRAFT"
            ),

            action="designation",

            requested_state={
                "designation": "Manager",
            },
        )[
            "event"
        ]
    )


    ledger.append_person_event(
        event
    )


    return (
        event,
        person_ledger,
        archive_queue,
    )


def approve(event):

    return (
        decisions.build_owner_decision(

            "future-manager-seat",

            event[
                "event_id"
            ],

            "APPROVED",

            reason=(
                "Owner approved"
            ),
        )
    )


def test_summary_truth_boundary():

    summary = (
        binding.person_archive_vault_queue_summary()
    )


    assert (
        summary[
            "existing_handoff_module"
        ]
        == "tower.archive_vault_handoff"
    )


    assert (
        summary[
            "tower_queue_status"
        ]
        == "VAULT_HANDOFF_QUEUED"
    )


    assert (
        summary[
            "vault_accepted"
        ]
        is False
    )


    assert (
        summary[
            "vault_sealed"
        ]
        is False
    )


    assert (
        summary[
            "archive_vault_app_wired"
        ]
        is False
    )


def test_unapproved_event_cannot_queue(
    monkeypatch,
    tmp_path,
):

    event, _, _ = (
        setup(
            monkeypatch,
            tmp_path,
        )
    )


    result = (
        binding.queue_person_event_for_archive_vault(

            "future-manager-seat",

            event[
                "event_id"
            ],
        )
    )


    assert (
        result[
            "status"
        ]
        == "owner_decision_required"
    )


    assert (
        result[
            "vault_queue_performed"
        ]
        is False
    )


def test_approved_event_builds_existing_handoff_record(
    monkeypatch,
    tmp_path,
):

    event, _, _ = (
        setup(
            monkeypatch,
            tmp_path,
        )
    )


    approve(
        event
    )


    result = (
        binding.build_person_archive_handoff_record(

            "future-manager-seat",

            event[
                "event_id"
            ],
        )
    )


    assert (
        result[
            "status"
        ]
        == "person_archive_handoff_record_ready"
    )


    record = (
        result[
            "handoff_record"
        ]
    )


    assert (
        record[
            "destination"
        ]
        == "Archive Vault"
    )


    assert (
        record[
            "source_type"
        ]
        == "tower_person_change_proof"
    )


    assert (
        record[
            "status"
        ]
        == "queued"
    )


    assert (
        record[
            "evidence_bundle_stub"
        ][
            "ready_for_archive_vault"
        ]
        is False
    )


def test_approved_event_queues_real_existing_handoff(
    monkeypatch,
    tmp_path,
):

    event, person_ledger, archive_queue = (
        setup(
            monkeypatch,
            tmp_path,
        )
    )


    approve(
        event
    )


    result = (
        binding.queue_person_event_for_archive_vault(

            "future-manager-seat",

            event[
                "event_id"
            ],

            owner_note=(
                "Archive approved person change."
            ),
        )
    )


    assert (
        result[
            "status"
        ]
        == "person_archive_vault_handoff_queued"
    )


    assert (
        result[
            "vault_status"
        ]
        == "VAULT_HANDOFF_QUEUED"
    )


    assert (
        result[
            "vault_accepted"
        ]
        is False
    )


    assert (
        result[
            "vault_sealed"
        ]
        is False
    )


    assert (
        result[
            "existing_handoff_reused"
        ]
        is True
    )


    assert (
        result[
            "creates_parallel_transport"
        ]
        is False
    )


    assert (
        result[
            "handoff_id"
        ]
    )


    assert (
        archive_queue.exists()
    )


    queued_data = (
        archive._load_json_list(
            archive_queue
        )
    )


    assert (
        len(
            queued_data
        )
        == 1
    )


    assert (
        queued_data[
            0
        ][
            "source_type"
        ]
        == "tower_person_change_proof"
    )


    person_events = (
        ledger.read_person_events(
            "future-manager-seat"
        )
    )


    assert any(
        item.get(
            "event_type"
        )
        == "PERSON_ARCHIVE_VAULT_HANDOFF_QUEUED"

        for item
        in person_events
    )


def test_queue_receipt_does_not_claim_sealed(
    monkeypatch,
    tmp_path,
):

    event, _, _ = (
        setup(
            monkeypatch,
            tmp_path,
        )
    )


    approve(
        event
    )


    result = (
        binding.queue_person_event_for_archive_vault(

            "future-manager-seat",

            event[
                "event_id"
            ],
        )
    )


    receipt = (
        result[
            "receipt"
        ]
    )


    assert (
        receipt[
            "vault_status"
        ]
        == "VAULT_HANDOFF_QUEUED"
    )


    assert (
        receipt[
            "vault_accepted"
        ]
        is False
    )


    assert (
        receipt[
            "vault_sealed"
        ]
        is False
    )


    assert (
        "has not occurred"
        in receipt[
            "message"
        ]
    )
