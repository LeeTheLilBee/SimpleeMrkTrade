"""Synthetic-only acceptance for five commercial-use-reviewed official catalyst adapters."""
from __future__ import annotations
from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.error import HTTPError

import pytest
from flask import Flask

from engine.market_intake.official_catalyst_sources import (
    OfficialCatalystClient, SourceHold, FEDERAL_REGISTER, CFTC, NWS, WORLD_BANK,
    WORLD_BANK_METADATA, EIA, REFERENCES,
)
from engine.market_intake.official_catalyst_radar import (
    OfficialCatalystRadar, SOURCES, reviewed_sources, reviewed_soulaana_sources,
    translate_for_soulaana,
)
from web.ob_official_catalyst_route import PATH, create_official_catalyst_blueprint

ROOT = Path(__file__).resolve().parent.parent
NOW = datetime.now(timezone.utc)

FR = {"results": [
    {"title": "Example SEC disclosure proposal", "type": "Proposed Rule",
     "publication_date": "2025-08-19", "document_number": "2025-12345",
     "html_url": "https://www.federalregister.gov/d/2025-12345"},
]}
COT = [{"report_date_as_yyyy_mm_dd": "2025-08-19T00:00:00.000",
        "market_and_exchange_names": "SYNTHETIC TREASURY FUTURES - EXCHANGE"}]
NWS_PACKET = {"features": [{
    "properties": {"status": "Actual", "event": "Synthetic wind warning",
                   "effective": "2025-08-19T16:00:00+00:00",
                   "@id": "https://api.weather.gov/alerts/urn:oid:synthetic"},
}]}
WB_META = [{"page": 1}, [{"id": "NY.GDP.MKTP.CD", "source": {"id": "2"}}]]
WB_DATA = [{"page": 1}, [
    {"indicator": {"id": "NY.GDP.MKTP.CD"}, "countryiso3code": "USA",
     "date": "2025", "value": 28800000000000},
    {"indicator": {"id": "NY.GDP.MKTP.CD"}, "countryiso3code": "USA",
     "date": "2024", "value": 27200000000000},
]]
EIA_DATA = {"response": {"data": [
    {"period": "2025-08-15", "value": "420000"},
    {"period": "2025-08-08", "value": "419000"},
]}}


class Response:
    status = 200
    def __init__(self, url, content):
        self.url = url
        self.content = content if isinstance(content, bytes) else json.dumps(content).encode()
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def geturl(self): return self.url
    def read(self, limit): return self.content[:limit]


class Transport:
    def __init__(self):
        self.requests = []
        self.responses = {
            FEDERAL_REGISTER: FR,
            CFTC: COT,
            NWS: NWS_PACKET,
            WORLD_BANK: WB_DATA,
            WORLD_BANK_METADATA: WB_META,
        }
    def __call__(self, request, *, timeout):
        self.requests.append((request.full_url, request.get_method(), timeout,
                              dict(request.header_items())))
        if request.full_url.startswith(EIA + "?"):
            return Response(request.full_url, EIA_DATA)
        assert request.full_url in self.responses
        return Response(request.full_url, self.responses[request.full_url])


def service(*, enabled=frozenset(SOURCES), ai=frozenset(SOURCES), key=None):
    transport = Transport()
    radar = OfficialCatalystRadar(
        enabled=enabled, ai_sources=ai,
        client=OfficialCatalystClient(opener=transport),
        eia_key=key, now=lambda: NOW,
    )
    return radar, transport


def test_default_off_requires_three_independent_reviews_and_world_bank_indicator():
    env = {"OB_CATALYST_RADAR_ENABLED": "1", "OB_CATALYST_SOULAANA_ENABLED": "1"}
    assert reviewed_sources(env) == frozenset()
    for field in ("COMMERCIAL_REUSE_REVIEWED", "AUTOMATED_USE_REVIEWED",
                  "OWNER_DISPLAY_REVIEWED"):
        env["OB_CATALYST_CFTC_" + field] = "1"
    assert reviewed_sources(env) == frozenset({"cftc"})
    assert reviewed_soulaana_sources(reviewed_sources(env), env) == frozenset()
    env["OB_CATALYST_CFTC_SOULAANA_CONTENT_REVIEWED"] = "1"
    assert reviewed_soulaana_sources(reviewed_sources(env), env) == frozenset({"cftc"})
    for field in ("COMMERCIAL_REUSE_REVIEWED", "AUTOMATED_USE_REVIEWED",
                  "OWNER_DISPLAY_REVIEWED", "SOULAANA_CONTENT_REVIEWED"):
        env["OB_CATALYST_WORLD_BANK_" + field] = "1"
    assert reviewed_sources(env) == frozenset({"cftc"})  # exception check
    env["OB_CATALYST_WORLD_BANK_GDP_LICENSE_REVIEWED"] = "1"
    assert reviewed_sources(env) == frozenset({"cftc", "world_bank"})
    env["OB_CATALYST_RADAR_ENABLED"] = "0"
    assert reviewed_sources(env) == frozenset()


