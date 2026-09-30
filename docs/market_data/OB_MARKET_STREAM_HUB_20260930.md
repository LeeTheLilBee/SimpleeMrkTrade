# Observatory MarketStreamHub — 2026-09-30

## Purpose

MarketStreamHub is the internal real-time nervous system for The Observatory.
It is not itself a vendor market-data feed, exchange entitlement, quote source,
scanner, broker, order route or trading authorization.

The first implementation carries only small authenticated invalidation events.
When an authoritative protected source changes, the event tells an authorized
consumer which protected REST snapshot must be re-read. Source facts, prices,
option-chain values, credentials and order data stay out of the event bus.

## Current event contract

Exact WebSocket path: /ob/market/stream

Current producer types:
- research_context_changed
- source_status_changed
- market_snapshot_changed
- scanner_context_changed
- candidate_context_changed

Every event is server-authored and includes an epoch/cursor, channel, source,
optional symbol, exact protected snapshot path, and explicit negative authority
flags. Every data-bearing consumer must recover truth from the authenticated
snapshot path.

The first installed producer is Official Catalyst Radar. A changed validated
Catalyst snapshot emits one research_context_changed event referencing
/ob/research/catalysts.json. Re-reading an unchanged snapshot does not emit a
new event.

## Security and recovery

The new socket reuses the existing Tower owner/session/step-up/OB handoff
authorization and local logout revocation boundary. HTTPS same-origin is
required. Client commands are rejected. Replay is bounded and process-local;
cursor gaps, restart epochs and queue overflow force an authenticated snapshot
resynchronization.

OB_MARKET_WS_ASGI_ENABLED=1 enables this socket. Either this flag or the older
OB_CATALYST_WS_ASGI_ENABLED flag selects the same single-worker Uvicorn ASGI
wrapper. Default remains off. Multiple workers or replicas require a reviewed
shared replay/revocation store before activation.

## What is deliberately not implemented yet

No upstream vendor WebSocket is claimed attached. No quote or option value
travels on this socket. No provider becomes commercially usable because it
appears in the provider catalog. No scanner/candidate event can authorize a
trade, and no client may subscribe itself into new rights.

The next provider-specific phase is to add adapters only for sources whose
streaming interface and commercial/display/non-display rights are explicitly
verified. Those adapters should update canonical market truth first, then use
MarketStreamHub to announce the change to Soulaana, scanner and UI consumers.
