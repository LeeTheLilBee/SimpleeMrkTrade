"""Offline synthetic SEC intake/collector validation: no real HTTP or provider keys."""
from dataclasses import replace
from datetime import datetime,timedelta,timezone
from email.message import Message
from hashlib import sha256
from pathlib import Path
from urllib.error import HTTPError
import json

import pytest

from scripts.obscan_public_edgar_fetch import fetch_public_sec,targets
from engine.market_intake.edgar_research import build_edgar_research,acceptance_evidence
from engine.market_intake.edgar_cache import (
    read_sec_cache,checked_cached_research,make_owner_edgar_resolver)
from engine.market_intake.contracts import SourceRights
from engine.market_intake.fundamental_research import FundamentalRights
from engine.market_intake.research_bridge import project_research
from engine.market_intake.universe import SymbolRow

CIK="0000000234"
ACC="0000000234-26-000001"
NOW=datetime.now(timezone.utc).replace(microsecond=0)
ACCEPTED=NOW-timedelta(hours=2)
RIGHTS_VERIFIED=NOW-timedelta(days=2)


def submission(*,cik=234,stamp=None,accession=ACC):
    stamp=stamp or ACCEPTED.isoformat()
    return {"cik":cik,"tickers":["XYZ"],"filings":{"recent":{
        "accessionNumber":[accession], "form":["10-Q"],
        "acceptanceDateTime":[stamp],"primaryDocument":["q2.htm"],
        "filingDate":[ACCEPTED.date().isoformat()]},
        "files":[{"name":"CIK0000000234-submissions-001.json"}]}}


def facts(*,cik=234,accession=ACC):
    return {"cik":cik,"facts":{"us-gaap":{"Assets":{"units":{"USD":[{
        "accn":accession,"form":"10-Q",
        "end":(ACCEPTED-timedelta(days=100)).date().isoformat(),
        "filed":ACCEPTED.date().isoformat(),"val":250000000
    }]}}}}}


def row(symbol="XYZ"):
    return SymbolRow(symbol,"Synthetic Issuer","NASDAQ","nasdaqlisted.txt",
                     NOW-timedelta(days=3),sec_cik=CIK,sec_name="Synthetic Issuer",
                     identity_status="CROSS_REFERENCED")


def event_rights(*,owner=True):
    return SourceRights("sec-edgar","SEC-EDGAR","reviewed-sec-public-internal-owner-use",
                        RIGHTS_VERIFIED,internal_research=True,
                        automated_non_display=True,owner_display=owner,
                        entitled_instruments=frozenset({"event"}))


def financial_rights(*,owner=True,ai=False):
    return FundamentalRights("sec-edgar","reviewed-sec-public-internal-financial-use",
         RIGHTS_VERIFIED,internal_research=True,owner_display=owner,
         ai_explanation=ai,retention=False)


class Reply:
    def __init__(self,url,payload,etag="fixture-etag"):
        self.url=url;self.payload=json.dumps(payload).encode()
        self.headers={"ETag":etag,"Last-Modified":"Tue, 29 Sep 2026 00:00:00 GMT"}
    def __enter__(self):return self
    def __exit__(self,*unused):return None
    def geturl(self):return self.url
    def read(self,n):return self.payload[:n]


def response(req,timeout=0):
    if req.full_url.endswith("company_tickers_exchange.json"):
        payload={"fields":["cik","name","ticker","exchange"],
                 "data":[[234,"Synthetic Issuer","XYZ","Nasdaq"]]}
    elif req.full_url.endswith(".json") and "companyfacts" in req.full_url:
        payload=facts()
    else:payload=submission()
    return Reply(req.full_url,payload)


def collector(tmp_path):
    slept=[]
    report=fetch_public_sec(ciks=[CIK],output=tmp_path,
        user_agent="Simplee World Research real-contact@example.org",
        enable_network=True,opener=response,sleeper=slept.append)
    assert report["state"]=="PUBLIC_RESEARCH_SNAPSHOT"
    assert report["requests_attempted"]==3 and slept==[1.0,1.0]
    return report


