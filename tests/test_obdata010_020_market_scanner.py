"""Source-only OBDATA010–020 scanner tests: all provider data here is TEST FIXTURE.

No network, credentials, Render resource, broker action or actual market quote.
"""
from datetime import datetime, timedelta, timezone
from engine.market_scanner.equity_research import Entitlement, scan_equities
from engine.market_scanner.source_contract import iso_period, macro_envelope
from engine.market_scanner.macro_sources import fred_observations, owid_observations
from engine.market_scanner.sec_filings import filing_context, submissions_url

NOW=datetime(2026, 9, 28, 15, 0, tzinfo=timezone.utc)
SCOPE=Entitlement(
    provider="TEST_SOURCE", product="TEST_IEX_PRODUCT", venue="IEX",
    license_verified=True, scope="owner_private_research", permits_derived_research=True,
    permits_client_display=True, is_consolidated=False,
)

def snapshot():
    quote={"symbol":"XYZ","provider":"TEST_SOURCE","product":"TEST_IEX_PRODUCT",
           "venue":"IEX","trade_as_of":(NOW-timedelta(seconds=20)).isoformat(),
           "trade_price":"101.25"}
    bars=[]
    for i in range(25):
        bars.append({"provider":"TEST_SOURCE","product":"TEST_IEX_PRODUCT",
                     "venue":"IEX","completed":True,
                     "day":(NOW.date()-timedelta(days=25-i)).isoformat(),
                     "close":str(88+i/2),"volume":"2000"})
    return quote,bars


def test_research_quote_respects_source_venue_time_and_no_trading():
    q,b=snapshot()
    result=scan_equities(observations=[q],daily_bars={"XYZ":b},entitlement=SCOPE,now=NOW)
    assert result["status"]=="SOURCE_OBSERVED"
    assert result["market_data_current"] is True
    assert len(result["market_quotes"])==1
    entry=result["research_observations"][0]
    assert entry["quote_age_seconds"]==20 and entry["trade_price"]==101.25
    assert entry["coverage"]=="single_venue_or_limited"
    assert entry["trading_signal"] is False
    assert entry["options_quote"] is False
    assert result["options_chains"]==result["manual_live_queue"]==result["broker_positions"]==[]
    assert result["trading_authorized"] is False and result["broker_api"] is False
    assert result["data_is_consolidated"] is False


def test_missing_entitlement_and_invitee_display_do_not_leak():
    q,b=snapshot()
    assert scan_equities(observations=[q],daily_bars={"XYZ":b},
                          entitlement=None,now=NOW)["status"]=="LICENSE_HOLD"
    missing=Entitlement(provider="TEST_SOURCE",product="TEST_IEX_PRODUCT",
        venue="IEX",license_verified=False,scope="owner_private_research",
        permits_derived_research=True,permits_client_display=True)
    assert scan_equities(observations=[q],daily_bars={"XYZ":b},
                          entitlement=missing,now=NOW)["market_quotes"]==[]
    assert scan_equities(observations=[q],daily_bars={"XYZ":b},
        entitlement=SCOPE,now=NOW,user_scope="invitee_display_approved")["status"]=="LICENSE_HOLD"
    nondisplay=Entitlement(provider="TEST_SOURCE",product="TEST_IEX_PRODUCT",
        venue="IEX",license_verified=True,scope="owner_private_research",
        permits_derived_research=True,permits_client_display=False)
    safe=scan_equities(observations=[q],daily_bars={"XYZ":b},entitlement=nondisplay,now=NOW)
    assert safe["research_observations"] and safe["market_quotes"]==[]


def test_missing_stale_future_mismatch_and_unsupported_history_are_rejected():
    q,b=snapshot()
    for changed,reason in [
        ({"trade_as_of":None},"Missing provider-supplied timestamp"),
        ({"trade_as_of":(NOW-timedelta(minutes=30)).isoformat()},"stale_quote"),
        ({"trade_as_of":(NOW+timedelta(minutes=1)).isoformat()},"future_vendor_timestamp"),
        ({"provider":"TEST_OTHER"},"source_entitlement_mismatch"),
        ({"trade_price":0},"Invalid market observation"),
    ]:
        res=scan_equities(observations=[dict(q,**changed)],daily_bars={"XYZ":b},
                          entitlement=SCOPE,now=NOW)
        assert res["market_data_current"] is False
        assert res["research_observations"]==[]
        assert any(reason in x["reason"] for x in res["rejections"]),res
    tampered=[dict(bar) for bar in b];tampered[0]["provider"]="fake"
    res=scan_equities(observations=[q],daily_bars={"XYZ":tampered},entitlement=SCOPE,now=NOW)
    assert res["research_observations"]==[]
    assert any(x["reason"]=="unverified_or_incomplete_history" for x in res["rejections"])
    expired=[dict(bar,day=(NOW.date()-timedelta(days=100+i)).isoformat()) for i,bar in enumerate(b)]
    res=scan_equities(observations=[q],daily_bars={"XYZ":expired},entitlement=SCOPE,now=NOW)
    assert res["research_observations"]==[]


