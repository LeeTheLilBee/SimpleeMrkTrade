"""SC005 source-only signed checkpoint and isolated encrypted recovery tests."""
import hashlib
import json
import os
import sqlite3
from dataclasses import replace

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from simplee_cloud.backup import IndependentBackupService
from simplee_cloud.checkpoints import (
    SignedCheckpoint, deliver_source_checkpoint, seal_source_checkpoint,
    verify_checkpoint,
)
from simplee_cloud.contracts import AccessDenied, CloudError, IntegrityError, ObjectMissing, StorageContext
from simplee_cloud.journal import SQLiteOperationalJournal
from simplee_cloud.local_backend import LocalPrivateCiphertextBackend
from simplee_cloud.operations import JournaledCiphertextOperations
from simplee_cloud.recovery_drill import run_source_restore_drill
from simplee_cloud.service import CiphertextStorageService

NAMESPACE = "a" * 64


class TestAuthority:
    __test__ = False
    def authorize(self, context, operation):
        if context.tower_decision_ref != "synthetic-tower" or context.operation != operation:
            raise AccessDenied("synthetic gate denied")


def context(op, request_id="source-test-1", entity="trust"):
    return StorageContext(
        request_id=request_id, caller_service="archive_vault",
        tower_decision_ref="synthetic-tower", entity_id=entity,
        purpose="archival", operation=op,
    )


class FakeImmutableAnchor:
    def __init__(self):
        self.items = {}

    def put_if_absent(self, reference, checkpoint):
        if reference in self.items:
            raise CloudError("checkpoint already externally anchored")
        self.items[reference] = checkpoint

    def get(self, reference):
        return self.items[reference]


def journal(tmp_path):
    return SQLiteOperationalJournal(
        tmp_path / "journal" / "operations.sqlite", mode="source_test",
    )


def event(j, request_id):
    # Generic synthetic append-only event for checkpoint-prefix tests. SC028
    # reserves read_intent/read_verified exclusively for real bound read scope.
    j.record_safe_event({
        "event": "restore_verification_intent", "request_id": request_id,
        "tower_decision_ref": "synthetic-tower", "namespace_digest": NAMESPACE,
    })


def keys():
    priv = Ed25519PrivateKey.generate()
    pub = priv.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return priv, {"synthetic-external-signer": pub}


def seal(j, priv, pubs, previous=None):
    return seal_source_checkpoint(
        journal=j, key_id="synthetic-external-signer",
        external_signer=priv.sign, pinned_public_keys=pubs,
        previous=previous, mode="source_test",
    )


def test_signed_checkpoint_reopening_and_prefix_lineage(tmp_path):
    j = journal(tmp_path)
    event(j, "request-1")
    private, pubs = keys()
    first = seal(j, private, pubs)
    d1 = verify_checkpoint(first, pinned_public_keys=pubs, journal=j)
    assert d1["event_count"] == 1
    sink = FakeImmutableAnchor()
    ref = deliver_source_checkpoint(
        signed=first, sink=sink, pinned_public_keys=pubs,
        journal=j, mode="source_test",
    )
    assert sink.get(ref) == first
    with pytest.raises(CloudError):
        deliver_source_checkpoint(
            signed=first, sink=sink, pinned_public_keys=pubs,
            journal=j, mode="source_test",
        )
    event(j, "request-2")
    assert verify_checkpoint(first, pinned_public_keys=pubs, journal=j) == d1
    second = seal(j, private, pubs, previous=first)
    doc = verify_checkpoint(second, pinned_public_keys=pubs, journal=j)
    assert doc["previous_checkpoint_sha256"] == first.sha256
    assert doc["event_count"] == 2
    with pytest.raises(CloudError, match="additional"):
        seal(j, private, pubs, previous=second)
    reopened = SQLiteOperationalJournal(j.path, mode="source_test")
    assert verify_checkpoint(first, pinned_public_keys=pubs, journal=reopened) == d1
    assert verify_checkpoint(second, pinned_public_keys=pubs, journal=reopened) == doc


def test_signature_and_history_rollback_detected(tmp_path):
    j = journal(tmp_path)
    event(j, "request-1")
    private, pubs = keys()
    sealed = seal(j, private, pubs)
    another, wrongpub = keys()
    with pytest.raises(IntegrityError):
        verify_checkpoint(sealed, pinned_public_keys=wrongpub, journal=j)
    tampered = replace(sealed, payload=sealed.payload[:-1] + b" ")
    with pytest.raises(IntegrityError):
        verify_checkpoint(tampered, pinned_public_keys=pubs, journal=j)
    with sqlite3.connect(j.path) as conn:
        conn.execute("DROP TRIGGER events_block_update")
        conn.execute("UPDATE events SET event_type='altered' WHERE seq=1")
    with pytest.raises(IntegrityError):
        verify_checkpoint(sealed, pinned_public_keys=pubs, journal=j)


