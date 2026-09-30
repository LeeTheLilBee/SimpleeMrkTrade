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
    ProviderProduct("twelve-data-business-basic", "Twelve Data", "Business Basic internal non-display US equity/ETF context", "equity",
                    "entitlement_defined", False, "https://twelvedata.com/pricing-business"),
    ProviderProduct("finazon-us-equities-basic", "Finazon", "US Equities Basic derived US market context; free trial AAPL/TSLA/GOOG", "equity",
                    "venue_limited", False, "https://finazon.io/dataset/us_stocks_essential"),
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
    ProviderProduct("treasury-debt-to-penny", "U.S. Treasury FiscalData", "Public debt-to-the-penny dataset; record-dated fiscal context only, not market yields or quotes", "event",
                    "reference", False, "https://fiscaldata.treasury.gov/datasets/debt-to-the-penny/"),
    ProviderProduct("bea-nipa", "U.S. Bureau of Economic Analysis", "NIPA historical economic data; free registered key required", "event",
                    "reference", False, "https://apps.bea.gov/api/signup/"),
    ProviderProduct("openfigi-identifier", "OpenFIGI", "Ticker / instrument FIGI mapping; no issuer or quote verification", "metadata",
                    "reference", False, "https://www.openfigi.com/api/documentation"),
    # Official Catalyst Radar: commercial-source-reviewed only on the separate
    # protected research corridor. Catalog presence never grants use or AI rights.
    ProviderProduct("official-federal-register-sec", "Federal Register", "SEC rulemaking publication metadata; no quote or effective-rule inference", "event",
                    "reference", False, "https://www.federalregister.gov/developers/documentation/api/v1"),
    ProviderProduct("official-cftc-tff-futures", "CFTC", "Weekly TFF futures-only leveraged money positioning; not listed options market data", "event",
                    "reference", False, "https://publicreporting.cftc.gov/stories/s/r4w3-av2u"),
    ProviderProduct("official-eia-weekly-inventory", "US EIA", "Official weekly crude inventories; free key required, exact rights and series verification", "event",
                    "reference", False, "https://www.eia.gov/opendata/"),
    ProviderProduct("official-world-bank-wdi-gdp", "World Bank", "US annual WDI nominal GDP; individual indicator CC BY review required", "event",
                    "reference", False, "https://data.worldbank.org/indicator/NY.GDP.MKTP.CD"),
    ProviderProduct("official-nws-georgia-alerts", "NOAA NWS", "Actual Georgia alert publications; no weather safety or market quote authority", "event",
                    "reference", False, "https://www.weather.gov/documentation/services-web-api"),
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
