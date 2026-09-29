"""Synthetic no-login keyless source and protected cross-room read tests.

No real API, provider secret, brokerage account, market quote or paid resource.
"""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path

from flask import Flask
import pytest

from engine.market_intake.keyless_public_context import (
    KeylessPublicContext, from_environment, enabled_sources_from_environment,
)
from engine.market_intake.public_research_sources import OwnerResearchPolicy, PublicReferenceClient
from engine.market_intake.treasury_public_context import TreasuryPublicClient, TREASURY_URL
from web.ob_keyless_context_route import PATH, create_keyless_context_blueprint
from tower.ob_route_guard import match_ob_guard_policy
from tower.ob_web_route_enforcement import (
    PROTECTED_EXACT_OB_ROUTES, register_ob_protected_route_enforcement,
)
import tower.ob_web_route_enforcement as enforcement

ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 9, 29, 17, 0, tzinfo=timezone.utc)
ENABLED = frozenset({"bls", "treasury", "openfigi"})
NO_KEY = OwnerResearchPolicy(
    source_use_reviewed=True, owner_display_reviewed=True,
    reviewed_sources=ENABLED, ai_use_reviewed=False,
)


class Response:
    def __init__(self, payload):
        self.body=json.dumps(payload).encode()
    def __enter__(self): return self
    def __exit__(self, *_): return False
    def read(self, n): return self.body[:n]


class FakeOfficialSources:
    def __init__(self):
        self.calls=[]
        self.bls={
            "status":"REQUEST_SUCCEEDED",
            "Results":{"series":[{"seriesID":"CUUR0000SA0", "data":[
                {"year":"2026","period":"M08","value":"320.10"},
                {"year":"2026","period":"M07","value":"318.7"}]}]}}
        self.treasury={"data":[{"record_date":"2026-09-26","tot_pub_debt_out_amt":"38900000000000.12"}]}
        self.figi=[{"data":[{"ticker":"MSFT","figi":"BBG000B9XRY4"}]}]
    def __call__(self,req,timeout):
        self.calls.append((req.full_url,req.get_method(),dict(req.header_items()),timeout))
        if req.full_url.endswith("/publicAPI/v1/timeseries/data/CUUR0000SA0"):
            return Response(self.bls)
        if req.full_url==TREASURY_URL:
            return Response(self.treasury)
        if req.full_url=="https://api.openfigi.com/v3/mapping":
            assert req.get_method()=="POST"
            assert b'"idValue": "MSFT"' in req.data or b'"idValue": "' in req.data
            return Response(self.figi)
        raise AssertionError("Only exact official keyless URLs permitted")


def service(source=None, *, enabled=ENABLED, now=None):
    source=source or FakeOfficialSources()
    return KeylessPublicContext(
        enabled=enabled, sec_delegated=True,
        reference=PublicReferenceClient(NO_KEY,opener=source),
        treasury=TreasuryPublicClient(NO_KEY,opener=source),
        now=now or (lambda: NOW)),source


def test_four_source_context_is_dated_public_reference_only_and_cached():
    svc,opener=service()
    result=svc.snapshot(symbol="MSFT")
    assert result["schema"]=="OB_KEYLESS_PUBLIC_CONTEXT_V1"
    assert result["source_only"] and result["context_only"]
    for flag in ("prices_attached","options_chain_attached","live_quote_verified",
                 "feeds_connected","candidate_admitted","broker_execution_authorized",
                 "ai_input_approved","sec_data_in_this_snapshot"):
        assert result[flag] is False
    rows={x["source"]:x for x in result["sources"]}
    assert rows["sec"]["state"]=="DELEGATED_ISSUER_RESEARCH"
    assert rows["sec"]["value"] is None and rows["sec"]["retrieved_at"] is None
    assert rows["bls"]["value"]=="320.10" and rows["bls"]["period"]=="2026-M08"
    assert rows["treasury"]["value"]=="38900000000000.12"
    assert rows["treasury"]["period"]=="2026-09-26"
    assert rows["openfigi"]["value"]=="BBG000B9XRY4" and rows["openfigi"]["symbol"]=="MSFT"
    assert all(x["quote_eligible"] is False and x["trading_authorized"] is False
               and x["ai_use_approved"] is False for x in result["sources"])
    assert len(opener.calls)==3
    again=svc.snapshot(symbol="MSFT")
    assert again["sources"]==result["sources"]
    assert len(opener.calls)==3
    assert all("x-openfigi-apikey" not in str(entry).lower() for entry in opener.calls)


def test_global_context_avoids_guessing_symbol_and_user_does_not_need_provider_login():
    svc,opener=service()
    rows={x["source"]:x for x in svc.snapshot()["sources"]}
    assert rows["openfigi"]["state"]=="SYMBOL_REQUIRED"
    assert rows["openfigi"]["value"] is None
    assert len(opener.calls)==2
    assert all("Authorization" not in str(call) for call in opener.calls)


def test_source_absent_or_revoked_exposes_no_cached_value():
    svc,opener=service()
    svc.snapshot(symbol="MSFT")
    svc.enabled=frozenset()
    rows={x["source"]:x for x in svc.snapshot(symbol="MSFT")["sources"]}
    assert all(rows[k]["state"]=="REVIEW_HOLD" and rows[k]["value"] is None
               for k in ENABLED)
    assert len(opener.calls)==3


