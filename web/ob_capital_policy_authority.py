"""Restriction-only, pre-policy capital projection for Experimental simulation.

This authority consumes a verified owner profile and existing immutable simulation
capital/OBTIME session-loss evidence. It deliberately does not import or resolve
Effective Policy; post-policy CAPSIM admission continues to consume Effective Policy
in the opposite direction. No live/account/broker authority is created here.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import math

from web.ob_capital_simulation_authority import (
    CapitalSessionLossLedger,
    SimulationCapitalState,
    verify_capital_session_loss_ledger,
    verify_simulation_capital_state,
)
from web.ob_multi_simulation_harness import SimulationLane
from web.ob_owner_operating_profile import (
    validate_limit_value,
    validate_operating_profile,
)

SCHEMA_VERSION = "OB_CAPITAL_POLICY_V1"
SERVICE_VERSION = "CAPSIM011_012_PRE_POLICY_RESTRICTION"
LIMIT_KEYS = (
    "max_loss_per_trade_pct",
    "max_position_allocation_pct",
    "daily_loss_cap_pct",
)
PRECISION = 1_000_000


@dataclass(frozen=True)
class PrePolicyCapitalProjection:
    projection_id: str
    authority: str
    account_key: str
    owner_profile_id: str
    owner_profile_hash: str
    capital_state_snapshot_id: str
    capital_state_hash: str
    session_loss_ledger_id: str
    session_loss_hash: str
    state: str
    reasons: tuple[str, ...]
    baseline_limits: tuple[tuple[str, float], ...]
    limits: tuple[tuple[str, float], ...]
    capacity_factor: float
    simulation_only: bool
    integrity_hash: str


def _material(projection: PrePolicyCapitalProjection) -> dict[str, object]:
    return {
        "authority": projection.authority,
        "account_key": projection.account_key,
        "owner_profile_id": projection.owner_profile_id,
        "owner_profile_hash": projection.owner_profile_hash,
        "capital_state_snapshot_id": projection.capital_state_snapshot_id,
        "capital_state_hash": projection.capital_state_hash,
        "session_loss_ledger_id": projection.session_loss_ledger_id,
        "session_loss_hash": projection.session_loss_hash,
        "state": projection.state,
        "reasons": list(projection.reasons),
        "baseline_limits": list(projection.baseline_limits),
        "limits": list(projection.limits),
        "capacity_factor": projection.capacity_factor,
        "simulation_only": projection.simulation_only,
    }


def _hash(material: dict[str, object]) -> str:
    return sha256(json.dumps(
        material, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    ).encode("utf-8")).hexdigest()


def verify_prepolicy_capital_projection(value: PrePolicyCapitalProjection) -> bool:
    if not isinstance(value, PrePolicyCapitalProjection):
        return False
    if value.authority != SCHEMA_VERSION or value.simulation_only is not True:
        return False
    if value.state not in {"READY", "BLOCK"}:
        return False
    if not 0 <= value.capacity_factor <= 1 or not math.isfinite(value.capacity_factor):
        return False
    baseline = dict(value.baseline_limits)
    limits = dict(value.limits)
    if tuple(baseline) != LIMIT_KEYS or len(value.baseline_limits) != len(LIMIT_KEYS):
        return False
    try:
        if any(validate_limit_value(key, baseline[key]) != baseline[key] for key in LIMIT_KEYS):
            return False
        if value.state == "READY":
            if value.reasons or tuple(limits) != LIMIT_KEYS or value.capacity_factor <= 0:
                return False
            for key in LIMIT_KEYS:
                v = validate_limit_value(key, limits[key])
                if v != limits[key] or not 0 < v <= baseline[key]:
                    return False
        elif limits or not value.reasons:
            return False
    except (ValueError, TypeError, KeyError):
        return False
    digest = _hash(_material(value))
    return (
        value.integrity_hash == digest
        and value.projection_id == "OBCAPPRE-" + digest[:24]
    )


def _floor_percentage(value: float) -> float:
    # Effective Policy uses six-decimal percentage-point normalization. Floor
    # first: a policy projection must not be rounded upward past its cap.
    return math.floor(value * PRECISION) / PRECISION


def build_prepolicy_capital_projection(
    owner_profile: dict[str, object],
    *,
    capital_state: SimulationCapitalState,
    session_loss: CapitalSessionLossLedger,
) -> PrePolicyCapitalProjection:
    profile = validate_operating_profile(owner_profile, require_active=True)
    if not verify_simulation_capital_state(capital_state):
        raise ValueError("pre-policy capital state must be verified")
    if not verify_capital_session_loss_ledger(session_loss):
        raise ValueError("pre-policy session-loss ledger must be verified")
    account = profile["account"]["account_key"]
    if account != capital_state.account_key or account != session_loss.account_key:
        raise ValueError("pre-policy capital sources may not cross account boundaries")
    if (
        capital_state.lane is not SimulationLane.EXPERIMENTAL
        or session_loss.lane is not SimulationLane.EXPERIMENTAL
    ):
        raise ValueError("pre-policy simulation projection requires Experimental lane")
    baseline = tuple(
        (key, validate_limit_value(key, profile["risk_envelope"]["effective_limits"][key]))
        for key in LIMIT_KEYS
    )
    owner_limits = dict(baseline)
    reasons: list[str] = []
    equity = capital_state.equity
    cash = capital_state.cash
    peak = capital_state.peak_equity
    if capital_state.receipt_chain_valid is not True:
        reasons.append("SIMULATION_RECEIPT_CHAIN_UNVERIFIED")
    if not session_loss.coverage_complete:
        reasons.append("INCOMPLETE_CANONICAL_SESSION_LOSS_HISTORY")
    if not all(math.isfinite(n) for n in (equity, cash, peak, session_loss.daily_loss_amount)):
        reasons.append("NONFINITE_CAPITAL_EVIDENCE")
    if equity <= 0 or cash <= 0 or peak <= 0:
        reasons.append("NO_POSITIVE_CAPITAL_CAPACITY")
    if not reasons and session_loss.daily_loss_amount >= equity * owner_limits["daily_loss_cap_pct"] / 100:
        reasons.append("OWNER_DAILY_LOSS_LIMIT_EXHAUSTED")
    if reasons:
        factor, limits = 0.0, ()
    else:
        # No new risk threshold: both ratios are bounded by actual simulation
        # liquidity and high-water/equity preservation. Loss ledger supplies a
        # fail-closed exhaustion check; CAPSIM retains the total-day loss test.
        factor = min(1.0, cash / equity, equity / peak)
        factor = max(0.0, factor)
        limits = tuple(
            (key, validate_limit_value(key, _floor_percentage(owner_limits[key] * factor)))
            for key in LIMIT_KEYS
        ) if factor > 0 else ()
        if not limits or any(value <= 0 for _, value in limits):
            reasons.append("NO_REPRESENTABLE_POSITIVE_RESTRICTION")
            factor, limits = 0.0, ()
    provisional = PrePolicyCapitalProjection(
        projection_id="PENDING",
        authority=SCHEMA_VERSION,
        account_key=account,
        owner_profile_id=profile["profile_id"],
        owner_profile_hash=profile["profile_hash"],
        capital_state_snapshot_id=capital_state.snapshot_id,
        capital_state_hash=capital_state.integrity_hash,
        session_loss_ledger_id=session_loss.ledger_id,
        session_loss_hash=session_loss.integrity_hash,
        state="BLOCK" if reasons else "READY",
        reasons=tuple(reasons),
        baseline_limits=baseline,
        limits=limits,
        capacity_factor=round(factor, 12),
        simulation_only=True,
        integrity_hash="PENDING",
    )
    digest = _hash(_material(provisional))
    result = PrePolicyCapitalProjection(
        **{
            **provisional.__dict__,
            "projection_id": "OBCAPPRE-" + digest[:24],
            "integrity_hash": digest,
        }
    )
    if not verify_prepolicy_capital_projection(result):
        raise ValueError("pre-policy capital projection failed verification")
    return result


def prepolicy_capital_contract() -> dict[str, object]:
    return {
        "authority": SCHEMA_VERSION,
        "service_version": SERVICE_VERSION,
        "pre_policy": True,
        "imports_effective_policy": False,
        "consumes_owner_profile": True,
        "consumes_verified_simulation_capital": True,
        "consumes_verified_session_loss": True,
        "experimental_only": True,
        "restriction_only": True,
        "precision": 6,
        "effective_policy_promotion": False,
        "simulation_only": True,
        "broker_submission": False,
        "capital_movement": False,
        "manual_live_unlock": False,
        "hybrid_unlock": False,
        "automated_unlock": False,
    }