def test_dry_run_does_not_request_or_create_files(tmp_path):
    def forbidden(*args,**kw):raise AssertionError("dry run opened network")
    x=fetch_public_sec(ciks=[CIK],output=tmp_path,user_agent="",opener=forbidden)
    assert x["state"]=="DRY_RUN_NO_REQUESTS" and len(x["planned_urls"])==3
    assert not list(tmp_path.iterdir())


def test_exact_cik_dedup_product_endpoints_and_real_contact(tmp_path):
    assert len(targets(["234",CIK]))==3
    assert targets(["234"])[1][1]=="https://data.sec.gov/submissions/CIK0000000234.json"
    assert targets(["234"])[2][1]=="https://data.sec.gov/api/xbrl/companyfacts/CIK0000000234.json"
    for bad in (["XYZ"],["12345678901"],["123"]*21):
        with pytest.raises(ValueError):targets(bad)
    for bad in ("anonymous","contact@example.org","Research fake\r\nX-injected:1"):
        with pytest.raises(ValueError):
            fetch_public_sec(ciks=[CIK],output=tmp_path,user_agent=bad,
                             enable_network=True,opener=response)
    with pytest.raises(ValueError):
        fetch_public_sec(ciks=[CIK],output=tmp_path,
             user_agent="Research person@example.org",enable_network=True,
             delay_seconds=0.1,opener=response)


def test_three_exact_public_products_checksums_and_no_quote(tmp_path):
    report=collector(tmp_path)
    assert report["real_time_market_data"] is False
    assert report["execution_ready"] is False
    for f in report["files"]:
        path=tmp_path/f["file"]
        meta=json.loads((tmp_path/(f["file"]+".http-metadata.json")).read_text())
        assert meta["sha256"]==sha256(path.read_bytes()).hexdigest()
        assert meta["url"].startswith("https://")
        assert meta["source_type"]=="PUBLIC_SEC_REFERENCE_NOT_QUOTE"
    contents,at=read_sec_cache(root=tmp_path,cik=CIK,kind="companyfacts")
    assert contents["cik"]==234 and at.tzinfo


def test_http_304_only_accepts_checked_cached_origin_and_digest(tmp_path):
    collector(tmp_path)
    def no_change(req,timeout=0):
        raise HTTPError(req.full_url,304,"not modified",Message(),None)
    ok=fetch_public_sec(ciks=[CIK],output=tmp_path,
         user_agent="Research person@example.org",enable_network=True,
         opener=no_change,sleeper=lambda _:None)
    assert ok["state"]=="PUBLIC_RESEARCH_SNAPSHOT"
    assert len(ok["files"])==3 and all(x["state"]=="NOT_MODIFIED_VALID_CACHE" for x in ok["files"])
    path=tmp_path/"company_tickers_exchange.json"
    path.write_text('{"fields":[],"data":[]}')
    bad=fetch_public_sec(ciks=[CIK],output=tmp_path,
         user_agent="Research person@example.org",enable_network=True,
         opener=no_change)
    assert bad["state"]=="EDGAR_SOURCE_HOLD" and bad["files"][0]["state"]=="CACHE_HOLD"


def test_http429_malformed_issuer_redirect_and_invalid_json_fail_closed(tmp_path):
    def too_many(req,timeout=0):
        h=Message();h["Retry-After"]="60"
        raise HTTPError(req.full_url,429,"rate limited",h,None)
    x=fetch_public_sec(ciks=[CIK],output=tmp_path,user_agent="Research person@example.org",
         enable_network=True,opener=too_many)
    assert x["state"]=="EDGAR_SOURCE_HOLD" and x["requests_attempted"]==1
    assert x["files"][0]["state"]=="RATE_LIMIT_HOLD_STOP"
    bad=fetch_public_sec(ciks=[],output=tmp_path,user_agent="Research person@example.org",
         enable_network=True,opener=lambda req,timeout=0:Reply(
             "https://unapproved.invalid/",{"fields":[],"data":[]}))
    assert bad["files"][0]["state"]=="SOURCE_HOLD"
    def invalid(req,timeout=0):
        return Reply(req.full_url,{"cik":999,"filings":{"recent":{}}})
    bad=fetch_public_sec(ciks=[CIK],output=tmp_path,user_agent="Research person@example.org",
         enable_network=True,opener=invalid)
    assert bad["state"]=="EDGAR_SOURCE_HOLD"


