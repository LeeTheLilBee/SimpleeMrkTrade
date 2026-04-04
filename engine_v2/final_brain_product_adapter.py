from typing import Dict, List


def adapt_final_brain_to_symbol_payload(symbol: str, final_brain: Dict) -> Dict:
    final_output = final_brain.get("final_output", {}) if isinstance(final_brain, dict) else {}
    final_summary = final_output.get("final_summary", {}) if isinstance(final_output, dict) else {}
    final_coaching = final_output.get("final_coaching", {}) if isinstance(final_output, dict) else {}
    truth_notes = final_output.get("truth_notes", {}) if isinstance(final_output, dict) else {}
    behavior_notes = final_output.get("behavior_notes", {}) if isinstance(final_output, dict) else {}

    reasons = list(final_summary.get("reasons", []) or [])

    return {
        "symbol": symbol,
        "hero_title": final_summary.get("verdict", "No final verdict available."),
        "hero_subtitle": final_summary.get("insight", "No final insight available."),
        "hero_action": final_summary.get("action", "wait"),
        "hero_confidence": final_summary.get("confidence", "low"),
        "hero_story": final_summary.get("story", ""),
        "hero_reasons": reasons,
        "coaching_message": final_coaching.get("final_coaching_message", ""),
        "coaching_tone": final_coaching.get("final_coaching_tone", "neutral"),
        "hard_reject": truth_notes.get("hard_reject", False),
        "hard_reject_reason": truth_notes.get("hard_reject_reason", ""),
        "behavior_override": behavior_notes.get("behavior_override", {}),
    }


def adapt_final_brain_to_spotlight_card(symbol: str, final_brain: Dict) -> Dict:
    final_output = final_brain.get("final_output", {}) if isinstance(final_brain, dict) else {}
    final_summary = final_output.get("final_summary", {}) if isinstance(final_output, dict) else {}
    final_coaching = final_output.get("final_coaching", {}) if isinstance(final_output, dict) else {}

    reasons = list(final_summary.get("reasons", []) or [])

    if final_summary.get("action") == "reject":
        highlights = ["Rejected by final brain", "Capital protected", "Do not act"]
    elif final_summary.get("action") == "wait":
        highlights = ["Patience required", "Setup not ready", "Stand by"]
    elif final_summary.get("action") == "cautious_act":
        highlights = ["Selective opportunity", "Requires precision", "Controlled execution"]
    else:
        highlights = ["Actionable now", "Final brain approved", "Execute with discipline"]

    return {
        "symbol": symbol,
        "title": final_summary.get("verdict", "No verdict"),
        "subtitle": final_summary.get("insight", "No insight"),
        "action": final_summary.get("action", "wait"),
        "confidence": final_summary.get("confidence", "low"),
        "story": final_summary.get("story", ""),
        "highlights": highlights,
        "reasons": reasons[:3],
        "coaching": final_coaching.get("final_coaching_message", ""),
    }


def adapt_final_brain_to_dashboard_payload(final_brain_map: Dict[str, Dict]) -> Dict:
    if not final_brain_map:
        return {
            "dominant_symbol": None,
            "dashboard_action": "wait",
            "dashboard_verdict": "No final brain output available.",
            "dashboard_insight": "No active final judgment is currently available.",
            "dashboard_story": "",
            "dashboard_coaching": "",
        }

    ranked = sorted(
        final_brain_map.items(),
        key=lambda item: (
            item[1].get("final_output", {}).get("final_summary", {}).get("action") == "act",
            item[1].get("final_output", {}).get("final_summary", {}).get("action") == "cautious_act",
            item[1].get("final_output", {}).get("final_summary", {}).get("confidence") == "high",
        ),
        reverse=True,
    )

    symbol, final_brain = ranked[0]
    final_output = final_brain.get("final_output", {}) if isinstance(final_brain, dict) else {}
    final_summary = final_output.get("final_summary", {}) if isinstance(final_output, dict) else {}
    final_coaching = final_output.get("final_coaching", {}) if isinstance(final_output, dict) else {}

    return {
        "dominant_symbol": symbol,
        "dashboard_action": final_summary.get("action", "wait"),
        "dashboard_verdict": final_summary.get("verdict", "No verdict"),
        "dashboard_insight": final_summary.get("insight", "No insight"),
        "dashboard_story": final_summary.get("story", ""),
        "dashboard_coaching": final_coaching.get("final_coaching_message", ""),
    }
