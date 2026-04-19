from datetime import datetime
from typing import Any, Dict, List

from engine.paper_portfolio import show_positions, replace_position
from engine.close_trade import close_position
from engine.data_utils import safe_download
from engine.explainability_engine import explain_position_state
from engine.engine_selection import get_learning_adjustment_map
from engine.engine_readiness import build_readiness_layer
from engine.engine_promotion import build_promotion_layer
from engine.engine_rebuild import build_rebuild_layer
from engine.soulaana_core import soulaana_explain_position
from engine.paper_portfolio import open_count
from engine.trade_history import executed_trade_count
from engine.risk_governor import governor_status


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return int(default)


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value).strip()
        return text if text else default
    except Exception:
        return default


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _days_open(opened_at: Any) -> float:
    try:
        dt = datetime.fromisoformat(str(opened_at))
        return max((datetime.now() - dt).total_seconds() / 86400, 0.0)
    except Exception:
        return 0.0


def _progress(entry: Any, current: Any, target: Any) -> float:
    try:
        entry = float(entry or 0)
        current = float(current or 0)
        target = float(target or 0)
    except Exception:
        return 0.0
    if not entry or not target or target == entry:
        return 0.0
    try:
        return (current - entry) / (target - entry)
    except Exception:
        return 0.0


def _pct_change(entry: Any, current: Any) -> float:
    try:
        entry = float(entry or 0)
        current = float(current or 0)
        if entry <= 0:
            return 0.0
        return ((current - entry) / entry) * 100.0
    except Exception:
        return 0.0


def _latest_price(symbol: str, fallback_price: Any) -> float:
    try:
        df = safe_download(symbol, period="5d", auto_adjust=True, progress=False)
        if df is None or getattr(df, "empty", True):
            return float(fallback_price or 0)
        close = df["Close"]
        if hasattr(close, "iloc"):
            val = close.iloc[-1]
            try:
                return float(val.item())
            except Exception:
                return float(val)
    except Exception:
        pass
    return float(fallback_price or 0)


def _build_learning_exit_map() -> Dict[str, Any]:
    try:
        adjustment_map = get_learning_adjustment_map()
    except Exception:
        adjustment_map = {}
    items = adjustment_map.get("items", []) if isinstance(adjustment_map, dict) else []
    behavior_flags = []
    for item in items:
        if not isinstance(item, dict):
            continue
        if str(item.get("type", "") or "").strip().lower() == "behavior_flag":
            behavior_flags.append(item)
    return {"behavior_flags": behavior_flags}


def _has_delay_exit_bias(learning_exit_map: Dict[str, Any]) -> bool:
    behavior_flags = learning_exit_map.get("behavior_flags", []) if isinstance(learning_exit_map, dict) else []
    for item in behavior_flags:
        if not isinstance(item, dict):
            continue
        action = str(item.get("action", "") or "").strip().lower()
        if action == "delay_exit_bias":
            return True
    return False


