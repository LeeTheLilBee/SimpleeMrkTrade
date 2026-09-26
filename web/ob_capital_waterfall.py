"""OBCAP006–010: read-only ATM sleeve capital waterfall *rehearsal*.

Consumes immutable, indicative OBCAP001–005 observations and explicitly supplied
existing plan/floor references. It does not create authoritative owner policy,
settlement proof, actual available acquisition money, transfers, or readiness.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict, replace
from hashlib import sha256
import json
import re

from web.ob_capital_truth import (
    CapitalSnapshot, verify_capital_snapshot,
)

SCHEMA_VERSION = "OB_CAPITAL_WATERFALL_PROJECTION_V1"
SOURCE_AUTHORITY = "OB_CAPITAL_TRUTH_V1"
ATM_ACCOUNT = "simplee_on_the_go_atm"
ATM_SCOPES = (
    "ATM_SET_1_ACQUISITION",
    "ATM_SET_1_OPERATIONS_VAULT",
    "ATM_SET_2_ACQUISITION",
    "ATM_SET_2_OPERATIONS_VAULT",
)
ESSENTIAL_FIELDS = (
    "settled_cash", "protected_base", "protected_reserve",
    "committed_capital", "pending_distribution", "total_account_value",
)
PROJECTION_STATES = ("CONFLICT", "UNKNOWN", "STALE", "REVIEW_INDICATIVE")
HASH_PATTERN = re.compile(r"[0-9a-f]{64}")


def _hash(item: object) -> str:
    return sha256(json.dumps(
        item, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    ).encode("utf-8")).hexdigest()


def _name(value: str, label: str) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise ValueError(label + " must be nonblank and exact")
    return value


def _cents(value: int, label: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(label + " must be a nonnegative integer-cent value")
    return value


def _hash_ref(value: str) -> str:
    if not isinstance(value, str) or not HASH_PATTERN.fullmatch(value):
        raise ValueError("source fingerprint must be lowercase SHA-256")
    return value


@dataclass(frozen=True)
class SleeveIntent:
    scope: str
    existing_protected_floor_minor: int
    minimum_target_minor: int
    prior_high_water_minor: int
    requested_floor_ratchet_minor: int


@dataclass(frozen=True)
class WaterfallPlan:
    plan_id: str
    authority: str
    account_key: str
    policy_source_ref: str
    policy_source_hash: str
    policy_revision: str
    owner_confirmed_intent: bool
    intents: tuple[SleeveIntent, ...]
    external_policy_authenticity_verified: bool
    policy_mutation: bool
    integrity_hash: str


@dataclass(frozen=True)
class SleeveProjection:
    scope: str
    snapshot_id: str
    snapshot_hash: str
    state: str
    reasons: tuple[str, ...]
    observed_field_states: tuple[tuple[str, str], ...]
    indicative_unallocated_minor: int | None
    indicative_target_gap_minor: int | None
    proposed_high_water_minor: int | None
    indicative_drawdown_minor: int | None
    existing_protected_floor_minor: int
    proposed_protected_floor_minor: int
    hypothetical_harvest_minor: int | None
    acquisition_readiness: str
    spend_authorized: bool


@dataclass(frozen=True)
class WaterfallProjection:
    projection_id: str
    authority: str
    plan_id: str
    plan_hash: str
    account_key: str
    as_of_utc: str
    sleeves: tuple[SleeveProjection, ...]
    external_capital_verified: bool
    capital_movement: bool
    owner_policy_changed: bool
    acquisition_readiness: str
    teller_readiness_required: bool
    integrity_hash: str


def _plan_material(plan: WaterfallPlan) -> dict[str, object]:
    return {
        "authority": plan.authority, "account_key": plan.account_key,
        "policy_source_ref": plan.policy_source_ref,
        "policy_source_hash": plan.policy_source_hash,
        "policy_revision": plan.policy_revision,
        "owner_confirmed_intent": plan.owner_confirmed_intent,
        "intents": [asdict(x) for x in plan.intents],
        "external_policy_authenticity_verified": plan.external_policy_authenticity_verified,
        "policy_mutation": plan.policy_mutation,
    }


def verify_waterfall_plan(plan: WaterfallPlan) -> bool:
    if not isinstance(plan, WaterfallPlan) or plan.authority != SCHEMA_VERSION:
        return False
    if plan.account_key != ATM_ACCOUNT or plan.owner_confirmed_intent is not True:
        return False
    if plan.external_policy_authenticity_verified is not False or plan.policy_mutation is not False:
        return False
    try:
        _name(plan.policy_source_ref, "policy_source_ref")
        _hash_ref(plan.policy_source_hash)
        _name(plan.policy_revision, "policy_revision")
        if not isinstance(plan.intents, tuple) or tuple(x.scope for x in plan.intents) != ATM_SCOPES:
            return False
        for sleeve in plan.intents:
            if not isinstance(sleeve, SleeveIntent):
                return False
            for value in (
                sleeve.existing_protected_floor_minor, sleeve.minimum_target_minor,
                sleeve.prior_high_water_minor, sleeve.requested_floor_ratchet_minor,
            ):
                _cents(value, "sleeve intent amount")
            if sleeve.minimum_target_minor < sleeve.existing_protected_floor_minor:
                return False
            if sleeve.requested_floor_ratchet_minor < sleeve.existing_protected_floor_minor:
                return False
        if not plan.intents[2].minimum_target_minor > plan.intents[0].minimum_target_minor:
            return False
        if not plan.intents[3].minimum_target_minor > plan.intents[1].minimum_target_minor:
            return False
    except (TypeError, ValueError, AttributeError):
        return False
    digest = _hash(_plan_material(plan))
    return plan.integrity_hash == digest and plan.plan_id == "OBCAPPLAN-" + digest[:24]


def build_atm_waterfall_plan(
    *, intents: tuple[SleeveIntent, ...], policy_source_ref: str,
    policy_source_hash: str, policy_revision: str, owner_confirmed_intent: bool,
) -> WaterfallPlan:
    if owner_confirmed_intent is not True:
        raise ValueError("explicit owner confirmation required for plan intent")
    tentative = WaterfallPlan(
        plan_id="PENDING", authority=SCHEMA_VERSION, account_key=ATM_ACCOUNT,
        policy_source_ref=policy_source_ref, policy_source_hash=policy_source_hash,
        policy_revision=policy_revision, owner_confirmed_intent=True,
        intents=intents, external_policy_authenticity_verified=False,
        policy_mutation=False, integrity_hash="PENDING",
    )
    # Avoid fingerprinting a malformed object as an accepted plan.
    digest = _hash(_plan_material(tentative))
    result = replace(tentative, plan_id="OBCAPPLAN-" + digest[:24], integrity_hash=digest)
    if not verify_waterfall_plan(result):
        raise ValueError("ATM Set 1/Set 2 intent/floor/target contract failed verification")
    return result


def _field(snap: CapitalSnapshot, key: str):
    return next(f for f in snap.fields if f.metric == key)


def _project_one(intent: SleeveIntent, snap: CapitalSnapshot) -> SleeveProjection:
    observed = tuple((name, _field(snap, name).state) for name in ESSENTIAL_FIELDS)
    states = {status for _, status in observed}
    if "CONFLICT" in states:
        state, reasons = "CONFLICT", ("SOURCE_CONFLICT",)
    elif "UNKNOWN" in states:
        state, reasons = "UNKNOWN", ("MISSING_REQUIRED_FIELD",)
    elif "STALE" in states:
        state, reasons = "STALE", ("STALE_REQUIRED_FIELD",)
    else:
        state, reasons = "REVIEW_INDICATIVE", ("NO_EXTERNAL_CAPITAL_AUTHENTICATION",)
    # A proposed floor may tighten but never alters the source policy/floor.
    candidate_floor = max(
        intent.existing_protected_floor_minor, intent.requested_floor_ratchet_minor,
    )
    indicative_unallocated = target_gap = hwm = drawdown = harvest = None
    if state == "REVIEW_INDICATIVE":
        get = lambda key: _field(snap, key).value_minor_units
        observed_protected = get("protected_base") + get("protected_reserve")
        protected = max(intent.existing_protected_floor_minor, observed_protected, candidate_floor)
        indicative_unallocated = max(0, get("settled_cash") - protected -
                                     get("committed_capital") - get("pending_distribution"))
        target_gap = max(0, intent.minimum_target_minor - indicative_unallocated)
        hwm = max(intent.prior_high_water_minor, get("total_account_value"))
        drawdown = max(0, intent.prior_high_water_minor - get("total_account_value"))
        surplus = _field(snap, "surplus_capital")
        realized = _field(snap, "realized_pnl")
        if surplus.state == realized.state == "CURRENT":
            harvest = min(indicative_unallocated, surplus.value_minor_units,
                          max(0, realized.value_minor_units))
            # Hypothetical only; never a transfer or permission to harvest.
    return SleeveProjection(
        scope=intent.scope, snapshot_id=snap.snapshot_id,
        snapshot_hash=snap.integrity_hash, state=state, reasons=reasons,
        observed_field_states=observed,
        indicative_unallocated_minor=indicative_unallocated,
        indicative_target_gap_minor=target_gap,
        proposed_high_water_minor=hwm, indicative_drawdown_minor=drawdown,
        existing_protected_floor_minor=intent.existing_protected_floor_minor,
        proposed_protected_floor_minor=candidate_floor,
        hypothetical_harvest_minor=harvest,
        acquisition_readiness="NOT_ASSESSED_BY_OB", spend_authorized=False,
    )


def _projection_material(result: WaterfallProjection) -> dict[str, object]:
    return {
        key: ([asdict(s) for s in result.sleeves] if key == "sleeves"
              else getattr(result, key))
        for key in WaterfallProjection.__dataclass_fields__
        if key not in ("projection_id", "integrity_hash")
    }


def build_atm_waterfall_projection(
    *, plan: WaterfallPlan, snapshots: tuple[CapitalSnapshot, ...],
) -> WaterfallProjection:
    if not verify_waterfall_plan(plan):
        raise ValueError("verified owner plan intent is required")
    if not isinstance(snapshots, tuple) or len(snapshots) != len(ATM_SCOPES):
        raise ValueError("one snapshot required per ATM mission sleeve")
    if any(not verify_capital_snapshot(x) for x in snapshots):
        raise ValueError("capital truth snapshot failed integrity verification")
    if tuple(s.capital_scope_ref for s in snapshots) != ATM_SCOPES:
        raise ValueError("ATM sleeve order/scope mismatch or cross-scope combination")
    if any(s.account_key != ATM_ACCOUNT for s in snapshots):
        raise ValueError("ATM sleeve snapshots cross account boundary")
    if len({s.snapshot_id for s in snapshots}) != 4:
        raise ValueError("duplicate sleeve snapshots forbidden")
    if len({s.as_of_utc for s in snapshots}) != 1:
        raise ValueError("mixed as_of time cannot be pooled")
    sleeves = tuple(_project_one(i, s) for i, s in zip(plan.intents, snapshots))
    provisional = WaterfallProjection(
        projection_id="PENDING", authority=SCHEMA_VERSION,
        plan_id=plan.plan_id, plan_hash=plan.integrity_hash,
        account_key=ATM_ACCOUNT, as_of_utc=snapshots[0].as_of_utc, sleeves=sleeves,
        external_capital_verified=False, capital_movement=False,
        owner_policy_changed=False, acquisition_readiness="NOT_ASSESSED_BY_OB",
        teller_readiness_required=True, integrity_hash="PENDING",
    )
    digest = _hash(_projection_material(provisional))
    result = replace(provisional, projection_id="OBCAPWATER-" + digest[:24], integrity_hash=digest)
    if not verify_atm_waterfall_projection(result, plan=plan, snapshots=snapshots):
        raise ValueError("waterfall projection failed independent verification")
    return result


def verify_atm_waterfall_projection(
    value: WaterfallProjection, *, plan: WaterfallPlan,
    snapshots: tuple[CapitalSnapshot, ...],
) -> bool:
    if not isinstance(value, WaterfallProjection) or not verify_waterfall_plan(plan):
        return False
    if value.authority != SCHEMA_VERSION or value.plan_id != plan.plan_id or value.plan_hash != plan.integrity_hash:
        return False
    if value.account_key != ATM_ACCOUNT or len(value.sleeves) != 4:
        return False
    if value.external_capital_verified is not False or value.capital_movement is not False:
        return False
    if value.owner_policy_changed is not False or value.teller_readiness_required is not True:
        return False
    if value.acquisition_readiness != "NOT_ASSESSED_BY_OB":
        return False
    try:
        if len(snapshots) != 4 or tuple(s.capital_scope_ref for s in snapshots) != ATM_SCOPES:
            return False
        if len({s.as_of_utc for s in snapshots}) != 1 or value.as_of_utc != snapshots[0].as_of_utc:
            return False
        if any(not verify_capital_snapshot(s) or s.account_key != ATM_ACCOUNT for s in snapshots):
            return False
        expected = tuple(_project_one(i, s) for i, s in zip(plan.intents, snapshots))
        if value.sleeves != expected:
            return False
    except (ValueError, TypeError, AttributeError, StopIteration):
        return False
    digest = _hash(_projection_material(value))
    return value.integrity_hash == digest and value.projection_id == "OBCAPWATER-" + digest[:24]


def waterfall_reference(value: WaterfallProjection, *, plan: WaterfallPlan,
                        snapshots: tuple[CapitalSnapshot, ...]) -> dict[str, object]:
    if not verify_atm_waterfall_projection(value, plan=plan, snapshots=snapshots):
        raise ValueError("waterfall reference requires verified lineage")
    return {
        "authority": SCHEMA_VERSION, "projection_id": value.projection_id,
        "integrity_hash": value.integrity_hash, "plan_id": value.plan_id,
        "account_key": value.account_key,
        "sleeve_states": {s.scope: s.state for s in value.sleeves},
        "acquisition_readiness": "NOT_ASSESSED_BY_OB",
        "amounts_exposed": False, "tower_authorization_required": True,
        "teller_readiness_required": True,
    }


def waterfall_contract() -> dict[str, object]:
    return {
        "authority": SCHEMA_VERSION, "source_authority": SOURCE_AUTHORITY,
        "account_key": ATM_ACCOUNT, "scopes": list(ATM_SCOPES),
        "two_distinct_atm_sets": True, "separate_acquisition_and_operations": True,
        "set_2_target_higher_than_set_1": True, "policy_source_is_owner_declared_not_authenticated": True,
        "protected_floor_non_decrease": True,
        "high_water_candidate_not_auto_adopted": True,
        "hypothetical_harvest_only": True, "cash_claims_are_indicative": True,
        "funded_does_not_mean_finished": True,
        "external_capital_verified": False, "acquisition_readiness_claim": False,
        "teller_owns_readiness": True, "teller_reassessment_on_material_terms_change": True,
        "direct_buybox_access": False, "tower_mediation_required": True,
        "owner_policy_mutation": False, "capital_movement": False,
        "broker_submission": False, "manual_live_unlock": False,
        "hybrid_unlock": False, "automated_unlock": False,
    }
