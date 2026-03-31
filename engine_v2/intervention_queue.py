import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List

INTERVENTION_QUEUE_FILE = Path("/content/SimpleeMrkTrade/data_v2/intervention_queue.json")

DEFAULT_QUEUE_ITEM = {
    "type": "",
    "headline": "",
    "body": "",
    "actions": [],
    "priority": "medium",
    "created_at": "",
    "seen": False,
    "dismissed": False,
}

VALID_PRIORITIES = {"low", "medium", "high"}


def _load_json(path: Path, default: Any):
    if not path.exists():
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _normalize_action(action: Dict[str, Any]) -> Dict[str, Any]:
    action = _safe_dict(action)
    return {
        "id": str(action.get("id", "") or "").strip(),
        "label": str(action.get("label", "") or "").strip(),
    }


def _normalize_item(item: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(DEFAULT_QUEUE_ITEM)
    if isinstance(item, dict):
        merged.update(item)

    priority = str(merged.get("priority", "medium")).strip().lower()
    if priority not in VALID_PRIORITIES:
        priority = "medium"

    actions = [_normalize_action(a) for a in _safe_list(merged.get("actions", []))]

    merged["type"] = str(merged.get("type", "") or "").strip()
    merged["headline"] = str(merged.get("headline", "") or "").strip()
    merged["body"] = str(merged.get("body", "") or "").strip()
    merged["actions"] = actions
    merged["priority"] = priority
    merged["created_at"] = str(merged.get("created_at", "") or "")
    merged["seen"] = bool(merged.get("seen", False))
    merged["dismissed"] = bool(merged.get("dismissed", False))
    return merged


def load_all_intervention_queues() -> Dict[str, Any]:
    payload = _load_json(INTERVENTION_QUEUE_FILE, {})
    return payload if isinstance(payload, dict) else {}


def save_all_intervention_queues(payload: Dict[str, Any]) -> None:
    if not isinstance(payload, dict):
        payload = {}
    _save_json(INTERVENTION_QUEUE_FILE, payload)


def get_intervention_queue(username: str) -> Dict[str, Any]:
    username = str(username or "").strip().lower()
    all_queues = load_all_intervention_queues()

    if username and username in all_queues:
        row = _safe_dict(all_queues.get(username))
        items = [_normalize_item(x) for x in _safe_list(row.get("items", []))]
        return {
            "username": username,
            "items": items,
            "updated_at": row.get("updated_at", ""),
        }

    return {
        "username": username,
        "items": [],
        "updated_at": "",
    }


def set_intervention_queue(username: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
    username = str(username or "").strip().lower()
    if not username:
        raise ValueError("username is required")

    normalized_items = [_normalize_item(x) for x in _safe_list(items)]
    all_queues = load_all_intervention_queues()

    row = {
        "username": username,
        "items": normalized_items,
        "updated_at": datetime.now().isoformat(),
    }
    all_queues[username] = row
    save_all_intervention_queues(all_queues)
    return row


def add_intervention_item(username: str, item: Dict[str, Any]) -> Dict[str, Any]:
    current = get_intervention_queue(username)
    items = list(current.get("items", []))

    normalized = _normalize_item(item)
    if not normalized.get("created_at"):
        normalized["created_at"] = datetime.now().isoformat()

    items.append(normalized)
    return set_intervention_queue(username, items)


def clear_intervention_queue(username: str) -> Dict[str, Any]:
    return set_intervention_queue(username, [])


def mark_intervention_seen(username: str, item_type: str) -> Dict[str, Any]:
    current = get_intervention_queue(username)
    updated_items = []

    for item in current.get("items", []):
        row = dict(item)
        if row.get("type") == item_type:
            row["seen"] = True
        updated_items.append(row)

    return set_intervention_queue(username, updated_items)


def dismiss_intervention(username: str, item_type: str) -> Dict[str, Any]:
    current = get_intervention_queue(username)
    updated_items = []

    for item in current.get("items", []):
        row = dict(item)
        if row.get("type") == item_type:
            row["dismissed"] = True
            row["seen"] = True
        updated_items.append(row)

    return set_intervention_queue(username, updated_items)


def active_interventions(username: str) -> List[Dict[str, Any]]:
    current = get_intervention_queue(username)
    items = []
    for item in current.get("items", []):
        if not item.get("dismissed", False):
            items.append(item)
    priority_rank = {"high": 0, "medium": 1, "low": 2}
    return sorted(items, key=lambda x: priority_rank.get(x.get("priority", "medium"), 99))
