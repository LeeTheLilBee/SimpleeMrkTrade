"""OBINTEL001-030 offline synthetic-only tests. No market network, API keys or broker."""
from dataclasses import replace
from datetime import datetime, date, timedelta, timezone
from copy import deepcopy
from pathlib import Path
from flask import Flask, render_template

import pytest

from engine.market_intake.contracts import (
    DiscoveryEvent, Observation, ScanContext, SourceRights,
)
from engine.market_intake.adapters import FeedAdapter
from engine.market_intake.gateway import UniversalMarketGateway
from engine.market_intake.historical_research import (
    HistoryRights, CompletedDailyBar, HistorySeries, history_context,
    replay_historical_horizon,
)
from engine.market_intake.fundamental_research import (
    FundamentalRights, parse_companyfacts, fundamental_context,
)
from engine.market_intake.universe import (
    parse_nasdaq_directory, parse_sec_ticker_exchange, reconcile_symbol_universe,
)
from engine.market_intake.symbol_research import (
    SymbolResearchInputs, symbol_research_snapshot,
)
from engine.market_intake.research_bridge import (
    attach_research_context, project_research, ROOMS,
)
from engine.market_intake.research_memory import (
    ResearchReferenceLedger, soulaana_research_brief,
)

NOW=datetime(2026,9,28,15,0,tzinfo=timezone.utc)
CIK="0000000234"
ACC="0000000234-26-000001"


def identity():
    nas=("Symbol|Security Name|Market Category|Test Issue|Financial Status|Round Lot Size|ETF|NextShares\n"
         "XYZ|Synthetic Example Co|Q|N|N|100|N|N\n")
    rows=parse_nasdaq_directory(nas,directory="nasdaqlisted.txt",
                                observed_at=NOW)
    sec='{"fields":["cik","name","ticker","exchange"],"data":[[234,"Synthetic Example Co","XYZ","Nasdaq"]]}'
    return reconcile_symbol_universe(rows,[],parse_sec_ticker_exchange(sec))["XYZ"]


def history(*, ai=True, retention=True, basis="raw"):
    rights=HistoryRights("test-equity-history","TEST_COMMITTED_DAILY","TEST-HISTORY",
                         "reviewed-license-fixture",NOW-timedelta(days=1),
                         research_allowed=True,automated_analysis_allowed=True,
                         owner_display_allowed=True,ai_explanation_allowed=ai,
                         retention_allowed=retention,basis=basis,
                         basis_reference="adjustment-method-proof" if basis!="raw" else "")
    bars=tuple(CompletedDailyBar(
        "XYZ","test-equity-history",NOW.date()-timedelta(days=225-i),
        90+i*.1,92+i*.1,89+i*.1,91+i*.1,1000+i,
        "test-source-completed-bar-"+str(i),basis,True,
    ) for i in range(225))
    return HistorySeries("XYZ",rights,bars,NOW,"verified-snapshot-test-1")


def financial(*, ai=True, retention=True):
    rights=FundamentalRights("sec-edgar","reviewed-test-terms",NOW-timedelta(days=1),
                              internal_research=True,owner_display=True,
                              ai_explanation=ai,retention=retention)
    accepted=NOW-timedelta(days=2)
    raw={"cik":234,"facts":{"us-gaap":{"Assets":{"units":{"USD":[
        {"accn":ACC,"form":"10-Q","end":"2026-06-30","filed":"2026-09-25",
         "val":100000000}
    ]}}}}}
    parsed=parse_companyfacts(raw,cik=CIK,accepted_accessions={ACC:accepted},
                               rights=rights,reviewed_at=NOW)
    return rights,parsed,raw


def issuer_event():
    ev=Observation("SEC:"+ACC,"sec-edgar","SEC-EDGAR","XYZ",
                   NOW-timedelta(minutes=5),NOW-timedelta(minutes=4),
                   "https://www.sec.gov/Archives/edgar/data/234/x",
                   "unknown","event")
    rights=SourceRights("sec-edgar","SEC-EDGAR","reviewed-internal-event-right",
                        NOW-timedelta(hours=1),internal_research=True,
                        automated_non_display=True,owner_display=True,
                        entitled_instruments=frozenset({"event"}))
    return DiscoveryEvent(ev,"filing","SEC 8-K accepted","https://www.sec.gov/test",CIK),rights


