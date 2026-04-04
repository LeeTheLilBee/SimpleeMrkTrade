from typing import Dict, List

from engine_v2.final_brain_page_helpers import (
    get_final_symbol_page_context,
    get_final_spotlight_page_context,
    get_final_dashboard_page_context,
)
from engine_v2.final_brain_tier_adapter import (
    adapt_final_symbol_by_tier,
    adapt_final_spotlight_by_tier,
    adapt_final_dashboard_by_tier,
)


def build_final_symbol_context(symbol: str, final_brain: Dict, tier: str = "free") -> Dict:
    if not isinstance(final_brain, dict):
        return {}

    final_output = final_brain.get("final_output", {})
    final_summary = final_output.get("final_summary", {})

    explainability_visuals = build_symbol_explainability_visuals(final_brain)

    return {
        "symbol": symbol,
        "hero_title": final_summary.get("verdict", ""),
        "hero_subtitle": final_summary.get("insight", ""),
        "hero_action": final_summary.get("action", "wait"),
        "hero_confidence": final_summary.get("confidence", "low"),
        "hero_story": final_summary.get("story", ""),
        "hero_reasons": final_summary.get("reasons", []),

        "coaching_message": final_output.get("final_coaching", {}).get("final_coaching_message", ""),
        "coaching_tone": final_output.get("final_coaching", {}).get("final_coaching_tone", "neutral"),

        "hard_reject": final_output.get("truth_notes", {}).get("hard_reject", False),
        "hard_reject_reason": final_output.get("truth_notes", {}).get("hard_reject_reason", ""),

        # 🔥 NEW (SECTION 59)
        "symbol_explainability": explainability_visuals,
    }


def build_final_spotlight_context(final_brain_map: Dict[str, Dict], tier: str = "free") -> List[Dict]:
    payload = get_final_spotlight_page_context(final_brain_map)
    return adapt_final_spotlight_by_tier(payload, tier)


def build_final_dashboard_context(final_brain_map: Dict[str, Dict], tier: str = "free") -> Dict:
    payload = get_final_dashboard_page_context(final_brain_map)
    return adapt_final_dashboard_by_tier(payload, tier)
