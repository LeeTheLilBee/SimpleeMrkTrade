"""BBX027-031 — source-bound, UNSUBMITTED Teller financing/readiness question.

This module does not call Teller, Tower, OB, a bank or brokerage; it cannot
verify capital, protected floors, available funds, management capacity or an
issuer receipt. Every figure is a locally proposed assumption. A future Tower
adapter must re-fetch the saved BuyBox source, derive owner/entity itself and
ask Teller for deal-terms-specific money AND management/capacity readiness.
"""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping

from .tower_action_draft import (
    BuyBoxTowerActionPreparationError,
    stored_source_snapshot,
)

SCHEMA_VERSION = "buybox.teller.readiness.question.v1"
MAX_LIFETIME_SECONDS = 300
MAX_MONEY = Decimal("1000000000000.00")
MONEY_FIELDS = (
    "proposed_purchase_price",
    "proposed_debt_amount",
    "proposed_equity_amount",
    "estimated_closing_costs",
    "proposed_reserve",
)
TERMS_FIELDS = frozenset((*MONEY_FIELDS, "funding_lane", "terms_reference"))
INTENT_FIELDS = frozenset({
    "schema_version", "source_app", "route_via", "destination",
    "requested_action", "purpose",
    "opportunity_id", "opportunity_revision", "input_snapshot_digest",
    "vertical_id", "stored_asking_price",
    "terms", "terms_fingerprint",
    "issued_at", "valid_until",
})
ALLOWED_LANES = {
    "atm": frozenset(("ATM_SET_1_ACQUISITION", "ATM_SET_2_ACQUISITION")),
    "multifamily": frozenset(("GROUNDS_ACQUISITION_UNVERIFIED",)),
}
OTHER_LANE = "MISSION_ACCOUNT_UNASSIGNED"
REF = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")


class TellerReadinessQuestionError(ValueError):
    """Local proposed-terms error, never a Teller/financing decision."""


def _clock(value: datetime | None) -> datetime:
    value = datetime.now(timezone.utc) if value is None else value
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise TellerReadinessQuestionError("UTC_TIME_REQUIRED")
    return value.astimezone(timezone.utc)


def _timestamp(value: Any) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise TellerReadinessQuestionError("TIMESTAMP_INVALID")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise TellerReadinessQuestionError("TIMESTAMP_INVALID") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise TellerReadinessQuestionError("TIMESTAMP_TIMEZONE_REQUIRED")
    return parsed.astimezone(timezone.utc)


def _amount(value: Any, *, positive: bool) -> str:
    # Reject floats and booleans so binary approximations are never silently
    # serialized into a source-bound proposed financing question.
    if not isinstance(value, str) or len(value) > 30 or not re.fullmatch(
        r"(?:0|[1-9][0-9]*)(?:\.[0-9]{1,2})?", value
    ):
        raise TellerReadinessQuestionError("MONEY_FORMAT_INVALID")
    try:
        number = Decimal(value)
        if not number.is_finite() or number > MAX_MONEY or (
            number <= 0 if positive else number < 0
        ):
            raise TellerReadinessQuestionError("MONEY_RANGE_INVALID")
        return format(number.quantize(Decimal("0.01")), ".2f")
    except InvalidOperation as exc:
        raise TellerReadinessQuestionError("MONEY_FORMAT_INVALID") from exc


def _canonical(payload: Mapping[str, Any]) -> str:
    return json.dumps(
        dict(payload), sort_keys=True, ensure_ascii=False,
        separators=(",", ":"), allow_nan=False,
    )