def gateway():
    g=UniversalMarketGateway()
    r=SourceRights("test-live-equity","TEST-SIP","test-approved-owner-right",
                   NOW-timedelta(hours=1),internal_research=True,
                   automated_non_display=True,owner_display=True,
                   real_time_entitled=True,entitled_instruments=frozenset({"equity"}))
    fields={k:k for k in ("observation_id","symbol","observed_at",
                         "provenance_reference","last","bid","ask","previous_close",
                         "volume","average_volume")}
    g.install("tradier-equity",rights=r,
              adapter=FeedAdapter(r,fields,"realtime","equity"))
    decision=g.ingest("test-live-equity",{
        "observation_id":"synthetic-1","symbol":"XYZ",
        "observed_at":(NOW-timedelta(seconds=2)).isoformat(),
        "provenance_reference":"synthetic-source-proof",
        "last":100.,"bid":99.8,"ask":100.2,"previous_close":96.,
        "volume":1000,"average_volume":500.},
        received_at=NOW,context=ScanContext(NOW,"REGULAR",True))
    assert decision.stored
    return g


def inputs(*,history_ai=True,facts_ai=True,hist_retention=True):
    hr=history(ai=history_ai,retention=hist_retention)
    fr,facts,_=financial(ai=facts_ai)
    ev,er=issuer_event()
    return SymbolResearchInputs(identity(),NOW,hr,facts,fr,(ev,),{"sec-edgar":er})


def packet(**kwargs):
    return symbol_research_snapshot(inputs(**kwargs),as_of=NOW,gateway=gateway(),
                                    market_context=ScanContext(NOW,"REGULAR",True))


def test_historical_complete_adjustment_rights_dates_and_indicators():
    series=history()
    out=history_context(series,cutoff=NOW)
    assert out["bars_used"]==225
    assert out["observations"]["close_sma_200_sessions"] is not None
    assert out["last_session"]==(NOW.date()-timedelta(days=1)).isoformat()
    assert out["historical_only"] and not out["current_quote_eligible"]
    assert out["history_calendar_completeness"]=="NOT_VERIFIED"
    assert out["ai_explanation_allowed"]
    with pytest.raises(ValueError):
        replace(series.rights,basis="split_adjusted",basis_reference="")
    with pytest.raises(ValueError):
        HistorySeries(series.symbol,replace(series.rights,research_allowed=False),
                      series.bars,NOW,series.snapshot_reference)
    with pytest.raises(ValueError):
        CompletedDailyBar("XYZ","test-equity-history",NOW.date(),101,100,99,100,
                          100,"test","raw",True)
    with pytest.raises(ValueError):
        HistorySeries("XYZ",series.rights,series.bars+(series.bars[-1],),NOW,"test")
    with pytest.raises(ValueError):
        HistorySeries("XYZ",series.rights,tuple(reversed(series.bars)),NOW,"test")


def test_historical_replay_separates_formation_and_future_outcome():
    series=history()
    cutoff=NOW.date()-timedelta(days=8)
    out=replay_historical_horizon(series,as_of_session=cutoff,horizon_sessions=5)
    assert out["state"]=="RETROSPECTIVE_OBSERVATION"
    assert out["formation"]["last_session"]==cutoff.isoformat()
    assert out["outcome"]["last_session"]>cutoff.isoformat()
    assert out["trade_count"] is None and out["strategy_pnl"] is None
    assert out["live_signal"] is False and out["options_backtest"] is False
    changed=list(series.bars)
    # Editing only the later outcome must not change the earlier formation.
    idx=next(i for i,b in enumerate(changed) if b.session_date>cutoff)
    changed[idx]=replace(changed[idx],close=changed[idx].close+1)
    revised=replace(series,bars=tuple(changed))
    altered=replay_historical_horizon(revised,as_of_session=cutoff,horizon_sessions=5)
    assert altered["formation"]==out["formation"]
    assert replay_historical_horizon(series,as_of_session=NOW.date(),
                                     horizon_sessions=5)["state"]=="INSUFFICIENT_HISTORY"


