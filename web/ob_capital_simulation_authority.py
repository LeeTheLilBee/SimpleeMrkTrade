from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
import json
from typing import Any

from web.ob_multi_simulation_harness import (
    MultiSimulationHarness,
    SimulationLane,
    lane_state,
    verify_lane_receipt_chain,
)


SCHEMA_VERSION = "OB_CAPITAL_SIMULATION_V1"
SERVICE_VERSION = "CAPSIM001_005_CAPITAL_SIMULATION_FOUNDATION"

EFFECTIVE_POLICY_AUTHORITY = "OB_EFFECTIVE_POLICY_V1"

PENDING_CAPITAL_POLICY_AUTHORITY = "PENDING_OBCAP"
PENDING_SESSION_LOSS_AUTHORITY = "PENDING_CAPSIM006_010"


class CapitalCheckState(str, Enum):
    PASS = "PASS"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"
    UNKNOWN = "UNKNOWN"


class CapitalAssessmentState(str, Enum):
    ALLOW = "ALLOW"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCK = "BLOCK"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class CapitalPolicySnapshot:
    snapshot_id: str
    authority: str
    account_key: str
    effective_policy_id: str
    effective_policy_hash: str
    max_loss_per_trade_pct: float
    max_position_allocation_pct: float
    daily_loss_cap_pct: float
    integrity_hash: str


@dataclass(frozen=True)
class SimulationCapitalState:
    snapshot_id: str
    authority: str
    account_key: str
    lane: SimulationLane
    build_ref: str
    starting_capital: float
    cash: float
    realized_pnl: float
    unrealized_pnl: float
    equity: float
    peak_equity: float
    max_drawdown_pct: float
    receipt_chain_valid: bool
    integrity_hash: str


@dataclass(frozen=True)
class CapitalProposal:
    proposal_id: str
    authority: str
    account_key: str
    lane: SimulationLane
    capital_required: float
    declared_max_loss_amount: float | None
    risk_reference: str | None
    integrity_hash: str


@dataclass(frozen=True)
class CapitalCheck:
    name: str
    state: CapitalCheckState
    observed_value: float | None
    limit_value: float | None
    unit: str
    reason: str


@dataclass(frozen=True)
class CapitalSimulationAssessment:
    assessment_id: str
    authority: str
    account_key: str
    lane: SimulationLane
    state: CapitalAssessmentState
    policy_snapshot_id: str
    policy_integrity_hash: str
    capital_state_snapshot_id: str
    capital_state_integrity_hash: str
    proposal_id: str
    proposal_integrity_hash: str
    checks: tuple[CapitalCheck, ...]
    blocking_checks: tuple[str, ...]
    review_checks: tuple[str, ...]
    unknown_checks: tuple[str, ...]
    integrity_hash: str


def _canonical_json(
    value: object,
) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
        ensure_ascii=True,
        default=str,
    )


def stable_hash(
    value: object,
) -> str:
    return sha256(
        _canonical_json(
            value
        ).encode(
            "utf-8"
        )
    ).hexdigest()


def _nonblank(
    value: object,
    *,
    name: str,
) -> str:
    if value is None:
        raise ValueError(
            f"{name} cannot be blank"
        )

    text = str(
        value
    ).strip()

    if not text:
        raise ValueError(
            f"{name} cannot be blank"
        )

    return text


def _nonnegative_float(
    value: object,
    *,
    name: str,
) -> float:
    number = float(
        value
    )

    if number < 0:
        raise ValueError(
            f"{name} cannot be negative"
        )

    return number


def _positive_float(
    value: object,
    *,
    name: str,
) -> float:
    number = float(
        value
    )

    if number <= 0:
        raise ValueError(
            f"{name} must be greater than zero"
        )

    return number


def _lane(
    value: SimulationLane | str,
) -> SimulationLane:
    return (
        value
        if isinstance(
            value,
            SimulationLane,
        )
        else SimulationLane(
            str(
                value
            ).strip().upper()
        )
    )