def _extract_v2_context(pos: Dict[str, Any]) -> Dict[str, Any]:
    v2 = _safe_dict(pos.get("v2", {}))
    v2_signal = _safe_dict(pos.get("v2_signal", {}))
    v2_overlay = _safe_dict(pos.get("v2_overlay", {}))
    v2_intelligence = _safe_dict(pos.get("v2_intelligence", {}))
    v2_payload = _safe_dict(pos.get("v2_payload", {}))

    merged: Dict[str, Any] = {}
    merged.update(v2_signal)
    merged.update(v2_overlay)
    merged.update(v2_intelligence)
    merged.update(v2_payload)
    merged.update(v2)

    # also fold in top-level persisted V2 fields
    if "v2_score" in pos and "score" not in merged:
        merged["score"] = pos.get("v2_score")
    if "v2_reason" in pos and "reason" not in merged:
        merged["reason"] = pos.get("v2_reason")
    if "v2_vehicle_bias" in pos and "vehicle_bias" not in merged:
        merged["vehicle_bias"] = pos.get("v2_vehicle_bias")
    if "v2_confidence" in pos and "confidence" not in merged:
        merged["confidence"] = pos.get("v2_confidence")
    if "v2_quality" in pos and "quality" not in merged:
        merged["quality"] = pos.get("v2_quality")

    return {
        "v2": merged,
        "v2_score": _safe_float(merged.get("score", pos.get("v2_score", 0.0)), 0.0),
        "v2_confidence": _safe_str(merged.get("confidence", pos.get("v2_confidence", "")), "").upper(),
        "v2_reason": _safe_str(merged.get("reason", pos.get("v2_reason", "")), ""),
        "v2_regime_alignment": _safe_str(
            merged.get("regime_alignment", merged.get("alignment", pos.get("v2_regime_alignment", ""))),
            "",
        ),
        "v2_signal_strength": _safe_float(
            merged.get("signal_strength", merged.get("strength", pos.get("v2_signal_strength", 0.0))),
            0.0,
        ),
        "v2_conviction_adjustment": _safe_float(
            merged.get(
                "conviction_adjustment",
                merged.get("confidence_adjustment", pos.get("v2_conviction_adjustment", 0.0)),
            ),
            0.0,
        ),
        "v2_vehicle_bias": _safe_str(
            merged.get("vehicle_bias", merged.get("preferred_vehicle", pos.get("v2_vehicle_bias", ""))),
            "",
        ).upper(),
        "v2_thesis": _safe_str(
            merged.get("thesis", merged.get("summary", pos.get("v2_thesis", ""))),
            "",
        ),
        "v2_notes": _safe_list(
            merged.get("notes", pos.get("v2_notes", merged.get("signals", [])))
        ),
        "v2_risk_flags": _safe_list(
            merged.get("risk_flags", pos.get("v2_risk_flags", merged.get("warnings", [])))
        ),
        "v2_quality": _safe_float(merged.get("quality", pos.get("v2_quality", 0.0)), 0.0),
    }


def _has_meaningful_existing_intelligence(pos: Dict[str, Any]) -> bool:
    return any(
        [
            _safe_float(pos.get("readiness_score", 0.0), 0.0) > 0,
            _safe_float(pos.get("promotion_score", 0.0), 0.0) > 0,
            _safe_float(pos.get("rebuild_pressure", 0.0), 0.0) > 0,
            bool(_safe_str(pos.get("setup_family", ""), "")),
            bool(_safe_str(pos.get("entry_quality", ""), "")),
        ]
    )


