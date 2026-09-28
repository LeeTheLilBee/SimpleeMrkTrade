"""SC022 journal-only backup coverage: one backup count cannot hide missing objects."""
import json
import os
import sqlite3

import pytest

from simplee_cloud.contracts import IntegrityError
from simplee_cloud.owner_evidence_desk import owner_local_evidence_desk
from simplee_cloud.source_status import owner_safe_source_markdown, owner_safe_source_snapshot
from simplee_cloud.tests.test_sc004b_bound_port import Harness, PEER
from simplee_cloud.tests.test_sc005b_backup_operations import AcceptBackupThenTimeout


def write(h, request, *, ref=None, digest=None, entity="trust"):
    return h.port.write(
        grant=h.grant(request, "WRITE_CIPHERTEXT", ref=ref, digest=digest, entity=entity),
        authenticated_transport_peer=PEER, request_id=request, envelope=h.data,
    )


def backup(h, request, *, ref=None, digest=None, entity="trust"):
    return h.port.create_encrypted_backup(
        grant=h.grant(request, "BACKUP_CIPHERTEXT", ref=ref, digest=digest, entity=entity),
        authenticated_transport_peer=PEER, request_id=request,
    )


def coverage(h):
    return h.journal.source_backup_coverage()


def test_empty_local_journal_is_not_physical_backup_evidence(tmp_path):
    h = Harness(tmp_path)
    report = coverage(h)
    assert report["acknowledged_primary_object_count"] == 0
    assert report["matched_backup_ack_count"] == 0
    assert report["uncovered_primary_object_count"] == 0
    assert report["actual_backup_bytes_reverified"] is False
    assert report["independent_failure_domain_certified"] is False
    assert report["vault_canonical_backup_receipt_verified"] is False
    assert report["production_authorized"] is False


def test_one_write_without_backup_is_visible_in_owner_focus_and_desk(tmp_path):
    h = Harness(tmp_path)
    write(h, "write-1")
    report = coverage(h)
    assert report["acknowledged_primary_object_count"] == 1
    assert report["uncovered_primary_object_count"] == 1
    assert report["uncovered_without_pending_backup_count"] == 1
    snapshot = owner_safe_source_snapshot(h.journal)
    assert snapshot["attention"] == "LOCAL_SOURCE_REVIEW_REQUIRED"
    assert any(x["key"] == "backup_coverage" and x["count"] == 1 for x in snapshot["work_queue"])
    assert "Objects without backup ACK | 1" in owner_safe_source_markdown(h.journal)
    desk = owner_local_evidence_desk(journal=h.journal, replay_store=h.nonces)
    assert desk["local_storage"]["uncovered_primary_object_count"] == 1
    assert desk["local_storage"]["actual_backup_bytes_reverified"] is False
    assert desk["production_authorized"] is False


def test_two_distinct_primary_objects_one_backup_only_covers_matching_object(tmp_path):
    h = Harness(tmp_path)
    write(h, "write-1")
    another = h.source.new_object_ref()
    write(h, "write-2", ref=another)
    backup(h, "backup-1")
    result = coverage(h)
    assert result["acknowledged_primary_object_count"] == 2
    assert result["matched_backup_ack_count"] == 1
    assert result["uncovered_primary_object_count"] == 1
    assert result["uncovered_without_pending_backup_count"] == 1


def test_pending_backup_does_not_count_as_covered_then_original_reconciliation_counts(tmp_path):
    h = Harness(tmp_path)
    write(h, "write-1")
    unreliable = AcceptBackupThenTimeout()
    h.backup.backup_backend = unreliable
    with pytest.raises(OSError):
        backup(h, "backup-1")
    pending = coverage(h)
    assert pending["acknowledged_primary_object_count"] == 1
    assert pending["matched_backup_ack_count"] == 0
    assert pending["uncovered_with_pending_backup_count"] == 1
    assert pending["uncovered_without_pending_backup_count"] == 0
    signed = h.grant("backup-1", "RECONCILE_BACKUP")
    result = h.port.reconcile_original_backup(
        grant=signed, authenticated_transport_peer=PEER,
        original_request_id="backup-1",
    )
    assert result["status"] == "PRESENT_INTERNAL_BACKUP_ONLY"
    after = coverage(h)
    assert after["matched_backup_ack_count"] == 1
    assert after["uncovered_primary_object_count"] == 0
    assert after["actual_backup_bytes_reverified"] is False
    assert unreliable.calls == 1


