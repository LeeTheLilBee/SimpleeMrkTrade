from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
import json
from typing import Iterable


SCHEMA_VERSION = "OB_MULTI_SIMULATION_V1"
SERVICE_VERSION = "OBSIM001_005_MULTI_SIMULATION_HARNESS"

PENDING_TIME_AUTHORITY = "PENDING_OBTIME"

OPTION_MULTIPLIER = 100
STOCK_MULTIPLIER = 1


class SimulationLane(str, Enum):
    CONTROL = "CONTROL"
    INTEGRATED = "INTEGRATED"
    EXPERIMENTAL = "EXPERIMENTAL"


class SimulationAction(str, Enum):
    OPEN = "OPEN"
    CLOSE = "CLOSE"
    HOLD = "HOLD"
    SKIP = "SKIP"


@dataclass(frozen=True)
class SimulationFillPolicy:
    slippage_bps: float = 25.0
    per_unit_commission: float = 0.005
    minimum_commission: float = 1.0


@dataclass(frozen=True)
class SimulationInstrument:
    symbol: str
    instrument_kind: str
    contract_id: str | None
    multiplier: int


@dataclass(frozen=True)
class SimulationMarketFrame:
    frame_id: str
    observed_at: str
    instrument: SimulationInstrument
    mark_price: float
    underlying_price: float | None
    source_reference: str


@dataclass(frozen=True)
class SimulationDecisionRecord:
    decision_id: str
    lane: SimulationLane
    frame_id: str
    action: SimulationAction
    strategy: str
    quantity: int
    reason: str
    evidence_refs: tuple[str, ...]
    status: str


@dataclass(frozen=True)
class SimulationPosition:
    position_id: str
    symbol: str
    instrument_kind: str
    contract_id: str | None
    strategy: str
    quantity: int
    multiplier: int
    entry_price: float
    entry_commission: float
    current_price: float
    opened_frame_id: str
    last_frame_id: str


@dataclass(frozen=True)
class SimulationTrade:
    trade_id: str
    decision_id: str
    lane: SimulationLane
    frame_id: str
    action: SimulationAction
    symbol: str
    instrument_kind: str
    contract_id: str | None
    strategy: str
    quantity: int
    multiplier: int
    requested_price: float
    fill_price: float
    commission: float
    gross_value: float
    cash_effect: float
    realized_pnl: float


@dataclass(frozen=True)
class SimulationReviewRecord:
    review_id: str
    lane: SimulationLane
    subject_id: str
    note: str


@dataclass(frozen=True)
class SimulationReceipt:
    receipt_id: str
    lane: SimulationLane
    event_type: str
    event_id: str
    payload_hash: str
    prior_receipt_hash: str | None
    integrity_hash: str


@dataclass(frozen=True)
class SimulationTimeBinding:
    binding_id: str
    frame_id: str
    market_time_receipt_id: str
    market_time_integrity_hash: str
    authority: str
    trading_date: str
    market_session: str
    state: str


@dataclass(frozen=True)
class SimulationLaneState:
    lane: SimulationLane
    build_ref: str
    starting_capital: float
    cash: float
    realized_pnl: float
    unrealized_pnl: float
    equity: float
    peak_equity: float
    max_drawdown_pct: float
    positions: tuple[SimulationPosition, ...]
    decisions: tuple[SimulationDecisionRecord, ...]
    trades: tuple[SimulationTrade, ...]
    review_history: tuple[SimulationReviewRecord, ...]
    receipts: tuple[SimulationReceipt, ...]
    time_bindings: tuple[SimulationTimeBinding, ...]


@dataclass(frozen=True)
class MultiSimulationHarness:
    harness_id: str
    account_key: str
    lanes: tuple[SimulationLaneState, ...]
    market_frames: tuple[SimulationMarketFrame, ...]


def _nonblank(
    value: object,
    *,
    name: str,
) -> str:
    text = str(
        value
    ).strip()

    if not text:
        raise ValueError(
            f"{name} cannot be blank"
        )

    return text


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


