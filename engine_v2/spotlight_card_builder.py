from typing import Dict


def build_spotlight_card(symbol: str, decision: Dict) -> Dict:
    summary = decision.get("summary", {})
    card = decision.get("card", {})
    explainability = decision.get("explainability", {})

    return {
        "symbol": symbol,
        "title": card.get("title", summary.get("verdict", "No verdict")),
        "subtitle": card.get("subtitle", summary.get("command", "No command")),
        "action": card.get("action", summary.get("action", "wait")),
        "confidence": card.get("confidence", summary.get("confidence", "low")),
        "grade": card.get("grade", summary.get("grade", "F")),
        "tone": card.get("tone", summary.get("tone", "neutral")),
        "highlights": card.get("highlights", []),
        "message": explainability.get("message", ""),
        "state": summary.get("state", "neutral"),
        "score": summary.get("score", 0),
    }
