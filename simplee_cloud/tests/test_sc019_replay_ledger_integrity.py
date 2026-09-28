"""SC019 tamper-evident one-use Tower grant replay source ledger tests.

This only protects the local source-test ledger from partial/accidental or
trigger-bypassed mutation. It is NOT independent multi-host replay state,
external WORM, HSM/KMS custody, or proof against full database rewrite.
"""
import sqlite3
from concurrent.futures import ThreadPoolExecutor

import pytest

from simplee_cloud.contracts import AccessDenied, CloudError
from simplee_cloud.tests.test_sc004b_bound_port import Harness, PEER
from simplee_cloud.tower_grants import SQLiteNonceReplayStore


def store(tmp_path):
    return SQLiteNonceReplayStore(
        tmp_path / "replay" / "consumed.sqlite", mode="source_test",
    )


def consume(s, suffix, expiry=2_000_000_030):
    nonce = f"{suffix:032x}"
    s.consume("synthetic-key", nonce, expiry)
    return nonce


def test_consumption_row_and_event_chain_are_atomic_and_reopenable(tmp_path):
    s = store(tmp_path)
    consume(s, 1)
    consume(s, 2, expiry=2_000_000_031)
    report = s.verify_chain()
    assert report["valid"] is True
    assert report["consumed_count"] == 2
    assert report["event_count"] == 2
    assert len(report["head_sha256"]) == 64
    assert report["external_checkpoint_certified"] is False
    assert report["production_authorized"] is False
    reopened = SQLiteNonceReplayStore(s.path, mode="source_test")
    assert reopened.verify_chain() == report
    assert reopened.count() == 2


def test_duplicate_nonce_still_denied_without_new_event(tmp_path):
    s = store(tmp_path)
    nonce = consume(s, 1)
    with pytest.raises(AccessDenied, match="already consumed"):
        s.consume("synthetic-key", nonce, 2_000_000_030)
    assert s.count() == 1
    assert s.verify_chain()["event_count"] == 1


@pytest.mark.parametrize("column,value", [
    ("nonce_tag", "f" * 64),
    ("expires_at", 2_000_000_999),
])
def test_mutated_consumed_row_is_detected_before_any_future_consume(
    tmp_path, column, value,
):
    s = store(tmp_path)
    consume(s, 1)
    with sqlite3.connect(s.path) as db:
        db.execute("DROP TRIGGER consumed_block_update")
        db.execute(f"UPDATE consumed SET {column}=?", (value,))
    with pytest.raises(AccessDenied, match="replay rows differ"):
        s.verify_chain()
    with pytest.raises(AccessDenied):
        s.count()
    with pytest.raises(AccessDenied):
        consume(s, 2)


def test_deleted_consumption_or_inserted_orphan_is_detected(tmp_path):
    s = store(tmp_path)
    consume(s, 1)
    with sqlite3.connect(s.path) as db:
        db.execute("DROP TRIGGER consumed_block_delete")
        db.execute("DELETE FROM consumed")
    with pytest.raises(AccessDenied, match="replay rows differ"):
        s.verify_chain()

    other = store(tmp_path / "other")
    with sqlite3.connect(other.path) as db:
        db.execute(
            "INSERT INTO consumed VALUES (?,?)",
            ("a" * 64, 2_000_000_030),
        )
    with pytest.raises(AccessDenied, match="replay rows differ"):
        other.verify_chain()


@pytest.mark.parametrize("field,value", [
    ("nonce_tag", "e" * 64),
    ("expires_at", 2_000_001_111),
    ("previous_hash", "f" * 64),
    ("event_hash", "a" * 64),
])
def test_mutated_replay_event_breaks_chain_or_row_binding(tmp_path, field, value):
    s = store(tmp_path)
    consume(s, 1)
    with sqlite3.connect(s.path) as db:
        db.execute("DROP TRIGGER replay_events_block_update")
        db.execute(f"UPDATE replay_events SET {field}=?", (value,))
    with pytest.raises(AccessDenied):
        s.verify_chain()


def test_missing_event_for_existing_consumption_is_detected(tmp_path):
    s = store(tmp_path)
    consume(s, 1)
    with sqlite3.connect(s.path) as db:
        db.execute("DROP TRIGGER replay_events_block_delete")
        db.execute("DELETE FROM replay_events")
    with pytest.raises(AccessDenied, match="replay rows differ"):
        s.verify_chain()


def test_old_unbound_source_test_database_is_not_silently_trusted(tmp_path):
    path = tmp_path / "legacy" / "consumed.sqlite"
    path.parent.mkdir(parents=True, mode=0o700)
    with sqlite3.connect(path) as db:
        db.execute(
            "CREATE TABLE consumed(nonce_tag TEXT PRIMARY KEY, expires_at INTEGER NOT NULL)"
        )
        db.execute(
            "INSERT INTO consumed VALUES (?,?)",
            ("b" * 64, 2_000_000_030),
        )
    path.chmod(0o600)
    s = SQLiteNonceReplayStore(path, mode="source_test")
    with pytest.raises(AccessDenied, match="replay rows differ"):
        s.count()


def test_concurrent_unique_nonce_consumption_serializes_into_one_valid_chain(tmp_path):
    s = store(tmp_path)

    def work(i):
        consume(s, i + 1)
        return True

    with ThreadPoolExecutor(max_workers=8) as pool:
        assert all(pool.map(work, range(8)))
    report = s.verify_chain()
    assert report["consumed_count"] == 8
    assert report["event_count"] == 8
    assert s.count() == 8


def test_replay_ledger_tamper_blocks_later_signed_cloud_operation_before_provider(tmp_path):
    h = Harness(tmp_path / "harness")
    h.port.write(
        grant=h.grant("write-1", "WRITE_CIPHERTEXT"),
        authenticated_transport_peer=PEER,
        request_id="write-1", envelope=h.data,
    )
    with sqlite3.connect(h.nonces.path) as db:
        db.execute("DROP TRIGGER consumed_block_update")
        db.execute("UPDATE consumed SET expires_at=expires_at+1")

    class MustNeverRead:
        get_calls = 0
        def get(self, namespace, ref):
            self.get_calls += 1
            raise AssertionError("provider must not be read after replay-ledger tamper")

    backend = MustNeverRead()
    h.source._backend = backend
    with pytest.raises(AccessDenied, match="replay rows differ"):
        h.port.read_encrypted(
            grant=h.grant("read-2", "READ_CIPHERTEXT"),
            authenticated_transport_peer=PEER,
            request_id="read-2",
        )
    assert backend.get_calls == 0


def test_live_replay_store_stays_disabled(tmp_path):
    with pytest.raises(CloudError, match="live replay store disabled"):
        SQLiteNonceReplayStore(tmp_path / "no-live.sqlite")
