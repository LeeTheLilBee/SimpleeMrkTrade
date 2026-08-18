# OBUX032 — Live Canonical Feed

Market Map uses the existing canonical OBDATA projection.

The existing engine adapter polls:

`/ob/engine-feed-snapshot.json`

on its existing 60-second cadence.

Market Map performs no independent market fetch.

When the canonical adapter emits:

`obEngineFeedAdapterUpdated`

Market Map rereads:

`OB_DATA_CONTRACTS_V22.marketMapContract()`

and:

`OB_ENGINE_FEED_ADAPTER_V25.getProjection()`

then rerenders the room in place.

Freshness and eligibility changes are reflected immediately on the next
canonical feed event.
