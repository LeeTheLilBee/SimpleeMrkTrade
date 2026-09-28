"""BBX102-106: canonical Vault archival receipt acceptance through trusted transport.

The existing metadata draft and response shape remain buybox.vault.evidence.v1.
This module still does no network I/O. A response becomes locally recordable
only when an injected trusted transport verifier authenticates it and the
receipt exactly correlates to the current persisted BuyBox source, frozen
snapshot, evidence record, source document and SHA-256 digest.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
import sqlite3

from .tower_action_draft import stored_source_snapshot, BuyBoxTowerActionPreparationError
from .tower_evidence import inspect_untrusted_response, HandoffPreparationError
from .external_proof_gate import _deal_fingerprint

class VaultReceiptError(ValueError):
    pass

def _source(db,op):
    if not isinstance(db,sqlite3.Connection):
        raise VaultReceiptError("PERSISTED_SOURCE_REQUIRED")
    try: return stored_source_snapshot(db,op["id"])
    except (BuyBoxTowerActionPreparationError,sqlite3.DatabaseError) as exc:
        raise VaultReceiptError("CURRENT_SOURCE_UNAVAILABLE") from exc

def record_authenticated_archival_receipt(db,op,*,packet,raw_response,trusted_response_verifier,now_utc=None):
    src=_source(db,op)
    if trusted_response_verifier is None or not callable(trusted_response_verifier):
        raise VaultReceiptError("TRUSTED_VAULT_RESPONSE_VERIFIER_REQUIRED")
    response=trusted_response_verifier(raw_response)
    if not isinstance(response,dict):
        raise VaultReceiptError("AUTHENTICATED_VAULT_RESPONSE_REQUIRED")
    try:
        checked=inspect_untrusted_response(packet,response)
    except HandoffPreparationError as exc:
        raise VaultReceiptError(str(exc)) from exc
    if not checked["correlated"] or response.get("status")!="ARCHIVED":
        raise VaultReceiptError("CANONICAL_ARCHIVED_RECEIPT_REQUIRED")
    if packet.get("acquisition",{}).get("deal_id")!=op.get("id"):
        raise VaultReceiptError("RECEIPT_DEAL_MISMATCH")
    if packet.get("acquisition",{}).get("evidence_id")!=response.get("evidence_id"):
        raise VaultReceiptError("RECEIPT_EVIDENCE_MISMATCH")
    if packet.get("document",{}).get("sha256")!=response.get("verified_sha256"):
        raise VaultReceiptError("RECEIPT_DIGEST_MISMATCH")
    snapshot_id=packet.get("acquisition",{}).get("decision_snapshot_id")
    snap=next((s for s in op.get("snapshots",[]) if s.get("snapshot_id")==snapshot_id),None)
    if snap is None:
        raise VaultReceiptError("LOCAL_FROZEN_SNAPSHOT_REQUIRED")
    expected=next((v for v in snap.get("evidence_versions",[]) if v.get("evidence_id")==response.get("evidence_id") and v.get("sha256")==response.get("verified_sha256")),None)
    if expected is None:
        raise VaultReceiptError("FROZEN_SOURCE_MISMATCH")
    if src["opportunity_revision"]!=op.get("version"):
        raise VaultReceiptError("CURRENT_SOURCE_REVISION_MISMATCH")
    now=datetime.now(timezone.utc) if now_utc is None else now_utc
    if not isinstance(now,datetime) or now.tzinfo is None or now.utcoffset() is None:
        raise VaultReceiptError("AWARE_TIME_REQUIRED")
    record={
        "kind":"VAULT_CANONICAL_ARCHIVAL","issuer":"tower-vault-authenticated-corridor",
        "receipt_ref":response["archival_receipt_id"],"purpose":"acquisition-evidence-archival",
        "source_opportunity_id":src["opportunity_id"],"source_opportunity_revision":src["opportunity_revision"],
        "source_snapshot_digest":src["input_snapshot_digest"],"deal_fingerprint":_deal_fingerprint(op),
        "evidence_id":response["evidence_id"],
        "source_document_id":packet["document"]["source_document_id"],"verified_sha256":response["verified_sha256"],
        "vault_document_ref":response["vault_document_ref"],"vault_version_ref":response["vault_version_ref"],
        "decision_snapshot_id":snapshot_id,"verified_at":now.astimezone(timezone.utc).isoformat(),
        "authentication_scope":"TRUSTED_TOWER_VAULT_ADAPTER_ONLY","browser_supplied_authority":False,
        "authorizes_purchase":False,"authorizes_money":False,
    }
    record["record_sha256"]=sha256(json.dumps(record,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
    revised=deepcopy(op)
    revised.setdefault("external_proofs",[]).append(record)
    return revised,deepcopy(record)
