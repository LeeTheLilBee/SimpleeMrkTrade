from __future__ import annotations

"""
Observatory Trade Cooldown / Anti-Repeat Guard

Purpose:
    Prevent the Observatory from repeatedly selecting or executing the same
    symbol/contract/setup too soon after an open position, close, rejection, or
    repeated stale appearance.

Canonical behavior:
    - Research can continue.
    - Execution can be blocked.
    - Selected-for-execution should be turned off when a cooldown/duplicate/fatigue
      rule blocks the trade.
    - The block reason must be visible and human-readable.

This module is intentionally standalone so process_signals, execution_selector,
canonical_execution_guard, or a notebook runner can consume it without creating
circular imports.
"""

import json
import math
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


PROJECT_ROOT = Path("/content/SimpleeMrkTrade")
DATA_DIR = PROJECT_ROOT / "data"

OPEN_POSITION_FILES = [
    DATA_DIR / "open_positions.json",
    DATA_DIR / "positions.json",
    DATA_DIR / "user_positions.json",
]

CLOSED_POSITION_FILES = [
    DATA_DIR / "closed_positions.json",
]

CANDIDATE_HISTORY_FILES = [
    DATA_DIR / "candidate_log.json",
    DATA_DIR / "top_candidates.json",
]

ACTIVITY_FILES = [
    DATA_DIR / "trade_activity_events.json",
]


DEFAULT_SYMBOL_COOLDOWN_HOURS = 48
DEFAULT_CONTRACT_COOLDOWN_HOURS = 96
DEFAULT_REJECTION_COOLDOWN_HOURS = 24
DEFAULT_STALE_SETUP_LOOKBACK_HOURS = 36
DEFAULT_STALE_SETUP_MAX_APPEARANCES = 4

VEHICLE_OPTION = "OPTION"
VEHICLE_STOCK = "STOCK"
VEHICLE_RESEARCH_ONLY = "RESEARCH_ONLY"


# =============================================================================
# SAFE HELPERS
# =============================================================================

def _now() -> datetime:
    return datetime.now()


def _now_iso() -> str:
    return _now().isoformat()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        for key in ["items", "rows", "positions", "candidates", "trades", "data"]:
            if isinstance(value.get(key), list):
                return value.get(key)
    return []


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value if value is not None else "").strip()
        return text if text else default
    except Exception:
        return default


def _upper(value: Any, default: str = "") -> str:
    return _safe_str(value, default).upper()


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or isinstance(value, bool):
            return float(default)
        if isinstance(value, str):
            cleaned = value.replace("$", "").replace(",", "").strip()
            if not cleaned:
                return float(default)
            value = cleaned
        number = float(value)
        if math.isnan(number) or math.isinf(number):
            return float(default)
        return number
    except Exception:
        return float(default)


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or isinstance(value, bool):
            return int(default)
        if isinstance(value, str):
            cleaned = value.replace(",", "").strip()
            if not cleaned:
                return int(default)
            value = cleaned
        return int(float(value))
    except Exception:
        return int(default)


def _safe_bool(value: Any, default: bool = False) -> bool:
    try:
        if value is None:
            return bool(default)
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"true", "yes", "y", "1"}:
                return True
            if lowered in {"false", "no", "n", "0"}:
                return False
        return bool(value)
    except Exception:
        return bool(default)


def _load_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _parse_dt(value: Any) -> Optional[datetime]:
    text = _safe_str(value, "")
    if not text:
        return None

    try:
        if text.endswith("Z"):
            text = text.replace("Z", "+00:00")
        return datetime.fromisoformat(text.replace("+00:00", ""))
    except Exception:
        return None


def _hours_since(value: Any) -> Optional[float]:
    dt = _parse_dt(value)
    if not dt:
        return None

    try:
        return max((_now() - dt).total_seconds() / 3600.0, 0.0)
    except Exception:
        return None


def _first_present(payload: Dict[str, Any], keys: List[str], default: Any = "") -> Any:
    payload = _safe_dict(payload)
    for key in keys:
        value = payload.get(key)
        if value is not None and str(value).strip() != "":
            return value
    return default


def _symbol(payload: Dict[str, Any]) -> str:
    return _upper(_first_present(payload, ["symbol", "ticker", "underlying_symbol"], ""), "")


