from typing import Dict


def build_dashboard_command_view(symbol: str, decision: Dict) -> Dict:
    summary = decision.get("summary", {})
    explainability = decision.get("explainability", {})

    return {
        "dominant_symbol": symbol,
        "posture": summary.get("action", "wait"),
        "verdict": summary.get("verdict", "No verdict available."),
        "command": summary.get("command", "No command available."),
        "confidence": summary.get("confidence", "low"),
        "grade": summary.get("grade", "F"),
        "score": summary.get("score", 0),
        "message": explainability.get("message", ""),
        "narrative": explainability.get("narrative", ""),
    }
