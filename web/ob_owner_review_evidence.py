"""OBREV001–005: owner decision and adverse-review evidence, not a broker ledger.

A review disposition is an explicit caller/owner assertion recorded against a
verified OBREC receipt. It is NOT Tower-authenticated, an order instruction,
a broker fill, realized P&L, or permission to bypass safety or capital gates.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from hashlib import sha256
import json
import re

from web.ob_market_time_authority import CanonicalMarketTimeReceipt
from web.ob_multi_simulation_harness import MultiSimulationHarness
from web.ob_portfolio_view import PortfolioComparison
from web.ob_position_truth import PositionSnapshot
from web.ob_strategy_review import StrategyCandidate, StrategyReview
from web.ob_safety_review import SafetyReview, SafetySignals
from web.ob_recommendation_review import (
    RecommendationReview, verify_recommendation_review,
)

SCHEMA_VERSION = "OB_OWNER_REVIEW_EVIDENCE_V1"
DISPOSITIONS = frozenset(("DEFER", "DECLINE", "REQUEST_MORE_EVIDENCE", "INTERESTED_FOR_REVIEW"))
ISSUE_CODES = frozenset(("NEGATIVE_DIVE", "OVERTIME", "OVERREACH", "SOURCE_GAP"))
SHA256 = re.compile(r"[0-9a-f]{64}")


def _hash(obj: object) -> str:
    return sha256(json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    ).encode()).hexdigest()


def _name(value: object, name: str) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise ValueError(name + " must be explicit and nonblank")
    return value


def _sha(value: object) -> str:
    if not isinstance(value, str) or not SHA256.fullmatch(value):
        raise ValueError("owner review source hash must be lowercase SHA-256")
    return value


def _instant(value: str) -> datetime:
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None or dt.utcoffset() is None:
            raise ValueError("missing timezone")
        return dt.astimezone(timezone.utc)
    except (ValueError, TypeError, AttributeError) as exc:
        raise ValueError("review timestamp must be timezone-aware ISO-8601") from exc


@dataclass(frozen=True)
class OwnerReviewDecision:
    decision_id: str
    disposition: str
    recorded_at_utc: str
    owner_context_ref: str
    owner_assertion_hash: str
    explicit_owner_acknowledgement: bool
    note: str


@dataclass(frozen=True)
class ReviewIssue:
    issue_id: str
    issue_code: str
    source_ref: str
    source_payload_hash: str
    source_revision: str
    note: str


@dataclass(frozen=True)
class OwnerReviewRecord:
    record_id: str
    authority: str
    account_key: str
    recommendation_id: str
    recommendation_hash: str
    safety_review_id: str
    decision: OwnerReviewDecision | None
    issues: tuple[ReviewIssue, ...]
    inherited_safety_reasons: tuple[str, ...]
    state: str
    owner_context_tower_authenticated: bool
    source_issue_authenticity_verified: bool
    execution_authorized: bool
    broker_submission: bool
    capital_movement: bool
    actual_fill_recorded: bool
    realized_pnl_asserted: bool
    mode_changed: bool
    integrity_hash: str


def _material(value: OwnerReviewRecord) -> dict[str, object]:
    return {
        field: (
            asdict(value.decision) if field == "decision" and value.decision else
            [asdict(i) for i in value.issues] if field == "issues" else
            getattr(value, field)
        )
        for field in OwnerReviewRecord.__dataclass_fields__
        if field not in ("record_id", "integrity_hash")
    }


def _build(
    recommendation: RecommendationReview, safety: SafetyReview, strategy: StrategyReview, *,
    portfolio: PortfolioComparison, harness: MultiSimulationHarness,
    sources: tuple[PositionSnapshot, ...], candidates: tuple[StrategyCandidate, ...],
    market_time: CanonicalMarketTimeReceipt, mode_state: dict[str, object],
    signals: SafetySignals | None = None, intent: dict[str, object] | None = None,
    context: dict[str, object] | None = None,
    decision: OwnerReviewDecision | None = None,
    issues: tuple[ReviewIssue, ...] = (),
) -> OwnerReviewRecord:
    if not verify_recommendation_review(
        recommendation, safety, strategy, portfolio=portfolio, harness=harness,
        sources=sources, candidates=candidates, market_time=market_time,
        mode_state=mode_state, signals=signals, intent=intent, context=context,
    ):
        raise ValueError("OBREV requires verified OBREC and upstream safety lineage")
    if not isinstance(issues, tuple):
        raise ValueError("review issues require an immutable tuple")
    seen_ids: set[str] = set()
    for issue in issues:
        if not isinstance(issue, ReviewIssue) or issue.issue_code not in ISSUE_CODES:
            raise ValueError("review issue must use explicit canonical issue code")
        for field in ("issue_id", "source_ref", "source_revision", "note"):
            _name(getattr(issue, field), field)
        _sha(issue.source_payload_hash)
        if issue.issue_id in seen_ids:
            raise ValueError("duplicate owner review issue ID")
        seen_ids.add(issue.issue_id)
    if decision is not None:
        if not isinstance(decision, OwnerReviewDecision) or decision.disposition not in DISPOSITIONS:
            raise ValueError("owner decision must use explicit review-only disposition")
        for field in ("decision_id", "owner_context_ref", "note"):
            _name(getattr(decision, field), field)
        _sha(decision.owner_assertion_hash)
        if decision.explicit_owner_acknowledgement is not True:
            raise ValueError("owner review requires explicit owner acknowledgement")
        if _instant(decision.recorded_at_utc) < market_time.observed_at_utc:
            raise ValueError("owner review cannot precede the bound market observation")
        if (decision.disposition == "INTERESTED_FOR_REVIEW" and
            recommendation.state != "OWNER_REVIEW_READY"):
            raise ValueError("interest for review cannot override safety hold/denial")
    if issues:
        state = "ADVERSE_REVIEW_PENDING"
    elif recommendation.state == "BLOCKED":
        state = "SOURCE_BLOCKED"
    elif recommendation.state == "EVIDENCE_PENDING":
        state = "EVIDENCE_HOLD"
    elif decision is None:
        state = "WAITING_OWNER"
    else:
        state = {
            "DEFER": "OWNER_DEFERRED",
            "DECLINE": "OWNER_DECLINED",
            "REQUEST_MORE_EVIDENCE": "MORE_EVIDENCE_REQUESTED",
            "INTERESTED_FOR_REVIEW": "OWNER_INTEREST_RECORDED",
        }[decision.disposition]
    provisional = OwnerReviewRecord(
        record_id="PENDING", authority=SCHEMA_VERSION,
        account_key=recommendation.account_key,
        recommendation_id=recommendation.recommendation_id,
        recommendation_hash=recommendation.integrity_hash,
        safety_review_id=safety.review_id, decision=decision, issues=issues,
        inherited_safety_reasons=recommendation.reason_codes,
        state=state, owner_context_tower_authenticated=False,
        source_issue_authenticity_verified=False, execution_authorized=False,
        broker_submission=False, capital_movement=False, actual_fill_recorded=False,
        realized_pnl_asserted=False, mode_changed=False, integrity_hash="PENDING",
    )
    digest = _hash(_material(provisional))
    return replace(provisional, record_id="OBREV-" + digest[:24], integrity_hash=digest)


def verify_owner_review(
    value: OwnerReviewRecord, recommendation: RecommendationReview,
    safety: SafetyReview, strategy: StrategyReview, *,
    portfolio: PortfolioComparison, harness: MultiSimulationHarness,
    sources: tuple[PositionSnapshot, ...], candidates: tuple[StrategyCandidate, ...],
    market_time: CanonicalMarketTimeReceipt, mode_state: dict[str, object],
    signals: SafetySignals | None = None, intent: dict[str, object] | None = None,
    context: dict[str, object] | None = None,
    decision: OwnerReviewDecision | None = None, issues: tuple[ReviewIssue, ...] = (),
) -> bool:
    if not isinstance(value, OwnerReviewRecord) or value.authority != SCHEMA_VERSION:
        return False
    if any(getattr(value, flag) is not False for flag in (
        "owner_context_tower_authenticated", "source_issue_authenticity_verified",
        "execution_authorized", "broker_submission", "capital_movement",
        "actual_fill_recorded", "realized_pnl_asserted", "mode_changed",
    )):
        return False
    try:
        return value == _build(
            recommendation, safety, strategy, portfolio=portfolio,
            harness=harness, sources=sources, candidates=candidates,
            market_time=market_time, mode_state=mode_state, signals=signals,
            intent=intent, context=context, decision=decision, issues=issues,
        )
    except (ValueError, TypeError, AttributeError, KeyError):
        return False


def build_owner_review(
    recommendation: RecommendationReview, safety: SafetyReview, strategy: StrategyReview, *,
    portfolio: PortfolioComparison, harness: MultiSimulationHarness,
    sources: tuple[PositionSnapshot, ...], candidates: tuple[StrategyCandidate, ...],
    market_time: CanonicalMarketTimeReceipt, mode_state: dict[str, object],
    signals: SafetySignals | None = None, intent: dict[str, object] | None = None,
    context: dict[str, object] | None = None,
    decision: OwnerReviewDecision | None = None, issues: tuple[ReviewIssue, ...] = (),
) -> OwnerReviewRecord:
    value = _build(
        recommendation, safety, strategy, portfolio=portfolio,
        harness=harness, sources=sources, candidates=candidates,
        market_time=market_time, mode_state=mode_state, signals=signals,
        intent=intent, context=context, decision=decision, issues=issues,
    )
    if not verify_owner_review(
        value, recommendation, safety, strategy, portfolio=portfolio,
        harness=harness, sources=sources, candidates=candidates,
        market_time=market_time, mode_state=mode_state, signals=signals,
        intent=intent, context=context, decision=decision, issues=issues,
    ):
        raise ValueError("owner review evidence failed independent verification")
    return value


def owner_review_contract() -> dict[str, object]:
    return {
        "authority": SCHEMA_VERSION,
        "source_authority": "OB_RECOMMENDATION_REVIEW_V1",
        "source_lineage_reverified": True,
        "owner_decision_is_claim_not_tower_authentication": True,
        "issues": sorted(ISSUE_CODES),
        "unknown_or_adverse_does_not_promote_review": True,
        "actual_broker_fills_tracked": False,
        "source_pnl_claimed_as_actual": False,
        "execution_authority": False, "broker_submission": False,
        "capital_movement": False, "mode_changed": False,
        "direct_buybox_access": False, "teller_owns_acquisition_readiness": True,
        "manual_live_unlock": False, "hybrid_unlock": False, "automated_unlock": False,
    }
