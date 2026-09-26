"""BBX016: BuyBox side of merged TWR202–206 action-draft contract.

Uses the exact existing saved opportunity revision+snapshot digest. Its output
is ALWAYS an UNTRUSTED_DRAFT. It is not Tower identity, owner permission,
readiness, an issuer receipt or execution. No endpoint, network or secrets.
Canonical source: tower/buybox_action_contract.py at Tower merge db57752b.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
import re
import sqlite3
from uuid import uuid4
from .registry import VERTICALS

SCHEMA_VERSION = "tower.buybox.action.v1"
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
    "DOWNLOAD_EVIDENCE", "FREEZE_DECISION", "REQUEST_EXCEPTION", "DRAFT_LOI",
    "AUTHORIZE_CLOSING", "REQUEST_ASSET_HANDOFF", "REQUEST_TELLER_READINESS",
    "REQUEST_VAULT_PROOF", "READ_GROUNDS_CONTEXT",
})
CLASSIFICATIONS = frozenset({"INTERNAL", "CONFIDENTIAL", "RESTRICTED"})
OPAQUE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
MAX_DRAFT_SECONDS = 300

class BuyBoxTowerActionPreparationError(ValueError):
    pass

def _required_ref(value, field):
    if not isinstance(value, str) or not OPAQUE.fullmatch(value):
        raise BuyBoxTowerActionPreparationError("INVALID_REFERENCE:" + field)
    return value

def stored_source_snapshot(db: sqlite3.Connection, opportunity_id: str):
    """Bind the action to the EXACT persisted revision and its stored digest.

    This consistency check is not a signed statement of external business truth.
    A stale UI form, fabricated in-memory opportunity and user-supplied digest
    cannot substitute for the persisted source.
    """
    _required_ref(opportunity_id, "opportunity_id")
    row = db.execute(
        """SELECT o.id, o.vertical, o.revision, o.current_json,
                  r.snapshot_json, r.digest
           FROM opportunities AS o JOIN revisions AS r
           ON o.id = r.opportunity_id AND o.revision = r.revision
           WHERE o.id = ?""", (opportunity_id,)
    ).fetchone()
    if row is None:
        raise BuyBoxTowerActionPreparationError("CURRENT_SNAPSHOT_NOT_FOUND")
    if row["current_json"] != row["snapshot_json"]:
        raise BuyBoxTowerActionPreparationError("CURRENT_REVISION_SNAPSHOT_CONFLICT")
    calculated = sha256(row["current_json"].encode("utf-8")).hexdigest()
    if calculated != row["digest"]:
        raise BuyBoxTowerActionPreparationError("CURRENT_SNAPSHOT_DIGEST_CONFLICT")
    try:
        op = json.loads(row["current_json"])
    except (ValueError, TypeError):
        raise BuyBoxTowerActionPreparationError("INVALID_STORED_OPPORTUNITY") from None
    if (op.get("id") != row["id"] or op.get("vertical") != row["vertical"]
            or type(row["revision"]) is not int
            or op.get("version") != row["revision"]
            or row["vertical"] not in VERTICALS):
        raise BuyBoxTowerActionPreparationError("CURRENT_SNAPSHOT_IDENTITY_CONFLICT")
    return {"opportunity_id": row["id"], "opportunity_revision": row["revision"],
            "input_snapshot_digest": calculated, "vertical_id": row["vertical"]}

def prepare_untrusted_tower_action_draft(
    db: sqlite3.Connection, opportunity_id: str, *, requested_action: str,
    claimed_identity_ref: str, claimed_entity_ref: str,
    classification: str, now_utc: datetime | None = None,
    lifetime_seconds: int = 120,
):
    """Local source-bound formatter, not a Tower request/authorization.

    Claimed actor/entity and classification MUST later be replaced or independently
    derived by authenticated Tower middleware. Never bind this to a browser input.
    """
    if requested_action not in ACTION_PURPOSES:
        raise BuyBoxTowerActionPreparationError("UNSUPPORTED_ACTION")
    if classification not in CLASSIFICATIONS:
        raise BuyBoxTowerActionPreparationError("INVALID_CLASSIFICATION")
    _required_ref(claimed_identity_ref, "claimed_identity_ref")
    _required_ref(claimed_entity_ref, "claimed_entity_ref")
    if type(lifetime_seconds) is not int or not 0 < lifetime_seconds <= MAX_DRAFT_SECONDS:
        raise BuyBoxTowerActionPreparationError("INVALID_DRAFT_LIFETIME")
    issued = now_utc if now_utc is not None else datetime.now(timezone.utc)
    if not isinstance(issued, datetime) or issued.tzinfo is None or issued.utcoffset() is None:
        raise BuyBoxTowerActionPreparationError("UTC_TIMEZONE_REQUIRED")
    issued = issued.astimezone(timezone.utc)
    current = stored_source_snapshot(db, opportunity_id)
    packet = {
        "schema_version": SCHEMA_VERSION, "source_app": "buybox",
        "destination": "tower", "request_id": str(uuid4()),
        "idempotency_key": str(uuid4()), "correlation_id": str(uuid4()),
        **current, "requester_identity_ref": claimed_identity_ref,
        "requester_entity_ref": claimed_entity_ref,
        "requested_action": requested_action,
        "purpose": ACTION_PURPOSES[requested_action],
        "issued_at": issued.isoformat(),
        "valid_until": (issued + timedelta(seconds=lifetime_seconds)).isoformat(),
        "data_classification": classification,
    }
    return {
        "state": "UNTRUSTED_DRAFT",
        "packet": packet,
        "authorizes_action": False, "issuer_receipt_present": False,
        "source_digest_verified_locally": True,
        "requester_authenticated_by_tower": False,
        "teller_readiness": "UNKNOWN", "external_call_made": False,
        "action_class": "PROTECTED" if requested_action in PROTECTED_ACTIONS else "REVIEW_ONLY",
    }

def draft_still_matches_store(db: sqlite3.Connection, packet: dict) -> bool:
    """Staleness check only; it never proves actor or grants Tower permissions."""
    current = stored_source_snapshot(db, packet.get("opportunity_id", ""))
    return all(packet.get(key) == current[key] for key in (
        "opportunity_id", "opportunity_revision", "input_snapshot_digest",
        "vertical_id",
    ))
