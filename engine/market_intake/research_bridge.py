"""OBINTEL023-027: sanctioned, read-only research-to-room/engine handoff.

No old engine is overwritten and no existing score, candidate, option chain,
execution decision, cash or permission is derived from historical context. The
payload is descriptive and must pass the existing independent authority chain
before any other use.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from math import isfinite
from typing import Mapping

from .contracts import clean_symbol

ROOMS={"market_map","symbol_page","trade_center","review_center",
       "equity_engine_v2","options_intelligence","candidate_fusion",
       "intelligence_fusion_v2","soulaana"}
FORBIDDEN_INPUT={"current_price","quote","options_chain","positions",
                 "signal","trading_signal","order","recommendation",
                 "broker_quote","execution","capital_available"}


def _verified_packet(packet:Mapping[str,object])->None:
    if not isinstance(packet,dict) or packet.get("schema")!="OB_SYMBOL_RESEARCH_RECORD_V1":
        raise ValueError("canonical source-bound research record required")
    if any(packet.get(flag) is not False for flag in (
        "candidate_admitted","manual_live_authorized","broker_quote_verified",
        "execution_authorized","capital_authority")):
        raise ValueError("research cannot carry trading authority")
    if packet.get("context_only") is not True or packet.get("history_is_not_a_live_quote") is not True:
        raise ValueError("historical source boundary is missing")
    clean_symbol(packet.get("symbol",""))
    stamp=datetime.fromisoformat(str(packet.get("as_of","")).replace("Z","+00:00"))
    if stamp.tzinfo is None or stamp.utcoffset() is None:
        raise ValueError("source research timestamp requires UTC offset")
    if not isinstance(packet.get("identity"),dict) or not isinstance(packet.get("historical"),dict) or (
        not isinstance(packet.get("fundamentals"),dict)) or not isinstance(packet.get("scanner"),dict):
        raise ValueError("research evidence segments required")
    if any(name in packet for name in FORBIDDEN_INPUT):
        raise ValueError("trade/quote-capable payload cannot be supplied as research record")


def _history_summary(item:dict)->dict:
    observations=item.get("observations",{})
    if not isinstance(observations,dict):observations={}
    safe={}
    for key in ("close_sma_20_sessions","close_sma_50_sessions","close_sma_200_sessions",
                "last_completed_close","last_completed_volume","sample_start_to_end_pct"):
        value=observations.get(key)
        safe[key]=value if (type(value) in {int,float} and isfinite(value)) else None
    return {"state":item.get("state","NOT_AVAILABLE"),
            "basis":item.get("basis"),"bars_used":item.get("bars_used"),
            "first_session":item.get("first_session"),"last_session":item.get("last_session"),
            "source_id":item.get("source_id"),"snapshot_reference":item.get("snapshot_reference"),
            "history_calendar_completeness":item.get("history_calendar_completeness","NOT_VERIFIED"),
            "observations":safe if item.get("state")=="SOURCE_BOUND_HISTORY" else {},
            "historical_only":True,"live_quote":False}


def _fundamentals_summary(item:dict, *, soulaana:bool)->dict:
    state=item.get("state","NOT_AVAILABLE")
    if soulaana and item.get("ai_explanation_allowed") is not True:
        return {"state":"EXPLANATION_RIGHTS_HOLD","reported_concepts":[],
                "year_end_balance_sheet_comparisons":[]}
    rows=item.get("reported_concepts",[])
    allowed=("concept","value","units","fiscal_end","accepted_at","accession","form","reference")
    safe=[{key:row[key] for key in allowed if key in row} for row in rows[:8]
          if isinstance(row,dict)] if isinstance(rows,list) else []
    comparisons=item.get("year_end_balance_sheet_comparisons",[])
    comparison_keys=("concept","unit","earlier_fiscal_end","later_fiscal_end",
                     "earlier_value","later_value","reported_change_pct",
                     "earlier_source","later_source","retrospective_only")
    allowed_comparisons=[{k:r[k] for k in comparison_keys if k in r}
                         for r in comparisons[:4] if isinstance(r,dict)] if isinstance(comparisons,list) else []
    return {"state":state,"reported_concepts":safe,
            "year_end_balance_sheet_comparisons":allowed_comparisons,
            "raw_concepts_not_normalized":True,"quote_eligible":False}


def project_research(packet:dict, room:str)->dict[str,object]:
    _verified_packet(packet)
    if room not in ROOMS:raise ValueError("unmapped research consumer")
    history=_history_summary(packet["historical"])
    facts=_fundamentals_summary(packet["fundamentals"],soulaana=room=="soulaana")
    events=[{k:e.get(k) for k in ("kind","source_id","accepted_at","headline","reference")
             if k in e} for e in packet.get("issuer_events",[])[:6] if isinstance(e,dict)]
    scanner=packet["scanner"]
    source_ids=[x for x in scanner.get("equity_sources",[])[:8] if isinstance(x,str)]
    option_ids=[x for x in scanner.get("option_sources",[])[:8] if isinstance(x,str)]
    state=packet["state"]
    notes=[]
    if state=="IDENTITY_HOLD":notes.append("Directory identity is not proven at this research cutoff.")
    if history["state"]!="SOURCE_BOUND_HISTORY":notes.append("Approved completed daily-price history is unavailable.")
    if facts["state"] not in {"SOURCE_BOUND","EXPLANATION_RIGHTS_HOLD"}:
        notes.append("Issuer financial evidence is missing or cannot be displayed.")
    if not source_ids:notes.append("No source-authorized current underlying is recorded for this research context.")
    if scanner.get("state")=="CONFLICT_HOLD":notes.append("Independent live sources disagree; the scanner holds.")
    if not notes:notes.append("This is context for review, not a trade admission or prediction.")
    result={
        "schema":"OB_RESEARCH_HANDOFF_V1","room":room,"symbol":packet["symbol"],
        "as_of":packet["as_of"],"state":state,
        "identity":{k:packet["identity"].get(k) for k in (
            "symbol","security_name","exchange_code","cik","identity_status")},
        "history":history,"fundamentals":facts,
        "issuer_events":events,
        "market_sources":{"scanner_state":scanner.get("state","NOT_CONNECTED"),
                          "equity_sources":source_ids,"option_sources":option_ids,
                          "broker_quote_verified":False},
        "soulaana_context":{"what_is_known":(
            "Historical observations and original evidence are shown only where independently licensed."),
            "what_is_missing":" ".join(notes),
            "next_step":("Open source references and independent canonical evidence review; "
                         "do not infer execution permission from this research.")},
        "context_only":True,"historical_not_live":True,
        "may_authorize_candidate":False,"may_authorize_order":False,
        "may_authorize_capital":False,"may_change_existing_engine_scores":False,
        "source_admission_still_required":True,
    }
    if room=="market_map":
        # Market sky gets a bounded spotlight, not a shadow live price board.
        result["history"]["observations"]={}
        result["fundamentals"]["reported_concepts"]=[]
        result["fundamentals"]["year_end_balance_sheet_comparisons"]=[]
    if room=="soulaana":
        # Never pass history numeric content to an assistant absent AI-use rights.
        # HistoryRights AI permission is represented by explicit record field.
        if packet["historical"].get("ai_explanation_allowed") is not True:
            result["history"]["observations"]={}
            result["history"]["state"]="EXPLANATION_RIGHTS_HOLD"
    if room in {"trade_center","review_center","equity_engine_v2",
                "options_intelligence","candidate_fusion","intelligence_fusion_v2"}:
        result["admission_lane"]="RESEARCH_CONTEXT_ONLY"
    return result


def attach_research_context(existing:dict, packet:dict, *, room:str)->dict:
    """Add one separately named evidence lane; preserve old decision and fields."""
    if not isinstance(existing,dict) or "research_context" in existing:
        raise ValueError("existing engine envelope required; replacement needs explicit review")
    enriched=deepcopy(existing)
    enriched["research_context"]=project_research(packet,room)
    return enriched
