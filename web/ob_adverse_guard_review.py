"""OBGUARD001–005: distinct-source adverse pattern review, never an actuator.

Each input must reverify OBLEARN→OBREV→OBREC→OBSAFE lineage. Multiple
owner-asserted review records do not become authenticated market events,
proof of profitability, an automatic kill switch, policy change, or live mode.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from hashlib import sha256
import json

from web.ob_market_time_authority import CanonicalMarketTimeReceipt
from web.ob_multi_simulation_harness import MultiSimulationHarness
from web.ob_portfolio_view import PortfolioComparison
from web.ob_position_truth import PositionSnapshot
from web.ob_strategy_review import StrategyCandidate, StrategyReview
from web.ob_safety_review import SafetyReview, SafetySignals
from web.ob_recommendation_review import RecommendationReview
from web.ob_owner_review_evidence import OwnerReviewRecord, OwnerReviewDecision, ReviewIssue
from web.ob_review_learning import ReviewLearning, verify_review_learning

SCHEMA_VERSION = "OB_ADVERSE_GUARD_REVIEW_V1"


def _hash(value: object) -> str:
    return sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    ).encode()).hexdigest()


def _instant(value: str) -> datetime:
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None or dt.utcoffset() is None:
            raise ValueError("naive")
        return dt.astimezone(timezone.utc)
    except (ValueError, TypeError, AttributeError) as exc:
        raise ValueError("guard requires explicit timezone-aware review chronology") from exc


@dataclass(frozen=True)
class GuardEvidence:
    learning: ReviewLearning
    review: OwnerReviewRecord
    recommendation: RecommendationReview
    safety: SafetyReview
    strategy: StrategyReview
    portfolio: PortfolioComparison
    harness: MultiSimulationHarness
    sources: tuple[PositionSnapshot, ...]
    candidates: tuple[StrategyCandidate, ...]
    market_time: CanonicalMarketTimeReceipt
    mode_state: dict[str, object]
    signals: SafetySignals | None = None
    intent: dict[str, object] | None = None
    context: dict[str, object] | None = None
    decision: OwnerReviewDecision | None = None
    issues: tuple[ReviewIssue, ...] = ()


@dataclass(frozen=True)
class GuardPattern:
    issue_code: str
    distinct_source_payload_count: int
    source_issue_ids: tuple[str, ...]
    source_payload_hashes: tuple[str, ...]
    repeated_source_assertion: bool
    authenticated_market_pattern: bool


@dataclass(frozen=True)
class GuardReview:
    guard_id: str
    authority: str
    account_key: str
    learning_receipt_ids: tuple[str, ...]
    learning_receipt_hashes: tuple[str, ...]
    review_record_ids: tuple[str, ...]
    source_assertion_patterns: tuple[GuardPattern, ...]
    owner_attention_tasks: tuple[str, ...]
    state: str
    all_sources_broker_authenticated: bool
    actual_outcome_verified: bool
    automatic_kill_switch_activated: bool
    policy_mutated: bool
    risk_limit_widened: bool
    mode_changed: bool
    capital_movement: bool
    broker_submission: bool
    integrity_hash: str


def _material(value: GuardReview) -> dict[str, object]:
    return {
        key: (
            [pattern.__dict__ for pattern in value.source_assertion_patterns]
            if key == "source_assertion_patterns" else getattr(value, key)
        ) for key in GuardReview.__dataclass_fields__
        if key not in ("guard_id", "integrity_hash")
    }


def _verify(item: GuardEvidence) -> bool:
    if not isinstance(item, GuardEvidence):
        return False
    return verify_review_learning(
        item.learning, item.review, item.recommendation, item.safety, item.strategy,
        portfolio=item.portfolio, harness=item.harness, sources=item.sources,
        candidates=item.candidates, market_time=item.market_time,
        mode_state=item.mode_state, signals=item.signals,
        intent=item.intent, context=item.context, decision=item.decision,
        issues=item.issues,
    )


def _build(evidence: tuple[GuardEvidence, ...]) -> GuardReview:
    if not isinstance(evidence, tuple) or not 1 <= len(evidence) <= 50:
        raise ValueError("guard needs one to fifty explicit review evidence entries")
    if any(not _verify(item) for item in evidence):
        raise ValueError("guard requires verified source-bound OBLEARN lineage")
    accounts = {item.learning.account_key for item in evidence}
    if len(accounts) != 1:
        raise ValueError("guard cannot mix accounts")
    record_ids = tuple(item.review.record_id for item in evidence)
    if len(set(record_ids)) != len(record_ids):
        raise ValueError("duplicate owner review receipt cannot count as a new pattern")
    instants = tuple(_instant(
        item.decision.recorded_at_utc if item.decision else
        item.market_time.observed_at_utc.isoformat()
    ) for item in evidence)
    if any(now <= previous for previous, now in zip(instants, instants[1:])):
        raise ValueError("owner guard reviews must advance strictly in observation time")
    per_code: dict[str, dict[str, set[str]]] = {}
    for item in evidence:
        for incident in item.issues:
            by_hash = per_code.setdefault(incident.issue_code, {})
            by_hash.setdefault(incident.source_payload_hash, set()).add(incident.issue_id)
    patterns = tuple(GuardPattern(
        issue_code=code, distinct_source_payload_count=len(by_hash),
        source_issue_ids=tuple(sorted({
            incident_id for ids in by_hash.values() for incident_id in ids
        })),
        source_payload_hashes=tuple(sorted(by_hash)),
        repeated_source_assertion=len(by_hash) >= 2,
        authenticated_market_pattern=False,
    ) for code, by_hash in sorted(per_code.items()))
    tasks = {task for item in evidence for task in item.learning.owner_review_tasks}
    if any(p.repeated_source_assertion for p in patterns):
        tasks.add("OWNER_REVIEW_REPEATED_DISTINCT_SOURCE_ASSERTIONS")
        state = "REPEATED_ADVERSE_SOURCE_REVIEW"
    elif patterns:
        state = "ADVERSE_SOURCE_REVIEW"
    elif any(item.recommendation.state != "OWNER_REVIEW_READY" for item in evidence):
        state = "SOURCE_EVIDENCE_HOLD"
    else:
        state = "NO_ADVERSE_SOURCE_REPORTED_NOT_SAFETY_PROOF"
    provisional = GuardReview(
        guard_id="PENDING", authority=SCHEMA_VERSION,
        account_key=evidence[0].learning.account_key,
        learning_receipt_ids=tuple(x.learning.learning_id for x in evidence),
        learning_receipt_hashes=tuple(x.learning.integrity_hash for x in evidence),
        review_record_ids=record_ids,
        source_assertion_patterns=patterns,
        owner_attention_tasks=tuple(sorted(tasks)), state=state,
        all_sources_broker_authenticated=False, actual_outcome_verified=False,
        automatic_kill_switch_activated=False, policy_mutated=False,
        risk_limit_widened=False, mode_changed=False, capital_movement=False,
        broker_submission=False, integrity_hash="PENDING",
    )
    digest = _hash(_material(provisional))
    return replace(provisional, guard_id="OBGUARD-" + digest[:24], integrity_hash=digest)


def verify_guard_review(value: GuardReview, evidence: tuple[GuardEvidence, ...]) -> bool:
    if not isinstance(value, GuardReview) or value.authority != SCHEMA_VERSION:
        return False
    if any(getattr(value, name) is not False for name in (
        "all_sources_broker_authenticated", "actual_outcome_verified",
        "automatic_kill_switch_activated", "policy_mutated", "risk_limit_widened",
        "mode_changed", "capital_movement", "broker_submission",
    )):
        return False
    try:
        return value == _build(evidence)
    except (ValueError, TypeError, AttributeError, KeyError):
        return False


def build_guard_review(evidence: tuple[GuardEvidence, ...]) -> GuardReview:
    value = _build(evidence)
    if not verify_guard_review(value, evidence):
        raise ValueError("guard review failed full source lineage verification")
    return value


def guard_reference(value: GuardReview, evidence: tuple[GuardEvidence, ...]) -> dict[str, object]:
    if not verify_guard_review(value, evidence):
        raise ValueError("guard reference requires fully verified source lineage")
    return {
        "authority": SCHEMA_VERSION, "guard_id": value.guard_id,
        "integrity_hash": value.integrity_hash,
        "state": value.state, "account_key": value.account_key,
        "source_assertion_codes": [p.issue_code for p in value.source_assertion_patterns],
        "amounts_exposed": False, "automatic_kill_switch_activated": False,
        "broker_submission": False, "capital_movement": False,
        "tower_authorization_required": True,
    }


def guard_contract() -> dict[str, object]:
    return {
        "authority": SCHEMA_VERSION, "upstream_authority": "OB_REVIEW_LEARNING_V1",
        "full_source_lineage_reverified": True,
        "distinct_payload_hash_required_for_repeat": True,
        "identical_source_replay_is_not_new_alert": True,
        "source_assertions_not_authenticated_market_events": True,
        "no_adverse_source_is_not_proof_of_safety": True,
        "actual_outcome_verified": False, "automatic_kill_switch": False,
        "risk_limit_widening": False, "policy_mutation": False, "mode_change": False,
        "broker_submission": False, "capital_movement": False,
        "direct_buybox_access": False, "teller_owns_acquisition_readiness": True,
        "manual_live_unlock": False, "hybrid_unlock": False, "automated_unlock": False,
    }