def simulation_contract() -> dict[str, object]:
    return {
        "schema_version":
            SCHEMA_VERSION,

        "service_version":
            SERVICE_VERSION,

        "simulation_only":
            True,

        "lane_isolation_required":
            True,

        "shared_mutable_portfolio":
            False,

        "common_market_frame_supported":
            True,

        "independent_cash":
            True,

        "independent_positions":
            True,

        "independent_decisions":
            True,

        "independent_trades":
            True,

        "independent_drawdown":
            True,

        "independent_review_history":
            True,

        "independent_receipt_chain":
            True,

        "canonical_market_time_authority":
            False,

        "canonical_market_time_authority_available":
            "OB_MARKET_TIME_V1",

        "canonical_market_time_binding_scope":
            "EXPERIMENTAL_ONLY",

        "unbound_frame_time_authority":
            PENDING_TIME_AUTHORITY,

        "simulation_performance_grants_live_authority":
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
    }


def build_simulation_instrument(
    *,
    symbol: str,
    instrument_kind: str,
    contract_id: str | None = None,
) -> SimulationInstrument:
    clean_symbol = _nonblank(
        symbol,
        name="symbol",
    ).upper()

    kind = _nonblank(
        instrument_kind,
        name="instrument_kind",
    ).upper()

    if kind not in {
        "STOCK",
        "OPTION",
    }:
        raise ValueError(
            "simulation instrument_kind must be STOCK or OPTION"
        )

    clean_contract = (
        None
        if contract_id is None
        else str(
            contract_id
        ).strip()
        or None
    )

    if (
        kind == "OPTION"
        and clean_contract is None
    ):
        raise ValueError(
            "OPTION simulation requires contract_id"
        )

    if kind == "STOCK":
        clean_contract = None

    return SimulationInstrument(
        symbol=clean_symbol,
        instrument_kind=kind,
        contract_id=clean_contract,
        multiplier=(
            OPTION_MULTIPLIER
            if kind == "OPTION"
            else STOCK_MULTIPLIER
        ),
    )


def build_market_frame(
    *,
    frame_id: str,
    observed_at: str,
    instrument: SimulationInstrument,
    mark_price: float,
    source_reference: str,
    underlying_price: float | None = None,
) -> SimulationMarketFrame:
    if not isinstance(
        instrument,
        SimulationInstrument,
    ):
        raise ValueError(
            "instrument must be SimulationInstrument"
        )

    mark = _positive_float(
        mark_price,
        name="mark_price",
    )

    underlying = (
        None
        if underlying_price is None
        else _positive_float(
            underlying_price,
            name="underlying_price",
        )
    )

    return SimulationMarketFrame(
        frame_id=_nonblank(
            frame_id,
            name="frame_id",
        ),
        observed_at=_nonblank(
            observed_at,
            name="observed_at",
        ),
        instrument=instrument,
        mark_price=round(
            mark,
            4,
        ),
        underlying_price=(
            None
            if underlying is None
            else round(
                underlying,
                4,
            )
        ),
        source_reference=_nonblank(
            source_reference,
            name="source_reference",
        ),
    )


def _new_lane(
    *,
    lane: SimulationLane,
    build_ref: str,
    starting_capital: float,
) -> SimulationLaneState:
    capital = _positive_float(
        starting_capital,
        name="starting_capital",
    )

    capital = round(
        capital,
        4,
    )

    return SimulationLaneState(
        lane=lane,
        build_ref=_nonblank(
            build_ref,
            name=f"{lane.value} build_ref",
        ),
        starting_capital=capital,
        cash=capital,
        realized_pnl=0.0,
        unrealized_pnl=0.0,
        equity=capital,
        peak_equity=capital,
        max_drawdown_pct=0.0,
        positions=(),
        decisions=(),
        trades=(),
        review_history=(),
        receipts=(),
        time_bindings=(),
    )


