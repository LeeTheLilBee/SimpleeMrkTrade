"""SC004B source-only signed-grant to storage binding harness.

No network ingress, production mode, Tower private key, mTLS implementation,
caller-controlled StorageContext or live Vault registry is introduced. The
trusted scope resolver MUST be an independent authenticated Vault canonical
record lookup, never request JSON. A fresh Tower-signed grant is consumed before
EVERY source operation; SC001's default-deny gate remains independently active.
"""
from __future__ import annotations

import hmac
from collections.abc import Callable

from .backup import IndependentBackupService
from .contracts import (
    AccessDenied, BackupReceipt, CloudError, IntegrityError, StorageReceipt,
)
from .operations import JournaledCiphertextOperations
from .journaled_backup import JournaledBackupOperations
from .recovery_drill import SyntheticRecoveryEvidence, run_source_restore_drill
from .tower_grants import (
    AuthorizedCloudInvocation, SignedTowerGrant, SourceOnlyTowerGrantVerifier,
    TrustedVaultScope,
)

CanonicalScopeResolver = Callable[[str, str], TrustedVaultScope]
CanonicalBackupResolver = Callable[[str], BackupReceipt]


class SourceOnlyBoundCloudPort:
    """An executable source contract, intentionally NOT a production receiver.

    Request ID is an opaque lookup key into the trusted test Vault registry,
    not a source of permission. No client-supplied object/digest/context is
    forwarded. A signed reconciliation grant uses the ORIGINAL write request ID
    with a fresh nonce/current Tower policy and exact canonical object/hash.
    """

    def __init__(
        self, *, operations: JournaledCiphertextOperations,
        tower_verifier: SourceOnlyTowerGrantVerifier,
        canonical_scope_resolver: CanonicalScopeResolver,
        backup: IndependentBackupService | None = None,
        journaled_backup: JournaledBackupOperations | None = None,
        canonical_backup_resolver: CanonicalBackupResolver | None = None,
        mode: str = "disabled",
    ):
        if mode != "source_test":
            raise CloudError("signed Cloud storage transport not authorized")
        if not isinstance(operations, JournaledCiphertextOperations) or not isinstance(
            tower_verifier, SourceOnlyTowerGrantVerifier
        ) or not callable(canonical_scope_resolver):
            raise CloudError("separate source journal, signed verifier and Vault lookup required")
        if backup is not None and (
            not isinstance(backup, IndependentBackupService) or
            backup.source is not operations.source or
            not isinstance(journaled_backup, JournaledBackupOperations) or
            journaled_backup.backup is not backup or
            journaled_backup.operations is not operations or
            not callable(canonical_backup_resolver)
        ):
            raise CloudError("backup requires same journaled source and trusted receipt resolver")
        if backup is None and (
            canonical_backup_resolver is not None or journaled_backup is not None
        ):
            raise CloudError("backup components must be configured together")
        self._operations = operations
        self._tower = tower_verifier
        self._resolve = canonical_scope_resolver
        self._backup = backup
        self._journaled_backup = journaled_backup
        self._resolve_backup = canonical_backup_resolver

    def _invocation(
        self, *, grant: SignedTowerGrant, authenticated_transport_peer: object,
        request_id: str, operation: str,
    ) -> AuthorizedCloudInvocation:
        if not isinstance(request_id, str) or not request_id:
            raise AccessDenied("canonical Vault record reference required")
        # The resolver is an injected trusted application/storage seam, not an
        # incoming JSON object. Fail closed when canonical state is unavailable.
        try:
            expected = self._resolve(request_id, operation)
        except Exception as exc:
            raise AccessDenied("canonical Vault scope unavailable") from exc
        if not isinstance(expected, TrustedVaultScope) or (
            expected.request_id != request_id or expected.operation != operation
        ):
            raise AccessDenied("canonical Vault request/operation mismatch")
        invocation = self._tower.verify_and_consume(
            grant=grant, authenticated_transport_peer=authenticated_transport_peer,
            expected=expected,
        )
        if invocation.context.operation != operation:
            raise AccessDenied("signed operation mismatch")
        return invocation

    def write(
        self, *, grant: SignedTowerGrant, authenticated_transport_peer: object,
        request_id: str, envelope: bytes,
    ) -> StorageReceipt:
        invocation = self._invocation(
            grant=grant, authenticated_transport_peer=authenticated_transport_peer,
            request_id=request_id, operation="WRITE_CIPHERTEXT",
        )
        # No ref/hash/context accepted from client; source operations perform
        # independent VLT1, bounded-size and SHA-256 checks before durable PUT.
        return self._operations.put_if_absent(
            context=invocation.context, object_ref=invocation.object_ref,
            envelope=envelope, expected_sha256=invocation.ciphertext_sha256,
        )

    def read_encrypted(
        self, *, grant: SignedTowerGrant, authenticated_transport_peer: object,
        request_id: str,
    ) -> bytes:
        invocation = self._invocation(
            grant=grant, authenticated_transport_peer=authenticated_transport_peer,
            request_id=request_id, operation="READ_CIPHERTEXT",
        )
        # VLT1 still encrypted. NO direct app/owner download route is exposed.
        return self._operations.get(
            context=invocation.context, object_ref=invocation.object_ref,
            expected_sha256=invocation.ciphertext_sha256,
        )

    def reconcile_original_write(
        self, *, grant: SignedTowerGrant, authenticated_transport_peer: object,
        original_request_id: str,
    ) -> dict:
        invocation = self._invocation(
            grant=grant, authenticated_transport_peer=authenticated_transport_peer,
            request_id=original_request_id, operation="RECONCILE_WRITE",
        )
        # Additional independent SC002 gate ensures the original append-only
        # intent is the exact entity/ref/digest signed by Tower now. Its nonce
        # and decision MUST be fresh even though the logical ID is original.
        namespace = self._operations.source._gate(
            invocation.context, "RECONCILE_WRITE",
        )
        intent = self._operations.journal.intent(
            namespace=namespace, request_id=original_request_id,
        )
        if intent["object_ref"] != invocation.object_ref or not hmac.compare_digest(
            intent["ciphertext_sha256"], invocation.ciphertext_sha256,
        ):
            raise AccessDenied("Tower grant differs from original durable write intent")
        result = self._operations.reconcile_write(
            context=invocation.context, original_request_id=original_request_id,
        )
        if result["vault_archive_committed"] is not False:
            raise IntegrityError("Cloud reconciliation cannot commit Vault archive")
        return result

    def create_encrypted_backup(
        self, *, grant: SignedTowerGrant, authenticated_transport_peer: object,
        request_id: str,
    ) -> BackupReceipt:
        if self._backup is None:
            raise AccessDenied("independent backup service not configured")
        invocation = self._invocation(
            grant=grant, authenticated_transport_peer=authenticated_transport_peer,
            request_id=request_id, operation="BACKUP_CIPHERTEXT",
        )
        return self._journaled_backup.create(
            context=invocation.context,
            source_object_ref=invocation.object_ref,
            source_ciphertext_sha256=invocation.ciphertext_sha256,
        )

    def reconcile_original_backup(
        self, *, grant: SignedTowerGrant, authenticated_transport_peer: object,
        original_request_id: str,
    ) -> dict:
        if self._journaled_backup is None:
            raise AccessDenied("durable independent backup not configured")
        invocation = self._invocation(
            grant=grant, authenticated_transport_peer=authenticated_transport_peer,
            request_id=original_request_id, operation="RECONCILE_BACKUP",
        )
        # Signed grant binds the ORIGINAL source object/hash. The journal
        # alone supplies the opaque generated backup ref that may have been
        # lost when provider ACK timed out; the caller cannot replace it.
        return self._journaled_backup.reconcile_original_backup(
            context=invocation.context, original_request_id=original_request_id,
            canonical_source_object_ref=invocation.object_ref,
            canonical_source_sha256=invocation.ciphertext_sha256,
        )

    def verify_backup_copy(
        self, *, grant: SignedTowerGrant, authenticated_transport_peer: object,
        request_id: str,
    ) -> SyntheticRecoveryEvidence:
        if self._backup is None or self._resolve_backup is None:
            raise AccessDenied("independent trusted backup lookup not configured")
        invocation = self._invocation(
            grant=grant, authenticated_transport_peer=authenticated_transport_peer,
            request_id=request_id, operation="VERIFY_BACKUP",
        )
        try:
            receipt = self._resolve_backup(request_id)
        except Exception as exc:
            raise AccessDenied("canonical backup receipt unavailable") from exc
        if not isinstance(receipt, BackupReceipt) or (
            receipt.backup_ref != invocation.object_ref or
            not hmac.compare_digest(
                receipt.backup_sha256, invocation.ciphertext_sha256
            )
        ):
            raise AccessDenied("signed backup ref/hash differs from canonical Vault receipt")
        # Isolated SC005 source drill returns only metrics/status. No plaintext,
        # primary overwrite, actual Vault restore/receipt or DR certification.
        return run_source_restore_drill(
            backup=self._backup, journal=self._operations.journal,
            context=invocation.context, receipt=receipt,
            expected_inner_sha256=receipt.source_ciphertext_sha256,
            drill_id=request_id, mode="source_test",
        )

    def health(self) -> dict:
        status = self._operations.health()
        return {
            **status,
            "source_bound_grant_contract": True,
            "real_tower_issuer_connected": False,
            "real_vault_canonical_registry_connected": False,
            "independent_peer_transport_certified": False,
            "hosted_receiver_enabled": False,
            "vault_archive_commit_authorized": False,
            "production_authorized": False,
            "status": "SOURCE_ONLY_NO_GO",
        }
