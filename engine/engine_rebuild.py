"""
REBUILD ENGINE
Marks setups and behaviors that should be repaired instead of promoted.
"""

from typing import Dict, List, Any

def _safe_float(value, default=0.0):
    try:
        return float(value or 0)
    except Exception:
        return default

def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value or 0)
    except Exception:
        return default


def compute_rebuild_pressure(signal: Dict) -> float:
    readiness_score = _safe_float(signal.get("readiness_score", 0), 0.0)
    promotion_score = _safe_float(signal.get("promotion_score", 0), 0.0)
    execution_quality = _safe_float(signal.get("execution_quality", 0), 0.0)

    rebuild_pressure = 0.0

    if readiness_score < 115:
        rebuild_pressure += 15
    if promotion_score < 95:
        rebuild_pressure += 15
    if execution_quality < 100:
        rebuild_pressure += 8

    return round(rebuild_pressure, 2)


def apply_learning_to_rebuild(signal: Dict, adjustment_map: Dict) -> Dict:
    signal = dict(signal or {})
    items = adjustment_map.get("items", []) if isinstance(adjustment_map, dict) else []
    auto_policy = adjustment_map.get("auto_policy", {}) if isinstance(adjustment_map, dict) else {}

    rebuild_pressure = _safe_float(signal.get("rebuild_pressure", 0), 0.0)
    notes = []
    penalties = []
    flags = []

    setup_family = str(signal.get("setup_family", "") or "").strip().lower()
    entry_quality = str(signal.get("entry_quality", "") or "").strip().lower()

    for item in items:
        if not isinstance(item, dict):
            continue

        item_type = str(item.get("type", "") or "").strip().lower()
        strength = str(item.get("strength", "") or "").strip().lower()
        action = str(item.get("action", "") or "").strip().lower()

        penalty = 0
        if strength == "high":
            penalty = 10
        elif strength == "medium":
            penalty = 5
        elif strength == "low":
            penalty = 2

        penalty *= _safe_float(auto_policy.get("rebuild_penalty_multiplier", 1.0), 1.0)
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
                rebuild_pressure += penalty
                penalties.append({
                    "type": "setup_penalty",
                    "target": target_setup,
                    "applied_to": setup_family,
                    "penalty": penalty,
                })
                notes.append(f"Rebuild pressure: {target_setup} -> {setup_family} (+{penalty})")

        elif item_type == "behavior_flag":
            target_behavior = str(item.get("entry_quality", "") or "").strip().lower()

            behavior_matches = False

            if target_behavior == entry_quality:
                behavior_matches = True
            elif target_behavior == "cut_on_weakness" and entry_quality in {
                "high_conviction", "acceptable"
            }:
                behavior_matches = True
            elif target_behavior == "manual_exit_loss" and entry_quality in {
                "high_conviction", "acceptable"
            }:
                behavior_matches = True

            if behavior_matches:
                flags.append({
                    "type": "behavior_flag",
                    "behavior": target_behavior,
                    "applied_to": entry_quality,
                    "action": action,
                })
                notes.append(f"Rebuild behavior flag: {target_behavior} -> {entry_quality}")

    signal["rebuild_before_learning"] = _safe_float(signal.get("rebuild_pressure", 0), 0.0)
    signal["rebuild_pressure"] = round(max(0, rebuild_pressure), 2)
    signal["rebuild_penalties"] = penalties
    signal["rebuild_flags"] = flags
    signal["rebuild_notes"] = notes
    signal["rebuild_adjusted"] = bool(penalties or flags)

    return signal


def build_rebuild_layer(signals: List[Dict], adjustment_map: Dict) -> List[Dict]:
    rebuilt = []

    for signal in signals:
        signal_copy = dict(signal or {})
        signal_copy["rebuild_pressure"] = compute_rebuild_pressure(signal_copy)
        signal_copy = apply_learning_to_rebuild(signal_copy, adjustment_map)
        rebuilt.append(signal_copy)

    rebuilt.sort(key=lambda x: x.get("rebuild_pressure", 0), reverse=True)
    return rebuilt
