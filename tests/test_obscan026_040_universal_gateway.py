"""Offline tests: synthetic quotes only, never actual vendor credentials or prices."""
from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from engine.market_intake.adapters import FeedAdapter
from engine.market_intake.contracts import ScanContext, SourceRights
from engine.market_intake.gateway import UniversalMarketGateway
from engine.market_intake.provider_catalog import CATALOG, ProviderProduct
from engine.market_intake.traffic import ProviderBudget
from engine.market_intake.universe import parse_nasdaq_directory

NOW = datetime(2026, 9, 28, 15, 0, tzinfo=timezone.utc)
CONTEXT = ScanContext(NOW, "REGULAR", True)
EQUITY_FIELDS = {name: name for name in (
    "observation_id", "symbol", "observed_at", "provenance_reference", "last",
    "bid", "ask", "previous_close", "volume", "average_volume")}
OPTION_FIELDS = {name: name for name in (
    "observation_id", "underlying", "occ_symbol", "observed_at",
    "provenance_reference", "bid", "ask", "strike", "expiry", "right",
    "volume", "open_interest")}


def rights(source, family, instrument, *, owner=True):
    return SourceRights(source, family, "reviewed-fixture-rights-" + source,
                        NOW - timedelta(hours=1), internal_research=True,
                        automated_non_display=True, owner_display=owner,
                        real_time_entitled=True, entitled_instruments=frozenset({instrument}))


def stock(source="feed-1", *, age=1, last=100.0, observation="q1"):
    return {"observation_id": observation, "symbol": "XYZ",
            "observed_at": (NOW-timedelta(seconds=age)).isoformat(),
            "provenance_reference": "signed-synthetic-fixture",
            "last": last, "bid": 99.9, "ask": 105.0, "previous_close": 96.0,
            "volume": 1000, "average_volume": 500.0,
            "source_id": "UNTRUSTED-SPOOFED-VENDOR"}


def option(*, age=1, observation="o1", volume=10):
    return {"observation_id": observation, "underlying": "XYZ",
            "occ_symbol": "XYZ   261002C00100000",
            "observed_at": (NOW-timedelta(seconds=age)).isoformat(),
            "provenance_reference": "synthetic-contract-fixture",
            "bid": 1.0, "ask": 1.2, "strike": 100.0, "expiry": "2026-10-02",
            "right": "call", "volume": volume, "open_interest": 100}


def universe():
    snapshot = ("Symbol|Security Name|Market Category|Test Issue|Financial Status|Round Lot Size|ETF|NextShares\n"
                "XYZ|Synthetic Example|Q|N|N|100|N|N\n")
    return {row.symbol: row for row in
            parse_nasdaq_directory(snapshot, directory="nasdaqlisted.txt", observed_at=NOW)}


def register_stock(gateway, source="feed-1", family="SIP", product="tradier-equity",
                   *, owner=True, budget=None):
    policy = rights(source, family, "equity", owner=owner)
    gateway.install(product, rights=policy,
                    adapter=FeedAdapter(policy, EQUITY_FIELDS, "realtime", "equity"),
                    budget=budget)
    return policy


def register_option(gateway, source="options-1", family="OPRA",
                    product="tradier-options", *, owner=True, budget=None):
    policy = rights(source, family, "option", owner=owner)
    gateway.install(product, rights=policy,
                    adapter=FeedAdapter(policy, OPTION_FIELDS, "realtime", "option"),
                    budget=budget)
    return policy


def test_catalog_has_all_planned_provider_families_without_claiming_subscription():
    gateway = UniversalMarketGateway()
    snapshot = gateway.provider_status()
    expected = {"tradier-equity", "tradier-options", "alpaca-iex-equity",
                "alpaca-sip-equity", "alpaca-opra-options", "alpaca-indicative-options",
                "ibkr-equity", "ibkr-options", "direct-sip-equity",
                "direct-opra-options", "nasdaq-directory", "occ-reports", "sec-edgar"}
    assert expected <= set(CATALOG)
    assert all(x["state"] == "NOT_CONFIGURED" for x in snapshot["providers"]
               if x["instrument"] in {"equity", "option"})
    assert all(x["state"] == "REFERENCE_ONLY" for x in snapshot["providers"]
               if x["instrument"] in {"event", "metadata"})
    assert snapshot["live_transport_connected"] is False
    assert snapshot["api_tokens_configured"] is False
    assert not snapshot["broker_order_transport"]


