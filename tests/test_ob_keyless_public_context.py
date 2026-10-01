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
    treasury_rates_enabled_from_environment,
)
from engine.market_intake.public_research_sources import OwnerResearchPolicy, PublicReferenceClient
from engine.market_intake.treasury_public_context import (
    TreasuryPublicClient, TREASURY_URL, TREASURY_RATE_DOCS,
)
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


class RawResponse:
    def __init__(self, raw):
        self.body = raw if isinstance(raw, bytes) else raw.encode()
    def __enter__(self): return self
    def __exit__(self, *_): return False
    def read(self, n): return self.body[:n]


def treasury_curve_xml(*, real=False):
    fields = (
        [
            ("TC_5YEAR", "1.55", "1.58"),
            ("TC_10YEAR", "1.80", "1.82"),
            ("TC_30YEAR", "2.20", "2.18"),
        ] if real else [
            ("BC_2YEAR", "3.50", "3.60"),
            ("BC_5YEAR", "3.70", "3.68"),
            ("BC_10YEAR", "4.00", "3.95"),
            ("BC_30YEAR", "4.55", "4.50"),
        ]
    )
    def entry(day, index):
        values = "".join(
            f'<d:{tag} m:type="Edm.Double">{pair[index]}</d:{tag}>'
            for tag, *pair in fields
        )
        return (
            "<entry><content type=\"application/xml\"><m:properties>"
            f'<d:NEW_DATE m:type="Edm.DateTime">{day}T00:00:00</d:NEW_DATE>'
            + values + "</m:properties></content></entry>"
        )
    return (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<feed xmlns="http://www.w3.org/2005/Atom" '
        'xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata" '
        'xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices">'
        + entry("2026-09-26", 1) + entry("2026-09-29", 0) + "</feed>"
    )


class TreasuryRatesSource:
    def __init__(self, *, malformed=False):
        self.calls = []
        self.malformed = malformed
        self.debt = {"data": [
            {"record_date":"2026-09-26","tot_pub_debt_out_amt":"38900000000000.12"},
            {"record_date":"2026-09-25","tot_pub_debt_out_amt":"38890000000000.12"},
        ]}
    def __call__(self, req, timeout):
        self.calls.append(req.full_url)
        if req.full_url == TREASURY_URL:
            return Response(self.debt)
        if "data=daily_treasury_yield_curve" in req.full_url:
            return RawResponse("<broken" if self.malformed else treasury_curve_xml())
        if "data=daily_treasury_real_yield_curve" in req.full_url:
            return RawResponse("<broken" if self.malformed else treasury_curve_xml(real=True))
        raise AssertionError("Unexpected Treasury URL")


