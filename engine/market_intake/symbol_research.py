"""OBINTEL017-022: one read-only symbol research record, source and date bounded.

Historical price, issuer filings and financial fact context are distinct from
current feed evidence, broker quotes, capital truth and execution permission.
The existing independent scanner remains the only gateway research source here;
this record does not construct signals, rank trades, synthesize option chains or
call a web provider. A valid company identity does not grant any feed rights.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Mapping

from .contracts import DiscoveryEvent, ScanContext, SourceRights, _aware, clean_symbol
from .fundamental_research import CompanyFact, FundamentalRights, fundamental_context
from .gateway import UniversalMarketGateway
from .historical_research import HistorySeries, history_context
from .universe import SymbolRow


@dataclass(frozen=True)
class SymbolResearchInputs:
    identity: SymbolRow
    captured_at: datetime
    history: HistorySeries | None = None
    financial_facts: tuple[CompanyFact,...] = ()
    financial_rights: FundamentalRights | None = None
    issuer_events: tuple[DiscoveryEvent,...] = ()
    event_rights: Mapping[str, SourceRights] | None = None

    def __post_init__(self)->None:
        _aware(self.captured_at,"research capture")
        clean_symbol(self.identity.symbol)
        if self.identity.directory_observed_at > self.captured_at:
            raise ValueError("identity evidence was observed after research capture")
        if self.history is not None and (
            self.history.symbol!=self.identity.symbol or self.history.received_at>self.captured_at):
            raise ValueError("history identity or snapshot timestamp mismatch")
        if self.financial_facts and (not self.identity.sec_cik or self.financial_rights is None
                                     or any(row.cik!=self.identity.sec_cik or row.accepted_at>self.captured_at
                                            for row in self.financial_facts)):
            raise ValueError("financial facts must belong to exact directory-linked CIK")
        if self.issuer_events and (not self.identity.sec_cik or self.event_rights is None):
            raise ValueError("issuer events require CIK binding and separately reviewed rights")
        for event in self.issuer_events:
            if (event.evidence.symbol != self.identity.symbol or
                event.issuer_cik != self.identity.sec_cik or
                event.evidence.observed_at > self.captured_at):
                raise ValueError("event's instrument, CIK or acceptance timestamp mismatches")


def symbol_research_snapshot(inputs: SymbolResearchInputs, *, as_of: datetime,
                             gateway: UniversalMarketGateway | None = None,
                             market_context: ScanContext | None = None) -> dict[str,object]:
    """Strictly read-only owner research; non-display sources stay unprojected."""
    _aware(as_of,"research as-of")
    if as_of>inputs.captured_at:
        raise ValueError("research cannot claim observations newer than snapshot")
    row=inputs.identity
    identity={
        "symbol":row.symbol,"security_name":row.security_name,
        "exchange_code":row.exchange,"cik":row.sec_cik,
        "identity_status":row.identity_status,
        "directory_evidence_as_of":row.directory_observed_at.isoformat(),
        "directory_source":row.source_file,
        "price_asserted_by_directory":False,
        "optionability_verified_by_directory":False,
    }
    # Past-replay identity must not include directory data captured in its future.
    if row.directory_observed_at>as_of:
        identity={"symbol":row.symbol,"security_name":None,"exchange_code":None,"cik":None,
                  "identity_status":"FUTURE_IDENTITY_HOLD",
                  "directory_evidence_as_of":None,"directory_source":None,
                  "price_asserted_by_directory":False,"optionability_verified_by_directory":False}

    historical={"state":"NOT_AVAILABLE","historical_only":True,
                "ai_explanation_allowed":False,"current_quote_eligible":False,"option_quote_eligible":False}
    if inputs.history is not None and inputs.history.received_at<=as_of:
        if inputs.history.rights.owner_display_allowed and inputs.history.rights.allowed_at(as_of):
            historical=history_context(inputs.history,cutoff=as_of)
        else:
            historical={"state":"RIGHTS_HOLD","historical_only":True,
                        "ai_explanation_allowed":False,"current_quote_eligible":False,"option_quote_eligible":False}

    fundamentals={"state":"NOT_AVAILABLE","quote_eligible":False,"signal_eligible":False}
    if inputs.financial_facts and inputs.financial_rights is not None:
        if inputs.financial_rights.owner_display and inputs.financial_rights.allowed_at(as_of):
            fundamentals=fundamental_context(cik=row.sec_cik or "",facts=inputs.financial_facts,
                                             rights=inputs.financial_rights,as_of=as_of)
        else:
            fundamentals={"state":"RIGHTS_HOLD","quote_eligible":False,"signal_eligible":False}

    events=[]
    source_rights=inputs.event_rights or {}
    for event in inputs.issuer_events:
        evidence=event.evidence
        rights=source_rights.get(evidence.source_id)
        if (evidence.observed_at>as_of or rights is None or
            rights.source_id!=evidence.source_id or rights.upstream_family!=evidence.upstream_family or
            "event" not in rights.entitled_instruments or not rights.reviewed_for_scan() or
            not rights.owner_display or rights.verified_at is None or rights.verified_at>as_of or
            rights.expires_at is not None and as_of>=rights.expires_at):
            continue
        events.append({"kind":event.category,"source_id":evidence.source_id,
                       "upstream_family":evidence.upstream_family,
                       "observation_id":evidence.observation_id,
                       "accepted_at":evidence.observed_at.isoformat(),
                       "headline":event.headline,"reference":event.reference_url,
                       "research_only":True,"is_quote":False})
    events.sort(key=lambda x:x["accepted_at"],reverse=True)

    scanner={"state":"NOT_CONNECTED","equity_sources":[],"option_sources":[],
             "source_observed_at":[],"research_only":True,"broker_quote_verified":False}
    # Current quote-source context must use the actual gateway and exact current
    # scan clock, never historical as_of extrapolated into a live quote assertion.
    if gateway is not None and market_context is not None and market_context.now==as_of and (
        row.directory_observed_at<=as_of):
        packet=gateway.owner_research_packet(row.symbol,universe={row.symbol:row},context=market_context)
        scanner={
            "state":packet["state"],
            "equity_sources":packet["equity_sources"],
            "option_sources":packet["option_sources"],
            "source_observed_at":packet["source_observed_at"],
            "explanations":packet["explanations"],
            "research_only":True,
            "broker_quote_verified":False,
        }
    states=[historical["state"],fundamentals["state"],scanner["state"]]
    state=("SOURCE_BOUND_RESEARCH" if any(x in {
        "SOURCE_BOUND_HISTORY","SOURCE_BOUND","RESEARCH_WATCH","OBSERVATION"} for x in states)
        else "EVIDENCE_PENDING")
    if identity["identity_status"]=="FUTURE_IDENTITY_HOLD":state="IDENTITY_HOLD"
    return {
        "schema":"OB_SYMBOL_RESEARCH_RECORD_V1","symbol":row.symbol,
        "as_of":as_of.isoformat(),"captured_at":inputs.captured_at.isoformat(),
        "state":state,"identity":identity,
        "historical":historical,"fundamentals":fundamentals,
        "issuer_events":events[:12],"scanner":scanner,
        "source_rights_and_freshness_required":True,
        "history_is_not_a_live_quote":True,
        "options_require_separate_entitlements":True,
        "context_only":True,
        "candidate_admitted":False,"manual_live_authorized":False,
        "broker_quote_verified":False,"execution_authorized":False,
        "capital_authority":False,
    }