def test_installed_equity_ingest_source_truth_and_survey_packet_only():
    gateway = UniversalMarketGateway()
    register_stock(gateway)
    decision = gateway.ingest("feed-1", stock(), received_at=NOW, context=CONTEXT)
    assert decision.state == "CURRENT_RESEARCH" and decision.stored
    assert decision.owner_visible and not decision.invitee_visible
    assert not decision.broker_execution_authorized
    packet = gateway.owner_research_packet("XYZ", universe=universe(), context=CONTEXT)
    assert packet["state"] == "RESEARCH_WATCH"
    assert packet["equity_sources"] == ["feed-1"]
    assert packet["gateway"]["audience"] == "owner_only"
    assert packet["eligibility"]["manual_live_authorized"] is False
    assert packet["eligibility"]["auto_execution"] is False
    assert "market_quotes" not in packet
    assert "UNTRUSTED-SPOOFED-VENDOR" not in str(packet)


def test_indicative_reference_unknown_or_mismatched_products_cannot_be_live_feed():
    gateway = UniversalMarketGateway()
    r = rights("indicative-1", "INDICATIVE", "option")
    for product in ("alpaca-indicative-options", "nasdaq-directory", "sec-edgar"):
        with pytest.raises(ValueError):
            gateway.install(product, rights=r,
                            adapter=FeedAdapter(r, OPTION_FIELDS, "realtime", "option"))
    with pytest.raises(ValueError):
        gateway.install("missing-connector", rights=r,
                        adapter=FeedAdapter(r, OPTION_FIELDS, "realtime", "option"))
    with pytest.raises(ValueError):
        gateway.install("tradier-equity", rights=r,
                        adapter=FeedAdapter(r, OPTION_FIELDS, "realtime", "option"))
    invalid = replace(r, real_time_entitled=False)
    with pytest.raises(ValueError):
        FeedAdapter(invalid, OPTION_FIELDS, "realtime", "option")


def test_freshness_missing_timestamp_future_receipt_and_expiry_holds():
    gateway = UniversalMarketGateway()
    register_stock(gateway)
    assert gateway.ingest("feed-1", stock(age=60), received_at=NOW,
                          context=CONTEXT).state == "TEMPORAL_HOLD"
    assert gateway.ingest("feed-1", {k:v for k,v in stock().items() if k != "observed_at"},
                          received_at=NOW, context=CONTEXT).state == "INVALID_HOLD"
    assert gateway.ingest("feed-1", stock(), received_at=NOW+timedelta(minutes=2),
                          context=CONTEXT).state == "TEMPORAL_HOLD"
    assert gateway.ingest("feed-1", stock(), received_at=NOW,
                          context=replace(CONTEXT, verified_market_time=False)).state == "CONTEXT_HOLD"
    assert gateway.ingest("feed-1", stock(), received_at=NOW,
                          context=replace(CONTEXT, now=NOW+timedelta(days=1))).state == "TEMPORAL_HOLD"
    expired = UniversalMarketGateway()
    policy = replace(rights("expired", "SIP", "equity"),
                     expires_at=NOW-timedelta(seconds=1))
    expired.install("tradier-equity", rights=policy,
                    adapter=FeedAdapter(policy, EQUITY_FIELDS, "realtime", "equity"))
    assert expired.ingest("expired", stock(), received_at=NOW,
                          context=CONTEXT).state == "RIGHTS_HOLD"
    assert expired.provider_status(CONTEXT)["providers"][
        next(i for i,p in enumerate(expired.provider_status(CONTEXT)["providers"])
             if p["product_key"] == "tradier-equity")]["state"] == "RIGHTS_HOLD"


def test_no_downgrade_on_out_of_order_and_revocation_purges_quotes():
    gateway = UniversalMarketGateway()
    register_stock(gateway)
    assert gateway.ingest("feed-1", stock(), received_at=NOW, context=CONTEXT).stored
    assert gateway.ingest("feed-1", stock(age=2, observation="older"),
                          received_at=NOW, context=CONTEXT).state == "OUT_OF_ORDER_HOLD"
    assert gateway.ingest("feed-1", stock(observation="duplicate"),
                          received_at=NOW, context=CONTEXT).state == "OUT_OF_ORDER_HOLD"
    gateway.revoke("feed-1")
    assert gateway.ingest("feed-1", stock(), received_at=NOW,
                          context=CONTEXT).state == "SOURCE_HOLD"
    packet = gateway.owner_research_packet("XYZ", universe=universe(), context=CONTEXT)
    assert packet["state"] == "DATA_HOLD" and packet["equity_sources"] == []


