from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
import json
from typing import Any, Iterable

from web.ob_multi_simulation_harness import (
    MultiSimulationHarness,
    SimulationAction,
    SimulationFillPolicy,
    SimulationLane,
    SimulationMarketFrame,
    apply_simulation_decision,
    lane_state,
    preview_simulation_open_cost,
    verify_lane_receipt_chain,
)


SCHEMA_VERSION = "OB_CAPITAL_SIMULATION_V1"
SERVICE_VERSION = "CAPSIM001_010_CAPITAL_SIMULATION"

EFFECTIVE_POLICY_AUTHORITY = "OB_EFFECTIVE_POLICY_V1"
MARKET_TIME_AUTHORITY = "OB_MARKET_TIME_V1"

PENDING_CAPITAL_POLICY_AUTHORITY = "PENDING_OBCAP"
SESSION_LOSS_AUTHORITY = SCHEMA_VERSION


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
    session_loss_ledger_id: str | None
    session_loss_integrity_hash: str | None
    integrity_hash: str


@dataclass(frozen=True)
class CapitalSessionLossEntry:
    trade_id: str
    frame_id: str
    market_time_receipt_id: str
    market_time_integrity_hash: str
    trading_date: str
    market_session: str
    realized_pnl: float


@dataclass(frozen=True)
class CapitalSessionLossLedger:
    ledger_id: str
    authority: str
    account_key: str
    lane: SimulationLane
    trading_date: str
    current_market_time_receipt_id: str
    current_market_time_integrity_hash: str
    entries: tuple[CapitalSessionLossEntry, ...]
    net_realized_pnl: float
    gross_realized_loss: float
    gross_realized_gain: float
    daily_loss_amount: float
    coverage_complete: bool
    unresolved_close_trade_ids: tuple[str, ...]
    integrity_hash: str


@dataclass(frozen=True)
class ExperimentalCapitalAdmission:
    admission_id: str
    authority: str
    account_key: str
    lane: SimulationLane
    frame_id: str
    decision_id: str
    assessment_id: str
    assessment_integrity_hash: str
    assessment_state: CapitalAssessmentState
    admitted: bool
    harness_mutated: bool
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


def _parse_frame_time(
    value: str,
) -> datetime:
    text = _nonblank(
        value,
        name="frame observed_at",
    )

    if text.endswith(
        "Z"
    ):
        text = (
            text[:-1]
            + "+00:00"
        )

    try:
        parsed = datetime.fromisoformat(
            text
        )

    except ValueError as exc:
        raise ValueError(
            "frame observed_at must be ISO-8601"
        ) from exc

    if (
        parsed.tzinfo is None
        or parsed.utcoffset() is None
    ):
        raise ValueError(
            "frame observed_at must be timezone-aware"
        )

    return parsed.astimezone(
        timezone.utc
    )


def _session_loss_entry_payload(
    entry: CapitalSessionLossEntry,
) -> dict[str, object]:
    return {
        "trade_id":
            entry.trade_id,

        "frame_id":
            entry.frame_id,

        "market_time_receipt_id":
            entry.market_time_receipt_id,

        "market_time_integrity_hash":
            entry.market_time_integrity_hash,

        "trading_date":
            entry.trading_date,

        "market_session":
            entry.market_session,

        "realized_pnl":
            entry.realized_pnl,
    }


def _session_loss_material(
    ledger: CapitalSessionLossLedger,
) -> dict[str, object]:
    return {
        "authority":
            ledger.authority,

        "account_key":
            ledger.account_key,

        "lane":
            ledger.lane.value,

        "trading_date":
            ledger.trading_date,

        "current_market_time_receipt_id":
            ledger.current_market_time_receipt_id,

        "current_market_time_integrity_hash":
            ledger.current_market_time_integrity_hash,

        "entries": [
            _session_loss_entry_payload(
                item
            )
            for item
            in ledger.entries
        ],

        "net_realized_pnl":
            ledger.net_realized_pnl,

        "gross_realized_loss":
            ledger.gross_realized_loss,

        "gross_realized_gain":
            ledger.gross_realized_gain,

        "daily_loss_amount":
            ledger.daily_loss_amount,

        "coverage_complete":
            ledger.coverage_complete,

        "unresolved_close_trade_ids":
            list(
                ledger.unresolved_close_trade_ids
            ),
    }


