"""Public API integration uses synthetic official-shaped data, NEVER a live account."""
from datetime import datetime, timedelta, timezone
import json

import pytest

from engine.market_intake.public_quote_readonly import (
    PublicQuoteHold, PublicReadPolicy, QuoteRequest, PublicReadOnlyQuoteClient,
    PublicReadOnlyOptionChainClient, normalize_public_quotes,
)
from engine.market_intake.adapters import FeedAdapter
from engine.market_intake.contracts import ScanContext, SourceRights
from engine.market_intake.gateway import UniversalMarketGateway
from engine.market_intake.provider_catalog import CATALOG


NOW = datetime(2026, 9, 29, 15, 0, tzinfo=timezone.utc)
STOCK = QuoteRequest("XYZ", "EQUITY")
OPTION = QuoteRequest("XYZ261002C00100000", "OPTION")
FIELDS = {n: n for n in (
    "observation_id", "symbol", "observed_at", "provenance_reference", "last",
    "bid", "ask", "previous_close", "volume", "average_volume",
)}
OPT_FIELDS = {n: n for n in (
    "observation_id", "underlying", "occ_symbol", "observed_at",
    "provenance_reference", "bid", "ask", "strike", "expiry", "right",
    "volume", "open_interest",
)}


def stamp(seconds=0):
    return (NOW + timedelta(seconds=seconds)).isoformat()


def equity(*, last_time=-1, bid_time=-1, ask_time=-1):
    return {"instrument": {"symbol": "XYZ", "type": "EQUITY"}, "outcome": "SUCCESS",
            "last": "100.3", "lastTimestamp": stamp(last_time),
            "bid": "100.1", "bidTimestamp": stamp(bid_time),
            "ask": "100.5", "askTimestamp": stamp(ask_time),
            "volume": 300, "previousClose": "99.5"}


def option(*, last_time=-1, bid_time=-1, ask_time=-1):
    return {"instrument": {"symbol": OPTION.symbol, "type": "OPTION"}, "outcome": "SUCCESS",
            "last": "1.25", "lastTimestamp": stamp(last_time),
            "bid": "1.20", "bidTimestamp": stamp(bid_time),
            "ask": "1.30", "askTimestamp": stamp(ask_time),
            "volume": 12, "openInterest": 90, "optionDetails": {"strikePrice": "100.00"}}


def parse(rows, req):
    return normalize_public_quotes({"quotes": rows}, req, received_at=NOW)


def test_equity_and_option_mapping_is_not_an_entitlement_or_execution():
    stock, opt = parse([equity(), option()], [STOCK, OPTION])
    assert stock.normalized["symbol"] == "XYZ"
    assert stock.normalized["previous_close"] == 99.5
    assert opt.normalized["occ_symbol"] == "XYZ   261002C00100000"
    assert opt.normalized["underlying"] == "XYZ"
    assert opt.normalized["expiry"] == "2026-10-02" and opt.normalized["right"] == "call"
    assert opt.normalized["strike"] == 100
    assert all(not p.quote_verified_live and not p.gateway_installed and
               not p.broker_execution_authorized for p in (stock, opt))
    assert "accountId" not in str(stock.gateway_fields())


def test_oldest_independent_event_prevents_fresh_bid_masking_stale_last():
    stock, = parse([equity(last_time=-60, bid_time=-1, ask_time=-1)], [STOCK])
    assert stock.normalized["observed_at"] == stamp(-60)
    assert stock.bid_timestamp.isoformat() == stamp(-1)
    rights = SourceRights("public-owned-equity", "UNKNOWN_UNVERIFIED_UPSTREAM",
        "synthetic-reviewed-permission", NOW - timedelta(hours=1),
        internal_research=True, automated_non_display=True, owner_display=True,
        real_time_entitled=True, entitled_instruments=frozenset({"equity"}))
    gateway = UniversalMarketGateway()
    gateway.install("public-account-equity", rights=rights,
                    adapter=FeedAdapter(rights, FIELDS, "realtime", "equity"))
    result = gateway.ingest(rights.source_id, stock.gateway_fields(),
                            received_at=NOW, context=ScanContext(NOW, "REGULAR", True))
    assert result.state == "TEMPORAL_HOLD" and not result.stored


