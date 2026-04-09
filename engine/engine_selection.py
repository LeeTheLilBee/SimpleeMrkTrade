"""
ENGINE SELECTION SYSTEM
"""

from typing import Any, Dict, List
from engine.engine_readiness import build_readiness_layer
from engine.engine_promotion import build_promotion_layer
from engine.engine_auto_learning import build_auto_learning_policy
from engine.engine_rebuild import build_rebuild_layer


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value or 0)
    except Exception:
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(value or 0))
    except Exception:
        return default


def normalize_market_regime(system_state: Dict) -> str:
    regime = str(system_state.get("regime", "Neutral")).strip().lower()

    if regime in {"bull", "risk-on", "strong", "trend", "bullish", "supportive"}:
        return "strong"
    if regime in {"weak", "risk-off", "defensive", "bear", "bearish"}:
        return "weak"
    return "neutral"


def normalize_volatility(system_state: Dict) -> str:
    vol = str(system_state.get("volatility", "Normal")).strip().lower()

    if vol in {"high", "elevated", "volatile"}:
        return "high"
    if vol in {"low", "calm"}:
        return "low"
    return "normal"


def infer_setup_family(signal: Dict) -> str:
    setup_family = str(
        signal.get("setup_family")
        or signal.get("setup_type")
        or ""
    ).strip().lower()

    if setup_family:
        return setup_family

    score = _safe_float(signal.get("score", signal.get("latest_score", 0)), 0.0)
    confidence = str(signal.get("confidence", signal.get("latest_confidence", "LOW"))).strip().upper()

    if score >= 180 and confidence == "HIGH":
        return "high_score_momentum"
    if score >= 120:
        return "strong_structured"
    if score >= 70:
        return "structured"
    return "speculative"


def infer_entry_quality(signal: Dict) -> str:
    entry_quality = str(signal.get("entry_quality", "") or "").strip().lower()
    if entry_quality:
        return entry_quality

    score = _safe_float(signal.get("score", signal.get("latest_score", 0)), 0.0)
    confidence = str(signal.get("confidence", signal.get("latest_confidence", "LOW"))).strip().upper()

    if score >= 180 and confidence == "HIGH":
        return "high_conviction"
    if score >= 100 and confidence in {"HIGH", "MEDIUM"}:
        return "acceptable"
    return "weak"


def score_signal_quality(signal: Dict) -> int:
    score = _safe_int(signal.get("score", signal.get("latest_score", 0)), 0)
    confidence = str(signal.get("confidence", signal.get("latest_confidence", "LOW"))).strip().upper()
    setup_type = str(signal.get("setup_type", "Continuation") or "Continuation").strip().title()
    setup_family = infer_setup_family(signal)
    entry_quality = infer_entry_quality(signal)

    quality = score

    if confidence == "HIGH":
        quality += 15
    elif confidence == "MEDIUM":
        quality += 7

    if setup_type == "Breakout":
        quality += 8
    elif setup_type == "Continuation":
        quality += 5
    elif setup_type == "Pullback":
        quality += 3

    if setup_family == "high_score_momentum":
        quality += 10
    elif setup_family == "strong_structured":
        quality += 6
    elif setup_family == "structured":
        quality += 3
    elif setup_family == "failed_high_score_momentum":
        quality -= 20
    elif setup_family == "failed_structured":
        quality -= 12
    elif setup_family == "speculative":
        quality -= 8

    if entry_quality in {"high_conviction", "high_conviction_win"}:
        quality += 6
    elif entry_quality in {"acceptable", "acceptable_win"}:
        quality += 2
    elif entry_quality in {"weak", "failed_clean", "weak_followthrough"}:
        quality -= 6
    elif entry_quality in {"cut_on_weakness", "manual_exit_loss", "stopped_out", "high_conviction_loss"}:
        quality -= 10

    return quality


