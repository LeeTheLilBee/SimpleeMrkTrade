from typing import Dict


def evaluate_integrity(system_state: Dict, portfolio_state: Dict, decision_context: Dict) -> Dict:
    required_keys = ["requested_action", "decision_ready", "capital_action"]
    missing = [k for k in required_keys if k not in decision_context]

    data_ok = bool(system_state.get("data_integrity_ok", True))
    ready = bool(system_state.get("system_ready", True))

    valid = data_ok and ready and not missing

    reasons = []
    if not data_ok:
        reasons.append("data integrity not confirmed")
    if not ready:
        reasons.append("system not ready")
    if missing:
        reasons.append(f"missing decision context keys: {', '.join(missing)}")

    return {
        "integrity_ok": valid,
        "integrity_reasons": reasons if reasons else ["system integrity verified"],
    }