def test_independent_equity_option_source_rights_are_required():
    gateway = UniversalMarketGateway()
    assert CATALOG["public-account-equity"].instrument == "equity"
    assert CATALOG["public-account-option"].instrument == "option"
    assert all(p["state"] == "NOT_CONFIGURED" for p in gateway.provider_status()["providers"]
               if p["product_key"].startswith("public-account-"))
    assert not gateway.provider_status()["live_transport_connected"]


def test_mismatched_missing_duplicate_crossed_or_unsuccessful_quotes_hold():
    for rows, requests in (
        ([equity()], [OPTION]),
        ([equity(), equity()], [STOCK, OPTION]),
        ([{**equity(), "outcome": "NO_DATA"}], [STOCK]),
        ([{**equity(), "bid": "200"}], [STOCK]),
        ([{k:v for k,v in equity().items() if k != "askTimestamp"}], [STOCK]),
        ([equity()], [STOCK, STOCK]),
    ):
        with pytest.raises(PublicQuoteHold):
            parse(rows, requests)


def test_bad_option_identifiers_and_strike_mismatch_hold():
    with pytest.raises(ValueError):
        QuoteRequest("XYZ 261002C00100000", "OPTION")
    bad = option()
    bad["optionDetails"]["strikePrice"] = "101.00"
    with pytest.raises(PublicQuoteHold, match="PUBLIC_OPTION_STRIKE_CONFLICT"):
        parse([bad], [OPTION])


def test_future_source_timestamp_or_negative_nonfinite_or_fractional_count_hold():
    variants = (
        {**equity(), "lastTimestamp": stamp(3)},
        {**equity(), "last": "NaN"},
        {**equity(), "last": "Infinity"},
        {**equity(), "last": "1e10000"},
        {**equity(), "volume": 1.5},
        {**equity(), "ask": "0"},
    )
    for row in variants:
        with pytest.raises(PublicQuoteHold):
            parse([row], [STOCK])


class Result:
    def __init__(self, payload):
        self.body = json.dumps(payload).encode()
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def read(self, n):
        return self.body[:n]


class Opener:
    def __init__(self):
        self.requests = []
    def __call__(self, request, timeout):
        self.requests.append((request, timeout))
        t = datetime.now(timezone.utc) - timedelta(seconds=1)
        row = equity()
        for k in ("lastTimestamp", "bidTimestamp", "askTimestamp"):
            row[k] = t.isoformat()
        return Result({"quotes": [row]})


TOKEN = "syntheticTokenForTestsOnly_12345"
ACCOUNT = "synthetic-account-1"


def test_no_transport_without_literal_reviewed_scope_or_instrument_permission():
    open_mock = Opener()
    incomplete = PublicReadPolicy(account_scope_reviewed=True,
                                  non_display_use_reviewed=True,
                                  owner_display_reviewed=True,
                                  marketdata_scope_verified=True)
    client = PublicReadOnlyQuoteClient(incomplete, opener=open_mock)
    with pytest.raises(PublicQuoteHold, match="PUBLIC_SCOPE_RIGHTS_HOLD"):
        client.fetch_once(backend_account_id=ACCOUNT, backend_access_token=TOKEN,
                          requests=[STOCK])
    assert open_mock.requests == []
    # Untrusted truthy strings are not policy grants.
    forged = PublicReadPolicy("true", "true", "true", "true", "true", "true")
    assert forged.permits({"EQUITY"}) is False


def test_authenticated_request_is_one_read_only_marketdata_endpoint():
    opener = Opener()
    reviewed = PublicReadPolicy(True, True, True, True, True, False)
    client = PublicReadOnlyQuoteClient(reviewed, opener=opener)
    result = client.fetch_once(backend_account_id=ACCOUNT,
                               backend_access_token=TOKEN, requests=[STOCK])
    assert len(result) == 1 and not result[0].broker_execution_authorized
    assert len(opener.requests) == 1
    req, timeout = opener.requests[0]
    assert timeout == 8 and req.get_method() == "POST"
    assert req.full_url == ("https://api.public.com/userapigateway/marketdata/"
                            + ACCOUNT + "/quotes")
    assert b'"type": "EQUITY"' in req.data
    assert not any(x in req.full_url for x in ("order", "preflight", "token"))
    assert TOKEN not in str(result[0]) and ACCOUNT not in str(result[0])
    with pytest.raises(PublicQuoteHold, match="PUBLIC_SCOPE_RIGHTS_HOLD"):
        client.fetch_once(backend_account_id=ACCOUNT,
                          backend_access_token=TOKEN, requests=[OPTION])


