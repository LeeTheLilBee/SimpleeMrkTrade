"""SC007B: full incident rows, not just event tags, are audit-committed.

Local privileged corruption injections bypass SQLite triggers solely in
synthetic tests; they are not proof against a malicious full journal rewrite.
"""
import sqlite3

import pytest

from simplee_cloud.contracts import IntegrityError
from simplee_cloud.journal import _hash_event
from simplee_cloud.tests.test_sc004b_bound_port import Harness, PEER


def with_incident(tmp_path, *, duplicate=False):
    h = Harness(tmp_path)
    receipt = h.port.write(
        grant=h.grant("write-1", "WRITE_CIPHERTEXT"),
        authenticated_transport_peer=PEER, request_id="write-1", envelope=h.data,
    )
    h.journal.record_read_incident(
        namespace=receipt.namespace_digest, request_id="read-1",
    )
    if duplicate:
        h.journal.record_read_incident(
            namespace=receipt.namespace_digest, request_id="read-1",
        )
    return h


def test_incident_event_contains_full_row_commitment_and_reopen(tmp_path):
    h = with_incident(tmp_path, duplicate=True)
    with sqlite3.connect(h.journal.path) as db:
        rows = db.execute(
            "SELECT event_type,code FROM events WHERE event_type='INCIDENT_RECORDED'"
        ).fetchall()
    assert len(rows) == 2
    assert all(row[1].startswith("incident:v2:") for row in rows)
    assert all(len(row[1]) == len("incident:v2:") + 64 for row in rows)
    assert rows[0][1] != rows[1][1]  # unique incident ID is also committed
    assert h.journal.health()["incident_count"] == 2
    assert h.journal.verify_chain()["valid"] is True
    from simplee_cloud.journal import SQLiteOperationalJournal
    reopened = SQLiteOperationalJournal(h.journal.path, mode="source_test")
    assert reopened.verify_chain()["head_sha256"] == h.journal.verify_chain()["head_sha256"]


@pytest.mark.parametrize("column,value", [
    ("incident_id", "b" * 32),
    ("request_tag", "a" * 64),
    ("incident_code", "BACKUP_INTEGRITY_FAILURE"),
    ("severity", "notice"),
    ("created_at", "2000-01-01T00:00:00Z"),
])
def test_mutated_incident_payload_is_detected_before_future_write(tmp_path, column, value):
    h = with_incident(tmp_path)
    with sqlite3.connect(h.journal.path) as db:
        db.execute("DROP TRIGGER incidents_block_update")
        db.execute(f"UPDATE incidents SET {column}=?", (value,))
    with pytest.raises(IntegrityError, match="incident metadata"):
        h.journal.verify_chain()
    with pytest.raises(IntegrityError):
        h.journal.health()
    with pytest.raises(IntegrityError):
        h.journal.checkpoint_head(1)
    with pytest.raises(IntegrityError):
        h.journal.record_read_incident(
            namespace="a" * 64, request_id="next-read",
        )


def test_deleted_incident_event_still_present_fails_closed(tmp_path):
    h = with_incident(tmp_path)
    with sqlite3.connect(h.journal.path) as db:
        db.execute("DROP TRIGGER incidents_block_delete")
        db.execute("DELETE FROM incidents")
    with pytest.raises(IntegrityError, match="incident metadata"):
        h.journal.verify_chain()


def test_forged_incident_without_event_fails_closed(tmp_path):
    h = with_incident(tmp_path)
    with sqlite3.connect(h.journal.path) as db:
        original = db.execute("SELECT * FROM incidents LIMIT 1").fetchone()
        values = list(original)
        values[0] = "f" * 32
        db.execute("INSERT INTO incidents VALUES(?,?,?,?,?)", values)
    with pytest.raises(IntegrityError, match="incident metadata"):
        h.journal.verify_chain()


def test_syntactically_valid_old_incident_event_code_is_not_silently_accepted(tmp_path):
    h = with_incident(tmp_path)
    with sqlite3.connect(h.journal.path) as db:
        db.execute("DROP TRIGGER events_block_update")
        row = db.execute(
            """SELECT seq,event_type,request_tag,namespace_digest,created_at,
                      previous_hash FROM events WHERE event_type='INCIDENT_RECORDED'"""
        ).fetchone()
        old_code = "READ_INTEGRITY_FAILURE"
        new_hash = _hash_event(
            row[0], row[1], row[2], row[3], old_code, row[4], row[5],
        )
        db.execute(
            "UPDATE events SET code=?,event_hash=? WHERE seq=?",
            (old_code, new_hash, row[0]),
        )
    # The legacy event now has a mathematically consistent individual chain
    # head but fails because its full incident row is not hash-bound.
    with pytest.raises(IntegrityError, match="incident metadata"):
        h.journal.verify_chain()
