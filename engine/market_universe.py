import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple

MARKET_UNIVERSE_FILE = "data/market_universe.json"
PIPELINE_STATUS_FILE = "data/pipeline_status.json"

SOURCE_FILES = {
    "signals": "data/signals.json",
    "symbol_intelligence": "data/symbol_intelligence.json",
    "symbol_meta": "data/symbol_meta.json",
    "symbol_news": "data/symbol_news.json",
    "candidate_log": "data/candidate_log.json",
    "trade_details": "data/trade_details.json",
    "positions": "data/positions.json",
    "open_positions": "data/open_positions.json",
    "closed_positions": "data/closed_positions.json",
    "user_positions": "data/user_positions.json",
    "my_plays": "data/my_plays.json",
}

STATIC_DIVERSITY_SYMBOLS = [
    ("SPY", "SPDR S&P 500 ETF Trust", 10, "etf"),
    ("QQQ", "Invesco QQQ Trust", 10, "etf"),
    ("IWM", "iShares Russell 2000 ETF", 9, "etf"),
    ("DIA", "SPDR Dow Jones Industrial Average ETF", 9, "etf"),
    ("VTI", "Vanguard Total Stock Market ETF", 9, "etf"),
    ("VOO", "Vanguard S&P 500 ETF", 9, "etf"),
    ("IVV", "iShares Core S&P 500 ETF", 9, "etf"),
    ("RSP", "Invesco S&P 500 Equal Weight ETF", 8, "etf"),
    ("SMH", "VanEck Semiconductor ETF", 8, "etf"),
    ("SOXX", "iShares Semiconductor ETF", 8, "etf"),
    ("XLF", "Financial Select Sector SPDR Fund", 7, "etf"),
    ("XLK", "Technology Select Sector SPDR Fund", 7, "etf"),
    ("XLE", "Energy Select Sector SPDR Fund", 7, "etf"),
    ("XLV", "Health Care Select Sector SPDR Fund", 7, "etf"),
    ("XLI", "Industrial Select Sector SPDR Fund", 6, "etf"),
    ("XLP", "Consumer Staples Select Sector SPDR Fund", 6, "etf"),
    ("XLY", "Consumer Discretionary Select Sector SPDR Fund", 6, "etf"),
    ("XLU", "Utilities Select Sector SPDR Fund", 6, "etf"),
    ("XLB", "Materials Select Sector SPDR Fund", 6, "etf"),
    ("XLRE", "Real Estate Select Sector SPDR Fund", 6, "etf"),
    ("XBI", "SPDR S&P Biotech ETF", 6, "etf"),
    ("KRE", "SPDR S&P Regional Banking ETF", 5, "etf"),
    ("ARKK", "ARK Innovation ETF", 5, "etf"),
    ("GLD", "SPDR Gold Shares", 6, "etf"),
    ("SLV", "iShares Silver Trust", 5, "etf"),
    ("USO", "United States Oil Fund", 5, "etf"),
    ("TLT", "iShares 20+ Year Treasury Bond ETF", 6, "etf"),
    ("HYG", "iShares iBoxx $ High Yield Corporate Bond ETF", 5, "etf"),
    ("LQD", "iShares iBoxx $ Investment Grade Corporate Bond ETF", 5, "etf"),
]