def create_multi_simulation_harness(
    *,
    harness_id: str,
    account_key: str,
    starting_capital: float,
    control_ref: str,
    integrated_ref: str,
    experimental_ref: str,
) -> MultiSimulationHarness:
    return MultiSimulationHarness(
        harness_id=_nonblank(
            harness_id,
            name="harness_id",
        ),
        account_key=_nonblank(
            account_key,
            name="account_key",
        ),
        lanes=(
            _new_lane(
                lane=SimulationLane.CONTROL,
                build_ref=control_ref,
                starting_capital=starting_capital,
            ),
            _new_lane(
                lane=SimulationLane.INTEGRATED,
                build_ref=integrated_ref,
                starting_capital=starting_capital,
            ),
            _new_lane(
                lane=SimulationLane.EXPERIMENTAL,
                build_ref=experimental_ref,
                starting_capital=starting_capital,
            ),
        ),
        market_frames=(),
    )


def _instrument_key(
    instrument: SimulationInstrument,
) -> tuple[str, str, str | None]:
    return (
        instrument.symbol,
        instrument.instrument_kind,
        instrument.contract_id,
    )


def _position_key(
    position: SimulationPosition,
) -> tuple[str, str, str | None]:
    return (
        position.symbol,
        position.instrument_kind,
        position.contract_id,
    )


def lane_state(
    harness: MultiSimulationHarness,
    lane: SimulationLane | str,
) -> SimulationLaneState:
    selected = (
        lane
        if isinstance(
            lane,
            SimulationLane,
        )
        else SimulationLane(
            str(
                lane
            ).strip().upper()
        )
    )

    matches = [
        item
        for item in harness.lanes
        if item.lane is selected
    ]

    if len(matches) != 1:
        raise ValueError(
            "simulation lane does not resolve exactly once"
        )

    return matches[0]


def _replace_lane(
    harness: MultiSimulationHarness,
    updated: SimulationLaneState,
) -> MultiSimulationHarness:
    lanes = tuple(
        updated
        if item.lane is updated.lane
        else item
        for item in harness.lanes
    )

    return replace(
        harness,
        lanes=lanes,
    )


def _receipt_integrity_payload(
    *,
    lane: SimulationLane,
    event_type: str,
    event_id: str,
    payload_hash: str,
    prior_receipt_hash: str | None,
) -> dict[str, object]:
    return {
        "lane":
            lane.value,

        "event_type":
            event_type,

        "event_id":
            event_id,

        "payload_hash":
            payload_hash,

        "prior_receipt_hash":
            prior_receipt_hash,
    }


def _append_receipt(
    state: SimulationLaneState,
    *,
    event_type: str,
    event_id: str,
    payload: object,
) -> SimulationLaneState:
    payload_hash = stable_hash(
        payload
    )

    prior = (
        None
        if not state.receipts
        else state.receipts[-1].integrity_hash
    )

    integrity = stable_hash(
        _receipt_integrity_payload(
            lane=state.lane,
            event_type=_nonblank(
                event_type,
                name="event_type",
            ),
            event_id=_nonblank(
                event_id,
                name="event_id",
            ),
            payload_hash=payload_hash,
            prior_receipt_hash=prior,
        )
    )

    receipt = SimulationReceipt(
        receipt_id=(
            "OBSIM-"
            + integrity[:24]
        ),
        lane=state.lane,
        event_type=event_type,
        event_id=event_id,
        payload_hash=payload_hash,
        prior_receipt_hash=prior,
        integrity_hash=integrity,
    )

    return replace(
        state,
        receipts=(
            state.receipts
            + (
                receipt,
            )
        ),
    )


def verify_lane_receipt_chain(
    state: SimulationLaneState,
) -> bool:
    prior = None

    for receipt in state.receipts:
        if receipt.lane is not state.lane:
            return False

        if (
            receipt.prior_receipt_hash
            != prior
        ):
            return False

        expected = stable_hash(
            _receipt_integrity_payload(
                lane=receipt.lane,
                event_type=receipt.event_type,
                event_id=receipt.event_id,
                payload_hash=receipt.payload_hash,
                prior_receipt_hash=(
                    receipt.prior_receipt_hash
                ),
            )
        )

        if (
            receipt.integrity_hash
            != expected
        ):
            return False

        if (
            receipt.receipt_id
            != "OBSIM-" + expected[:24]
        ):
            return False

        prior = (
            receipt.integrity_hash
        )

    return True


