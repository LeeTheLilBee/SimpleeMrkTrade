
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SECTION = "ARCHIVE VAULT — OWNER SAFE PREVIEW LOCK PREP LAYER / GP331-GP340"
LAYER_ID = "vault_gp331_340_owner_safe_preview_lock_prep_layer"
READINESS_LABEL = "Owner safe preview lock prep layer ready"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "vault_owner_safe_preview_lock_prep_layer.sqlite"

try:
    from vault.owner_owned_file_storage_foundation_layer_service import calculate_sha256_bytes
    from vault.owner_folder_browse_metadata_layer_service import (
        get_folder_file_row_payload_builder,
        get_folder_browse_index_builder,
        validate_owner_folder_browse_metadata_layer,
    )
except Exception as exc:
    raise RuntimeError(
        "GP331-GP340 requires GP321-GP330 owner folder browse metadata layer first."
    ) from exc


PREVIEW_ALLOWED_MIME_TYPES = {
    "application/pdf": {
        "preview_family": "pdf",
        "safe_preview_prep_state": "eligible_policy_only",
        "content_extraction_allowed": False,
        "rendering_allowed": False,
    },
    "image/png": {
        "preview_family": "image",
        "safe_preview_prep_state": "eligible_policy_only",
        "content_extraction_allowed": False,
        "rendering_allowed": False,
    },
    "image/jpeg": {
        "preview_family": "image",
        "safe_preview_prep_state": "eligible_policy_only",
        "content_extraction_allowed": False,
        "rendering_allowed": False,
    },
    "text/plain": {
        "preview_family": "text",
        "safe_preview_prep_state": "eligible_policy_only",
        "content_extraction_allowed": False,
        "rendering_allowed": False,
    },
    "application/json": {
        "preview_family": "structured_text",
        "safe_preview_prep_state": "eligible_policy_only",
        "content_extraction_allowed": False,
        "rendering_allowed": False,
    },
    "text/csv": {
        "preview_family": "structured_text",
        "safe_preview_prep_state": "eligible_policy_only",
        "content_extraction_allowed": False,
        "rendering_allowed": False,
    },
}

PREVIEW_BLOCKED_MIME_TYPES = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx preview requires a later document-safe renderer",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx preview requires a later spreadsheet-safe renderer",
    "application/octet-stream": "binary files require explicit owner review",
    "application/x-msdownload": "executable files are never preview eligible",
}

LOCKS = {
    "owner_safe_preview_lock_prep_layer": True,
    "preview_eligibility_metadata_allowed": True,
    "preview_mime_policy_allowed": True,
    "preview_redaction_policy_allowed": True,
    "owner_preview_approval_lock_allowed": True,
    "preview_route_payload_draft_allowed": True,
    "preview_receipt_draft_allowed": True,
    "preview_safety_review_queue_allowed": True,
    "object_body_read_allowed": False,
    "plaintext_content_extraction_allowed": False,
    "preview_rendering_allowed": False,
    "preview_endpoint_execution_allowed": False,
    "preview_cache_write_allowed": False,
    "preview_cache_read_allowed": False,
    "file_preview_unlocked": False,
    "file_download_unlocked": False,
    "file_share_unlocked": False,
    "file_delete_unlocked": False,
    "file_restore_unlocked": False,
    "quarantine_release_allowed": False,
    "quarantine_object_move_allowed": False,
    "public_upload_unlocked": False,
    "beta_upload_unlocked": False,
    "provider_upload_unlocked": False,
    "provider_storage_required": False,
    "external_sync_unlocked": False,
}

PACKS = [
    {"gp": 331, "title": "Owner Safe Preview Lock Prep Shell", "status": "ready", "route": "/vault/owner-safe-preview-lock-prep-shell.json"},
    {"gp": 332, "title": "Preview Eligibility Policy Board", "status": "ready", "route": "/vault/preview-eligibility-policy-board.json"},
    {"gp": 333, "title": "Preview MIME Type Contract", "status": "ready", "route": "/vault/preview-mime-type-contract.json"},
    {"gp": 334, "title": "Preview Redaction Policy Board", "status": "ready", "route": "/vault/preview-redaction-policy-board.json"},
    {"gp": 335, "title": "Owner Preview Approval Lock Board", "status": "ready", "route": "/vault/owner-preview-approval-lock-board.json"},
    {"gp": 336, "title": "Preview Route Payload Draft Builder", "status": "ready", "route": "/vault/preview-route-payload-draft-builder.json"},
    {"gp": 337, "title": "Preview Receipt Draft Ledger", "status": "ready", "route": "/vault/preview-receipt-draft-ledger.json"},
    {"gp": 338, "title": "Preview Safety Review Queue", "status": "ready", "route": "/vault/preview-safety-review-queue.json"},
    {"gp": 339, "title": "Preview Safety Blocker Board", "status": "ready", "route": "/vault/preview-safety-blocker-board.json"},
    {"gp": 340, "title": "Owner Safe Preview Lock Prep Readiness Checkpoint", "status": "ready", "route": "/vault/owner-safe-preview-lock-prep-readiness-checkpoint.json"},
]

