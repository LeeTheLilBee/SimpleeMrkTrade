from typing import Any, Dict, List

from engine_v2.engine_helpers import _load_json, _save_json, now_iso

BEHAVIOR_EVENT_LOG_FILE = "/content/SimpleeMrkTrade/data_v2/behavior_event_log.json"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def load_behavior_event_log() -> Dict[str, Any]:
    payload = _load_json(BEHAVIOR_EVENT_LOG_FILE, {})
    return payload if isinstance(payload, dict) else {}


def _normalize_event(event: Dict[str, Any]) -> Dict[str, Any]:
    event = _safe_dict(event)
    return {
        "username": str(event.get("username", "") or "").strip().lower(),
        "event_type": str(event.get("event_type", "") or "").strip().lower(),
        "symbol": str(event.get("symbol", "") or "").strip().upper(),
        "context": _safe_dict(event.get("context", {})),
        "note": str(event.get("note", "") or "").strip(),
        "timestamp": str(event.get("timestamp", "") or now_iso()),
    }


def append_behavior_event(
    username: str,
    event_type: str,
    symbol: str = "",
    context: Dict[str, Any] | None = None,
    note: str = "",
) -> Dict[str, Any]:
    username = str(username or "").strip().lower()
    event_type = str(event_type or "").strip().lower()

    payload = load_behavior_event_log()
    items = _safe_list(payload.get("items", []))

    event = _normalize_event({
        "username": username,
        "event_type": event_type,
        "symbol": symbol,
        "context": context or {},
        "note": note,
        "timestamp": now_iso(),
    })

    items.append(event)

    payload["items"] = items[-500:]
    payload["meta"] = {
        "updated_at": now_iso(),
        "count": len(payload["items"]),
    }

    _save_json(BEHAVIOR_EVENT_LOG_FILE, payload)
    return event


def get_user_behavior_events(username: str) -> List[Dict[str, Any]]:
    username = str(username or "").strip().lower()
    payload = load_behavior_event_log()
    items = _safe_list(payload.get("items", []))
    return [item for item in items if _safe_dict(item).get("username") == username]


def build_behavior_event_log_summary(username: str) -> Dict[str, Any]:
    events = get_user_behavior_events(username)

    counts: Dict[str, int] = {}
    symbols: Dict[str, int] = {}

    for event in events:
        row = _safe_dict(event)
        event_type = str(row.get("event_type", "") or "").strip().lower()
        symbol = str(row.get("symbol", "") or "").strip().upper()

        if event_type:
            counts[event_type] = counts.get(event_type, 0) + 1
        if symbol:
            symbols[symbol] = symbols.get(symbol, 0) + 1

    top_symbols = sorted(
        [{"symbol": k, "count": v} for k, v in symbols.items()],
        key=lambda x: x["count"],
        reverse=True,
    )[:10]

    return {
        "username": username,
        "event_count": len(events),
        "counts": counts,
        "top_symbols": top_symbols,
    }