def _strategy(payload: Dict[str, Any]) -> str:
    return _upper(
        _first_present(
            payload,
            ["strategy", "final_strategy", "starting_strategy", "side", "direction"],
            "CALL",
        ),
        "CALL",
    )


def _vehicle(payload: Dict[str, Any]) -> str:
    payload = _safe_dict(payload)

    raw = _upper(
        _first_present(
            payload,
            ["vehicle_selected", "selected_vehicle", "vehicle", "asset_type", "instrument_type"],
            "",
        ),
        "",
    )

    if raw in {"OPTION", "OPTIONS", "OPT"}:
        return VEHICLE_OPTION

    if raw in {"STOCK", "EQUITY", "SHARE", "SHARES"}:
        return VEHICLE_STOCK

    if raw in {"RESEARCH_ONLY", "RESEARCH"}:
        return VEHICLE_RESEARCH_ONLY

    option = _safe_dict(payload.get("option"))
    contract = _safe_dict(payload.get("contract"))

    contract_symbol = _contract_symbol(payload)
    right = _upper(
        _first_present(payload, ["right", "option_type", "call_put", "contract_right"], "")
        or _first_present(option, ["right", "option_type", "call_put", "contract_right"], "")
        or _first_present(contract, ["right", "option_type", "call_put", "contract_right"], ""),
        "",
    )

    contracts = _safe_int(payload.get("contracts", payload.get("contract_count", 0)), 0)

    if option or contract or contract_symbol or right in {"CALL", "PUT", "C", "P"} or contracts > 0:
        return VEHICLE_OPTION

    return VEHICLE_STOCK


def _contract_symbol(payload: Dict[str, Any]) -> str:
    payload = _safe_dict(payload)
    option = _safe_dict(payload.get("option"))
    contract = _safe_dict(payload.get("contract"))
    selected_contract = _safe_dict(payload.get("selected_contract"))
    best_option = _safe_dict(payload.get("best_option"))
    best_option_preview = _safe_dict(payload.get("best_option_preview"))

    keys = [
        "contract_symbol",
        "contractSymbol",
        "option_symbol",
        "option_contract_symbol",
        "selected_contract_symbol",
        "occ_symbol",
        "contract",
    ]

    direct = _first_present(payload, keys, "")
    if direct and not isinstance(direct, dict):
        return _safe_str(direct, "").upper()

    for obj in [option, contract, selected_contract, best_option, best_option_preview]:
        value = _first_present(obj, keys, "")
        if value and not isinstance(value, dict):
            return _safe_str(value, "").upper()

    return ""


def _expiry(payload: Dict[str, Any]) -> str:
    payload = _safe_dict(payload)
    option = _safe_dict(payload.get("option"))
    contract = _safe_dict(payload.get("contract"))

    keys = ["expiry", "expiration", "expiration_date", "contract_expiry"]
    return _safe_str(
        _first_present(payload, keys, "")
        or _first_present(option, keys, "")
        or _first_present(contract, keys, ""),
        "",
    )


def _strike(payload: Dict[str, Any]) -> float:
    payload = _safe_dict(payload)
    option = _safe_dict(payload.get("option"))
    contract = _safe_dict(payload.get("contract"))

    return _safe_float(
        _first_present(payload, ["strike", "strike_price", "contract_strike"], "")
        or _first_present(option, ["strike", "strike_price", "contract_strike"], "")
        or _first_present(contract, ["strike", "strike_price", "contract_strike"], ""),
        0.0,
    )


def _right(payload: Dict[str, Any]) -> str:
    payload = _safe_dict(payload)
    option = _safe_dict(payload.get("option"))
    contract = _safe_dict(payload.get("contract"))

    raw = _upper(
        _first_present(payload, ["right", "option_type", "call_put", "contract_right"], "")
        or _first_present(option, ["right", "option_type", "call_put", "contract_right"], "")
        or _first_present(contract, ["right", "option_type", "call_put", "contract_right"], ""),
        "",
    )

    if raw == "C":
        return "CALL"
    if raw == "P":
        return "PUT"
    return raw


