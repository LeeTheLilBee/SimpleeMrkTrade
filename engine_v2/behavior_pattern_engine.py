from typing import Dict


def detect_behavior_pattern(user_state: Dict) -> Dict:
    trade_frequency = int(user_state.get("trades_last_24h", 0) or 0)
    avg_hold_time = float(user_state.get("avg_hold_time", 0) or 0)
    deviation = float(user_state.get("rule_deviation_score", 0) or 0)

    pattern = "stable"
    reason = "behavior is within expected bounds"

    if trade_frequency > 6:
        pattern = "overtrading"
        reason = "too many trades in short time window"
    elif avg_hold_time < 5:
        pattern = "impatience"
        reason = "positions closed too quickly"
    elif deviation > 50:
        pattern = "rule_breaking"
        reason = "user is deviating from system discipline"

    return {
        "behavior_pattern": pattern,
        "behavior_pattern_reason": reason,
    }