def test_companyfacts_exact_cik_acceptance_and_retrospective_cutoff():
    r,rows,raw=financial()
    assert len(rows)==1 and rows[0].cik==CIK
    assert rows[0].value==100000000
    current=fundamental_context(cik=CIK,facts=rows,rights=r,as_of=NOW)
    assert current["reported_concepts"][0]["accepted_at"]==rows[0].accepted_at.isoformat()
    assert current["quote_eligible"] is False and current["execution_authorized"] is False
    with pytest.raises(ValueError):
        fundamental_context(cik=CIK,facts=rows,rights=r,as_of=NOW-timedelta(days=3))


def test_companyfacts_year_end_comparisons_are_exact_concept_and_retro_only():
    rights,_,_=financial()
    earlier="0000000234-25-000002"
    later="0000000234-26-000003"
    raw={"cik":234,"facts":{"us-gaap":{"Assets":{"units":{"USD":[
        {"accn":earlier,"form":"10-K","end":"2024-12-31","filed":"2025-02-01","val":80},
        {"accn":later,"form":"10-K","end":"2025-12-31","filed":"2026-02-02","val":100},
        {"accn":ACC,"form":"10-Q","end":"2026-06-30","filed":"2026-09-25","val":110},
    ]}}}}}
    facts=parse_companyfacts(raw,cik=CIK,accepted_accessions={
        earlier:datetime(2025,2,2,tzinfo=timezone.utc),
        later:datetime(2026,2,3,tzinfo=timezone.utc),
        ACC:NOW-timedelta(days=2)},rights=rights,reviewed_at=NOW)
    context=fundamental_context(cik=CIK,facts=facts,rights=rights,as_of=NOW)
    assert context["reported_concepts"][0]["value"]==110.0
    trend=context["year_end_balance_sheet_comparisons"]
    assert len(trend)==1 and trend[0]["concept"]=="Assets"
    assert trend[0]["reported_change_pct"]==25.0
    assert trend[0]["earlier_source"].startswith("https://www.sec.gov/")
    assert trend[0]["retrospective_only"] and not context["execution_authorized"]
    truncated=fundamental_context(cik=CIK,facts=facts,rights=rights,
                                   as_of=NOW-timedelta(days=1))
    earlier_trend=truncated["year_end_balance_sheet_comparisons"]
    assert len(earlier_trend)==1 and earlier_trend[0]["reported_change_pct"]==25.0
    assert earlier_trend[0]["revisions_as_of"] != trend[0]["revisions_as_of"]


def test_companyfacts_reject_missing_acceptance_future_facts_and_wrong_cik():
    r,rows,raw=financial()
    assert parse_companyfacts(raw,cik=CIK,accepted_accessions={},
                              rights=r,reviewed_at=NOW)==()
    assert parse_companyfacts(raw,cik=CIK,accepted_accessions={
        ACC:NOW+timedelta(hours=1)},rights=r,reviewed_at=NOW)==()
    with pytest.raises(ValueError):
        parse_companyfacts(raw,cik="0000000235",accepted_accessions={ACC:NOW},
                           rights=r,reviewed_at=NOW)
    with pytest.raises(ValueError):
        parse_companyfacts(raw,cik=CIK,accepted_accessions={ACC:NOW},
                           rights=replace(r,internal_research=False),reviewed_at=NOW)


def test_record_carries_independent_evidence_and_zero_authority():
    view=packet()
    assert view["identity"]["cik"]==CIK
    assert view["historical"]["bars_used"]==225
    assert view["fundamentals"]["reported_concepts"][0]["concept"]=="Assets"
    assert len(view["issuer_events"])==1
    assert view["scanner"]["equity_sources"]==["test-live-equity"]
    assert not view["manual_live_authorized"] and not view["execution_authorized"]
    assert not view["candidate_admitted"] and not view["broker_quote_verified"]
    assert "market_quotes" not in view


