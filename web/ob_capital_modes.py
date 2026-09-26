"""OBCAP011–015: advice-only capital-mode review, never an OB trading-mode switch.

Sources are the verified, *indicative* ATM four-sleeve waterfall and an explicit
owner-declared policy intent. No external provider verification, owner policy
mutation, capital deployment, financing readiness, or automatic activation.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from datetime import datetime
from hashlib import sha256
import json
import re

from web.ob_capital_waterfall import (
    ATM_ACCOUNT, ATM_SCOPES, WaterfallPlan, WaterfallProjection,
    verify_atm_waterfall_projection,
)
from web.ob_capital_truth import CapitalSnapshot

SCHEMA_VERSION = "OB_CAPITAL_MODE_REVIEW_V1"
MODES = (
    "ACCUMULATE", "BALANCED_GROWTH", "PROTECT",
    "SURPLUS_GROWTH", "HARVEST", "RECOVERY",
)
HASH = re.compile(r"[0-9a-f]{64}")


def _digest(obj: object) -> str:
    return sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()


def _name(value: object, label: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError(label + " requires an explicit value")
    return value


def _minor(value: object, label: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(label + " must be nonnegative exact cents")
    return value


@dataclass(frozen=True)
class CapitalModeThresholds:
    drawdown_watch_bps: int
    drawdown_protect_bps: int
    recovery_exit_bps: int
    minimum_hypothetical_harvest_minor: int
    minimum_indicative_surplus_growth_minor: int
    consecutive_reviews_required: int


@dataclass(frozen=True)
class SleeveModeIntent:
    scope: str
    owner_declared_current_mode: str
    owner_mode_source_ref: str


@dataclass(frozen=True)
class ModeReviewPolicy:
    policy_id: str
    authority: str
    account_key: str
    waterfall_plan_id: str
    waterfall_plan_hash: str
    owner_policy_source_ref: str
    owner_policy_source_hash: str
    revision: str
    owner_confirmed_intent: bool
    thresholds: CapitalModeThresholds
    sleeve_intents: tuple[SleeveModeIntent, ...]
    external_policy_authenticity_verified: bool
    policy_mutation: bool
    integrity_hash: str


@dataclass(frozen=True)
class SleeveModeReview:
    scope: str
    source_evidence_fingerprint: str
    candidate_mode: str | None
    review_state: str
    consistent_observation_streak: int
    drawdown_bps: int | None
    reasons: tuple[str, ...]
    activation_authorized: bool
    acquisition_readiness: str


@dataclass(frozen=True)
class CapitalModeReview:
    review_id: str
    authority: str
    account_key: str
    policy_id: str
    policy_hash: str
    waterfall_id: str
    waterfall_hash: str
    as_of_utc: str
    prior_review_id: str | None
    prior_review_hash: str | None
    sleeves: tuple[SleeveModeReview, ...]
    external_capital_verified: bool
    owner_mode_changed: bool
    trading_mode_changed: bool
    capital_movement: bool
    acquisition_readiness: str
    integrity_hash: str


def _policy_material(item: ModeReviewPolicy) -> dict[str, object]:
    return {key: (
        asdict(item.thresholds) if key == "thresholds" else
        [asdict(s) for s in item.sleeve_intents] if key == "sleeve_intents"
        else getattr(item, key))
        for key in ModeReviewPolicy.__dataclass_fields__ if key not in ("policy_id", "integrity_hash")}


def verify_mode_review_policy(item: ModeReviewPolicy, *, plan: WaterfallPlan) -> bool:
    if not isinstance(item, ModeReviewPolicy) or item.authority != SCHEMA_VERSION:
        return False
    if item.account_key != ATM_ACCOUNT or item.owner_confirmed_intent is not True:
        return False
    if item.external_policy_authenticity_verified is not False or item.policy_mutation is not False:
        return False
    if item.waterfall_plan_id != plan.plan_id or item.waterfall_plan_hash != plan.integrity_hash:
        return False
    try:
        _name(item.owner_policy_source_ref, "owner_policy_source_ref")
        _name(item.revision, "revision")
        if not isinstance(item.owner_policy_source_hash, str) or not HASH.fullmatch(item.owner_policy_source_hash):
            return False
        t = item.thresholds
        if not isinstance(t, CapitalModeThresholds):
            return False
        for x in (t.drawdown_watch_bps, t.drawdown_protect_bps, t.recovery_exit_bps):
            if type(x) is not int:
                return False
        if not (0 <= t.recovery_exit_bps < t.drawdown_watch_bps < t.drawdown_protect_bps <= 10000):
            return False
        if _minor(t.minimum_hypothetical_harvest_minor, "harvest threshold") == 0:
            return False
        if _minor(t.minimum_indicative_surplus_growth_minor, "surplus threshold") == 0:
            return False
        if type(t.consecutive_reviews_required) is not int or not 2 <= t.consecutive_reviews_required <= 100:
            return False
        if tuple(x.scope for x in item.sleeve_intents) != ATM_SCOPES:
            return False
        for intent in item.sleeve_intents:
            if not isinstance(intent, SleeveModeIntent) or intent.owner_declared_current_mode not in MODES:
                return False
            _name(intent.owner_mode_source_ref, "owner_mode_source_ref")
    except (ValueError, TypeError, AttributeError):
        return False
    digest = _digest(_policy_material(item))
    return item.integrity_hash == digest and item.policy_id == "OBCAPMODEPLAN-" + digest[:24]


def build_mode_review_policy(
    *, plan: WaterfallPlan, thresholds: CapitalModeThresholds,
    sleeve_intents: tuple[SleeveModeIntent, ...], owner_policy_source_ref: str,
    owner_policy_source_hash: str, revision: str, owner_confirmed_intent: bool,
) -> ModeReviewPolicy:
    if owner_confirmed_intent is not True:
        raise ValueError("owner confirmation required for mode-review intent")
    provisional = ModeReviewPolicy(
        policy_id="PENDING", authority=SCHEMA_VERSION, account_key=ATM_ACCOUNT,
        waterfall_plan_id=plan.plan_id, waterfall_plan_hash=plan.integrity_hash,
        owner_policy_source_ref=owner_policy_source_ref,
        owner_policy_source_hash=owner_policy_source_hash, revision=revision,
        owner_confirmed_intent=True, thresholds=thresholds,
        sleeve_intents=sleeve_intents,
        external_policy_authenticity_verified=False,
        policy_mutation=False, integrity_hash="PENDING",
    )
    digest = _digest(_policy_material(provisional))
    value = replace(provisional, policy_id="OBCAPMODEPLAN-" + digest[:24], integrity_hash=digest)
    if not verify_mode_review_policy(value, plan=plan):
        raise ValueError("capital-mode thresholds, sleeves or owner policy source invalid")
    return value


def _material(value: CapitalModeReview) -> dict[str, object]:
    return {key: ([asdict(s) for s in value.sleeves] if key == "sleeves" else getattr(value, key))
            for key in CapitalModeReview.__dataclass_fields__ if key not in ("review_id", "integrity_hash")}


def _valid_receipt(previous: CapitalModeReview) -> bool:
    if not isinstance(previous, CapitalModeReview) or previous.authority != SCHEMA_VERSION:
        return False
    if previous.account_key != ATM_ACCOUNT or len(previous.sleeves) != len(ATM_SCOPES):
        return False
    if tuple(s.scope for s in previous.sleeves) != ATM_SCOPES:
        return False
    if any(s.activation_authorized or s.acquisition_readiness != "NOT_ASSESSED_BY_OB" for s in previous.sleeves):
        return False
    if previous.external_capital_verified or previous.owner_mode_changed or previous.trading_mode_changed or previous.capital_movement:
        return False
    if previous.acquisition_readiness != "NOT_ASSESSED_BY_OB":
        return False
    if (previous.prior_review_id is None) != (previous.prior_review_hash is None):
        return False
    digest = _digest(_material(previous))
    return previous.integrity_hash == digest and previous.review_id == "OBCAPMODEREV-" + digest[:24]


def _review_one(waterfall_sleeve, owner_intent: SleeveModeIntent,
                policy: ModeReviewPolicy, prior: SleeveModeReview | None,
                snapshot: CapitalSnapshot) -> SleeveModeReview:
    # Distinct as_of projections over unchanged source observations are not
    # independent confirmations of a policy signal.
    source_fingerprint = _digest([o.integrity_hash for o in snapshot.observations])
    if waterfall_sleeve.state != "REVIEW_INDICATIVE":
        return SleeveModeReview(
            scope=owner_intent.scope, source_evidence_fingerprint=source_fingerprint,
            candidate_mode=None, review_state="INSUFFICIENT_EVIDENCE", consistent_observation_streak=0,
            drawdown_bps=None, reasons=("MISSING_STALE_OR_CONFLICTING_CAPITAL_SOURCE",),
            activation_authorized=False, acquisition_readiness="NOT_ASSESSED_BY_OB",
        )
    previous_peak = waterfall_sleeve.proposed_high_water_minor
    loss = waterfall_sleeve.indicative_drawdown_minor
    if previous_peak is None or loss is None:
        raise ValueError("missing waterfall high-water/drawdown projection")
    drawdown = ((loss * 10000 + previous_peak - 1) // previous_peak) if previous_peak else 0
    t = policy.thresholds
    reasons = ["INDICATIVE_SOURCE_NOT_EXTERNALLY_VERIFIED"]
    if drawdown >= t.drawdown_protect_bps:
        candidate = "PROTECT"
        reasons.append("PROTECT_DRAWDOWN_THRESHOLD")
    elif drawdown >= t.drawdown_watch_bps:
        candidate = "PROTECT"
        reasons.append("WATCH_DRAWDOWN_THRESHOLD")
    elif owner_intent.owner_declared_current_mode in ("PROTECT", "RECOVERY") and drawdown > t.recovery_exit_bps:
        candidate = "RECOVERY"
        reasons.append("RECOVERY_EXIT_NOT_YET_MET")
    elif owner_intent.owner_declared_current_mode == "PROTECT":
        candidate = "RECOVERY"
        reasons.append("OWNER_PROTECT_MODE_REQUIRES_REVIEWED_RECOVERY")
    elif waterfall_sleeve.indicative_target_gap_minor > 0:
        candidate = "ACCUMULATE"
        reasons.append("INDICATIVE_TARGET_SHORTFALL")
    elif waterfall_sleeve.hypothetical_harvest_minor is not None and (
        waterfall_sleeve.hypothetical_harvest_minor >= t.minimum_hypothetical_harvest_minor
    ):
        candidate = "HARVEST"
        reasons.append("HYPOTHETICAL_HARVEST_ONLY")
    elif waterfall_sleeve.indicative_unallocated_minor >= t.minimum_indicative_surplus_growth_minor:
        candidate = "SURPLUS_GROWTH"
        reasons.append("INDICATIVE_SURPLUS_NOT_DEPLOYABLE")
    else:
        candidate = "BALANCED_GROWTH"
        reasons.append("NO_OTHER_ADVISORY_THRESHOLD_MET")
    consistent_prior = (
        prior is not None and prior.candidate_mode == candidate
        and prior.review_state != "INSUFFICIENT_EVIDENCE"
    )
    source_changed = prior is None or prior.source_evidence_fingerprint != source_fingerprint
    streak = (
        prior.consistent_observation_streak + (1 if source_changed else 0)
        if consistent_prior else 1
    )
    # Risk escalation cannot be delayed by a planning hysteresis counter.
    state = (
        "PROTECT_PRIORITY_OWNER_REVIEW" if candidate == "PROTECT" else
        "AWAITING_FRESH_SOURCE_EVIDENCE" if not source_changed else
        "CONSECUTIVE_REVIEW_CRITERION_MET" if streak >= t.consecutive_reviews_required else
        "OBSERVING_HYSTERESIS"
    )
    return SleeveModeReview(
        scope=owner_intent.scope, source_evidence_fingerprint=source_fingerprint,
        candidate_mode=candidate,
        review_state=state, consistent_observation_streak=streak,
        drawdown_bps=drawdown, reasons=tuple(reasons),
        activation_authorized=False, acquisition_readiness="NOT_ASSESSED_BY_OB",
    )


def _build_review(
    *, policy: ModeReviewPolicy, plan: WaterfallPlan,
    waterfall: WaterfallProjection, snapshots: tuple[CapitalSnapshot, ...],
    previous: CapitalModeReview | None,
) -> CapitalModeReview:
    if not verify_mode_review_policy(policy, plan=plan):
        raise ValueError("mode review requires verified owner-declared policy intent")
    if not verify_atm_waterfall_projection(waterfall, plan=plan, snapshots=snapshots):
        raise ValueError("mode review requires verified current waterfall inputs")
    if previous is not None:
        if not _valid_receipt(previous) or previous.policy_id != policy.policy_id or previous.policy_hash != policy.integrity_hash:
            raise ValueError("previous mode review must be a valid same-policy receipt")
        if previous.waterfall_id == waterfall.projection_id:
            raise ValueError("duplicate waterfall cannot increase hysteresis")
        if datetime.fromisoformat(previous.as_of_utc) >= datetime.fromisoformat(waterfall.as_of_utc):
            raise ValueError("mode review chronology must strictly advance")
    signals = tuple(
        _review_one(w, i, policy, previous.sleeves[index] if previous else None, snapshots[index])
        for index, (w, i) in enumerate(zip(waterfall.sleeves, policy.sleeve_intents))
    )
    provisional = CapitalModeReview(
        review_id="PENDING", authority=SCHEMA_VERSION, account_key=ATM_ACCOUNT,
        policy_id=policy.policy_id, policy_hash=policy.integrity_hash,
        waterfall_id=waterfall.projection_id, waterfall_hash=waterfall.integrity_hash,
        as_of_utc=waterfall.as_of_utc,
        prior_review_id=previous.review_id if previous else None,
        prior_review_hash=previous.integrity_hash if previous else None,
        sleeves=signals, external_capital_verified=False,
        owner_mode_changed=False, trading_mode_changed=False,
        capital_movement=False, acquisition_readiness="NOT_ASSESSED_BY_OB",
        integrity_hash="PENDING",
    )
    digest = _digest(_material(provisional))
    return replace(provisional, review_id="OBCAPMODEREV-" + digest[:24], integrity_hash=digest)


def build_capital_mode_review(
    *, policy: ModeReviewPolicy, plan: WaterfallPlan,
    waterfall: WaterfallProjection, snapshots: tuple[CapitalSnapshot, ...],
    previous: CapitalModeReview | None = None,
) -> CapitalModeReview:
    result = _build_review(policy=policy, plan=plan, waterfall=waterfall,
                           snapshots=snapshots, previous=previous)
    if not verify_capital_mode_review(result, policy=policy, plan=plan,
                                      waterfall=waterfall, snapshots=snapshots, previous=previous):
        raise ValueError("capital-mode review failed independent verification")
    return result


def verify_capital_mode_review(
    value: CapitalModeReview, *, policy: ModeReviewPolicy,
    plan: WaterfallPlan, waterfall: WaterfallProjection,
    snapshots: tuple[CapitalSnapshot, ...],
    previous: CapitalModeReview | None = None,
) -> bool:
    if not _valid_receipt(value):
        return False
    try:
        expected = _build_review(policy=policy, plan=plan, waterfall=waterfall,
                                 snapshots=snapshots, previous=previous)
        return value == expected
    except (ValueError, TypeError, AttributeError, ZeroDivisionError):
        return False


def capital_mode_review_reference(
    review: CapitalModeReview, *, policy: ModeReviewPolicy, plan: WaterfallPlan,
    waterfall: WaterfallProjection, snapshots: tuple[CapitalSnapshot, ...],
    previous: CapitalModeReview | None = None,
) -> dict[str, object]:
    if not verify_capital_mode_review(review, policy=policy, plan=plan,
                                     waterfall=waterfall, snapshots=snapshots, previous=previous):
        raise ValueError("capital-mode reference requires verified lineage")
    return {
        "authority": SCHEMA_VERSION, "review_id": review.review_id,
        "integrity_hash": review.integrity_hash, "account_key": review.account_key,
        "sleeve_states": {s.scope: s.review_state for s in review.sleeves},
        "amounts_exposed": False, "activation_authorized": False,
        "acquisition_readiness": "NOT_ASSESSED_BY_OB",
        "tower_authorization_required": True, "teller_readiness_required": True,
    }


def capital_mode_review_contract() -> dict[str, object]:
    return {
        "authority": SCHEMA_VERSION,
        "waterfall_authority": "OB_CAPITAL_WATERFALL_PROJECTION_V1",
        "six_advisory_modes": list(MODES), "explicit_owner_thresholds_required": True,
        "hysteresis": "CHRONOLOGICAL_REVIEWS_WITH_NEW_PER_SLEEVE_SOURCE_EVIDENCE",
        "risk_escalation_not_delayed": True, "previous_receipts_not_external_authenticity": True,
        "policy_changes_reset_hysteresis": True,
        "owner_mode_changed": False, "trading_mode_changed": False,
        "external_capital_verified": False, "capital_movement": False,
        "acquisition_readiness_claim": False, "direct_buybox_access": False,
        "tower_mediation_required": True, "teller_owns_readiness": True,
        "broker_submission": False, "manual_live_unlock": False,
        "hybrid_unlock": False, "automated_unlock": False,
    }
