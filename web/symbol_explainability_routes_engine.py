from typing import Dict

from engine_v2.symbol_explainability_adapter import build_symbol_explainability_context


def build_symbol_page_explainability(final_brain: Dict) -> Dict:
    return build_symbol_explainability_context(final_brain)