class FakeOfficialSources:
    def __init__(self):
        self.calls=[]
        self.bls={
            "status":"REQUEST_SUCCEEDED",
            "Results":[{"series":[{"seriesID":"CUUR0000SA0", "data":[
                {"year":"2026","period":"M08","value":"320.10"},
                {"year":"2026","period":"M07","value":"318.7"}]}]}]}
        self.bls_v2={
            "LNS14000000": [
                {"year":"2026","period":"M08","value":"4.3"},
                {"year":"2026","period":"M07","value":"4.2"}],
            "CES0000000001": [
                {"year":"2026","period":"M08","value":"159500"},
                {"year":"2026","period":"M07","value":"159300"}],
            "WPUFD4": [
                {"year":"2026","period":"M08","value":"157.604"},
                {"year":"2026","period":"M07","value":"157.155"}],
        }
        self.treasury={"data":[
            {"record_date":"2026-09-26","tot_pub_debt_out_amt":"38900000000000.12"},
            {"record_date":"2026-09-25","tot_pub_debt_out_amt":"38890000000000.12"}
        ]}
        self.figi=[{"data":[{"ticker":"MSFT","figi":"BBG000B9XRY4"}]}]
    def __call__(self,req,timeout):
        self.calls.append((req.full_url,req.get_method(),dict(req.header_items()),timeout))
        if req.full_url.endswith("/publicAPI/v1/timeseries/data/CUUR0000SA0"):
            return Response(self.bls)
        for series_id, rows in self.bls_v2.items():
            if req.full_url.endswith("/publicAPI/v2/timeseries/data/" + series_id):
                return Response({"status":"REQUEST_SUCCEEDED","Results":{"series":[
                    {"seriesID":series_id,"data":rows}]}})
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
    assert [x["series_id"] for x in rows["bls"]["series"]]==[
        "CUUR0000SA0","LNS14000000","CES0000000001","WPUFD4"]
    assert all(x["state"]=="SOURCE_BOUND" for x in rows["bls"]["series"])
    assert rows["bls"]["series"][1]["value"]=="4.3"
    assert rows["bls"]["series"][2]["value"]=="159500"
    assert rows["bls"]["series"][3]["value"]=="157.604"
    assert rows["treasury"]["value"]=="38900000000000.12"
    assert rows["treasury"]["period"]=="2026-09-26"
    assert rows["treasury"]["previous_period"]=="2026-09-25"
    assert rows["treasury"]["previous_value"]=="38890000000000.12"
    assert rows["bls"]["previous_period"]=="2026-M07"
    assert rows["bls"]["previous_value"]=="318.7"
    assert rows["openfigi"]["value"]=="BBG000B9XRY4" and rows["openfigi"]["symbol"]=="MSFT"
    assert all(x["quote_eligible"] is False and x["trading_authorized"] is False
               and x["ai_use_approved"] is False for x in result["sources"])
    assert len(opener.calls)==6
    again=svc.snapshot(symbol="MSFT")
    assert again["sources"]==result["sources"]
    assert len(opener.calls)==6
    assert all("x-openfigi-apikey" not in str(entry).lower() for entry in opener.calls)


def test_global_context_avoids_guessing_symbol_and_user_does_not_need_provider_login():
    svc,opener=service()
    rows={x["source"]:x for x in svc.snapshot()["sources"]}
    assert rows["openfigi"]["state"]=="SYMBOL_REQUIRED"
    assert rows["openfigi"]["value"] is None
    assert len(opener.calls)==5
    assert all("Authorization" not in str(call) for call in opener.calls)


def test_source_absent_or_revoked_exposes_no_cached_value():
    svc,opener=service()
    svc.snapshot(symbol="MSFT")
    svc.enabled=frozenset()
    rows={x["source"]:x for x in svc.snapshot(symbol="MSFT")["sources"]}
    assert all(rows[k]["state"]=="REVIEW_HOLD" and rows[k]["value"] is None
               for k in ENABLED)
    assert len(opener.calls)==6


def test_treasury_official_rate_feeds_derive_curve_real_yield_and_breakeven():
    source = TreasuryRatesSource()
    policy = OwnerResearchPolicy(
        source_use_reviewed=True, owner_display_reviewed=True,
        reviewed_sources=frozenset({"treasury"}), ai_use_reviewed=False,
    )
    rates = TreasuryPublicClient(policy, opener=source).latest_rates_context()
    assert rates["state"] == "SOURCE_BOUND"
    assert rates["source_reference"] == TREASURY_RATE_DOCS
    assert rates["nominal"]["date"] == "2026-09-29"
    assert rates["nominal"]["yields_percent"] == {
        "2Y":"3.50", "5Y":"3.70", "10Y":"4.00", "30Y":"4.55"}
    assert rates["real"]["yields_percent"]["10Y"] == "1.80"
    assert rates["derived"]["two_year_change_bp"] == "-10.0"
    assert rates["derived"]["ten_year_change_bp"] == "5.0"
    assert rates["derived"]["two_ten_spread_bp"] == "50.0"
    assert rates["derived"]["previous_two_ten_spread_bp"] == "35.0"
    assert rates["derived"]["curve_shape"] == "POSITIVE"
    assert rates["derived"]["curve_change"] == "STEEPENED"
    assert rates["derived"]["real_ten_year_change_bp"] == "-2.0"
    assert rates["derived"]["ten_year_breakeven_percent"] == "2.20"
    assert rates["derived"]["previous_ten_year_breakeven_percent"] == "2.13"
    assert rates["derived"]["breakeven_change_bp"] == "7.0"
    assert rates["intraday"] is False and rates["executable_quote"] is False
    assert len(source.calls) == 2