def verify_capital_session_loss_ledger(
    ledger: CapitalSessionLossLedger,
) -> bool:
    if not isinstance(
        ledger,
        CapitalSessionLossLedger,
    ):
        return False

    if (
        ledger.authority
        !=
        SESSION_LOSS_AUTHORITY
    ):
        return False

    if (
        ledger.lane
        is not
        SimulationLane.EXPERIMENTAL
    ):
        return False

    if (
        ledger.coverage_complete
        !=
        (
            len(
                ledger.unresolved_close_trade_ids
            )
            == 0
        )
    ):
        return False

    expected_net = round(
        sum(
            item.realized_pnl
            for item
            in ledger.entries
        ),
        4,
    )

    expected_loss = round(
        sum(
            -item.realized_pnl
            for item
            in ledger.entries
            if item.realized_pnl < 0
        ),
        4,
    )

    expected_gain = round(
        sum(
            item.realized_pnl
            for item
            in ledger.entries
            if item.realized_pnl > 0
        ),
        4,
    )

    expected_daily_loss = round(
        max(
            0.0,
            -expected_net,
        ),
        4,
    )

    if (
        ledger.net_realized_pnl
        != expected_net
        or
        ledger.gross_realized_loss
        != expected_loss
        or
        ledger.gross_realized_gain
        != expected_gain
        or
        ledger.daily_loss_amount
        != expected_daily_loss
    ):
        return False

    digest = stable_hash(
        _session_loss_material(
            ledger
        )
    )

    return (
        ledger.integrity_hash
        == digest
        and
        ledger.ledger_id
        ==
        "OBCAPLOSS-"
        + digest[:24]
    )