def _build_position_intelligence(pos: Dict[str, Any]) -> Dict[str, Any]:
    v2_context = _extract_v2_context(pos)

    existing = {
        "readiness_score": _safe_float(pos.get("readiness_score", 0.0), 0.0),
        "promotion_score": _safe_float(pos.get("promotion_score", 0.0), 0.0),
        "rebuild_pressure": _safe_float(pos.get("rebuild_pressure", 0.0), 0.0),
        "readiness_notes": _safe_list(pos.get("readiness_notes", [])),
        "promotion_notes": _safe_list(pos.get("promotion_notes", [])),
        "rebuild_notes": _safe_list(pos.get("rebuild_notes", [])),
        "setup_family": _safe_str(pos.get("setup_family", ""), ""),
        "entry_quality": _safe_str(pos.get("entry_quality", ""), ""),
    }

    # Prefer existing canonical/fused values if already present.
    if _has_meaningful_existing_intelligence(pos):
        return {
            **existing,
            "v2": v2_context.get("v2", {}),
            "v2_score": v2_context.get("v2_score", 0.0),
            "v2_confidence": v2_context.get("v2_confidence", ""),
            "v2_reason": v2_context.get("v2_reason", ""),
            "v2_regime_alignment": v2_context.get("v2_regime_alignment", ""),
            "v2_signal_strength": v2_context.get("v2_signal_strength", 0.0),
            "v2_conviction_adjustment": v2_context.get("v2_conviction_adjustment", 0.0),
            "v2_vehicle_bias": v2_context.get("v2_vehicle_bias", ""),
            "v2_thesis": v2_context.get("v2_thesis", ""),
            "v2_notes": v2_context.get("v2_notes", []),
            "v2_risk_flags": v2_context.get("v2_risk_flags", []),
            "v2_quality": v2_context.get("v2_quality", 0.0),
        }

    signal_like = {
        "symbol": pos.get("symbol"),
        "score": pos.get("fused_score", pos.get("score", 0)),
        "confidence": pos.get("confidence", "LOW"),
        "setup_type": pos.get("setup_type", "Continuation"),
        "setup_family": pos.get("setup_family", ""),
        "entry_quality": pos.get("entry_quality", ""),
        "vehicle_selected": pos.get("vehicle_selected", pos.get("vehicle", "STOCK")),
        "decision_reason": pos.get("decision_reason", pos.get("final_reason", "")),
        "v2": v2_context.get("v2", {}),
        "v2_score": v2_context.get("v2_score", 0.0),
        "v2_confidence": v2_context.get("v2_confidence", ""),
        "v2_reason": v2_context.get("v2_reason", ""),
        "v2_regime_alignment": v2_context.get("v2_regime_alignment", ""),
        "v2_signal_strength": v2_context.get("v2_signal_strength", 0.0),
        "v2_conviction_adjustment": v2_context.get("v2_conviction_adjustment", 0.0),
        "v2_vehicle_bias": v2_context.get("v2_vehicle_bias", ""),
        "v2_thesis": v2_context.get("v2_thesis", ""),
        "v2_notes": v2_context.get("v2_notes", []),
        "v2_risk_flags": v2_context.get("v2_risk_flags", []),
        "v2_quality": v2_context.get("v2_quality", 0.0),
    }

    try:
        adjustment_map = get_learning_adjustment_map()
    except Exception:
        adjustment_map = {}

    try:
        readiness_view = build_readiness_layer([signal_like], adjustment_map)
        readiness_row = readiness_view[0] if readiness_view else {}
    except Exception:
        readiness_row = {}

    try:
        promotion_view = build_promotion_layer([readiness_row], adjustment_map)
        promotion_row = promotion_view[0] if promotion_view else readiness_row
    except Exception:
        promotion_row = readiness_row

    try:
        rebuild_view = build_rebuild_layer([promotion_row], adjustment_map)
        rebuild_row = rebuild_view[0] if rebuild_view else promotion_row
    except Exception:
        rebuild_row = promotion_row

    return {
        "readiness_score": float(rebuild_row.get("readiness_score", 0) or 0),
        "promotion_score": float(rebuild_row.get("promotion_score", 0) or 0),
        "rebuild_pressure": float(rebuild_row.get("rebuild_pressure", 0) or 0),
        "readiness_notes": rebuild_row.get("readiness_notes", []) or [],
        "promotion_notes": rebuild_row.get("promotion_notes", []) or [],
        "rebuild_notes": rebuild_row.get("rebuild_notes", []) or [],
        "setup_family": rebuild_row.get("setup_family", pos.get("setup_family", "")),
        "entry_quality": rebuild_row.get("entry_quality", pos.get("entry_quality", "")),
        "v2": v2_context.get("v2", {}),
        "v2_score": v2_context.get("v2_score", 0.0),
        "v2_confidence": v2_context.get("v2_confidence", ""),
        "v2_reason": v2_context.get("v2_reason", ""),
        "v2_regime_alignment": v2_context.get("v2_regime_alignment", ""),
        "v2_signal_strength": v2_context.get("v2_signal_strength", 0.0),
        "v2_conviction_adjustment": v2_context.get("v2_conviction_adjustment", 0.0),
        "v2_vehicle_bias": v2_context.get("v2_vehicle_bias", ""),
        "v2_thesis": v2_context.get("v2_thesis", ""),
        "v2_notes": v2_context.get("v2_notes", []),
        "v2_risk_flags": v2_context.get("v2_risk_flags", []),
        "v2_quality": v2_context.get("v2_quality", 0.0),
    }