def test_treasury_rates_reach_soulaana_as_explanation_not_trade_signal():
    source = TreasuryRatesSource()
    policy = OwnerResearchPolicy(
        source_use_reviewed=True, owner_display_reviewed=True,
        ai_use_reviewed=True, reviewed_sources=frozenset({"treasury"}),
        ai_reviewed_sources=frozenset({"treasury"}),
    )
    svc = KeylessPublicContext(
        enabled=frozenset({"treasury"}), ai_sources=frozenset({"treasury"}),
        treasury=TreasuryPublicClient(policy, opener=source),
        treasury_rates_enabled=True, now=lambda: datetime.now(timezone.utc),
    )
    packet = svc.snapshot()
    rates = packet["sources"][2]["rates"]
    assert rates["state"] == "SOURCE_BOUND"
    explain = packet["soulaana_evidence_brief"]["macro_explanation"]["rates"]
    assert explain["state"] == "SOURCE_BOUND"
    assert "steepened" in explain["rates_story"]
    assert "10-year real/TIPS yield" in explain["real_yield_story"]
    assert "simple 10-year nominal-minus-real breakeven" in explain["inflation_compensation_story"]
    assert explain["breakeven_is_simple_approximation"] is True
    assert explain["causality_claimed"] is False
    assert explain["trade_signal_created"] is False
    assert packet["soulaana_evidence_brief"]["external_model_called"] is False
    assert packet["candidate_admitted"] is False
    assert len(source.calls) == 3  # debt + nominal curve + real curve


def test_treasury_rate_failure_does_not_erase_valid_fiscal_context():
    source = TreasuryRatesSource(malformed=True)
    policy = OwnerResearchPolicy(
        source_use_reviewed=True, owner_display_reviewed=True,
        ai_use_reviewed=True, reviewed_sources=frozenset({"treasury"}),
        ai_reviewed_sources=frozenset({"treasury"}),
    )
    svc = KeylessPublicContext(
        enabled=frozenset({"treasury"}), ai_sources=frozenset({"treasury"}),
        treasury=TreasuryPublicClient(policy, opener=source),
        treasury_rates_enabled=True, now=lambda: datetime.now(timezone.utc),
    )
    treasury = svc.snapshot()["sources"][2]
    assert treasury["state"] == "SOURCE_BOUND"
    assert treasury["value"] == "38900000000000.12"
    assert treasury["rates"]["state"] == "SOURCE_HOLD"
    explain = svc.snapshot()["soulaana_evidence_brief"]["macro_explanation"]["rates"]
    assert explain["state"] == "SOURCE_HOLD"
    assert "not available" in explain["rates_story"]


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




def test_treasury_rates_require_independent_enable_and_display_review(monkeypatch):
    enabled = frozenset({"treasury"})
    for key in (
        "OB_KEYLESS_TREASURY_RATES_ENABLED",
        "OB_KEYLESS_TREASURY_RATES_USE_REVIEWED",
        "OB_KEYLESS_TREASURY_RATES_OWNER_DISPLAY_REVIEWED",
    ):
        monkeypatch.delenv(key, raising=False)
    assert treasury_rates_enabled_from_environment(enabled) is False
    monkeypatch.setenv("OB_KEYLESS_TREASURY_RATES_ENABLED", "1")
    assert treasury_rates_enabled_from_environment(enabled) is False
    monkeypatch.setenv("OB_KEYLESS_TREASURY_RATES_USE_REVIEWED", "1")
    assert treasury_rates_enabled_from_environment(enabled) is False
    monkeypatch.setenv("OB_KEYLESS_TREASURY_RATES_OWNER_DISPLAY_REVIEWED", "1")
    assert treasury_rates_enabled_from_environment(enabled) is True
    assert treasury_rates_enabled_from_environment(frozenset()) is False


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
    assert len(fake.calls)==6
    state["admitted"]=False
    assert client.get(PATH).status_code==302
    assert len(fake.calls)==6


