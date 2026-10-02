"""TWR212-216 — strict, source-only Tower review of BuyBox -> Teller proposal v1.

This validates an UNTRUSTED request's syntax and internal fingerprint only.
It does not connect to BuyBox, Teller, OB or a brokerage, fetch true source,
derive an actor/entity, issue a receipt, approve capital, or register a route.
A matching SHA-256 is not authenticity. The financial readiness result remains
UNKNOWN until Tower and Teller independently re-fetch and verify live sources.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping

SCHEMA_VERSION = "buybox.teller.readiness.question.v1"
MAX_LIFETIME_SECONDS = 300
MONEY_MAX = Decimal("1000000000000.00")
MONEY_FIELDS = (
    "proposed_purchase_price", "proposed_debt_amount",
    "proposed_equity_amount", "estimated_closing_costs", "proposed_reserve",
)
TERM_FIELDS = frozenset((*MONEY_FIELDS, "funding_lane", "terms_reference"))
FIELDS = frozenset({
    "schema_version", "source_app", "route_via", "destination",
    "requested_action", "purpose", "opportunity_id",
    "opportunity_revision", "input_snapshot_digest", "vertical_id",
    "stored_asking_price", "terms", "terms_fingerprint",
    "issued_at", "valid_until",
})
VERTICAL_IDS = frozenset({
    "atm", "multifamily", "commercial", "laundromat",
    "land_farm", "business", "equipment",
})
ATM_LANES = frozenset(("ATM_SET_1_ACQUISITION", "ATM_SET_2_ACQUISITION"))
LANES = {
    "atm": ATM_LANES,
    "multifamily": frozenset(("GROUNDS_ACQUISITION_UNVERIFIED",)),
}
OTHER_LANE = frozenset(("MISSION_ACCOUNT_UNASSIGNED",))
REF = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
MONEY = re.compile(r"^(?:0|[1-9][0-9]*)(?:\.[0-9]{1,2})?$")


class BuyBoxTellerProposalError(ValueError):
    """A request-shape failure, not a Teller or Tower financial decision."""


def _time(value: Any) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise BuyBoxTellerProposalError("TIMESTAMP_INVALID")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise BuyBoxTellerProposalError("TIMESTAMP_INVALID") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise BuyBoxTellerProposalError("TIMESTAMP_TIMEZONE_REQUIRED")
    return parsed.astimezone(timezone.utc)


def _money(value: Any, *, positive: bool = False) -> str:
    if not isinstance(value, str) or len(value) > 30 or MONEY.fullmatch(value) is None:
        raise BuyBoxTellerProposalError("PROPOSED_MONEY_FORMAT_INVALID")
    try:
        amount = Decimal(value)
        if (
            not amount.is_finite() or amount > MONEY_MAX
            or (amount <= 0 if positive else amount < 0)
        ):
            raise BuyBoxTellerProposalError("PROPOSED_MONEY_RANGE_INVALID")
        return format(amount.quantize(Decimal("0.01")), ".2f")
    except InvalidOperation as exc:
        raise BuyBoxTellerProposalError("PROPOSED_MONEY_FORMAT_INVALID") from exc


def _canonical(value: Mapping[str, Any]) -> str:
    return json.dumps(
        dict(value), sort_keys=True, ensure_ascii=False,
        separators=(",", ":"), allow_nan=False,
    )


def validate_untrusted_teller_readiness_proposal(
    packet: Mapping[str, Any], *, now_utc: datetime | None = None
) -> dict[str, Any]:
    """Validate exact cross-product v1 format without authenticating its source."""
    if not isinstance(packet, Mapping) or set(packet) != FIELDS:
        raise BuyBoxTellerProposalError("REQUEST_FIELDS_INVALID")
    if (
        packet["schema_version"] != SCHEMA_VERSION
        or packet["source_app"] != "buybox"
        or packet["route_via"] != "tower"
        or packet["destination"] != "teller"
        or packet["requested_action"] != "REQUEST_TELLER_READINESS"
        or packet["purpose"] != "acquisition_financing"
    ):
        raise BuyBoxTellerProposalError("REQUEST_ROUTE_INVALID")
    opportunity_id = packet["opportunity_id"]
    if not isinstance(opportunity_id, str) or REF.fullmatch(opportunity_id) is None:
        raise BuyBoxTellerProposalError("OPPORTUNITY_REFERENCE_INVALID")
    revision = packet["opportunity_revision"]
    if type(revision) is not int or revision <= 0:
        raise BuyBoxTellerProposalError("REVISION_INVALID")
    digest = packet["input_snapshot_digest"]
    if not isinstance(digest, str) or SHA256.fullmatch(digest) is None:
        raise BuyBoxTellerProposalError("SNAPSHOT_DIGEST_INVALID")
    vertical = packet["vertical_id"]
    if not isinstance(vertical, str) or vertical not in VERTICAL_IDS:
        raise BuyBoxTellerProposalError("VERTICAL_UNKNOWN")

    asking = packet["stored_asking_price"]
    if asking is not None and _money(asking) != asking:
        raise BuyBoxTellerProposalError("STORED_PRICE_NOT_CANONICAL")
    terms = packet["terms"]
    if not isinstance(terms, Mapping) or set(terms) != TERM_FIELDS:
        raise BuyBoxTellerProposalError("PROPOSED_TERMS_FIELDS_INVALID")
    normalized = {
        field: _money(terms[field], positive=field == "proposed_purchase_price")
        for field in MONEY_FIELDS
    }
    if any(normalized[field] != terms[field] for field in MONEY_FIELDS):
        raise BuyBoxTellerProposalError("PROPOSED_TERMS_NOT_CANONICAL")
    lane = terms["funding_lane"]
    if not isinstance(lane, str) or lane not in LANES.get(vertical, OTHER_LANE):
        raise BuyBoxTellerProposalError("UNVERIFIED_FUNDING_LANE_INVALID")
    terms_ref = terms["terms_reference"]
    if not isinstance(terms_ref, str) or REF.fullmatch(terms_ref) is None:
        raise BuyBoxTellerProposalError("TERMS_REFERENCE_INVALID")

    core = {
        "opportunity_id": opportunity_id,
        "opportunity_revision": revision,
        "input_snapshot_digest": digest,
        "vertical_id": vertical,
        "stored_asking_price": asking,
        "terms": {**normalized, "funding_lane": lane, "terms_reference": terms_ref},
    }
    fingerprint = hashlib.sha256(_canonical(core).encode("utf-8")).hexdigest()
    if (
        not isinstance(packet["terms_fingerprint"], str)
        or not SHA256.fullmatch(packet["terms_fingerprint"])
        or fingerprint != packet["terms_fingerprint"]
    ):
        raise BuyBoxTellerProposalError("TERMS_FINGERPRINT_MISMATCH")

    now = datetime.now(timezone.utc) if now_utc is None else now_utc
    if not isinstance(now, datetime) or now.tzinfo is None or now.utcoffset() is None:
        raise BuyBoxTellerProposalError("EVALUATION_TIME_INVALID")
    now = now.astimezone(timezone.utc)
    issued, expires = _time(packet["issued_at"]), _time(packet["valid_until"])
    if (
        issued > now + timedelta(seconds=30)
        or not timedelta(0) < expires - issued <= timedelta(seconds=MAX_LIFETIME_SECONDS)
    ):
        raise BuyBoxTellerProposalError("REQUEST_TIME_INVALID")
    if now >= expires:
        raise BuyBoxTellerProposalError("REQUEST_EXPIRED")

    # Return only normalized, non-authoritative shape; do not reinterpret money
    # figures as account facts or use client-provided buyer/entity assertions.
    return json.loads(_canonical(packet))


def review_untrusted_teller_readiness_proposal(
    packet: Mapping[str, Any], *, now_utc: datetime | None = None
) -> dict[str, Any]:
    """Always remain blocked until real independent source/Tower/Teller proofs."""
    validated = validate_untrusted_teller_readiness_proposal(
        packet, now_utc=now_utc,
    )
    return {
        "schema_version": "tower.buybox.teller.intake.review.v1",
        "state": "SOURCE_ONLY_NOT_SUBMITTED",
        "opportunity_id": validated["opportunity_id"],
        "opportunity_revision": validated["opportunity_revision"],
        "terms_fingerprint": validated["terms_fingerprint"],
        "proposed_funding_lane": validated["terms"]["funding_lane"],
        "reason_codes": [
            "CURRENT_BUYBOX_SNAPSHOT_NOT_INDEPENDENTLY_FETCHED",
            "TOWER_OWNER_ENTITY_AND_PURPOSE_NOT_AUTHENTICATED_FOR_ACTION",
            "TELLER_CURRENT_MONEY_AND_MANAGEMENT_READINESS_NOT_RECEIVED",
            "ATM_PROTECTED_FLOORS_AND_SET_ISOLATION_NOT_INDEPENDENTLY_VERIFIED",
        ],
        "untrusted_shape_valid": True,
        "source_authenticity_verified": False,
        "tower_action_authorized": False,
        "teller_request_sent": False,
        "teller_issuer_verified": False,
        "teller_receipt_present": False,
        "buyer_money_ready": "UNKNOWN",
        "management_capacity_ready": "UNKNOWN",
        "acquisition_ready": False,
        "capital_deployment_authorized": False,
        "external_call_made": False,
    }