STATIC_EQUITY_UNIVERSE = [
    ("AAPL", "Apple Inc.", 10, "equity"),
    ("MSFT", "Microsoft Corporation", 10, "equity"),
    ("NVDA", "NVIDIA Corporation", 10, "equity"),
    ("AMZN", "Amazon.com, Inc.", 10, "equity"),
    ("META", "Meta Platforms, Inc.", 10, "equity"),
    ("GOOGL", "Alphabet Inc.", 10, "equity"),
    ("TSLA", "Tesla, Inc.", 9, "equity"),
    ("BRK-B", "Berkshire Hathaway Inc.", 9, "equity"),
    ("JPM", "JPMorgan Chase & Co.", 9, "equity"),
    ("UNH", "UnitedHealth Group Incorporated", 9, "equity"),
    ("LLY", "Eli Lilly and Company", 9, "equity"),
    ("AVGO", "Broadcom Inc.", 9, "equity"),
    ("V", "Visa Inc.", 8, "equity"),
    ("MA", "Mastercard Incorporated", 8, "equity"),
    ("XOM", "Exxon Mobil Corporation", 8, "equity"),
    ("COST", "Costco Wholesale Corporation", 8, "equity"),
    ("WMT", "Walmart Inc.", 8, "equity"),
    ("PG", "The Procter & Gamble Company", 8, "equity"),
    ("JNJ", "Johnson & Johnson", 8, "equity"),
    ("HD", "The Home Depot, Inc.", 8, "equity"),
    ("AMD", "Advanced Micro Devices, Inc.", 8, "equity"),
    ("INTC", "Intel Corporation", 6, "equity"),
    ("QCOM", "QUALCOMM Incorporated", 7, "equity"),
    ("MU", "Micron Technology, Inc.", 7, "equity"),
    ("TXN", "Texas Instruments Incorporated", 7, "equity"),
    ("ADI", "Analog Devices, Inc.", 6, "equity"),
    ("AMAT", "Applied Materials, Inc.", 7, "equity"),
    ("LRCX", "Lam Research Corporation", 7, "equity"),
    ("KLAC", "KLA Corporation", 6, "equity"),
    ("MRVL", "Marvell Technology, Inc.", 6, "equity"),
    ("ARM", "Arm Holdings plc", 6, "equity"),
    ("ASML", "ASML Holding N.V.", 8, "equity"),
    ("CRM", "Salesforce, Inc.", 7, "equity"),
    ("ORCL", "Oracle Corporation", 7, "equity"),
    ("ADBE", "Adobe Inc.", 7, "equity"),
    ("NOW", "ServiceNow, Inc.", 7, "equity"),
    ("PANW", "Palo Alto Networks, Inc.", 7, "equity"),
    ("CRWD", "CrowdStrike Holdings, Inc.", 7, "equity"),
    ("ZS", "Zscaler, Inc.", 5, "equity"),
    ("NET", "Cloudflare, Inc.", 5, "equity"),
    ("SNOW", "Snowflake Inc.", 5, "equity"),
    ("DDOG", "Datadog, Inc.", 5, "equity"),
    ("PLTR", "Palantir Technologies Inc.", 6, "equity"),
    ("MDB", "MongoDB, Inc.", 5, "equity"),
    ("SHOP", "Shopify Inc.", 5, "equity"),
    ("UBER", "Uber Technologies, Inc.", 6, "equity"),
    ("ABNB", "Airbnb, Inc.", 5, "equity"),
    ("BAC", "Bank of America Corporation", 7, "equity"),
    ("C", "Citigroup Inc.", 6, "equity"),
    ("WFC", "Wells Fargo & Company", 6, "equity"),
    ("GS", "The Goldman Sachs Group, Inc.", 6, "equity"),
    ("MS", "Morgan Stanley", 6, "equity"),
    ("BLK", "BlackRock, Inc.", 6, "equity"),
    ("AXP", "American Express Company", 6, "equity"),
    ("SCHW", "The Charles Schwab Corporation", 5, "equity"),
    ("COF", "Capital One Financial Corporation", 5, "equity"),
    ("PYPL", "PayPal Holdings, Inc.", 5, "equity"),
    ("SQ", "Block, Inc.", 5, "equity"),
    ("SOFI", "SoFi Technologies, Inc.", 4, "equity"),
    ("CVX", "Chevron Corporation", 7, "equity"),
    ("COP", "ConocoPhillips", 6, "equity"),
    ("EOG", "EOG Resources, Inc.", 6, "equity"),
    ("SLB", "Schlumberger Limited", 5, "equity"),
    ("OXY", "Occidental Petroleum Corporation", 5, "equity"),
    ("PSX", "Phillips 66", 5, "equity"),
    ("MPC", "Marathon Petroleum Corporation", 5, "equity"),
    ("VLO", "Valero Energy Corporation", 5, "equity"),
    ("MRK", "Merck & Co., Inc.", 7, "equity"),
    ("ABBV", "AbbVie Inc.", 7, "equity"),
    ("PFE", "Pfizer Inc.", 6, "equity"),
    ("TMO", "Thermo Fisher Scientific Inc.", 6, "equity"),
    ("DHR", "Danaher Corporation", 6, "equity"),
    ("ISRG", "Intuitive Surgical, Inc.", 6, "equity"),
    ("VRTX", "Vertex Pharmaceuticals Incorporated", 6, "equity"),
    ("REGN", "Regeneron Pharmaceuticals, Inc.", 6, "equity"),
    ("BIIB", "Biogen Inc.", 4, "equity"),
    ("GILD", "Gilead Sciences, Inc.", 5, "equity"),
    ("CAT", "Caterpillar Inc.", 6, "equity"),
    ("DE", "Deere & Company", 6, "equity"),
    ("GE", "GE Aerospace", 6, "equity"),
    ("BA", "The Boeing Company", 5, "equity"),
    ("RTX", "RTX Corporation", 6, "equity"),
    ("LMT", "Lockheed Martin Corporation", 6, "equity"),
    ("NOC", "Northrop Grumman Corporation", 5, "equity"),
    ("GD", "General Dynamics Corporation", 5, "equity"),
    ("UPS", "United Parcel Service, Inc.", 5, "equity"),
    ("FDX", "FedEx Corporation", 5, "equity"),
    ("DAL", "Delta Air Lines, Inc.", 4, "equity"),
    ("UAL", "United Airlines Holdings, Inc.", 4, "equity"),
    ("AAL", "American Airlines Group Inc.", 4, "equity"),
    ("MCD", "McDonald's Corporation", 6, "equity"),
    ("SBUX", "Starbucks Corporation", 5, "equity"),
    ("NKE", "NIKE, Inc.", 5, "equity"),
    ("LOW", "Lowe's Companies, Inc.", 5, "equity"),
    ("TGT", "Target Corporation", 5, "equity"),
    ("DIS", "The Walt Disney Company", 6, "equity"),
    ("NFLX", "Netflix, Inc.", 7, "equity"),
    ("BKNG", "Booking Holdings Inc.", 5, "equity"),
    ("MAR", "Marriott International, Inc.", 5, "equity"),
    ("HLT", "Hilton Worldwide Holdings Inc.", 5, "equity"),
    ("TMUS", "T-Mobile US, Inc.", 6, "equity"),
    ("VZ", "Verizon Communications Inc.", 5, "equity"),
    ("T", "AT&T Inc.", 5, "equity"),
    ("CMCSA", "Comcast Corporation", 5, "equity"),
    ("CHTR", "Charter Communications, Inc.", 4, "equity"),
    ("SPOT", "Spotify Technology S.A.", 4, "equity"),
    ("ROKU", "Roku, Inc.", 4, "equity"),
    ("NEE", "NextEra Energy, Inc.", 5, "equity"),
    ("DUK", "Duke Energy Corporation", 4, "equity"),
    ("SO", "The Southern Company", 4, "equity"),
    ("AMT", "American Tower Corporation", 5, "equity"),
    ("PLD", "Prologis, Inc.", 5, "equity"),
    ("EQIX", "Equinix, Inc.", 5, "equity"),
    ("LIN", "Linde plc", 6, "equity"),
    ("FCX", "Freeport-McMoRan Inc.", 5, "equity"),
    ("NEM", "Newmont Corporation", 4, "equity"),
    ("RIVN", "Rivian Automotive, Inc.", 4, "equity"),
    ("LCID", "Lucid Group, Inc.", 4, "equity"),
    ("AFRM", "Affirm Holdings, Inc.", 4, "equity"),
    ("UPST", "Upstart Holdings, Inc.", 4, "equity"),
    ("COIN", "Coinbase Global, Inc.", 5, "equity"),
    ("U", "Unity Software Inc.", 4, "equity"),
    ("PATH", "UiPath Inc.", 4, "equity"),
    ("HOOD", "Robinhood Markets, Inc.", 4, "equity"),
    ("DKNG", "DraftKings Inc.", 4, "equity"),
]

