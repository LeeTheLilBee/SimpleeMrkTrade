"""OBSCAN021-025: deterministic traffic planner, no HTTP client and no hidden API limits.

The planner considers an entire symbol universe without requesting every quote constantly.
It has no credentials, does not bypass a vendor cap and never creates extra sessions.
Actual adapters must report 429/retry-after and upstream entitlements independently.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable

from .contracts import ScanContext, SourceRights, _aware, clean_symbol


@dataclass(frozen=True)
class ProviderBudget:
    source_id: str
    requests_per_minute: int
    max_symbols_per_request: int
    supports_options: bool = False
    supports_streaming: bool = False
    max_stream_symbols: int = 0
    research_entitlement_confirmed: bool = False

    def __post_init__(self) -> None:
        if not self.source_id.strip():
            raise ValueError("source_id required")
        if self.requests_per_minute < 0 or self.max_symbols_per_request < 0 or self.max_stream_symbols < 0:
            raise ValueError("provider limits must be nonnegative; unknown limits default to zero")
        if self.supports_streaming and self.max_stream_symbols < 1:
            raise ValueError("do not invent a streaming-symbol allowance")


@dataclass(frozen=True)
class FetchProposal:
    source_id: str
    lane: str
    symbols: tuple[str, ...]
    reason: str
    planned_at: str
    network_called: bool = False
    order_placed: bool = False


class TrafficPlanner:
    def __init__(self, budget: ProviderBudget, rights: SourceRights | None,
                 *, quote_cooldown_seconds: int = 30, options_cooldown_seconds: int = 120):
        if quote_cooldown_seconds < 1 or options_cooldown_seconds < 1:
            raise ValueError("cooldowns must be positive")
        self.budget = budget
        self.rights = rights
        self.cooldown = {"equity": quote_cooldown_seconds, "options": options_cooldown_seconds}
        self._request_times: list[datetime] = []
        self._last: dict[tuple[str, str], datetime] = {}
        self._backoff_until: datetime | None = None
        self._round_robin_cursor = 0

    def backoff(self, until: datetime) -> None:
        _aware(until, "backoff_until")
        if self._backoff_until is None or until > self._backoff_until:
            self._backoff_until = until

    def _authorized(self, context: ScanContext) -> bool:
        return (self.budget.research_entitlement_confirmed and self.rights is not None
                and self.rights.source_id == self.budget.source_id and self.rights.reviewed_for_scan()
                and self.rights.real_time_entitled and "equity" in self.rights.entitled_instruments
                and (self.rights.verified_at is None or self.rights.verified_at <= context.now)
                and (self.rights.expires_at is None or context.now < self.rights.expires_at)
                and context.verified_market_time
                and context.market_session == "REGULAR")

    @staticmethod
    def _symbols(values: Iterable[str]) -> list[str]:
        unique: dict[str, None] = {}
        for value in values:
            try:
                unique[clean_symbol(value)] = None
            except ValueError:
                continue
        return list(unique)

    def propose(self, *, context: ScanContext, watchlist: Iterable[str] = (),
                event_symbols: Iterable[str] = (), cold_universe: Iterable[str] = (),
                option_underlyings: Iterable[str] = ()) -> list[FetchProposal]:
        """Proposal only: watchlist > identity-checked event follow-up > fair cold rotation.

        'option_underlyings' MUST be supplied by a separate, current-quote gate; the planner
        never assumes that being listed, newsworthy or on a watchlist means optionable.
        """
        now = context.now
        if (not self._authorized(context) or not self.budget.requests_per_minute
                or not self.budget.max_symbols_per_request
                or self._backoff_until is not None and now < self._backoff_until):
            return []
        cutoff = now - timedelta(seconds=60)
        self._request_times = [x for x in self._request_times if x > cutoff]
        quota = max(0, self.budget.requests_per_minute-len(self._request_times))
        if not quota:
            return []
        hot = self._symbols(watchlist)
        warm = [s for s in self._symbols(event_symbols) if s not in hot]
        cold = [s for s in self._symbols(cold_universe) if s not in hot and s not in warm]
        if cold:
            offset = self._round_robin_cursor % len(cold)
            cold = cold[offset:] + cold[:offset]
        proposals: list[FetchProposal] = []
        covered_cold = 0

        def offer(lane: str, values: list[str], reason: str) -> None:
            nonlocal quota, covered_cold
            due = [s for s in values if (lane,s) not in self._last or
                   now-self._last[(lane,s)] >= timedelta(seconds=self.cooldown[lane])]
            size = self.budget.max_symbols_per_request
            for start in range(0,len(due),size):
                if not quota:
                    break
                subset = tuple(due[start:start+size])
                if not subset:
                    continue
                proposals.append(FetchProposal(self.budget.source_id,lane,subset,reason,now.isoformat()))
                quota -= 1
                self._request_times.append(now)
                for s in subset:self._last[(lane,s)] = now
                if reason == "rotating-broad-discovery":
                    covered_cold += len(subset)
        # One narrow event batch cannot starve the explicit watchlist.
        offer("equity", hot, "owner-watchlist")
        offer("equity", warm, "event-followup-not-price-proof")
        offer("equity", cold, "rotating-broad-discovery")
        if self.budget.supports_options and self.rights is not None and "option" in self.rights.entitled_instruments:
            offer("options", self._symbols(option_underlyings), "separately-verified-underlying")
        self._round_robin_cursor += covered_cold
        return proposals

    def stream_selection(self, *, context: ScanContext, watchlist: Iterable[str] = (),
                         event_symbols: Iterable[str] = ()) -> tuple[str, ...]:
        """Single existing provider session; no stream open/close or invented full-exchange subscription."""
        if not self._authorized(context) or not self.budget.supports_streaming:
            return ()
        merged = self._symbols([*watchlist, *event_symbols])
        return tuple(merged[:self.budget.max_stream_symbols])

    def status(self) -> dict[str, object]:
        return {"source_id":self.budget.source_id,"known_cap":self.budget.requests_per_minute,
                "used_window":len(self._request_times), "backoff_until":self._backoff_until.isoformat()
                if self._backoff_until is not None else None,
                "no_network_client":True,"no_cap_inference":True,"no_order_transport":True}
