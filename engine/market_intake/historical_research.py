"""OBINTEL001-010: source-licensed, daily historical equity context and replay.

No network, yfinance, market quote promotion, broker execution or trading P&L.
Every bar must be a completed observation from one reviewed product, with an
explicit raw/split/total-return adjustment basis. Calendar completeness needs
separate exchange-calendar proof; 252 bars is not automatically a 52-week year.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from math import isfinite
from typing import Iterable

from .contracts import _aware, clean_symbol


def _finite(value: float, name: str, *, zero: bool = False) -> None:
    if type(value) not in {int, float} or not isfinite(value) or (
        value < 0 if zero else value <= 0
    ):
        raise ValueError(f"{name} must be finite, {'nonnegative' if zero else 'positive'} numeric")


@dataclass(frozen=True)
class HistoryRights:
    source_id: str
    product: str
    upstream_family: str
    license_reference: str
    verified_at: datetime
    research_allowed: bool = False
    automated_analysis_allowed: bool = False
    owner_display_allowed: bool = False
    ai_explanation_allowed: bool = False
    retention_allowed: bool = False
    basis: str = "raw"
    basis_reference: str = ""
    expires_at: datetime | None = None

    def __post_init__(self) -> None:
        _aware(self.verified_at, "history rights verification")
        for field in ("source_id", "product", "upstream_family", "license_reference"):
            if not isinstance(getattr(self, field), str) or not getattr(self, field).strip():
                raise ValueError(f"{field} is required")
        if self.basis not in {"raw", "split_adjusted", "total_return_adjusted"}:
            raise ValueError("historical adjustment basis must be explicit")
        if self.basis != "raw" and not self.basis_reference.strip():
            raise ValueError("adjusted history requires source adjustment-method proof")
        if self.expires_at is not None:
            _aware(self.expires_at, "history license expiry")
            if self.expires_at <= self.verified_at:
                raise ValueError("history rights expiry must follow approval")

    def allowed_at(self, at: datetime) -> bool:
        _aware(at, "history check time")
        return (self.verified_at <= at and
                (self.expires_at is None or at < self.expires_at) and
                self.research_allowed and self.automated_analysis_allowed and
                bool(self.license_reference.strip()))


@dataclass(frozen=True)
class CompletedDailyBar:
    symbol: str
    source_id: str
    session_date: date
    open: float
    high: float
    low: float
    close: float
    volume: int
    provenance_reference: str
    basis: str
    completed: bool

    def __post_init__(self) -> None:
        clean_symbol(self.symbol)
        if not isinstance(self.session_date, date) or isinstance(self.session_date, datetime):
            raise ValueError("actual source session date required")
        if not self.source_id.strip() or not self.provenance_reference.strip() or not self.completed:
            raise ValueError("source/proof and completed session are required")
        if self.basis not in {"raw", "split_adjusted", "total_return_adjusted"}:
            raise ValueError("unsupported bar adjustment basis")
        for f in ("open", "high", "low", "close"):
            _finite(getattr(self, f), f)
        if type(self.volume) is not int or self.volume < 0:
            raise ValueError("nonnegative integer volume required")
        if self.low > min(self.open, self.close) or self.high < max(self.open, self.close) or self.low > self.high:
            raise ValueError("inconsistent OHLC values")


@dataclass(frozen=True)
class HistorySeries:
    symbol: str
    rights: HistoryRights
    bars: tuple[CompletedDailyBar, ...]
    received_at: datetime
    snapshot_reference: str

    def __post_init__(self) -> None:
        symbol=clean_symbol(self.symbol)
        _aware(self.received_at, "history snapshot receipt")
        if not self.snapshot_reference.strip() or not self.rights.allowed_at(self.received_at):
            raise ValueError("historical source permission/snapshot proof unavailable")
        if not self.bars or len(self.bars) > 10_000:
            raise ValueError("bounded non-empty history required")
        seen=set()
        for bar in self.bars:
            if bar.symbol != symbol or bar.source_id != self.rights.source_id or bar.basis != self.rights.basis:
                raise ValueError("mixed instrument, source or adjustment basis")
            if bar.session_date in seen:
                raise ValueError("duplicate session date; revised bars need a new snapshot")
            seen.add(bar.session_date)
            if bar.session_date > self.received_at.date():
                raise ValueError("future or incomplete daily session cannot enter history")
        if tuple(sorted(self.bars,key=lambda b:b.session_date)) != self.bars:
            raise ValueError("history must arrive in strictly chronological order")


def _authorized(series: HistorySeries, cutoff: datetime) -> None:
    _aware(cutoff,"historical cutoff")
    if cutoff > series.received_at:
        raise ValueError("research cutoff exceeds captured evidence snapshot")
    if not series.rights.allowed_at(cutoff):
        raise ValueError("historical rights absent, future-dated or expired")


def history_asof(series: HistorySeries, *, cutoff: datetime) -> tuple[CompletedDailyBar, ...]:
    """Select bars with source dates at or before cutoff; no future-bar replay leak.

    This assumes caller supplies a closed-session cutoff; calendar/session proof is
    not present in a date-only historical product, so no intraday permission follows.
    """
    _authorized(series, cutoff)
    return tuple(bar for bar in series.bars if bar.session_date < cutoff.date())


def history_context(series: HistorySeries, *, cutoff: datetime) -> dict[str, object]:
    bars=history_asof(series,cutoff=cutoff)
    out={
        "schema":"OB_SOURCE_HISTORY_CONTEXT_V1", "symbol":series.symbol,
        "source_id":series.rights.source_id, "product":series.rights.product,
        "upstream_family":series.rights.upstream_family,
        "snapshot_reference":series.snapshot_reference,
        "license_reference":series.rights.license_reference,
        "as_of":cutoff.isoformat(),"basis":series.rights.basis,
        "bars_used":len(bars),
        "first_session":bars[0].session_date.isoformat() if bars else None,
        "last_session":bars[-1].session_date.isoformat() if bars else None,
        "history_calendar_completeness":"NOT_VERIFIED",
        "state":"SOURCE_BOUND_HISTORY" if bars else "INSUFFICIENT_HISTORY",
        "historical_only":True, "ai_explanation_allowed":series.rights.ai_explanation_allowed,
        "retention_allowed":series.rights.retention_allowed, "current_quote_eligible":False,
        "option_quote_eligible":False, "capital_truth":False,
        "execution_authorized":False,"data_quality":"HOLD" if not bars else "SOURCE_BOUND_HISTORY",
        "observations":{},
    }
    if not bars:return out
    closes=[bar.close for bar in bars]
    for n in (20,50,200):
        out["observations"][f"close_sma_{n}_sessions"]=(sum(closes[-n:])/n if len(closes)>=n else None)
    out["observations"]["last_completed_close"]=closes[-1]
    out["observations"]["last_completed_volume"]=bars[-1].volume
    if len(bars)>=2:
        out["observations"]["sample_start_to_end_pct"]=(closes[-1]/closes[0]-1)*100
    else:
        out["observations"]["sample_start_to_end_pct"]=None
    out["observations"]["sample_high"]=max(bar.high for bar in bars)
    out["observations"]["sample_low"]=min(bar.low for bar in bars)
    return out


def replay_historical_horizon(series: HistorySeries, *, as_of_session: date,
                              horizon_sessions: int = 5) -> dict[str, object]:
    """Historical *diagnostic*, not a backtested fill/trade/edge or prediction.

    Formation uses only bars through prior completed session; outcome bars remain
    isolated and are reported after the cutoff as retrospective comparison only.
    No fees, option quote, order size, capital, market impact or survivorship proof.
    """
    if type(horizon_sessions) is not int or horizon_sessions<1 or horizon_sessions>60:
        raise ValueError("bounded positive session horizon required")
    if not isinstance(as_of_session,date) or isinstance(as_of_session,datetime):
        raise ValueError("historical session cutoff required")
    # Rights are checked at snapshot receipt, not retroactively assumed granted at
    # the older event date. Lookahead prevention is evaluated by session slices.
    if not series.rights.allowed_at(series.received_at):
        raise ValueError("no source research rights")
    prior=[x for x in series.bars if x.session_date <= as_of_session]
    future=[x for x in series.bars if x.session_date>as_of_session]
    base={"schema":"OB_HISTORICAL_SCENARIO_V1","symbol":series.symbol,
          "as_of_session":as_of_session.isoformat(),"horizon_sessions":horizon_sessions,
          "basis":series.rights.basis,"source_id":series.rights.source_id,
          "snapshot_reference":series.snapshot_reference,
          "purpose":"RETROSPECTIVE_DIAGNOSTIC_ONLY","trade_count":None,
          "win_rate":None,"strategy_pnl":None,"live_signal":False,
          "options_backtest":False,"trading_authorized":False,
          "limitations":["No execution fills, bid-ask slippage, fees or borrow/margin assumptions.",
                         "Not survivorship-bias or calendar-completeness certified."]}
    if len(prior)<20 or len(future)<horizon_sessions:
        return {**base,"state":"INSUFFICIENT_HISTORY","formation":None,"outcome":None}
    formation=prior[-20:]
    sma20=sum(x.close for x in formation)/20
    # Historical outcome is not passed back into formation.
    outcome=future[horizon_sessions-1]
    return {**base,"state":"RETROSPECTIVE_OBSERVATION",
            "formation":{"last_close":prior[-1].close,"prior_20_session_sma":sma20,
                         "last_session":prior[-1].session_date.isoformat()},
            "outcome":{"last_session":outcome.session_date.isoformat(),
                       "close":outcome.close,
                       "close_to_close_change_pct":(outcome.close/prior[-1].close-1)*100}}
