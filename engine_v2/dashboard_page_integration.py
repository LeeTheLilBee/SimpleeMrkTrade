from typing import Dict, Optional
from engine_v2.dashboard_command_view_builder import build_dashboard_command_view


def build_dashboard_page_payload(decision_map: Dict[str, Dict]) -> Dict:
    if not decision_map:
        return {
            "dominant_symbol": None,
            "posture": "wait",
            "verdict": "No active decisions available.",
            "command": "Stand by.",
            "confidence": "none",
            "grade": "F",
            "score": 0,
            "message": "No explainability available.",
            "narrative": "No active opportunities are currently being evaluated.",
        }

    ranked = sorted(
        decision_map.items(),
        key=lambda item: (
            item[1].get("summary", {}).get("action") == "act",
            item[1].get("summary", {}).get("confidence") == "high",
            item[1].get("summary", {}).get("grade") == "A",
            item[1].get("summary", {}).get("score", 0),
        ),
        reverse=True,
    )

    symbol, decision = ranked[0]
    return build_dashboard_command_view(symbol=symbol, decision=decision)