REDACTION_POLICIES = [
    {
        "policy_id": "preview_no_plaintext_extraction",
        "label": "No plaintext extraction during preview prep",
        "field_name": "plaintext_content",
        "policy_state": "blocked",
        "redaction_required": True,
        "reason": "This layer prepares preview policy but does not read or extract file contents.",
    },
    {
        "policy_id": "preview_no_object_body",
        "label": "No object body exposed during preview prep",
        "field_name": "object_body",
        "policy_state": "blocked",
        "redaction_required": True,
        "reason": "Preview prep must remain metadata-only.",
    },
    {
        "policy_id": "preview_no_physical_path",
        "label": "No physical quarantine path exposed",
        "field_name": "physical_quarantine_path",
        "policy_state": "hidden",
        "redaction_required": True,
        "reason": "Physical storage internals remain hidden from preview payloads.",
    },
    {
        "policy_id": "preview_allow_identity_metadata",
        "label": "Allow identity metadata",
        "field_name": "identity_metadata",
        "policy_state": "visible",
        "redaction_required": False,
        "reason": "Safe preview prep can show filename, MIME type, size, hash, lane, and lock state.",
    },
    {
        "policy_id": "preview_allow_receipt_reference",
        "label": "Allow receipt reference metadata",
        "field_name": "receipt_reference",
        "policy_state": "visible",
        "redaction_required": False,
        "reason": "Receipts are metadata references, not file content.",
    },
]

