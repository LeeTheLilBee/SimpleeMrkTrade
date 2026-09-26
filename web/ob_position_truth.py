"""OBPOS001–005: position truth views over existing canonical sources.

No second fill/position ledger: reconcile OBSIM's already-executed simulation
fills, source receipts, current marks and positions, or expose OBENG's existing
explicit-store status. Neither path claims authenticated broker/live positions.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict, replace
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
import re

from web.ob_account_identity_truth import resolve_account_identity
from web.ob_multi_simulation_harness import (
    MultiSimulationHarness, SimulationAction, SimulationLane, SimulationPosition,
    lane_state, stable_hash, verify_lane_receipt_chain,
)
from web.ob_engine_account_authority import build_account_authority, build_position_authority

SCHEMA_VERSION = "OB_POSITION_TRUTH_V1"
SOURCE_AUTHORITY = "OB_MULTI_SIMULATION_V1"
REPOSITORY_AUTHORITY = "OB_ENGINE_ACCOUNT_AUTHORITY_V1"
HASH = re.compile(r"[0-9a-f]{64}")


def _digest(value: object) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()


def _close(left: float, right: float) -> bool:
    return math.isfinite(left) and math.isfinite(right) and math.isclose(
        left, right, rel_tol=0, abs_tol=0.00011,
    )


def _identity(key: str) -> dict[str, object]:
    value = resolve_account_identity(key)
    if value["known"] is not True:
        raise ValueError("explicit canonical account identity is required")
    return value


def _instant(value: str) -> datetime:
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None or dt.utcoffset() is None:
            raise ValueError("timezone missing")
        return dt.astimezone(timezone.utc)
    except (ValueError, TypeError, AttributeError) as exc:
        raise ValueError("position source needs timezone-aware as-of") from exc


@dataclass(frozen=True)
class PositionView:
    position_id: str
    source_open_trade_id: str
    symbol: str
    instrument_kind: str
    contract_id: str | None
    quantity: int
    multiplier: int
    entry_fill_price: float
    entry_commission: float
    latest_mark_price: float
    entry_frame_id: str
    last_frame_id: str
    strategy: str
    source_truth: str


@dataclass(frozen=True)
class PositionSnapshot:
    snapshot_id: str
    authority: str
    account_key: str
    account_identity_fingerprint: str
    harness_id: str
    lane: str
    build_ref: str
    as_of_utc: str | None
    source_role: str
    source_receipt_root: str | None
    source_trade_ids: tuple[str, ...]
    open_positions: tuple[PositionView, ...]
    source_equity: float
    source_cash: float
    source_realized_pnl: float
    source_unrealized_pnl: float
    simulation_only: bool
    broker_authenticated: bool
    trading_authority: bool
    capital_movement: bool
    integrity_hash: str


def _snapshot_material(value: PositionSnapshot) -> dict[str, object]:
    return {
        key: [asdict(p) for p in value.open_positions] if key == "open_positions" else getattr(value, key)
        for key in PositionSnapshot.__dataclass_fields__
        if key not in ("snapshot_id", "integrity_hash")
    }


def _checked_lane(harness: MultiSimulationHarness, selected: SimulationLane):
    if not isinstance(harness, MultiSimulationHarness) or not isinstance(selected, SimulationLane):
        raise ValueError("OBPOS requires OBSIM source and explicit lane enum")
    identity = _identity(harness.account_key)
    if len(harness.lanes) != 3 or {x.lane for x in harness.lanes} != set(SimulationLane):
        raise ValueError("exactly three independent canonical lanes required")
    state = lane_state(harness, selected)
    if not verify_lane_receipt_chain(state):
        raise ValueError("OBSIM lane receipt chain failed")
    frame_by_id = {f.frame_id: f for f in harness.market_frames}
    if len(frame_by_id) != len(harness.market_frames):
        raise ValueError("duplicate source frame IDs")
    prior_time = None
    for frame in harness.market_frames:
        observed = _instant(frame.observed_at)
        if prior_time is not None and observed <= prior_time:
            raise ValueError("nonchronological source frame history")
        prior_time = observed
    return identity, state, frame_by_id


def _build(harness: MultiSimulationHarness, selected: SimulationLane) -> PositionSnapshot:
    identity, state, frame_by_id = _checked_lane(harness, selected)
    filled = {d.decision_id: d for d in state.decisions if d.status == "FILLED"}
    if len(filled) != sum(d.status == "FILLED" for d in state.decisions):
        raise ValueError("duplicate filled decision")
    open_by_key: dict[tuple[str, str, str | None], tuple[object, str]] = {}
    seen_trades: set[str] = set()
    realized = 0.0
    cash_effect = 0.0
    receipt_index = {(r.event_type, r.event_id) for r in state.receipts}
    if len(receipt_index) != len(state.receipts):
        raise ValueError("duplicate source receipt events")
    for trade in state.trades:
        if trade.lane is not selected or trade.trade_id in seen_trades:
            raise ValueError("cross-lane or duplicate source trade")
        seen_trades.add(trade.trade_id)
        kind = "TRADE_OPEN" if trade.action is SimulationAction.OPEN else "TRADE_CLOSE"
        if (kind, trade.trade_id) not in receipt_index or trade.frame_id not in frame_by_id:
            raise ValueError("source trade lacks matching receipt or market frame")
        decision = filled.get(trade.decision_id)
        if decision is None or decision.frame_id != trade.frame_id or decision.action is not trade.action:
            raise ValueError("source trade lacks matching filled decision")
        frame = frame_by_id[trade.frame_id]
        key = (trade.symbol, trade.instrument_kind, trade.contract_id)
        if key != (frame.instrument.symbol, frame.instrument.instrument_kind, frame.instrument.contract_id):
            raise ValueError("trade instrument differs from canonical market frame")
        if (trade.quantity < 1 or type(trade.quantity) is not int or
            trade.multiplier != frame.instrument.multiplier or
            not all(math.isfinite(v) for v in (trade.fill_price, trade.commission, trade.gross_value,
                                              trade.cash_effect, trade.realized_pnl)) or
            trade.fill_price <= 0 or trade.commission < 0):
            raise ValueError("invalid canonical simulation fill quantities")
        if not _close(trade.requested_price, frame.mark_price):
            raise ValueError("trade request price differs from source market frame")
        if not _close(trade.gross_value, round(trade.fill_price * trade.quantity * trade.multiplier, 4)):
            raise ValueError("source trade gross value mismatch")
        if trade.action is SimulationAction.OPEN:
            if key in open_by_key or not _close(trade.realized_pnl, 0) or not _close(
                trade.cash_effect, -round(trade.gross_value + trade.commission, 4)
            ):
                raise ValueError("invalid or duplicate source OPEN fill")
            position_id = "OBSIMPOS-" + stable_hash({
                "lane": selected.value, "decision_id": trade.decision_id,
                "frame_id": trade.frame_id, "symbol": trade.symbol,
                "instrument_kind": trade.instrument_kind, "contract_id": trade.contract_id,
            })[:24]
            open_by_key[key] = (trade, position_id)
        elif trade.action is SimulationAction.CLOSE:
            opened = open_by_key.pop(key, None)
            if opened is None:
                raise ValueError("source CLOSE lacks exact open instrument")
            original = opened[0]
            if trade.quantity != original.quantity or trade.multiplier != original.multiplier:
                raise ValueError("source CLOSE differs from full-open quantity")
            expected = round((trade.fill_price - original.fill_price) *
                             original.quantity * original.multiplier -
                             original.commission - trade.commission, 4)
            if not _close(trade.realized_pnl, expected) or not _close(
                trade.cash_effect, round(trade.gross_value - trade.commission, 4)
            ):
                raise ValueError("source CLOSE economics conflict with canonical OPEN")
            realized += trade.realized_pnl
        else:
            raise ValueError("position truth accepts only existing executed OPEN/CLOSE fills")
        cash_effect += trade.cash_effect
    existing = {
        (p.symbol, p.instrument_kind, p.contract_id): p for p in state.positions
    }
    if len(existing) != len(state.positions) or set(existing) != set(open_by_key):
        raise ValueError("source open store differs from filled trade history")
    views: list[PositionView] = []
    unrealized = 0.0
    market_value = 0.0
    for key, (trade, pid) in open_by_key.items():
        p: SimulationPosition = existing[key]
        if p.position_id != pid or p.quantity != trade.quantity or p.multiplier != trade.multiplier:
            raise ValueError("source position ID or quantity conflicts with OPEN receipt")
        if p.opened_frame_id != trade.frame_id or p.entry_price != trade.fill_price:
            raise ValueError("source position entry mismatches fill")
        if not _close(p.entry_commission, trade.commission) or p.strategy != trade.strategy:
            raise ValueError("source position strategy/commission mismatch")
        relevant = [f for f in harness.market_frames if (
            f.instrument.symbol, f.instrument.instrument_kind,
            f.instrument.contract_id,
        ) == key]
        if not relevant:
            raise ValueError("open position missing source market mark")
        latest = relevant[-1]
        if p.last_frame_id != latest.frame_id or not _close(p.current_price, latest.mark_price):
            raise ValueError("position latest mark conflicts with market frame")
        if p.instrument_kind not in ("OPTION", "STOCK") or (
            p.instrument_kind == "OPTION" and (not p.contract_id or p.multiplier != 100)
        ) or (p.instrument_kind == "STOCK" and (p.contract_id is not None or p.multiplier != 1)):
            raise ValueError("malformed stock/option position source")
        market_value += p.current_price * p.quantity * p.multiplier
        unrealized += (p.current_price - p.entry_price) * p.quantity * p.multiplier
        views.append(PositionView(
            position_id=p.position_id, source_open_trade_id=trade.trade_id,
            symbol=p.symbol, instrument_kind=p.instrument_kind,
            contract_id=p.contract_id, quantity=p.quantity, multiplier=p.multiplier,
            entry_fill_price=p.entry_price, entry_commission=p.entry_commission,
            latest_mark_price=p.current_price, entry_frame_id=p.opened_frame_id,
            last_frame_id=p.last_frame_id, strategy=p.strategy,
            source_truth="OBSIM_ONLY_NOT_BROKER",
        ))
    if not _close(state.cash, round(state.starting_capital + cash_effect, 4)):
        raise ValueError("source cash differs from recorded canonical fill effects")
    if not _close(state.realized_pnl, round(realized, 4)):
        raise ValueError("source realized P&L differs from CLOSE records")
    if not _close(state.unrealized_pnl, round(unrealized, 4)):
        raise ValueError("source unrealized P&L differs from existing marks")
    if not _close(state.equity, round(state.cash + market_value, 4)):
        raise ValueError("source equity differs from existing position marks")
    root = state.receipts[-1].integrity_hash if state.receipts else None
    provisional = PositionSnapshot(
        snapshot_id="PENDING", authority=SCHEMA_VERSION,
        account_key=harness.account_key,
        account_identity_fingerprint=identity["identity_fingerprint"],
        harness_id=harness.harness_id, lane=selected.value, build_ref=state.build_ref,
        as_of_utc=_instant(harness.market_frames[-1].observed_at).isoformat()
        if harness.market_frames else None,
        source_role="OBSIM_SIMULATED_LEDGER",
        source_receipt_root=root, source_trade_ids=tuple(t.trade_id for t in state.trades),
        open_positions=tuple(sorted(views, key=lambda p: p.position_id)),
        source_equity=state.equity, source_cash=state.cash,
        source_realized_pnl=state.realized_pnl, source_unrealized_pnl=state.unrealized_pnl,
        simulation_only=True, broker_authenticated=False,
        trading_authority=False, capital_movement=False, integrity_hash="PENDING",
    )
    digest = _digest(_snapshot_material(provisional))
    return replace(provisional, snapshot_id="OBPOS-" + digest[:24], integrity_hash=digest)


def verify_simulated_position_snapshot(
    snapshot: PositionSnapshot, harness: MultiSimulationHarness,
) -> bool:
    if not isinstance(snapshot, PositionSnapshot) or snapshot.authority != SCHEMA_VERSION:
        return False
    if snapshot.simulation_only is not True or snapshot.broker_authenticated is not False:
        return False
    if snapshot.trading_authority is not False or snapshot.capital_movement is not False:
        return False
    try:
        return snapshot == _build(harness, SimulationLane(snapshot.lane))
    except (ValueError, TypeError, AttributeError, KeyError):
        return False


def build_simulated_position_snapshot(
    harness: MultiSimulationHarness, *, lane: SimulationLane,
) -> PositionSnapshot:
    result = _build(harness, lane)
    if not verify_simulated_position_snapshot(result, harness):
        raise ValueError("simulation position snapshot failed independent verification")
    return result


def repository_position_source_summary(
    *, account_key: str, explicit_source_values: dict[str, object],
    source_ref: str, source_revision: str, source_payload_hash: str,
) -> dict[str, object]:
    identity = _identity(account_key)
    if not isinstance(explicit_source_values, dict):
        raise ValueError("repository source payload must be explicit dict")
    if not all(isinstance(x, str) and x.strip() for x in (source_ref, source_revision)):
        raise ValueError("source metadata required")
    if not isinstance(source_payload_hash, str) or not HASH.fullmatch(source_payload_hash):
        raise ValueError("source payload integrity reference required")
    # Delegate exclusively to existing OBENG source-role reconciliation. Do NOT
    # derive position rows from count or historical reporting.
    authority = build_account_authority(explicit_source_values)
    position = build_position_authority(explicit_source_values, authority)
    open_state = position["open_position_records"]
    closed_state = position["closed_position_records"]
    material = {
        "authority": SCHEMA_VERSION, "upstream_authority": REPOSITORY_AUTHORITY,
        "account_key": identity["account_key"],
        "account_identity_fingerprint": identity["identity_fingerprint"],
        "source_ref": source_ref, "source_revision": source_revision,
        "source_payload_hash": source_payload_hash,
        "open_source_state": open_state["authority_status"],
        "open_count": open_state["record_count"],
        "closed_source_state": closed_state["authority_status"],
        "closed_count": closed_state["record_count"],
        "repository_not_broker_authenticated": True,
        "empty_or_unreadable_means_zero": False,
        "historical_reporting_not_open_truth": True,
        "position_rows_reconstructed": False,
        "broker_submission": False, "capital_movement": False,
    }
    return {**material, "summary_hash": _digest(material)}


def position_truth_contract() -> dict[str, object]:
    return {
        "authority": SCHEMA_VERSION,
        "simulation_source": SOURCE_AUTHORITY,
        "repository_source": REPOSITORY_AUTHORITY,
        "account_identity_source": "OB_ACCOUNT_IDENTITY_TRUTH_V1",
        "new_fill_engine": False, "new_position_ledger": False,
        "simulation_receipt_and_trade_reconciliation": True,
        "explicit_store_absent_is_unknown_not_zero": True,
        "historical_reporting_never_open_position_truth": True,
        "broker_authenticated": False,
        "simulation_never_promoted_to_live": True,
        "cross_lane_aggregation": False,
        "direct_buybox_access": False, "teller_owns_acquisition_readiness": True,
        "execution_authority": False, "broker_submission": False,
        "capital_movement": False, "manual_live_unlock": False,
        "hybrid_unlock": False, "automated_unlock": False,
    }
