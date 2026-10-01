"""SC038 durable redacted namespace binding and restart split-write defenses."""
import hashlib
import os
import sqlite3
from concurrent.futures import ThreadPoolExecutor

import pytest

from simplee_cloud.contracts import AccessDenied, CloudError, IntegrityError, StorageContext
from simplee_cloud.journal import SQLiteOperationalJournal
from simplee_cloud.local_backend import LocalPrivateCiphertextBackend
from simplee_cloud.namespace_bindings import SQLiteNamespaceBindingLedger
from simplee_cloud.operations import JournaledCiphertextOperations
from simplee_cloud.service import CiphertextStorageService


KEY = b"b" * 32


class Authority:
    def authorize(self, context, operation):
        if (
            context.caller_service != "archive_vault" or
            context.tower_decision_ref != "synthetic-gate" or
            context.operation != operation
        ):
            raise AccessDenied("synthetic authority denied")


class CountingBackend:
    def __init__(self, actual):
        self.actual = actual
        self.put_calls = 0
        self.get_calls = 0

    def put_if_absent(self, namespace, ref, body):
        self.put_calls += 1
        return self.actual.put_if_absent(namespace, ref, body)

    def get(self, namespace, ref):
        self.get_calls += 1
        return self.actual.get(namespace, ref)


def ctx(operation, request, entity="trust"):
    return StorageContext(
        request_id=request, caller_service="archive_vault",
        tower_decision_ref="synthetic-gate", entity_id=entity,
        purpose="archive", operation=operation,
    )


def ledger(tmp_path, key=KEY):
    return SQLiteNamespaceBindingLedger(
        tmp_path / "namespace" / "bindings.sqlite",
        binding_key=key, mode="source_test",
    )


def service(tmp_path, *, namespace, binding, backend=None):
    actual = backend or LocalPrivateCiphertextBackend(tmp_path / "objects")
    journal = SQLiteOperationalJournal(
        tmp_path / "audit" / "operations.sqlite", mode="source_test",
    )
    svc = CiphertextStorageService(
        backend=actual, namespace_resolver=lambda entity: namespace,
        namespace_binding_ledger=binding,
        authority=Authority(), audit_event=journal.record_safe_event,
        mode="source_test",
    )
    return svc, JournaledCiphertextOperations(source=svc, journal=journal), journal, actual


def envelope():
    body = b"VLT1" + os.urandom(48)
    return body, hashlib.sha256(body).hexdigest()


def test_binding_persists_across_ledger_reopen_without_raw_entity(tmp_path):
    first = ledger(tmp_path)
    namespace = "a" * 64
    assert first.enroll_source_binding(entity_id="trust", namespace=namespace) == namespace
    report = first.verify_chain()
    assert report["valid"] is True
    assert report["binding_count"] == 1
    assert report["event_count"] == 1
    assert report["raw_entity_ids_persisted"] is False
    reopened = ledger(tmp_path)
    assert reopened.require_binding(entity_id="trust", namespace=namespace) == namespace
    assert reopened.verify_chain()["head_sha256"] == report["head_sha256"]
    with sqlite3.connect(first.path) as db:
        wire = repr(db.execute("SELECT * FROM bindings").fetchall()) + repr(
            db.execute("SELECT * FROM binding_events").fetchall()
        )
    assert "trust" not in wire


def test_enrollment_is_idempotent_but_drift_and_collision_fail_closed(tmp_path):
    bindings = ledger(tmp_path)
    namespace = "a" * 64
    assert bindings.enroll_source_binding(entity_id="trust", namespace=namespace) == namespace
    assert bindings.enroll_source_binding(entity_id="trust", namespace=namespace) == namespace
    assert bindings.verify_chain()["binding_count"] == 1
    with pytest.raises(AccessDenied, match="binding drift"):
        bindings.enroll_source_binding(entity_id="trust", namespace="b" * 64)
    with pytest.raises(AccessDenied, match="another entity"):
        bindings.enroll_source_binding(entity_id="different-entity", namespace=namespace)


def test_wrong_binding_key_after_restart_cannot_claim_existing_namespace(tmp_path):
    original = ledger(tmp_path, KEY)
    namespace = "a" * 64
    original.enroll_source_binding(entity_id="trust", namespace=namespace)
    wrong = ledger(tmp_path, b"x" * 32)
    with pytest.raises(AccessDenied, match="key/entity mismatch"):
        wrong.require_binding(entity_id="trust", namespace=namespace)
    assert wrong.verify_chain()["valid"] is True
    assert wrong.verify_chain()["binding_key_custody_certified"] is False


