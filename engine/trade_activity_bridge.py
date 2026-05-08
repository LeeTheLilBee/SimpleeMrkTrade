from __future__ import annotations

"""
Observatory Trade Activity Bridge

Purpose:
    Create one safe place where execution modules can record trade activity
    after a position is successfully persisted.

Why this exists:
    The risk governor now reads reconciled activity counters, but execution_loop
    must feed that activity log every time it opens a position.

Design:
    - Safe for paper mode.
    - Safe no-op if account_state does not expose a recorder yet.
    - Writes a fallback JSON event file so the activity is still auditable.
    - Keeps ENTRY, CLOSE, REJECT, SKIP activity separate.
    - Does not change live execution behavior.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path("/content/SimpleeMrkTrade")
DATA_DIR = PROJECT_ROOT / "data"
FALLBACK_EVENT_PATH = DATA_DIR / "trade_activity_events.json"


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
            value = value.replace("$", "").replace(",", "").strip()
            if value == "":
                return float(default)
        return float(value)
    except Exception:
        return float(default)


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return int(default)
        if isinstance(value, str):
            value = value.replace(",", "").strip()
            if value == "":
                return int(default)
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

    return {
        "event_id": f"{event_type}-{trade_id}-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
        "event_type": event_type,
        "action": event_type,
        "timestamp": _now_iso(),
        "date_key": _today_key(),
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
        "right": _safe_str(position.get("right") or position.get("option_type") or position.get("call_put"), ""),
        "strike": _safe_float(position.get("strike") or position.get("strike_price"), 0.0),
        "monitoring_price_type": _safe_str(position.get("monitoring_price_type"), ""),
        "price_review_basis": _safe_str(position.get("price_review_basis"), ""),
        "pnl_basis": _safe_str(position.get("pnl_basis"), ""),
        "activity_bridge_version": "2026-05-08.1",
    }


def _append_fallback_event(event: Dict[str, Any]) -> None:
    events = _read_json(FALLBACK_EVENT_PATH, [])
    if not isinstance(events, list):
        events = []

    event_id = _safe_str(event.get("event_id"), "")
    existing_ids = {
        _safe_str(row.get("event_id"), "")
        for row in events
        if isinstance(row, dict)
    }

    if event_id and event_id in existing_ids:
        return

    events.append(event)
    _write_json(FALLBACK_EVENT_PATH, events)


def _try_account_state_record(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Attempts several likely recorder names without breaking if account_state
    has not implemented one yet.
    """

    result = {
        "attempted": False,
        "recorded": False,
        "recorder": "",
        "error": "",
    }

    try:
        import engine.account_state as account_state
    except Exception as exc:
        result["error"] = f"account_state_import_failed: {exc}"
        return result

    recorder_names = [
        "record_trade_activity",
        "record_activity_event",
        "append_activity_event",
        "record_account_activity",
        "remember_trade_activity",
        "record_trade_event",
    ]

    for name in recorder_names:
        fn = getattr(account_state, name, None)
        if not callable(fn):
            continue

        result["attempted"] = True
        result["recorder"] = name

        try:
            fn(event)
            result["recorded"] = True
            return result
        except TypeError:
            try:
                fn(
                    event_type=event.get("event_type"),
                    trade_id=event.get("trade_id"),
                    symbol=event.get("symbol"),
                    vehicle=event.get("vehicle"),
                    timestamp=event.get("timestamp"),
                    account_id=event.get("account_id"),
                    payload=event,
                )
                result["recorded"] = True
                return result
            except Exception as exc:
                result["error"] = f"{name}_failed: {exc}"
        except Exception as exc:
            result["error"] = f"{name}_failed: {exc}"

    return result


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

    account_state_result = _try_account_state_record(event)
    _append_fallback_event(event)

    result = {
        "recorded": True,
        "event": event,
        "account_state_result": account_state_result,
        "fallback_path": str(FALLBACK_EVENT_PATH),
        "fallback_recorded": True,
    }

    print("TRADE ACTIVITY RECORDED:", {
        "event_type": event.get("event_type"),
        "symbol": event.get("symbol"),
        "trade_id": event.get("trade_id"),
        "vehicle": event.get("vehicle"),
        "account_state_recorded": account_state_result.get("recorded"),
        "fallback_recorded": True,
    })

    return result


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

    account_state_result = _try_account_state_record(event)
    _append_fallback_event(event)

    print("TRADE SKIP ACTIVITY RECORDED:", {
        "event_type": event.get("event_type"),
        "symbol": event.get("symbol"),
        "trade_id": event.get("trade_id"),
        "reason": reason,
        "account_state_recorded": account_state_result.get("recorded"),
        "fallback_recorded": True,
    })

    return {
        "recorded": True,
        "event": event,
        "account_state_result": account_state_result,
        "fallback_path": str(FALLBACK_EVENT_PATH),
        "fallback_recorded": True,
    }


__all__ = [
    "record_entry_event",
    "record_skip_event",
]
