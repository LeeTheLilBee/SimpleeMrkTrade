from typing import Dict


def suggest_family_penalties(meta: Dict) -> Dict:
    setup_health = meta.get("setup_family_health", {})
    families = setup_health.get("families", {})

    penalties = {}

    for name, info in families.items():
        state = info.get("state")

        if state == "failing":
            penalties[name] = "heavy_penalty"
        elif state == "weak":
            penalties[name] = "moderate_penalty"
        elif state == "mixed":
            penalties[name] = "light_penalty"

    if not penalties:
        penalties["status"] = "no family penalties suggested"

    return penalties
