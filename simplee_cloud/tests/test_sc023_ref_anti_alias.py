"""SC023: one physical object key per logical write/backup in each namespace."""
import hashlib
import os
import sqlite3
from concurrent.futures import ThreadPoolExecutor

import pytest

from simplee_cloud.contracts import CloudError, IntegrityError
from simplee_cloud.journal import SQLiteOperationalJournal
from simplee_cloud.tests.test_sc004b_bound_port import Harness, PEER


def write(h, request, *, entity="trust", ref=None):
    return h.port.write(
        grant=h.grant(request, "WRITE_CIPHERTEXT", ref=ref, entity=entity),
        authenticated_transport_peer=PEER, request_id=request, envelope=h.data,
    )


def namespace(h, entity="trust"):
    from simplee_cloud.service import namespace_digest
    return namespace_digest(entity, namespace_key=h.source._namespace_key)


def test_different_requests_cannot_alias_same_primary_ref_or_use_reconcile_to_claim_it(tmp_path):
    h = Harness(tmp_path)
    first = write(h, "write-1")
    with pytest.raises(CloudError, match="already reserved to another request"):
        write(h, "write-2")
    assert h.journal.health()["write_count"] == 1
    assert h.journal.verify_chain()["valid"] is True
    with pytest.raises(CloudError, match="unknown write intent"):
        h.journal.intent(namespace=first.namespace_digest, request_id="write-2")


def test_same_original_request_replay_is_still_exactly_idempotent(tmp_path):
    h = Harness(tmp_path)
    original = write(h, "write-1")
    assert write(h, "write-1") == original
    assert h.journal.health()["write_count"] == 1
    assert h.journal.verify_chain()["valid"] is True


def test_identical_ref_is_allowed_in_independently_namespaced_entities(tmp_path):
    h = Harness(tmp_path)
    trust = write(h, "trust-write", entity="trust")
    another = write(h, "other-write", entity="different-entity")
    assert trust.object_ref == another.object_ref == h.ref
    assert trust.namespace_digest != another.namespace_digest
    assert h.journal.health()["write_count"] == 2
    assert h.journal.verify_chain()["valid"] is True


def test_two_distinct_primary_refs_in_one_namespace_allowed(tmp_path):
    h = Harness(tmp_path)
    first = write(h, "write-1")
    second = write(h, "write-2", ref=h.source.new_object_ref())
    assert first.object_ref != second.object_ref
    assert h.journal.health()["write_count"] == 2


def test_different_backup_requests_cannot_alias_same_backup_ref(tmp_path):
    h = Harness(tmp_path)
    write(h, "write-1")
    scope = namespace(h)
    ref = "backups/" + "a" * 48
    digest = hashlib.sha256(b"SCB1" + os.urandom(64)).hexdigest()
    kwargs = dict(
        namespace=scope, source_object_ref=h.ref, source_digest=h.digest,
        backup_ref=ref, backup_digest=digest, backup_size=68,
        key_reference="synthetic-key",
    )
    h.journal.reserve_backup(request_id="backup-1", **kwargs)
    with pytest.raises(CloudError, match="already reserved to another request"):
        h.journal.reserve_backup(request_id="backup-2", **kwargs)
    assert h.journal.health()["backup_count"] == 1
    assert h.journal.verify_chain()["valid"] is True


def test_backup_ref_can_repeat_across_different_namespace(tmp_path):
    h = Harness(tmp_path)
    write(h, "write-trust", entity="trust")
    write(h, "write-other", entity="different-entity")
    ref = "backups/" + "a" * 48
    digest = hashlib.sha256(b"SCB1" + os.urandom(64)).hexdigest()
    for request, entity in (("backup-1", "trust"), ("backup-2", "different-entity")):
        h.journal.reserve_backup(
            namespace=namespace(h, entity), request_id=request,
            source_object_ref=h.ref, source_digest=h.digest,
            backup_ref=ref, backup_digest=digest, backup_size=68,
            key_reference="synthetic-key",
        )
    assert h.journal.health()["backup_count"] == 2
    assert h.journal.verify_chain()["valid"] is True


def test_concurrent_distinct_write_requests_same_ref_only_one_reserves(tmp_path):
    h = Harness(tmp_path)
    def work(i):
        try:
            return "ok", write(h, f"write-{i}")
        except CloudError as exc:
            return "blocked", str(exc)
    with ThreadPoolExecutor(max_workers=6) as pool:
        outcomes = list(pool.map(work, range(6)))
    assert len([one for state, one in outcomes if state == "ok"]) == 1
    assert len([one for state, one in outcomes if state == "blocked"]) == 5
    assert h.journal.health()["write_count"] == 1


def test_privileged_duplicate_insertion_after_dropping_index_is_detected(tmp_path):
    h = Harness(tmp_path)
    receipt = write(h, "write-1")
    with sqlite3.connect(h.journal.path) as db:
        db.execute("DROP INDEX unique_primary_ref")
        row = db.execute("SELECT * FROM intents LIMIT 1").fetchone()
        duplicate = list(row)
        duplicate[0] = "f" * 64
        db.execute("INSERT INTO intents VALUES(?,?,?,?,?,?)", duplicate)
    with pytest.raises(IntegrityError):
        h.journal.verify_chain()


def test_existing_aliased_source_database_fails_at_constructor_not_silent_migration(tmp_path):
    h = Harness(tmp_path)
    write(h, "write-1")
    with sqlite3.connect(h.journal.path) as db:
        db.execute("DROP INDEX unique_primary_ref")
        row = db.execute("SELECT * FROM intents LIMIT 1").fetchone()
        another = list(row)
        another[0] = "f" * 64
        db.execute("INSERT INTO intents VALUES(?,?,?,?,?,?)", another)
    with pytest.raises(IntegrityError, match="aliased physical"):
        SQLiteOperationalJournal(h.journal.path, mode="source_test")
