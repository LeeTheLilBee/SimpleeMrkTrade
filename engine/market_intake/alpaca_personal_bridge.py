"""Install Alpaca IEX into OB's provider-neutral research gateway.

This is intentionally owner-development only. It converts the reviewed Alpaca
IEX payload into the same SourceRights / FeedAdapter / UniversalMarketGateway
contracts used by the scanner. No order transport is present.
"""
from __future__ import annotations

from datetime import datetime, timezone

from engine.market_intake import FeedAdapter, SourceRights, UniversalMarketGateway

SOURCE_ID = "alpaca-personal-iex"
UPSTREAM = "iex"
PRODUCT_KEY = "alpaca-iex-equity"
PERMISSION_REFERENCE = "https://docs.alpaca.markets/us/docs/about-market-data-api"


def reviewed_rights(*, verified_at=None):
    verified_at = verified_at or datetime.now(timezone.utc)
    return SourceRights(
        source_id=SOURCE_ID,
        upstream_family=UPSTREAM,
        permission_reference=PERMISSION_REFERENCE,
        verified_at=verified_at,
        internal_research=True,
        automated_non_display=True,
        owner_display=True,
        invitee_display=False,
        redistribution=False,
        real_time_entitled=True,
        entitled_instruments=frozenset({"equity"}),
    )


def adapter(*, verified_at=None):
    rights = reviewed_rights(verified_at=verified_at)
    return FeedAdapter(
        source=rights,
        instrument="equity",
        feed_label="realtime",
        fields={
            "observation_id": "observation_id",
            "observed_at": "observed_at",
            "provenance_reference": "provenance_reference",
            "symbol": "symbol",
            "last": "last",
            "bid": "bid",
            "ask": "ask",
            "volume": "volume",
        },
    )


def installed_gateway(*, verified_at=None):
    rights = reviewed_rights(verified_at=verified_at)
    feed = FeedAdapter(
        source=rights,
        instrument="equity",
        feed_label="realtime",
        fields={
            "observation_id": "observation_id",
            "observed_at": "observed_at",
            "provenance_reference": "provenance_reference",
            "symbol": "symbol",
            "last": "last",
            "bid": "bid",
            "ask": "ask",
            "volume": "volume",
        },
    )
    gateway = UniversalMarketGateway()
    gateway.install(PRODUCT_KEY, rights=rights, adapter=feed)
    return gateway, rights


def snapshot_to_gateway_raw(snapshot):
    quote = snapshot["quote"]
    bar = snapshot["bar"]
    bid = quote.get("bid")
    ask = quote.get("ask")
    last = quote.get("midpoint")
    if last is None:
        last = bar.get("close")
    observed_at = quote.get("timestamp") or bar.get("timestamp") or snapshot["as_of"]
    return {
        "observation_id": f"alpaca-iex:{snapshot['symbol']}:{observed_at}",
        "observed_at": observed_at,
        "provenance_reference": PERMISSION_REFERENCE,
        "symbol": snapshot["symbol"],
        "last": last,
        "bid": bid,
        "ask": ask,
        "volume": bar.get("volume"),
    }