@pytest.mark.parametrize("table,column,value", [
    ("bindings", "namespace_digest", "b" * 64),
    ("bindings", "created_at", "2000-01-01T00:00:00Z"),
    ("binding_events", "namespace_digest", "b" * 64),
    ("binding_events", "event_hash", "f" * 64),
])
def test_trigger_bypassed_binding_or_event_tamper_is_detected(tmp_path, table, column, value):
    bindings = ledger(tmp_path)
    bindings.enroll_source_binding(entity_id="trust", namespace="a" * 64)
    with sqlite3.connect(bindings.path) as db:
        db.execute(f"DROP TRIGGER {table}_block_update")
        db.execute(f"UPDATE {table} SET {column}=?", (value,))
    with pytest.raises(IntegrityError):
        bindings.verify_chain()
    with pytest.raises(IntegrityError):
        bindings.require_binding(entity_id="trust", namespace="a" * 64)


def test_missing_event_or_forged_binding_row_is_detected(tmp_path):
    bindings = ledger(tmp_path)
    bindings.enroll_source_binding(entity_id="trust", namespace="a" * 64)
    with sqlite3.connect(bindings.path) as db:
        db.execute("DROP TRIGGER binding_events_block_delete")
        db.execute("DELETE FROM binding_events")
    with pytest.raises(IntegrityError, match="rows differ"):
        bindings.verify_chain()

    other = ledger(tmp_path / "other")
    with sqlite3.connect(other.path) as db:
        db.execute(
            "INSERT INTO bindings VALUES(?,?,?)",
            ("f" * 64, "c" * 64, "2000-01-01T00:00:00Z"),
        )
    with pytest.raises(IntegrityError, match="rows differ"):
        other.verify_chain()


def test_concurrent_conflicting_enrollment_serializes_one_mapping(tmp_path):
    bindings = ledger(tmp_path)
    namespaces = [f"{i:064x}" for i in range(1, 7)]

    def work(ns):
        try:
            bindings.enroll_source_binding(entity_id="trust", namespace=ns)
            return "ok", ns
        except AccessDenied:
            return "blocked", ns

    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(work, namespaces))
    assert len([r for r in results if r[0] == "ok"]) == 1
    assert len([r for r in results if r[0] == "blocked"]) == 5
    assert bindings.verify_chain()["binding_count"] == 1
    assert bindings.verify_chain()["event_count"] == 1


def test_wrong_resolver_after_restart_cannot_split_new_write_namespace(tmp_path):
    namespace = "a" * 64
    bindings = ledger(tmp_path)
    bindings.enroll_source_binding(entity_id="trust", namespace=namespace)
    backend = CountingBackend(LocalPrivateCiphertextBackend(tmp_path / "objects"))
    svc1, ops1, journal, _ = service(
        tmp_path, namespace=namespace, binding=bindings, backend=backend,
    )
    data, digest = envelope()
    ref1 = svc1.new_object_ref()
    ops1.put_if_absent(
        context=ctx("WRITE_CIPHERTEXT", "write-1"),
        object_ref=ref1, envelope=data, expected_sha256=digest,
    )
    assert backend.put_calls == 1

    # New process, same durable ledgers, wrong resolver. The dangerous case is
    # a brand-new ref: journal provenance alone could not protect it.
    wrong = CiphertextStorageService(
        backend=backend, namespace_resolver=lambda entity: "b" * 64,
        namespace_binding_ledger=bindings,
        authority=Authority(), audit_event=journal.record_safe_event,
        mode="source_test",
    )
    ops2 = JournaledCiphertextOperations(source=wrong, journal=journal)
    with pytest.raises(AccessDenied, match="stable namespace binding mismatch"):
        ops2.put_if_absent(
            context=ctx("WRITE_CIPHERTEXT", "write-after-wrong-restart"),
            object_ref=wrong.new_object_ref(), envelope=data,
            expected_sha256=digest,
        )
    assert backend.put_calls == 1
    assert journal.health()["write_count"] == 1


def test_unenrolled_resolver_mapping_denied_before_provider_or_journal(tmp_path):
    bindings = ledger(tmp_path)
    backend = CountingBackend(LocalPrivateCiphertextBackend(tmp_path / "objects"))
    _, ops, journal, _ = service(
        tmp_path, namespace="a" * 64, binding=bindings, backend=backend,
    )
    data, digest = envelope()
    with pytest.raises(AccessDenied, match="not independently enrolled"):
        ops.put_if_absent(
            context=ctx("WRITE_CIPHERTEXT", "write-1"),
            object_ref=CiphertextStorageService.new_object_ref(),
            envelope=data, expected_sha256=digest,
        )
    assert backend.put_calls == 0
    assert journal.health()["write_count"] == 0


def test_binding_ledger_has_no_live_mode_or_false_external_certification(tmp_path):
    with pytest.raises(CloudError, match="live namespace binding registry disabled"):
        SQLiteNamespaceBindingLedger(
            tmp_path / "live.sqlite", binding_key=KEY,
        )
    bindings = ledger(tmp_path)
    report = bindings.verify_chain()
    assert report["external_registry_certified"] is False
    assert report["binding_key_custody_certified"] is False
    assert report["production_authorized"] is False
