"""SC002 focused tests use only synthetic Vault envelopes and test authority."""
import hashlib
import os
import sqlite3
from dataclasses import replace

import pytest

from simplee_cloud.contracts import (
    AccessDenied, CloudError, IntegrityError, ObjectMissing, StorageContext,
)
from simplee_cloud.journal import SQLiteOperationalJournal
from simplee_cloud.local_backend import LocalPrivateCiphertextBackend
from simplee_cloud.operations import JournaledCiphertextOperations
from simplee_cloud.service import CiphertextStorageService


class SyntheticAuthority:
    __test__ = False
    def authorize(self, context, operation):
        if context.tower_decision_ref != "synthetic-gate" or context.operation != operation:
            raise AccessDenied("synthetic Tower grant denied")


class FailBeforeWrite:
    def __init__(self):
        self.objects = {}
        self.calls = 0

    def put_if_absent(self, namespace, ref, body):
        self.calls += 1
        raise OSError("simulated provider unreachable")

    def get(self, namespace, ref):
        raise ObjectMissing("synthetic missing object")


class FailAfterWrite:
    def __init__(self):
        self.objects = {}
        self.calls = 0

    def put_if_absent(self, namespace, ref, body):
        self.calls += 1
        self.objects[(namespace, ref)] = body
        raise OSError("provider accepted object but acknowledgement lost")

    def get(self, namespace, ref):
        try:
            return self.objects[(namespace, ref)]
        except KeyError as exc:
            raise ObjectMissing("not found") from exc


class FailingAckJournal(SQLiteOperationalJournal):
    def transition(self, *, namespace, request_id, next_state):
        if next_state == "WRITE_ACKNOWLEDGED":
            raise OSError("simulated durable journal outage")
        return super().transition(
            namespace=namespace, request_id=request_id, next_state=next_state,
        )


def context(op, request_id="req-1", entity="trust"):
    return StorageContext(
        request_id=request_id, caller_service="archive_vault",
        tower_decision_ref="synthetic-gate", entity_id=entity,
        purpose="synthetic-archival", operation=op,
    )


def setup(tmp_path, backend=None, journal_class=SQLiteOperationalJournal):
    journal = journal_class(tmp_path / "audit" / "operations.sqlite", mode="source_test")
    actual_backend = backend or LocalPrivateCiphertextBackend(tmp_path / "objects")
    source = CiphertextStorageService(
        backend=actual_backend, namespace_key=os.urandom(32),
        authority=SyntheticAuthority(), audit_event=journal.record_safe_event,
        mode="source_test",
    )
    ops = JournaledCiphertextOperations(source=source, journal=journal)
    data = b"VLT1" + os.urandom(48)
    return ops, journal, actual_backend, data, hashlib.sha256(data).hexdigest(), source.new_object_ref()


def write(ops, data, digest, ref, ctx=None):
    return ops.put_if_absent(
        context=ctx or context("WRITE_CIPHERTEXT"), object_ref=ref,
        envelope=data, expected_sha256=digest,
    )


def test_acknowledged_write_is_durable_and_idempotent(tmp_path):
    ops, journal, _, data, digest, ref = setup(tmp_path)
    first = write(ops, data, digest, ref)
    second = write(ops, data, digest, ref)
    assert first == second
    assert ops.get(
        context=context("READ_CIPHERTEXT", request_id="read-1"),
        object_ref=ref, expected_sha256=digest,
    ) == data
    assert journal.intent(
        namespace=first.namespace_digest, request_id="req-1",
    )["state"] == "WRITE_ACKNOWLEDGED"
    assert journal.health()["pending_writes"] == 0
    assert journal.verify_chain()["valid"] is True
    assert ops.health()["production_authorized"] is False
    assert ops.health()["status"] == "SOURCE_ONLY_NO_GO"


def test_idempotency_conflict_and_cross_entity_not_reused(tmp_path):
    ops, journal, _, data, digest, ref = setup(tmp_path)
    first = write(ops, data, digest, ref)
    with pytest.raises(CloudError, match="idempotency conflict"):
        write(ops, data, digest, ops.source.new_object_ref())
    with pytest.raises(ObjectMissing):
        ops.get(
            context=context("READ_CIPHERTEXT", "r2", "other-entity"),
            object_ref=ref, expected_sha256=digest,
        )
    assert journal.health()["incident_count"] == 1
    with pytest.raises(AccessDenied):
        write(ops, data, digest, ops.source.new_object_ref(),
              replace(context("WRITE_CIPHERTEXT", "req-denied"),
                      tower_decision_ref="untrusted"))
    assert first.ciphertext_sha256 == digest


def test_failed_after_provider_acceptance_requires_explicit_reconcile(tmp_path):
    backend = FailAfterWrite()
    ops, journal, _, data, digest, ref = setup(tmp_path, backend)
    with pytest.raises(OSError, match="acknowledgement lost"):
        write(ops, data, digest, ref)
    assert backend.calls == 1
    with pytest.raises(CloudError, match="unresolved"):
        write(ops, data, digest, ref)
    assert backend.calls == 1
    assert journal.health()["pending_writes"] == 1
    assert journal.health()["incident_count"] == 1
    recovered = ops.reconcile_write(
        context=context("RECONCILE_WRITE", "fresh-authorized-reconcile"),
        original_request_id="req-1",
    )
    assert recovered["status"] == "PRESENT_INTERNAL_STORAGE_ONLY"
    assert recovered["vault_archive_committed"] is False
    assert recovered["storage_receipt"].ciphertext_sha256 == digest
    assert journal.health()["pending_writes"] == 0
    assert write(ops, data, digest, ref) == recovered["storage_receipt"]
    assert backend.calls == 1


