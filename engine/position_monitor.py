from datetime import datetime

from engine.paper_portfolio import show_positions, replace_position
from engine.close_trade import close_position
from engine.data_utils import safe_download
from engine.explainability_engine import explain_position_state
from engine.engine_selection import get_learning_adjustment_map
from engine.engine_readiness import build_readiness_layer
from engine.engine_promotion import build_promotion_layer
from engine.engine_rebuild import build_rebuild_layer


def _days_open(opened_at):
    try:
        dt = datetime.fromisoformat(opened_at)
        return (datetime.now() - dt).total_seconds() / 86400
    except Exception:
        return 0.0


def _progress(entry, current, target):
    if not entry or not target or target == entry:
        return 0.0
    return (current - entry) / (target - entry)


def _latest_price(symbol, fallback_price):
    df = safe_download(symbol, period="5d", auto_adjust=True, progress=False)
    if df is None or df.empty:
        return float(fallback_price or 0)

    try:
        close = df["Close"]
        if hasattr(close, "iloc"):
            val = close.iloc[-1]
            try:
                return float(val.item())
            except Exception:
                return float(val)
        return float(fallback_price or 0)
    except Exception:
        return float(fallback_price or 0)


def _build_learning_exit_map():
    adjustment_map = get_learning_adjustment_map()
    items = adjustment_map.get("items", []) if isinstance(adjustment_map, dict) else []

    behavior_flags = []
    for item in items:
        if not isinstance(item, dict):
            continue
        if str(item.get("type", "") or "").strip().lower() == "behavior_flag":
            behavior_flags.append(item)

    return {
        "behavior_flags": behavior_flags,
    }


def _has_delay_exit_bias(learning_exit_map):
    behavior_flags = learning_exit_map.get("behavior_flags", []) if isinstance(learning_exit_map, dict) else []
    for item in behavior_flags:
        if not isinstance(item, dict):
            continue
        action = str(item.get("action", "") or "").strip().lower()
        if action == "delay_exit_bias":
            return True
    return False


def _build_position_intelligence(pos: dict) -> dict:
    signal_like = {
        "symbol": pos.get("symbol"),
        "score": pos.get("score", 0),
        "confidence": pos.get("confidence", "LOW"),
        "setup_type": pos.get("setup_type", "Continuation"),
        "setup_family": pos.get("setup_family", ""),
        "entry_quality": pos.get("entry_quality", ""),
    }

    adjustment_map = get_learning_adjustment_map()

    readiness_view = build_readiness_layer([signal_like], adjustment_map)
    readiness_row = readiness_view[0] if readiness_view else {}

    promotion_view = build_promotion_layer([readiness_row], adjustment_map)
    promotion_row = promotion_view[0] if promotion_view else readiness_row

    rebuild_view = build_rebuild_layer([promotion_row], adjustment_map)
    rebuild_row = rebuild_view[0] if rebuild_view else promotion_row

    return {
        "readiness_score": float(rebuild_row.get("readiness_score", 0) or 0),
        "promotion_score": float(rebuild_row.get("promotion_score", 0) or 0),
        "rebuild_pressure": float(rebuild_row.get("rebuild_pressure", 0) or 0),
        "readiness_notes": rebuild_row.get("readiness_notes", []) or [],
        "promotion_notes": rebuild_row.get("promotion_notes", []) or [],
        "rebuild_notes": rebuild_row.get("rebuild_notes", []) or [],
        "setup_family": rebuild_row.get("setup_family", pos.get("setup_family", "")),
        "entry_quality": rebuild_row.get("entry_quality", pos.get("entry_quality", "")),
    }


