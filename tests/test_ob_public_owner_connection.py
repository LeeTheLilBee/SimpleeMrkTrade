"""Owner-only Public connect tests use fake HTTP, never actual keys/quotes."""
from datetime import timedelta
import re

from flask import Flask
import pytest

from test_ob_public_local_probe import Recorder, Response, SECRET, TOKEN, ACCOUNT_ID
from scripts.ob_public_local_probe import _ACCOUNTS
from tower.ob_public_owner_connection import (
    PATH, OwnerConnectionStore, _now, create_public_owner_blueprint,
)
from tower.ob_route_guard import match_ob_guard_policy
from tower.ob_web_route_enforcement import PROTECTED_EXACT_OB_ROUTES

@pytest.fixture
def setup(monkeypatch):
    monkeypatch.setenv("OB_PUBLIC_OWNER_CONNECT_ENABLED", "1")
    for field in ("ACCOUNT_SCOPE_REVIEWED","NONDISPLAY_REVIEWED","OWNER_DISPLAY_REVIEWED",
                  "MARKETDATA_SCOPE_VERIFIED","EQUITY_ENTITLED","OPTION_ENTITLED"):
        monkeypatch.delenv("OB_PUBLIC_"+field,raising=False)
    recorder = Recorder()
    store = OwnerConnectionStore()
    state = {"authorized": False}
    app = Flask(__name__, template_folder="../web/templates", static_folder="../web/static")
    app.secret_key = "synthetic-only-secret"
    app.config["TESTING"] = True
    app.register_blueprint(create_public_owner_blueprint(
        owner_authorize=lambda: state["authorized"], opener=recorder, store=store))
    client = app.test_client()
    with client.session_transaction(base_url="https://tower.test") as s:
        s["tower_session_id"] = "tower_session_" + "x"*30
    return client, state, store, recorder

def page(client):
    return client.get(PATH, base_url="https://tower.test")

def csrf(html):
    x = re.search(r'name="csrf" value="([^"]+)"',html)
    assert x
    return x.group(1)

def post(client, token, *, action="connect", secret=SECRET, extra=None, origin="https://tower.test"):
    data = {"csrf": token,"operation":action}
    if action=="connect": data["secret"]=secret
    data.update(extra or {})
    return client.post(PATH,base_url="https://tower.test",data=data,
                       headers={"Origin":origin,"Sec-Fetch-Site":"same-origin"})

def test_owner_step_up_and_exact_guard_default_denial(setup):
    client,state,store,rec=setup
    assert page(client).status_code==403
    state["authorized"]=True
    assert page(client).status_code==200
    assert PATH in PROTECTED_EXACT_OB_ROUTES
    assert match_ob_guard_policy(PATH)["match_type"]=="exact"
    assert match_ob_guard_policy(PATH+"/other")["match_type"]=="unmapped_default_deny"
    state["authorized"]=False
    assert post(client,"wrong").status_code==403
    assert not rec.calls

def test_connection_key_only_in_post_not_cookie_disk_or_html(setup):
    client,state,store,rec=setup;state["authorized"]=True
    token=csrf(page(client).get_data(as_text=True))
    response=post(client,token)
    assert response.status_code==303
    html=page(client).get_data(as_text=True)
    assert "Authenticated" in html
    assert "One BROKERAGE account" in html
    assert SECRET not in html and TOKEN not in html and ACCOUNT_ID not in html
    with client.session_transaction(base_url="https://tower.test") as sess:
        assert SECRET not in str(dict(sess))
        assert TOKEN not in str(dict(sess))
        assert ACCOUNT_ID not in str(dict(sess))
    record=store.get("tower_session_"+"x"*30)
    assert record.access_token==TOKEN and record.account_id==ACCOUNT_ID
    assert not hasattr(record,"secret")
    assert len(rec.calls)==2
    assert response.headers["Cache-Control"].startswith("no-store")
    assert response.headers["Referrer-Policy"]=="same-origin"
    assert page(client).headers["Referrer-Policy"]=="same-origin"
    assert page(client).headers["X-Frame-Options"]=="DENY"

