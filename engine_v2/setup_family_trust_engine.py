from typing import Dict


def evaluate_setup_family_trust(setup_type: str, pattern_reputation: Dict) -> Dict:
    family_map = pattern_reputation.get("pattern_reputation", {}) if isinstance(pattern_reputation, dict) else {}
    info = family_map.get(setup_type, {})

    reputation = str(info.get("reputation", "unproven") or "unproven")

    if reputation == "trusted":
        score = 85
        state = "high_trust"
        reason = "this setup family currently deserves strong trust"
    elif reputation == "usable":
        score = 60
        state = "moderate_trust"
        reason = "this setup family remains usable, but not fully trusted"
    elif reputation == "weak":
        score = 35
        state = "low_trust"
        reason = "this setup family is weakening and should be penalized"
    elif reputation == "damaged":
        score = 10
        state = "minimal_trust"
        reason = "this setup family is damaged and should not receive normal conviction"
    else:
        score = 45
        state = "uncertain_trust"
        reason = "this setup family lacks enough evidence for strong trust"

    return {
        "setup_family": setup_type,
        "trust_score": score,
        "trust_state": state,
        "trust_reason": reason,
    }
