"""SC037 stable opaque namespace resolver and namespace-key rotation source tests."""
import hashlib
import os
import sqlite3

import pytest

from simplee_cloud.contracts import AccessDenied, CloudError, StorageContext
from simplee_cloud.journal import SQLiteOperationalJournal
from simplee_cloud.local_backend import LocalPrivateCiphertextBackend
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


def ctx(operation, request, entity="trust"):
    return StorageContext(
        request_id=request, caller_service="archive_vault",
        tower_decision_ref="synthetic-gate", entity_id=entity,
        purpose="archive", operation=operation,
    )


def source(*, backend, journal, key=None, resolver=None):
    service = CiphertextStorageService(
        backend=backend, namespace_key=key, namespace_resolver=resolver,
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
    first, ops1 = source(backend=backend, journal=journal, resolver=resolver)
    receipt = ops1.put_if_absent(
        context=ctx("WRITE_CIPHERTEXT", "write-1"),
        object_ref=ref, envelope=data, expected_sha256=digest,
    )
    assert receipt.namespace_digest == stable["trust"]

    # Simulate a reconstructed process after namespace-secret policy changes:
    # no HMAC secret is passed to the second service, only the stable resolver.
    second, ops2 = source(backend=backend, journal=journal, resolver=resolver)
    assert ops2.get(
        context=ctx("READ_CIPHERTEXT", "read-1"),
        object_ref=ref, expected_sha256=digest,
    ) == data
    assert second.health()["source_stable_namespace_resolver_injected"] is True
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
    mapping = {
        "trust": "a" * 64,
    }
    resolver = lambda entity: mapping[entity]
    service, ops = source(backend=backend, journal=journal, resolver=resolver)
    ops.put_if_absent(
        context=ctx("WRITE_CIPHERTEXT", "write-1"),
        object_ref=ref, envelope=data, expected_sha256=digest,
    )
    mapping["trust"] = "b" * 64
    spy = CountGet(backend)
    service._backend = spy
    with pytest.raises(AccessDenied, match="changed entity binding"):
        ops.get(
            context=ctx("READ_CIPHERTEXT", "read-drift"),
            object_ref=ref, expected_sha256=digest,
        )
    assert spy.get_calls == 0


def test_stable_resolver_collision_between_entities_denied_in_process(tmp_path):
    backend, journal, data, digest, ref = prepared(tmp_path)
    same = "a" * 64
    resolver = lambda entity: same
    service, ops = source(backend=backend, journal=journal, resolver=resolver)
    ops.put_if_absent(
        context=ctx("WRITE_CIPHERTEXT", "write-trust", "trust"),
        object_ref=ref, envelope=data, expected_sha256=digest,
    )
    spy = CountGet(backend)
    service._backend = spy
    with pytest.raises(AccessDenied, match="resolver collision"):
        service.get(
            context=ctx("READ_CIPHERTEXT", "read-other", "different-entity"),
            object_ref=ref, expected_sha256=digest,
        )
    assert spy.get_calls == 0


def test_resolver_unavailable_or_malformed_denied_before_provider(tmp_path):
    backend, journal, data, digest, ref = prepared(tmp_path)
    spy = CountGet(backend)
    unavailable, _ = source(
        backend=spy, journal=journal,
        resolver=lambda entity: (_ for _ in ()).throw(OSError("secret outage")),
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
    with pytest.raises(CloudError, match="either namespace secret or stable resolver"):
        CiphertextStorageService(
            backend=backend, namespace_key=b"a" * 32,
            namespace_resolver=lambda entity: "a" * 64,
            mode="source_test",
        )


def test_resolver_cache_contains_no_raw_entity_name(tmp_path):
    backend, journal, data, digest, ref = prepared(tmp_path)
    resolver = lambda entity: "a" * 64
    service, ops = source(backend=backend, journal=journal, resolver=resolver)
    ops.put_if_absent(
        context=ctx("WRITE_CIPHERTEXT", "write-1", "trust"),
        object_ref=ref, envelope=data, expected_sha256=digest,
    )
    assert "trust" not in repr(service._resolver_entity_to_namespace)
    assert "trust" not in repr(service._resolver_namespace_to_entity)
    with sqlite3.connect(journal.path) as db:
        assert "trust" not in repr(db.execute("SELECT * FROM events").fetchall())
        assert "trust" not in repr(db.execute("SELECT * FROM intents").fetchall())


def test_wrong_stable_mapping_after_process_restart_fails_journal_provenance_before_get(tmp_path):
    backend, journal, data, digest, ref = prepared(tmp_path)
    first_resolver = lambda entity: "a" * 64
    _, ops1 = source(backend=backend, journal=journal, resolver=first_resolver)
    ops1.put_if_absent(
        context=ctx("WRITE_CIPHERTEXT", "write-1"),
        object_ref=ref, envelope=data, expected_sha256=digest,
    )

    spy = CountGet(backend)
    wrong_resolver = lambda entity: "b" * 64
    _, ops2 = source(backend=spy, journal=journal, resolver=wrong_resolver)
    with pytest.raises(CloudError, match="acknowledged exact primary"):
        ops2.get(
            context=ctx("READ_CIPHERTEXT", "read-wrong-stable-map"),
            object_ref=ref, expected_sha256=digest,
        )
    assert spy.get_calls == 0