def test_bad_csrf_bad_origin_and_cross_site_never_read_secret(setup):
    client,state,store,rec=setup;state["authorized"]=True
    valid=csrf(page(client).get_data(as_text=True))
    bad_csrf=post(client,"wrong")
    assert bad_csrf.status_code==403 and "CSRF_HOLD" in bad_csrf.get_data(as_text=True)
    mismatched=post(client,valid,origin="https://attacker.example")
    assert mismatched.status_code==403 and "ORIGIN_EXPECTED_HOST_HOLD" in mismatched.get_data(as_text=True)
    assert SECRET not in mismatched.get_data(as_text=True)
    assert not rec.calls

def test_default_off_connect_without_provider_traffic(setup,monkeypatch):
    client,state,store,rec=setup;state["authorized"]=True
    existing_csrf=csrf(page(client).get_data(as_text=True))
    monkeypatch.delenv("OB_PUBLIC_OWNER_CONNECT_ENABLED")
    html=page(client).get_data(as_text=True)
    assert "switched off" in html
    assert post(client,existing_csrf).status_code==403
    assert not rec.calls

def test_quote_rights_default_hold_without_vendor_call(setup):
    client,state,store,rec=setup;state["authorized"]=True
    key=csrf(page(client).get_data(as_text=True))
    post(client,key)
    assert len(rec.calls)==2
    response=post(client,key,action="quote",extra={"symbol":"AAPL","kind":"EQUITY"})
    assert response.status_code==303 and len(rec.calls)==2
    assert "Quote held" in page(client).get_data(as_text=True)

def test_quote_after_explicit_independent_rights_stays_source_only(setup,monkeypatch):
    client,state,store,rec=setup;state["authorized"]=True
    key=csrf(page(client).get_data(as_text=True))
    post(client,key)
    for flag in ("ACCOUNT_SCOPE_REVIEWED","NONDISPLAY_REVIEWED","OWNER_DISPLAY_REVIEWED",
                 "MARKETDATA_SCOPE_VERIFIED","EQUITY_ENTITLED"):
        monkeypatch.setenv("OB_PUBLIC_"+flag,"1")
    assert post(client,key,action="quote",extra={"symbol":"AAPL","kind":"EQUITY"}).status_code==303
    html=page(client).get_data(as_text=True)
    assert "101.1" in html and "SOURCE RESPONSE" in html
    assert "not installed" in html.lower()
    assert len(rec.calls)==3
    monkeypatch.delenv("OB_PUBLIC_OWNER_DISPLAY_REVIEWED")
    assert "101.1" not in page(client).get_data(as_text=True)
    assert all("/orders" not in r.full_url and "/preflight" not in r.full_url for r,t in rec.calls)
    # Option rights cannot be inferred from a stock grant.
    assert "OPTION" not in re.findall(r'<option value="([^"]+)"',html)

def test_disconnect_and_expiry_erase_in_memory_token(setup):
    client,state,store,rec=setup;state["authorized"]=True
    key=csrf(page(client).get_data(as_text=True))
    post(client,key)
    assert post(client,key,action="disconnect").status_code==303
    assert store.get("tower_session_"+"x"*30) is None
    post(client,key)
    record=store.get("tower_session_"+"x"*30)
    record.expires_at=_now()-timedelta(seconds=1)
    assert store.get("tower_session_"+"x"*30) is None
    assert "Not connected" in page(client).get_data(as_text=True)

def test_owner_connection_does_not_register_orders_or_live_gateway(setup):
    client,state,store,rec=setup
    app=client.application
    assert sorted(str(r.rule) for r in app.url_map.iter_rules() if r.rule.startswith("/ob/")) == [PATH]
    assert not any("order" in r.rule for r in app.url_map.iter_rules())

