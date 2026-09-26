"""OBLEARN001–005: bounded owner-review feedback, never an outcome oracle.

Consumes a fully reverified OBREV receipt. It may surface evidence gaps and
adverse-source review tasks, but it has no authenticated broker fill/P&L input,
no new prediction model, no self-training policy or risk-mode actuator.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
import json

from web.ob_market_time_authority import CanonicalMarketTimeReceipt
from web.ob_multi_simulation_harness import MultiSimulationHarness
from web.ob_portfolio_view import PortfolioComparison
from web.ob_position_truth import PositionSnapshot
from web.ob_strategy_review import StrategyCandidate, StrategyReview
from web.ob_safety_review import SafetyReview, SafetySignals
from web.ob_recommendation_review import RecommendationReview
from web.ob_owner_review_evidence import (
    OwnerReviewRecord, OwnerReviewDecision, ReviewIssue, verify_owner_review,
)

SCHEMA_VERSION = "OB_REVIEW_LEARNING_V1"
ISSUE_TASKS = {
    "NEGATIVE_DIVE": "REVIEW_NEGATIVE_DIVE",
    "OVERTIME": "REVIEW_OVERTIME",
    "OVERREACH": "REVIEW_OVERREACH",
    "SOURCE_GAP": "REQUEST_MISSING_SOURCE_EVIDENCE",
}
DECISION_TASKS = {
    "DEFER": "REVISIT_OWNER_DEFER",
    "DECLINE": "REVIEW_OWNER_DECLINE_CONTEXT",
    "REQUEST_MORE_EVIDENCE": "REQUEST_ADDITIONAL_EVIDENCE",
    "INTERESTED_FOR_REVIEW": "AWAIT_AUTHENTICATED_OUTCOME_BEFORE_LEARNING",
}


def _hash(value: object) -> str:
    return sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    ).encode()).hexdigest()


@dataclass(frozen=True)
class ReviewLearning:
    learning_id: str
    authority: str
    account_key: str
    owner_review_id: str
    owner_review_hash: str
    recommendation_id: str
    recommendation_hash: str
    source_issue_ids: tuple[str, ...]
    source_issue_codes: tuple[str, ...]
    owner_review_tasks: tuple[str, ...]
    state: str
    actual_broker_outcome_verified: bool
    numeric_return_estimated: bool
    training_feedback_applied: bool
    effective_policy_mutated: bool
    risk_limits_widened: bool
    guardrails_relaxed: bool
    owner_mode_changed: bool
    simulation_promoted_to_live: bool
    broker_submission: bool
    capital_movement: bool
    integrity_hash: str


def _material(item: ReviewLearning) -> dict[str, object]:
    return {
        k: getattr(item, k) for k in ReviewLearning.__dataclass_fields__
        if k not in ("learning_id", "integrity_hash")
    }


def _build(
    review: OwnerReviewRecord, recommendation: RecommendationReview,
    safety: SafetyReview, strategy: StrategyReview, *,
    portfolio: PortfolioComparison, harness: MultiSimulationHarness,
    sources: tuple[PositionSnapshot, ...], candidates: tuple[StrategyCandidate, ...],
    market_time: CanonicalMarketTimeReceipt, mode_state: dict[str, object],
    signals: SafetySignals | None = None, intent: dict[str, object] | None = None,
    context: dict[str, object] | None = None,
    decision: OwnerReviewDecision | None = None, issues: tuple[ReviewIssue, ...] = (),
) -> ReviewLearning:
    if not verify_owner_review(
        review, recommendation, safety, strategy,
        portfolio=portfolio, harness=harness, sources=sources,
        candidates=candidates, market_time=market_time, mode_state=mode_state,
        signals=signals, intent=intent, context=context, decision=decision, issues=issues,
    ):
        raise ValueError("learning requires verified OBREV source lineage")
    tasks = {ISSUE_TASKS[x.issue_code] for x in review.issues}
    if review.decision is not None:
        tasks.add(DECISION_TASKS[review.decision.disposition])
    if recommendation.state == "BLOCKED":
        tasks.add("RETAIN_CANONICAL_SAFETY_BLOCK")
    elif recommendation.state == "EVIDENCE_PENDING":
        tasks.add("RESOLVE_CANONICAL_SAFETY_EVIDENCE")
    # No actual institution-authenticated outcome is present in OBREV001–005.
    # Review conclusions are never treated as realized P&L or training reward.
    if review.issues:
        state = "ADVERSE_SOURCE_REVIEW_REQUIRED"
    elif tasks:
        state = "REVIEW_FEEDBACK_ONLY"
    else:
        state = "INSUFFICIENT_OUTCOME_EVIDENCE"
    provisional = ReviewLearning(
        learning_id="PENDING", authority=SCHEMA_VERSION,
        account_key=review.account_key, owner_review_id=review.record_id,
        owner_review_hash=review.integrity_hash,
        recommendation_id=recommendation.recommendation_id,
        recommendation_hash=recommendation.integrity_hash,
        source_issue_ids=tuple(x.issue_id for x in review.issues),
        source_issue_codes=tuple(x.issue_code for x in review.issues),
        owner_review_tasks=tuple(sorted(tasks)), state=state,
        actual_broker_outcome_verified=False, numeric_return_estimated=False,
        training_feedback_applied=False, effective_policy_mutated=False,
        risk_limits_widened=False, guardrails_relaxed=False,
        owner_mode_changed=False, simulation_promoted_to_live=False,
        broker_submission=False, capital_movement=False,
        integrity_hash="PENDING",
    )
    digest = _hash(_material(provisional))
    return replace(provisional, learning_id="OBLEARN-" + digest[:24], integrity_hash=digest)


def verify_review_learning(
    value: ReviewLearning, review: OwnerReviewRecord,
    recommendation: RecommendationReview, safety: SafetyReview, strategy: StrategyReview, *,
    portfolio: PortfolioComparison, harness: MultiSimulationHarness,
    sources: tuple[PositionSnapshot, ...], candidates: tuple[StrategyCandidate, ...],
    market_time: CanonicalMarketTimeReceipt, mode_state: dict[str, object],
    signals: SafetySignals | None = None, intent: dict[str, object] | None = None,
    context: dict[str, object] | None = None,
    decision: OwnerReviewDecision | None = None, issues: tuple[ReviewIssue, ...] = (),
) -> bool:
    if not isinstance(value, ReviewLearning) or value.authority != SCHEMA_VERSION:
        return False
    if any(getattr(value, key) is not False for key in (
        "actual_broker_outcome_verified", "numeric_return_estimated",
        "training_feedback_applied", "effective_policy_mutated", "risk_limits_widened",
        "guardrails_relaxed", "owner_mode_changed", "simulation_promoted_to_live",
        "broker_submission", "capital_movement",
    )):
        return False
    try:
        return value == _build(
            review, recommendation, safety, strategy, portfolio=portfolio,
            harness=harness, sources=sources, candidates=candidates,
            market_time=market_time, mode_state=mode_state, signals=signals,
            intent=intent, context=context, decision=decision, issues=issues,
        )
    except (ValueError, TypeError, AttributeError, KeyError):
        return False


def build_review_learning(
    review: OwnerReviewRecord, recommendation: RecommendationReview,
    safety: SafetyReview, strategy: StrategyReview, *,
    portfolio: PortfolioComparison, harness: MultiSimulationHarness,
    sources: tuple[PositionSnapshot, ...], candidates: tuple[StrategyCandidate, ...],
    market_time: CanonicalMarketTimeReceipt, mode_state: dict[str, object],
    signals: SafetySignals | None = None, intent: dict[str, object] | None = None,
    context: dict[str, object] | None = None,
    decision: OwnerReviewDecision | None = None, issues: tuple[ReviewIssue, ...] = (),
) -> ReviewLearning:
    value = _build(
        review, recommendation, safety, strategy, portfolio=portfolio,
        harness=harness, sources=sources, candidates=candidates,
        market_time=market_time, mode_state=mode_state, signals=signals,
        intent=intent, context=context, decision=decision, issues=issues,
    )
    if not verify_review_learning(
        value, review, recommendation, safety, strategy, portfolio=portfolio,
        harness=harness, sources=sources, candidates=candidates,
        market_time=market_time, mode_state=mode_state, signals=signals,
        intent=intent, context=context, decision=decision, issues=issues,
    ):
        raise ValueError("learning review source verification failed")
    return value


def learning_review_contract() -> dict[str, object]:
    return {
        "authority": SCHEMA_VERSION,
        "upstream_authority": "OB_OWNER_REVIEW_EVIDENCE_V1",
        "review_tasks_only": True, "actual_broker_outcome_available": False,
        "review_notes_are_not_reward_labels": True,
        "numeric_return_estimated": False, "new_prediction_engine": False,
        "autonomous_training": False, "effective_policy_mutation": False,
        "risk_limit_widening": False, "guardrail_relaxation": False,
        "simulation_promotion_to_live": False, "broker_submission": False,
        "capital_movement": False, "direct_buybox_access": False,
        "teller_owns_acquisition_readiness": True,
        "manual_live_unlock": False, "hybrid_unlock": False, "automated_unlock": False,
    }