def test_research_backend_stays_shared_but_generic_ui_shell_is_not_injected_into_rooms():
    pages=("market_data_desk","market_map","symbol_page",
           "trade_center","review_center","owner_dashboard","owner_console")
    for name in pages:
        source=(ROOT/"web/templates"/(name+".html")).read_text()
        assert 'id="obKeylessContextRoot"' not in source,name
        assert "/static/ob/ob_keyless_context.js" not in source,name
        assert "/static/ob/ob_keyless_context.css" not in source,name
        assert "/static/ob/ob_official_catalyst_radar.js" not in source,name
    symbol=(ROOT/"web/templates/symbol_page.html").read_text()
    assert "/static/ob/ob_symbol_research.js?v=symbolresearch001" in symbol
    js=(ROOT/"web/static/ob/ob_symbol_research.js").read_text()
    assert '"/ob/research/keyless.json?symbol="' in js
    assert '"/ob/research/catalysts.json"' in js
    assert 'credentials: "same-origin"' in js
    from engine.market_intake.provider_catalog import CATALOG
    product=CATALOG["treasury-debt-to-penny"]
    assert product.current_quote_eligible is False
    assert product.instrument=="event" and product.quote_kind=="reference"


def test_soulaana_receives_checked_status_register_not_raw_unreviewed_content():
    svc, transport = service()
    packet = svc.snapshot(symbol="MSFT")
    brief = packet["soulaana_source_register"]
    assert brief["schema"] == "OB_SOULAANA_KEYLESS_STATUS_V1"
    assert brief["channel"] == "SOULAANA_SOURCE_STATUS_ONLY"
    assert brief["source_observations_verified"] == 3
    assert brief["sec_issuer_corridor_delegated"] is True
    assert [item["source"] for item in brief["source_register"]] == [
        "sec", "bls", "treasury", "openfigi",
    ]
    assert all(item["meaning"] and item["label"] for item in brief["source_register"])
    for flag in ("raw_source_values_included", "source_content_ai_authorized",
                 "candidate_admitted", "quote_verified", "broker_execution_authorized"):
        assert brief[flag] is False
    # The owner-only cards are source-bound, but Soulaana's status projection
    # cannot smuggle financial values, FIGIs, ticker IDs or vendor payloads.
    rendered = json.dumps(brief)
    for forbidden in ("320.10", "38900000000000.12", "BBG000B9XRY4",
                      "synthetic", "CUUR0000SA0", "MSFT", "2026-M08"):
        assert forbidden not in rendered
    assert len(transport.calls) == 6


def test_soulaana_default_off_and_revocation_recompute_from_current_source_state():
    svc,transport=service()
    svc.snapshot(symbol="MSFT")
    svc.enabled=frozenset()
    packet=svc.snapshot(symbol="MSFT")
    brief=packet["soulaana_source_register"]
    assert brief["source_observations_verified"]==0
    assert {item["state"] for item in brief["source_register"][1:]}=={"REVIEW_HOLD"}
    assert "no keyless observations" in brief["what_i_see"]
    assert "320.10" not in json.dumps(brief)
    assert len(transport.calls)==6


def test_soulaana_bridge_rejects_faux_prices_ai_grants_or_injected_source_identity():
    from engine.market_intake.keyless_soulaana import build_soulaana_source_register
    svc,_=service()
    good=svc.snapshot(symbol="MSFT")
    for changed in (
        {**good,"prices_attached":True},
        {**good,"ai_input_approved":True},
        {**good,"sources":good["sources"][:3]},
        {**good,"sources":[{**good["sources"][0],"source":"public"}]+good["sources"][1:]},
        {**good,"sources":[{**good["sources"][0],"ai_use_approved":True}]+good["sources"][1:]},
        {**good,"sources":[{**good["sources"][0],"state":"SOURCE_BOUND"}]+good["sources"][1:]},
    ):
        with pytest.raises(ValueError, match="SOULAANA_KEYLESS_SOURCE_CONTRACT_HOLD"):
            build_soulaana_source_register(changed)


