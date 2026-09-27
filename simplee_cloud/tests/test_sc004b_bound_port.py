"""Synthetic SC004B signed Tower→Vault→Cloud composition; no live identities."""
import hashlib
import json
import os
from dataclasses import replace

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from simplee_cloud.backup import IndependentBackupService
from simplee_cloud.bound_port import SourceOnlyBoundCloudPort
from simplee_cloud.contracts import (
    AccessDenied, CloudError, ObjectMissing,
)
from simplee_cloud.journal import SQLiteOperationalJournal
from simplee_cloud.journaled_backup import JournaledBackupOperations
from simplee_cloud.local_backend import LocalPrivateCiphertextBackend
from simplee_cloud.operations import JournaledCiphertextOperations
from simplee_cloud.service import CiphertextStorageService
from simplee_cloud.tower_grants import (
    SQLiteNonceReplayStore, SignedTowerGrant, SourceOnlyTowerGrantVerifier,
    TrustedVaultScope,
)

NOW = 2_000_000_000
PEER = object()


class SyntheticSourceAuthority:
    def authorize(self, context, operation):
        if (
            context.caller_service != "archive_vault" or
            context.tower_decision_ref != "tower-decision-1" or
            context.operation != operation
        ):
            raise AccessDenied("synthetic SC001 source authority denied")


class AcceptThenTimeout:
    """Store bytes and lose the acknowledgement, like a network ambiguity."""
    def __init__(self):
        self.rows = {}
        self.put_calls = 0

    def put_if_absent(self, namespace, ref, body):
        self.put_calls += 1
        self.rows[(namespace, ref)] = body
        raise OSError("synthetic ack lost")

    def get(self, namespace, ref):
        try:
            return self.rows[(namespace, ref)]
        except KeyError as exc:
            raise ObjectMissing("synthetic ciphertext missing") from exc


class Harness:
    def __init__(self, tmp_path, *, primary=None, peer_is_valid=None, policy_is_current=None):
        self.key = Ed25519PrivateKey.generate()
        public = self.key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw,
        )
        self.journal = SQLiteOperationalJournal(
            tmp_path / "audit" / "operations.sqlite", mode="source_test",
        )
        self.primary = primary if primary is not None else LocalPrivateCiphertextBackend(
            tmp_path / "primary",
        )
        self.source = CiphertextStorageService(
            backend=self.primary, namespace_key=os.urandom(32),
            authority=SyntheticSourceAuthority(),
            audit_event=self.journal.record_safe_event, mode="source_test",
        )
        self.operations = JournaledCiphertextOperations(
            source=self.source, journal=self.journal,
        )
        self.nonces = SQLiteNonceReplayStore(
            tmp_path / "nonces" / "used.sqlite", mode="source_test",
        )
        self.verifier = SourceOnlyTowerGrantVerifier(
            tower_public_keys={"synthetic-signing-key": public},
            peer_is_authenticated_vault=peer_is_valid or (lambda peer: peer is PEER),
            tower_policy_is_current=policy_is_current or (
                lambda policy: policy["decision_ref"] == "tower-decision-1" and
                policy["approval_ref"] == "approval-1" and
                policy["step_up_ref"] == "stepup-1"
            ),
            replay_store=self.nonces, now_epoch_seconds=lambda: NOW,
            mode="source_test",
        )
        self.canonical = {}
        self.receipts = {}
        self.backup_backend = LocalPrivateCiphertextBackend(tmp_path / "backup")
        self.backup = IndependentBackupService(
            source=self.source, backup_backend=self.backup_backend,
            backup_key=os.urandom(32), key_reference="synthetic-backup-key",
        )
        self.journaled_backup = JournaledBackupOperations(
            operations=self.operations, backup=self.backup, mode="source_test",
        )
        self.port = SourceOnlyBoundCloudPort(
            operations=self.operations, tower_verifier=self.verifier,
            canonical_scope_resolver=lambda request, operation: self.canonical[
                (request, operation)
            ],
            backup=self.backup, journaled_backup=self.journaled_backup,
            canonical_backup_resolver=lambda request: self.receipts[request],
            mode="source_test",
        )
        self.data = b"VLT1" + os.urandom(48)
        self.digest = hashlib.sha256(self.data).hexdigest()
        self.ref = self.source.new_object_ref()

    def grant(self, request_id, operation, *, ref=None, digest=None, entity="trust",
              purpose="archive", classification="owner_private", approval="approval-1",
              stepup="stepup-1", canonical=True):
        ref = self.ref if ref is None else ref
        digest = self.digest if digest is None else digest
        expected = TrustedVaultScope(
            request_id=request_id, entity_id=entity, purpose=purpose,
            operation=operation, classification=classification, object_ref=ref,
            ciphertext_sha256=digest,
        )
        if canonical:
            self.canonical[(request_id, operation)] = expected
        claims = {
            "schema": "simplee.cloud.tower-grant.v1", "iss": "tower",
            "aud": "simplee_sovereign_cloud", "service": "archive_vault",
            "request_id": request_id, "entity_id": entity, "purpose": purpose,
            "operation": operation, "classification": classification,
            "decision_ref": "tower-decision-1", "approval_ref": approval,
            "step_up_ref": stepup, "object_ref": ref, "ciphertext_sha256": digest,
            "nonce": os.urandom(16).hex(), "iat": NOW - 1, "exp": NOW + 30,
        }
        payload = json.dumps(
            claims, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        ).encode()
        return SignedTowerGrant(
            "synthetic-signing-key", payload, self.key.sign(payload),
        )


