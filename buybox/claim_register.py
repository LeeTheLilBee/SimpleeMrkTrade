"""BBX037-041: source-bound, append-only cross-document claim discrepancy register.

Owner-reviewed DOCUMENT SUPPORT is not third-party verification, acceptance of a
financial field, ownership clearance, Tower approval, or permission to buy.
Conflicting source statements are compared only within like-for-like subject,
field, unit and exact period/as-of date. None is silently chosen as truth.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
import re
from uuid import uuid4

FIELDS = {
    "ASKING_PRICE": "USD",
    "ANNUAL_REVENUE": "USD",
    "ANNUAL_EXPENSES": "USD",
    "INCLUDED_ASSET_COUNT": "COUNT",
    "OWNERSHIP": "TEXT",
    "CONTRACT_ASSIGNABILITY": "TEXT",
    "OTHER": "TEXT",
}
ANNUAL = frozenset({"ANNUAL_REVENUE", "ANNUAL_EXPENSES"})
ACTIVE_STATES = frozenset({"SOURCE_RECORDED", "OWNER_DOCUMENT_REVIEWED"})
MONEY_PATTERN = re.compile(r"(?:0|[1-9]\d*)(?:\.\d{1,2})?\Z")
COUNT_PATTERN = re.compile(r"(?:0|[1-9]\d*)\Z")
MAX_MONEY = Decimal("1000000000000.00")


class ClaimRegisterError(ValueError):
    """Safe input error; never includes source bytes or privileged file paths."""


def _instant():
    return datetime.now(timezone.utc).isoformat()


def _nonblank(value, field, limit):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ClaimRegisterError("INVALID_" + field)
    if "\x00" in value:
        raise ClaimRegisterError("INVALID_" + field)
    return value.strip()


def _period(field, value):
    value = _nonblank(value, "PERIOD", 30)
    if field in ANNUAL:
        try:
            a, b = value.split(" / ")
            start, end = date.fromisoformat(a), date.fromisoformat(b)
            if (end - start).days + 1 not in (365, 366):
                raise ValueError
        except ValueError as exc:
            raise ClaimRegisterError("FULL_YEAR_PERIOD_REQUIRED") from exc
        return start.isoformat() + " / " + end.isoformat()
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise ClaimRegisterError("AS_OF_DATE_REQUIRED") from exc


def _normalized(field, raw):
    raw = _nonblank(raw, "CLAIM_VALUE", 300)
    unit = FIELDS[field]
    if unit == "USD":
        if not MONEY_PATTERN.fullmatch(raw):
            raise ClaimRegisterError("MONEY_FORMAT_INVALID")
        try:
            number = Decimal(raw)
            if not number.is_finite() or number > MAX_MONEY:
                raise ClaimRegisterError("MONEY_RANGE_INVALID")
        except InvalidOperation as exc:
            raise ClaimRegisterError("MONEY_FORMAT_INVALID") from exc
        return str(number.quantize(Decimal("0.01")))
    if unit == "COUNT":
        if not COUNT_PATTERN.fullmatch(raw) or int(raw) > 1000000:
            raise ClaimRegisterError("COUNT_INVALID")
        return str(int(raw))
    return " ".join(raw.casefold().split())


def _active(op):
    all_claims = op.get("source_claims", [])
    superseded = {c.get("supersedes") for c in all_claims if c.get("supersedes")}
    return [c for c in all_claims
            if c.get("id") not in superseded and c.get("state") in ACTIVE_STATES]


def active_claims(op):
    return deepcopy(_active(op))


def _source(op, evidence_id):
    evidence = [e for e in op.get("evidence", []) if
                isinstance(e, dict) and e.get("id") == evidence_id]
    if len(evidence) != 1 or evidence[0].get("status") not in (
            "RECEIVED", "DOCUMENT_SUPPORTED", "THIRD_PARTY_VERIFIED"):
        raise ClaimRegisterError("ACTIVE_DOCUMENT_EVIDENCE_REQUIRED")
    artifact_id = evidence[0].get("artifact_id")
    artifacts = [a for a in op.get("artifacts", []) if
                 isinstance(a, dict) and a.get("id") == artifact_id]
    if len(artifacts) != 1 or not artifacts[0].get("sha256"):
        raise ClaimRegisterError("LINKED_ORIGINAL_REQUIRED")
    return evidence[0], artifacts[0]


def _invalidate(op, fields, reference, reason):
    # Import locally to keep core.evaluation's integration dependency acyclic.
    from .workflow import invalidate_on_change
    return invalidate_on_change(op, changed_fields=fields,
                                reason=reason, source_reference=reference)


def record_source_claim(op, *, evidence_id, subject_id, field, value,
                        period_key, locator, topic_key=None,
                        supersedes_claim_id=None, correction_reason=None):
    """Record a value exactly as transcribed from one uploaded original.

    This is not an accepted accounting/financial input and does not mutate
    machine ownership, seller asking price, underwriting or external readiness.
    """
    if field not in FIELDS:
        raise ClaimRegisterError("UNREGISTERED_CLAIM_FIELD")
    evidence, artifact = _source(op, evidence_id)
    subject = _nonblank(subject_id, "SUBJECT", 128)
    topic = _nonblank(topic_key, "TOPIC", 100) if field == "OTHER" else field
    if field != "OTHER" and topic_key not in (None, ""):
        raise ClaimRegisterError("TOPIC_NOT_ALLOWED_FOR_FIELD")
    source_locator = _nonblank(locator, "SOURCE_LOCATOR", 240)
    raw_value = _nonblank(value, "CLAIM_VALUE", 300)
    period = _period(field, period_key)
    normalized = _normalized(field, raw_value)
    corrected = None
    if supersedes_claim_id:
        corrected = next((c for c in _active(op) if c["id"] == supersedes_claim_id), None)
        if corrected is None:
            raise ClaimRegisterError("ACTIVE_CORRECTION_TARGET_REQUIRED")
        if (corrected["field"], corrected["subject_id"], corrected["topic_key"],
            corrected["unit"], corrected["period_key"]) != (
            field, subject, topic, FIELDS[field], period):
            raise ClaimRegisterError("CORRECTION_SCOPE_MISMATCH")
        _nonblank(correction_reason, "CORRECTION_REASON", 1000)
    elif correction_reason not in (None, ""):
        raise ClaimRegisterError("CORRECTION_TARGET_REQUIRED")
    # The original source may contain more than one statement, but a correction
    # does not retroactively rewrite the earlier source or its review.
    record = {
        "id": str(uuid4()), "artifact_id": artifact["id"],
        "artifact_sha256": artifact["sha256"], "evidence_id": evidence["id"],
        "subject_id": subject, "field": field, "topic_key": topic,
        "unit": FIELDS[field], "raw_value": raw_value,
        "normalized_value": normalized, "period_key": period,
        "locator": source_locator, "source_party": evidence.get("source"),
        "state": "SOURCE_RECORDED", "recorded_at": _instant(),
        "supersedes": corrected["id"] if corrected else None,
        "correction_reason": correction_reason.strip() if corrected else None,
        "review": None, "promoted_to_metric": False,
        "independently_verified": False,
    }
    revised = deepcopy(op)
    revised.setdefault("source_claims", []).append(record)
    revised = _invalidate(
        revised, ["source_claims", field],
        artifact["id"], "Original-document source claim or correction recorded")
    return revised, deepcopy(record)


def record_owner_document_review(op, *, claim_id, rationale):
    """Append a review revision only after actual linked evidence was reviewed.

    An owner's review cannot create third-party verification, apply the claim
    to a numeric underwriting metric, resolve competing sources, or buy an asset.
    """
    reason = _nonblank(rationale, "REVIEW_RATIONALE", 1000)
    original = next((c for c in _active(op) if c.get("id") == claim_id), None)
    if original is None or original.get("state") != "SOURCE_RECORDED":
        raise ClaimRegisterError("ACTIVE_UNREVIEWED_CLAIM_REQUIRED")
    e, a = _source(op, original["evidence_id"])
    if (e.get("status") != "DOCUMENT_SUPPORTED"
            or a["id"] != original["artifact_id"]
            or a["sha256"] != original["artifact_sha256"]):
        raise ClaimRegisterError("MATCHING_OWNER_REVIEWED_ORIGINAL_REQUIRED")
    revised = deepcopy(op)
    reviewed = {
        **deepcopy(original), "id": str(uuid4()),
        "state": "OWNER_DOCUMENT_REVIEWED", "supersedes": original["id"],
        "recorded_at": _instant(),
        "review": {"actor": "local_owner", "reason": reason, "at": _instant(),
                   "scope": "DOCUMENT_SUPPORT_ONLY"},
    }
    revised.setdefault("source_claims", []).append(reviewed)
    revised = _invalidate(
        revised, ["source_claims", original["field"]],
        reviewed["id"], "Owner reviewed a source-located original claim")
    return revised, deepcopy(reviewed)


def integrity_report(op):
    """Compare current source claims without selecting a winning document.

    Price differences as of different dates are historical change, not a
    same-period discrepancy. Corrections/reviews supersede the older revision
    but independent contradictory sources remain visible.
    """
    claims = _active(op)
    groups = {}
    for claim in claims:
        key = (claim["subject_id"].casefold(), claim["field"],
               claim["topic_key"].casefold(), claim["unit"], claim["period_key"])
        groups.setdefault(key, []).append(claim)
    discrepancies = []
    for key, members in groups.items():
        distinct = {c["normalized_value"] for c in members}
        if len(members) < 2 or len(distinct) < 2:
            continue
        digest = sha256(json.dumps(key, separators=(",",":"),
                                   ensure_ascii=False).encode()).hexdigest()[:16]
        artifacts = sorted({c["artifact_id"] for c in members})
        discrepancies.append({
            "id": "claim-conflict-" + digest,
            "subject_id": members[0]["subject_id"],
            "field": members[0]["field"], "topic_key": members[0]["topic_key"],
            "unit": members[0]["unit"], "period_key": members[0]["period_key"],
            "claim_ids": [c["id"] for c in members],
            "artifact_ids": artifacts, "distinct_values": len(distinct),
            "kind": ("CROSS_SOURCE_DISCREPANCY" if len(artifacts)>1
                     else "WITHIN_SOURCE_DISCREPANCY"),
            "state": "UNRESOLVED_REVIEW_REQUIRED",
            "automatically_accepted": False,
        })
    discrepancies.sort(key=lambda c:(c["field"], c["subject_id"], c["period_key"]))
    return {
        "active_claim_count": len(claims),
        "owner_document_reviewed_count": sum(
            c["state"] == "OWNER_DOCUMENT_REVIEWED" for c in claims),
        "source_recorded_count": sum(c["state"] == "SOURCE_RECORDED" for c in claims),
        "unresolved_count": len(discrepancies),
        "discrepancies": discrepancies,
        "auto_resolved": False, "source_picked_as_truth": False,
        "external_authorization": False,
    }