def test_source_reviewed_offline_edgar_join_reuses_existing_symbol_record():
    bundle=build_edgar_research(identity=row(),submissions=submission(),companyfacts=facts(),
         received_at=NOW,event_rights=event_rights(),
         fundamental_rights=financial_rights(ai=True))
    assert bundle.filings==1 and bundle.selected_facts==1 and bundle.accepted_accessions==1
    assert bundle.timestamp_assurance=="SEC_JSON_REPORTED_NOT_RAW_HEADER_VERIFIED"
    assert bundle.historical_filing_coverage=="RECENT_ONLY_OLDER_PAGES_NOT_IMPORTED"
    record=bundle.owner_snapshot()
    assert record["identity"]["cik"]==CIK
    assert record["fundamentals"]["reported_concepts"][0]["value"]==250000000
    assert record["issuer_events"][0]["kind"]=="filing"
    assert record["scanner"]["state"]=="NOT_CONNECTED"
    assert not record["execution_authorized"] and not record["broker_quote_verified"]
    view=project_research(record,"symbol_page")
    assert view["fundamentals"]["state"]=="SOURCE_BOUND"
    assert view["may_authorize_order"] is False
    assert bundle.status()["current_option_quote"] is False


def test_mismatched_issuer_future_acceptance_and_partial_columns_are_holds():
    with pytest.raises(ValueError):
        build_edgar_research(identity=row(),submissions=submission(cik=235),companyfacts=facts(),
           received_at=NOW,event_rights=event_rights(),
           fundamental_rights=financial_rights())
    with pytest.raises(ValueError):
        build_edgar_research(identity=row(),submissions=submission(),companyfacts=facts(cik=235),
           received_at=NOW,event_rights=event_rights(),
           fundamental_rights=financial_rights())
    bad=submission();bad["filings"]["recent"]["form"]=[]
    with pytest.raises(ValueError):
        acceptance_evidence(bad,received_at=NOW)
    future=submission(stamp=(NOW+timedelta(days=1)).isoformat())
    a,held=acceptance_evidence(future,received_at=NOW)
    assert a=={} and held==(ACC,)
    result=build_edgar_research(identity=row(),submissions=future,companyfacts=facts(),
         received_at=NOW,event_rights=event_rights(),
         fundamental_rights=financial_rights())
    assert result.filings==0 and result.selected_facts==0


def test_owner_rights_cannot_be_inferred_from_free_endpoint():
    with pytest.raises(ValueError):
        build_edgar_research(identity=row(),submissions=submission(),companyfacts=facts(),
            received_at=NOW,event_rights=event_rights(owner=False),
            fundamental_rights=financial_rights())
    with pytest.raises(ValueError):
        build_edgar_research(identity=row(),submissions=submission(),companyfacts=facts(),
            received_at=NOW,event_rights=event_rights(),
            fundamental_rights=financial_rights(owner=False))
    with pytest.raises(ValueError):
        build_edgar_research(identity=replace(row(),sec_cik=None),
            submissions=submission(),companyfacts=facts(),received_at=NOW,
            event_rights=event_rights(),fundamental_rights=financial_rights())