def _timestamp(payload: Dict[str, Any]) -> str:
    return _safe_str(
        _first_present(
            payload,
            [
                "timestamp",
                "opened_at",
                "closed_at",
                "entered_at",
                "created_at",
                "updated_at",
                "last_seen_at",
            ],
            "",
        ),
        "",
    )


def _status(payload: Dict[str, Any]) -> str:
    return _upper(
        _first_present(payload, ["status", "position_status", "lifecycle_stage", "execution_status"], ""),
        "",
    )


def _is_open_position(payload: Dict[str, Any]) -> bool:
    status = _status(payload)
    if status in {"CLOSED", "EXITED", "CLOSE", "SOLD", "DONE"}:
        return False

    closed_at = _safe_str(payload.get("closed_at"), "")
    if closed_at:
        return False

    close_reason = _safe_str(payload.get("close_reason"), "")
    if close_reason:
        return False

    return True


def _fresh_catalyst_present(candidate: Dict[str, Any]) -> bool:
    candidate = _safe_dict(candidate)

    bool_keys = [
        "fresh_catalyst",
        "has_fresh_catalyst",
        "fresh_news",
        "news_catalyst_fresh",
        "catalyst_fresh",
        "conditions_changed",
        "setup_changed",
        "reentry_allowed",
    ]

    for key in bool_keys:
        if _safe_bool(candidate.get(key), False):
            return True

    text_keys = [
        "fresh_catalyst_reason",
        "catalyst_reason",
        "news_catalyst",
        "latest_news_reason",
        "reentry_reason",
        "setup_change_reason",
    ]

    for key in text_keys:
        text = _safe_str(candidate.get(key), "")
        if text and text.lower() not in {"no_recent_closed_trade", "recent_close_not_guarded", "none", "n/a"}:
            return True

    return False


def _setup_fingerprint(payload: Dict[str, Any]) -> str:
    symbol = _symbol(payload)
    vehicle = _vehicle(payload)
    strategy = _strategy(payload)
    contract_symbol = _contract_symbol(payload)
    expiry = _expiry(payload)
    strike = _strike(payload)
    right = _right(payload)

    if vehicle == VEHICLE_OPTION:
        parts = [
            symbol,
            vehicle,
            strategy,
            contract_symbol,
            expiry,
            right,
            str(round(strike, 4)) if strike else "",
        ]
    else:
        setup = _safe_str(
            _first_present(payload, ["setup_type", "setup_family", "trade_intent", "pattern"], ""),
            "",
        )
        parts = [symbol, vehicle, strategy, setup]

    return "|".join([p for p in parts if _safe_str(p, "")])


# =============================================================================
# DATA LOADERS
# =============================================================================

def load_open_positions() -> List[Dict[str, Any]]:
    positions: List[Dict[str, Any]] = []

    for path in OPEN_POSITION_FILES:
        payload = _load_json(path, [])
        for item in _safe_list(payload):
            if isinstance(item, dict):
                positions.append(item)

    # Dedupe by trade_id first, then symbol/contract
    seen = set()
    out: List[Dict[str, Any]] = []

    for pos in positions:
        key = (
            _safe_str(pos.get("trade_id"), "")
            or _setup_fingerprint(pos)
            or f"{_symbol(pos)}-{len(out)}"
        )
        if key in seen:
            continue
        seen.add(key)
        if _is_open_position(pos):
            out.append(pos)

    return out


def load_closed_positions() -> List[Dict[str, Any]]:
    closed: List[Dict[str, Any]] = []

    for path in CLOSED_POSITION_FILES:
        payload = _load_json(path, [])
        for item in _safe_list(payload):
            if isinstance(item, dict):
                closed.append(item)

    return closed


def load_candidate_history() -> List[Dict[str, Any]]:
    history: List[Dict[str, Any]] = []

    for path in CANDIDATE_HISTORY_FILES:
        payload = _load_json(path, [])
        for item in _safe_list(payload):
            if isinstance(item, dict):
                history.append(item)

    return history


def load_activity_events() -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []

    for path in ACTIVITY_FILES:
        payload = _load_json(path, [])
        for item in _safe_list(payload):
            if isinstance(item, dict):
                events.append(item)

    return events


# =============================================================================
# GUARD CHECKS
# =============================================================================

