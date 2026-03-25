import json
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict

EVENTS_FILE = "data/product_events.json"
CANDIDATE_FILE = "data/candidate_log.json"


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
    events = events[-5000:]
    _save(EVENTS_FILE, events)
    return event


def track_premium_wall_seen(source=None, section=None, extra=None):
    payload = {
        "source": source or "unknown",
        "section": section or "unknown",
    }
    if extra:
        payload.update(extra)
    return log_event("premium_wall_seen", payload)


def track_premium_content_view(source=None, section=None, extra=None):
    payload = {
        "source": source or "unknown",
        "section": section or "unknown",
    }
    if extra:
        payload.update(extra)
    return log_event("premium_content_view", payload)


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


def top_engaged_symbols(limit=10):
    events = load_product_events()
    symbol_counts = Counter()

    for e in events:
        if e.get("event_type") in {"symbol_click", "trade_click", "symbol_exposed"}:
            symbol = e.get("symbol")
            if symbol:
                symbol_counts[symbol] += 1

    return [symbol for symbol, _ in symbol_counts.most_common(limit)]


def top_engaged_symbols_with_counts(limit=5):
    events = load_product_events()
    symbol_counts = Counter()

    for e in events:
        if e.get("event_type") in {"symbol_click", "trade_click", "symbol_exposed"}:
            symbol = e.get("symbol")
            if symbol:
                symbol_counts[symbol] += 1

    return [
        {"symbol": symbol, "count": count}
        for symbol, count in symbol_counts.most_common(limit)
    ]


def most_underrated_symbols(limit=5):
    events = load_product_events()
    symbol_counts = Counter()

    for e in events:
        if e.get("event_type") in {"symbol_click", "trade_click", "symbol_exposed"}:
            symbol = e.get("symbol")
            if symbol:
                symbol_counts[symbol] += 1

    candidates = _load(CANDIDATE_FILE, [])
    if not isinstance(candidates, list):
        candidates = []

    best_by_symbol = {}

    for row in candidates:
        symbol = row.get("symbol")
        score = float(row.get("score", 0) or 0)

        if not symbol:
            continue

        existing = best_by_symbol.get(symbol)
        if existing is None or score > existing["score"]:
            best_by_symbol[symbol] = {
                "symbol": symbol,
                "score": score,
                "confidence": row.get("confidence"),
                "views": symbol_counts.get(symbol, 0),
                "status": row.get("status"),
            }

    underrated = []
    for symbol, row in best_by_symbol.items():
        views = max(row["views"], 1)
        row["underrated_score"] = round(row["score"] / views, 2)
        underrated.append(row)

    underrated.sort(key=lambda x: (x["underrated_score"], x["score"]), reverse=True)
    return underrated[:limit]


def build_product_analytics():
    events = load_product_events()

    event_counts = Counter()
    page_counts = Counter()
    symbol_counts = Counter()
    cta_counts = Counter()
    upgrade_counts = Counter()
    source_counts = Counter()
    page_views = Counter()
    page_to_followups = defaultdict(int)

    recent_events = events[-30:][::-1]

    # 🔹 MAIN EVENT LOOP
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

    # 🔹 MOST REVISITED
    symbol_sessions = {}

    for e in events:
        symbol = e.get("symbol")
        if not symbol:
            continue

        symbol_sessions.setdefault(symbol, set())
        ts = e.get("timestamp", "")[:16]
        symbol_sessions[symbol].add(ts)

    most_revisited = []

    for symbol, sessions in symbol_sessions.items():
        revisit_count = len(sessions)

        if revisit_count >= 2:
            most_revisited.append({
                "symbol": symbol,
                "revisits": revisit_count,
            })

    most_revisited.sort(key=lambda x: x["revisits"], reverse=True)

    # 🔹 FRICTION SIGNALS
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

    # 🔹 HIGH ATTENTION / LOW ACTION
    high_attention_low_action = []

    for symbol, views in symbol_counts.items():
        actions = sum(
            1 for e in events
            if e.get("event_type") == "trade_click" and e.get("symbol") == symbol
        )

        views_safe = max(views, 1)
        action_rate = round((actions / views_safe) * 100, 1)

        if views >= 3 and action_rate < 20:
            high_attention_low_action.append({
                "symbol": symbol,
                "views": views,
                "actions": actions,
                "action_rate": action_rate,
            })

    high_attention_low_action.sort(
        key=lambda x: (x["action_rate"], -x["views"])
    )
    

    premium_wall_counts = Counter()
    premium_content_counts = Counter()
    premium_curiosity = []

    for e in events:
        event_type = e.get("event_type")
        source = e.get("source", "unknown")
        section = e.get("section", "unknown")
        key = f"{source}::{section}"

        if event_type == "premium_wall_seen":
            premium_wall_counts[key] += 1
        elif event_type == "premium_content_view":
            premium_content_counts[key] += 1

    all_premium_keys = set(premium_wall_counts.keys()) | set(premium_content_counts.keys())

    for key in all_premium_keys:
        wall_views = premium_wall_counts.get(key, 0)
        content_views = premium_content_counts.get(key, 0)
        followthrough_rate = round((content_views / max(wall_views, 1)) * 100, 1)

        source, section = key.split("::", 1)

        premium_curiosity.append({
            "source": source,
            "section": section,
            "wall_views": wall_views,
            "content_views": content_views,
            "followthrough_rate": followthrough_rate,
        })

    premium_curiosity.sort(
        key=lambda x: (x["followthrough_rate"], -x["wall_views"])
    )


    # 🔹 INSIGHTS
    insights = []

    for row in friction_signals:
        insights.append(
            f"{row['page']} is drawing attention but producing weak follow-through ({row['followup_rate']}%)."
        )

    for row in high_attention_low_action[:3]:
        insights.append(
            f"{row['symbol']} has high attention ({row['views']} views) but low action ({row['action_rate']}%)."
        )

    for row in premium_curiosity[:3]:
        if row["wall_views"] >= 2 and row["followthrough_rate"] < 35:
            insights.append(
                f"Premium curiosity is forming around {row['section']} from {row['source']}, but follow-through is only {row['followthrough_rate']}%."
            )

    for row in most_revisited[:3]:
        insights.append(
            f"{row['symbol']} is being revisited frequently ({row['revisits']} sessions)."
        )

    if upgrade_counts:
        total_upgrade_clicks = sum(upgrade_counts.values())
        if total_upgrade_clicks < 3:
            insights.append("Upgrade interest is low. Premium value may not be clear.")
    else:
        insights.append("No upgrade activity recorded yet.")

    if symbol_counts:
        top_symbol, count = symbol_counts.most_common(1)[0]
        insights.append(f"{top_symbol} is the most interacted symbol ({count} interactions).")

    if page_counts:
        top_page, count = page_counts.most_common(1)[0]
        insights.append(f"{top_page} is the highest traffic page ({count} visits).")

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
        "high_attention_low_action": high_attention_low_action[:10],
        "premium_curiosity": premium_curiosity[:10],
        "most_revisited": most_revisited[:10],
        "recent_events": recent_events,
        "insights": insights,
    }
