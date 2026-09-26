"""TWR202-206: untrusted BuyBox -> Tower action request contract v1.

A parsed client draft is never identity, entitlement, financial readiness,
a Tower decision, a signed receipt, or verified opportunity source truth.
No network calls or product activation are implemented here.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Mapping

SCHEMA_VERSION = "tower.buybox.action.v1"
MAX_DRAFT_LIFETIME_SECONDS = 300

VERTICAL_IDS = frozenset({
    "atm", "multifamily", "commercial", "laundromat",
    "land_farm", "business", "equipment",
})

ACTION_PURPOSES = {
    "READ_OPPORTUNITY": "acquisition_due_diligence",
    "EDIT_OPPORTUNITY": "acquisition_due_diligence",
    "UPLOAD_EVIDENCE": "acquisition_due_diligence",
    "DOWNLOAD_EVIDENCE": "acquisition_due_diligence",
    "REVIEW_SCENARIO": "acquisition_underwriting",
    "FREEZE_DECISION": "acquisition_decision",
    "REQUEST_EXCEPTION": "acquisition_decision",
    "DRAFT_LOI": "acquisition_negotiation",
    "AUTHORIZE_CLOSING": "acquisition_closing",
    "REQUEST_ASSET_HANDOFF": "acquisition_handoff",
    "REQUEST_TELLER_READINESS": "acquisition_financing",
    "REQUEST_VAULT_PROOF": "acquisition_due_diligence",
    "READ_GROUNDS_CONTEXT": "acquisition_due_diligence",
    "READ_CLOUDS_STATUS": "acquisition_due_diligence",
}
PROTECTED_ACTIONS = frozenset({
    "DOWNLOAD_EVIDENCE", "FREEZE_DECISION", "REQUEST_EXCEPTION",
    "DRAFT_LOI", "AUTHORIZE_CLOSING", "REQUEST_ASSET_HANDOFF",
    "REQUEST_TELLER_READINESS", "REQUEST_VAULT_PROOF",
    "READ_GROUNDS_CONTEXT",
})
CLASSIFICATIONS = frozenset({"INTERNAL", "CONFIDENTIAL", "RESTRICTED"})
DIGEST = re.compile(r"^[0-9a-f]{64}$")
OPAQUE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
FIELDS = frozenset({
    "schema_version", "source_app", "destination",
    "request_id", "idempotency_key", "correlation_id",
    "opportunity_id", "opportunity_revision", "input_snapshot_digest",
    "vertical_id", "requester_identity_ref", "requester_entity_ref",
    "requested_action", "purpose", "issued_at", "valid_until",
    "data_classification",
})


class BuyBoxActionDraftError(ValueError):
    """Malformed, stale, unsupported or excess-field untrusted request."""


def _timestamp(value: Any, field: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise BuyBoxActionDraftError(field + "_invalid")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise BuyBoxActionDraftError(field + "_invalid") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise BuyBoxActionDraftError(field + "_timezone_required")
    return parsed.astimezone(timezone.utc)


def _id(value: Any, field: str) -> str:
    if not isinstance(value, str) or OPAQUE.fullmatch(value) is None:
        raise BuyBoxActionDraftError(field + "_invalid")
    return value


def validate_buybox_action_draft(
    packet: Mapping[str, Any], *, now_utc: datetime | None = None
) -> dict[str, Any]:
    """Validate draft SHAPE; never authenticate the claimed requester."""
    if not isinstance(packet, Mapping):
        raise BuyBoxActionDraftError("packet_not_mapping")
    if set(packet) != FIELDS:
        raise BuyBoxActionDraftError("packet_fields_mismatch")
    if packet["schema_version"] != SCHEMA_VERSION:
        raise BuyBoxActionDraftError("schema_version_unsupported")
    if packet["source_app"] != "buybox" or packet["destination"] != "tower":
        raise BuyBoxActionDraftError("routing_invalid")

    for key in (
        "request_id", "idempotency_key", "correlation_id",
        "opportunity_id", "requester_identity_ref", "requester_entity_ref",
    ):
        _id(packet[key], key)

    revision = packet["opportunity_revision"]
    if type(revision) is not int or revision <= 0:
        raise BuyBoxActionDraftError("opportunity_revision_invalid")
    digest = packet["input_snapshot_digest"]
    if not isinstance(digest, str) or DIGEST.fullmatch(digest) is None:
        raise BuyBoxActionDraftError("input_snapshot_digest_invalid")
    if packet["vertical_id"] not in VERTICAL_IDS:
        raise BuyBoxActionDraftError("vertical_id_unknown")
    action = packet["requested_action"]
    if not isinstance(action, str) or action not in ACTION_PURPOSES:
        raise BuyBoxActionDraftError("requested_action_unknown")
    if packet["purpose"] != ACTION_PURPOSES[action]:
        raise BuyBoxActionDraftError("action_purpose_mismatch")
    if packet["data_classification"] not in CLASSIFICATIONS:
        raise BuyBoxActionDraftError("data_classification_invalid")

    issued = _timestamp(packet["issued_at"], "issued_at")
    expires = _timestamp(packet["valid_until"], "valid_until")
    now = datetime.now(timezone.utc) if now_utc is None else now_utc
    if not isinstance(now, datetime) or now.tzinfo is None or now.utcoffset() is None:
        raise BuyBoxActionDraftError("evaluation_time_invalid")
    now = now.astimezone(timezone.utc)
    if issued > now + timedelta(seconds=30):
        raise BuyBoxActionDraftError("issued_at_in_future")
    if expires <= now:
        raise BuyBoxActionDraftError("draft_expired")
    lifetime = (expires - issued).total_seconds()
    if not (0 < lifetime <= MAX_DRAFT_LIFETIME_SECONDS):
        raise BuyBoxActionDraftError("draft_lifetime_invalid")

    return json.loads(json.dumps(dict(packet), sort_keys=True, separators=(",", ":"), allow_nan=False))


def buybox_action_draft_fingerprint(
    packet: Mapping[str, Any], *, now_utc: datetime | None = None
) -> str:
    valid = validate_buybox_action_draft(packet, now_utc=now_utc)
    canonical = json.dumps(valid, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def prepare_buybox_action_review(
    packet: Mapping[str, Any], *, now_utc: datetime | None = None
) -> dict[str, Any]:
    """Classify a future review, never issue grants, receipts or cross-app calls."""
    valid = validate_buybox_action_draft(packet, now_utc=now_utc)
    action = valid["requested_action"]
    return {
        "schema_version": SCHEMA_VERSION,
        "request_id": valid["request_id"],
        "request_fingerprint": buybox_action_draft_fingerprint(valid, now_utc=now_utc),
        "opportunity_id": valid["opportunity_id"],
        "opportunity_revision": valid["opportunity_revision"],
        "input_snapshot_digest": valid["input_snapshot_digest"],
        "requested_action": action,
        "action_class": "PROTECTED" if action in PROTECTED_ACTIONS else "REVIEW_ONLY",
        "state": "UNTRUSTED_DRAFT",
        "authoritative_principal": False,
        "authoritative_entity": False,
        "snapshot_verified_against_buybox": False,
        "issuer_receipt_present": False,
        "authorizes_action": False,
        "teller_readiness": "UNKNOWN",
        "external_call_made": False,
    }


def draft_matches_current_opportunity(
    packet: Mapping[str, Any],
    *,
    current_opportunity_id: str,
    current_revision: int,
    current_snapshot_digest: str,
    now_utc: datetime | None = None,
) -> bool:
    """Equality check only. Production caller must fetch current state securely."""
    valid = validate_buybox_action_draft(packet, now_utc=now_utc)
    return bool(
        valid["opportunity_id"] == current_opportunity_id
        and type(current_revision) is int
        and valid["opportunity_revision"] == current_revision
        and valid["input_snapshot_digest"] == current_snapshot_digest
    )
