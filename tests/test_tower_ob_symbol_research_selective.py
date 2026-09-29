"""Source-only synthetic acceptance of research overlays on Tower's guarded Desk branch.

No actual provider network call, no strategy P&L, no broker account or credentials.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from dataclasses import replace

from flask import Flask, render_template
import pytest

import tower.ob_symbol_research_integration as integration
import tower.ob_web_route_enforcement as enforcement
from engine.market_intake.universe import SymbolRow
from engine.market_intake.symbol_research import SymbolResearchInputs
from engine.market_intake.historical_research import (
    HistoryRights, HistorySeries, CompletedDailyBar,
)
from engine.market_intake.fundamental_research import FundamentalRights, CompanyFact
from web.hosted_tower import app as hosted_app

ROOT=Path(__file__).resolve().parents[1]
_CIK="0000000234"
_ACC="0000000234-26-000001"


def synthetic_inputs(name="Synthetic Test Company",symbol="XYZ"):
    now=datetime.now(timezone.utc)-timedelta(minutes=3)
    directory=SymbolRow(symbol,name,"NASDAQ","SYNTHETIC_TEST_DIRECTORY",now-timedelta(days=1),
                        sec_cik=_CIK,identity_status="VERIFIED")
    rights=HistoryRights(
        "synthetic-daily","TEST_DAILY","SYNTHETIC_SOURCE_FAMILY",
        "SYNTHETIC_LICENSE_RECEIPT",now-timedelta(days=2),
        research_allowed=True,automated_analysis_allowed=True,
        owner_display_allowed=True,ai_explanation_allowed=True,
        retention_allowed=False,basis="raw",
    )
    bars=tuple(CompletedDailyBar(symbol,"synthetic-daily",
        (now-timedelta(days=35-i)).date(),
        100.0+i/10,101.0+i/10,99.0+i/10,100.5+i/10,
        1000+i,"SYNTHETIC_COMPLETE_BAR_"+str(i),"raw",True)
        for i in range(25))
    hist=HistorySeries(symbol,rights,bars,now,"SYNTHETIC_SNAPSHOT_NOT_LIVE")
    fr=FundamentalRights("sec-edgar","SYNTHETIC_SEC_TERMS",
        now-timedelta(days=2),internal_research=True,
        owner_display=True,ai_explanation=True,retention=False)
    fact=CompanyFact(_CIK,_ACC,"Assets","USD",2500.0,
         (now-timedelta(days=90)).date(),now-timedelta(days=1),
         "10-Q",f"https://www.sec.gov/Archives/edgar/data/234/{_ACC.replace('-','')}/index.html")
    return SymbolResearchInputs(directory,now,hist,(fact,),fr)


def source_app(monkeypatch, *,resolver=None,selector=None):
    state={"owner":False,"step":False,"admitted":False}
    for mod in (integration,enforcement):
        monkeypatch.setattr(mod,"owner_session_active",lambda:state["owner"])
        monkeypatch.setattr(mod,"step_up_active",lambda:state["step"])
        monkeypatch.setattr(mod,"operational_ob_access_active",lambda:state["admitted"])
    app=Flask("synthetic_source_research",template_folder=str(ROOT/"web/templates"),
              static_folder=str(ROOT/"web/static"))
    app.testing=True
    enforcement.register_ob_protected_route_enforcement(app)
    integration.register_protected_symbol_research_context(
        app,research_resolver=resolver,trusted_selected_symbol=selector)
    @app.get("/ob/symbol/<symbol>")
    def symbol(symbol):
        return render_template_string_source(symbol)
    @app.get("/ob/market-map")
    def map_view():
        return render_template_string_source(None)
    @app.get("/ob/trade-center")
    def trade_view():
        return render_template_string_source(None)
    @app.get("/ob/review-center")
    def review_view():
        return render_template_string_source(None)
    @app.get("/ob/owner-console")
    def owner():
        return render_template_string_source(None)
    return app,state


def render_template_string_source(symbol):
    # Deliberately isolate the partial from pre-existing full-page route globals.
    from flask import render_template_string
    return render_template_string(
        "{{ '{' }}% include 'ob_research_context_partial.html' %{{ '}' }}",
        symbol=symbol,
    )


def grant_owner(state):
    state.update(owner=True,step=True,admitted=True)


def test_hosted_composition_registers_dormant_context_after_existing_desk():
    markers=hosted_app.extensions
    assert markers["tower_ob_market_data_desk_source_only_v1"]["runtime_provider_attached"] is False
    assert markers["tower_ob_symbol_research_context_v1"] == {
        "source_only":True,"provider_attached":False,
        "runtime_market_feed_attached":False,"trading_authorized":False,
        "browser_mutations":False,
    }
    assert "/ob/data-desk" in {r.rule for r in hosted_app.url_map.iter_rules()}
    assert "/ob/symbol-research/connect" not in {r.rule for r in hosted_app.url_map.iter_rules()}


def test_no_resolver_displays_no_research_instead_of_making_up_prices(monkeypatch):
    app,state=source_app(monkeypatch)
    grant_owner(state)
    html=app.test_client().get("/ob/symbol/XYZ").get_data(as_text=True)
    assert "Symbol research context" not in html
    assert app.extensions["tower_ob_symbol_research_context_v1"]["provider_attached"] is False


def test_synthetic_evidence_reaches_owner_symbol_without_trade_or_price_promotion(monkeypatch):
    touched=[]
    def resolver(room,symbol):
        touched.append((room,symbol))
        return synthetic_inputs()
    app,state=source_app(monkeypatch,resolver=resolver)
    client=app.test_client()
    assert client.get("/ob/symbol/XYZ").status_code==302
    assert touched==[]
    state["owner"]=True
    assert client.get("/ob/symbol/XYZ").status_code==302
    assert touched==[]
    state["step"]=True
    assert client.get("/ob/symbol/XYZ").status_code==302
    assert touched==[]
    state["admitted"]=True
    res=client.get("/ob/symbol/XYZ")
    assert res.status_code==200
    html=res.get_data(as_text=True)
    assert touched==[("symbol_page","XYZ")]
    assert "Synthetic Test Company" in html
    assert "SOURCE-BOUND" in html
    assert "SYNTHETIC_SNAPSHOT_NOT_LIVE" in html
    assert "25 completed sessions" in html
    assert "Not a live quote, signal or permission" in html
    assert "2500.0" not in html # no silent conversion to market quote
    assert 'href="/ob/data-desk/connect"' not in html


def test_exact_symbol_binding_and_unknown_route_fail_closed(monkeypatch):
    app,state=source_app(monkeypatch,resolver=lambda room,symbol:synthetic_inputs())
    grant_owner(state)
    client=app.test_client()
    assert client.get("/ob/symbol/ABC").status_code==503
    assert client.get("/ob/symbol/XYZ/secret").status_code==403
    assert client.get("/ob/not-a-research-room").status_code==403


def test_other_rooms_require_server_selected_symbol_never_query_string(monkeypatch):
    touched=[]
    def resolver(room,symbol):
        touched.append((room,symbol))
        return synthetic_inputs()
    app,state=source_app(monkeypatch,resolver=resolver)
    grant_owner(state)
    c=app.test_client()
    for path in ("/ob/market-map","/ob/trade-center","/ob/review-center"):
        assert c.get(path+"?symbol=XYZ").status_code==200
    assert touched==[]
    assert "Symbol research context" not in c.get("/ob/market-map?symbol=XYZ").get_data(as_text=True)


def test_server_selected_symbol_overlay_is_read_only_and_room_scoped(monkeypatch):
    calls=[]
    def resolver(room,symbol):
        calls.append((room,symbol))
        return synthetic_inputs()
    app,state=source_app(monkeypatch,resolver=resolver,
                         selector=lambda room:"XYZ")
    grant_owner(state)
    c=app.test_client()
    for path,room in (("/ob/market-map","market_map"),
                      ("/ob/trade-center","trade_center"),
                      ("/ob/review-center","review_center")):
        text=c.get(path).get_data(as_text=True)
        assert "Symbol research context" in text
        assert "Synthetic Test Company" in text
        assert "live quote, signal or permission" in text
        assert (room,"XYZ") in calls
    assert "Symbol research context" not in c.get("/ob/owner-console").get_data(as_text=True)


def test_source_error_sanitized_and_html_escapes_issuer_text(monkeypatch):
    app,state=source_app(monkeypatch,resolver=lambda *args:(_ for _ in ()).throw(
        RuntimeError("SECRET_SYNTHETIC_PROVIDER_TOKEN")))
    grant_owner(state)
    res=app.test_client().get("/ob/symbol/XYZ")
    assert res.status_code==503
    assert "SECRET_SYNTHETIC_PROVIDER_TOKEN" not in res.get_data(as_text=True)
    app2,state2=source_app(monkeypatch,resolver=lambda room,symbol:synthetic_inputs(
        name="<script>alert(1)</script>"))
    grant_owner(state2)
    escaped=app2.test_client().get("/ob/symbol/XYZ").get_data(as_text=True)
    assert "<script>alert(1)</script>" not in escaped
    assert "&lt;script&gt;" in escaped


def test_invalid_provider_receipt_or_future_capture_never_enters_owner_page(monkeypatch):
    now=datetime.now(timezone.utc)
    def bad_provider(room,symbol):
        raw=synthetic_inputs()
        return replace(raw,captured_at=now+timedelta(hours=1))
    app,state=source_app(monkeypatch,resolver=bad_provider)
    grant_owner(state)
    assert app.test_client().get("/ob/symbol/XYZ").status_code==503
    with pytest.raises(RuntimeError):
        integration.register_protected_symbol_research_context(app)
