"""OBSCAN026-040: universal provider gateway; source-only, read-only and fail-closed.

Installation is a trusted internal review step, NOT an HTTP/browser endpoint.
No client, API secret, brokerage SDK, stream opening, or order transport here.
Provider/product templates advertise possible integrations, never grant feed rights.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Mapping

from .adapters import FeedAdapter, IngressRegistry
from .contracts import EquityQuote, Gate, OptionQuote, ScanContext, SourceRights, _aware, assess
from .provider_catalog import CATALOG, ProviderProduct
from .scanner import ScanPolicy, inspect_symbol, research_packet
from .traffic import FetchProposal, ProviderBudget, TrafficPlanner
from .universe import SymbolRow


@dataclass(frozen=True)
class IngressDecision:
    source_id: str
    instrument: str
    state: str
    reason: str
    stored: bool = False
    owner_visible: bool = False
    invitee_visible: bool = False
    broker_execution_authorized: bool = False


@dataclass(frozen=True)
class _Installation:
    product: ProviderProduct
    rights: SourceRights
    adapter: FeedAdapter
    planner: TrafficPlanner | None


class UniversalMarketGateway:
    """Keep products, rights, independent quote observations and request budgets separate.

    Multiple provider products can run concurrently. Source identities must be unique
    per entitled product; separate equity and option rights are never inferred from
    a company name or another installed adapter. Revoke purges observations.
    """

    def __init__(self) -> None:
        self._catalog: dict[str, ProviderProduct] = dict(CATALOG)
        self._installed: dict[str, _Installation] = {}
        self._ingress = IngressRegistry()
        self._equities: dict[tuple[str, str], EquityQuote] = {}
        self._options: dict[tuple[str, str], OptionQuote] = {}

    def add_product(self, product: ProviderProduct) -> None:
        """Enable future vendors without modifying the scanner or trading broker."""
        if product.key in self._catalog:
            raise ValueError("provider product exists; change requires explicit review")
        self._catalog[product.key] = product

    def install(self, product_key: str, *, rights: SourceRights, adapter: FeedAdapter,
                budget: ProviderBudget | None = None) -> None:
        """Only trusted internal entitlement review may invoke this method."""
        if product_key not in self._catalog:
            raise ValueError("unknown provider product")
        product = self._catalog[product_key]
        if product.instrument not in {"equity", "option"} or not product.current_quote_eligible:
            raise ValueError("reference or indicative product cannot install as current quote")
        if rights.source_id in self._installed:
            raise ValueError("source ID already installed; no silent overwrite or account mixing")
        if not rights.reviewed_for_scan() or not rights.real_time_entitled:
            raise ValueError("reviewed automated research and exact real-time entitlement required")
        if product.instrument not in rights.entitled_instruments or adapter.instrument != product.instrument:
            raise ValueError("separate product/instrument entitlement required")
        if adapter.source != rights or adapter.feed_label != "realtime":
            raise ValueError("installed adapter must use reviewed registry rights and current feed")
        if budget is not None and (budget.source_id != rights.source_id or
                                   not budget.research_entitlement_confirmed):
            raise ValueError("traffic budget must be confirmed for this exact product source")
        self._ingress.register(adapter)
        self._installed[rights.source_id] = _Installation(
            product, rights, adapter, TrafficPlanner(budget, rights) if budget else None)

    def revoke(self, source_id: str) -> None:
        """Drop entitlements and all cached observations, fail-closed."""
        if source_id not in self._installed:
            raise ValueError("unknown installed source")
        del self._installed[source_id]
        self._equities = {k: v for k, v in self._equities.items() if k[0] != source_id}
        self._options = {k: v for k, v in self._options.items() if k[0] != source_id}
        # IngressRegistry is internal: its lingering entry is inaccessible after
        # revoke because ingest checks _installed first. A new source ID is required
        # for renewed rights, avoiding reactivation of previously approved mapping.

    def ingest(self, source_id: str, raw: Mapping[str, object], *,
               received_at: datetime, context: ScanContext) -> IngressDecision:
        """Accept already-fetched trusted transport payload; never fetch or emit raw prices."""
        _aware(received_at, "received_at")
        installed = self._installed.get(source_id)
        if installed is None:
            return IngressDecision(source_id, "unknown", "SOURCE_HOLD", "Source not installed.")
        instrument = installed.product.instrument
        if received_at > context.now and (received_at-context.now).total_seconds() > context.clock_skew_seconds:
            return IngressDecision(source_id, instrument, "TEMPORAL_HOLD", "Receipt is future-dated.")
        try:
            quote = self._ingress.normalize(source_id, instrument, raw, received_at=received_at)
        except (ValueError, KeyError, TypeError, OverflowError) as exc:
            # No vendor payload or secret is returned in failure reason.
            return IngressDecision(source_id, instrument, "INVALID_HOLD", type(exc).__name__ + " in source payload.")
        gate = assess(quote.evidence, installed.rights, context)
        if gate.gate != Gate.CURRENT_RESEARCH:
            return IngressDecision(source_id, instrument, gate.gate.value, gate.reason)
        key = (source_id, quote.occ_symbol if instrument == "option" else quote.evidence.symbol)
        store = self._options if instrument == "option" else self._equities
        old = store.get(key)
        if old is not None and quote.evidence.observed_at <= old.evidence.observed_at:
            return IngressDecision(source_id, instrument, "OUT_OF_ORDER_HOLD",
                                   "Older or duplicate observation cannot replace source state.")
        store[key] = quote
        return IngressDecision(source_id, instrument, "CURRENT_RESEARCH",
                               "Source-bound observation accepted for non-trading research.",
                               True, gate.display_to_owner, gate.display_to_invitees)

    def provider_status(self, context: ScanContext | None = None) -> dict[str, object]:
        """Capability dashboard: source-independent descriptions; no credentials or prices."""
        rows = []
        for key, product in sorted(self._catalog.items()):
            installed = next((i for i in self._installed.values() if i.product.key == key), None)
            state = "REFERENCE_ONLY" if product.instrument in {"metadata", "event"} else "NOT_CONFIGURED"
            if installed is not None:
                state = "SOURCE_ONLY_READY"
                if context is not None:
                    r = installed.rights
                    if (r.verified_at is not None and r.verified_at > context.now) or (
                        r.expires_at is not None and context.now >= r.expires_at):
                        state = "RIGHTS_HOLD"
            rows.append({"product_key": key, "company": product.company,
                         "instrument": product.instrument, "quote_kind": product.quote_kind,
                         "current_quote_eligible_if_entitled": product.current_quote_eligible,
                         "state": state})
        return {"schema": "OB_MULTI_PROVIDER_STATUS_V1", "providers": rows,
                "live_transport_connected": False, "api_tokens_configured": False,
                "broker_order_transport": False, "manual_live_unlocked": False}

    def plan_requests(self, *, context: ScanContext, watchlist: Iterable[str] = (),
                      event_symbols: Iterable[str] = (), cold_universe: Iterable[str] = (),
                      verified_option_underlyings: Iterable[str] = ()) -> tuple[FetchProposal, ...]:
        """One independent budget per exact product, never fan out past provider quotas."""
        proposals: list[FetchProposal] = []
        for source_id in sorted(self._installed):
            installed = self._installed[source_id]
            if installed.planner is None:
                continue
            proposals.extend(installed.planner.propose(
                context=context, watchlist=watchlist if installed.product.instrument == "equity" else (),
                event_symbols=event_symbols if installed.product.instrument == "equity" else (),
                cold_universe=cold_universe if installed.product.instrument == "equity" else (),
                option_underlyings=(verified_option_underlyings
                                    if installed.product.instrument == "option" else ())))
        return tuple(proposals)

    def stream_selection(self, source_id: str, *, context: ScanContext,
                         symbols: Iterable[str] = ()) -> tuple[str, ...]:
        installed = self._installed.get(source_id)
        if installed is None or installed.planner is None:
            return ()
        return installed.planner.stream_selection(
            context=context,
            watchlist=symbols,
            instrument=installed.product.instrument)

    def owner_research_packet(self, symbol: str, *, universe: Mapping[str, SymbolRow],
                              context: ScanContext, policy: ScanPolicy = ScanPolicy()) -> dict[str, object]:
        """Only owner-display-granted observations reach this owner-facing packet.

        It is a Survey research packet, not broker quote truth, capital readiness,
        an execution request or permission to redistribute to invitees.
        """
        permitted_equities = [
            q for q in self._equities.values()
            if assess(q.evidence, self._installed[q.evidence.source_id].rights, context).display_to_owner
        ]
        permitted_options = [
            q for q in self._options.values()
            if assess(q.evidence, self._installed[q.evidence.source_id].rights, context).display_to_owner
        ]
        lead = inspect_symbol(symbol, universe=universe, equities=permitted_equities,
                              options=permitted_options, rights={k: v.rights for k,v in self._installed.items()},
                              context=context, policy=policy)
        packet = research_packet(lead)
        packet["gateway"] = {"schema": "OB_MULTI_PROVIDER_GATEWAY_V1",
                             "audience": "owner_only", "source_only": True,
                             "network_called": False, "quote_values_disclosed": False,
                             "broker_execution_authorized": False}
        return packet
