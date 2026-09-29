"""OBSCAN001–025: offline, no paid resources, no broker/order paths."""
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import tempfile

import pytest

from engine.market_intake import (
    BOUNDARIES, FeedAdapter, IngressRegistry, DiscoveryEvent, EquityQuote, Gate, Observation, OptionQuote,
    ProviderBudget, ScanContext, ScanPolicy, SourceRights, TrafficPlanner,
    assess, diff_directory, directory_snapshot, inspect_symbol,
    parse_nasdaq_directory, parse_sec_ticker_exchange, reconcile_symbol_universe,
    research_packet,
)
from engine.market_intake.local_catalog import run

NOW = datetime(2026, 9, 28, 15, 0, tzinfo=timezone.utc)
CONTEXT = ScanContext(NOW, "REGULAR", True)
A = SourceRights("vendor-a", "SIP", "approved-internal-entitlement-123", NOW,
                 internal_research=True, automated_non_display=True,
                 owner_display=True, real_time_entitled=True,
                 entitled_instruments=frozenset({"equity", "option"}))
B = SourceRights("vendor-b", "DIRECT", "approved-internal-entitlement-456", NOW,
                 internal_research=True, automated_non_display=True,
                 owner_display=True, real_time_entitled=True,
                 entitled_instruments=frozenset({"equity", "option"}))
DUP = SourceRights("vendor-mirror", "SIP", "approved-internal-entitlement-789", NOW,
                   internal_research=True, automated_non_display=True, real_time_entitled=True,
                   entitled_instruments=frozenset({"equity", "option"}))
EVENT_RIGHTS = SourceRights("public-filings", "SEC", "reviewed-terms", NOW,
                            internal_research=True, automated_non_display=True,
                            entitled_instruments=frozenset({"event"}))
RIGHTS = {x.source_id: x for x in (A, B, DUP, EVENT_RIGHTS)}
NAS = "Symbol|Security Name|Market Category|Test Issue|Financial Status|Round Lot Size|ETF|NextShares\nXYZ|Example Co|Q|N|N|100|N|N\nTEST|Test Co|Q|Y|N|100|N|N\nFile Creation Time: 092820261100|||\n"
OTHER = "ACT Symbol|Security Name|Exchange|CQS Symbol|ETF|Round Lot Size|Test Issue|NASDAQ Symbol\nDEF|Example Two|N|DEF|N|100|N|DEF\n"
SEC = json.dumps({"fields":["cik","name","ticker","exchange"],
                  "data":[[234,"Example Co","XYZ","Nasdaq"],[235,"Example Two","DEF","NYSE"],
                          [999,"Only SEC","NOTLISTED","Nasdaq"]]})


def universe():
    n = parse_nasdaq_directory(NAS,directory="nasdaqlisted.txt",observed_at=NOW)
    o = parse_nasdaq_directory(OTHER,directory="otherlisted.txt",observed_at=NOW)
    return reconcile_symbol_universe(n,o,parse_sec_ticker_exchange(SEC))


def obs(source="vendor-a", symbol="XYZ", kind="equity", age=1, family="SIP",
        label="realtime", observation_id="q1"):
    return Observation(observation_id,source,family,symbol,NOW-timedelta(seconds=age),
                       NOW-timedelta(seconds=max(age-0.2,0)),
                       "test-local-fixture-only",label,kind)


def equity(e=None, **fields):
    return EquityQuote(e or obs(), fields.get("last",100.0),fields.get("bid",99.9),
                       fields.get("ask",100.1), fields.get("previous_close",96.0),
                       fields.get("volume",2000),fields.get("average_volume",1000.0))


def opt(e=None, **fields):
    return OptionQuote(e or obs(kind="option"),"XYZ","XYZ   261002C00100000",
                       fields.get("bid",1.0),fields.get("ask",1.2),100.0,
                       "2026-10-02","call",fields.get("open_interest",100),
                       fields.get("volume",10))


def event(e=None, cik="0000000234"):
    return DiscoveryEvent(e or obs(source="public-filings",kind="event",
                                  family="SEC",observation_id="form8k",label="unknown"),
                          "filing","Issuer filing","https://www.sec.gov/test",issuer_cik=cik)


def test_universe_directory_and_sec_crossref_never_prove_quotes():
    u=universe()
    assert sorted(u)==["DEF","XYZ"]
    assert u["XYZ"].sec_cik=="0000000234"
    assert u["XYZ"].identity_status=="CROSS_REFERENCED"
    assert u["DEF"].exchange=="N"
    assert directory_snapshot(u)["current_price_provided"] is False
    assert directory_snapshot(u)["option_contract_prices_provided"] is False
    assert "NOTLISTED" not in u


