from __future__ import annotations

from typing import Any, Dict, List


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value or "").strip()
        return text if text else default
    except Exception:
        return default


def _safe_bool(value: Any, default: bool = False) -> bool:
    try:
        if value is None:
            return bool(default)
        return bool(value)
    except Exception:
        return bool(default)


def _norm_symbol(value: Any) -> str:
    return _safe_str(value, "").upper()


def build_global_market_universe() -> List[Dict[str, Any]]:
    """
    Global expansion layer for the Observatory.

    Beta-safe rule:
    - U.S.-listed ADRs and U.S.-listed global ETFs may be research candidates.
    - Direct foreign-exchange tickers are research-only.
    - Nothing here should bypass account permissions, broker permissions,
      currency checks, or execution guard logic.
    """

    adr_watchlist = [
        {
            "symbol": "TSM",
            "display_name": "Taiwan Semiconductor",
            "country": "Taiwan",
            "region": "Asia",
            "exchange": "NYSE ADR",
            "currency": "USD",
            "asset_type": "ADR",
            "execution_allowed": True,
            "options_allowed": True,
            "research_allowed": True,
            "global_research_only": False,
        },
        {
            "symbol": "ASML",
            "display_name": "ASML Holding",
            "country": "Netherlands",
            "region": "Europe",
            "exchange": "NASDAQ ADR",
            "currency": "USD",
            "asset_type": "ADR",
            "execution_allowed": True,
            "options_allowed": True,
            "research_allowed": True,
            "global_research_only": False,
        },
        {
            "symbol": "NVO",
            "display_name": "Novo Nordisk",
            "country": "Denmark",
            "region": "Europe",
            "exchange": "NYSE ADR",
            "currency": "USD",
            "asset_type": "ADR",
            "execution_allowed": True,
            "options_allowed": True,
            "research_allowed": True,
            "global_research_only": False,
        },
        {
            "symbol": "AZN",
            "display_name": "AstraZeneca",
            "country": "United Kingdom",
            "region": "Europe",
            "exchange": "NASDAQ ADR",
            "currency": "USD",
            "asset_type": "ADR",
            "execution_allowed": True,
            "options_allowed": True,
            "research_allowed": True,
            "global_research_only": False,
        },
        {
            "symbol": "SHEL",
            "display_name": "Shell",
            "country": "United Kingdom",
            "region": "Europe",
            "exchange": "NYSE ADR",
            "currency": "USD",
            "asset_type": "ADR",
            "execution_allowed": True,
            "options_allowed": True,
            "research_allowed": True,
            "global_research_only": False,
        },
        {
            "symbol": "BABA",
            "display_name": "Alibaba",
            "country": "China",
            "region": "Asia",
            "exchange": "NYSE ADR",
            "currency": "USD",
            "asset_type": "ADR",
            "execution_allowed": True,
            "options_allowed": True,
            "research_allowed": True,
            "global_research_only": False,
        },
        {
            "symbol": "PDD",
            "display_name": "PDD Holdings",
            "country": "China",
            "region": "Asia",
            "exchange": "NASDAQ ADR",
            "currency": "USD",
            "asset_type": "ADR",
            "execution_allowed": True,
            "options_allowed": True,
            "research_allowed": True,
            "global_research_only": False,
        },
        {
            "symbol": "SONY",
            "display_name": "Sony Group",
            "country": "Japan",
            "region": "Asia",
            "exchange": "NYSE ADR",
            "currency": "USD",
            "asset_type": "ADR",
            "execution_allowed": True,
            "options_allowed": True,
            "research_allowed": True,
            "global_research_only": False,
        },
        {
            "symbol": "TM",
            "display_name": "Toyota",
            "country": "Japan",
            "region": "Asia",
            "exchange": "NYSE ADR",
            "currency": "USD",
            "asset_type": "ADR",
            "execution_allowed": True,
            "options_allowed": True,
            "research_allowed": True,
            "global_research_only": False,
        },
        {
            "symbol": "SAP",
            "display_name": "SAP",
            "country": "Germany",
            "region": "Europe",
            "exchange": "NYSE ADR",
            "currency": "USD",
            "asset_type": "ADR",
            "execution_allowed": True,
            "options_allowed": True,
            "research_allowed": True,
            "global_research_only": False,
        },
        {
            "symbol": "SHOP",
            "display_name": "Shopify",
            "country": "Canada",
            "region": "North America",
            "exchange": "NYSE",
            "currency": "USD",
            "asset_type": "FOREIGN_COMPANY_US_LISTING",
            "execution_allowed": True,
            "options_allowed": True,
            "research_allowed": True,
            "global_research_only": False,
        },
        {
            "symbol": "RIO",
            "display_name": "Rio Tinto",
            "country": "United Kingdom / Australia",
            "region": "Global Materials",
            "exchange": "NYSE ADR",
            "currency": "USD",
            "asset_type": "ADR",
            "execution_allowed": True,
            "options_allowed": True,
            "research_allowed": True,
            "global_research_only": False,
        },
        {
            "symbol": "VALE",
            "display_name": "Vale",
            "country": "Brazil",
            "region": "South America",
            "exchange": "NYSE ADR",
            "currency": "USD",
            "asset_type": "ADR",
            "execution_allowed": True,
            "options_allowed": True,
            "research_allowed": True,
            "global_research_only": False,
        },
    ]

    global_etfs = [
        {
            "symbol": "EFA",
            "display_name": "Developed Markets ETF",
            "country": "Multi-country",
            "region": "Developed Markets",
            "exchange": "NYSE Arca",
            "currency": "USD",
            "asset_type": "GLOBAL_ETF",
            "execution_allowed": True,
            "options_allowed": True,
            "research_allowed": True,
            "global_research_only": False,
        },
        {
            "symbol": "EEM",
            "display_name": "Emerging Markets ETF",
            "country": "Multi-country",
            "region": "Emerging Markets",
            "exchange": "NYSE Arca",
            "currency": "USD",
            "asset_type": "GLOBAL_ETF",
            "execution_allowed": True,
            "options_allowed": True,
            "research_allowed": True,
            "global_research_only": False,
        },
        {
            "symbol": "EWJ",
            "display_name": "Japan ETF",
            "country": "Japan",
            "region": "Asia",
            "exchange": "NYSE Arca",
            "currency": "USD",
            "asset_type": "COUNTRY_ETF",
            "execution_allowed": True,
            "options_allowed": True,
            "research_allowed": True,
            "global_research_only": False,
        },
        {
            "symbol": "EWU",
            "display_name": "United Kingdom ETF",
            "country": "United Kingdom",
            "region": "Europe",
            "exchange": "NYSE Arca",
            "currency": "USD",
            "asset_type": "COUNTRY_ETF",
            "execution_allowed": True,
            "options_allowed": True,
            "research_allowed": True,
            "global_research_only": False,
        },
        {
            "symbol": "EWG",
            "display_name": "Germany ETF",
            "country": "Germany",
            "region": "Europe",
            "exchange": "NYSE Arca",
            "currency": "USD",
            "asset_type": "COUNTRY_ETF",
            "execution_allowed": True,
            "options_allowed": True,
            "research_allowed": True,
            "global_research_only": False,
        },
        {
            "symbol": "EWQ",
            "display_name": "France ETF",
            "country": "France",
            "region": "Europe",
            "exchange": "NYSE Arca",
            "currency": "USD",
            "asset_type": "COUNTRY_ETF",
            "execution_allowed": True,
            "options_allowed": True,
            "research_allowed": True,
            "global_research_only": False,
        },
        {
            "symbol": "EWC",
            "display_name": "Canada ETF",
            "country": "Canada",
            "region": "North America",
            "exchange": "NYSE Arca",
            "currency": "USD",
            "asset_type": "COUNTRY_ETF",
            "execution_allowed": True,
            "options_allowed": True,
            "research_allowed": True,
            "global_research_only": False,
        },
        {
            "symbol": "EWZ",
            "display_name": "Brazil ETF",
            "country": "Brazil",
            "region": "South America",
            "exchange": "NYSE Arca",
            "currency": "USD",
            "asset_type": "COUNTRY_ETF",
            "execution_allowed": True,
            "options_allowed": True,
            "research_allowed": True,
            "global_research_only": False,
        },
        {
            "symbol": "INDA",
            "display_name": "India ETF",
            "country": "India",
            "region": "Asia",
            "exchange": "NYSE Arca",
            "currency": "USD",
            "asset_type": "COUNTRY_ETF",
            "execution_allowed": True,
            "options_allowed": True,
            "research_allowed": True,
            "global_research_only": False,
        },
        {
            "symbol": "MCHI",
            "display_name": "China ETF",
            "country": "China",
            "region": "Asia",
            "exchange": "NYSE Arca",
            "currency": "USD",
            "asset_type": "COUNTRY_ETF",
            "execution_allowed": True,
            "options_allowed": True,
            "research_allowed": True,
            "global_research_only": False,
        },
        {
            "symbol": "FXI",
            "display_name": "China Large Cap ETF",
            "country": "China",
            "region": "Asia",
            "exchange": "NYSE Arca",
            "currency": "USD",
            "asset_type": "COUNTRY_ETF",
            "execution_allowed": True,
            "options_allowed": True,
            "research_allowed": True,
            "global_research_only": False,
        },
        {
            "symbol": "EWY",
            "display_name": "South Korea ETF",
            "country": "South Korea",
            "region": "Asia",
            "exchange": "NYSE Arca",
            "currency": "USD",
            "asset_type": "COUNTRY_ETF",
            "execution_allowed": True,
            "options_allowed": True,
            "research_allowed": True,
            "global_research_only": False,
        },
        {
            "symbol": "EWT",
            "display_name": "Taiwan ETF",
            "country": "Taiwan",
            "region": "Asia",
            "exchange": "NYSE Arca",
            "currency": "USD",
            "asset_type": "COUNTRY_ETF",
            "execution_allowed": True,
            "options_allowed": True,
            "research_allowed": True,
            "global_research_only": False,
        },
        {
            "symbol": "EWW",
            "display_name": "Mexico ETF",
            "country": "Mexico",
            "region": "North America",
            "exchange": "NYSE Arca",
            "currency": "USD",
            "asset_type": "COUNTRY_ETF",
            "execution_allowed": True,
            "options_allowed": True,
            "research_allowed": True,
            "global_research_only": False,
        },
    ]

    direct_foreign_research = [
        {
            "symbol": "7203.T",
            "display_name": "Toyota Motor Tokyo",
            "country": "Japan",
            "region": "Asia",
            "exchange": "Tokyo Stock Exchange",
            "currency": "JPY",
            "asset_type": "DIRECT_FOREIGN_STOCK",
            "execution_allowed": False,
            "options_allowed": False,
            "research_allowed": True,
            "global_research_only": True,
        },
        {
            "symbol": "9984.T",
            "display_name": "SoftBank Group Tokyo",
            "country": "Japan",
            "region": "Asia",
            "exchange": "Tokyo Stock Exchange",
            "currency": "JPY",
            "asset_type": "DIRECT_FOREIGN_STOCK",
            "execution_allowed": False,
            "options_allowed": False,
            "research_allowed": True,
            "global_research_only": True,
        },
        {
            "symbol": "0700.HK",
            "display_name": "Tencent Hong Kong",
            "country": "China",
            "region": "Asia",
            "exchange": "Hong Kong",
            "currency": "HKD",
            "asset_type": "DIRECT_FOREIGN_STOCK",
            "execution_allowed": False,
            "options_allowed": False,
            "research_allowed": True,
            "global_research_only": True,
        },
        {
            "symbol": "9988.HK",
            "display_name": "Alibaba Hong Kong",
            "country": "China",
            "region": "Asia",
            "exchange": "Hong Kong",
            "currency": "HKD",
            "asset_type": "DIRECT_FOREIGN_STOCK",
            "execution_allowed": False,
            "options_allowed": False,
            "research_allowed": True,
            "global_research_only": True,
        },
        {
            "symbol": "HSBA.L",
            "display_name": "HSBC London",
            "country": "United Kingdom",
            "region": "Europe",
            "exchange": "London Stock Exchange",
            "currency": "GBP",
            "asset_type": "DIRECT_FOREIGN_STOCK",
            "execution_allowed": False,
            "options_allowed": False,
            "research_allowed": True,
            "global_research_only": True,
        },
        {
            "symbol": "BP.L",
            "display_name": "BP London",
            "country": "United Kingdom",
            "region": "Europe",
            "exchange": "London Stock Exchange",
            "currency": "GBP",
            "asset_type": "DIRECT_FOREIGN_STOCK",
            "execution_allowed": False,
            "options_allowed": False,
            "research_allowed": True,
            "global_research_only": True,
        },
        {
            "symbol": "RY.TO",
            "display_name": "Royal Bank of Canada Toronto",
            "country": "Canada",
            "region": "North America",
            "exchange": "Toronto Stock Exchange",
            "currency": "CAD",
            "asset_type": "DIRECT_FOREIGN_STOCK",
            "execution_allowed": False,
            "options_allowed": False,
            "research_allowed": True,
            "global_research_only": True,
        },
        {
            "symbol": "SHOP.TO",
            "display_name": "Shopify Toronto",
            "country": "Canada",
            "region": "North America",
            "exchange": "Toronto Stock Exchange",
            "currency": "CAD",
            "asset_type": "DIRECT_FOREIGN_STOCK",
            "execution_allowed": False,
            "options_allowed": False,
            "research_allowed": True,
            "global_research_only": True,
        },
    ]

    rows = adr_watchlist + global_etfs + direct_foreign_research

    normalized: List[Dict[str, Any]] = []
    seen = set()

    for row in rows:
        symbol = _norm_symbol(row.get("symbol"))
        if not symbol or symbol in seen:
            continue

        seen.add(symbol)

        normalized.append({
            "symbol": symbol,
            "display_name": _safe_str(row.get("display_name"), symbol),
            "country": _safe_str(row.get("country"), "Unknown"),
            "region": _safe_str(row.get("region"), "Global"),
            "exchange": _safe_str(row.get("exchange"), "Unknown"),
            "currency": _safe_str(row.get("currency"), "USD").upper(),
            "asset_type": _safe_str(row.get("asset_type"), "GLOBAL_RESEARCH").upper(),
            "execution_allowed": _safe_bool(row.get("execution_allowed"), False),
            "options_allowed": _safe_bool(row.get("options_allowed"), False),
            "research_allowed": _safe_bool(row.get("research_allowed"), True),
            "global_research_only": _safe_bool(row.get("global_research_only"), True),
            "universe_source": "global_market_universe",
        })

    return normalized


def get_global_market_symbols(
    include_research_only: bool = True,
    include_execution_allowed: bool = True,
) -> List[str]:
    symbols: List[str] = []

    for row in build_global_market_universe():
        if row.get("global_research_only") and not include_research_only:
            continue
        if row.get("execution_allowed") and not include_execution_allowed:
            continue
        symbols.append(row["symbol"])

    return symbols


def get_global_market_metadata(symbol: str) -> Dict[str, Any]:
    clean = _norm_symbol(symbol)

    for row in build_global_market_universe():
        if row.get("symbol") == clean:
            return dict(row)

    return {}


def is_global_research_only(symbol: str) -> bool:
    metadata = get_global_market_metadata(symbol)
    return bool(metadata.get("global_research_only", False))


def global_execution_allowed(symbol: str) -> bool:
    metadata = get_global_market_metadata(symbol)
    return bool(metadata.get("execution_allowed", False))


__all__ = [
    "build_global_market_universe",
    "get_global_market_symbols",
    "get_global_market_metadata",
    "is_global_research_only",
    "global_execution_allowed",
]
