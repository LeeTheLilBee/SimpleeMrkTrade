from typing import Dict


def build_pressure_visuals(explainability: Dict) -> Dict:
    pressure = explainability.get("pressure", {}) if isinstance(explainability, dict) else {}

    supportive = pressure.get("supportive_pressures", []) if isinstance(pressure.get("supportive_pressures", []), list) else []
    restrictive = pressure.get("restrictive_pressures", []) if isinstance(pressure.get("restrictive_pressures", []), list) else []
    balance = str(pressure.get("pressure_balance", "mixed") or "mixed")

    if balance == "supportive":
        badge = "Supportive Pressure"
    elif balance == "hostile":
        badge = "Hostile Pressure"
    else:
        badge = "Mixed Pressure"

    return {
        "pressure_badge": badge,
        "pressure_balance": balance,
        "support_count": len(supportive),
        "restriction_count": len(restrictive),
    }