def test_bound_write_read_fresh_grants_no_user_supplied_object_or_context(tmp_path):
    h = Harness(tmp_path)
    written = h.port.write(
        grant=h.grant("write-1", "WRITE_CIPHERTEXT"),
        authenticated_transport_peer=PEER, request_id="write-1", envelope=h.data,
    )
    assert written.object_ref == h.ref
    assert written.ciphertext_sha256 == h.digest
    encrypted = h.port.read_encrypted(
        grant=h.grant("read-1", "READ_CIPHERTEXT"),
        authenticated_transport_peer=PEER, request_id="read-1",
    )
    assert encrypted == h.data
    assert h.nonces.count() == 2
    assert h.journal.health()["write_count"] == 1
    assert h.port.health()["production_authorized"] is False
    assert h.port.health()["hosted_receiver_enabled"] is False


def test_replay_denied_and_new_signed_nonce_uses_original_idempotent_intent(tmp_path):
    h = Harness(tmp_path)
    signed = h.grant("write-1", "WRITE_CIPHERTEXT")
    args = {
        "grant": signed, "authenticated_transport_peer": PEER,
        "request_id": "write-1", "envelope": h.data,
    }
    first = h.port.write(**args)
    with pytest.raises(AccessDenied, match="already consumed"):
        h.port.write(**args)
    again = h.port.write(
        grant=h.grant("write-1", "WRITE_CIPHERTEXT"),
        authenticated_transport_peer=PEER, request_id="write-1", envelope=h.data,
    )
    assert again == first
    assert h.journal.health()["write_count"] == 1
    assert h.nonces.count() == 2


def test_signed_wrong_digest_and_untrusted_canonical_scope_denied_before_write(tmp_path):
    h = Harness(tmp_path)
    grant = h.grant("write-1", "WRITE_CIPHERTEXT")
    h.canonical[("write-1", "WRITE_CIPHERTEXT")] = replace(
        h.canonical[("write-1", "WRITE_CIPHERTEXT")],
        object_ref=h.source.new_object_ref(),
    )
    with pytest.raises(AccessDenied, match="trusted Vault scope"):
        h.port.write(
            grant=grant, authenticated_transport_peer=PEER,
            request_id="write-1", envelope=h.data,
        )
    assert h.nonces.count() == 0
    assert h.journal.health()["write_count"] == 0
    assert h.journal.health()["event_count"] == 0


def test_resolver_unavailable_peer_unauthenticated_or_policy_revoked_denies(tmp_path):
    h = Harness(tmp_path)
    signed = h.grant("write-1", "WRITE_CIPHERTEXT")
    with pytest.raises(AccessDenied, match="canonical Vault scope unavailable"):
        h.port.write(
            grant=signed, authenticated_transport_peer=PEER,
            request_id="unknown-request", envelope=h.data,
        )
    with pytest.raises(AccessDenied, match="unauthenticated"):
        h.port.write(
            grant=signed, authenticated_transport_peer=object(),
            request_id="write-1", envelope=h.data,
        )
    assert h.nonces.count() == 0
    assert h.journal.health()["write_count"] == 0
    revoked = Harness(
        tmp_path / "revoked", policy_is_current=lambda policy: False,
    )
    denied = revoked.grant("write-2", "WRITE_CIPHERTEXT")
    with pytest.raises(AccessDenied, match="revoked"):
        revoked.port.write(
            grant=denied, authenticated_transport_peer=PEER,
            request_id="write-2", envelope=revoked.data,
        )
    assert revoked.journal.health()["write_count"] == 0