def _policy_material(
    snapshot: CapitalPolicySnapshot,
) -> dict[str, object]:
    return {
        "authority":
            snapshot.authority,

        "account_key":
            snapshot.account_key,

        "effective_policy_id":
            snapshot.effective_policy_id,

        "effective_policy_hash":
            snapshot.effective_policy_hash,

        "max_loss_per_trade_pct":
            snapshot.max_loss_per_trade_pct,

        "max_position_allocation_pct":
            snapshot.max_position_allocation_pct,

        "daily_loss_cap_pct":
            snapshot.daily_loss_cap_pct,
    }


def verify_capital_policy_snapshot(
    snapshot: CapitalPolicySnapshot,
) -> bool:
    if not isinstance(
        snapshot,
        CapitalPolicySnapshot,
    ):
        return False

    if (
        snapshot.authority
        !=
        SCHEMA_VERSION
    ):
        return False

    digest = stable_hash(
        _policy_material(
            snapshot
        )
    )

    return (
        snapshot.integrity_hash
        == digest
        and
        snapshot.snapshot_id
        ==
        "OBCAPPOL-"
        + digest[:24]
    )


def build_capital_policy_snapshot(
    effective_policy: dict[str, Any],
) -> CapitalPolicySnapshot:
    if not isinstance(
        effective_policy,
        dict,
    ):
        raise ValueError(
            "effective_policy must be an object"
        )

    if (
        effective_policy.get(
            "authority"
        )
        !=
        EFFECTIVE_POLICY_AUTHORITY
    ):
        raise ValueError(
            "capital policy snapshot requires OB_EFFECTIVE_POLICY_V1"
        )

    if (
        effective_policy.get(
            "status"
        )
        !=
        "RESOLVED"
    ):
        raise ValueError(
            "capital policy snapshot requires resolved Effective Policy"
        )

    for forbidden in (
        "execution_authority",
        "broker_submission",
        "capital_movement",
        "automatic_contract_selection",
        "hybrid_execution",
        "automatic_execution",
    ):
        if (
            effective_policy.get(
                forbidden
            )
            is not False
        ):
            raise ValueError(
                "Effective Policy contains forbidden authority: "
                + forbidden
            )

    account_key = _nonblank(
        effective_policy.get(
            "account_key"
        ),
        name="effective policy account_key",
    )

    policy_id = _nonblank(
        effective_policy.get(
            "policy_id"
        ),
        name="effective policy_id",
    )

    policy_hash = _nonblank(
        effective_policy.get(
            "policy_fingerprint"
        ),
        name="effective policy fingerprint",
    )

    limits = effective_policy.get(
        "effective_limits"
    )

    if not isinstance(
        limits,
        dict,
    ):
        raise ValueError(
            "Effective Policy effective_limits missing"
        )

    max_loss = _positive_float(
        limits.get(
            "max_loss_per_trade_pct"
        ),
        name="max_loss_per_trade_pct",
    )

    max_allocation = _positive_float(
        limits.get(
            "max_position_allocation_pct"
        ),
        name="max_position_allocation_pct",
    )

    daily_loss = _positive_float(
        limits.get(
            "daily_loss_cap_pct"
        ),
        name="daily_loss_cap_pct",
    )

    provisional = CapitalPolicySnapshot(
        snapshot_id="PENDING",
        authority=SCHEMA_VERSION,
        account_key=account_key,
        effective_policy_id=policy_id,
        effective_policy_hash=policy_hash,
        max_loss_per_trade_pct=max_loss,
        max_position_allocation_pct=max_allocation,
        daily_loss_cap_pct=daily_loss,
        integrity_hash="PENDING",
    )

    digest = stable_hash(
        _policy_material(
            provisional
        )
    )

    result = CapitalPolicySnapshot(
        snapshot_id=(
            "OBCAPPOL-"
            + digest[:24]
        ),
        authority=provisional.authority,
        account_key=provisional.account_key,
        effective_policy_id=provisional.effective_policy_id,
        effective_policy_hash=provisional.effective_policy_hash,
        max_loss_per_trade_pct=provisional.max_loss_per_trade_pct,
        max_position_allocation_pct=provisional.max_position_allocation_pct,
        daily_loss_cap_pct=provisional.daily_loss_cap_pct,
        integrity_hash=digest,
    )

    if not verify_capital_policy_snapshot(
        result
    ):
        raise ValueError(
            "constructed capital policy snapshot failed verification"
        )

    return result


