import json

import tower.archive_vault_handoff as handoff
import tower.archive_vault_intake_acceptance as intake
import tower.owner_person_event_ledger as ledger


def sample_packet():

    packet = {

        "schema_version": (
            "tower.vault.person-change-proof.v1"
        ),

        "packet_id": (
            "packet-test"
        ),

        "packet_type": (
            "TOWER_PERSON_CHANGE_PROOF"
        ),

        "source_system": (
            "TOWER"
        ),

        "destination_system": (
            "VAULT"
        ),

        "person_id": (
            "future-manager-seat"
        ),

        "display_name": (
            "Future Manager Seat"
        ),

        "event_id": (
            "event-test"
        ),

        "event_type": (
            "PERSON_CONTROL_DRAFT"
        ),

        "action": (
            "designation"
        ),

        "before_state": {
            "designation": (
                "Manager Candidate"
            ),
        },

        "requested_state": {
            "designation": (
                "Manager"
            ),
        },

        "resulting_state": {},

        "reason": (
            "Owner requested"
        ),

        "owner_decision": (
            "APPROVED"
        ),

        "decision_reason": (
            "Approved"
        ),

        "decision_receipt_id": (
            "decision-receipt"
        ),

        "tower_event_integrity_hash": (
            "tower-event-hash"
        ),

        "tower_validation": {},

        "related_receipt_ids": [],

        "created_at_utc": (
            "2026-08-20T00:00:00Z"
        ),

        "packet_created_at_utc": (
            "2026-08-20T00:01:00Z"
        ),

        "archive_ready": True,

        "vault_status": (
            "READY_FOR_VAULT"
        ),

        "vault_delivery_performed": False,

        "vault_acceptance_receipt": None,
    }


    packet[
        "packet_integrity_hash"
    ] = intake._sha256({

        key: value

        for key, value
        in packet.items()

        if key
        != "packet_integrity_hash"
    })


    return packet


def sample_handoff():

    packet = (
        sample_packet()
    )


    record = (

        handoff.build_archive_vault_handoff_record(

            source_type=(
                "tower_person_change_proof"
            ),

            source_id=(
                "event-test"
            ),

            title=(
                "Tower person change proof"
            ),

            summary=(
                "Approved change"
            ),

            related_object={

                "person_id": (
                    "future-manager-seat"
                ),

                "event_id": (
                    "event-test"
                ),

                "packet_id": (
                    packet[
                        "packet_id"
                    ]
                ),

                "tower_event_integrity_hash": (
                    packet[
                        "tower_event_integrity_hash"
                    ]
                ),

                "packet_integrity_hash": (
                    packet[
                        "packet_integrity_hash"
                    ]
                ),
            },

            source_payload={

                "person_change_proof_packet": (
                    packet
                ),
            },
        )
    )


    return record


def setup_paths(
    monkeypatch,
    tmp_path,
):

    queue = (
        tmp_path
        / "queue.json"
    )

    acceptance = (
        tmp_path
        / "acceptance.jsonl"
    )

    person_ledger = (
        tmp_path
        / "person-ledger.jsonl"
    )


    monkeypatch.setattr(
        intake,
        "ARCHIVE_HANDOFF_PATH",
        queue,
    )


    monkeypatch.setattr(
        intake,
        "ARCHIVE_VAULT_ACCEPTANCE_PATH",
        acceptance,
    )


    monkeypatch.setattr(
        ledger,
        "_runtime_ledger_path",
        lambda: person_ledger,
    )


    monkeypatch.setattr(
        intake,
        "append_person_event",
        ledger.append_person_event,
    )


    return (
        queue,
        acceptance,
        person_ledger,
    )


def write_queue(
    queue,
    record,
):

    queue.write_text(
        json.dumps(
            [
                record
            ],
            indent=2,
        ),
        encoding="utf-8",
    )


def test_summary():

    summary = (
        intake.archive_vault_intake_summary()
    )


    assert (
        summary[
            "queue_state"
        ]
        == "VAULT_HANDOFF_QUEUED"
    )


    assert (
        summary[
            "accepted_state"
        ]
        == "VAULT_ACCEPTED"
    )


    assert (
        summary[
            "sealed_state"
        ]
        == "VAULT_SEALED"
    )


    assert (
        summary[
            "duplicate_acceptance_blocked"
        ]
        is True
    )


    assert (
        summary[
            "external_hardened_archive_storage"
        ]
        is False
    )


