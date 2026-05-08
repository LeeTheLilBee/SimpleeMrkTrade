from __future__ import annotations

"""
Observatory Trade Activity Bridge

Purpose:
    Feed executed trade activity back into the governor-readable account state.

Why this matters:
    The risk governor can only enforce daily / rolling activity limits if every
    successful execution creates an activity event.

Writes:
    1. data/trade_activity_events.json
       - fallback audit trail

    2. data/account_state.json["activity_log"]
       - official account activity source used by governor reconciliation

Rules:
    - ENTRY events count as new openings.
    - SKIP / REJECT events are stored for audit but should not count as entries.
    - Duplicate ENTRY events for the same trade_id are ignored.
    - This module does not place trades. It only records already-finished outcomes.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path("/content/SimpleeMrkTrade")
DATA_DIR = PROJECT_ROOT / "data"
FALLBACK_EVENT_PATH = DATA_DIR / "trade_activity_events.json"
ACCOUNT_STATE_PATH = DATA_DIR / "account_state.json"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value if value is not None else "").strip()
        return text if text else default
    except Exception:
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return float(default)
        if isinstance(value, str):
            cleaned = value.replace("$", "").replace(",", "").strip()
            if cleaned == "":
                return float(default)
            value = cleaned
        return float(value)
    except Exception:
        return float(default)


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return int(default)
        if isinstance(value, str):
            cleaned = value.replace(",", "").strip()
            if cleaned == "":
                return int(default)
            value = cleaned
        return int(float(value))
    except Exception:
        return int(default)


def _now_iso() -> str:
    return datetime.now().isoformat()


def _today_key() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _read_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    tmp.replace(path)


def _event_key(event: Dict[str, Any]) -> str:
    event = _safe_dict(event)
    return "|".join([
        _safe_str(event.get("event_type"), "").upper(),
        _safe_str(event.get("trade_id"), ""),
        _safe_str(event.get("symbol"), "").upper(),
        _safe_str(event.get("account_id"), "default"),
    ])


def _activity_event_from_position(
    *,
    position: Dict[str, Any],
    event_type: str,
    account_id: str = "default",
    source: str = "execution_loop",
    reason: str = "",
) -> Dict[str, Any]:
    position = _safe_dict(position)
    event_type = _safe_str(event_type, "ENTRY").upper()

    vehicle = _safe_str(
        position.get("vehicle_selected")
        or position.get("selected_vehicle")
        or position.get("vehicle")
        or position.get("asset_type"),
        "UNKNOWN",
    ).upper()

    symbol = _safe_str(position.get("symbol"), "UNKNOWN").upper()
    strategy = _safe_str(position.get("strategy") or position.get("side"), "").upper()

    trade_id = _safe_str(position.get("trade_id"), "")
    if not trade_id:
        trade_id = f"{symbol}-{strategy}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    entry_price = _safe_float(
        position.get("entry")
        or position.get("entry_price")
        or position.get("entry_premium")
        or position.get("fill_price"),
        0.0,
    )

    underlying_price = _safe_float(
        position.get("underlying_price")
        or position.get("current_underlying_price")
        or position.get("stock_price"),
        0.0,
    )

    premium = _safe_float(
        position.get("entry_premium")
        or position.get("premium_entry")
        or position.get("option_entry")
        or position.get("option_entry_price")
        or entry_price,
        0.0,
    )

    timestamp = _safe_str(position.get("opened_at") or position.get("timestamp"), _now_iso())
    date_key = timestamp[:10] if len(timestamp) >= 10 else _today_key()

    return {
        "event_id": f"{event_type}-{trade_id}-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
        "event_key": "",
        "event_type": event_type,
        "activity_type": event_type,
        "type": event_type,
        "action": event_type,
        "timestamp": timestamp,
        "date_key": date_key,
        "account_id": _safe_str(account_id, "default"),
        "source": _safe_str(source, "execution_loop"),
        "reason": _safe_str(reason, ""),
        "trade_id": trade_id,
        "symbol": symbol,
        "strategy": strategy,
        "vehicle": vehicle,
        "vehicle_selected": vehicle,
        "selected_vehicle": vehicle,
        "status": _safe_str(position.get("status"), "OPEN"),
        "position_status": _safe_str(position.get("position_status"), "OPEN"),
        "contracts": _safe_int(position.get("contracts"), 0),
        "shares": _safe_int(position.get("shares"), 0),
        "quantity": _safe_int(position.get("quantity") or position.get("qty") or position.get("size"), 0),
        "entry": entry_price,
        "entry_price": entry_price,
        "entry_premium": premium,
        "premium_entry": premium,
        "underlying_price": underlying_price,
        "capital_required": _safe_float(position.get("capital_required"), 0.0),
        "minimum_trade_cost": _safe_float(position.get("minimum_trade_cost"), 0.0),
        "actual_cost": _safe_float(position.get("actual_cost"), 0.0),
        "contract_symbol": _safe_str(
            position.get("contract_symbol")
            or position.get("contractSymbol")
            or position.get("option_symbol")
            or position.get("option_contract_symbol"),
            "",
        ),
        "expiry": _safe_str(position.get("expiry") or position.get("expiration"), ""),
        "expiration": _safe_str(position.get("expiration") or position.get("expiry"), ""),
        "right": _safe_str(position.get("right") or position.get("option_type") or position.get("call_put"), ""),
        "strike": _safe_float(position.get("strike") or position.get("strike_price"), 0.0),
        "monitoring_price_type": _safe_str(position.get("monitoring_price_type"), ""),
        "price_review_basis": _safe_str(position.get("price_review_basis"), ""),
        "pnl_basis": _safe_str(position.get("pnl_basis"), ""),
        "count_as_entry": event_type == "ENTRY",
        "count_as_close": event_type == "CLOSE",
        "activity_bridge_version": "2026-05-08.2",
    }


def _append_unique_event(path: Path, event: Dict[str, Any]) -> bool:
    events = _read_json(path, [])
    if not isinstance(events, list):
        events = []

    key = _event_key(event)
    event["event_key"] = key

    existing_keys = {
        _safe_str(row.get("event_key"), "") or _event_key(row)
        for row in events
        if isinstance(row, dict)
    }

    if key in existing_keys:
        return False

    events.append(event)
    _write_json(path, events)
    return True


def _append_account_state_activity(event: Dict[str, Any]) -> Dict[str, Any]:
    state = _read_json(ACCOUNT_STATE_PATH, {})
    if not isinstance(state, dict):
        state = {}

    activity_log = state.get("activity_log", [])
    if not isinstance(activity_log, list):
        activity_log = []

    key = _event_key(event)
    event["event_key"] = key

    existing_keys = {
        _safe_str(row.get("event_key"), "") or _event_key(row)
        for row in activity_log
        if isinstance(row, dict)
    }

    existing_entry_trade_ids = {
        _safe_str(row.get("trade_id"), "")
        for row in activity_log
        if isinstance(row, dict)
        and _safe_str(row.get("event_type") or row.get("activity_type") or row.get("type"), "").upper() == "ENTRY"
    }

    event_type = _safe_str(event.get("event_type"), "").upper()
    trade_id = _safe_str(event.get("trade_id"), "")

    if key in existing_keys:
        return {
            "recorded": False,
            "reason": "duplicate_event_key",
            "activity_log_count": len(activity_log),
        }

    if event_type == "ENTRY" and trade_id and trade_id in existing_entry_trade_ids:
        return {
            "recorded": False,
            "reason": "duplicate_entry_trade_id",
            "activity_log_count": len(activity_log),
        }

    activity_log.append(event)
    state["activity_log"] = activity_log
    state["last_activity_event"] = event
    state["last_activity_update"] = _now_iso()

    _write_json(ACCOUNT_STATE_PATH, state)

    return {
        "recorded": True,
        "reason": "recorded_to_account_state_activity_log",
        "activity_log_count": len(activity_log),
    }


def record_entry_event(
    position: Dict[str, Any],
    *,
    account_id: str = "default",
    source: str = "execution_loop",
    reason: str = "position_persisted",
) -> Dict[str, Any]:
    event = _activity_event_from_position(
        position=position,
        event_type="ENTRY",
        account_id=account_id,
        source=source,
        reason=reason,
    )

    fallback_recorded = _append_unique_event(FALLBACK_EVENT_PATH, dict(event))
    account_state_result = _append_account_state_activity(dict(event))

    print("TRADE ACTIVITY RECORDED:", {
        "event_type": event.get("event_type"),
        "symbol": event.get("symbol"),
        "trade_id": event.get("trade_id"),
        "vehicle": event.get("vehicle"),
        "account_state_recorded": account_state_result.get("recorded"),
        "account_state_reason": account_state_result.get("reason"),
        "fallback_recorded": fallback_recorded,
    })

    return {
        "recorded": bool(account_state_result.get("recorded")) or fallback_recorded,
        "event": event,
        "account_state_result": account_state_result,
        "fallback_path": str(FALLBACK_EVENT_PATH),
        "fallback_recorded": fallback_recorded,
    }


def record_skip_event(
    trade: Dict[str, Any],
    *,
    account_id: str = "default",
    source: str = "execution_loop",
    reason: str = "skipped",
) -> Dict[str, Any]:
    event = _activity_event_from_position(
        position=trade,
        event_type="SKIP",
        account_id=account_id,
        source=source,
        reason=reason,
    )

    fallback_recorded = _append_unique_event(FALLBACK_EVENT_PATH, dict(event))
    account_state_result = _append_account_state_activity(dict(event))

    print("TRADE SKIP ACTIVITY RECORDED:", {
        "event_type": event.get("event_type"),
        "symbol": event.get("symbol"),
        "trade_id": event.get("trade_id"),
        "reason": reason,
        "account_state_recorded": account_state_result.get("recorded"),
        "account_state_reason": account_state_result.get("reason"),
        "fallback_recorded": fallback_recorded,
    })

    return {
        "recorded": bool(account_state_result.get("recorded")) or fallback_recorded,
        "event": event,
        "account_state_result": account_state_result,
        "fallback_path": str(FALLBACK_EVENT_PATH),
        "fallback_recorded": fallback_recorded,
    }


__all__ = [
    "record_entry_event",
    "record_skip_event",
]
