from typing import Dict


def evaluate_kill_switch(system_state: Dict, portfolio_state: Dict) -> Dict:
    data_ok = bool(system_state.get("data_integrity_ok", True))
    broker_ok = bool(system_state.get("broker_connection_ok", True))
    execution_errors = int(system_state.get("execution_error_count", 0) or 0)
    stress_state = str(portfolio_state.get("stress_state", "low") or "low")

    active = False
    reasons = []

    if not data_ok:
        active = True
        reasons.append("data_integrity_failure")

    if not broker_ok:
        active = True
        reasons.append("broker_connection_failure")

    if execution_errors >= 3:
        active = True
        reasons.append("excess_execution_errors")

    if stress_state == "critical":
        active = True
        reasons.append("critical_portfolio_stress")

    return {
        "kill_switch_active": active,
        "kill_switch_reasons": reasons,
    }