def passes_trade_gate(signal: Dict, system_state: Dict) -> bool:
    regime = normalize_market_regime(system_state)
    volatility = normalize_volatility(system_state)

    raw_score = _safe_float(signal.get("score", signal.get("latest_score", 0)), 0.0)
    confidence = str(signal.get("confidence", signal.get("latest_confidence", "LOW"))).strip().upper()
    setup_family = infer_setup_family(signal)
    learning_penalties = signal.get("learning_penalties", [])
    learning_flags = signal.get("learning_flags", [])

    min_score = 65.0

    if regime == "weak":
        min_score += 12
    elif regime == "neutral":
        min_score += 3

    if volatility == "high":
        min_score += 8

    if setup_family == "failed_high_score_momentum":
        min_score += 6
    elif setup_family == "failed_structured":
        min_score += 4
    elif setup_family == "speculative":
        min_score += 8

    if isinstance(learning_penalties, list) and learning_penalties:
        min_score += min(
            4.0,
            sum(_safe_float(x.get("penalty", 0), 0.0) for x in learning_penalties if isinstance(x, dict)) * 0.10
        )

    if raw_score < min_score:
        return False

    if regime == "weak" and confidence == "LOW":
        return False

    if isinstance(learning_flags, list):
        for flag in learning_flags:
            if not isinstance(flag, dict):
                continue
            action = str(flag.get("action", "") or "").strip().lower()
            if action == "reduce_manual_override" and confidence == "LOW":
                return False

    return True


def max_active_candidates(system_state: Dict) -> int:
    regime = normalize_market_regime(system_state)
    volatility = normalize_volatility(system_state)

    if regime == "strong" and volatility in {"low", "normal"}:
        return 15
    if regime == "strong" and volatility == "high":
        return 10
    if regime == "neutral" and volatility == "normal":
        return 8
    if regime == "neutral" and volatility == "high":
        return 6
    if regime == "weak":
        return 4
    return 6


def get_learning_adjustment_map() -> dict:
    try:
        from web.app import build_learning_dashboard_payload, get_canonical_snapshot

        snapshot = get_canonical_snapshot()
        if not isinstance(snapshot, dict):
            snapshot = {}

        learning = build_learning_dashboard_payload()
        adjustments = learning.get("adjustments", {}) if isinstance(learning, dict) else {}
        memory = learning.get("memory", {}) if isinstance(learning, dict) else {}
        items = adjustments.get("adjustments", []) if isinstance(adjustments, dict) else []

        auto_policy = build_auto_learning_policy(memory, adjustments)

        return {
            "raw_snapshot": snapshot,
            "items": items if isinstance(items, list) else [],
            "memory": memory if isinstance(memory, dict) else {},
            "auto_policy": auto_policy if isinstance(auto_policy, dict) else {},
        }
    except Exception:
        return {
            "raw_snapshot": {},
            "items": [],
            "memory": {},
            "auto_policy": {},
        }


def apply_learning_adjustments_to_signal(signal: dict, adjustment_map: dict) -> dict:
    signal = dict(signal or {})
    items = adjustment_map.get("items", []) if isinstance(adjustment_map, dict) else []
    auto_policy = adjustment_map.get("auto_policy", {}) if isinstance(adjustment_map, dict) else {}

    score_before = _safe_float(signal.get("score", 0), 0.0)
    score = score_before
    notes = list(signal.get("learning_notes", []) or [])
    penalties: List[Dict[str, Any]] = []
    flags: List[Dict[str, Any]] = []

    setup_family = infer_setup_family(signal)
    entry_quality = infer_entry_quality(signal)

    signal["setup_family"] = setup_family
    signal["entry_quality"] = entry_quality

    for item in items:
        if not isinstance(item, dict):
            continue

        item_type = str(item.get("type", "") or "").strip().lower()
        action = str(item.get("action", "") or "").strip().lower()
        strength = str(item.get("strength", "") or "").strip().lower()

        penalty = 0
        if strength == "high":
            penalty = 5
        elif strength == "medium":
            penalty = 3
        elif strength == "low":
            penalty = 1

        penalty *= _safe_float(auto_policy.get("execution_penalty_multiplier", 1.0), 1.0)
        penalty = round(penalty, 2)

        if item_type == "setup_penalty":
            target_setup = str(item.get("setup", "") or "").strip().lower()

            setup_matches = False

            if target_setup == setup_family:
                setup_matches = True
            elif target_setup == "failed_high_score_momentum" and setup_family in {
                "high_score_momentum", "continuation", "breakout", "pullback"
            }:
                setup_matches = True
            elif target_setup == "failed_structured" and setup_family in {
                "strong_structured", "structured"
            }:
                setup_matches = True

            if setup_matches:
                score -= penalty
                penalties.append({
                    "type": "setup_penalty",
                    "setup": target_setup,
                    "applied_to": setup_family,
                    "penalty": penalty,
                    "reason": item.get("reason", ""),
                })
                notes.append(f"Learning penalty applied: {target_setup} -> {setup_family} (-{penalty})")

        elif item_type == "behavior_flag":
            target_entry_quality = str(item.get("entry_quality", "") or "").strip().lower()

            entry_matches = False

            if target_entry_quality == entry_quality:
                entry_matches = True
            elif target_entry_quality == "cut_on_weakness" and entry_quality in {
                "high_conviction", "acceptable"
            }:
                entry_matches = True
            elif target_entry_quality == "manual_exit_loss" and entry_quality in {
                "high_conviction", "acceptable"
            }:
                entry_matches = True

            if entry_matches:
                flags.append({
                    "type": "behavior_flag",
                    "entry_quality": target_entry_quality,
                    "applied_to": entry_quality,
                    "action": action,
                    "reason": item.get("reason", ""),
                })
                notes.append(f"Learning behavior flag active: {target_entry_quality} -> {entry_quality} ({action})")
    
    if auto_policy.get("delay_exit_bias_active"):
        notes.append("Auto learning policy active: delay_exit_bias")

    if auto_policy.get("manual_override_caution"):
        notes.append("Auto learning policy active: manual_override_caution")

    if auto_policy.get("failed_high_score_momentum_pressure"):
        notes.append("Auto learning policy active: failed_high_score_momentum_pressure")

    signal["auto_learning_policy"] = auto_policy
    signal["score_before_learning"] = round(score_before, 2)
    signal["score"] = round(max(0, score), 2)
    signal["learning_penalties"] = penalties
    signal["learning_flags"] = flags
    signal["learning_notes"] = notes
    signal["learning_adjusted"] = bool(penalties or flags)
    signal["learning_blocked"] = bool(
        penalties and signal["score"] <= 60
    )

    return signal


