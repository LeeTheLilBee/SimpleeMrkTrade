"""OBATTN001–005: deterministic owner attention over canonical Soulaana receipts.

A queue card is not an alarm dispatch, proof of an actual broker incident,
recommendation, policy update, acknowledgement or execution authority. Sources
are reverified recursively, and source-blocked review cannot be re-ranked ready.
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
from web.ob_soulaana_explanations import (
    SoulaanaExplanation, verify_soulaana_explanation,
)

SCHEMA_VERSION = "OB_OWNER_ATTENTION_V1"
PRIORITY_ORDER = (
    "P0_CANONICAL_BLOCK",
    "P1_REPEATED_SOURCE_GUARD",
    "P2_EVIDENCE_HOLD",
    "P3_OWNER_REVIEW",
)
PRIORITY_INDEX = {value: index for index, value in enumerate(PRIORITY_ORDER)}
STATE_TASK = {
    "BLOCKED": ("P0_CANONICAL_BLOCK", "REVIEW_CANONICAL_SAFETY_BLOCK"),
    "EVIDENCE_PENDING": ("P2_EVIDENCE_HOLD", "REQUEST_MISSING_CANONICAL_EVIDENCE"),
    "OWNER_REVIEW_READY": ("P3_OWNER_REVIEW", "OWNER_MAY_INSPECT_REVIEW_PACKET"),
}
STATE_TEXT = {
    "BLOCKED": "Canonical safety blocks owner review. Inspect source reasons; no trade permission.",
    "EVIDENCE_PENDING": "Canonical evidence is incomplete. Review its missing or held source reasons.",
    "OWNER_REVIEW_READY": "An owner review packet is available. Review is not permission to trade.",
}


def _hash(value: object) -> str:
    return sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    ).encode()).hexdigest()


@dataclass(frozen=True)
class AttentionItem:
    priority: str
    task_code: str
    source_authority: str
    source_receipt_id: str
    source_integrity_hash: str
    reason_codes: tuple[str, ...]
    text: str
    asserted_source_only: bool
    actionable_execution: bool
    dismisses_safety_block: bool


@dataclass(frozen=True)
class OwnerAttention:
    queue_id: str
    authority: str
    account_key: str
    recommendation_id: str
    recommendation_hash: str
    safety_review_id: str
    safety_review_hash: str
    explanation_id: str
    explanation_hash: str
    guard_id: str | None
    guard_hash: str | None
    source_recommendation_state: str
    items: tuple[AttentionItem, ...]
    top_priority: str
    owner_action_is_manual_review_only: bool
    external_broker_events_verified: bool
    live_notification_dispatched: bool
    source_truth_mutated: bool
    safety_override: bool
    broker_submission: bool
    capital_movement: bool
    trading_mode_change: bool
    direct_buybox_access: bool
    integrity_hash: str


def _material(value: OwnerAttention) -> dict[str, object]:
    return {
        key: [asdict(i) for i in value.items] if key == "items" else getattr(value, key)
        for key in OwnerAttention.__dataclass_fields__
        if key not in ("queue_id", "integrity_hash")
    }


def _build(
    explanation: SoulaanaExplanation, recommendation: RecommendationReview,
    safety: SafetyReview, strategy: StrategyReview, *,
    portfolio: PortfolioComparison, harness: MultiSimulationHarness,
    sources: tuple[PositionSnapshot, ...],
    candidates: tuple[StrategyCandidate, ...],
    market_time: CanonicalMarketTimeReceipt,
    mode_state: dict[str, object], signals: SafetySignals | None = None,
    intent: dict[str, object] | None = None,
    context: dict[str, object] | None = None,
    guard: GuardReview | None = None,
    guard_evidence: tuple[GuardEvidence, ...] | None = None,
) -> OwnerAttention:
    if not verify_soulaana_explanation(
        explanation, recommendation, safety, strategy,
        portfolio=portfolio, harness=harness, sources=sources,
        candidates=candidates, market_time=market_time, mode_state=mode_state,
        signals=signals, intent=intent, context=context, guard=guard,
        guard_evidence=guard_evidence,
    ):
        raise ValueError("OBATTN requires verified full OBSOUL source lineage")
    if explanation.account_key != recommendation.account_key or safety.account_key != recommendation.account_key:
        raise ValueError("owner attention cannot cross account identity")
    if explanation.source_state != recommendation.state:
        raise ValueError("Soulaana/recommendation source states diverge")
    if recommendation.state not in STATE_TASK:
        raise ValueError("unknown canonical recommendation state")
    priority, task = STATE_TASK[recommendation.state]
    items = [AttentionItem(
        priority=priority, task_code=task,
        source_authority=recommendation.authority,
        source_receipt_id=recommendation.recommendation_id,
        source_integrity_hash=recommendation.integrity_hash,
        reason_codes=tuple(recommendation.reason_codes),
        text=STATE_TEXT[recommendation.state],
        asserted_source_only=True, actionable_execution=False,
        dismisses_safety_block=False,
    )]
    if guard is not None:
        repeated = tuple(sorted(
            p.issue_code for p in guard.source_assertion_patterns
            if p.repeated_source_assertion
        ))
        if repeated:
            items.append(AttentionItem(
                priority="P1_REPEATED_SOURCE_GUARD",
                task_code="INSPECT_REPEATED_DISTINCT_SOURCE_ASSERTIONS",
                source_authority=guard.authority,
                source_receipt_id=guard.guard_id,
                source_integrity_hash=guard.integrity_hash,
                reason_codes=repeated,
                text=(
                    "Inspect repeated distinct source assertions. These are not "
                    "authenticated market events and do not actuate a kill switch."
                ),
                asserted_source_only=True, actionable_execution=False,
                dismisses_safety_block=False,
            ))
    ordered = tuple(sorted(
        items, key=lambda x: (
            PRIORITY_INDEX[x.priority], x.task_code, x.source_receipt_id,
        ),
    ))
    provisional = OwnerAttention(
        queue_id="PENDING", authority=SCHEMA_VERSION,
        account_key=recommendation.account_key,
        recommendation_id=recommendation.recommendation_id,
        recommendation_hash=recommendation.integrity_hash,
        safety_review_id=safety.review_id, safety_review_hash=safety.integrity_hash,
        explanation_id=explanation.explanation_id,
        explanation_hash=explanation.integrity_hash,
        guard_id=guard.guard_id if guard else None,
        guard_hash=guard.integrity_hash if guard else None,
        source_recommendation_state=recommendation.state, items=ordered,
        top_priority=ordered[0].priority,
        owner_action_is_manual_review_only=True,
        external_broker_events_verified=False,
        live_notification_dispatched=False,
        source_truth_mutated=False, safety_override=False,
        broker_submission=False, capital_movement=False,
        trading_mode_change=False, direct_buybox_access=False,
        integrity_hash="PENDING",
    )
    digest = _hash(_material(provisional))
    return replace(provisional, queue_id="OBATTN-" + digest[:24], integrity_hash=digest)


def verify_owner_attention(
    value: OwnerAttention, explanation: SoulaanaExplanation,
    recommendation: RecommendationReview, safety: SafetyReview,
    strategy: StrategyReview, *,
    portfolio: PortfolioComparison, harness: MultiSimulationHarness,
    sources: tuple[PositionSnapshot, ...],
    candidates: tuple[StrategyCandidate, ...],
    market_time: CanonicalMarketTimeReceipt,
    mode_state: dict[str, object], signals: SafetySignals | None = None,
    intent: dict[str, object] | None = None,
    context: dict[str, object] | None = None,
    guard: GuardReview | None = None,
    guard_evidence: tuple[GuardEvidence, ...] | None = None,
) -> bool:
    if not isinstance(value, OwnerAttention) or value.authority != SCHEMA_VERSION:
        return False
    if value.owner_action_is_manual_review_only is not True or any(
        getattr(value, field) is not False for field in (
            "external_broker_events_verified", "live_notification_dispatched",
            "source_truth_mutated", "safety_override", "broker_submission",
            "capital_movement", "trading_mode_change", "direct_buybox_access",
        )
    ):
        return False
    try:
        return value == _build(
            explanation, recommendation, safety, strategy,
            portfolio=portfolio, harness=harness, sources=sources,
            candidates=candidates, market_time=market_time, mode_state=mode_state,
            signals=signals, intent=intent, context=context,
            guard=guard, guard_evidence=guard_evidence,
        )
    except (ValueError, TypeError, AttributeError, KeyError):
        return False


def build_owner_attention(
    explanation: SoulaanaExplanation,
    recommendation: RecommendationReview, safety: SafetyReview,
    strategy: StrategyReview, *,
    portfolio: PortfolioComparison, harness: MultiSimulationHarness,
    sources: tuple[PositionSnapshot, ...],
    candidates: tuple[StrategyCandidate, ...],
    market_time: CanonicalMarketTimeReceipt,
    mode_state: dict[str, object], signals: SafetySignals | None = None,
    intent: dict[str, object] | None = None,
    context: dict[str, object] | None = None,
    guard: GuardReview | None = None,
    guard_evidence: tuple[GuardEvidence, ...] | None = None,
) -> OwnerAttention:
    value = _build(
        explanation, recommendation, safety, strategy,
        portfolio=portfolio, harness=harness, sources=sources,
        candidates=candidates, market_time=market_time, mode_state=mode_state,
        signals=signals, intent=intent, context=context,
        guard=guard, guard_evidence=guard_evidence,
    )
    if not verify_owner_attention(
        value, explanation, recommendation, safety, strategy,
        portfolio=portfolio, harness=harness, sources=sources,
        candidates=candidates, market_time=market_time, mode_state=mode_state,
        signals=signals, intent=intent, context=context,
        guard=guard, guard_evidence=guard_evidence,
    ):
        raise ValueError("owner attention failed full source verification")
    return value


def attention_reference(
    value: OwnerAttention, explanation: SoulaanaExplanation,
    recommendation: RecommendationReview, safety: SafetyReview,
    strategy: StrategyReview, *,
    portfolio: PortfolioComparison, harness: MultiSimulationHarness,
    sources: tuple[PositionSnapshot, ...],
    candidates: tuple[StrategyCandidate, ...],
    market_time: CanonicalMarketTimeReceipt,
    mode_state: dict[str, object], signals: SafetySignals | None = None,
    intent: dict[str, object] | None = None,
    context: dict[str, object] | None = None,
    guard: GuardReview | None = None,
    guard_evidence: tuple[GuardEvidence, ...] | None = None,
) -> dict[str, object]:
    if not verify_owner_attention(
        value, explanation, recommendation, safety, strategy,
        portfolio=portfolio, harness=harness, sources=sources,
        candidates=candidates, market_time=market_time, mode_state=mode_state,
        signals=signals, intent=intent, context=context,
        guard=guard, guard_evidence=guard_evidence,
    ):
        raise ValueError("attention reference requires fully verified source lineage")
    return {
        "authority": SCHEMA_VERSION, "queue_id": value.queue_id,
        "integrity_hash": value.integrity_hash,
        "account_key": value.account_key,
        "top_priority": value.top_priority,
        "source_recommendation_state": value.source_recommendation_state,
        "source_receipt_ids": [
            value.recommendation_id, value.safety_review_id, value.explanation_id,
        ] + ([value.guard_id] if value.guard_id else []),
        "amounts_exposed": False,
        "live_notification_dispatched": False,
        "broker_submission": False,
        "capital_movement": False,
        "tower_authorization_required": True,
    }


def attention_contract() -> dict[str, object]:
    return {
        "authority": SCHEMA_VERSION,
        "upstream_explanation": "OB_SOULAANA_EXPLANATION_V1",
        "upstream_recommendation": "OB_RECOMMENDATION_REVIEW_V1",
        "upstream_guard": "OB_ADVERSE_GUARD_REVIEW_V1",
        "canonical_state_never_overridden": True,
        "source_lineage_fully_reverified": True,
        "repeated_guard_requires_distinct_source_payloads": True,
        "priority_only_not_trade_or_strategy_ranking": True,
        "missing_guard_not_proof_of_safety": True,
        "source_assertions_not_broker_verified": True,
        "owner_manual_review_only": True,
        "live_notification_dispatch": False,
        "acknowledgement_or_dismissal_mutates_safety": False,
        "order_authority": False,
        "broker_submission": False, "capital_movement": False,
        "trading_mode_change": False, "manual_live_unlock": False,
        "hybrid_unlock": False, "automated_unlock": False,
        "direct_buybox_access": False, "teller_owns_acquisition_readiness": True,
    }