def _state_material(
    snapshot: SimulationCapitalState,
) -> dict[str, object]:
    return {
        "authority":
            snapshot.authority,

        "account_key":
            snapshot.account_key,

        "lane":
            snapshot.lane.value,

        "build_ref":
            snapshot.build_ref,

        "starting_capital":
            snapshot.starting_capital,

        "cash":
            snapshot.cash,

        "realized_pnl":
            snapshot.realized_pnl,

        "unrealized_pnl":
            snapshot.unrealized_pnl,

        "equity":
            snapshot.equity,

        "peak_equity":
            snapshot.peak_equity,

        "max_drawdown_pct":
            snapshot.max_drawdown_pct,

        "receipt_chain_valid":
            snapshot.receipt_chain_valid,
    }


def verify_simulation_capital_state(
    snapshot: SimulationCapitalState,
) -> bool:
    if not isinstance(
        snapshot,
        SimulationCapitalState,
    ):
        return False

    if (
        snapshot.authority
        !=
        SCHEMA_VERSION
    ):
        return False

    digest = stable_hash(
        _state_material(
            snapshot
        )
    )

    return (
        snapshot.integrity_hash
        == digest
        and
        snapshot.snapshot_id
        ==
        "OBCAPSTATE-"
        + digest[:24]
    )


def build_simulation_capital_state(
    harness: MultiSimulationHarness,
    *,
    lane: SimulationLane | str,
) -> SimulationCapitalState:
    if not isinstance(
        harness,
        MultiSimulationHarness,
    ):
        raise ValueError(
            "capital state requires MultiSimulationHarness"
        )

    selected_lane = _lane(
        lane
    )

    state = lane_state(
        harness,
        selected_lane,
    )

    chain_valid = (
        verify_lane_receipt_chain(
            state
        )
    )

    if not chain_valid:
        raise ValueError(
            "simulation lane receipt chain failed verification"
        )

    provisional = SimulationCapitalState(
        snapshot_id="PENDING",
        authority=SCHEMA_VERSION,
        account_key=_nonblank(
            harness.account_key,
            name="harness account_key",
        ),
        lane=selected_lane,
        build_ref=_nonblank(
            state.build_ref,
            name="simulation build_ref",
        ),
        starting_capital=float(
            state.starting_capital
        ),
        cash=float(
            state.cash
        ),
        realized_pnl=float(
            state.realized_pnl
        ),
        unrealized_pnl=float(
            state.unrealized_pnl
        ),
        equity=float(
            state.equity
        ),
        peak_equity=float(
            state.peak_equity
        ),
        max_drawdown_pct=float(
            state.max_drawdown_pct
        ),
        receipt_chain_valid=True,
        integrity_hash="PENDING",
    )

    digest = stable_hash(
        _state_material(
            provisional
        )
    )

    result = SimulationCapitalState(
        snapshot_id=(
            "OBCAPSTATE-"
            + digest[:24]
        ),
        authority=provisional.authority,
        account_key=provisional.account_key,
        lane=provisional.lane,
        build_ref=provisional.build_ref,
        starting_capital=provisional.starting_capital,
        cash=provisional.cash,
        realized_pnl=provisional.realized_pnl,
        unrealized_pnl=provisional.unrealized_pnl,
        equity=provisional.equity,
        peak_equity=provisional.peak_equity,
        max_drawdown_pct=provisional.max_drawdown_pct,
        receipt_chain_valid=provisional.receipt_chain_valid,
        integrity_hash=digest,
    )

    if not verify_simulation_capital_state(
        result
    ):
        raise ValueError(
            "constructed simulation capital state failed verification"
        )

    return result