def test_non_display_permission_does_not_leak_into_owner_packet():
    gateway = UniversalMarketGateway()
    register_stock(gateway, owner=False)
    decision = gateway.ingest("feed-1", stock(), received_at=NOW, context=CONTEXT)
    assert decision.stored and not decision.owner_visible
    packet = gateway.owner_research_packet("XYZ", universe=universe(), context=CONTEXT)
    assert packet["state"] == "DATA_HOLD" and packet["equity_sources"] == []


def test_distinct_upstream_feeds_and_reused_sip_cannot_fake_corroboration():
    gateway = UniversalMarketGateway()
    register_stock(gateway, source="a", family="SIP", product="tradier-equity")
    register_stock(gateway, source="b", family="SIP", product="alpaca-sip-equity")
    gateway.ingest("a", stock(observation="a"), received_at=NOW, context=CONTEXT)
    gateway.ingest("b", stock(last=104, observation="b"), received_at=NOW, context=CONTEXT)
    packet = gateway.owner_research_packet("XYZ", universe=universe(), context=CONTEXT)
    assert packet["state"] != "CONFLICT_HOLD"
    assert len(packet["equity_sources"]) == 1
    register_stock(gateway, source="c", family="DIRECT-INDEPENDENT", product="ibkr-equity")
    gateway.ingest("c", stock(last=104, observation="c"), received_at=NOW, context=CONTEXT)
    packet = gateway.owner_research_packet("XYZ", universe=universe(), context=CONTEXT)
    assert packet["state"] == "CONFLICT_HOLD" and len(packet["equity_sources"]) == 2
    assert not packet["eligibility"]["candidate_admitted"]


def test_options_only_source_has_separate_budget_and_verified_underlying_queue():
    gateway = UniversalMarketGateway()
    register_option(gateway, budget=ProviderBudget("options-1", 2, 3, supports_options=True,
        supports_streaming=True, max_stream_symbols=2, research_entitlement_confirmed=True))
    proposals = gateway.plan_requests(context=CONTEXT, watchlist=["XYZ"],
                                     verified_option_underlyings=["XYZ", "DEF"])
    assert len(proposals) == 1 and proposals[0].lane == "options"
    assert proposals[0].symbols == ("XYZ", "DEF")
    assert not proposals[0].network_called and not proposals[0].order_placed
    assert gateway.stream_selection("options-1", context=CONTEXT,
                                    symbols=["XYZ", "DEF", "AAA"]) == ("XYZ", "DEF")
    assert gateway.plan_requests(context=CONTEXT,
                                 verified_option_underlyings=["XYZ"]) == ()


def test_option_quote_needs_separate_rights_and_current_underlying_for_research():
    gateway = UniversalMarketGateway()
    register_option(gateway)
    decision = gateway.ingest("options-1", option(), received_at=NOW, context=CONTEXT)
    assert decision.stored
    no_underlying = gateway.owner_research_packet("XYZ", universe=universe(), context=CONTEXT)
    assert no_underlying["option_sources"] == [] and no_underlying["state"] == "DATA_HOLD"
    register_stock(gateway)
    gateway.ingest("feed-1", stock(), received_at=NOW, context=CONTEXT)
    ready = gateway.owner_research_packet("XYZ", universe=universe(), context=CONTEXT)
    assert ready["option_sources"] == ["options-1"]
    assert ready["eligibility"]["broker_quote_verified"] is False
    bad = gateway.ingest("options-1", option(observation="fraction", volume=1.5),
                         received_at=NOW, context=CONTEXT)
    assert bad.state == "INVALID_HOLD"


def test_unknown_limits_no_requests_and_future_provider_extension():
    gateway = UniversalMarketGateway()
    register_stock(gateway, budget=ProviderBudget("feed-1", 0, 0,
        research_entitlement_confirmed=True))
    assert gateway.plan_requests(context=CONTEXT, watchlist=["XYZ"]) == ()
    product = ProviderProduct("future-equity", "Future approved vendor",
                              "Custom venue equities", "equity",
                              "entitlement_defined", True, "https://example.org/documentation")
    gateway.add_product(product)
    assert any(x["product_key"] == "future-equity" for x in gateway.provider_status()["providers"])
    with pytest.raises(ValueError):
        gateway.add_product(product)
    with pytest.raises(ValueError):
        ProviderProduct("fake-live", "Fake", "Indicative", "option",
                        "indicative", True, "https://example.org/")
