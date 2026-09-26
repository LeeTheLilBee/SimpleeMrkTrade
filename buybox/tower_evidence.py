"""BuyBox-side metadata preparation for Tower ↔ Vault evidence contract v1.

STRICTLY NO NETWORK, NO VAULT IMPORT, NO AUTHORIZATION, NO ARCHIVAL.
The authoritative schema is in PR #35:
vault/buybox_evidence_handoff_contract.py @ 1b9a3e191cf8f8b61adb59b790033983f767f42f.
This module produces metadata drafts for Tower to authenticate/revalidate later.
"""
from __future__ import annotations
from copy import deepcopy
from hashlib import sha256
import json
import re
from uuid import uuid4
from .core import now
from .registry import get_vertical

SCHEMA_VERSION = "buybox.vault.evidence.v1"
MIMES = frozenset({
    "application/pdf", "image/jpeg", "image/png", "text/plain",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
})
ASSET_TYPE = {
    "atm": "ATM_ROUTE", "multifamily": "MULTIFAMILY",
    "commercial": "COMMERCIAL_PROPERTY", "laundromat": "LAUNDROMAT",
    "land_farm": "LAND_FARM", "business": "OPERATING_BUSINESS",
    "equipment": "EQUIPMENT",
}
OPAQUE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
SHA256 = re.compile(r"^[a-f0-9]{64}$")
STATES = frozenset({"PENDING", "DENIED", "QUARANTINED", "ARCHIVED",
                    "FAILED", "SUPERSEDED", "AUTHORIZED"})

class HandoffPreparationError(ValueError):
    pass

def _ref(value, field):
    if not isinstance(value, str) or not OPAQUE.fullmatch(value):
        raise HandoffPreparationError("INVALID_OPAQUE_REFERENCE:" + field)
    return value

def _artifact_and_evidence(op, artifact_id, evidence_id):
    artifact = next((x for x in op.get("artifacts", []) if x.get("id") == artifact_id), None)
    evidence = next((x for x in op.get("evidence", []) if x.get("id") == evidence_id), None)
    if not artifact or not evidence or evidence.get("artifact_id") != artifact_id:
        raise HandoffPreparationError("ARTIFACT_EVIDENCE_LINK_REQUIRED")
    if not SHA256.fullmatch(str(artifact.get("sha256", ""))):
        raise HandoffPreparationError("INVALID_SOURCE_HASH")
    if artifact.get("mime") not in MIMES:
        raise HandoffPreparationError("MIME_NOT_IN_CANONICAL_CONTRACT")
    size = artifact.get("size_bytes")
    if type(size) is not int or size <= 0:
        raise HandoffPreparationError("INVALID_SOURCE_SIZE")
    # Never include local encrypted storage_reference or filesystem paths.
    return artifact, evidence

