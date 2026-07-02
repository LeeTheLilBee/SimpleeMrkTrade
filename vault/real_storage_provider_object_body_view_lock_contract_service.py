"""
VAULT GP069 — Real Storage Provider Object Body View Lock Contract

Current section:
Archive Vault — Real Storage Provider Configuration Layer / GP061-GP070

This pack creates a real SQLite-backed object body view lock contract sourced
from GP068. It keeps object body visibility, plaintext exposure, downloads,
read/write, direct upload, export, and execution locked.
"""

from __future__ import annotations

import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any, Dict, Optional

from vault.real_storage_provider_read_path_lock_contract_service import (
    DEFAULT_READ_PATH_LOCK_CONTRACT_ID,
    get_storage_provider_read_path_blockers,
    get_storage_provider_read_path_lock_contract_record,
    get_storage_provider_read_path_requirements,
)

PACK_ID = "VAULT_GP069"
PACK_NAME = "Real Storage Provider Object Body View Lock Contract"
SCHEMA_VERSION = "vault.real_storage_provider_object_body_view_lock_contract.v1"

SECTION_ID = "ARCHIVE_VAULT_REAL_STORAGE_PROVIDER_CONFIGURATION_LAYER"
SECTION_TITLE = "Archive Vault — Real Storage Provider Configuration Layer"
SECTION_RANGE = "GP061-GP070"

NEXT_PACK = "VAULT_GP070_REAL_STORAGE_PROVIDER_CONFIGURATION_READINESS_CHECKPOINT"
NEXT_PACK_TITLE = "Real Storage Provider Configuration Readiness Checkpoint"

DEFAULT_OBJECT_BODY_VIEW_LOCK_CONTRACT_ID = "VSPOBVLC-GP069-001"
DEFAULT_DB_ENV = "VAULT_STORAGE_PROVIDER_OBJECT_BODY_VIEW_LOCK_CONTRACT_DB"
DEFAULT_DB_PATH = "data/vault_storage_provider_object_body_view_lock_contract.sqlite"

OBJECT_BODY_VIEW_REQUIREMENT_SPECS = [
    ("object_body_view_lock_record_required", "Object body view lock record required", "object_body_view_lock"),
    ("tower_object_body_unlock_required", "Tower object body unlock required", "tower_gate"),
    ("owner_object_body_review_required", "Owner object body review required", "owner_review"),
    ("read_path_precondition_required", "Read path precondition required", "read_precondition"),
    ("object_body_receipt_precondition_required", "Object body receipt precondition required", "receipt_precondition"),
    ("plaintext_body_lock_required", "Plaintext body lock required", "plaintext_lock"),
    ("object_download_lock_required", "Object download lock required", "download_lock"),
    ("export_boundary_required", "Export boundary required", "export_boundary"),
]

OBJECT_BODY_VIEW_POLICIES = [
    ("no_object_body_view_configuration", "No object body view configuration", "object_body_view_lock"),
    ("no_object_body_view_attempt", "No object body view attempt", "object_body_view_lock"),
    ("no_object_body_view_enablement", "No object body view enablement", "object_body_view_lock"),
    ("no_object_body_content_exposure", "No object body content exposure", "content_exposure_lock"),
    ("no_plaintext_object_body_visibility", "No plaintext object body visibility", "plaintext_lock"),
    ("metadata_only_redacted_view", "Metadata-only redacted view", "redaction"),
    ("no_object_body_download", "No object body download", "download_lock"),
    ("no_read_unlock_from_object_body_view_contract", "No read unlock from object body view contract", "read_lock"),
    ("no_export_from_object_body_view_contract", "No export from object body view contract", "export_lock"),
    ("no_execution_from_object_body_view_contract", "No execution from object body view contract", "execution_lock"),
]

FALSE_FIELDS = [
    "object_body_view_configured",
    "object_body_view_attempted",
    "object_body_view_enabled",
    "object_body_receipt_created",
    "object_body_content_exposed",
    "object_body_plaintext_visible",
    "object_body_download_enabled",
    "read_path_configured",
    "read_path_attempted",
    "read_path_enabled",
    "read_receipt_created",
    "object_listing_configured",
    "object_list_attempted",
    "object_listed",
    "object_body_read_attempted",
    "object_body_read",
    "actual_secret_values_stored",
    "secret_values_present",
    "token_material_present",
    "encrypted_secret_payload_present",
    "key_material_stored",
    "kms_key_id_stored",
    "key_locator_present",
    "encryption_policy_configured",
    "secret_references_created",
    "secret_references_activated",
    "credentials_configured",
    "provider_endpoint_configured",
    "storage_container_configured",
    "namespace_configured",
    "connection_probe_configured",
    "connection_test_attempted",
    "provider_connection_tested",
    "write_path_configured",
    "write_path_attempted",
    "upload_path_configured",
    "object_create_attempted",
    "object_created",
    "provider_approval_ready",
    "provider_activation_ready",
    "provider_configuration_ready",
    "provider_read_write_ready",
    "provider_approved",
    "provider_activated",
    "provider_recommended",
    "provider_selected",
    "provider_configured",
    "provider_read_enabled",
    "provider_write_enabled",
    "provider_object_read_claimed",
    "provider_object_write_claimed",
    "risk_accepted",
    "risk_waived",
    "mitigation_approved",
    "official_storage_receipt",
    "finalized_storage_receipt",
    "closed_storage_receipt",
    "direct_upload_enabled",
    "export_enabled",
    "execution_enabled",
    "vault_done",
]

TRUE_CONTRACT_FIELDS = [
    "object_body_view_lock_contract_ready",
    "object_body_view_requirements_ready",
    "object_body_view_policy_ready",
    "object_body_view_locked",
    "object_body_metadata_only",
    "object_body_redacted_view_only",
]

TRUE_REQUIREMENT_FIELDS = [
    "requirement_required",
    "object_body_view_locked",
    "object_body_metadata_only",
    "object_body_redacted_view_only",
    "tower_review_required",
]

TRUE_BLOCKER_FIELDS = [
    "blocks_provider_approval",
    "blocks_provider_activation",
    "blocks_provider_selection",
    "blocks_provider_configuration",
    "blocks_provider_read_write",
    "blocks_object_body_view",
    "blocks_export",
    "blocks_execution",
    "tower_review_required",
]

def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def _resolve_db_path(db_path: Optional[str] = None) -> Path:
    return Path(db_path or os.environ.get(DEFAULT_DB_ENV) or DEFAULT_DB_PATH)

def _json_dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))

def _json_loads(value: str) -> Any:
    return json.loads(value)

def _connect(db_path: Optional[str] = None) -> sqlite3.Connection:
    path = _resolve_db_path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def _insert_dict(conn: sqlite3.Connection, table: str, payload: Dict[str, Any]) -> None:
    cols = list(payload.keys())
    conn.execute(
        f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({', '.join(['?'] * len(cols))})",
        tuple(payload[c] for c in cols),
    )

