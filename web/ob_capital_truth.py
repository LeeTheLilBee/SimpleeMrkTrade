"""OBCAP001–005: account-scoped, evidence-bound capital observations.

This module does not read broker APIs, trade, transfer funds, infer acquisition
readiness, or turn a self-asserted source hash into external verification.
It records source-labelled monetary claims and reconciles only compatible,
account/scope-bound claims. Teller remains the financial-readiness authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
import re
from typing import Iterable

from web.ob_account_identity_truth import (
    SOURCE_ROLE_TAXONOMY,
    resolve_account_identity,
)

SCHEMA_VERSION = "OB_CAPITAL_TRUTH_V1"
SERVICE_VERSION = "OBCAP001_005_SOURCE_BOUND_CAPITAL_TRUTH"
ACCOUNT_AUTHORITY = "OB_ACCOUNT_IDENTITY_TRUTH_V1"

CAPITAL_FIELDS = (
    "total_account_value",
    "settled_cash",
    "realized_pnl",
    "unrealized_pnl",
    "protected_base",
    "protected_reserve",
    "committed_capital",
    "available_growth_capital",
    "available_trading_capital",
    "maximum_capital_at_risk",
    "harvestable_profit",
    "pending_distribution",
    "surplus_capital",
)
SIGNED_FIELDS = frozenset(("realized_pnl", "unrealized_pnl"))
TRUTH_STATES = frozenset(("CURRENT", "STALE", "UNKNOWN", "CONFLICT"))
# Existing source taxonomy has no authenticated broker-read role. Do not make
# "BROKER_VERIFIED" a user-selectable enum or assume a matching source hash is
# a trusted external attestation.
SOURCE_ROLES = frozenset(SOURCE_ROLE_TAXONOMY)
CAPITAL_SOURCE_ROLES = frozenset((
    "account_operational_state",
    "account_snapshot_projection",
    "performance_reporting",
    "owner_operating_profile",
    "proof_demo_account",
))
assert CAPITAL_SOURCE_ROLES == SOURCE_ROLES


def _timestamp(value: datetime, name: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(name + " must be a timezone-aware datetime")
    return value.astimezone(timezone.utc)


def _name(value: object, name: str) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise ValueError(name + " must be an explicit nonblank string")
    return value


def _hash(value: object) -> str:
    return sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    ).encode("utf-8")).hexdigest()


def _source_hash(value: str) -> str:
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise ValueError("source_payload_hash must be a 64-character lowercase SHA-256")
    return value


def _minor_units(value: str | int | Decimal | None, metric: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, (float, bool)) or not isinstance(value, (str, int, Decimal)):
        raise ValueError("capital amount must be an exact decimal, not float/bool")
    try:
        number = Decimal(str(value).strip())
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("capital amount must be finite decimal") from exc
    if not number.is_finite():
        raise ValueError("capital amount must be finite decimal")
    cents = number * 100
    if cents != cents.to_integral_value():
        raise ValueError("capital money may not contain fractional cents")
    if number < 0 and metric not in SIGNED_FIELDS:
        raise ValueError("negative capital forbidden except signed P&L")
    return int(cents)


@dataclass(frozen=True)
class CapitalObservation:
    observation_id: str
    authority: str
    account_key: str
    account_identity_fingerprint: str
    capital_scope_ref: str
    metric: str
    value_minor_units: int | None
    currency: str
    source_role: str
    origin_class: str
    source_ref: str
    source_revision: str
    source_payload_hash: str
    observed_at_utc: str
    received_at_utc: str
    expires_at_utc: str
    explicit_conflict: bool
    external_authenticity_verified: bool
    integrity_hash: str


@dataclass(frozen=True)
class CapitalField:
    metric: str
    state: str
    value_minor_units: int | None
    observation_ids: tuple[str, ...]
    source_roles: tuple[str, ...]
    origin_classes: tuple[str, ...]
    reason: str
    external_authenticity_verified: bool


@dataclass(frozen=True)
class CapitalSnapshot:
    snapshot_id: str
    authority: str
    account_key: str
    account_identity_fingerprint: str
    capital_scope_ref: str
    currency: str
    as_of_utc: str
    observations: tuple[CapitalObservation, ...]
    fields: tuple[CapitalField, ...]
    deployment_verified: bool
    acquisition_readiness: str
    execution_authority: bool
    capital_movement: bool
    integrity_hash: str


def _observation_material(observation: CapitalObservation) -> dict[str, object]:
    return {
        key: getattr(observation, key)
        for key in CapitalObservation.__dataclass_fields__
        if key not in ("observation_id", "integrity_hash")
    }


def build_capital_observation(
    *, account_key: str, capital_scope_ref: str, metric: str,
    value: str | int | Decimal | None, source_role: str, source_ref: str,
    source_revision: str, source_payload_hash: str,
    observed_at: datetime, received_at: datetime, expires_at: datetime,
    explicit_conflict: bool = False,
) -> CapitalObservation:
    identity = resolve_account_identity(account_key)
    if identity["known"] is not True or identity["account_key"] == "proof_demo" and source_role != "proof_demo_account":
        raise ValueError("capital observation requires correct explicit account identity")
    scope = _name(capital_scope_ref, "capital_scope_ref")
    if metric not in CAPITAL_FIELDS:
        raise ValueError("unknown canonical capital metric")
    if source_role not in CAPITAL_SOURCE_ROLES:
        raise ValueError("source role is not in existing canonical source taxonomy")
    if source_role == "proof_demo_account" and account_key != "proof_demo":
        raise ValueError("simulated Proof/Demo state may not cross into real mission accounts")
    observed = _timestamp(observed_at, "observed_at")
    received = _timestamp(received_at, "received_at")
    expires = _timestamp(expires_at, "expires_at")
    if not observed <= received or expires <= observed:
        raise ValueError("invalid source observation/receipt/expiry sequence")
    if not isinstance(explicit_conflict, bool):
        raise ValueError("explicit_conflict must be boolean")
    provisional = CapitalObservation(
        observation_id="PENDING", authority=SCHEMA_VERSION,
        account_key=identity["account_key"],
        account_identity_fingerprint=identity["identity_fingerprint"],
        capital_scope_ref=scope, metric=metric,
        value_minor_units=_minor_units(value, metric), currency="USD",
        source_role=source_role,
        origin_class=SOURCE_ROLE_TAXONOMY[source_role]["origin_class"],
        source_ref=_name(source_ref, "source_ref"),
        source_revision=_name(source_revision, "source_revision"),
        source_payload_hash=_source_hash(source_payload_hash),
        observed_at_utc=observed.isoformat(),
        received_at_utc=received.isoformat(),
        expires_at_utc=expires.isoformat(),
        explicit_conflict=explicit_conflict,
        external_authenticity_verified=False, integrity_hash="PENDING",
    )
    digest = _hash(_observation_material(provisional))
    result = CapitalObservation(
        **{**provisional.__dict__,
           "observation_id": "OBCAPOBS-" + digest[:24],
           "integrity_hash": digest}
    )
    if not verify_capital_observation(result):
        raise ValueError("constructed capital observation failed verification")
    return result


def verify_capital_observation(value: CapitalObservation) -> bool:
    if not isinstance(value, CapitalObservation) or value.authority != SCHEMA_VERSION:
        return False
    identity = resolve_account_identity(value.account_key)
    if identity["known"] is not True or identity["identity_fingerprint"] != value.account_identity_fingerprint:
        return False
    if value.account_key == "proof_demo" and value.source_role != "proof_demo_account":
        return False
    if value.source_role == "proof_demo_account" and value.account_key != "proof_demo":
        return False
    if value.metric not in CAPITAL_FIELDS or not value.capital_scope_ref or value.currency != "USD":
        return False
    if value.source_role not in CAPITAL_SOURCE_ROLES:
        return False
    if value.origin_class != SOURCE_ROLE_TAXONOMY[value.source_role]["origin_class"]:
        return False
    if value.external_authenticity_verified is not False or not isinstance(value.explicit_conflict, bool):
        return False
    if type(value.value_minor_units) is not int and value.value_minor_units is not None:
        return False
    if value.value_minor_units is not None and value.value_minor_units < 0 and value.metric not in SIGNED_FIELDS:
        return False
    try:
        _source_hash(value.source_payload_hash)
        _name(value.source_ref, "source_ref")
        _name(value.source_revision, "source_revision")
        _name(value.capital_scope_ref, "capital_scope_ref")
        observed = _timestamp(datetime.fromisoformat(value.observed_at_utc), "observed_at")
        received = _timestamp(datetime.fromisoformat(value.received_at_utc), "received_at")
        expires = _timestamp(datetime.fromisoformat(value.expires_at_utc), "expires_at")
        if not observed <= received or expires <= observed:
            return False
    except (ValueError, TypeError):
        return False
    digest = _hash(_observation_material(value))
    return value.integrity_hash == digest and value.observation_id == "OBCAPOBS-" + digest[:24]


def _resolve_field(
    metric: str, observations: tuple[CapitalObservation, ...], as_of: datetime,
) -> CapitalField:
    claims = tuple(sorted(
        (o for o in observations if o.metric == metric),
        key=lambda o: (o.observation_id, o.source_ref, o.source_revision),
    ))
    ids = tuple(o.observation_id for o in claims)
    roles = tuple(sorted({o.source_role for o in claims}))
    origins = tuple(sorted({o.origin_class for o in claims}))
    values = {o.value_minor_units for o in claims if o.value_minor_units is not None}
    if not claims:
        state, value, reason = "UNKNOWN", None, "NO_SOURCE_OBSERVATION"
    elif any(o.explicit_conflict for o in claims):
        state, value, reason = "CONFLICT", None, "EXPLICIT_SOURCE_CONFLICT"
    elif len(values) > 1:
        state, value, reason = "CONFLICT", None, "DISAGREEING_SOURCE_VALUES"
    elif any(o.value_minor_units is None for o in claims):
        state, value, reason = "UNKNOWN", None, "MISSING_SOURCE_VALUE"
    elif any(as_of >= datetime.fromisoformat(o.expires_at_utc) for o in claims):
        state, value, reason = "STALE", None, "SOURCE_EXPIRED"
    else:
        # CURRENT means a recent source-labelled observation, never that a
        # financial institution authenticated its origin or released its funds.
        state, value, reason = "CURRENT", next(iter(values)), "SOURCE_VALUES_AGREE_INDICATIVE"
    return CapitalField(
        metric=metric, state=state, value_minor_units=value,
        observation_ids=ids, source_roles=roles, origin_classes=origins,
        reason=reason, external_authenticity_verified=False,
    )


def _snapshot_material(value: CapitalSnapshot) -> dict[str, object]:
    return {
        "authority": value.authority,
        "account_key": value.account_key,
        "account_identity_fingerprint": value.account_identity_fingerprint,
        "capital_scope_ref": value.capital_scope_ref,
        "currency": value.currency,
        "as_of_utc": value.as_of_utc,
        "observation_hashes": [o.integrity_hash for o in value.observations],
        "fields": [field.__dict__ for field in value.fields],
        "deployment_verified": value.deployment_verified,
        "acquisition_readiness": value.acquisition_readiness,
        "execution_authority": value.execution_authority,
        "capital_movement": value.capital_movement,
    }


def build_capital_snapshot(
    *, account_key: str, capital_scope_ref: str, observations: Iterable[CapitalObservation],
    as_of: datetime,
) -> CapitalSnapshot:
    identity = resolve_account_identity(account_key)
    if identity["known"] is not True:
        raise ValueError("capital snapshot requires explicit known account")
    scope = _name(capital_scope_ref, "capital_scope_ref")
    at = _timestamp(as_of, "as_of")
    claims = tuple(observations)
    if any(not verify_capital_observation(o) for o in claims):
        raise ValueError("capital snapshot requires verified observation integrity")
    if len({o.observation_id for o in claims}) != len(claims):
        raise ValueError("duplicate observation ID")
    for claim in claims:
        if claim.account_key != identity["account_key"] or claim.account_identity_fingerprint != identity["identity_fingerprint"]:
            raise ValueError("capital snapshot source crosses account boundary")
        if claim.capital_scope_ref != scope:
            raise ValueError("capital snapshot cannot silently combine mission scopes")
        if datetime.fromisoformat(claim.received_at_utc) > at:
            raise ValueError("capital source receipt lies after requested as_of")
    ordered = tuple(sorted(claims, key=lambda o: (o.metric, o.observation_id)))
    fields = tuple(_resolve_field(name, ordered, at) for name in CAPITAL_FIELDS)
    provisional = CapitalSnapshot(
        snapshot_id="PENDING", authority=SCHEMA_VERSION,
        account_key=identity["account_key"],
        account_identity_fingerprint=identity["identity_fingerprint"],
        capital_scope_ref=scope, currency="USD", as_of_utc=at.isoformat(),
        observations=ordered, fields=fields,
        deployment_verified=False, acquisition_readiness="NOT_ASSESSED",
        execution_authority=False, capital_movement=False,
        integrity_hash="PENDING",
    )
    digest = _hash(_snapshot_material(provisional))
    result = CapitalSnapshot(**{
        **provisional.__dict__,
        "snapshot_id": "OBCAPSNAP-" + digest[:24], "integrity_hash": digest,
    })
    if not verify_capital_snapshot(result):
        raise ValueError("constructed capital snapshot failed verification")
    return result


def verify_capital_snapshot(value: CapitalSnapshot) -> bool:
    if not isinstance(value, CapitalSnapshot) or value.authority != SCHEMA_VERSION:
        return False
    identity = resolve_account_identity(value.account_key)
    if identity["known"] is not True or value.account_identity_fingerprint != identity["identity_fingerprint"]:
        return False
    if value.currency != "USD" or not value.capital_scope_ref:
        return False
    if value.deployment_verified is not False or value.acquisition_readiness != "NOT_ASSESSED":
        return False
    if value.execution_authority is not False or value.capital_movement is not False:
        return False
    try:
        at = _timestamp(datetime.fromisoformat(value.as_of_utc), "as_of")
        if len({o.observation_id for o in value.observations}) != len(value.observations):
            return False
        if tuple(sorted(value.observations, key=lambda o: (o.metric, o.observation_id))) != value.observations:
            return False
        for o in value.observations:
            if not verify_capital_observation(o) or o.account_key != value.account_key:
                return False
            if o.account_identity_fingerprint != value.account_identity_fingerprint or o.capital_scope_ref != value.capital_scope_ref:
                return False
            if datetime.fromisoformat(o.received_at_utc) > at:
                return False
        expected_fields = tuple(_resolve_field(name, value.observations, at) for name in CAPITAL_FIELDS)
        if value.fields != expected_fields:
            return False
    except (TypeError, ValueError, AttributeError):
        return False
    digest = _hash(_snapshot_material(value))
    return value.integrity_hash == digest and value.snapshot_id == "OBCAPSNAP-" + digest[:24]


def capital_truth_reference(snapshot: CapitalSnapshot) -> dict[str, object]:
    """Non-money-bearing proof reference; Tower must authorize any later disclosure."""
    if not verify_capital_snapshot(snapshot):
        raise ValueError("capital snapshot failed verification")
    return {
        "authority": SCHEMA_VERSION, "snapshot_id": snapshot.snapshot_id,
        "integrity_hash": snapshot.integrity_hash,
        "account_key": snapshot.account_key,
        "account_identity_fingerprint": snapshot.account_identity_fingerprint,
        "capital_scope_ref": snapshot.capital_scope_ref,
        "as_of_utc": snapshot.as_of_utc,
        "metric_states": {f.metric: f.state for f in snapshot.fields},
        "external_authenticity_verified": False,
        "deployment_verified": False, "acquisition_readiness": "NOT_ASSESSED",
        "amounts_exposed": False,
    }


def capital_truth_contract() -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION, "service_version": SERVICE_VERSION,
        "account_authority": ACCOUNT_AUTHORITY,
        "source_roles": sorted(CAPITAL_SOURCE_ROLES),
        "currency": "USD", "money_unit": "INTEGER_CENTS",
        "canonical_fields": list(CAPITAL_FIELDS),
        "missing_is_not_zero": True, "conflicts_never_synthetically_merged": True,
        "historical_is_not_current": True, "simulation_is_not_real": True,
        "owner_entered_is_not_broker_verified": True,
        "source_payload_hash_proves_external_authenticity": False,
        "authenticated_broker_adapter_present": False,
        "broker_verified_values_available": False,
        "source_claims_are_indicative": True, "acquisition_spendability_claim": False,
        "existing_atm_set1_set2_and_protected_floor_policy_unchanged": True,
        "cross_scope_aggregation": False, "read_only": True,
        "tower_authorized_evidence_reference_only": True,
        "teller_owns_financial_administration_and_readiness": True,
        "buybox_may_consume_directly": False, "ob_to_buybox_connection": False,
        "requires_fresh_teller_readiness_on_material_deal_change": True,
        "execution_authority": False, "broker_submission": False,
        "capital_movement": False, "policy_mutation": False,
        "manual_live_unlock": False, "hybrid_unlock": False,
        "automated_unlock": False,
    }
