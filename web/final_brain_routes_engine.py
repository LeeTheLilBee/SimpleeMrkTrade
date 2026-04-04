from typing import Dict, List

from engine_v2.final_master_brain_engine import build_final_master_brain
from engine_v2.final_brain_live_helpers import (
    build_final_symbol_context,
    build_final_spotlight_context,
    build_final_dashboard_context,
)


def _safe_dict(value) -> Dict:
    return value if isinstance(value, dict) else {}


def _safe_list(value) -> List:
    return value if isinstance(value, list) else []


def build_symbol_final_brain(symbol: str, decision_bundle: Dict) -> Dict:
    symbol = str(symbol or "").upper().strip()
    bundle = _safe_dict(decision_bundle)

    return build_final_master_brain(
        base_decision=_safe_dict(bundle.get("base_decision")),
        base_explainability=_safe_dict(bundle.get("explainability")),
        enhanced_integration=_safe_dict(bundle.get("enhanced")),
        truth_integration=_safe_dict(bundle.get("truth")),
        behavior_intelligence=_safe_dict(bundle.get("behavior")),
        causality_intelligence=_safe_dict(bundle.get("causality")),
        counterfactual_intelligence=_safe_dict(bundle.get("counterfactual")),
    )


def build_all_final_brains(decision_map: Dict[str, Dict]) -> Dict[str, Dict]:
    final_map: Dict[str, Dict] = {}

    if not isinstance(decision_map, dict):
        return final_map

    for symbol, bundle in decision_map.items():
        clean_symbol = str(symbol or "").upper().strip()
        if not clean_symbol:
            continue

        try:
            final_map[clean_symbol] = build_symbol_final_brain(clean_symbol, _safe_dict(bundle))
        except Exception as e:
            print(f"[FINAL_BRAIN_BUILD:{clean_symbol}] {e}")

    return final_map


def build_final_symbol_page_context(symbol: str, decision_bundle: Dict, tier: str = "free") -> Dict:
    clean_symbol = str(symbol or "").upper().strip()
    final_brain = build_symbol_final_brain(clean_symbol, decision_bundle)
    return build_final_symbol_context(
        symbol=clean_symbol,
        final_brain=final_brain,
        tier=str(tier or "free").lower(),
    )


def build_final_spotlight_cards(decision_map: Dict[str, Dict], tier: str = "free") -> List[Dict]:
    final_brain_map = build_all_final_brains(decision_map)
    return build_final_spotlight_context(
        final_brain_map=final_brain_map,
        tier=str(tier or "free").lower(),
    )


def build_final_dashboard_view(decision_map: Dict[str, Dict], tier: str = "free") -> Dict:
    final_brain_map = build_all_final_brains(decision_map)
    return build_final_dashboard_context(
        final_brain_map=final_brain_map,
        tier=str(tier or "free").lower(),
    )


def build_final_all_symbol_cards(decision_map: Dict[str, Dict], tier: str = "free") -> List[Dict]:
    final_brain_map = build_all_final_brains(decision_map)
    cards = build_final_spotlight_context(
        final_brain_map=final_brain_map,
        tier=str(tier or "free").lower(),
    )

    out: List[Dict] = []
    for card in cards:
        clean_card = _safe_dict(card)
        out.append(
            {
                "symbol": clean_card.get("symbol"),
                "title": clean_card.get("title"),
                "subtitle": clean_card.get("subtitle"),
                "action": clean_card.get("action"),
                "confidence": clean_card.get("confidence"),
                "story": clean_card.get("story", ""),
                "highlights": _safe_list(clean_card.get("highlights")),
                "reasons": _safe_list(clean_card.get("reasons")),
                "coaching": clean_card.get("coaching", ""),
            }
        )

    return out