def test_all_unreviewed_are_hold_and_do_not_trigger_transport():
    radar, transport = service(enabled=frozenset(), ai=frozenset())
    packet = radar.snapshot()
    assert packet["schema"] == "OB_OFFICIAL_CATALYST_RADAR_V1"
    assert all(x["state"] == "REVIEW_HOLD" and not x["facts"]
               for x in packet["sources"][:-1])
    assert packet["sources"][-1]["state"] == "EXISTING_PROTECTED_CORRIDOR"
    assert packet["soulaana"]["observations"] == []
    assert not transport.requests
    assert packet["prices_attached"] is False
    assert packet["broker_execution_authorized"] is False


def test_five_official_source_parsers_and_source_specific_translations():
    radar, transport = service(key="SYNTHETICKEY1234567")
    packet = radar.snapshot()
    rows = {x["source"]: x for x in packet["sources"]}
    assert all(rows[key]["state"] == "SOURCE_BOUND" for key in SOURCES)
    assert rows["federal_register"]["facts"][0]["stage"] == "Proposed Rule"
    assert rows["cftc"]["facts"][0]["category"] == "TFF_FUTURES_ONLY"
    assert rows["eia"]["facts"][0]["value"] == "420000"
    assert rows["world_bank"]["facts"][0]["category"] == "ANNUAL_GDP_USD"
    assert rows["nws"]["facts"][0]["title"] == "Synthetic wind warning"
    soulaana = packet["soulaana"]
    assert soulaana["observation_count"] == 5
    assert [x["source"] for x in soulaana["observations"]] == list(SOURCES)
    assert soulaana["external_model_called"] is False
    assert soulaana["candidate_admitted"] is False
    assert soulaana["broker_execution_authorized"] is False
    assert "A proposed rule is not a final rule" in soulaana["observations"][0]["how_to_interpret"]
    assert "NOT a live options chain" in soulaana["observations"][1]["how_to_interpret"]
    assert "not CPI" in soulaana["observations"][3]["how_to_interpret"]
    assert len(transport.requests) == 6  # World Bank metadata is separately checked.
    assert all(request[1] == "GET" and request[2] == 8 for request in transport.requests)
    assert "SYNTHETICKEY1234567" not in json.dumps(packet)
    assert rows["sec_edgar"]["facts"] == []  # existing corridor, no fake filing


def test_no_free_eia_key_does_not_call_eia_or_leak_into_owner_reply():
    radar, transport = service()
    packet = radar.snapshot()
    assert packet["sources"][2]["source"] == "eia"
    assert packet["sources"][2]["state"] == "KEY_REQUIRED"
    assert all(not x[0].startswith(EIA) for x in transport.requests)
    assert all(o["source"] != "eia" for o in packet["soulaana"]["observations"])


def test_independent_ai_review_and_revocation_remove_evidence_even_if_cached():
    radar, transport = service(ai=frozenset({"cftc", "nws"}))
    first = radar.snapshot()
    assert [x["source"] for x in first["soulaana"]["observations"]] == ["cftc", "nws"]
    count = len(transport.requests)
    radar.ai_sources = frozenset()
    cached = radar.snapshot()
    assert cached["soulaana"]["observations"] == []
    assert all(not x["ai_use_approved"] for x in cached["sources"])
    assert len(transport.requests) == count
    radar.enabled = frozenset()
    held = radar.snapshot()
    assert not any(x["facts"] for x in held["sources"])
    assert held["soulaana"]["observations"] == []
    assert len(transport.requests) == count


def test_failed_source_does_not_poison_other_official_sources():
    radar, transport = service(key="SYNTHETICKEY1234567")
    transport.responses[WORLD_BANK_METADATA] = {"unexpected": "shape"}
    packet = radar.snapshot()
    rows = {x["source"]: x for x in packet["sources"]}
    assert rows["world_bank"]["state"] == "SOURCE_HOLD"
    assert rows["world_bank"]["facts"] == []
    assert all(rows[k]["state"] == "SOURCE_BOUND"
               for k in ("federal_register", "cftc", "eia", "nws"))
    assert [x["source"] for x in packet["soulaana"]["observations"]] == [
        "federal_register", "cftc", "eia", "nws"]