def test_write_bytes_must_equal_signed_and_canonical_digest(tmp_path):
    h = Harness(tmp_path)
    signed = h.grant("write-1", "WRITE_CIPHERTEXT")
    with pytest.raises(CloudError, match="hash mismatch"):
        h.port.write(
            grant=signed, authenticated_transport_peer=PEER,
            request_id="write-1", envelope=b"VLT1" + os.urandom(48),
        )
    # Grant cannot be reused even though the subsequent storage validation
    # failed. A fresh Tower decision/nonce is required for another attempt.
    assert h.nonces.count() == 1
    assert h.journal.health()["write_count"] == 0


def test_reconciliation_matches_original_intent_and_never_commits_vault(tmp_path):
    backend = AcceptThenTimeout()
    h = Harness(tmp_path, primary=backend)
    with pytest.raises(OSError, match="ack lost"):
        h.port.write(
            grant=h.grant("write-1", "WRITE_CIPHERTEXT"),
            authenticated_transport_peer=PEER,
            request_id="write-1", envelope=h.data,
        )
    assert backend.put_calls == 1
    result = h.port.reconcile_original_write(
        grant=h.grant("write-1", "RECONCILE_WRITE"),
        authenticated_transport_peer=PEER, original_request_id="write-1",
    )
    assert result["status"] == "PRESENT_INTERNAL_STORAGE_ONLY"
    assert result["vault_archive_committed"] is False
    assert backend.put_calls == 1
    assert h.journal.health()["pending_writes"] == 0


def test_reconciliation_can_not_substitute_another_signed_object(tmp_path):
    backend = AcceptThenTimeout()
    h = Harness(tmp_path, primary=backend)
    with pytest.raises(OSError):
        h.port.write(
            grant=h.grant("write-1", "WRITE_CIPHERTEXT"),
            authenticated_transport_peer=PEER, request_id="write-1",
            envelope=h.data,
        )
    unrelated = h.source.new_object_ref()
    signed = h.grant("write-1", "RECONCILE_WRITE", ref=unrelated)
    with pytest.raises(AccessDenied, match="original durable write intent"):
        h.port.reconcile_original_write(
            grant=signed, authenticated_transport_peer=PEER,
            original_request_id="write-1",
        )
    assert h.journal.health()["pending_writes"] == 1
    assert backend.put_calls == 1


def test_backup_creation_and_isolated_verified_copy_bound_to_exact_receipt(tmp_path):
    h = Harness(tmp_path)
    h.port.write(
        grant=h.grant("write-1", "WRITE_CIPHERTEXT"),
        authenticated_transport_peer=PEER, request_id="write-1",
        envelope=h.data,
    )
    backup_receipt = h.port.create_encrypted_backup(
        grant=h.grant("backup-1", "BACKUP_CIPHERTEXT"),
        authenticated_transport_peer=PEER, request_id="backup-1",
    )
    assert backup_receipt.source_ciphertext_sha256 == h.digest
    h.receipts["verify-1"] = backup_receipt
    signed = h.grant(
        "verify-1", "VERIFY_BACKUP",
        ref=backup_receipt.backup_ref, digest=backup_receipt.backup_sha256,
    )
    evidence = h.port.verify_backup_copy(
        grant=signed, authenticated_transport_peer=PEER,
        request_id="verify-1",
    )
    assert evidence.verified_ciphertext is True
    assert evidence.primary_rewritten is False
    assert evidence.vault_original_authenticated is False
    assert evidence.production_recovery_authorized is False


def test_backup_wrong_canonical_receipt_denied_without_releasing_ciphertext(tmp_path):
    h = Harness(tmp_path)
    h.port.write(
        grant=h.grant("write-1", "WRITE_CIPHERTEXT"),
        authenticated_transport_peer=PEER, request_id="write-1",
        envelope=h.data,
    )
    receipt = h.port.create_encrypted_backup(
        grant=h.grant("backup-1", "BACKUP_CIPHERTEXT"),
        authenticated_transport_peer=PEER, request_id="backup-1",
    )
    h.receipts["verify-1"] = receipt
    signed = h.grant("verify-1", "VERIFY_BACKUP",
                     ref=receipt.backup_ref, digest="f" * 64)
    with pytest.raises(AccessDenied, match="canonical Vault receipt"):
        h.port.verify_backup_copy(
            grant=signed, authenticated_transport_peer=PEER,
            request_id="verify-1",
        )


def test_no_source_fixture_can_provision_live_bridge(tmp_path):
    h = Harness(tmp_path)
    with pytest.raises(CloudError, match="not authorized"):
        SourceOnlyBoundCloudPort(
            operations=h.operations, tower_verifier=h.verifier,
            canonical_scope_resolver=lambda r, o: h.canonical[(r, o)],
        )
    assert h.port.health()["status"] == "SOURCE_ONLY_NO_GO"
