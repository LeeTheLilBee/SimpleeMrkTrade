"""SC009 synthetic primary-loss and independent encrypted-copy recovery tests.

This is deliberately local and source-only. Separate directories on one test
filesystem are NOT independent infrastructure failure domains or a real RTO/RPO
measurement. Vault original decryption occurs only in this test-side caller.
"""
import hashlib
import os

import pytest

from simplee_cloud.contracts import (
    AccessDenied, IntegrityError, ObjectMissing, StorageContext,
)
from simplee_cloud.tests.test_sc004b_bound_port import Harness, PEER
from vault.real_operations_encrypted_storage import decrypt_original, encrypt_original


def prepared(tmp_path):
    h = Harness(tmp_path / "synthetic-cloud")
    original = os.urandom(1049)
    key = os.urandom(32)
    envelope, metadata = encrypt_original(
        original, key=key, entity_id="trust",
        evidence_id="synthetic-evidence", version_id="synthetic-version",
    )
    h.data = envelope
    h.digest = metadata["ciphertext_sha256"]
    write = h.port.write(
        grant=h.grant("write-1", "WRITE_CIPHERTEXT"),
        authenticated_transport_peer=PEER, request_id="write-1", envelope=envelope,
    )
    receipt = h.port.create_encrypted_backup(
        grant=h.grant("backup-1", "BACKUP_CIPHERTEXT"),
        authenticated_transport_peer=PEER, request_id="backup-1",
    )
    assert receipt.source_ciphertext_sha256 == write.ciphertext_sha256
    return h, original, key, envelope, metadata, receipt


def verified(h, receipt, *, request_id="verify-1", entity="trust"):
    h.receipts[request_id] = receipt
    return h.port.verify_backup_copy(
        grant=h.grant(
            request_id, "VERIFY_BACKUP", entity=entity,
            ref=receipt.backup_ref, digest=receipt.backup_sha256,
        ),
        authenticated_transport_peer=PEER, request_id=request_id,
    )


def backup_path(h, receipt):
    return h.backup_backend.root / receipt.namespace_digest / receipt.backup_ref


def source_recovery_context():
    # This context is an explicit local test fixture, not a Tower credential.
    return StorageContext(
        request_id="isolated-source-restore",
        caller_service="archive_vault", tower_decision_ref="tower-decision-1",
        entity_id="trust", purpose="archive", operation="VERIFY_BACKUP",
    )


def test_separate_encrypted_backup_verifies_after_entire_primary_root_is_lost(tmp_path):
    h, original, key, envelope, metadata, receipt = prepared(tmp_path)
    missing_root = h.primary.root
    moved_to = tmp_path / "simulated-lost-primary"
    missing_root.rename(moved_to)
    assert not missing_root.exists()
    assert h.backup_backend.root.exists()
    assert backup_path(h, receipt).is_file()
    recovery = verified(h, receipt)
    assert recovery.verified_ciphertext is True
    assert recovery.primary_rewritten is False
    assert recovery.vault_original_authenticated is False
    assert recovery.external_failure_domain_verified is False
    assert recovery.recovery_point_objective_certified is False
    assert recovery.recovery_time_objective_certified is False
    assert recovery.production_recovery_authorized is False
    assert not missing_root.exists()  # verification cannot recreate primary

    # Vault-side isolated source caller separately authenticates VLT1 AAD and
    # original hash; Cloud returns only source recovery status to its port.
    restored_vlt1 = h.backup.verify_restore_copy(
        context=source_recovery_context(), receipt=receipt,
    )
    assert hashlib.sha256(restored_vlt1).hexdigest() == metadata["ciphertext_sha256"]
    assert decrypt_original(
        restored_vlt1, key=key, entity_id="trust",
        evidence_id="synthetic-evidence", version_id="synthetic-version",
        expected_sha256=metadata["original_sha256"],
    ) == original
    assert not missing_root.exists()


def test_no_canonical_backup_receipt_cannot_be_bypassed_by_physical_bytes(tmp_path):
    h, _, _, _, _, receipt = prepared(tmp_path)
    assert backup_path(h, receipt).is_file()
    with pytest.raises(AccessDenied, match="canonical backup receipt unavailable"):
        h.port.verify_backup_copy(
            grant=h.grant(
                "verify-uncommitted", "VERIFY_BACKUP",
                ref=receipt.backup_ref, digest=receipt.backup_sha256,
            ),
            authenticated_transport_peer=PEER, request_id="verify-uncommitted",
        )
    assert h.port.health()["vault_archive_commit_authorized"] is False


@pytest.mark.parametrize("failure", ["tamper", "missing", "wrong_key"])
def test_backup_corrupt_lost_or_key_unavailable_records_incident_and_no_success(
    tmp_path, failure,
):
    h, _, _, _, _, receipt = prepared(tmp_path)
    if failure == "tamper":
        path = backup_path(h, receipt)
        body = path.read_bytes()
        path.write_bytes(body[:-1] + bytes([body[-1] ^ 0x01]))
    elif failure == "missing":
        backup_path(h, receipt).unlink()
    else:
        h.backup._backup_key = os.urandom(32)  # synthetic loss of correct key
    with pytest.raises((IntegrityError, ObjectMissing)):
        verified(h, receipt)
    assert h.journal.health()["incident_count"] >= 1
    assert h.journal.verify_chain()["valid"] is True
    assert h.port.health()["production_authorized"] is False


def test_forged_wrong_entity_backup_receipt_denied_even_if_signature_shape_matches(tmp_path):
    h, _, _, _, _, receipt = prepared(tmp_path)
    with pytest.raises(AccessDenied, match="backup entity"):
        verified(h, receipt, request_id="foreign-verify", entity="different-entity")
    assert h.port.health()["hosted_receiver_enabled"] is False


def test_primary_corruption_not_rewritten_by_isolated_backup_verification(tmp_path):
    h, _, _, envelope, _, receipt = prepared(tmp_path)
    primary_path = h.primary.root / receipt.namespace_digest / h.ref
    changed = b"VLT1" + os.urandom(len(envelope) - 4)
    primary_path.write_bytes(changed)
    assert primary_path.read_bytes() == changed
    evidence = verified(h, receipt)
    assert evidence.verified_ciphertext is True
    assert evidence.primary_rewritten is False
    assert primary_path.read_bytes() == changed


def test_backup_provider_outage_is_not_misreported_as_missing_or_healthy(tmp_path):
    h, _, _, _, _, receipt = prepared(tmp_path)

    class Unavailable:
        def get(self, namespace, ref):
            raise OSError("source simulated backup provider outage")

    h.backup.backup_backend = Unavailable()
    with pytest.raises(OSError, match="provider outage"):
        verified(h, receipt)
    assert h.port.health()["production_authorized"] is False
    assert h.journal.verify_chain()["valid"] is True