def build_capital_session_loss_ledger(
    harness: MultiSimulationHarness,
    *,
    market_time,
    market_time_receipts: Iterable[Any] = (),
) -> CapitalSessionLossLedger:
    from web.ob_market_time_authority import (
        MarketTimeState,
        verify_canonical_market_time_receipt,
    )

    if not isinstance(
        harness,
        MultiSimulationHarness,
    ):
        raise ValueError(
            "session loss ledger requires MultiSimulationHarness"
        )

    if not verify_canonical_market_time_receipt(
        market_time
    ):
        raise ValueError(
            "session loss ledger requires verified canonical market time"
        )

    if (
        market_time.state
        is MarketTimeState.SCHEDULE_DATE_MISMATCH
    ):
        raise ValueError(
            "session loss ledger cannot use schedule-date-mismatched market time"
        )

    state = lane_state(
        harness,
        SimulationLane.EXPERIMENTAL,
    )

    if not verify_lane_receipt_chain(
        state
    ):
        raise ValueError(
            "Experimental lane receipt chain failed verification"
        )

    receipt_map = {}

    supplied = (
        (
            market_time,
        )
        +
        tuple(
            market_time_receipts
        )
    )

    for receipt in supplied:
        if not verify_canonical_market_time_receipt(
            receipt
        ):
            raise ValueError(
                "session loss history contains unverified canonical market time"
            )

        if (
            receipt.state
            is MarketTimeState.SCHEDULE_DATE_MISMATCH
        ):
            raise ValueError(
                "session loss history contains schedule-date mismatch"
            )

        existing = receipt_map.get(
            receipt.receipt_id
        )

        if (
            existing is not None
            and
            existing.integrity_hash
            !=
            receipt.integrity_hash
        ):
            raise ValueError(
                "duplicate market-time receipt ID has conflicting integrity hash"
            )

        receipt_map[
            receipt.receipt_id
        ] = receipt

    bindings = {}

    for binding in state.time_bindings:
        if (
            binding.frame_id
            in bindings
        ):
            raise ValueError(
                "duplicate Experimental time binding for frame"
            )

        bindings[
            binding.frame_id
        ] = binding

    frames = {}

    for frame in harness.market_frames:
        if (
            frame.frame_id
            in frames
        ):
            raise ValueError(
                "duplicate market frame ID in harness"
            )

        frames[
            frame.frame_id
        ] = frame

    target_date = (
        market_time.trading_date.isoformat()
    )

    entries = []
    unresolved = []

    for trade in state.trades:
        if (
            trade.action
            is not
            SimulationAction.CLOSE
        ):
            continue

        binding = bindings.get(
            trade.frame_id
        )

        if binding is None:
            unresolved.append(
                trade.trade_id
            )
            continue

        receipt = receipt_map.get(
            binding.market_time_receipt_id
        )

        if receipt is None:
            unresolved.append(
                trade.trade_id
            )
            continue

        if (
            receipt.integrity_hash
            !=
            binding.market_time_integrity_hash
        ):
            raise ValueError(
                "Experimental time binding integrity does not match verified receipt"
            )

        if (
            receipt.authority
            !=
            binding.authority
            or
            receipt.trading_date.isoformat()
            !=
            binding.trading_date
            or
            receipt.market_session.value
            !=
            binding.market_session
            or
            receipt.state.value
            !=
            binding.state
        ):
            raise ValueError(
                "Experimental time binding disagrees with verified receipt"
            )

        frame = frames.get(
            trade.frame_id
        )

        if frame is None:
            raise ValueError(
                "simulation trade references missing market frame"
            )

        if (
            _parse_frame_time(
                frame.observed_at
            )
            !=
            receipt.observed_at_utc
        ):
            raise ValueError(
                "simulation frame timestamp disagrees with verified market time"
            )

        if (
            binding.trading_date
            !=
            target_date
        ):
            continue

        entries.append(
            CapitalSessionLossEntry(
                trade_id=trade.trade_id,
                frame_id=trade.frame_id,
                market_time_receipt_id=receipt.receipt_id,
                market_time_integrity_hash=receipt.integrity_hash,
                trading_date=binding.trading_date,
                market_session=binding.market_session,
                realized_pnl=round(
                    float(
                        trade.realized_pnl
                    ),
                    4,
                ),
            )
        )

    entries_tuple = tuple(
        entries
    )

    unresolved_tuple = tuple(
        sorted(
            set(
                unresolved
            )
        )
    )

    net = round(
        sum(
            item.realized_pnl
            for item
            in entries_tuple
        ),
        4,
    )

    gross_loss = round(
        sum(
            -item.realized_pnl
            for item
            in entries_tuple
            if item.realized_pnl < 0
        ),
        4,
    )

    gross_gain = round(
        sum(
            item.realized_pnl
            for item
            in entries_tuple
            if item.realized_pnl > 0
        ),
        4,
    )

    daily_loss = round(
        max(
            0.0,
            -net,
        ),
        4,
    )

    provisional = CapitalSessionLossLedger(
        ledger_id="PENDING",
        authority=SESSION_LOSS_AUTHORITY,
        account_key=_nonblank(
            harness.account_key,
            name="harness account_key",
        ),
        lane=SimulationLane.EXPERIMENTAL,
        trading_date=target_date,
        current_market_time_receipt_id=market_time.receipt_id,
        current_market_time_integrity_hash=market_time.integrity_hash,
        entries=entries_tuple,
        net_realized_pnl=net,
        gross_realized_loss=gross_loss,
        gross_realized_gain=gross_gain,
        daily_loss_amount=daily_loss,
        coverage_complete=(
            len(
                unresolved_tuple
            )
            == 0
        ),
        unresolved_close_trade_ids=unresolved_tuple,
        integrity_hash="PENDING",
    )

    digest = stable_hash(
        _session_loss_material(
            provisional
        )
    )

    result = CapitalSessionLossLedger(
        ledger_id=(
            "OBCAPLOSS-"
            + digest[:24]
        ),
        authority=provisional.authority,
        account_key=provisional.account_key,
        lane=provisional.lane,
        trading_date=provisional.trading_date,
        current_market_time_receipt_id=provisional.current_market_time_receipt_id,
        current_market_time_integrity_hash=provisional.current_market_time_integrity_hash,
        entries=provisional.entries,
        net_realized_pnl=provisional.net_realized_pnl,
        gross_realized_loss=provisional.gross_realized_loss,
        gross_realized_gain=provisional.gross_realized_gain,
        daily_loss_amount=provisional.daily_loss_amount,
        coverage_complete=provisional.coverage_complete,
        unresolved_close_trade_ids=provisional.unresolved_close_trade_ids,
        integrity_hash=digest,
    )

    if not verify_capital_session_loss_ledger(
        result
    ):
        raise ValueError(
            "constructed capital session loss ledger failed verification"
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

        "session_loss_ledger_id":
            assessment.session_loss_ledger_id,

        "session_loss_integrity_hash":
            assessment.session_loss_integrity_hash,

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

    if (
        (
            assessment.session_loss_ledger_id
            is None
        )
        !=
        (
            assessment.session_loss_integrity_hash
            is None
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
    session_loss: CapitalSessionLossLedger | None = None,
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

    session_loss_ledger_id = None
    session_loss_integrity_hash = None

    if session_loss is not None:
        if not verify_capital_session_loss_ledger(
            session_loss
        ):
            raise ValueError(
                "capital session loss ledger failed verification"
            )

        if (
            session_loss.account_key
            !=
            policy.account_key
        ):
            raise ValueError(
                "session loss ledger crosses account boundary"
            )

        if (
            session_loss.lane
            is not
            capital_state.lane
        ):
            raise ValueError(
                "session loss ledger crosses simulation lane boundary"
            )

        session_loss_ledger_id = (
            session_loss.ledger_id
        )

        session_loss_integrity_hash = (
            session_loss.integrity_hash
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

    if session_loss is None:
        daily_loss_pct = None

        daily_state = (
            CapitalCheckState.REVIEW
        )

        daily_reason = (
            "Canonical session-loss ledger was not supplied."
        )

    elif not session_loss.coverage_complete:
        daily_loss_pct = None

        daily_state = (
            CapitalCheckState.UNKNOWN
        )

        daily_reason = (
            "Historical CLOSE trade time coverage is incomplete."
        )

    elif (
        capital_state.equity
        <= 0
    ):
        daily_loss_pct = None

        daily_state = (
            CapitalCheckState.BLOCK
        )

        daily_reason = (
            "Lane equity is not positive, so daily-loss admission is blocked."
        )

    else:
        current_daily_loss_pct = round(
            (
                session_loss.daily_loss_amount
                /
                capital_state.equity
            )
            * 100.0,
            6,
        )

        if (
            current_daily_loss_pct
            >
            policy.daily_loss_cap_pct
        ):
            daily_loss_pct = (
                current_daily_loss_pct
            )

            daily_state = (
                CapitalCheckState.BLOCK
            )

            daily_reason = (
                "Verified realized daily loss already exceeds Effective Policy cap."
            )

        elif (
            proposal.declared_max_loss_amount
            is None
        ):
            daily_loss_pct = (
                current_daily_loss_pct
            )

            daily_state = (
                CapitalCheckState.REVIEW
            )

            daily_reason = (
                "Current daily loss is known, but proposed maximum loss is not proven."
            )

        else:
            projected_daily_loss_amount = round(
                session_loss.daily_loss_amount
                + proposal.declared_max_loss_amount,
                4,
            )

            projected_daily_loss_pct = round(
                (
                    projected_daily_loss_amount
                    /
                    capital_state.equity
                )
                * 100.0,
                6,
            )

            daily_loss_pct = (
                projected_daily_loss_pct
            )

            daily_state = (
                CapitalCheckState.BLOCK
                if (
                    projected_daily_loss_pct
                    >
                    policy.daily_loss_cap_pct
                )
                else
                CapitalCheckState.PASS
            )

            daily_reason = (
                "Projected daily loss exceeds Effective Policy cap."
                if (
                    daily_state
                    is CapitalCheckState.BLOCK
                )
                else
                "Projected daily loss remains within Effective Policy cap."
            )

    checks.append(
        CapitalCheck(
            name="daily_loss_cap",
            state=daily_state,
            observed_value=daily_loss_pct,
            limit_value=policy.daily_loss_cap_pct,
            unit="percentage_points",
            reason=daily_reason,
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
        session_loss_ledger_id=session_loss_ledger_id,
        session_loss_integrity_hash=session_loss_integrity_hash,
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
        session_loss_ledger_id=provisional.session_loss_ledger_id,
        session_loss_integrity_hash=provisional.session_loss_integrity_hash,
        integrity_hash=digest,
    )

    if not verify_capital_simulation_assessment(
        result
    ):
        raise ValueError(
            "constructed capital simulation assessment failed verification"
        )

    return result


def _current_frame_time_binding(
    harness: MultiSimulationHarness,
    *,
    frame: SimulationMarketFrame,
    market_time,
):
    from web.ob_market_time_authority import (
        MarketTimeState,
        verify_canonical_market_time_receipt,
    )

    if not verify_canonical_market_time_receipt(
        market_time
    ):
        raise ValueError(
            "Experimental capital admission requires verified canonical market time"
        )

    if (
        market_time.state
        is MarketTimeState.SCHEDULE_DATE_MISMATCH
    ):
        raise ValueError(
            "Experimental capital admission rejects schedule-date mismatch"
        )

    state = lane_state(
        harness,
        SimulationLane.EXPERIMENTAL,
    )

    matches = [
        item
        for item
        in state.time_bindings
        if (
            item.frame_id
            ==
            frame.frame_id
        )
    ]

    if len(
        matches
    ) != 1:
        raise ValueError(
            "Experimental OPEN requires exactly one canonical time binding for frame"
        )

    binding = matches[0]

    if (
        binding.market_time_receipt_id
        !=
        market_time.receipt_id
        or
        binding.market_time_integrity_hash
        !=
        market_time.integrity_hash
        or
        binding.authority
        !=
        market_time.authority
        or
        binding.trading_date
        !=
        market_time.trading_date.isoformat()
        or
        binding.market_session
        !=
        market_time.market_session.value
        or
        binding.state
        !=
        market_time.state.value
    ):
        raise ValueError(
            "Experimental frame time binding disagrees with verified market time"
        )

    if (
        _parse_frame_time(
            frame.observed_at
        )
        !=
        market_time.observed_at_utc
    ):
        raise ValueError(
            "Experimental frame timestamp disagrees with verified market time"
        )

    return binding


def _admission_material(
    admission: ExperimentalCapitalAdmission,
) -> dict[str, object]:
    return {
        "authority":
            admission.authority,

        "account_key":
            admission.account_key,

        "lane":
            admission.lane.value,

        "frame_id":
            admission.frame_id,

        "decision_id":
            admission.decision_id,

        "assessment_id":
            admission.assessment_id,

        "assessment_integrity_hash":
            admission.assessment_integrity_hash,

        "assessment_state":
            admission.assessment_state.value,

        "admitted":
            admission.admitted,

        "harness_mutated":
            admission.harness_mutated,
    }


def verify_experimental_capital_admission(
    admission: ExperimentalCapitalAdmission,
) -> bool:
    if not isinstance(
        admission,
        ExperimentalCapitalAdmission,
    ):
        return False

    if (
        admission.authority
        !=
        SCHEMA_VERSION
        or
        admission.lane
        is not
        SimulationLane.EXPERIMENTAL
    ):
        return False

    expected_admitted = (
        admission.assessment_state
        is CapitalAssessmentState.ALLOW
    )

    if (
        admission.admitted
        != expected_admitted
    ):
        return False

    if (
        admission.harness_mutated
        != admission.admitted
    ):
        return False

    digest = stable_hash(
        _admission_material(
            admission
        )
    )

    return (
        admission.integrity_hash
        == digest
        and
        admission.admission_id
        ==
        "OBCAPADMIT-"
        + digest[:24]
    )


def _build_experimental_capital_admission(
    *,
    account_key: str,
    frame_id: str,
    decision_id: str,
    assessment: CapitalSimulationAssessment,
) -> ExperimentalCapitalAdmission:
    admitted = (
        assessment.state
        is CapitalAssessmentState.ALLOW
    )

    provisional = ExperimentalCapitalAdmission(
        admission_id="PENDING",
        authority=SCHEMA_VERSION,
        account_key=_nonblank(
            account_key,
            name="account_key",
        ),
        lane=SimulationLane.EXPERIMENTAL,
        frame_id=_nonblank(
            frame_id,
            name="frame_id",
        ),
        decision_id=_nonblank(
            decision_id,
            name="decision_id",
        ),
        assessment_id=assessment.assessment_id,
        assessment_integrity_hash=assessment.integrity_hash,
        assessment_state=assessment.state,
        admitted=admitted,
        harness_mutated=admitted,
        integrity_hash="PENDING",
    )

    digest = stable_hash(
        _admission_material(
            provisional
        )
    )

    result = ExperimentalCapitalAdmission(
        admission_id=(
            "OBCAPADMIT-"
            + digest[:24]
        ),
        authority=provisional.authority,
        account_key=provisional.account_key,
        lane=provisional.lane,
        frame_id=provisional.frame_id,
        decision_id=provisional.decision_id,
        assessment_id=provisional.assessment_id,
        assessment_integrity_hash=provisional.assessment_integrity_hash,
        assessment_state=provisional.assessment_state,
        admitted=provisional.admitted,
        harness_mutated=provisional.harness_mutated,
        integrity_hash=digest,
    )

    if not verify_experimental_capital_admission(
        result
    ):
        raise ValueError(
            "constructed Experimental capital admission failed verification"
        )

    return result


def apply_experimental_open_with_capital_admission(
    harness: MultiSimulationHarness,
    *,
    effective_policy: dict[str, Any],
    frame: SimulationMarketFrame,
    market_time,
    market_time_receipts: Iterable[Any] = (),
    decision_id: str,
    strategy: str,
    reason: str,
    quantity: int,
    declared_max_loss_amount: float | None,
    risk_reference: str | None,
    evidence_refs: Iterable[str] = (),
    fill_policy: SimulationFillPolicy = SimulationFillPolicy(),
) -> tuple[
    MultiSimulationHarness,
    ExperimentalCapitalAdmission,
    CapitalSimulationAssessment,
]:
    if not isinstance(
        harness,
        MultiSimulationHarness,
    ):
        raise ValueError(
            "Experimental capital admission requires MultiSimulationHarness"
        )

    if (
        harness.account_key
        !=
        effective_policy.get(
            "account_key"
        )
    ):
        raise ValueError(
            "Experimental capital admission crosses account boundary"
        )

    _current_frame_time_binding(
        harness,
        frame=frame,
        market_time=market_time,
    )

    control_before = lane_state(
        harness,
        SimulationLane.CONTROL,
    )

    integrated_before = lane_state(
        harness,
        SimulationLane.INTEGRATED,
    )

    experimental_before = lane_state(
        harness,
        SimulationLane.EXPERIMENTAL,
    )

    policy = (
        build_capital_policy_snapshot(
            effective_policy
        )
    )

    capital_state = (
        build_simulation_capital_state(
            harness,
            lane=SimulationLane.EXPERIMENTAL,
        )
    )

    ledger = (
        build_capital_session_loss_ledger(
            harness,
            market_time=market_time,
            market_time_receipts=market_time_receipts,
        )
    )

    preview = (
        preview_simulation_open_cost(
            frame,
            quantity=quantity,
            fill_policy=fill_policy,
        )
    )

    proposal = (
        build_capital_proposal(
            account_key=harness.account_key,
            lane=SimulationLane.EXPERIMENTAL,
            capital_required=float(
                preview[
                    "total_cost"
                ]
            ),
            declared_max_loss_amount=declared_max_loss_amount,
            risk_reference=risk_reference,
        )
    )

    assessment = (
        assess_capital_proposal(
            policy=policy,
            capital_state=capital_state,
            proposal=proposal,
            session_loss=ledger,
        )
    )

    admission = (
        _build_experimental_capital_admission(
            account_key=harness.account_key,
            frame_id=frame.frame_id,
            decision_id=decision_id,
            assessment=assessment,
        )
    )

    if not admission.admitted:
        if (
            lane_state(
                harness,
                SimulationLane.CONTROL,
            )
            !=
            control_before
            or
            lane_state(
                harness,
                SimulationLane.INTEGRATED,
            )
            !=
            integrated_before
            or
            lane_state(
                harness,
                SimulationLane.EXPERIMENTAL,
            )
            !=
            experimental_before
        ):
            raise RuntimeError(
                "blocked capital admission unexpectedly mutated simulation harness"
            )

        return (
            harness,
            admission,
            assessment,
        )

    refs = tuple(
        _nonblank(
            item,
            name="evidence_ref",
        )
        for item
        in evidence_refs
    )

    refs = (
        refs
        +
        (
            assessment.assessment_id,
            ledger.ledger_id,
            policy.snapshot_id,
        )
    )

    updated = (
        apply_simulation_decision(
            harness,
            lane=SimulationLane.EXPERIMENTAL,
            frame=frame,
            decision_id=decision_id,
            action=SimulationAction.OPEN,
            strategy=strategy,
            reason=reason,
            quantity=quantity,
            evidence_refs=refs,
            fill_policy=fill_policy,
        )
    )

    if (
        lane_state(
            updated,
            SimulationLane.CONTROL,
        )
        !=
        control_before
    ):
        raise RuntimeError(
            "Experimental capital admission mutated CONTROL"
        )

    if (
        lane_state(
            updated,
            SimulationLane.INTEGRATED,
        )
        !=
        integrated_before
    ):
        raise RuntimeError(
            "Experimental capital admission mutated INTEGRATED"
        )

    experimental_after = lane_state(
        updated,
        SimulationLane.EXPERIMENTAL,
    )

    matches = [
        item
        for item
        in experimental_after.decisions
        if (
            item.decision_id
            ==
            decision_id
        )
    ]

    if len(
        matches
    ) != 1:
        raise RuntimeError(
            "admitted Experimental decision did not resolve exactly once"
        )

    if (
        assessment.assessment_id
        not in
        matches[0].evidence_refs
        or
        ledger.ledger_id
        not in
        matches[0].evidence_refs
        or
        policy.snapshot_id
        not in
        matches[0].evidence_refs
    ):
        raise RuntimeError(
            "admitted Experimental decision is missing CAPSIM evidence"
        )

    return (
        updated,
        admission,
        assessment,
    )


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
            True,

        "daily_loss_authority":
            SESSION_LOSS_AUTHORITY,

        "future_daily_loss_authority":
            None,

        "session_loss_basis":
            "NET_REALIZED_PNL_BY_OBTIME_TRADING_DATE",

        "session_loss_receipt_coverage_required":
            True,

        "projected_daily_loss_includes_declared_trade_loss":
            True,

        "daily_loss_missing_behavior":
            "REVIEW_REQUIRED",

        "daily_loss_incomplete_coverage_behavior":
            "UNKNOWN",

        "experimental_open_admission":
            True,

        "experimental_open_admission_scope":
            "EXPERIMENTAL_ONLY",

        "experimental_open_requires_allow":
            True,

        "delegates_existing_obsim_open_path":
            True,

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

        "session_loss_ledger_id":
            assessment.session_loss_ledger_id,

        "session_loss_integrity_hash":
            assessment.session_loss_integrity_hash,

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