def _boolify(row: sqlite3.Row, json_fields: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    json_fields = json_fields or {}
    out = {}
    for key in row.keys():
        if key in json_fields:
            out[json_fields[key]] = _json_loads(row[key])
        elif isinstance(row[key], int):
            out[key] = bool(row[key])
        else:
            out[key] = row[key]
    return out

def ensure_storage_provider_object_body_view_lock_contract_schema(db_path: Optional[str] = None) -> Dict[str, Any]:
    path = _resolve_db_path(db_path)
    with _connect(str(path)) as conn:
        contract_false_sql = ",\n".join(f"{f} INTEGER NOT NULL DEFAULT 0" for f in FALSE_FIELDS)
        contract_true_sql = ",\n".join(f"{f} INTEGER NOT NULL DEFAULT 1" for f in TRUE_CONTRACT_FIELDS)

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_storage_provider_object_body_view_lock_contracts (
                object_body_view_lock_contract_id TEXT PRIMARY KEY,
                pack_id TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                source_read_path_lock_contract_id TEXT NOT NULL,
                source_read_path_pack_id TEXT NOT NULL,
                contract_status TEXT NOT NULL,
                tower_authority_status TEXT NOT NULL,
                contract_data_json TEXT NOT NULL,
                {contract_true_sql},
                {contract_false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        requirement_false_fields = [
            "requirement_verified",
            "object_body_view_configured",
            "object_body_view_attempted",
            "object_body_view_enabled",
            "object_body_receipt_created",
            "object_body_content_exposed",
            "object_body_plaintext_visible",
            "object_body_download_enabled",
            "read_path_configured",
            "read_path_attempted",
            "read_path_enabled",
            "object_listing_configured",
            "object_listed",
            "object_body_read",
            "credentials_configured",
            "provider_endpoint_configured",
            "storage_container_configured",
            "namespace_configured",
            "encryption_policy_configured",
            "provider_connection_tested",
            "provider_read_enabled",
            "provider_write_enabled",
            "direct_upload_enabled",
            "export_enabled",
            "execution_enabled",
            "tower_review_granted",
        ]
        requirement_false_sql = ",\n".join(f"{f} INTEGER NOT NULL DEFAULT 0" for f in requirement_false_fields)
        requirement_true_sql = ",\n".join(f"{f} INTEGER NOT NULL DEFAULT 1" for f in TRUE_REQUIREMENT_FIELDS)

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_storage_provider_object_body_view_requirements (
                object_body_view_requirement_id TEXT PRIMARY KEY,
                object_body_view_lock_contract_id TEXT NOT NULL,
                provider_candidate_id TEXT NOT NULL,
                requirement_code TEXT NOT NULL,
                requirement_name TEXT NOT NULL,
                requirement_category TEXT NOT NULL,
                requirement_message TEXT NOT NULL,
                requirement_status TEXT NOT NULL,
                {requirement_true_sql},
                {requirement_false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(object_body_view_lock_contract_id)
                    REFERENCES vault_storage_provider_object_body_view_lock_contracts(object_body_view_lock_contract_id)
                    ON DELETE CASCADE,
                UNIQUE(object_body_view_lock_contract_id, provider_candidate_id, requirement_code)
            )
            """
        )

        policy_false_fields = [
            "policy_verified",
            "object_body_view_configured",
            "object_body_view_attempted",
            "object_body_view_enabled",
            "object_body_receipt_created",
            "object_body_content_exposed",
            "object_body_plaintext_visible",
            "object_body_download_enabled",
            "read_path_configured",
            "read_path_attempted",
            "read_path_enabled",
            "object_body_read",
            "actual_secret_values_stored",
            "secret_values_present",
            "token_material_present",
            "secret_references_created",
            "secret_references_activated",
            "credentials_configured",
            "provider_read_enabled",
            "provider_write_enabled",
            "direct_upload_enabled",
            "export_enabled",
            "execution_enabled",
            "tower_review_granted",
        ]
        policy_false_sql = ",\n".join(f"{f} INTEGER NOT NULL DEFAULT 0" for f in policy_false_fields)

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_storage_provider_object_body_view_policies (
                object_body_view_policy_id TEXT PRIMARY KEY,
                object_body_view_lock_contract_id TEXT NOT NULL,
                policy_code TEXT NOT NULL,
                policy_name TEXT NOT NULL,
                policy_category TEXT NOT NULL,
                policy_message TEXT NOT NULL,
                policy_status TEXT NOT NULL,
                policy_required INTEGER NOT NULL DEFAULT 1,
                tower_review_required INTEGER NOT NULL DEFAULT 1,
                {policy_false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(object_body_view_lock_contract_id)
                    REFERENCES vault_storage_provider_object_body_view_lock_contracts(object_body_view_lock_contract_id)
                    ON DELETE CASCADE,
                UNIQUE(object_body_view_lock_contract_id, policy_code)
            )
            """
        )

        blocker_false_fields = [
            "tower_review_granted",
            "risk_accepted",
            "risk_waived",
            "mitigation_approved",
            "resolved",
        ]
        blocker_true_sql = ",\n".join(f"{f} INTEGER NOT NULL DEFAULT 1" for f in TRUE_BLOCKER_FIELDS)
        blocker_false_sql = ",\n".join(f"{f} INTEGER NOT NULL DEFAULT 0" for f in blocker_false_fields)

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_storage_provider_object_body_view_blockers (
                object_body_view_blocker_id TEXT PRIMARY KEY,
                object_body_view_lock_contract_id TEXT NOT NULL,
                source_read_path_blocker_id TEXT NOT NULL,
                source_write_path_blocker_id TEXT NOT NULL,
                source_connection_test_blocker_id TEXT NOT NULL,
                source_encryption_blocker_id TEXT NOT NULL,
                source_endpoint_namespace_blocker_id TEXT NOT NULL,
                source_ledger_blocker_id TEXT NOT NULL,
                source_credential_blocker_id TEXT NOT NULL,
                source_config_blocker_id TEXT NOT NULL,
                source_readiness_blocker_id TEXT NOT NULL,
                source_receipt_line_id TEXT NOT NULL,
                source_finding_id TEXT NOT NULL,
                provider_candidate_id TEXT NOT NULL,
                blocker_category TEXT NOT NULL,
                blocker_code TEXT NOT NULL,
                blocker_name TEXT NOT NULL,
                severity TEXT NOT NULL,
                blocker_status TEXT NOT NULL,
                {blocker_true_sql},
                {blocker_false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(object_body_view_lock_contract_id)
                    REFERENCES vault_storage_provider_object_body_view_lock_contracts(object_body_view_lock_contract_id)
                    ON DELETE CASCADE,
                UNIQUE(object_body_view_lock_contract_id, source_read_path_blocker_id)
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_storage_provider_object_body_view_events (
                event_id TEXT PRIMARY KEY,
                object_body_view_lock_contract_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(object_body_view_lock_contract_id)
                    REFERENCES vault_storage_provider_object_body_view_lock_contracts(object_body_view_lock_contract_id)
                    ON DELETE CASCADE
            )
            """
        )
        conn.commit()

    return {
        "schema_ready": True,
        "db_path": str(path),
        "real_sqlite_backed": True,
        "tables": [
            "vault_storage_provider_object_body_view_lock_contracts",
            "vault_storage_provider_object_body_view_requirements",
            "vault_storage_provider_object_body_view_policies",
            "vault_storage_provider_object_body_view_blockers",
            "vault_storage_provider_object_body_view_events",
        ],
    }

def _source_candidates(requirements):
    seen = {}
    for item in requirements:
        seen[item["provider_candidate_id"]] = {"provider_candidate_id": item["provider_candidate_id"]}
    return [seen[k] for k in sorted(seen)]

def _insert_event(conn, contract_id: str, event_type: str, event_payload: Dict[str, Any]) -> str:
    event_id = f"VSPOBVEVT-{uuid.uuid4().hex[:16].upper()}"
    _insert_dict(
        conn,
        "vault_storage_provider_object_body_view_events",
        {
            "event_id": event_id,
            "object_body_view_lock_contract_id": contract_id,
            "event_type": event_type,
            "event_payload_json": _json_dumps(event_payload),
            "created_at": _now_iso(),
        },
    )
    return event_id

def _counts(db_path: Optional[str] = None) -> Dict[str, int]:
    with _connect(db_path) as conn:
        return {
            "contract_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_object_body_view_lock_contracts").fetchone()["c"]),
            "requirement_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_object_body_view_requirements").fetchone()["c"]),
            "policy_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_object_body_view_policies").fetchone()["c"]),
            "blocker_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_object_body_view_blockers").fetchone()["c"]),
            "event_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_object_body_view_events").fetchone()["c"]),
        }

def initialize_real_storage_provider_object_body_view_lock_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    schema = ensure_storage_provider_object_body_view_lock_contract_schema(db_path)
    path = schema["db_path"]

    with _connect(path) as conn:
        exists = conn.execute(
            "SELECT object_body_view_lock_contract_id FROM vault_storage_provider_object_body_view_lock_contracts WHERE object_body_view_lock_contract_id = ?",
            (DEFAULT_OBJECT_BODY_VIEW_LOCK_CONTRACT_ID,),
        ).fetchone()

        if exists is None:
            source_contract = get_storage_provider_read_path_lock_contract_record()["read_path_lock_contract"]
            source_requirements_payload = get_storage_provider_read_path_requirements()
            blockers_payload = get_storage_provider_read_path_blockers()
            source_requirements = source_requirements_payload["requirements"]
            blockers = blockers_payload["blockers"]
            candidates = _source_candidates(source_requirements)
            now = _now_iso()

            contract_data = {
                "schema_version": SCHEMA_VERSION,
                "contract_type": "REAL_STORAGE_PROVIDER_OBJECT_BODY_VIEW_LOCK_CONTRACT",
                "metadata_source": "VAULT_GP068_REAL_STORAGE_PROVIDER_READ_PATH_LOCK_CONTRACT",
                "source_read_path_lock_contract_id": source_contract["read_path_lock_contract_id"],
                "source_read_path_pack_id": source_contract["pack_id"],
                "provider_candidate_count": len(candidates),
                "requirement_count": len(candidates) * len(OBJECT_BODY_VIEW_REQUIREMENT_SPECS),
                "policy_count": len(OBJECT_BODY_VIEW_POLICIES),
                "carried_blocker_count": blockers_payload["blocker_count"],
                "object_body_view_locked": True,
                "object_body_metadata_only": True,
                "object_body_redacted_view_only": True,
                "object_body_view_enabled": False,
                "object_body_content_exposed": False,
                "object_body_plaintext_visible": False,
                "object_body_download_enabled": False,
                "safe_to_continue_to_gp070": True,
            }

            contract_payload = {
                "object_body_view_lock_contract_id": DEFAULT_OBJECT_BODY_VIEW_LOCK_CONTRACT_ID,
                "pack_id": PACK_ID,
                "section_id": SECTION_ID,
                "section_range": SECTION_RANGE,
                "source_read_path_lock_contract_id": source_contract["read_path_lock_contract_id"],
                "source_read_path_pack_id": source_contract["pack_id"],
                "contract_status": "REAL_OBJECT_BODY_VIEW_LOCK_CONTRACT_OPEN_TOWER_LOCKED",
                "tower_authority_status": "TOWER_REVIEW_REQUIRED_NOT_GRANTED",
                "contract_data_json": _json_dumps(contract_data),
                "created_at": now,
                "updated_at": now,
            }
            for field in TRUE_CONTRACT_FIELDS:
                contract_payload[field] = 1
            for field in FALSE_FIELDS:
                contract_payload[field] = 0
            _insert_dict(conn, "vault_storage_provider_object_body_view_lock_contracts", contract_payload)

            for candidate in candidates:
                for code, name, category in OBJECT_BODY_VIEW_REQUIREMENT_SPECS:
                    payload = {
                        "object_body_view_requirement_id": f"VSPOBVR-{candidate['provider_candidate_id'].replace('VSPC-', '')}-{code.upper().replace('_', '-')}",
                        "object_body_view_lock_contract_id": DEFAULT_OBJECT_BODY_VIEW_LOCK_CONTRACT_ID,
                        "provider_candidate_id": candidate["provider_candidate_id"],
                        "requirement_code": code,
                        "requirement_name": name,
                        "requirement_category": category,
                        "requirement_message": f"{name} remains required before object body visibility can be considered.",
                        "requirement_status": "REAL_OBJECT_BODY_VIEW_REQUIREMENT_RECORDED_LOCKED_TOWER_LOCKED",
                        "created_at": now,
                        "updated_at": now,
                    }
                    for field in TRUE_REQUIREMENT_FIELDS:
                        payload[field] = 1
                    for field in [
                        "requirement_verified",
                        "object_body_view_configured",
                        "object_body_view_attempted",
                        "object_body_view_enabled",
                        "object_body_receipt_created",
                        "object_body_content_exposed",
                        "object_body_plaintext_visible",
                        "object_body_download_enabled",
                        "read_path_configured",
                        "read_path_attempted",
                        "read_path_enabled",
                        "object_listing_configured",
                        "object_listed",
                        "object_body_read",
                        "credentials_configured",
                        "provider_endpoint_configured",
                        "storage_container_configured",
                        "namespace_configured",
                        "encryption_policy_configured",
                        "provider_connection_tested",
                        "provider_read_enabled",
                        "provider_write_enabled",
                        "direct_upload_enabled",
                        "export_enabled",
                        "execution_enabled",
                        "tower_review_granted",
                    ]:
                        payload[field] = 0
                    _insert_dict(conn, "vault_storage_provider_object_body_view_requirements", payload)

            for code, name, category in OBJECT_BODY_VIEW_POLICIES:
                payload = {
                    "object_body_view_policy_id": f"VSPOBVP-{code.upper().replace('_', '-')}",
                    "object_body_view_lock_contract_id": DEFAULT_OBJECT_BODY_VIEW_LOCK_CONTRACT_ID,
                    "policy_code": code,
                    "policy_name": name,
                    "policy_category": category,
                    "policy_message": f"{name}; GP069 cannot expose body content, export, or execute.",
                    "policy_status": "REAL_OBJECT_BODY_VIEW_POLICY_RECORDED_TOWER_LOCKED",
                    "policy_required": 1,
                    "tower_review_required": 1,
                    "created_at": now,
                    "updated_at": now,
                }
                for field in [
                    "policy_verified",
                    "object_body_view_configured",
                    "object_body_view_attempted",
                    "object_body_view_enabled",
                    "object_body_receipt_created",
                    "object_body_content_exposed",
                    "object_body_plaintext_visible",
                    "object_body_download_enabled",
                    "read_path_configured",
                    "read_path_attempted",
                    "read_path_enabled",
                    "object_body_read",
                    "actual_secret_values_stored",
                    "secret_values_present",
                    "token_material_present",
                    "secret_references_created",
                    "secret_references_activated",
                    "credentials_configured",
                    "provider_read_enabled",
                    "provider_write_enabled",
                    "direct_upload_enabled",
                    "export_enabled",
                    "execution_enabled",
                    "tower_review_granted",
                ]:
                    payload[field] = 0
                _insert_dict(conn, "vault_storage_provider_object_body_view_policies", payload)

            for blocker in blockers:
                payload = {
                    "object_body_view_blocker_id": f"VSPOBVB-{blocker['read_path_blocker_id'].replace('VSPRPB-', '')}",
                    "object_body_view_lock_contract_id": DEFAULT_OBJECT_BODY_VIEW_LOCK_CONTRACT_ID,
                    "source_read_path_blocker_id": blocker["read_path_blocker_id"],
                    "source_write_path_blocker_id": blocker["source_write_path_blocker_id"],
                    "source_connection_test_blocker_id": blocker["source_connection_test_blocker_id"],
                    "source_encryption_blocker_id": blocker["source_encryption_blocker_id"],
                    "source_endpoint_namespace_blocker_id": blocker["source_endpoint_namespace_blocker_id"],
                    "source_ledger_blocker_id": blocker["source_ledger_blocker_id"],
                    "source_credential_blocker_id": blocker["source_credential_blocker_id"],
                    "source_config_blocker_id": blocker["source_config_blocker_id"],
                    "source_readiness_blocker_id": blocker["source_readiness_blocker_id"],
                    "source_receipt_line_id": blocker["source_receipt_line_id"],
                    "source_finding_id": blocker["source_finding_id"],
                    "provider_candidate_id": blocker["provider_candidate_id"],
                    "blocker_category": blocker["blocker_category"],
                    "blocker_code": blocker["blocker_code"],
                    "blocker_name": blocker["blocker_name"],
                    "severity": blocker["severity"],
                    "blocker_status": "REAL_OBJECT_BODY_VIEW_BLOCKER_ACTIVE_CARRIED_FROM_GP068",
                    "created_at": now,
                    "updated_at": now,
                }
                for field in TRUE_BLOCKER_FIELDS:
                    payload[field] = 1
                for field in ["tower_review_granted", "risk_accepted", "risk_waived", "mitigation_approved", "resolved"]:
                    payload[field] = 0
                _insert_dict(conn, "vault_storage_provider_object_body_view_blockers", payload)

            event_payloads = [
                ("REAL_STORAGE_PROVIDER_OBJECT_BODY_VIEW_LOCK_CONTRACT_CREATED", contract_data),
                ("SOURCE_GP068_READ_PATH_LOCK_CONTRACT_ATTACHED", {
                    "source_read_path_lock_contract_id": source_contract["read_path_lock_contract_id"],
                    "source_read_path_pack_id": source_contract["pack_id"],
                    "source_requirement_count": source_requirements_payload["requirement_count"],
                    "source_blocker_count": blockers_payload["blocker_count"],
                }),
                ("REAL_OBJECT_BODY_VIEW_REQUIREMENTS_CREATED_LOCKED", {"requirement_count": len(candidates) * len(OBJECT_BODY_VIEW_REQUIREMENT_SPECS)}),
                ("REAL_OBJECT_BODY_VIEW_POLICIES_CREATED", {"policy_count": len(OBJECT_BODY_VIEW_POLICIES)}),
                ("REAL_OBJECT_BODY_VIEW_BLOCKERS_CARRIED_FORWARD", {"blocker_count": blockers_payload["blocker_count"]}),
                ("OBJECT_BODY_VIEW_LOCKS_CONFIRMED", {
                    "object_body_view_configured": False,
                    "object_body_content_exposed": False,
                    "object_body_plaintext_visible": False,
                    "object_body_download_enabled": False,
                    "export_enabled": False,
                    "execution_enabled": False,
                }),
            ]
            for event_type, payload in event_payloads:
                _insert_event(conn, DEFAULT_OBJECT_BODY_VIEW_LOCK_CONTRACT_ID, event_type, payload)

            conn.commit()

    counts = _counts(path)
    return {"initialized": True, "schema": schema, "real_sqlite_backed": True, **counts}

def _sum_counts(table: str, contract_col: str, contract_id: str, fields: list[str], db_path: Optional[str] = None) -> Dict[str, int]:
    selects = ["COUNT(*) AS total_count"]
    for field in fields:
        selects.append(f"SUM(CASE WHEN {field} = 1 THEN 1 ELSE 0 END) AS {field}_count")
    with _connect(db_path) as conn:
        row = conn.execute(
            f"SELECT {', '.join(selects)} FROM {table} WHERE {contract_col} = ?",
            (contract_id,),
        ).fetchone()
    return {key: int(row[key] or 0) for key in row.keys()}

def get_storage_provider_object_body_view_lock_contract_record(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_object_body_view_lock_contract(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM vault_storage_provider_object_body_view_lock_contracts WHERE object_body_view_lock_contract_id = ?",
            (DEFAULT_OBJECT_BODY_VIEW_LOCK_CONTRACT_ID,),
        ).fetchone()
    return {"pack": _pack_payload(), "real_sqlite_backed": True, "object_body_view_lock_contract": _boolify(row, {"contract_data_json": "contract_data"})}

def get_storage_provider_object_body_view_requirements(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_object_body_view_lock_contract(db_path)
    fields = [
        "requirement_required", "requirement_verified", "object_body_view_locked", "object_body_metadata_only",
        "object_body_redacted_view_only", "object_body_view_configured", "object_body_view_attempted",
        "object_body_view_enabled", "object_body_receipt_created", "object_body_content_exposed",
        "object_body_plaintext_visible", "object_body_download_enabled", "read_path_configured",
        "read_path_attempted", "read_path_enabled", "object_listing_configured", "object_listed",
        "object_body_read", "credentials_configured", "provider_endpoint_configured",
        "storage_container_configured", "namespace_configured", "encryption_policy_configured",
        "provider_connection_tested", "provider_read_enabled", "provider_write_enabled",
        "direct_upload_enabled", "export_enabled", "execution_enabled", "tower_review_required",
        "tower_review_granted",
    ]
    counts = _sum_counts(
        "vault_storage_provider_object_body_view_requirements",
        "object_body_view_lock_contract_id",
        DEFAULT_OBJECT_BODY_VIEW_LOCK_CONTRACT_ID,
        fields,
        db_path,
    )
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_object_body_view_requirements
            WHERE object_body_view_lock_contract_id = ?
            ORDER BY provider_candidate_id, requirement_category, requirement_code
            """,
            (DEFAULT_OBJECT_BODY_VIEW_LOCK_CONTRACT_ID,),
        ).fetchall()
        provider_candidate_count = conn.execute(
            """
            SELECT COUNT(DISTINCT provider_candidate_id) AS c
            FROM vault_storage_provider_object_body_view_requirements
            WHERE object_body_view_lock_contract_id = ?
            """,
            (DEFAULT_OBJECT_BODY_VIEW_LOCK_CONTRACT_ID,),
        ).fetchone()["c"]
        requirement_code_count = conn.execute(
            """
            SELECT COUNT(DISTINCT requirement_code) AS c
            FROM vault_storage_provider_object_body_view_requirements
            WHERE object_body_view_lock_contract_id = ?
            """,
            (DEFAULT_OBJECT_BODY_VIEW_LOCK_CONTRACT_ID,),
        ).fetchone()["c"]
    counts["requirement_count"] = counts.pop("total_count")
    counts["provider_candidate_count"] = int(provider_candidate_count)
    counts["requirement_code_count"] = int(requirement_code_count)
    return {"pack": _pack_payload(), "real_sqlite_backed": True, **counts, "requirements": [_boolify(r) for r in rows]}

def get_storage_provider_object_body_view_policies(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_object_body_view_lock_contract(db_path)
    fields = [
        "policy_required", "policy_verified", "object_body_view_configured", "object_body_view_attempted",
        "object_body_view_enabled", "object_body_receipt_created", "object_body_content_exposed",
        "object_body_plaintext_visible", "object_body_download_enabled", "read_path_configured",
        "read_path_attempted", "read_path_enabled", "object_body_read", "actual_secret_values_stored",
        "secret_values_present", "token_material_present", "secret_references_created",
        "secret_references_activated", "credentials_configured", "provider_read_enabled",
        "provider_write_enabled", "direct_upload_enabled", "export_enabled", "execution_enabled",
        "tower_review_required", "tower_review_granted",
    ]
    counts = _sum_counts(
        "vault_storage_provider_object_body_view_policies",
        "object_body_view_lock_contract_id",
        DEFAULT_OBJECT_BODY_VIEW_LOCK_CONTRACT_ID,
        fields,
        db_path,
    )
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_object_body_view_policies
            WHERE object_body_view_lock_contract_id = ?
            ORDER BY policy_category, policy_code
            """,
            (DEFAULT_OBJECT_BODY_VIEW_LOCK_CONTRACT_ID,),
        ).fetchall()
        code_count = conn.execute(
            """
            SELECT COUNT(DISTINCT policy_code) AS c
            FROM vault_storage_provider_object_body_view_policies
            WHERE object_body_view_lock_contract_id = ?
            """,
            (DEFAULT_OBJECT_BODY_VIEW_LOCK_CONTRACT_ID,),
        ).fetchone()["c"]
    counts["policy_count"] = counts.pop("total_count")
    counts["policy_code_count"] = int(code_count)
    return {"pack": _pack_payload(), "real_sqlite_backed": True, **counts, "policies": [_boolify(r) for r in rows]}

def get_storage_provider_object_body_view_blockers(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_object_body_view_lock_contract(db_path)
    fields = [
        "blocks_provider_approval", "blocks_provider_activation", "blocks_provider_selection",
        "blocks_provider_configuration", "blocks_provider_read_write", "blocks_object_body_view",
        "blocks_export", "blocks_execution", "tower_review_required", "tower_review_granted",
        "risk_accepted", "risk_waived", "mitigation_approved", "resolved",
    ]
    counts = _sum_counts(
        "vault_storage_provider_object_body_view_blockers",
        "object_body_view_lock_contract_id",
        DEFAULT_OBJECT_BODY_VIEW_LOCK_CONTRACT_ID,
        fields,
        db_path,
    )
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_object_body_view_blockers
            WHERE object_body_view_lock_contract_id = ?
            ORDER BY provider_candidate_id, blocker_category, blocker_code
            """,
            (DEFAULT_OBJECT_BODY_VIEW_LOCK_CONTRACT_ID,),
        ).fetchall()
        category_rows = conn.execute(
            """
            SELECT blocker_category, COUNT(*) AS c
            FROM vault_storage_provider_object_body_view_blockers
            WHERE object_body_view_lock_contract_id = ?
            GROUP BY blocker_category
            """,
            (DEFAULT_OBJECT_BODY_VIEW_LOCK_CONTRACT_ID,),
        ).fetchall()
    counts["blocker_count"] = counts.pop("total_count")
    for row in category_rows:
        counts[f"{row['blocker_category']}_blocker_count"] = int(row["c"])
    counts.setdefault("capability_contract_blocker_count", counts.get("capability_blocker_count", 0))
    counts.setdefault("criteria_validation_blocker_count", counts.get("criteria_blocker_count", 0))
    counts.setdefault("risk_validation_blocker_count", counts.get("risk_blocker_count", 0))
    counts["capability_blocker_count"] = counts.get("capability_contract_blocker_count", 0)
    counts["criteria_blocker_count"] = counts.get("criteria_validation_blocker_count", 0)
    counts["risk_blocker_count"] = counts.get("risk_validation_blocker_count", 0)
    return {"pack": _pack_payload(), "real_sqlite_backed": True, **counts, "blockers": [_boolify(r) for r in rows]}

def get_storage_provider_object_body_view_events(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_object_body_view_lock_contract(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_object_body_view_events
            WHERE object_body_view_lock_contract_id = ?
            ORDER BY created_at, event_id
            """,
            (DEFAULT_OBJECT_BODY_VIEW_LOCK_CONTRACT_ID,),
        ).fetchall()
    events = [
        {
            "event_id": r["event_id"],
            "object_body_view_lock_contract_id": r["object_body_view_lock_contract_id"],
            "event_type": r["event_type"],
            "event_payload": _json_loads(r["event_payload_json"]),
            "created_at": r["created_at"],
        }
        for r in rows
    ]
    return {"pack": _pack_payload(), "real_sqlite_backed": True, "event_count": len(events), "events": events}

def record_storage_provider_object_body_view_event(event_type: str, event_payload: Optional[Dict[str, Any]] = None, db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_object_body_view_lock_contract(db_path)
    payload = dict(event_payload or {})
    payload.update({
        "write_type": "REAL_STORAGE_PROVIDER_OBJECT_BODY_VIEW_LOCK_EVENT",
        "object_body_view_lock_contract_ready": True,
        "object_body_view_locked": True,
        "object_body_metadata_only": True,
        "object_body_redacted_view_only": True,
        "object_body_view_configured": False,
        "object_body_view_attempted": False,
        "object_body_view_enabled": False,
        "object_body_receipt_created": False,
        "object_body_content_exposed": False,
        "object_body_plaintext_visible": False,
        "object_body_download_enabled": False,
        "read_path_enabled": False,
        "object_body_read": False,
        "provider_read_enabled": False,
        "provider_write_enabled": False,
        "direct_upload_enabled": False,
        "export_enabled": False,
        "execution_enabled": False,
        "vault_done": False,
    })
    with _connect(db_path) as conn:
        event_id = _insert_event(conn, DEFAULT_OBJECT_BODY_VIEW_LOCK_CONTRACT_ID, event_type, payload)
        conn.commit()
    return {
        "pack": _pack_payload(),
        "event_written": True,
        "event_id": event_id,
        "object_body_view_lock_contract_id": DEFAULT_OBJECT_BODY_VIEW_LOCK_CONTRACT_ID,
        "real_sqlite_backed": True,
        **payload,
    }

def validate_storage_provider_object_body_view_lock_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    contract = get_storage_provider_object_body_view_lock_contract_record(db_path)["object_body_view_lock_contract"]
    requirements = get_storage_provider_object_body_view_requirements(db_path)
    policies = get_storage_provider_object_body_view_policies(db_path)
    blockers = get_storage_provider_object_body_view_blockers(db_path)
    events = get_storage_provider_object_body_view_events(db_path)

    expected_requirements = 5 * len(OBJECT_BODY_VIEW_REQUIREMENT_SPECS)
    expected_policies = len(OBJECT_BODY_VIEW_POLICIES)
    expected_blockers = 140

    checks = [
        ("REAL_SQLITE_OBJECT_BODY_VIEW_LOCK_CONTRACT_EXISTS", contract["object_body_view_lock_contract_id"] == DEFAULT_OBJECT_BODY_VIEW_LOCK_CONTRACT_ID),
        ("SOURCE_GP068_READ_PATH_LOCK_CONTRACT_ATTACHED", contract["source_read_path_lock_contract_id"] == DEFAULT_READ_PATH_LOCK_CONTRACT_ID),
        ("OBJECT_BODY_VIEW_LOCK_CONTRACT_READY", contract["object_body_view_lock_contract_ready"] is True),
        ("OBJECT_BODY_VIEW_LOCKED", contract["object_body_view_locked"] is True),
        ("OBJECT_BODY_METADATA_ONLY", contract["object_body_metadata_only"] is True),
        ("OBJECT_BODY_REDACTED_VIEW_ONLY", contract["object_body_redacted_view_only"] is True),
        ("REAL_OBJECT_BODY_VIEW_REQUIREMENTS_EXIST", requirements["requirement_count"] == expected_requirements),
        ("REAL_OBJECT_BODY_VIEW_POLICIES_EXIST", policies["policy_count"] == expected_policies),
        ("REAL_OBJECT_BODY_VIEW_BLOCKERS_CARRIED_FORWARD", blockers["blocker_count"] == expected_blockers),
        ("NO_REQUIREMENT_OBJECT_BODY_VIEW_CONFIGURED", requirements["object_body_view_configured_count"] == 0),
        ("NO_REQUIREMENT_OBJECT_BODY_VIEW_ATTEMPTED", requirements["object_body_view_attempted_count"] == 0),
        ("NO_REQUIREMENT_OBJECT_BODY_VIEW_ENABLED", requirements["object_body_view_enabled_count"] == 0),
        ("NO_REQUIREMENT_OBJECT_BODY_CONTENT_EXPOSED", requirements["object_body_content_exposed_count"] == 0),
        ("NO_REQUIREMENT_OBJECT_BODY_PLAINTEXT_VISIBLE", requirements["object_body_plaintext_visible_count"] == 0),
        ("NO_REQUIREMENT_OBJECT_BODY_DOWNLOAD_ENABLED", requirements["object_body_download_enabled_count"] == 0),
        ("NO_POLICY_OBJECT_BODY_VIEW_CONFIGURED", policies["object_body_view_configured_count"] == 0),
        ("NO_POLICY_OBJECT_BODY_CONTENT_EXPOSED", policies["object_body_content_exposed_count"] == 0),
        ("NO_POLICY_OBJECT_BODY_PLAINTEXT_VISIBLE", policies["object_body_plaintext_visible_count"] == 0),
        ("NO_POLICY_OBJECT_BODY_DOWNLOAD_ENABLED", policies["object_body_download_enabled_count"] == 0),
        ("NO_BLOCKERS_TOWER_REVIEW_GRANTED", blockers["tower_review_granted_count"] == 0),
        ("ALL_BLOCKERS_BLOCK_OBJECT_BODY_VIEW", blockers["blocks_object_body_view_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_EXPORT", blockers["blocks_export_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_EXECUTION", blockers["blocks_execution_count"] == expected_blockers),
        ("NO_CONTRACT_OBJECT_BODY_VIEW_CONFIGURED", contract["object_body_view_configured"] is False),
        ("NO_CONTRACT_OBJECT_BODY_VIEW_ATTEMPTED", contract["object_body_view_attempted"] is False),
        ("NO_CONTRACT_OBJECT_BODY_VIEW_ENABLED", contract["object_body_view_enabled"] is False),
        ("NO_CONTRACT_OBJECT_BODY_CONTENT_EXPOSED", contract["object_body_content_exposed"] is False),
        ("NO_CONTRACT_OBJECT_BODY_PLAINTEXT_VISIBLE", contract["object_body_plaintext_visible"] is False),
        ("NO_CONTRACT_OBJECT_BODY_DOWNLOAD_ENABLED", contract["object_body_download_enabled"] is False),
        ("NO_PROVIDER_READ_WRITE", contract["provider_read_enabled"] is False and contract["provider_write_enabled"] is False),
        ("NO_DIRECT_UPLOAD", contract["direct_upload_enabled"] is False),
        ("NO_EXPORT", contract["export_enabled"] is False),
        ("NO_EXECUTION", contract["execution_enabled"] is False),
        ("VAULT_NOT_DONE", contract["vault_done"] is False),
        ("EVENT_LOG_EXISTS", events["event_count"] >= 6),
    ]
    checks_payload = [{"code": code, "passed": bool(passed)} for code, passed in checks]
    failed = [c for c in checks_payload if not c["passed"]]
    return {
        "pack": _pack_payload(),
        "validation_ready": True,
        "valid": len(failed) == 0,
        "check_count": len(checks_payload),
        "passed_count": len(checks_payload) - len(failed),
        "failed_count": len(failed),
        "failed_checks": failed,
        "checks": checks_payload,
        "real_sqlite_backed": True,
        "safe_to_continue_to_gp070": len(failed) == 0,
    }

def get_storage_provider_object_body_view_next_step() -> Dict[str, Any]:
    return {
        "pack": _pack_payload(),
        "next_step": {
            "current_section": SECTION_ID,
            "current_section_title": SECTION_TITLE,
            "current_section_range": SECTION_RANGE,
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
            "safe_to_continue_to_gp070": True,
            "vault_done": False,
            "clouds_should_continue": False,
            "owner_notebook_note": "Continue under ARCHIVE VAULT — REAL STORAGE PROVIDER CONFIGURATION LAYER / GP061-GP070. GP070 should build the real storage provider configuration readiness checkpoint while keeping secrets, provider connection, read/write, object body view, direct upload, export, and execution locked.",
            "carry_forward_rules": [
                "Keep the real SQLite object body view lock contract.",
                "Keep real object-body-view requirement rows.",
                "Keep real object-body-view policy rows.",
                "Keep real blockers carried from GP068.",
                "Build GP070 Real Storage Provider Configuration Readiness Checkpoint next.",
                "Do not configure object body view.",
                "Do not attempt object body view.",
                "Do not enable object body view.",
                "Do not expose object body content.",
                "Do not expose plaintext object bodies.",
                "Do not enable object body downloads.",
                "Do not unlock direct upload.",
                "Do not unlock export.",
                "Do not unlock execution.",
                "Do not treat Vault as done.",
            ],
        },
    }

def _pack_payload() -> Dict[str, Any]:
    return {
        "id": PACK_ID,
        "name": PACK_NAME,
        "schema_version": SCHEMA_VERSION,
        "generated_at": _now_iso(),
        "depends_on": ["VAULT_GP068"],
        "foundation_status": "object_body_view_lock_contract_ready_safe_to_continue_not_done",
        "product_depth_layer": "real_storage_provider_object_body_view_lock_contract",
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
    }

def _routes_payload() -> Dict[str, str]:
    return {
        "route": "/vault/real-storage-provider-object-body-view-lock-contract",
        "json_route": "/vault/real-storage-provider-object-body-view-lock-contract.json",
        "record_route": "/vault/storage-provider-object-body-view-lock-contract-record.json",
        "requirements_route": "/vault/storage-provider-object-body-view-requirements.json",
        "policies_route": "/vault/storage-provider-object-body-view-policies.json",
        "blockers_route": "/vault/storage-provider-object-body-view-blockers.json",
        "events_route": "/vault/storage-provider-object-body-view-events.json",
        "validation_route": "/vault/storage-provider-object-body-view-validation.json",
        "next_step_route": "/vault/storage-provider-object-body-view-next-step.json",
        "gp069_status_route": "/vault/gp069-status.json",
    }

def get_real_storage_provider_object_body_view_lock_contract_home(db_path: Optional[str] = None) -> Dict[str, Any]:
    init = initialize_real_storage_provider_object_body_view_lock_contract(db_path)
    contract = get_storage_provider_object_body_view_lock_contract_record(db_path)["object_body_view_lock_contract"]
    requirements = get_storage_provider_object_body_view_requirements(db_path)
    policies = get_storage_provider_object_body_view_policies(db_path)
    blockers = get_storage_provider_object_body_view_blockers(db_path)
    events = get_storage_provider_object_body_view_events(db_path)
    validation = validate_storage_provider_object_body_view_lock_contract(db_path)
    truth = {
        "real_storage_provider_object_body_view_lock_contract_ready": True,
        "real_sqlite_backed": True,
        "real_schema_ready": True,
        "source_gp068_read_path_lock_contract_attached": contract["source_read_path_lock_contract_id"] == DEFAULT_READ_PATH_LOCK_CONTRACT_ID,
        "validation_passed": validation["valid"],
        "object_body_view_lock_contract_ready": contract["object_body_view_lock_contract_ready"],
        "object_body_view_locked": contract["object_body_view_locked"],
        "object_body_metadata_only": contract["object_body_metadata_only"],
        "object_body_redacted_view_only": contract["object_body_redacted_view_only"],
        "requirement_count": requirements["requirement_count"],
        "policy_count": policies["policy_count"],
        "blocker_count": blockers["blocker_count"],
        "object_body_view_configured_count": requirements["object_body_view_configured_count"] + policies["object_body_view_configured_count"],
        "object_body_view_attempted_count": requirements["object_body_view_attempted_count"] + policies["object_body_view_attempted_count"],
        "object_body_view_enabled_count": requirements["object_body_view_enabled_count"] + policies["object_body_view_enabled_count"],
        "object_body_content_exposed_count": requirements["object_body_content_exposed_count"] + policies["object_body_content_exposed_count"],
        "object_body_plaintext_visible_count": requirements["object_body_plaintext_visible_count"] + policies["object_body_plaintext_visible_count"],
        "object_body_download_enabled_count": requirements["object_body_download_enabled_count"] + policies["object_body_download_enabled_count"],
        "provider_read_enabled": contract["provider_read_enabled"],
        "provider_write_enabled": contract["provider_write_enabled"],
        "direct_upload_enabled": contract["direct_upload_enabled"],
        "export_enabled": contract["export_enabled"],
        "execution_enabled": contract["execution_enabled"],
        "vault_done": contract["vault_done"],
        "safe_to_continue_to_gp070": validation["safe_to_continue_to_gp070"],
    }
    return {
        "pack": _pack_payload(),
        "object_body_view_truth": truth,
        "store": init,
        "object_body_view_lock_contract": contract,
        "requirements": requirements,
        "policies": policies,
        "blockers": blockers,
        "event_count": events["event_count"],
        "validation": validation,
        "routes": _routes_payload(),
        "next_step": get_storage_provider_object_body_view_next_step()["next_step"],
    }

def get_gp069_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    home = get_real_storage_provider_object_body_view_lock_contract_home(db_path)
    contract = home["object_body_view_lock_contract"]
    requirements = home["requirements"]
    policies = home["policies"]
    blockers = home["blockers"]
    validation = home["validation"]

    return {
        "pack": _pack_payload(),
        "gp069_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "real_storage_provider_object_body_view_lock_contract_ready": True,
            "real_sqlite_backed": True,
            "real_schema_ready": True,
            "real_contract_count": home["store"]["contract_count"],
            "real_requirement_count": home["store"]["requirement_count"],
            "real_policy_count": home["store"]["policy_count"],
            "real_blocker_count": home["store"]["blocker_count"],
            "real_event_count": home["store"]["event_count"],
            "source_gp068_read_path_lock_contract_attached": True,
            "object_body_view_lock_contract_ready": contract["object_body_view_lock_contract_ready"],
            "object_body_view_requirements_ready": contract["object_body_view_requirements_ready"],
            "object_body_view_policy_ready": contract["object_body_view_policy_ready"],
            "object_body_view_locked": contract["object_body_view_locked"],
            "object_body_metadata_only": contract["object_body_metadata_only"],
            "object_body_redacted_view_only": contract["object_body_redacted_view_only"],
            "provider_candidate_count": requirements["provider_candidate_count"],
            "requirement_code_count": requirements["requirement_code_count"],
            "policy_code_count": policies["policy_code_count"],
            "object_body_view_configured_count": requirements["object_body_view_configured_count"] + policies["object_body_view_configured_count"],
            "object_body_view_attempted_count": requirements["object_body_view_attempted_count"] + policies["object_body_view_attempted_count"],
            "object_body_view_enabled_count": requirements["object_body_view_enabled_count"] + policies["object_body_view_enabled_count"],
            "object_body_receipt_created_count": requirements["object_body_receipt_created_count"] + policies["object_body_receipt_created_count"],
            "object_body_content_exposed_count": requirements["object_body_content_exposed_count"] + policies["object_body_content_exposed_count"],
            "object_body_plaintext_visible_count": requirements["object_body_plaintext_visible_count"] + policies["object_body_plaintext_visible_count"],
            "object_body_download_enabled_count": requirements["object_body_download_enabled_count"] + policies["object_body_download_enabled_count"],
            "read_path_enabled_count": requirements["read_path_enabled_count"] + policies["read_path_enabled_count"],
            "object_body_read_count": requirements["object_body_read_count"] + policies["object_body_read_count"],
            "provider_read_enabled_count": requirements["provider_read_enabled_count"] + policies["provider_read_enabled_count"],
            "provider_write_enabled_count": requirements["provider_write_enabled_count"] + policies["provider_write_enabled_count"],
            "direct_upload_enabled_count": requirements["direct_upload_enabled_count"] + policies["direct_upload_enabled_count"],
            "blocks_provider_configuration_count": blockers["blocks_provider_configuration_count"],
            "blocks_provider_read_write_count": blockers["blocks_provider_read_write_count"],
            "blocks_object_body_view_count": blockers["blocks_object_body_view_count"],
            "blocks_export_count": blockers["blocks_export_count"],
            "blocks_execution_count": blockers["blocks_execution_count"],
            "tower_review_granted_count": blockers["tower_review_granted_count"],
            "resolved_count": blockers["resolved_count"],
            "validation_ready": True,
            "validation_passed": validation["valid"],
            "safe_to_continue_to_gp070": validation["safe_to_continue_to_gp070"],
            "foundation_status": "object_body_view_lock_contract_ready_safe_to_continue_not_done",
            "vault_done": False,
            "object_body_view_configured": contract["object_body_view_configured"],
            "object_body_view_attempted": contract["object_body_view_attempted"],
            "object_body_view_enabled": contract["object_body_view_enabled"],
            "object_body_receipt_created": contract["object_body_receipt_created"],
            "object_body_content_exposed": contract["object_body_content_exposed"],
            "object_body_plaintext_visible": contract["object_body_plaintext_visible"],
            "object_body_download_enabled": contract["object_body_download_enabled"],
            "provider_read_enabled": contract["provider_read_enabled"],
            "provider_write_enabled": contract["provider_write_enabled"],
            "provider_object_read_claimed": contract["provider_object_read_claimed"],
            "provider_object_write_claimed": contract["provider_object_write_claimed"],
            "direct_upload_enabled": contract["direct_upload_enabled"],
            "export_enabled": contract["export_enabled"],
            "execution_enabled": contract["execution_enabled"],
            "clouds_status": "parked_do_not_continue_from_vault_gp069",
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
        },
        "object_body_view_truth": home["object_body_view_truth"],
        "routes": home["routes"],
        "object_body_view_lock_contract": contract,
        "requirements": requirements,
        "policies": policies,
        "blockers": blockers,
        "validation": validation,
        "next_step": home["next_step"],
    }

def render_real_storage_provider_object_body_view_lock_contract_page() -> str:
    home = get_real_storage_provider_object_body_view_lock_contract_home()
    truth = home["object_body_view_truth"]
    checks = "\n".join(
        f"<div class='row'><strong>{escape(c['code'])}</strong><span>{'PASS' if c['passed'] else 'FAIL'}</span></div>"
        for c in home["validation"]["checks"]
    )
    routes = home["routes"]
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Vault Real Storage Provider Object Body View Lock Contract · GP069</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root {{
  --bg0:#040612; --bg1:#090d22; --panel:rgba(15,23,52,.86); --panel2:rgba(21,32,74,.76);
  --line:rgba(160,179,255,.24); --text:#eef3ff; --muted:#9da9d7; --gold:#f5d17e;
  --cyan:#83eaff; --danger:#ff8c9c; --ok:#9dffca;
}}
* {{ box-sizing:border-box; }}
body {{
  margin:0; min-height:100vh; color:var(--text);
  font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  background:
    radial-gradient(circle at 12% 9%, rgba(173,141,255,.18), transparent 34%),
    radial-gradient(circle at 88% 5%, rgba(131,234,255,.13), transparent 30%),
    linear-gradient(135deg,var(--bg0),var(--bg1) 52%,#03040b);
}}
.shell {{ width:min(1240px, calc(100% - 32px)); margin:0 auto; padding:34px 0 48px; }}
.hero,.section {{ border:1px solid var(--line); background:var(--panel); border-radius:28px; padding:26px; margin-top:18px; }}
.eyebrow {{ color:var(--gold); letter-spacing:.18em; text-transform:uppercase; font-size:12px; font-weight:850; }}
h1 {{ margin:14px 0; font-size:clamp(34px,5vw,62px); line-height:.95; }}
p {{ color:var(--muted); line-height:1.62; }}
.grid {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:14px; margin-top:18px; }}
.metric,.card {{ border:1px solid var(--line); background:var(--panel2); border-radius:20px; padding:16px; }}
.metric strong {{ display:block; font-size:26px; }}
.metric span,.muted {{ color:var(--muted); }}
.chips {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:14px; }}
.pill {{ border:1px solid var(--line); border-radius:999px; padding:7px 10px; font-size:12px; font-weight:800; background:rgba(10,16,38,.72); }}
.ok {{ color:var(--ok); }} .danger {{ color:var(--danger); }}
.row {{ display:flex; justify-content:space-between; gap:12px; padding:10px 0; border-bottom:1px solid rgba(160,179,255,.14); }}
code {{ color:var(--cyan); background:rgba(0,0,0,.28); border:1px solid var(--line); border-radius:8px; padding:2px 6px; }}
@media(max-width:900px) {{ .grid {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<main class="shell">
  <section class="hero">
    <div class="eyebrow">Archive Vault · Giant Pack 069</div>
    <div class="eyebrow">Real Storage Provider Configuration Layer · GP061-GP070</div>
    <h1>Real Storage Provider Object Body View Lock Contract</h1>
    <p>GP069 creates a real object body view lock contract. It does not expose object body content, plaintext, downloads, exports, or execution.</p>
    <div class="grid">
      <div class="metric"><strong>{truth['requirement_count']}</strong><span>requirements</span></div>
      <div class="metric"><strong>{truth['policy_count']}</strong><span>policies</span></div>
      <div class="metric"><strong>{truth['object_body_view_attempted_count']}</strong><span>view attempts</span></div>
      <div class="metric"><strong>{str(truth['vault_done']).lower()}</strong><span>vault done</span></div>
    </div>
    <div class="chips">
      <span class="pill ok">Object body view lock ready</span>
      <span class="pill ok">Real SQLite-backed</span>
      <span class="pill danger">No object body view</span>
      <span class="pill danger">No plaintext</span>
      <span class="pill danger">No download</span>
      <span class="pill danger">No execution</span>
    </div>
  </section>
  <section class="section">
    <h2>Validation Checks</h2>
    {checks}
  </section>
  <section class="section">
    <h2>GP069 JSON Endpoints</h2>
    <p>
      <code>{escape(routes['json_route'])}</code>
      <code>{escape(routes['record_route'])}</code>
      <code>{escape(routes['requirements_route'])}</code>
      <code>{escape(routes['policies_route'])}</code>
      <code>{escape(routes['blockers_route'])}</code>
      <code>{escape(routes['events_route'])}</code>
      <code>{escape(routes['validation_route'])}</code>
      <code>{escape(routes['next_step_route'])}</code>
      <code>{escape(routes['gp069_status_route'])}</code>
    </p>
  </section>
</main>
</body>
</html>"""
