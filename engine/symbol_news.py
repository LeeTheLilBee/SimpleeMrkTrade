from datetime import datetime
from engine.symbol_metadata import get_symbol_meta

try:
    import yfinance as yf
except Exception:
    yf = None


def _normalize_news_item(item, symbol):
    title = item.get("title") or "Untitled"
    publisher = item.get("publisher") or item.get("source") or "Unknown source"
    link = item.get("link") or item.get("url")
    published = item.get("providerPublishTime") or item.get("published_at")

    published_text = None
    if isinstance(published, (int, float)):
        try:
            published_text = datetime.fromtimestamp(published).isoformat()
        except Exception:
            published_text = None
    elif isinstance(published, str):
        published_text = published

    return {
        "symbol": symbol,
        "title": title,
        "publisher": publisher,
        "link": link,
        "published_at": published_text,
    }


def get_symbol_news(symbol: str, limit: int = 8):
    symbol = (symbol or "").upper()

    if yf is None:
        return []

    try:
        ticker = yf.Ticker(symbol)
        news = getattr(ticker, "news", []) or []
        normalized = [_normalize_news_item(item, symbol) for item in news[:limit]]
        return normalized
    except Exception:
        return []


def get_symbol_profile(symbol: str):
    symbol = (symbol or "").upper()
    return get_symbol_meta(symbol)
