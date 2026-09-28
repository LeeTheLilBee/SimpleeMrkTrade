"""BBX082–086: exact saved insurance + financing source proposal to future Teller.

Source-only, private, unsubmitted and NOT the existing version-one Teller wire.
No issuer/receiver, lender approval, coverage verification, real balance, quote
purchase, Vault receipt, Tower entitlement or capital deployment is created.
Only a future independently authenticated Tower adapter may re-fetch this same
current source and propose costs to Teller, which alone judges money/capacity.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Any, Mapping

from .financing import current_options, option_analysis
from .insurance import current_insurance_records, inspect_insurance_record, project_financing_with_insurance
from .tower_action_draft import BuyBoxTowerActionPreparationError, stored_source_snapshot

SCHEMA = "buybox.teller.insurance.costs.source.v1"
MAX_SECONDS = 300
CORE_KEYS = frozenset({
    "schema_version", "source_app", "route_via", "destination",
    "purpose", "opportunity_id", "opportunity_revision", "input_snapshot_digest",
    "vertical_id", "financing_option_id", "financing_original_sha256",
    "insurance_record_id", "insurance_original_sha256", "insurance_document_kind",
    "insurance_source_review_flags", "financing_source_review_flags",
    "annual_premium", "upfront_premium_due",
    "upfront_already_in_recorded_financing_costs",
    "annual_already_in_recorded_operating_expenses",
    "illustrative_additional_upfront_premium", "illustrative_buyer_cash_gap",
    "illustrative_annual_operating_after_premium",
    "coverage_in_force", "insurer_confirmed", "lender_approved",
    "teller_money_readiness", "teller_management_capacity_readiness",
    "authorizes_acquisition", "authorizes_capital_deployment",
})
PACKET_KEYS = CORE_KEYS | frozenset({"source_fingerprint", "issued_at", "valid_until"})


class InsuranceCostSourceError(ValueError):
    """No submitted or independently validated external financial decision."""


def _now(value: datetime | None) -> datetime:
    parsed = datetime.now(timezone.utc) if value is None else value
    if not isinstance(parsed, datetime) or parsed.tzinfo is None or parsed.utcoffset() is None:
        raise InsuranceCostSourceError("TIMEZONE_REQUIRED")
    return parsed.astimezone(timezone.utc)


def _iso(value: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise InsuranceCostSourceError("TIMESTAMP_INVALID")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise InsuranceCostSourceError("TIMESTAMP_INVALID") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise InsuranceCostSourceError("TIMESTAMP_TIMEZONE_REQUIRED")
    return parsed.astimezone(timezone.utc)


def _json(value: Mapping[str, Any]) -> str:
    return json.dumps(dict(value), sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False)


def _sha(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(_json(value).encode("utf-8")).hexdigest()


def _saved(db: sqlite3.Connection, opportunity_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    if not isinstance(db, sqlite3.Connection) or db.in_transaction:
        raise InsuranceCostSourceError("FRESH_DATABASE_TRANSACTION_REQUIRED")
    db.execute("BEGIN IMMEDIATE")
    try:
        source = stored_source_snapshot(db, opportunity_id)
        row = db.execute("SELECT current_json FROM opportunities WHERE id=?",
                         (opportunity_id,)).fetchone()
        if row is None:
            raise InsuranceCostSourceError("CURRENT_OPPORTUNITY_UNAVAILABLE")
        op = json.loads(row["current_json"])
        if (op.get("id") != source["opportunity_id"] or
                op.get("version") != source["opportunity_revision"] or
                op.get("vertical") != source["vertical_id"]):
            raise InsuranceCostSourceError("CURRENT_SAVED_SOURCE_CONFLICT")
        return source, op
    except (BuyBoxTowerActionPreparationError, sqlite3.DatabaseError,
            ValueError, TypeError) as exc:
        raise InsuranceCostSourceError("CURRENT_SAVED_SOURCE_UNAVAILABLE") from exc
    finally:
        db.rollback()


def _active_one(rows: list[dict[str, Any]], selected_id: str, kind: str) -> dict[str, Any]:
    if not isinstance(selected_id, str) or not selected_id:
        raise InsuranceCostSourceError("EXACT_" + kind + "_ID_REQUIRED")
    found = [record for record in rows if record.get("id") == selected_id]
    if len(found) != 1:
        raise InsuranceCostSourceError("CURRENT_" + kind + "_RECORD_REQUIRED")
    return found[0]


def _core(op: dict[str, Any], source: dict[str, Any], *,
          insurance_record_id: str, financing_option_id: str,
          date_string: str) -> dict[str, Any]:
    insurance = _active_one(current_insurance_records(op), insurance_record_id, "INSURANCE")
    financing = _active_one(current_options(op), financing_option_id, "FINANCING")
    insurance_review = inspect_insurance_record(op, insurance, today=date_string)
    finance_review = option_analysis(op, financing, today=date_string)
    if (insurance_review["source_link_intact"] is not True or
            "ORIGINAL_DOCUMENT_LINK_OR_HASH_CHANGED" in finance_review["review_flags"]):
        raise InsuranceCostSourceError("CURRENT_ORIGINAL_REFERENCE_INVALID")
    if (insurance.get("annual_premium") is None or
            insurance.get("upfront_premium_due") is None):
        raise InsuranceCostSourceError("INSURANCE_PREMIUM_NOT_RECORDED")
    overlay = project_financing_with_insurance(op, insurance, financing, today=date_string)
    core = {
        "schema_version": SCHEMA,
        "source_app": "buybox", "route_via": "tower", "destination": "teller",
        "purpose": "acquisition_financing_cost_review",
        **source,
        "financing_option_id": financing["id"],
        "financing_original_sha256": financing["source_sha256"],
        "insurance_record_id": insurance["id"],
        "insurance_original_sha256": insurance["source_sha256"],
        "insurance_document_kind": insurance["document_kind"],
        "insurance_source_review_flags": insurance_review["review_flags"],
        "financing_source_review_flags": finance_review["review_flags"],
        "annual_premium": insurance["annual_premium"],
        "upfront_premium_due": insurance["upfront_premium_due"],
        "upfront_already_in_recorded_financing_costs": insurance["upfront_in_financing_costs"],
        "annual_already_in_recorded_operating_expenses": insurance["annual_in_operating_expenses"],
        "illustrative_additional_upfront_premium": overlay[
            "additional_upfront_premium_if_not_already_counted"],
        "illustrative_buyer_cash_gap": overlay["illustrative_buyer_cash_gap_with_premium"],
        "illustrative_annual_operating_after_premium": overlay[
            "illustrative_annual_operating_after_premium"],
        "coverage_in_force": "UNKNOWN", "insurer_confirmed": False,
        "lender_approved": False, "teller_money_readiness": "UNKNOWN",
        "teller_management_capacity_readiness": "UNKNOWN",
        "authorizes_acquisition": False, "authorizes_capital_deployment": False,
    }
    if set(core) != CORE_KEYS:
        raise InsuranceCostSourceError("INTERNAL_SOURCE_CONTRACT_MISMATCH")
    return core


def prepare_unsubmitted_insurance_cost_proposal(
    db: sqlite3.Connection, opportunity_id: str, *,
    insurance_record_id: str, financing_option_id: str,
    now_utc: datetime | None = None, lifetime_seconds: int = 120,
) -> dict[str, Any]:
    """Prepare a private source-only cost comparison, not the existing Teller v1 request."""
    now = _now(now_utc)
    if type(lifetime_seconds) is not int or not 0 < lifetime_seconds <= MAX_SECONDS:
        raise InsuranceCostSourceError("INVALID_PROPOSAL_LIFETIME")
    source, op = _saved(db, opportunity_id)
    core = _core(op, source, insurance_record_id=insurance_record_id,
                 financing_option_id=financing_option_id, date_string=now.date().isoformat())
    packet = {**core, "source_fingerprint": _sha(core), "issued_at": now.isoformat(),
              "valid_until": (now + timedelta(seconds=lifetime_seconds)).isoformat()}
    return {
        "state": "LOCAL_INSURANCE_COST_PROPOSAL_UNSUBMITTED", "packet": packet,
        "original_bytes_reverified": False,
        "owner_cost_inclusion_assumptions_verified": False,
        "coverage_in_force": "UNKNOWN", "teller_readiness": "UNKNOWN",
        "teller_request_sent": False, "tower_authorization": False,
        "teller_receipt_present": False, "authorizes_acquisition": False,
        "authorizes_capital_deployment": False,
    }


def recheck_unsubmitted_insurance_cost_proposal(
    db: sqlite3.Connection, packet: Mapping[str, Any], *,
    now_utc: datetime | None = None,
) -> dict[str, Any]:
    """Compare the current saved revision and exact selected records, never claim READY."""
    now = _now(now_utc)
    if not isinstance(packet, Mapping) or set(packet) != PACKET_KEYS:
        raise InsuranceCostSourceError("EXACT_PROPOSAL_FIELDS_REQUIRED")
    if packet.get("schema_version") != SCHEMA:
        raise InsuranceCostSourceError("SCHEMA_VERSION_INVALID")
    issued, expires = _iso(packet["issued_at"]), _iso(packet["valid_until"])
    if (issued > now + timedelta(seconds=30) or
            not timedelta(0) < expires - issued <= timedelta(seconds=MAX_SECONDS)):
        raise InsuranceCostSourceError("PROPOSAL_TIME_INVALID")
    offered = {key: packet[key] for key in CORE_KEYS}
    if (not isinstance(packet["source_fingerprint"], str) or
            _sha(offered) != packet["source_fingerprint"]):
        raise InsuranceCostSourceError("PROPOSAL_FINGERPRINT_MISMATCH")
    reasons: list[str] = []
    if now >= expires:
        reasons.append("LOCAL_PROPOSAL_EXPIRED")
    try:
        source, op = _saved(db, packet["opportunity_id"])
        current = _core(op, source, insurance_record_id=packet["insurance_record_id"],
                        financing_option_id=packet["financing_option_id"],
                        date_string=now.date().isoformat())
        if current != offered:
            reasons.append("CURRENT_SAVED_SOURCE_OR_COST_TERMS_CHANGED")
    except (InsuranceCostSourceError, KeyError, TypeError, ValueError):
        reasons.append("CURRENT_SOURCE_OR_ORIGINAL_UNAVAILABLE")
    return {
        "state": "STALE_OR_EXPIRED_LOCAL" if reasons else "CURRENT_LOCAL_UNSUBMITTED",
        "reason_codes": reasons, "source_fingerprint": packet["source_fingerprint"],
        "teller_readiness": "UNKNOWN", "teller_request_sent": False,
        "teller_receipt_present": False, "coverage_in_force": "UNKNOWN",
        "authorizes_acquisition": False, "authorizes_capital_deployment": False,
    }
