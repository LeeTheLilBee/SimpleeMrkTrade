"""BuyBox acquisition-evidence contract. Metadata-only, no Vault transport or authorization."""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Mapping

SCHEMA_VERSION = "buybox.vault.evidence.v1"
OPERATIONS = frozenset({"PREPARE_ARCHIVAL", "ARCHIVAL_STATUS", "PROOF_STATUS", "VERSION_HISTORY", "REQUEST_PROTECTED_DOWNLOAD", "REGISTER_CORRECTION"})
OUTPUTS = frozenset({"ARCHIVAL_RECEIPT", "STATUS", "PROOF_REFERENCE", "VERSION_HISTORY", "DOWNLOAD_DECISION"})
SHA256 = re.compile(r"^[a-f0-9]{64}$")
OPAQUE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
FORBIDDEN = ("raw_path", "vault_path", "vault_url", "public_url", "download_token", "share_token", "file_bytes", "raw_bytes", "secret", "authorization_header", "bearer")
REQUIRED = {
    "request_id", "idempotency_key", "source_app", "destination", "workflow_type",
    "requested_operation", "requester", "acquisition", "document", "controls", "transport", "schema_version"
}

class ContractError(ValueError):
    pass

def _object(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise ContractError(name + " must be an object")
    return value

def _id(value: Any, name: str) -> str:
    if not isinstance(value, str) or not OPAQUE_ID.fullmatch(value):
        raise ContractError(name + " must be an opaque identifier")
    return value

def _keys(value: Mapping[str, Any], allowed: set[str], name: str) -> None:
    extra = set(value) - allowed
    if extra:
        raise ContractError(name + " contains unrecognized fields: " + ", ".join(sorted(extra)))

def validate_buybox_evidence_request(packet: Mapping[str, Any]) -> dict[str, Any]:
    p = _object(packet, "packet")
    _keys(p, REQUIRED, "packet")
    if set(p) != REQUIRED:
        raise ContractError("packet required fields missing")
    if p["schema_version"] != SCHEMA_VERSION or p["source_app"] != "BUYBOX" or p["destination"] != "TOWER":
        raise ContractError("invalid schema or routing")
    if p["workflow_type"] != "acquisition_evidence_archive" or p["requested_operation"] not in OPERATIONS:
        raise ContractError("unsupported workflow or operation")
    _id(p["request_id"], "request_id")
    _id(p["idempotency_key"], "idempotency_key")
    requester = _object(p["requester"], "requester")
    _keys(requester, {"principal_ref", "role", "entity_id", "purpose"}, "requester")
    for k in ("principal_ref", "role", "entity_id", "purpose"):
        _id(requester.get(k), k)
    if requester["purpose"] != "acquisition_due_diligence":
        raise ContractError("unsupported purpose")
    acquisition = _object(p["acquisition"], "acquisition")
    _keys(acquisition, {"deal_id", "asset_type", "evidence_id", "decision_snapshot_id"}, "acquisition")
    for k in ("deal_id", "asset_type", "evidence_id", "decision_snapshot_id"):
        _id(acquisition.get(k), k)
    document = _object(p["document"], "document")
    _keys(document, {"source_document_id", "source_version_id", "original_document_ref", "sha256", "byte_size", "declared_mime_type", "classification", "parent_version_id", "correction_of_version_id"}, "document")
    for k in ("source_document_id", "source_version_id", "original_document_ref", "classification"):
        _id(document.get(k), k)
    for k in ("parent_version_id", "correction_of_version_id"):
        if document.get(k) is not None:
            _id(document[k], k)
            if document[k] == document["source_version_id"]:
                raise ContractError("a version cannot refer to itself")
    if not isinstance(document.get("sha256"), str) or not SHA256.fullmatch(document["sha256"]):
        raise ContractError("invalid sha256")
    if type(document.get("byte_size")) is not int or document["byte_size"] < 0:
        raise ContractError("invalid byte size")
    if document.get("declared_mime_type") not in {"application/pdf", "image/jpeg", "image/png", "text/plain", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}:
        raise ContractError("unsupported declared mime type")
    controls = _object(p["controls"], "controls")
    _keys(controls, {"malware_scan_required", "retention_policy_id", "redaction_profile_id", "owner_approval_required", "requested_output"}, "controls")
    if controls.get("malware_scan_required") is not True or controls.get("owner_approval_required") is not True:
        raise ContractError("required safety gates missing")
    _id(controls.get("retention_policy_id"), "retention_policy_id")
    _id(controls.get("redaction_profile_id"), "redaction_profile_id")
    if controls.get("requested_output") not in OUTPUTS:
        raise ContractError("unsupported output")
    transport = _object(p["transport"], "transport")
    _keys(transport, {"metadata_only", "raw_bytes_in_json", "public_url_requested", "direct_vault_access"}, "transport")
    if transport != {"metadata_only": True, "raw_bytes_in_json": False, "public_url_requested": False, "direct_vault_access": False}:
        raise ContractError("unsafe transport request")
    serialized = json.dumps(p, sort_keys=True, separators=(",", ":"), allow_nan=False)
    if any('"' + k + '"' in serialized.lower() for k in FORBIDDEN):
        raise ContractError("forbidden field")
    return json.loads(serialized)

def request_fingerprint(packet: Mapping[str, Any]) -> str:
    valid = validate_buybox_evidence_request(packet)
    return hashlib.sha256(json.dumps(valid, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def validate_tower_safe_response(response: Mapping[str, Any]) -> dict[str, Any]:
    r = _object(response, "response")
    allowed = {"schema_version", "request_id", "status", "reason_code", "evidence_id", "vault_document_ref", "vault_version_ref", "archival_receipt_id", "verified_sha256", "proof_reference", "retention_policy_id", "decision_snapshot_id"}
    _keys(r, allowed, "response")
    if r.get("schema_version") != SCHEMA_VERSION:
        raise ContractError("invalid response schema")
    for k, v in r.items():
        if k in {"schema_version", "status", "reason_code"}:
            if not isinstance(v, str):
                raise ContractError("invalid response value")
        elif k == "verified_sha256":
            if not isinstance(v, str) or not SHA256.fullmatch(v):
                raise ContractError("invalid verified hash")
        elif v is not None:
            _id(v, k)
    if r.get("status") not in {"PENDING", "DENIED", "QUARANTINED", "ARCHIVED", "FAILED", "SUPERSEDED", "AUTHORIZED"}:
        raise ContractError("invalid status")
    if r["status"] == "ARCHIVED" and not all(r.get(k) for k in ("archival_receipt_id", "vault_document_ref", "vault_version_ref", "verified_sha256")):
        raise ContractError("archived requires verified receipt and version")
    return dict(r)