def _load_json(path: str, default):
    file_path = Path(path)
    if not file_path.exists():
        return default
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def _save_json(path: str, payload) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []

def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}

def _norm_text(value: Any, default: str = "") -> str:
    text = str(value or "").strip()
    return text if text else default

def _norm_upper(value: Any, default: str = "") -> str:
    text = _norm_text(value, "").upper()
    return text if text else default

def _touch_pipeline_status(row_count: int, source_status: Dict[str, Any]) -> None:
    status = _safe_dict(_load_json(PIPELINE_STATUS_FILE, {}))
    now_iso = datetime.now().isoformat()
    status["market_universe_run_at"] = now_iso
    status["market_universe_count"] = row_count
    status["market_universe_source_status"] = source_status
    _save_json(PIPELINE_STATUS_FILE, status)

def _fresh_row(symbol: str) -> Dict[str, Any]:
    return {
        "symbol": symbol,
        "company_name": symbol,
        "asset_type": "equity",
        "source_tags": [],
        "priority_rank": 0,
        "last_seen_at": datetime.now().isoformat(),
    }

def _add_source_tag(row: Dict[str, Any], tag: str) -> None:
    tags = row.get("source_tags", [])
    if not isinstance(tags, list):
        tags = []
    if tag not in tags:
        tags.append(tag)
    row["source_tags"] = tags

