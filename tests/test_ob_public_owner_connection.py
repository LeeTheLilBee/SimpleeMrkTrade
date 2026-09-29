"""Owner-only Public connect tests use fake HTTP, never actual keys/quotes."""
from datetime import timedelta
import re

from flask import Flask
import pytest

from test_ob_public_local_probe import Recorder, SECRET, TOKEN, ACCOUNT_ID
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
    assert "One brokerage account" in html
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
    assert page(client).headers["X-Frame-Options"]=="DENY"

def test_bad_csrf_bad_origin_and_cross_site_never_read_secret(setup):
    client,state,store,rec=setup;state["authorized"]=True
    valid=csrf(page(client).get_data(as_text=True))
    bad_csrf=post(client,"wrong")
    assert bad_csrf.status_code==403 and "CSRF_HOLD" in bad_csrf.get_data(as_text=True)
    mismatched=post(client,valid,origin="https://attacker.example")
    assert mismatched.status_code==403 and "ORIGIN_HOLD" in mismatched.get_data(as_text=True)
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
                    {"Sec-Fetch-Site":"same-origin","Sec-Fetch-Mode":"cors"}):
        response=client.post(PATH,base_url="https://tower.test",data=data,headers=headers)
        assert response.status_code==403
        assert "HOLD" in response.get_data(as_text=True)
        assert SECRET not in response.get_data(as_text=True)
    assert not rec.calls

def test_approved_render_hostname_origin_when_proxy_host_differs(setup,monkeypatch):
    client,state,store,rec=setup; state["authorized"]=True
    token=csrf(page(client).get_data(as_text=True))
    monkeypatch.setenv("RENDER_EXTERNAL_HOSTNAME","simplee-tower-ob-tunv.onrender.com")
    valid=post(client,token,origin="https://simplee-tower-ob-tunv.onrender.com")
    assert valid.status_code==303 and len(rec.calls)==2
    # A different origin remains rejected even if the browser claims same-origin.
    response=post(client,token,origin="https://attacker.example")
    assert response.status_code==403 and "ORIGIN_HOLD" in response.get_data(as_text=True)

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
