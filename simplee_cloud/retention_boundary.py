"""SC032 source-only Vault retention/disposition boundary.

Cloud stores opaque ciphertext. Vault owns retention/legal-hold/disposition
semantics. Even a valid disposition review MUST NOT become Cloud deletion
authority; a future deletion protocol requires independent Tower/Vault design,
provider semantics, owner acceptance and separate source review.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from .contracts import CloudError, valid_object_ref, valid_sha256

_ID = re.compile(r"[A-Za-z0-9_.:-]{1,128}\Z")


@dataclass(frozen=True)
class TrustedVaultRetentionScope:
    """Trusted server-side metadata from Vault, never request JSON authority."""

    version_id: str
    object_ref: str
    ciphertext_sha256: str
    archival_retention_policy_id: str
    governance_policy_id: str
    legal_hold: bool
    disposition_blocked: bool
    disposition_reviewed: bool


def source_retention_disposition_status(
    scope: TrustedVaultRetentionScope,
) -> dict:
    """Validate a Vault retention snapshot and return an unconditional delete HOLD."""
    if not isinstance(scope, TrustedVaultRetentionScope):
        raise CloudError("trusted Vault retention scope required")
    for value in (
        scope.version_id,
        scope.archival_retention_policy_id,
        scope.governance_policy_id,
    ):
        if not isinstance(value, str) or not _ID.fullmatch(value):
            raise CloudError("invalid trusted Vault retention identifier")
    if not valid_object_ref(scope.object_ref) or not valid_sha256(
        scope.ciphertext_sha256
    ):
        raise CloudError("invalid canonical Cloud object retention binding")
    if any(
        type(value) is not bool
        for value in (
            scope.legal_hold,
            scope.disposition_blocked,
            scope.disposition_reviewed,
        )
    ):
        raise CloudError("invalid Vault retention state")

    if scope.archival_retention_policy_id != scope.governance_policy_id:
        raise CloudError("Vault archival and governance retention policy mismatch")
    if scope.legal_hold and not scope.disposition_blocked:
        raise CloudError("legal hold must block disposition")
    if scope.legal_hold and scope.disposition_reviewed:
        raise CloudError("held evidence cannot be disposition reviewed")
    if scope.disposition_reviewed and scope.disposition_blocked:
        raise CloudError("reviewed disposition cannot remain governance-blocked")

    return {
        "schema": "simplee.cloud.retention-disposition-boundary.v1",
        "status": (
            "SOURCE_ONLY_DISPOSITION_REVIEWED_NO_DELETE"
            if scope.disposition_reviewed
            else "SOURCE_ONLY_RETENTION_HOLD"
        ),
        "retention_policy_match": True,
        "legal_hold": scope.legal_hold,
        "disposition_blocked": scope.disposition_blocked,
        "disposition_reviewed": scope.disposition_reviewed,
        "cloud_delete_capability_exposed": False,
        "provider_delete_authorized": False,
        "vault_canonical_receipt_deleted": False,
        "backup_delete_authorized": False,
        "future_separate_tower_vault_deletion_protocol_required": True,
        "owner_release_required": True,
        "production_authorized": False,
    }