def test_shared_soulaana_panel_consumes_same_tower_snapshot_not_vendor_or_llm_api():
    js=(ROOT/"web/static/ob/ob_keyless_context.js").read_text()
    assert 'packet.soulaana_source_register' in js
    assert '"OB_SOULAANA_KEYLESS_STATUS_V1"' in js
    assert '"SOULAANA_SOURCE_STATUS_ONLY"' in js
    assert 'source_content_ai_authorized !== false' in js
    assert 'raw_source_values_included !== false' in js
    assert 'renderSoulaana(packet.soulaana_source_register)' in js
    assert 'soulaana.replaceChildren()' in js
    assert 'el("span", "", item.meaning)' in js
    assert "innerHTML" not in js
    assert "openai.com" not in js.lower()
    assert "api.public.com" not in js



def reviewed_content_service(ai_sources=frozenset({"bls", "treasury", "openfigi"})):
    source=FakeOfficialSources()
    svc=KeylessPublicContext(
        enabled=ENABLED, ai_sources=ai_sources, sec_delegated=True,
        reference=PublicReferenceClient(NO_KEY,opener=source),
        treasury=TreasuryPublicClient(NO_KEY,opener=source),
        now=lambda: datetime.now(timezone.utc),
    )
    return svc,source


def test_soulaana_receives_only_three_reviewed_source_facts_never_sec_or_market_prices():
    svc,opened=reviewed_content_service()
    packet=svc.snapshot(symbol="MSFT")
    register=packet["soulaana_source_register"]
    brief=packet["soulaana_evidence_brief"]
    assert register["schema"]=="OB_SOULAANA_KEYLESS_STATUS_V1"
    assert register["raw_source_values_included"] is False
    assert register["source_content_ai_authorized"] is False
    assert "320.10" not in str(register) and "BBG000B9XRY4" not in str(register)
    assert packet["ai_input_approved"] is False  # never a blanket grant
    assert brief["schema"]=="OB_SOULAANA_KEYLESS_EVIDENCE_V1"
    assert brief["channel"]=="SOULAANA_REVIEWED_PUBLIC_RESEARCH"
    assert brief["source_specific_ai_use_approved"] is True
    assert brief["observation_count"]==6
    assert [x["source"] for x in brief["observations"]]==[
        "bls","bls","bls","bls","treasury","openfigi"]
    assert [x.get("series_id") for x in brief["observations"][:4]]==[
        "CUUR0000SA0","LNS14000000","CES0000000001","WPUFD4"]
    assert "320.10" in brief["observations"][0]["interpretation"]
    assert "4.3%" in brief["observations"][1]["interpretation"]
    assert "159500" in brief["observations"][2]["interpretation"]
    assert "157.604" in brief["observations"][3]["interpretation"]
    assert "38900000000000.12" in brief["observations"][4]["interpretation"]
    assert "BBG000B9XRY4" in brief["observations"][5]["interpretation"]
    assert brief["macro_explanation"]["state"]=="SOURCE_BOUND_DIRECTIONAL_CONTEXT_ONLY"
    assert "price indexes both rose" in brief["macro_explanation"]["inflation"]
    assert "mixed labor signal" in brief["macro_explanation"]["labor"]
    assert brief["macro_explanation"]["trade_signal_created"] is False
    assert all(x["research_only"] and x["quote_verified"] is False
               and x["execution_authorized"] is False and x["source_reference"].startswith("https://")
               for x in brief["observations"])
    assert brief["external_model_called"] is False
    assert brief["blanket_ai_authority"] is False
    assert brief["public_brokerage_auth_inferred"] is False
    assert not any(x["source"]=="sec" for x in brief["observations"])
    assert "BLS.gov cannot vouch" in brief["bls_attribution"]
    assert len(opened.calls)==6


