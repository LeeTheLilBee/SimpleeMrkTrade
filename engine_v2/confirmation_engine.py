from typing import Dict, List


def build_confirmations(signal: Dict) -> Dict:
    confirmations: List[str] = []

    if signal.get("trend_strength", 0) > 60:
        confirmations.append("trend continuation remains intact")

    if signal.get("volume_confirmation", 0) > 60:
        confirmations.append("volume supports the move")

    if not confirmations:
        confirmations.append("no strong confirmation signals yet")

    return {
        "confirmations": confirmations
    }
