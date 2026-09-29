"""Offline operator bridge from verified SEC snapshots to OB Symbol Research.

No network, authentication bypass, quote, broker order, scheduled task or rights
self-approval. Use only a separately reviewed owner-research rights record.
"""
from __future__ import annotations

import argparse
from datetime import datetime,timezone
import json
from pathlib import Path

from engine.market_intake.contracts import SourceRights,clean_symbol,_aware
from engine.market_intake.edgar_cache import checked_cached_research
from engine.market_intake.fundamental_research import FundamentalRights
from engine.market_intake.research_bridge import project_research
from engine.market_intake.universe import (
    parse_nasdaq_directory,parse_sec_ticker_exchange,reconcile_symbol_universe,
)


def _approved_rights(path:Path)->tuple[SourceRights,FundamentalRights]:
    review=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(review,dict) or review.get("scope")!="owner_internal":
        raise ValueError("reviewed owner-internal source use record required")
    event=review.get("event")
    financial=review.get("fundamentals")
    if not isinstance(event,dict) or not isinstance(financial,dict):
        raise ValueError("individual event and financial product reviews required")
    try:
        event_at=datetime.fromisoformat(event["verified_at"].replace("Z","+00:00"))
        financial_at=datetime.fromisoformat(financial["reviewed_at"].replace("Z","+00:00"))
    except (KeyError,TypeError,ValueError) as exc:
        raise ValueError("both signed-off review times require explicit timezone") from exc
    _aware(event_at,"event source review");_aware(financial_at,"fundamentals review")
    if event_at>datetime.now(timezone.utc) or financial_at>datetime.now(timezone.utc):
        raise ValueError("future source approval cannot authorize research")
    if (event.get("internal_research") is not True or
        event.get("automated_non_display") is not True or
        event.get("owner_display") is not True or
        financial.get("internal_research") is not True or
        financial.get("owner_display") is not True):
        raise ValueError("all individual internal/non-display/owner display scopes require true review")
    source=SourceRights("sec-edgar","SEC-EDGAR",event.get("permission_reference",""),
        event_at,internal_research=True,automated_non_display=True,
        owner_display=True,entitled_instruments=frozenset({"event"}))
    financial_source=FundamentalRights("sec-edgar",financial.get("reference",""),
        financial_at,internal_research=True,owner_display=True,
        ai_explanation=financial.get("ai_explanation") is True,
        retention=financial.get("long_term_retention") is True)
    if not source.reviewed_for_scan() or not financial_source.reference.strip():
        raise ValueError("real product-specific review references are required")
    return source,financial_source


def run(*,nasdaq:Path,other:Path,crossref:Path,cache:Path,
        symbol:str,rights_record:Path)->dict[str,object]:
    sym=clean_symbol(symbol)
    at=datetime.now(timezone.utc)
    first=parse_nasdaq_directory(nasdaq.read_text(encoding="utf-8"),
                                 directory="nasdaqlisted.txt",observed_at=at)
    second=parse_nasdaq_directory(other.read_text(encoding="utf-8"),
                                  directory="otherlisted.txt",observed_at=at)
    sec=parse_sec_ticker_exchange(crossref.read_text(encoding="utf-8"))
    universe=reconcile_symbol_universe(first,second,sec)
    if sym not in universe or universe[sym].identity_status!="CROSS_REFERENCED":
        raise ValueError("ticker needs independent listing/SEC CIK identity before EDGAR join")
    event,financial=_approved_rights(rights_record)
    bundle=checked_cached_research(identity=universe[sym],root=cache,
                          event_rights=event,fundamental_rights=financial)
    view=project_research(bundle.owner_snapshot(),"symbol_page")
    # This is a *local* read-only report, never published as canonical live
    # broker price, trade selection or unrestricted invitee display.
    return {"schema":"OB_OWNER_EDGAR_OFFLINE_REPORT_V1",
            "edgar_status":bundle.status(),"symbol_research":view,
            "data_source":"OFFICIAL_SEC_CACHED_REVIEWED",
            "current_quote_available":False,
            "owner_report_not_runtime_feed":True,
            "manual_live_authorized":False,"execution_authorized":False}


def main()->None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nasdaq",required=True,type=Path)
    parser.add_argument("--other",required=True,type=Path)
    parser.add_argument("--crossref",required=True,type=Path)
    parser.add_argument("--cache",required=True,type=Path)
    parser.add_argument("--symbol",required=True)
    parser.add_argument("--rights-review",required=True,type=Path)
    args=parser.parse_args()
    report=run(nasdaq=args.nasdaq,other=args.other,crossref=args.crossref,
               cache=args.cache,symbol=args.symbol,rights_record=args.rights_review)
    print(json.dumps(report,indent=2))


if __name__=="__main__":main()