def test_no_review_no_soulaana_values_even_when_owner_cards_show_data():
    svc,opened=reviewed_content_service(frozenset())
    packet=svc.snapshot(symbol="MSFT")
    assert all(row["ai_use_approved"] is False for row in packet["sources"])
    brief=packet["soulaana_evidence_brief"]
    assert brief["observations"]==[]
    assert brief["source_specific_ai_use_approved"] is False
    assert brief["bls_attribution"] is None
    assert all(row["content_readable"] is False for row in brief["source_register"])
    assert len(opened.calls)==6  # card availability and AI processing distinct


def test_one_source_ai_review_does_not_unlock_another_or_sec_content():
    svc,_=reviewed_content_service(frozenset({"treasury"}))
    packet=svc.snapshot(symbol="MSFT")
    brief=packet["soulaana_evidence_brief"]
    assert [row["source"] for row in brief["observations"]]==["treasury"]
    assert [row["source"] for row in packet["sources"] if row["ai_use_approved"]]==["treasury"]
    assert packet["sources"][0]["value"] is None  # SEC is delegated, not fabricated


def test_revoked_or_failed_source_cannot_leak_old_soulaana_evidence():
    svc,_=reviewed_content_service()
    assert svc.snapshot(symbol="MSFT")["soulaana_evidence_brief"]["observation_count"]==6
    svc.enabled=frozenset()
    packet=svc.snapshot(symbol="MSFT")
    assert packet["soulaana_evidence_brief"]["observations"]==[]
    assert all(row["state"]=="REVIEW_HOLD" for row in packet["sources"][1:])


def test_tampered_provider_ai_or_original_source_provenance_holds_closed():
    from engine.market_intake.keyless_soulaana import build_soulaana_evidence_brief
    svc,_=reviewed_content_service(frozenset({"bls"}))
    packet=svc.snapshot(symbol="MSFT")
    packet["sources"][1]["source_reference"]="https://attacker.example/"
    with pytest.raises(ValueError,match="SOULAANA_EVIDENCE_REFERENCE_HOLD"):
        build_soulaana_evidence_brief(packet,approved_sources=frozenset({"bls"}))
    packet["sources"][1]["source_reference"]="https://www.bls.gov/developers/api_signature.htm"
    packet["sources"][2]["ai_use_approved"]=True
    with pytest.raises(ValueError,match="SOULAANA_EVIDENCE_RIGHTS_HOLD"):
        build_soulaana_evidence_brief(packet,approved_sources=frozenset({"bls"}))
    with pytest.raises(ValueError,match="SOULAANA_EVIDENCE_RIGHTS_HOLD"):
        build_soulaana_evidence_brief(packet,approved_sources=frozenset({"sec"}))


def test_env_requires_distinct_ai_use_flag_and_parent_display_grant(monkeypatch):
    from engine.market_intake.keyless_public_context import soulaana_sources_from_environment
    for name in ("OB_KEYLESS_SOULAANA_CONTENT_ENABLED","OB_KEYLESS_RESEARCH_ENABLED"):
        monkeypatch.delenv(name,raising=False)
    for provider in ("BLS","TREASURY","OPENFIGI"):
        for suffix in ("USE_REVIEWED","OWNER_DISPLAY_REVIEWED","AI_USE_REVIEWED"):
            monkeypatch.delenv(f"OB_KEYLESS_{provider}_{suffix}",raising=False)
    monkeypatch.setenv("OB_KEYLESS_SOULAANA_CONTENT_ENABLED","1")
    monkeypatch.setenv("OB_KEYLESS_BLS_AI_USE_REVIEWED","1")
    assert soulaana_sources_from_environment(enabled_sources_from_environment())==frozenset()
    monkeypatch.setenv("OB_KEYLESS_RESEARCH_ENABLED","1")
    monkeypatch.setenv("OB_KEYLESS_BLS_USE_REVIEWED","1")
    monkeypatch.setenv("OB_KEYLESS_BLS_OWNER_DISPLAY_REVIEWED","1")
    assert soulaana_sources_from_environment(enabled_sources_from_environment())==frozenset({"bls"})
    monkeypatch.delenv("OB_KEYLESS_SOULAANA_CONTENT_ENABLED")
    assert soulaana_sources_from_environment(enabled_sources_from_environment())==frozenset()


