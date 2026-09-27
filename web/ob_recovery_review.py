"""OBRES001–005: fail-closed source-recovery review, never a failover actuator.

OBRES re-verifies canonical OBATTN source lineage and only tracks separately
labelled source assertions about outage, conflict, staleness and restoration.
A repeated restored assertion requires distinct chronological underlying source
revisions and hashes, then requires a NEW canonical upstream revalidation.
Neither source hashes nor recovery review authenticate an institution or
restore permissions, clear a safety hold or restart a process.
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
from web.ob_recommendation_review import RecommendationReview
from web.ob_adverse_guard_review import GuardEvidence, GuardReview
from web.ob_soulaana_explanations import SoulaanaExplanation
from web.ob_owner_attention import OwnerAttention, verify_owner_attention

SCHEMA_VERSION = "OB_RECOVERY_REVIEW_V1"
SHA = re.compile(r"[0-9a-f]{64}")
COMPONENTS = frozenset((
    "MARKET_SOURCE", "POSITION_SOURCE", "CAPITAL_SOURCE",
    "OWNER_IDENTITY", "BROKER_SOURCE", "HOSTED_RUNTIME", "TELLER_SOURCE",
))
SOURCE_STATES = frozenset((
    "OUTAGE", "STALE", "CONFLICT", "UNKNOWN", "RESTORED_ASSERTED",
))
DENIAL_STATES = frozenset(("OUTAGE", "STALE", "CONFLICT", "UNKNOWN"))
REQUIREMENT_CODES = {
    "MARKET_SOURCE": "REVERIFY_CANONICAL_MARKET_TIME_AND_FRESHNESS",
    "POSITION_SOURCE": "REVERIFY_CANONICAL_POSITION_AND_FILL_LINEAGE",
    "CAPITAL_SOURCE": "REQUIRE_AUTHENTICATED_EXTERNAL_SETTLEMENT_AND_PROTECTED_RESERVE",
    "OWNER_IDENTITY": "REQUIRE_NEW_TOWER_OWNER_AUTHORIZATION_AND_STEP_UP",
    "BROKER_SOURCE": "REQUIRE_PROVIDER_AUTHENTICATED_READ_ONLY_BROKER_RECONCILIATION",
    "HOSTED_RUNTIME": "REQUIRE_INDEPENDENT_HOSTED_RUNTIME_AND_REVISION_CHECK",
    "TELLER_SOURCE": "REQUIRE_FRESH_TOWER_AUTHORIZED_TELLER_READINESS",
}


def _digest(value: object) -> str:
    return sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    ).encode()).hexdigest()


def _instant(value: str, label: str) -> datetime:
    try:
        if not isinstance(value, str):
            raise ValueError("not text")
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if result.tzinfo is None or result.utcoffset() is None:
            raise ValueError("naive")
        return result.astimezone(timezone.utc)
    except (TypeError, ValueError, AttributeError) as exc:
        raise ValueError(label + " must be timezone-aware ISO-8601") from exc


def _name(value: object, label: str) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise ValueError(label + " must be explicit nonblank text")
    return value


@dataclass(frozen=True)
class RecoveryObservation:
    account_key: str
    component: str
    source_ref: str
    source_revision: str
    source_payload_hash: str
    observed_at_utc: str
    received_at_utc: str
    expires_at_utc: str
    source_state: str
    source_claim_external_authenticity: bool
    observation_id: str
    integrity_hash: str


def _observation_material(value: RecoveryObservation) -> dict[str, object]:
    return {
        key: getattr(value, key) for key in RecoveryObservation.__dataclass_fields__
        if key not in ("observation_id", "integrity_hash")
    }


def _validate_observation(value: RecoveryObservation) -> tuple[datetime, datetime, datetime]:
    if not isinstance(value, RecoveryObservation):
        raise ValueError("recovery observation needs explicit immutable record")
    _name(value.account_key, "account_key")
    if value.component not in COMPONENTS or value.source_state not in SOURCE_STATES:
        raise ValueError("unknown recovery component or source state")
    for key in ("source_ref", "source_revision"):
        _name(getattr(value, key), key)
    if not isinstance(value.source_payload_hash, str) or not SHA.fullmatch(value.source_payload_hash):
        raise ValueError("source payload SHA-256 required")
    if value.source_claim_external_authenticity is not False:
        raise ValueError("owner/source assertion cannot claim external authenticity")
    observed = _instant(value.observed_at_utc, "observed_at_utc")
    received = _instant(value.received_at_utc, "received_at_utc")
    expires = _instant(value.expires_at_utc, "expires_at_utc")
    if not observed <= received < expires:
        raise ValueError("recovery source observation/receipt/expiry chronology invalid")
    material = _observation_material(value)
    digest = _digest(material)
    if value.integrity_hash != digest or value.observation_id != "OBRESOBS-" + digest[:24]:
        raise ValueError("recovery observation integrity mismatch")
    return observed, received, expires


def build_recovery_observation(
    *, account_key: str, component: str, source_ref: str,
    source_revision: str, source_payload_hash: str, observed_at_utc: str,
    received_at_utc: str, expires_at_utc: str, source_state: str,
) -> RecoveryObservation:
    provisional = RecoveryObservation(
        account_key=account_key, component=component, source_ref=source_ref,
        source_revision=source_revision, source_payload_hash=source_payload_hash,
        observed_at_utc=observed_at_utc, received_at_utc=received_at_utc,
        expires_at_utc=expires_at_utc, source_state=source_state,
        source_claim_external_authenticity=False,
        observation_id="PENDING", integrity_hash="PENDING",
    )
    # Validate before generating a receipt; later verification repeats checks.
    if component not in COMPONENTS or source_state not in SOURCE_STATES:
        raise ValueError("unknown recovery component or source state")
    for value, name in ((account_key, "account_key"), (source_ref, "source_ref"),
                        (source_revision, "source_revision")):
        _name(value, name)
    if not isinstance(source_payload_hash, str) or not SHA.fullmatch(source_payload_hash):
        raise ValueError("source payload SHA-256 required")
    if not _instant(observed_at_utc, "observed_at_utc") <= _instant(received_at_utc, "received_at_utc") < _instant(expires_at_utc, "expires_at_utc"):
        raise ValueError("recovery source observation/receipt/expiry chronology invalid")
    digest = _digest(_observation_material(provisional))
    result = replace(provisional, observation_id="OBRESOBS-" + digest[:24], integrity_hash=digest)
    _validate_observation(result)
    return result


@dataclass(frozen=True)
class RecoveryComponent:
    component: str
    source_state: str
    observation_ids: tuple[str, ...]
    latest_source_hash: str | None
    latest_source_revision: str | None
    two_distinct_restoration_claims: bool
    requires_canonical_revalidation: bool
    external_authenticity_verified: bool
    requirement_code: str


@dataclass(frozen=True)
class RecoveryReview:
    review_id: str
    authority: str
    account_key: str
    attention_queue_id: str
    attention_queue_hash: str
    canonical_recommendation_state: str
    as_of_utc: str
    monitored_components: tuple[str, ...]
    components: tuple[RecoveryComponent, ...]
    source_observation_ids: tuple[str, ...]
    state: str
    reason_codes: tuple[str, ...]
    source_payload_hash_proves_authenticity: bool
    source_recovery_authenticates_institution: bool
    inherited_canonical_block_cleared: bool
    protected_capital_released: bool
    owner_or_provider_authorization_granted: bool
    automatic_failover: bool
    automatic_restart: bool
    automatic_replay: bool
    kill_switch_cleared: bool
    mode_changed: bool
    execution_authority: bool
    broker_submission: bool
    capital_movement: bool
    direct_buybox_access: bool
    integrity_hash: str


def _review_material(value: RecoveryReview) -> dict[str, object]:
    return {
        key: [asdict(c) for c in value.components] if key == "components" else getattr(value, key)
        for key in RecoveryReview.__dataclass_fields__ if key not in ("review_id", "integrity_hash")
    }


def _build(
    attention: OwnerAttention, explanation: SoulaanaExplanation,
    recommendation: RecommendationReview, safety: SafetyReview,
    strategy: StrategyReview, *, portfolio: PortfolioComparison,
    harness: MultiSimulationHarness, sources: tuple[PositionSnapshot, ...],
    candidates: tuple[StrategyCandidate, ...], market_time: CanonicalMarketTimeReceipt,
    mode_state: dict[str, object], monitored_components: tuple[str, ...],
    as_of_utc: str, observations: tuple[RecoveryObservation, ...] = (),
    signals: SafetySignals | None = None, intent: dict[str, object] | None = None,
    context: dict[str, object] | None = None, guard: GuardReview | None = None,
    guard_evidence: tuple[GuardEvidence, ...] | None = None,
) -> RecoveryReview:
    if not verify_owner_attention(
        attention, explanation, recommendation, safety, strategy,
        portfolio=portfolio, harness=harness, sources=sources,
        candidates=candidates, market_time=market_time, mode_state=mode_state,
        signals=signals, intent=intent, context=context,
        guard=guard, guard_evidence=guard_evidence,
    ):
        raise ValueError("OBRES requires verified canonical OBATTN and upstream lineage")
    if not isinstance(monitored_components, tuple) or not monitored_components:
        raise ValueError("recovery requires explicit monitored components")
    if len(monitored_components) != len(set(monitored_components)) or any(x not in COMPONENTS for x in monitored_components):
        raise ValueError("monitored components must be known and unique")
    if not isinstance(observations, tuple) or len(observations) > 100:
        raise ValueError("recovery observations must be a bounded immutable tuple")
    as_of = _instant(as_of_utc, "as_of_utc")
    if as_of < market_time.observed_at_utc:
        raise ValueError("recovery review cannot precede canonical market-time source")
    per_component: dict[str, list[tuple[RecoveryObservation, datetime, datetime]]] = {
        x: [] for x in monitored_components
    }
    unique_ids: set[str] = set()
    for obs in observations:
        observed, received, expires = _validate_observation(obs)
        if obs.account_key != attention.account_key or obs.component not in per_component:
            raise ValueError("recovery source crosses account/monitored component boundary")
        if obs.observation_id in unique_ids:
            raise ValueError("duplicate recovery observation replay")
        unique_ids.add(obs.observation_id)
        if observed > as_of or received > as_of:
            raise ValueError("source observation/receipt cannot be future-dated")
        prior = per_component[obs.component]
        if prior:
            last = prior[-1][0]
            if observed <= prior[-1][1]:
                raise ValueError("recovery observations must advance strictly by underlying observed-at")
            if obs.source_revision == last.source_revision or obs.source_payload_hash == last.source_payload_hash:
                raise ValueError("same source revision/payload replay cannot advance recovery")
            if any(x.source_revision == obs.source_revision or x.source_payload_hash == obs.source_payload_hash for x, _, _ in prior):
                raise ValueError("previously seen source revision/payload cannot be reused")
        prior.append((obs, observed, expires))
    components: list[RecoveryComponent] = []
    reason_codes: set[str] = set()
    latest_states = []
    all_distinct_restored = True
    for component in monitored_components:
        records = per_component[component]
        latest = records[-1] if records else None
        if latest is None:
            state = "MISSING"
        elif as_of >= latest[2]:
            state = "EXPIRED"
        else:
            state = latest[0].source_state
        distinct = (
            len(records) >= 2 and state == "RESTORED_ASSERTED"
            and records[-2][0].source_state == "RESTORED_ASSERTED"
            and records[-2][2] > records[-1][1]
            and records[-2][0].source_payload_hash != records[-1][0].source_payload_hash
            and records[-2][0].source_revision != records[-1][0].source_revision
        )
        if not distinct:
            all_distinct_restored = False
        latest_states.append(state)
        if state != "RESTORED_ASSERTED" or not distinct:
            reason_codes.add(component + ":" + (
                "AWAIT_DISTINCT_SOURCE_RESTORATION_EVIDENCE"
                if state == "RESTORED_ASSERTED" else state
            ))
        components.append(RecoveryComponent(
            component=component, source_state=state,
            observation_ids=tuple(x.observation_id for x, _, _ in records),
            latest_source_hash=latest[0].source_payload_hash if latest else None,
            latest_source_revision=latest[0].source_revision if latest else None,
            two_distinct_restoration_claims=distinct,
            requires_canonical_revalidation=True, external_authenticity_verified=False,
            requirement_code=REQUIREMENT_CODES[component],
        ))
        reason_codes.add(REQUIREMENT_CODES[component])
    if attention.source_recommendation_state == "BLOCKED":
        state = "CANONICAL_BLOCK_RETAINED"
        reason_codes.add("CANONICAL_SAFETY_BLOCK_CANNOT_BE_CLEARED_BY_SOURCE_RECOVERY")
    elif any(x in ("OUTAGE", "CONFLICT") for x in latest_states):
        state = "OUTAGE_OR_CONFLICT_HOLD"
    elif all_distinct_restored:
        state = "FRESH_CANONICAL_REVALIDATION_REQUIRED"
    else:
        state = "SOURCE_RECONCILIATION_REQUIRED"
    if attention.source_recommendation_state == "EVIDENCE_PENDING":
        reason_codes.add("CANONICAL_EVIDENCE_HOLD_REQUIRES_NEW_UPSTREAM_REVIEW")
    if any(x == "STALE" or x == "EXPIRED" for x in latest_states):
        reason_codes.add("STALE_OR_EXPIRED_EVIDENCE_CANNOT_BE_CURRENT")
    if state == "FRESH_CANONICAL_REVALIDATION_REQUIRED":
        reason_codes.add("SOURCE_RESTORATION_ASSERTIONS_NOT_NEW_OBSAFE_OR_OBATTN")
    provisional = RecoveryReview(
        review_id="PENDING", authority=SCHEMA_VERSION, account_key=attention.account_key,
        attention_queue_id=attention.queue_id, attention_queue_hash=attention.integrity_hash,
        canonical_recommendation_state=attention.source_recommendation_state,
        as_of_utc=as_of.isoformat(), monitored_components=monitored_components,
        components=tuple(components),
        source_observation_ids=tuple(x.observation_id for x in observations),
        state=state, reason_codes=tuple(sorted(reason_codes)),
        source_payload_hash_proves_authenticity=False,
        source_recovery_authenticates_institution=False,
        inherited_canonical_block_cleared=False, protected_capital_released=False,
        owner_or_provider_authorization_granted=False, automatic_failover=False,
        automatic_restart=False, automatic_replay=False, kill_switch_cleared=False,
        mode_changed=False, execution_authority=False, broker_submission=False,
        capital_movement=False, direct_buybox_access=False, integrity_hash="PENDING",
    )
    digest = _digest(_review_material(provisional))
    return replace(provisional, review_id="OBRES-" + digest[:24], integrity_hash=digest)


def verify_recovery_review(
    value: RecoveryReview, attention: OwnerAttention, explanation: SoulaanaExplanation,
    recommendation: RecommendationReview, safety: SafetyReview, strategy: StrategyReview,
    *, portfolio: PortfolioComparison, harness: MultiSimulationHarness,
    sources: tuple[PositionSnapshot, ...], candidates: tuple[StrategyCandidate, ...],
    market_time: CanonicalMarketTimeReceipt, mode_state: dict[str, object],
    monitored_components: tuple[str, ...], as_of_utc: str,
    observations: tuple[RecoveryObservation, ...] = (),
    signals: SafetySignals | None = None, intent: dict[str, object] | None = None,
    context: dict[str, object] | None = None, guard: GuardReview | None = None,
    guard_evidence: tuple[GuardEvidence, ...] | None = None,
) -> bool:
    if not isinstance(value, RecoveryReview) or value.authority != SCHEMA_VERSION:
        return False
    if any(getattr(value, name) is not False for name in (
        "source_payload_hash_proves_authenticity", "source_recovery_authenticates_institution",
        "inherited_canonical_block_cleared", "protected_capital_released",
        "owner_or_provider_authorization_granted", "automatic_failover", "automatic_restart",
        "automatic_replay", "kill_switch_cleared", "mode_changed", "execution_authority",
        "broker_submission", "capital_movement", "direct_buybox_access",
    )):
        return False
    try:
        return value == _build(
            attention, explanation, recommendation, safety, strategy,
            portfolio=portfolio, harness=harness, sources=sources, candidates=candidates,
            market_time=market_time, mode_state=mode_state,
            monitored_components=monitored_components, as_of_utc=as_of_utc,
            observations=observations, signals=signals, intent=intent, context=context,
            guard=guard, guard_evidence=guard_evidence,
        )
    except (ValueError, TypeError, AttributeError, KeyError):
        return False


def build_recovery_review(
    attention: OwnerAttention, explanation: SoulaanaExplanation,
    recommendation: RecommendationReview, safety: SafetyReview, strategy: StrategyReview,
    *, portfolio: PortfolioComparison, harness: MultiSimulationHarness,
    sources: tuple[PositionSnapshot, ...], candidates: tuple[StrategyCandidate, ...],
    market_time: CanonicalMarketTimeReceipt, mode_state: dict[str, object],
    monitored_components: tuple[str, ...], as_of_utc: str,
    observations: tuple[RecoveryObservation, ...] = (),
    signals: SafetySignals | None = None, intent: dict[str, object] | None = None,
    context: dict[str, object] | None = None, guard: GuardReview | None = None,
    guard_evidence: tuple[GuardEvidence, ...] | None = None,
) -> RecoveryReview:
    value = _build(
        attention, explanation, recommendation, safety, strategy,
        portfolio=portfolio, harness=harness, sources=sources, candidates=candidates,
        market_time=market_time, mode_state=mode_state,
        monitored_components=monitored_components, as_of_utc=as_of_utc,
        observations=observations, signals=signals, intent=intent, context=context,
        guard=guard, guard_evidence=guard_evidence,
    )
    if not verify_recovery_review(
        value, attention, explanation, recommendation, safety, strategy,
        portfolio=portfolio, harness=harness, sources=sources, candidates=candidates,
        market_time=market_time, mode_state=mode_state,
        monitored_components=monitored_components, as_of_utc=as_of_utc,
        observations=observations, signals=signals, intent=intent, context=context,
        guard=guard, guard_evidence=guard_evidence,
    ):
        raise ValueError("OBRES recovery review failed independent source verification")
    return value


def recovery_reference(
    value: RecoveryReview, attention: OwnerAttention, explanation: SoulaanaExplanation,
    recommendation: RecommendationReview, safety: SafetyReview, strategy: StrategyReview,
    *, portfolio: PortfolioComparison, harness: MultiSimulationHarness,
    sources: tuple[PositionSnapshot, ...], candidates: tuple[StrategyCandidate, ...],
    market_time: CanonicalMarketTimeReceipt, mode_state: dict[str, object],
    monitored_components: tuple[str, ...], as_of_utc: str,
    observations: tuple[RecoveryObservation, ...] = (),
    signals: SafetySignals | None = None, intent: dict[str, object] | None = None,
    context: dict[str, object] | None = None, guard: GuardReview | None = None,
    guard_evidence: tuple[GuardEvidence, ...] | None = None,
) -> dict[str, object]:
    if not verify_recovery_review(
        value, attention, explanation, recommendation, safety, strategy,
        portfolio=portfolio, harness=harness, sources=sources, candidates=candidates,
        market_time=market_time, mode_state=mode_state,
        monitored_components=monitored_components, as_of_utc=as_of_utc,
        observations=observations, signals=signals, intent=intent, context=context,
        guard=guard, guard_evidence=guard_evidence,
    ):
        raise ValueError("recovery proof reference needs verified entire source lineage")
    return {
        "authority": SCHEMA_VERSION, "review_id": value.review_id,
        "integrity_hash": value.integrity_hash, "account_key": value.account_key,
        "attention_queue_id": value.attention_queue_id,
        "state": value.state, "reason_codes": list(value.reason_codes),
        "amounts_exposed": False, "automatic_restart": False,
        "kill_switch_cleared": False, "broker_submission": False,
        "capital_movement": False, "tower_authorization_required": True,
    }


def recovery_contract() -> dict[str, object]:
    return {
        "authority": SCHEMA_VERSION, "upstream_authority": "OB_OWNER_ATTENTION_V1",
        "recompute_full_source_lineage": True,
        "source_observations_bound_to_account_and_component": True,
        "strict_chronology_and_distinct_source_fingerprints": True,
        "restoration_assertion_is_not_actual_reconciliation": True,
        "canonical_block_or_hold_never_auto_cleared": True,
        "requires_fresh_canonical_upstream_review": True,
        "source_hash_proves_external_authenticity": False,
        "automatic_provider_failover": False, "automatic_restart": False,
        "automatic_replay": False, "kill_switch_clear": False,
        "release_protected_capital": False, "execution_authority": False,
        "broker_submission": False, "capital_movement": False,
        "manual_live_unlock": False, "hybrid_unlock": False,
        "automated_unlock": False, "direct_buybox_access": False,
        "teller_owns_acquisition_readiness": True,
    }
