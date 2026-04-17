from __future__ import annotations

import json
import os
from threading import Lock
from typing import Any, Dict, List, Optional

QUEUE_FILE = "data/trade_queue.json"

_trade_queue: List[Dict[str, Any]] = []
_queue_lock = Lock()
_loaded = False


def _ensure_parent_dir(path: str) -> None:
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)


def _normalize_trade(trade: Dict[str, Any]) -> Dict[str, Any]:
    return dict(trade or {})


def _save_queue() -> None:
    _ensure_parent_dir(QUEUE_FILE)
    temp_path = f"{QUEUE_FILE}.tmp"
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(_trade_queue, f, indent=2)
    os.replace(temp_path, QUEUE_FILE)


def _load_queue() -> None:
    global _loaded, _trade_queue
    if _loaded:
        return

    _ensure_parent_dir(QUEUE_FILE)

    if not os.path.exists(QUEUE_FILE):
        _trade_queue = []
        _save_queue()
        _loaded = True
        return

    try:
        with open(QUEUE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            _trade_queue = [dict(item) for item in data if isinstance(item, dict)]
        else:
            _trade_queue = []
    except Exception:
        _trade_queue = []

    _loaded = True
    _save_queue()


def add_trade(trade: Dict[str, Any]) -> Dict[str, Any]:
    item = _normalize_trade(trade)
    with _queue_lock:
        _load_queue()
        _trade_queue.append(item)
        _save_queue()
    return item


def next_trade() -> Optional[Dict[str, Any]]:
    with _queue_lock:
        _load_queue()
        if not _trade_queue:
            return None
        item = _trade_queue.pop(0)
        _save_queue()
        return item


def clear_trade_queue() -> None:
    with _queue_lock:
        _load_queue()
        _trade_queue.clear()
        _save_queue()


def queue_size() -> int:
    with _queue_lock:
        _load_queue()
        return len(_trade_queue)


def show_trade_queue() -> List[Dict[str, Any]]:
    with _queue_lock:
        _load_queue()
        return [dict(item) for item in _trade_queue]


def reload_trade_queue() -> List[Dict[str, Any]]:
    global _loaded
    with _queue_lock:
        _loaded = False
        _load_queue()
        return [dict(item) for item in _trade_queue]
