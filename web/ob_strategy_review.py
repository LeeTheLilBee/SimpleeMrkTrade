"""OBSTRAT001–005: explicit source-backed strategy evidence, not auto selection.

Uses the accepted OBPORT comparison and pre-existing OBSIM market-frame
identities. A candidate and owner-selected *review* status do not constitute
trade intent, capital admission, broker order, or permission for a mode.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict, replace
from hashlib import sha256
import json

from web.ob_multi_simulation_harness import (
    MultiSimulationHarness, SimulationLane,
)
from web.ob_position_truth import PositionSnapshot
from web.ob_portfolio_view import PortfolioComparison, verify_portfolio_comparison

SCHEMA_VERSION = "OB_STRATEGY_REVIEW_V1"
LANES = tuple(SimulationLane)


def _text(value: str, name: str) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise ValueError(name + " must be explicit and nonblank")
    return value


def _digest(value: object) -> str:
    return sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    ).encode()).hexdigest()


@dataclass(frozen=True)
class StrategyCandidate:
    candidate_id: str
    lane: str
    market_frame_id: str
    symbol: str
    instrument_kind: str
    contract_id: str | None
    strategy_label: str
    source_evidence_refs: tuple[str, ...]
    owner_declared_stock_fallback_reason: str | None = None


@dataclass(frozen=True)
class StrategyReview:
    review_id: str
    authority: str
    account_key: str
    portfolio_comparison_id: str
    portfolio_comparison_hash: str
    harness_id: str
    candidates: tuple[StrategyCandidate, ...]
    owner_selected_candidate_id: str | None
    owner_confirmed_selection_for_review: bool
    option_first_stock_fallback_is_explicit: bool
    evidence_is_source_asserted_not_broker_verified: bool
    ranking_generated: bool
    winner_selected_by_system: bool
    trade_intent_created: bool
    capital_admission_granted: bool
    broker_submission: bool
    capital_movement: bool
    mode_unlock: bool
    integrity_hash: str


def _material(item: StrategyReview) -> dict[str, object]:
    return {
        key: [asdict(v) for v in item.candidates] if key == "candidates" else getattr(item, key)
        for key in StrategyReview.__dataclass_fields__
        if key not in ("review_id", "integrity_hash")
    }


def _build(
    portfolio: PortfolioComparison, *, harness: MultiSimulationHarness,
    sources: tuple[PositionSnapshot, ...], candidates: tuple[StrategyCandidate, ...],
    owner_selected_candidate_id: str | None, owner_confirmed_selection_for_review: bool,
) -> StrategyReview:
    if not verify_portfolio_comparison(portfolio, harness=harness, sources=sources):
        raise ValueError("OBSTRAT requires verified OBPORT lineage")
    if not isinstance(candidates, tuple) or not candidates:
        raise ValueError("strategy review requires at least one explicit candidate")
    if type(owner_confirmed_selection_for_review) is not bool:
        raise ValueError("owner selection review confirmation must be boolean")
    if (owner_selected_candidate_id is None) != (owner_confirmed_selection_for_review is False):
        raise ValueError("owner selection for review requires explicit matching confirmation")
    frames = {f.frame_id: f for f in harness.market_frames}
    if len(frames) != len(harness.market_frames):
        raise ValueError("duplicate frame IDs in portfolio history")
    IDs = set()
    for candidate in candidates:
        if not isinstance(candidate, StrategyCandidate):
            raise ValueError("candidate must use explicit canonical packet")
        for field in ("candidate_id", "lane", "market_frame_id", "symbol",
                      "instrument_kind", "strategy_label"):
            _text(getattr(candidate, field), field)
        if candidate.candidate_id in IDs:
            raise ValueError("candidate IDs must be unique")
        IDs.add(candidate.candidate_id)
        if candidate.lane not in {lane.value for lane in LANES}:
            raise ValueError("candidate lane must be one of the isolated OBPORT lanes")
        if candidate.instrument_kind not in ("OPTION", "STOCK"):
            raise ValueError("only canonical STOCK/OPTION instruments allowed")
        if not isinstance(candidate.source_evidence_refs, tuple) or not candidate.source_evidence_refs:
            raise ValueError("strategy evidence references cannot be missing")
        for ref in candidate.source_evidence_refs:
            _text(ref, "source evidence reference")
        frame = frames.get(candidate.market_frame_id)
        if frame is None or (
            frame.instrument.symbol, frame.instrument.instrument_kind,
            frame.instrument.contract_id,
        ) != (
            candidate.symbol, candidate.instrument_kind, candidate.contract_id,
        ):
            raise ValueError("strategy candidate must match an explicit canonical market frame")
        if candidate.instrument_kind == "OPTION":
            if not candidate.contract_id or candidate.owner_declared_stock_fallback_reason is not None:
                raise ValueError("OPTION candidate requires exact contract and no stock fallback")
        elif (
            candidate.contract_id is not None or
            not isinstance(candidate.owner_declared_stock_fallback_reason, str) or
            not candidate.owner_declared_stock_fallback_reason.strip()
        ):
            raise ValueError("STOCK fallback needs owner-declared reason and no option contract")
    if owner_selected_candidate_id is not None and owner_selected_candidate_id not in IDs:
        raise ValueError("owner selected candidate not in explicit reviewed set")
    provisional = StrategyReview(
        review_id="PENDING", authority=SCHEMA_VERSION, account_key=portfolio.account_key,
        portfolio_comparison_id=portfolio.comparison_id,
        portfolio_comparison_hash=portfolio.integrity_hash,
        harness_id=harness.harness_id, candidates=candidates,
        owner_selected_candidate_id=owner_selected_candidate_id,
        owner_confirmed_selection_for_review=owner_confirmed_selection_for_review,
        option_first_stock_fallback_is_explicit=True,
        evidence_is_source_asserted_not_broker_verified=True,
        ranking_generated=False, winner_selected_by_system=False,
        trade_intent_created=False, capital_admission_granted=False,
        broker_submission=False, capital_movement=False, mode_unlock=False,
        integrity_hash="PENDING",
    )
    digest = _digest(_material(provisional))
    return replace(provisional, review_id="OBSTRAT-" + digest[:24], integrity_hash=digest)


def verify_strategy_review(
    value: StrategyReview, *, portfolio: PortfolioComparison, harness: MultiSimulationHarness,
    sources: tuple[PositionSnapshot, ...], candidates: tuple[StrategyCandidate, ...],
    owner_selected_candidate_id: str | None = None,
    owner_confirmed_selection_for_review: bool = False,
) -> bool:
    if not isinstance(value, StrategyReview) or value.authority != SCHEMA_VERSION:
        return False
    if any(getattr(value, name) is not False for name in (
        "ranking_generated", "winner_selected_by_system", "trade_intent_created",
        "capital_admission_granted", "broker_submission", "capital_movement", "mode_unlock",
    )):
        return False
    if value.option_first_stock_fallback_is_explicit is not True or value.evidence_is_source_asserted_not_broker_verified is not True:
        return False
    try:
        return value == _build(
            portfolio, harness=harness, sources=sources, candidates=candidates,
            owner_selected_candidate_id=owner_selected_candidate_id,
            owner_confirmed_selection_for_review=owner_confirmed_selection_for_review,
        )
    except (ValueError, TypeError, AttributeError, KeyError):
        return False


def build_strategy_review(
    portfolio: PortfolioComparison, *, harness: MultiSimulationHarness,
    sources: tuple[PositionSnapshot, ...], candidates: tuple[StrategyCandidate, ...],
    owner_selected_candidate_id: str | None = None,
    owner_confirmed_selection_for_review: bool = False,
) -> StrategyReview:
    result = _build(
        portfolio, harness=harness, sources=sources, candidates=candidates,
        owner_selected_candidate_id=owner_selected_candidate_id,
        owner_confirmed_selection_for_review=owner_confirmed_selection_for_review,
    )
    if not verify_strategy_review(
        result, portfolio=portfolio, harness=harness, sources=sources,
        candidates=candidates, owner_selected_candidate_id=owner_selected_candidate_id,
        owner_confirmed_selection_for_review=owner_confirmed_selection_for_review,
    ):
        raise ValueError("strategy review failed verification")
    return result


def strategy_review_contract() -> dict[str, object]:
    return {
        "authority": SCHEMA_VERSION, "source_authority": "OB_PORTFOLIO_VIEW_V1",
        "candidate_market_frame_evidence_required": True,
        "explicit_owner_choice_for_review_only": True,
        "option_contract_must_be_explicit": True,
        "stock_fallback_requires_owner_declared_reason": True,
        "source_refs_do_not_prove_external_authentication": True,
        "ranking_generated": False, "automatic_selection": False,
        "trade_intent_created": False, "capital_admission_granted": False,
        "broker_submission": False, "capital_movement": False,
        "direct_buybox_access": False, "teller_owns_acquisition_readiness": True,
        "manual_live_unlock": False, "hybrid_unlock": False, "automated_unlock": False,
    }
