"""
PROMOTION ENGINE
Ranks which ideas deserve elevation after readiness scoring.
"""

from typing import Dict, List, Any


def _safe_float(value, default=0.0):
    try:
        return float(value or 0)
    except Exception:
        return default


def compute_promotion_score(signal: Dict) -> float:
    readiness_score = _safe_float(signal.get("readiness_score", 0), 0.0)
    execution_quality = _safe_float(signal.get("execution_quality", 0), 0.0)
    score = _safe_float(signal.get("score", 0), 0.0)

    promotion_score = (readiness_score * 0.5) + (execution_quality * 0.3) + (score * 0.2)
    return round(promotion_score, 2)


def apply_learning_to_promotion(signal: Dict, adjustment_map: Dict) -> Dict:
    signal = dict(signal or {})
    items = adjustment_map.get("items", []) if isinstance(adjustment_map, dict) else []
    auto_policy = adjustment_map.get("auto_policy", {}) if isinstance(adjustment_map, dict) else {}

    promotion_score = _safe_float(signal.get("promotion_score", 0), 0.0)
    notes = list(signal.get("promotion_notes", []) or [])
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
            penalty = 8
        elif strength == "medium":
            penalty = 4
        elif strength == "low":
            penalty = 2

        penalty *= _safe_float(auto_policy.get("promotion_penalty_multiplier", 1.0), 1.0)
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
                promotion_score -= penalty
                penalties.append({
                    "type": "setup_penalty",
                    "target": target_setup,
                    "applied_to": setup_family,
                    "penalty": penalty,
                })
                notes.append(f"Promotion penalty: {target_setup} -> {setup_family} (-{penalty})")

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
                notes.append(f"Promotion behavior flag: {target_behavior} -> {entry_quality}")

    signal["promotion_before_learning"] = _safe_float(signal.get("promotion_score", 0), 0.0)
    signal["promotion_score"] = round(max(0, promotion_score), 2)
    signal["promotion_penalties"] = penalties
    signal["promotion_flags"] = flags
    signal["promotion_notes"] = notes
    signal["promotion_adjusted"] = bool(penalties or flags)

    return signal


def build_promotion_layer(signals: list, adjustment_map: dict) -> list:
    promoted = []

    items = adjustment_map.get("items", []) if isinstance(adjustment_map, dict) else []

    for row in signals:
        if not isinstance(row, dict):
            continue

        enriched = dict(row)

        base_score = float(enriched.get("readiness_score", enriched.get("score", 0)) or 0)
        promotion_score = base_score * 0.65  # base compression into promotion layer

        penalties = []
        flags = []
        notes = []

        setup_family = str(enriched.get("setup_family", "") or "").strip().lower()
        entry_quality = str(enriched.get("entry_quality", "") or "").strip().lower()

        # -----------------------------
        # LEARNING ADJUSTMENTS (STRONGER THAN BEFORE)
        # -----------------------------
        for item in items:
            if not isinstance(item, dict):
                continue

            item_type = str(item.get("type", "")).lower()
            strength = str(item.get("strength", "low")).lower()

            penalty_value = 0
            if strength == "high":
                penalty_value = 12
            elif strength == "medium":
                penalty_value = 6
            elif strength == "low":
                penalty_value = 3

            # SETUP PENALTY (MAIN DRIVER)
            if item_type == "setup_penalty":
                target = str(item.get("setup", "")).lower()

                # 🔥 IMPORTANT: apply to ALL setups (not just exact match)
                if target:
                    promotion_score -= penalty_value

                    penalties.append({
                        "type": "setup_penalty",
                        "target": target,
                        "applied_to": setup_family,
                        "penalty": penalty_value,
                    })

                    notes.append(
                        f"Promotion penalty: {target} -> {setup_family} (-{penalty_value})"
                    )

            # BEHAVIOR FLAG
            elif item_type == "behavior_flag":
                behavior = str(item.get("entry_quality", "")).lower()
                action = str(item.get("action", "")).lower()

                flags.append({
                    "type": "behavior_flag",
                    "behavior": behavior,
                    "applied_to": entry_quality,
                    "action": action,
                })

                notes.append(
                    f"Promotion behavior flag: {behavior} -> {entry_quality}"
                )

        # -----------------------------
        # REBUILD PRESSURE INTEGRATION
        # -----------------------------
        rebuild_pressure = float(enriched.get("rebuild_pressure", 0) or 0)

        if rebuild_pressure >= 40:
            promotion_score -= 14
            notes.append("Promotion suppressed due to high rebuild pressure")

        elif rebuild_pressure >= 25:
            promotion_score -= 6
            notes.append("Promotion reduced due to moderate rebuild pressure")

        # -----------------------------
        # FINAL FIELDS
        # -----------------------------
        enriched["promotion_before_learning"] = round(base_score * 0.65, 2)
        enriched["promotion_score"] = round(max(0, promotion_score), 2)

        enriched["promotion_penalties"] = penalties
        enriched["promotion_flags"] = flags
        enriched["promotion_notes"] = notes
        enriched["promotion_adjusted"] = bool(penalties or flags)

        # -----------------------------
        # PROMOTION GATE (NEW 🔥)
        # -----------------------------
        enriched["promotion_gate_passed"] = (
            enriched["promotion_score"] >= 100
            and rebuild_pressure < 45
        )

        promoted.append(enriched)

    return promoted