def test_catalog_snapshot_can_run_offline_without_mutating_active_universe():
    with tempfile.TemporaryDirectory() as temp:
        root=Path(temp)
        (root/"nasdaqlisted.txt").write_text(NAS)
        (root/"otherlisted.txt").write_text(OTHER)
        (root/"company_tickers_exchange.json").write_text(SEC)
        report=run(root/"nasdaqlisted.txt",root/"otherlisted.txt",root/"company_tickers_exchange.json")
        assert report["symbols"]==2
        assert report["not_promoted_to_active_ob_engine"]
        assert report["source_license_review_required"]


def test_directory_rejects_bad_headers_flags_collisions_and_mismatch():
    with pytest.raises(ValueError):
        parse_nasdaq_directory(OTHER,directory="nasdaqlisted.txt",observed_at=NOW)
    with pytest.raises(ValueError):
        parse_nasdaq_directory(NAS.replace("|N|N|100","|Z|N|100"),directory="nasdaqlisted.txt",observed_at=NOW)
    with pytest.raises(ValueError):
        reconcile_symbol_universe([universe()["XYZ"]],[universe()["XYZ"]])
    with pytest.raises(ValueError):
        parse_sec_ticker_exchange('{"fields":["ticker"],"data":[]}')
    with pytest.raises(ValueError):
        parse_nasdaq_directory(NAS,directory="other.txt",observed_at=NOW)


def test_directory_diff_is_not_automatic_delisting():
    old=universe()
    newer={k:v for k,v in old.items() if k!="XYZ"}
    assert diff_directory(old,newer)["not_in_latest_file"]==("XYZ",)
    assert "newly_seen" in diff_directory(old,newer)


def test_data_rights_default_deny_and_two_distinct_entitlements():
    assert assess(obs(), None, CONTEXT).gate==Gate.SOURCE_HOLD
    assert assess(obs(), SourceRights("vendor-a","SIP"), CONTEXT).gate==Gate.RIGHTS_HOLD
    assert assess(obs(), replace(A, real_time_entitled=False), CONTEXT).gate==Gate.RIGHTS_HOLD
    assert assess(obs(label="delayed"),A,CONTEXT).gate==Gate.RIGHTS_HOLD
    assert assess(obs(family="different"),A,CONTEXT).gate==Gate.SOURCE_HOLD
    ok=assess(obs(),A,CONTEXT)
    assert ok.gate==Gate.CURRENT_RESEARCH and ok.display_to_owner and not ok.execution_authority
    assert not ok.display_to_invitees


def test_equity_rights_do_not_authorize_option_data_or_adapters():
    equities_only = replace(A, entitled_instruments=frozenset({"equity"}))
    assert assess(obs(kind="equity"),equities_only,CONTEXT).gate==Gate.CURRENT_RESEARCH
    assert assess(obs(kind="option"),equities_only,CONTEXT).gate==Gate.RIGHTS_HOLD
    rights={**RIGHTS,"vendor-a":equities_only}
    lead=inspect_symbol("XYZ",universe=universe(),equities=[equity()],options=[opt()],
                        rights=rights,context=CONTEXT)
    assert lead.option_source_ids==()
    mapping={x:x for x in ("observation_id","underlying","occ_symbol","observed_at",
                           "provenance_reference","bid","ask","strike","expiry","right")}
    with pytest.raises(ValueError):
        FeedAdapter(equities_only,mapping,feed_label="realtime",instrument="option")


def test_bad_time_and_no_schedule_fail_closed():
    assert assess(obs(age=60),A,CONTEXT).gate==Gate.TEMPORAL_HOLD
    assert assess(obs(age=-30),A,CONTEXT).gate==Gate.TEMPORAL_HOLD
    assert assess(obs(age=1),A,replace(CONTEXT,verified_market_time=False)).gate==Gate.CONTEXT_HOLD
    assert assess(obs(age=1),A,replace(CONTEXT,market_session="CLOSED")).gate==Gate.CONTEXT_HOLD
    with pytest.raises(ValueError):
        ScanContext(datetime(2026,9,28,12))


