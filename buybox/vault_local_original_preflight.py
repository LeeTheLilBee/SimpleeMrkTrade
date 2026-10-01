"""BBX032–036: read-only local encrypted-original integrity preflight.

This is NOT malware scanning, Tower identity, Vault authorization, secure
transfer, proof of title, or archival. It checks only the saved current BuyBox
source + newest persisted frozen snapshot + locally decrypted original bytes.
No transport, user-facing URL or byte-bearing return value is supplied.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from typing import Any

from .documents import PrivateDocumentStore, _check_magic
from .tower_action_draft import (
    BuyBoxTowerActionPreparationError, stored_source_snapshot,
)
from .tower_evidence import MIMES


class LocalVaultOriginalPreflightError(ValueError):
    """Safe local failure; do not expose original bytes or filesystem paths."""


def _sha(value: Any) -> str:
    try:
        encoded = json.dumps(
            value, sort_keys=True, separators=(",", ":"), allow_nan=False,
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()
    except (TypeError, ValueError) as exc:
        raise LocalVaultOriginalPreflightError("FROZEN_SNAPSHOT_INVALID") from exc


def verify_latest_local_original_unsent(
    db: sqlite3.Connection, documents: PrivateDocumentStore, *,
    opportunity_id: str, evidence_id: str, artifact_id: str, snapshot_id: str,
) -> dict[str, Any]:
    """Return only an unsubmitted local inspection record, never an archive grant.

    Freeze normally stores its source opportunity version N, then the ordinary
    optimistic save stores the frozen snapshot at revision N+1. A later edit
    makes that previously frozen snapshot stale; require a new freeze and save.
    """
    if not isinstance(db, sqlite3.Connection) or not isinstance(documents, PrivateDocumentStore):
        raise LocalVaultOriginalPreflightError("CERTIFIED_LOCAL_STORE_REQUIRED")
    if any(not isinstance(v, str) or not v or len(v) > 128 for v in (
        opportunity_id, evidence_id, artifact_id, snapshot_id,
    )):
        raise LocalVaultOriginalPreflightError("SOURCE_IDENTIFIERS_INVALID")
    try:
        current = stored_source_snapshot(db, opportunity_id)
        row = db.execute(
            "SELECT current_json FROM opportunities WHERE id=?", (opportunity_id,)
        ).fetchone()
        if row is None:
            raise LocalVaultOriginalPreflightError("CURRENT_SOURCE_NOT_SAVED")
        op = json.loads(row["current_json"])
        if not isinstance(op, dict):
            raise LocalVaultOriginalPreflightError("CURRENT_SOURCE_INVALID")
    except (BuyBoxTowerActionPreparationError, sqlite3.DatabaseError, ValueError, TypeError) as exc:
        raise LocalVaultOriginalPreflightError("CURRENT_SOURCE_NOT_VERIFIED") from exc

    artifacts = [
        x for x in op.get("artifacts", [])
        if isinstance(x, dict) and x.get("id") == artifact_id
    ]
    evidence = [
        x for x in op.get("evidence", [])
        if isinstance(x, dict) and x.get("id") == evidence_id
    ]
    frozen = [
        x for x in op.get("snapshots", [])
        if isinstance(x, dict) and x.get("snapshot_id") == snapshot_id
    ]
    if len(artifacts) != 1 or len(evidence) != 1 or len(frozen) != 1:
        raise LocalVaultOriginalPreflightError("EXACT_SAVED_ARTIFACT_EVIDENCE_SNAPSHOT_REQUIRED")
    artifact, claim, snapshot = artifacts[0], evidence[0], frozen[0]
    if claim.get("artifact_id") != artifact_id:
        raise LocalVaultOriginalPreflightError("SOURCE_EVIDENCE_LINK_MISMATCH")
    if artifact.get("mime") not in MIMES:
        # CSV is allowed in local BuyBox intake but excluded from PR #35's
        # canonical Vault metadata-only v1 declared MIME allowlist.
        raise LocalVaultOriginalPreflightError("MIME_NOT_IN_CANONICAL_VAULT_V1_CONTRACT")
    source_revision = snapshot.get("opportunity_revision")
    if (
        snapshot.get("deal_id") != opportunity_id
        or snapshot.get("archive_state") != "NOT_REQUESTED"
        or snapshot.get("authorizes_action") is not False
        or type(source_revision) is not int
        or source_revision + 1 != current["opportunity_revision"]
    ):
        raise LocalVaultOriginalPreflightError("LATEST_PERSISTED_FROZEN_SNAPSHOT_REQUIRED")
    material = {key: value for key, value in snapshot.items() if key != "snapshot_sha256"}
    if snapshot.get("snapshot_sha256") != _sha(material):
        raise LocalVaultOriginalPreflightError("FROZEN_SNAPSHOT_DIGEST_MISMATCH")
    versions = snapshot.get("evidence_versions")
    if (
        not isinstance(versions, list)
        or len(versions) != 1
        or not isinstance(versions[0], dict)
        or versions[0] != {
            "evidence_id": evidence_id,
            "source_document_id": artifact_id,
            "source_version_id": artifact_id,
            "sha256": artifact.get("sha256"),
            "evidence_state": claim.get("status"),
        }
    ):
        raise LocalVaultOriginalPreflightError("FROZEN_DOCUMENT_LINEAGE_MISMATCH")

    expected_size, expected_hash = artifact.get("size_bytes"), artifact.get("sha256")
    if (
        type(expected_size) is not int or expected_size <= 0
        or not isinstance(expected_hash, str) or len(expected_hash) != 64
    ):
        raise LocalVaultOriginalPreflightError("SOURCE_DOCUMENT_DESCRIPTOR_INVALID")
    try:
        original = documents.read(artifact)
        if (
            len(original) != expected_size
            or hashlib.sha256(original).hexdigest() != expected_hash
            or not _check_magic(original, artifact["mime"])
        ):
            raise LocalVaultOriginalPreflightError("LOCAL_ORIGINAL_INTEGRITY_INVALID")
    except (ValueError, OSError, KeyError, TypeError) as exc:
        raise LocalVaultOriginalPreflightError("LOCAL_ORIGINAL_UNAVAILABLE_OR_INVALID") from exc
    finally:
        # Python cannot guarantee complete zeroization; never return/log bytes.
        original = None

    return {
        "schema_version": "buybox.vault.local_original_preflight.v1",
        "state": "LOCAL_ORIGINAL_VERIFIED_UNSENT",
        "opportunity_id": opportunity_id,
        "opportunity_revision": current["opportunity_revision"],
        "input_snapshot_digest": current["input_snapshot_digest"],
        "evidence_id": evidence_id,
        "artifact_id": artifact_id,
        "snapshot_id": snapshot_id,
        "snapshot_sha256": snapshot["snapshot_sha256"],
        "original_sha256": expected_hash,
        "mime_type": artifact["mime"],
        "size_bytes": expected_size,
        "tower_identity_verified": False,
        "tower_owner_approval_verified": False,
        "malware_scan_verified": False,
        "vault_issuer_receipt_present": False,
        "vault_archived": False,
        "original_transferred": False,
        "external_request_made": False,
        "authorizes_download": False,
        "authorizes_acquisition": False,
    }