def test_missing_write_holds_without_auto_retry(tmp_path):
    backend = FailBeforeWrite()
    ops, journal, _, data, digest, ref = setup(tmp_path, backend)
    with pytest.raises(OSError):
        write(ops, data, digest, ref)
    result = ops.reconcile_write(
        context=context("RECONCILE_WRITE", "fresh-reconcile-2"),
        original_request_id="req-1",
    )
    assert result == {
        "status": "MISSING_HOLD", "storage_receipt": None,
        "vault_archive_committed": False,
    }
    with pytest.raises(CloudError, match="unresolved"):
        write(ops, data, digest, ref)
    assert backend.calls == 1
    assert journal.health()["missing_or_corrupt"] == 1


def test_journal_ack_failure_stays_reserved_then_reconciles(tmp_path):
    ops, journal, _, data, digest, ref = setup(tmp_path, journal_class=FailingAckJournal)
    with pytest.raises(OSError, match="journal outage"):
        write(ops, data, digest, ref)
    record = journal.intent(
        namespace=ops.source._gate(context("WRITE_CIPHERTEXT"), "WRITE_CIPHERTEXT"),
        request_id="req-1",
    )
    assert record["state"] == "WRITE_RESERVED"
    result = ops.reconcile_write(
        context=context("RECONCILE_WRITE", "new-reconcile"),
        original_request_id="req-1",
    )
    assert result["status"] == "PRESENT_INTERNAL_STORAGE_ONLY"


def test_tampering_reconcile_and_replay_fail_closed(tmp_path):
    ops, journal, backend, data, digest, ref = setup(tmp_path)
    receipt = write(ops, data, digest, ref)
    object_path = backend.root / receipt.namespace_digest / "objects" / ref.split("/")[1]
    object_path.write_bytes(b"VLT1" + os.urandom(48))
    with pytest.raises(IntegrityError, match="acknowledged"):
        write(ops, data, digest, ref)
    assert journal.health()["missing_or_corrupt"] == 1
    assert journal.health()["incident_count"] == 1
    with pytest.raises(CloudError, match="unresolved"):
        write(ops, data, digest, ref)


def test_uncertain_corruption_is_hold_and_incident(tmp_path):
    backend = FailAfterWrite()
    ops, journal, _, data, digest, ref = setup(tmp_path, backend)
    with pytest.raises(OSError):
        write(ops, data, digest, ref)
    namespace = journal.intent(
        namespace=ops.source._gate(context("WRITE_CIPHERTEXT"), "WRITE_CIPHERTEXT"),
        request_id="req-1",
    )["namespace_digest"]
    backend.objects[(namespace, ref)] = b"VLT1" + os.urandom(48)
    result = ops.reconcile_write(
        context=context("RECONCILE_WRITE", "reconcile-corrupt"),
        original_request_id="req-1",
    )
    assert result["status"] == "CORRUPT_HOLD"
    assert result["storage_receipt"] is None
    assert journal.health()["missing_or_corrupt"] == 1
    assert journal.health()["incident_count"] == 2


def test_append_only_sql_and_chain_detection(tmp_path):
    ops, journal, _, data, digest, ref = setup(tmp_path)
    write(ops, data, digest, ref)
    with sqlite3.connect(journal.path) as conn:
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            conn.execute("DELETE FROM events")
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            conn.execute("UPDATE intents SET ciphertext_size=123")
    # Simulate a hostile administrator able to bypass SQL triggers. Hash
    # verification detects a partial edit but NOT a forged entire DB+head.
    with sqlite3.connect(journal.path) as conn:
        conn.execute("DROP TRIGGER events_block_update")
        conn.execute("UPDATE events SET event_type='FAKE' WHERE seq=1")
    with pytest.raises(IntegrityError, match="integrity"):
        journal.verify_chain()
    with pytest.raises(IntegrityError):
        write(ops, data, digest, ref)


def test_operational_health_never_leaks_object_or_raw_entity(tmp_path):
    ops, journal, _, data, digest, ref = setup(tmp_path)
    write(ops, data, digest, ref)
    health = str(ops.health())
    assert ref not in health
    assert "'trust'" not in health
    assert "synthetic-gate" not in health
    assert journal.health()["external_checkpoint_certified"] is False


def test_journal_or_audit_sink_absence_denies_storage(tmp_path):
    backend = LocalPrivateCiphertextBackend(tmp_path / "storage")
    key = os.urandom(32)
    source = CiphertextStorageService(
        backend=backend, namespace_key=key,
        authority=SyntheticAuthority(), audit_event=lambda _: None,
        mode="source_test",
    )
    journal = SQLiteOperationalJournal(
        tmp_path / "audit" / "operations.sqlite", mode="source_test",
    )
    with pytest.raises(CloudError, match="audit sink"):
        JournaledCiphertextOperations(source=source, journal=journal)
    with pytest.raises(CloudError):
        SQLiteOperationalJournal(tmp_path / "other" / "db.sqlite")