def _merge_symbol(
    rows: Dict[str, Dict[str, Any]],
    symbol: str,
    company_name: str = "",
    tag: str = "",
    priority_boost: int = 0,
    asset_type: str = "equity",
) -> None:
    symbol = _norm_upper(symbol)
    if not symbol:
        return
    symbol = symbol.replace(".", "-")
    row = rows.get(symbol)
    if not row:
        row = _fresh_row(symbol)
        rows[symbol] = row
    if company_name and row.get("company_name", symbol) == symbol:
        row["company_name"] = company_name
    if tag:
        _add_source_tag(row, tag)
    row["priority_rank"] = int(row.get("priority_rank", 0) or 0) + int(priority_boost or 0)
    row["asset_type"] = _norm_text(asset_type, "equity")
    row["last_seen_at"] = datetime.now().isoformat()

def _extract_from_static_diversity(rows: Dict[str, Dict[str, Any]], source_status: Dict[str, Any]) -> None:
    count_before = len(rows)
    for symbol, company_name, priority_rank, asset_type in STATIC_DIVERSITY_SYMBOLS:
        _merge_symbol(rows, symbol, company_name, "diversity_seed", priority_rank, asset_type)
    source_status["diversity_seed"] = {"ok": True, "rows_added_estimate": len(rows) - count_before}

def _extract_from_static_equities(rows: Dict[str, Dict[str, Any]], source_status: Dict[str, Any]) -> None:
    count_before = len(rows)
    for symbol, company_name, priority_rank, asset_type in STATIC_EQUITY_UNIVERSE:
        _merge_symbol(rows, symbol, company_name, "equity_seed", priority_rank, asset_type)
    source_status["equity_seed"] = {"ok": True, "rows_added_estimate": len(rows) - count_before}

def _extract_from_signals(rows: Dict[str, Dict[str, Any]], source_status: Dict[str, Any]) -> None:
    count_before = len(rows)
    signals = _safe_list(_load_json(SOURCE_FILES["signals"], []))
    for item in signals:
        if isinstance(item, dict):
            _merge_symbol(rows, item.get("symbol"), item.get("company_name", ""), "signals", 6, "equity")
    source_status["signals"] = {
        "ok": True,
        "rows_added_estimate": len(rows) - count_before,
        "source_rows": len(signals),
    }

def _extract_from_symbol_intelligence(rows: Dict[str, Dict[str, Any]], source_status: Dict[str, Any]) -> None:
    count_before = len(rows)
    intel = _safe_dict(_load_json(SOURCE_FILES["symbol_intelligence"], {}))
    for symbol, payload in intel.items():
        if isinstance(payload, dict):
            _merge_symbol(rows, symbol, payload.get("company_name", ""), "symbol_intelligence", 5, "equity")
    source_status["symbol_intelligence"] = {
        "ok": True,
        "rows_added_estimate": len(rows) - count_before,
        "source_rows": len(intel),
    }

def _extract_from_symbol_meta(rows: Dict[str, Dict[str, Any]], source_status: Dict[str, Any]) -> None:
    count_before = len(rows)
    meta = _safe_dict(_load_json(SOURCE_FILES["symbol_meta"], {}))
    for symbol, payload in meta.items():
        if isinstance(payload, dict):
            _merge_symbol(rows, symbol, payload.get("name", ""), "symbol_meta", 2, "equity")
    source_status["symbol_meta"] = {
        "ok": True,
        "rows_added_estimate": len(rows) - count_before,
        "source_rows": len(meta),
    }

def _extract_from_symbol_news(rows: Dict[str, Dict[str, Any]], source_status: Dict[str, Any]) -> None:
    count_before = len(rows)
    news = _safe_dict(_load_json(SOURCE_FILES["symbol_news"], {}))
    for symbol, payload in news.items():
        item_count = 0
        if isinstance(payload, dict):
            item_count = len(_safe_list(payload.get("items", [])))
        elif isinstance(payload, list):
            item_count = len(payload)
        _merge_symbol(rows, symbol, "", "symbol_news", 3 if item_count > 0 else 1, "equity")
    source_status["symbol_news"] = {
        "ok": True,
        "rows_added_estimate": len(rows) - count_before,
        "source_rows": len(news),
    }

