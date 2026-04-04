from typing import Dict

from engine_v2.replay_normalizer import normalize_replay_trade
from engine_v2.replay_brain_runner import build_replay_final_brain
from engine_v2.replay_explainability_runner import build_replay_explainability


def build_trade_replay_package(trade: Dict, decision_bundle: Dict) -> Dict:
    normalized_trade = normalize_replay_trade(trade)
    final_brain = build_replay_final_brain(decision_bundle)
    explainability_bundle = build_replay_explainability(final_brain)

    final_output = final_brain.get("final_output", {}) if isinstance(final_brain.get("final_output", {}), dict) else {}
    final_summary = final_output.get("final_summary", {}) if isinstance(final_output.get("final_summary", {}), dict) else {}
    final_coaching = final_output.get("final_coaching", {}) if isinstance(final_output.get("final_coaching", {}), dict) else {}
    truth_notes = final_output.get("truth_notes", {}) if isinstance(final_output.get("truth_notes", {}), dict) else {}

    return {
        "trade": normalized_trade,
        "final_brain": final_brain,
        "replay_summary": {
            "symbol": normalized_trade.get("symbol", ""),
            "outcome": normalized_trade.get("outcome", "unknown"),
            "pnl": normalized_trade.get("pnl", 0),
            "action": final_summary.get("action", "wait"),
            "confidence": final_summary.get("confidence", "low"),
            "verdict": final_summary.get("verdict", ""),
            "insight": final_summary.get("insight", ""),
            "story": final_summary.get("story", ""),
            "coaching_message": final_coaching.get("final_coaching_message", ""),
            "coaching_tone": final_coaching.get("final_coaching_tone", "neutral"),
            "hard_reject": truth_notes.get("hard_reject", False),
            "hard_reject_reason": truth_notes.get("hard_reject_reason", ""),
        },
        "replay_explainability": explainability_bundle.get("explainability", {}),
        "replay_visuals": explainability_bundle.get("visuals", {}),
    }
