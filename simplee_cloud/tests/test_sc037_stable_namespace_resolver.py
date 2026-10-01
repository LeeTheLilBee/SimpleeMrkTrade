"""SC037/SC038 stable opaque namespace resolver and durable binding tests."""
import hashlib
import os
import sqlite3

import pytest

from simplee_cloud.contracts import AccessDenied, CloudError, StorageContext
from simplee_cloud.journal import SQLiteOperationalJournal
from simplee_cloud.local_backend import LocalPrivateCiphertextBackend
from simplee_cloud.namespace_bindings import SQLiteNamespaceBindingLedger
from simplee_cloud.operations import JournaledCiphertextOperations
from simplee_cloud.service import CiphertextStorageService, namespace_digest


class Authority:
    def authorize(self, context, operation):
        if (
            context.caller_service != "archive_vault" or
            context.tower_decision_ref != "synthetic-gate" or
            context.operation != operation
        ):
            raise AccessDenied("synthetic authority denied")


class CountGet:
    def __init__(self, actual):
        self.actual = actual
        self.get_calls = 0
        self.put_calls = 0

    def get(self, namespace, ref):
        self.get_calls += 1
        return self.actual.get(namespace, ref)

    def put_if_absent(self, namespace, ref, body):
        self.put_calls += 1
        return self.actual.put_if_absent(namespace, ref, body)


BINDING_KEY = b"n" * 32


def ctx(operation, request, entity="trust"):
    return StorageContext(
        request_id=request, caller_service="archive_vault",
        tower_decision_ref="synthetic-gate", entity_id=entity,
        purpose="archive", operation=operation,
    )


def binding_ledger(journal):
    return SQLiteNamespaceBindingLedger(
        journal.path.parent / "namespace-bindings.sqlite",
        binding_key=BINDING_KEY, mode="source_test",
    )


def source(*, backend, journal, key=None, resolver=None, ledger=None):
    service = CiphertextStorageService(
        backend=backend, namespace_key=key, namespace_resolver=resolver,
        namespace_binding_ledger=ledger,
        authority=Authority(), audit_event=journal.record_safe_event,
        mode="source_test",
    )
    return service, JournaledCiphertextOperations(
        source=service, journal=journal,
    )


def prepared(tmp_path):
    backend = LocalPrivateCiphertextBackend(tmp_path / "objects")
    journal = SQLiteOperationalJournal(
        tmp_path / "audit" / "ops.sqlite", mode="source_test",
    )
    data = b"VLT1" + os.urandom(48)
    digest = hashlib.sha256(data).hexdigest()
    ref = CiphertextStorageService.new_object_ref()
    return backend, journal, data, digest, ref


def test_external_stable_namespace_survives_service_reconstruction_without_namespace_secret(tmp_path):
    backend, journal, data, digest, ref = prepared(tmp_path)
    old_key = b"a" * 32
    stable = {
        "trust": namespace_digest("trust", namespace_key=old_key),
    }
    resolver = lambda entity: stable[entity]
    ledger = binding_ledger(journal)
    ledger.enroll_source_binding(entity_id="trust", namespace=stable["trust"])
    first, ops1 = source(
        backend=backend, journal=journal, resolver=resolver, ledger=ledger,
    )
    receipt = ops1.put_if_absent(
        context=ctx("WRITE_CIPHERTEXT", "write-1"),
        object_ref=ref, envelope=data, expected_sha256=digest,
    )
    assert receipt.namespace_digest == stable["trust"]

    second, ops2 = source(
        backend=backend, journal=journal, resolver=resolver, ledger=ledger,
    )
    assert ops2.get(
        context=ctx("READ_CIPHERTEXT", "read-1"),
        object_ref=ref, expected_sha256=digest,
    ) == data
    assert second.health()["source_stable_namespace_resolver_injected"] is True
    assert second.health()["source_namespace_binding_ledger_verified"] is True
    assert second.health()["namespace_rotation_custody_certified"] is False
    assert second.health()["production_authorized"] is False


