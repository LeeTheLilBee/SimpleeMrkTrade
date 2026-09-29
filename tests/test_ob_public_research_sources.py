"""Offline tests: all values, keys and payloads are synthetic fixtures, never live feeds."""
from __future__ import annotations

from datetime import timezone
import json
from urllib.error import URLError

import pytest

from engine.market_intake.public_research_sources import (
    OwnerResearchPolicy, PublicReferenceClient, PublicResearchUnavailable,
)


class Response:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode() if not isinstance(payload, bytes) else payload
    def __enter__(self):
        return self
    def __exit__(self, *_):
        return False
    def read(self, limit):
        return self.payload[:limit]


class FixtureOpener:
    def __init__(self, response):
        self.response = response
        self.requests = []
    def __call__(self, request, *, timeout):
        self.requests.append((request, timeout))
        if isinstance(self.response, Exception):
            raise self.response
        return Response(self.response)


POLICY = OwnerResearchPolicy(
    source_use_reviewed=True, owner_display_reviewed=True,
    reviewed_sources=frozenset({"bls", "bea", "openfigi"}),
)


def test_no_network_without_explicit_rights_review():
    opener = FixtureOpener({})
    client = PublicReferenceClient(OwnerResearchPolicy(), opener=opener)
    with pytest.raises(PublicResearchUnavailable, match="OWNER_SOURCE_REVIEW_REQUIRED"):
        client.bls_v1("CUUR0000SA0")
    with pytest.raises(PublicResearchUnavailable, match="OWNER_SOURCE_REVIEW_REQUIRED"):
        client.openfigi_ticker("MSFT")
    assert not opener.requests


def test_bls_unregistered_v1_source_bound_and_never_price_authority():
    payload = {"status": "REQUEST_SUCCEEDED", "Results": [{"series": [
        {"seriesID": "CUUR0000SA0", "data": [
            {"year": "2026", "period": "M08", "value": "321.7"},
            {"year": "2026", "period": "M07", "value": "320.1"},
            {"year": "2025", "period": "M12", "value": "310"},
        ]}]}]
    opener = FixtureOpener(payload)
    row = PublicReferenceClient(POLICY, opener=opener).bls_v1("CUUR0000SA0")
    assert row.value == "321.7" and row.period == "2026-M08"
    assert row.release_at is None and row.fetched_at.tzinfo == timezone.utc
    assert row.current_quote_eligible is False
    assert row.ai_use_approved is False and row.broker_execution_authorized is False
    assert opener.requests[0][0].full_url.endswith("/CUUR0000SA0")
    assert opener.requests[0][1] == 8


def test_bls_rejects_unknown_or_malformed_records():
    opener = FixtureOpener({"status": "REQUEST_SUCCEEDED", "Results": {"series": [
        {"seriesID": "CUUR0000SA0", "data": [{"year": "2026", "period": "M09", "value": "NaN"}]}]}]})
    with pytest.raises(PublicResearchUnavailable):
        PublicReferenceClient(POLICY, opener=opener).bls_v1("CUUR0000SA0")
    with pytest.raises(PublicResearchUnavailable):
        PublicReferenceClient(POLICY, opener=opener).bls_v1("../price")
    assert len(opener.requests) == 1


def test_bea_uses_backend_key_and_never_exposes_it_in_reference():
    payload = {"BEAAPI": {"Results": {"Data": [
        {"LineNumber": "1", "TimePeriod": "2026Q1", "DataValue": "30,001.2"},
        {"LineNumber": "1", "TimePeriod": "2025Q4", "DataValue": "29,900.0"},
        {"LineNumber": "2", "TimePeriod": "2026Q2", "DataValue": "77"},
    ]}}}
    opener = FixtureOpener(payload)
    client = PublicReferenceClient(POLICY, opener=opener)
    with pytest.raises(PublicResearchUnavailable, match="BEA_KEY_NOT_CONFIGURED"):
        client.bea_nipa("")
    row = client.bea_nipa("synthetic-key-12345")
    assert row.series_id == "T10105:Q:1"
    assert row.value == "30001.2" and row.period == "2026Q1"
    assert "synthetic-key" not in str(row)
    assert "synthetic-key" in opener.requests[0][0].full_url
    assert row.current_quote_eligible is False and row.release_at is None


def test_openfigi_single_mapping_and_ambiguous_hold():
    unique = [{"data": [{"figi": "BBG000B9XRY4", "ticker": "MSFT",
                         "name": "SYNTHETIC EXAMPLE"}]}]
    opener = FixtureOpener(unique)
    result = PublicReferenceClient(POLICY, opener=opener).openfigi_ticker("MSFT")
    assert result.status == "MATCH" and result.figi == "BBG000B9XRY4"
    assert result.company_identity_verified is False and result.current_quote_eligible is False
    assert opener.requests[0][0].get_method() == "POST"
    assert b'"idType": "TICKER"' in opener.requests[0][0].data
    ambiguous = FixtureOpener([{"data": unique[0]["data"] * 2}])
    held = PublicReferenceClient(POLICY, opener=ambiguous).openfigi_ticker("MSFT")
    assert held.status == "AMBIGUOUS_HOLD" and held.figi is None
    with pytest.raises(PublicResearchUnavailable):
        PublicReferenceClient(POLICY, opener=opener).openfigi_ticker("../../BAD")
    assert len(opener.requests) == 1


def test_openfigi_vendor_errors_and_incomplete_shapes_fail_closed():
    for response in ([{"error": "simulated upstream failure"}], [{"warning": "not mapped"}]):
        opener = FixtureOpener(response)
        with pytest.raises(PublicResearchUnavailable, match="FIGI_SOURCE_SHAPE_HOLD"):
            PublicReferenceClient(POLICY, opener=opener).openfigi_ticker("MSFT")


