"""OBREC001–005: owner-facing recommendation proof, never execution authority.

The only entry is a fully revalidated OBSAFE receipt and canonical strategy
lineage. A strategy chosen for review is not an autonomous selection or order.
No new expected-return, fill, policy, ranking, capital or broker engine.
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
from web.ob_safety_review import SafetyReview, SafetySignals, verify_safety_review

SCHEMA_VERSION = "OB_RECOMMENDATION_REVIEW_V1"
RECOMMENDATION_STATES = (
    "BLOCKED", "EVIDENCE_PENDING", "OWNER_REVIEW_READY",
)


def _digest(value: object) -> str:
    return sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    ).encode()).hexdigest()


@dataclass(frozen=True)
class CandidateReviewCard:
    candidate_id: str
    lane: str
    symbol: str
    instrument_kind: str
    contract_id: str | None
    strategy_label: str
    market_frame_id: str
    source_evidence_refs: tuple[str, ...]
    owner_declared_stock_fallback_reason: str | None
    is_explicit_owner_review_selection: bool
    source_truth: str


@dataclass(frozen=True)
class RecommendationReview:
    recommendation_id: str
    authority: str
    account_key: str
    strategy_review_id: str
    strategy_review_hash: str
    safety_review_id: str
    safety_review_hash: str
    selected_candidate_id: str | None
    state: str
    reason_codes: tuple[str, ...]
    explanation_code: str
    candidate_cards: tuple[CandidateReviewCard, ...]
    owner_review_ready: bool
    source_authenticated_as_broker: bool
    ranked_by_system: bool
    auto_selected_contract: bool
    expected_return_promised: bool
    executable_trade_intent: bool
    trade_execution_permission: bool
    broker_submission: bool
    capital_movement: bool
    mode_change: bool
    integrity_hash: str


def _material(value: RecommendationReview) -> dict[str, object]:
    return {
        name: ([asdict(card) for card in value.candidate_cards]
               if name == "candidate_cards" else getattr(value, name))
        for name in RecommendationReview.__dataclass_fields__
        if name not in ("recommendation_id", "integrity_hash")
    }


def _build(
    safety: SafetyReview, strategy: StrategyReview, *, portfolio: PortfolioComparison,
    harness: MultiSimulationHarness, sources: tuple[PositionSnapshot, ...],
    candidates: tuple[StrategyCandidate, ...],
    market_time: CanonicalMarketTimeReceipt,
    mode_state: dict[str, object],
    signals: SafetySignals | None = None,
    intent: dict[str, object] | None = None,
    context: dict[str, object] | None = None,
) -> RecommendationReview:
    if not verify_safety_review(
        safety, strategy, portfolio=portfolio, harness=harness,
        sources=sources, candidates=candidates, market_time=market_time,
        mode_state=mode_state, signals=signals, intent=intent, context=context,
    ):
        raise ValueError("OBREC requires fully verified canonical OBSAFE lineage")
    if safety.state == "BLOCK":
        state, explanation = "BLOCKED", "CANONICAL_SAFETY_DENIAL"
    elif safety.state == "HOLD":
        state, explanation = "EVIDENCE_PENDING", "CANONICAL_SAFETY_OR_EVIDENCE_HOLD"
    elif safety.state == "REVIEW_ONLY":
        state, explanation = "OWNER_REVIEW_READY", "EXPLICIT_OWNER_REVIEW_NO_EXECUTION"
    else:
        raise ValueError("unknown canonical safety review state")
    selected = strategy.owner_selected_candidate_id
    if state == "OWNER_REVIEW_READY" and selected is None:
        raise ValueError("owner-review-ready requires exact owner-selected source candidate")
    cards = tuple(CandidateReviewCard(
        candidate_id=c.candidate_id, lane=c.lane, symbol=c.symbol,
        instrument_kind=c.instrument_kind, contract_id=c.contract_id,
        strategy_label=c.strategy_label, market_frame_id=c.market_frame_id,
        source_evidence_refs=c.source_evidence_refs,
        owner_declared_stock_fallback_reason=c.owner_declared_stock_fallback_reason,
        is_explicit_owner_review_selection=c.candidate_id == selected,
        source_truth="HISTORICAL_SIMULATION_SOURCE_NOT_BROKER",
    ) for c in candidates)
    provisional = RecommendationReview(
        recommendation_id="PENDING", authority=SCHEMA_VERSION,
        account_key=safety.account_key, strategy_review_id=strategy.review_id,
        strategy_review_hash=strategy.integrity_hash,
        safety_review_id=safety.review_id, safety_review_hash=safety.integrity_hash,
        selected_candidate_id=selected, state=state, reason_codes=safety.reasons,
        explanation_code=explanation, candidate_cards=cards,
        owner_review_ready=state == "OWNER_REVIEW_READY",
        source_authenticated_as_broker=False, ranked_by_system=False,
        auto_selected_contract=False, expected_return_promised=False,
        executable_trade_intent=False, trade_execution_permission=False,
        broker_submission=False, capital_movement=False, mode_change=False,
        integrity_hash="PENDING",
    )
    digest = _digest(_material(provisional))
    return replace(provisional, recommendation_id="OBREC-" + digest[:24], integrity_hash=digest)


def verify_recommendation_review(
    value: RecommendationReview, safety: SafetyReview, strategy: StrategyReview, *,
    portfolio: PortfolioComparison, harness: MultiSimulationHarness,
    sources: tuple[PositionSnapshot, ...], candidates: tuple[StrategyCandidate, ...],
    market_time: CanonicalMarketTimeReceipt, mode_state: dict[str, object],
    signals: SafetySignals | None = None,
    intent: dict[str, object] | None = None,
    context: dict[str, object] | None = None,
) -> bool:
    if not isinstance(value, RecommendationReview) or value.authority != SCHEMA_VERSION:
        return False
    if any(getattr(value, flag) is not False for flag in (
        "source_authenticated_as_broker", "ranked_by_system", "auto_selected_contract",
        "expected_return_promised", "executable_trade_intent", "trade_execution_permission",
        "broker_submission", "capital_movement", "mode_change",
    )):
        return False
    try:
        return value == _build(
            safety, strategy, portfolio=portfolio, harness=harness, sources=sources,
            candidates=candidates, market_time=market_time, mode_state=mode_state,
            signals=signals, intent=intent, context=context,
        )
    except (ValueError, TypeError, AttributeError, KeyError):
        return False


def build_recommendation_review(
    safety: SafetyReview, strategy: StrategyReview, *, portfolio: PortfolioComparison,
    harness: MultiSimulationHarness, sources: tuple[PositionSnapshot, ...],
    candidates: tuple[StrategyCandidate, ...], market_time: CanonicalMarketTimeReceipt,
    mode_state: dict[str, object], signals: SafetySignals | None = None,
    intent: dict[str, object] | None = None, context: dict[str, object] | None = None,
) -> RecommendationReview:
    result = _build(
        safety, strategy, portfolio=portfolio, harness=harness, sources=sources,
        candidates=candidates, market_time=market_time, mode_state=mode_state,
        signals=signals, intent=intent, context=context,
    )
    if not verify_recommendation_review(
        result, safety, strategy, portfolio=portfolio, harness=harness,
        sources=sources, candidates=candidates, market_time=market_time,
        mode_state=mode_state, signals=signals, intent=intent, context=context,
    ):
        raise ValueError("recommendation review failed source-bound verification")
    return result


def recommendation_reference(
    value: RecommendationReview, safety: SafetyReview, strategy: StrategyReview, *,
    portfolio: PortfolioComparison, harness: MultiSimulationHarness,
    sources: tuple[PositionSnapshot, ...], candidates: tuple[StrategyCandidate, ...],
    market_time: CanonicalMarketTimeReceipt, mode_state: dict[str, object],
    signals: SafetySignals | None = None,
    intent: dict[str, object] | None = None, context: dict[str, object] | None = None,
) -> dict[str, object]:
    if not verify_recommendation_review(
        value, safety, strategy, portfolio=portfolio, harness=harness,
        sources=sources, candidates=candidates, market_time=market_time,
        mode_state=mode_state, signals=signals, intent=intent, context=context,
    ):
        raise ValueError("recommendation reference requires full verified source lineage")
    return {
        "authority": SCHEMA_VERSION, "recommendation_id": value.recommendation_id,
        "integrity_hash": value.integrity_hash, "account_key": value.account_key,
        "safety_review_id": value.safety_review_id, "state": value.state,
        "reason_codes": list(value.reason_codes),
        "amounts_exposed": False, "broker_submission": False,
        "trade_execution_permission": False, "capital_movement": False,
        "tower_authorization_required": True,
    }


def recommendation_contract() -> dict[str, object]:
    return {
        "authority": SCHEMA_VERSION, "upstream_safety": "OB_SAFETY_REVIEW_V1",
        "upstream_strategy": "OB_STRATEGY_REVIEW_V1",
        "source_lineage_reverified": True, "status_not_execution_grant": True,
        "states": list(RECOMMENDATION_STATES),
        "automatic_candidate_ranking": False, "automatic_contract_selection": False,
        "no_new_prediction_or_expected_return_engine": True,
        "manual_live_unlock": False, "hybrid_unlock": False,
        "automated_unlock": False, "broker_submission": False,
        "capital_movement": False, "mode_change": False,
        "direct_buybox_access": False, "teller_owns_acquisition_readiness": True,
    }
