from typing import Dict


def build_replay_card(replay_package: Dict) -> Dict:
    if not isinstance(replay_package, dict):
        return {}

    trade = replay_package.get("trade", {})
    summary = replay_package.get("replay_summary", {})
    visuals = replay_package.get("replay_visuals", {})

    symbol = trade.get("symbol", "")
    outcome = trade.get("outcome", "unknown")
    pnl = trade.get("pnl", 0)

    verdict = summary.get("verdict", "")
    insight = summary.get("insight", "")
    action = summary.get("action", "wait")
    confidence = summary.get("confidence", "low")

    tone = visuals.get("explainability_tone", "neutral")
    pressure = visuals.get("pressure_badge", "Neutral")

    return {
        "symbol": symbol,
        "title": verdict,
        "subtitle": insight,
        "action": action,
        "confidence": confidence,
        "outcome": outcome,
        "pnl": pnl,
        "tone": tone,
        "pressure": pressure,
        "summary_line": visuals.get("summary_line", ""),
        "story": visuals.get("story", ""),
        "coaching": summary.get("coaching_message", ""),
    }
