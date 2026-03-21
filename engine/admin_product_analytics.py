import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter, defaultdict

ANALYTICS_FILE = Path("data/admin_product_analytics.json")
ANALYTICS_FILE.parent.mkdir(parents=True, exist_ok=True)

def _load():
    if not ANALYTICS_FILE.exists():
        return []
    try:
        with open(ANALYTICS_FILE, "r") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []

def _save(data):
    trimmed = data[-5000:]
    with open(ANALYTICS_FILE, "w") as f:
        json.dump(trimmed, f, indent=2)

def track_event(event_type, username=None, page=None, symbol=None, meta=None):
    data = _load()
    row = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "username": username,
        "page": page,
        "symbol": symbol,
        "meta": meta or {},
    }
    data.append(row)
    _save(data)
    return row

def get_events():
    return _load()

def summarize_events(days=30):
    events = _load()
    cutoff = datetime.utcnow() - timedelta(days=days)

    recent = []
    for e in events:
        try:
            ts = datetime.fromisoformat(e.get("timestamp"))
            if ts >= cutoff:
                recent.append(e)
        except Exception:
            continue

    total_events = len(recent)
    unique_users = len(set(e.get("username") for e in recent if e.get("username")))
    page_views = [e for e in recent if e.get("event_type") == "page_view"]
    upgrade_clicks = [e for e in recent if e.get("event_type") == "upgrade_click"]
    login_failures = [e for e in recent if e.get("event_type") == "login_failure"]
    symbol_views = [e for e in recent if e.get("event_type") == "symbol_view"]

    page_counts = Counter(e.get("page") for e in page_views if e.get("page"))
    symbol_counts = Counter(e.get("symbol") for e in symbol_views if e.get("symbol"))
    user_counts = Counter(e.get("username") for e in recent if e.get("username"))

    user_event_buckets = defaultdict(list)
    for e in recent:
        user = e.get("username")
        if user:
            user_event_buckets[user].append(e)

    friction_alerts = []
    for user, rows in user_event_buckets.items():
        fail_count = sum(1 for r in rows if r.get("event_type") == "login_failure")
        upgrade_visits = sum(1 for r in rows if r.get("page") == "/upgrade")
        premium_hits = sum(1 for r in rows if r.get("page") in ["/premium", "/premium-analysis", "/why-this-trade"])

        if fail_count >= 3:
            friction_alerts.append({
                "user": user,
                "type": "login_friction",
                "detail": f"{fail_count} login failures",
            })

        if upgrade_visits >= 2 and premium_hits >= 2:
            friction_alerts.append({
                "user": user,
                "type": "conversion_interest",
                "detail": "Repeated premium/upgrade interest detected",
            })

    summary = {
        "days": days,
        "total_events": total_events,
        "unique_users": unique_users,
        "page_view_count": len(page_views),
        "upgrade_click_count": len(upgrade_clicks),
        "login_failure_count": len(login_failures),
        "symbol_view_count": len(symbol_views),
        "top_pages": [{"name": k, "count": v} for k, v in page_counts.most_common(10)],
        "top_symbols": [{"name": k, "count": v} for k, v in symbol_counts.most_common(10)],
        "top_users": [{"name": k, "count": v} for k, v in user_counts.most_common(10)],
        "friction_alerts": friction_alerts[:20],
        "recent_events": recent[-50:][::-1],
    }
    return summary