def test_equity_invalid_malformed_and_option_contract_identity_validation():
    with pytest.raises(ValueError):equity(bid=101,ask=100)
    with pytest.raises(ValueError):equity(last=float("nan"))
    with pytest.raises(ValueError):equity(volume=-1)
    assert opt().right=="call"
    with pytest.raises(ValueError):opt(ask=0)
    with pytest.raises(ValueError):replace(opt(),right="put")
    with pytest.raises(ValueError):replace(opt(),expiry="2026-10-03")
    with pytest.raises(ValueError):replace(opt(),underlying="DEF")


def test_events_wake_research_without_promoting_price():
    u=universe()
    lead=inspect_symbol("XYZ",universe=u,events=[event()],rights=RIGHTS,context=CONTEXT)
    assert lead.state=="EVENT_RESEARCH_ONLY"
    assert lead.event_ids==("form8k",)
    assert not lead.execution_ready and not lead.recommendation
    assert research_packet(lead)["eligibility"]["candidate_admitted"] is False
    assert inspect_symbol("XYZ",universe=u,events=[event(cik="9")],rights=RIGHTS,
                          context=CONTEXT).state=="DATA_HOLD"
    assert inspect_symbol("NOTLISTED",universe=u,events=[event()],rights=RIGHTS,
                          context=CONTEXT).state=="IDENTITY_HOLD"
    # Untimestamped/upstream-unknown press headlines cannot establish a filing's issuer.
    assert inspect_symbol("XYZ",universe=u,events=[replace(event(),issuer_cik="")],
                          rights=RIGHTS,context=CONTEXT).state=="DATA_HOLD"


def test_event_expiry_and_unreviewed_terms_are_not_research_admitted():
    ev=event(obs(source="public-filings",kind="event",family="SEC",age=90000,label="unknown"))
    assert inspect_symbol("XYZ",universe=universe(),events=[ev],rights=RIGHTS,
                          context=CONTEXT).state=="DATA_HOLD"
    rights={**RIGHTS,"public-filings":SourceRights("public-filings","SEC")}
    assert inspect_symbol("XYZ",universe=universe(),events=[event()],rights=rights,
                          context=CONTEXT).state=="DATA_HOLD"


def test_quote_watch_without_options_can_be_research_worthy():
    lead=inspect_symbol("XYZ",universe=universe(),equities=[equity()],
                        rights=RIGHTS,context=CONTEXT)
    assert lead.state=="RESEARCH_WATCH"
    assert lead.option_source_ids==()
    assert lead.underlying_source_ids==("vendor-a",)
    assert "2%" in lead.explanation[0]
    assert research_packet(lead)["eligibility"]["manual_live_authorized"] is False


def test_fresh_quote_does_not_invent_triggers():
    q=equity(previous_close=None,volume=None,average_volume=None)
    lead=inspect_symbol("XYZ",universe=universe(),equities=[q],rights=RIGHTS,context=CONTEXT)
    assert lead.state=="OBSERVATION"
    assert "no configured research trigger" in lead.explanation[0]


def test_corroboration_uses_independent_upstream_families():
    other=equity(obs(source="vendor-mirror",family="SIP",observation_id="same-upstream"),last=105)
    lead=inspect_symbol("XYZ",universe=universe(),equities=[equity(),other],
                        rights=RIGHTS,context=CONTEXT)
    assert lead.state=="RESEARCH_WATCH"
    assert len(lead.underlying_source_ids)==1
    separate=equity(obs(source="vendor-b",family="DIRECT",observation_id="independent"),last=105)
    conflict=inspect_symbol("XYZ",universe=universe(),equities=[equity(),separate],
                            rights=RIGHTS,context=CONTEXT)
    assert conflict.state=="CONFLICT_HOLD"
    assert not conflict.execution_ready


def test_option_gate_requires_current_underlying_and_independently_entitled_option_source():
    u=universe()
    q=equity()
    research=inspect_symbol("XYZ",universe=u,equities=[q],options=[opt()],
                            rights=RIGHTS,context=CONTEXT)
    assert research.option_source_ids==("vendor-a",)
    none=inspect_symbol("XYZ",universe=u,options=[opt()],rights=RIGHTS,context=CONTEXT)
    assert none.option_source_ids==()
    delayed=replace(opt(),evidence=obs(kind="option",label="delayed",observation_id="opt2"))
    held=inspect_symbol("XYZ",universe=u,equities=[q],options=[delayed],rights=RIGHTS,context=CONTEXT)
    assert held.option_source_ids==()


