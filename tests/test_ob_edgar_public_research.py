"""Offline acceptance for real SEC transport and research wiring. Never calls SEC."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import io
import json
from urllib.error import HTTPError

import pytest

from engine.market_intake.sec_public_client import (
    EDGARPublicClient, SECResearchUnavailable, SEC_TICKERS,
)
from engine.market_intake.sec_public_research import (
    EDGARPolicy, EDGARResearchCollector, accepted_recent_accessions,
    exact_sec_identity,
)
from engine.market_intake.universe import SymbolRow
from engine.market_intake.research_memory import soulaana_research_brief


NOW = datetime(2026, 9, 29, 12, 0, tzinfo=timezone.utc)
SEC_API = "https://www.sec.gov/search-filings/edgar-application-programming-interfaces"
CIK = "0000320193"
ACC = "0000320193-26-000001"
ST = "2026-09-28T14:30:00Z"
INDEX = {"fields": ["cik", "name", "ticker", "exchange"],
         "data": [[320193, "Apple Inc.", "AAPL", "Nasdaq"]]}
SUBS = {
    "cik": 320193,
    "filings": {"recent": {
        "accessionNumber": [ACC], "form": ["10-Q"],
        "acceptanceDateTime": [ST],
        "primaryDocument": ["sample-filing.htm"],
    }},
}
FACTS = {
    "cik": 320193, "facts": {"us-gaap": {
        "Assets": {"units": {"USD": [{
            "accn": ACC, "form": "10-Q", "end": "2026-06-30",
            "filed": "2026-09-28", "val": 2000000000,
        }]}},
    }},
}


class FakeResponse:
    status = 200
    headers = {"Content-Type": "application/json; charset=utf-8"}

    def __init__(self, url, payload, *, actual_url=None):
        self.url = actual_url or url
        self.file = io.BytesIO(json.dumps(payload).encode())

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def geturl(self):
        return self.url

    def read(self, n):
        return self.file.read(n)


class FakeOpener:
    def __init__(self, payloads):
        self.payloads = payloads
        self.calls = []

    def open(self, request, timeout):
        self.calls.append(request)
        return FakeResponse(request.full_url, self.payloads[request.full_url])


def fixtures():
    urls = {
        SEC_TICKERS: INDEX,
        f"https://data.sec.gov/submissions/CIK{CIK}.json": SUBS,
        f"https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK}.json": FACTS,
    }
    opener = FakeOpener(urls)
    client = EDGARPublicClient("research@example.org", opener=opener, sleeper=lambda _: None)
    policy = EDGARPolicy(SEC_API, NOW - timedelta(days=2), True, True, True)
    row = SymbolRow("AAPL", "Apple Inc.", "NASDAQ", "nasdaqlisted.txt",
                    NOW - timedelta(days=2))
    return opener, client, policy, row


def test_no_api_key_no_account_and_only_official_endpoints():
    opener, client, _, _ = fixtures()
    payload, stamp = client.ticker_directory()
    assert payload["data"][0][2] == "AAPL"
    assert stamp.tzinfo is not None
    assert "Simplee World Observatory" in opener.calls[0].get_header("User-agent")
    assert "research@example.org" in opener.calls[0].get_header("User-agent")
    assert not any("authorization" in k.lower() or "api-key" in k.lower()
                   for k, _ in opener.calls[0].header_items())
    assert client.submissions(CIK)[0]["cik"] == 320193
    assert client.companyfacts(CIK)[0]["cik"] == 320193
    assert len(opener.calls) == 3
    for invalid in ("https://example.org/submissions/CIK0000320193.json",
                    "http://data.sec.gov/submissions/CIK0000320193.json",
                    "https://data.sec.gov/submissions/CIK0000320193.json?x=y",
                    "https://data.sec.gov/api/xbrl/frames/us-gaap.json"):
        with pytest.raises(ValueError):
            client._get_json(invalid, max_bytes=100)
    for invalid in ("320193", "000032019X", "../0000320193"):
        with pytest.raises(ValueError):
            client.submissions(invalid)


def test_throttle_and_bounded_payload_fail_closed():
    moments = [100.0]
    sleeps = []
    def sleep(seconds):
        sleeps.append(seconds)
        moments[0] += seconds
    opener, _, _, _ = fixtures()
    client = EDGARPublicClient("research@example.org", opener=opener,
                               clock=lambda: moments[0], sleeper=sleep)
    client.ticker_directory()
    client.ticker_directory()
    assert len(sleeps) == 1 and sleeps[0] >= 0.5
    with pytest.raises(SECResearchUnavailable, match="SEC_RESPONSE_TOO_LARGE"):
        client._get_json(SEC_TICKERS, max_bytes=1)
    with pytest.raises(ValueError):
        EDGARPublicClient("research@example.org", spacing_seconds=0.1)
    with pytest.raises(ValueError):
        EDGARPublicClient("contact@example.invalid")


def test_redirect_error_and_wrong_content_are_not_followed():
    opener, _, _, _ = fixtures()
    client = EDGARPublicClient("research@example.org", opener=opener)
    class RedirectOpener:
        def open(self, req, timeout):
            return FakeResponse(req.full_url, INDEX, actual_url="https://evil.example.net/")
    client._opener = RedirectOpener()
    with pytest.raises(SECResearchUnavailable, match="SEC_SOURCE_UNAVAILABLE"):
        client.ticker_directory()
    class ErrorOpener:
        def open(self, req, timeout):
            raise HTTPError(req.full_url, 429, "rate limited", {}, None)
    client._opener = ErrorOpener()
    with pytest.raises(SECResearchUnavailable, match="SEC_SOURCE_UNAVAILABLE"):
        client.ticker_directory()


def test_requires_explicit_policy_owner_and_worker_controls():
    opener, client, policy, row = fixtures()
    with pytest.raises(SECResearchUnavailable, match="OWNER_AUTHORIZATION_REQUIRED"):
        EDGARResearchCollector(client, policy, owner_authorized=False, single_worker_confirmed=True)
    with pytest.raises(SECResearchUnavailable, match="SEC_ORG_RATE_LIMIT_REVIEW_REQUIRED"):
        EDGARResearchCollector(client, policy, owner_authorized=True)
    with pytest.raises(SECResearchUnavailable, match="SEC_RIGHTS_REVIEW_PENDING"):
        EDGARResearchCollector(client, EDGARPolicy(SEC_API, NOW, False, True, False),
                               owner_authorized=True, single_worker_confirmed=True)
    assert opener.calls == []


def test_exact_cik_and_existing_exchange_identity_are_required():
    opener, client, policy, row = fixtures()
    index = EDGARResearchCollector(client, policy, owner_authorized=True,
                                   single_worker_confirmed=True).public_ticker_index()
    assert exact_sec_identity(row, index).sec_cik == CIK
    with pytest.raises(SECResearchUnavailable, match="SEC_IDENTITY_NOT_MATCHED"):
        exact_sec_identity(row, {})
    with pytest.raises(SECResearchUnavailable, match="SEC_IDENTITY_CONFLICT"):
        exact_sec_identity(SymbolRow("AAPL", "Apple Inc.", "NASDAQ", "nasdaqlisted.txt",
                                     NOW - timedelta(days=2), sec_cik="0000000001"), index)


def test_real_source_shapes_reach_existing_research_without_quote_or_trade_authority():
    opener, client, policy, row = fixtures()
    collector = EDGARResearchCollector(client, policy, owner_authorized=True,
                                       single_worker_confirmed=True)
    index = collector.public_ticker_index()
    inputs = collector.collect_symbol(row, index)
    result = collector.owner_snapshot(row, index)
    assert inputs.identity.sec_cik == CIK
    assert len(inputs.financial_facts) == 1
    assert inputs.financial_facts[0].value == 2000000000
    assert len(inputs.issuer_events) == 1
    assert result["schema"] == "OB_SYMBOL_RESEARCH_RECORD_V1"
    assert result["fundamentals"]["state"] == "SOURCE_BOUND"
    assert result["scanner"]["state"] == "NOT_CONNECTED"
    assert result["candidate_admitted"] is False
    assert result["manual_live_authorized"] is False
    assert result["broker_quote_verified"] is False
    assert result["execution_authorized"] is False
    assert result["history_is_not_a_live_quote"] is True
    brief = soulaana_research_brief(result)
    assert brief["can_authorize_trading"] is False
    assert brief["symbol"] == "AAPL"
    assert not any("real-time quote" in s.lower() for s in brief["statements"])


def test_future_or_unverifiable_acceptance_never_turns_into_history():
    source = {"filings": {"recent": {
        "accessionNumber": [ACC, "0000320193-26-000002", "0000320193-26-000003"],
        "form": ["10-Q"] * 3,
        "acceptanceDateTime": [ST, "2026-10-01T00:00:00Z", "2026-09-28T10:00:00"],
    }}}
    accepted = accepted_recent_accessions(source, received_at=NOW)
    assert list(accepted) == [ACC]
    source["filings"]["recent"]["form"] = []
    with pytest.raises(SECResearchUnavailable, match="SEC_SUBMISSIONS_INVALID"):
        accepted_recent_accessions(source, received_at=NOW)