def _proposal_material(
    proposal: CapitalProposal,
) -> dict[str, object]:
    return {
        "authority":
            proposal.authority,

        "account_key":
            proposal.account_key,

        "lane":
            proposal.lane.value,

        "capital_required":
            proposal.capital_required,

        "declared_max_loss_amount":
            proposal.declared_max_loss_amount,

        "risk_reference":
            proposal.risk_reference,
    }


def verify_capital_proposal(
    proposal: CapitalProposal,
) -> bool:
    if not isinstance(
        proposal,
        CapitalProposal,
    ):
        return False

    if (
        proposal.authority
        !=
        SCHEMA_VERSION
    ):
        return False

    digest = stable_hash(
        _proposal_material(
            proposal
        )
    )

    return (
        proposal.integrity_hash
        == digest
        and
        proposal.proposal_id
        ==
        "OBCAPPROP-"
        + digest[:24]
    )


def build_capital_proposal(
    *,
    account_key: str,
    lane: SimulationLane | str,
    capital_required: float,
    declared_max_loss_amount: float | None,
    risk_reference: str | None = None,
) -> CapitalProposal:
    selected_lane = _lane(
        lane
    )

    capital = _positive_float(
        capital_required,
        name="capital_required",
    )

    if declared_max_loss_amount is None:
        max_loss = None

        if (
            risk_reference is not None
            and
            str(
                risk_reference
            ).strip()
        ):
            raise ValueError(
                "risk_reference cannot be supplied without declared max loss"
            )

        clean_risk_reference = None

    else:
        max_loss = _nonnegative_float(
            declared_max_loss_amount,
            name="declared_max_loss_amount",
        )

        clean_risk_reference = _nonblank(
            risk_reference,
            name="risk_reference",
        )

    provisional = CapitalProposal(
        proposal_id="PENDING",
        authority=SCHEMA_VERSION,
        account_key=_nonblank(
            account_key,
            name="account_key",
        ),
        lane=selected_lane,
        capital_required=capital,
        declared_max_loss_amount=max_loss,
        risk_reference=clean_risk_reference,
        integrity_hash="PENDING",
    )

    digest = stable_hash(
        _proposal_material(
            provisional
        )
    )

    result = CapitalProposal(
        proposal_id=(
            "OBCAPPROP-"
            + digest[:24]
        ),
        authority=provisional.authority,
        account_key=provisional.account_key,
        lane=provisional.lane,
        capital_required=provisional.capital_required,
        declared_max_loss_amount=provisional.declared_max_loss_amount,
        risk_reference=provisional.risk_reference,
        integrity_hash=digest,
    )

    if not verify_capital_proposal(
        result
    ):
        raise ValueError(
            "constructed capital proposal failed verification"
        )

    return result


def _check_payload(
    check: CapitalCheck,
) -> dict[str, object]:
    return {
        "name":
            check.name,

        "state":
            check.state.value,

        "observed_value":
            check.observed_value,

        "limit_value":
            check.limit_value,

        "unit":
            check.unit,

        "reason":
            check.reason,
    }


def _assessment_state(
    checks: tuple[CapitalCheck, ...],
) -> CapitalAssessmentState:
    states = {
        item.state
        for item
        in checks
    }

    if (
        CapitalCheckState.BLOCK
        in states
    ):
        return CapitalAssessmentState.BLOCK

    if (
        CapitalCheckState.UNKNOWN
        in states
    ):
        return CapitalAssessmentState.UNKNOWN

    if (
        CapitalCheckState.REVIEW
        in states
    ):
        return CapitalAssessmentState.REVIEW_REQUIRED

    return CapitalAssessmentState.ALLOW


