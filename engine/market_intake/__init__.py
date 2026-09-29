"""OBSCAN001-025 — optional, provider-neutral research intake; never a trading authority."""
from .contracts import (
    BOUNDARIES, VERSION, DiscoveryEvent, EquityQuote, Gate, Observation,
    OptionQuote, ScanContext, SourceRights, assess,
)
from .adapters import FeedAdapter, IngressRegistry
from .provider_catalog import CATALOG, ProviderProduct
from .gateway import IngressDecision, UniversalMarketGateway
from .sec_events import parse_sec_submissions
from .scanner import ResearchLead, ScanPolicy, inspect_symbol, research_packet
from .traffic import FetchProposal, ProviderBudget, TrafficPlanner
from .universe import (
    SymbolRow, diff_directory, directory_snapshot, parse_nasdaq_directory,
    parse_sec_ticker_exchange, reconcile_symbol_universe,
)
__all__ = (
    "FeedAdapter", "IngressRegistry", "CATALOG", "ProviderProduct", "IngressDecision",
    "UniversalMarketGateway", "BOUNDARIES", "VERSION", "DiscoveryEvent", "EquityQuote", "Gate", "Observation",
    "OptionQuote", "ScanContext", "SourceRights", "assess", "ResearchLead",
    "ScanPolicy", "parse_sec_submissions", "inspect_symbol", "research_packet", "FetchProposal",
    "ProviderBudget", "TrafficPlanner", "SymbolRow", "diff_directory",
    "directory_snapshot", "parse_nasdaq_directory", "parse_sec_ticker_exchange",
    "reconcile_symbol_universe",
)
