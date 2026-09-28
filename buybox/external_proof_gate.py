"""BBX097-101: authenticated-external-proof intake boundary and owner release matrix.

BuyBox never authenticates another product by trusting browser JSON. External
proofs may enter only through a separately injected trusted verifier that
returns server-verified claims bound to the exact persisted BuyBox source.
This module itself performs no network calls and grants no acquisition action.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
import re
import sqlite3

from .store import encode
from .tower_action_draft import stored_source_snapshot, BuyBoxTowerActionPreparationError

KINDS = frozenset({
    "TOWER_PROTECTED_ACTION",
    "TELLER_MONEY_AND_MANAGEMENT",
    "VAULT_CANONICAL_ARCHIVAL",
    "OPERATIONS_RECEIVER_ACCEPTANCE",
})
OPAQUE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{7,255}$")

class ExternalProofError(ValueError):
    pass

def _deal_fingerprint(op):
    """Stable across proof-only saves; changes for ordinary deal-source edits."""
    material=deepcopy(op)
    material.pop("external_proofs",None)
    material.pop("version",None)
    material.pop("updated_at",None)
    return sha256(json.dumps(
        material,sort_keys=True,separators=(",",":"),ensure_ascii=False
    ).encode()).hexdigest()

def _current_source(db, op):
    if not isinstance(db, sqlite3.Connection):
        raise ExternalProofError("PERSISTED_SOURCE_REQUIRED")
    try:
        src = stored_source_snapshot(db, op["id"])
    except (BuyBoxTowerActionPreparationError, sqlite3.DatabaseError) as exc:
        raise ExternalProofError("CURRENT_SOURCE_UNAVAILABLE") from exc
    digest = sha256(encode(op).encode("utf-8")).hexdigest()
    if src["opportunity_revision"] != op.get("version") or src["input_snapshot_digest"] != digest:
        raise ExternalProofError("CURRENT_SOURCE_CHANGED")
    return src

def _verified_claims(verifier, raw_proof):
    if verifier is None or not callable(verifier):
        raise ExternalProofError("TRUSTED_VERIFIER_REQUIRED")
    claims = verifier(raw_proof)
    if not isinstance(claims, dict) or claims.get("authenticated") is not True:
        raise ExternalProofError("EXTERNAL_PROOF_NOT_AUTHENTICATED")
    return claims

def record_verified_external_proof(db, op, *, kind, raw_proof, verifier, now_utc=None):
    if kind not in KINDS:
        raise ExternalProofError("PROOF_KIND_INVALID")
    src = _current_source(db, op)
    claims = _verified_claims(verifier, raw_proof)
    required = {
        "authenticated","issuer","receipt_ref","opportunity_id",
        "opportunity_revision","input_snapshot_digest","purpose",
    }
    if set(claims) != required:
        raise ExternalProofError("VERIFIED_CLAIMS_FIELDS_INVALID")
    if claims["opportunity_id"] != src["opportunity_id"] or claims["opportunity_revision"] != src["opportunity_revision"] or claims["input_snapshot_digest"] != src["input_snapshot_digest"]:
        raise ExternalProofError("VERIFIED_PROOF_SOURCE_MISMATCH")
    if not isinstance(claims["issuer"], str) or OPAQUE.fullmatch(claims["issuer"]) is None:
        raise ExternalProofError("VERIFIED_ISSUER_INVALID")
    if not isinstance(claims["receipt_ref"], str) or OPAQUE.fullmatch(claims["receipt_ref"]) is None:
        raise ExternalProofError("VERIFIED_RECEIPT_INVALID")
    if not isinstance(claims["purpose"], str) or OPAQUE.fullmatch(claims["purpose"]) is None:
        raise ExternalProofError("VERIFIED_PURPOSE_INVALID")
    now = datetime.now(timezone.utc) if now_utc is None else now_utc
    if not isinstance(now, datetime) or now.tzinfo is None or now.utcoffset() is None:
        raise ExternalProofError("AWARE_TIME_REQUIRED")
    record = {
        "kind":kind,
        "issuer":claims["issuer"],
        "receipt_ref":claims["receipt_ref"],
        "purpose":claims["purpose"],
        "source_opportunity_id":src["opportunity_id"],
        "source_opportunity_revision":src["opportunity_revision"],
        "source_snapshot_digest":src["input_snapshot_digest"],
        "deal_fingerprint":_deal_fingerprint(op),
        "verified_at":now.astimezone(timezone.utc).isoformat(),
        "authentication_scope":"TRUSTED_SERVER_ADAPTER_ONLY",
        "browser_supplied_authority":False,
        "authorizes_purchase":False,
        "authorizes_money":False,
    }
    record["record_sha256"] = sha256(json.dumps(
        record,sort_keys=True,separators=(",",":"),ensure_ascii=False
    ).encode()).hexdigest()
    revised=deepcopy(op)
    revised.setdefault("external_proofs",[]).append(record)
    return revised, deepcopy(record)

def integration_readiness(op):
    current = {}
    fingerprint=_deal_fingerprint(op)
    for proof in op.get("external_proofs",[]):
        if proof.get("deal_fingerprint") == fingerprint:
            current[proof.get("kind")] = proof
    required = [
        "TOWER_PROTECTED_ACTION",
        "TELLER_MONEY_AND_MANAGEMENT",
        "VAULT_CANONICAL_ARCHIVAL",
    ]
    if op.get("vertical") in ("atm","multifamily"):
        required.append("OPERATIONS_RECEIVER_ACCEPTANCE")
    rows=[{"kind":kind,"present":kind in current,
           "receipt_ref":current.get(kind,{}).get("receipt_ref")} for kind in required]
    missing=[row["kind"] for row in rows if not row["present"]]
    return {
        "requirements":rows,
        "missing":missing,
        "external_proofs_complete":not missing,
        "source_state":"EXTERNAL_PROOFS_COMPLETE_OWNER_RELEASE_STILL_REQUIRED" if not missing else "EXTERNAL_PROOFS_PENDING",
        "owner_release_required":True,
        "hosted_runtime_certified":False,
        "authorizes_purchase":False,
        "authorizes_money":False,
        "authorizes_closing":False,
        "can_mark_operational":False,
    }