def test_real_browser_form_without_origin_requires_fetch_metadata_and_csrf(setup):
    client,state,store,rec=setup; state["authorized"]=True
    token=csrf(page(client).get_data(as_text=True))
    data={"csrf":token, "operation":"connect", "secret":SECRET}
    # Some privacy clients omit Origin on normal form submissions. A verified
    # same-origin browser navigation + session CSRF remains acceptable.
    success=client.post(PATH,base_url="https://tower.test",data=data,
        headers={"Sec-Fetch-Site":"same-origin","Sec-Fetch-Mode":"navigate"})
    assert success.status_code==303
    assert len(rec.calls)==2
    assert "Authenticated" in page(client).get_data(as_text=True)

def test_missing_origin_without_affirmative_browser_metadata_holds(setup):
    client,state,store,rec=setup; state["authorized"]=True
    token=csrf(page(client).get_data(as_text=True))
    data={"csrf":token, "operation":"connect", "secret":SECRET}
    for headers in ({}, {"Sec-Fetch-Site":"cross-site","Sec-Fetch-Mode":"navigate"},
                    {"Sec-Fetch-Site":"same-site","Sec-Fetch-Mode":"navigate"}):
        response=client.post(PATH,base_url="https://tower.test",data=data,headers=headers)
        assert response.status_code==403
        assert "HOLD" in response.get_data(as_text=True)
        assert SECRET not in response.get_data(as_text=True)
    assert not rec.calls

def test_exact_configured_render_public_origin_when_proxy_host_differs(setup,monkeypatch):
    client,state,store,rec=setup; state["authorized"]=True
    token=csrf(page(client).get_data(as_text=True))
    # Flask sees the proxy-facing tower.test Host but the browser Origin is
    # the actual approved Render HTTPS address, configured per service.
    monkeypatch.setenv("RENDER_SERVICE_ID","srv-synthetic")
    monkeypatch.setenv("OB_PUBLIC_OWNER_CANONICAL_ORIGIN","https://simplee-tower-ob-tunv.onrender.com")
    good=post(client,token,origin="https://simplee-tower-ob-tunv.onrender.com")
    assert good.status_code==303 and len(rec.calls)==2
    response=post(client,token,origin="https://attacker.example")
    assert response.status_code==403 and "ORIGIN_EXPECTED_HOST_HOLD" in response.get_data(as_text=True)
    assert len(rec.calls)==2

def test_bad_host_config_and_opaque_origin_are_diagnostic_and_fail_closed(setup,monkeypatch):
    client,state,store,rec=setup;state["authorized"]=True
    token=csrf(page(client).get_data(as_text=True))
    monkeypatch.setenv("RENDER_SERVICE_ID","srv-synthetic")
    config_missing=post(client,token)
    assert config_missing.status_code==403
    assert "ORIGIN_CONFIG_HOLD" in config_missing.get_data(as_text=True)
    monkeypatch.setenv("OB_PUBLIC_OWNER_CANONICAL_ORIGIN","https://bad.invalid:abc")
    config_bad=post(client,token)
    assert config_bad.status_code==403
    assert "ORIGIN_CONFIG_HOLD" in config_bad.get_data(as_text=True)
    monkeypatch.setenv("OB_PUBLIC_OWNER_CANONICAL_ORIGIN","https://tower.test")
    opaque=post(client,token,origin="null")
    assert opaque.status_code==403
    assert "ORIGIN_OPAQUE_HOLD" in opaque.get_data(as_text=True)
    assert opaque.headers["Referrer-Policy"]=="same-origin"
    assert SECRET not in opaque.get_data(as_text=True)
    assert not rec.calls

