"""SC008 real merged Vault metadata/journal with synthetic Cloud source contract.

The explicit test-only coordinator models the required order. It is NOT a
Tower verifier, malware scanner, canonical hosted Vault resolver or deployment
orchestrator. Only Vault owns its final registry transaction and receipt.
"""
import hashlib
import os
import sqlite3

import pytest

from simplee_cloud.contracts import CloudError, IntegrityError
from simplee_cloud.tests.test_sc004b_bound_port import (
    AcceptThenTimeout, Harness, PEER,
)
from vault.archival_transaction_journal import ArchivalJournal, JournalError
from vault.canonical_evidence_registry import CanonicalEvidenceRegistry, RegistryError
from vault.real_operations_encrypted_storage import decrypt_original, encrypt_original


class SyntheticVaultAcceptance:
    def __init__(self, tmp_path, h, *, request_id="write-1",
                 evidence_id="synthetic-evidence", version_id="synthetic-version",
                 parent_version_id=None):
        tmp_path.mkdir(parents=True, exist_ok=True)
        self.h = h
        self.request_id = request_id
        self.evidence_id = evidence_id
        self.version_id = version_id
        self.parent_version_id = parent_version_id
        self.original = os.urandom(913)
        self.key = os.urandom(32)
        self.envelope, self.meta = encrypt_original(
            self.original, key=self.key, entity_id="trust",
            evidence_id=evidence_id, version_id=version_id,
        )
        h.data = self.envelope
        h.digest = self.meta["ciphertext_sha256"]
        self.journal = ArchivalJournal(tmp_path / "vault_workflow.sqlite")
        self.registry = CanonicalEvidenceRegistry(tmp_path / "vault_registry.sqlite")
        self.journal.begin(
            request_id=request_id, entity_id="trust",
            evidence_id=evidence_id, version_id=version_id,
        )
        self.journal.advance(
            request_id=request_id, expected_state="RECEIVED",
            to_state="QUARANTINED",
        )
        # Synthetic scan digest only. This does not claim malware scanning.
        self.journal.advance(
            request_id=request_id, expected_state="QUARANTINED",
            to_state="VERIFIED", receipt_digest=self.meta["original_sha256"],
        )
        self.journal.advance(
            request_id=request_id, expected_state="VERIFIED",
            to_state="ENCRYPTED", receipt_digest=self.meta["ciphertext_sha256"],
        )

    def write(self):
        return self.h.port.write(
            grant=self.h.grant(self.request_id, "WRITE_CIPHERTEXT"),
            authenticated_transport_peer=PEER, request_id=self.request_id,
            envelope=self.envelope,
        )

    def assert_not_archived(self):
        assert self.journal.status(self.request_id) != "ARCHIVED"
        assert self.registry.redacted_receipt(
            "receipt-" + self.request_id, "trust",
        ) is None

    def finalized_after_independent_source_check(self, storage_receipt,
                                                   *, expected_state="ENCRYPTED"):
        assert self.journal.status(self.request_id) == expected_state
        assert storage_receipt.object_ref == self.h.ref
        assert storage_receipt.ciphertext_sha256 == self.meta["ciphertext_sha256"]
        assert storage_receipt.ciphertext_size == len(self.envelope)
        intent = self.h.journal.intent(
            namespace=storage_receipt.namespace_digest, request_id=self.request_id,
        )
        assert intent["state"] in ("WRITE_ACKNOWLEDGED", "RECONCILE_PRESENT")
        assert intent["object_ref"] == storage_receipt.object_ref
        assert intent["ciphertext_sha256"] == storage_receipt.ciphertext_sha256
        # Synthetic separately signed read permission and physical verification
        # of exact Vault envelope, not a real approved operational issuer.
        verified = self.h.port.read_encrypted(
            grant=self.h.grant("verify-" + self.request_id, "READ_CIPHERTEXT"),
            authenticated_transport_peer=PEER,
            request_id="verify-" + self.request_id,
        )
        assert hashlib.sha256(verified).hexdigest() == self.meta["ciphertext_sha256"]
        assert decrypt_original(
            verified, key=self.key, entity_id="trust",
            evidence_id=self.evidence_id, version_id=self.version_id,
            expected_sha256=self.meta["original_sha256"],
        ) == self.original
        # This digest represents synthetic authenticated Cloud receipt evidence
        # ONLY for test sequencing; a real verifier must prove receipt origin.
        cloud_receipt_digest = hashlib.sha256(
            (storage_receipt.object_ref + ":" + storage_receipt.ciphertext_sha256 +
             ":" + str(storage_receipt.ciphertext_size)).encode()
        ).hexdigest()
        self.journal.advance(
            request_id=self.request_id, expected_state=expected_state,
            to_state="CLOUD_COMMITTED", receipt_digest=cloud_receipt_digest,
        )
        self.assert_not_archived()
        receipt_id = "receipt-" + self.request_id
        self.registry.record_archival(
            receipt_id=receipt_id, request_id=self.request_id,
            entity_id="trust", evidence_id=self.evidence_id,
            version_id=self.version_id, parent_version_id=self.parent_version_id,
            original_sha256=self.meta["original_sha256"],
            ciphertext_sha256=storage_receipt.ciphertext_sha256,
            object_ref=storage_receipt.object_ref,
            scan_receipt_ref="synthetic-scan-1",
            tower_receipt_ref="synthetic-tower-1",
            retention_policy_id="synthetic-retention-1",
        )
        registry_digest = hashlib.sha256(receipt_id.encode()).hexdigest()
        assert registry_digest != cloud_receipt_digest
        self.journal.advance(
            request_id=self.request_id, expected_state="CLOUD_COMMITTED",
            to_state="ARCHIVED", receipt_digest=registry_digest,
        )
        assert self.journal.verify_chain(self.request_id)
        assert self.registry.redacted_receipt(receipt_id, "trust")["version_id"] == self.version_id
        with sqlite3.connect(self.registry.path) as db:
            canonical = db.execute(
                """SELECT entity_id,evidence_id,version_id,object_ref,
                   original_sha256,ciphertext_sha256 FROM archival_receipts
                   WHERE receipt_id=?""", (receipt_id,),
            ).fetchone()
        assert canonical == (
            "trust", self.evidence_id, self.version_id,
            storage_receipt.object_ref, self.meta["original_sha256"],
            self.meta["ciphertext_sha256"],
        )
        return receipt_id