def monitor_open_positions():
    positions = show_positions()
    actions = []
    learning_exit_map = _build_learning_exit_map()
    delay_exit_bias_active = _has_delay_exit_bias(learning_exit_map)

    for pos in positions:
        symbol = pos.get("symbol")

        entry = float(pos.get("entry", pos.get("price", 0)) or 0)
        current = _latest_price(symbol, pos.get("current_price", entry))
        target = float(pos.get("target", entry) or entry)
        stop = float(pos.get("stop", entry) or entry)

        score = float(pos.get("score", 0) or 0)
        prev_score = float(pos.get("previous_score", score) or score)
        opened_at = pos.get("opened_at")

        pos["current_price"] = round(current, 2)
        pos["position_explanation"] = explain_position_state(pos, current)

        position_intel = _build_position_intelligence(pos)
        pos["readiness_score"] = position_intel.get("readiness_score", 0)
        pos["promotion_score"] = position_intel.get("promotion_score", 0)
        pos["rebuild_pressure"] = position_intel.get("rebuild_pressure", 0)
        pos["setup_family"] = position_intel.get("setup_family", pos.get("setup_family", ""))
        pos["entry_quality"] = position_intel.get("entry_quality", pos.get("entry_quality", ""))
        pos["readiness_notes"] = position_intel.get("readiness_notes", [])
        pos["promotion_notes"] = position_intel.get("promotion_notes", [])
        pos["rebuild_notes"] = position_intel.get("rebuild_notes", [])

        days = _days_open(opened_at)
        prog = _progress(entry, current, target)
        rebuild_pressure = float(pos.get("rebuild_pressure", 0) or 0)
        readiness_score = float(pos.get("readiness_score", 0) or 0)

        learning_notes = []
        action = "HOLD"

        if current <= stop:
            action = "STOP_LOSS"

        elif current >= target:
            action = "TAKE_PROFIT"

        elif current < entry and prog < 0:
            if delay_exit_bias_active and current > stop * 1.01 and days < 2 and rebuild_pressure < 35:
                action = "HOLD"
                learning_notes.append("delay_exit_bias prevented immediate CUT_WEAKNESS")
            else:
                action = "CUT_WEAKNESS"

        elif current < entry * 0.995:
            if rebuild_pressure >= 40:
                action = "RISK_ALERT"
            else:
                action = "HOLD"
                learning_notes.append("minor weakness tolerated because rebuild pressure is not extreme")

        elif days > 1 and prog < 0.2:
            if readiness_score < 110 or rebuild_pressure >= 35:
                action = "NO_FOLLOW_THROUGH"
            else:
                action = "HOLD"
                learning_notes.append("position given more time because readiness still supports it")

        elif days > 2 and prog < 0.5:
            if rebuild_pressure >= 35:
                action = "TIME_EXIT"
            else:
                action = "HOLD"
                learning_notes.append("time-based exit delayed because rebuild pressure is moderate")

        elif score < prev_score:
            if delay_exit_bias_active and prog > -0.1 and current > stop * 1.02 and rebuild_pressure < 35:
                action = "HOLD"
                learning_notes.append("delay_exit_bias prevented structure-based early exit")
            else:
                action = "STRUCTURE_DETERIORATION"

        elif prog > 0.6:
            action = "PROTECT_PROFIT"

        if learning_notes:
            existing_notes = pos.get("learning_exit_notes", [])
            if not isinstance(existing_notes, list):
                existing_notes = []
            pos["learning_exit_notes"] = existing_notes + learning_notes

        replace_position(symbol, pos)

        print(
            f"{symbol} | Current: {round(current, 2)} | Stop: {round(stop, 2)} | "
            f"Readiness: {round(readiness_score, 2)} | Rebuild: {round(rebuild_pressure, 2)} | Action: {action}"
        )

        if action != "HOLD":
            result = close_position(symbol, current, reason=action.lower())

            actions.append({
                "symbol": symbol,
                "reason": action.lower(),
                "result": result,
            })

            if result.get("closed"):
                print(f"CLOSED: {symbol} | Reason: {action} | PnL: {result.get('pnl')}")
            elif result.get("blocked"):
                print(f"BLOCKED CLOSE: {symbol} | Reason: {result.get('reason')}")

    return actions