def freeze_local_evidence_snapshot(op, *, evidence_id, artifact_id, actor_reference):
    """Return a revised opportunity and an immutable-by-value reference draft.

    Persistence must use the ordinary optimistic versioned store. This is NOT a
    canonical Vault receipt and does not confer seller/title verification.
    """
    if not actor_reference:
        raise HandoffPreparationError("ACTOR_REQUIRED")
    artifact, evidence = _artifact_and_evidence(op, artifact_id, evidence_id)
    snapshot_id = str(uuid4())
    material = {
        "snapshot_id": snapshot_id,
        "deal_id": op["id"],
        "opportunity_revision": op["version"],
        "vertical_id": op["vertical"],
        "rule_version": get_vertical(op["vertical"])["version"],
        "evidence_versions": [{
            "evidence_id": evidence["id"],
            "source_document_id": artifact["id"],
            "source_version_id": artifact["id"],
            "sha256": artifact["sha256"],
            "evidence_state": evidence["status"],
        }],
        "actor_reference": _ref(actor_reference, "actor_reference"),
        "created_at": now(),
        "archive_state": "NOT_REQUESTED",
        "authorizes_action": False,
    }
    digest = sha256(json.dumps(material,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    snapshot = {**material,"snapshot_sha256": digest}
    revised = deepcopy(op)
    revised.setdefault("snapshots", []).append(snapshot)
    return revised,deepcopy(snapshot)

def make_tower_metadata_draft(op, *, evidence_id, artifact_id, snapshot_id,
                              principal_ref, role, entity_id, classification,
                              retention_policy_id, redaction_profile_id,
                              request_id=None, idempotency_key=None,
                              parent_version_id=None, correction_of_version_id=None):
    """Create only a locally prepared packet; actual Tower must derive requester.

    Identity, policy IDs and authorization MUST be supplied and independently
    verified by the eventual Tower caller, NOT accepted from web form inputs.
    This method performs shape/provenance checks, not identity verification.
    """
    artifact,evidence=_artifact_and_evidence(op,artifact_id,evidence_id)
    snapshot=next((x for x in op.get("snapshots",[])
                   if x.get("snapshot_id")==snapshot_id),None)
    if not snapshot or snapshot.get("deal_id")!=op["id"] or snapshot.get("archive_state")!="NOT_REQUESTED":
        raise HandoffPreparationError("LOCAL_EVIDENCE_SNAPSHOT_REQUIRED")
    expected=[x for x in snapshot.get("evidence_versions",[])
              if x.get("evidence_id")==evidence_id and
                 x.get("source_document_id")==artifact_id and
                 x.get("sha256")==artifact["sha256"]]
    if not expected:
        raise HandoffPreparationError("SNAPSHOT_SOURCE_MISMATCH")
    for field,value in {
        "principal_ref": principal_ref,"role":role,"entity_id":entity_id,
        "classification":classification,"retention_policy_id":retention_policy_id,
        "redaction_profile_id":redaction_profile_id,
    }.items(): _ref(value,field)
    for field,value in {"parent_version_id":parent_version_id,
                        "correction_of_version_id":correction_of_version_id}.items():
        if value is not None:
            _ref(value,field)
            if value==artifact["id"]:
                raise HandoffPreparationError("SELF_REFERENCING_VERSION")
    req=_ref(request_id or str(uuid4()),"request_id")
    idem=_ref(idempotency_key or req,"idempotency_key")
    packet={
        "schema_version":SCHEMA_VERSION,
        "request_id":req,
        "idempotency_key":idem,
        "source_app":"BUYBOX","destination":"TOWER",
        "workflow_type":"acquisition_evidence_archive",
        "requested_operation":"PREPARE_ARCHIVAL",
        "requester":{
            "principal_ref":principal_ref,"role":role,"entity_id":entity_id,
            "purpose":"acquisition_due_diligence",
        },
        "acquisition":{
            "deal_id":op["id"],"asset_type":ASSET_TYPE[op["vertical"]],
            "evidence_id":evidence["id"],"decision_snapshot_id":snapshot_id,
        },
        "document":{
            "source_document_id":artifact["id"],
            "source_version_id":artifact["id"],
            "original_document_ref":artifact["id"],
            "sha256":artifact["sha256"],
            "byte_size":artifact["size_bytes"],
            "declared_mime_type":artifact["mime"],
            "classification":classification,
            "parent_version_id":parent_version_id,
            "correction_of_version_id":correction_of_version_id,
        },
        "controls":{
            "malware_scan_required":True,
            "retention_policy_id":retention_policy_id,
            "redaction_profile_id":redaction_profile_id,
            "owner_approval_required":True,
            "requested_output":"ARCHIVAL_RECEIPT",
        },
        "transport":{
            "metadata_only":True,
            "raw_bytes_in_json":False,
            "public_url_requested":False,
            "direct_vault_access":False,
        },
    }
    # Do not provide a transport, fake verified Tower context, or archived status.
    return deepcopy(packet)

def inspect_untrusted_response(packet, response):
    """Validate correlation only; never promote arbitrary JSON to archival truth."""
    if not isinstance(response,dict) or response.get("schema_version")!=SCHEMA_VERSION:
        raise HandoffPreparationError("INVALID_RESPONSE_SCHEMA")
    if response.get("request_id")!=packet.get("request_id"):
        raise HandoffPreparationError("RESPONSE_REQUEST_MISMATCH")
    if response.get("status") not in STATES:
        raise HandoffPreparationError("INVALID_RESPONSE_STATUS")
    allowed={
        "schema_version","request_id","status","reason_code","evidence_id",
        "vault_document_ref","vault_version_ref","archival_receipt_id",
        "verified_sha256","proof_reference","retention_policy_id",
        "decision_snapshot_id",
    }
    if set(response)-allowed:
        raise HandoffPreparationError("UNSAFE_RESPONSE_FIELDS")
    if response.get("status")=="ARCHIVED":
        required=("archival_receipt_id","vault_document_ref",
                  "vault_version_ref","verified_sha256")
        if any(not response.get(k) for k in required):
            raise HandoffPreparationError("ARCHIVAL_RECEIPT_INCOMPLETE")
        if response["verified_sha256"]!=packet["document"]["sha256"]:
            raise HandoffPreparationError("ARCHIVAL_DIGEST_MISMATCH")
        if response.get("evidence_id") not in (None,packet["acquisition"]["evidence_id"]):
            raise HandoffPreparationError("ARCHIVAL_EVIDENCE_MISMATCH")
    # No authenticated connector exists. This is an UNTRUSTED observation,
    # never an authorized transition even if the JSON says ARCHIVED.
    return {"correlated":True,"authoritative":False,
            "archived":False,"reason":"AUTHENTICATED_TOWER_CONNECTOR_UNAVAILABLE",
            "untrusted_claimed_status":response["status"]}