def _get_governor_snapshot() -> Dict[str, Any]:
    try:
        return governor_status(
            current_open_positions=_safe_int(open_count(), 0),
            executed_trades_today=_safe_int(executed_trade_count(), 0),
        )
    except Exception:
        return {}


def _capital_protection_mode(governor: Dict[str, Any]) -> Dict[str, Any]:
    controls = governor.get("controls", {}) if isinstance(governor, dict) else {}
    reasons = governor.get("reasons", []) if isinstance(governor, dict) else []
    reserve_broken = bool(controls.get("cash_reserve_too_low", False)) or ("cash_reserve_too_low" in reasons)
    max_positions_hit = bool(controls.get("max_open_positions", False)) or ("max_open_positions" in reasons)
    enabled = reserve_broken or max_positions_hit
    return {
        "enabled": enabled,
        "reserve_broken": reserve_broken,
        "max_positions_hit": max_positions_hit,
        "cash": _safe_float(governor.get("cash", 0.0), 0.0),
        "buying_power": _safe_float(governor.get("buying_power", 0.0), 0.0),
    }


def _capital_pressure_score(pos: Dict[str, Any]) -> float:
    pct_change = _safe_float(pos.get("_monitor_pct_change", 0.0), 0.0)
    progress = _safe_float(pos.get("_monitor_progress", 0.0), 0.0)
    days_open = _safe_float(pos.get("_monitor_days_open", 0.0), 0.0)
    readiness_score = _safe_float(pos.get("readiness_score", 0.0), 0.0)
    rebuild_pressure = _safe_float(pos.get("rebuild_pressure", 0.0), 0.0)
    promotion_score = _safe_float(pos.get("promotion_score", 0.0), 0.0)
    confidence_text = str(pos.get("confidence", "LOW") or "LOW").upper().strip()
    v2_signal_strength = _safe_float(pos.get("v2_signal_strength", 0.0), 0.0)
    v2_conviction_adjustment = _safe_float(pos.get("v2_conviction_adjustment", 0.0), 0.0)
    v2_regime_alignment = _safe_str(pos.get("v2_regime_alignment", ""), "").lower()
    v2_risk_flags = _safe_list(pos.get("v2_risk_flags", []))

    score = 0.0

    if pct_change < 0:
        score += min(abs(pct_change) * 18.0, 36.0)
    else:
        score -= min(pct_change * 8.0, 10.0)

    if progress < 0:
        score += min(abs(progress) * 30.0, 24.0)
    elif progress < 0.10:
        score += (0.10 - progress) * 40.0
    else:
        score -= min(progress * 8.0, 8.0)

    if days_open >= 0.5 and progress < 0.15:
        score += min(days_open * 4.0, 18.0)

    score += min(rebuild_pressure * 0.55, 32.0)

    if readiness_score < 160:
        score += min((160.0 - readiness_score) * 0.18, 26.0)

    if promotion_score < 160:
        score += min((160.0 - promotion_score) * 0.08, 10.0)

    if confidence_text == "LOW":
        score += 8.0
    elif confidence_text == "MEDIUM":
        score += 3.5
    elif confidence_text == "HIGH":
        score -= 2.0

    if pct_change < 0 and days_open >= 1.0:
        score += min(days_open * 2.5, 10.0)

    if v2_signal_strength < 0:
        score += min(abs(v2_signal_strength) * 10.0, 12.0)
    elif v2_signal_strength > 0:
        score -= min(v2_signal_strength * 4.0, 6.0)

    if v2_conviction_adjustment < 0:
        score += min(abs(v2_conviction_adjustment) * 8.0, 10.0)
    elif v2_conviction_adjustment > 0:
        score -= min(v2_conviction_adjustment * 4.0, 5.0)

    if v2_regime_alignment in {"misaligned", "against_regime", "weak"}:
        score += 8.0
    elif v2_regime_alignment in {"aligned", "strong"}:
        score -= 4.0

    if v2_risk_flags:
        score += min(len(v2_risk_flags) * 2.5, 10.0)

    return round(max(score, 0.0), 2)