def test_naive_fixed_namespace_key_rotation_cannot_silently_claim_old_object(tmp_path):
    backend, journal, data, digest, ref = prepared(tmp_path)
    key1 = b"a" * 32
    key2 = b"b" * 32
    assert namespace_digest("trust", namespace_key=key1) != namespace_digest(
        "trust", namespace_key=key2,
    )
    first, ops1 = source(backend=backend, journal=journal, key=key1)
    ops1.put_if_absent(
        context=ctx("WRITE_CIPHERTEXT", "write-1"),
        object_ref=ref, envelope=data, expected_sha256=digest,
    )
    spy = CountGet(backend)
    _, ops2 = source(backend=spy, journal=journal, key=key2)
    with pytest.raises(CloudError, match="acknowledged matching primary intent"):
        ops2.get(
            context=ctx("READ_CIPHERTEXT", "read-after-naive-rotation"),
            object_ref=ref, expected_sha256=digest,
        )
    assert spy.get_calls == 0


def test_stable_resolver_mapping_drift_in_same_process_denied_before_provider(tmp_path):
    backend, journal, data, digest, ref = prepared(tmp_path)
    mapping = {"trust": "a" * 64}
    resolver = lambda entity: mapping[entity]
    ledger = binding_ledger(journal)
    ledger.enroll_source_binding(entity_id="trust", namespace="a" * 64)
    service, ops = source(
        backend=backend, journal=journal, resolver=resolver, ledger=ledger,
    )
    ops.put_if_absent(
        context=ctx("WRITE_CIPHERTEXT", "write-1"),
        object_ref=ref, envelope=data, expected_sha256=digest,
    )
    mapping["trust"] = "b" * 64
    spy = CountGet(backend)
    service._backend = spy
    with pytest.raises(AccessDenied, match="stable namespace binding mismatch"):
        ops.get(
            context=ctx("READ_CIPHERTEXT", "read-drift"),
            object_ref=ref, expected_sha256=digest,
        )
    assert spy.get_calls == 0


def test_stable_resolver_collision_between_entities_denied_in_process(tmp_path):
    backend, journal, data, digest, ref = prepared(tmp_path)
    same = "a" * 64
    resolver = lambda entity: same
    ledger = binding_ledger(journal)
    ledger.enroll_source_binding(entity_id="trust", namespace=same)
    service, ops = source(
        backend=backend, journal=journal, resolver=resolver, ledger=ledger,
    )
    ops.put_if_absent(
        context=ctx("WRITE_CIPHERTEXT", "write-trust", "trust"),
        object_ref=ref, envelope=data, expected_sha256=digest,
    )
    spy = CountGet(backend)
    service._backend = spy
    with pytest.raises(AccessDenied, match="binding key/entity mismatch"):
        service.get(
            context=ctx("READ_CIPHERTEXT", "read-other", "different-entity"),
            object_ref=ref, expected_sha256=digest,
        )
    assert spy.get_calls == 0


def test_resolver_unavailable_or_malformed_denied_before_provider(tmp_path):
    backend, journal, data, digest, ref = prepared(tmp_path)
    spy = CountGet(backend)
    ledger = binding_ledger(journal)
    ledger.enroll_source_binding(entity_id="trust", namespace="a" * 64)

    unavailable, _ = source(
        backend=spy, journal=journal,
        resolver=lambda entity: (_ for _ in ()).throw(OSError("secret outage")),
        ledger=ledger,
    )
    with pytest.raises(AccessDenied, match="stable namespace unavailable"):
        unavailable.get(
            context=ctx("READ_CIPHERTEXT", "read-offline"),
            object_ref=ref, expected_sha256=digest,
        )
    assert spy.get_calls == 0

    malformed, _ = source(
        backend=spy, journal=journal,
        resolver=lambda entity: "NOT-A-NAMESPACE",
        ledger=ledger,
    )
    with pytest.raises(AccessDenied, match="invalid trusted stable namespace"):
        malformed.get(
            context=ctx("READ_CIPHERTEXT", "read-malformed"),
            object_ref=ref, expected_sha256=digest,
        )
    assert spy.get_calls == 0