def _revalue_lane(
    state: SimulationLaneState,
) -> SimulationLaneState:
    market_value = sum(
        (
            position.current_price
            * position.quantity
            * position.multiplier
        )
        for position
        in state.positions
    )

    unrealized = sum(
        (
            (
                position.current_price
                - position.entry_price
            )
            * position.quantity
            * position.multiplier
        )
        for position
        in state.positions
    )

    equity = round(
        state.cash
        + market_value,
        4,
    )

    peak = max(
        state.peak_equity,
        equity,
    )

    drawdown = (
        0.0
        if peak <= 0
        else round(
            (
                (
                    peak
                    - equity
                )
                / peak
            )
            * 100.0,
            6,
        )
    )

    return replace(
        state,
        unrealized_pnl=round(
            unrealized,
            4,
        ),
        equity=equity,
        peak_equity=round(
            peak,
            4,
        ),
        max_drawdown_pct=max(
            state.max_drawdown_pct,
            drawdown,
        ),
    )


def broadcast_market_frame(
    harness: MultiSimulationHarness,
    frame: SimulationMarketFrame,
) -> MultiSimulationHarness:
    if not isinstance(
        frame,
        SimulationMarketFrame,
    ):
        raise ValueError(
            "frame must be SimulationMarketFrame"
        )

    if any(
        existing.frame_id
        == frame.frame_id
        for existing
        in harness.market_frames
    ):
        raise ValueError(
            "duplicate simulation market frame"
        )

    frame_key = _instrument_key(
        frame.instrument
    )

    updated_lanes = []

    for state in harness.lanes:
        positions = tuple(
            replace(
                position,
                current_price=frame.mark_price,
                last_frame_id=frame.frame_id,
            )
            if _position_key(
                position
            ) == frame_key
            else position
            for position
            in state.positions
        )

        updated = replace(
            state,
            positions=positions,
        )

        updated = _revalue_lane(
            updated
        )

        updated = _append_receipt(
            updated,
            event_type="MARKET_FRAME",
            event_id=frame.frame_id,
            payload={
                "frame_id":
                    frame.frame_id,

                "observed_at":
                    frame.observed_at,

                "symbol":
                    frame.instrument.symbol,

                "instrument_kind":
                    frame.instrument.instrument_kind,

                "contract_id":
                    frame.instrument.contract_id,

                "mark_price":
                    frame.mark_price,

                "underlying_price":
                    frame.underlying_price,

                "source_reference":
                    frame.source_reference,

                "canonical_time_claimed":
                    False,

                "time_authority":
                    PENDING_TIME_AUTHORITY,
            },
        )

        updated_lanes.append(
            updated
        )

    return replace(
        harness,
        lanes=tuple(
            updated_lanes
        ),
        market_frames=(
            harness.market_frames
            + (
                frame,
            )
        ),
    )