def test_synthetic_nws_no_active_alerts_is_not_forecast_or_safety_claim():
    radar, transport = service(enabled=frozenset({"nws"}), ai=frozenset({"nws"}))
    transport.responses[NWS] = {"features": []}
    p = radar.snapshot()
    assert p["sources"][4]["state"] == "SOURCE_BOUND"
    assert p["sources"][4]["facts"] == []
    findings = p["soulaana"]["observations"][0]["factual_findings"]
    assert "No actual active Georgia alerts" in findings[0]
    assert "not a promise" in p["soulaana"]["observations"][0]["how_to_interpret"]


def test_unknown_urls_and_official_host_spoofing_fail_closed():
    transport = Transport()
    client = OfficialCatalystClient(opener=transport)
    with pytest.raises(SourceHold, match="SOURCE_URL_HOLD"):
        client._json("https://api.evil.example/trusted")
    assert transport.requests == []
    transport.responses[FEDERAL_REGISTER] = {"results": [{
        **FR["results"][0], "html_url": "https://evil.example/d/2025-12345"
    }]}
    with pytest.raises(SourceHold, match="SOURCE_URL_HOLD"):
        client.federal_register()


def test_injected_unreviewed_world_bank_metadata_stays_held():
    transport = Transport()
    transport.responses[WORLD_BANK_METADATA] = [
        {"page": 1}, [{"id": "NY.GDP.MKTP.CD", "source": {"id": "999"}}]]
    with pytest.raises(SourceHold, match="WORLD_BANK_METADATA_HOLD"):
        OfficialCatalystClient(opener=transport).world_bank()


def test_same_origin_exact_tower_route_blocks_anonymous_methods_and_arguments():
    import tower.ob_web_route_enforcement as enforcement
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.secret_key = "synthetic-only"
    state = {"owner": False, "step": False, "admit": False}
    original = (enforcement.owner_session_active, enforcement.step_up_active,
                enforcement.operational_ob_access_active)
    enforcement.owner_session_active = lambda: state["owner"]
    enforcement.step_up_active = lambda: state["step"]
    enforcement.operational_ob_access_active = lambda: state["admit"]
    try:
        enforcement.register_ob_protected_route_enforcement(app)
        radar, opened = service(enabled=frozenset(), ai=frozenset())
        app.register_blueprint(create_official_catalyst_blueprint(
            owner_authorize=lambda: all(state.values()), catalyst_service=radar))
        client = app.test_client()
        assert PATH in enforcement.PROTECTED_EXACT_OB_ROUTES
        assert client.get(PATH).status_code == 302
        assert client.head(PATH).status_code == 405
        assert client.post(PATH).status_code == 405
        state["owner"] = state["step"] = state["admit"] = True
        assert client.get(PATH + "/unmapped").status_code == 403
        assert client.get(PATH + "?symbol=MSFT").status_code == 400
        ok = client.get(PATH)
        assert ok.status_code == 200
        assert ok.get_json()["schema"] == "OB_OFFICIAL_CATALYST_RADAR_V1"
        assert ok.headers["Cache-Control"].startswith("private, no-store")
        assert opened.requests == []
    finally:
        (enforcement.owner_session_active, enforcement.step_up_active,
         enforcement.operational_ob_access_active) = original


def test_eight_rooms_share_one_protected_radar_and_no_browser_source_calls():
    rooms = ("market_data_desk", "dashboard", "market_map", "symbol_page",
             "trade_center", "review_center", "owner_dashboard", "owner_console")
    for room in rooms:
        body = (ROOT / "web/templates" / (room + ".html")).read_text()
        assert "/static/ob/ob_official_catalyst_radar.js" in body, room
        assert 'id="obKeylessContextRoot"' in body, room
    script = (ROOT / "web/static/ob/ob_official_catalyst_radar.js").read_text()
    assert '"/ob/research/catalysts.json"' in script
    assert 'credentials: "same-origin"' in script
    assert "textContent" in script
    assert "innerHTML" not in script
    assert "api.eia.gov" not in script
    assert "api.weather.gov/alerts/active" not in script
    assert "publicreporting.cftc.gov/resource" not in script
    assert "broker_execution_authorized === false" in script