def test_valid_intake():

    result = (
        intake.validate_archive_vault_intake(
            sample_handoff()
        )
    )


    assert (
        result[
            "status"
        ]
        == "archive_vault_intake_valid"
    )


    assert (
        result[
            "errors"
        ]
        == []
    )


def test_tampered_packet_rejected():

    record = (
        sample_handoff()
    )


    record[
        "source_payload"
    ][
        "person_change_proof_packet"
    ][
        "person_id"
    ] = "tampered-person"


    result = (
        intake.validate_archive_vault_intake(
            record
        )
    )


    assert (
        result[
            "status"
        ]
        == "archive_vault_intake_invalid"
    )


    assert (
        "packet_integrity_hash_mismatch"
        in result[
            "errors"
        ]
    )


def test_unapproved_packet_rejected():

    record = (
        sample_handoff()
    )


    packet = (
        record[
            "source_payload"
        ][
            "person_change_proof_packet"
        ]
    )


    packet[
        "owner_decision"
    ] = "REJECTED"


    packet[
        "packet_integrity_hash"
    ] = intake._sha256({

        key: value

        for key, value
        in packet.items()

        if key
        != "packet_integrity_hash"
    })


    result = (
        intake.validate_archive_vault_intake(
            record
        )
    )


    assert (
        "owner_decision_not_approved"
        in result[
            "errors"
        ]
    )


def test_acceptance_creates_receipt(
    monkeypatch,
    tmp_path,
):

    queue, acceptance, _ = (
        setup_paths(
            monkeypatch,
            tmp_path,
        )
    )


    record = (
        sample_handoff()
    )


    write_queue(
        queue,
        record,
    )


    result = (
        intake.accept_archive_vault_handoff(

            record[
                "handoff_id"
            ],

            queue_path=queue,

            acceptance_path=acceptance,
        )
    )


    assert (
        result[
            "status"
        ]
        == "archive_vault_handoff_accepted"
    )


    assert (
        result[
            "accepted"
        ]
        is True
    )


    assert (
        result[
            "sealed"
        ]
        is True
    )


    assert (
        result[
            "vault_status"
        ]
        == "VAULT_SEALED"
    )


    assert (
        result[
            "vault_receipt_id"
        ]
    )


    assert (
        result[
            "vault_record_reference"
        ]
    )


    assert (
        acceptance.exists()
    )


def test_duplicate_acceptance_blocked(
    monkeypatch,
    tmp_path,
):

    queue, acceptance, _ = (
        setup_paths(
            monkeypatch,
            tmp_path,
        )
    )


    record = (
        sample_handoff()
    )


    write_queue(
        queue,
        record,
    )


    first = (
        intake.accept_archive_vault_handoff(

            record[
                "handoff_id"
            ],

            queue_path=queue,

            acceptance_path=acceptance,
        )
    )


    second = (
        intake.accept_archive_vault_handoff(

            record[
                "handoff_id"
            ],

            queue_path=queue,

            acceptance_path=acceptance,
        )
    )


    assert (
        first[
            "status"
        ]
        == "archive_vault_handoff_accepted"
    )


    assert (
        second[
            "status"
        ]
        == "archive_vault_handoff_already_accepted"
    )


    assert (
        second[
            "duplicate_acceptance_blocked"
        ]
        is True
    )


def test_record_person_history_after_acceptance(
    monkeypatch,
    tmp_path,
):

    queue, acceptance, _ = (
        setup_paths(
            monkeypatch,
            tmp_path,
        )
    )


    record = (
        sample_handoff()
    )


    write_queue(
        queue,
        record,
    )


    result = (
        intake.accept_archive_vault_handoff(

            record[
                "handoff_id"
            ],

            queue_path=queue,

            acceptance_path=acceptance,
        )
    )


    history = (
        intake.record_person_vault_acceptance(
            result
        )
    )


    assert (
        history[
            "status"
        ]
        == "person_vault_acceptance_recorded"
    )


    assert (
        history[
            "event"
        ][
            "event_type"
        ]
        == "PERSON_ARCHIVE_VAULT_ACCEPTED"
    )


    assert (
        history[
            "event"
        ][
            "resulting_state"
        ][
            "vault_status"
        ]
        == "VAULT_SEALED"
    )
