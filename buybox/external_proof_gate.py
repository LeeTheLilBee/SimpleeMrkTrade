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

_PROOF_RECORD_FIELDS = frozenset({
    "kind", "issuer", "receipt_ref", "purpose", "source_opportunity_id",
    "source_opportunity_revision", "source_snapshot_digest", "deal_fingerprint",
    "verified_at", "authentication_scope", "browser_supplied_authority",
    "authorizes_purchase", "authorizes_money", "record_sha256",
})
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
# BBX102–106's separately authenticated canonical Vault receiver stores a
# narrower archival source linkage in addition to the generic proof fields.
_VAULT_RECEIPT_FIELDS = frozenset({
    "evidence_id", "source_document_id", "verified_sha256",
    "vault_document_ref", "vault_version_ref", "decision_snapshot_id",
})


def _valid_stored_proof(proof, op, fingerprint):
    """Check local receipt-record integrity before displaying it as present.

    This is NOT external issuer authentication: SHA-256 is not a MAC or
    signature. Only record_verified_external_proof's trusted server verifier
    may create authoritative external proof; owner release is separate.
    """
    if not isinstance(proof, dict) or not isinstance(proof.get("kind"), str):
        return False
    if proof["kind"] not in KINDS:
        return False
    canonical_vault = (proof["kind"] == "VAULT_CANONICAL_ARCHIVAL"
                       and set(proof) == _PROOF_RECORD_FIELDS | _VAULT_RECEIPT_FIELDS)
    if set(proof) != _PROOF_RECORD_FIELDS and not canonical_vault:
        return False
    expected_scope = (
        "TRUSTED_TOWER_VAULT_ADAPTER_ONLY" if canonical_vault
        else "TRUSTED_SERVER_ADAPTER_ONLY"
    )
    if (
        proof["kind"] not in KINDS
        or proof["source_opportunity_id"] != op.get("id")
        or type(proof["source_opportunity_revision"]) is not int
        or proof["source_opportunity_revision"] < 1
        or type(op.get("version")) is not int
        or proof["source_opportunity_revision"] > op["version"]
        or proof["deal_fingerprint"] != fingerprint
        or proof["authentication_scope"] != expected_scope
        or proof["browser_supplied_authority"] is not False
        or proof["authorizes_purchase"] is not False
        or proof["authorizes_money"] is not False
    ):
        return False
    if not isinstance(proof["source_snapshot_digest"], str) or not _HEX64.fullmatch(
        proof["source_snapshot_digest"]
    ):
        return False
    if canonical_vault:
        if not isinstance(proof["verified_sha256"], str) or not _HEX64.fullmatch(
            proof["verified_sha256"]
        ):
            return False
        if not all(
            isinstance(proof[key], str) and OPAQUE.fullmatch(proof[key])
            for key in _VAULT_RECEIPT_FIELDS - {"verified_sha256"}
        ):
            return False
    if not all(isinstance(proof[key], str) and OPAQUE.fullmatch(proof[key])
               for key in ("issuer", "receipt_ref", "purpose")):
        return False
    timestamp = proof["verified_at"]
    if not isinstance(timestamp, str):
        return False
    try:
        verified_at = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError:
        return False
    if verified_at.tzinfo is None or verified_at.utcoffset() is None:
        return False
    checksum = proof["record_sha256"]
    if not isinstance(checksum, str) or not _HEX64.fullmatch(checksum):
        return False
    body = {key: value for key, value in proof.items() if key != "record_sha256"}
    expected = sha256(json.dumps(
        body, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()).hexdigest()
    return checksum == expected


def integration_readiness(op):
    current = {}
    fingerprint=_deal_fingerprint(op)
    candidates = op.get("external_proofs", [])
    if not isinstance(candidates, list):
        candidates = []
    for proof in candidates:
        if _valid_stored_proof(proof, op, fingerprint):
            current[proof["kind"]] = proof
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