def test_fred_is_human_reference_only_with_no_ai_feed_or_cache():
    assert iso_period("2024",annual_allowed=True)=="2024"
    now=NOW
    hold=fred_observations(series_id="DGS10",api_key=None,permission_approved=True,
         get_json=None,collected_at=now)
    assert hold["status"]=="not_configured"
    assert hold["ai_assistant_input_eligible"] is False
    assert hold["persistent_cache_eligible"] is False
    assert hold["market_quotes"]==[] and hold["can_authorize_order"] is False
    no_rights=fred_observations(series_id="DGS10",api_key="a"*32,
         permission_approved=False,get_json=lambda _:{"observations":[]},collected_at=now)
    assert no_rights["status"]=="license_review_required"
    got=fred_observations(series_id="DGS10",api_key="a"*32,permission_approved=True,
         get_json=lambda _:{"observations":[
           {"date":"2026-09-25","value":"3.55","realtime_start":"2026-09-25",
            "realtime_end":"2026-09-25"}]},
         collected_at=now)
    assert got["status"]=="source_observed" and got["observations"][0]["period"]=="2026-09-25"
    assert got["ai_assistant_input_eligible"] is False
    assert got["current_market_data_eligible"] is False


def test_owid_requires_chart_rights_and_metadata_attribution():
    no=owid_observations(slug="example-public-chart",column="Metric",
        entity_code="USA",chart_approved=True,third_party_license_approved=False,
        get_csv=None,get_json=None,collected_at=NOW)
    assert no["status"]=="license_review_required"
    good=owid_observations(slug="example-public-chart",column="Metric",
        entity_code="USA",chart_approved=True,third_party_license_approved=True,
        get_csv=lambda _:"Entity,Code,Year,Metric\nUnited States,USA,2025,12.5\n",
        get_json=lambda _:{"chart":{"citation":"Example public source (test fixture)"},
            "columns":{"Metric":{"unit":"units","titleShort":"Illustration"}}},collected_at=NOW)
    assert good["status"]=="source_observed"
    assert good["observations"][0]["period"]=="2025"
    assert good["observations"][0]["cadence"]=="annual"
    assert good["ai_assistant_input_eligible"] is False
    assert good["market_quotes"]==[]


def test_sec_public_json_is_filings_not_market_data():
    assert submissions_url(1234)=="https://data.sec.gov/submissions/CIK0000001234.json"
    fixture={"cik":"1234","filings":{"recent":{
        "accessionNumber":["0000001234-26-000001"],
        "filingDate":["2026-09-28"],"form":["8-K"],"primaryDocument":["case.htm"]}}}
    denied=filing_context(cik=1234,payload=fixture,
        access_policy_verified=False,owner_use_permitted=True)
    assert denied["status"]=="HOLD" and denied["filings"]==[]
    good=filing_context(cik=1234,payload=fixture,
        access_policy_verified=True,owner_use_permitted=True)
    assert good["status"]=="SOURCE_OBSERVED"
    assert good["filings"][0]["form"]=="8-K"
    assert good["market_quotes"]==good["options_chains"]==good["positions"]==[]
    assert good["trading_authorized"] is False


def test_alpaca_iex_mapper_never_fetches_or_confuses_limited_feed():
    from engine.market_scanner.alpaca_iex_ingress import (
        normalize_trade, normalize_completed_daily_bars, PRODUCT, PROVIDER, VENUE,
    )
    trade={"T":"t","S":"XYZ","x":"V","p":"101.25","s":10,
           "t":(NOW-timedelta(seconds=20)).isoformat()}
    try:
        normalize_trade(trade,transport_verified=False,feed="iex")
        assert False,"Must deny unverified source transport"
    except ValueError:
        pass
    mapped=normalize_trade(trade,transport_verified=True,feed="iex")
    assert (mapped["provider"],mapped["product"],mapped["venue"])==(PROVIDER,PRODUCT,VENUE)
    assert mapped["source_is_consolidated"] is False
    assert mapped["eligible_as_options_quote"] is False
    vendor_bars=[]
    for i in range(25):
        vendor_bars.append({"t":(NOW-timedelta(days=25-i)).isoformat(),
                            "c":str(88+i/2),"v":2000})
    try:
        normalize_completed_daily_bars(vendor_bars,transport_verified=True,
              feed="iex",vendor_dataset_completed=False)
        assert False,"In-progress day cannot become finalized history"
    except ValueError:
        pass
    converted=normalize_completed_daily_bars(vendor_bars,transport_verified=True,
        feed="iex",vendor_dataset_completed=True)
    approved=Entitlement(provider=PROVIDER,product=PRODUCT,venue=VENUE,
        license_verified=True,scope="owner_private_research",
        permits_derived_research=True,permits_client_display=True,
        is_consolidated=False)
    result=scan_equities(observations=[mapped],daily_bars={"XYZ":converted},
         entitlement=approved,now=NOW)
    assert result["status"]=="SOURCE_OBSERVED"
    assert result["coverage"]=="single_venue_or_limited"
    assert result["trading_authorized"] is False