def test_planner_never_assumes_provider_limits_or_rights():
    budget=ProviderBudget("vendor-a",0,10)
    assert TrafficPlanner(budget,A).propose(context=CONTEXT,watchlist=["XYZ"])==[]
    budget=ProviderBudget("vendor-a",2,2,research_entitlement_confirmed=True,supports_options=True)
    assert TrafficPlanner(budget,None).propose(context=CONTEXT,watchlist=["XYZ"])==[]
    assert TrafficPlanner(budget,A).propose(context=replace(CONTEXT,market_session="CLOSED"),
                                            watchlist=["XYZ"])==[]


def test_planner_watchlist_event_then_rotating_cold_quota_and_cooldown():
    budget=ProviderBudget("vendor-a",2,2,research_entitlement_confirmed=True,supports_options=True)
    planner=TrafficPlanner(budget,A,quote_cooldown_seconds=30)
    requests=planner.propose(context=CONTEXT,watchlist=["XYZ"],event_symbols=["DEF"],
                              cold_universe=["EEE","FFF","GGG"],option_underlyings=["XYZ"])
    assert len(requests)==2
    assert [x.reason for x in requests]==["owner-watchlist","event-followup-not-price-proof"]
    assert all(not x.network_called and not x.order_placed for x in requests)
    assert planner.propose(context=CONTEXT,watchlist=["XYZ"])==[]
    assert planner.status()["used_window"]==2
    planner.backoff(NOW+timedelta(minutes=3))
    assert planner.propose(context=replace(CONTEXT,now=NOW+timedelta(minutes=1)),
                           watchlist=["XYZ"])==[]


def test_planner_options_only_when_caller_supplied_preverified_underlying():
    budget=ProviderBudget("vendor-a",3,2,supports_options=True,research_entitlement_confirmed=True)
    planner=TrafficPlanner(budget,A)
    req=planner.propose(context=CONTEXT,option_underlyings=["XYZ"])
    assert len(req)==1 and req[0].lane=="options" and req[0].symbols==("XYZ",)
    assert TrafficPlanner(budget,A).propose(context=CONTEXT,event_symbols=["XYZ"])[0].lane=="equity"


def test_stream_is_one_bounded_selection_and_no_client_open():
    b=ProviderBudget("vendor-a",3,2,supports_streaming=True,max_stream_symbols=2,
                     research_entitlement_confirmed=True)
    p=TrafficPlanner(b,A)
    assert p.stream_selection(context=CONTEXT,watchlist=["XYZ","DEF","GGG"])==("XYZ","DEF")
    assert p.stream_selection(context=replace(CONTEXT,verified_market_time=False),
                              watchlist=["XYZ"])==()
    assert not BOUNDARIES["provider_fetch_enabled"] and not BOUNDARIES["broker_order_submission"]
    assert not BOUNDARIES["synthetic_quote_fallback"]

def test_provider_adapter_requires_installed_rights_and_explicit_timestamp():
    with pytest.raises(ValueError):
        FeedAdapter(SourceRights("unknown","upstream"),{},feed_label="realtime")
    with pytest.raises(ValueError):
        FeedAdapter(replace(A,real_time_entitled=False),{},feed_label="realtime")
    mapping={x:x for x in ("observation_id","symbol","observed_at","provenance_reference",
                           "last","bid","ask","previous_close","volume","average_volume")}
    adapter=FeedAdapter(A,mapping,feed_label="realtime")
    registry=IngressRegistry()
    registry.register(adapter)
    raw={"observation_id":"q1","symbol":"XYZ","observed_at":"2026-09-28T14:59:59Z",
         "provenance_reference":"signed-source-event-1","last":100.0,
         "bid":99.9,"ask":100.1,"previous_close":98.0,"volume":1000,"average_volume":500,
         "source_id":"fraudulent-vendor","real_time_entitled":True}
    quote=registry.normalize("vendor-a","equity",raw,received_at=NOW)
    assert quote.evidence.source_id=="vendor-a"
    assert quote.evidence.upstream_family=="SIP"
    assert assess(quote.evidence,A,CONTEXT).gate==Gate.CURRENT_RESEARCH
    assert not registry.capability_snapshot()["network_enabled"]
    with pytest.raises(ValueError):
        registry.register(adapter)
    with pytest.raises(ValueError):
        adapter.normalize({**raw,"observed_at":"2026-09-28T14:59:59"},received_at=NOW)
    with pytest.raises(ValueError):
        adapter.normalize({k:v for k,v in raw.items() if k!="observed_at"},received_at=NOW)