def test_all_room_soulaana_ui_has_typed_content_lane_and_no_unreviewed_model_request():
    js=(ROOT/"web/static/ob/ob_keyless_context.js").read_text()
    assert "validSoulaanaEvidence" in js and "renderSoulaanaEvidence" in js
    assert "SOULAANA_REVIEWED_PUBLIC_RESEARCH" in js
    assert "external_model_called !== false" in js
    assert 'packet.ai_input_approved !== false' in js
    assert "innerHTML" not in js and "api.openai.com" not in js


def test_soulaana_examines_same_source_prior_records_not_just_static_descriptions():
    svc,opened=reviewed_content_service()
    packet=svc.snapshot(symbol="MSFT")
    brief=packet["soulaana_evidence_brief"]
    assert brief["comparison_count"]==5
    bls={item["series_id"]:item for item in brief["comparisons"] if item["source"]=="bls"}
    assert bls["CUUR0000SA0"]["earlier_period"]=="2026-M07"
    assert bls["CUUR0000SA0"]["later_period"]=="2026-M08"
    assert bls["CUUR0000SA0"]["direction"]=="UP"
    assert "318.7" in bls["CUUR0000SA0"]["insight"] and "320.10" in bls["CUUR0000SA0"]["insight"]
    assert bls["LNS14000000"]["direction"]=="UP"
    assert bls["CES0000000001"]["direction"]=="UP"
    assert bls["WPUFD4"]["direction"]=="UP"
    treasury=next(item for item in brief["comparisons"] if item["source"]=="treasury")
    assert treasury["earlier_period"]=="2026-09-25"
    assert treasury["later_period"]=="2026-09-26"
    assert treasury["difference"]=="10000000000.00"
    assert treasury["direction"]=="UP"
    assert "different measures" in brief["what_needs_investigation"]
    assert brief["cross_source_causality_claimed"] is False
    assert all(x["research_only"] and not x["causality_claimed"] and not x["quote_verified"]
               for x in brief["comparisons"])
    assert brief["external_model_called"] is False
    assert len(opened.calls)==6   # same official GET, no second network request


def test_comparison_without_explicit_ai_use_is_not_in_soulaana_brief():
    svc,opened=reviewed_content_service(frozenset())
    brief=svc.snapshot(symbol="MSFT")["soulaana_evidence_brief"]
    assert brief["observations"]==[] and brief["comparisons"]==[]
    assert brief["comparison_count"]==0
    assert "No validated two-period comparison" in brief["what_changed"]
    assert len(opened.calls)==6


def test_one_source_ai_review_limits_comparison_to_that_source():
    svc,_=reviewed_content_service(frozenset({"bls"}))
    brief=svc.snapshot(symbol="MSFT")["soulaana_evidence_brief"]
    assert [c["series_id"] for c in brief["comparisons"]]==[
        "CUUR0000SA0","LNS14000000","CES0000000001","WPUFD4"]
    assert [x["series_id"] for x in brief["observations"]]==[
        "CUUR0000SA0","LNS14000000","CES0000000001","WPUFD4"]
    assert "treasury" not in str(brief["comparisons"]).lower()


