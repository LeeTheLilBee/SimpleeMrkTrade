from __future__ import annotations
import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

FILE = "data/research_signals.json"
MAX_ROWS = 500


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value or "").strip()
        return text if text else default
    except Exception:
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)


def _norm_symbol(value: Any) -> str:
    return _safe_str(value, "UNKNOWN").upper()


def _now_iso() -> str:
    return datetime.now().isoformat()


def _ensure_parent() -> None:
    Path(FILE).parent.mkdir(parents=True, exist_ok=True)


def _load() -> List[Dict[str, Any]]:
    path = Path(FILE)
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _save(data: List[Dict[str, Any]]) -> None:
    _ensure_parent()
    trimmed = data[-MAX_ROWS:] if isinstance(data, list) else []
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(trimmed, f, indent=2)


def save_research_signal(trade, regime=None, mode=None, volatility=None, source="research"):
    trade = _safe_dict(trade)
    data = _load()

    entry = {
        "timestamp": _safe_str(trade.get("timestamp"), _now_iso()),
        "symbol": _norm_symbol(trade.get("symbol")),
        "trade_id": _safe_str(trade.get("trade_id"), ""),
        "source": _safe_str(source, "research"),
        "regime": _safe_str(regime, trade.get("regime", "")),
        "mode": _safe_str(mode, trade.get("mode", "")),
        "volatility": _safe_str(volatility, trade.get("volatility_state", "")),
        "strategy": _safe_str(trade.get("strategy"), "CALL").upper(),
        "score": round(_safe_float(trade.get("score"), 0.0), 4),
        "fused_score": round(_safe_float(trade.get("fused_score", trade.get("score", 0.0)), 0.0), 4),
        "confidence": _safe_str(trade.get("confidence"), "LOW").upper(),
        "price": round(_safe_float(trade.get("price", trade.get("current_price", trade.get("entry", 0.0))), 0.0), 4),
        "vehicle_selected": _safe_str(trade.get("vehicle_selected", trade.get("vehicle", "RESEARCH_ONLY")), "RESEARCH_ONLY").upper(),
        "capital_required": round(_safe_float(trade.get("capital_required"), 0.0), 4),
        "minimum_trade_cost": round(_safe_float(trade.get("minimum_trade_cost"), 0.0), 4),
        "research_approved": bool(trade.get("research_approved", False)),
        "execution_ready": bool(trade.get("execution_ready", False)),
        "selected_for_execution": bool(trade.get("selected_for_execution", False)),
        "decision_reason": _safe_str(trade.get("decision_reason"), ""),
        "final_reason": _safe_str(trade.get("final_reason"), ""),
        "blocked_at": _safe_str(trade.get("blocked_at"), ""),
        "readiness_score": round(_safe_float(trade.get("readiness_score"), 0.0), 4),
        "promotion_score": round(_safe_float(trade.get("promotion_score"), 0.0), 4),
        "rebuild_pressure": round(_safe_float(trade.get("rebuild_pressure"), 0.0), 4),
        "v2_score": round(_safe_float(trade.get("v2_score"), 0.0), 4),
        "v2_reason": _safe_str(trade.get("v2_reason"), ""),
        "v2_vehicle_bias": _safe_str(trade.get("v2_vehicle_bias"), "").upper(),
        "v2_confidence": _safe_str(trade.get("v2_confidence"), "").upper(),
        "why": _safe_list(trade.get("why")),
        "option_explanation": _safe_list(trade.get("option_explanation")),
        "raw": deepcopy(trade),
    }

    data.append(entry)
    _save(data)
    return entry


def load_research_signals():
    return _load()