def test_account_token_and_batch_rejection_before_network():
    opener = Opener()
    client = PublicReadOnlyQuoteClient(PublicReadPolicy(True, True, True, True, True, True),
                                        opener=opener)
    for account, token, requests in (
        ("../../bad", TOKEN, [STOCK]), (ACCOUNT, "", [STOCK]),
        (ACCOUNT, TOKEN, [STOCK, STOCK]), (ACCOUNT, TOKEN, []),
        (ACCOUNT, TOKEN, [STOCK] * 9),
    ):
        with pytest.raises(PublicQuoteHold):
            client.fetch_once(backend_account_id=account,
                              backend_access_token=token, requests=requests)
    assert not opener.requests


class OptionChainOpener:
    def __init__(self):
        self.requests = []

    def __call__(self, request, timeout):
        self.requests.append((request, timeout))
        now = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()
        if request.full_url.endswith("/option-expirations"):
            return Result({"baseSymbol": "XYZ", "expirations": ["2026-10-02", "2026-10-09"]})
        if request.full_url.endswith("/quotes"):
            row = equity()
            for key in ("lastTimestamp", "bidTimestamp", "askTimestamp"):
                row[key] = now
            return Result({"quotes": [row]})
        if request.full_url.endswith("/option-chain"):
            def chain_row(symbol, strike, oi, volume, delta, iv):
                return {
                    "instrument": {"symbol": symbol, "type": "OPTION"},
                    "outcome": "SUCCESS",
                    "last": "1.25", "lastTimestamp": now,
                    "bid": "1.20", "bidSize": 5, "bidTimestamp": now,
                    "ask": "1.30", "askSize": 7, "askTimestamp": now,
                    "volume": volume, "openInterest": oi,
                    "optionDetails": {
                        "strikePrice": str(strike),
                        "midPrice": "1.25",
                        "greeks": {
                            "delta": str(delta), "gamma": "0.05",
                            "theta": "-0.03", "vega": "0.08",
                            "rho": "0.01", "impliedVolatility": str(iv),
                        },
                    },
                }
            return Result({
                "baseSymbol": "XYZ",
                "calls": [
                    chain_row("XYZ261002C00100000", "100", 900, 120, 0.52, 0.31),
                    chain_row("XYZ261002C00105000", "105", 300, 40, 0.31, 0.36),
                ],
                "puts": [
                    chain_row("XYZ261002P00100000", "100", 800, 110, -0.48, 0.33),
                    chain_row("XYZ261002P00095000", "95", 250, 35, -0.28, 0.39),
                ],
            })
        raise AssertionError(request.full_url)


def test_public_option_chain_is_bounded_owner_research_and_never_order_authority():
    opener = OptionChainOpener()
    policy = PublicReadPolicy(True, True, True, True, True, True)
    snapshot = PublicReadOnlyOptionChainClient(policy, opener=opener).fetch_nearest(
        backend_account_id=ACCOUNT,
        backend_access_token=TOKEN,
        symbol="XYZ",
    )
    assert snapshot.underlying == "XYZ"
    assert snapshot.expiration == "2026-10-02"
    assert snapshot.underlying_midpoint == 100.3
    assert len(snapshot.contracts) == 4
    assert any(row["greeks"]["implied_volatility"] == 0.31 for row in snapshot.contracts)
    assert any(row["open_interest"] == 900 for row in snapshot.contracts)
    assert snapshot.broker_execution_authorized is False
    assert [req.full_url.rsplit("/", 1)[-1] for req, _ in opener.requests] == [
        "option-expirations", "quotes", "option-chain"
    ]
    assert all("order" not in req.full_url and "preflight" not in req.full_url
               for req, _ in opener.requests)
