"""Official no-key BLS v1 POST is independently tested, never a FRED AI shortcut."""
import json

import pytest

from engine.market_intake.public_research_sources import (
    OwnerResearchPolicy, PublicReferenceClient, PublicResearchUnavailable,
    BLS_BULK_CPI,
)

SERIES = "CUUR0000SA0"
ENDPOINT = "https://api.bls.gov/publicAPI/v1/timeseries/data/"
POLICY = OwnerResearchPolicy(
    source_use_reviewed=True, owner_display_reviewed=True,
    ai_use_reviewed=True, reviewed_sources=frozenset({"bls"}),
    ai_reviewed_sources=frozenset({"bls"}),
)
GOOD = {"status": "REQUEST_SUCCEEDED", "Results": {"series": [{
    "seriesID": SERIES,
    "data": [
        {"year": "2026", "period": "M08", "value": "334.980"},
        {"year": "2026", "period": "M07", "value": "333.918"},
    ],
}]}}


class Reply:
    status = 200
    def __init__(self, doc):
        self.body = json.dumps(doc).encode() if isinstance(doc, (dict, list)) else doc
    def __enter__(self):
        return self
    def __exit__(self, *unused):
        return False
    def read(self, limit):
        return self.body[:limit]


class OfficialTransport:
    def __init__(self, get, post, bulk=b"denied"):
        self.get, self.post, self.bulk = get, post, bulk
        self.calls = []
    def __call__(self, req, timeout):
        url, method = req.full_url, req.get_method()
        self.calls.append((url, method, req.data, timeout))
        if url == ENDPOINT + SERIES and method == "GET":
            return Reply(self.get)
        if url == ENDPOINT and method == "POST":
            assert req.data == b'{"seriesid":["CUUR0000SA0"]}'
            assert req.get_header("Content-type") == "application/json"
            return Reply(self.post)
        if url == BLS_BULK_CPI and method == "GET":
            return Reply(self.bulk)
        raise AssertionError("unexpected endpoint or method")


def test_verified_post_recovers_after_unsuccessful_get(monkeypatch):
    monkeypatch.setenv("OB_KEYLESS_BLS_V1_POST_FALLBACK_ENABLED", "1")
    t = OfficialTransport({"status": "REQUEST_NOT_PROCESSED", "Results": {}}, GOOD)
    observation = PublicReferenceClient(POLICY, opener=t).bls_v1(SERIES)
    assert [(url, method) for url, method, *_ in t.calls] == [
        (ENDPOINT + SERIES, "GET"), (ENDPOINT, "POST")]
    assert observation.provider == "BLS"
    assert observation.source_reference == "https://www.bls.gov/developers/"
    assert observation.period == "2026-M08" and observation.previous_period == "2026-M07"
    assert observation.value == "334.980" and observation.previous_value == "333.918"
    assert observation.ai_use_approved is True
    assert observation.current_quote_eligible is False
    assert observation.broker_execution_authorized is False


def test_good_get_never_calls_post_even_when_enabled(monkeypatch):
    monkeypatch.setenv("OB_KEYLESS_BLS_V1_POST_FALLBACK_ENABLED", "1")
    t = OfficialTransport(GOOD, None)
    assert PublicReferenceClient(POLICY, opener=t).bls_v1(SERIES).value == "334.980"
    assert len(t.calls) == 1 and t.calls[0][1] == "GET"


def test_off_by_default_uses_original_bulk_behavior(monkeypatch):
    monkeypatch.delenv("OB_KEYLESS_BLS_V1_POST_FALLBACK_ENABLED", raising=False)
    bulk = (
        "series_id\\tyear\\tperiod\\tvalue\\tfootnote_codes\\n"
        "CUUR0000SA0\\t2026\\tM08\\t334.980\\t\\n"
        "CUUR0000SA0\\t2026\\tM07\\t333.918\\t\\n"
    ).encode().replace(b"\\t", b"\t").replace(b"\\n", b"\n")
    t = OfficialTransport({"status": "REQUEST_NOT_PROCESSED", "Results": {}}, GOOD, bulk)
    assert PublicReferenceClient(POLICY, opener=t).bls_v1(SERIES).period == "2026-M08"
    assert [method for _, method, *_ in t.calls] == ["GET", "GET"]


def test_post_failure_does_not_become_fake_cpi(monkeypatch):
    monkeypatch.setenv("OB_KEYLESS_BLS_V1_POST_FALLBACK_ENABLED", "1")
    t = OfficialTransport({"status": "REQUEST_NOT_PROCESSED", "Results": {}},
                          {"status": "REQUEST_FAILED", "Results": {}}, b"not official CPI")
    with pytest.raises(PublicResearchUnavailable):
        PublicReferenceClient(POLICY, opener=t).bls_v1(SERIES)
    assert [method for _, method, *_ in t.calls] == ["GET", "POST", "GET"]


def test_post_wrong_series_or_unknown_body_is_blocked_before_network(monkeypatch):
    monkeypatch.setenv("OB_KEYLESS_BLS_V1_POST_FALLBACK_ENABLED", "1")
    t = OfficialTransport(None, None)
    client = PublicReferenceClient(POLICY, opener=t)
    for body in (b'{"seriesid":["CUUR0000SA0","SECRET"]}',
                 b'{"seriesid":["SOME_OTHER"]}', b'{"registrationKey":"secret"}'):
        with pytest.raises(PublicResearchUnavailable, match="SOURCE_ENDPOINT_NOT_ALLOWED"):
            client._json(ENDPOINT, source="bls", method="POST", body=body,
                         headers={"Content-Type": "application/json", "Accept": "application/json"})
    assert t.calls == []


def test_no_rights_mean_no_network_or_post(monkeypatch):
    monkeypatch.setenv("OB_KEYLESS_BLS_V1_POST_FALLBACK_ENABLED", "1")
    t = OfficialTransport(None, None)
    with pytest.raises(PublicResearchUnavailable, match="OWNER_SOURCE_REVIEW_REQUIRED"):
        PublicReferenceClient(OwnerResearchPolicy(), opener=t).bls_v1(SERIES)
    assert t.calls == []
