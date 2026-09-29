"""Offline lifecycle/desk route tests; no real quotes or provider sessions."""
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from flask import Flask

from engine.market_intake.contracts import ScanContext, SourceRights
from engine.market_intake.desk_process import (
    CaseState, ConnectionCheck, DeskReceipt, ProviderDeskProcess,
)
from engine.market_intake.desk_projection import build_desk_snapshot
from engine.market_intake.gateway import UniversalMarketGateway
from web.ob_market_data_desk_route import create_market_data_desk_blueprint, _valid

NOW = datetime(2026, 9, 28, 15, 0, tzinfo=timezone.utc)
CONTEXT = ScanContext(NOW, "REGULAR", True)


def receipt(n, *, actor="tower-review:internal"):
    return DeskReceipt("test-receipt-"+str(n), NOW+timedelta(seconds=n),
                       actor, "synthetic-audit-proof-"+str(n), "Synthetic test only; no live feed.")


def rights():
    return SourceRights("source-tradier-equity", "SIP", "reviewed-internal-test-rights",
                        NOW-timedelta(minutes=10), internal_research=True,
                        automated_non_display=True, owner_display=True,
                        real_time_entitled=True, entitled_instruments=frozenset({"equity"}))


def check(**changes):
    defaults=dict(product_key="tradier-equity", source_id="source-tradier-equity",
                  verified_at=NOW+timedelta(seconds=5),
                  transport_authenticated=True, read_only_transport=True,
                  exact_feed_entitled=True, true_provider_event_time_verified=True,
                  canonical_market_time_verified=True, real_time_non_indicative=True,
                  provider_limits_verified=True, receipt_reference="synthetic-test-validation")
    defaults.update(changes)
    return ConnectionCheck(**defaults)


def start():
    desk=ProviderDeskProcess()
    desk.discover(case_id="case1",product_key="tradier-equity",
                  source_id="source-tradier-equity",receipt=receipt(1))
    return desk


def to_config(desk):
    desk.begin_review("case1",receipt(2))
    desk.record_rights("case1",rights(),receipt(3))


def to_approval(desk):
    to_config(desk)
    desk.configuration_verified("case1",backend_secret_reference_verified=True,receipt=receipt(4))
    desk.verify("case1",check(),receipt(6))


def test_owner_workflow_requires_every_gate_and_remains_nontrading():
    desk=start()
    assert desk.status(NOW)["cases"][0]["state"]=="DISCOVERED"
    with pytest.raises(ValueError):
        desk.approve("case1",tower_owner_step_up_verified=True,receipt=receipt(9))
    to_config(desk)
    with pytest.raises(ValueError):
        desk.configuration_verified("case1",backend_secret_reference_verified=False,receipt=receipt(4))
    desk.configuration_verified("case1",backend_secret_reference_verified=True,receipt=receipt(4))
    with pytest.raises(ValueError):
        desk.verify("case1",check(true_provider_event_time_verified=False),receipt(6))
    desk.verify("case1",check(),receipt(6))
    with pytest.raises(ValueError):
        desk.approve("case1",tower_owner_step_up_verified=False,receipt=receipt(7,actor="tower-owner:stepup"))
    with pytest.raises(ValueError):
        desk.approve("case1",tower_owner_step_up_verified=True,receipt=receipt(7))
    desk.approve("case1",tower_owner_step_up_verified=True,
                 receipt=receipt(8,actor="tower-owner:verified-stepup"))
    status=desk.status(NOW+timedelta(seconds=9))
    assert status["cases"][0]["state"]=="OBSERVING"
    assert status["cases"][0]["live_data_connected"] is False
    assert status["execution_authorized"] is False
    assert status["cases"][0]["audit_count"]==6


def test_reference_or_indicative_cannot_become_quote_without_rights():
    for key in ("sec-edgar","nasdaq-directory","occ-reports","alpaca-indicative-options"):
        desk=ProviderDeskProcess()
        desk.discover(case_id="c",product_key=key,source_id="source-tradier-equity",receipt=receipt(1))
        desk.begin_review("c",receipt(2))
        with pytest.raises(ValueError):
            desk.record_rights("c",rights(),receipt(3))
    desk=start();desk.begin_review("case1",receipt(2))
    with pytest.raises(ValueError):
        desk.record_rights("case1",replace(rights(),entitled_instruments=frozenset({"option"})),receipt(3))
    with pytest.raises(ValueError):
        desk.record_rights("case1",replace(rights(),real_time_entitled=False),receipt(3))


def test_receipt_replay_wrong_product_and_bad_verification_denied():
    desk=start()
    with pytest.raises(ValueError):
        desk.begin_review("case1",receipt(1))
    with pytest.raises(ValueError):
        desk.begin_review("case1",receipt(0)) # replayed/retroactive case event
    desk.begin_review("case1",receipt(2));desk.record_rights("case1",rights(),receipt(3))
    desk.configuration_verified("case1",backend_secret_reference_verified=True,receipt=receipt(4))
    for changed in ({"product_key":"alpaca-iex-equity"},{"source_id":"other"},
                    {"read_only_transport":False},{"real_time_non_indicative":False},
                    {"provider_limits_verified":False}):
        with pytest.raises(ValueError):
            desk.verify("case1",check(**changed),receipt(6))