def _extract_symbol_field_list(
    rows: Dict[str, Dict[str, Any]],
    path: str,
    tag: str,
    source_status: Dict[str, Any],
    symbol_key: str = "symbol",
    company_key: str = "company_name",
    boost: int = 1,
) -> None:
    count_before = len(rows)
    items = _safe_list(_load_json(path, []))
    for item in items:
        if isinstance(item, dict):
            _merge_symbol(rows, item.get(symbol_key), item.get(company_key, ""), tag, boost, "equity")
    source_status[tag] = {
        "ok": True,
        "rows_added_estimate": len(rows) - count_before,
        "source_rows": len(items),
    }

def build_market_universe() -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    rows: Dict[str, Dict[str, Any]] = {}
    source_status: Dict[str, Any] = {}

    _extract_from_static_diversity(rows, source_status)
    _extract_from_static_equities(rows, source_status)
    _extract_from_signals(rows, source_status)
    _extract_from_symbol_intelligence(rows, source_status)
    _extract_from_symbol_meta(rows, source_status)
    _extract_from_symbol_news(rows, source_status)

    _extract_symbol_field_list(rows, SOURCE_FILES["candidate_log"], "candidate_log", source_status, boost=4)
    _extract_symbol_field_list(rows, SOURCE_FILES["trade_details"], "trade_details", source_status, boost=3)
    _extract_symbol_field_list(rows, SOURCE_FILES["positions"], "positions", source_status, boost=3)
    _extract_symbol_field_list(rows, SOURCE_FILES["open_positions"], "open_positions", source_status, boost=4)
    _extract_symbol_field_list(rows, SOURCE_FILES["closed_positions"], "closed_positions", source_status, boost=2)
    _extract_symbol_field_list(rows, SOURCE_FILES["user_positions"], "user_positions", source_status, boost=3)
    _extract_symbol_field_list(rows, SOURCE_FILES["my_plays"], "my_plays", source_status, boost=3)

    output = list(rows.values())
    output.sort(key=lambda x: (-int(x.get("priority_rank", 0) or 0), x.get("symbol", "")))
    return output, source_status

def save_market_universe(rows: List[Dict[str, Any]], source_status: Dict[str, Any]) -> None:
    payload = {
        "rows": rows,
        "meta": {
            "saved_at": datetime.now().isoformat(),
            "count": len(rows),
            "source_status": source_status,
        },
    }
    _save_json(MARKET_UNIVERSE_FILE, payload)
    _touch_pipeline_status(len(rows), source_status)

def load_market_universe() -> List[Dict[str, Any]]:
    payload = _load_json(MARKET_UNIVERSE_FILE, [])
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        rows = payload.get("rows", [])
        return rows if isinstance(rows, list) else []
    return []

def load_market_universe_meta() -> Dict[str, Any]:
    payload = _load_json(MARKET_UNIVERSE_FILE, {})
    if isinstance(payload, dict):
        meta = payload.get("meta", {})
        return meta if isinstance(meta, dict) else {}
    return {}

def refresh_market_universe() -> List[Dict[str, Any]]:
    rows, source_status = build_market_universe()
    save_market_universe(rows, source_status)
    return rows

def market_universe_is_stale(max_age_hours: int = 12) -> bool:
    status = _safe_dict(_load_json(PIPELINE_STATUS_FILE, {}))
    run_at = _norm_text(status.get("market_universe_run_at"), "")
    if not run_at:
        return True
    try:
        then = datetime.fromisoformat(run_at)
    except Exception:
        return True
    return datetime.now() - then > timedelta(hours=max_age_hours)

def refresh_market_universe_if_stale(max_age_hours: int = 12) -> List[Dict[str, Any]]:
    if market_universe_is_stale(max_age_hours=max_age_hours):
        return refresh_market_universe()
    return load_market_universe()

def get_market_universe_summary() -> Dict[str, Any]:
    rows = load_market_universe()
    meta = load_market_universe_meta()
    counts_by_tag: Dict[str, int] = {}
    counts_by_type: Dict[str, int] = {}

    for row in rows:
        asset_type = _norm_text(row.get("asset_type", "equity"), "equity")
        counts_by_type[asset_type] = counts_by_type.get(asset_type, 0) + 1
        for tag in _safe_list(row.get("source_tags", [])):
            counts_by_tag[tag] = counts_by_tag.get(tag, 0) + 1

    top_sources = sorted(
        [{"tag": k, "count": v} for k, v in counts_by_tag.items()],
        key=lambda x: x["count"],
        reverse=True,
    )[:15]

    return {
        "total": len(rows),
        "counts_by_type": counts_by_type,
        "top_sources": top_sources,
        "rows": rows,
        "meta": meta,
    }