def _assessment_material(
    assessment: CapitalSimulationAssessment,
) -> dict[str, object]:
    return {
        "authority":
            assessment.authority,

        "account_key":
            assessment.account_key,

        "lane":
            assessment.lane.value,

        "state":
            assessment.state.value,

        "policy_snapshot_id":
            assessment.policy_snapshot_id,

        "policy_integrity_hash":
            assessment.policy_integrity_hash,

        "capital_state_snapshot_id":
            assessment.capital_state_snapshot_id,

        "capital_state_integrity_hash":
            assessment.capital_state_integrity_hash,

        "proposal_id":
            assessment.proposal_id,

        "proposal_integrity_hash":
            assessment.proposal_integrity_hash,

        "checks": [
            _check_payload(
                item
            )
            for item
            in assessment.checks
        ],

        "blocking_checks":
            list(
                assessment.blocking_checks
            ),

        "review_checks":
            list(
                assessment.review_checks
            ),

        "unknown_checks":
            list(
                assessment.unknown_checks
            ),
    }


def verify_capital_simulation_assessment(
    assessment: CapitalSimulationAssessment,
) -> bool:
    if not isinstance(
        assessment,
        CapitalSimulationAssessment,
    ):
        return False

    if (
        assessment.authority
        !=
        SCHEMA_VERSION
    ):
        return False

    if (
        assessment.state
        is not
        _assessment_state(
            assessment.checks
        )
    ):
        return False

    if (
        assessment.blocking_checks
        !=
        tuple(
            item.name
            for item
            in assessment.checks
            if (
                item.state
                is CapitalCheckState.BLOCK
            )
        )
    ):
        return False

    if (
        assessment.review_checks
        !=
        tuple(
            item.name
            for item
            in assessment.checks
            if (
                item.state
                is CapitalCheckState.REVIEW
            )
        )
    ):
        return False

    if (
        assessment.unknown_checks
        !=
        tuple(
            item.name
            for item
            in assessment.checks
            if (
                item.state
                is CapitalCheckState.UNKNOWN
            )
        )
    ):
        return False

    digest = stable_hash(
        _assessment_material(
            assessment
        )
    )

    return (
        assessment.integrity_hash
        == digest
        and
        assessment.assessment_id
        ==
        "OBCAPASSESS-"
        + digest[:24]
    )


