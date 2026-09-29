"""OBSCAN011-020: attentive scanner with event-led discovery, quote corroboration and option gate.

This code produces research packets only. It does not alter the existing OB candidate
admission chain, Capital Defense, Tower policy, broker permissions or user modes.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Iterable, Mapping

from .contracts import (
    DiscoveryEvent, EquityQuote, Gate, OptionQuote, ScanContext, SourceRights,
    assess, clean_symbol,
)
from .universe import SymbolRow


@dataclass(frozen=True)
class ResearchLead:
    symbol: str
    state: str
    explanation: tuple[str, ...]
    underlying_source_ids: tuple[str, ...]
    option_source_ids: tuple[str, ...]
    event_ids: tuple[str, ...]
    source_observed_at: tuple[str, ...]
    requested_followup: tuple[str, ...]
    execution_ready: bool = False
    recommendation: bool = False
    prices_redistributable: bool = False


@dataclass(frozen=True)
class ScanPolicy:
    price_change_watch_pct: float = 2.0
    relative_volume_watch: float = 1.8
    max_relative_last_disagreement: float = 0.005
    max_events_per_symbol: int = 4
    max_options_per_symbol: int = 10

    def __post_init__(self) -> None:
        if any(not isfinite(x) or x <= 0 for x in (
            self.price_change_watch_pct, self.relative_volume_watch,
            self.max_relative_last_disagreement)):
            raise ValueError("positive finite research thresholds required")
        if not 0 < self.max_events_per_symbol <= 20 or not 0 < self.max_options_per_symbol <= 50:
            raise ValueError("bounded research queue required")


def _provider_families(items: Iterable[EquityQuote]) -> tuple[EquityQuote, ...]:
    """Two resellers of the same upstream feed are not two independent witnesses."""
    selected: dict[str, EquityQuote] = {}
    for item in items:
        name = item.evidence.upstream_family
        prior = selected.get(name)
        if prior is None or item.evidence.observed_at > prior.evidence.observed_at:
            selected[name] = item
    return tuple(sorted(selected.values(), key=lambda x: x.evidence.source_id))


def _event_leads(symbol: str, events: Iterable[DiscoveryEvent], universe: Mapping[str, SymbolRow],
                 rights: Mapping[str, SourceRights], context: ScanContext,
                 policy: ScanPolicy) -> tuple[DiscoveryEvent, ...]:
    identity = universe.get(symbol)
    if identity is None:
        return ()
    selected: list[DiscoveryEvent] = []
    seen: set[tuple[str, str, str]] = set()
    for event in events:
        e = event.evidence
        if e.symbol != symbol or assess(e, rights.get(e.source_id), context, quote=False).gate != Gate.CURRENT_RESEARCH:
            continue
        # A company event must be associated with a directory-resolved issuer; a
        # ticker string in a headline is never sufficient identity evidence.
        if event.issuer_cik:
            if not identity.sec_cik or event.issuer_cik.zfill(10) != identity.sec_cik:
                continue
        elif event.category in {"filing", "company_release"}:
            continue
        key = (e.upstream_family, e.observation_id, event.category)
        if key not in seen:
            seen.add(key)
            selected.append(event)
        if len(selected) >= policy.max_events_per_symbol:
            break
    return tuple(selected)


def inspect_symbol(symbol: str, *, universe: Mapping[str, SymbolRow],
                   equities: Iterable[EquityQuote] = (),
                   options: Iterable[OptionQuote] = (),
                   events: Iterable[DiscoveryEvent] = (),
                   rights: Mapping[str, SourceRights],
                   context: ScanContext,
                   policy: ScanPolicy = ScanPolicy()) -> ResearchLead:
    symbol = clean_symbol(symbol)
    if symbol not in universe:
        return ResearchLead(symbol, "IDENTITY_HOLD", ("Symbol is not in the reviewed directory snapshot.",),
                            (), (), (), (), ("Verify instrument identity.",))
    observations = [q for q in equities if q.evidence.symbol == symbol]
    accepted, issues = [], []
    for q in observations:
        gate = assess(q.evidence, rights.get(q.evidence.source_id), context)
        if gate.gate == Gate.CURRENT_RESEARCH:
            accepted.append(q)
        else:
            issues.append(f"{q.evidence.source_id}: {gate.gate.value} — {gate.reason}")
    independent = _provider_families(accepted)
    discovery = _event_leads(symbol, events, universe, rights, context, policy)
    event_ids = tuple(event.evidence.observation_id for event in discovery)
    if len(independent) >= 2:
        prices = [q.last for q in independent]
        center = sum(prices) / len(prices)
        if center <= 0 or (max(prices)-min(prices))/center > policy.max_relative_last_disagreement:
            return ResearchLead(symbol, "CONFLICT_HOLD",
                ("Independent eligible quote families disagree beyond policy; do not pick whichever price looks better.",),
                tuple(q.evidence.source_id for q in independent), (), event_ids,
                tuple(q.evidence.observed_at.isoformat() for q in independent),
                ("Inspect timestamps, venue, upstream lineage and market-time context.",))
    if not independent:
        reason = ["No entitled, current, session-verified equity quote. Discovery events are research leads, not live prices."]
        reason.extend(issues[:3])
        if discovery:
            reason.append(f"{len(discovery)} identity-checked event(s) for follow-up.")
        return ResearchLead(symbol, "EVENT_RESEARCH_ONLY" if discovery else "DATA_HOLD", tuple(reason),
                            (), (), event_ids, tuple(e.evidence.observed_at.isoformat() for e in discovery),
                            ("Obtain authorized current underlying quote.", "Check company filings and original sources.") if discovery
                            else ("Wait for authorized, current underlying evidence.",))
    chosen = independent[0]  # only for bounded calculations; never a broker-side 'true' quote.
    reasons: list[str] = []
    if chosen.previous_close is not None:
        change = (chosen.last / chosen.previous_close - 1) * 100
        if abs(change) >= policy.price_change_watch_pct:
            reasons.append(f"Underlying move crossed {policy.price_change_watch_pct:g}% watch threshold; verify context.")
    if chosen.volume is not None and chosen.average_volume is not None:
        ratio = chosen.volume / chosen.average_volume
        if ratio >= policy.relative_volume_watch:
            reasons.append(f"Reported volume crossed {policy.relative_volume_watch:g}x comparison threshold; verify period alignment.")
    if discovery:
        reasons.append(f"{len(discovery)} identity-checked event(s) merit source review; not a price confirmation.")
    option_ok: list[OptionQuote] = []
    option_reasons: list[str] = []
    for quote in options:
        if quote.underlying != symbol or quote.evidence.symbol != symbol:
            continue
        gate = assess(quote.evidence, rights.get(quote.evidence.source_id), context)
        if gate.gate != Gate.CURRENT_RESEARCH:
            option_reasons.append(f"{quote.evidence.source_id}: {gate.gate.value}")
            continue
        if quote.open_interest is None or quote.volume is None:
            option_reasons.append("Option OI/volume not supplied; do not infer liquidity.")
            continue
        option_ok.append(quote)
        if len(option_ok) >= policy.max_options_per_symbol:
            break
    if option_reasons:
        reasons.append("Option research partial: " + "; ".join(sorted(set(option_reasons))[:2]))
    if not reasons:
        reasons.append("Current underlying is observed; no configured research trigger crossed.")
    return ResearchLead(
        symbol, "RESEARCH_WATCH" if discovery or len(reasons) > (1 if reasons[0].startswith("Current underlying") else 0)
            and not reasons[0].startswith("Current underlying") else "OBSERVATION",
        tuple(reasons), tuple(q.evidence.source_id for q in independent),
        tuple(q.evidence.source_id for q in option_ok), event_ids,
        tuple(q.evidence.observed_at.isoformat() for q in independent) +
        tuple(q.evidence.observed_at.isoformat() for q in option_ok),
        ("Open underlying source evidence.", "Inspect options liquidity only where separately entitled."),
    )


def research_packet(lead: ResearchLead) -> dict[str, object]:
    """A bounded, read-only packet, NOT a canonical OB candidate admission receipt."""
    return {
        "schema": "OB_SCAN_RESEARCH_PACKET_V1", "symbol": lead.symbol,
        "state": lead.state, "explanations": list(lead.explanation),
        "equity_sources": list(lead.underlying_source_ids),
        "option_sources": list(lead.option_source_ids),
        "discovery_event_ids": list(lead.event_ids),
        "source_observed_at": list(lead.source_observed_at),
        "next_research_actions": list(lead.requested_followup),
        "eligibility": {"survey_research_only": True, "candidate_admitted": False,
                        "broker_quote_verified": False, "manual_live_authorized": False,
                        "auto_execution": False, "capital_authority": False},
    }