def test_checked_cache_and_optional_tower_resolver_never_use_browser_symbol(tmp_path):
    collector(tmp_path)
    bundle=checked_cached_research(identity=row(),root=tmp_path,event_rights=event_rights(),
                                    fundamental_rights=financial_rights())
    assert bundle.inputs.identity.sec_cik==CIK and bundle.filings==1
    resolver=make_owner_edgar_resolver(identities={"XYZ":row()},root=tmp_path,
                            event_rights=event_rights(),fundamental_rights=financial_rights())
    assert resolver("symbol_page","XYZ") is not None
    assert resolver("symbol_page","ABC") is None
    with pytest.raises(ValueError):resolver("unmapped","XYZ")
    (tmp_path/f"CIK{CIK}.companyfacts.json").write_text('{"cik":234,"facts":{}}')
    assert resolver("symbol_page","XYZ") is None
    with pytest.raises(ValueError):
        read_sec_cache(root=tmp_path,cik=CIK,kind="companyfacts")


def test_no_network_route_order_or_generated_fake_prices_in_edgar_sources():
    root=Path("engine/market_intake")
    code="\n".join((root/x).read_text() for x in (
        "edgar_research.py","edgar_cache.py"))
    assert not any(q in code for q in (
        "urlopen(","requests.get(","submit_order(","place_order(","WebSocket(","yfinance"))
    assert "current_equity_quote" in code and "candidate_admitted" in code


def test_offline_operator_bridge_requires_independent_symbol_and_explicit_review(tmp_path):
    from scripts.ob_edgar_research import run
    collector(tmp_path)
    nasdaq=tmp_path/"nasdaqlisted.txt"
    other=tmp_path/"otherlisted.txt"
    nasdaq.write_text("Symbol|Security Name|Market Category|Test Issue|Financial Status|Round Lot Size|ETF|NextShares\\nXYZ|Synthetic Issuer|Q|N|N|100|N|N\\n")
    other.write_text("ACT Symbol|Security Name|Exchange|CQS Symbol|ETF|Round Lot Size|Test Issue|NASDAQ Symbol\\n")
    rights=tmp_path/"review.json"
    review={
        "scope":"owner_internal",
        "event":{"permission_reference":"owner-reviewed-public-SEC-terms",
                 "verified_at":RIGHTS_VERIFIED.isoformat(),
                 "internal_research":True,"automated_non_display":True,"owner_display":True},
        "fundamentals":{"reference":"owner-reviewed-public-SEC-financial-terms",
                 "reviewed_at":RIGHTS_VERIFIED.isoformat(),
                 "internal_research":True,"owner_display":True,
                 "ai_explanation":False,"long_term_retention":False}}
    rights.write_text(json.dumps(review))
    kwargs=dict(nasdaq=nasdaq,other=other,
                crossref=tmp_path/"company_tickers_exchange.json",
                cache=tmp_path,symbol="XYZ",rights_record=rights)
    view=run(**kwargs)
    assert view["edgar_status"]["financial_facts_selected"]==1
    assert view["symbol_research"]["fundamentals"]["state"]=="SOURCE_BOUND"
    assert view["manual_live_authorized"] is False
    assert set(view["edgar_status"]["cache_receipts"])=={"submissions","companyfacts"}
    review["event"]["owner_display"]=False
    rights.write_text(json.dumps(review))
    with pytest.raises(ValueError):run(**kwargs)


def test_protected_research_partial_renders_sec_concepts_but_no_fake_feed():
    from flask import Flask,render_template
    from engine.market_intake.edgar_research import build_edgar_research
    b=build_edgar_research(identity=row(),submissions=submission(),companyfacts=facts(),
        received_at=NOW,event_rights=event_rights(),
        fundamental_rights=financial_rights(ai=True))
    view=project_research(b.owner_snapshot(),"symbol_page")
    app=Flask("edgar_template_test",template_folder=str(Path("web/templates").resolve()))
    with app.test_request_context():
        page=render_template("ob_research_context_partial.html",ob_research_context=view)
    assert "SEC EDGAR" in page and "Assets" in page
    assert "250000000" in page and ACC in page
    assert "live equity or option price" in page
    assert "submit_order" not in page