def test_malformed_or_reverse_chronology_cannot_reach_soulaana():
    from engine.market_intake.keyless_soulaana import build_soulaana_evidence_brief
    svc,_=reviewed_content_service(frozenset({"treasury"}))
    valid=svc.snapshot(symbol="MSFT")
    for previous_period,previous_value in (
        ("2026-09-27","38890000000000.12"),
        ("2026-09-25","NaN"),
        ("2026-09-25",None),
        ("http://bad.example/","1")
    ):
        changed={**valid,"sources":[dict(row) for row in valid["sources"]]}
        changed["sources"][2]["previous_period"]=previous_period
        changed["sources"][2]["previous_value"]=previous_value
        with pytest.raises(ValueError,match="SOULAANA_COMPARISON_SHAPE_HOLD"):
            build_soulaana_evidence_brief(
                changed,approved_sources=frozenset({"treasury"}))


def test_browser_uses_nested_source_provenance_for_macro_comparisons():
    js=(ROOT/"web/static/ob/ob_keyless_context.js").read_text()
    assert 'packetOwnsReference(packet, item.source, item.source_reference)' in js
    assert 'packet.sources.some(r => r.source === item.source &&' not in js


def test_shared_soulaana_read_displays_insights_not_unreviewed_source_copy():
    js=(ROOT/"web/static/ob/ob_keyless_context.js").read_text()
    assert 'brief.comparisons.forEach' in js
    assert 'brief.what_changed' in js
    assert 'brief.what_needs_investigation' in js
    assert 'brief.cross_source_causality_claimed !== false' in js
    assert 'item.causality_claimed === false' in js
    assert 'panel.append(digest)' in js
    assert "innerHTML" not in js and "api.public.com" not in js


def test_bls_official_bulk_recovery_reaches_soulaana_with_real_provenance():
    from engine.market_intake.public_research_sources import BLS_BULK_CPI
    class Raw:
        status = 200
        def __enter__(self): return self
        def __exit__(self, *_): return False
        def geturl(self): return BLS_BULK_CPI
        def read(self, n): return self.body[:n]
        def __init__(self, body): self.body=body
    rows = ("series_id\tyear\tperiod\tvalue\tfootnote_codes\n"
            "CUUR0000SA0\t2026\tM07\t333.918\t\n"
            "CUUR0000SA0\t2026\tM08\t334.980\t\n").encode()
    calls = []
    def official(request, timeout):
        calls.append(request.full_url)
        if request.full_url.endswith("/publicAPI/v1/timeseries/data/CUUR0000SA0"):
            return Response({"status":"REQUEST_NOT_PROCESSED","Results":{}})
        if request.full_url == BLS_BULK_CPI:
            return Raw(rows)
        if "/publicAPI/v2/timeseries/data/" in request.full_url:
            return Response({"status":"REQUEST_FAILED","Results":{}})
        raise AssertionError("Unexpected official host")
    reviewed = OwnerResearchPolicy(
        source_use_reviewed=True, owner_display_reviewed=True,
        ai_use_reviewed=True, reviewed_sources=frozenset({"bls"}),
        ai_reviewed_sources=frozenset({"bls"}),
    )
    svc = KeylessPublicContext(
        enabled=frozenset({"bls"}), ai_sources=frozenset({"bls"}),
        reference=PublicReferenceClient(reviewed, opener=official),
        now=lambda: datetime.now(timezone.utc),
    )
    packet = svc.snapshot()
    bls = packet["sources"][1]
    brief = packet["soulaana_evidence_brief"]
    assert bls["state"] == "SOURCE_BOUND"
    assert bls["source_reference"] == BLS_BULK_CPI
    assert bls["value"] == "334.980" and bls["previous_value"] == "333.918"
    assert brief["observations"][0]["source_reference"] == BLS_BULK_CPI
    assert brief["comparisons"][0]["source_reference"] == BLS_BULK_CPI
    assert brief["comparison_count"] == 1
    assert brief["external_model_called"] is False
    assert len(calls) == 5
    js = (ROOT/"web/static/ob/ob_keyless_context.js").read_text()
    assert BLS_BULK_CPI in js
    assert "validReference(item.source, item.source_reference)" in js
    assert "link.href = item.source_reference" in js
