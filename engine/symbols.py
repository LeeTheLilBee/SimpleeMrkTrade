import json
import time
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List

import requests
import yfinance as yf

SYMBOL_NEWS_FILE = "data/symbol_news.json"
PIPELINE_STATUS_FILE = "data/pipeline_status.json"

GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"


def _load_json(path: str, default):
    file_path = Path(path)
    if not file_path.exists():
        return default
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _save_json(path: str, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _norm_text(value, default=""):
    text = str(value or "").strip()
    return text if text else default


def _norm_upper(value, default=""):
    text = _norm_text(value).upper()
    return text if text else default


def _safe_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default


def _load_news_store() -> Dict[str, Any]:
    data = _load_json(SYMBOL_NEWS_FILE, {})
    return data if isinstance(data, dict) else {}


def _save_news_store(data: Dict[str, Any]) -> None:
    if not isinstance(data, dict):
        data = {}
    _save_json(SYMBOL_NEWS_FILE, data)


def _load_pipeline_status() -> Dict[str, Any]:
    data = _load_json(PIPELINE_STATUS_FILE, {})
    return data if isinstance(data, dict) else {}


def _save_pipeline_status(data: Dict[str, Any]) -> None:
    if not isinstance(data, dict):
        data = {}
    _save_json(PIPELINE_STATUS_FILE, data)


def _touch_news_sync(symbol: str, item_count: int) -> None:
    status = _load_pipeline_status()
    now_iso = datetime.now().isoformat()

    status["news_sync_at"] = now_iso

    per_symbol = status.get("symbol_news_sync", {})
    if not isinstance(per_symbol, dict):
        per_symbol = {}

    per_symbol[symbol] = {
        "synced_at": now_iso,
        "item_count": item_count,
    }
    status["symbol_news_sync"] = per_symbol
    _save_pipeline_status(status)


def _touch_bulk_news_sync(symbol_count: int) -> None:
    status = _load_pipeline_status()
    now_iso = datetime.now().isoformat()
    status["news_sync_at"] = now_iso
    status["bulk_news_sync_at"] = now_iso
    status["bulk_news_symbol_count"] = symbol_count
    _save_pipeline_status(status)


def _parse_google_news_rss(xml_text: str) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []

    root = ET.fromstring(xml_text)
    channel = root.find("channel")
    if channel is None:
        return items

    for item in channel.findall("item"):
        title = _norm_text(item.findtext("title"))
        link = _norm_text(item.findtext("link"))
        pub_date = _norm_text(item.findtext("pubDate"))
        source_el = item.find("source")
        source = _norm_text(source_el.text if source_el is not None else "", "Google News")

        if not title:
            continue

        items.append({
            "title": title,
            "summary": "",
            "source": source,
            "published_at": pub_date,
            "url": link,
        })

    return items


def _normalize_news_item(item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "title": _norm_text(item.get("title"), "Untitled"),
        "summary": _norm_text(item.get("summary"), ""),
        "source": _norm_text(item.get("source"), "Unknown source"),
        "published_at": item.get("published_at"),
        "url": _norm_text(item.get("url"), ""),
    }


def _fetch_yfinance_news(symbol: str, limit: int = 8) -> List[Dict[str, Any]]:
    try:
        ticker = yf.Ticker(symbol)
        raw = ticker.news or []
    except Exception:
        return []

    items: List[Dict[str, Any]] = []

    for item in raw[: max(limit * 2, 10)]:
        content = item.get("content", {}) if isinstance(item, dict) else {}

        title = _norm_text(content.get("title") or item.get("title"))
        summary = _norm_text(content.get("summary") or item.get("summary"))
        source = _norm_text(
            content.get("provider", {}).get("displayName")
            if isinstance(content.get("provider"), dict) else item.get("publisher"),
            "Yahoo Finance",
        )
        url = _norm_text(
            content.get("canonicalUrl", {}).get("url")
            if isinstance(content.get("canonicalUrl"), dict) else item.get("link")
        )

        pub_raw = content.get("pubDate") or item.get("providerPublishTime") or item.get("published_at")

        if isinstance(pub_raw, (int, float)):
            published_at = datetime.fromtimestamp(pub_raw).isoformat()
        else:
            published_at = _norm_text(pub_raw)

        if not title:
            continue

        items.append(_normalize_news_item({
            "title": title,
            "summary": summary,
            "source": source,
            "published_at": published_at,
            "url": url,
        }))

    return items[:limit]


def get_symbol_detail(symbol: str) -> dict:
    symbol = str(symbol or "").upper().strip()

    news = []
    try:
        news = load_symbol_news(symbol) or []
        if not isinstance(news, list):
            news = []
    except Exception:
        news = []

    return {
        "symbol": symbol,
        "company_name": symbol,
        "price": None,
        "change_pct": None,
        "trend_label": "",
        "headline": "",
        "summary": "",
        "news": news[:3],
    }


def _fetch_google_news(symbol: str, company_name: str = "", limit: int = 8, timeout: int = 15) -> List[Dict[str, Any]]:
    if company_name:
        query = f'"{symbol}" OR "{company_name}" stock'
    else:
        query = f'"{symbol}" stock'

    url = GOOGLE_NEWS_RSS.format(query=urllib.parse.quote(query))

    try:
        response = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": "Mozilla/5.0 SimpleeMrkTrade/1.0"},
        )
        response.raise_for_status()
        items = _parse_google_news_rss(response.text)
        return [_normalize_news_item(x) for x in items[:limit]]
    except Exception:
        return []


