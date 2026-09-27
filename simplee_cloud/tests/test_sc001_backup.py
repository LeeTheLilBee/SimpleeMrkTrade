import hashlib
import os

import pytest

from simplee_cloud.backup import IndependentBackupService
from simplee_cloud.contracts import AccessDenied, CloudError, IntegrityError, StorageContext
from simplee_cloud.local_backend import LocalPrivateCiphertextBackend
from simplee_cloud.service import CiphertextStorageService


class TestOnlyAuthority:
    __test__ = False
    def authorize(self, context, operation):
        if context.tower_decision_ref != "synthetic-allow" or context.operation != operation:
            raise AccessDenied("synthetic authority denied")


def ctx(op, entity="trust"):
    return StorageContext(
        request_id="test-request", caller_service="archive_vault",
        tower_decision_ref="synthetic-allow", entity_id=entity,
        purpose="approved-test", operation=op,
    )


def setup(tmp_path):
    primary = LocalPrivateCiphertextBackend(tmp_path / "primary")
    backup = LocalPrivateCiphertextBackend(tmp_path / "separate-backup")
    events = []
    source = CiphertextStorageService(
        backend=primary, namespace_key=os.urandom(32),
        authority=TestOnlyAuthority(), audit_event=events.append, mode="source_test",
    )
    key = os.urandom(32)
    recovery = IndependentBackupService(
        source=source, backup_backend=backup, backup_key=key,
        key_reference="synthetic-backup-key-v1",
    )
    original = b"VLT1" + os.urandom(48)
    ref = source.new_object_ref()
    digest = hashlib.sha256(original).hexdigest()
    source.put_if_absent(
        context=ctx("WRITE_CIPHERTEXT"), object_ref=ref,
        envelope=original, expected_sha256=digest,
    )
    return source, recovery, original, ref, digest, events


def test_independently_encrypted_backup_and_restore_check(tmp_path):
    source, recovery, original, ref, digest, events = setup(tmp_path)
    receipt = recovery.create(
        context=ctx("BACKUP_CIPHERTEXT"),
        source_object_ref=ref, source_ciphertext_sha256=digest,
    )
    raw_backup = recovery.backup_backend.get(receipt.namespace_digest, receipt.backup_ref)
    assert raw_backup.startswith(b"SCB1")
    assert raw_backup != original
    assert original not in raw_backup
    assert receipt.backup_sha256 == hashlib.sha256(raw_backup).hexdigest()
    assert recovery.verify_restore_copy(
        context=ctx("VERIFY_BACKUP"), receipt=receipt,
    ) == original
    assert events[-1]["event"] == "restore_copy_verified"


def test_wrong_entity_key_tamper_and_missing_separation(tmp_path):
    source, recovery, original, ref, digest, _ = setup(tmp_path)
    receipt = recovery.create(
        context=ctx("BACKUP_CIPHERTEXT"),
        source_object_ref=ref, source_ciphertext_sha256=digest,
    )
    with pytest.raises(AccessDenied):
        recovery.verify_restore_copy(
            context=ctx("VERIFY_BACKUP", entity="other-entity"), receipt=receipt,
        )
    wrong_key = IndependentBackupService(
        source=source, backup_backend=recovery.backup_backend,
        backup_key=os.urandom(32), key_reference=recovery.key_reference,
    )
    with pytest.raises(IntegrityError):
        wrong_key.verify_restore_copy(context=ctx("VERIFY_BACKUP"), receipt=receipt)
    path = (tmp_path / "separate-backup" / receipt.namespace_digest /
            "backups" / receipt.backup_ref.split("/")[1])
    body = bytearray(path.read_bytes())
    body[-1] ^= 1
    path.write_bytes(body)
    with pytest.raises(IntegrityError):
        recovery.verify_restore_copy(context=ctx("VERIFY_BACKUP"), receipt=receipt)
    with pytest.raises(CloudError):
        IndependentBackupService(
            source=source, backup_backend=source._backend,
            backup_key=os.urandom(32), key_reference="same-backend",
        )
