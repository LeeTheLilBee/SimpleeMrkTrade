"""SC018: actual Vault ARCHIVED primary record is necessary but not sufficient for backup verify.

A separate canonical backup receipt is required. This test-only adapter joins the
actual merged Vault archival workflow/registry metadata to Cloud's durable
BackupReceipt without creating a runtime Vault API or direct Cloud DB connection.
"""
import sqlite3
from dataclasses import replace

import pytest

from simplee_cloud.bound_port import SourceOnlyBoundCloudPort
from simplee_cloud.contracts import AccessDenied, BackupReceipt
from simplee_cloud.tests.test_sc004b_bound_port import Harness, PEER
from simplee_cloud.tests.test_sc008_vault_finalization import SyntheticVaultAcceptance
from simplee_cloud.tower_grants import TrustedVaultScope


class SyntheticCanonicalBackupScope:
    """Test-only authoritative join; production belongs to Vault/Tower service."""
    def __init__(self, vault_journal, registry):
        self.vault_journal = vault_journal
        self.registry = registry
        self.assignments = {}

    def assign(self, *, verify_request_id, archival_request_id, receipt_id,
               entity_id, backup_receipt):
        self.assignments[verify_request_id] = {
            "archival_request_id": archival_request_id,
            "receipt_id": receipt_id,
            "entity_id": entity_id,
            "backup_receipt": backup_receipt,
        }

    def _resolved(self, request_id):
        try:
            item = self.assignments[request_id]
        except KeyError as exc:
            raise AccessDenied("canonical backup assignment unavailable") from exc
        original_request = item["archival_request_id"]
        if not self.vault_journal.verify_chain(original_request) or (
            self.vault_journal.status(original_request) != "ARCHIVED"
        ):
            raise AccessDenied("Vault source workflow is not verified ARCHIVED")
        with sqlite3.connect(
            "file:" + self.registry.path + "?mode=ro", uri=True,
        ) as db:
            row = db.execute(
                """SELECT object_ref,ciphertext_sha256,version_id,retention_policy_id
                   FROM archival_receipts
                   WHERE receipt_id=? AND request_id=? AND entity_id=?""",
                (item["receipt_id"], original_request, item["entity_id"]),
            ).fetchone()
        if row is None:
            raise AccessDenied("canonical primary archival receipt unavailable")
        receipt = item["backup_receipt"]
        if not isinstance(receipt, BackupReceipt):
            raise AccessDenied("separate canonical backup receipt unavailable")
        if (
            receipt.source_object_ref != row[0] or
            receipt.source_ciphertext_sha256 != row[1]
        ):
            raise AccessDenied("backup receipt source differs from canonical archive")
        if not row[2] or not row[3]:
            raise AccessDenied("canonical version/retention metadata unavailable")
        return item, receipt

    def __call__(self, request_id, operation):
        if operation != "VERIFY_BACKUP":
            raise AccessDenied("backup-verification-only synthetic Vault scope")
        item, receipt = self._resolved(request_id)
        return TrustedVaultScope(
            request_id=request_id,
            entity_id=item["entity_id"],
            purpose="archive",
            operation="VERIFY_BACKUP",
            classification="owner_private",
            object_ref=receipt.backup_ref,
            ciphertext_sha256=receipt.backup_sha256,
        )

    def backup_receipt(self, request_id):
        _, receipt = self._resolved(request_id)
        return receipt


class MustNeverGetBackup:
    def __init__(self, wrapped):
        self.wrapped = wrapped
        self.get_calls = 0

    def put_if_absent(self, namespace, ref, body):
        return self.wrapped.put_if_absent(namespace, ref, body)

    def get(self, namespace, ref):
        self.get_calls += 1
        raise AssertionError("backup bytes must not be read before canonical proof")


def prepared(tmp_path, *, archive=True):
    h = Harness(tmp_path / "cloud")
    step = SyntheticVaultAcceptance(tmp_path / "vault", h)
    write_receipt = step.write()
    if archive:
        step.finalized_after_independent_source_check(write_receipt)
    backup = h.port.create_encrypted_backup(
        grant=h.grant("backup-1", "BACKUP_CIPHERTEXT"),
        authenticated_transport_peer=PEER,
        request_id="backup-1",
    )
    scope = SyntheticCanonicalBackupScope(step.journal, step.registry)
    port = SourceOnlyBoundCloudPort(
        operations=h.operations,
        tower_verifier=h.verifier,
        canonical_scope_resolver=scope,
        backup=h.backup,
        journaled_backup=h.journaled_backup,
        canonical_backup_resolver=scope.backup_receipt,
        mode="source_test",
    )
    return h, step, backup, scope, port


def assign(scope, backup, *, request="verify-1", archival="write-1",
           receipt="receipt-write-1", entity="trust"):
    scope.assign(
        verify_request_id=request,
        archival_request_id=archival,
        receipt_id=receipt,
        entity_id=entity,
        backup_receipt=backup,
    )


def verify(h, port, backup, *, request="verify-1", entity="trust",
           ref=None, digest=None):
    return port.verify_backup_copy(
        grant=h.grant(
            request,
            "VERIFY_BACKUP",
            entity=entity,
            ref=backup.backup_ref if ref is None else ref,
            digest=backup.backup_sha256 if digest is None else digest,
            canonical=False,
        ),
        authenticated_transport_peer=PEER,
        request_id=request,
    )


