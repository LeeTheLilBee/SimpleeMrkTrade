from typing import Dict


def suggest_threshold_tuning(meta: Dict, regime: Dict) -> Dict:
    drift = meta.get("drift", {})
    signal_quality = meta.get("signal_quality", {})
    confidence = meta.get("confidence_honesty", {})

    actions = []

    if drift.get("drift_state") in {"soft_drift", "hard_drift"}:
        actions.append("tighten timing threshold")

    if signal_quality.get("signal_quality_state") in {"crowded", "noisy"}:
        actions.append("raise minimum edge requirement")

    if confidence.get("confidence_state") in {"inflated", "dishonest"}:
        actions.append("tighten rejection requirements for high-confidence setups")

    if not actions:
        actions.append("no threshold change suggested")

    return {
        "actions": actions
    }
