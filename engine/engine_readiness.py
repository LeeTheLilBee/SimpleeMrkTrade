"""
READINESS ENGINE
Pre-execution intelligence layer
"""

from typing import Dict, List
from engine.engine_auto_learning import build_auto_learning_policy

def _safe_float(value, default=0.0):
    try:
        return float(value or 0)
    except Exception:
        return default

# ===============================
# BASE READINESS SCORE
# ===============================

def compute_base_readiness(signal: Dict) -> float:
    score = float(signal.get("score", 0) or 0)
    confidence = str(signal.get("confidence", "LOW")).upper()

    readiness = score

    if confidence == "HIGH":
        readiness += 10
    elif confidence == "MEDIUM":
        readiness += 5

    return readiness


# ===============================
# LEARNING ADJUSTMENTS (READINESS)
# ===============================

def apply_learning_to_readiness(signal: Dict, adjustment_map: Dict) -> Dict:
    from engine.engine_selection import infer_setup_family, infer_entry_quality

    signal = dict(signal or {})
    items = adjustment_map.get("items", []) if isinstance(adjustment_map, dict) else []
    auto_policy = adjustment_map.get("auto_policy", {}) if isinstance(adjustment_map, dict) else {}

    readiness = float(signal.get("readiness_score", 0) or 0)

    notes = []
    penalties = []
    flags = []

    setup_family = infer_setup_family(signal)
    entry_quality = infer_entry_quality(signal)

    signal["setup_family"] = setup_family
    signal["entry_quality"] = entry_quality

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

        penalty *= _safe_float(auto_policy.get("readiness_penalty_multiplier", 1.0), 1.0)
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
                readiness -= penalty
                penalties.append({
                    "type": "setup_penalty",
                    "target": target_setup,
                    "applied_to": setup_family,
                    "penalty": penalty,
                })
                notes.append(f"Readiness penalty: {target_setup} -> {setup_family} (-{penalty})")

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
                notes.append(f"Behavior flag: {target_behavior} -> {entry_quality}")

    signal["readiness_before_learning"] = float(signal.get("readiness_score", 0) or 0)
    signal["readiness_score"] = round(max(0, readiness), 2)
    signal["readiness_penalties"] = penalties
    signal["readiness_flags"] = flags
    signal["readiness_notes"] = notes
    signal["readiness_adjusted"] = bool(penalties or flags)

    return signal


# ===============================
# BUILD READINESS LAYER
# ===============================

def build_readiness_layer(signals: List[Dict], adjustment_map: Dict) -> List[Dict]:
    enriched = []

    for signal in signals:
        signal_copy = dict(signal)

        # base readiness
        readiness = compute_base_readiness(signal_copy)
        signal_copy["readiness_score"] = readiness

        # apply learning pressure
        signal_copy = apply_learning_to_readiness(signal_copy, adjustment_map)

        enriched.append(signal_copy)

    # sort by readiness
    enriched.sort(key=lambda x: x.get("readiness_score", 0), reverse=True)

    return enriched
