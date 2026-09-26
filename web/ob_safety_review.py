"""OBSAFE001–005: fail-closed, read-only overreach/danger review.

This is an evidence join, not a second risk/policy engine. Owner-fit recomputes
through canonical Effective Policy and the bound canonical Operating Mode.
Source-reported danger may restrict but cannot grant broker or trade authority.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from hashlib import sha256
import json
import re

from web.ob_market_time_authority import (
    CanonicalMarketTimeReceipt, MarketTimeState,
    verify_canonical_market_time_receipt,
)
from web.ob_multi_simulation_harness import MultiSimulationHarness
from web.ob_operating_mode import validate_mode_state
from web.ob_owner_fit_eligibility import evaluate_owner_fit
from web.ob_portfolio_view import PortfolioComparison
from web.ob_position_truth import PositionSnapshot
from web.ob_strategy_review import (
    StrategyCandidate, StrategyReview, verify_strategy_review,
)

SCHEMA_VERSION = "OB_SAFETY_REVIEW_V1"
HASH = re.compile(r"[0-9a-f]{64}")
SOURCE_FLAGS = (
    "source_conflict", "source_stale", "overreach",
    "negative_dive", "overtime", "kill_switch_engaged",
)
HARD_STOPS = frozenset((
    "source_conflict", "overreach", "negative_dive",
    "overtime", "kill_switch_engaged",
))


def _digest(value: object) -> str:
    return sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    ).encode()).hexdigest()


@dataclass(frozen=True)
class SafetySignals:
    source_ref: str
    source_payload_hash: str
    source_revision: str
    source_conflict: bool | None = None
    source_stale: bool | None = None
    overreach: bool | None = None
    negative_dive: bool | None = None
    overtime: bool | None = None
    kill_switch_engaged: bool | None = None


@dataclass(frozen=True)
class SafetyReview:
    review_id: str
    authority: str
    account_key: str
    strategy_review_id: str
    strategy_review_hash: str
    candidate_id: str | None
    market_time_receipt_id: str
    market_time_hash: str
    mode_state_id: str
    mode_state_hash: str
    owner_fit_fingerprint: str | None
    effective_policy_fingerprint: str | None
    source_signals_hash: str | None
    state: str
    reasons: tuple[str, ...]
    source_claims_not_externally_authenticated: bool
    owner_review_allowed: bool
    order_authorized: bool
    execution_authorized: bool
    broker_submission: bool
    capital_movement: bool
    mode_changed: bool
    integrity_hash: str


def _material(value: SafetyReview) -> dict[str, object]:
    return {
        key: getattr(value, key) for key in SafetyReview.__dataclass_fields__
        if key not in ("review_id", "integrity_hash")
    }


def _signals(signals: SafetySignals | None) -> tuple[dict[str, bool | None] | None, str | None]:
    if signals is None:
        return None, None
    if not isinstance(signals, SafetySignals):
        raise ValueError("safety signals require canonical explicit source packet")
    if any(
        not isinstance(getattr(signals, key), str) or
        not getattr(signals, key) or getattr(signals, key).strip() != getattr(signals, key)
        for key in ("source_ref", "source_revision")
    ):
        raise ValueError("safety source revision/reference is required")
    if not isinstance(signals.source_payload_hash, str) or not HASH.fullmatch(signals.source_payload_hash):
        raise ValueError("safety source payload hash must be SHA-256")
    flags = {key: getattr(signals, key) for key in SOURCE_FLAGS}
    if any(value is not None and type(value) is not bool for value in flags.values()):
        raise ValueError("safety signal must be true/false/unknown")
    return flags, _digest(asdict(signals))


def _matching_research_contract(intent: dict[str, object], candidate: StrategyCandidate) -> bool:
    research = intent.get("options_research")
    if not isinstance(research, dict):
        return False
    for name in ("ranked_contracts", "research_contracts"):
        rows = research.get(name, [])
        if not isinstance(rows, list):
            continue
        for row in rows:
            if isinstance(row, dict) and row.get("contract_symbol") == candidate.contract_id:
                return row.get("symbol") == candidate.symbol
    return False


def _build(
    strategy: StrategyReview, *, portfolio: PortfolioComparison,
    harness: MultiSimulationHarness, sources: tuple[PositionSnapshot, ...],
    candidates: tuple[StrategyCandidate, ...], market_time: CanonicalMarketTimeReceipt,
    mode_state: dict[str, object], signals: SafetySignals | None = None,
    intent: dict[str, object] | None = None,
    context: dict[str, object] | None = None,
) -> SafetyReview:
    if not verify_strategy_review(
        strategy, portfolio=portfolio, harness=harness, sources=sources,
        candidates=candidates,
        owner_selected_candidate_id=strategy.owner_selected_candidate_id,
        owner_confirmed_selection_for_review=strategy.owner_confirmed_selection_for_review,
    ):
        raise ValueError("safety requires verified OBSTRAT source lineage")
    if not verify_canonical_market_time_receipt(market_time):
        raise ValueError("safety requires verified OBTIME receipt")
    mode = validate_mode_state(mode_state)
    if mode["account_key"] != strategy.account_key or strategy.account_key != harness.account_key:
        raise ValueError("safety account/mode source mismatch")
    flags, signals_hash = _signals(signals)
    selected = next(
        (x for x in candidates if x.candidate_id == strategy.owner_selected_candidate_id), None
    )
    reasons: set[str] = set()
    bucket = None
    fit_fingerprint = None
    policy_fingerprint = None
    if selected is None:
        reasons.add("NO_EXPLICIT_OWNER_SELECTED_CANDIDATE")
    else:
        frame = next(
            (f for f in harness.market_frames if f.frame_id == selected.market_frame_id), None
        )
        if frame is None:
            raise ValueError("selected strategy frame missing")
        frame_instant = datetime.fromisoformat(frame.observed_at.replace("Z", "+00:00"))
        if frame_instant.astimezone(timezone.utc) != market_time.observed_at_utc:
            raise ValueError("selected strategy and market-time receipts differ")
        if market_time.state is not MarketTimeState.RESOLVED or market_time.market_session.value != "REGULAR":
            reasons.add("NOT_RESOLVED_REGULAR_MARKET_TIME")
        if intent is None:
            reasons.add("OWNER_FIT_SOURCE_NOT_PROVIDED")
        else:
            if not isinstance(intent, dict):
                raise ValueError("owner-fit source intent must be canonical object")
            source = intent.get("candidate")
            if not isinstance(source, dict) or source.get("symbol") != selected.symbol:
                raise ValueError("strategy/owner-fit candidate symbol mismatch")
            # Canonical OBTradeIntent stores the original candidate inside
            # source_payload; never treat the wrapper as another source engine.
            payload = source.get("source_payload")
            if payload is not None and not isinstance(payload, dict):
                raise ValueError("owner-fit candidate source payload must be a source object")
            kind = (payload or {}).get("instrument_type", source.get("instrument_type"))
            if not isinstance(kind, str) or kind.upper() != selected.instrument_kind:
                raise ValueError("strategy/owner-fit instrument mismatch")
            if selected.instrument_kind == "OPTION" and not _matching_research_contract(intent, selected):
                raise ValueError("selected option contract absent from canonical owner-fit research")
            mode_binding = intent.get("mode_authority")
            if not isinstance(mode_binding, dict) or mode_binding.get("snapshot") != mode:
                raise ValueError("owner-fit intent does not bind the supplied canonical mode")
            account = intent.get("account_context")
            if not isinstance(account, dict) or account.get("account_key") != strategy.account_key:
                raise ValueError("owner-fit intent crosses account boundary")
            if context is not None and not isinstance(context, dict):
                raise ValueError("owner-fit context must be explicit object")
            fit = evaluate_owner_fit(intent, context=context)
            bucket = fit["bucket"]
            fit_fingerprint = fit["evaluation_fingerprint"]
            policy_fingerprint = fit["owner_fit"]["effective_policy_ref"]["policy_fingerprint"]
            if bucket == "NOT_YET":
                reasons.add("CANONICAL_OWNER_FIT_NOT_YET")
                reasons.update("OWNER_FIT:" + x for x in fit["owner_fit"]["hard_failure_reasons"])
            elif bucket == "WATCH":
                reasons.add("CANONICAL_OWNER_FIT_WATCH")
                reasons.update("OWNER_FIT:" + x for x in fit["owner_fit"]["watch_reasons"])
            elif bucket != "NOW":
                raise ValueError("unknown canonical owner-fit status")
    if flags is None:
        reasons.add("SAFETY_SOURCE_SIGNALS_MISSING")
    else:
        reasons.update("DANGER:" + key.upper() for key in HARD_STOPS if flags[key] is True)
        if flags["source_stale"] is True:
            reasons.add("SAFETY_SOURCE_STALE")
        if any(value is None for value in flags.values()):
            reasons.add("SAFETY_SOURCE_SIGNAL_UNKNOWN")
    if any(reason.startswith("DANGER:") for reason in reasons) or "CANONICAL_OWNER_FIT_NOT_YET" in reasons:
        state = "BLOCK"
    elif reasons:
        state = "HOLD"
    else:
        state = "REVIEW_ONLY"
    provisional = SafetyReview(
        review_id="PENDING", authority=SCHEMA_VERSION, account_key=strategy.account_key,
        strategy_review_id=strategy.review_id, strategy_review_hash=strategy.integrity_hash,
        candidate_id=selected.candidate_id if selected else None,
        market_time_receipt_id=market_time.receipt_id,
        market_time_hash=market_time.integrity_hash,
        mode_state_id=mode["state_id"], mode_state_hash=mode["mode_state_fingerprint"],
        owner_fit_fingerprint=fit_fingerprint, effective_policy_fingerprint=policy_fingerprint,
        source_signals_hash=signals_hash, state=state, reasons=tuple(sorted(reasons)),
        source_claims_not_externally_authenticated=True,
        owner_review_allowed=state == "REVIEW_ONLY", order_authorized=False,
        execution_authorized=False, broker_submission=False, capital_movement=False,
        mode_changed=False, integrity_hash="PENDING",
    )
    digest = _digest(_material(provisional))
    return replace(provisional, review_id="OBSAFE-" + digest[:24], integrity_hash=digest)


def verify_safety_review(
    value: SafetyReview, strategy: StrategyReview, *, portfolio: PortfolioComparison,
    harness: MultiSimulationHarness, sources: tuple[PositionSnapshot, ...],
    candidates: tuple[StrategyCandidate, ...], market_time: CanonicalMarketTimeReceipt,
    mode_state: dict[str, object], signals: SafetySignals | None = None,
    intent: dict[str, object] | None = None, context: dict[str, object] | None = None,
) -> bool:
    if not isinstance(value, SafetyReview) or value.authority != SCHEMA_VERSION:
        return False
    if any(getattr(value, name) is not False for name in (
        "order_authorized", "execution_authorized", "broker_submission",
        "capital_movement", "mode_changed",
    )):
        return False
    try:
        return value == _build(
            strategy, portfolio=portfolio, harness=harness, sources=sources,
            candidates=candidates, market_time=market_time, mode_state=mode_state,
            signals=signals, intent=intent, context=context,
        )
    except (ValueError, TypeError, AttributeError, KeyError):
        return False


def build_safety_review(
    strategy: StrategyReview, *, portfolio: PortfolioComparison,
    harness: MultiSimulationHarness, sources: tuple[PositionSnapshot, ...],
    candidates: tuple[StrategyCandidate, ...], market_time: CanonicalMarketTimeReceipt,
    mode_state: dict[str, object], signals: SafetySignals | None = None,
    intent: dict[str, object] | None = None, context: dict[str, object] | None = None,
) -> SafetyReview:
    value = _build(
        strategy, portfolio=portfolio, harness=harness, sources=sources,
        candidates=candidates, market_time=market_time, mode_state=mode_state,
        signals=signals, intent=intent, context=context,
    )
    if not verify_safety_review(
        value, strategy, portfolio=portfolio, harness=harness, sources=sources,
        candidates=candidates, market_time=market_time, mode_state=mode_state,
        signals=signals, intent=intent, context=context,
    ):
        raise ValueError("safety receipt failed independent recomputation")
    return value


def safety_review_reference(
    value: SafetyReview, strategy: StrategyReview, *, portfolio: PortfolioComparison,
    harness: MultiSimulationHarness, sources: tuple[PositionSnapshot, ...],
    candidates: tuple[StrategyCandidate, ...], market_time: CanonicalMarketTimeReceipt,
    mode_state: dict[str, object], signals: SafetySignals | None = None,
    intent: dict[str, object] | None = None, context: dict[str, object] | None = None,
) -> dict[str, object]:
    if not verify_safety_review(
        value, strategy, portfolio=portfolio, harness=harness, sources=sources,
        candidates=candidates, market_time=market_time, mode_state=mode_state,
        signals=signals, intent=intent, context=context,
    ):
        raise ValueError("safety reference requires verified full source lineage")
    return {
        "authority": SCHEMA_VERSION, "review_id": value.review_id,
        "integrity_hash": value.integrity_hash,
        "account_key": value.account_key, "state": value.state,
        "reason_codes": list(value.reasons), "amounts_exposed": False,
        "broker_submission": False, "capital_movement": False,
        "execution_authorized": False, "tower_authorization_required": True,
    }


def safety_review_contract() -> dict[str, object]:
    return {
        "authority": SCHEMA_VERSION, "strategy_source": "OB_STRATEGY_REVIEW_V1",
        "owner_fit_source": "OB_OWNER_FIT_ELIGIBILITY_V1",
        "effective_policy_recomputed_via_owner_fit": True,
        "operating_mode_revalidated": True, "canonical_market_time_revalidated": True,
        "source_danger_signals_can_only_restrict": True,
        "source_hash_proves_external_authenticity": False,
        "states": ["BLOCK", "HOLD", "REVIEW_ONLY"],
        "review_only_is_execution_permission": False,
        "no_second_policy_or_fill_engine": True,
        "direct_buybox_access": False, "teller_owns_acquisition_readiness": True,
        "order_authorized": False, "execution_authorized": False,
        "broker_submission": False, "capital_movement": False, "mode_changed": False,
        "manual_live_unlock": False, "hybrid_unlock": False, "automated_unlock": False,
    }
