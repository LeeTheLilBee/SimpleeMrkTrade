"""OBSCAN001-025 — optional, provider-neutral research intake; never a trading authority."""
from .contracts import (
    BOUNDARIES, VERSION, DiscoveryEvent, EquityQuote, Gate, Observation,
    OptionQuote, ScanContext, SourceRights, assess,
)
from .adapters import FeedAdapter, IngressRegistry
from .provider_catalog import CATALOG, ProviderProduct
from .gateway import IngressDecision, UniversalMarketGateway
from .commercial_free_market import (
    FINAZON_FREE_TRIAL_SYMBOLS, FINAZON_ID, TWELVE_DATA_ID,
    MarketContextRecord, normalize_finazon_snapshot, normalize_twelve_data_quote,
    parse_finazon_ws_bar, parse_twelve_data_ws_price, record_digest, stream_plan,
)
from .historical_research import (CompletedDailyBar, HistoryRights, HistorySeries,
                                  history_context, replay_historical_horizon)
from .fundamental_research import (CompanyFact, FundamentalRights, parse_companyfacts,
                                   fundamental_context)
from .symbol_research import SymbolResearchInputs, symbol_research_snapshot
from .research_bridge import project_research, attach_research_context
from .research_memory import ResearchReferenceLedger, soulaana_research_brief
from .sec_events import parse_sec_submissions
from .edgar_research import (EdgarResearchBundle, acceptance_evidence, build_edgar_research)
from .edgar_cache import (read_sec_cache, checked_cached_research, make_owner_edgar_resolver)
from .scanner import ResearchLead, ScanPolicy, inspect_symbol, research_packet
from .traffic import FetchProposal, ProviderBudget, TrafficPlanner
from .universe import (
    SymbolRow, diff_directory, directory_snapshot, parse_nasdaq_directory,
    parse_sec_ticker_exchange, reconcile_symbol_universe,
)
__all__ = (
    "FeedAdapter", "IngressRegistry", "CATALOG", "ProviderProduct", "IngressDecision",
    "UniversalMarketGateway",
    "MarketContextRecord", "TWELVE_DATA_ID", "FINAZON_ID", "FINAZON_FREE_TRIAL_SYMBOLS",
    "normalize_twelve_data_quote", "normalize_finazon_snapshot", "parse_twelve_data_ws_price",
    "parse_finazon_ws_bar", "stream_plan", "record_digest",
    "CompletedDailyBar", "HistoryRights", "HistorySeries",
    "history_context", "replay_historical_horizon", "CompanyFact",
    "FundamentalRights", "parse_companyfacts", "fundamental_context",
    "SymbolResearchInputs", "symbol_research_snapshot", "project_research",
    "attach_research_context", "EdgarResearchBundle", "acceptance_evidence",
    "build_edgar_research", "read_sec_cache", "checked_cached_research",
    "make_owner_edgar_resolver", "ResearchReferenceLedger",
    "soulaana_research_brief", "BOUNDARIES", "VERSION", "DiscoveryEvent", "EquityQuote", "Gate", "Observation",
    "OptionQuote", "ScanContext", "SourceRights", "assess", "ResearchLead",
    "ScanPolicy", "parse_sec_submissions", "inspect_symbol", "research_packet", "FetchProposal",
    "ProviderBudget", "TrafficPlanner", "SymbolRow", "diff_directory",
    "directory_snapshot", "parse_nasdaq_directory", "parse_sec_ticker_exchange",
    "reconcile_symbol_universe",
)