def monitor_open_positions() -> List[Dict[str, Any]]:
    try:
        positions = show_positions()
    except Exception:
        positions = []

    if not isinstance(positions, list):
        positions = []

    actions: List[Dict[str, Any]] = []
    learning_exit_map = _build_learning_exit_map()
    delay_exit_bias_active = _has_delay_exit_bias(learning_exit_map)
    governor = _get_governor_snapshot()
    protection = _capital_protection_mode(governor)
    enriched_positions: List[Dict[str, Any]] = []

    for pos in positions:
        if not isinstance(pos, dict):
            continue

        symbol = str(pos.get("symbol", "") or "").upper().strip()
        if not symbol:
            continue

        entry = float(pos.get("entry", pos.get("price", 0)) or 0)
        current = _latest_price(symbol, pos.get("current_price", entry))
        target = float(pos.get("target", entry) or entry)
        stop = float(pos.get("stop", entry) or entry)

        pos["symbol"] = symbol
        pos["current_price"] = round(current, 2)

        position_intel = _build_position_intelligence(pos)

        # preserve existing upstream values unless missing/zeroish
        if _safe_float(pos.get("readiness_score", 0.0), 0.0) <= 0:
            pos["readiness_score"] = position_intel.get("readiness_score", 0)
        if _safe_float(pos.get("promotion_score", 0.0), 0.0) <= 0:
            pos["promotion_score"] = position_intel.get("promotion_score", 0)
        if _safe_float(pos.get("rebuild_pressure", 0.0), 0.0) <= 0:
            pos["rebuild_pressure"] = position_intel.get("rebuild_pressure", 0)

        if not _safe_str(pos.get("setup_family", ""), ""):
            pos["setup_family"] = position_intel.get("setup_family", "")
        if not _safe_str(pos.get("entry_quality", ""), ""):
            pos["entry_quality"] = position_intel.get("entry_quality", "")

        if not _safe_list(pos.get("readiness_notes", [])):
            pos["readiness_notes"] = position_intel.get("readiness_notes", [])
        if not _safe_list(pos.get("promotion_notes", [])):
            pos["promotion_notes"] = position_intel.get("promotion_notes", [])
        if not _safe_list(pos.get("rebuild_notes", [])):
            pos["rebuild_notes"] = position_intel.get("rebuild_notes", [])

        pos["v2"] = position_intel.get("v2", pos.get("v2", {}))
        pos["v2_score"] = position_intel.get("v2_score", pos.get("v2_score", 0.0))
        pos["v2_confidence"] = position_intel.get("v2_confidence", pos.get("v2_confidence", ""))
        pos["v2_reason"] = position_intel.get("v2_reason", pos.get("v2_reason", ""))
        pos["v2_regime_alignment"] = position_intel.get("v2_regime_alignment", pos.get("v2_regime_alignment", ""))
        pos["v2_signal_strength"] = position_intel.get("v2_signal_strength", pos.get("v2_signal_strength", 0.0))
        pos["v2_conviction_adjustment"] = position_intel.get(
            "v2_conviction_adjustment",
            pos.get("v2_conviction_adjustment", 0.0),
        )
        pos["v2_vehicle_bias"] = position_intel.get("v2_vehicle_bias", pos.get("v2_vehicle_bias", ""))
        pos["v2_thesis"] = position_intel.get("v2_thesis", pos.get("v2_thesis", ""))
        pos["v2_notes"] = position_intel.get("v2_notes", pos.get("v2_notes", []))
        pos["v2_risk_flags"] = position_intel.get("v2_risk_flags", pos.get("v2_risk_flags", []))
        pos["v2_quality"] = position_intel.get("v2_quality", pos.get("v2_quality", 0.0))

        rebuild_pressure = float(pos.get("rebuild_pressure", 0) or 0)
        readiness_score = float(pos.get("readiness_score", 0) or 0)
        days = _days_open(pos.get("opened_at"))
        prog = _progress(entry, current, target)
        pct_change = _pct_change(entry, current)

        try:
            pos["position_explanation"] = explain_position_state(
                pos,
                current_price=current,
                progress=prog,
                pct_change=pct_change,
                days_open=days,
                readiness_score=readiness_score,
                rebuild_pressure=rebuild_pressure,
            )
        except TypeError:
            pos["position_explanation"] = explain_position_state(pos, current)
        except Exception:
            pos["position_explanation"] = {
                "headline": f"{symbol} position review",
                "summary": "Position explanation unavailable.",
            }

        try:
            pos["soulaana"] = soulaana_explain_position(
                {
                    "symbol": symbol,
                    "current_price": round(current, 2),
                    "entry": entry,
                    "target": target,
                    "stop": stop,
                    "pnl": pos.get("pnl", pos.get("unrealized_pnl", 0)),
                    "progress": prog,
                    "pct_change": pct_change,
                    "days_open": days,
                    "readiness_score": pos.get("readiness_score"),
                    "promotion_score": pos.get("promotion_score"),
                    "rebuild_pressure": pos.get("rebuild_pressure"),
                    "setup_family": pos.get("setup_family"),
                    "entry_quality": pos.get("entry_quality"),
                    "decision_reason": pos.get("decision_reason", pos.get("final_reason", "")),
                    "vehicle_selected": pos.get("vehicle_selected", pos.get("vehicle", "STOCK")),
                    "v2": pos.get("v2", {}),
                    "v2_score": pos.get("v2_score", 0.0),
                    "v2_confidence": pos.get("v2_confidence", ""),
                    "v2_reason": pos.get("v2_reason", ""),
                    "v2_regime_alignment": pos.get("v2_regime_alignment", ""),
                    "v2_signal_strength": pos.get("v2_signal_strength", 0.0),
                    "v2_conviction_adjustment": pos.get("v2_conviction_adjustment", 0.0),
                    "v2_vehicle_bias": pos.get("v2_vehicle_bias", ""),
                    "v2_thesis": pos.get("v2_thesis", ""),
                    "v2_notes": pos.get("v2_notes", []),
                    "v2_risk_flags": pos.get("v2_risk_flags", []),
                    "v2_quality": pos.get("v2_quality", 0.0),
                }
            )
        except Exception:
            pos["soulaana"] = {}

        pos["_monitor_days_open"] = days
        pos["_monitor_progress"] = prog
        pos["_monitor_pct_change"] = pct_change
        pos["_capital_pressure_score"] = _capital_pressure_score(pos)
        enriched_positions.append(pos)

    weakest_symbol = None
    if protection["enabled"] and enriched_positions:
        ranked = sorted(
            enriched_positions,
            key=lambda p: (
                _safe_float(p.get("_capital_pressure_score", 0.0), 0.0),
                _safe_float(p.get("rebuild_pressure", 0.0), 0.0),
                -_safe_float(p.get("_monitor_progress", 0.0), 0.0),
                -_safe_float(p.get("readiness_score", 0.0), 0.0),
            ),
            reverse=True,
        )
        weakest_symbol = str(ranked[0].get("symbol", "") or "").upper().strip()

    for pos in enriched_positions:
        symbol = pos["symbol"]
        entry = float(pos.get("entry", pos.get("price", 0)) or 0)
        current = float(pos.get("current_price", entry) or entry)
        stop = float(pos.get("stop", entry) or entry)
        target = float(pos.get("target", entry) or entry)
        score = float(pos.get("score", 0) or 0)
        prev_score = float(pos.get("previous_score", score) or score)
        days = _safe_float(pos.get("_monitor_days_open", 0.0), 0.0)
        prog = _safe_float(pos.get("_monitor_progress", 0.0), 0.0)
        pct_change = _safe_float(pos.get("_monitor_pct_change", 0.0), 0.0)
        rebuild_pressure = float(pos.get("rebuild_pressure", 0) or 0)
        readiness_score = float(pos.get("readiness_score", 0) or 0)
        v2_signal_strength = _safe_float(pos.get("v2_signal_strength", 0.0), 0.0)
        v2_conviction_adjustment = _safe_float(pos.get("v2_conviction_adjustment", 0.0), 0.0)
        v2_regime_alignment = _safe_str(pos.get("v2_regime_alignment", ""), "").lower()
        v2_risk_flags = _safe_list(pos.get("v2_risk_flags", []))

        learning_notes: List[str] = []
        pressure_reasons: List[str] = []
        action = "HOLD"

        hard_stop_hit = current <= stop
        target_hit = current >= target
        deep_loss = pct_change <= -1.25
        medium_loss = pct_change <= -0.75
        light_loss = pct_change <= -0.35
        very_new_trade = days < 0.20
        early_trade = days < 0.50
        meaningful_progress_failure = days >= 1.5 and prog < 0.10
        severe_stall = days >= 3 and prog < 0.20
        structure_drop = score < prev_score - 12
        heavy_rebuild = rebuild_pressure >= 45
        very_heavy_rebuild = rebuild_pressure >= 60
        weak_readiness = readiness_score < 105

        v2_negative = (
            v2_signal_strength < 0
            or v2_conviction_adjustment < 0
            or v2_regime_alignment in {"misaligned", "against_regime", "weak"}
            or len(v2_risk_flags) > 0
        )

        if hard_stop_hit:
            action = "STOP_LOSS"
            pressure_reasons.append("hard stop hit")
        elif target_hit:
            action = "TAKE_PROFIT"
            pressure_reasons.append("target hit")
        elif very_new_trade:
            action = "HOLD"
            learning_notes.append("very new trade protected from premature exit")
        elif early_trade and not deep_loss:
            action = "HOLD"
            learning_notes.append("early trade given room before weakness exit logic")
        elif deep_loss and days >= 0.10:
            action = "CUT_WEAKNESS"
            pressure_reasons.append("deep adverse move")
        elif medium_loss and very_heavy_rebuild and days >= 0.20:
            action = "RISK_ALERT"
            pressure_reasons.append("medium loss with heavy rebuild pressure")
        elif severe_stall and heavy_rebuild:
            action = "TIME_EXIT"
            pressure_reasons.append("trade stalled too long with elevated rebuild pressure")
        elif meaningful_progress_failure and weak_readiness and heavy_rebuild:
            action = "NO_FOLLOW_THROUGH"
            pressure_reasons.append("weak follow-through plus weak readiness")
        elif structure_drop and heavy_rebuild and days >= 0.25:
            if delay_exit_bias_active and current > stop * 1.01:
                action = "HOLD"
                learning_notes.append("delay_exit_bias held the position despite structure deterioration")
            else:
                action = "STRUCTURE_DETERIORATION"
                pressure_reasons.append("structure deteriorated with rebuild pressure")
        elif v2_negative and days >= 0.50 and prog < 0.15 and pct_change <= -0.35:
            action = "V2_DETERIORATION"
            pressure_reasons.append("V2 posture turned against the position")
        elif prog > 0.60 and current > entry:
            action = "PROTECT_PROFIT"
            pressure_reasons.append("profit protection zone reached")
        else:
            action = "HOLD"
            if light_loss:
                learning_notes.append("minor weakness tolerated")
            if days < 0.50:
                learning_notes.append("early-life trade given room to work")
            if not heavy_rebuild:
                learning_notes.append("rebuild pressure not extreme")
            if readiness_score >= 105:
                learning_notes.append("readiness still supportive")
            if not v2_negative:
                learning_notes.append("V2 posture not materially bearish")

        if protection["enabled"]:
            pos["capital_protection_mode"] = True
            pos["capital_protection_snapshot"] = protection
            if symbol == weakest_symbol:
                if action == "HOLD":
                    if days >= 0.20:
                        if pct_change < -0.75 and rebuild_pressure >= 20:
                            action = "CAPITAL_PROTECTION_EXIT"
                            pressure_reasons.append("weakest open position under reserve breach")
                        elif pct_change <= -0.50:
                            action = "CAPITAL_PROTECTION_EXIT"
                            pressure_reasons.append("capital protection exit on active loser")
                        elif days >= 1 and prog < 0.10:
                            action = "CAPITAL_PROTECTION_EXIT"
                            pressure_reasons.append("capital protection exit on stalled position")
                        elif v2_negative and pct_change < -0.25:
                            action = "CAPITAL_PROTECTION_EXIT"
                            pressure_reasons.append("capital protection plus negative V2 posture")
                        else:
                            learning_notes.append("flagged as weakest position, but not weak enough to force exit yet")
                    else:
                        learning_notes.append("capital protection active, but fresh trade shield delayed forced exit")
            else:
                learning_notes.append("capital protection active, but this is not the weakest position")
        else:
            pos["capital_protection_mode"] = False
            pos["capital_protection_snapshot"] = protection

        if learning_notes:
            existing_notes = pos.get("learning_exit_notes", [])
            if not isinstance(existing_notes, list):
                existing_notes = []
            pos["learning_exit_notes"] = existing_notes + learning_notes

        pos["monitor_debug"] = {
            "days_open": round(days, 3),
            "progress": round(prog, 3),
            "pct_change": round(pct_change, 3),
            "readiness_score": round(readiness_score, 2),
            "rebuild_pressure": round(rebuild_pressure, 2),
            "score": round(score, 2),
            "previous_score": round(prev_score, 2),
            "pressure_reasons": pressure_reasons,
            "learning_notes": learning_notes,
            "delay_exit_bias_active": delay_exit_bias_active,
            "capital_protection_mode": protection["enabled"],
            "weakest_symbol": weakest_symbol,
            "capital_pressure_score": round(_safe_float(pos.get("_capital_pressure_score", 0.0), 0.0), 2),
            "v2_score": round(_safe_float(pos.get("v2_score", 0.0), 0.0), 2),
            "v2_signal_strength": round(v2_signal_strength, 2),
            "v2_conviction_adjustment": round(v2_conviction_adjustment, 2),
            "v2_regime_alignment": v2_regime_alignment,
            "v2_risk_flags": v2_risk_flags,
            "final_action": action,
        }

        replace_position(symbol, pos)

        print(
            f"{symbol} | Current: {round(current, 2)} | Entry: {round(entry, 2)} | "
            f"Stop: {round(stop, 2)} | Progress: {round(prog, 2)} | "
            f"Readiness: {round(readiness_score, 2)} | Rebuild: {round(rebuild_pressure, 2)} | "
            f"V2Score: {round(_safe_float(pos.get('v2_score', 0.0), 0.0), 2)} | "
            f"V2Strength: {round(v2_signal_strength, 2)} | "
            f"CapitalPressure: {round(_safe_float(pos.get('_capital_pressure_score', 0.0), 0.0), 2)} | "
            f"Action: {action}"
        )

        if action != "HOLD":
            close_reason = action.lower()
            result = close_position(symbol, current, reason=close_reason)
            actions.append(
                {
                    "symbol": symbol,
                    "reason": close_reason,
                    "result": result,
                }
            )
            if result.get("closed"):
                print(
                    f"CLOSED: {symbol} | Reason: {action} | "
                    f"PnL: {result.get('pnl')} | Exit: {result.get('exit_price')}"
                )
            elif result.get("blocked"):
                print(f"BLOCKED CLOSE: {symbol} | Reason: {result.get('reason')}")

    return actions
