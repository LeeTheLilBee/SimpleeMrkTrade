from typing import Dict, List


def build_invalidation(signal: Dict, decision: Dict) -> Dict:
    invalidation: List[str] = []

    trend_strength = float(signal.get("trend_strength", 0) or 0)
    volume_confirmation = float(signal.get("volume_confirmation", 0) or 0)
    extension_score = float(signal.get("extension_score", 0) or 0)
    pullback_quality = float(signal.get("pullback_quality", 0) or 0)
    ready_state = str(decision.get("ready_state", "watch") or "watch")
    direction = str(signal.get("direction", "") or "").upper()
    setup_type = str(signal.get("setup_type", "") or "").lower()

    if ready_state == "reject":
        invalidation.append("setup is already below execution threshold")

    if trend_strength < 45:
        invalidation.append("trend strength is too weak to support continuation")

    if volume_confirmation < 40:
        invalidation.append("volume support is too weak to confirm the move")

    if extension_score > 80 and ready_state in {"ready_now", "ready_soon"}:
        invalidation.append("move is too extended and risks failing without fresh follow-through")

    if pullback_quality < 25 and ready_state == "ready_now":
        invalidation.append("entry quality is fragile and could fail without a cleaner reset")

    if setup_type == "continuation":
        invalidation.append("continuation thesis breaks if momentum no longer follows through")

    if setup_type == "breakout":
        invalidation.append("breakout thesis fails if price cannot hold the breakout zone")

    if direction == "CALL":
        invalidation.append("bullish thesis fails if upside pressure fades and buyers lose control")

    if direction == "PUT":
        invalidation.append("bearish thesis fails if downside pressure fades and sellers lose control")

    # dedupe while preserving order
    seen = set()
    cleaned = []
    for item in invalidation:
        if item not in seen:
            cleaned.append(item)
            seen.add(item)

    return {
        "invalidation": cleaned
    }