def _open_duplicate_check(candidate: Dict[str, Any], open_positions: List[Dict[str, Any]]) -> Dict[str, Any]:
    symbol = _symbol(candidate)
    vehicle = _vehicle(candidate)
    contract_symbol = _contract_symbol(candidate)
    fingerprint = _setup_fingerprint(candidate)

    for pos in open_positions:
        pos_symbol = _symbol(pos)
        pos_vehicle = _vehicle(pos)
        pos_contract_symbol = _contract_symbol(pos)
        pos_fingerprint = _setup_fingerprint(pos)

        if symbol and pos_symbol == symbol:
            if vehicle == VEHICLE_OPTION and contract_symbol and pos_contract_symbol == contract_symbol:
                return {
                    "blocked": True,
                    "reason": "duplicate_open_contract",
                    "detail": f"{symbol} already has open contract {contract_symbol}.",
                    "matched_trade_id": _safe_str(pos.get("trade_id"), ""),
                    "matched_symbol": pos_symbol,
                    "matched_contract": pos_contract_symbol,
                }

            if fingerprint and pos_fingerprint == fingerprint:
                return {
                    "blocked": True,
                    "reason": "duplicate_open_setup",
                    "detail": f"{symbol} already has the same open setup.",
                    "matched_trade_id": _safe_str(pos.get("trade_id"), ""),
                    "matched_symbol": pos_symbol,
                    "matched_contract": pos_contract_symbol,
                }

            return {
                "blocked": True,
                "reason": "duplicate_open_symbol",
                "detail": f"{symbol} already has an open position.",
                "matched_trade_id": _safe_str(pos.get("trade_id"), ""),
                "matched_symbol": pos_symbol,
                "matched_contract": pos_contract_symbol,
            }

    return {"blocked": False, "reason": "", "detail": ""}


def _recent_close_check(
    candidate: Dict[str, Any],
    closed_positions: List[Dict[str, Any]],
    *,
    symbol_cooldown_hours: int = DEFAULT_SYMBOL_COOLDOWN_HOURS,
    contract_cooldown_hours: int = DEFAULT_CONTRACT_COOLDOWN_HOURS,
) -> Dict[str, Any]:
    symbol = _symbol(candidate)
    vehicle = _vehicle(candidate)
    contract_symbol = _contract_symbol(candidate)
    fingerprint = _setup_fingerprint(candidate)

    if _fresh_catalyst_present(candidate):
        return {
            "blocked": False,
            "reason": "",
            "detail": "fresh_catalyst_present",
            "fresh_catalyst_override": True,
        }

    best_match: Optional[Dict[str, Any]] = None
    best_match_hours: Optional[float] = None
    best_reason = ""

    for closed in closed_positions:
        closed_symbol = _symbol(closed)
        if not symbol or closed_symbol != symbol:
            continue

        closed_contract = _contract_symbol(closed)
        closed_fingerprint = _setup_fingerprint(closed)

        timestamp = (
            _safe_str(closed.get("closed_at"), "")
            or _safe_str(closed.get("timestamp"), "")
            or _safe_str(closed.get("updated_at"), "")
        )
        hours = _hours_since(timestamp)

        if hours is None:
            continue

        if vehicle == VEHICLE_OPTION and contract_symbol and closed_contract == contract_symbol:
            if hours <= contract_cooldown_hours:
                best_match = closed
                best_match_hours = hours
                best_reason = "recently_closed_same_contract"
                break

        if fingerprint and closed_fingerprint == fingerprint:
            if hours <= contract_cooldown_hours:
                best_match = closed
                best_match_hours = hours
                best_reason = "recently_closed_same_setup"
                break

        if hours <= symbol_cooldown_hours:
            if best_match is None or best_match_hours is None or hours < best_match_hours:
                best_match = closed
                best_match_hours = hours
                best_reason = "recently_closed_symbol_cooldown"

    if best_match is None:
        return {"blocked": False, "reason": "", "detail": ""}

    return {
        "blocked": True,
        "reason": best_reason,
        "detail": (
            f"{symbol} was closed {round(best_match_hours or 0.0, 2)} hours ago. "
            "Fresh catalyst required before re-entry."
        ),
        "matched_trade_id": _safe_str(best_match.get("trade_id"), ""),
        "matched_symbol": _symbol(best_match),
        "matched_contract": _contract_symbol(best_match),
        "matched_close_reason": _safe_str(best_match.get("close_reason"), ""),
        "hours_since_close": round(best_match_hours or 0.0, 4),
        "fresh_catalyst_override": False,
    }