def test_hold_requires_new_case_and_expired_rights_projection_fails_closed():
    desk=start();to_approval(desk)
    desk.hold("case1","Source timestamps invalid",receipt(7))
    assert desk.status(NOW+timedelta(seconds=8))["cases"][0]["state"]=="HOLD"
    with pytest.raises(ValueError):
        desk.approve("case1",tower_owner_step_up_verified=True,
                     receipt=receipt(8,actor="tower-owner:stepup"))
    desk.revoke("case1",receipt(9))
    assert desk.status(NOW+timedelta(seconds=10))["cases"][0]["state"]=="REVOKED"
    with pytest.raises(ValueError):
        desk.revoke("case1",receipt(11))
    with pytest.raises(ValueError):
        desk.discover(case_id="case2",product_key="tradier-equity",
                      source_id="source-tradier-equity",receipt=receipt(12))

    exp=start();exp.begin_review("case1",receipt(2))
    exp.record_rights("case1",replace(rights(),expires_at=NOW+timedelta(seconds=20)),receipt(3))
    assert exp.status(NOW+timedelta(seconds=21))["cases"][0]["state"]=="HOLD"


def test_projection_keeps_no_live_numbers_or_secret_fields():
    gateway=UniversalMarketGateway();desk=start()
    snapshot=build_desk_snapshot(gateway=gateway,process=desk,context=CONTEXT)
    assert snapshot["schema"]=="OB_MARKET_DATA_DESK_V1"
    assert snapshot["summary"]["catalog_products"]>=13
    assert snapshot["summary"]["live_feeds_verified"] is None
    assert snapshot["traffic"]["verified_usage"] is None
    assert snapshot["connection_truth"]=="UNVERIFIED"
    assert _valid(snapshot)
    assert "credential" not in str(snapshot).lower()
    assert not snapshot["safety"]["can_execute"]


def app_for(guard, source):
    app=Flask(__name__, template_folder=str(Path("web/templates").resolve()),
              static_folder=str(Path("web/static").resolve()))
    app.testing=True
    app.register_blueprint(create_market_data_desk_blueprint(
        tower_owner_authorize=guard, protected_snapshot=source))
    return app


def test_exact_protected_route_denies_without_owner_before_snapshot_call():
    touched=[]
    app=app_for(lambda:False,lambda:touched.append(True))
    res=app.test_client().get("/ob/data-desk")
    assert res.status_code==403 and touched==[]
    app2=app_for(lambda:"truthy-but-not-authority",lambda:touched.append(True))
    assert app2.test_client().get("/ob/data-desk").status_code==403
    assert app.test_client().get("/ob/unmapped-data-desk").status_code==404
    assert app.test_client().post("/ob/data-desk").status_code==405


def test_owner_route_only_embeds_sealed_source_only_projection():
    snapshot=build_desk_snapshot(gateway=UniversalMarketGateway(),
                                 process=ProviderDeskProcess(),context=CONTEXT)
    client=app_for(lambda:True,lambda:snapshot).test_client()
    response=client.get("/ob/data-desk")
    assert response.status_code==200
    assert response.headers["Cache-Control"]=="no-store, private"
    assert b"Market Data" in response.data
    assert b'OB_MARKET_DATA_DESK_V1' in response.data
    assert b'data-ob-data-desk-route-enabled="true"' in response.data
    assert b"api_secret" not in response.data and b"access_token" not in response.data
    assert client.head("/ob/data-desk").status_code==200


def test_malformed_snapshot_fails_closed_without_fallback():
    good=build_desk_snapshot(gateway=UniversalMarketGateway(),
                             process=ProviderDeskProcess(),context=CONTEXT)
    for bad in ({**good,"prices_attached":True},
                {**good,"secret_value":"NEVER_EMBED"},
                {**good,"safety":{**good["safety"],"can_execute":True}},
                {**good,"providers":[{"product_key":"tradier","price":99}]},
                {**good,"summary":{**good["summary"],"access_token":"LEAK"}},
                {**good,"traffic":{**good["traffic"],"verified_usage":999}},
                {**good,"soulaana":{**good["soulaana"],"private_account":"LEAK"}}):
        assert not _valid(bad)
        assert app_for(lambda:True,lambda:bad).test_client().get("/ob/data-desk").status_code==503


def test_frontend_is_no_network_no_browser_approval_and_navigation_gated():
    js=Path("web/static/ob/ob_market_data_desk.js").read_text()
    nav=Path("web/static/ob/ob_nav_shell.js").read_text()
    template=Path("web/templates/market_data_desk.html").read_text()
    assert "fetch(" not in js and "WebSocket(" not in js
    assert "localStorage" not in js and "innerHTML" not in js
    assert "data-mdd-filter" in template and "mddDrawer" in template
    assert "data_desk_route_enabled" in template
    assert 'dataset.obDataDeskRouteEnabled === "true"' in nav
    assert '"/ob/data-desk"' in nav
