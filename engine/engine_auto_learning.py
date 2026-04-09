"""
AUTO LEARNING ENGINE
Turns repeated learning outcomes into threshold and pressure adjustments.
"""

from typing import Dict, Any


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value or 0)
    except Exception:
        return default


def build_auto_learning_policy(memory: Dict, adjustments: Dict) -> Dict:
    memory = memory or {}
    adjustments = adjustments or {}

    top_failures = memory.get("top_failures", []) if isinstance(memory.get("top_failures", []), list) else []
    by_entry_quality = memory.get("by_entry_quality", {}) if isinstance(memory.get("by_entry_quality", {}), dict) else {}
    by_setup = memory.get("by_setup", {}) if isinstance(memory.get("by_setup", {}), dict) else {}
    adjustment_items = adjustments.get("adjustments", []) if isinstance(adjustments.get("adjustments", []), list) else []

    policy = {
        "readiness_penalty_multiplier": 1.0,
        "promotion_penalty_multiplier": 1.0,
        "rebuild_penalty_multiplier": 1.0,
        "execution_penalty_multiplier": 1.0,
        "delay_exit_bias_active": False,
        "manual_override_caution": False,
        "failed_high_score_momentum_pressure": False,
        "notes": [],
    }

    for item in top_failures:
        if not isinstance(item, dict):
            continue
        tag = str(item.get("tag", "") or "").strip().lower()
        count = int(item.get("count", 0) or 0)

        if tag == "cut_on_weakness" and count >= 5:
            policy["delay_exit_bias_active"] = True
            policy["execution_penalty_multiplier"] = 0.8
            policy["notes"].append("Auto learning: cut_on_weakness cluster activated delay-exit protection.")
        elif tag == "manual_exit_loss" and count >= 3:
            policy["manual_override_caution"] = True
            policy["promotion_penalty_multiplier"] = 1.1
            policy["notes"].append("Auto learning: manual exit losses raised promotion caution.")
        elif tag == "setup_failed_high_score_momentum" and count >= 5:
            policy["failed_high_score_momentum_pressure"] = True
            policy["readiness_penalty_multiplier"] = 1.2
            policy["promotion_penalty_multiplier"] = 1.2
            policy["rebuild_penalty_multiplier"] = 1.2
            policy["notes"].append("Auto learning: failed high-score momentum cluster increased pressure.")

    failed_setup = by_setup.get("failed_high_score_momentum", {})
    if isinstance(failed_setup, dict):
        losses = int(failed_setup.get("losses", 0) or 0)
        if losses >= 5:
            policy["failed_high_score_momentum_pressure"] = True
            policy["readiness_penalty_multiplier"] = max(policy["readiness_penalty_multiplier"], 1.2)
            policy["promotion_penalty_multiplier"] = max(policy["promotion_penalty_multiplier"], 1.2)
            policy["rebuild_penalty_multiplier"] = max(policy["rebuild_penalty_multiplier"], 1.2)

    cut_cluster = by_entry_quality.get("cut_on_weakness", {})
    if isinstance(cut_cluster, dict):
        losses = int(cut_cluster.get("losses", 0) or 0)
        if losses >= 5:
            policy["delay_exit_bias_active"] = True
            policy["execution_penalty_multiplier"] = min(policy["execution_penalty_multiplier"], 0.8)

    for item in adjustment_items:
        if not isinstance(item, dict):
            continue
        action = str(item.get("action", "") or "").strip().lower()
        if action == "delay_exit_bias":
            policy["delay_exit_bias_active"] = True

    return policy
