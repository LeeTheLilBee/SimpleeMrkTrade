"""SC026: one local verified point-in-time owner storage/backup snapshot."""
from concurrent.futures import ThreadPoolExecutor
from threading import Event
import sqlite3
import time

import pytest

from simplee_cloud.contracts import IntegrityError
from simplee_cloud.journal import SQLiteOperationalJournal
from simplee_cloud.owner_evidence_desk import owner_local_evidence_desk
from simplee_cloud.source_status import owner_safe_source_snapshot
from simplee_cloud.tests.test_sc004b_bound_port import Harness, PEER


def write(h, request="write-1", ref=None):
    return h.port.write(
        grant=h.grant(request, "WRITE_CIPHERTEXT", ref=ref),
        authenticated_transport_peer=PEER, request_id=request, envelope=h.data,
    )


def test_one_verified_journal_snapshot_combines_primary_and_backup_counts(tmp_path):
    h = Harness(tmp_path)
    write(h)
    h.port.create_encrypted_backup(
        grant=h.grant("backup-1", "BACKUP_CIPHERTEXT"),
        authenticated_transport_peer=PEER, request_id="backup-1",
    )
    health, coverage = h.journal.source_owner_metrics()
    assert health == h.journal.health()
    assert coverage == h.journal.source_backup_coverage()
    assert health["write_count"] == 1
    assert health["backup_count"] == 1
    assert coverage["acknowledged_primary_object_count"] == 1
    assert coverage["matched_backup_ack_count"] == 1
    assert coverage["production_authorized"] is False


def test_owner_snapshot_uses_joint_method_not_two_individually_timed_reads(tmp_path):
    h = Harness(tmp_path)
    write(h)

    def wrong_path():
        raise AssertionError("owner snapshot must not make separately timed metrics reads")

    h.journal.health = wrong_path
    h.journal.source_backup_coverage = wrong_path
    report = owner_safe_source_snapshot(h.journal)
    assert report["local_storage_point_in_time_consistent"] is True
    assert report["cross_ledger_point_in_time_certified"] is False
    assert report["primary_write_count"] == 1
    assert report["acknowledged_primary_object_count"] == 1
    desk = owner_local_evidence_desk(
        journal=h.journal, replay_store=h.nonces,
    )
    assert desk["local_storage"]["local_storage_point_in_time_consistent"] is True
    assert desk["cross_ledger_point_in_time_certified"] is False
    assert desk["production_authorized"] is False


def test_writer_attempt_during_owner_aggregate_cannot_split_one_local_snapshot(
    tmp_path, monkeypatch,
):
    h = Harness(tmp_path)
    write(h)
    newer_ref = h.source.new_object_ref()
    signed = h.grant("write-2", "WRITE_CIPHERTEXT", ref=newer_ref)
    writer_started = Event()
    original = SQLiteOperationalJournal._source_backup_coverage
    futures = []

    def another_write():
        writer_started.set()
        return h.port.write(
            grant=signed, authenticated_transport_peer=PEER,
            request_id="write-2", envelope=h.data,
        )

    with ThreadPoolExecutor(max_workers=1) as pool:
        def intercept(conn):
            futures.append(pool.submit(another_write))
            assert writer_started.wait(timeout=2)
            # The writer may reserve but cannot commit while our read
            # transaction still holds its original snapshot.
            time.sleep(0.05)
            return original(conn)

        monkeypatch.setattr(
            SQLiteOperationalJournal, "_source_backup_coverage",
            staticmethod(intercept),
        )
        snapshot = owner_safe_source_snapshot(h.journal)
        assert snapshot["primary_write_count"] == 1
        assert snapshot["acknowledged_primary_object_count"] == 1
        assert snapshot["uncovered_primary_object_count"] == 1
        assert snapshot["local_storage_point_in_time_consistent"] is True
        futures[0].result(timeout=10)
    monkeypatch.setattr(
        SQLiteOperationalJournal, "_source_backup_coverage",
        staticmethod(original),
    )
    after = owner_safe_source_snapshot(h.journal)
    assert after["primary_write_count"] == 2
    assert after["acknowledged_primary_object_count"] == 2
    assert after["uncovered_primary_object_count"] == 2


def test_tampered_audit_chain_denies_entire_owner_snapshot_not_partially_readable(tmp_path):
    h = Harness(tmp_path)
    write(h)
    with sqlite3.connect(h.journal.path) as db:
        db.execute("DROP TRIGGER intents_block_update")
        db.execute("UPDATE intents SET ciphertext_sha256=?", ("0" * 64,))
    with pytest.raises(IntegrityError):
        h.journal.source_owner_metrics()
    with pytest.raises(IntegrityError):
        owner_safe_source_snapshot(h.journal)
    with pytest.raises(IntegrityError):
        owner_local_evidence_desk(journal=h.journal, replay_store=h.nonces)


def test_empty_source_report_stays_no_go_even_with_consistent_local_snapshot(tmp_path):
    h = Harness(tmp_path)
    report = owner_safe_source_snapshot(h.journal)
    assert report["attention"] == "NO_LOCAL_SOURCE_FLAGS"
    assert report["local_storage_point_in_time_consistent"] is True
    assert report["cross_ledger_point_in_time_certified"] is False
    assert report["live_provider_health_verified"] is False
    assert report["production_authorized"] is False
