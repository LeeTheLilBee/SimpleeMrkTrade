# Owner Catalyst Radar transport history

> Superseded on 2026-09-30 by the unified ObservatoryEventHub. Catalyst no longer
> owns a feature-specific WebSocket, replay queue, cursor or session-revocation
> store. Its validated snapshot now publishes a research_context_changed
> invalidation onto /ob/events/stream, and consumers re-read
> /ob/research/catalysts.json.

The original Catalyst-specific WebSocket design established the safety rules now
carried forward by the shared Observatory event transport: same canonical Tower,
signed owner session, active step-up, consumed OB handoff, strict HTTPS
same-origin, bounded replay, overflow/resync behavior, no client command
protocol, no provider payloads or quote values on the wire, and no broker or
capital authority.

Current activation is OB_EVENT_WS_ASGI_ENABLED=1. The previous
OB_CATALYST_WS_ASGI_ENABLED feature flag and /ob/research/catalysts/stream path
are no longer runtime contracts.

See docs/market_data/OB_OBSERVATORY_EVENT_HUB_20260930.md for the current design.