def test_real_vault_workflow_remains_separate_until_canonical_receipt(tmp_path):
    h = Harness(tmp_path / "cloud")
    step = SyntheticVaultAcceptance(tmp_path / "vault", h)
    step.assert_not_archived()
    receipt = step.write()
    assert step.journal.status("write-1") == "ENCRYPTED"
    assert receipt.ciphertext_sha256 == step.meta["ciphertext_sha256"]
    step.assert_not_archived()
    assert step.finalized_after_independent_source_check(receipt) == "receipt-write-1"
    assert step.registry.redacted_receipt("receipt-write-1", "foreign-entity") is None
    assert h.port.health()["vault_archive_commit_authorized"] is False
    assert h.port.health()["production_authorized"] is False


def test_provider_accepted_write_but_ack_lost_requires_separate_vault_reconciliation(tmp_path):
    provider = AcceptThenTimeout()
    h = Harness(tmp_path / "cloud", primary=provider)
    step = SyntheticVaultAcceptance(tmp_path / "vault", h)
    with pytest.raises(OSError, match="ack lost"):
        step.write()
    assert provider.put_calls == 1
    assert step.journal.status("write-1") == "ENCRYPTED"
    step.journal.advance(
        request_id="write-1", expected_state="ENCRYPTED",
        to_state="RECONCILE_REQUIRED",
    )
    step.assert_not_archived()
    result = h.port.reconcile_original_write(
        grant=h.grant("write-1", "RECONCILE_WRITE"),
        authenticated_transport_peer=PEER, original_request_id="write-1",
    )
    assert result["status"] == "PRESENT_INTERNAL_STORAGE_ONLY"
    assert result["vault_archive_committed"] is False
    assert provider.put_calls == 1
    step.assert_not_archived()
    assert step.finalized_after_independent_source_check(
        result["storage_receipt"], expected_state="RECONCILE_REQUIRED",
    ) == "receipt-write-1"


