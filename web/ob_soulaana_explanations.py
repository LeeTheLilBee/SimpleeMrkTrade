"""OBSOUL001–005: Soulaana explains canonical receipts, never authors their truth.

Every explanation is recomputed from the full verified recommendation/safety
lineage, with optional full OBGUARD lineage. Cards are deterministic translations
of observed source codes and source-only historical simulation candidate labels.
They are NOT model-generated facts, an order, a safety override or a prediction.
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
from web.ob_recommendation_review import (
    RecommendationReview, verify_recommendation_review,
)
from web.ob_adverse_guard_review import GuardEvidence, GuardReview, verify_guard_review

SCHEMA_VERSION = "OB_SOULAANA_EXPLANATION_V1"
STATE_TEXT = {
    "BLOCKED": "Canonical safety evidence blocks this candidate from owner review.",
    "EVIDENCE_PENDING": "More canonical evidence is needed before owner review.",
    "OWNER_REVIEW_READY": "The canonical receipt permits owner review only; it does not authorize a trade.",
}
REASON_TEXT = {
    "CANONICAL_OWNER_FIT_NOT_YET": "The existing owner-fit authority recorded a hard stop.",
    "CANONICAL_OWNER_FIT_WATCH": "The existing owner-fit authority recorded watch conditions.",
    "OWNER_FIT_SOURCE_NOT_PROVIDED": "The owner-fit source evidence has not been provided.",
    "SAFETY_SOURCE_SIGNALS_MISSING": "The independent safety-source signal packet is missing.",
    "SAFETY_SOURCE_SIGNAL_UNKNOWN": "At least one safety-source signal remains unknown.",
    "SAFETY_SOURCE_STALE": "The safety-source observation is stale.",
    "NOT_RESOLVED_REGULAR_MARKET_TIME": "Canonical market time is not a resolved regular session.",
    "NO_EXPLICIT_OWNER_SELECTED_CANDIDATE": "No candidate was explicitly selected by the owner for review.",
    "DANGER:OVERREACH": "The source asserted an overreach concern.",
    "DANGER:NEGATIVE_DIVE": "The source asserted a Negative Dive concern.",
    "DANGER:OVERTIME": "The source asserted an Overtime concern.",
    "DANGER:KILL_SWITCH_ENGAGED": "The source asserted that a kill switch is engaged.",
    "DANGER:SOURCE_CONFLICT": "The source asserted conflicting evidence.",
}
# Unmapped reason codes retain the exact code. No hallucinated causal interpretation.


def _digest(value: object) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()


@dataclass(frozen=True)
class ExplanationCard:
    kind: str
    source_code: str
    text: str
    source_authority: str
    source_receipt_id: str
    source_integrity_hash: str
    severity: str
    observed_fact_only: bool


@dataclass(frozen=True)
class SoulaanaExplanation:
    explanation_id: str
    authority: str
    account_key: str
    recommendation_id: str
    recommendation_hash: str
    safety_review_id: str
    safety_review_hash: str
    guard_id: str | None
    guard_hash: str | None
    source_state: str
    cards: tuple[ExplanationCard, ...]
    selected_candidate_id: str | None
    source_is_historical_simulation: bool
    source_claims_broker_authenticated: bool
    market_return_predicted: bool
    safety_decision_overridden: bool
    trade_intent_created: bool
    trading_mode_changed: bool
    broker_submission: bool
    capital_movement: bool
    direct_buybox_access: bool
    integrity_hash: str


def _material(value: SoulaanaExplanation) -> dict[str, object]:
    return {
        key: [asdict(c) for c in value.cards] if key == "cards" else getattr(value, key)
        for key in SoulaanaExplanation.__dataclass_fields__
        if key not in ("explanation_id", "integrity_hash")
    }


def _build(
    recommendation: RecommendationReview, safety: SafetyReview,
    strategy: StrategyReview, *, portfolio: PortfolioComparison,
    harness: MultiSimulationHarness, sources: tuple[PositionSnapshot, ...],
    candidates: tuple[StrategyCandidate, ...], market_time: CanonicalMarketTimeReceipt,
    mode_state: dict[str, object], signals: SafetySignals | None = None,
    intent: dict[str, object] | None = None, context: dict[str, object] | None = None,
    guard: GuardReview | None = None, guard_evidence: tuple[GuardEvidence, ...] | None = None,
) -> SoulaanaExplanation:
    if not verify_recommendation_review(
        recommendation, safety, strategy, portfolio=portfolio, harness=harness,
        sources=sources, candidates=candidates, market_time=market_time,
        mode_state=mode_state, signals=signals, intent=intent, context=context,
    ):
        raise ValueError("Soulaana requires fully verified OBREC/OBSAFE source lineage")
    if (guard is None) != (guard_evidence is None):
        raise ValueError("optional guard requires both receipt and full source evidence")
    if guard is not None:
        if (
            guard.account_key != recommendation.account_key or
            not verify_guard_review(guard, guard_evidence) or
            not any(
                item.recommendation.recommendation_id == recommendation.recommendation_id
                and item.recommendation.integrity_hash == recommendation.integrity_hash
                for item in guard_evidence
            )
        ):
            raise ValueError("guard context must reverify and contain this recommendation")
    cards = [ExplanationCard(
        kind="RECOMMENDATION_STATE", source_code=recommendation.state,
        text=STATE_TEXT[recommendation.state],
        source_authority=recommendation.authority,
        source_receipt_id=recommendation.recommendation_id,
        source_integrity_hash=recommendation.integrity_hash,
        severity=("BLOCK" if recommendation.state == "BLOCKED" else
                  "HOLD" if recommendation.state == "EVIDENCE_PENDING" else "REVIEW"),
        observed_fact_only=True,
    )]
    for code in recommendation.reason_codes:
        cards.append(ExplanationCard(
            kind="CANONICAL_REASON", source_code=code,
            text=REASON_TEXT.get(code, "Source recorded reason code: " + code),
            source_authority=safety.authority,
            source_receipt_id=safety.review_id, source_integrity_hash=safety.integrity_hash,
            severity="BLOCK" if code.startswith("DANGER:") else "SOURCE_CONTEXT",
            observed_fact_only=True,
        ))
    for candidate in recommendation.candidate_cards:
        if candidate.is_explicit_owner_review_selection:
            text = (
                "Owner selected the exact source-backed " + candidate.instrument_kind +
                " candidate for review; historical simulation evidence only, not a live quote or order."
            )
            cards.append(ExplanationCard(
                kind="OWNER_SELECTED_CANDIDATE", source_code=candidate.candidate_id,
                text=text, source_authority=strategy.authority,
                source_receipt_id=strategy.review_id,
                source_integrity_hash=strategy.integrity_hash,
                severity="SOURCE_CONTEXT", observed_fact_only=True,
            ))
    if guard is not None:
        for pattern in guard.source_assertion_patterns:
            cards.append(ExplanationCard(
                kind="SOURCE_GUARD_PATTERN", source_code=pattern.issue_code,
                text=("Repeated distinct source assertions warrant owner inspection; "
                      "they are not independently authenticated market incidents."
                      if pattern.repeated_source_assertion else
                      "A source-asserted adverse issue is recorded; external authenticity is not established."),
                source_authority=guard.authority, source_receipt_id=guard.guard_id,
                source_integrity_hash=guard.integrity_hash,
                severity="OWNER_ATTENTION", observed_fact_only=True,
            ))
    provisional = SoulaanaExplanation(
        explanation_id="PENDING", authority=SCHEMA_VERSION,
        account_key=recommendation.account_key,
        recommendation_id=recommendation.recommendation_id,
        recommendation_hash=recommendation.integrity_hash,
        safety_review_id=safety.review_id, safety_review_hash=safety.integrity_hash,
        guard_id=guard.guard_id if guard else None,
        guard_hash=guard.integrity_hash if guard else None,
        source_state=recommendation.state, cards=tuple(cards),
        selected_candidate_id=recommendation.selected_candidate_id,
        source_is_historical_simulation=True,
        source_claims_broker_authenticated=False, market_return_predicted=False,
        safety_decision_overridden=False, trade_intent_created=False,
        trading_mode_changed=False, broker_submission=False, capital_movement=False,
        direct_buybox_access=False, integrity_hash="PENDING",
    )
    digest = _digest(_material(provisional))
    return replace(provisional, explanation_id="OBSOUL-" + digest[:24], integrity_hash=digest)


def verify_soulaana_explanation(
    value: SoulaanaExplanation, recommendation: RecommendationReview,
    safety: SafetyReview, strategy: StrategyReview, *,
    portfolio: PortfolioComparison, harness: MultiSimulationHarness,
    sources: tuple[PositionSnapshot, ...], candidates: tuple[StrategyCandidate, ...],
    market_time: CanonicalMarketTimeReceipt, mode_state: dict[str, object],
    signals: SafetySignals | None = None, intent: dict[str, object] | None = None,
    context: dict[str, object] | None = None, guard: GuardReview | None = None,
    guard_evidence: tuple[GuardEvidence, ...] | None = None,
) -> bool:
    if not isinstance(value, SoulaanaExplanation) or value.authority != SCHEMA_VERSION:
        return False
    if any(getattr(value, field) is not False for field in (
        "source_claims_broker_authenticated", "market_return_predicted",
        "safety_decision_overridden", "trade_intent_created", "trading_mode_changed",
        "broker_submission", "capital_movement", "direct_buybox_access",
    )):
        return False
    try:
        return value == _build(
            recommendation, safety, strategy, portfolio=portfolio, harness=harness,
            sources=sources, candidates=candidates, market_time=market_time,
            mode_state=mode_state, signals=signals, intent=intent, context=context,
            guard=guard, guard_evidence=guard_evidence,
        )
    except (ValueError, TypeError, AttributeError, KeyError):
        return False


def build_soulaana_explanation(
    recommendation: RecommendationReview, safety: SafetyReview,
    strategy: StrategyReview, *, portfolio: PortfolioComparison,
    harness: MultiSimulationHarness, sources: tuple[PositionSnapshot, ...],
    candidates: tuple[StrategyCandidate, ...], market_time: CanonicalMarketTimeReceipt,
    mode_state: dict[str, object], signals: SafetySignals | None = None,
    intent: dict[str, object] | None = None, context: dict[str, object] | None = None,
    guard: GuardReview | None = None, guard_evidence: tuple[GuardEvidence, ...] | None = None,
) -> SoulaanaExplanation:
    result = _build(
        recommendation, safety, strategy, portfolio=portfolio, harness=harness,
        sources=sources, candidates=candidates, market_time=market_time,
        mode_state=mode_state, signals=signals, intent=intent, context=context,
        guard=guard, guard_evidence=guard_evidence,
    )
    if not verify_soulaana_explanation(
        result, recommendation, safety, strategy, portfolio=portfolio,
        harness=harness, sources=sources, candidates=candidates, market_time=market_time,
        mode_state=mode_state, signals=signals, intent=intent, context=context,
        guard=guard, guard_evidence=guard_evidence,
    ):
        raise ValueError("Soulaana source explanation failed independent verification")
    return result


def soulaana_explanation_reference(
    value: SoulaanaExplanation, recommendation: RecommendationReview,
    safety: SafetyReview, strategy: StrategyReview, *,
    portfolio: PortfolioComparison, harness: MultiSimulationHarness,
    sources: tuple[PositionSnapshot, ...], candidates: tuple[StrategyCandidate, ...],
    market_time: CanonicalMarketTimeReceipt, mode_state: dict[str, object],
    signals: SafetySignals | None = None, intent: dict[str, object] | None = None,
    context: dict[str, object] | None = None, guard: GuardReview | None = None,
    guard_evidence: tuple[GuardEvidence, ...] | None = None,
) -> dict[str, object]:
    if not verify_soulaana_explanation(
        value, recommendation, safety, strategy, portfolio=portfolio, harness=harness,
        sources=sources, candidates=candidates, market_time=market_time,
        mode_state=mode_state, signals=signals, intent=intent, context=context,
        guard=guard, guard_evidence=guard_evidence,
    ):
        raise ValueError("Soulaana reference requires complete verified source lineage")
    return {
        "authority": SCHEMA_VERSION, "explanation_id": value.explanation_id,
        "integrity_hash": value.integrity_hash, "account_key": value.account_key,
        "source_state": value.source_state,
        "source_receipt_ids": [value.recommendation_id, value.safety_review_id] +
        ([value.guard_id] if value.guard_id else []),
        "amounts_exposed": False, "broker_submission": False,
        "capital_movement": False, "tower_authorization_required": True,
    }


def soulaana_contract() -> dict[str, object]:
    return {
        "authority": SCHEMA_VERSION, "upstream_recommendation": "OB_RECOMMENDATION_REVIEW_V1",
        "upstream_guard": "OB_ADVERSE_GUARD_REVIEW_V1",
        "full_source_lineage_reverified": True,
        "unknown_reason_codes_preserved_not_invented": True,
        "source_assertion_not_market_authentication": True,
        "canonical_state_not_overridden": True, "source_only_explanation_cards": True,
        "no_new_market_or_financial_truth": True,
        "numeric_return_prediction": False, "execution_authority": False,
        "capital_movement": False, "broker_submission": False,
        "manual_live_unlock": False, "hybrid_unlock": False, "automated_unlock": False,
        "direct_buybox_access": False, "teller_owns_acquisition_readiness": True,
    }