def build_execution_universe(signals: List[Dict], system_state: Dict) -> Dict:
    learning_adjustment_map = get_learning_adjustment_map()

    signals = build_readiness_layer(signals, learning_adjustment_map)
    signals = build_promotion_layer(signals, learning_adjustment_map)
    signals = build_rebuild_layer(signals, learning_adjustment_map)

    ranked = []
    for signal in signals:
        if not isinstance(signal, dict):
            continue

        signal_copy = dict(signal)
        signal_copy = apply_learning_adjustments_to_signal(signal_copy, learning_adjustment_map)

        quality = score_signal_quality(signal_copy)
        signal_copy["execution_quality"] = quality

        promotion_score = _safe_float(signal_copy.get("promotion_score", 0), 0.0)
        readiness_score = _safe_float(signal_copy.get("readiness_score", 0), 0.0)

        promotion_gate_passed = promotion_score >= 95
        readiness_gate_passed = readiness_score >= 115

        base_eligible = passes_trade_gate(signal_copy, system_state)
        signal_copy["promotion_gate_passed"] = promotion_gate_passed
        signal_copy["readiness_gate_passed"] = readiness_gate_passed
        rebuild_pressure = _safe_float(signal_copy.get("rebuild_pressure", 0), 0.0)
        rebuild_gate_passed = rebuild_pressure < 32

        signal_copy["rebuild_gate_passed"] = rebuild_gate_passed
        signal_copy["eligible"] = bool(
            base_eligible and promotion_gate_passed and readiness_gate_passed and rebuild_gate_passed
        )

        if signal_copy.get("learning_adjusted") and signal_copy.get("score", 0) < signal_copy.get("score_before_learning", 0):
            signal_copy["learning_blocked"] = not signal_copy.get("eligible", False)
        else:
            signal_copy["learning_blocked"] = False

        ranked.append(signal_copy)

    ranked.sort(
        key=lambda x: (
            x.get("promotion_score", 0),
            x.get("readiness_score", 0),
            -x.get("rebuild_pressure", 0),
            x.get("execution_quality", 0),
        ),
        reverse=True,
    )

    eligible = [s for s in ranked if s.get("eligible")]
    rejected = [s for s in ranked if not s.get("eligible")]
    cap = max_active_candidates(system_state)
    selected = eligible[:cap]

    return {
        "selected": selected,
        "eligible_count": len(eligible),
        "rejected_count": len(rejected),
        "cap": cap,
        "regime": normalize_market_regime(system_state),
        "volatility": normalize_volatility(system_state),
    }


def build_execution_summary(universe: Dict) -> Dict:
    selected = universe.get("selected", []) if isinstance(universe, dict) else []

    return {
        "selected_symbols": [s.get("symbol") for s in selected if isinstance(s, dict)],
        "selected_count": len(selected),
        "eligible_count": universe.get("eligible_count", 0),
        "rejected_count": universe.get("rejected_count", 0),
        "cap": universe.get("cap", 0),
        "regime": universe.get("regime", "neutral"),
        "volatility": universe.get("volatility", "normal"),
    }
