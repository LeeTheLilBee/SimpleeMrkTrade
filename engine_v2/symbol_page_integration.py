"""Existing Symbol Page adapter, with optional source-bound research context.

The legacy decision payload remains unchanged unless a separately reviewed
research record is explicitly supplied. No score/trading-mode mutation.
"""
from typing import Dict

from engine_v2.symbol_page_view_builder import build_symbol_page_view
from engine.market_intake.contracts import clean_symbol
from engine.market_intake.research_bridge import project_research


def build_symbol_page_payload(symbol: str, decision: Dict,
                              research_record: Dict | None = None) -> Dict:
    view = build_symbol_page_view(symbol=symbol, decision=decision)
    if research_record is not None:
        evidence = project_research(research_record, "symbol_page")
        if evidence["symbol"] != clean_symbol(symbol):
            raise ValueError("Symbol Page research cannot cross instrument identities")
        view["research_context"] = evidence
    return view