def test_network_error_response_ceiling_and_no_price_promotion():
    failing = FixtureOpener(URLError("synthetic-sensitive-error"))
    with pytest.raises(PublicResearchUnavailable, match="SOURCE_TRANSPORT_HOLD") as error:
        PublicReferenceClient(POLICY, opener=failing).bls_v1("LNS14000000")
    assert "synthetic-sensitive" not in str(error.value)
    huge = FixtureOpener(b"{" + b"x" * 1_000_001)
    with pytest.raises(PublicResearchUnavailable, match="SOURCE_RESPONSE_TOO_LARGE"):
        PublicReferenceClient(POLICY, opener=huge).bls_v1("LNS14000000")


def test_research_sources_cannot_install_as_equity_or_option_quote():
    from engine.market_intake.gateway import UniversalMarketGateway
    from engine.market_intake.provider_catalog import CATALOG
    keys = {"bls-public-v1", "bea-nipa", "openfigi-identifier",
            "fred-macro-review-only", "public-business-review-only"}
    assert keys <= set(CATALOG)
    assert all(CATALOG[key].current_quote_eligible is False for key in keys)
    assert all(CATALOG[key].quote_kind == "reference" for key in keys)
    gateway = UniversalMarketGateway()
    rows = {p["product_key"]: p for p in gateway.provider_status()["providers"]}
    assert all(rows[key]["state"] == "REFERENCE_ONLY" for key in keys)
    assert gateway.provider_status()["live_transport_connected"] is False


def test_one_provider_review_never_inherits_use_or_ai_permission_for_another():
    bls_only = OwnerResearchPolicy(
        source_use_reviewed=True, owner_display_reviewed=True, ai_use_reviewed=True,
        reviewed_sources=frozenset({"bls"}), ai_reviewed_sources=frozenset({"bls"}),
    )
    opener = FixtureOpener({"BEAAPI": {"Results": {"Data": []}}})
    client = PublicReferenceClient(bls_only, opener=opener)
    with pytest.raises(PublicResearchUnavailable, match="OWNER_SOURCE_REVIEW_REQUIRED"):
        client.bea_nipa("synthetic-key-12345")
    with pytest.raises(PublicResearchUnavailable, match="OWNER_SOURCE_REVIEW_REQUIRED"):
        client.openfigi_ticker("MSFT")
    assert not opener.requests
    bls_opener = FixtureOpener({"status":"REQUEST_SUCCEEDED", "Results":[{"series":[{
        "seriesID":"LNS14000000","data":[{"year":"2026","period":"M08","value":"4.2"}]
    }]}]})
    result = PublicReferenceClient(bls_only, opener=bls_opener).bls_v1("LNS14000000")
    assert result.ai_use_approved is True
    review_without_ai = OwnerResearchPolicy(
        source_use_reviewed=True, owner_display_reviewed=True, ai_use_reviewed=True,
        reviewed_sources=frozenset({"bls"}), ai_reviewed_sources=frozenset(),
    )
    result = PublicReferenceClient(review_without_ai, opener=bls_opener).bls_v1("LNS14000000")
    assert result.ai_use_approved is False


@pytest.mark.parametrize("bad_kwargs", [
    {"table":None}, {"table":[]}, {"frequency":None}, {"frequency":[]},
    {"line_number":None}, {"line_number":1}, {"line_number":[]},
])
def test_bea_malformed_query_is_redacted_hold_without_network(bad_kwargs):
    opener=FixtureOpener({})
    client=PublicReferenceClient(POLICY, opener=opener)
    with pytest.raises(PublicResearchUnavailable, match="BEA_QUERY_INVALID"):
        client.bea_nipa("synthetic-key-12345", **bad_kwargs)
    assert opener.requests==[]


def test_fixed_endpoint_and_method_pair_rejects_nonstandard_calls():
    opener=FixtureOpener({})
    client=PublicReferenceClient(POLICY, opener=opener)
    with pytest.raises(PublicResearchUnavailable, match="SOURCE_ENDPOINT_NOT_ALLOWED"):
        client._json("https://api.bls.gov/publicAPI/v1/timeseries/data/ABC123",
                     source="bea", method="GET")
    with pytest.raises(PublicResearchUnavailable, match="SOURCE_ENDPOINT_NOT_ALLOWED"):
        client._json("https://api.openfigi.com/v3/mapping", source="openfigi",
                     method="GET")
    with pytest.raises(PublicResearchUnavailable, match="BLS_SERIES_INVALID"):
        client.bls_v1("ABC#fragment")
    assert not opener.requests


def test_owner_cli_needs_per_provider_flags_before_constructing_network(monkeypatch, capsys):
    import scripts.ob_public_research_check as cli
    import sys
    monkeypatch.setattr(sys, "argv", ["ob_public_research_check", "--source", "bea"])
    for key in ("OB_PUBLIC_RESEARCH_ENABLED", "OB_PUBLIC_RESEARCH_USE_REVIEWED",
                "OB_PUBLIC_RESEARCH_OWNER_DISPLAY_REVIEWED"):
        monkeypatch.setenv(key,"1")
    monkeypatch.delenv("OB_PUBLIC_RESEARCH_BEA_USE_REVIEWED",raising=False)
    monkeypatch.delenv("OB_PUBLIC_RESEARCH_BEA_OWNER_DISPLAY_REVIEWED",raising=False)
    assert cli.main()==2
    assert "independently reviewed" in capsys.readouterr().out
