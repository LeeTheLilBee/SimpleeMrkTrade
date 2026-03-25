import json
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict

EVENTS_FILE = "data/product_events.json"


def _load(path, default):
    file_path = Path(path)
    if not file_path.exists():
        return default
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _save(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def log_event(event_type, payload=None):
    events = _load(EVENTS_FILE, [])
    if not isinstance(events, list):
        events = []

    payload = payload or {}
    event = {
        "event_type": event_type,
        "timestamp": datetime.now().isoformat(),
        **payload,
    }
    events.append(event)

    # keep last 5000 events
    events = events[-5000:]
    _save(EVENTS_FILE, events)
    return event


def maybe_track_page_view(path, extra=None):
    return log_event("page_view", {"page": path, **(extra or {})})


def track_symbol_click(symbol, source=None, extra=None):
    payload = {
        "symbol": symbol,
        "source": source or "unknown",
    }
    if extra:
        payload.update(extra)
    return log_event("symbol_click", payload)


def track_trade_click(symbol, trade_id=None, source=None, extra=None):
    payload = {
        "symbol": symbol,
        "trade_id": trade_id,
        "source": source or "unknown",
    }
    if extra:
        payload.update(extra)
    return log_event("trade_click", payload)


def track_upgrade_click(source=None, tier=None, extra=None):
    payload = {
        "source": source or "unknown",
        "tier": tier or "unknown",
    }
    if extra:
        payload.update(extra)
    return log_event("upgrade_click", payload)


def track_cta_click(cta_name, source=None, extra=None):
    payload = {
        "cta_name": cta_name,
        "source": source or "unknown",
    }
    if extra:
        payload.update(extra)
    return log_event("cta_click", payload)


def load_product_events():
    events = _load(EVENTS_FILE, [])
    return events if isinstance(events, list) else []


def build_product_analytics():
    events = load_product_events()

    event_counts = Counter()
    page_counts = Counter()
    symbol_counts = Counter()
    cta_counts = Counter()
    upgrade_counts = Counter()
    source_counts = Counter()

    recent_events = events[-30:][::-1]

    page_to_followups = defaultdict(int)
    page_views = Counter()

    for e in events:
        event_type = e.get("event_type", "unknown")
        event_counts[event_type] += 1

        page = e.get("page")
        symbol = e.get("symbol")
        source = e.get("source")
        cta_name = e.get("cta_name")
        tier = e.get("tier")

        if page:
            page_counts[page] += 1
        if symbol:
            symbol_counts[symbol] += 1
        if cta_name:
            cta_counts[cta_name] += 1
        if tier and event_type == "upgrade_click":
            upgrade_counts[tier] += 1
        if source:
            source_counts[source] += 1

        if event_type == "page_view" and page:
            page_views[page] += 1
        elif source:
            page_to_followups[source] += 1

    friction_signals = []
    for page, views in page_views.items():
        followups = page_to_followups.get(page, 0)
        followup_rate = round((followups / views) * 100, 1) if views else 0.0
        if views >= 3 and followup_rate < 25:
            friction_signals.append({
                "page": page,
                "views": views,
                "followups": followups,
                "followup_rate": followup_rate,
                "signal": "high_attention_low_followthrough",
            })

    friction_signals = sorted(
        friction_signals,
        key=lambda x: (x["followup_rate"], -x["views"])
    )

    return {
        "totals": {
            "events": len(events),
            "page_views": event_counts.get("page_view", 0),
            "symbol_clicks": event_counts.get("symbol_click", 0),
            "trade_clicks": event_counts.get("trade_click", 0),
            "upgrade_clicks": event_counts.get("upgrade_click", 0),
            "cta_clicks": event_counts.get("cta_click", 0),
        },
        "top_pages": page_counts.most_common(10),
        "top_symbols": symbol_counts.most_common(10),
        "top_ctas": cta_counts.most_common(10),
        "upgrade_interest": upgrade_counts.most_common(10),
        "top_sources": source_counts.most_common(10),
        "friction_signals": friction_signals[:10],
        "recent_events": recent_events,
    }
