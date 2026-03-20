import json
from datetime import datetime
from pathlib import Path
from engine.notification_settings import get_notification_settings

FILE = "data/notifications.json"

TIER_ORDER = {
    "free": 0,
    "guest": 0,
    "starter": 1,
    "pro": 2,
    "elite": 3,
    "master": 4,
}

TYPE_TO_SETTING = {
    "HIGH_CONVICTION": "research_alerts",
    "RESEARCH_ALPHA": "research_alerts",
    "EXECUTION_APPROVED": "execution_alerts",
    "AUTO_CLOSE": "risk_alerts",
    "RISK_WARNING": "risk_alerts",
    "SYSTEM": "system_alerts",
}

def _load():
    if not Path(FILE).exists():
        return []
    with open(FILE, "r") as f:
        return json.load(f)

def _save(data):
    with open(FILE, "w") as f:
        json.dump(data[-400:], f, indent=2)

def push_notification(
    notif_type,
    message,
    trade_id=None,
    min_tier="starter",
    level="info",
    score=None,
    strategy=None,
    volatility=None,
    source=None,
):
    data = _load()
    entry = {
        "timestamp": datetime.now().isoformat(),
        "type": notif_type,
        "message": message,
        "trade_id": trade_id,
        "tier_required": min_tier,
        "level": level,
        "score": score,
        "strategy": strategy,
        "volatility": volatility,
        "source": source,
    }
    data.append(entry)
    _save(data)
    return entry

def _passes_tier(user_tier, item):
    current = TIER_ORDER.get((user_tier or "guest").lower(), 0)
    required = TIER_ORDER.get((item.get("tier_required") or "starter").lower(), 1)
    return current >= required

def _passes_settings(settings, item):
    notif_type = item.get("type", "SYSTEM")
    toggle_name = TYPE_TO_SETTING.get(notif_type, "system_alerts")

    if not settings.get(toggle_name, True):
        return False

    if settings.get("high_conviction_only"):
        score = item.get("score")
        if score is None or score < 120:
            return False

    min_score = int(settings.get("min_score", 0) or 0)
    score = item.get("score")
    if score is not None and score < min_score:
        return False

    strategy_filter = settings.get("strategy_filter", "ALL")
    if strategy_filter != "ALL":
        if (item.get("strategy") or "").upper() != strategy_filter.upper():
            return False

    volatility_filter = settings.get("volatility_filter", "ALL")
    if volatility_filter != "ALL":
        if (item.get("volatility") or "").upper() != volatility_filter.upper():
            return False

    source = (item.get("source") or "").lower()
    if source == "research" and not settings.get("research_alerts", True):
        return False
    if source == "execution" and not settings.get("execution_alerts", True):
        return False

    return True

def notifications_for_user(username, user_tier):
    settings = get_notification_settings(username) if username else {
        "high_conviction_only": False,
        "research_alerts": True,
        "execution_alerts": True,
        "risk_alerts": True,
        "system_alerts": True,
        "min_score": 0,
        "strategy_filter": "ALL",
        "volatility_filter": "ALL",
    }

    visible = []
    for item in _load():
        if not _passes_tier(user_tier, item):
            continue
        if not _passes_settings(settings, item):
            continue
        visible.append(item)

    return sorted(visible, key=lambda x: x.get("timestamp", ""), reverse=True)

def clear_notifications():
    _save([])
    return True