def test_no_external_checkpointer_enabled_by_default(tmp_path):
    j = journal(tmp_path)
    private, pubs = keys()
    with pytest.raises(CloudError):
        seal_source_checkpoint(
            journal=j, key_id="synthetic-external-signer",
            external_signer=private.sign, pinned_public_keys=pubs,
        )
    sealed = seal(j, private, pubs)
    with pytest.raises(CloudError):
        deliver_source_checkpoint(
            signed=sealed, sink=FakeImmutableAnchor(),
            pinned_public_keys=pubs, journal=j,
        )


def setup_backup(tmp_path):
    j = journal(tmp_path)
    primary = LocalPrivateCiphertextBackend(tmp_path / "primary")
    secondary = LocalPrivateCiphertextBackend(tmp_path / "backup")
    source = CiphertextStorageService(
        backend=primary, namespace_key=os.urandom(32),
        authority=TestAuthority(), audit_event=j.record_safe_event,
        mode="source_test",
    )
    ops = JournaledCiphertextOperations(source=source, journal=j)
    original = b"VLT1" + os.urandom(48)
    digest = hashlib.sha256(original).hexdigest()
    ref = source.new_object_ref()
    receipt = ops.put_if_absent(
        context=context("WRITE_CIPHERTEXT"), object_ref=ref,
        envelope=original, expected_sha256=digest,
    )
    recovery = IndependentBackupService(
        source=source, backup_backend=secondary,
        backup_key=os.urandom(32), key_reference="synthetic-key-only",
    )
    backup_receipt = recovery.create(
        context=context("BACKUP_CIPHERTEXT", "backup-operation"),
        source_object_ref=ref, source_ciphertext_sha256=digest,
    )
    return j, source, receipt, recovery, backup_receipt, original, digest


def drill(j, recovery, receipt, digest, *, ctx=None):
    return run_source_restore_drill(
        backup=recovery, journal=j,
        context=ctx or context("VERIFY_BACKUP", "restore-operation"),
        receipt=receipt, expected_inner_sha256=digest,
        drill_id="synthetic-drill-1", mode="source_test",
    )


def test_backup_restores_inner_envelope_without_primary_write(tmp_path):
    j, source, primary_receipt, recovery, receipt, original, digest = setup_backup(tmp_path)
    primary_path = (source._backend.root / primary_receipt.namespace_digest /
                    "objects" / primary_receipt.object_ref.split("/")[1])
    primary_path.unlink()  # Simulated primary loss, no repair or write authorized.
    evidence = drill(j, recovery, receipt, digest)
    assert evidence.verified_ciphertext is True
    assert evidence.status == "SOURCE_ONLY_ENCRYPTED_COPY_VERIFIED"
    assert evidence.primary_rewritten is False
    assert evidence.vault_original_authenticated is False
    assert evidence.external_failure_domain_verified is False
    assert evidence.recovery_point_objective_certified is False
    assert evidence.recovery_time_objective_certified is False
    assert evidence.production_recovery_authorized is False
    assert not primary_path.exists()
    assert j.health()["incident_count"] == 0


@pytest.mark.parametrize("fault", ["tamper", "missing"])
def test_backup_corruption_or_loss_durable_incident(tmp_path, fault):
    j, source, primary_receipt, recovery, receipt, original, digest = setup_backup(tmp_path)
    path = (recovery.backup_backend.root / receipt.namespace_digest /
            "backups" / receipt.backup_ref.split("/")[1])
    if fault == "tamper":
        corrupted = bytearray(path.read_bytes())
        corrupted[-1] ^= 1
        path.write_bytes(corrupted)
        failure = IntegrityError
    else:
        path.unlink()
        failure = ObjectMissing
    with pytest.raises(failure):
        drill(j, recovery, receipt, digest)
    assert j.health()["incident_count"] == 1
    assert j.verify_chain()["valid"] is True


def test_wrong_scope_and_live_restore_denied(tmp_path):
    j, source, primary_receipt, recovery, receipt, original, digest = setup_backup(tmp_path)
    with pytest.raises(AccessDenied):
        drill(j, recovery, receipt, digest,
              ctx=context("VERIFY_BACKUP", "restore-denied", "another-entity"))
    with pytest.raises(AccessDenied):
        run_source_restore_drill(
            backup=recovery, journal=j, context=context("VERIFY_BACKUP"),
            receipt=receipt, expected_inner_sha256=digest,
            drill_id="not-live",
        )
    assert j.health()["incident_count"] == 0