def assess_capital_proposal(
    *,
    policy: CapitalPolicySnapshot,
    capital_state: SimulationCapitalState,
    proposal: CapitalProposal,
) -> CapitalSimulationAssessment:
    if not verify_capital_policy_snapshot(
        policy
    ):
        raise ValueError(
            "capital policy snapshot failed verification"
        )

    if not verify_simulation_capital_state(
        capital_state
    ):
        raise ValueError(
            "simulation capital state failed verification"
        )

    if not verify_capital_proposal(
        proposal
    ):
        raise ValueError(
            "capital proposal failed verification"
        )

    if not (
        policy.account_key
        ==
        capital_state.account_key
        ==
        proposal.account_key
    ):
        raise ValueError(
            "capital assessment crosses account boundary"
        )

    if (
        capital_state.lane
        is not
        proposal.lane
    ):
        raise ValueError(
            "capital proposal crosses simulation lane boundary"
        )

    checks = []

    if (
        proposal.capital_required
        >
        capital_state.cash
    ):
        cash_state = (
            CapitalCheckState.BLOCK
        )

        cash_reason = (
            "Proposed simulated capital exceeds lane cash."
        )

    else:
        cash_state = (
            CapitalCheckState.PASS
        )

        cash_reason = (
            "Proposed simulated capital is within lane cash."
        )

    checks.append(
        CapitalCheck(
            name="cash_available",
            state=cash_state,
            observed_value=round(
                proposal.capital_required,
                6,
            ),
            limit_value=round(
                capital_state.cash,
                6,
            ),
            unit="currency",
            reason=cash_reason,
        )
    )

    if (
        capital_state.equity
        <= 0
    ):
        allocation_pct = None

        allocation_state = (
            CapitalCheckState.BLOCK
        )

        allocation_reason = (
            "Lane equity is not positive, so new capital allocation is blocked."
        )

    else:
        allocation_pct = round(
            (
                proposal.capital_required
                /
                capital_state.equity
            )
            * 100.0,
            6,
        )

        allocation_state = (
            CapitalCheckState.BLOCK
            if (
                allocation_pct
                >
                policy.max_position_allocation_pct
            )
            else
            CapitalCheckState.PASS
        )

        allocation_reason = (
            "Proposed allocation exceeds Effective Policy maximum."
            if (
                allocation_state
                is CapitalCheckState.BLOCK
            )
            else
            "Proposed allocation is within Effective Policy maximum."
        )

    checks.append(
        CapitalCheck(
            name="position_allocation",
            state=allocation_state,
            observed_value=allocation_pct,
            limit_value=policy.max_position_allocation_pct,
            unit="percentage_points",
            reason=allocation_reason,
        )
    )

    if (
        proposal.declared_max_loss_amount
        is None
    ):
        loss_pct = None

        loss_state = (
            CapitalCheckState.REVIEW
        )

        loss_reason = (
            "Per-trade maximum loss is not yet proven for this proposal."
        )

    elif (
        capital_state.equity
        <= 0
    ):
        loss_pct = None

        loss_state = (
            CapitalCheckState.BLOCK
        )

        loss_reason = (
            "Lane equity is not positive, so per-trade risk cannot be admitted."
        )

    else:
        loss_pct = round(
            (
                proposal.declared_max_loss_amount
                /
                capital_state.equity
            )
            * 100.0,
            6,
        )

        loss_state = (
            CapitalCheckState.BLOCK
            if (
                loss_pct
                >
                policy.max_loss_per_trade_pct
            )
            else
            CapitalCheckState.PASS
        )

        loss_reason = (
            "Declared per-trade loss exceeds Effective Policy maximum."
            if (
                loss_state
                is CapitalCheckState.BLOCK
            )
            else
            "Declared per-trade loss is within Effective Policy maximum."
        )

    checks.append(
        CapitalCheck(
            name="max_loss_per_trade",
            state=loss_state,
            observed_value=loss_pct,
            limit_value=policy.max_loss_per_trade_pct,
            unit="percentage_points",
            reason=loss_reason,
        )
    )

    checks.append(
        CapitalCheck(
            name="daily_loss_cap",
            state=CapitalCheckState.REVIEW,
            observed_value=None,
            limit_value=policy.daily_loss_cap_pct,
            unit="percentage_points",
            reason=(
                "Canonical session/day realized-loss derivation is deferred "
                "to CAPSIM006-010. CAPSIM001-005 will not fabricate it."
            ),
        )
    )

    ordered = tuple(
        checks
    )

    state = _assessment_state(
        ordered
    )

    blocking = tuple(
        item.name
        for item
        in ordered
        if (
            item.state
            is CapitalCheckState.BLOCK
        )
    )

    review = tuple(
        item.name
        for item
        in ordered
        if (
            item.state
            is CapitalCheckState.REVIEW
        )
    )

    unknown = tuple(
        item.name
        for item
        in ordered
        if (
            item.state
            is CapitalCheckState.UNKNOWN
        )
    )

    provisional = CapitalSimulationAssessment(
        assessment_id="PENDING",
        authority=SCHEMA_VERSION,
        account_key=policy.account_key,
        lane=capital_state.lane,
        state=state,
        policy_snapshot_id=policy.snapshot_id,
        policy_integrity_hash=policy.integrity_hash,
        capital_state_snapshot_id=capital_state.snapshot_id,
        capital_state_integrity_hash=capital_state.integrity_hash,
        proposal_id=proposal.proposal_id,
        proposal_integrity_hash=proposal.integrity_hash,
        checks=ordered,
        blocking_checks=blocking,
        review_checks=review,
        unknown_checks=unknown,
        integrity_hash="PENDING",
    )

    digest = stable_hash(
        _assessment_material(
            provisional
        )
    )

    result = CapitalSimulationAssessment(
        assessment_id=(
            "OBCAPASSESS-"
            + digest[:24]
        ),
        authority=provisional.authority,
        account_key=provisional.account_key,
        lane=provisional.lane,
        state=provisional.state,
        policy_snapshot_id=provisional.policy_snapshot_id,
        policy_integrity_hash=provisional.policy_integrity_hash,
        capital_state_snapshot_id=provisional.capital_state_snapshot_id,
        capital_state_integrity_hash=provisional.capital_state_integrity_hash,
        proposal_id=provisional.proposal_id,
        proposal_integrity_hash=provisional.proposal_integrity_hash,
        checks=provisional.checks,
        blocking_checks=provisional.blocking_checks,
        review_checks=provisional.review_checks,
        unknown_checks=provisional.unknown_checks,
        integrity_hash=digest,
    )

    if not verify_capital_simulation_assessment(
        result
    ):
        raise ValueError(
            "constructed capital simulation assessment failed verification"
        )

    return result


