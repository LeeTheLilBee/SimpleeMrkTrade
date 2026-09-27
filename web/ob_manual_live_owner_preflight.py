"""OBML001–005: owner-only Manual Live L1 *source preflight*, not a live unlock.

Recomputes complete OBRES lineage. Tower real owner identity/step-up and external
broker evidence have no authenticated adapter yet. A source-only owner assertion
or simulation receipt can only produce a fail-closed inspection packet.
Legacy GP045 rehearsals remain dry-run-only and are not promoted here.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from hashlib import sha256
import json

from web.ob_market_time_authority import CanonicalMarketTimeReceipt
from web.ob_multi_simulation_harness import MultiSimulationHarness
from web.ob_portfolio_view import PortfolioComparison
from web.ob_position_truth import PositionSnapshot
from web.ob_strategy_review import StrategyCandidate, StrategyReview
from web.ob_safety_review import SafetyReview, SafetySignals
from web.ob_recommendation_review import RecommendationReview
from web.ob_adverse_guard_review import GuardEvidence, GuardReview
from web.ob_soulaana_explanations import SoulaanaExplanation
from web.ob_owner_attention import OwnerAttention
from web.ob_recovery_review import (
    RecoveryReview, RecoveryObservation, verify_recovery_review,
)
from web.ob_operating_mode import validate_mode_state

SCHEMA_VERSION = "OB_OWNER_MANUAL_LIVE_SOURCE_PREFLIGHT_V1"
TOWER_REQUEST = "TOWER_OBML_OWNER_HANDOFF_REQUEST_V1"
MANUAL_STEPS = (
    "RECHECK_CANONICAL_SOURCE_AND_OWNER_REVIEW",
    "OBTAIN_REAL_TOWER_OWNER_SESSION_AND_PURPOSE_BOUND_STEP_UP",
    "INDEPENDENTLY_VERIFY_BROKER_ACCOUNT_AND_INSTRUMENT_PERMISSIONS",
    "REVIEW_PROTECTED_FLOORS_AND_CURRENT_RISK_WITH_REQUIRED_AUTHORITIES",
    "OBTAIN_SEPARATE_MANUAL_LIVE_AUTHORIZATION_AND_REVIEW_CENTER_RECEIPT",
    "OWNER_USES_BROKER_APPLICATION_DIRECTLY_ONLY_AFTER_ALL_REAL_GATES",
    "RECONCILE_ACTUAL_BROKER_ORDER_AND_FILL_FROM_PROVIDER_EVIDENCE",
    "RECORD_DISTINCT_OWNER_REVIEW_AND_SAFE_SESSION_CLOSE",
)


def _digest(value: object) -> str:
    return sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    ).encode()).hexdigest()


@dataclass(frozen=True)
class ManualLiveSourceBundle:
    attention: OwnerAttention
    explanation: SoulaanaExplanation
    recommendation: RecommendationReview
    safety: SafetyReview
    strategy: StrategyReview
    portfolio: PortfolioComparison
    harness: MultiSimulationHarness
    sources: tuple[PositionSnapshot, ...]
    candidates: tuple[StrategyCandidate, ...]
    market_time: CanonicalMarketTimeReceipt
    mode_state: dict[str, object]
    monitored_components: tuple[str, ...]
    as_of_utc: str
    observations: tuple[RecoveryObservation, ...] = ()
    signals: SafetySignals | None = None
    intent: dict[str, object] | None = None
    context: dict[str, object] | None = None
    guard: GuardReview | None = None
    guard_evidence: tuple[GuardEvidence, ...] | None = None


@dataclass(frozen=True)
class OwnerReviewPlan:
    account_key: str
    candidate_id: str
    owner_declared_purpose: str
    owner_acknowledges_review_not_execution: bool
    owner_note: str


@dataclass(frozen=True)
class OwnerManualLivePreflight:
    preflight_id: str
    authority: str
    account_key: str
    source_recovery_id: str
    source_recovery_hash: str
    source_attention_id: str
    source_attention_hash: str
    strategy_review_id: str
    canonical_mode_state_id: str
    canonical_mode: str
    selected_candidate_id: str | None
    owner_plan: OwnerReviewPlan | None
    status: str
    reason_codes: tuple[str, ...]
    owner_manual_steps: tuple[str, ...]
    tower_handoff_contract: str
    tower_server_authorization_verified: bool
    tower_owner_session_authenticated: bool
    tower_purpose_bound_step_up_verified: bool
    actual_broker_account_authenticated: bool
    actual_broker_options_permission_verified: bool
    actual_broker_order_or_fill_verified: bool
    real_account_spendability_verified: bool
    actual_owner_live_mode_enabled: bool
    source_only_rehearsal: bool
    legacy_dry_run_is_production_permission: bool
    manual_placement_recorded_as_provider_fill: bool
    trade_intent_created: bool
    broker_api_order_placed: bool
    unattended_execution: bool
    hybrid_or_automated_mode_enabled: bool
    capital_movement: bool
    protected_floors_released: bool
    kill_switch_cleared: bool
    safety_override: bool
    tower_permission_mutated: bool
    direct_buybox_access: bool
    integrity_hash: str


def _material(item: OwnerManualLivePreflight) -> dict[str, object]:
    return {
        k: (asdict(item.owner_plan) if k == "owner_plan" and item.owner_plan else getattr(item, k))
        for k in OwnerManualLivePreflight.__dataclass_fields__
        if k not in ("preflight_id", "integrity_hash")
    }


def _verify_bundle(value: RecoveryReview, bundle: ManualLiveSourceBundle) -> bool:
    if not isinstance(bundle, ManualLiveSourceBundle):
        return False
    return verify_recovery_review(
        value, bundle.attention, bundle.explanation, bundle.recommendation,
        bundle.safety, bundle.strategy, portfolio=bundle.portfolio,
        harness=bundle.harness, sources=bundle.sources, candidates=bundle.candidates,
        market_time=bundle.market_time, mode_state=bundle.mode_state,
        monitored_components=bundle.monitored_components, as_of_utc=bundle.as_of_utc,
        observations=bundle.observations, signals=bundle.signals, intent=bundle.intent,
        context=bundle.context, guard=bundle.guard, guard_evidence=bundle.guard_evidence,
    )


def _build(
    recovery: RecoveryReview, bundle: ManualLiveSourceBundle,
    *, owner_plan: OwnerReviewPlan | None = None,
) -> OwnerManualLivePreflight:
    if not _verify_bundle(recovery, bundle):
        raise ValueError("OBML requires full independent OBRES and upstream source revalidation")
    mode = validate_mode_state(bundle.mode_state)
    if recovery.account_key != mode["account_key"] or recovery.account_key != bundle.strategy.account_key:
        raise ValueError("OBML account and mode binding mismatch")
    if mode["mode"] not in ("SURVEY", "PAPER", "MANUAL_LIVE_1"):
        raise ValueError("OBML source review cannot inherit Hybrid or Automated mode")
    selected = bundle.recommendation.selected_candidate_id
    if owner_plan is not None:
        if not isinstance(owner_plan, OwnerReviewPlan):
            raise ValueError("owner plan requires canonical explicit review assertion")
        if (
            owner_plan.account_key != recovery.account_key or
            selected is None or owner_plan.candidate_id != selected or
            owner_plan.owner_declared_purpose != "MANUAL_LIVE_1_HUMAN_BROKER_REVIEW" or
            owner_plan.owner_acknowledges_review_not_execution is not True or
            not isinstance(owner_plan.owner_note, str) or
            not owner_plan.owner_note.strip() or
            len(owner_plan.owner_note) > 512
        ):
            raise ValueError("owner plan must bind same account, exact selection and review-only acknowledgement")
    reasons = set(recovery.reason_codes)
    reasons.update((
        "TOWER_OBML_SERVER_VERIFIED_HANDOFF_NOT_IMPLEMENTED",
        "FRESH_TOWER_PURPOSE_BOUND_STEP_UP_NOT_VERIFIED",
        "BROKER_ACCOUNT_AND_OPTIONS_PERMISSIONS_NOT_EXTERNALLY_VERIFIED",
        "CURRENT_REAL_MARKET_AND_SETTLEMENT_SOURCES_NOT_AUTHENTICATED",
        "OWNER_LIVE_MODE_AND_REVIEW_CENTER_NOT_SEPARATELY_AUTHORIZED",
        "ACTUAL_BROKER_PLACEMENT_AND_FILL_NOT_RECONCILED",
    ))
    if owner_plan is None:
        reasons.add("NO_EXPLICIT_OWNER_REVIEW_PLAN")
    if mode["mode"] != "MANUAL_LIVE_1":
        reasons.add("SOURCE_MODE_IS_NOT_MANUAL_LIVE_1")
    if recovery.state == "CANONICAL_BLOCK_RETAINED" or bundle.safety.state == "BLOCK":
        status = "BLOCKED_CANONICAL_SAFETY"
        reasons.add("CANONICAL_SAFETY_DENIAL_CANNOT_BE_CLEARED_BY_OWNER_ASSERTION")
    elif bundle.recommendation.state != "OWNER_REVIEW_READY":
        status = "HOLD_UPSTREAM_OWNER_REVIEW"
        reasons.add("CANONICAL_OWNER_REVIEW_NOT_READY")
    elif recovery.state != "FRESH_CANONICAL_REVALIDATION_REQUIRED":
        status = "HOLD_SOURCE_RECONCILIATION"
        reasons.add("RECOVERY_SOURCES_NOT_RECONCILED")
    else:
        status = "HOLD_FRESH_REVALIDATION_TOWER_AND_BROKER"
        reasons.add("DISTINCT_RESTORATION_CLAIMS_REQUIRE_FRESH_CANONICAL_REVALIDATION")
    item = OwnerManualLivePreflight(
        preflight_id="PENDING", authority=SCHEMA_VERSION,
        account_key=recovery.account_key,
        source_recovery_id=recovery.review_id, source_recovery_hash=recovery.integrity_hash,
        source_attention_id=bundle.attention.queue_id,
        source_attention_hash=bundle.attention.integrity_hash,
        strategy_review_id=bundle.strategy.review_id,
        canonical_mode_state_id=mode["state_id"],
        canonical_mode=mode["mode"], selected_candidate_id=selected, owner_plan=owner_plan,
        status=status, reason_codes=tuple(sorted(reasons)), owner_manual_steps=MANUAL_STEPS,
        tower_handoff_contract=TOWER_REQUEST,
        tower_server_authorization_verified=False, tower_owner_session_authenticated=False,
        tower_purpose_bound_step_up_verified=False,
        actual_broker_account_authenticated=False,
        actual_broker_options_permission_verified=False,
        actual_broker_order_or_fill_verified=False,
        real_account_spendability_verified=False,
        actual_owner_live_mode_enabled=False,
        source_only_rehearsal=True, legacy_dry_run_is_production_permission=False,
        manual_placement_recorded_as_provider_fill=False, trade_intent_created=False,
        broker_api_order_placed=False, unattended_execution=False,
        hybrid_or_automated_mode_enabled=False, capital_movement=False,
        protected_floors_released=False, kill_switch_cleared=False,
        safety_override=False, tower_permission_mutated=False,
        direct_buybox_access=False, integrity_hash="PENDING",
    )
    digest = _digest(_material(item))
    return replace(item, preflight_id="OBML-" + digest[:24], integrity_hash=digest)


def verify_owner_manual_live_preflight(
    value: OwnerManualLivePreflight, recovery: RecoveryReview,
    bundle: ManualLiveSourceBundle, *, owner_plan: OwnerReviewPlan | None = None,
) -> bool:
    if not isinstance(value, OwnerManualLivePreflight) or value.authority != SCHEMA_VERSION:
        return False
    if value.source_only_rehearsal is not True or any(getattr(value, k) is not False for k in (
        "tower_server_authorization_verified", "tower_owner_session_authenticated",
        "tower_purpose_bound_step_up_verified", "actual_broker_account_authenticated",
        "actual_broker_options_permission_verified", "actual_broker_order_or_fill_verified",
        "real_account_spendability_verified", "actual_owner_live_mode_enabled",
        "legacy_dry_run_is_production_permission", "manual_placement_recorded_as_provider_fill",
        "trade_intent_created", "broker_api_order_placed", "unattended_execution",
        "hybrid_or_automated_mode_enabled", "capital_movement", "protected_floors_released",
        "kill_switch_cleared", "safety_override", "tower_permission_mutated",
        "direct_buybox_access",
    )):
        return False
    try:
        return value == _build(recovery, bundle, owner_plan=owner_plan)
    except (ValueError, TypeError, AttributeError, KeyError):
        return False


def build_owner_manual_live_preflight(
    recovery: RecoveryReview, bundle: ManualLiveSourceBundle,
    *, owner_plan: OwnerReviewPlan | None = None,
) -> OwnerManualLivePreflight:
    value = _build(recovery, bundle, owner_plan=owner_plan)
    if not verify_owner_manual_live_preflight(value, recovery, bundle, owner_plan=owner_plan):
        raise ValueError("OBML preflight failed independent source revalidation")
    return value


def manual_live_preflight_reference(
    value: OwnerManualLivePreflight, recovery: RecoveryReview,
    bundle: ManualLiveSourceBundle, *, owner_plan: OwnerReviewPlan | None = None,
) -> dict[str, object]:
    if not verify_owner_manual_live_preflight(value, recovery, bundle, owner_plan=owner_plan):
        raise ValueError("OBML reference requires complete canonical source verification")
    return {
        "authority": SCHEMA_VERSION, "preflight_id": value.preflight_id,
        "integrity_hash": value.integrity_hash, "account_key": value.account_key,
        "source_recovery_id": value.source_recovery_id, "status": value.status,
        "reason_codes": list(value.reason_codes), "tower_handoff_contract": TOWER_REQUEST,
        "amounts_exposed": False, "real_manual_live_enabled": False,
        "broker_submission": False, "capital_movement": False,
        "tower_authorization_required": True,
    }


def manual_live_preflight_contract() -> dict[str, object]:
    return {
        "authority": SCHEMA_VERSION, "upstream_authority": "OB_RECOVERY_REVIEW_V1",
        "tower_requested_authority": TOWER_REQUEST,
        "full_source_lineage_recomputed": True,
        "owner_claim_is_not_tower_or_broker_authentication": True,
        "dry_run_is_not_production_permission": True,
        "owner_places_any_eventual_order_outside_ob": True,
        "broker_order_api": False, "actual_broker_fill_verified": False,
        "tower_owner_verification_implemented_by_this_pack": False,
        "manual_live_unlock": False, "hybrid_unlock": False,
        "automated_unlock": False, "trade_intent_created": False,
        "broker_submission": False, "capital_movement": False,
        "kill_switch_clear": False, "protected_floor_release": False,
        "direct_buybox_access": False, "teller_owns_acquisition_readiness": True,
    }
