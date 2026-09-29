"""Optional, non-authoritative evidence overlays for EXISTING V2 outputs.

This module is a narrow integration seam. It does not run, replace, score or
retrain Equity Engine V2, Options Intelligence, Candidate/Intelligence Fusion
or Soulaana. Existing outputs retain their original decisions and gate flags.
"""
from __future__ import annotations

from typing import Mapping
from copy import deepcopy

from engine.market_intake.contracts import clean_symbol
from engine.market_intake.research_bridge import attach_research_context, project_research

LANES={
    "equity":"equity_engine_v2",
    "options":"options_intelligence",
    "candidate":"candidate_fusion",
    "fusion":"intelligence_fusion_v2",
    "soulaana":"soulaana",
}


def attach_to_engine_output(output:dict, research_record:dict, *, lane:str,
                            symbol:str)->dict:
    """Add a separate descriptive lane only; never replace result fields."""
    if lane not in LANES:raise ValueError("unknown preexisting OB engine")
    symbol=clean_symbol(symbol)
    if not isinstance(output,dict) or research_record.get("symbol") != symbol:
        raise ValueError("independent research identity must match engine output")
    if output.get("symbol") is not None and output["symbol"] != symbol:
        raise ValueError("engine result symbol mismatch")
    if "research_context" in output:
        raise ValueError("existing research context cannot be overwritten")
    return attach_research_context(output,research_record,room=LANES[lane])


def attach_to_v2_universe(universe:dict, research_records:Mapping[str,dict], *,
                          lane:str)->dict:
    """Overlay existing selected/rejected rows by exact symbol, without re-ranking.

    Only equity and options universe views are supported; no persistence, no
    changes to item selection, trade price, score, options chain or mode flags.
    """
    if lane not in {"equity","options"} or not isinstance(universe,dict):
        raise ValueError("equity or options V2 universe expected")
    if not isinstance(research_records,Mapping):
        raise ValueError("research source registry required")
    enriched=deepcopy(universe)
    for key in ("selected","spotlight","rejected"):
        items=enriched.get(key,[])
        if not isinstance(items,list):raise ValueError("V2 universe row list required")
        for index,item in enumerate(items):
            if not isinstance(item,dict):raise ValueError("V2 universe item must be a record")
            symbol=item.get("symbol")
            if symbol not in research_records:continue
            items[index]=attach_to_engine_output(item,research_records[symbol],
                                                 lane=lane,symbol=symbol)
    enriched["research_overlay"]={
        "schema":"OB_ENGINE_RESEARCH_OVERLAY_V1","source_only":True,
        "changes_selection":False,"changes_scores":False,
        "changes_execution_or_capital":False,
    }
    return enriched
