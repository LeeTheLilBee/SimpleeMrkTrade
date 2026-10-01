"""Evidence lineage primitives.

Pure, storage-independent records. The original bytes belong in an encrypted
object store behind a Tower-controlled document flow, not in opportunity JSON.
Neither extraction nor document receipt means factual verification.
"""
from __future__ import annotations
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from uuid import uuid4

ALLOWED_STATES = frozenset({
    "CLAIMED", "RECEIVED", "DOCUMENT_SUPPORTED", "THIRD_PARTY_VERIFIED",
    "CONFLICTED", "STALE", "MISSING", "NOT_APPLICABLE", "SUPERSEDED",
})
TRUTH_KINDS = frozenset({"FACT", "ASSUMPTION", "RULE", "JUDGMENT"})
VALID_MIMES = frozenset({
    "application/pdf", "image/png", "image/jpeg", "text/csv",
    "text/plain", "application/json",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
})
MAX_BYTES = 50 * 1024 * 1024

def instant():
    return datetime.now(timezone.utc).isoformat()

def artifact_descriptor(contents, *, filename, mime, storage_reference, source_party=None):
    """Derive the actual digest from bytes; caller is responsible for protected storage.

    Empty or oversized files and unsafe names are rejected. The storage reference
    is a reference, not a public download URL.
    """
    if not isinstance(contents, bytes) or not contents or len(contents) > MAX_BYTES:
        raise ValueError("INVALID_ARTIFACT_BYTES")
    if mime not in VALID_MIMES:
        raise ValueError("UNSUPPORTED_ARTIFACT_MIME")
    if not isinstance(filename, str) or not filename or "/" in filename or "\\" in filename or "\x00" in filename:
        raise ValueError("INVALID_ARTIFACT_NAME")
    if not isinstance(storage_reference, str) or not storage_reference.strip():
        raise ValueError("MISSING_STORAGE_REFERENCE")
    if storage_reference.startswith(("http://", "https://", "file://")):
        raise ValueError("STORAGE_REFERENCE_MUST_BE_OPAQUE")
    return {
        "id": str(uuid4()), "name": filename, "mime": mime, "size_bytes": len(contents),
        "sha256": sha256(contents).hexdigest(), "storage_reference": storage_reference,
        "source_party": source_party, "received_at": instant(),
        "verification_state": "RECEIVED", "extraction_state": "NOT_STARTED",
        "supersedes": None,
    }

def claim(*, artifact_id, claim_type, subject_id, value, locator, method="EXTRACTED",
          evidence_state="CLAIMED", source_party=None):
    """A claim must always point to a source artifact and an exact source locator.

    There is deliberately no arbitrary auto-verified flag. Verification is a
    separate reviewed action, not an AI extraction side effect.
    """
    if not all(isinstance(x,str) and x.strip() for x in (artifact_id, claim_type, subject_id, locator)):
        raise ValueError("CLAIM_REQUIRES_SOURCE_AND_LOCATOR")
    if evidence_state not in ALLOWED_STATES:
        raise ValueError("INVALID_EVIDENCE_STATE")
    if method not in ("EXTRACTED", "MANUAL_TRANSCRIPTION", "SOURCE_STATEMENT"):
        raise ValueError("INVALID_CLAIM_METHOD")
    return {
        "id": str(uuid4()), "artifact_id": artifact_id, "claim_type": claim_type,
        "subject_id": subject_id, "value": deepcopy(value), "locator": locator,
        "method": method, "evidence_state": evidence_state, "source_party": source_party,
        "created_at": instant(), "verification": None, "supersedes": None,
    }

def review_claim(source_claim, *, reviewer_reference, decision, supporting_references=(),
                 explanation=""):
    """Make a new revision of a claim; never overwrite the source statement."""
    if not reviewer_reference or decision not in ("DOCUMENT_SUPPORTED", "THIRD_PARTY_VERIFIED",
                                                  "CONFLICTED", "STALE", "SUPERSEDED"):
        raise ValueError("INVALID_REVIEW")
    revised = deepcopy(source_claim)
    revised["id"] = str(uuid4())
    revised["supersedes"] = source_claim["id"]
    revised["evidence_state"] = decision
    revised["verification"] = {
        "reviewer_reference": reviewer_reference, "decision": decision,
        "supporting_references": list(supporting_references),
        "explanation": explanation, "reviewed_at": instant(),
    }
    return revised

def detect_conflicts(claims):
    """Identify competing accepted values; do not automatically decide who is right."""
    groups = {}
    for item in claims:
        if item.get("evidence_state") not in ("DOCUMENT_SUPPORTED", "THIRD_PARTY_VERIFIED"):
            continue
        key = (item["subject_id"], item["claim_type"])
        groups.setdefault(key, []).append(item)
    results = []
    for (subject,kind),records in groups.items():
        # JSON-like values get deterministic representation without guessing units.
        distinct = {repr(r.get("value")) for r in records}
        if len(distinct) > 1:
            results.append({"subject_id": subject, "claim_type":kind,
                            "claim_ids":[r["id"] for r in records],
                            "status":"REVIEW_CONFLICT"})
    return results

def evidence_change_record(artifact, kind, reviewed=False):
    return {"artifact_id": artifact["id"], "kind":kind,
            "verified": bool(reviewed), "sha256": artifact["sha256"],
            "received_at": artifact["received_at"]}