def test_cross_entity_backup_cannot_count_for_other_entity_even_same_ref_and_digest(tmp_path):
    h = Harness(tmp_path)
    write(h, "write-trust", entity="trust")
    write(h, "write-other", entity="different-entity")
    backup(h, "backup-trust", entity="trust")
    result = coverage(h)
    assert result["acknowledged_primary_object_count"] == 2
    assert result["matched_backup_ack_count"] == 1
    assert result["uncovered_primary_object_count"] == 1
    assert result["vault_canonical_backup_receipt_verified"] is False


def test_wrong_source_ref_backup_does_not_cover_primary(tmp_path):
    h = Harness(tmp_path)
    write(h, "write-1")
    other_ref = h.source.new_object_ref()
    with pytest.raises(Exception):
        backup(h, "backup-other", ref=other_ref)
    result = coverage(h)
    assert result["uncovered_primary_object_count"] == 1
    assert result["matched_backup_ack_count"] == 0


def test_backup_replay_integrity_hold_removes_ack_coverage(tmp_path):
    h = Harness(tmp_path)
    write(h, "write-1")
    receipt = backup(h, "backup-1")
    assert coverage(h)["matched_backup_ack_count"] == 1
    target = h.backup_backend.root / receipt.namespace_digest / receipt.backup_ref
    data = target.read_bytes()
    target.write_bytes(data[:-1] + bytes([data[-1] ^ 1]))
    with pytest.raises(IntegrityError):
        backup(h, "backup-1")
    result = coverage(h)
    assert result["uncovered_primary_object_count"] == 1
    assert result["matched_backup_ack_count"] == 0


def test_primary_replay_integrity_hold_is_not_counted_as_acknowledged(tmp_path):
    h = Harness(tmp_path)
    receipt = write(h, "write-1")
    backup(h, "backup-1")
    assert coverage(h)["acknowledged_primary_object_count"] == 1
    target = h.primary.root / receipt.namespace_digest / h.ref
    data = target.read_bytes()
    target.write_bytes(data[:-1] + bytes([data[-1] ^ 1]))
    with pytest.raises(IntegrityError):
        write(h, "write-1")
    result = coverage(h)
    assert result["acknowledged_primary_object_count"] == 0
    assert result["uncovered_primary_object_count"] == 0
    assert h.journal.health()["missing_or_corrupt"] == 1


def test_tampered_reservation_cannot_generate_reassuring_coverage(tmp_path):
    h = Harness(tmp_path)
    write(h, "write-1")
    backup(h, "backup-1")
    with sqlite3.connect(h.journal.path) as db:
        db.execute("DROP TRIGGER backup_intents_block_update")
        db.execute("UPDATE backup_intents SET source_ciphertext_sha256=?", ("f" * 64,))
    with pytest.raises(IntegrityError):
        coverage(h)
    with pytest.raises(IntegrityError):
        owner_safe_source_snapshot(h.journal)


def test_no_raw_refs_or_entity_leak_into_coverage_owner_views(tmp_path):
    h = Harness(tmp_path)
    write(h, "write-1")
    snapshot = owner_safe_source_snapshot(h.journal)
    desk = owner_local_evidence_desk(journal=h.journal, replay_store=h.nonces)
    wire = json.dumps([coverage(h), snapshot, desk])
    assert h.ref not in wire
    assert "trust" not in wire
    assert h.digest not in wire
    assert str(h.journal.path) not in wire