def _sha(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()


def _terms(terms: Mapping[str, Any], vertical: str) -> dict[str, str]:
    if not isinstance(terms, Mapping) or set(terms) != TERMS_FIELDS:
        raise TellerReadinessQuestionError("EXACT_PROPOSED_TERMS_REQUIRED")
    candidate = {
        key: _amount(terms[key], positive=key == "proposed_purchase_price")
        for key in MONEY_FIELDS
    }
    lane, ref = terms["funding_lane"], terms["terms_reference"]
    expected = ALLOWED_LANES.get(vertical, frozenset((OTHER_LANE,)))
    if not isinstance(lane, str) or lane not in expected:
        raise TellerReadinessQuestionError("UNVERIFIED_FUNDING_LANE_NOT_ALLOWED")
    if not isinstance(ref, str) or REF.fullmatch(ref) is None:
        raise TellerReadinessQuestionError("TERMS_REFERENCE_INVALID")
    candidate.update({"funding_lane": lane, "terms_reference": ref})
    return candidate


def _source(db: sqlite3.Connection, opportunity_id: str) -> tuple[dict[str, Any], str | None]:
    if not isinstance(db, sqlite3.Connection):
        raise TellerReadinessQuestionError("LOCAL_STORE_REQUIRED")
    try:
        source = stored_source_snapshot(db, opportunity_id)
        row = db.execute(
            "SELECT current_json FROM opportunities WHERE id=?", (opportunity_id,)
        ).fetchone()
        if row is None:
            raise TellerReadinessQuestionError("CURRENT_SOURCE_UNAVAILABLE")
        stored = json.loads(row["current_json"])
        if stored.get("id") != source["opportunity_id"] or stored.get("version") != source["opportunity_revision"]:
            raise TellerReadinessQuestionError("CURRENT_SOURCE_IDENTITY_CONFLICT")
        price = stored.get("asking_price")
        if price is not None:
            price = _amount(price, positive=False)
        return source, price
    except (BuyBoxTowerActionPreparationError, sqlite3.DatabaseError, ValueError, TypeError) as exc:
        raise TellerReadinessQuestionError("CURRENT_SOURCE_UNAVAILABLE") from exc


def prepare_unsubmitted_teller_readiness_question(
    db: sqlite3.Connection, opportunity_id: str, *,
    proposed_terms: Mapping[str, Any],
    now_utc: datetime | None = None,
    lifetime_seconds: int = 120,
) -> dict[str, Any]:
    """Read the current persisted BuyBox source and fingerprint proposed terms.

    Does NOT store or dispatch the packet, assert authenticated Tower identity,
    pool ATM Set 1/2, query OB balances, or claim that financing is available.
    """
    now = _clock(now_utc)
    if type(lifetime_seconds) is not int or not 0 < lifetime_seconds <= MAX_LIFETIME_SECONDS:
        raise TellerReadinessQuestionError("QUESTION_LIFETIME_INVALID")
    source, asking_price = _source(db, opportunity_id)
    terms = _terms(proposed_terms, source["vertical_id"])
    core = {**source, "stored_asking_price": asking_price, "terms": terms}
    packet = {
        "schema_version": SCHEMA_VERSION,
        "source_app": "buybox", "route_via": "tower", "destination": "teller",
        "requested_action": "REQUEST_TELLER_READINESS",
        "purpose": "acquisition_financing",
        **core,
        "terms_fingerprint": _sha(core),
        "issued_at": now.isoformat(),
        "valid_until": (now + timedelta(seconds=lifetime_seconds)).isoformat(),
    }
    return {
        "state": "LOCAL_TERMS_QUESTION_UNSUBMITTED",
        "packet": packet,
        "terms_origin": "LOCAL_PROPOSAL_UNVERIFIED",
        "buyer_money_ready": "UNKNOWN",
        "management_capacity_ready": "UNKNOWN",
        "teller_readiness": "UNKNOWN",
        "atm_protected_floors_checked": False,
        "tower_identity_verified": False,
        "teller_issuer_verified": False,
        "external_request_sent": False,
        "teller_receipt_present": False,
        "authorizes_capital_deployment": False,
        "authorizes_acquisition": False,
    }


def recheck_unsubmitted_teller_readiness_question(
    db: sqlite3.Connection, packet: Mapping[str, Any], *,
    now_utc: datetime | None = None,
) -> dict[str, Any]:
    """Return only source/terms currency; never accept a shaped 'READY' claim."""
    now = _clock(now_utc)
    if not isinstance(packet, Mapping) or set(packet) != INTENT_FIELDS:
        raise TellerReadinessQuestionError("QUESTION_FIELDS_INVALID")
    if (
        packet["schema_version"] != SCHEMA_VERSION or
        packet["source_app"] != "buybox" or
        packet["route_via"] != "tower" or
        packet["destination"] != "teller" or
        packet["requested_action"] != "REQUEST_TELLER_READINESS" or
        packet["purpose"] != "acquisition_financing"
    ):
        raise TellerReadinessQuestionError("QUESTION_ROUTE_INVALID")
    opportunity_id = packet["opportunity_id"]
    if not isinstance(opportunity_id, str) or REF.fullmatch(opportunity_id) is None:
        raise TellerReadinessQuestionError("QUESTION_OPPORTUNITY_INVALID")
    if type(packet["opportunity_revision"]) is not int or packet["opportunity_revision"] <= 0:
        raise TellerReadinessQuestionError("QUESTION_REVISION_INVALID")
    if not isinstance(packet["input_snapshot_digest"], str) or not re.fullmatch(
        r"[0-9a-f]{64}", packet["input_snapshot_digest"]
    ):
        raise TellerReadinessQuestionError("QUESTION_DIGEST_INVALID")
    vertical = packet["vertical_id"]
    if not isinstance(vertical, str):
        raise TellerReadinessQuestionError("QUESTION_VERTICAL_INVALID")
    terms = _terms(packet["terms"], vertical)
    if terms != packet["terms"]:
        raise TellerReadinessQuestionError("QUESTION_TERMS_NOT_CANONICAL")
    asking_price = packet["stored_asking_price"]
    if asking_price is not None and (
        not isinstance(asking_price, str) or _amount(asking_price, positive=False) != asking_price
    ):
        raise TellerReadinessQuestionError("QUESTION_ASKING_PRICE_INVALID")
    core = {
        "opportunity_id": opportunity_id,
        "opportunity_revision": packet["opportunity_revision"],
        "input_snapshot_digest": packet["input_snapshot_digest"],
        "vertical_id": vertical,
        "stored_asking_price": asking_price,
        "terms": terms,
    }
    if not isinstance(packet["terms_fingerprint"], str) or _sha(core) != packet["terms_fingerprint"]:
        raise TellerReadinessQuestionError("QUESTION_FINGERPRINT_MISMATCH")
    issued, expires = _timestamp(packet["issued_at"]), _timestamp(packet["valid_until"])
    if issued > now + timedelta(seconds=30) or not (
        timedelta(0) < expires - issued <= timedelta(seconds=MAX_LIFETIME_SECONDS)
    ):
        raise TellerReadinessQuestionError("QUESTION_TIME_INVALID")

    reasons = []
    try:
        current, current_asking = _source(db, opportunity_id)
        if any(current[key] != packet[key] for key in (
            "opportunity_id", "opportunity_revision", "input_snapshot_digest", "vertical_id"
        )) or current_asking != asking_price:
            reasons.append("CURRENT_SAVED_OPPORTUNITY_CHANGED")
    except TellerReadinessQuestionError:
        reasons.append("CURRENT_SAVED_OPPORTUNITY_UNAVAILABLE")
    if now >= expires:
        reasons.append("LOCAL_TERMS_QUESTION_EXPIRED")
    return {
        "state": "STALE_OR_EXPIRED_LOCAL" if reasons else "CURRENT_LOCAL_UNSUBMITTED",
        "reason_codes": reasons,
        "terms_fingerprint": packet["terms_fingerprint"],
        "teller_readiness": "UNKNOWN",
        "buyer_money_ready": "UNKNOWN",
        "management_capacity_ready": "UNKNOWN",
        "issuer_receipt_present": False,
        "external_request_sent": False,
        "authorizes_capital_deployment": False,
    }