def capital_simulation_contract() -> dict[str, object]:
    return {
        "schema_version":
            SCHEMA_VERSION,

        "service_version":
            SERVICE_VERSION,

        "authority":
            SCHEMA_VERSION,

        "simulation_only":
            True,

        "effective_policy_authority":
            EFFECTIVE_POLICY_AUTHORITY,

        "capital_policy_source_status":
            "PENDING",

        "pending_capital_policy_authority":
            PENDING_CAPITAL_POLICY_AUTHORITY,

        "policy_limits_consumed": [
            "max_loss_per_trade_pct",
            "max_position_allocation_pct",
            "daily_loss_cap_pct",
        ],

        "simulation_state_consumed": [
            "starting_capital",
            "cash",
            "realized_pnl",
            "unrealized_pnl",
            "equity",
            "peak_equity",
            "max_drawdown_pct",
        ],

        "daily_loss_canonical_authority":
            False,

        "future_daily_loss_authority":
            PENDING_SESSION_LOSS_AUTHORITY,

        "daily_loss_missing_behavior":
            "REVIEW_REQUIRED",

        "known_policy_violation_behavior":
            "BLOCK",

        "policy_widening":
            False,

        "effective_policy_mutation":
            False,

        "simulation_lane_mutation":
            False,

        "portfolio_policy_authority":
            False,

        "position_selection_authority":
            False,

        "strategy_selection_authority":
            False,

        "execution_authority":
            False,

        "broker_submission":
            False,

        "capital_movement":
            False,

        "automatic_contract_selection":
            False,

        "manual_live_unlock":
            False,

        "hybrid_unlock":
            False,

        "automated_unlock":
            False,

        "simulation_performance_grants_live_authority":
            False,
    }


def capital_simulation_snapshot(
    assessment: CapitalSimulationAssessment,
) -> dict[str, object]:
    if not verify_capital_simulation_assessment(
        assessment
    ):
        raise ValueError(
            "capital simulation assessment failed verification"
        )

    return {
        "assessment_id":
            assessment.assessment_id,

        "authority":
            assessment.authority,

        "account_key":
            assessment.account_key,

        "lane":
            assessment.lane.value,

        "state":
            assessment.state.value,

        "policy_snapshot_id":
            assessment.policy_snapshot_id,

        "capital_state_snapshot_id":
            assessment.capital_state_snapshot_id,

        "proposal_id":
            assessment.proposal_id,

        "blocking_checks":
            list(
                assessment.blocking_checks
            ),

        "review_checks":
            list(
                assessment.review_checks
            ),

        "unknown_checks":
            list(
                assessment.unknown_checks
            ),

        "checks": [
            _check_payload(
                item
            )
            for item
            in assessment.checks
        ],

        "integrity_hash":
            assessment.integrity_hash,

        "authority_boundary":
            capital_simulation_contract(),
    }