def test_future_identity_and_history_not_recast_as_old_live_truth():
    raw=inputs()
    old=NOW-timedelta(days=5)
    view=symbol_research_snapshot(raw,as_of=old,gateway=gateway(),
                                  market_context=ScanContext(old,"REGULAR",True))
    assert view["state"]=="IDENTITY_HOLD"
    assert view["historical"]["state"]=="NOT_AVAILABLE"
    assert view["scanner"]["state"]=="NOT_CONNECTED"
    with pytest.raises(ValueError):
        symbol_research_snapshot(raw,as_of=NOW+timedelta(minutes=1))


def test_record_mismatched_cik_and_future_event_fail_closed():
    raw=inputs()
    with pytest.raises(ValueError):
        replace(raw,financial_facts=(replace(raw.financial_facts[0],cik="0000000555"),))
    with pytest.raises(ValueError):
        replace(raw,issuer_events=(replace(raw.issuer_events[0],
            evidence=replace(raw.issuer_events[0].evidence,
                              observed_at=NOW+timedelta(hours=1))),))


def test_all_engine_room_adapters_preserve_original_decisions():
    raw=packet()
    original={"score":88,"decision":{"action":"hold"},"execution":{"eligible":False}}
    for room in ROOMS:
        enriched=attach_research_context(original,raw,room=room)
        assert enriched["research_context"]["room"]==room
        assert enriched["score"]==88 and enriched["decision"]["action"]=="hold"
        assert enriched["research_context"]["may_authorize_candidate"] is False
        assert enriched["research_context"]["may_authorize_order"] is False
        assert enriched["research_context"]["may_change_existing_engine_scores"] is False
    assert "research_context" not in original
    with pytest.raises(ValueError):
        attach_research_context({"research_context":{}},raw,room="symbol_page")


def test_existing_v2_symbol_and_universe_adapters_are_optional_and_nonpromoting():
    from engine_v2.symbol_page_integration import build_symbol_page_payload
    from engine_v2.research_context_adapter import attach_to_engine_output, attach_to_v2_universe
    research=packet()
    original={"summary":{"verdict":"Review only","score":12,"action":"wait"}}
    plain=build_symbol_page_payload("XYZ",original)
    enhanced=build_symbol_page_payload("XYZ",original,research_record=research)
    assert "research_context" not in plain
    assert enhanced["hero_score"]==plain["hero_score"]
    assert enhanced["research_context"]["may_authorize_order"] is False
    with pytest.raises(ValueError):
        build_symbol_page_payload("ABC",original,research_record=research)
    base={"symbol":"XYZ","score":88,"execution":{"eligible":False}}
    overlay=attach_to_engine_output(base,research,lane="equity",symbol="XYZ")
    assert overlay["score"]==88 and overlay["execution"]==base["execution"]
    assert "research_context" not in base
    old={"selected":[base],"spotlight":[base],"rejected":[],"meta":{"selected_count":1}}
    new=attach_to_v2_universe(old,{"XYZ":research},lane="equity")
    assert new["selected"][0]["research_context"]["room"]=="equity_engine_v2"
    assert new["meta"]==old["meta"] and old["selected"][0]==base
    assert not new["research_overlay"]["changes_selection"]
    with pytest.raises(ValueError):
        attach_to_engine_output({"symbol":"BAD"},research,lane="equity",symbol="XYZ")


def test_market_map_and_soulaana_cannot_take_unlicensed_numeric_evidence():
    p=packet(history_ai=False,facts_ai=False)
    sky=project_research(p,"market_map")
    assert sky["history"]["observations"]=={}
    assert sky["fundamentals"]["reported_concepts"]==[]
    soulaana=project_research(p,"soulaana")
    assert soulaana["history"]["observations"]=={}
    assert soulaana["fundamentals"]["reported_concepts"]==[]
    brief=soulaana_research_brief(p)
    assert "AI-use" in " ".join(brief["statements"])
    assert not brief["can_authorize_trading"]


