"""SC041 resolver-used namespace coverage versus durable binding registry tests."""
import hashlib
import os
import sqlite3

import pytest

from simplee_cloud.contracts import AccessDenied, IntegrityError, StorageContext
from simplee_cloud.journal import SQLiteOperationalJournal
from simplee_cloud.local_backend import LocalPrivateCiphertextBackend
from simplee_cloud.namespace_bindings import SQLiteNamespaceBindingLedger
from simplee_cloud.namespace_coverage import source_namespace_binding_coverage
from simplee_cloud.operations import JournaledCiphertextOperations
from simplee_cloud.owner_evidence_desk import owner_local_evidence_desk
from simplee_cloud.service import CiphertextStorageService
from simplee_cloud.tower_grants import SQLiteNonceReplayStore


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

    def put_if_absent(self, namespace, ref, body):
        self.put_calls += 1
        return self.actual.put_if_absent(namespace, ref, body)

    def get(self, namespace, ref):
        return self.actual.get(namespace, ref)


def ctx(operation, request, entity="trust"):
    return StorageContext(
        request_id=request, caller_service="archive_vault",
        tower_decision_ref="synthetic-gate", entity_id=entity,
        purpose="archive", operation=operation,
    )


def binding_ledger(tmp_path, name="bindings"):
    return SQLiteNamespaceBindingLedger(
        tmp_path / name / "namespace.sqlite",
        binding_key=b"c" * 32, mode="source_test",
    )


def replay_store(tmp_path):
    return SQLiteNonceReplayStore(
        tmp_path / "replay" / "consumed.sqlite", mode="source_test",
    )


def resolver_stack(tmp_path, mapping, bindings, backend=None):
    journal = SQLiteOperationalJournal(
        tmp_path / "audit" / "operations.sqlite", mode="source_test",
    )
    actual = backend or LocalPrivateCiphertextBackend(tmp_path / "objects")
    service = CiphertextStorageService(
        backend=actual, namespace_resolver=lambda entity: mapping[entity],
        namespace_binding_ledger=bindings,
        authority=Authority(), audit_event=journal.record_safe_event,
        mode="source_test",
    )
    return service, JournaledCiphertextOperations(
        source=service, journal=journal,
    ), journal, actual


def write(ops, service, request, entity="trust"):
    body = b"VLT1" + os.urandom(48)
    digest = hashlib.sha256(body).hexdigest()
    return ops.put_if_absent(
        context=ctx("WRITE_CIPHERTEXT", request, entity),
        object_ref=service.new_object_ref(),
        envelope=body, expected_sha256=digest,
    )


def test_fixed_secret_operations_do_not_create_false_resolver_coverage_requirement(tmp_path):
    journal = SQLiteOperationalJournal(
        tmp_path / "audit" / "ops.sqlite", mode="source_test",
    )
    backend = LocalPrivateCiphertextBackend(tmp_path / "objects")
    service = CiphertextStorageService(
        backend=backend, namespace_key=b"k" * 32,
        authority=Authority(), audit_event=journal.record_safe_event,
        mode="source_test",
    )
    ops = JournaledCiphertextOperations(source=service, journal=journal)
    write(ops, service, "write-fixed")
    bindings = binding_ledger(tmp_path)
    report = source_namespace_binding_coverage(journal, bindings)
    assert report["resolver_namespace_count"] == 0
    assert report["missing_resolver_namespace_count"] == 0
    assert report["status"] == "SOURCE_ONLY_NAMESPACE_BINDING_COVERAGE_VERIFIED"
    assert report["production_authorized"] is False


def test_resolver_backed_write_marks_namespace_and_exact_binding_covers_it(tmp_path):
    mapping = {"trust": "a" * 64}
    bindings = binding_ledger(tmp_path)
    bindings.enroll_source_binding(entity_id="trust", namespace=mapping["trust"])
    service, ops, journal, _ = resolver_stack(
        tmp_path, mapping, bindings,
    )
    write(ops, service, "write-1")
    inventory = journal.source_resolver_namespace_inventory()
    assert inventory["namespace_count"] == 1
    report = source_namespace_binding_coverage(journal, bindings)
    assert report["resolver_namespace_count"] == 1
    assert report["enrolled_namespace_count"] == 1
    assert report["matched_namespace_count"] == 1
    assert report["missing_resolver_namespace_count"] == 0
    assert report["unused_enrolled_namespace_count"] == 0
    assert report["status"] == "SOURCE_ONLY_NAMESPACE_BINDING_COVERAGE_VERIFIED"


def test_recreated_empty_binding_db_becomes_hold_for_existing_resolver_history(tmp_path):
    mapping = {"trust": "a" * 64}
    original = binding_ledger(tmp_path, "original")
    original.enroll_source_binding(entity_id="trust", namespace=mapping["trust"])
    service, ops, journal, _ = resolver_stack(
        tmp_path, mapping, original,
    )
    write(ops, service, "write-1")

    lost_replacement = binding_ledger(tmp_path, "replacement-empty")
    report = source_namespace_binding_coverage(journal, lost_replacement)
    assert report["resolver_namespace_count"] == 1
    assert report["enrolled_namespace_count"] == 0
    assert report["matched_namespace_count"] == 0
    assert report["missing_resolver_namespace_count"] == 1
    assert report["status"] == "SOURCE_ONLY_NAMESPACE_BINDING_HOLD"

    desk = owner_local_evidence_desk(
        journal=journal, replay_store=replay_store(tmp_path),
        namespace_bindings=lost_replacement,
    )
    ready = desk["namespace_binding_readiness"]
    assert ready["status"] == "SOURCE_ONLY_NAMESPACE_BINDING_HOLD"
    assert ready["missing_resolver_namespace_count"] == 1
    assert desk["production_authorized"] is False


