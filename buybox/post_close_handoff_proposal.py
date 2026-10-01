"""BBX052–056: two-phase post-close handoff PROPOSAL from actual saved source.

This cannot issue or consume Tower closing receipts, approve title or machine
ownership, call Grounds/ATM Operations, make a property operational, move
funds, or accept a receiver. A local ACQUIRED label is never authority.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from typing import Any

from .tower_action_draft import (
    BuyBoxTowerActionPreparationError,
    stored_source_snapshot,
)

VERSION = "buybox.post_close.operational_handoff.proposal.v1"
TARGETS = {"atm": "simplee_on_the_go", "multifamily": "grounds"}


class PostCloseProposalError(ValueError):
    """Source is unavailable or malformed; never a live receiver denial."""


def _now(now_utc: datetime | None) -> str:
    value = datetime.now(timezone.utc) if now_utc is None else now_utc
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise PostCloseProposalError("AWARE_TIME_REQUIRED")
    return value.astimezone(timezone.utc).isoformat()


def _stored(db: sqlite3.Connection, opportunity_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    if not isinstance(db, sqlite3.Connection):
        raise PostCloseProposalError("CURRENT_STORE_REQUIRED")
    try:
        snapshot = stored_source_snapshot(db, opportunity_id)
        row = db.execute(
            "SELECT current_json FROM opportunities WHERE id=?", (opportunity_id,)
        ).fetchone()
        if row is None:
            raise PostCloseProposalError("CURRENT_SOURCE_UNAVAILABLE")
        source = json.loads(row["current_json"])
        if not isinstance(source, dict) or source.get("id") != snapshot["opportunity_id"] or (
            source.get("version") != snapshot["opportunity_revision"]
        ):
            raise PostCloseProposalError("CURRENT_SOURCE_IDENTITY_CONFLICT")
    except (BuyBoxTowerActionPreparationError, sqlite3.DatabaseError, TypeError, ValueError) as exc:
        raise PostCloseProposalError("CURRENT_SOURCE_UNAVAILABLE") from exc
    return snapshot, source


def prepare_untrusted_post_close_handoff(
    db: sqlite3.Connection, opportunity_id: str, *,
    now_utc: datetime | None = None,
) -> dict[str, Any]:
    """Describe required handoff lanes, never authorize or send one."""
    at = _now(now_utc)
    snapshot, source = _stored(db, opportunity_id)
    vertical = snapshot["vertical_id"]
    recipient = TARGETS.get(vertical)
    stage = source.get("lifecycle")
    if not isinstance(stage, str):
        raise PostCloseProposalError("LOCAL_STAGE_INVALID")

    included_count = None
    if vertical == "atm":
        data = source.get("vertical_data")
        if not isinstance(data, dict):
            raise PostCloseProposalError("ATM_SOURCE_DATA_INVALID")
        inventory = data.get("machine_inventory", [])
        if not isinstance(inventory, list) or not all(isinstance(x, dict) for x in inventory):
            raise PostCloseProposalError("ATM_INVENTORY_INVALID")
        included_count = sum(item.get("included") is True for item in inventory)
    body = {
        "schema_version": VERSION,
        "opportunity_id": snapshot["opportunity_id"],
        "opportunity_revision": snapshot["opportunity_revision"],
        "input_snapshot_digest": snapshot["input_snapshot_digest"],
        "vertical_id": vertical,
        "proposed_recipient": recipient,
        "locally_recorded_lifecycle": stage,
        "included_atm_count_from_local_records": included_count,
    }
    digest = hashlib.sha256(json.dumps(
        body, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")).hexdigest()
    reasons = [
        "CURRENT_TOWER_CLOSE_RECEIPT_NOT_INDEPENDENTLY_VERIFIED",
        "TITLE_CONTRACT_AND_LIEN_PROOF_NOT_INDEPENDENTLY_VERIFIED",
        "RECIPIENT_SCOPE_IDEMPOTENCY_AND_ACCEPTANCE_NOT_CONNECTED",
    ]
    if recipient is None:
        reasons.append("NO_OPERATIONAL_RECEIVER_CONTRACT_FOR_VERTICAL")
    if stage != "ACQUIRED":
        reasons.append("LOCAL_STAGE_NOT_ACQUIRED")
    if vertical == "atm" and included_count == 0:
        reasons.append("NO_INCLUDED_SERIAL_NUMBERED_ATM_RECORDS")
    return {
        **body,
        "proposal_fingerprint": digest,
        "prepared_at": at,
        "state": "SOURCE_ONLY_UNSENT",
        "reason_codes": reasons,
        "local_stage_is_external_proof": False,
        "tower_close_receipt_verified": False,
        "title_or_contract_verified": False,
        "recipient_independent_acceptance": False,
        "idempotency_and_replay_verified": False,
        "owned_asset_record_created": False,
        "money_movement_authorized": False,
        "tower_handoff_issued": False,
        "external_call_made": False,
        "can_mark_operational": False,
    }