def test_tampered_input_rejected_without_lifting_mode_gates():
    raw=packet()
    for key,value in (("execution_authorized",True),("broker_quote_verified",True),
                      ("history_is_not_a_live_quote",False)):
        with pytest.raises(ValueError):
            project_research({**raw,key:value},"symbol_page")
    with pytest.raises(ValueError):
        project_research({**raw,"current_price":102.},"symbol_page")
    with pytest.raises(ValueError):
        project_research(raw,"invented-room")


def test_transient_reference_ledger_requires_retention_and_monotonicity():
    ledger=ResearchReferenceLedger()
    no=inputs(hist_retention=False)
    with pytest.raises(ValueError):
        ledger.append(no,receipt_id="one")
    approved=inputs()
    item=ledger.append(approved,receipt_id="one")
    assert item.can_authorize_order is False
    assert "test-equity-history" not in str(item)
    assert item.evidence_digest and ledger.get("one")==item
    with pytest.raises(ValueError):
        ledger.append(approved,receipt_id="one")
    with pytest.raises(ValueError):
        ledger.append(approved,receipt_id="two")
    ledger.forget_runtime()
    assert ledger.get("one") is None

def test_four_protected_room_templates_only_offer_server_bound_context():
    root=Path("web/templates")
    app=Flask("source_research_test",template_folder=str(root.resolve()))
    expected={
        "symbol_page.html":"symbol_page",
        "market_map.html":"market_map",
        "trade_center.html":"trade_center",
        "review_center.html":"review_center",
    }
    for name,room in expected.items():
        template=(root/name).read_text()
        app.jinja_env.parse(template)
        assert "ob_research_context_partial.html" in template
        assert "ob_research_context.get('room') == '"+room+"'" in template
        assert "ob_research_context.css" in template
        assert "fetch(" not in (root/"ob_research_context_partial.html").read_text()
    with app.test_request_context():
        blank=render_template("ob_research_context_partial.html")
        assert "Symbol research context" not in blank
        view=project_research(packet(),"symbol_page")
        rendered=render_template("ob_research_context_partial.html",ob_research_context=view)
        assert "Symbol research context" in rendered and "SOURCE-BOUND" in rendered
        assert "No broker execution" not in rendered # no new action button
        malicious=deepcopy(view)
        malicious["identity"]["security_name"]="<script>alert(1)</script>"
        safe=render_template("ob_research_context_partial.html",ob_research_context=malicious)
        assert "<script>alert(1)</script>" not in safe
        assert "&lt;script&gt;" in safe


def test_soulaana_does_not_infer_ai_rights_from_human_owner_display():
    # SourceRights currently has owner/invitee display but NO distinct event or
    # quote-source AI-use grant. The owner packet may be rich while the AI
    # projection must not inherit its protected issuer text or provider IDs.
    owner=packet()
    assert owner["issuer_events"] and owner["scanner"]["equity_sources"]
    view=project_research(owner,"soulaana")
    assert view["issuer_events"]==[]
    assert view["market_sources"]["equity_sources"]==[]
    assert view["market_sources"]["option_sources"]==[]
    assert view["market_sources"]["scanner_state"]=="AI_SOURCE_RIGHTS_HOLD"
    brief=soulaana_research_brief(owner)
    assert brief["source_event_references"]==[]
    assert any("AI-use rights" in s for s in brief["statements"])
    assert not brief["can_authorize_trading"]


def test_soulaana_history_without_ai_grant_hides_counts_dates_and_references():
    owner=packet(history_ai=False)
    assert owner["historical"]["bars_used"]>0
    view=project_research(owner,"soulaana")
    assert view["history"]=={
        "state":"EXPLANATION_RIGHTS_HOLD","historical_only":True,
        "live_quote":False,"observations":{},
    }
    brief=soulaana_research_brief(owner)
    assert brief["historical_source_reference"] is None
    assert brief["source_event_references"]==[]
    assert "verified-snapshot-test-1" not in str(brief)