def test_treasury_bad_value_or_date_never_promotes_or_reuses_data():
    fake=FakeOfficialSources()
    svc,_=service(fake,enabled=ENABLED)
    fake.treasury={"data":[{"record_date":"2026-10-31","tot_pub_debt_out_amt":"1"}]}
    result={x["source"]:x for x in svc.snapshot()["sources"]}
    assert result["treasury"]["state"]=="SOURCE_HOLD"
    assert result["treasury"]["value"] is None
    assert result["bls"]["state"]=="SOURCE_BOUND"
    other=FakeOfficialSources()
    other.treasury={"data":[{"record_date":"2026-09-26","tot_pub_debt_out_amt":"NaN"}]}
    next_svc,_=service(other)
    assert {x["source"]:x for x in next_svc.snapshot()["sources"]}["treasury"]["state"]=="SOURCE_HOLD"


def test_bad_symbol_not_forwarded_and_local_figi_budget_caps_untrusted_browse():
    svc,opener=service()
    for symbol in ("aapl","../../secret","GOOG/SECRET","A" * 99, "", ".."):
        with pytest.raises(ValueError):
            svc.snapshot(symbol=symbol)
    assert opener.calls==[]
    for i in range(6):
        symbol=f"A{i}" if i else "MSFT"
        svc.snapshot(symbol=symbol)
    rows={x["source"]:x for x in svc.snapshot(symbol="A5")["sources"]}
    assert rows["openfigi"]["state"]=="LOCAL_QUOTA_HOLD"
    assert sum("/v3/mapping" in url for url, *_ in opener.calls)==5


def test_default_off_and_independent_provider_reviews(monkeypatch):
    for name in ("OB_KEYLESS_RESEARCH_ENABLED","OB_SEC_PUBLIC_RESEARCH_ENABLED"):
        monkeypatch.delenv(name,raising=False)
    for source in ENABLED:
        monkeypatch.delenv(f"OB_KEYLESS_{source.upper()}_USE_REVIEWED",raising=False)
        monkeypatch.delenv(f"OB_KEYLESS_{source.upper()}_OWNER_DISPLAY_REVIEWED",raising=False)
    assert enabled_sources_from_environment()==frozenset()
    assert all(x["state"]=="REVIEW_HOLD" for x in from_environment().snapshot()["sources"])
    monkeypatch.setenv("OB_KEYLESS_RESEARCH_ENABLED","1")
    monkeypatch.setenv("OB_KEYLESS_BLS_USE_REVIEWED","1")
    assert enabled_sources_from_environment()==frozenset()
    monkeypatch.setenv("OB_KEYLESS_BLS_OWNER_DISPLAY_REVIEWED","1")
    assert enabled_sources_from_environment()==frozenset({"bls"})
    # BEA, FRED and Public credentials are never attached by this path.
    assert not {"bea","fred","public"} & set(ENABLED)


def test_tower_exact_route_requires_owner_stepup_admission_before_transport(monkeypatch):
    state={"owner":False,"step":False,"admitted":False}
    monkeypatch.setattr(enforcement,"owner_session_active",lambda:state["owner"])
    monkeypatch.setattr(enforcement,"step_up_active",lambda:state["step"])
    monkeypatch.setattr(enforcement,"operational_ob_access_active",lambda:state["admitted"])
    fake=FakeOfficialSources()
    svc,_=service(fake)
    app=Flask(__name__)
    app.secret_key="synthetic-only"
    app.config["TESTING"]=True
    register_ob_protected_route_enforcement(app)
    app.register_blueprint(create_keyless_context_blueprint(
        owner_authorize=lambda:all(state.values()),context_service=svc))
    client=app.test_client()
    assert PATH in PROTECTED_EXACT_OB_ROUTES
    assert match_ob_guard_policy(PATH)["match_type"]=="exact"
    assert match_ob_guard_policy(PATH+"/secret")["match_type"]=="unmapped_default_deny"
    assert client.get(PATH).status_code==302
    state["owner"]=True
    assert client.get(PATH).status_code==302
    state["step"]=True
    assert client.get(PATH).status_code==302
    assert fake.calls==[]
    state["admitted"]=True
    assert client.head(PATH).status_code==405
    assert client.post(PATH).status_code==405
    assert client.get(PATH+"-unmapped").status_code==403
    assert client.get(PATH+"?symbol=../../etc").status_code==400
    assert client.get(PATH+"?debug=1").status_code==400
    assert fake.calls==[]
    ok=client.get(PATH+"?symbol=MSFT")
    assert ok.status_code==200
    assert ok.headers["Cache-Control"].startswith("no-store")
    data=ok.get_json()
    assert data["schema"]=="OB_KEYLESS_PUBLIC_CONTEXT_V1"
    assert data["prices_attached"] is False
    assert len(fake.calls)==3
    state["admitted"]=False
    assert client.get(PATH).status_code==302
    assert len(fake.calls)==3


def test_private_room_consumers_share_one_endpoint_without_faux_live_quotes():
    pages=("market_data_desk","dashboard","market_map","symbol_page",
           "trade_center","review_center","owner_dashboard","owner_console")
    for name in pages:
        source=(ROOT/"web/templates"/(name+".html")).read_text()
        assert 'id="obKeylessContextRoot"' in source,name
        assert "/static/ob/ob_keyless_context.js" in source,name
        assert "/static/ob/ob_keyless_context.css" in source,name
    js=(ROOT/"web/static/ob/ob_keyless_context.js").read_text()
    assert '"/ob/research/keyless.json"' in js
    assert 'credentials: "same-origin"' in js
    assert "innerHTML" not in js
    assert "api.public.com" not in js and "api.openfigi.com" not in js
    assert "trade" in js.lower()
    assert 'packet.prices_attached !== false' in js
    assert 'packet.broker_execution_authorized !== false' in js
    from engine.market_intake.provider_catalog import CATALOG
    product=CATALOG["treasury-debt-to-penny"]
    assert product.current_quote_eligible is False
    assert product.instrument=="event" and product.quote_kind=="reference"
