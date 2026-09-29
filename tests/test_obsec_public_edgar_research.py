"""SEC public transport/source/Tower readiness tests: synthetic SEC-shaped fixtures only."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
import os
from urllib.error import HTTPError

import pytest

from engine.market_intake.sec_public_client import (
    EDGARPublicClient, SECResearchUnavailable, SEC_TICKERS,
)
from engine.market_intake.sec_public_research import (
    SECOfficialResearchResolver, SECResearchPolicy, sec_owner_resolver_from_environment,
)
from engine.market_intake.symbol_research import symbol_research_snapshot
from engine.market_intake.research_bridge import project_research
from engine.market_intake.research_memory import soulaana_research_brief


class FakeResponse:
    def __init__(self, url, payload, *, mime="application/json"):
        self.url = url
        self.status = 200
        self.headers = {"Content-Type": mime}
        self.payload = json.dumps(payload).encode()
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def geturl(self):
        return self.url
    def read(self, limit):
        return self.payload[:limit]


class FakeOpener:
    def __init__(self, payloads):
        self.payloads = payloads
        self.calls = []
    def open(self, request, timeout):
        url = request.full_url
        self.calls.append((url, request.get_header("User-agent"), timeout))
        return FakeResponse(url, self.payloads[url])


@pytest.fixture
def sec_fixture():
    cik = "0000320193"
    now = datetime.now(timezone.utc)
    accepted = now - timedelta(days=1)
    end = accepted.date() - timedelta(days=60)
    accession = "0000320193-26-000001"
    ticker = {"fields": ["cik", "name", "ticker", "exchange"],
              "data": [[320193, "Apple Synthetic Test", "AAPL", "Nasdaq"]]}
    submissions = {
        "cik": 320193,
        "filings": {"recent": {
            "accessionNumber": [accession],
            "form": ["10-K"],
            "acceptanceDateTime": [accepted.isoformat()],
            "primaryDocument": ["test.htm"],
        }},
    }
    facts = {"cik": 320193, "facts": {"us-gaap": {
        "Assets": {"units": {"USD": [{
            "accn": accession, "form": "10-K", "end": end.isoformat(),
            "filed": accepted.date().isoformat(), "val": 123456.0,
        }]}}
    }}}
    payloads = {
        SEC_TICKERS: ticker,
        f"https://data.sec.gov/submissions/CIK{cik}.json": submissions,
        f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json": facts,
    }
    return cik, payloads


def setup_resolver(sec_fixture, *, ai=True, opener=None, times=None):
    _, payloads = sec_fixture
    opener = opener or FakeOpener(payloads)
    now = datetime.now(timezone.utc)
    times = times if times is not None else []
    def fake_clock():
        return times[-1] if times else 0.0
    def fake_sleep(seconds):
        times.append((times[-1] if times else 0.0) + seconds)
    client = EDGARPublicClient(
        "operator@simplee-world.com", opener=opener,
        clock=fake_clock, sleeper=fake_sleep, spacing_seconds=0.6)
    policy = SECResearchPolicy(now - timedelta(seconds=5), True, ai)
    return SECOfficialResearchResolver(client, policy), opener, times


def test_real_endpoint_shapes_make_a_source_bound_record_without_prices(sec_fixture):
    resolver, opener, times = setup_resolver(sec_fixture)
    inputs = resolver("symbol_page", "AAPL")
    packet = symbol_research_snapshot(inputs, as_of=inputs.captured_at)
    assert len(opener.calls) == 3
    assert times == [0.6, 1.2]
    assert all(item[1].startswith("Simplee World Observatory public research (") for item in opener.calls)
    assert all(item[2] == 10 for item in opener.calls)
    assert packet["identity"]["cik"] == "0000320193"
    assert packet["identity"]["identity_status"] == "SEC_OFFICIAL_TICKER_CIK_ASSOCIATION_ONLY"
    assert packet["fundamentals"]["state"] == "SOURCE_BOUND"
    assert packet["fundamentals"]["reported_concepts"][0]["value"] == 123456.0
    assert packet["issuer_events"][0]["kind"] == "filing"
    assert packet["historical"]["state"] == "NOT_AVAILABLE"
    assert packet["scanner"]["state"] == "NOT_CONNECTED"
    assert packet["candidate_admitted"] is False
    assert packet["execution_authorized"] is False
    assert packet["manual_live_authorized"] is False
    view = project_research(packet, "symbol_page")
    assert view["may_authorize_order"] is False
    brief = soulaana_research_brief(packet)
    assert brief["can_authorize_trading"] is False


def test_unknown_ticker_never_guesses_a_cik_or_requests_issuer(sec_fixture):
    resolver, opener, _ = setup_resolver(sec_fixture)
    assert resolver("symbol_page", "ZZZZ") is None
    assert len(opener.calls) == 1
    assert resolver("unapproved_room", "AAPL") is None
    assert len(opener.calls) == 1


def test_mismatched_companyfacts_never_becomes_company_research(sec_fixture):
    _, payloads = sec_fixture
    payloads[next(k for k in payloads if "companyfacts" in k)]["cik"] = 111
    resolver, _, _ = setup_resolver(sec_fixture)
    with pytest.raises(ValueError, match="issuer differs"):
        resolver("symbol_page", "AAPL")


def test_missing_ai_review_redacts_values_from_soulaana(sec_fixture):
    resolver, _, _ = setup_resolver(sec_fixture, ai=False)
    inputs = resolver("symbol_page", "AAPL")
    record = symbol_research_snapshot(inputs, as_of=inputs.captured_at)
    assert project_research(record, "symbol_page")["fundamentals"]["state"] == "SOURCE_BOUND"
    brief = project_research(record, "soulaana")
    assert brief["fundamentals"]["state"] == "EXPLANATION_RIGHTS_HOLD"
    assert brief["fundamentals"]["reported_concepts"] == []


def test_public_transport_rejects_arbitrary_urls_invalid_contact_and_redirect(sec_fixture):
    _, payloads = sec_fixture
    client = EDGARPublicClient("operator@simplee-world.com", opener=FakeOpener(payloads))
    with pytest.raises(ValueError, match="Unapproved SEC"):
        client._get_json("https://example.com/private", max_bytes=100)
    with pytest.raises(ValueError, match="contact"):
        EDGARPublicClient("bad\r\nUser-Agent: bad")
    with pytest.raises(ValueError, match="CIK"):
        client.companyfacts("../0000320193")
    class RedirectOpener:
        def open(self, request, timeout):
            return FakeResponse("https://not-sec.example/redirect", {})
    client = EDGARPublicClient("operator@simplee-world.com", opener=RedirectOpener())
    with pytest.raises(SECResearchUnavailable, match="SEC_SOURCE_UNAVAILABLE"):
        client.ticker_directory()


def test_source_failures_do_not_leak_http_error_or_contact():
    class Denied:
        def open(self, request, timeout):
            raise HTTPError(request.full_url, 429, "operator@simplee-world.com", {}, None)
    client = EDGARPublicClient("operator@simplee-world.com", opener=Denied())
    with pytest.raises(SECResearchUnavailable) as failure:
        client.ticker_directory()
    assert str(failure.value) == "SEC_SOURCE_UNAVAILABLE"


def test_opt_in_configuration_default_off_and_fails_closed(monkeypatch):
    for key in ("OB_SEC_PUBLIC_RESEARCH_ENABLED", "OB_SEC_CONTACT_EMAIL",
                "OB_SEC_PUBLIC_USE_REVIEWED", "OB_SEC_OWNER_DISPLAY_REVIEWED",
                "OB_SEC_AI_EXPLANATION_REVIEWED"):
        monkeypatch.delenv(key, raising=False)
    assert sec_owner_resolver_from_environment() is None
    monkeypatch.setenv("OB_SEC_PUBLIC_RESEARCH_ENABLED", "1")
    with pytest.raises(ValueError, match="rights review"):
        sec_owner_resolver_from_environment()
    monkeypatch.setenv("OB_SEC_PUBLIC_USE_REVIEWED", "1")
    with pytest.raises(ValueError, match="owner-display"):
        sec_owner_resolver_from_environment()
    monkeypatch.setenv("OB_SEC_OWNER_DISPLAY_REVIEWED", "1")
    with pytest.raises(ValueError, match="contact"):
        sec_owner_resolver_from_environment()
    monkeypatch.setenv("OB_SEC_CONTACT_EMAIL", "operator@simplee-world.com")
    resolver = sec_owner_resolver_from_environment()
    assert isinstance(resolver, SECOfficialResearchResolver)
    assert resolver.policy.ai_explanation_reviewed is False


def test_old_filing_with_future_acceptance_does_not_enter_research(sec_fixture):
    _, payloads = sec_fixture
    submissions_key = next(k for k in payloads if "submissions" in k)
    payloads[submissions_key]["filings"]["recent"]["acceptanceDateTime"] = [
        (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()]
    resolver, _, _ = setup_resolver(sec_fixture)
    inputs = resolver("symbol_page", "AAPL")
    record = symbol_research_snapshot(inputs, as_of=inputs.captured_at)
    assert record["issuer_events"] == []
    assert record["fundamentals"]["state"] == "NOT_AVAILABLE"
    assert record["scanner"]["state"] == "NOT_CONNECTED"