def _parse_frame_observed_at(
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


def bind_canonical_market_time_to_experimental(
    harness: MultiSimulationHarness,
    *,
    frame: SimulationMarketFrame,
    market_time,
) -> MultiSimulationHarness:
    from web.ob_market_time_authority import (
        MarketTimeState,
        market_time_reference,
        verify_canonical_market_time_receipt,
    )

    if not isinstance(
        frame,
        SimulationMarketFrame,
    ):
        raise ValueError(
            "frame must be SimulationMarketFrame"
        )

    if not _frame_is_broadcast(
        harness,
        frame,
    ):
        raise ValueError(
            "market frame must be broadcast before canonical time binding"
        )

    if not verify_canonical_market_time_receipt(
        market_time
    ):
        raise ValueError(
            "Experimental time binding requires verified canonical market time"
        )

    if (
        market_time.state
        is MarketTimeState.SCHEDULE_DATE_MISMATCH
    ):
        raise ValueError(
            "schedule-date mismatch cannot bind as Experimental canonical time"
        )

    frame_time = _parse_frame_observed_at(
        frame.observed_at
    )

    if (
        frame_time
        != market_time.observed_at_utc
    ):
        raise ValueError(
            "market frame observed_at does not match canonical market time"
        )

    state = lane_state(
        harness,
        SimulationLane.EXPERIMENTAL,
    )

    if any(
        item.frame_id
        == frame.frame_id
        for item
        in state.time_bindings
    ):
        raise ValueError(
            "Experimental frame already has canonical time binding"
        )

    reference = market_time_reference(
        market_time
    )

    material = {
        "lane":
            SimulationLane.EXPERIMENTAL.value,

        "frame_id":
            frame.frame_id,

        "market_time_reference":
            reference,
    }

    binding_hash = stable_hash(
        material
    )

    binding = SimulationTimeBinding(
        binding_id=(
            "OBSIMTIME-"
            + binding_hash[:24]
        ),
        frame_id=frame.frame_id,
        market_time_receipt_id=market_time.receipt_id,
        market_time_integrity_hash=market_time.integrity_hash,
        authority=market_time.authority,
        trading_date=market_time.trading_date.isoformat(),
        market_session=market_time.market_session.value,
        state=market_time.state.value,
    )

    updated = replace(
        state,
        time_bindings=(
            state.time_bindings
            + (
                binding,
            )
        ),
    )

    updated = _append_receipt(
        updated,
        event_type="CANONICAL_MARKET_TIME",
        event_id=binding.binding_id,
        payload={
            "binding_id":
                binding.binding_id,

            "frame_id":
                frame.frame_id,

            "canonical_time_claimed":
                True,

            "time_authority":
                market_time.authority,

            "market_time_reference":
                reference,

            "simulation_only":
                True,

            "execution_authority":
                False,

            "broker_submission":
                False,

            "capital_movement":
                False,

            "manual_live_unlock":
                False,

            "hybrid_unlock":
                False,

            "automated_unlock":
                False,
        },
    )

    return _replace_lane(
        harness,
        updated,
    )


def _fill_price(
    *,
    requested_price: float,
    side: str,
    policy: SimulationFillPolicy,
) -> float:
    price = _positive_float(
        requested_price,
        name="requested_price",
    )

    slip = (
        float(
            policy.slippage_bps
        )
        / 10000.0
    )

    normalized_side = _nonblank(
        side,
        name="side",
    ).upper()

    if normalized_side == "BUY":
        result = (
            price
            * (
                1.0
                + slip
            )
        )

    elif normalized_side == "SELL":
        result = (
            price
            * (
                1.0
                - slip
            )
        )

    else:
        raise ValueError(
            "simulation fill side must be BUY or SELL"
        )

    return round(
        result,
        4,
    )


def _commission(
    *,
    quantity: int,
    policy: SimulationFillPolicy,
) -> float:
    if (
        not isinstance(
            quantity,
            int,
        )
        or quantity < 1
    ):
        raise ValueError(
            "simulation quantity must be a positive integer"
        )

    return round(
        max(
            float(
                policy.minimum_commission
            ),
            (
                quantity
                * float(
                    policy.per_unit_commission
                )
            ),
        ),
        4,
    )


def _frame_is_broadcast(
    harness: MultiSimulationHarness,
    frame: SimulationMarketFrame,
) -> bool:
    return any(
        existing.frame_id
        == frame.frame_id
        for existing
        in harness.market_frames
    )


def apply_simulation_decision(
    harness: MultiSimulationHarness,
    *,
    lane: SimulationLane | str,
    frame: SimulationMarketFrame,
    decision_id: str,
    action: SimulationAction | str,
    strategy: str,
    reason: str,
    quantity: int = 0,
    evidence_refs: Iterable[str] = (),
    fill_policy: SimulationFillPolicy = SimulationFillPolicy(),
) -> MultiSimulationHarness:
    if not _frame_is_broadcast(
        harness,
        frame,
    ):
        raise ValueError(
            "market frame must be broadcast before lane decisions"
        )

    state = lane_state(
        harness,
        lane,
    )

    clean_decision_id = _nonblank(
        decision_id,
        name="decision_id",
    )

    if any(
        item.decision_id
        == clean_decision_id
        for item
        in state.decisions
    ):
        raise ValueError(
            "duplicate decision_id within simulation lane"
        )

    selected_action = (
        action
        if isinstance(
            action,
            SimulationAction,
        )
        else SimulationAction(
            str(
                action
            ).strip().upper()
        )
    )

    clean_strategy = _nonblank(
        strategy,
        name="strategy",
    ).upper()

    clean_reason = _nonblank(
        reason,
        name="reason",
    )

    refs = tuple(
        _nonblank(
            item,
            name="evidence_ref",
        )
        for item
        in evidence_refs
    )

    instrument_key = _instrument_key(
        frame.instrument
    )

    matching_positions = [
        item
        for item
        in state.positions
        if _position_key(
            item
        ) == instrument_key
    ]

    if selected_action in {
        SimulationAction.HOLD,
        SimulationAction.SKIP,
    }:
        if quantity not in {
            0,
        }:
            raise ValueError(
                "HOLD and SKIP decisions cannot carry quantity"
            )

        decision = SimulationDecisionRecord(
            decision_id=clean_decision_id,
            lane=state.lane,
            frame_id=frame.frame_id,
            action=selected_action,
            strategy=clean_strategy,
            quantity=0,
            reason=clean_reason,
            evidence_refs=refs,
            status=selected_action.value,
        )

        updated = replace(
            state,
            decisions=(
                state.decisions
                + (
                    decision,
                )
            ),
        )

        updated = _append_receipt(
            updated,
            event_type="DECISION",
            event_id=clean_decision_id,
            payload={
                "decision_id":
                    clean_decision_id,

                "frame_id":
                    frame.frame_id,

                "action":
                    selected_action.value,

                "strategy":
                    clean_strategy,

                "reason":
                    clean_reason,

                "evidence_refs":
                    list(
                        refs
                    ),
            },
        )

        return _replace_lane(
            harness,
            updated,
        )

    if (
        not isinstance(
            quantity,
            int,
        )
        or quantity < 1
    ):
        raise ValueError(
            "OPEN and CLOSE require positive integer quantity"
        )

    if selected_action is SimulationAction.OPEN:
        if matching_positions:
            raise ValueError(
                "simulation lane already has an open position for instrument"
            )

        fill = _fill_price(
            requested_price=frame.mark_price,
            side="BUY",
            policy=fill_policy,
        )

        commission = _commission(
            quantity=quantity,
            policy=fill_policy,
        )

        gross = round(
            (
                fill
                * quantity
                * frame.instrument.multiplier
            ),
            4,
        )

        total_cost = round(
            gross
            + commission,
            4,
        )

        if total_cost > state.cash:
            raise ValueError(
                "simulation lane has insufficient cash"
            )

        position_payload = {
            "lane":
                state.lane.value,

            "decision_id":
                clean_decision_id,

            "frame_id":
                frame.frame_id,

            "symbol":
                frame.instrument.symbol,

            "instrument_kind":
                frame.instrument.instrument_kind,

            "contract_id":
                frame.instrument.contract_id,
        }

        position_id = (
            "OBSIMPOS-"
            + stable_hash(
                position_payload
            )[:24]
        )

        position = SimulationPosition(
            position_id=position_id,
            symbol=frame.instrument.symbol,
            instrument_kind=frame.instrument.instrument_kind,
            contract_id=frame.instrument.contract_id,
            strategy=clean_strategy,
            quantity=quantity,
            multiplier=frame.instrument.multiplier,
            entry_price=fill,
            entry_commission=commission,
            current_price=frame.mark_price,
            opened_frame_id=frame.frame_id,
            last_frame_id=frame.frame_id,
        )

        trade_payload = {
            "lane":
                state.lane.value,

            "decision_id":
                clean_decision_id,

            "action":
                selected_action.value,

            "position_id":
                position_id,
        }

        trade_id = (
            "OBSIMTRD-"
            + stable_hash(
                trade_payload
            )[:24]
        )

        trade = SimulationTrade(
            trade_id=trade_id,
            decision_id=clean_decision_id,
            lane=state.lane,
            frame_id=frame.frame_id,
            action=selected_action,
            symbol=frame.instrument.symbol,
            instrument_kind=frame.instrument.instrument_kind,
            contract_id=frame.instrument.contract_id,
            strategy=clean_strategy,
            quantity=quantity,
            multiplier=frame.instrument.multiplier,
            requested_price=frame.mark_price,
            fill_price=fill,
            commission=commission,
            gross_value=gross,
            cash_effect=round(
                -total_cost,
                4,
            ),
            realized_pnl=0.0,
        )

        decision = SimulationDecisionRecord(
            decision_id=clean_decision_id,
            lane=state.lane,
            frame_id=frame.frame_id,
            action=selected_action,
            strategy=clean_strategy,
            quantity=quantity,
            reason=clean_reason,
            evidence_refs=refs,
            status="FILLED",
        )

        updated = replace(
            state,
            cash=round(
                state.cash
                - total_cost,
                4,
            ),
            positions=(
                state.positions
                + (
                    position,
                )
            ),
            decisions=(
                state.decisions
                + (
                    decision,
                )
            ),
            trades=(
                state.trades
                + (
                    trade,
                )
            ),
        )

        updated = _revalue_lane(
            updated
        )

        updated = _append_receipt(
            updated,
            event_type="TRADE_OPEN",
            event_id=trade_id,
            payload={
                "decision_id":
                    clean_decision_id,

                "trade_id":
                    trade_id,

                "position_id":
                    position_id,

                "frame_id":
                    frame.frame_id,

                "fill_price":
                    fill,

                "quantity":
                    quantity,

                "multiplier":
                    frame.instrument.multiplier,

                "commission":
                    commission,

                "simulation_only":
                    True,
            },
        )

        return _replace_lane(
            harness,
            updated,
        )

    if selected_action is SimulationAction.CLOSE:
        if len(
            matching_positions
        ) != 1:
            raise ValueError(
                "CLOSE requires exactly one matching open position"
            )

        position = (
            matching_positions[0]
        )

        if quantity != position.quantity:
            raise ValueError(
                "OBSIM001-005 supports full-position close only"
            )

        fill = _fill_price(
            requested_price=frame.mark_price,
            side="SELL",
            policy=fill_policy,
        )

        commission = _commission(
            quantity=quantity,
            policy=fill_policy,
        )

        gross = round(
            (
                fill
                * quantity
                * position.multiplier
            ),
            4,
        )

        proceeds = round(
            gross
            - commission,
            4,
        )

        realized = round(
            (
                (
                    fill
                    - position.entry_price
                )
                * quantity
                * position.multiplier
            )
            - position.entry_commission
            - commission,
            4,
        )

        trade_payload = {
            "lane":
                state.lane.value,

            "decision_id":
                clean_decision_id,

            "action":
                selected_action.value,

            "position_id":
                position.position_id,
        }

        trade_id = (
            "OBSIMTRD-"
            + stable_hash(
                trade_payload
            )[:24]
        )

        trade = SimulationTrade(
            trade_id=trade_id,
            decision_id=clean_decision_id,
            lane=state.lane,
            frame_id=frame.frame_id,
            action=selected_action,
            symbol=position.symbol,
            instrument_kind=position.instrument_kind,
            contract_id=position.contract_id,
            strategy=clean_strategy,
            quantity=quantity,
            multiplier=position.multiplier,
            requested_price=frame.mark_price,
            fill_price=fill,
            commission=commission,
            gross_value=gross,
            cash_effect=proceeds,
            realized_pnl=realized,
        )

        decision = SimulationDecisionRecord(
            decision_id=clean_decision_id,
            lane=state.lane,
            frame_id=frame.frame_id,
            action=selected_action,
            strategy=clean_strategy,
            quantity=quantity,
            reason=clean_reason,
            evidence_refs=refs,
            status="FILLED",
        )

        remaining = tuple(
            item
            for item
            in state.positions
            if item.position_id
            != position.position_id
        )

        updated = replace(
            state,
            cash=round(
                state.cash
                + proceeds,
                4,
            ),
            realized_pnl=round(
                state.realized_pnl
                + realized,
                4,
            ),
            positions=remaining,
            decisions=(
                state.decisions
                + (
                    decision,
                )
            ),
            trades=(
                state.trades
                + (
                    trade,
                )
            ),
        )

        updated = _revalue_lane(
            updated
        )

        updated = _append_receipt(
            updated,
            event_type="TRADE_CLOSE",
            event_id=trade_id,
            payload={
                "decision_id":
                    clean_decision_id,

                "trade_id":
                    trade_id,

                "position_id":
                    position.position_id,

                "frame_id":
                    frame.frame_id,

                "fill_price":
                    fill,

                "quantity":
                    quantity,

                "multiplier":
                    position.multiplier,

                "commission":
                    commission,

                "realized_pnl":
                    realized,

                "simulation_only":
                    True,
            },
        )

        return _replace_lane(
            harness,
            updated,
        )

    raise ValueError(
        "unsupported simulation action"
    )


def record_simulation_review(
    harness: MultiSimulationHarness,
    *,
    lane: SimulationLane | str,
    review_id: str,
    subject_id: str,
    note: str,
) -> MultiSimulationHarness:
    state = lane_state(
        harness,
        lane,
    )

    clean_review_id = _nonblank(
        review_id,
        name="review_id",
    )

    if any(
        item.review_id
        == clean_review_id
        for item
        in state.review_history
    ):
        raise ValueError(
            "duplicate review_id within simulation lane"
        )

    review = SimulationReviewRecord(
        review_id=clean_review_id,
        lane=state.lane,
        subject_id=_nonblank(
            subject_id,
            name="subject_id",
        ),
        note=_nonblank(
            note,
            name="note",
        ),
    )

    updated = replace(
        state,
        review_history=(
            state.review_history
            + (
                review,
            )
        ),
    )

    updated = _append_receipt(
        updated,
        event_type="REVIEW",
        event_id=clean_review_id,
        payload={
            "review_id":
                review.review_id,

            "subject_id":
                review.subject_id,

            "note":
                review.note,
        },
    )

    return _replace_lane(
        harness,
        updated,
    )


def lane_metrics(
    state: SimulationLaneState,
) -> dict[str, object]:
    return {
        "lane":
            state.lane.value,

        "build_ref":
            state.build_ref,

        "starting_capital":
            state.starting_capital,

        "cash":
            state.cash,

        "equity":
            state.equity,

        "realized_pnl":
            state.realized_pnl,

        "unrealized_pnl":
            state.unrealized_pnl,

        "max_drawdown_pct":
            state.max_drawdown_pct,

        "open_positions":
            len(
                state.positions
            ),

        "decisions":
            len(
                state.decisions
            ),

        "trades":
            len(
                state.trades
            ),

        "reviews":
            len(
                state.review_history
            ),

        "receipts":
            len(
                state.receipts
            ),

        "canonical_time_bindings":
            len(
                state.time_bindings
            ),

        "receipt_chain_valid":
            verify_lane_receipt_chain(
                state
            ),
    }


def compare_simulation_lanes(
    harness: MultiSimulationHarness,
) -> dict[str, object]:
    metrics = {
        state.lane.value:
            lane_metrics(
                state
            )
        for state
        in harness.lanes
    }

    starting = {
        state.starting_capital
        for state
        in harness.lanes
    }

    return {
        "harness_id":
            harness.harness_id,

        "account_key":
            harness.account_key,

        "market_frames":
            len(
                harness.market_frames
            ),

        "same_starting_capital":
            len(
                starting
            )
            == 1,

        "lanes":
            metrics,

        "ranking_generated":
            False,

        "winner_selected":
            False,

        "simulation_only":
            True,

        "live_authority":
            False,
    }


def harness_snapshot(
    harness: MultiSimulationHarness,
) -> dict[str, object]:
    comparison = compare_simulation_lanes(
        harness
    )

    return {
        "schema_version":
            SCHEMA_VERSION,

        "service_version":
            SERVICE_VERSION,

        "harness_id":
            harness.harness_id,

        "account_key":
            harness.account_key,

        "market_frame_ids": [
            frame.frame_id
            for frame
            in harness.market_frames
        ],

        "comparison":
            comparison,

        "authority_boundary":
            simulation_contract(),
    }
