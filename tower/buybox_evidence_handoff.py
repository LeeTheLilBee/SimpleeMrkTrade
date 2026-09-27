"""Tower-side BuyBox evidence intake preparation; does not execute archival or grant authority."""
from __future__ import annotations
from typing import Any, Mapping
from vault.buybox_evidence_handoff_contract import validate_buybox_evidence_request, request_fingerprint, validate_tower_safe_response

def prepare_buybox_evidence_handoff(packet: Mapping[str, Any], *, tower_context: Mapping[str, Any]) -> dict[str, Any]:
    """Fail closed. Caller must supply a verified Tower decision, not a BuyBox assertion."""
    p = validate_buybox_evidence_request(packet)
    c = dict(tower_context)
    required = ("identity_verified", "permission_verified", "entity_verified", "purpose_verified", "classification_verified", "retention_verified", "redaction_verified", "approval_verified")
    if any(c.get(key) is not True for key in required):
        return validate_tower_safe_response({"schema_version": p["schema_version"], "request_id": p["request_id"], "status": "DENIED", "reason_code": "TOWER_GATE_INCOMPLETE"})
    if c.get("principal_ref") != p["requester"]["principal_ref"] or c.get("entity_id") != p["requester"]["entity_id"]:
        return validate_tower_safe_response({"schema_version": p["schema_version"], "request_id": p["request_id"], "status": "DENIED", "reason_code": "TOWER_CONTEXT_MISMATCH"})
    # A verified gate is not a transfer, scan result, storage commit, or archival receipt.
    return validate_tower_safe_response({"schema_version": p["schema_version"], "request_id": p["request_id"], "status": "PENDING", "reason_code": "CONTROLLED_TRANSFER_AND_SCAN_REQUIRED", "evidence_id": p["acquisition"]["evidence_id"], "decision_snapshot_id": p["acquisition"]["decision_snapshot_id"]})
