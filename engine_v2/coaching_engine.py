from typing import Dict


def generate_coaching(
    emotional_bias: Dict,
    behavior_pattern: Dict,
    risk_discipline: Dict,
) -> Dict:
    bias = emotional_bias.get("emotional_bias")
    behavior = behavior_pattern.get("behavior_pattern")
    discipline = risk_discipline.get("risk_discipline")

    message = "Stay disciplined and follow the system."
    tone = "neutral"

    if bias == "revenge_trading_risk":
        message = "You’re pressing after losses. Slow down."
        tone = "warning"
    elif bias == "overconfidence_risk":
        message = "You’re hot, but don’t get sloppy."
        tone = "caution"
    elif bias == "hesitation_conflict":
        message = "This is a valid setup. Trust your system."
        tone = "encourage"
    elif bias == "forcing_trades":
        message = "You’re trying to force opportunity. Stand down."
        tone = "warning"

    if behavior == "overtrading":
        message = "You’re overtrading. Quality over quantity."
    elif behavior == "rule_breaking":
        message = "You’re breaking your own rules. Reset."
    
    if discipline == "overrisking":
        message = "You’re risking too much. Protect capital."
    elif discipline == "undisciplined_entry":
        message = "Low confidence is not for execution."

    return {
        "coaching_message": message,
        "coaching_tone": tone,
    }