def load_symbol_news(symbol: str) -> List[Dict[str, Any]]:
    symbol = _norm_upper(symbol)
    store = _load_news_store()

    rows = store.get(symbol, [])
    if isinstance(rows, dict):
        rows = rows.get("items", [])
    if not isinstance(rows, list):
        return []

    return [_normalize_news_item(x) for x in rows if isinstance(x, dict)]


def refresh_symbol_news(
    symbol: str,
    company_name: str = "",
    limit: int = 8,
    max_age_minutes: int = 30,
    force: bool = False,
) -> List[Dict[str, Any]]:
    symbol = _norm_upper(symbol)
    if not symbol:
        return []

    store = _load_news_store()
    existing = store.get(symbol, {})
    now_ts = int(time.time())

    if isinstance(existing, dict):
        refreshed_at_ts = _safe_int(existing.get("refreshed_at_ts"), 0)
        items = existing.get("items", [])
        if (
            not force
            and refreshed_at_ts > 0
            and (now_ts - refreshed_at_ts) < max_age_minutes * 60
            and isinstance(items, list)
            and len(items) > 0
        ):
            return [_normalize_news_item(x) for x in items if isinstance(x, dict)]

    items = _fetch_yfinance_news(symbol=symbol, limit=limit)

    if not items:
        items = _fetch_google_news(symbol=symbol, company_name=company_name, limit=limit)

    payload = {
        "items": items,
        "refreshed_at": datetime.now().isoformat(),
        "refreshed_at_ts": now_ts,
        "source": "yfinance_then_google",
    }

    store[symbol] = payload
    _save_news_store(store)
    _touch_news_sync(symbol, len(items))

    return items


def refresh_news_for_symbols(
    symbol_rows: List[Dict[str, Any]],
    limit_per_symbol: int = 8,
    max_symbols: int = 250,
    force: bool = False,
) -> Dict[str, Any]:
    store = _load_news_store()
    refreshed = 0

    for row in symbol_rows[:max_symbols]:
        if not isinstance(row, dict):
            continue

        symbol = _norm_upper(row.get("symbol"))
        company_name = _norm_text(row.get("company_name"), "")
        if not symbol:
            continue

        items = refresh_symbol_news(
            symbol=symbol,
            company_name=company_name,
            limit=limit_per_symbol,
            max_age_minutes=30,
            force=force,
        )
        refreshed += 1
        store[symbol] = {
            "items": items,
            "refreshed_at": datetime.now().isoformat(),
            "refreshed_at_ts": int(time.time()),
            "source": "bulk_refresh",
        }

    _save_news_store(store)
    _touch_bulk_news_sync(refreshed)

    return {
        "refreshed_symbols": refreshed,
        "cached_symbols": len(store),
    }