def test_configured_origin_absent_privacy_browser_same_origin_csrf_succeeds(setup,monkeypatch):
    client,state,store,rec=setup;state["authorized"]=True
    token=csrf(page(client).get_data(as_text=True))
    monkeypatch.setenv("RENDER_SERVICE_ID","srv-synthetic")
    monkeypatch.setenv("OB_PUBLIC_OWNER_CANONICAL_ORIGIN","https://tower.test")
    data={"csrf":token, "operation":"connect", "secret":SECRET}
    result=client.post(PATH,base_url="https://tower.test",data=data,
                       headers={"Sec-Fetch-Site":"same-origin"})
    assert result.status_code==303 and len(rec.calls)==2
    wrong=client.post(PATH,base_url="https://tower.test",data=data,
                      headers={"Sec-Fetch-Site":"same-site"})
    assert wrong.status_code==403 and len(rec.calls)==2

def test_owner_and_disabled_feature_form_holds_are_specific_without_secret(setup,monkeypatch):
    client,state,store,rec=setup
    key=csrf(page(client).get_data(as_text=True)) if state["authorized"] else "synthetic"
    denied=post(client,key)
    assert denied.status_code==403 and "OWNER_GATE_HOLD" in denied.get_data(as_text=True)
    assert SECRET not in denied.get_data(as_text=True)
    state["authorized"]=True
    key=csrf(page(client).get_data(as_text=True))
    monkeypatch.delenv("OB_PUBLIC_OWNER_CONNECT_ENABLED",raising=False)
    disabled=post(client,key)
    assert disabled.status_code==403 and "CONNECT_DISABLED_HOLD" in disabled.get_data(as_text=True)
    assert not rec.calls


def test_html_form_referrer_policy_preserves_origin_and_is_cross_site_private(setup):
    client,state,store,rec=setup; state["authorized"]=True
    first=page(client)
    assert first.status_code==200
    assert first.headers["Referrer-Policy"]=="same-origin"
    # Prior no-referrer page policy made ordinary browser HTML form POSTs send
    # Origin:null, which the strict Origin checker correctly denied. Preserve
    # that checker; fix the page's initiating policy, including error screens.
    token=csrf(first.get_data(as_text=True))
    malformed=post(client,token,origin="null")
    assert malformed.status_code==403
    assert malformed.headers["Referrer-Policy"]=="same-origin"
    assert "ORIGIN_OPAQUE_HOLD" in malformed.get_data(as_text=True)
    assert not rec.calls
    accepted=post(client,token,origin="https://tower.test")
    assert accepted.status_code==303
    assert accepted.headers["Referrer-Policy"]=="same-origin"
    assert len(rec.calls)==2


def _alternate_account_response(monkeypatch, recorder, accounts):
    """Synthetic vendor account-list response. No real account data ever used."""
    original = Recorder.__call__
    def replacement(self, req, timeout):
        if req.full_url == _ACCOUNTS:
            self.calls.append((req, timeout))
            return Response({"accounts": accounts})
        return original(self, req, timeout)
    monkeypatch.setattr(Recorder, "__call__", replacement)


def test_unique_entity_account_is_recognized_not_misreported_as_brokerage(setup,monkeypatch):
    client,state,store,rec=setup; state["authorized"]=True
    entity_id="synthetic-entity-12345"
    _alternate_account_response(monkeypatch,rec,[
        {"accountId":entity_id,"accountType":"ENTITY"}])
    key=csrf(page(client).get_data(as_text=True))
    assert post(client,key).status_code==303
    html=page(client).get_data(as_text=True)
    assert "Public authenticated" in html
    assert "One ENTITY account" in html
    assert entity_id not in html and TOKEN not in html and SECRET not in html
    item=store.get("tower_session_"+"x"*30)
    assert item.account_id==entity_id and item.account_kind=="ENTITY"
    assert len(rec.calls)==2