def test_constructor_requires_exactly_one_namespace_strategy(tmp_path):
    backend = LocalPrivateCiphertextBackend(tmp_path / "objects")
    with pytest.raises(CloudError, match="namespace secret or stable resolver"):
        CiphertextStorageService(backend=backend, mode="source_test")

    ledger = SQLiteNamespaceBindingLedger(
        tmp_path / "bindings" / "namespace.sqlite",
        binding_key=BINDING_KEY, mode="source_test",
    )
    with pytest.raises(CloudError, match="durable redacted binding ledger"):
        CiphertextStorageService(
            backend=backend, namespace_resolver=lambda entity: "a" * 64,
            mode="source_test",
        )
    with pytest.raises(CloudError, match="either namespace secret or stable resolver"):
        CiphertextStorageService(
            backend=backend, namespace_key=b"a" * 32,
            namespace_resolver=lambda entity: "a" * 64,
            namespace_binding_ledger=ledger,
            mode="source_test",
        )
    with pytest.raises(CloudError, match="only valid with stable resolver"):
        CiphertextStorageService(
            backend=backend, namespace_key=b"a" * 32,
            namespace_binding_ledger=ledger, mode="source_test",
        )


def test_resolver_cache_and_binding_ledger_contain_no_raw_entity_name(tmp_path):
    backend, journal, data, digest, ref = prepared(tmp_path)
    resolver = lambda entity: "a" * 64
    ledger = binding_ledger(journal)
    ledger.enroll_source_binding(entity_id="trust", namespace="a" * 64)
    service, ops = source(
        backend=backend, journal=journal, resolver=resolver, ledger=ledger,
    )
    ops.put_if_absent(
        context=ctx("WRITE_CIPHERTEXT", "write-1", "trust"),
        object_ref=ref, envelope=data, expected_sha256=digest,
    )
    assert "trust" not in repr(service._resolver_entity_to_namespace)
    assert "trust" not in repr(service._resolver_namespace_to_entity)
    with sqlite3.connect(journal.path) as db:
        assert "trust" not in repr(db.execute("SELECT * FROM events").fetchall())
        assert "trust" not in repr(db.execute("SELECT * FROM intents").fetchall())
    with sqlite3.connect(ledger.path) as db:
        assert "trust" not in repr(db.execute("SELECT * FROM bindings").fetchall())
        assert "trust" not in repr(db.execute("SELECT * FROM binding_events").fetchall())


def test_wrong_stable_mapping_after_process_restart_denied_by_durable_binding_before_get(tmp_path):
    backend, journal, data, digest, ref = prepared(tmp_path)
    first_resolver = lambda entity: "a" * 64
    ledger = binding_ledger(journal)
    ledger.enroll_source_binding(entity_id="trust", namespace="a" * 64)
    _, ops1 = source(
        backend=backend, journal=journal, resolver=first_resolver, ledger=ledger,
    )
    ops1.put_if_absent(
        context=ctx("WRITE_CIPHERTEXT", "write-1"),
        object_ref=ref, envelope=data, expected_sha256=digest,
    )

    spy = CountGet(backend)
    wrong_resolver = lambda entity: "b" * 64
    _, ops2 = source(
        backend=spy, journal=journal, resolver=wrong_resolver, ledger=ledger,
    )
    with pytest.raises(AccessDenied, match="stable namespace binding mismatch"):
        ops2.get(
            context=ctx("READ_CIPHERTEXT", "read-wrong-stable-map"),
            object_ref=ref, expected_sha256=digest,
        )
    assert spy.get_calls == 0
