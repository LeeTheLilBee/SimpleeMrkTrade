# ObservatoryEventHub — unified OB event transport (2026-09-30)

## Why this exists

The Observatory needs one internal nervous system, not one WebSocket/event hub
per feature. Official Catalyst Radar, market state, provider health, scanner
context and candidate context all publish into the same bounded event bus.

ObservatoryEventHub does not own source data. It only announces that protected
authoritative state changed so an authorized consumer can re-read the correct
Tower-protected snapshot.

## Exact transport

WebSocket: /ob/events/stream
Activation: OB_EVENT_WS_ASGI_ENABLED=1
Default: OFF
Runtime: the same canonical Tower Flask app wrapped by the existing single-worker
ASGI entrypoint.

The old feature-specific Catalyst and MarketStream WebSockets are superseded.
There is one replay queue, one epoch/cursor sequence, one heartbeat/reconnect
contract and one process-local logout/replacement-session denylist.

## Event families

- research_context_changed
- source_status_changed
- market_snapshot_changed
- scanner_context_changed
- candidate_context_changed

Events contain only routing/invalidation metadata: event type, channel,
epoch/cursor, source identifier, optional symbol and an exact protected snapshot
path. Source facts, prices, bid/ask values, option-chain data, credentials,
positions and order data do not ride this socket.

Official Catalyst Radar is the first installed producer. It validates and hashes
its own source packet, then calls the shared hub only when the deterministic
fingerprint changes. The event points back to /ob/research/catalysts.json.

## Consumer rule

The WebSocket is the bell, not the book.

A page, scanner or Soulaana consumer receives an event and re-reads the exact
protected canonical snapshot. Unrelated events are ignored by consumers that do
not own that surface. Cursor gaps, queue overflow or process restart produce a
resync_required control event.

## Security

The socket requires the existing signed Tower owner session, active step-up,
consumed OB handoff and strict HTTPS same-origin. Authorization is rechecked
before accept and while connected. Client commands are rejected. Logout or
replacement login revokes the old event session in the current single-worker
process.

Multiple workers or replicas remain held until a reviewed shared replay and
session-revocation store exists.

## What this does not claim

No upstream market-data vendor WebSocket is attached by this work. No provider
gains commercial/display/non-display rights because it appears in the catalog.
No event authorizes scanner admission, a trade, broker execution, capital use or
a mode change.

Future provider-native streaming adapters must first establish their specific
rights and transport contract, update canonical OB market truth, and then publish
a small change event into this same ObservatoryEventHub.
