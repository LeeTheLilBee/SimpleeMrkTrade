"""SC007: exact journal reservation payloads must be chain-committed.

These are local synthetic integrity checks, NOT hostile database administrator
protection, offsite WORM evidence or a live provider guarantee.
"""
import os
import sqlite3

import pytest

from simplee_cloud.contracts import IntegrityError
from simplee_cloud.journal import SQLiteOperationalJournal, _hash_event
from simplee_cloud.tests.test_sc004b_bound_port import Harness, PEER

def seeded(tmp_path):
    h = Harness(tmp_path)
    primary = h.port.write(
        grant=h.grant("write-1", "WRITE_CIPHERTEXT"),
        authenticated_transport_peer=PEER,
        request_id="write-1", envelope=h.data,
    )
    backup = h.port.create_encrypted_backup(
        grant=h.grant("backup-1", "BACKUP_CIPHERTEXT"),
        authenticated_transport_peer=PEER, request_id="backup-1",
    )
    return h, primary, backup


def test_reservation_hash_commits_every_field_and_reopening_works(tmp_path):
    h, primary, backup = seeded(tmp_path)
    with sqlite3.connect(h.journal.path) as db:
        reservations = db.execute(
            "SELECT event_type,code FROM events WHERE event_type IN "
            "('WRITE_RESERVED','BACKUP_RESERVED') ORDER BY seq"
        ).fetchall()
    assert [r[0] for r in reservations] == ["WRITE_RESERVED", "BACKUP_RESERVED"]
    assert all(r[1].startswith("reservation:v2:") and len(r[1]) == len("reservation:v2:") + 64 for r in reservations)
    reopened = SQLiteOperationalJournal(h.journal.path, mode="source_test")
    assert reopened.verify_chain()["head_sha256"] == h.journal.verify_chain()["head_sha256"]
    assert reopened.health()["write_count"] == 1
    assert reopened.health()["backup_count"] == 1
    assert primary.ciphertext_sha256 == h.digest
    assert backup.source_ciphertext_sha256 == h.digest


@pytest.mark.parametrize("table,column,replacement", [
    ("intents", "object_ref", "objects/" + "e" * 48),
    ("intents", "ciphertext_sha256", "0" * 64),
    ("intents", "ciphertext_size", 42),
    ("intents", "created_at", "2000-01-01T00:00:00Z"),
    ("intents", "namespace_digest", "b" * 64),
    ("backup_intents", "source_object_ref", "objects/" + "d" * 48),
    ("backup_intents", "source_ciphertext_sha256", "f" * 64),
    ("backup_intents", "backup_ref", "backups/" + "a" * 48),
    ("backup_intents", "backup_sha256", "f" * 64),
    ("backup_intents", "backup_size", 42),
    ("backup_intents", "key_reference", "other-source-key"),
    ("backup_intents", "created_at", "2000-01-01T00:00:00Z"),
    ("backup_intents", "namespace_digest", "b" * 64),
])
def test_changed_reservation_metadata_without_event_rewrite_fails_closed(tmp_path, table, column, replacement):
    h, _, _ = seeded(tmp_path)
    with sqlite3.connect(h.journal.path) as db:
        # Simulate a privileged tester bypassing append-only triggers. This is
        # precisely the old gap: valid event chain but different object intent.
        db.execute(f"DROP TRIGGER {table}_block_update")
        db.execute(f"UPDATE {table} SET {column}=?", (replacement,))
    with pytest.raises(IntegrityError, match="reserved ciphertext metadata"):
        h.journal.verify_chain()
    with pytest.raises(IntegrityError):
        h.journal.health()
    with pytest.raises(IntegrityError):
        h.journal.checkpoint_head(1)


@pytest.mark.parametrize("table", ["intents", "backup_intents"])
def test_deleted_intent_cannot_leave_plausible_reservation_event(tmp_path, table):
    h, _, _ = seeded(tmp_path)
    with sqlite3.connect(h.journal.path) as db:
        db.execute(f"DROP TRIGGER {table}_block_delete")
        db.execute(f"DELETE FROM {table}")
    with pytest.raises(IntegrityError, match="missing or surplus"):
        h.journal.verify_chain()


@pytest.mark.parametrize("table", ["intents", "backup_intents"])
def test_unsolicited_row_cannot_appear_without_one_reservation_event(tmp_path, table):
    h, _, _ = seeded(tmp_path)
    with sqlite3.connect(h.journal.path) as db:
        cols = [x[1] for x in db.execute("PRAGMA table_info(" + table + ")")]
        record = db.execute("SELECT * FROM " + table + " LIMIT 1").fetchone()
        mutated = list(record)
        mutated[0] = "e" * 64
        db.execute(
            "INSERT INTO " + table + " VALUES (" + ",".join("?" for _ in cols) + ")",
            mutated,
        )
    with pytest.raises(IntegrityError, match="missing or surplus"):
        h.journal.verify_chain()


def test_old_unbound_but_self_consistent_source_journal_is_not_silently_accepted(tmp_path):
    h = Harness(tmp_path)
    h.port.write(
        grant=h.grant("write-1", "WRITE_CIPHERTEXT"),
        authenticated_transport_peer=PEER, request_id="write-1", envelope=h.data,
    )
    # Rewrite only the first reservation event and its own chain hash as though
    # old source_test schema had stored '-' instead of reservation commitment.
    with sqlite3.connect(h.journal.path) as db:
        db.execute("DROP TRIGGER events_block_update")
        first = db.execute(
            "SELECT seq,event_type,request_tag,namespace_digest,created_at,previous_hash "
            "FROM events WHERE event_type='WRITE_RESERVED'"
        ).fetchone()
        digest = _hash_event(first[0], first[1], first[2], first[3], "-", first[4], first[5])
        db.execute(
            "UPDATE events SET code=?,event_hash=? WHERE seq=?", ("-", digest, first[0]),
        )
        # Any subsequent event would have the prior hash changed as well, so
        # this test expects event chain failure OR reservation-v2 failure.
    with pytest.raises(IntegrityError):
        h.journal.verify_chain()