def _recent_rejection_check(
    candidate: Dict[str, Any],
    activity_events: List[Dict[str, Any]],
    *,
    rejection_cooldown_hours: int = DEFAULT_REJECTION_COOLDOWN_HOURS,
) -> Dict[str, Any]:
    symbol = _symbol(candidate)
    fingerprint = _setup_fingerprint(candidate)

    if _fresh_catalyst_present(candidate):
        return {"blocked": False, "reason": "", "detail": "fresh_catalyst_present"}

    for event in reversed(activity_events):
        event_type = _upper(event.get("event_type", event.get("action", "")), "")
        if event_type not in {"REJECTED", "REJECTION", "SKIP", "SKIPPED", "BLOCKED"}:
            continue

        if _symbol(event) != symbol:
            continue

        event_fingerprint = _setup_fingerprint(event)
        if fingerprint and event_fingerprint and event_fingerprint != fingerprint:
            continue

        hours = _hours_since(_timestamp(event))
        if hours is not None and hours <= rejection_cooldown_hours:
            return {
                "blocked": True,
                "reason": "recently_rejected_cooldown",
                "detail": f"{symbol} was rejected/skipped {round(hours, 2)} hours ago.",
                "matched_trade_id": _safe_str(event.get("trade_id"), ""),
                "hours_since_rejection": round(hours, 4),
            }

    return {"blocked": False, "reason": "", "detail": ""}


def _stale_setup_fatigue_check(
    candidate: Dict[str, Any],
    candidate_history: List[Dict[str, Any]],
    *,
    lookback_hours: int = DEFAULT_STALE_SETUP_LOOKBACK_HOURS,
    max_appearances: int = DEFAULT_STALE_SETUP_MAX_APPEARANCES,
) -> Dict[str, Any]:
    symbol = _symbol(candidate)
    fingerprint = _setup_fingerprint(candidate)

    if not symbol:
        return {"blocked": False, "reason": "", "detail": ""}

    if _fresh_catalyst_present(candidate):
        return {"blocked": False, "reason": "", "detail": "fresh_catalyst_present"}

    appearances = 0
    matched_trade_ids: List[str] = []

    for row in candidate_history:
        if _symbol(row) != symbol:
            continue

        row_fingerprint = _setup_fingerprint(row)
        if fingerprint and row_fingerprint and row_fingerprint != fingerprint:
            continue

        ts = _timestamp(row)
        hours = _hours_since(ts)

        # Some candidate logs do not have timestamps. Count only timestamped rows
        # to avoid old static files blocking everything forever.
        if hours is None or hours > lookback_hours:
            continue

        appearances += 1

        trade_id = _safe_str(row.get("trade_id"), "")
        if trade_id:
            matched_trade_ids.append(trade_id)

    if appearances >= max_appearances:
        return {
            "blocked": True,
            "reason": "setup_fatigue_detected",
            "detail": (
                f"{symbol} appeared {appearances} times inside {lookback_hours} hours "
                "without a fresh catalyst."
            ),
            "appearances": appearances,
            "lookback_hours": lookback_hours,
            "matched_trade_ids": matched_trade_ids[-10:],
        }

    return {
        "blocked": False,
        "reason": "",
        "detail": "",
        "appearances": appearances,
        "lookback_hours": lookback_hours,
    }


# =============================================================================
# PUBLIC API
# =============================================================================