def test_multiple_accounts_require_explicit_owner_selection_and_no_identity_leak(setup,monkeypatch):
    client,state,store,rec=setup; state["authorized"]=True
    first,second="synthetic-broker-123456","synthetic-entity-654321"
    _alternate_account_response(monkeypatch,rec,[
        {"accountId":first,"accountType":"BROKERAGE"},
        {"accountId":second,"accountType":"ENTITY"},
        {"accountId":"synthetic-cash-3333","accountType":"HIGH_YIELD_CASH"}])
    key=csrf(page(client).get_data(as_text=True))
    assert post(client,key).status_code==303
    html=page(client).get_data(as_text=True)
    assert "Choose one of 2 accounts" in html
    assert "BROKERAGE" in html and "ENTITY" in html
    assert first not in html and second not in html and TOKEN not in html and SECRET not in html
    assert "123456" not in html and "654321" not in html
    item=store.get("tower_session_"+"x"*30)
    assert item.account_id=="" and len(item.candidates)==2
    with client.session_transaction(base_url="https://tower.test") as sess:
        assert first not in str(dict(sess)) and second not in str(dict(sess))
        assert TOKEN not in str(dict(sess))
    # Invalid or arbitrary choices do not silently select first account.
    assert post(client,key,action="select",extra={"account_index":"0"}).status_code==303
    assert item.account_id==""
    assert post(client,key,action="select",extra={"account_index":"2"}).status_code==303
    html=page(client).get_data(as_text=True)
    assert "Selected ENTITY account" in html and second not in html
    assert item.account_id==second and item.account_kind=="ENTITY" and item.candidates==()
    assert len(rec.calls)==2


def test_no_supported_types_are_diagnosed_not_labeled_bad_credentials(setup,monkeypatch):
    client,state,store,rec=setup;state["authorized"]=True
    _alternate_account_response(monkeypatch,rec,[
        {"accountId":"synthetic-cash-3333","accountType":"HIGH_YIELD_CASH"}])
    key=csrf(page(client).get_data(as_text=True))
    assert post(client,key).status_code==303
    html=page(client).get_data(as_text=True)
    assert "Public accepted authentication and returned accounts" in html
    assert "Not connected" in html
    assert store.get("tower_session_"+"x"*30) is None
    assert len(rec.calls)==2


def test_empty_and_duplicate_accounts_fail_closed_with_specific_diagnostic(setup,monkeypatch):
    client,state,store,rec=setup;state["authorized"]=True
    original=Recorder.__call__
    responses=[[],[
        {"accountId":"synthetic-dup-1111","accountType":"BROKERAGE"},
        {"accountId":"synthetic-dup-1111","accountType":"ENTITY"}]]
    def replacement(self,req,timeout):
        if req.full_url==_ACCOUNTS:
            self.calls.append((req,timeout))
            return Response({"accounts":responses.pop(0)})
        return original(self,req,timeout)
    monkeypatch.setattr(Recorder,"__call__",replacement)
    key=csrf(page(client).get_data(as_text=True))
    assert post(client,key).status_code==303
    assert "returned no accounts" in page(client).get_data(as_text=True)
    assert post(client,key).status_code==303
    assert "unexpected structure" in page(client).get_data(as_text=True)
    assert store.get("tower_session_"+"x"*30) is None
    assert len(rec.calls)==4


def test_pending_selection_expires_without_exposing_account_or_contacting_vendor(setup,monkeypatch):
    client,state,store,rec=setup;state["authorized"]=True
    _alternate_account_response(monkeypatch,rec,[
        {"accountId":"synthetic-broker-123456","accountType":"BROKERAGE"},
        {"accountId":"synthetic-entity-654321","accountType":"ENTITY"}])
    key=csrf(page(client).get_data(as_text=True))
    post(client,key)
    item=store.get("tower_session_"+"x"*30)
    item.expires_at=_now()-timedelta(seconds=1)
    answer=post(client,key,action="select",extra={"account_index":"1"})
    assert answer.status_code==303
    html=page(client).get_data(as_text=True)
    assert "Account selection expired" in html and "Not connected" in html
    assert len(rec.calls)==2