def test_actual_vault_archived_primary_plus_separate_backup_receipt_allows_source_verify(tmp_path):
    h, step, backup, scope, port = prepared(tmp_path)
    assign(scope, backup)
    evidence = verify(h, port, backup)
    assert evidence.verified_ciphertext is True
    assert evidence.primary_rewritten is False
    assert evidence.vault_original_authenticated is False
    assert evidence.external_failure_domain_verified is False
    assert evidence.production_recovery_authorized is False
    assert port.health()["production_authorized"] is False


def test_primary_archival_registry_alone_cannot_authorize_backup_restore(tmp_path):
    h, step, backup, scope, port = prepared(tmp_path)
    scope.assign(
        verify_request_id="verify-1",
        archival_request_id="write-1",
        receipt_id="receipt-write-1",
        entity_id="trust",
        backup_receipt=None,
    )
    original = h.backup.backup_backend
    guard = MustNeverGetBackup(original)
    h.backup.backup_backend = guard
    with pytest.raises(AccessDenied, match="canonical Vault scope unavailable"):
        verify(h, port, backup)
    assert guard.get_calls == 0


def test_physical_backup_without_canonical_assignment_cannot_be_read(tmp_path):
    h, step, backup, scope, port = prepared(tmp_path)
    original = h.backup.backup_backend
    guard = MustNeverGetBackup(original)
    h.backup.backup_backend = guard
    with pytest.raises(AccessDenied, match="canonical Vault scope unavailable"):
        verify(h, port, backup)
    assert guard.get_calls == 0


@pytest.mark.parametrize("field", ["source_ref", "source_sha"])
def test_backup_receipt_must_bind_exact_actual_vault_archived_primary(tmp_path, field):
    h, step, backup, scope, port = prepared(tmp_path)
    forged = replace(
        backup,
        **({
            "source_object_ref": h.source.new_object_ref()
        } if field == "source_ref" else {
            "source_ciphertext_sha256": "0" * 64
        }),
    )
    assign(scope, forged)
    original = h.backup.backup_backend
    guard = MustNeverGetBackup(original)
    h.backup.backup_backend = guard
    with pytest.raises(AccessDenied, match="canonical Vault scope unavailable"):
        verify(h, port, forged)
    assert guard.get_calls == 0


def test_vault_must_be_archived_before_backup_verification(tmp_path):
    h, step, backup, scope, port = prepared(tmp_path, archive=False)
    assign(scope, backup)
    original = h.backup.backup_backend
    guard = MustNeverGetBackup(original)
    h.backup.backup_backend = guard
    with pytest.raises(AccessDenied, match="canonical Vault scope unavailable"):
        verify(h, port, backup)
    assert guard.get_calls == 0
    assert step.journal.status("write-1") == "ENCRYPTED"


@pytest.mark.parametrize("wrong", ["entity", "receipt", "archival_request"])
def test_wrong_vault_primary_identity_cannot_authorize_backup(tmp_path, wrong):
    h, step, backup, scope, port = prepared(tmp_path)
    values = {
        "request": "verify-wrong",
        "archival": "write-1",
        "receipt": "receipt-write-1",
        "entity": "trust",
    }
    if wrong == "entity":
        values["entity"] = "foreign-entity"
    elif wrong == "receipt":
        values["receipt"] = "not-a-receipt"
    else:
        values["archival"] = "foreign-write"
    assign(
        scope, backup,
        request=values["request"],
        archival=values["archival"],
        receipt=values["receipt"],
        entity=values["entity"],
    )
    with pytest.raises(AccessDenied):
        verify(
            h, port, backup,
            request=values["request"],
            entity=values["entity"],
        )


def test_primary_object_ref_cannot_be_reused_as_verify_backup_grant_ref(tmp_path):
    h, step, backup, scope, port = prepared(tmp_path)
    assign(scope, backup)
    with pytest.raises(AccessDenied, match="object reference does not match operation"):
        verify(h, port, backup, ref=h.ref)


@pytest.mark.parametrize("wrong", ["backup_ref", "backup_sha"])
def test_signed_backup_ref_and_digest_must_match_separate_canonical_backup_receipt(tmp_path, wrong):
    h, step, backup, scope, port = prepared(tmp_path)
    assign(scope, backup)
    with pytest.raises(AccessDenied, match="trusted Vault scope"):
        verify(
            h, port, backup,
            ref=("backups/" + "f" * 48) if wrong == "backup_ref" else None,
            digest=("0" * 64) if wrong == "backup_sha" else None,
        )


def test_tampered_actual_vault_workflow_blocks_backup_before_physical_get(tmp_path):
    h, step, backup, scope, port = prepared(tmp_path)
    assign(scope, backup)
    with sqlite3.connect(step.journal.path) as db:
        db.execute("DROP TRIGGER events_no_update")
        db.execute(
            "UPDATE workflow_events SET to_state='REJECTED' "
            "WHERE request_id='write-1' AND step=1"
        )
    original = h.backup.backup_backend
    guard = MustNeverGetBackup(original)
    h.backup.backup_backend = guard
    with pytest.raises(AccessDenied, match="canonical Vault scope unavailable"):
        verify(h, port, backup)
    assert guard.get_calls == 0