def evaluate_trade_cooldown(
    candidate: Dict[str, Any],
    *,
    open_positions: Optional[List[Dict[str, Any]]] = None,
    closed_positions: Optional[List[Dict[str, Any]]] = None,
    candidate_history: Optional[List[Dict[str, Any]]] = None,
    activity_events: Optional[List[Dict[str, Any]]] = None,
    symbol_cooldown_hours: int = DEFAULT_SYMBOL_COOLDOWN_HOURS,
    contract_cooldown_hours: int = DEFAULT_CONTRACT_COOLDOWN_HOURS,
    rejection_cooldown_hours: int = DEFAULT_REJECTION_COOLDOWN_HOURS,
    stale_setup_lookback_hours: int = DEFAULT_STALE_SETUP_LOOKBACK_HOURS,
    stale_setup_max_appearances: int = DEFAULT_STALE_SETUP_MAX_APPEARANCES,
) -> Dict[str, Any]:
    candidate = _safe_dict(candidate)

    open_positions = open_positions if isinstance(open_positions, list) else load_open_positions()
    closed_positions = closed_positions if isinstance(closed_positions, list) else load_closed_positions()
    candidate_history = candidate_history if isinstance(candidate_history, list) else load_candidate_history()
    activity_events = activity_events if isinstance(activity_events, list) else load_activity_events()

    symbol = _symbol(candidate)
    vehicle = _vehicle(candidate)
    contract_symbol = _contract_symbol(candidate)
    fingerprint = _setup_fingerprint(candidate)

    checks: List[Dict[str, Any]] = []

    checks.append(_open_duplicate_check(candidate, open_positions))
    checks.append(
        _recent_close_check(
            candidate,
            closed_positions,
            symbol_cooldown_hours=symbol_cooldown_hours,
            contract_cooldown_hours=contract_cooldown_hours,
        )
    )
    checks.append(
        _recent_rejection_check(
            candidate,
            activity_events,
            rejection_cooldown_hours=rejection_cooldown_hours,
        )
    )
    checks.append(
        _stale_setup_fatigue_check(
            candidate,
            candidate_history,
            lookback_hours=stale_setup_lookback_hours,
            max_appearances=stale_setup_max_appearances,
        )
    )

    blocking_checks = [x for x in checks if isinstance(x, dict) and x.get("blocked")]

    if blocking_checks:
        primary = blocking_checks[0]
        return {
            "allowed": False,
            "blocked": True,
            "reason": _safe_str(primary.get("reason"), "anti_repeat_blocked"),
            "detail": _safe_str(primary.get("detail"), ""),
            "symbol": symbol,
            "vehicle": vehicle,
            "contract_symbol": contract_symbol,
            "setup_fingerprint": fingerprint,
            "fresh_catalyst_present": _fresh_catalyst_present(candidate),
            "checks": checks,
            "timestamp": _now_iso(),
        }

    return {
        "allowed": True,
        "blocked": False,
        "reason": "ok",
        "detail": "No duplicate, cooldown, rejection, or fatigue block found.",
        "symbol": symbol,
        "vehicle": vehicle,
        "contract_symbol": contract_symbol,
        "setup_fingerprint": fingerprint,
        "fresh_catalyst_present": _fresh_catalyst_present(candidate),
        "checks": checks,
        "timestamp": _now_iso(),
    }


def apply_trade_cooldown_guard(
    candidate: Dict[str, Any],
    *,
    open_positions: Optional[List[Dict[str, Any]]] = None,
    closed_positions: Optional[List[Dict[str, Any]]] = None,
    candidate_history: Optional[List[Dict[str, Any]]] = None,
    activity_events: Optional[List[Dict[str, Any]]] = None,
    preserve_research_approval: bool = True,
    **kwargs: Any,
) -> Dict[str, Any]:
    candidate = dict(candidate) if isinstance(candidate, dict) else {}

    decision = evaluate_trade_cooldown(
        candidate,
        open_positions=open_positions,
        closed_positions=closed_positions,
        candidate_history=candidate_history,
        activity_events=activity_events,
        **kwargs,
    )

    candidate["anti_repeat_guard"] = decision
    candidate["anti_repeat_checked"] = True
    candidate["anti_repeat_checked_at"] = _now_iso()

    if decision.get("blocked"):
        candidate["anti_repeat_blocked"] = True
        candidate["cooldown_blocked"] = True
        candidate["cooldown_reason"] = decision.get("reason", "anti_repeat_blocked")
        candidate["cooldown_detail"] = decision.get("detail", "")

        if preserve_research_approval:
            candidate["research_approved"] = bool(candidate.get("research_approved", True))

        candidate["execution_ready"] = False
        candidate["selected_for_execution"] = False
        candidate["blocked_at"] = "anti_repeat_guard"
        candidate["final_reason"] = decision.get("reason", "anti_repeat_blocked")
        candidate["final_reason_detail"] = decision.get("detail", "")

        candidate.setdefault("execution_guard_reason", decision.get("reason", "anti_repeat_blocked"))
        candidate.setdefault("execution_guard_blocked", True)

    else:
        candidate["anti_repeat_blocked"] = False
        candidate["cooldown_blocked"] = False
        candidate["cooldown_reason"] = ""
        candidate["cooldown_detail"] = ""

    return candidate


