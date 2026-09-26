"""OBPORT001–005: read-only source-bound portfolio comparison.

Projection only: consumes verified OBPOS per-lane views and the same OBSIM
harness. It neither aggregates three development lanes into one account nor
creates investment recommendations, real brokerage balances or deployable funds.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict, replace
from hashlib import sha256
import json
import math

from web.ob_multi_simulation_harness import (
    MultiSimulationHarness, SimulationLane, lane_state,
)
from web.ob_position_truth import (
    PositionSnapshot, build_simulated_position_snapshot,
    verify_simulated_position_snapshot,
)

SCHEMA_VERSION = "OB_PORTFOLIO_VIEW_V1"
LANES = tuple(SimulationLane)


def _hash(value: object) -> str:
    return sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    ).encode()).hexdigest()


@dataclass(frozen=True)
class LanePortfolioView:
    lane: str
    build_ref: str
    position_snapshot_id: str
    position_snapshot_hash: str
    source_receipt_root: str | None
    as_of_utc: str | None
    position_count: int
    option_position_count: int
    stock_position_count: int
    gross_market_exposure: float
    option_market_exposure: float
    stock_market_exposure: float
    gross_entry_cost_including_open_commissions: float
    simulated_cash: float
    simulated_equity: float
    simulated_realized_pnl: float
    simulated_unrealized_pnl: float
    source_truth: str
    source_verified_as_broker: bool
    deployable_for_acquisition: bool


@dataclass(frozen=True)
class PortfolioComparison:
    comparison_id: str
    authority: str
    account_key: str
    harness_id: str
    common_market_frame_ids: tuple[str, ...]
    lanes: tuple[LanePortfolioView, ...]
    ranking_generated: bool
    winner_selected: bool
    automatic_promotion: bool
    broker_authenticated: bool
    acquisition_readiness: str
    capital_movement: bool
    execution_authority: bool
    integrity_hash: str


def _lane_view(source: PositionSnapshot) -> LanePortfolioView:
    if not isinstance(source, PositionSnapshot):
        raise ValueError("portfolio requires canonical OBPOS input")
    positions = source.open_positions
    for p in positions:
        if (p.quantity < 1 or p.multiplier not in (1, 100)
            or not all(math.isfinite(v) and v >= 0 for v in (
                p.entry_fill_price, p.entry_commission, p.latest_mark_price,
            ))):
            raise ValueError("invalid canonical position projection")
    option_market = round(sum(p.quantity * p.multiplier * p.latest_mark_price
                              for p in positions if p.instrument_kind == "OPTION"), 4)
    stock_market = round(sum(p.quantity * p.multiplier * p.latest_mark_price
                             for p in positions if p.instrument_kind == "STOCK"), 4)
    total = round(option_market + stock_market, 4)
    entry = round(sum(
        p.quantity * p.multiplier * p.entry_fill_price + p.entry_commission
        for p in positions
    ), 4)
    if not math.isclose(
        round(source.source_cash + total, 4), source.source_equity,
        abs_tol=0.00011, rel_tol=0,
    ):
        raise ValueError("portfolio source equity/exposure reconciliation failed")
    return LanePortfolioView(
        lane=source.lane, build_ref=source.build_ref,
        position_snapshot_id=source.snapshot_id,
        position_snapshot_hash=source.integrity_hash,
        source_receipt_root=source.source_receipt_root, as_of_utc=source.as_of_utc,
        position_count=len(positions),
        option_position_count=sum(p.instrument_kind == "OPTION" for p in positions),
        stock_position_count=sum(p.instrument_kind == "STOCK" for p in positions),
        gross_market_exposure=total, option_market_exposure=option_market,
        stock_market_exposure=stock_market,
        gross_entry_cost_including_open_commissions=entry,
        simulated_cash=source.source_cash,
        simulated_equity=source.source_equity,
        simulated_realized_pnl=source.source_realized_pnl,
        simulated_unrealized_pnl=source.source_unrealized_pnl,
        source_truth="OBSIM_ONLY_INDICATIVE_NOT_BROKER",
        source_verified_as_broker=False, deployable_for_acquisition=False,
    )


def _material(value: PortfolioComparison) -> dict[str, object]:
    return {
        key: [asdict(x) for x in value.lanes] if key == "lanes" else getattr(value, key)
        for key in PortfolioComparison.__dataclass_fields__
        if key not in ("comparison_id", "integrity_hash")
    }


def _build(harness: MultiSimulationHarness, sources: tuple[PositionSnapshot, ...]) -> PortfolioComparison:
    if not isinstance(harness, MultiSimulationHarness) or len(sources) != len(LANES):
        raise ValueError("requires canonical three-lane OBSIM and OBPOS sources")
    if tuple(s.lane for s in sources) != tuple(lane.value for lane in LANES):
        raise ValueError("portfolio lane order/identity must be exact")
    for lane, source in zip(LANES, sources):
        if not verify_simulated_position_snapshot(source, harness):
            raise ValueError("portfolio source failed OBPOS verification")
        if source.build_ref != lane_state(harness, lane).build_ref:
            raise ValueError("portfolio source build reference changed")
    if len({s.account_key for s in sources}) != 1 or sources[0].account_key != harness.account_key:
        raise ValueError("portfolio source account mismatch")
    if len({s.as_of_utc for s in sources}) != 1:
        raise ValueError("portfolio sources must share the canonical as-of")
    views = tuple(_lane_view(s) for s in sources)
    provisional = PortfolioComparison(
        comparison_id="PENDING", authority=SCHEMA_VERSION,
        account_key=harness.account_key, harness_id=harness.harness_id,
        common_market_frame_ids=tuple(f.frame_id for f in harness.market_frames),
        lanes=views, ranking_generated=False, winner_selected=False,
        automatic_promotion=False, broker_authenticated=False,
        acquisition_readiness="NOT_ASSESSED_BY_OB", capital_movement=False,
        execution_authority=False, integrity_hash="PENDING",
    )
    digest = _hash(_material(provisional))
    return replace(provisional, comparison_id="OBPORT-" + digest[:24], integrity_hash=digest)


def verify_portfolio_comparison(
    value: PortfolioComparison, *, harness: MultiSimulationHarness,
    sources: tuple[PositionSnapshot, ...],
) -> bool:
    if not isinstance(value, PortfolioComparison) or value.authority != SCHEMA_VERSION:
        return False
    if (value.ranking_generated is not False or value.winner_selected is not False
        or value.automatic_promotion is not False or value.broker_authenticated is not False
        or value.capital_movement is not False or value.execution_authority is not False
        or value.acquisition_readiness != "NOT_ASSESSED_BY_OB"):
        return False
    try:
        return value == _build(harness, sources)
    except (ValueError, TypeError, AttributeError, KeyError):
        return False


def build_portfolio_comparison(
    harness: MultiSimulationHarness, *,
    sources: tuple[PositionSnapshot, ...] | None = None,
) -> PortfolioComparison:
    if sources is None:
        sources = tuple(build_simulated_position_snapshot(harness, lane=lane) for lane in LANES)
    result = _build(harness, sources)
    if not verify_portfolio_comparison(result, harness=harness, sources=sources):
        raise ValueError("portfolio comparison failed verification")
    return result


def portfolio_reference(
    value: PortfolioComparison, *, harness: MultiSimulationHarness,
    sources: tuple[PositionSnapshot, ...],
) -> dict[str, object]:
    if not verify_portfolio_comparison(value, harness=harness, sources=sources):
        raise ValueError("portfolio reference requires verified lineage")
    return {
        "authority": SCHEMA_VERSION, "comparison_id": value.comparison_id,
        "integrity_hash": value.integrity_hash, "account_key": value.account_key,
        "source_snapshot_ids": [s.position_snapshot_id for s in value.lanes],
        "source_truth": "SIMULATION_ONLY",
        "amounts_exposed": False, "broker_authenticated": False,
        "acquisition_readiness": "NOT_ASSESSED_BY_OB",
        "tower_authorization_required": True, "teller_readiness_required": True,
    }


def portfolio_contract() -> dict[str, object]:
    return {
        "authority": SCHEMA_VERSION, "source_authority": "OB_POSITION_TRUTH_V1",
        "new_position_ledger": False, "source_accounting_reused": True,
        "three_lanes_isolated": True, "shared_market_frames_not_pooled_capital": True,
        "automatic_winner_selection": False, "broker_authenticated": False,
        "execution_authority": False, "capital_movement": False,
        "direct_buybox_access": False, "teller_owns_acquisition_readiness": True,
        "manual_live_unlock": False, "hybrid_unlock": False, "automated_unlock": False,
    }
