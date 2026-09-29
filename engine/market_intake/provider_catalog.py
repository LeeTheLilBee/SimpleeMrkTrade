"""Provider/product catalog for OB's universal read-only market gateway.

Catalog entries are *possible connectors*, not subscribed feeds, licenses, credentials,
working transports, or grants to display/redistribute. Exact upstream lineage
comes from a separately reviewed SourceRights record, never from this list.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderProduct:
    key: str
    company: str
    product: str
    instrument: str  # equity, option, event or metadata
    quote_kind: str  # consolidated, venue_limited, entitlement_defined, indicative, reference
    current_quote_eligible: bool
    documentation: str

    def __post_init__(self) -> None:
        if not self.key or not self.company or not self.product or not self.documentation.startswith("https://"):
            raise ValueError("provider identity and official documentation required")
        if self.instrument not in {"equity", "option", "event", "metadata"}:
            raise ValueError("unknown provider instrument")
        if self.quote_kind not in {"consolidated", "venue_limited", "entitlement_defined", "indicative", "reference"}:
            raise ValueError("explicit source coverage category required")
        if self.instrument in {"event", "metadata"} and self.current_quote_eligible:
            raise ValueError("a research/reference feed cannot be a market quote")
        if self.quote_kind in {"indicative", "reference"} and self.current_quote_eligible:
            raise ValueError("indicative or reference data cannot assert an executable current quote")


_PRODUCTS = (
    ProviderProduct("tradier-equity", "Tradier", "Production brokerage equities", "equity",
                    "consolidated", True, "https://docs.tradier.com/docs/market-data"),
    ProviderProduct("tradier-options", "Tradier", "Production brokerage options", "option",
                    "consolidated", True, "https://docs.tradier.com/docs/market-data"),
    ProviderProduct("alpaca-iex-equity", "Alpaca", "IEX equities", "equity",
                    "venue_limited", True, "https://docs.alpaca.markets/us/docs/real-time-stock-pricing-data"),
    ProviderProduct("alpaca-sip-equity", "Alpaca", "SIP equities (entitlement required)", "equity",
                    "consolidated", True, "https://docs.alpaca.markets/us/docs/real-time-stock-pricing-data"),
    ProviderProduct("alpaca-opra-options", "Alpaca", "OPRA options (entitlement required)", "option",
                    "consolidated", True, "https://docs.alpaca.markets/us/docs/real-time-option-data"),
    ProviderProduct("alpaca-indicative-options", "Alpaca", "Indicative options; not live quote authority", "option",
                    "indicative", False, "https://docs.alpaca.markets/us/reference/optionchain"),
    ProviderProduct("ibkr-equity", "Interactive Brokers", "Equity market data; exact subscription/venue varies", "equity",
                    "entitlement_defined", True, "https://www.interactivebrokers.com/docs/tws-api/doc/market-data-delayed/introduction"),
    ProviderProduct("ibkr-options", "Interactive Brokers", "Options market data; exact subscription/venue varies", "option",
                    "entitlement_defined", True, "https://www.interactivebrokers.com/docs/tws-api/doc/market-data-delayed/introduction"),
    ProviderProduct("direct-sip-equity", "Direct licensed market data", "SIP equities; contractual approval", "equity",
                    "consolidated", True, "https://www.ctaplan.com/"),
    ProviderProduct("direct-opra-options", "Direct licensed market data", "OPRA options; contractual approval", "option",
                    "consolidated", True, "https://www.opraplan.com/"),
    ProviderProduct("nasdaq-directory", "Nasdaq Trader", "Listed-security directory; metadata only", "metadata",
                    "reference", False, "https://www.nasdaqtrader.com/Trader.aspx?id=SymbolDirDefs"),
    ProviderProduct("occ-reports", "OCC", "Series/volume/open-interest research; not streaming quotes", "metadata",
                    "reference", False, "https://www.theocc.com/market-data/market-data-reports"),
    ProviderProduct("sec-edgar", "SEC", "Issuer filings, submission history and structured companyfacts; research only, never a quote", "event",
                    "reference", False, "https://www.sec.gov/search-filings/edgar-application-programming-interfaces"),
    ProviderProduct("bls-public-v1", "U.S. Bureau of Labor Statistics", "Public economic series, historical release context; no quotes", "event",
                    "reference", False, "https://www.bls.gov/developers/"),
    ProviderProduct("bea-nipa", "U.S. Bureau of Economic Analysis", "NIPA historical economic data; free registered key required", "event",
                    "reference", False, "https://apps.bea.gov/api/signup/"),
    ProviderProduct("openfigi-identifier", "OpenFIGI", "Ticker / instrument FIGI mapping; no issuer or quote verification", "metadata",
                    "reference", False, "https://www.openfigi.com/api/documentation"),
    ProviderProduct("fred-macro-review-only", "Federal Reserve Bank of St. Louis", "FRED policy HOLD: AI, storage and use restrictions; no runtime transport", "event",
                    "reference", False, "https://fred.stlouisfed.org/legal/terms/"),
    ProviderProduct("public-business-review-only", "Public", "Business API candidate; account and data/display rights review required", "metadata",
                    "reference", False, "https://public.com/api/docs"),
    ProviderProduct("public-account-equity", "Public", "Authenticated account-scoped equity quotes, exact rights required", "equity",
                    "entitlement_defined", True, "https://public.com/api/docs/resources/market-data/get-quotes"),
    ProviderProduct("public-account-option", "Public", "Authenticated account-scoped option quotes, separate exact rights required", "option",
                    "entitlement_defined", True, "https://public.com/api/docs/resources/market-data/get-quotes"),

)
CATALOG: dict[str, ProviderProduct] = {p.key: p for p in _PRODUCTS}
if len(CATALOG) != len(_PRODUCTS):
    raise RuntimeError("duplicate provider catalog identifier")
