from typing import Dict


def build_symbol_page_view(symbol: str, decision: Dict) -> Dict:
    summary = decision.get("summary", {})
    explainability = decision.get("explainability", {})
    card = decision.get("card", {})
    explanation = decision.get("explanation", {})

    return {
        "symbol": symbol,
        "hero_title": summary.get("verdict", "No verdict available."),
        "hero_subtitle": summary.get("command", "No command available."),
        "hero_state": summary.get("state", "neutral"),
        "hero_action": summary.get("action", "wait"),
        "hero_confidence": summary.get("confidence", "low"),
        "hero_grade": summary.get("grade", "F"),
        "hero_score": summary.get("score", 0),
        "hero_tone": summary.get("tone", "neutral"),
        "highlights": card.get("highlights", []),
        "message": explainability.get("message", ""),
        "narrative": explainability.get("narrative", ""),
        "reasons": explainability.get("reasons", explanation.get("why", [])),
        "system_flags": decision.get("system_flags", []),
    }
