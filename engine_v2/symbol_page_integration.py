from typing import Dict
from engine_v2.symbol_page_view_builder import build_symbol_page_view


def build_symbol_page_payload(symbol: str, decision: Dict) -> Dict:
    return build_symbol_page_view(symbol=symbol, decision=decision)