@pytest.mark.parametrize("failure", ["missing", "corrupt"])
def test_missing_or_corrupt_reconciled_cloud_object_never_archives(tmp_path, failure):
    provider = AcceptThenTimeout()
    h = Harness(tmp_path / "cloud", primary=provider)
    step = SyntheticVaultAcceptance(tmp_path / "vault", h)
    with pytest.raises(OSError):
        step.write()
    step.journal.advance(
        request_id="write-1", expected_state="ENCRYPTED",
        to_state="RECONCILE_REQUIRED",
    )
    key = next(iter(provider.rows))
    if failure == "missing":
        provider.rows.clear()
    else:
        provider.rows[key] = b"VLT1" + os.urandom(len(provider.rows[key]) - 4)
    result = h.port.reconcile_original_write(
        grant=h.grant("write-1", "RECONCILE_WRITE"),
        authenticated_transport_peer=PEER, original_request_id="write-1",
    )
    assert result["status"] == ("MISSING_HOLD" if failure == "missing" else "CORRUPT_HOLD")
    assert result["storage_receipt"] is None
    assert result["vault_archive_committed"] is False
    step.assert_not_archived()
    with pytest.raises(JournalError, match="invalid state transition"):
        step.journal.advance(
            request_id="write-1", expected_state="RECONCILE_REQUIRED",
            to_state="ARCHIVED", receipt_digest="a" * 64,
        )
    assert provider.put_calls == 1
    assert step.journal.verify_chain("write-1")


def test_signed_hash_mismatch_blocks_cloud_reservation_and_vault_finality(tmp_path):
    h = Harness(tmp_path / "cloud")
    step = SyntheticVaultAcceptance(tmp_path / "vault", h)
    with pytest.raises(IntegrityError):
        h.port.write(
            grant=h.grant("write-1", "WRITE_CIPHERTEXT"),
            authenticated_transport_peer=PEER, request_id="write-1",
            envelope=b"VLT1" + os.urandom(len(step.envelope) - 4),
        )
    assert h.journal.health()["write_count"] == 0
    step.assert_not_archived()
    assert step.journal.status("write-1") == "ENCRYPTED"


def test_actual_vault_registry_refuses_conflicting_cloud_ref_replay(tmp_path):
    h = Harness(tmp_path / "cloud")
    step = SyntheticVaultAcceptance(tmp_path / "vault", h)
    receipt = step.write()
    step.finalized_after_independent_source_check(receipt)
    with pytest.raises(RegistryError, match="conflicting request replay"):
        step.registry.record_archival(
            receipt_id="receipt-write-1", request_id="write-1",
            entity_id="trust", evidence_id=step.evidence_id,
            version_id=step.version_id,
            original_sha256=step.meta["original_sha256"],
            ciphertext_sha256=step.meta["ciphertext_sha256"],
            object_ref="objects/" + "f" * 48,
            scan_receipt_ref="synthetic-scan-1",
            tower_receipt_ref="synthetic-tower-1",
            retention_policy_id="synthetic-retention-1",
        )
    assert step.registry.redacted_receipt("receipt-write-1", "trust") is not None


def test_vault_journal_and_registry_are_not_themselves_live_receipt_verifiers(tmp_path):
    # Their API trusts the owning orchestrator's independently verified inputs;
    # accepting well-shaped metadata is not evidence of a live Tower identity.
    journal = ArchivalJournal(tmp_path / "source_journal.sqlite")
    registry = CanonicalEvidenceRegistry(tmp_path / "source_registry.sqlite")
    assert journal.begin(
        request_id="fake-1", entity_id="trust",
        evidence_id="fake-evidence", version_id="fake-version",
    ) == "RECEIVED"
    assert registry.redacted_receipt("fake-receipt", "trust") is None
    # No Cloud storage call, principal authentication, provider or archival
    # receipt is created by a journal start or a source registry constructor.