def guard_candidate_list(
    candidates: List[Dict[str, Any]],
    *,
    preserve_research_approval: bool = True,
    **kwargs: Any,
) -> Dict[str, Any]:
    candidates = [dict(x) for x in candidates if isinstance(x, dict)]

    open_positions = load_open_positions()
    closed_positions = load_closed_positions()
    candidate_history = load_candidate_history()
    activity_events = load_activity_events()

    guarded: List[Dict[str, Any]] = []
    blocked: List[Dict[str, Any]] = []
    allowed: List[Dict[str, Any]] = []

    for candidate in candidates:
        updated = apply_trade_cooldown_guard(
            candidate,
            open_positions=open_positions,
            closed_positions=closed_positions,
            candidate_history=candidate_history,
            activity_events=activity_events,
            preserve_research_approval=preserve_research_approval,
            **kwargs,
        )
        guarded.append(updated)

        if updated.get("anti_repeat_blocked"):
            blocked.append(updated)
        else:
            allowed.append(updated)

    return {
        "guarded": guarded,
        "allowed": allowed,
        "blocked": blocked,
        "allowed_count": len(allowed),
        "blocked_count": len(blocked),
        "input_count": len(candidates),
        "open_position_count": len(open_positions),
        "closed_position_count": len(closed_positions),
        "candidate_history_count": len(candidate_history),
        "activity_event_count": len(activity_events),
        "timestamp": _now_iso(),
    }


def guard_execution_queue(
    queue: List[Dict[str, Any]],
    *,
    preserve_research_approval: bool = True,
    **kwargs: Any,
) -> Dict[str, Any]:
    result = guard_candidate_list(
        queue,
        preserve_research_approval=preserve_research_approval,
        **kwargs,
    )

    # Execution queue should only keep allowed candidates.
    result["queue"] = result["allowed"]
    result["selected_trades"] = result["allowed"]

    return result


def print_cooldown_guard_summary(result: Dict[str, Any]) -> None:
    result = _safe_dict(result)

    print("\n" + "=" * 80)
    print("OBSERVATORY ANTI-REPEAT / COOLDOWN GUARD SUMMARY")
    print("=" * 80)
    print("Input candidates:", result.get("input_count", 0))
    print("Allowed:", result.get("allowed_count", 0))
    print("Blocked:", result.get("blocked_count", 0))
    print("Open positions seen:", result.get("open_position_count", 0))
    print("Closed positions seen:", result.get("closed_position_count", 0))
    print("-" * 80)

    blocked = result.get("blocked", [])
    if not blocked:
        print("No anti-repeat blocks.")
    else:
        for candidate in blocked:
            guard = _safe_dict(candidate.get("anti_repeat_guard"))
            print(
                f"{candidate.get('symbol')} | {candidate.get('vehicle_selected', candidate.get('vehicle'))} | "
                f"BLOCKED: {guard.get('reason')} | {guard.get('detail')}"
            )

    allowed = result.get("allowed", [])
    if allowed:
        print("-" * 80)
        for candidate in allowed:
            guard = _safe_dict(candidate.get("anti_repeat_guard"))
            print(
                f"{candidate.get('symbol')} | {candidate.get('vehicle_selected', candidate.get('vehicle'))} | "
                f"ALLOWED: {guard.get('reason')}"
            )

    print("=" * 80)


__all__ = [
    "evaluate_trade_cooldown",
    "apply_trade_cooldown_guard",
    "guard_candidate_list",
    "guard_execution_queue",
    "print_cooldown_guard_summary",
    "load_open_positions",
    "load_closed_positions",
    "load_candidate_history",
    "load_activity_events",
]