def test_partial_registry_counts_missing_namespace_without_exposing_which_one(tmp_path):
    mapping = {"trust": "a" * 64, "other": "b" * 64}
    original = binding_ledger(tmp_path, "original")
    for entity, namespace in mapping.items():
        original.enroll_source_binding(entity_id=entity, namespace=namespace)
    service, ops, journal, _ = resolver_stack(tmp_path, mapping, original)
    write(ops, service, "write-1", "trust")
    write(ops, service, "write-2", "other")

    partial = binding_ledger(tmp_path, "partial")
    partial.enroll_source_binding(entity_id="trust", namespace=mapping["trust"])
    report = source_namespace_binding_coverage(journal, partial)
    assert report["resolver_namespace_count"] == 2
    assert report["enrolled_namespace_count"] == 1
    assert report["matched_namespace_count"] == 1
    assert report["missing_resolver_namespace_count"] == 1
    assert "namespace_digests" not in report
    assert "a" * 64 not in repr(report)
    assert "b" * 64 not in repr(report)


def test_extra_pre_enrolled_unused_namespace_is_not_a_missing_coverage_hold(tmp_path):
    mapping = {"trust": "a" * 64}
    bindings = binding_ledger(tmp_path)
    bindings.enroll_source_binding(entity_id="trust", namespace=mapping["trust"])
    bindings.enroll_source_binding(entity_id="future", namespace="b" * 64)
    service, ops, journal, _ = resolver_stack(tmp_path, mapping, bindings)
    write(ops, service, "write-1")
    report = source_namespace_binding_coverage(journal, bindings)
    assert report["missing_resolver_namespace_count"] == 0
    assert report["unused_enrolled_namespace_count"] == 1
    assert report["status"] == "SOURCE_ONLY_NAMESPACE_BINDING_COVERAGE_VERIFIED"


def test_unenrolled_resolver_denial_emits_no_success_marker_or_provider_put(tmp_path):
    mapping = {"trust": "a" * 64}
    bindings = binding_ledger(tmp_path)
    backend = CountingBackend(LocalPrivateCiphertextBackend(tmp_path / "objects"))
    service, ops, journal, _ = resolver_stack(
        tmp_path, mapping, bindings, backend=backend,
    )
    with pytest.raises(AccessDenied, match="not independently enrolled"):
        write(ops, service, "write-denied")
    assert backend.put_calls == 0
    inventory = journal.source_resolver_namespace_inventory()
    assert inventory["namespace_count"] == 0
    assert journal.health()["write_count"] == 0


def test_journal_or_binding_tamper_blocks_coverage_instead_of_reporting_missing(tmp_path):
    mapping = {"trust": "a" * 64}
    bindings = binding_ledger(tmp_path)
    bindings.enroll_source_binding(entity_id="trust", namespace=mapping["trust"])
    service, ops, journal, _ = resolver_stack(tmp_path, mapping, bindings)
    write(ops, service, "write-1")

    with sqlite3.connect(journal.path) as db:
        db.execute("DROP TRIGGER events_block_update")
        db.execute(
            "UPDATE events SET namespace_digest=? "
            "WHERE event_type='namespace_binding_verified'",
            ("f" * 64,),
        )
    with pytest.raises(IntegrityError):
        source_namespace_binding_coverage(journal, bindings)

    # Independent fresh stack for binding-ledger tamper.
    other_root = tmp_path / "other"
    other_bindings = binding_ledger(other_root)
    other_bindings.enroll_source_binding(entity_id="trust", namespace="a" * 64)
    service2, ops2, journal2, _ = resolver_stack(
        other_root, {"trust": "a" * 64}, other_bindings,
    )
    write(ops2, service2, "write-1")
    with sqlite3.connect(other_bindings.path) as db:
        db.execute("DROP TRIGGER bindings_block_update")
        db.execute("UPDATE bindings SET namespace_digest=?", ("e" * 64,))
    with pytest.raises(IntegrityError):
        source_namespace_binding_coverage(journal2, other_bindings)


def test_owner_coverage_output_contains_counts_only_no_entity_or_namespace_values(tmp_path):
    mapping = {"private-entity-name": "a" * 64}
    bindings = binding_ledger(tmp_path)
    bindings.enroll_source_binding(
        entity_id="private-entity-name", namespace=mapping["private-entity-name"],
    )
    service, ops, journal, _ = resolver_stack(tmp_path, mapping, bindings)
    write(ops, service, "private-request", "private-entity-name")
    desk = owner_local_evidence_desk(
        journal=journal, replay_store=replay_store(tmp_path),
        namespace_bindings=bindings,
    )
    wire = repr(desk)
    assert "private-entity-name" not in wire
    assert "private-request" not in wire
    assert "a" * 64 not in wire
    ready = desk["namespace_binding_readiness"]
    assert ready["resolver_namespace_count"] == 1
    assert ready["matched_namespace_count"] == 1
    assert ready["missing_resolver_namespace_count"] == 0
    assert ready["external_registry_certified"] is False
    assert ready["binding_key_custody_certified"] is False