BLOCKERS = [
    {
        "blocker_id": "no_object_body_read",
        "label": "Object body read remains locked",
        "blocked_action": "object_body_read",
        "allowed": False,
        "reason": "Safe preview prep does not open, read, stream, decode, or render file bodies.",
    },
    {
        "blocker_id": "no_plaintext_extraction",
        "label": "Plaintext extraction remains locked",
        "blocked_action": "plaintext_extraction",
        "allowed": False,
        "reason": "Text extraction belongs to a later controlled preview execution layer.",
    },
    {
        "blocker_id": "no_preview_rendering",
        "label": "Preview rendering remains locked",
        "blocked_action": "preview_rendering",
        "allowed": False,
        "reason": "This layer prepares policy and approval locks only.",
    },
    {
        "blocker_id": "no_preview_endpoint_execution",
        "label": "Preview endpoint execution remains locked",
        "blocked_action": "preview_endpoint_execution",
        "allowed": False,
        "reason": "No route in this layer may return rendered content.",
    },
    {
        "blocker_id": "no_preview_cache_write",
        "label": "Preview cache write remains locked",
        "blocked_action": "preview_cache_write",
        "allowed": False,
        "reason": "No preview artifacts are created in this layer.",
    },
    {
        "blocker_id": "no_preview_cache_read",
        "label": "Preview cache read remains locked",
        "blocked_action": "preview_cache_read",
        "allowed": False,
        "reason": "No preview cache exists yet.",
    },
    {
        "blocker_id": "no_download",
        "label": "Download remains locked",
        "blocked_action": "file_download",
        "allowed": False,
        "reason": "Preview prep does not unlock download.",
    },
    {
        "blocker_id": "no_share",
        "label": "Sharing remains locked",
        "blocked_action": "file_share",
        "allowed": False,
        "reason": "Sharing belongs to a later access/share layer.",
    },
    {
        "blocker_id": "no_delete",
        "label": "Delete remains locked",
        "blocked_action": "file_delete",
        "allowed": False,
        "reason": "Delete remains trash/recovery locked.",
    },
    {
        "blocker_id": "no_restore",
        "label": "Restore remains locked",
        "blocked_action": "file_restore",
        "allowed": False,
        "reason": "Restore belongs to a later recovery approval layer.",
    },
    {
        "blocker_id": "no_quarantine_release",
        "label": "Quarantine release remains locked",
        "blocked_action": "quarantine_release",
        "allowed": False,
        "reason": "Preview prep does not move or release physical objects.",
    },
    {
        "blocker_id": "no_public_upload",
        "label": "Public upload remains locked",
        "blocked_action": "public_upload",
        "allowed": False,
        "reason": "Preview prep does not expose public upload.",
    },
    {
        "blocker_id": "no_beta_upload",
        "label": "Beta upload remains locked",
        "blocked_action": "beta_upload",
        "allowed": False,
        "reason": "Preview prep does not expose beta upload.",
    },
    {
        "blocker_id": "no_provider_upload",
        "label": "Provider upload remains locked",
        "blocked_action": "provider_upload",
        "allowed": False,
        "reason": "Owner-owned storage remains provider-independent.",
    },
    {
        "blocker_id": "no_external_sync",
        "label": "External sync remains locked",
        "blocked_action": "external_sync",
        "allowed": False,
        "reason": "Preview prep does not sync externally.",
    },
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _rows(conn: sqlite3.Connection, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    return [dict(row) for row in conn.execute(query, params).fetchall()]


def _eligibility_id(active_file_id: str) -> str:
    return "preview_eligibility_" + calculate_sha256_bytes(("eligibility|" + active_file_id).encode("utf-8"))[:24]


def _approval_lock_id(active_file_id: str) -> str:
    return "preview_approval_lock_" + calculate_sha256_bytes(("approval|" + active_file_id).encode("utf-8"))[:24]


def _payload_draft_id(active_file_id: str) -> str:
    return "preview_payload_draft_" + calculate_sha256_bytes(("payload|" + active_file_id).encode("utf-8"))[:24]


def _receipt_draft_id(active_file_id: str) -> str:
    return "preview_receipt_draft_" + calculate_sha256_bytes(("receipt|" + active_file_id).encode("utf-8"))[:24]


def _review_queue_id(active_file_id: str) -> str:
    return "preview_review_" + calculate_sha256_bytes(("review|" + active_file_id).encode("utf-8"))[:24]


def _is_allowed_mime(mime_type: str) -> bool:
    return mime_type in PREVIEW_ALLOWED_MIME_TYPES


def _preview_family(mime_type: str) -> str:
    if mime_type in PREVIEW_ALLOWED_MIME_TYPES:
        return PREVIEW_ALLOWED_MIME_TYPES[mime_type]["preview_family"]
    if mime_type in PREVIEW_BLOCKED_MIME_TYPES:
        return "blocked"
    return "unknown_review_required"


def _uncached_initialize_owner_safe_preview_lock_prep_layer() -> Dict[str, Any]:
    previous = validate_owner_folder_browse_metadata_layer()

    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS preview_eligibility_candidates (
                eligibility_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                folder_key TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                safe_stored_name TEXT NOT NULL,
                mission_lane TEXT NOT NULL,
                owner_lane TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,
                mime_type TEXT NOT NULL,
                sha256_hash TEXT NOT NULL,
                preview_family TEXT NOT NULL,
                eligibility_state TEXT NOT NULL,
                policy_eligible INTEGER NOT NULL,
                owner_approval_required INTEGER NOT NULL,
                object_body_read_allowed INTEGER NOT NULL,
                preview_rendering_allowed INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS preview_mime_type_contract (
                mime_type TEXT PRIMARY KEY,
                preview_family TEXT NOT NULL,
                policy_state TEXT NOT NULL,
                allowed_for_future_preview INTEGER NOT NULL,
                content_extraction_allowed INTEGER NOT NULL,
                rendering_allowed INTEGER NOT NULL,
                reason TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS preview_redaction_policies (
                policy_id TEXT PRIMARY KEY,
                label TEXT NOT NULL,
                field_name TEXT NOT NULL,
                policy_state TEXT NOT NULL,
                redaction_required INTEGER NOT NULL,
                reason TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS owner_preview_approval_locks (
                approval_lock_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                eligibility_id TEXT NOT NULL,
                approval_state TEXT NOT NULL,
                owner_approval_required INTEGER NOT NULL,
                approval_recording_allowed INTEGER NOT NULL,
                preview_execution_allowed INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS preview_route_payload_drafts (
                payload_draft_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                eligibility_id TEXT NOT NULL,
                route_state TEXT NOT NULL,
                metadata_only INTEGER NOT NULL,
                object_body_included INTEGER NOT NULL,
                plaintext_content_included INTEGER NOT NULL,
                rendered_preview_included INTEGER NOT NULL,
                download_url_included INTEGER NOT NULL,
                payload_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS preview_receipt_draft_ledger (
                receipt_draft_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                eligibility_id TEXT NOT NULL,
                receipt_state TEXT NOT NULL,
                finalized INTEGER NOT NULL,
                finalization_allowed INTEGER NOT NULL,
                receipt_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS preview_safety_review_queue (
                review_queue_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                eligibility_id TEXT NOT NULL,
                review_state TEXT NOT NULL,
                reviewer_action_allowed INTEGER NOT NULL,
                preview_execution_allowed INTEGER NOT NULL,
                reason TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS preview_safety_blockers (
                blocker_id TEXT PRIMARY KEY,
                label TEXT NOT NULL,
                blocked_action TEXT NOT NULL,
                allowed INTEGER NOT NULL,
                reason TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        now = _now()

        for mime_type, policy in PREVIEW_ALLOWED_MIME_TYPES.items():
            conn.execute(
                """
                INSERT OR REPLACE INTO preview_mime_type_contract (
                    mime_type, preview_family, policy_state,
                    allowed_for_future_preview, content_extraction_allowed,
                    rendering_allowed, reason, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    mime_type,
                    policy["preview_family"],
                    policy["safe_preview_prep_state"],
                    1,
                    1 if policy["content_extraction_allowed"] else 0,
                    1 if policy["rendering_allowed"] else 0,
                    "Allowed for future controlled preview policy only; execution remains locked.",
                    now,
                    now,
                ),
            )

        for mime_type, reason in PREVIEW_BLOCKED_MIME_TYPES.items():
            conn.execute(
                """
                INSERT OR REPLACE INTO preview_mime_type_contract (
                    mime_type, preview_family, policy_state,
                    allowed_for_future_preview, content_extraction_allowed,
                    rendering_allowed, reason, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    mime_type,
                    "blocked",
                    "blocked_or_later_renderer_required",
                    0,
                    0,
                    0,
                    reason,
                    now,
                    now,
                ),
            )

        for policy in REDACTION_POLICIES:
            conn.execute(
                """
                INSERT OR REPLACE INTO preview_redaction_policies (
                    policy_id, label, field_name, policy_state,
                    redaction_required, reason, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    policy["policy_id"],
                    policy["label"],
                    policy["field_name"],
                    policy["policy_state"],
                    1 if policy["redaction_required"] else 0,
                    policy["reason"],
                    now,
                    now,
                ),
            )

        for blocker in BLOCKERS:
            conn.execute(
                """
                INSERT OR REPLACE INTO preview_safety_blockers (
                    blocker_id, label, blocked_action, allowed, reason, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    blocker["blocker_id"],
                    blocker["label"],
                    blocker["blocked_action"],
                    1 if blocker["allowed"] else 0,
                    blocker["reason"],
                    now,
                    now,
                ),
            )

        rows = get_folder_file_row_payload_builder().get("rows", [])

        for row in rows:
            identity = row["identity"]
            active_file_id = row["active_file_id"]
            mime_type = identity["mime_type"]
            eligibility_id = _eligibility_id(active_file_id)
            policy_eligible = _is_allowed_mime(mime_type)
            preview_family = _preview_family(mime_type)
            eligibility_state = "eligible_policy_only_preview_locked" if policy_eligible else "not_eligible_or_review_required_preview_locked"

            conn.execute(
                """
                INSERT OR REPLACE INTO preview_eligibility_candidates (
                    eligibility_id, active_file_id, folder_key, original_filename,
                    safe_stored_name, mission_lane, owner_lane, size_bytes,
                    mime_type, sha256_hash, preview_family, eligibility_state,
                    policy_eligible, owner_approval_required, object_body_read_allowed,
                    preview_rendering_allowed, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    eligibility_id,
                    active_file_id,
                    row["folder_key"],
                    identity["original_filename"],
                    identity["safe_stored_name"],
                    identity["mission_lane"],
                    identity["owner_lane"],
                    identity["size_bytes"],
                    mime_type,
                    identity["sha256_hash"],
                    preview_family,
                    eligibility_state,
                    1 if policy_eligible else 0,
                    1,
                    0,
                    0,
                    now,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO owner_preview_approval_locks (
                    approval_lock_id, active_file_id, eligibility_id,
                    approval_state, owner_approval_required,
                    approval_recording_allowed, preview_execution_allowed,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _approval_lock_id(active_file_id),
                    active_file_id,
                    eligibility_id,
                    "owner_preview_approval_required_locked",
                    1,
                    0,
                    0,
                    now,
                    now,
                ),
            )

            payload_material = {
                "active_file_id": active_file_id,
                "eligibility_id": eligibility_id,
                "original_filename": identity["original_filename"],
                "mime_type": mime_type,
                "preview_family": preview_family,
                "eligibility_state": eligibility_state,
                "metadata_only": True,
                "object_body_included": False,
                "plaintext_content_included": False,
                "rendered_preview_included": False,
                "download_url_included": False,
            }
            payload_hash = calculate_sha256_bytes(repr(sorted(payload_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO preview_route_payload_drafts (
                    payload_draft_id, active_file_id, eligibility_id,
                    route_state, metadata_only, object_body_included,
                    plaintext_content_included, rendered_preview_included,
                    download_url_included, payload_hash, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _payload_draft_id(active_file_id),
                    active_file_id,
                    eligibility_id,
                    "draft_locked_metadata_only",
                    1,
                    0,
                    0,
                    0,
                    0,
                    payload_hash,
                    now,
                    now,
                ),
            )

            receipt_material = {
                "active_file_id": active_file_id,
                "eligibility_id": eligibility_id,
                "sha256_hash": identity["sha256_hash"],
                "receipt_scope": "safe_preview_lock_prep",
                "preview_execution_allowed": False,
                "object_body_read_allowed": False,
            }
            receipt_hash = calculate_sha256_bytes(repr(sorted(receipt_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO preview_receipt_draft_ledger (
                    receipt_draft_id, active_file_id, eligibility_id,
                    receipt_state, finalized, finalization_allowed,
                    receipt_hash, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _receipt_draft_id(active_file_id),
                    active_file_id,
                    eligibility_id,
                    "draft_locked",
                    0,
                    0,
                    receipt_hash,
                    now,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO preview_safety_review_queue (
                    review_queue_id, active_file_id, eligibility_id,
                    review_state, reviewer_action_allowed,
                    preview_execution_allowed, reason, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _review_queue_id(active_file_id),
                    active_file_id,
                    eligibility_id,
                    "queued_for_future_preview_safety_review_locked",
                    0,
                    0,
                    "Preview safety review exists as a queue record only; no reviewer action or preview execution allowed.",
                    now,
                    now,
                ),
            )

        conn.commit()

    return {
        "initialized": True,
        "previous_folder_browse_metadata_ready": bool(previous.get("ready", False)),
        "db_path": str(DB_PATH.relative_to(PROJECT_ROOT)),
    }


def get_owner_safe_preview_lock_prep_shell() -> Dict[str, Any]:
    init = initialize_owner_safe_preview_lock_prep_layer()
    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "gp": 331,
        "title": "Owner Safe Preview Lock Prep Shell",
        "ready": True,
        "initialized": init,
        "preview_policy_prep_allowed": True,
        "object_body_read_allowed": False,
        "preview_rendering_allowed": False,
        "file_preview_unlocked": False,
        "locks": LOCKS,
    }


def get_preview_eligibility_policy_board() -> Dict[str, Any]:
    initialize_owner_safe_preview_lock_prep_layer()
    with _connect() as conn:
        candidates = _rows(conn, "SELECT * FROM preview_eligibility_candidates ORDER BY folder_key, original_filename")

    return {
        "section": SECTION,
        "gp": 332,
        "title": "Preview Eligibility Policy Board",
        "ready": True,
        "candidate_count": len(candidates),
        "eligible_policy_count": sum(1 for item in candidates if bool(item["policy_eligible"])),
        "candidates": candidates,
        "metadata_only": True,
        "preview_execution_allowed": False,
        "object_body_read_allowed": False,
    }


def get_preview_mime_type_contract() -> Dict[str, Any]:
    initialize_owner_safe_preview_lock_prep_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM preview_mime_type_contract ORDER BY mime_type")

    return {
        "section": SECTION,
        "gp": 333,
        "title": "Preview MIME Type Contract",
        "ready": True,
        "mime_type_count": len(rows),
        "mime_types": rows,
        "future_preview_policy_count": sum(1 for item in rows if bool(item["allowed_for_future_preview"])),
        "all_content_extraction_locked": all(not bool(item["content_extraction_allowed"]) for item in rows),
        "all_rendering_locked": all(not bool(item["rendering_allowed"]) for item in rows),
    }


def get_preview_redaction_policy_board() -> Dict[str, Any]:
    initialize_owner_safe_preview_lock_prep_layer()
    with _connect() as conn:
        policies = _rows(conn, "SELECT * FROM preview_redaction_policies ORDER BY policy_id")

    return {
        "section": SECTION,
        "gp": 334,
        "title": "Preview Redaction Policy Board",
        "ready": True,
        "policy_count": len(policies),
        "policies": policies,
        "object_body_blocked": any(item["field_name"] == "object_body" and bool(item["redaction_required"]) for item in policies),
        "plaintext_content_blocked": any(item["field_name"] == "plaintext_content" and bool(item["redaction_required"]) for item in policies),
        "physical_path_hidden": any(item["field_name"] == "physical_quarantine_path" and bool(item["redaction_required"]) for item in policies),
    }


def get_owner_preview_approval_lock_board() -> Dict[str, Any]:
    initialize_owner_safe_preview_lock_prep_layer()
    with _connect() as conn:
        locks = _rows(conn, "SELECT * FROM owner_preview_approval_locks ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 335,
        "title": "Owner Preview Approval Lock Board",
        "ready": True,
        "approval_lock_count": len(locks),
        "approval_locks": locks,
        "all_owner_approval_required": all(bool(item["owner_approval_required"]) for item in locks),
        "all_approval_recording_locked": all(not bool(item["approval_recording_allowed"]) for item in locks),
        "all_preview_execution_locked": all(not bool(item["preview_execution_allowed"]) for item in locks),
    }


def get_preview_route_payload_draft_builder() -> Dict[str, Any]:
    initialize_owner_safe_preview_lock_prep_layer()
    with _connect() as conn:
        drafts = _rows(conn, "SELECT * FROM preview_route_payload_drafts ORDER BY created_at DESC")

    payloads = []
    for item in drafts:
        payloads.append(
            {
                "payload_draft_id": item["payload_draft_id"],
                "active_file_id": item["active_file_id"],
                "eligibility_id": item["eligibility_id"],
                "route_state": item["route_state"],
                "metadata_only": bool(item["metadata_only"]),
                "display": {
                    "object_body": "LOCKED",
                    "plaintext_content": "LOCKED",
                    "rendered_preview": "LOCKED",
                    "download_url": "LOCKED",
                },
                "locks": {
                    "object_body_included": bool(item["object_body_included"]),
                    "plaintext_content_included": bool(item["plaintext_content_included"]),
                    "rendered_preview_included": bool(item["rendered_preview_included"]),
                    "download_url_included": bool(item["download_url_included"]),
                },
                "payload_hash": item["payload_hash"],
            }
        )

    return {
        "section": SECTION,
        "gp": 336,
        "title": "Preview Route Payload Draft Builder",
        "ready": True,
        "payload_draft_count": len(payloads),
        "payload_drafts": payloads,
        "metadata_only": True,
        "object_body_included": False,
        "plaintext_content_included": False,
        "rendered_preview_included": False,
        "download_url_included": False,
    }


def get_preview_receipt_draft_ledger() -> Dict[str, Any]:
    initialize_owner_safe_preview_lock_prep_layer()
    with _connect() as conn:
        receipts = _rows(conn, "SELECT * FROM preview_receipt_draft_ledger ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 337,
        "title": "Preview Receipt Draft Ledger",
        "ready": True,
        "receipt_draft_count": len(receipts),
        "receipt_drafts": receipts,
        "all_receipts_draft_locked": all(not bool(item["finalized"]) and not bool(item["finalization_allowed"]) for item in receipts),
        "receipt_finalization_allowed": False,
    }


def get_preview_safety_review_queue() -> Dict[str, Any]:
    initialize_owner_safe_preview_lock_prep_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM preview_safety_review_queue ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 338,
        "title": "Preview Safety Review Queue",
        "ready": True,
        "review_queue_count": len(rows),
        "review_queue": rows,
        "all_reviewer_actions_locked": all(not bool(item["reviewer_action_allowed"]) for item in rows),
        "all_preview_execution_locked": all(not bool(item["preview_execution_allowed"]) for item in rows),
    }


def get_preview_safety_blocker_board() -> Dict[str, Any]:
    initialize_owner_safe_preview_lock_prep_layer()
    with _connect() as conn:
        blockers = _rows(conn, "SELECT * FROM preview_safety_blockers ORDER BY blocker_id")

    return {
        "section": SECTION,
        "gp": 339,
        "title": "Preview Safety Blocker Board",
        "ready": True,
        "blocker_count": len(blockers),
        "blockers": blockers,
        "unsafe_action_count": sum(1 for item in blockers if bool(item["allowed"])),
        "all_dangerous_actions_blocked": all(not bool(item["allowed"]) for item in blockers),
    }


def get_owner_safe_preview_lock_prep_readiness_checkpoint() -> Dict[str, Any]:
    init = initialize_owner_safe_preview_lock_prep_layer()

    shell = get_owner_safe_preview_lock_prep_shell()
    eligibility = get_preview_eligibility_policy_board()
    mime_contract = get_preview_mime_type_contract()
    redaction = get_preview_redaction_policy_board()
    approvals = get_owner_preview_approval_lock_board()
    payloads = get_preview_route_payload_draft_builder()
    receipts = get_preview_receipt_draft_ledger()
    review_queue = get_preview_safety_review_queue()
    blockers = get_preview_safety_blocker_board()

    checks = {
        "previous_folder_browse_metadata_ready": init["previous_folder_browse_metadata_ready"] is True,
        "safe_preview_shell_ready": shell["ready"] is True,
        "preview_eligibility_ready": eligibility["ready"] is True and eligibility["candidate_count"] >= 2,
        "mime_contract_ready": mime_contract["ready"] is True and mime_contract["future_preview_policy_count"] >= 1,
        "mime_content_extraction_locked": mime_contract["all_content_extraction_locked"] is True,
        "mime_rendering_locked": mime_contract["all_rendering_locked"] is True,
        "redaction_policy_ready": redaction["ready"] is True and redaction["object_body_blocked"] is True,
        "owner_preview_approval_locks_ready": approvals["ready"] is True and approvals["all_preview_execution_locked"] is True,
        "preview_payload_drafts_ready": payloads["ready"] is True and payloads["payload_draft_count"] >= 2,
        "preview_payloads_metadata_only": payloads["object_body_included"] is False and payloads["rendered_preview_included"] is False,
        "preview_receipt_drafts_locked": receipts["ready"] is True and receipts["all_receipts_draft_locked"] is True,
        "preview_safety_review_queue_ready": review_queue["ready"] is True and review_queue["all_preview_execution_locked"] is True,
        "safety_blockers_ready": blockers["ready"] is True and blockers["all_dangerous_actions_blocked"] is True,
        "object_body_read_still_locked": LOCKS["object_body_read_allowed"] is False,
        "preview_rendering_still_locked": LOCKS["preview_rendering_allowed"] is False,
        "preview_endpoint_execution_still_locked": LOCKS["preview_endpoint_execution_allowed"] is False,
        "download_still_locked": LOCKS["file_download_unlocked"] is False,
        "share_still_locked": LOCKS["file_share_unlocked"] is False,
        "provider_not_required": LOCKS["provider_storage_required"] is False,
    }

    ready = all(checks.values())

    return {
        "section": SECTION,
        "gp": 340,
        "title": "Owner Safe Preview Lock Prep Readiness Checkpoint",
        "readiness_label": READINESS_LABEL if ready else "Owner safe preview lock prep layer blocked",
        "ready": ready,
        "checks": checks,
        "next_recommended_layer": "ARCHIVE VAULT — CONTROLLED OWNER SAFE PREVIEW EXECUTION LAYER / GP341-GP350",
        "still_locked": [
            "no object body read",
            "no plaintext content extraction",
            "no preview rendering",
            "no preview endpoint execution",
            "no preview cache write/read",
            "no download",
            "no sharing",
            "no delete",
            "no restore",
            "no quarantine release",
            "no physical object move",
            "no public upload",
            "no beta upload",
            "no provider upload",
            "no external sync",
        ],
    }


def get_owner_safe_preview_lock_prep_home() -> Dict[str, Any]:
    checkpoint = get_owner_safe_preview_lock_prep_readiness_checkpoint()
    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "ready": checkpoint["ready"],
        "readiness_label": checkpoint["readiness_label"],
        "packs": PACKS,
        "locks": LOCKS,
        "checkpoint": checkpoint,
    }


def validate_owner_safe_preview_lock_prep_layer() -> Dict[str, Any]:
    checkpoint = get_owner_safe_preview_lock_prep_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_folder_browse_metadata_ready"] is True
    assert checkpoint["checks"]["preview_eligibility_ready"] is True
    assert checkpoint["checks"]["mime_contract_ready"] is True
    assert checkpoint["checks"]["mime_content_extraction_locked"] is True
    assert checkpoint["checks"]["mime_rendering_locked"] is True
    assert checkpoint["checks"]["redaction_policy_ready"] is True
    assert checkpoint["checks"]["owner_preview_approval_locks_ready"] is True
    assert checkpoint["checks"]["preview_payload_drafts_ready"] is True
    assert checkpoint["checks"]["preview_payloads_metadata_only"] is True
    assert checkpoint["checks"]["preview_receipt_drafts_locked"] is True
    assert checkpoint["checks"]["preview_safety_review_queue_ready"] is True
    assert checkpoint["checks"]["safety_blockers_ready"] is True

    assert LOCKS["preview_eligibility_metadata_allowed"] is True
    assert LOCKS["preview_mime_policy_allowed"] is True
    assert LOCKS["preview_redaction_policy_allowed"] is True
    assert LOCKS["owner_preview_approval_lock_allowed"] is True
    assert LOCKS["preview_route_payload_draft_allowed"] is True
    assert LOCKS["preview_receipt_draft_allowed"] is True
    assert LOCKS["preview_safety_review_queue_allowed"] is True

    assert LOCKS["object_body_read_allowed"] is False
    assert LOCKS["plaintext_content_extraction_allowed"] is False
    assert LOCKS["preview_rendering_allowed"] is False
    assert LOCKS["preview_endpoint_execution_allowed"] is False
    assert LOCKS["preview_cache_write_allowed"] is False
    assert LOCKS["preview_cache_read_allowed"] is False
    assert LOCKS["file_preview_unlocked"] is False
    assert LOCKS["file_download_unlocked"] is False
    assert LOCKS["file_share_unlocked"] is False
    assert LOCKS["file_delete_unlocked"] is False
    assert LOCKS["file_restore_unlocked"] is False
    assert LOCKS["quarantine_release_allowed"] is False
    assert LOCKS["quarantine_object_move_allowed"] is False
    assert LOCKS["public_upload_unlocked"] is False
    assert LOCKS["beta_upload_unlocked"] is False
    assert LOCKS["provider_upload_unlocked"] is False
    assert LOCKS["provider_storage_required"] is False
    assert LOCKS["external_sync_unlocked"] is False

    return {
        "ok": True,
        "section": SECTION,
        "ready": checkpoint["ready"],
        "readiness_label": checkpoint["readiness_label"],
        "validated_at": _now(),
    }


def _gp_status(gp: int) -> Dict[str, Any]:
    pack = next(item for item in PACKS if item["gp"] == gp)
    checkpoint = get_owner_safe_preview_lock_prep_readiness_checkpoint()
    return {
        "section": SECTION,
        "gp": gp,
        "title": pack["title"],
        "status": pack["status"],
        "route": pack["route"],
        "ready": True,
        "checkpoint_ready": checkpoint["ready"],
        "locks_preserved": True,
        "preview_policy_prep_allowed": True,
        "object_body_read_allowed": False,
        "preview_rendering_allowed": False,
        "download_allowed": False,
    }


def get_gp331_status() -> Dict[str, Any]:
    return _gp_status(331)


def get_gp332_status() -> Dict[str, Any]:
    return _gp_status(332)


def get_gp333_status() -> Dict[str, Any]:
    return _gp_status(333)


def get_gp334_status() -> Dict[str, Any]:
    return _gp_status(334)


def get_gp335_status() -> Dict[str, Any]:
    return _gp_status(335)


def get_gp336_status() -> Dict[str, Any]:
    return _gp_status(336)


def get_gp337_status() -> Dict[str, Any]:
    return _gp_status(337)


def get_gp338_status() -> Dict[str, Any]:
    return _gp_status(338)


def get_gp339_status() -> Dict[str, Any]:
    return _gp_status(339)


def get_gp340_status() -> Dict[str, Any]:
    return _gp_status(340)


# GP331_INITIALIZER_CACHE_REPAIR
_GP331_INIT_CACHE = None

def initialize_owner_safe_preview_lock_prep_layer() -> Dict[str, Any]:
    """
    Cached wrapper added to prevent repeated dependency rebuilds during pytest/readiness getters.
    Runtime DBs are still cleaned between pack cells; this only caches inside one Python process.
    """
    global _GP331_INIT_CACHE
    if _GP331_INIT_CACHE is not None and DB_PATH.exists():
        return dict(_GP331_INIT_CACHE)

    result = _uncached_initialize_owner_safe_preview_lock_prep_layer()
    _GP331_INIT_CACHE = dict(result)
    return result
